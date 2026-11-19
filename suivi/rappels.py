# -*- coding: utf-8 -*-
"""
NEBULA SUIVI · le rappel qui insiste (Mongazi, 19/11 : « le rappel en alerte demain avec insistance, tout message que je
dois envoyer ou toute relance »).

Une passe = une alerte, s'il reste des messages de la file « À envoyer » dont l'heure est venue. Lancé toutes les
20 minutes par une tâche planifiée de Windows, il revient donc tant que Mongazi n'a pas touché « Envoyé ✓ ».
Plus un message est en retard, plus l'alerte insiste (titre, vibration, elle reste à l'écran).

    python suivi/rappels.py              # une passe
    python suivi/rappels.py --voir       # dit ce qu'il enverrait, sans rien envoyer

L'heure d'un message est lue dans son champ `heure` : « Ven. 20/11 · 9 h 30 (…) », « 14 h - 16 h », « CE SOIR ».
Un message d'un jour à venir attend son jour. Ce fichier ne contient aucune donnée.
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# lancé par la tâche planifiée avec pythonw (aucune fenêtre) : pas de console, le journal va dans un fichier
if sys.stdout is None or sys.stderr is None:
    journal = Path(os.environ.get("LOCALAPPDATA", ".")) / "nebula" / "rappels.log"
    journal.parent.mkdir(parents=True, exist_ok=True)
    sys.stdout = sys.stderr = open(journal, "a", encoding="utf-8", buffering=1)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from suivi import BENIN, connexion, push  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def debut(heure, maintenant):
    """Le moment où le message devient dû (datetime Bénin), ou None s'il n'a pas d'heure lisible (dû tout de suite)."""
    h = (heure or "").lower()
    if "ce soir" in h or "maintenant" in h:
        return None
    jour = maintenant.date()
    d = re.search(r"\b(\d{1,2})/(\d{1,2})\b", h)
    if d:
        jour = jour.replace(month=int(d.group(2)), day=int(d.group(1)))
    t = re.search(r"\b(\d{1,2}) ?h ?(\d{2})?", h)
    hh, mm = (int(t.group(1)), int(t.group(2) or 0)) if t else (9, 0)
    return datetime(jour.year, jour.month, jour.day, hh, mm, tzinfo=BENIN)


def passe(voir=False):
    maintenant = datetime.now(BENIN)
    with connexion() as c:
        file = c.execute("select id, pour, heure from public.nebula_suivi_envois where not envoye order by id").fetchall()
    dus = []
    for r in file:
        d = debut(r["heure"], maintenant)
        if d is None or d <= maintenant:
            dus.append((r, (maintenant - d).total_seconds() / 60 if d else 0))
    if not dus:
        print(f"{maintenant:%H:%M} · rien de dû ({len(file)} en file pour plus tard)")
        return 0
    retard = max(m for _, m in dus)
    noms = [re.sub(r"\s*\(.*?\)", "", r["pour"]) for r, _ in dus]
    tete = ", ".join(noms[:3]) + (f" et {len(noms) - 3} autre(s)" if len(noms) > 3 else "")
    if retard >= 90:
        titre = f"⛔ {len(dus)} message(s) en retard"
    elif retard >= 30:
        titre = f"⏰ Toujours {len(dus)} message(s) à envoyer"
    else:
        titre = f"📲 {len(dus)} message(s) à envoyer maintenant"
    texte = f"{tete}. Ouvre « À envoyer », un toucher par message, puis « Envoyé ✓ »."
    print(f"{maintenant:%H:%M} · {titre} · {texte}")
    if voir:
        return len(dus)
    push(titre, texte, cle="rappel-envois", url="./#envois", insiste=True)
    return len(dus)


if __name__ == "__main__":
    passe("--voir" in sys.argv)
