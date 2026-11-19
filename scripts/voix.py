# -*- coding: utf-8 -*-
"""
LA VOIX DES CLIENTS : tout ce que disent les prospects et les clients, gardé, classé, analysé, puis appliqué.

Demande de Mongazi (2026-11-19) : garder leurs propos, leurs plaintes, ce qu'il faut changer, leurs constats, les
barrages qui reviennent, « absolument tout », pour être en amélioration constante et atteindre l'objectif plus vite.

⛔ Aucune donnée ici : ce dépôt est PUBLIC. Les propos vivent dans Supabase (`piste.prospection_voix`, RLS active, aucun
accès public) et le dossier lisible est écrit HORS du dépôt, dans `C:\\Users\\USER\\nebula-apercus\\voix-clients\\`.

LA BOUCLE
  1. récolter  : la page WhatsApp exporte les discussions en JSON, `importer` les range (sans doublon, par identifiant).
  2. classer   : chaque propos reçoit ses catégories. Des règles dégrossissent, une lecture humaine tranche (`a-classer`, `classer`).
  3. mesurer   : quel message obtient une réponse, où ça bloque, qui attend quoi (`dossier`).
  4. décider   : `point` nomme ce qui bloque le plus et ce qu'on change AUJOURD'HUI.
  5. appliquer : `ameliorer` écrit le changement et comment on saura s'il marche ; `resultat` ferme la boucle.

    python scripts/voix.py installer
    python scripts/voix.py importer <voix-discussions.json>
    python scripts/voix.py transcrire              # vocaux/<nom>-HHMM.ogg rattachés au bon message
    python scripts/voix.py a-classer               # écrit voix-clients/_a-classer.md
    python scripts/voix.py classer <fichier.json>  # [{"id": 12, "c": ["barrage:prix"], "n": "note", "e": "a_traiter"}]
    python scripts/voix.py dire <prospect|tel> "propos" [categorie ...]   # un propos entendu ailleurs (appel, vocal de Mongazi)
    python scripts/voix.py ameliorer "constat" "changement" "où" "mesure" ["preuve"]
    python scripts/voix.py resultat <id> <garde|abandonne|en_test> "ce qu'on a observé"
    python scripts/voix.py dossier                 # refait tout le dossier lisible
    python scripts/voix.py point                   # le point du jour, à lire chaque matin
"""
import io, json, re, statistics, sys, unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from prospection import connexion, formes  # même base, même règle sur les numéros

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DOSSIER = Path(r"C:\Users\USER\nebula-apercus\voix-clients")
VOCAUX = Path(r"C:\Users\USER\nebula-apercus\vocaux")
BENIN = timezone(timedelta(hours=1))

CATEGORIES = {
    "signal_achat": "Signal d'achat : il avance vers le oui",
    "besoin": "Ce qu'il veut vraiment",
    "question": "Ce qu'il demande",
    "constat": "Ce qu'il observe sur son commerce, ses clients, son marché",
    "plainte": "Plainte : contre nous, contre un prestataire passé, contre son métier",
    "a_changer": "À changer : une demande précise sur l'aperçu, l'offre ou notre façon de faire",
    "compliment": "Ce qui lui a plu",
    "refus": "Non clair",
    "automatique": "Réponse automatique ou assistant",
    "info": "Information pratique (adresse, horaires, autre numéro)",
}
BARRAGES = {
    "barrage:prix": ("C'est trop cher", "VENDEUR § 3 : accueillir, comprendre, étaler, calculer avec ses chiffres, réduire sans brader."),
    "barrage:budget": ("Pas d'argent en ce moment", "Moitié pour démarrer, périmètre réduit, date notée."),
    "barrage:confiance": ("Il ne nous croit pas encore, a été déçu", "Aperçu avec ses produits avant tout paiement, preuves, appel de Mongazi."),
    "barrage:deja_equipe": ("Il a déjà un site, un catalogue, quelqu'un", "Demander à voir, saluer, montrer le manque réel."),
    "barrage:pas_besoin": ("Il ne voit pas l'utilité", "Montrer ce que perd son client aujourd'hui, avec sa fiche Google."),
    "barrage:plus_tard": ("Plus tard, on vous revient", "Date précise, un seul rappel utile, jamais « avez-vous vu ? »."),
    "barrage:decideur": ("Ce n'est pas lui qui décide", "Demander qui décide et préparer un message à lui transmettre."),
    "barrage:incompris": ("Il n'a pas compris ce qu'on propose", "Refaire l'explication en une phrase avec un exemple de son métier."),
    "barrage:temps": ("Il n'a pas le temps", "« Vous m'envoyez vos photos, je fais le reste. »"),
    "barrage:contenu": ("Il n'a pas ses photos, ses prix", "Partir de ce qui existe : téléphone, statuts, catalogue WhatsApp."),
    "barrage:silence_prix": ("Silence après le prix", "Relance avec du neuf : son aperçu, un calcul, un choix entre deux options."),
    "barrage:canal": ("Il ne répond qu'en vocal, ou veut parler", "Faire appeler ou envoyer un vocal par Mongazi."),
    "barrage:technique": ("Un obstacle technique", "Lien, paiement, ouverture de page : corriger puis lui redire."),
}
TOUTES = {**CATEGORIES, **{k: v[0] for k, v in BARRAGES.items()}}

