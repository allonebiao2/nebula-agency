# -*- coding: utf-8 -*-
"""
Met le site à jour depuis la base : le stock affiché, et les fiches d'aperçu.

DEUX CHOSES, ET UNE RÈGLE
  1. Le **stock** que le générateur affiche en direct. Ce sont des NOMBRES :
     ils peuvent vivre dans le dépôt public sans rien donner à personne.
  2. Les **fiches d'aperçu** montrées avant paiement. Ce sont de vrais
     commerces, et leur numéro est donc **coupé à la source**.

⚠️ LA FUITE QUI A ÉTÉ CORRIGÉE ICI
  Le masquage se faisait à l'affichage : le numéro complet partait quand même
  dans le paquet JavaScript, et se lisait en trois secondes. Un masque qui
  n'existe qu'à l'écran ne masque rien. Désormais les quatre derniers chiffres
  n'existent nulle part dans le site.

    python piste/_stock.py
"""
import io, re, sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "piste/src/donnees.js"
VILLES = ["cotonou", "benin-autres", "lome", "togo-autres", "abidjan"]
METIERS = ["couture", "restaurant", "patisserie", "autre"]


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
        raise SystemExit("  DATABASE_URL introuvable")
    c = psycopg.connect(dsn, row_factory=dict_row)
    c.prepare_threshold = None
    return c


def couper(numero):
    """Retire les quatre derniers chiffres, pour de bon.

    Le site n'a jamais besoin d'un numéro entier : il ne sert qu'à montrer que
    la fiche est vraie et complète. Ce qu'on ne publie pas ne fuit pas."""
    return numero[:-4] + "XXXX"


def main():
    c = connexion()

    # ---- le stock, hors de ce qui est déjà réservé ---------------------------
    reserve = set()
    for r in c.execute(
        "select fiches from piste.carnets where cree_le > now() - interval '90 days'"
    ).fetchall():
        for f in r["fiches"]:
            reserve.add(f["nom"])

    compte = {}
    for r in c.execute(
        "select metier, ville, nom from piste.fiches where actif"
    ).fetchall():
        if r["nom"] in reserve:
            continue
        compte[f"{r['metier']}|{r['ville']}"] = compte.get(f"{r['metier']}|{r['ville']}", 0) + 1

    lignes = []
    for m in METIERS:
        for v in VILLES:
            lignes.append(f"  '{m}|{v}': {compte.get(f'{m}|{v}', 0)},")
    bloc_stock = "export const STOCK = {\n" + "\n".join(lignes) + "\n}"

    # ---- trois fiches d'aperçu par combinaison, numéro coupé ----------------
    fiches = []
    for m in METIERS[:3]:
        for v in VILLES[:4]:
            for r in c.execute(
                """select nom, metier, ville, localite, quartier, pays, numero
                   from piste.fiches
                   where actif and not fixe and metier=%s and ville=%s and quartier <> ''
                   order by nom limit 3""",
                (m, v),
            ).fetchall():
                if r["nom"] in reserve:
                    continue
                fiches.append(r)

    def js(x):
        return "'" + str(x).replace("\\", "\\\\").replace("'", "\\'") + "'"

    corps = "\n".join(
        "  {\n"
        f"    nom: {js(f['nom'])},\n"
        f"    metier: '{f['metier']}', ville: '{f['ville']}',\n"
        f"    localite: {js(f['localite'])}, quartier: {js(f['quartier'])},\n"
        f"    pays: '{f['pays']}', numero: '{couper(f['numero'])}',\n"
        "  },"
        for f in fiches
    )
    bloc_fiches = "export const FICHES = [\n" + corps + "\n]"

    # ---- les chiffres de la preuve -----------------------------------------
    # TOTAL_FICHES et REPARTITION se calculent deja depuis STOCK. Restent le
    # nombre de fixes et la date du releve, qui doivent suivre : la vitrine
    # annoncait encore « 187 commerces » alors qu'il y en avait presque mille.
    fixes = c.execute(
        "select count(*) n from piste.fiches where actif and fixe"
    ).fetchone()["n"]
    jour = c.execute("select max(revu_le) d from piste.fiches where actif").fetchone()["d"]
    MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"]
    date_texte = f"{jour.day} {MOIS[jour.month - 1]} {jour.year}" if jour else ""

    # ---- on repose tout ----------------------------------------------------
    s = io.open(DONNEES, encoding="utf-8").read()
    for nom, bloc in (("STOCK", bloc_stock), ("FICHES", bloc_fiches)):
        deb = s.index(f"export const {nom} = ")
        fin = s.index("\n}", deb) + 2 if nom == "STOCK" else s.index("\n]", deb) + 2
        s = s[:deb] + bloc + s[fin:]
    s = re.sub(r"export const NOMBRE_FIXES = \d+", f"export const NOMBRE_FIXES = {fixes}", s)
    if date_texte:
        s = re.sub(
            r"export const DATE_RELEVE = '[^']*'",
            f"export const DATE_RELEVE = '{date_texte}'",
            s,
        )
    io.open(DONNEES, "w", encoding="utf-8", newline="").write(s)

    total = sum(compte.values())
    print(f"  stock à jour : {total} fiches libres")
    for m in METIERS[:3]:
        d = " · ".join(f"{v} {compte.get(f'{m}|{v}', 0)}" for v in VILLES[:4])
        print(f"    {m:<11} {d}")
    print(f"  {len(fiches)} fiches d'aperçu, numéros coupés à la source")
    print(f"  {fixes} lignes fixes · relevé au {date_texte}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
