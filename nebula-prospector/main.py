"""NEBULA Prospector — orchestrateur CLI principal.

Usage:
    python main.py healthcheck                  # Vérifie config + connexions
    python main.py sourcing                     # Lance toutes les sources actives
    python main.py sourcing --country BJ        # Limite à un pays
    python main.py list-prospects --status new  # Liste les prospects
    python main.py stats                        # Stats globales pipeline
"""
from __future__ import annotations

import logging
from itertools import product

import typer
from rich.console import Console
from rich.table import Table

from config import settings
from db.client import (
    count_prospects_by_status,
    get_db,
    list_prospects,
)

app = typer.Typer(add_completion=False, help="NEBULA Prospector — agent IA de prospection.")
console = Console()


# ---------------------------------------------------------------------------
# Healthcheck
# ---------------------------------------------------------------------------

@app.command()
def healthcheck() -> None:
    """Vérifie config + connexions Supabase + clés API présentes."""
    logging.basicConfig(level=settings.log_level)

    table = Table(title="🩺 NEBULA Prospector — Healthcheck")
    table.add_column("Composant"); table.add_column("Statut"); table.add_column("Détail")

    # Supabase
    try:
        db = get_db()
        r = db.table("prospects").select("id", count="exact").limit(1).execute()
        table.add_row("Supabase", "[green]OK[/green]", f"{r.count or 0} prospects en base")
    except Exception as e:
        table.add_row("Supabase", "[red]FAIL[/red]", str(e)[:80])

    # Anthropic
    if settings.anthropic_api_key:
        table.add_row("Anthropic key", "[green]OK[/green]", f"...{settings.anthropic_api_key[-6:]}")
    else:
        table.add_row("Anthropic key", "[yellow]VIDE[/yellow]", "Requis vague 2+")

    # Google Maps
    if settings.google_maps_api_key:
        table.add_row("Google Maps key", "[green]OK[/green]", f"...{settings.google_maps_api_key[-6:]}")
    else:
        table.add_row("Google Maps key", "[dim]vide[/dim]", "Optionnel — OSM utilisé à la place (gratuit)")

    # OpenStreetMap (toujours dispo)
    table.add_row("OpenStreetMap", "[green]OK[/green]", "Gratuit, aucune clé requise")

    # Vagues suivantes
    for label, key in [
        ("Hunter (vague 2)", settings.hunter_api_key),
        ("Resend (vague 3)", settings.resend_api_key),
        ("IMAP (vague 4)", settings.imap_password),
        ("Telegram (vague 5)", settings.telegram_bot_token),
    ]:
        status = "[green]OK[/green]" if key else "[dim]vide[/dim]"
        table.add_row(label, status, "")

    table.add_row("Pays cibles", "", ", ".join(settings.target_countries_list))
    table.add_row("Villes cibles", "", ", ".join(settings.target_cities_list))

    console.print(table)


# ---------------------------------------------------------------------------
# Sourcing
# ---------------------------------------------------------------------------

