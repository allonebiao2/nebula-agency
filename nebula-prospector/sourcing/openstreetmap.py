"""Sourcing via OpenStreetMap (Overpass API).

100 % gratuit, aucun compte ni clé API. Bonne couverture sur les
capitales d'Afrique de l'Ouest francophone (Cotonou, Lomé, Abidjan,
Dakar, Ouagadougou) — moins riche que Google Maps en zones rurales.

Respect du serveur Overpass : 1 requête lourde toutes les ~5 secondes,
timeout 90s, retry exponential.

CLI:
    python -m sourcing.openstreetmap --city Cotonou
    python -m sourcing.openstreetmap --city Lomé --category beauty
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx
import typer
from rich.console import Console
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from core.events import (
    emit_action,
    emit_discovery,
    emit_error,
    emit_thought,
    set_state,
)
from db.client import (
    finish_sourcing_run,
    get_prospect_by_external,
    start_sourcing_run,
    upsert_prospect,
)
from sourcing._http import USER_AGENT

logger = logging.getLogger(__name__)
console = Console()


# Serveurs Overpass (mirroring fallback)
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]


# ---------------------------------------------------------------------------
# Mapping de catégories NEBULA → filtre Overpass
# ---------------------------------------------------------------------------
CATEGORIES = {
    "beauty": {
        "label": "Beauté · cosmétique · coiffure",
        "filter": '[shop~"^(beauty|hairdresser|cosmetics|tattoo|massage|perfumery)$"]',
        "sector": "beauty",
    },
    "fashion": {
        "label": "Mode · vêtements · chaussures · bijoux",
        "filter": '[shop~"^(clothes|shoes|jewelry|watches|bag|fashion_accessories)$"]',
        "sector": "fashion",
    },
    "restaurant": {
        "label": "Restauration · bars · cafés",
        "filter": '[amenity~"^(restaurant|cafe|bar|fast_food|food_court|biergarten)$"]',
        "sector": "restaurant",
    },
    "bakery": {
        "label": "Boulangeries · pâtisseries",
        "filter": '[shop~"^(bakery|pastry|confectionery)$"]',
        "sector": "restaurant",
    },
    "health": {
        "label": "Santé · pharmacies · cliniques",
        "filter": '[amenity~"^(pharmacy|clinic|doctors|dentist|veterinary)$"]',
        "sector": "health",
    },
    "hospitality": {
        "label": "Hôtels · maisons d'hôtes",
        "filter": '[tourism~"^(hotel|guest_house|hostel|motel|apartment)$"]',
        "sector": "hospitality",
    },
    "office": {
        "label": "Bureaux professionnels (avocats, comptables, conseil)",
        "filter": '[office]',
        "sector": "professional_services",
    },
    "retail": {
        "label": "Boutiques générales",
        "filter": '[shop~"^(supermarket|mobile_phone|electronics|optician|stationery|toys|sports|pet|florist|gift|furniture)$"]',
        "sector": "retail",
    },
    "automotive": {
        "label": "Garages · concessionnaires · auto-écoles",
        "filter": '[shop~"^(car|car_repair|car_parts|motorcycle|bicycle)$"]',
        "sector": "automotive",
    },
    "events": {
        "label": "Événementiel · photographie",
        "filter": '[craft~"^(photographer|event)$"]',
        "sector": "events",
    },
}

CITY_TO_COUNTRY = {
    "cotonou": "BJ", "porto-novo": "BJ", "parakou": "BJ", "abomey": "BJ",
    "lomé": "TG", "lome": "TG", "kpalimé": "TG",
    "abidjan": "CI", "yamoussoukro": "CI", "bouaké": "CI", "bouake": "CI",
    "dakar": "SN", "thiès": "SN", "thies": "SN", "saint-louis": "SN",
    "ouagadougou": "BF", "bobo-dioulasso": "BF",
}


@dataclass
class OsmStats:
    found: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0


# ---------------------------------------------------------------------------
# Overpass query builder
# ---------------------------------------------------------------------------
def build_query(city: str, category_filter: str, timeout: int = 90) -> str:
    """Construit une requête Overpass QL pour une catégorie dans une ville."""
    return f"""
