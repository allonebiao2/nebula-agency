# -*- coding: utf-8 -*-
"""
Fabrique le carnet d'un client, et rend le lien à lui envoyer.

POURQUOI CET OUTIL TOURNE SUR LE PC, ET PAS DANS LE SITE
  Les 187 fiches sont la marchandise. Si elles partaient dans le paquet
  JavaScript public, n'importe qui les lirait sans payer, en trois secondes.
  Elles ne quittent donc jamais ce dépôt, sauf pour le client qui les a
  achetées, et uniquement les siennes.

L'EXCLUSIVITÉ DE 90 JOURS EST TENUE ICI
  Une fiche déjà livrée à quelqu'un dans les 90 derniers jours ne repart pas
  chez un autre. C'est vérifié en base avant de composer, pas promis.

USAGE
    python piste/_carnet.py --voir
        montre ce qui est disponible, sans rien écrire

    python piste/_carnet.py --metier couture --ville lome --n 50 \\
        --options teste,message --offre "je propose une assurance sante" \\
        --prenom Adjoa --nom Kponou --email adjoa@exemple.com \\
        --tel 22997000000 --ref PISTE-4471 --ecrire
"""
import argparse, hashlib, io, json, re, secrets, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "_documents/nebula-agency/vente/prospection"))
from _donnees import PROSPECTS  # noqa: E402

SITE = "https://piste.nebula-agency.online"
COTONOU = {"Cotonou", "Abomey-Calavi", "Godomey", "Cocotomey"}
METIERS = {
    "couture": ("Ateliers de couture", "atelier de couture"),
    "restaurant": ("Restaurants, maquis et bars", "restaurant"),
    "patisserie": ("Pâtisseries et boulangeries", "pâtisserie"),
}
VILLES = {
    "cotonou": "Cotonou et ses environs",
    "benin-autres": "Autres villes du Bénin",
    "lome": "Lomé",
    "togo-autres": "Autres villes du Togo",
}
PRIX = {"base": 100, "teste": 150, "sansSite": 100, "dirigeant": 100, "message": 50}
PALIERS = [(500, 0.30), (200, 0.20), (50, 0.10)]


def ville_cle(pays, v):
    if pays == "BJ":
        return "cotonou" if v in COTONOU else "benin-autres"
    return "lome" if v == "Lomé" else "togo-autres"


def est_fixe(pays, n):
    if not n:
        return True
    return n.startswith(("0121", "0120")) if pays == "BJ" else n.startswith("22")


def message_pour(f, offre):
    _, singulier = METIERS[f["metier"]]
    lieu = ", ".join(x for x in (f.get("quartier"), f["localite"]) if x)
    phrase = (offre or "").strip().rstrip(". ")
    corps = (
        f"{phrase[0].upper()}{phrase[1:]}."
        if phrase
        else "Je vous écris au sujet de ce que je propose aux commerces comme le vôtre."
    )
    return "\n\n".join(
        [
            "Bonjour,",
            f"Je vous écris au sujet de {f['nom']}, votre {singulier} à {lieu}.",
            corps,
            "Est-ce que je peux vous en dire deux mots ? Ça prend deux minutes.",
        ]
    )


def viviers():
    """Tout ce qui est relevé, rangé par métier et par ville. Les fixes restent :
    ils se vendent, on les appelle au lieu de leur écrire."""
    par = {}
    for nom, pays, ville, quartier, metier, num in PROSPECTS:
        if not num or metier not in METIERS:
            continue
        k = (metier, ville_cle(pays, ville))
        par.setdefault(k, []).append(
            dict(
                nom=nom,
                metier=metier,
                ville=k[1],
                localite=ville,
                quartier=quartier,
                pays=pays,
                numero=num,
            )
        )
    return par


def connexion():
    import psycopg
    from psycopg.rows import dict_row

    dsn = next(
        (
            l.split("=", 1)[1].strip()
            for l in io.open(RACINE / "secrets/supabase.env", encoding="utf-8")
            if l.startswith("DATABASE_URL=")
        ),
        None,
    )
    if not dsn:
        raise SystemExit("  DATABASE_URL introuvable dans secrets/supabase.env")
    c = psycopg.connect(dsn, row_factory=dict_row)
    c.prepare_threshold = None  # obligatoire avec le pooler Supabase
    return c


def deja_livrees(c):
    """Les fiches réservées : livrées à quelqu'un dans les 90 derniers jours."""
    limite = datetime.now(timezone.utc) - timedelta(days=90)
    pris = {}
    for r in c.execute(
        "select jeton, fiches, cree_le from piste.carnets where cree_le > %s", (limite,)
    ).fetchall():
        for f in r["fiches"]:
            pris[f["nom"]] = r["jeton"]
    return pris


def calcul(n, options):
    unitaire = PRIX["base"] + sum(PRIX[o] for o in options)
    sous = unitaire * n
    taux = next((t for s, t in PALIERS if n >= s), 0)
    remise = round(sous * taux)
    return dict(unitaire=unitaire, sousTotal=sous, taux=taux, remise=remise, total=sous - remise)


