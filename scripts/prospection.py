# -*- coding: utf-8 -*-
"""
La prospection NEBULA : les commerces trouvés sur Google Maps, notés et suivis.

⛔ Aucune donnée ici : ce dépôt est PUBLIC. Les fiches vivent dans Supabase,
table privée `piste.prospection` (RLS active, aucun accès public).
Méthode et messages : `_documents/nebula-agency/vente/PROSPECTION-GOOGLE-MAPS.md`.

    python scripts/prospection.py importer fiches.json   # fiches lues sur Google Maps
    python scripts/prospection.py liste [30]             # les plus hautes notes à contacter
    python scripts/prospection.py bilan                  # combien à chaque étape
    python scripts/prospection.py envois [10]            # liens WhatsApp Web des prochains messages
    python scripts/prospection.py suivi [fichier.md]     # tableau de suivi (fichier HORS du dépôt : il a les numéros)
    python scripts/prospection.py relance <id> AAAA-MM-JJ [note]
    python scripts/prospection.py vcf <fichier.vcf>      # tous les prospects contactés, à importer sur le téléphone
    python scripts/prospection.py statut <id> <statut> [note]

LA NOTE DE BESOIN (sur 10) : pas de site +3 (une simple page Facebook : +2),
vend des produits +2, actif (10 avis ou plus +2, 3 ou plus +1), bonne note
(4,3 ou plus) +1, numéro mobile +1, métier des fêtes +1.
Un vrai site = écarté. Pas de numéro = injoignable.
"""
import io, json, re, sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Les métiers cherchés vendent tous des produits, et tous vendent plus en décembre.
FETES = {"pâtisserie", "boutique de vêtements", "boutique cosmétiques", "traiteur", "bijouterie",
         "décoration événementielle", "boutique de chaussures", "parfumerie", "magasin de jouets",
         "fleuriste", "cave à vin"}
# Une page de réseau social n'est pas un site : le commerçant a toujours besoin d'un catalogue.
PAS_UN_SITE = ("facebook.com", "instagram.com", "tiktok.com", "wa.me", "whatsapp.com", "linktr.ee", "business.site")
STATUTS = ("a_contacter", "contacte", "repondu", "interesse", "paye", "refus", "ne_plus_contacter", "injoignable", "ecarte")


def connexion():
    import psycopg
    from psycopg.rows import dict_row
    dsn = next(l.split("=", 1)[1].strip() for l in io.open(RACINE / "secrets/supabase.env", encoding="utf-8")
               if l.startswith("DATABASE_URL="))
    c = psycopg.connect(dsn, row_factory=dict_row)
    c.prepare_threshold = None  # obligatoire avec le pooler Supabase
    return c


def formes(tel):
    """(forme à 10 chiffres, forme à 8 chiffres). Le 01 fait partie du numéro : on ne le retire jamais."""
    d = re.sub(r"\D", "", tel or "")
    if d.startswith("229") and len(d) in (11, 13):
        d = d[3:]
    if len(d) == 8:
        return "01" + d, d
    if len(d) == 10 and d.startswith("01"):
        return d, d[2:]
    return None, None


def est_mobile(dix):
    # Mobiles : 01 puis 4x, 5x, 6x ou 9x. Le bloc 012x porte les fixes historiques.
    return bool(dix) and dix[2] in "4569"


def noter(f):
    site = (f.get("site") or "").lower()
    dix, huit = formes(f.get("tel"))
    if site and not any(s in site for s in PAS_UN_SITE):
        return 0, "a déjà un site", "ecarte", dix, huit
    if not dix:
        return 0, "aucun numéro sur la fiche", "injoignable", dix, huit
    note, avis, metier = f.get("note") or 0, f.get("avis") or 0, f.get("requete") or ""
    s, raisons = 0, []
    if site:
        s += 2; raisons.append("seulement une page de réseau social")
    else:
        s += 3; raisons.append("pas de site")
    if metier in FETES:
        s += 3; raisons.append(f"{metier} : vend plus en décembre")
    if avis >= 10:
        s += 2; raisons.append(f"{avis} avis, donc actif")
    elif avis >= 3:
        s += 1; raisons.append(f"{avis} avis")
    if note >= 4.3:
        s += 1; raisons.append(f"note {str(note).replace('.', ',')}")
    if est_mobile(dix):
        s += 1
    resume = (f.get("resume") or "").lower()
    if "livraison" in resume:
        raisons.append("livre déjà : ses clients commandent à distance")
    return min(s, 10), " · ".join(raisons), "a_contacter", dix, huit


