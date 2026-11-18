# -*- coding: utf-8 -*-
"""
Transcrit une note vocale (WhatsApp .ogg/.opus, .mp3, .m4a, .wav) en texte français.

    python scripts/transcrire.py <fichier audio> [<fichier audio> ...]
    python scripts/transcrire.py --gemini <fichier audio>      (passer directement par Gemini)

1. Deepgram Nova-3 d'abord : rapide, bon en français standard.
2. **Gemini ensuite, tout seul, si Deepgram a décroché.** Le 18/11, sur un vocal de 53 s d'une restauratrice
   de Cotonou, Deepgram s'est arrêté à 13 s (et a écrit « Souris, yogourt » pour « riz, igname ») : le vocal
   mêlait le français et les noms des plats du pays. Ni un son normalisé, ni Nova-3 multilingue, ni Whisper
   n'ont fait mieux ; Gemini a tout entendu. Le signe du décrochage : moins de 6 caractères par seconde de
   vocal (le français parlé en fait 12 à 15).

Les clés viennent de `secrets/deepgram.env` et `secrets/gemini.env` (jamais affichées, jamais dans le dépôt).
⚠️ La voix d'un prospect part chez Deepgram et Google (États-Unis) : usage ponctuel pour répondre à un message
reçu, jamais d'archivage des fichiers audio (on garde le texte, on supprime l'audio).
"""
import base64
import io
import json
import mimetypes
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEUIL = 6.0                                   # caractères par seconde sous lesquels Deepgram a décroché
MODELES_GEMINI = ("gemini-2.5-flash", "gemini-3.8-flash")   # le 18/11, 2.5 a tout rendu, 3.8 a dépassé 90 s
TROU = 6.0                                    # secondes entre le dernier mot entendu et la fin du vocal
CONSIGNE = ("Transcris mot à mot cette note vocale WhatsApp, envoyée par un commerçant de Cotonou (Bénin). "
            "Elle est surtout en français, avec parfois des mots en fon, goun, yoruba ou mina, et des noms de "
            "plats ou de produits locaux : écris-les tels qu'on les entend. N'invente rien, ne résume pas, ne "
            "corrige pas le style. Si un passage est inaudible, écris [inaudible]. "
            "Rends uniquement la transcription, sans commentaire.")


def cle(fichier, indices):
    for l in io.open(RACINE / "secrets" / fichier, encoding="utf-8"):
        if "=" in l and not l.startswith("#"):
            nom, val = l.split("=", 1)
            if any(i in nom.upper() for i in indices):
                return val.strip().strip('"').strip("'")
    raise SystemExit(f"clé introuvable dans secrets/{fichier}")


def type_audio(chemin):
    if chemin.lower().endswith((".ogg", ".opus", ".oga")):
        return "audio/ogg"
    return mimetypes.guess_type(chemin)[0] or "audio/ogg"


def duree(chemin):
    try:
        s = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", chemin],
                           capture_output=True, text=True, timeout=30).stdout.strip()
        return float(s)
    except Exception:
        return 0.0


def deepgram(chemin):
    url = ("https://api.deepgram.com/v1/listen?model=nova-3&language=fr"
           "&smart_format=true&punctuate=true&paragraphs=true")
    req = urllib.request.Request(url, data=Path(chemin).read_bytes(), method="POST",
                                 headers={"Authorization": "Token " + cle("deepgram.env", ("KEY", "DEEPGRAM")),
                                          "Content-Type": type_audio(chemin)})
    with urllib.request.urlopen(req, timeout=120) as r:
        rep = json.load(r)
    alt = rep["results"]["channels"][0]["alternatives"][0]
    mots = alt.get("words") or []
    dernier = mots[-1].get("end", 0) if mots else 0
    return alt.get("transcript", "").strip(), rep.get("metadata", {}).get("duration", 0), dernier


def gemini(chemin):
    """Rend (texte, modèle), ou (None, raison) si Gemini est indisponible.
    Le 18/11 à 23 h, l'API a répondu 503 (saturée) sur les deux modèles : on réessaie, puis on rend la main."""
    corps = json.dumps({"contents": [{"parts": [
        {"text": CONSIGNE},
        {"inline_data": {"mime_type": type_audio(chemin),
                         "data": base64.b64encode(Path(chemin).read_bytes()).decode()}}]}],
        "generationConfig": {"temperature": 0}}).encode()
    derniere = None
    fin = time.time() + 120                         # deux minutes au plus pour tout Gemini, tentatives comprises
    for m in MODELES_GEMINI:
        for essai in range(3):
            reste = fin - time.time()
            if reste < 10:
                return None, (derniere or "") + " · délai de 2 min dépassé"
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", data=corps,
                method="POST", headers={"Content-Type": "application/json",
                                        "x-goog-api-key": cle("gemini.env", ("GEMINI", "KEY"))})
            try:
                with urllib.request.urlopen(req, timeout=min(45, reste)) as r:
                    rep = json.load(r)
                parts = rep["candidates"][0]["content"]["parts"]
                return " ".join(p.get("text", "") for p in parts).strip(), m
            except urllib.error.HTTPError as e:
                derniere = f"{m} : HTTP {e.code}"
                if e.code in (429, 500, 503) and essai < 2:
                    time.sleep(8 * (essai + 1))         # saturé : on attend un peu et on réessaie
                    continue
                break                                   # autre erreur : modèle suivant
            except (OSError, KeyError, IndexError) as e:
                derniere = f"{m} : {type(e).__name__}"
                break
    return None, derniere


def transcrire(chemin, forcer_gemini=False):
    """Rend (texte, durée en s, moteur). Jamais d'attente sans fin, jamais un texte partiel déguisé en complet."""
    d = duree(chemin)
    texte = ""
    if not forcer_gemini:
        texte, d_dg, dernier = deepgram(chemin)
        d = d or d_dg
        # deux signes de décrochage : trop peu de texte pour la durée, ou un long silence après le dernier mot entendu
        decroche = d >= 10 and (len(texte) / max(d, 1) < SEUIL or dernier < d - TROU)
        if not decroche:
            return texte, d, "Deepgram"
    complet, modele = gemini(chemin)
    if complet:
        return complet, d, modele
    marque = f"⚠️ PARTIEL : Deepgram a décroché et Gemini est indisponible ({modele}). Réessayer plus tard."
    return (marque + ("\n" + texte if texte else "")), d, "Deepgram (partiel)"


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--gemini"]
    if not args:
        raise SystemExit(__doc__)
    for f in args:
        texte, d, moteur = transcrire(f, "--gemini" in sys.argv)
        print(f"── {Path(f).name} ({d:.0f} s · {moteur})\n{texte or '(rien entendu)'}\n")