[out:json][timeout:{timeout}];
area["name"~"^{city}$",i]->.searchArea;
(
  nwr{category_filter}(area.searchArea);
);
out center tags;
""".strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=5, max=60))
def overpass_query(query: str) -> dict[str, Any]:
    """Exécute une requête Overpass avec rotation des endpoints."""
    last_err: Exception | None = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            logger.debug("Overpass POST → %s", endpoint)
            resp = httpx.post(
                endpoint,
                data={"data": query},
                headers={"User-Agent": USER_AGENT},
                timeout=120.0,
            )
            if resp.status_code == 429:
                logger.warning("Overpass rate limit (%s), retrying next endpoint", endpoint)
                time.sleep(5)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_err = e
            logger.warning("Overpass endpoint failed (%s) : %s", endpoint, e)
    if last_err:
        raise last_err
    raise RuntimeError("Tous les endpoints Overpass ont échoué")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
def extract_coord(elem: dict[str, Any]) -> tuple[float | None, float | None]:
    if "lat" in elem and "lon" in elem:
        return elem["lat"], elem["lon"]
    center = elem.get("center") or {}
    return center.get("lat"), center.get("lon")


def build_prospect_payload(
    elem: dict[str, Any],
    *,
    city: str,
    country: str | None,
    sector_normalized: str | None,
) -> dict[str, Any] | None:
    tags = elem.get("tags") or {}
    name = tags.get("name") or tags.get("name:fr")
    if not name:
        return None  # Pas de nom → inutile

    osm_type = elem.get("type")
    osm_id = elem.get("id")
    if not osm_type or osm_id is None:
        return None
    external_id = f"{osm_type}/{osm_id}"

    lat, lng = extract_coord(elem)
    website = tags.get("website") or tags.get("contact:website")
    phone = tags.get("phone") or tags.get("contact:phone")
    email = tags.get("email") or tags.get("contact:email")

    # Score initial : pas de site = 10, sinon 3
    initial_score = 10 if not website else 3
    if email:                       initial_score += 2
    if phone:                       initial_score += 1
    if tags.get("opening_hours"):   initial_score += 1   # business actif

    address_parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb") or tags.get("addr:district"),
        tags.get("addr:city") or city,
    ]
    address = " ".join(p for p in address_parts if p)

    facebook = tags.get("contact:facebook")
    instagram = tags.get("contact:instagram")

    sector_full = ", ".join(
        f"{k}={v}" for k, v in tags.items()
        if k in ("amenity", "shop", "tourism", "office", "craft")
    ) or None

    return {
        "source": "openstreetmap",
        "source_external_id": external_id,
        "name": name[:200],
        "sector": sector_full,
        "sector_normalized": sector_normalized,
        "country": country,
        "city": city,
        "address": address or None,
        "lat": lat,
        "lng": lng,
        "website": website,
        "has_website": bool(website),
        "phone": phone,
        "email": email,
        "facebook_url": facebook,
        "instagram_url": instagram,
        "raw_json": elem,
        "score": initial_score,
        "status": "new",
    }


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def search_city_category(
    city: str,
    category_key: str,
    *,
    country_hint: str | None = None,
) -> OsmStats:
    """Cherche tous les businesses d'une catégorie dans une ville via OSM."""
    cat = CATEGORIES.get(category_key)
    if not cat:
        raise ValueError(f"Catégorie inconnue : {category_key}. Dispos : {list(CATEGORIES)}")

    stats = OsmStats()
    country = (country_hint or CITY_TO_COUNTRY.get(city.lower(), "")).upper() or None

    run_id = start_sourcing_run("openstreetmap", query=category_key, location=city)
    console.print(f"[cyan]🌍 OSM · {city} · {cat['label']}[/cyan]")

    set_state(status="sourcing", mood="focused",
              current_activity=f"J'explore {city} via OpenStreetMap ({cat['label']})...",
              current_target=f"{city} · {category_key}")
    emit_action(f"Scan OSM : {city} · {cat['label']}", target=city)

    try:
        query = build_query(city, cat["filter"])
        result = overpass_query(query)
        elements = result.get("elements", [])
        stats.found = len(elements)
        console.print(f"   → {stats.found} élément(s) trouvé(s) sur OSM")

        for elem in elements:
            payload = build_prospect_payload(
                elem, city=city, country=country,
                sector_normalized=cat["sector"],
            )
            if not payload:
                stats.skipped += 1
                continue

            existing = get_prospect_by_external(
                "openstreetmap", payload["source_external_id"]
            )

            try:
                row = upsert_prospect(payload)
                if existing:
                    stats.updated += 1
                else:
                    stats.inserted += 1
                    console.print(
                        f"   ✓ [green]NEW[/green] {payload['name']} "
                        f"[dim]({cat['sector']} · "
                        f"site={'oui' if payload['has_website'] else 'NON'})[/dim]"
                    )
                    emit_discovery(
                        payload["name"],
                        prospect_id=(row or {}).get("id"),
                        city=city,
                        sector=cat["sector"],
                        no_website=not payload["has_website"],
                    )
                    set_state(prospects_found_today=1)
            except Exception as e:
                logger.warning("upsert fail (%s) : %s", payload.get("name"), e)
                stats.skipped += 1

        finish_sourcing_run(
            run_id,
            results_count=stats.found,
            inserted_count=stats.inserted,
            updated_count=stats.updated,
            skipped_count=stats.skipped,
        )
        emit_thought(
            f"OSM {city} · {cat['label']} terminé",
            description=(f"{stats.inserted} nouveaux, {stats.updated} mis à jour, "
                         f"sur {stats.found} résultats."),
        )
        set_state(status="idle", mood="serene",
                  current_activity=None, current_target=None)

    except Exception as e:
        logger.exception("OSM sourcing failed : %s", e)
        finish_sourcing_run(run_id, status="failed", error_message=str(e))
        emit_error(f"OSM {city}/{category_key} échoué", description=str(e)[:200])
        set_state(status="error", mood="concerned")
        raise

    return stats


