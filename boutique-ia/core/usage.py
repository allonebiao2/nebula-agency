"""Mesure du COÛT IA (F3) — télémétrie des appels modèle.

Enregistre, pour chaque réponse Anthropic : tokens d'entrée / de sortie / de cache
(lecture & écriture) + coût estimé en USD, par TÂCHE et par BOUTIQUE. Sert à répondre
à « quelle boutique coûte le plus », « le cache tourne-t-il », « Démarrage est-il
rentable ». C'est ce qui rend visible l'efficacité du cache (cf. F1).

RÈGLE ABSOLUE : ne JAMAIS lever. La télémétrie ne doit jamais bloquer une réponse
client. Tout est encapsulé dans des try/except ; sans la table `bia_usage` (migration
non encore appliquée), on ignore silencieusement.
"""
from __future__ import annotations

import logging

log = logging.getLogger("boutique-ia.usage")

# Prix par MILLION de tokens (USD), vérifiés juin 2026 : (entrée, sortie).
# Cache : lecture ≈ 0,1× le prix d'entrée ; écriture ≈ 1,25× le prix d'entrée.
PRICES: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
}
_DEFAULT = (3.0, 15.0)  # repli prudent = tarif Sonnet


def _price(model: str) -> tuple[float, float]:
    return PRICES.get(model or "", _DEFAULT)


def cost_usd(model: str, in_tok: int, out_tok: int,
             cache_read: int, cache_write: int) -> float:
    """Coût estimé d'un appel (USD), cache compris."""
    pin, pout = _price(model)
    return (
        (in_tok * pin)
        + (cache_write * pin * 1.25)
        + (cache_read * pin * 0.1)
        + (out_tok * pout)
    ) / 1_000_000


def track(task: str, model: str, resp, merchant_id: str | None = None) -> None:
    """Enregistre l'usage d'UNE réponse Anthropic. Ne lève jamais."""
    try:
        u = getattr(resp, "usage", None)
        if u is None:
            return
        in_tok = int(getattr(u, "input_tokens", 0) or 0)
        out_tok = int(getattr(u, "output_tokens", 0) or 0)
        cr = int(getattr(u, "cache_read_input_tokens", 0) or 0)
        cw = int(getattr(u, "cache_creation_input_tokens", 0) or 0)
        c = cost_usd(model, in_tok, out_tok, cr, cw)
        from db.client import record_usage
        record_usage(merchant_id, task, model, in_tok, out_tok, cr, cw, c)
    except Exception:  # noqa: BLE001
        log.debug("télémétrie usage ignorée", exc_info=True)
