"""Réglage RUNTIME des modèles + effort par tâche — piloté depuis le cockpit admin.

Source : un réglage JSON `cfg_models` en base (table `bia_settings`), avec repli
sur les défauts de `config.py`. Permet à Mongazi de changer, sans redéploiement :
- le MODÈLE de chaque tâche (vendeur / manager / rédaction / créatif-CEO) ;
- l'EFFORT (éco / standard / max) = multiplicateur sur la longueur de réponse.

Robuste par construction : toute erreur de lecture → on retombe sur les défauts
(`config.py`). L'import de la base est fait DANS les fonctions (pas au chargement)
pour éviter tout import circulaire. Petit cache (TTL) pour ne pas lire la base à
chaque message.
"""
from __future__ import annotations

import json
import time

from config import settings

# Tâches pilotables → attribut de défaut dans config.Settings.
TASKS: dict[str, dict] = {
    "vendeur": {"attr": "claude_model", "label": "Vendeur — réponses aux clients"},
    "manager": {"attr": "manager_model", "label": "Manager — ordres du commerçant"},
    "writer":  {"attr": "writer_model",  "label": "Rédaction — emails · social · coach"},
    "builder": {"attr": "builder_model", "label": "Créatif / CEO — visuels, stratégie (lourd)"},
}

# Modèles proposés dans le cockpit (du plus éco au plus puissant).
MODELS: list[dict] = [
    {"id": "claude-haiku-4-5-20251001", "label": "Haiku — éco & rapide"},
    {"id": "claude-sonnet-4-6",         "label": "Sonnet — équilibré (recommandé)"},
    {"id": "claude-opus-4-8",           "label": "Opus — qualité max (cher)"},
]
_MODEL_IDS = {m["id"] for m in MODELS}

EFFORTS = ["eco", "standard", "max"]
_EFFORT_MULT = {"eco": 0.6, "standard": 1.0, "max": 1.8}

_TTL = 30.0
_cache: dict = {"data": None, "ts": 0.0}


def _defaults() -> dict:
    return {t: {"model": getattr(settings, v["attr"]), "effort": "standard"}
            for t, v in TASKS.items()}


def _load() -> dict:
    now = time.time()
    if _cache["data"] is not None and (now - _cache["ts"]) < _TTL:
        return _cache["data"]
    cfg = _defaults()
    try:
        from db.client import get_setting
        raw = get_setting("cfg_models")
        if raw:
            stored = json.loads(raw) if isinstance(raw, str) else raw
            for t in TASKS:
                s = (stored or {}).get(t) or {}
                if s.get("model") in _MODEL_IDS:
                    cfg[t]["model"] = s["model"]
                if s.get("effort") in _EFFORT_MULT:
                    cfg[t]["effort"] = s["effort"]
    except Exception:  # noqa: BLE001
        pass  # base indispo / JSON cassé → défauts config.py
    _cache["data"] = cfg
    _cache["ts"] = now
    return cfg


def model_for(task: str) -> str:
    """Modèle configuré pour la tâche (repli : défaut config.py, sinon vendeur)."""
    cfg = _load().get(task)
    if cfg and cfg.get("model"):
        return cfg["model"]
    attr = TASKS.get(task, {}).get("attr", "claude_model")
    return getattr(settings, attr, settings.claude_model)


def tokens_for(task: str, base: int) -> int:
    """Applique l'effort (éco/standard/max) à un budget de tokens de base."""
    eff = _load().get(task, {}).get("effort", "standard")
    return max(120, min(4096, int(base * _EFFORT_MULT.get(eff, 1.0))))


def current_config() -> dict:
    """Données prêtes pour le cockpit admin."""
    cfg = _load()
    return {
        "tasks": [{"key": t, "label": TASKS[t]["label"],
                   "model": cfg[t]["model"], "effort": cfg[t]["effort"]}
                  for t in TASKS],
        "models": MODELS,
        "efforts": EFFORTS,
    }


def save_config(updates: dict) -> dict:
    """Enregistre les réglages (validés/filtrés) et rafraîchit le cache."""
    cfg = _load()
    out = {t: dict(cfg[t]) for t in TASKS}
    for t in TASKS:
        u = (updates or {}).get(t) or {}
        if u.get("model") in _MODEL_IDS:
            out[t]["model"] = u["model"]
        if u.get("effort") in _EFFORT_MULT:
            out[t]["effort"] = u["effort"]
    from db.client import set_setting
    set_setting("cfg_models", json.dumps(out))
    _cache["data"] = out
    _cache["ts"] = time.time()
    return out
