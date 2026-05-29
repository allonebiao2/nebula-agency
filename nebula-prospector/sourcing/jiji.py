"""Scraper Jiji (services + PME, multi-pays).

Jiji est l'un des plus gros sites d'annonces en Afrique de l'Ouest.
Présent en : Bénin (jiji.bj), Togo (jiji.tg), Côte d'Ivoire (jiji.ci),
Sénégal (jiji.sn), Burkina (jiji.bf), etc.

⚠️  Les sélecteurs CSS peuvent évoluer. Ce module est conçu pour être
robuste (best-effort) et logguer ce qu'il extrait. Si le rendement chute,
vérifier les sélecteurs dans `_LISTING_SELECTORS`.

CLI:
    python -m sourcing.jiji --country BJ --category "beauty-salons-spa"
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import typer
from bs4 import BeautifulSoup
from rich.console import Console

from config import settings
from core.events import emit_action, emit_discovery, emit_error, emit_thought, set_state
from db.client import finish_sourcing_run, start_sourcing_run, upsert_prospect
from sourcing._http import polite_get

logger = logging.getLogger(__name__)
console = Console()


COUNTRY_DOMAINS = {
    "BJ": "jiji.bj",
    "TG": "jiji.tg",
    "CI": "jiji.ci",
    "SN": "jiji.sn",
    "BF": "jiji.bf",
    "NG": "jiji.ng",
    "GH": "jiji.com.gh",
}

# Catégories qui matchent les business NEBULA pourrait servir
DEFAULT_CATEGORIES = [
    "beauty-salons-spa",
    "restaurants-fast-food",
    "clothes-women",
    "shoes",
    "jewelry-watches",
    "wedding-events-services",
    "photography",
    "design-craftsmen",
]

# Sélecteurs à essayer dans l'ordre (Jiji change régulièrement)
_LISTING_SELECTORS = [
    "div.b-list-advert-base",
    "div.qa-advert-list-item",
    "a.qa-advert-list-item-link",
    "div[data-id]",
]
_TITLE_SELECTORS = ["div.b-advert-title-inner", "a.qa-advert-list-item-link", "h3"]
_PRICE_SELECTORS = ["div.qa-advert-price", "span.qa-advert-price"]
_LOCATION_SELECTORS = ["span.b-list-advert__region__text", "span.b-list-advert__region"]
_LINK_SELECTORS = ["a.qa-advert-list-item-link", "a[href*='/']"]


@dataclass
class JijiAd:
    external_id: str
    title: str
    url: str
    price: str | None
    location: str | None


def _find_listings(soup: BeautifulSoup):
    for sel in _LISTING_SELECTORS:
        items = soup.select(sel)
        if items:
            logger.debug("Sélecteur listing OK : %s (%d items)", sel, len(items))
            return items
    return []


def _first_text(node, selectors: list[str]) -> str | None:
    for sel in selectors:
        el = node.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None


def _first_href(node, selectors: list[str], base_url: str) -> str | None:
    for sel in selectors:
        el = node.select_one(sel)
        if el and el.get("href"):
            href = el["href"]
            if href.startswith("http"):
                return href
            return f"{base_url.rstrip('/')}{href}"
    return None


def parse_listing_page(html: str, base_url: str) -> list[JijiAd]:
    soup = BeautifulSoup(html, "lxml")
    ads: list[JijiAd] = []
    for node in _find_listings(soup):
        title = _first_text(node, _TITLE_SELECTORS)
        url = _first_href(node, _LINK_SELECTORS, base_url)
        if not title or not url:
            continue
        # external_id = dernier segment du slug avant query
        external_id = url.rstrip("/").split("/")[-1].split("?")[0]
        ads.append(JijiAd(
            external_id=external_id,
            title=title,
            url=url,
            price=_first_text(node, _PRICE_SELECTORS),
            location=_first_text(node, _LOCATION_SELECTORS),
        ))
    return ads


def scrape_category(country: str, category: str, max_pages: int = 3) -> int:
    """Scrape une catégorie Jiji pour un pays. Retourne le nombre d'insertions."""
    country = country.upper()
    domain = COUNTRY_DOMAINS.get(country)
    if not domain:
        raise ValueError(f"Pays non supporté Jiji : {country}")

    base_url = f"https://{domain}"
    run_id = start_sourcing_run("jiji", query=category, location=country)
    inserted = updated = skipped = found = 0

    set_state(status="sourcing", mood="focused",
              current_activity=f"J'explore Jiji {country} · {category}",
              current_target=f"{domain}/{category}")
    emit_action(f"Scan Jiji {country} · {category}", target=domain)

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}/{category}?page={page}"
            console.print(f"[cyan]🔍 Jiji {country} · {category} · page {page}[/cyan]")
            try:
                resp = polite_get(url)
            except Exception as e:
                logger.warning("GET fail %s : %s", url, e)
                break
            if resp.status_code != 200:
                logger.warning("HTTP %d pour %s", resp.status_code, url)
                break

            ads = parse_listing_page(resp.text, base_url)
            if not ads:
                logger.info("Aucune annonce extraite page %d (sélecteurs à revoir ?)", page)
                break

            found += len(ads)
            for ad in ads:
                payload = {
                    "source": "jiji",
                    "source_external_id": ad.external_id,
                    "name": ad.title,
                    "sector_normalized": _category_to_sector(category),
                    "country": country,
                    "city": ad.location,
                    "website": ad.url,  # lien Jiji en attendant le vrai site
                    "has_website": False,
                    "raw_json": {
                        "category": category,
                        "title": ad.title,
                        "price": ad.price,
                        "url": ad.url,
                        "location": ad.location,
                    },
                    "score": 7,  # un peu moins que Google Maps (moins de data)
                    "status": "new",
                }
                try:
                    row = upsert_prospect(payload)
                    inserted += 1
                    emit_discovery(
                        ad.title[:80],
                        prospect_id=(row or {}).get("id"),
                        city=ad.location,
                        sector=_category_to_sector(category),
                        no_website=True,
                    )
                    set_state(prospects_found_today=1)
                except Exception as e:
                    logger.warning("upsert fail : %s", e)
                    skipped += 1

        finish_sourcing_run(
            run_id, results_count=found, inserted_count=inserted,
            updated_count=updated, skipped_count=skipped,
        )
        emit_thought(
            f"Jiji {country} · {category} terminé",
            description=f"{inserted} annonces ajoutées sur {found} trouvées.",
        )
        set_state(status="idle", mood="serene", current_activity=None, current_target=None)
        return inserted

    except Exception as e:
        logger.exception("scrape_category failed : %s", e)
        finish_sourcing_run(run_id, status="failed", error_message=str(e))
        emit_error(f"Jiji {country}/{category} a échoué", description=str(e)[:200])
        set_state(status="error", mood="concerned")
        raise


