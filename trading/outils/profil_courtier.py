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
from trading.noyau.identifiants import charger, profils_disponibles  # noqa: E402

TERMINAUX_CONNUS = {
    "Deriv (demo)":  r"C:\Program Files\MetaTrader 5 Terminal\terminal64.exe",
    "Deriv (SVG)":   r"C:\Program Files\MetaTrader\terminal64.exe",
    "Exness":        r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe",
    "MetaQuotes":    r"C:\Program Files\MetaTrader 5\terminal64.exe",
}


def _sessions() -> dict[str, Courtier]:
    """Qui interroger, dans l'ordre de fiabilité.

    1. Un chemin donné en argument : on l'ouvre tel quel.
    2. Les profils COMPLETS de `secrets/mt5.env` (compte, mot de passe et
       serveur nommés) : la seule voie qui a franchi le `-6` (2026-09-16).
    3. À défaut, les terminaux connus, en espérant qu'ils aient mémorisé un
       compte : c'est la voie qui renvoyait `-6 Authorization failed`.
    """
    if len(sys.argv) > 1:
        return {f"(argument)\n    {sys.argv[1]}": Courtier(chemin_terminal=sys.argv[1])}
    profils = {}
    for nom in profils_disponibles():
        ids = charger(nom)
        if ids.complets:
            profils[str(ids)] = Courtier.depuis_profil(nom)
        else:
            print(f"  profil incomplet, ignoré : {ids}")
    if profils:
        return profils
    return {f"{n}\n    {c}": Courtier(chemin_terminal=c)
            for n, c in TERMINAUX_CONNUS.items() if Path(c).exists()}


def main() -> int:
    sessions = _sessions()
    if not sessions:
        print("Aucun profil complet dans secrets/mt5.env, "
              "et aucun terminal MT5 aux emplacements habituels.")
        return 1

    trouve = False
    for nom, session in sessions.items():
        print(f"\n### {nom}")
        try:
            with session as c:
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
