"""L'ASSISTANT D'INSTALLATION — de « rien » à « l'agent répond », en quelques questions.

    python whatsapp-agent/installer.py

Il pose ce que seul l'humain sait (les numéros, les jetons), écrit `.env` et
complète la fiche de la maison, lance les contrôles, et affiche l'adresse exacte
à recopier chez le fournisseur. Il ne devine rien : ce qu'on ne lui dit pas
reste vide, et il le dit.

⛔ IL N'INVENTE JAMAIS UN NUMÉRO. C'est la règle qui a fait laisser la fiche
d'Au Braisé d'Or vide : le dépôt en porte deux, l'enseigne un troisième. Un
numéro deviné, ce sont les commandes d'un restaurant envoyées chez quelqu'un
d'autre.
"""
from __future__ import annotations

import re
import secrets
import subprocess
import sys
from pathlib import Path

RACINE_KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE_KIT))

from agent import maison as maisons_mod          # noqa: E402
from agent.service import charger_catalogue      # noqa: E402

CANAUX = {
    "1": ("whapi", "Whapi.cloud — le WhatsApp du client, branché aujourd'hui",
          ["Créez un compte sur whapi.cloud et un « channel ».",
           "Scannez le QR code depuis le téléphone de la maison (comme WhatsApp Web).",
           "Copiez le jeton du channel."],
          "⚠️ Ce n'est pas l'API officielle : c'est rapide et sans paperasse, mais "
          "WhatsApp peut suspendre un numéro qui automatise par ce chemin. Parfait "
          "pour un pilote ; pour du définitif, Meta."),
    "2": ("meta", "Meta Cloud API — l'officiel, demande la vérification d'entreprise",
          ["Meta Business Manager → vérifiez l'entreprise du client.",
           "WhatsApp Business Platform → ajoutez le numéro DU CLIENT.",
           "Relevez le Phone Number ID, un jeton permanent, et l'App Secret."],
          "Gratuit jusqu'à 1 000 conversations de service par mois. C'est ce qu'on "
          "livre quand la maison veut du durable."),
    "3": ("twilio", "Twilio — le bac à sable, pour montrer que ça marche en une heure",
          ["Console Twilio → WhatsApp Sandbox.",
           "Relevez le SID, le jeton, et le numéro d'émission."],
          "Numéro PARTAGÉ : la marque du client n'apparaît pas. Démonstration "
          "seulement."),
}


def demander(question: str, defaut: str = "", obligatoire: bool = False) -> str:
    suffixe = f" [{defaut}]" if defaut else ""
    while True:
        reponse = input(f"  {question}{suffixe} : ").strip() or defaut
        if reponse or not obligatoire:
            return reponse
        print("     (il en faut une : sans elle, l'agent ne peut pas démarrer)")


def numero(question: str, obligatoire: bool = True) -> str:
    """Un numéro WhatsApp, réduit à ses chiffres, avec l'indicatif pays.

    ⚠️ On refuse un numéro trop court : « 0197085576 » sans le 229 ne joint
    personne, et l'erreur ne se voit qu'au premier client perdu.
    """
    while True:
        brut = demander(question, obligatoire=obligatoire)
        if not brut and not obligatoire:
            return ""
        chiffres = re.sub(r"\D", "", brut)
        if len(chiffres) >= 10:
            return chiffres
        print(f"     « {brut} » fait {len(chiffres)} chiffres. Il faut l'indicatif "
              f"pays : 229 pour le Bénin, 225 Côte d'Ivoire, 221 Sénégal, 228 Togo.")


