"""Scraper CoinAfrique (services + PME, multi-pays).

CoinAfrique a des sous-domaines par pays :
- bj.coinafrique.com  (Bénin)
- tg.coinafrique.com  (Togo)
- ci.coinafrique.com  (Côte d'Ivoire)
- sn.coinafrique.com  (Sénégal)
- bf.coinafrique.com  (Burkina)

⚠️  Comme Jiji, les sélecteurs CSS peuvent changer. Le code est best-effort.

CLI:
    python -m sourcing.coinafrique --country BJ --category beaute-soins
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import typer
from bs4 import BeautifulSoup
from rich.console import Console

from config import settings
from db.client import finish_sourcing_run, start_sourcing_run, upsert_prospect
from sourcing._http import polite_get

logger = logging.getLogger(__name__)
console = Console()


COUNTRY_SUBDOMAINS = {
    "BJ": "bj",
    "TG": "tg",
    "CI": "ci",
    "SN": "sn",
    "BF": "bf",
}

DEFAULT_CATEGORIES = [
    "beaute-soins",
    "mode-femmes",
    "mode-hommes",
    "bijoux-montres",
    "evenements-services",
    "services",
    "restauration",
]

_LISTING_SELECTORS = [
    "div.card-product-list",
    "div.ad__card",
    "div[data-product]",
    "a.card-product-list__link",
]
_TITLE_SELECTORS = ["p.ad__card-description", "h5", "h3", "a"]
_PRICE_SELECTORS = ["p.ad__card-price", "span.price"]
_LOCATION_SELECTORS = ["p.ad__card-location span", "p.ad__card-location"]


@dataclass
class CoinAd:
    external_id: str
    title: str
    url: str
    price: str | None
    location: str | None


def _find_listings(soup: BeautifulSoup):
    for sel in _LISTING_SELECTORS:
        items = soup.select(sel)
        if items:
            return items
    return []


def _first_text(node, selectors: list[str]) -> str | None:
    for sel in selectors:
        el = node.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None


def parse_listing_page(html: str, base_url: str) -> list[CoinAd]:
    soup = BeautifulSoup(html, "lxml")
    ads: list[CoinAd] = []
    for node in _find_listings(soup):
        title = _first_text(node, _TITLE_SELECTORS)
        link_el = node.select_one("a[href]")
        if not title or not link_el:
            continue
        href = link_el["href"]
        url = href if href.startswith("http") else f"{base_url.rstrip('/')}{href}"
        external_id = url.rstrip("/").split("/")[-1].split("?")[0]
        ads.append(CoinAd(
            external_id=external_id,
            title=title,
            url=url,
            price=_first_text(node, _PRICE_SELECTORS),
            location=_first_text(node, _LOCATION_SELECTORS),
        ))
    return ads


def scrape_category(country: str, category: str, max_pages: int = 3) -> int:
    country = country.upper()
    sub = COUNTRY_SUBDOMAINS.get(country)
    if not sub:
        raise ValueError(f"Pays non supporté CoinAfrique : {country}")

    base_url = f"https://{sub}.coinafrique.com"
    run_id = start_sourcing_run("coinafrique", query=category, location=country)
    inserted = updated = skipped = found = 0

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}/categorie/{category}?page={page}"
            console.print(f"[cyan]🔍 CoinAfrique {country} · {category} · page {page}[/cyan]")
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
                logger.info("Aucune annonce extraite page %d", page)
                break

            found += len(ads)
            for ad in ads:
                payload = {
                    "source": "coinafrique",
                    "source_external_id": ad.external_id,
                    "name": ad.title[:200],
                    "country": country,
                    "city": ad.location,
                    "website": ad.url,
                    "has_website": False,
                    "raw_json": {
                        "category": category,
                        "title": ad.title,
                        "price": ad.price,
                        "url": ad.url,
                        "location": ad.location,
                    },
                    "score": 6,
                    "status": "new",
                }
                try:
                    upsert_prospect(payload)
                    inserted += 1
                except Exception as e:
                    logger.warning("upsert fail : %s", e)
                    skipped += 1

        finish_sourcing_run(
            run_id, results_count=found, inserted_count=inserted,
            updated_count=updated, skipped_count=skipped,
        )
        return inserted

    except Exception as e:
        logger.exception("scrape_category failed : %s", e)
        finish_sourcing_run(run_id, status="failed", error_message=str(e))
        raise


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
app = typer.Typer(add_completion=False, help="Scraper CoinAfrique pour NEBULA.")


@app.command()
def scrape(
    country: str = typer.Option("BJ", "--country", "-C"),
    category: str = typer.Option("beaute-soins", "--category", "-c"),
    max_pages: int = typer.Option(3, "--pages", "-p"),
) -> None:
    logging.basicConfig(level=settings.log_level)
    n = scrape_category(country, category, max_pages=max_pages)
    console.print(f"[green]✓ {n} annonces insérées en base.[/green]")


@app.command()
def scrape_all(country: str = typer.Option("BJ", "--country", "-C")) -> None:
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