def importer(chemin):
    fiches = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if isinstance(fiches, dict):
        fiches = list(fiches.values())
    n = {"a_contacter": 0, "ecarte": 0, "injoignable": 0}
    with connexion() as c:
        for f in fiches:
            score, raison, statut, dix, huit = noter(f)
            # Le même commerce peut venir de deux sources (Maps, liste locale de Google) :
            # c'est le NUMÉRO qui dit que c'est le même, jamais le nom.
            if dix and c.execute("select 1 from piste.prospection where telephone = %s and id <> %s",
                                 (dix, f["id"])).fetchone():
                n["doublon"] = n.get("doublon", 0) + 1
                continue
            n[statut] += 1
            c.execute("""
              insert into piste.prospection (id, nom, metier, adresse, telephone, site, note, avis, maps_url, score, raison, statut, notes)
              values (%(id)s, %(nom)s, %(metier)s, %(adresse)s, %(tel)s, %(site)s, %(note)s, %(avis)s, %(url)s, %(score)s, %(raison)s, %(statut)s, %(notes)s)
              on conflict (id) do update set
                nom = excluded.nom, metier = excluded.metier, adresse = excluded.adresse, telephone = excluded.telephone,
                site = excluded.site, note = excluded.note, avis = excluded.avis, maps_url = excluded.maps_url,
                score = excluded.score, raison = excluded.raison,
                -- un statut de suivi déjà posé (contacté, refus...) ne revient jamais en arrière
                statut = case when piste.prospection.statut in ('a_contacter', 'ecarte', 'injoignable')
                              then excluded.statut else piste.prospection.statut end
            """, {"id": f["id"], "nom": f.get("nom"), "metier": f.get("requete"), "adresse": (f.get("adresse") or "").strip(),
                  "tel": dix, "site": f.get("site") or None, "note": f.get("note"), "avis": f.get("avis") or 0,
                  "url": f.get("url"), "score": score, "raison": raison, "statut": statut,
                  "notes": f"autre forme : {huit}" if huit else None})
    print(f"{len(fiches)} fiches lues · {n['a_contacter']} à contacter · {n['ecarte']} écartées (vrai site) · "
          f"{n['injoignable']} sans numéro · {n.get('doublon', 0)} déjà connues")


def liste(limite=30):
    with connexion() as c:
        for r in c.execute("""select id, nom, metier, telephone, note, avis, score, raison from piste.prospection
                              where statut = 'a_contacter' order by score desc, avis desc limit %s""", (limite,)):
            print(f"{r['score']:>2} · {r['nom'][:38]:<38} · {r['metier'] or '':<24} · {r['telephone']} · {r['raison']}")


# Les mots du métier : « je crée pour [les pâtisseries] un catalogue en ligne : [vos gâteaux] en photo ».
MOTS = {
    "pâtisserie": ("les pâtisseries", "vos gâteaux"),
    "boutique de vêtements": ("les boutiques de mode", "vos tenues"),
    "boutique cosmétiques": ("les boutiques de beauté", "vos produits"),
    "traiteur": ("les traiteurs", "vos plats"),
    "bijouterie": ("les bijouteries", "vos bijoux"),
    "décoration événementielle": ("les décorateurs", "vos décors"),
    "boutique de chaussures": ("les boutiques de chaussures", "vos chaussures"),
    "parfumerie": ("les parfumeries", "vos parfums"),
    "magasin de jouets": ("les magasins de jouets", "vos jouets"),
    "fleuriste": ("les fleuristes", "vos bouquets"),
    "cave à vin": ("les caves", "vos bouteilles"),
}


