"""LE SIMULATEUR — parler à l'agent dans un terminal, sans compte WhatsApp.

    python whatsapp-agent/simuler.py braise-dor            # avec le vrai modèle
    python whatsapp-agent/simuler.py braise-dor --faux      # sans clé, réponses écrites

C'est le premier outil à lancer quand on prépare un client : on voit la carte
qu'il a vraiment, on entend le ton qu'il aura, et on peut essayer de le piéger
sur un prix. Le garde-fou est le même qu'en production, la mémoire aussi : ce
qui passe ici passera en ligne.
"""
from __future__ import annotations

import argparse
import logging
import sys
import tempfile
from pathlib import Path

RACINE_KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE_KIT))

from agent import maison as maisons_mod          # noqa: E402
from agent.memoire import Memoire                # noqa: E402
from agent.service import Service                # noqa: E402
from canaux.console import CanalConsole          # noqa: E402


def main() -> int:
    analyseur = argparse.ArgumentParser(description="Parler à un agent WhatsApp NEBULA.")
    analyseur.add_argument("maison", help="l'identifiant d'un fichier de maisons/")
    analyseur.add_argument("--racine", default=str(RACINE_KIT.parent))
    analyseur.add_argument("--numero", default="22900000000",
                           help="le numéro qui joue le client")
    analyseur.add_argument("--nom", default="", help="le prénom du client, s'il est connu")
    analyseur.add_argument("--base", default="", help="une base à garder (sinon, éphémère)")
    analyseur.add_argument("--faux", action="store_true",
                           help="ne pas appeler le modèle : réponses écrites d'avance")
    analyseur.add_argument("--bavard", action="store_true")
    args = analyseur.parse_args()

    logging.basicConfig(level=logging.INFO if args.bavard else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")

    fiche = RACINE_KIT / "maisons" / f"{args.maison}.yaml"
    if not fiche.exists():
        disponibles = ", ".join(sorted(f.stem for f in (RACINE_KIT / "maisons").glob("*.yaml")))
        print(f"Pas de maison « {args.maison} ». Disponibles : {disponibles}")
        return 1
    maison = maisons_mod.charger(fiche)

    client = None
    if args.faux:
        from tests.faux import FauxModele
        client = FauxModele(["(mode --faux : le modèle n'est pas appelé, "
                             "la carte et le garde-fou le sont)"] * 50)

    base = Path(args.base) if args.base else Path(tempfile.mkdtemp()) / "simulation.db"
    memoire = Memoire(base)
    canal = CanalConsole()
    service = Service(maison, Path(args.racine), memoire, canal, client=client)

    prete, manques = maison.prete
    print(f"\n=== {maison.nom} — {len(service.catalogue)} articles lus dans "
          f"{service.catalogue.source} ===")
    print(f"    {service.garde.resume()}")
    if not prete:
        print("    ⚠️ pas prête pour la production : " + " ; ".join(manques))
    if maison.accueil:
        print(f"\n[{maison.nom}] {maison.accueil.strip()}")
    print("\n(une ligne vide ou « fin » pour sortir · « /carte » pour voir la carte lue)\n")

    while True:
        try:
            entree = input("vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not entree or entree.lower() in ("fin", "quit", "exit"):
            break
        if entree == "/carte":
            print(service.catalogue.texte())
            continue

        traitement = service.traiter(args.numero, entree, nom_client=args.nom)
        reponse = traitement.reponse
        if reponse.sortie == "silence":
            print(f"  … l'agent se tait : {reponse.motif}")
            continue
        print(f"\n[{maison.nom}] {reponse.texte}\n")
        if reponse.verdict and not reponse.verdict.sur:
            print(f"  ⛔ GARDE-FOU : {reponse.verdict.explication()}")
        for e in reponse.escalades:
            print(f"  → passé à un humain : {e.get('raison', '')}")
        for c in reponse.commandes:
            print(f"  → commande notée : {c}")
        if reponse.jetons.get("entree"):
            j = reponse.jetons
            print(f"  · jetons entrée {j['entree']} · sortie {j['sortie']} "
                  f"· cache lu {j['cache_lu']}")
    print("À bientôt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
