# -*- coding: utf-8 -*-
"""
LE CARNET · une ligne par chose qui arrive avec un prospect ou un client, et les chiffres qui en sortent.
Mongazi, 2026-11-25 : « prendre des notes sur chaque client pour s'améliorer, voir les problèmes, les choses à
changer, avoir des statistiques claires ». Il n'a rien à remplir : Claude écrit une ligne à chaque lien donné et à
chaque capture de réponse. Les données vivent dans Supabase (RLS), ce script n'en contient aucune.

    python suivi/carnet.py note <tél> <événement> "<ce qui s'est passé>" [--nom N] [--source S] [--secteur S]
                                 [--accroche A] [--lecon "ce qu'on change"] [--montant 40000]
    python suivi/carnet.py fiche <tél>                 # l'histoire d'un client, dans l'ordre
    python suivi/carnet.py stats [--jours 7]           # l'entonnoir, par source, par métier, par accroche
    python suivi/carnet.py remplir                     # reprend l'historique (file d'envois + portefeuille)

Événements : contact · relance · reponse · oui · non · objection · apercu · paiement · silence · note
Sources    : meta (annonceur Facebook) · tiktok · annuaire · google · facebook · instagram · recommandation · autre
"""
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from prospection import connexion  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
EVENEMENTS = {"contact", "relance", "reponse", "oui", "non", "objection", "apercu", "paiement", "silence", "note"}
REPOND = {"reponse", "oui", "non", "objection", "paiement"}

SCHEMA = """
create table if not exists public.nebula_suivi_carnet (
  id bigserial primary key,
  quand timestamptz not null default now(),
  telephone text not null,                      -- 8 chiffres au Bénin, indicatif compris ailleurs
  nom text, evenement text not null, source text, secteur text,
  accroche text,                                -- le message qui a déclenché la réponse (étiquette courte)
  detail text,                                  -- ce qu'il a dit, ce qui s'est passé
  lecon text,                                   -- ce qu'on change
  montant int,
  origine text unique                           -- d'où vient la ligne reprise (envoi:<id>, portefeuille:<id>:<statut>)
);
alter table public.nebula_suivi_carnet enable row level security;
drop policy if exists "Mongazi seul" on public.nebula_suivi_carnet;
create policy "Mongazi seul" on public.nebula_suivi_carnet for all to authenticated
  using ((auth.jwt() ->> 'email') in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'))
  with check ((auth.jwt() ->> 'email') in ('allonebiao@gmail.com', 'allonebiao2@gmail.com'));
grant select on public.nebula_suivi_carnet to authenticated;
"""


def cle(tel):
    """Une seule forme par numéro : les 8 derniers chiffres au Bénin, le numéro complet ailleurs."""
    d = re.sub(r"\D", "", tel or "")
    if d.startswith("229"):
        d = d[3:]
    if len(d) == 10 and d.startswith("01"):
        d = d[2:]
    return d


def source_de(pour, heure):
    t = f"{pour} {heure or ''}".lower()
    if "annonceur" in t: return "meta"
    if "tiktok" in t: return "tiktok"
    if "annuaire" in t or "orion" in t: return "annuaire"
    if "google" in t or "maps" in t: return "google"
    return None


def nom_de(pour):
    n = re.sub(r"^(P\d+|①|②|🔥|🎉|🇨🇮|🇹🇬|🇧🇯|\s|·)+", "", pour).strip()
    return re.split(r"\s+\(", n)[0].strip() or pour


def note(c, tel, ev, detail=None, **k):
    if ev not in EVENEMENTS:
        sys.exit(f"événement inconnu : {ev} (attendus : {', '.join(sorted(EVENEMENTS))})")
    c.execute("""insert into public.nebula_suivi_carnet (quand, telephone, nom, evenement, source, secteur, accroche,
                 detail, lecon, montant, origine) values (coalesce(%s, now()), %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                 on conflict (origine) do nothing""",
              (k.get("quand"), cle(tel), k.get("nom"), ev, k.get("source"), k.get("secteur"), k.get("accroche"),
               detail, k.get("lecon"), k.get("montant"), k.get("origine")))


