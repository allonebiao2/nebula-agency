"""Sourcing via Google Maps Places API.

Trouve des PME dans une ville donnée, récupère leurs détails (site web,
téléphone), et les insère dans Supabase. Les PME SANS site web sont
prioritaires (score plus élevé).

CLI:
    python -m sourcing.google_maps --query "salon de beauté" --city Cotonou
    python -m sourcing.google_maps --query "restaurant" --city Lomé --max 30
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import googlemaps
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

logger = logging.getLogger(__name__)
console = Console()


# ---------------------------------------------------------------------------
# Mapping pays / langue / code ISO 2
# ---------------------------------------------------------------------------
CITY_TO_COUNTRY = {
    "cotonou": "BJ",
    "porto-novo": "BJ",
    "parakou": "BJ",
    "abomey": "BJ",
    "lomé": "TG",
    "lome": "TG",
    "abidjan": "CI",
    "yamoussoukro": "CI",
    "bouaké": "CI",
    "dakar": "SN",
    "thiès": "SN",
    "thies": "SN",
    "ouagadougou": "BF",
    "bobo-dioulasso": "BF",
}

# Mapping types Google → secteur normalisé NEBULA
TYPE_TO_SECTOR = {
    "beauty_salon": "beauty",
    "hair_care": "beauty",
    "spa": "beauty",
    "restaurant": "restaurant",
    "cafe": "restaurant",
    "bakery": "restaurant",
    "meal_takeaway": "restaurant",
    "meal_delivery": "restaurant",
    "clothing_store": "fashion",
    "shoe_store": "fashion",
    "jewelry_store": "jewelry",
    "real_estate_agency": "real_estate",
    "lawyer": "professional_services",
    "accounting": "professional_services",
    "doctor": "health",
    "dentist": "health",
    "pharmacy": "health",
    "gym": "fitness",
    "school": "education",
    "store": "retail",
    "car_repair": "automotive",
    "car_dealer": "automotive",
    "lodging": "hospitality",
    "travel_agency": "travel",
}


@dataclass
class SourcingStats:
    found: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0


def normalize_sector(types: list[str] | None) -> str | None:
    if not types:
        return None
    for t in types:
        if t in TYPE_TO_SECTOR:
            return TYPE_TO_SECTOR[t]
    return None


def infer_country(city: str, country_hint: str | None = None) -> str | None:
    if country_hint:
        return country_hint.upper()
    return CITY_TO_COUNTRY.get(city.strip().lower())


# ---------------------------------------------------------------------------
# Client Google Maps
# ---------------------------------------------------------------------------

def _client() -> googlemaps.Client:
    settings.require("google_maps_api_key")
    return googlemaps.Client(key=settings.google_maps_api_key)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
def _text_search(gmaps: googlemaps.Client, query: str, **kwargs) -> dict[str, Any]:
    return gmaps.places(query=query, **kwargs)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
def _place_details(gmaps: googlemaps.Client, place_id: str) -> dict[str, Any]:
    return gmaps.place(
        place_id=place_id,
        fields=[
            "place_id", "name", "formatted_address", "geometry/location",
            "international_phone_number", "website", "business_status",
            "type", "url", "rating", "user_ratings_total",
        ],
        language="fr",
    )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def search_businesses(
    query: str,
    city: str,
    country_hint: str | None = None,
    max_results: int = 60,
) -> SourcingStats:
    """Cherche, enrichit et stocke les PME pour une requête + ville.

    Args:
        query: Type de business ("salon de beauté", "restaurant", "boutique mode")
        city: Ville cible (ex: "Cotonou")
        country_hint: Override le mapping CITY_TO_COUNTRY (ex: "BJ")
        max_results: Plafond (Google rend ~60 max par requête Text Search)
    """
    gmaps = _client()
    stats = SourcingStats()
    country = infer_country(city, country_hint)
    full_query = f"{query} {city}"

    run_id = start_sourcing_run("google_maps", query=full_query, location=city)
    console.print(f"[cyan]🔍 Google Maps · {full_query}[/cyan]")

    set_state(status="sourcing", mood="focused",
              current_activity=f"Je scanne {city} via Google Maps...",
              current_target=full_query)
    emit_action(f"Recherche : {full_query}", target=city)

    try:
        results: list[dict[str, Any]] = []
        response = _text_search(gmaps, full_query, language="fr", region=country.lower() if country else None)
        results.extend(response.get("results", []))

        # Pagination (max 3 pages → 60 résultats)
        page_token = response.get("next_page_token")
        while page_token and len(results) < max_results:
            time.sleep(2.5)  # next_page_token requiert un délai
            response = _text_search(gmaps, full_query, page_token=page_token)
            results.extend(response.get("results", []))
            page_token = response.get("next_page_token")

        results = results[:max_results]
        stats.found = len(results)
        console.print(f"   → {stats.found} résultat(s) trouvé(s) en search")

        for raw in results:
            place_id = raw.get("place_id")
            if not place_id:
                stats.skipped += 1
                continue

            existing = get_prospect_by_external("google_maps", place_id)

            # Toujours rafraîchir les détails (website peut être ajouté plus tard)
            try:
                details_resp = _place_details(gmaps, place_id)
                details = details_resp.get("result", {})
            except Exception as e:
                logger.warning("place_details failed pour %s : %s", place_id, e)
                details = {}

            payload = _build_prospect_payload(raw, details, city=city, country=country)

            try:
                row = upsert_prospect(payload)
                if existing:
                    stats.updated += 1
                else:
                    stats.inserted += 1
                    console.print(
                        f"   ✓ [green]NEW[/green] {payload['name']} "
                        f"[dim]({payload.get('sector_normalized') or 'unknown'} · "
                        f"site={'oui' if payload.get('has_website') else 'NON'})[/dim]"
                    )
                    emit_discovery(
                        payload["name"],
                        prospect_id=(row or {}).get("id"),
                        city=city,
                        sector=payload.get("sector_normalized"),
                        no_website=not payload.get("has_website"),
                    )
                    set_state(prospects_found_today=1, bump_heartbeat=True)
            except Exception as e:
                logger.exception("upsert failed pour %s : %s", payload.get("name"), e)
                stats.skipped += 1

        finish_sourcing_run(
            run_id,
            results_count=stats.found,
            inserted_count=stats.inserted,
            updated_count=stats.updated,
            skipped_count=stats.skipped,
        )

        emit_thought(
            f"Scan terminé : {full_query}",
            description=(f"{stats.inserted} nouveaux prospects, "
                         f"{stats.updated} mis à jour, "
                         f"sur {stats.found} résultats."),
        )
        set_state(status="idle", mood="serene",
                  current_activity=None, current_target=None)

    except Exception as e:
        logger.exception("sourcing failed : %s", e)
        finish_sourcing_run(run_id, status="failed", error_message=str(e))
        emit_error(f"Sourcing échoué : {full_query}", description=str(e)[:200])
        set_state(status="error", mood="concerned",
                  current_activity=f"Erreur sur {full_query}")
        raise

    return stats


def _build_prospect_payload(
    raw: dict[str, Any],
    details: dict[str, Any],
    *,
    city: str,
    country: str | None,
) -> dict[str, Any]:
    """Fusionne les données text-search + place-details en un payload prospect."""
    merged = {**raw, **details}
    types = merged.get("types") or []
    website = merged.get("website")
    geom = merged.get("geometry", {}).get("location") or {}

    # Score initial : pas de site = 10, sinon 3 (on cible ceux SANS site)
    initial_score = 10 if not website else 3
    # Bonus si highly-rated et actif
    if (merged.get("user_ratings_total") or 0) >= 20:
        initial_score += 2
    if merged.get("business_status") == "OPERATIONAL":
        initial_score += 1

    return {
        "source": "google_maps",
        "source_external_id": merged["place_id"],
        "name": merged.get("name", "(sans nom)"),
        "sector": ", ".join(types[:3]) if types else None,
        "sector_normalized": normalize_sector(types),
        "country": country,
        "city": city,
        "address": merged.get("formatted_address") or merged.get("vicinity"),
        "lat": geom.get("lat"),
        "lng": geom.get("lng"),
        "website": website,
        "has_website": bool(website),
        "phone": merged.get("international_phone_number"),
        "raw_json": merged,
        "score": initial_score,
        "status": "new",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

app = typer.Typer(add_completion=False, help="Sourcing Google Maps pour NEBULA.")


@app.command()
def search(
    query: str = typer.Option(..., "--query", "-q", help='Type de business (ex: "salon de beauté")'),
    city: str = typer.Option(..., "--city", "-c", help='Ville (ex: "Cotonou")'),
    country: str | None = typer.Option(None, "--country", help="Code ISO 2 (BJ, TG, CI...)"),
    max_results: int = typer.Option(60, "--max", "-m", help="Plafond résultats (max ~60)"),
) -> None:
    """Cherche des PME via Google Maps et les stocke en base."""
    logging.basicConfig(level=settings.log_level)
    stats = search_businesses(query, city, country_hint=country, max_results=max_results)

    table = Table(title="Résultats sourcing")
    table.add_column("Métrique"); table.add_column("Valeur", justify="right")
    table.add_row("Trouvés (search)",  str(stats.found))
    table.add_row("Nouveaux insérés", f"[green]{stats.inserted}[/green]")
    table.add_row("Mis à jour",        str(stats.updated))
    table.add_row("Ignorés",           str(stats.skipped))
    console.print(table)


if __name__ == "__main__":
    app()
