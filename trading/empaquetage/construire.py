# -*- coding: utf-8 -*-
"""
Construire le produit installable : un dossier autonome + une archive .zip.

    python -m trading.empaquetage.construire

Résultat : `trading/empaquetage/sortie/NEBULA-Trader-<version>.zip`, qui contient
`NEBULA Trader.exe` et ses fichiers. Le client dézippe, double-clique, et
l'interface s'ouvre dans son navigateur. Aucune installation de Python.

Trois règles de construction :
  · LA SUITE QC DOIT ÊTRE VERTE, sinon on ne construit pas.
  · RIEN DE `secrets/` N'ENTRE DANS LE PAQUET : ni la clé privée de licence, ni
    les identifiants MT5 de Mongazi. Le paquet est inspecté après construction.
  · LES RAPPORTS LIVRÉS SONT CEUX DU DÉPÔT : walk-forward et mesure du capital,
    copiés au premier lancement dans le dossier de l'utilisateur.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parents[2]
TRADING = RACINE / "trading"
ICI = Path(__file__).resolve().parent
SORTIE = ICI / "sortie"
TRAVAIL = ICI / "travail"
NOM = "NEBULA Trader"

# Par NOM : ce qui vient de secrets/ ou du dossier de données de Mongazi.
INTERDITS = ("mt5.env", "deriv.env", "nebula-trader-licence.pem", "licence.txt", "compte.json",
             "secrets.json", "journal.db", "reglages.json", "cloudflare.env", "render.env")
# Par CONTENU : une clé privée, quel que soit son nom. (`certifi/cacert.pem` est la
# liste PUBLIQUE des autorités de certification : un .pem n'est pas un secret.)
MARQUEUR_PRIVE = b"PRIVATE KEY-----"


def main() -> int:
    from trading.interface.serveur import VERSION

    print("1. Contrôle qualité")
    qc = subprocess.run([sys.executable, "-m", "trading.outils.qc"], cwd=RACINE,
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    derniere = [l for l in qc.stdout.splitlines() if "verts" in l]
    print("   " + (derniere[-1].strip() if derniere else "QC sans résultat"))
    if qc.returncode != 0:
        print("⛔ QC rouge : construction refusée.")
        return 1

    print("2. PyInstaller")
    shutil.rmtree(SORTIE, ignore_errors=True)
    sep = ";"
    donnees = [
        (TRADING / "interface" / "statique", "trading/interface/statique"),
        (TRADING / "config.toml", "trading"),
    ]
    rapports = list((TRADING / "rapports").glob("*.json"))
    for r in rapports:
        donnees.append((r, "trading/rapports"))
    commande = [
        sys.executable, "-m", "PyInstaller", str(ICI / "lanceur.py"),
        "--name", NOM, "--noconfirm", "--clean", "--onedir", "--console",
        "--distpath", str(SORTIE), "--workpath", str(TRAVAIL), "--specpath", str(TRAVAIL),
        "--paths", str(RACINE),
        "--collect-submodules", "uvicorn", "--collect-submodules", "trading",
        "--hidden-import", "MetaTrader5", "--hidden-import", "anthropic",
        "--exclude-module", "pandas", "--exclude-module", "scipy", "--exclude-module", "matplotlib",
        "--exclude-module", "tkinter", "--exclude-module", "IPython", "--exclude-module", "pytest",
    ]
    for source, cible in donnees:
        commande += ["--add-data", f"{source}{sep}{cible}"]
    r = subprocess.run(commande, cwd=RACINE)
    if r.returncode != 0:
        print("⛔ PyInstaller a échoué.")
        return 1

    dossier = SORTIE / NOM
    print("3. Inspection du paquet")
    fautes = [str(p.relative_to(dossier)) for p in dossier.rglob("*")
              if p.is_file() and p.name in INTERDITS]
    fautes += [str(p.relative_to(dossier)) for p in dossier.rglob("*")
               if p.is_file() and p.stat().st_size < 2_000_000 and p.suffix not in (".pyd", ".dll")
               and MARQUEUR_PRIVE in p.read_bytes()]
    if fautes:
        print(f"⛔ fichiers interdits dans le paquet : {fautes}")
        return 1
    for attendu in ("trading/interface/statique/app.js", "trading/config.toml"):
        if not list(dossier.rglob(Path(attendu).name)):
            print(f"⛔ fichier manquant dans le paquet : {attendu}")
            return 1
    print(f"   {len(rapports)} rapport(s) livrés, aucun secret, interface présente")

    (dossier / "LISEZ-MOI.txt").write_text(LISEZ_MOI.format(version=VERSION), encoding="utf-8")

    print("4. Archive")
    archive = SORTIE / f"NEBULA-Trader-{VERSION}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for p in dossier.rglob("*"):
            if p.is_file():
                z.write(p, Path(NOM) / p.relative_to(dossier))
    taille = archive.stat().st_size / 1e6
    print(f"   -> {archive} ({taille:.0f} Mo)")
    shutil.rmtree(TRAVAIL, ignore_errors=True)
    return 0


LISEZ_MOI = """NEBULA Trader {version}
=======================

Installer
  1. Dézipper ce dossier où tu veux (par exemple Documents).
  2. Double-cliquer sur « NEBULA Trader.exe ». L'interface s'ouvre dans ton navigateur.
     Si Windows affiche « Windows a protégé votre ordinateur », cliquer sur
     « Informations complémentaires » puis « Exécuter quand même ».

Brancher MetaTrader 5
  1. Installer MetaTrader 5 chez ton courtier et te connecter une fois à ton compte.
  2. Dans MetaTrader 5 : bouton « Trading Algo » VERT, et dans Outils > Options >
     Expert Advisors, la case qui DÉSACTIVE le trading via l'API Python DÉCOCHÉE.
  3. Dans NEBULA Trader, page « Compte et licence » : numéro de compte, serveur et
     mot de passe PRINCIPAL (pas celui « investisseur »). Il est chiffré par Windows.

Les trois modes
  Observation  l'agent analyse et explique, il n'envoie aucun ordre (par défaut)
  Démo         ordres réels sur un compte DÉMO uniquement
  Réel         argent réel : licence, compte réel et plafond de capital obligatoires

Petit capital
  Sous 250 $ sur un compte standard, aucun signal ne tient dans le risque autorisé.
  Ouvre un compte CENT chez ton courtier : dès 10 $, le risque de 1 % reste exact.

Avertissement
  Le trading sur marge comporte un risque élevé de perte en capital. Aucun résultat
  passé, mesuré ou réel, ne garantit les résultats futurs. NEBULA Trader ne promet
  aucun rendement : il garantit que le risque que tu choisis n'est jamais dépassé.

Tes données (journal, réglages, licence) : %APPDATA%\\NEBULA Trader
"""


if __name__ == "__main__":
    sys.exit(main())
