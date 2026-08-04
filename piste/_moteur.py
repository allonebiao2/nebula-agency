# -*- coding: utf-8 -*-
"""
LE MOTEUR · il remplit le vivier tout seul.

POURQUOI IL EXISTE
  187 fiches, 5 à 10 commandes par jour, minimum 10 fiches, et une exclusivité
  de 90 jours qui retire du stock chaque fiche vendue : sept commandes de 30
  fiches et il ne reste plus rien à vendre. Sans moteur, la boutique affiche
  « 0 disponible » le deuxième jour.

POURQUOI PAS VIBE PROSPECTING
  Testé le 2026-08-04, et la réponse est nette. Il connaît 6 779 entreprises au
  Bénin et au Togo, mais ce sont des entreprises inscrites sur LinkedIn :
  banques, cabinets de recrutement, agences de communication. Une recherche
  « restaurant, maquis, couture, tailleur, pâtisserie » y rend 61 résultats,
  dont pas un seul restaurant ni un seul atelier de couture. Et aucune fiche
  d'entreprise ne porte de numéro de téléphone.
  Les commerçants que PISTE vend ne sont pas sur LinkedIn. Ils sont dans les
  annuaires professionnels locaux, et c'est là qu'on va les chercher.

OÙ VONT LES DONNÉES
  ⚠️ Dans la base, JAMAIS dans le dépôt : `allonebiao2/nebula-agency` est
  public. Une fiche rangée dans un fichier du dépôt est lisible par tout le
  monde, gratuitement, et c'est exactement ce qu'on vend.

CE QU'IL RESPECTE
  · `robots.txt` de chaque source, et une requête par seconde au maximum.
  · Le droit à l'oubli : un numéro dans `piste.oubli` n'est jamais réinséré.
  · Aucune donnée de personne physique. L'entreprise, et rien d'autre.

USAGE
    python piste/_moteur.py --voir              ce qu'il y a en base
    python piste/_moteur.py --semer             pose les 187 déjà relevées
    python piste/_moteur.py --collecter         va en chercher de nouvelles
    python piste/_moteur.py --collecter --pages 8
"""
import argparse, hashlib, html as html_lib, io, re, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
COTONOU = {"Cotonou", "Abomey-Calavi", "Godomey", "Cocotomey"}
# Le Grand Abidjan : les communes du district. Tout le reste de la Cote d'Ivoire
# part dans « autres villes », on ne fait pas passer Bouake pour Abidjan.
ABIDJAN = {
    "Abidjan", "Cocody", "Yopougon", "Treichville", "Plateau", "Marcory",
    "Adjame", "Adjamé", "Abobo", "Koumassi", "Port-Bouet", "Port-Bouët",
    "Attecoube", "Attécoubé", "Bingerville", "Songon", "Anyama", "Riviera",
}

