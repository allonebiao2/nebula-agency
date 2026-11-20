# -*- coding: utf-8 -*-
"""
NEBULA SUIVI · ce que Mongazi voit sur son téléphone (https://nebula-suivi.pages.dev, installable, avec notifications).
Tout est écrit dans des tables privées (RLS sur ses e-mails) ; ce script ne contient aucune donnée.

    python suivi/suivi.py cles                                    # une fois : les clés des notifications (secrets/)
    python suivi/suivi.py note "titre" ["texte"] [lien] [--genre lien|alerte|besoin|point|vente] [--push]
    python suivi/suivi.py prospects                               # refait le portefeuille depuis piste.prospection
    python suivi/suivi.py chiffres [encaissé]                     # les chiffres du jour
    python suivi/suivi.py envois <envois.json>                    # la file des messages prêts (envoi d'un toucher)
    python suivi/suivi.py push "titre" "texte"                    # une notification seule
"""
import base64
import io
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
from prospection import connexion  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BENIN = timezone(timedelta(hours=1))
PEM = RACINE / "secrets" / "suivi_vapid.pem"
ENV = RACINE / "secrets" / "suivi.env"


def cles():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    if PEM.exists():
        print("clés déjà là"); return
    k = ec.generate_private_key(ec.SECP256R1())
    PEM.write_bytes(k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    pub = k.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    ENV.write_text(f"VAPID_PUBLIC={base64.urlsafe_b64encode(pub).decode().rstrip('=')}\nVAPID_SUB=mailto:contact@nebula-agency.online\n", encoding="utf-8")
    print("clés créées dans secrets/ (jamais commitées)")


def env():
    return dict(re.findall(r"^([A-Z_0-9]+)=(.+)$", ENV.read_text(encoding="utf-8"), re.M))


def push(titre, texte, cle="nebula", url="./", insiste=False):
    from pywebpush import WebPushException, webpush
    e, n = env(), 0
    with connexion() as c:
        for r in c.execute("select endpoint, p256dh, auth from public.nebula_suivi_abonnements").fetchall():
            try:
                webpush({"endpoint": r["endpoint"], "keys": {"p256dh": r["p256dh"], "auth": r["auth"]}},
                        json.dumps({"titre": titre, "texte": texte, "tag": cle, "url": url, "insiste": insiste}, ensure_ascii=False),
                        vapid_private_key=str(PEM), vapid_claims={"sub": e["VAPID_SUB"].strip()}, ttl=3600,
                        headers={"Urgency": "high"}, timeout=10)
                n += 1
            except WebPushException as x:
                if x.response is not None and x.response.status_code in (404, 410):
                    c.execute("delete from public.nebula_suivi_abonnements where endpoint = %s", (r["endpoint"],))
            except Exception as x:  # réseau : on le dit, on continue
                print("envoi :", type(x).__name__, str(x)[:120])
    print(f"notification envoyée à {n} appareil(s)")
    return n


def note(titre, texte=None, lien=None, genre="action", pousser=False):
    with connexion() as c:
        c.execute("insert into public.nebula_suivi_journal (genre, titre, texte, lien) values (%s,%s,%s,%s)", (genre, titre, texte, lien))
    print("journal :", titre)
    if pousser:
        push(titre, (texte or "")[:180] + (f"\n{lien}" if lien else ""), cle=f"{genre}-{datetime.now().timestamp():.0f}")


def prospects():
    """Le portefeuille vu de son téléphone : statut, dernier échange, prochaine action."""
    with connexion() as c:
        fiches = c.execute("select id, nom, metier, telephone, statut, score, notes, relance_le from piste.prospection").fetchall()
        derniers = {r["prospect_id"]: r for r in c.execute("""
            select distinct on (prospect_id) prospect_id, sens, quand, coalesce(nullif(transcription,''), nullif(texte,''), '[' || nature || ']') propos
            from piste.prospection_voix order by prospect_id, quand desc nulls last, rang desc""").fetchall()}
        c.execute("delete from public.nebula_suivi_prospects")
        for f in fiches:
            d = derniers.get(f["id"])
            dernier = None
            if d:
                q = d["quand"].astimezone(BENIN).strftime("%d/%m %H:%M") if d["quand"] else ""
                dernier = f"{q} · {'lui' if d['sens'] == 'eux' else 'nous'} : {re.sub(r'\s+', ' ', d['propos'] or '')[:160]}"
            notes = f["notes"] or ""
            m = re.search(r"(\d{2,3}[   ]?000)\s?F", notes)
            prochaine = f"relance le {f['relance_le'].astimezone(BENIN).strftime('%d/%m')}" if f["relance_le"] else None
            c.execute("""insert into public.nebula_suivi_prospects (id, nom, metier, telephone, statut, score, dernier, prochaine, montant)
                         values (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                      (f["id"], f["nom"], f["metier"], f["telephone"], f["statut"], f["score"], dernier, prochaine,
                       int(re.sub(r"\D", "", m.group(1))) if m else None))
    print(len(fiches), "prospects dans l'espace de suivi")


def chiffres(encaisse=None):
    with connexion() as c:
        s = {r["statut"]: r["n"] for r in c.execute("select statut, count(*) n from piste.prospection group by 1").fetchall()}
        contactes = sum(v for k, v in s.items() if k not in ("a_contacter", "ecarte", "injoignable"))
        c.execute("""insert into public.nebula_suivi_chiffres (jour, encaisse, contactes, reponses, interesses, payes)
                     values (%s, coalesce(%s, 0), %s, %s, %s, %s)
                     on conflict (jour) do update set encaisse = coalesce(%s, nebula_suivi_chiffres.encaisse), contactes = excluded.contactes,
                       reponses = excluded.reponses, interesses = excluded.interesses, payes = excluded.payes, maj = now()""",
                  (date.today(), encaisse, contactes, s.get("repondu", 0) + s.get("interesse", 0) + s.get("apercu", 0) + s.get("paye", 0),
                   s.get("interesse", 0) + s.get("apercu", 0), s.get("paye", 0), encaisse))
    print("chiffres du jour à jour", s)


def envois(chemin):
    d = json.load(io.open(chemin, encoding="utf-8"))
    with connexion() as c:
        for e in d:
            if not c.execute("select 1 from public.nebula_suivi_envois where telephone = %s and message = %s", (e["dix"], e["message"])).fetchone():
                c.execute("insert into public.nebula_suivi_envois (pour, telephone, message, heure) values (%s,%s,%s,%s)",
                          (e["nom"], e["dix"], e["message"], e.get("heure")))
    print(len(d), "messages dans la file")


if __name__ == "__main__":
    a = sys.argv[1:]
    drap = lambda n: (a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else None)
    libres = [x for i, x in enumerate(a[1:], 1) if not x.startswith("--") and not (i > 1 and a[i - 1] == "--genre")]
    {"cles": cles, "prospects": prospects,
     "note": lambda: note(libres[0], libres[1] if len(libres) > 1 else None, libres[2] if len(libres) > 2 else None,
                          drap("--genre") or "action", "--push" in a),
     "chiffres": lambda: chiffres(int(libres[0]) if libres else None),
     "envois": lambda: envois(libres[0]),
     "push": lambda: push(libres[0], libres[1] if len(libres) > 1 else "")}[a[0]]()
