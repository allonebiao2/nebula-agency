"""Intelligence collective entre boutiques — le moat de Vendora.

Plus il y a de boutiques, meilleur devient chaque agent : on agrège des repères
ANONYMISÉS par secteur (ventes/CA moyens) et on les réinjecte (ex : dans le coach
commercial) pour situer une boutique vs ses pairs. Aucune donnée nominative n'est
exposée — uniquement des moyennes de secteur.

Dormant tant qu'il n'y a pas assez de boutiques par secteur (min_peers) → renvoie
une ligne vide, et s'active tout seul quand le réseau grandit.
"""
from __future__ import annotations

import logging

log = logging.getLogger("boutique-ia.collective")


def _sector_key(merchant: dict) -> str:
    return (merchant.get("sector") or "").strip().lower()


def _fmt(n) -> str:
    return f"{int(n):,}".replace(",", " ")


def benchmark_for(merchant: dict, min_peers: int = 3, cap: int = 40) -> str:
    """Repère anonymisé du secteur (ventes/CA moyens) vs la boutique. '' si trop peu de pairs.

    `min_peers` garantit l'anonymat + un signal réel (jamais sur 1-2 boutiques).
    """
    sec = _sector_key(merchant)
    if not sec:
        return ""
    try:
        from db.client import list_all_merchants, order_stats
        peers = [m for m in (list_all_merchants() or [])
                 if _sector_key(m) == sec and m.get("id") != merchant.get("id")][:cap]
        if len(peers) < min_peers:
            return ""
        sales, revs = [], []
        for m in peers:
            st = order_stats(m["id"]) or {}
            sales.append(st.get("count", 0) or 0)
            revs.append(st.get("revenue", 0) or 0)
        avg_sales = round(sum(sales) / len(sales), 1)
        avg_rev = sum(revs) / len(revs)
        return (f"Repère secteur « {sec} » ({len(peers)} boutiques) : en moyenne "
                f"{avg_sales} ventes et {_fmt(avg_rev)} F/mois.")
    except Exception:  # noqa: BLE001
        log.warning("benchmark secteur KO", exc_info=True)
        return ""