def message(r):
    """Le premier message, version 2 (Mongazi, 2026-11-18 vers 16 h : « tu dois les choquer et les intriguer,
    élever le niveau tout en parlant moins, de la manière la plus humaine possible »).
    Trois lignes : qui je suis, un compliment PRÉCIS et vrai, puis un fait vrai qui dérange (sa fiche Google
    n'a pas de site : on y trouve son nom, pas ses produits ni ses prix) posé en question. L'offre attend la
    réponse. La version 1, plus longue et qui vendait d'entrée, est dans l'historique git."""
    les, vos = MOTS.get(r["metier"], ("les commerces", "vos produits"))
    note = str(r["note"]).replace(".", ",").rstrip("0").rstrip(",") if r["note"] else ""
    nom = r["nom"].split("|")[0].strip()
    if (r["avis"] or 0) >= 5 and note:
        vu = f"{nom} : {note} sur Google avec {r['avis']} avis, vos clients vous aiment."
    elif note:
        vu = f"{nom} : {note} étoiles sur Google, bravo."
    else:
        vu = f"Je suis tombé sur {nom} sur Google."
    prix = "vos prix" if "prix" not in vos else ""
    return ("Bonjour, c'est Mongazi 🙂\n" + vu + "\n"
            f"Mais un client qui vous trouve à 23 h ne voit ni {vos} ni {prix or 'vos tarifs'}. "
            "Il commande chez qui, à votre avis ?")


def envois(limite=10):
    """Les liens WhatsApp Web des prochains à contacter (forme à 10 chiffres, puis l'autre forme)."""
    from urllib.parse import quote
    with connexion() as c:
        for r in c.execute("""select id, nom, metier, telephone, note, avis, notes from piste.prospection
                              where statut = 'a_contacter' order by score desc, avis desc limit %s""", (limite,)):
            texte = quote(message(r))
            autre = re.search(r"autre forme : (\d+)", r["notes"] or "")
            print(f"{r['id']}\t{r['nom']}\thttps://web.whatsapp.com/send?phone=229{r['telephone']}&text={texte}"
                  + (f"\tautre:229{autre.group(1)}" if autre else ""))


def vcf(sortie):
    """Un fichier contact (.vcf) de tous les prospects déjà contactés, à importer d'un coup sur le téléphone.
    Les deux formes du numéro : 10 chiffres pour appeler, 8 chiffres pour le compte WhatsApp resté sur l'ancienne."""
    lignes, n = [], 0
    with connexion() as c:
        for r in c.execute("""select nom, metier, telephone, statut from piste.prospection
                              where statut in ('contacte', 'repondu', 'interesse', 'paye', 'refus', 'ne_plus_contacter') and telephone is not null
                              order by statut desc, nom"""):
            nom = re.sub(r"[;\\,]", " ", r["nom"]).strip()
            lignes += ["BEGIN:VCARD", "VERSION:3.0", f"N:{nom};Prospect;;;", f"FN:Prospect {nom}",
                       f"TEL;TYPE=CELL:+229{r['telephone']}", f"TEL;TYPE=OTHER:+229{r['telephone'][2:]}",
                       f"NOTE:{r['metier'] or ''} · {r['statut']} · NEBULA", "END:VCARD"]
            n += 1
    # newline="" : sinon Windows transforme chaque \r\n en \r\r\n, et un téléphone lit des lignes vides
    with open(sortie, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lignes) + "\r\n")
    print(f"{n} contacts écrits dans {sortie}")


GROUPES = [  # l'ordre du tableau de suivi : ce qui rapporte d'abord
    ("paye", "💰 PAYÉ"),
    ("interesse", "🔥 INTÉRESSÉS : à faire avancer"),
    ("repondu", "💬 ONT RÉPONDU"),
    ("contacte", "📤 CONTACTÉS : en attente de réponse"),
    ("a_contacter", "🎯 À CONTACTER"),
    ("refus", "⏸️ PAS MAINTENANT"),
    ("ne_plus_contacter", "⛔ NE PLUS CONTACTER"),
    ("injoignable", "📵 SANS NUMÉRO"),
]


