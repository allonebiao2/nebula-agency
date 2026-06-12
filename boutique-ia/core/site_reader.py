"""Lecture automatique du site d'un client → texte pour la base de connaissances.

Le client donne juste l'URL de son site ; on récupère la page + quelques pages
internes (même domaine), on en extrait le texte, et on l'injecte dans la base de
connaissances de l'agent support. Bounded & safe : timeout, taille plafonnée, http(s)
uniquement, nombre de pages limité. Ne lève jamais (retourne '' en cas d'échec).
"""
from __future__ import annotations

import logging
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

log = logging.getLogger("boutique-ia.site_reader")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.links: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg", "head"):
            self._skip += 1
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.links.append(v)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "head") and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0:
            t = data.strip()
            if t:
                self.parts.append(t)


def _extract(html: str) -> tuple[str, list[str]]:
    p = _TextExtractor()
    try:
        p.feed(html)
    except Exception:  # noqa: BLE001
        pass
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(p.parts))
    return text, p.links


def fetch_site_text(url: str, max_pages: int = 4, max_chars: int = 40000) -> str:
    """Récupère le texte du site (page donnée + quelques pages internes). '' si échec."""
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        base = urlparse(url)
        if not base.netloc:
            return ""
    except Exception:  # noqa: BLE001
        return ""

    seen: set[str] = set()
    queue: list[str] = [url]
    out: list[str] = []
    headers = {"User-Agent": "VendoraSupportBot/1.0 (+https://nebula-agency.online)"}
    try:
        with httpx.Client(timeout=12.0, follow_redirects=True, headers=headers) as cli:
            while queue and len(seen) < max_pages:
                u = queue.pop(0)
                if u in seen:
                    continue
                seen.add(u)
                try:
                    r = cli.get(u)
                    if r.status_code != 200 or "text/html" not in r.headers.get("content-type", ""):
                        continue
                    html = r.text[:400000]
                except Exception:  # noqa: BLE001
                    continue
                text, links = _extract(html)
                if text:
                    out.append(f"# Page : {u}\n{text[:12000]}")
                for ln in links:
                    try:
                        full = urljoin(u, ln).split("#")[0]
                        if (urlparse(full).netloc == base.netloc and full not in seen
                                and len(seen) + len(queue) < max_pages * 3):
                            queue.append(full)
                    except Exception:  # noqa: BLE001
                        pass
    except Exception:  # noqa: BLE001
        log.exception("lecture site échouée")
        return ("\n\n".join(out))[:max_chars]
    return ("\n\n".join(out))[:max_chars]
