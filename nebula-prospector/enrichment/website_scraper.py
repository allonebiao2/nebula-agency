"""Scraping de sites web pour extraire emails + résumé textuel."""
from __future__ import annotations

import re
import logging
from typing import Optional

import httpx
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Emails-bruit à filtrer
SKIP_EMAILS = {"example@example.com", "name@example.com", "user@domain.com"}
SKIP_SUBSTRINGS = (
    "noreply", "no-reply", "donotreply", "do-not-reply",
    "sentry.io", "wixpress.com", "@2x", "@1x", ".png", ".jpg",
    ".webp", ".svg", "googlemail.com.example",
)

# Chemins typiques où trouver un email
CONTACT_PATHS = ("/contact", "/contact-us", "/contactez-nous", "/about",
                  "/about-us", "/a-propos", "/mentions-legales")

USER_AGENT = "Mozilla/5.0 (compatible; NEBULA-NOVA/1.0; +https://nebula-agency-production.up.railway.app)"


def _clean_email(email: str) -> str:
    """Normalise et nettoie une adresse email."""
    return email.strip().lower().rstrip(".,;:")


def _is_valid_email(email: str) -> bool:
    """Filtre les emails-bruit."""
    e = email.lower()
    if e in SKIP_EMAILS:
        return False
    if any(s in e for s in SKIP_SUBSTRINGS):
        return False
    # Filtre les extensions d'image qui matchent le regex par erreur
    if e.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")):
        return False
    return True


def extract_emails(text: str) -> list[str]:
    """Extrait les emails valides d'un texte brut."""
    found = {_clean_email(m) for m in EMAIL_RE.findall(text)}
    return sorted(e for e in found if _is_valid_email(e))


def _fetch(url: str, timeout: float = 8.0) -> Optional[str]:
    """Fetch URL, retourne le texte HTML ou None en cas d'échec."""
    try:
        r = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "fr,en;q=0.8"},
        )
        if r.status_code == 200 and "text/html" in r.headers.get("content-type", ""):
            return r.text
    except Exception as e:
        log.debug(f"fetch failed for {url}: {e}")
    return None


def _normalize_url(website: str) -> str:
    """Ajoute https:// si manquant, retire les espaces."""
    w = website.strip()
    if not w.startswith(("http://", "https://")):
        w = "https://" + w
    return w.rstrip("/")


def scrape_emails_from_site(website: str) -> list[str]:
    """Scrape la homepage + pages contact/about pour extraire des emails.

    Retourne une liste d'emails uniques (max 5 pour rester pertinent).
    """
    if not website:
        return []

    base = _normalize_url(website)
    emails: set[str] = set()

    # Homepage
    html = _fetch(base)
    if html:
        emails.update(extract_emails(html))
        # Liens mailto: explicites
        try:
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=re.compile(r"^\s*mailto:", re.I)):
                href = a.get("href", "")
                addr = href.split(":", 1)[1].split("?")[0].strip()
                if addr and _is_valid_email(addr):
                    emails.add(_clean_email(addr))
        except Exception as e:
            log.debug(f"BS parse failed: {e}")

    # Pages contact/about
    for path in CONTACT_PATHS:
        html = _fetch(base + path)
        if html:
            emails.update(extract_emails(html))

    # Limite à 5, tri par "qualité" (les contact@/info@/hello@ d'abord)
    PRIORITY_PREFIXES = ("contact@", "info@", "hello@", "bonjour@", "commande@", "vente@")
    sorted_emails = sorted(
        emails,
        key=lambda e: (0 if e.startswith(PRIORITY_PREFIXES) else 1, e),
    )
    return sorted_emails[:5]


def get_site_summary(website: str, max_chars: int = 2500) -> str:
    """Récupère un résumé textuel du site (homepage) — pour analyse Claude."""
    if not website:
        return ""
    base = _normalize_url(website)
    html = _fetch(base)
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "lxml")
        # Retire scripts/styles/nav répétitifs
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:max_chars]
    except Exception as e:
        log.debug(f"summary parse failed: {e}")
        return ""