# Un premier tri automatique, pour que rien ne dorme quand personne ne relit. La lecture humaine l'emporte toujours.
REGLES = [
    ("automatique", r"merci (de|d.avoir|pour votre) (nous )?(contact|message)|bienvenue (chez|à|au)|nous (vous )?(répondrons|reviendrons)|"
                    r"(sommes|suis) (actuellement )?(ferm|absent|indisponible)|comment (pouvons|puis)[- ](nous|je) vous aider|"
                    r"je vous ai connect|assistant|consultez notre catalogue|horaires d.ouverture|message automatique"),
    ("refus", r"non merci|pas int[ée]ress|ne m.int[ée]resse|pas besoin|arr[êe]tez|ne plus (me )?contact"),
    ("barrage:prix", r"trop cher|c.est cher|moins cher|r[ée]duction|n[ée]goci|remise|baisser"),
    ("barrage:budget", r"pas (d.)?(argent|moyen|budget)|moyens? limit|difficile en ce moment|la conjoncture"),
    ("barrage:plus_tard", r"plus tard|on vous revient|je (vous )?reviens|je reviendrai|on attend|pour le moment|apr[èe]s les f[êe]tes|je vous recontacte|r[ée]fl[ée]chi"),
    ("barrage:deja_equipe", r"(j.ai|on a|nous avons) d[ée]j[àa]|d[ée]j[àa] un (catalogue|site)|notre site"),
    ("barrage:incompris", r"pas compris|ne comprends|c.est (pour )?quoi|c.est qui|qui [êe]tes|de quoi s.agit"),
    ("barrage:confiance", r"arnaqu|escroc|d[ée][çc]u|d[ée]j[àa] pay[ée]|pas confiance|s[ée]rieux"),
    ("barrage:temps", r"pas le temps|d[ée]bord[ée]|trop occup"),
    ("barrage:contenu", r"pas (de|les) photos?|pas encore (les|de) photos?"),
    ("signal_achat", r"[çc]a marche|je veux|je suis int[ée]ress|on commence|comment (on|je) (fait|fais|paie|proc[èe]de)|envoyez|montrez|c.est combien|quel (est le )?prix|combien"),
    ("question", r"\?\s*$"),
    ("compliment", r"\b(magnifique|super|tr[èe]s beau|j.aime|sympa|bravo|impressionn)"),
]
EXEMPLES = ("hillary-m-styl", "luxuryclub229", "speed-weinkeller", "djambarteam", "aubraisedor")


def sql_install(c):
    c.execute("""create table if not exists piste.prospection_voix (
        id bigserial primary key,
        msg_id text not null unique,
        prospect_id text,
        titre text,
        quand timestamptz,
        rang integer,
        sens text not null check (sens in ('eux','nous')),
        nature text not null default 'texte',
        texte text not null default '',
        duree text,
        transcription text,
        categories text[] not null default '{}',
        note text,
        etat text not null default 'a_lire' check (etat in ('a_lire','lu','a_traiter','traite')),
        action text,
        cree_le timestamptz not null default now())""")
    c.execute("alter table piste.prospection_voix add column if not exists cite text")   # le message auquel il répond
    c.execute("create index if not exists prospection_voix_p on piste.prospection_voix (prospect_id, quand)")
    c.execute("alter table piste.prospection_voix enable row level security")
    c.execute("""create table if not exists piste.prospection_amelioration (
        id bigserial primary key,
        cree_le timestamptz not null default now(),
        constat text not null,
        preuve text,
        changement text not null,
        ou text,
        mesure text,
        etat text not null default 'a_faire' check (etat in ('a_faire','en_test','garde','abandonne')),
        resultat text)""")
    c.execute("alter table piste.prospection_amelioration enable row level security")