def main():
    a = argparse.ArgumentParser(add_help=True)
    a.add_argument("--voir", action="store_true", help="montre le disponible, n'écrit rien")
    a.add_argument("--metier", choices=list(METIERS))
    a.add_argument("--ville", choices=list(VILLES))
    a.add_argument("--n", type=int)
    a.add_argument("--options", default="", help="teste,sansSite,dirigeant,message")
    a.add_argument("--offre", default="")
    a.add_argument("--prenom", default="")
    a.add_argument("--nom", default="")
    a.add_argument("--email", default="")
    a.add_argument("--tel", default="")
    a.add_argument("--ref", default="")
    a.add_argument("--ecrire", action="store_true", help="écrit vraiment le carnet")
    o = a.parse_args()

    par = viviers()
    c = connexion()
    pris = deja_livrees(c)

    if o.voir or not (o.metier and o.ville and o.n):
        print(f"\n  {len(pris)} fiche(s) réservée(s) par un carnet des 90 derniers jours.\n")
        print(f"  {'métier':<12} {'ville':<14} {'relevé':>7} {'libre':>7}")
        print("  " + "-" * 44)
        for k in sorted(par):
            libres = [f for f in par[k] if f["nom"] not in pris]
            print(f"  {k[0]:<12} {k[1]:<14} {len(par[k]):>7} {len(libres):>7}")
        print("\n  Pour composer un carnet, relancez avec --metier --ville --n --ecrire")
        return 0

    options = [x for x in re.split(r"[,\s]+", o.options) if x]
    for x in options:
        if x not in ("teste", "sansSite", "dirigeant", "message"):
            raise SystemExit(f"  option inconnue : {x}")
    if "message" in options and len(o.offre.strip()) < 8:
        raise SystemExit("  --offre est obligatoire avec l'option « message »")

    libres = [f for f in par.get((o.metier, o.ville), []) if f["nom"] not in pris]
    # Celles qui portent un quartier d'abord : une fiche située se travaille mieux.
    libres.sort(key=lambda f: (not f["quartier"], f["nom"]))

    if "teste" in options:
        # ⚠️ Le numéro « testé » se teste À LA MAIN avant l'envoi. Cet outil ne
        # peut pas composer un numéro : il ne fait que marquer la promesse, et
        # c'est Mongazi qui la tient. On ne coche jamais ça à la légère.
        print("  ⚠️  Option « numéro testé » : appelez chaque numéro AVANT d'envoyer.")
        print("      Une fiche qui ne répond pas ne part pas, elle est remplacée.\n")

    if len(libres) < o.n:
        raise SystemExit(
            f"  Pas assez de fiches libres : {len(libres)} disponibles, {o.n} demandées.\n"
            f"  Le reste est réservé par d'autres carnets (exclusivité 90 jours)."
        )

    choisies = libres[: o.n]
    for f in choisies:
        f["fixe"] = est_fixe(f["pays"], f["numero"])
        if "message" in options and not f["fixe"]:
            f["message"] = message_pour(f, o.offre)
        if "sansSite" in options:
            f["sansSite"] = True

    prix = calcul(o.n, options)
    jeton = secrets.token_urlsafe(24)
    ref = o.ref or "PISTE-" + secrets.token_hex(2).upper()
    metier_nom, _ = METIERS[o.metier]

    print(f"  {len(choisies)} fiches composées · {sum(1 for f in choisies if f['fixe'])} fixes")
    print(f"  {metier_nom} · {VILLES[o.ville]}")
    print(f"  {prix['total']} F  (unitaire {prix['unitaire']} F, remise {int(prix['taux']*100)} %)")

    if not o.ecrire:
        print("\n  Rien n'a été écrit. Ajoutez --ecrire pour fabriquer le carnet.")
        return 0

    c.execute(
        """insert into piste.carnets(jeton, reference, client, commande, fiches)
           values (%s,%s,%s,%s,%s)""",
        (
            jeton,
            ref,
            json.dumps(
                dict(prenom=o.prenom, nom=o.nom, email=o.email, tel=o.tel), ensure_ascii=False
            ),
            json.dumps(
                dict(
                    metier=o.metier,
                    metierNom=metier_nom,
                    ville=o.ville,
                    villeNom=VILLES[o.ville],
                    n=o.n,
                    options=options,
                    offre=o.offre,
                    **prix,
                ),
                ensure_ascii=False,
            ),
            json.dumps(choisies, ensure_ascii=False),
        ),
    )
    c.commit()

    lien = f"{SITE}/#/carnet/{jeton}"
    prenom = o.prenom or "Bonjour"
    courriel = f"""Objet : Votre carnet PISTE est prêt · {ref}

Bonjour {prenom},

Votre carnet est prêt : {o.n} {metier_nom.lower()} à {VILLES[o.ville]}.

Il s'ouvre ici, et ce lien est à vous :
{lien}

Comment s'en servir, en trois lignes :
  1. Ouvrez le lien sur votre téléphone.
  2. Appuyez sur « Écrire sur WhatsApp » : la conversation s'ouvre, le message
     est déjà dedans. Les lignes fixes n'ont pas WhatsApp, on les appelle.
  3. Marquez chaque fiche au fur et à mesure. Votre avancement se garde, même
     si vous fermez.

Un numéro ne répond plus ? Appuyez sur « Injoignable ? » dans le carnet : la
fiche est remplacée sans frais, et la remplaçante apparaît dans ce même lien.

Ces fiches sont à vous seul pendant 90 jours.

Gardez ce lien : il ne périme pas. Perdu ? Écrivez-nous, on vous le renvoie.

NEBULA Agency
"""
    dossier = RACINE / "piste/_carnets"
    dossier.mkdir(exist_ok=True)
    io.open(dossier / f"{ref}.txt", "w", encoding="utf-8", newline="").write(
        f"{lien}\n\n{courriel}"
    )

    print(f"\n  ✓ carnet écrit · {ref}")
    print(f"\n  LE LIEN À ENVOYER\n  {lien}")
    print(f"\n  Le courriel prêt à copier est dans piste/_carnets/{ref}.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