@app.command()
def sourcing(
    country: str | None = typer.Option(None, "--country", "-C", help="Code pays (ex: BJ). Sinon tous."),
    osm_only: bool = typer.Option(False, "--osm-only", help="OSM uniquement (gratuit)"),
    google_only: bool = typer.Option(False, "--google-only"),
    jiji_only: bool = typer.Option(False, "--jiji-only"),
    coinafrique_only: bool = typer.Option(False, "--coinafrique-only"),
) -> None:
    """Lance toutes les sources actives (OpenStreetMap + Google Maps si clé + Jiji + CoinAfrique).

    Si GOOGLE_MAPS_API_KEY est vide → Google Maps est skip automatiquement.
    OSM est gratuit et ne demande aucune clé.
    """
    logging.basicConfig(level=settings.log_level)

    countries = [country.upper()] if country else settings.target_countries_list
    only_flags = [osm_only, google_only, jiji_only, coinafrique_only]
    any_only = any(only_flags)

    run_osm = osm_only or not any_only
    run_google = (google_only or not any_only) and bool(settings.google_maps_api_key)
    run_jiji = jiji_only or not any_only
    run_coin = coinafrique_only or not any_only

    cities_to_use = settings.target_cities_list
    if country:
        from sourcing.openstreetmap import CITY_TO_COUNTRY as OSM_CITY
        cities_to_use = [c for c in cities_to_use
                         if OSM_CITY.get(c.lower()) == country.upper()]

    # --- OpenStreetMap (gratuit, prioritaire) ---
    if run_osm:
        from sourcing.openstreetmap import search_city_all as osm_search_all
        for city in cities_to_use:
            try:
                osm_search_all(city)
            except Exception as e:
                console.print(f"[red]✗ OSM {city} : {e}[/red]")

    # --- Google Maps (skip si pas de clé) ---
    if run_google:
        from sourcing.google_maps import search_businesses
        google_queries = [
            "salon de beauté", "institut de beauté", "boutique mode",
            "restaurant", "boutique bijoux", "photographe mariage",
        ]
        for city, query in product(cities_to_use, google_queries):
            try:
                search_businesses(query, city, max_results=20)
            except Exception as e:
                console.print(f"[red]✗ Google Maps {city}/{query} : {e}[/red]")
    elif google_only:
        console.print("[yellow]⚠ GOOGLE_MAPS_API_KEY vide, Google Maps skip.[/yellow]")

    # --- Jiji ---
    if run_jiji:
        from sourcing.jiji import DEFAULT_CATEGORIES as JIJI_CATS, scrape_category as jiji_scrape
        for c, cat in product(countries, JIJI_CATS):
            try:
                jiji_scrape(c, cat, max_pages=2)
            except Exception as e:
                console.print(f"[red]✗ Jiji {c}/{cat} : {e}[/red]")

    # --- CoinAfrique ---
    if run_coin:
        from sourcing.coinafrique import DEFAULT_CATEGORIES as COIN_CATS, scrape_category as coin_scrape
        for c, cat in product(countries, COIN_CATS):
            try:
                coin_scrape(c, cat, max_pages=2)
            except Exception as e:
                console.print(f"[red]✗ CoinAfrique {c}/{cat} : {e}[/red]")

    console.print("\n[bold green]✓ Sourcing terminé.[/bold green]")
    stats()


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

@app.command("list-prospects")
def list_prospects_cmd(
    status: str | None = typer.Option(None, "--status", "-s"),
    limit: int = typer.Option(20, "--limit", "-l"),
) -> None:
    """Liste les prospects (triés par score décroissant)."""
    prospects = list_prospects(status=status, limit=limit)
    table = Table(title=f"Prospects (status={status or 'all'})")
    for col in ("Score", "Source", "Nom", "Secteur", "Ville", "Site", "Email", "Statut"):
        table.add_column(col)
    for p in prospects:
        table.add_row(
            str(p.get("score") or 0),
            (p.get("source") or "")[:8],
            (p.get("name") or "")[:35],
            (p.get("sector_normalized") or "—")[:12],
            (p.get("city") or "—")[:12],
            "oui" if p.get("has_website") else "[red]NON[/red]",
            (p.get("email") or "—")[:25],
            p.get("status") or "",
        )
    console.print(table)


@app.command()
def stats() -> None:
    """Affiche les compteurs par statut + dernières runs de sourcing."""
    counts = count_prospects_by_status()
    total = sum(counts.values())

    table = Table(title=f"📊 Pipeline ({total} prospects au total)")
    table.add_column("Statut"); table.add_column("Compte", justify="right")
    for status in ("new", "enriched", "scored", "contacted", "replied",
                   "engaged", "ready_to_pay", "won", "lost", "blacklisted"):
        n = counts.get(status, 0)
        color = "green" if status in ("ready_to_pay", "won") else "white"
        table.add_row(status, f"[{color}]{n}[/{color}]")
    console.print(table)

    # Dernières runs
    db = get_db()
    runs = (
        db.table("sourcing_runs")
        .select("*")
        .order("started_at", desc=True)
        .limit(8)
        .execute()
        .data
        or []
    )
    if runs:
        rt = Table(title="Dernières runs de sourcing")
        for col in ("Quand", "Source", "Query", "Trouvés", "Insérés", "Statut"):
            rt.add_column(col)
        for r in runs:
            rt.add_row(
                (r.get("started_at") or "")[:19],
                r.get("source") or "",
                (r.get("query") or "")[:30],
                str(r.get("results_count") or 0),
                str(r.get("inserted_count") or 0),
                r.get("status") or "",
            )
        console.print(rt)


if __name__ == "__main__":
    app()