def installer():
    with connexion() as c:
        sql_install(c)
    print("tables prêtes, RLS active, aucun accès public")


def sans_accents(s):
    return "".join(x for x in unicodedata.normalize("NFD", s or "") if unicodedata.category(x) != "Mn")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", sans_accents(s).lower()).strip("-")[:48] or "sans-nom"


def nom_court(titre):
    return re.sub(r"^Prospect\s+", "", titre or "").strip() or "?"


def pre_tri(texte):
    t = (texte or "").lower()
    return [c for c, motif in REGLES if re.search(motif, t)]


def horodatage(h, d):
    try:
        return datetime.strptime(f"{d} {h}", "%d/%m/%Y %H:%M").replace(tzinfo=BENIN)
    except ValueError:
        return None


def importer(chemin):
    d = json.load(io.open(chemin, encoding="utf-8"))
    aujourd = datetime.now(BENIN).strftime("%d/%m/%Y")
    neufs, vus = 0, 0
    with connexion() as c:
        sql_install(c)
        for disc in d["discussions"]:
            msgs = disc["messages"]
            # les vocaux et les images n'ont pas de date lisible : celle du message voisin
            connu = next((m["d"] for m in msgs if m.get("d")), aujourd)
            for m in msgs:
                connu = m.get("d") or connu
                m["d"] = connu
            for m in msgs:
                texte = m.get("texte") or ""
                if not texte and m.get("nature") == "texte":
                    texte = m.get("brut") or ""
                cats, etat = [], "lu"
                if m["sens"] == "eux":
                    cats = pre_tri(texte)
                    etat = "lu" if "automatique" in cats else "a_lire"
                r = c.execute("""insert into piste.prospection_voix
                      (msg_id, prospect_id, titre, quand, rang, sens, nature, texte, cite, duree, categories, etat)
                      values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                      on conflict (msg_id) do update set titre = excluded.titre, rang = excluded.rang,
                        quand = coalesce(excluded.quand, piste.prospection_voix.quand),
                        texte = case when excluded.texte <> '' then excluded.texte else piste.prospection_voix.texte end,
                        cite = coalesce(excluded.cite, piste.prospection_voix.cite), sens = excluded.sens,
                        categories = case when piste.prospection_voix.etat = 'a_lire' or piste.prospection_voix.sens <> excluded.sens
                                          then excluded.categories else piste.prospection_voix.categories end,
                        nature = excluded.nature, duree = coalesce(excluded.duree, piste.prospection_voix.duree)
                      returning (xmax = 0) as neuf""",
                              (m["id"], disc["prospect_id"], disc["titre"], horodatage(m.get("h"), m["d"]), m.get("rang"),
                               m["sens"], m.get("nature") or "texte", texte, m.get("cite") or None, m.get("duree") or None, cats, etat)).fetchone()
                neufs += 1 if r["neuf"] else 0
                vus += 1
    print(f"{len(d['discussions'])} discussions · {vus} messages · {neufs} nouveaux")


def trouver(c, cle):
    d = re.sub(r"\D", "", cle)
    r = None
    if len(d) >= 8:
        r = c.execute("select id, nom from piste.prospection where regexp_replace(telephone,'\\D','','g') like %s", (f"%{d[-8:]}",)).fetchone()
    return r or c.execute("select id, nom from piste.prospection where id = %s or nom ilike %s order by id limit 1", (cle, f"%{cle}%")).fetchone()


def dire(cle, texte, cats):
    """Un propos qui n'est pas dans WhatsApp : appel, vocal raconté par Mongazi, visite."""
    with connexion() as c:
        p = trouver(c, cle)
        if not p:
            raise SystemExit(f"fiche introuvable : {cle}")
        maintenant = datetime.now(BENIN)
        c.execute("""insert into piste.prospection_voix (msg_id, prospect_id, titre, quand, sens, nature, texte, categories, etat)
                     values (%s,%s,%s,%s,'eux','rapporte',%s,%s,'lu')""",
                  (f"rapporte-{maintenant.timestamp():.0f}", p["id"], p["nom"], maintenant, texte, cats))
    print("noté pour", p["nom"])