# ─────────────────────────── LES VIVIERS ───────────────────────────────────
# Une categorie d'annuaire n'est pas un metier vendable : « boutiques pret-a-
# porter » et « mode vetements textiles » sont le meme client pour l'acheteur.
# On regroupe donc les 96 categories en metiers que le client reconnait.
#
# ⚠️ CE QUI EST VOLONTAIREMENT ECARTE : administrations, ambassades, consulats,
# commissariats, lieux de culte, ordres professionnels, associations, urgences,
# aeroports. Ce ne sont pas des commerces : personne ne leur vend un catalogue,
# et les demarcher serait une perte de temps pour l'acheteur comme pour eux.
METIERS = {
    "couture": ("Couture et mode", "atelier de couture", [
        "ateliers-de-couture", "mode-vetements-textiles", "vente-vetements-textiles",
        "boutiques-pret-a-porter"]),
    "restaurant": ("Restaurants, maquis et bars", "restaurant", [
        "restaurants", "traiteurs", "brasseries"]),
    "patisserie": ("Pâtisseries et boulangeries", "pâtisserie", [
        "boulangeries-patisseries"]),
    "beaute": ("Beauté et bien-être", "salon de beauté", [
        "salon-beaute-esthetique", "bien-etre", "spa-sauna", "hygiene-corporelle-sante"]),
    "alimentation": ("Alimentation et supermarchés", "commerce d'alimentation", [
        "alimentation", "supermarches", "poissoneries", "abattoirs-viande",
        "entreprises-agroalimentaires"]),
    "quincaillerie": ("Quincaillerie et bâtiment", "quincaillerie", [
        "quincailleries", "plomberie-sanitaires", "miroiterie-vitrerie",
        "entreprises-batiment-construction", "societes-specialistes-aluminium"]),
    "auto": ("Auto, moto et pièces", "garage", [
        "automobile-moto", "vente-cycles-motos", "vente-voitures-automobile"]),
    "maison": ("Maison et décoration", "magasin de décoration", [
        "ameublement", "maison-decoration", "produits-entretien", "produits-hygiene"]),
    "sante": ("Santé et pharmacies", "cabinet de santé", [
        "sante", "veterinaires", "pharmacies-veterinaires", "chirurgiens", "cardiologues"]),
    "ecole": ("Écoles et formation", "établissement scolaire", [
        "ecoles-primaires", "ecole-secondaire-technique", "formations-education"]),
    "informatique": ("Informatique et cybercafés", "commerce informatique", [
        "informatique-internet", "cybercafes", "telecommunications"]),
    "imprimerie": ("Imprimerie et communication", "imprimerie", [
        "imprimeries", "communication-publicite", "agences-de-communication", "cartonnerie"]),
    "hotel": ("Hôtels et tourisme", "hôtel", [
        "auberges", "tourisme-et-loisirs"]),
    "immobilier": ("Immobilier", "agence immobilière", [
        "agences-immobilieres", "professionnels-immobilier", "promoteurs-immobiliers"]),
    "transport": ("Transport et voyage", "société de transport", [
        "transports", "courrier-express", "agences-de-voyage"]),
    "services": ("Services aux entreprises", "société de services", [
        "societes-services", "societes-nettoyage-industriel", "societes-gardiennage-securite",
        "societes-securite", "societes-travail-temporaire-interim", "audit-conseil",
        "expert-comptable", "comptabilite-juridique-conseil", "assurances",
        "courtiers-en-assurance"]),
    "artisan": ("Artisans et art", "artisan", [
        "artisans", "galerie-art", "animaux", "vente-articles-sport", "sport"]),
    "commerce": ("Commerces divers", "commerce", [
        "commerces", "commerce-import-export", "societes-negoce", "centrales-achat"]),
}

METIERS_CONNUS = set(METIERS)

# Ce que le moteur va parcourir : chaque categorie, dans chaque pays.
SOURCES = []
for _cle, (_nom, _sing, _cats) in METIERS.items():
    for _c in _cats:
        for _pays, _p in (("BJ", "bj"), ("TG", "tg"), ("CI", "ci")):
            SOURCES.append((f"https://www.goafricaonline.com/{_p}/annuaire/{_c}", _cle, _pays))

ENTETES = {
    # On se présente. Un robot qui ment sur ce qu'il est n'a pas sa place ici.
    "User-Agent": "PISTE/1.0 (NEBULA Agency, Cotonou · contact +229 96 74 07 32)",
    "Accept-Language": "fr",
}
PAUSE = 1.2  # secondes entre deux requêtes, jamais moins


def ville_cle(pays, localite):
    if pays == "BJ":
        return "cotonou" if localite in COTONOU else "benin-autres"
    if pays == "CI":
        return "abidjan" if localite in ABIDJAN else "ci-autres"
    return "lome" if localite.startswith("Lom") else "togo-autres"


def est_fixe(pays, n):
    if not n:
        return True
    if pays == "BJ":
        return n.startswith(("0121", "0120"))
    if pays == "CI":
        # Cote d'Ivoire : les fixes commencent par 2, les mobiles par 0 ou 1.
        return n.startswith("2")
    return n.startswith("22")


def empreinte(nom, numero):
    return hashlib.sha1(f"{nom}|{numero}".encode("utf-8")).hexdigest()[:20]


