# -*- coding: utf-8 -*-
"""
Transcrit une note vocale (WhatsApp .ogg/.opus, .mp3, .m4a, .wav) en texte français, avec Deepgram Nova-3.

    python scripts/transcrire.py <fichier audio> [<fichier audio> ...]

La clé vient de `secrets/deepgram.env` (jamais affichée, jamais dans le dépôt).
Pourquoi Deepgram : déjà branché pour NEBULA VOIX (2026-11-05), français vérifié, quelques secondes par vocal.
⚠️ La voix d'un prospect part chez Deepgram (États-Unis) : usage ponctuel pour répondre à un message reçu,
jamais d'archivage des fichiers audio (on garde le texte, on supprime l'audio).
"""
import io, json, mimetypes, sys, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def cle():
    for l in io.open(RACINE / "secrets/deepgram.env", encoding="utf-8"):
        if "=" in l and not l.startswith("#"):
            nom, val = l.split("=", 1)
            if "KEY" in nom.upper() or "DEEPGRAM" in nom.upper():
                return val.strip().strip('"').strip("'")
    raise SystemExit("clé Deepgram introuvable dans secrets/deepgram.env")


def transcrire(chemin):
    donnees = Path(chemin).read_bytes()
    type_ = mimetypes.guess_type(chemin)[0] or "audio/ogg"
    if chemin.lower().endswith((".ogg", ".opus", ".oga")):
        type_ = "audio/ogg"
    url = ("https://api.deepgram.com/v1/listen?model=nova-3&language=fr"
           "&smart_format=true&punctuate=true&paragraphs=true")
    req = urllib.request.Request(url, data=donnees, method="POST",
                                 headers={"Authorization": "Token " + cle(), "Content-Type": type_})
    with urllib.request.urlopen(req, timeout=120) as r:
        rep = json.load(r)
    alt = rep["results"]["channels"][0]["alternatives"][0]
    return alt.get("transcript", "").strip(), rep.get("metadata", {}).get("duration", 0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for f in sys.argv[1:]:
        texte, duree = transcrire(f)
        print(f"── {Path(f).name} ({duree:.0f} s)\n{texte or '(rien entendu)'}\n")
