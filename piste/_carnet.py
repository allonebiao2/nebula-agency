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
# ⚠️ Doit rester identique a src/prix.js. Une fiche coute entre 100 F et 250 F,
# jamais plus : les quatre supplements reunis valent exactement 150 F.
PRIX = {"base": 100, "teste": 60, "sansSite": 40, "dirigeant": 30, "message": 20}
assert PRIX["base"] + sum(v for k, v in PRIX.items() if k != "base") == 250, (
    "le plafond de 250 F par fiche est casse"
)
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


def viviers(c):
    """Tout ce qui est relevé, rangé par métier et par ville.

    ⚠️ Lu DANS LA BASE, plus dans le dépôt : `allonebiao2/nebula-agency` est
    public, et une fiche rangée dans un fichier y serait lisible gratuitement
    par tout le monde. Le dépôt garde les outils, la base garde la marchandise.

    Les lignes fixes restent du lot : elles se vendent, on les appelle au lieu
    de leur écrire, et le carnet le dit sur la fiche."""
    par = {}
    for r in c.execute(
        """select nom, metier, ville, localite, quartier, pays, numero, fixe,
                  site, dirigeant
           from piste.fiches where actif order by nom"""
    ).fetchall():
        par.setdefault((r["metier"], r["ville"]), []).append(dict(r))
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


def relances(c, jours=7):
    """Les carnets livrés il y a `jours` jours ou plus, et jamais relancés.

    POURQUOI CE MESSAGE EXISTE
    Un acheteur content qui n'entend plus parler de vous ne recommande pas. Et
    surtout : c'est la SEULE façon de savoir si les fiches ont vraiment servi.
    C'est le chiffre qui dira si le barème tient et si la donnée est bonne.

    Le message n'est pas générique : il lit les marques que le client a posées
    dans son carnet et lui parle de SES résultats. « Vous avez marqué 4
    rendez-vous » vaut cent fois « alors, ça s'est bien passé ? »."""
    from datetime import datetime, timedelta, timezone

    limite = datetime.now(timezone.utc) - timedelta(days=jours)
    sortie = []
    for r in c.execute(
        """select k.jeton, k.reference, k.client, k.commande, k.cree_le,
                  (select count(*) from piste.retours t where t.jeton = k.jeton) marques,
                  (select count(*) from piste.retours t
                    where t.jeton = k.jeton and t.marque = 'rdv') rdv,
                  (select count(*) from piste.retours t
                    where t.jeton = k.jeton and t.marque = 'vendu') vendu,
                  (select count(*) from piste.retours t
                    where t.jeton = k.jeton and t.marque = 'injoignable') injoignables
           from piste.carnets k
           where k.cree_le < %s
           order by k.cree_le""",
        (limite,),
    ).fetchall():
        sortie.append(r)
    return sortie


def texte_relance(r):
    cl = r["client"] or {}
    cmd = r["commande"] or {}
    prenom = (cl.get("prenom") or "").strip() or "Bonjour"
    n = cmd.get("n") or 0

    lignes = [f"Bonjour {prenom},", ""]
    if r["marques"]:
        # On lui parle de SES chiffres. Il sait qu'on regarde, c'est écrit dans
        # son carnet : il n'y a rien à cacher, et ça rend le message crédible.
        bouts = []
        if r["rdv"]:
            bouts.append(f"{r['rdv']} rendez-vous")
        if r["vendu"]:
            bouts.append(f"{r['vendu']} vente" + ("s" if r["vendu"] > 1 else ""))
        if bouts:
            lignes.append(
                f"Dans votre carnet {r['reference']}, vous avez marqué "
                + " et ".join(bouts)
                + ". Bravo."
            )
        else:
            lignes.append(
                f"J'ai vu que vous aviez commencé à travailler votre carnet {r['reference']}."
            )
        lignes.append("")
        lignes.append("Une question simple : combien de ces commerces vous ont répondu ?")
    else:
        lignes.append(
            f"Votre carnet {r['reference']} vous a été livré il y a une semaine, "
            f"avec {n} fiches."
        )
        lignes.append("")
        lignes.append(
            "Vous avez eu le temps de vous en servir ? Si quelque chose bloque, "
            "dites-le moi : c'est plus utile pour moi que si vous ne dites rien."
        )
    lignes.append("")
    lignes.append(
        "Votre réponse me sert vraiment : c'est comme ça que je choisis mieux "
        "les fiches de la prochaine fois."
    )
    if r["injoignables"]:
        lignes.append("")
        lignes.append(
            f"Vous avez signalé {r['injoignables']} fiche"
            + ("s" if r["injoignables"] > 1 else "")
            + " injoignable"
            + ("s" if r["injoignables"] > 1 else "")
            + ". Je vous les remplace, c'est prévu et c'est sans frais."
        )
    lignes.append("")
    lignes.append("NEBULA Agency")
    return "\n".join(lignes)


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
    a.add_argument("--relances", action="store_true", help="les messages à J+7 à envoyer")
    o = a.parse_args()

    c = connexion()

    if o.relances:
        l = relances(c)
        if not l:
            print("\n  Aucun carnet livré depuis plus de 7 jours. Rien à relancer.")
            return 0
        print(f"\n  {len(l)} carnet(s) à relancer :\n")
        for r in l:
            cl = r["client"] or {}
            wa = (cl.get("tel") or cl.get("whatsapp") or "").strip()
            print("  " + "─" * 66)
            print(f"  {r['reference']} · {cl.get('prenom','')} {cl.get('nom','')} · {wa or 'pas de numéro'}")
            def _s(n):
                return "s" if n > 1 else ""

            print(
                f"  {r['marques']} marque{_s(r['marques'])}"
                f" · {r['rdv']} rendez-vous"
                f" · {r['vendu']} vendu{_s(r['vendu'])}"
                f" · {r['injoignables']} injoignable{_s(r['injoignables'])}"
            )
            if wa:
                from urllib.parse import quote
                print(f"  https://wa.me/{wa}?text={quote(texte_relance(r))}")
            print()
            print("  " + texte_relance(r).replace("\n", "\n"))
            print()
        return 0

    par = viviers(c)
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
        f["fixe"] = bool(f.get("fixe"))
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
