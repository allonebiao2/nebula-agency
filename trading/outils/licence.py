# -*- coding: utf-8 -*-
"""
Émettre une licence NEBULA Trader. RÉSERVÉ À NEBULA.

    python -m trading.outils.licence --nom "Koffi A." --email koffi@exemple.com --mois 12
    python -m trading.outils.licence --verifier "NTR1.xxx.yyy"

La clé privée vit dans `secrets/nebula-trader-licence.pem` (ignoré par git,
dépôt public). ⛔ La perdre = ne plus pouvoir émettre ; la publier = n'importe
qui émet des licences. Elle se sauvegarde hors du dépôt.
"""
from __future__ import annotations

import argparse
import secrets as alea
import sys
from datetime import date, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from trading.noyau.licence import signer, verifier                     # noqa: E402

CLE = Path(__file__).resolve().parents[2] / "secrets" / "nebula-trader-licence.pem"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nom", default="")
    ap.add_argument("--email", default="")
    ap.add_argument("--mois", type=int, default=12, help="0 = sans expiration")
    ap.add_argument("--edition", default="pro")
    ap.add_argument("--verifier", default="")
    a = ap.parse_args()

    if a.verifier:
        print(verifier(a.verifier))
        return 0
    if not CLE.exists():
        print(f"⛔ clé privée absente : {CLE}")
        return 1
    charge = {"nom": a.nom, "email": a.email, "edition": a.edition,
              "emis": date.today().isoformat(), "id": alea.token_hex(6),
              "expire": (date.today() + timedelta(days=30 * a.mois)).isoformat() if a.mois else None}
    cle = signer(charge, CLE.read_bytes())
    lic = verifier(cle)
    assert lic.valide, lic
    print(cle)
    print(f"\n  {lic.titulaire} · {lic.email} · {lic.edition} · expire {lic.expire or 'jamais'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
