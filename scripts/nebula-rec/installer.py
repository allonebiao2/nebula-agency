# -*- coding: utf-8 -*-
"""Installe NEBULA REC sur ce PC.

    python scripts/nebula-rec/installer.py            # installer, ou mettre à jour après une modification
    python scripts/nebula-rec/installer.py --retirer  # désinstaller (les vidéos ne sont jamais touchées)

Copie le logiciel dans %LOCALAPPDATA%\\Programs\\NEBULA REC (une opération git dans le dépôt ne le casse
donc pas pendant qu'il tourne), fabrique son icône, pose un raccourci sur le Bureau et dans le menu Démarrer.
"""

import os
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import moteur  # noqa: E402
from icone import fabriquer_icone  # noqa: E402

NOM = "NEBULA REC"
DEST = os.path.join(os.environ["LOCALAPPDATA"], "Programs", NOM)
DONNEES = os.path.join(os.environ["LOCALAPPDATA"], NOM)
FICHIERS = ("nebula_rec.pyw", "moteur.py", "icone.py")

RACCOURCIS = r"""
$sh = New-Object -ComObject WScript.Shell
foreach ($d in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
  $lnk = Join-Path $d 'NEBULA REC.lnk'
  if ($env:NR_ACTION -eq 'retirer') {
    if (Test-Path -LiteralPath $lnk) { Remove-Item -LiteralPath $lnk -Force; "retire : $lnk" }
    continue
  }
  $s = $sh.CreateShortcut($lnk)
  $s.TargetPath = $env:NR_CIBLE
  $s.Arguments = $env:NR_ARGS
  $s.WorkingDirectory = $env:NR_DOSSIER
  $s.IconLocation = "$env:NR_ICONE,0"
  $s.Description = 'Enregistreur d ecran NEBULA REC'
  $s.Save()
  "ok : $lnk"
}
"""


def raccourcis(action, cible="", args="", icone=""):
    env = dict(os.environ, NR_ACTION=action, NR_CIBLE=cible, NR_ARGS=args, NR_DOSSIER=DEST, NR_ICONE=icone)
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", RACCOURCIS],
                       env=env, capture_output=True)
    sortie = moteur.decoder(r.stdout).strip()
    if sortie:
        print(sortie)
    if r.returncode != 0:
        print("⚠️ raccourcis :", moteur.decoder(r.stderr)[-400:])
    return r.returncode == 0


def installer():
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        sys.exit(f"pythonw.exe introuvable à côté de {sys.executable}")
    if not moteur.trouver("ffmpeg") or not moteur.trouver("ffprobe"):
        print("⚠️ ffmpeg introuvable : installe-le avec  winget install Gyan.FFmpeg  (NEBULA REC en a besoin).")
    os.makedirs(DEST, exist_ok=True)
    for f in FICHIERS:
        shutil.copy2(os.path.join(ICI, f), os.path.join(DEST, f))
    icone = fabriquer_icone(os.path.join(DEST, "nebula-rec.ico"))
    os.makedirs(DONNEES, exist_ok=True)
    shutil.copy2(icone, os.path.join(DONNEES, "nebula-rec.ico"))
    ok = raccourcis("installer", pythonw, f'"{os.path.join(DEST, "nebula_rec.pyw")}"', icone)
    print(f"✅ NEBULA REC installé dans {DEST}" + ("" if ok else " (sans raccourcis)"))


def retirer():
    raccourcis("retirer")
    shutil.rmtree(DEST, ignore_errors=True)
    en_cours = moteur.sessions_interrompues(os.path.join(DONNEES, "en-cours"))
    if en_cours:
        print(f"⚠️ {len(en_cours)} enregistrement(s) interrompu(s) gardé(s) dans {DONNEES}")
    else:
        shutil.rmtree(DONNEES, ignore_errors=True)
    print("✅ NEBULA REC retiré. Les vidéos enregistrées sont restées à leur place.")


if __name__ == "__main__":
    retirer() if "--retirer" in sys.argv else installer()