def remplir(c):
    """Reprend l'historique : la file d'envois (1er message = contact, puis relances et réponses) et le portefeuille.
    Relançable : les lignes reprises sont effacées puis réécrites ; les notes écrites à la main ne sont jamais touchées."""
    c.execute(SCHEMA)
    c.execute("delete from public.nebula_suivi_carnet where origine like 'envoi:%%' or origine like 'portefeuille:%%'")
    porte = {cle(r["telephone"]): r for r in c.execute(
        "select id, nom, telephone, metier, raison, statut, contacte_le, relance_le from piste.prospection where telephone is not null").fetchall()}
    def src(pour, heure, k):
        s = source_de(pour, heure)
        if s: return s
        r = porte.get(k)
        return "google" if r and (str(r["id"]).startswith("ChIJ") or "avis" in (r["raison"] or "")) else None
    vus, n = set(), 0
    for r in c.execute("select id, quand, pour, telephone, heure from public.nebula_suivi_envois where envoye order by quand, id").fetchall():
        pour, heure, k = r["pour"], r["heure"] or "", cle(r["telephone"])
        if "PAS SUR WHATSAPP" in heure.upper():
            continue
        base = dict(quand=r["quand"], nom=nom_de(pour), source=src(pour, heure, k), secteur=(porte.get(k) or {}).get("metier"))
        dit = re.findall(r"«\s*([^»]+?)\s*»", pour)
        if dit:   # on répondait à ce qu'il avait écrit : sa réponse est dans l'étiquette
            ev = "non" if re.search(r"non|pas intéress", dit[0], re.I) else ("oui" if re.fullmatch(r"(oui|ok|d'accord).*", dit[0], re.I) else "reponse")
            if k not in vus:   # il nous a parlé avant notre premier message noté : le contact a eu lieu avant
                note(c, r["telephone"], "contact", None, origine=f"envoi:{r['id']}:avant", **{**base, "quand": r["quand"] - timedelta(hours=1)}); n += 1
            note(c, r["telephone"], ev, dit[0], origine=f"envoi:{r['id']}:dit", **base); n += 1
        else:
            ev = "relance" if (k in vus or "RELANCE" in heure.upper()) else "contact"
            note(c, r["telephone"], ev, None, origine=f"envoi:{r['id']}", **base); n += 1
        if re.search(r"APERÇU.*LIVRÉ|DÉMO.*LIVRÉE", pour):
            note(c, r["telephone"], "apercu", None, origine=f"envoi:{r['id']}:apercu", **base); n += 1
        vus.add(k)
    etapes = {"refus": "non", "ne_plus_contacter": "non", "interesse": "oui", "apercu": "apercu", "repondu": "reponse"}
    for k, r in porte.items():
        s = "google" if str(r["id"]).startswith("ChIJ") or "avis" in (r["raison"] or "") else None
        if r["contacte_le"] and k not in vus:
            note(c, r["telephone"], "contact", None, quand=r["contacte_le"], nom=r["nom"], secteur=r["metier"], source=s,
                 origine=f"portefeuille:{r['id']}:contact"); n += 1
        ev = etapes.get(r["statut"])
        if ev:
            note(c, r["telephone"], ev, None, quand=r["relance_le"] or r["contacte_le"], nom=r["nom"], secteur=r["metier"],
                 source=s, origine=f"portefeuille:{r['id']}:{r['statut']}"); n += 1
    print(n, "lignes reprises (approximatives : la file d'envois était cochée en retard avant le 25/11)")


def fiche(c, tel):
    for r in c.execute("select * from public.nebula_suivi_carnet where telephone=%s order by quand", (cle(tel),)).fetchall():
        bout = " · ".join(x for x in (r["detail"], r["lecon"] and f"leçon : {r['lecon']}", r["montant"] and f"{r['montant']} F") if x)
        print(f"{r['quand']:%d/%m %H:%M}  {r['evenement']:<9} {r['nom'] or ''}  {bout}")


