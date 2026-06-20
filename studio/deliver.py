# -*- coding: utf-8 -*-
"""
NEBULA Studio Quotidien — LIVRAISON Telegram.

Envoie chaque matin à Mongazi : la vidéo + l'affiche + le script prêt à publier
(accroche, script, légende, hashtags, CTA). Utilise le bot et le chat_id déjà
configurés dans l'écosystème NEBULA (env TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID*).
"""
import os, pathlib

def _httpx():
    import httpx
    return httpx

def _token_chat():
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = (os.environ.get("TELEGRAM_CHAT_ID")
            or os.environ.get("TELEGRAM_CHAT_ID_MONGAZI"))
    return tok, chat

def _api(method, tok):
    return f"https://api.telegram.org/bot{tok}/{method}"

def caption_block(c):
    tags = " ".join(c.get("hashtags", []) or [])
    slot = f" · Post {c.get('slot')}" if c.get("slot") else ""
    parts = [
        f"NEBULA STUDIO · {c.get('date','')}{slot}",
        f"{c.get('brand','')} — {c.get('format','')}",
        "",
        f"ACCROCHE : {c.get('hook','')}",
        "",
        c.get("script", ""),
        "",
        f"LÉGENDE : {c.get('caption','')}",
        f"CTA : {c.get('cta','')}",
        tags,
        "",
        f"(style {c.get('visual',{}).get('style','')} · {c.get('platform','')})",
        f"Pourquoi c'est neuf : {c.get('freshness_note','')}",
    ]
    return "\n".join(p for p in parts if p is not None)

def deliver(concept, paths):
    tok, chat = _token_chat()
    if not tok or not chat:
        print("Telegram non configuré (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID*) — livraison ignorée.")
        return False
    httpx = _httpx()
    text = caption_block(concept)
    short = (concept.get("hook", "") + "\n\n" + concept.get("caption", "")).strip()[:1000]
    ok = True
    with httpx.Client(timeout=120) as cli:
        video = paths.get("video")
        poster = paths.get("poster")
        try:
            if video and pathlib.Path(video).exists():
                with open(video, "rb") as fh:
                    r = cli.post(_api("sendVideo", tok),
                                 data={"chat_id": chat, "caption": short},
                                 files={"video": fh})
                ok = ok and r.status_code == 200
            elif poster and pathlib.Path(poster).exists():
                with open(poster, "rb") as fh:
                    r = cli.post(_api("sendPhoto", tok),
                                 data={"chat_id": chat, "caption": short},
                                 files={"photo": fh})
                ok = ok and r.status_code == 200
        except Exception as e:
            print("Envoi média KO:", e); ok = False
        # le script complet, en message texte (toujours, même si la vidéo a échoué)
        for chunk_start in range(0, len(text), 3800):
            chunk = text[chunk_start:chunk_start + 3800]
            try:
                r = cli.post(_api("sendMessage", tok), data={"chat_id": chat, "text": chunk})
                ok = ok and r.status_code == 200
            except Exception as e:
                print("Envoi texte KO:", e); ok = False
    print("Telegram :", "envoyé ✓" if ok else "partiel/échec")
    return ok
