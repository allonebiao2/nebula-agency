"""LA DÉMONSTRATION — voir l'agent travailler, sans clé et sans compte WhatsApp.

    python whatsapp-agent/demonstration.py            # Au Braisé d'Or
    python whatsapp-agent/demonstration.py hillary    # Hillary M. Styl

⚠️ CE QUI EST SIMULÉ ET CE QUI NE L'EST PAS, parce que la différence est tout.

    SIMULÉ    : les réponses de l'agent, écrites d'avance (ce conteneur n'a pas
                de clé Anthropic). En production, c'est Claude qui les écrit.
    RÉEL      : la carte — lue à l'instant dans le fichier que le site sert.
                Le garde-fou — le vrai code, qui bloque vraiment.
                La mémoire, les escalades, les alertes au patron, la fenêtre 24 h.

Et c'est précisément pour ça que les réponses sont écrites : pour faire dire à
l'agent un prix FAUX et prouver qu'il ne sort pas. Un vrai modèle refuserait
justement de l'inventer le jour de la démonstration.
"""
from __future__ import annotations

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
from tests.faux import FauxModele                # noqa: E402

CLIENT = "22997001122"
PATRON = "22997009988"

# Chaque scène : ce que le client écrit, puis ce que le modèle répondrait.
# Un « ("outil", nom, entrée) » fait appeler un outil avant de répondre.
SCENES = {
    "braise-dor": [
        ("Bonsoir, vous êtes ouverts ?",
         ["Bonsoir et bienvenue Au Braisé d'Or ! Dites-moi ce qui vous ferait "
          "plaisir, je vous donne les prix et je passe la commande à la maison."],
         "l'accueil"),

        ("c'est combien le tilapia ?",
         ["Le tilapia braisé est à {tilapia1} en portion normale et {tilapia2} en "
          "grand. Il est servi avec l'accompagnement de votre choix : riz, "
          "attiéké, aloco, frites…"],
         "un prix simple, lu dans la carte"),

        ("et la sauce gombo ?",
         ["La sauce gombo va de {gombo1} à {gombo2} selon ce que vous mettez "
          "dedans : crabe, kpanmom ou poisson. La maison vous confirme le prix "
          "exact à la commande."],
         "une FOURCHETTE, jamais un prix ferme"),

        ("ok je prends un tilapia normal avec attiéké, je viens le chercher",
         [("outil", "noter_la_commande",
           {"articles": [{"nom": "Tilapia braisé", "quantite": 1,
                          "precisions": "portion normale, avec attiéké"}],
            "total_estime": None, "retrait_ou_livraison": "retrait"}),
          "C'est noté : un tilapia braisé normal avec attiéké, à {tilapia1}, à "
          "récupérer sur place. La maison vous confirme dans un instant."],
         "une commande — et la maison est prévenue"),

        ("vous avez une glace 3 boules ?",
         ["Oui : la glace se vend à la boule, {glace1} pour une, {glace2} pour "
          "deux et {glace3} pour trois."],
         "un BARÈME à trois crans, pas un prix unique"),

        ("je peux réserver une table pour huit personnes samedi ?",
         [("outil", "passer_la_main",
           {"raison": "réservation de table pour huit",
            "resume": "Le client veut réserver une table pour huit personnes samedi.",
            "urgent": False}),
          "Pour une table de huit, je passe la main à la maison : elle vous "
          "répond ici même pour confirmer."],
         "ce qu'il ne sait pas, il le passe"),

        ("et un poulet bicyclette, c'est combien ?",
         ["Le poulet bicyclette est à 4 500 F."],
         "⛔ LE MODÈLE INVENTE UN PRIX — regardez ce qui part"),
    ],
    "hillary": [
        ("Bonjour, la robe de cérémonie coûte combien ?",
         ["Bonjour et bienvenue chez Hillary M. Styl. La robe de cérémonie est à "
          "{p1} en confection normale, sous {d1}. En express, elle est à {p2}."],
         "prix ET délai, lus dans la vitrine"),
        ("je fais du 42, vous prenez mes mesures comment ?",
         [("outil", "passer_la_main",
           {"raison": "prise de mesures",
            "resume": "La cliente veut donner ses mesures pour une robe de cérémonie.",
            "urgent": False}),
          "Pour les mesures, je passe la main à l'atelier : Hillary vous "
          "accompagne directement, c'est plus sûr qu'un tableau de tailles."],
         "les mesures partent TOUJOURS à un humain"),
        ("et si je la veux à 80 000 vous faites ?",
         ["Oui, je peux vous la faire à 80 000 F."],
         "⛔ LE MODÈLE NÉGOCIE UN PRIX QUI N'EXISTE PAS"),
    ],
}


