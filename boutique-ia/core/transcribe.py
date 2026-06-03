"""Transcription des messages VOCAUX WhatsApp (booster).

Beaucoup de clients en Afrique de l'Ouest envoient des notes vocales plutôt que
du texte. Ce module télécharge l'audio depuis Twilio puis le transcrit via
Groq Whisper (gratuit, rapide), pour que l'agent comprenne et réponde.

Dormant tant que GROQ_API_KEY n'est pas configuré (retourne None).
"""
from __future__ import annotations

import logging

import httpx

from config import settings

log = logging.getLogger("boutique-ia.transcribe")


def transcribe_audio(media_url: str, content_type: str | None = None) -> str | None:
    """Télécharge le vocal (Twilio) et le transcrit (Groq Whisper). None si KO."""
    if not (settings.groq_api_key and media_url):
        return None

    # 1. Télécharger l'audio depuis Twilio (auth requise, suit la redirection)
    try:
        auth = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            auth = (settings.twilio_account_sid, settings.twilio_auth_token)
        r = httpx.get(media_url, auth=auth, follow_redirects=True, timeout=25.0)
        r.raise_for_status()
        audio = r.content
        if not audio:
            return None
    except Exception as e:  # noqa: BLE001
        log.warning("Téléchargement vocal KO: %s", e)
        return None

    # 2. Transcrire via Groq (API compatible OpenAI)
    ext = "ogg"
    if content_type and "/" in content_type:
        ext = content_type.split("/")[-1].split(";")[0] or "ogg"
    try:
        resp = httpx.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            files={"file": (f"audio.{ext}", audio, content_type or "audio/ogg")},
            data={"model": settings.groq_whisper_model, "language": "fr",
                  "response_format": "text"},
            timeout=45.0,
        )
        if resp.status_code == 200:
            return resp.text.strip() or None
        log.warning("Groq transcription %s: %s", resp.status_code, resp.text[:160])
        return None
    except Exception as e:  # noqa: BLE001
        log.warning("Groq transcription KO: %s", e)
        return None
