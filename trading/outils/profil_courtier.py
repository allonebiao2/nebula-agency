# -*- coding: utf-8 -*-
"""
Carte d'identité du courtier : à lancer AVANT d'armer quoi que ce soit,
et à relancer à chaque fois qu'on change de courtier.

    python trading/outils/profil_courtier.py
    python trading/outils/profil_courtier.py "C:\\Program Files\\MetaTrader 5 EXNESS\\terminal64.exe"

Il ne passe aucun ordre. Il lit, il mesure, il imprime — dont la seule valeur
qu'aucun courtier ne publie honnêtement : le décalage horaire de son serveur.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from trading.noyau.courtier import Courtier, CourtierIndisponible   # noqa: E402

TERMINAUX_CONNUS = {
    "Deriv (demo)":  r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe",
    "Deriv (SVG)":   r"C:\Program Files\MetaTrader\terminal64.exe",
    "Exness":        r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe",
    "MetaQuotes":    r"C:\Program Files\MetaTrader 5\terminal64.exe",
}


def main() -> int:
    if len(sys.argv) > 1:
        chemins = {"(argument)": sys.argv[1]}
    else:
        chemins = {n: c for n, c in TERMINAUX_CONNUS.items() if Path(c).exists()}
        if not chemins:
            print("Aucun terminal MT5 trouvé aux emplacements habituels.")
            return 1

    trouve = False
    for nom, chemin in chemins.items():
        print(f"\n### {nom}\n    {chemin}")
        try:
            with Courtier(chemin_terminal=chemin) as c:
                print()
                print(c.diagnostic("EURUSD"))
                trouve = True
        except CourtierIndisponible as e:
            print(f"\n    ⛔ {e}\n")

    if not trouve:
        print("\n" + "=" * 70)
        print("  AUCUN COMPTE CONNECTÉ — c'est la seule étape qui demande tes mains.")
        print("=" * 70)
        print("""
  1. Ouvre MetaTrader 5 (celui de Deriv)
  2. Fichier > Se connecter à un compte de trading
  3. Entre le compte DÉMO Deriv, et coche « Enregistrer les données du compte »
  4. Outils > Options > Expert Advisors : coche « Autoriser le trading algorithmique »
  5. Laisse le terminal OUVERT, puis relance cette commande.

  Tant que ce n'est pas fait, rien ne peut lire les vraies spécifications du
  contrat — et sans elles, tout dimensionnement serait une supposition.
""")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