def normaliser(pays, brut):
    """Rend un numéro national propre, ou rien du tout.

    ⚠️ Au Bénin, seuls les numéros à 10 chiffres fonctionnent depuis le
    1er janvier 2025 (réforme ARCEP du 30 novembre 2024 : le préfixe `01` est
    ajouté devant l'ancien numéro). Un annuaire qui affiche encore 8 chiffres
    donne un numéro MORT : on le complète, on ne le recopie pas."""
    c = re.sub(r"[^\d]", "", brut or "")
    if pays == "BJ":
        c = c[3:] if c.startswith("229") else c
        if len(c) == 8:
            c = "01" + c
        return c if len(c) == 10 else ""
    if pays == "CI":
        # Cote d'Ivoire : 10 chiffres depuis la reforme du 31 janvier 2021.
        # Un annuaire qui affiche encore 8 chiffres donne un numero MORT.
        c = c[3:] if c.startswith("225") else c
        return c if len(c) == 10 else ""
    c = c[3:] if c.startswith("228") else c
    return c if len(c) == 8 else ""


def lire(url):
    r = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(r, timeout=25) as rep:
        return rep.read().decode("utf-8", "replace")


def robots_autorise(hote):
    """On lit `robots.txt` avant de toucher à quoi que ce soit."""
    try:
        txt = lire(f"https://{hote}/robots.txt")
    except Exception:
        return True  # pas de fichier : rien n'est interdit
    interdits = []
    pour_nous = False
    for l in txt.splitlines():
        l = l.strip()
        if l.lower().startswith("user-agent:"):
            pour_nous = l.split(":", 1)[1].strip() in ("*", "PISTE")
        elif pour_nous and l.lower().startswith("disallow:"):
            c = l.split(":", 1)[1].strip()
            if c:
                interdits.append(c)
    return "/" not in interdits


# La forme réelle d'une carte d'annuaire, relevée le 2026-08-04 :
#   · la carte s'ouvre sur  data-collect-event-on-click="{...click_company_card...}"
#   · le nom      <a class="stretched-link ..." href="...">NOM</a>
#   · le numéro   <a href="tel:+229 01 97 27 71 59"
#   · l'adresse   <address ...>quartier,<br/>Ville - Pays</address>
#
# Bonus inattendu : l'annuaire donne le QUARTIER, que le relevé à la main du
# 3 août n'avait pas. Une fiche située se travaille mieux, et vaut plus cher.
RX_CARTE = re.compile(r"click_company_card")
RX_NOM = re.compile(r'stretched-link[^>]*>\s*([^<]{3,90}?)\s*</a>', re.S)
RX_TEL = re.compile(r'href="tel:([^"]+)"')
RX_ADRESSE = re.compile(r"<address[^>]*>(.*?)</address>", re.S)