def transcrire():
    import transcrire as T
    with connexion() as c:
        for f in sorted(VOCAUX.glob("*.ogg")):
            m = re.match(r"(mongazi-vers-)?(.+)-(\d{2})(\d{2})$", f.stem)
            if not m:
                continue
            sens = "nous" if m[1] else "eux"
            r = c.execute("""select id, transcription from piste.prospection_voix where nature = 'vocal' and sens = %s and titre ilike %s
                             and to_char(quand at time zone 'Africa/Porto-Novo','HH24:MI') = %s order by quand desc limit 1""",
                          (sens, f"%{m[2]}%", f"{m[3]}:{m[4]}")).fetchone()
            if not r:
                print("sans message :", f.name); continue
            if r["transcription"]:
                continue
            texte, _, moteur = T.transcrire(str(f))
            c.execute("update piste.prospection_voix set transcription = %s, categories = %s, etat = 'a_lire' where id = %s",
                      (texte, pre_tri(texte) if sens == "eux" else [], r["id"]))
            c.commit()
            print(f.name, "→", moteur, len(texte), "caractères")


def propos(r):
    return (r.get("transcription") or r.get("texte") or "").strip() or f"[{r['nature']}{' ' + r['duree'] if r.get('duree') else ''}]"


def a_classer(tout=False):
    with connexion() as c:
        rs = c.execute(f"""select id, titre, quand, nature, texte, cite, transcription, duree, categories from piste.prospection_voix
                           where sens = 'eux' {"" if tout else "and etat = 'a_lire'"} order by titre, quand, rang""").fetchall()
    DOSSIER.mkdir(parents=True, exist_ok=True)
    L = [f"# À classer : {len(rs)} propos\n"]
    titre = None
    for r in rs:
        if r["titre"] != titre:
            titre = r["titre"]; L.append(f"\n## {nom_court(titre)}")
        q = r["quand"].astimezone(BENIN).strftime("%d/%m %H:%M") if r["quand"] else "?"
        rep = f" (en réponse à : {r['cite'][:70]}…)" if r.get("cite") else ""
        L.append(f"- #{r['id']} · {q} · {r['nature']}{rep} · pré-tri {','.join(r['categories']) or '-'} : {propos(r)[:600]}")
    (DOSSIER / "_a-classer.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(len(rs), "propos à classer →", DOSSIER / "_a-classer.md")


def classer(chemin):
    d = json.load(io.open(chemin, encoding="utf-8"))
    inconnues = sorted({x for e in d for x in e.get("c", []) if x not in TOUTES})
    if inconnues:
        raise SystemExit(f"catégories inconnues : {inconnues}")
    with connexion() as c:
        for e in d:
            c.execute("""update piste.prospection_voix set categories = %s, note = coalesce(%s, note), etat = %s,
                         action = coalesce(%s, action) where id = %s""",
                      (e.get("c", []), e.get("n"), e.get("e", "lu"), e.get("a"), e["id"]))
    print(len(d), "propos classés")


def ameliorer(constat, changement, ou, mesure, preuve=None):
    with connexion() as c:
        sql_install(c)
        r = c.execute("""insert into piste.prospection_amelioration (constat, changement, ou, mesure, preuve)
                         values (%s,%s,%s,%s,%s) returning id""", (constat, changement, ou, mesure, preuve)).fetchone()
    print("amélioration n°", r["id"])


def resultat(ident, etat, texte):
    with connexion() as c:
        c.execute("update piste.prospection_amelioration set etat = %s, resultat = %s where id = %s", (etat, texte, ident))
    print("noté")


# ---------------------------------------------------------------- l'analyse

def charger():
    with connexion() as c:
        sql_install(c)
        fiches = {r["id"]: r for r in c.execute("select * from piste.prospection").fetchall()}
        voix = c.execute("select * from piste.prospection_voix order by quand nulls last, rang").fetchall()
        amel = c.execute("select * from piste.prospection_amelioration order by id desc").fetchall()
    conv = defaultdict(list)
    for v in voix:
        conv[v["prospect_id"]].append(v)
    for l in conv.values():
        l.sort(key=lambda m: ((m["quand"] or datetime.min.replace(tzinfo=BENIN)), m["rang"] or 0))
    return fiches, conv, amel


humain = lambda m: m["sens"] == "eux" and "automatique" not in (m["categories"] or [])


def genre(m, i):
    t = (m["texte"] or "").lower()
    if i == 0:
        return "1er message"
    if ".pages.dev" in t and not any(e in t for e in EXEMPLES):
        return "aperçu à son nom"
    if any(e in t for e in EXEMPLES):
        return "exemple d'un autre client"
    if re.search(r"\b\d{2,3}[ .\u202f\u00a0]?000\s?(f\b|fcfa|francs)", t):
        return "annonce du prix"
    return "suite de conversation"


def mesures(fiches, conv):
    M = {"contactes": 0, "humains": 0, "auto_seul": 0, "silence": 0, "delais": [], "heures": Counter(), "genres": defaultdict(lambda: [0, 0]),
         "metiers": defaultdict(lambda: [0, 0]), "attend": [], "silence_prix": [], "vocaux": []}
    for pid, l in conv.items():
        nous = [m for m in l if m["sens"] == "nous"]
        if not nous:
            continue
        M["contactes"] += 1
        f = fiches.get(pid) or {}
        hum = [m for m in l if humain(m)]
        eux = [m for m in l if m["sens"] == "eux"]
        met = M["metiers"][f.get("metier") or "?"]
        met[0] += 1
        if hum:
            M["humains"] += 1; met[1] += 1
        elif eux:
            M["auto_seul"] += 1
        else:
            M["silence"] += 1
        t0 = nous[0]["quand"]
        apres = [m for m in hum if m["quand"] and t0 and m["quand"] > t0]
        if apres:
            M["delais"].append((apres[0]["quand"] - t0).total_seconds() / 60)
        for m in hum:
            if m["quand"]:
                M["heures"][m["quand"].astimezone(BENIN).hour] += 1
            if m["nature"] == "vocal" and not m["transcription"]:
                M["vocaux"].append((pid, m))
        for i, m in enumerate(nous):
            if not m["quand"]:
                continue
            g = genre(m, i)
            M["genres"][g][0] += 1
            if any(x["quand"] and m["quand"] < x["quand"] <= m["quand"] + timedelta(hours=24) for x in hum):
                M["genres"][g][1] += 1
        dern = l[-1]
        if dern["sens"] == "eux" and "MONGAZI" not in (f.get("notes") or ""):
            M["attend"].append((pid, dern))
        if dern["sens"] == "nous" and genre(dern, len(nous) - 1) == "annonce du prix":
            M["silence_prix"].append((pid, dern))
    return M


def pct(a, b):
    return f"{round(100 * a / b)} %" if b else "-"


def date(m):
    return m["quand"].astimezone(BENIN).strftime("%d/%m %H:%M") if m["quand"] else "?"


def citation(m, n=170):
    t = re.sub(r"\s+", " ", propos(m))
    return "« " + (t[:n] + "…" if len(t) > n else t) + " »"


def par_categorie(conv):
    P = defaultdict(list)
    for pid, l in conv.items():
        for m in l:
            if m["sens"] == "eux":
                for c in m["categories"] or []:
                    P[c].append((pid, m))
    return P


def ordre_barrages(P, M):
    lignes = []
    for k, (titre, levier) in BARRAGES.items():
        n = len({p for p, _ in P.get(k, [])}) + (len(M["silence_prix"]) if k == "barrage:silence_prix" else 0)
        if n:
            lignes.append((n, k, titre, levier))
    return sorted(lignes, reverse=True)


def point_texte(fiches, conv, amel):
    M, P = mesures(fiches, conv), par_categorie(conv)
    nom = lambda p: nom_court((fiches.get(p) or {}).get("nom") or p)
    L = [f"# Le point du jour · {datetime.now(BENIN).strftime('%d/%m/%Y %H:%M')}", ""]
    L += [f"**{M['contactes']} contactés · {M['humains']} ont vraiment répondu ({pct(M['humains'], M['contactes'])}) · "
          f"{M['auto_seul']} automatiques seuls · {M['silence']} silences.**", ""]
    L += ["## Ce qui bloque le plus", ""]
    bar = ordre_barrages(P, M)
    L += [f"{i}. **{t}** ({n}) : {lev}" for i, (n, k, t, lev) in enumerate(bar[:5], 1)] or ["Rien de classé pour l'instant."]
    L += ["", "## Qui attend une réponse de nous", ""]
    L += [f"- **{nom(p)}** · {date(m)} : {citation(m, 120)}" for p, m in M["attend"]] or ["Personne."]
    if M["vocaux"]:
        L += ["", "## Vocaux pas encore transcrits", ""] + [f"- {nom(p)} · {date(m)} · {m['duree'] or ''}" for p, m in M["vocaux"]]
    if M["silence_prix"]:
        L += ["", "## Silence après le prix : à relancer avec du neuf", ""] + [f"- {nom(p)} · prix annoncé le {date(m)}" for p, m in M["silence_prix"]]
    ouverts = [(p, m) for p, l in conv.items() for m in l if m["etat"] == "a_traiter"]
    L += ["", "## Promesses et demandes ouvertes", ""]
    L += [f"- #{m['id']} **{nom(p)}** : {m['note'] or citation(m, 120)}" for p, m in ouverts] or ["Aucune."]
    enc = [a for a in amel if a["etat"] in ("a_faire", "en_test")]
    L += ["", "## Améliorations en cours", ""] + ([f"- n°{a['id']} [{a['etat']}] {a['changement']} · mesure : {a['mesure'] or '?'}" for a in enc] or ["Aucune."])
    return L


def dossier():
    fiches, conv, amel = charger()
    (DOSSIER / "clients").mkdir(parents=True, exist_ok=True)
    M, P = mesures(fiches, conv), par_categorie(conv)
    nom = lambda p: nom_court((fiches.get(p) or {}).get("nom") or p)
    ecrire = lambda n, L: (DOSSIER / n).write_text("\n".join(L) + "\n", encoding="utf-8")

    ecrire("00-POINT-DU-JOUR.md", point_texte(fiches, conv, amel))

    L = ["# Les barrages, du plus fréquent au plus rare", "", "Compté en personnes, pas en messages. Le levier est ce qu'on fait contre.", ""]
    for n, k, t, lev in ordre_barrages(P, M):
        L += [f"## {t} · {n} personne(s)", "", f"**Levier :** {lev}", ""]
        L += [f"- **{nom(p)}** ({(fiches.get(p) or {}).get('statut', '?')}) · {date(m)} : {citation(m)}" + (f" · _{m['note']}_" if m["note"] else "") for p, m in P.get(k, [])]
        if k == "barrage:silence_prix":
            L += [f"- **{nom(p)}** : prix annoncé le {date(m)}, plus rien depuis" for p, m in M["silence_prix"]]
        L.append("")
    ecrire("01-BARRAGES.md", L)

    for fichier, titre, cats in (("02-PLAINTES.md", "Les plaintes", ["plainte"]), ("03-A-CHANGER.md", "Ce qu'il faut changer", ["a_changer"]),
                                 ("04-CONSTATS-ET-LEURS-MOTS.md", "Leurs constats, avec leurs mots (à réutiliser dans nos messages)", ["constat", "besoin", "compliment"]),
                                 ("05-QUESTIONS.md", "Ce qu'ils demandent", ["question"]), ("06-SIGNAUX-D-ACHAT.md", "Les signaux d'achat", ["signal_achat"]),
                                 ("07-REFUS.md", "Les refus", ["refus"])):
        L = [f"# {titre}", ""]
        for c in cats:
            if len(cats) > 1:
                L += [f"## {CATEGORIES[c]}", ""]
            L += [f"- **{nom(p)}** · {date(m)} · {'✅ ' if m['etat'] == 'traite' else ''}{citation(m, 260)}" + (f" · _{m['note']}_" if m["note"] else "") + (f" · fait : {m['action']}" if m["action"] else "")
                  for p, m in P.get(c, [])] or ["Rien pour l'instant."]
            L.append("")
        ecrire(fichier, L)

    L = ["# Les chiffres", "", "| | |", "|---|---|", f"| Contactés avec discussion archivée | {M['contactes']} |",
         f"| Ont vraiment répondu | {M['humains']} ({pct(M['humains'], M['contactes'])}) |", f"| Automatique seulement | {M['auto_seul']} |", f"| Silence | {M['silence']} |"]
    if M["delais"]:
        L.append(f"| Délai médian de la première vraie réponse | {round(statistics.median(M['delais']))} min |")
    L += ["", "## Quel message obtient une réponse dans les 24 h", "", "| Message | Envoyés | Suivis d'une réponse | Taux |", "|---|---|---|---|"]
    L += [f"| {g} | {a} | {b} | {pct(b, a)} |" for g, (a, b) in sorted(M["genres"].items(), key=lambda x: -x[1][0])]
    L += ["", "## Par métier", "", "| Métier | Contactés | Vraies réponses | Taux |", "|---|---|---|---|"]
    L += [f"| {g} | {a} | {b} | {pct(b, a)} |" for g, (a, b) in sorted(M["metiers"].items(), key=lambda x: -x[1][1] / max(1, x[1][0]))]
    L += ["", "## À quelle heure ils répondent", "", "| Heure | Réponses |", "|---|---|"] + [f"| {h} h | {n} |" for h, n in sorted(M["heures"].items())]
    ecrire("08-CHIFFRES.md", L)

    L = ["# Le journal des améliorations", "", "Chaque ligne : ce que les clients ont montré, ce qu'on a changé, comment on saura si ça marche, ce qui s'est passé.", ""]
    for a in amel:
        L += [f"## n°{a['id']} · {a['etat']} · {a['cree_le'].astimezone(BENIN).strftime('%d/%m')}", "", f"- **Constat :** {a['constat']}", f"- **Preuve :** {a['preuve'] or '-'}",
              f"- **Changement :** {a['changement']} ({a['ou'] or '-'})", f"- **Mesure :** {a['mesure'] or '-'}", f"- **Résultat :** {a['resultat'] or 'à observer'}", ""]
    ecrire("09-AMELIORATIONS.md", L)

    for pid, l in conv.items():
        f = fiches.get(pid) or {}
        L = [f"# {nom(pid)}", "", f"{f.get('metier') or '?'} · {f.get('ville') or ''} · tél. {f.get('telephone') or '?'} · note {f.get('note') or '?'} ({f.get('avis') or 0} avis) · statut **{f.get('statut') or '?'}**", ""]
        cl = [m for m in l if m["sens"] == "eux" and m["etat"] != "a_lire" and set(m["categories"] or []) - {"automatique", "question", "info"}]
        if cl:
            L += ["## Ce qu'il faut retenir", ""] + [f"- {', '.join(TOUTES.get(c, c).split(' : ')[0] for c in m['categories'])} : {citation(m, 200)}" + (f" · _{m['note']}_" if m["note"] else "") for m in cl] + [""]
        if f.get("notes"):
            L += ["## Notes de suivi", "", f["notes"], ""]
        L += ["## La discussion", ""]
        for m in l:
            qui = "**LUI**" if m["sens"] == "eux" else "nous"
            L.append(f"- {date(m)} · {qui}{' (auto)' if 'automatique' in (m['categories'] or []) else ''}{' · ' + m['nature'] if m['nature'] != 'texte' else ''} : {re.sub(chr(10) + '+', ' / ', propos(m))}")
        ecrire(f"clients/{slug(nom(pid))}.md", L)

    ecrire("LISEZ-MOI.md", ["# La voix des clients", "", "Tout ce que disent les prospects et les clients, pour nous améliorer sans arrêt.", "",
                            "⛔ Ce dossier contient des propos et des numéros : il ne va jamais sur GitHub. La référence est la base Supabase, ces fichiers sont refaits par `python scripts/voix.py dossier`.", "",
                            "- `00-POINT-DU-JOUR.md` : à lire chaque matin", "- `01-BARRAGES.md` : ce qui empêche de dire oui, classé", "- `02-PLAINTES.md`, `03-A-CHANGER.md`, `04-CONSTATS-ET-LEURS-MOTS.md`",
                            "- `05-QUESTIONS.md`, `06-SIGNAUX-D-ACHAT.md`, `07-REFUS.md`", "- `08-CHIFFRES.md` : quel message marche, quel métier répond, à quelle heure", "- `09-AMELIORATIONS.md` : ce qu'on a changé et ce que ça a donné", "- `clients/` : une fiche et toute la discussion par personne"])
    print(f"dossier refait : {len(conv)} discussions →", DOSSIER)


def point():
    fiches, conv, amel = charger()
    print("\n".join(point_texte(fiches, conv, amel)))


if __name__ == "__main__":
    a = sys.argv[1:] or ["point"]
    {"installer": installer, "importer": lambda: importer(a[1]), "transcrire": transcrire, "a-classer": lambda: a_classer("--tout" in a), "classer": lambda: classer(a[1]),
     "dire": lambda: dire(a[1], a[2], a[3:]), "ameliorer": lambda: ameliorer(*a[1:6]), "resultat": lambda: resultat(a[1], a[2], a[3]),
     "dossier": dossier, "point": point}[a[0]]()