def valeurs(catalogue, identifiant: str) -> dict:
    """Les prix réels, pris dans la carte, pour remplir les répliques.

    ⚠️ Rien n'est écrit en dur dans les scènes : si la maison change un prix,
    la démonstration change avec elle. C'est le sujet même de ce kit.
    """
    def prix(nom):
        return catalogue.trouver(nom).prix

    if identifiant == "braise-dor":
        t, g, gl = prix("Tilapia braisé"), prix("Sauce gombo"), prix("Glace")
        from agent.catalogue import formater_fcfa as f
        return {"tilapia1": f(t.montants[0][1]), "tilapia2": f(t.montants[1][1]),
                "gombo1": f(g.bas), "gombo2": f(g.haut),
                "glace1": f(gl.montants[0][1]), "glace2": f(gl.montants[1][1]),
                "glace3": f(gl.montants[2][1])}
    from agent.catalogue import formater_fcfa as f
    robe = catalogue.trouver("Robe de cérémonie")
    return {"p1": f(robe.prix.montants[0][1]), "p2": f(robe.prix.montants[1][1]),
            "d1": robe.delai.split(" · ")[0]}


def main() -> int:
    # Le garde-fou journalise en avertissement quand il bloque ; ici on l'affiche
    # nous-mêmes, en couleur et à sa place. Deux fois la même information brouille
    # la démonstration.
    logging.disable(logging.WARNING)
    identifiant = sys.argv[1] if len(sys.argv) > 1 else "braise-dor"
    if identifiant not in SCENES:
        print(f"Scènes disponibles : {', '.join(SCENES)}")
        return 1

    maison = maisons_mod.charger(RACINE_KIT / "maisons" / f"{identifiant}.yaml")
    # Le numéro du patron est simulé pour la démonstration ; en production il
    # vient de la fiche, et le serveur refuse de démarrer sans lui.
    maison.numero_patron = PATRON

    scenes = SCENES[identifiant]
    repliques = []
    for _, suite, _ in scenes:
        repliques.extend(suite)

    canal = CanalConsole()
    memoire = Memoire(Path(tempfile.mkdtemp()) / "demo.db")
    service = Service(maison, RACINE_KIT.parent, memoire, canal,
                      client=FauxModele([]))
    vals = valeurs(service.catalogue, identifiant)
    service.cerveau._client = FauxModele([
        r if isinstance(r, tuple) else r.format(**vals) for r in repliques])

    largeur = 74
    print("\n" + "═" * largeur)
    print(f"  {maison.nom.upper()} — l'agent WhatsApp".center(largeur - 2))
    print("═" * largeur)
    print(f"  Carte lue à l'instant dans {service.catalogue.source}")
    print(f"  {service.garde.resume()}")
    print("  Réponses de l'agent : écrites d'avance (pas de clé ici).")
    print("  Carte, garde-fou, mémoire, escalades : RÉELS.")
    print("═" * largeur)

    for question, _, note in scenes:
        vus = len(canal.envoyes)
        print(f"\n  \033[1m▸ Le client\033[0m  {question}")
        traitement = service.traiter(CLIENT, question)
        reponse = traitement.reponse

        etiquette = "◂ L'agent  "
        for destinataire, texte in canal.envoyes[vus:]:
            if destinataire == CLIENT:
                for i, ligne in enumerate(texte.split("\n")):
                    marge = etiquette if i == 0 else " " * len(etiquette)
                    print(f"    \033[32m{marge}\033[0m{ligne}")

        if reponse.verdict and not reponse.verdict.sur:
            print(f"    \033[31m⛔ GARDE-FOU  {reponse.verdict.explication()}\033[0m")
            print("    \033[31m   → le message du modèle N'EST PAS PARTI.\033[0m")

        for destinataire, texte in canal.envoyes[vus:]:
            if destinataire == PATRON:
                print("    \033[33m📱 Le patron reçoit :\033[0m")
                for ligne in texte.split("\n"):
                    print(f"    \033[33m│\033[0m {ligne}")
        print(f"    \033[2m{note}\033[0m")

    print("\n" + "═" * largeur)
    fenetre = memoire.fenetre_ouverte(maison.id, CLIENT)
    print(f"  Fenêtre de 24 h ouverte : {fenetre} · "
          f"{len(memoire.historique(maison.id, CLIENT, 100))} tours en mémoire")
    print("═" * largeur + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