def search_city_all(city: str, country_hint: str | None = None) -> OsmStats:
    """Lance toutes les catégories pour une ville. Total cumulé."""
    total = OsmStats()
    for cat_key in CATEGORIES:
        try:
            s = search_city_category(city, cat_key, country_hint=country_hint)
            total.found += s.found
            total.inserted += s.inserted
            total.updated += s.updated
            total.skipped += s.skipped
        except Exception as e:
            console.print(f"[red]✗ {city}/{cat_key} : {e}[/red]")
        # Respect du serveur Overpass : pause entre 2 grosses requêtes
        time.sleep(3)
    return total


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
app = typer.Typer(add_completion=False, help="Sourcing OpenStreetMap (gratuit) pour NEBULA.")


@app.command()
def search(
    city: str = typer.Option(..., "--city", "-c", help='Ville (ex: "Cotonou")'),
    category: str = typer.Option(
        "beauty", "--category", "-k",
        help=f"Catégorie. Dispos : {', '.join(CATEGORIES)}",
    ),
    country: str | None = typer.Option(None, "--country", help="Code ISO 2 (BJ, TG, CI...)"),
) -> None:
    """Cherche une catégorie dans une ville via OpenStreetMap."""
    logging.basicConfig(level=settings.log_level)
    stats = search_city_category(city, category, country_hint=country)

    table = Table(title=f"OSM · {city} · {category}")
    table.add_column("Métrique"); table.add_column("Valeur", justify="right")
    table.add_row("Trouvés OSM",     str(stats.found))
    table.add_row("Nouveaux insérés", f"[green]{stats.inserted}[/green]")
    table.add_row("Mis à jour",       str(stats.updated))
    table.add_row("Ignorés",          str(stats.skipped))
    console.print(table)


@app.command("search-all")
def search_all_cmd(
    city: str = typer.Option(..., "--city", "-c"),
    country: str | None = typer.Option(None, "--country"),
) -> None:
    """Lance TOUTES les catégories pour une ville."""
    logging.basicConfig(level=settings.log_level)
    stats = search_city_all(city, country_hint=country)
    console.print(f"\n[bold green]✓ {stats.inserted} nouveaux prospects "
                  f"sur {stats.found} trouvés sur OSM dans {city}.[/bold green]")


@app.command("list-categories")
def list_categories() -> None:
    table = Table(title="Catégories OSM disponibles")
    table.add_column("Clé"); table.add_column("Label"); table.add_column("Secteur")
    for k, v in CATEGORIES.items():
        table.add_row(k, v["label"], v["sector"])
    console.print(table)


if __name__ == "__main__":
    app()