def stats(c, jours):
    depuis = datetime.now(timezone.utc) - timedelta(days=jours)
    lignes = c.execute("select * from public.nebula_suivi_carnet where quand >= %s order by quand", (depuis,)).fetchall()
    par_tel = defaultdict(list)
    for r in lignes:
        par_tel[r["telephone"]].append(r)
    profil = {}   # un client = sa source, son métier, sa première accroche, et jusqu'où il est allé
    for tel, ev in par_tel.items():
        noms = {e["evenement"] for e in ev}
        premier = next((e for e in ev if e["evenement"] == "contact"), None)
        rep = next((e for e in ev if e["evenement"] in REPOND), None)
        profil[tel] = dict(
            source=next((e["source"] for e in ev if e["source"]), "inconnue"),
            secteur=next((e["secteur"] for e in ev if e["secteur"]), "inconnu"),
            accroche=next((e["accroche"] for e in ev if e["accroche"]), None),
            contacte=bool(premier), repondu=bool(noms & REPOND), oui=bool(noms & {"oui", "apercu", "paiement"}),
            apercu="apercu" in noms, paye="paiement" in noms, non="non" in noms,
            delai=(rep["quand"] - premier["quand"]).total_seconds() / 3600 if premier and rep and rep["quand"] > premier["quand"] else None)
    P = list(profil.values())
    pc = lambda a, b: f"{100 * a / b:.0f} %" if b else "-"
    print(f"\n== LE CARNET · {jours} derniers jours · {len(P)} personnes ==")
    nb = {k: sum(p[k] for p in P) for k in ("contacte", "repondu", "oui", "apercu", "paye", "non")}
    rc = sum(p["repondu"] for p in P if p["contacte"])
    print(f"Entonnoir : {nb['contacte']} contactés → {rc} ont répondu ({pc(rc, nb['contacte'])})"
          f" → {nb['oui']} oui → {nb['apercu']} aperçus → {nb['paye']} payés · {nb['non']} non")
    print(f"Encaissé : {sum(r['montant'] or 0 for r in lignes if r['evenement'] == 'paiement'):,} F".replace(",", " "))
    delais = sorted(p["delai"] for p in P if p["delai"] is not None)
    if delais:
        print(f"Délai de réponse médian : {delais[len(delais) // 2]:.1f} h (sur {len(delais)} réponses)")
    for axe in ("source", "secteur", "accroche"):
        g = defaultdict(list)
        for p in P:
            if p["contacte"] and p[axe]:
                g[p[axe]].append(p)
        if not g: continue
        print(f"\nPar {axe} (premiers contacts → réponse → oui → payé) :")
        for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))[:12]:
            r_, o_, y_ = sum(p["repondu"] for p in v), sum(p["oui"] for p in v), sum(p["paye"] for p in v)
            print(f"  {k[:34]:<34} {len(v):>3} → {r_:>3} ({pc(r_, len(v)):>4}) → {o_:>3} → {y_}")
    obj = [r for r in lignes if r["evenement"] in ("objection", "non") and r["detail"]]
    if obj:
        print("\nCe qui bloque (objections et refus, les plus fréquents) :")
        for k, n in Counter(r["detail"].strip().lower()[:70] for r in obj).most_common(10):
            print(f"  {n} × {k}")
    lec = [r for r in lignes if r["lecon"]]
    if lec:
        print("\nLeçons de la période :")
        for r in lec[-10:]:
            print(f"  {r['quand']:%d/%m} {r['nom'] or r['telephone']} : {r['lecon']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda n: a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else None
    libres = [x for i, x in enumerate(a) if not x.startswith("--") and not (i and a[i - 1].startswith("--"))]
    with connexion() as c:
        if a[0] == "note":
            note(c, libres[1], libres[2], libres[3] if len(libres) > 3 else None, nom=opt("--nom"), source=opt("--source"),
                 secteur=opt("--secteur"), accroche=opt("--accroche"), lecon=opt("--lecon"),
                 montant=int(opt("--montant")) if opt("--montant") else None)
            print("noté")
        elif a[0] == "fiche":
            fiche(c, libres[1])
        elif a[0] == "stats":
            stats(c, int(opt("--jours") or 30))
        elif a[0] == "remplir":
            remplir(c)