def suivi(sortie=None):
    """Le tableau de suivi : chaque fiche, son statut, sa prochaine relance et l'historique en une ligne.
    Écrit en Markdown HORS du dépôt (il porte des numéros), et affiche le résumé."""
    from datetime import date
    aujourd_hui = date.today()
    lignes = [f"# Suivi des prospects NEBULA · {aujourd_hui:%d/%m/%Y}", "",
              "Statuts : à contacter → contacté → répondu → intéressé → payé (ou pas maintenant / ne plus contacter).",
              "Outil : `python scripts/prospection.py suivi` · méthode et réponses types : "
              "`_documents/nebula-agency/vente/PROSPECTION-GOOGLE-MAPS.md`.", ""]
    resume = []
    with connexion() as c:
        rows = c.execute("""select nom, metier, telephone, note, avis, statut, contacte_le, relance_le, notes
                            from piste.prospection order by relance_le nulls last, score desc, avis desc""").fetchall()
    a_faire = [r for r in rows if r["relance_le"] and r["relance_le"].date() <= aujourd_hui
               and r["statut"] not in ("paye", "ne_plus_contacter", "ecarte", "injoignable")]
    if a_faire:
        lignes += ["## ⏰ À FAIRE AUJOURD'HUI", ""]
        lignes += [f"- **{r['nom']}** ({r['statut']}) · +229 {r['telephone']} · {r['notes'] or ''}" for r in a_faire]
        lignes.append("")
    for statut, titre in GROUPES:
        groupe = [r for r in rows if r["statut"] == statut]
        if not groupe:
            continue
        resume.append(f"{titre.split(' ', 1)[1].split(' :')[0]} {len(groupe)}")
        lignes += [f"## {titre} ({len(groupe)})", ""]
        for r in groupe:
            relance = f" · relance le {r['relance_le']:%d/%m}" if r["relance_le"] else ""
            note = f"{r['note']}".replace(".", ",") if r["note"] else "-"
            lignes.append(f"- **{r['nom']}** · {r['metier'] or ''} · {note} ★ ({r['avis'] or 0} avis) · "
                          f"+229 {r['telephone'] or '?'}{relance}")
            if r["notes"]:
                lignes.append(f"  - {r['notes']}")
        lignes.append("")
    if sortie:
        with open(sortie, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lignes))
    print(" · ".join(resume))
    if a_faire:
        print("À FAIRE AUJOURD'HUI : " + ", ".join(r["nom"] for r in a_faire))
    if sortie:
        print(f"→ {sortie}")


def relance(ident, jour, note=None):
    """Pose la date de la prochaine relance (AAAA-MM-JJ)."""
    with connexion() as c:
        r = c.execute("""update piste.prospection set relance_le = %s::date,
                         notes = coalesce(notes || ' · ', '') || coalesce(%s, '') where id = %s returning nom""",
                      (jour, note, ident)).fetchone()
    print(f"{r['nom']} → relance le {jour}" if r else f"aucune fiche {ident}")


def bilan():
    with connexion() as c:
        for r in c.execute("select statut, count(*) n from piste.prospection group by 1 order by 2 desc"):
            print(f"{r['statut']:<18} {r['n']}")


def statut(ident, nouveau, note=None):
    if nouveau not in STATUTS:
        raise SystemExit(f"statut inconnu : {nouveau} (attendu : {', '.join(STATUTS)})")
    champ = {"contacte": ", contacte_le = now()"}.get(nouveau, "")
    with connexion() as c:
        r = c.execute(f"""update piste.prospection set statut = %s{champ},
                          notes = coalesce(notes || ' · ', '') || coalesce(%s, '') where id = %s returning nom""",
                      (nouveau, note, ident)).fetchone()
    print(f"{r['nom']} → {nouveau}" if r else f"aucune fiche {ident}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "importer":
        importer(a[1])
    elif a[0] == "liste":
        liste(int(a[1]) if len(a) > 1 else 30)
    elif a[0] == "bilan":
        bilan()
    elif a[0] == "envois":
        envois(int(a[1]) if len(a) > 1 else 10)
    elif a[0] == "vcf":
        vcf(a[1])
    elif a[0] == "suivi":
        suivi(a[1] if len(a) > 1 else None)
    elif a[0] == "relance":
        relance(a[1], a[2], a[3] if len(a) > 3 else None)
    elif a[0] == "statut":
        statut(a[1], a[2], a[3] if len(a) > 3 else None)
    else:
        raise SystemExit(__doc__)