def _category_to_sector(category: str) -> str | None:
    mapping = {
        "beauty-salons-spa": "beauty",
        "restaurants-fast-food": "restaurant",
        "clothes-women": "fashion",
        "shoes": "fashion",
        "jewelry-watches": "jewelry",
        "wedding-events-services": "events",
        "photography": "photography",
        "design-craftsmen": "creative",
    }
    return mapping.get(category)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
app = typer.Typer(add_completion=False, help="Scraper Jiji pour NEBULA.")


@app.command()
def scrape(
    country: str = typer.Option("BJ", "--country", "-C", help="Code pays (BJ, TG, CI, SN, BF)"),
    category: str = typer.Option(
        "beauty-salons-spa", "--category", "-c",
        help=f"Slug catégorie Jiji. Suggérées : {', '.join(DEFAULT_CATEGORIES)}",
    ),
    max_pages: int = typer.Option(3, "--pages", "-p", help="Nb max de pages à scraper"),
) -> None:
    logging.basicConfig(level=settings.log_level)
    n = scrape_category(country, category, max_pages=max_pages)
    console.print(f"[green]✓ {n} annonces insérées en base.[/green]")


@app.command()
def scrape_all(country: str = typer.Option("BJ", "--country", "-C")) -> None:
    """Scrape toutes les catégories par défaut pour un pays."""
    logging.basicConfig(level=settings.log_level)
    total = 0
    for cat in DEFAULT_CATEGORIES:
        try:
            total += scrape_category(country, cat, max_pages=2)
        except Exception as e:
            console.print(f"[red]✗ {cat} : {e}[/red]")
    console.print(f"[green]✓ Total {total} annonces insérées.[/green]")


if __name__ == "__main__":
    app()