def _texte(h):
    """⚠️ On décode TOUTES les entités HTML, pas une liste choisie à la main.
    Une liste incomplète laisse passer `&#039;` et on livre au client une fiche
    qui s'appelle « ANTONIO&#039;S COUTURE ». C'est le genre de detail qui fait
    passer un produit payant pour du travail bâclé."""
    h = re.sub(r"<br\s*/?>", "|", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html_lib.unescape(h)
    return re.sub(r"\s+", " ", h).strip()


def depecer(html, metier, pays):
    """Sort les fiches d'une page d'annuaire.

    On découpe sur le marqueur de carte plutôt que sur une balise : une page
    change de balises sans prévenir, alors que le marqueur porte le sens.
    Ce qui n'est pas sûr est jeté, jamais deviné."""
    sortie = []
    for bloc in RX_CARTE.split(html)[1:]:
        bloc = bloc[:4000]  # une carte ne dépasse jamais ça
        mn, mt = RX_NOM.search(bloc), RX_TEL.search(bloc)
        if not (mn and mt):
            continue
        nom = _texte(mn.group(1))
        numero = normaliser(pays, mt.group(1))
        if len(nom) < 3 or not numero:
            continue

        quartier, localite = "", ""
        ma = RX_ADRESSE.search(bloc)
        if ma:
            bouts = [x.strip(" ,") for x in _texte(ma.group(1)).split("|") if x.strip(" ,")]
            if bouts:
                # la dernière ligne porte « Ville - Pays »
                localite = bouts[-1].split(" - ")[0].strip()
                if len(bouts) > 1:
                    quartier = bouts[0]
        sortie.append(
            dict(
                nom=nom,
                metier=metier,
                pays=pays,
                numero=numero,
                localite=localite or ("Cotonou" if pays == "BJ" else "Lomé"),
                quartier=quartier,
            )
        )
    return sortie


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


def poser(c, fiches, source):
    """Insère ce qui est nouveau, rafraîchit ce qui existe. Idempotent.

    Le droit à l'oubli passe avant tout le reste : un numéro qui a demandé à
    disparaître ne revient jamais, quelle que soit la source qui le propose."""
    oubli = {r["numero"] for r in c.execute("select numero from piste.oubli").fetchall()}
    neuves = revues = ignorees = 0
    for f in fiches:
        if f["numero"] in oubli:
            ignorees += 1
            continue
        fid = empreinte(f["nom"], f["numero"])
        r = c.execute(
            """insert into piste.fiches
                 (id,nom,metier,ville,localite,quartier,pays,numero,fixe,source)
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               on conflict (id) do update set revu_le = now(), actif = true
               returning (xmax = 0) as neuve""",
            (
                fid,
                f["nom"],
                f["metier"],
                ville_cle(f["pays"], f["localite"]),
                f["localite"],
                f.get("quartier", ""),
                f["pays"],
                f["numero"],
                est_fixe(f["pays"], f["numero"]),
                source,
            ),
        ).fetchone()
        if r and r["neuve"]:
            neuves += 1
        else:
            revues += 1
    return neuves, revues, ignorees


def semer(c):
    """Pose les 187 déjà relevées à la main le 3 août 2026."""
    sys.path.insert(0, str(RACINE / "_documents/nebula-agency/vente/prospection"))
    from _donnees import PROSPECTS

    fiches = [
        dict(nom=n, metier=m, pays=p, numero=num, localite=v, quartier=q)
        for n, p, v, q, m, num in PROSPECTS
        if num and m in METIERS_CONNUS
    ]
    return poser(c, fiches, "goafricaonline·2026-08-03")


def etat(c):
    print(f"\n  {'métier':<12} {'ville':<14} {'total':>7} {'joignables':>11}")
    print("  " + "-" * 48)
    total = 0
    for r in c.execute(
        """select metier, ville, count(*) n, count(*) filter (where not fixe) mobiles
           from piste.fiches where actif group by metier, ville order by metier, ville"""
    ).fetchall():
        print(f"  {r['metier']:<12} {r['ville']:<14} {r['n']:>7} {r['mobiles']:>11}")
        total += r["n"]
    o = c.execute("select count(*) n from piste.oubli").fetchone()["n"]
    print(f"\n  {total} fiches actives · {o} numéro(s) en droit à l'oubli")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--voir", action="store_true")
    a.add_argument("--semer", action="store_true")
    a.add_argument("--collecter", action="store_true")
    a.add_argument("--pages", type=int, default=4)
    o = a.parse_args()

    c = connexion()

    if o.semer:
        n, r, i = semer(c)
        c.commit()
        print(f"  semé : {n} nouvelles, {r} revues, {i} ignorées (droit à l'oubli)")

    if o.collecter:
        hotes = {u.split("/")[2] for u, _, _ in SOURCES}
        for h in hotes:
            if not robots_autorise(h):
                raise SystemExit(f"  {h} interdit la collecte dans son robots.txt. On s'arrête.")
            print(f"  {h} : robots.txt lu, la collecte est permise")
        total_n = total_r = 0
        for url, metier, pays in SOURCES:
            for page in range(1, o.pages + 1):
                adresse = url if page == 1 else f"{url}?p={page}"
                try:
                    html = lire(adresse)
                except urllib.error.HTTPError as e:
                    print(f"    {metier}/{pays} p{page} : {e.code}, on passe")
                    break
                except Exception as e:
                    print(f"    {metier}/{pays} p{page} : {e}, on passe")
                    break
                fiches = depecer(html, metier, pays)
                if not fiches:
                    break
                n, r, i = poser(c, fiches, f"goafricaonline·{metier}·{pays}")
                c.commit()
                total_n += n
                total_r += r
                print(f"    {metier:<11} {pays} p{page} : {len(fiches):>3} lues · {n:>3} nouvelles")
                time.sleep(PAUSE)
        print(f"\n  collecte finie : {total_n} nouvelles, {total_r} revues")

    if o.voir or not (o.semer or o.collecter):
        etat(c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