def main() -> int:
    fiches = sorted((RACINE_KIT / "maisons").glob("*.yaml"))
    if not fiches:
        print("Aucune fiche dans maisons/. Créez-en une d'abord (voir le README).")
        return 1

    print("\n" + "═" * 70)
    print("  LE STANDARD — installation".center(70))
    print("═" * 70)

    print("\n  Quelle maison met-on en ligne ?")
    for i, f in enumerate(fiches, 1):
        m = maisons_mod.charger(f)
        try:
            taille = f"{len(charger_catalogue(m, RACINE_KIT.parent))} articles"
        except Exception as exc:  # noqa: BLE001
            taille = f"⛔ catalogue illisible : {exc}"
        pret = "prête" if m.prete[0] else "incomplète"
        print(f"    {i}. {m.nom} — {taille} — {pret}")
    choix = demander("Numéro", "1")
    try:
        fiche = fiches[int(choix) - 1]
    except (ValueError, IndexError):
        print("  Choix inconnu.")
        return 1
    maison = maisons_mod.charger(fiche)
    print(f"\n  → {maison.nom}\n")

    # --- les deux numéros -------------------------------------------------
    print("  ── Les numéros ──")
    if maison.numero_whatsapp:
        print(f"  Numéro de la maison, déjà connu : +{maison.numero_whatsapp}")
        if demander("Le changer ? (o/N)", "n").lower().startswith("o"):
            maison.numero_whatsapp = numero("Numéro WhatsApp de la maison")
    else:
        print("  Le numéro WhatsApp DE LA MAISON — celui sur lequel les clients écrivent.")
        maison.numero_whatsapp = numero("Numéro WhatsApp de la maison")

    print("\n  Le numéro qui reçoit les alertes : commandes, et tout ce que l'agent")
    print("  ne sait pas. C'est souvent le patron, ou la personne au comptoir.")
    maison.numero_patron = numero("Numéro d'alerte", obligatoire=True) \
        or maison.numero_patron

    # --- le canal ---------------------------------------------------------
    print("\n  ── Par où passe WhatsApp ? ──")
    for cle, (_, titre, _, note) in CANAUX.items():
        print(f"    {cle}. {titre}\n       {note}")
    cle = demander("Numéro", "1")
    if cle not in CANAUX:
        print("  Choix inconnu.")
        return 1
    canal, _, etapes, _ = CANAUX[cle]
    print(f"\n  Avant de continuer, chez le fournisseur :")
    for i, etape in enumerate(etapes, 1):
        print(f"    {i}. {etape}")
    print()

    variables = {"WA_CANAL": canal}
    secret = ""
    if canal == "whapi":
        variables["WA_WHAPI_TOKEN"] = demander("Jeton Whapi", obligatoire=True)
        secret = secrets.token_urlsafe(24)
        variables["WA_WHAPI_SECRET"] = secret
    elif canal == "meta":
        variables["WA_META_TOKEN"] = demander("Jeton permanent Meta", obligatoire=True)
        variables["WA_META_PHONE_ID"] = demander("Phone Number ID", obligatoire=True)
        variables["WA_META_SECRET"] = demander("App Secret", obligatoire=True)
        variables["WA_META_VERIFY"] = secrets.token_urlsafe(16)
    else:
        variables["WA_TWILIO_SID"] = demander("Account SID", obligatoire=True)
        variables["WA_TWILIO_TOKEN"] = demander("Auth Token", obligatoire=True)
        variables["WA_TWILIO_FROM"] = demander("Numéro d'émission (+1415…)",
                                               obligatoire=True)

    print()
    cle_api = demander("Clé API Anthropic (sk-ant-…)", obligatoire=True)
    variables["ANTHROPIC_API_KEY"] = cle_api
    adresse = demander("Adresse publique du serveur (https://…), si vous la connaissez")

    # --- on écrit ---------------------------------------------------------
    fiche_texte = fiche.read_text(encoding="utf-8")
    for champ, valeur in (("numero_whatsapp", maison.numero_whatsapp),
                          ("numero_patron", maison.numero_patron)):
        # ⚠️ ON GARDE LE COMMENTAIRE DE LA LIGNE. Il porte la provenance du
        # numéro (« posé et vérifié en ligne le 2026-08-01 »), et dans ce dépôt
        # la provenance vaut autant que la valeur : c'est elle qui dit si on
        # peut s'y fier. Un remplacement naïf l'effaçait sans un mot.
        motif = re.compile(rf'^{champ}:(?P<valeur>[^#\n]*)(?P<note>#.*)?$', re.M)
        trouve = motif.search(fiche_texte)
        if trouve:
            note = (trouve.group("note") or "").strip()
            # …sauf le commentaire qui décrivait le VIDE : « à remplir », « vide
            # exprès ». Le garder à côté d'une valeur posée ferait mentir la fiche.
            if note and re.search(r"à remplir|vide exprès|à compléter", note, re.I):
                note = ""
            ligne = f'{champ}: "{valeur}"' + (f'   {note}' if note else "")
            fiche_texte = fiche_texte[:trouve.start()] + ligne + fiche_texte[trouve.end():]
        else:
            fiche_texte += f'\n{champ}: "{valeur}"\n'
    fiche.write_text(fiche_texte, encoding="utf-8")

    env = RACINE_KIT / ".env"
    lignes = ["# Écrit par installer.py. NE JAMAIS COMMITER CE FICHIER.",
              *[f"{c}={v}" for c, v in variables.items()]]
    env.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"\n  ✓ {fiche.name} complété")
    print(f"  ✓ {env.name} écrit ({len(variables)} variables)")

    # --- on contrôle ------------------------------------------------------
    print("\n  ── Contrôles ──")
    resultat = subprocess.run([sys.executable, str(RACINE_KIT / "_qc.py")],
                              capture_output=True, text=True)
    derniere = [l for l in resultat.stdout.splitlines() if "contrôles" in l]
    print("  " + (derniere[-1] if derniere else "⛔ la suite n'a rien rendu"))
    if resultat.returncode != 0:
        print("  ⛔ Des contrôles sont rouges. On ne met rien en ligne comme ça.")
        for ligne in resultat.stdout.splitlines():
            if ligne.strip().startswith("✗"):
                print("   " + ligne)
        return 1

    # --- ce qu'il reste à faire, à la main --------------------------------
    base = adresse.rstrip("/") if adresse else "https://VOTRE-ADRESSE"
    route = {"whapi": "whapi", "meta": "webhook", "twilio": "twilio"}[canal]
    print("\n" + "═" * 70)
    print("  IL RESTE DEUX GESTES".center(70))
    print("═" * 70)
    print(f"\n  1. Démarrer le serveur :")
    print(f"       cd {RACINE_KIT.name} && python serveur.py --racine ..")
    print(f"\n  2. Chez le fournisseur, pointer le webhook sur :")
    print(f"       {base}/{route}/{maison.id}")
    if canal == "whapi":
        print(f"\n     Et ajouter ce « custom header » au webhook, sans quoi la porte")
        print(f"     reste ouverte à n'importe qui :")
        print(f"       X-Nebula-Secret: {secret}")
    if canal == "meta":
        print(f"\n     Mot de passe de vérification à recopier chez Meta :")
        print(f"       {variables['WA_META_VERIFY']}")
        print("     Et cochez le champ « messages ».")
    print(f"\n  Pour essayer sans attendre :")
    print(f"       python {RACINE_KIT.name}/simuler.py {maison.id}")
    print()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n  Interrompu. Rien n'a été écrit si vous n'êtes pas allé au bout.")
        raise SystemExit(1)
