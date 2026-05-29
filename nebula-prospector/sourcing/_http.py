"""HTTP session polie, partagée par tous les scrapers.

Règles :
- User-Agent honnête (identifie NEBULA, contact email)
- Délai minimum 2s entre 2 requêtes vers le même domaine
- Respect robots.txt (à activer si on industrialise)
- Pas de proxies / pas de contournement de protections
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from threading import Lock

import httpx

logger = logging.getLogger(__name__)

USER_AGENT = (
    "NebulaProspectorBot/0.1 (+https://nebula-agency.com/bot; "
    "contact: mongazi@nebula-agency.com)"
)

_last_call_per_host: dict[str, float] = defaultdict(float)
_lock = Lock()
MIN_DELAY_SECONDS = 2.0


def polite_get(url: str, *, timeout: float = 20.0, **kwargs) -> httpx.Response:
    """GET HTTP avec délai minimum entre appels au même host."""
    host = httpx.URL(url).host

    with _lock:
        elapsed = time.time() - _last_call_per_host[host]
        if elapsed < MIN_DELAY_SECONDS:
            time.sleep(MIN_DELAY_SECONDS - elapsed)
        _last_call_per_host[host] = time.time()

    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    headers.setdefault("Accept-Language", "fr-FR,fr;q=0.9,en;q=0.8")
    headers.setdefault("Accept", "text/html,application/xhtml+xml")

    logger.debug("GET %s", url)
    return httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True, **kwargs)
