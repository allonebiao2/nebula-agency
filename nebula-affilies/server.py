# -*- coding: utf-8 -*-
"""
NEBULA Affiliés — back-office du programme partenaires
======================================================
Système à deux faces, base de données SQLite, tout interconnecté :

  • ADMIN (Mongazi)  → /admin     : voit tous les affiliés + tous les clients,
                                    change les statuts, marque les paiements.
  • AFFILIÉ          → /partenaire : son espace « jeu vidéo » (rang, XP, RCM),
                                    ses clients en temps réel, son lien + QR.
  • PUBLIC           → /r/<code>   : le formulaire que l'affilié partage.

Quand un client remplit le formulaire d'un affilié :
  1. le lead est enregistré et rattaché à l'affilié (mémoire) ;
  2. l'ADMIN reçoit une notification ;
  3. le client apparaît chez l'AFFILIÉ avec le statut « Attente de validation ».
Mongazi fait ensuite évoluer le statut (En cours → Terminé / Annulé) et le
paiement (gris → vert fluo) : l'affilié est notifié à chaque étape.

Lancement local :  uvicorn server:app --port 8780 --reload
Stack identique à NEXO/Vendora (FastAPI + SQLite, 100% gratuit, sans CB).
"""
import os, json, time, pathlib, sqlite3, hmac, hashlib, base64, secrets, re, threading, datetime, contextlib
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import FastAPI, Request, Response, Cookie, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

try:
    from dotenv import load_dotenv
    HERE0 = pathlib.Path(__file__).resolve().parent
    load_dotenv(HERE0 / ".env")
    load_dotenv(HERE0.parent / "boutique-ia" / ".env", override=False)   # repli clé Claude (démo)
except Exception:
    pass

HERE = pathlib.Path(__file__).resolve().parent
DATA_DIR = pathlib.Path(os.getenv("NAFF_DATA_DIR", str(HERE)))   # volume persistant en prod
DATA_DIR.mkdir(parents=True, exist_ok=True)
DBF = DATA_DIR / "affilies.db"
SECRET_FILE = DATA_DIR / "secret.key"
if SECRET_FILE.exists():
    SECRET = SECRET_FILE.read_bytes()
else:
    SECRET = secrets.token_bytes(32); SECRET_FILE.write_bytes(SECRET)
COOKIE = "naff_session"

# ---- Identité NEBULA / paiement (repris de la maison) ----
MOMO_NUMBER = os.getenv("NAFF_MOMO_NUMBER", "0196740732")
MOMO_NAME   = os.getenv("NAFF_MOMO_NAME", "BIAO Mongazi Yan Karl")
WHATSAPP    = os.getenv("NAFF_WHATSAPP", "+22996740732")

# ---- Compte ADMIN (Mongazi) ----
ADMIN_EMAILS = set(e.strip().lower() for e in os.getenv(
    "NAFF_ADMIN_EMAILS",
    "allonebiao@gmail.com,allonebiao2@gmail.com,mongazi@nebula-agency.online").split(",") if e.strip())
ADMIN_PASS = os.getenv("NAFF_ADMIN_PASS", "founder123")

# ---- Cerveau IA « NOVA » (Claude) ----
BRAIN_MODEL = os.getenv("NAFF_BRAIN_MODEL", "claude-sonnet-4-6")
def anthropic_key() -> str:
    return os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY") or ""

# ---- Notifications Telegram (push réel pour Mongazi — gratuit, optionnel) ----
TG_TOKEN = os.getenv("NAFF_TG_TOKEN", "")
TG_CHAT = os.getenv("NAFF_TG_CHAT", "")
def tg_send(text: str):
    if not (TG_TOKEN and TG_CHAT):
        return
    def _go():
        try:
            httpx.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                       json={"chat_id": TG_CHAT, "text": text}, timeout=6)
        except Exception:
            pass
    threading.Thread(target=_go, daemon=True).start()

# ---- Catalogue NEBULA (grille tarifaire réelle, sert au calcul RCM) ----
SERVICES: Dict[str, Dict[str, Any]] = {
    "vitrine":          {"label": "Vitrine Digitale + QR Code",   "price": 150000},
    "catalogue":        {"label": "Catalogue Digital + QR Code",  "price": 50000},
    "maps":             {"label": "Fiche Google Maps",            "price": 20000},
    "review":           {"label": "QR Code Google Review",        "price": 30000},
    "avatar_essentiel": {"label": "Avatar IA — Essentiel (/mois)", "price": 30000},
    "avatar_pro":       {"label": "Avatar IA — Pro (/mois)",       "price": 100000},
    "autre":            {"label": "Autre / à discuter",            "price": 0},
}
# Taux de commission affilié par défaut (modifiable — à valider par Mongazi).
COMMISSION_RATE = float(os.getenv("NAFF_COMMISSION_RATE", "0.10"))

# ---- Statuts du travail côté NEBULA ----
STATUSES: Dict[str, Dict[str, str]] = {
    "attente":  {"label": "Attente de validation", "color": "#f5b14c"},
    "en_cours": {"label": "En cours",              "color": "#4cc6ff"},
    "termine":  {"label": "Terminé",               "color": "#36f5a0"},
    "annule":   {"label": "Annulé",                "color": "#ff5c7a"},
}
STATUS_POINTS = {"attente": 10, "en_cours": 35, "termine": 70, "annule": 0}
PAID_BONUS = 30

# ---- RANKS cosmiques : PRESTIGE, selon les VENTES CUMULÉES (toute la carrière) ----
RANKS: List[Tuple[int, str, str]] = [
    (0,   "Recrue",    "✦"),
    (1,   "Météore",   "🌑"),
    (6,   "Comète",    "☄️"),
    (16,  "Planète",   "🪐"),
    (36,  "Étoile",    "⭐"),
    (66,  "Supernova", "💥"),
    (111, "Nébuleuse", "🌌"),
    (151, "Galaxie",   "👑"),
]
# ---- PALIERS mensuels : ta COMMISSION DIRECTE, selon les ventes DU MOIS (remis à zéro) ----
# (seuil mini de ventes du mois, label, emoji, taux direct)
PALIERS: List[Tuple[int, str, str, float]] = [
    (0,  "STARTER", "⬜", 0.25),   # 1 à 4 ventes / mois
    (5,  "SILVER",  "🟣", 0.30),   # 5 à 9 ventes / mois
    (10, "GOLD",    "🟡", 0.35),   # 10+ ventes / mois
]
# ---- Profondeurs réseau (FIXES, identiques pour tous — Vague B : parrainage) ----
DEPTH_N1 = 0.10   # sur les ventes de tes recrues directes
DEPTH_N2 = 0.05   # sur les ventes des recrues de tes recrues
# Réseaux Mobile Money du Bénin
RESEAUX = ["MTN MoMo", "Moov Money", "Celtiis Cash"]

# ---- Documentation & Publication (bibliothèques gérées par l'admin) ----
UP_DIR = DATA_DIR / "uploads"
UP_DIR.mkdir(parents=True, exist_ok=True)
DOC_CATEGORIES = ["Vente", "Formation", "Produits", "Juridique", "Marketing", "Autre"]
PLATFORMS = ["WhatsApp", "Facebook", "Instagram", "TikTok", "Statut/Story", "Autre"]
PUB_TYPES = {"post": "Publication", "image": "Visuel", "video": "Vidéo", "script": "Script"}

# ---- Conditions Générales du Programme Partenaires (acceptation obligatoire) ----
TERMS_VERSION = "1.0"   # incrémenter à chaque révision -> ré-acceptation tracée
TERMS_HTML = """
<h3>Conditions Générales du Programme Partenaires NEBULA Agency</h3>
<p class="faint">Version 1.0 — Cotonou, Bénin. En soumettant ta candidature, tu reconnais avoir lu et accepté l'intégralité des présentes conditions.</p>

<h4>1. Objet</h4>
<p>Les présentes conditions régissent la relation entre <b>NEBULA Agency</b> (« NEBULA ») et toute personne admise comme <b>partenaire apporteur d'affaires</b> (« le Partenaire »). Le Partenaire présente les produits et services de NEBULA (vitrines digitales, catalogues, fiches Google, avatars IA et services associés) à des clients potentiels, en échange de commissions.</p>

<h4>2. Adhésion</h4>
<p>L'adhésion est <b>gratuite</b> et soumise à validation de NEBULA, qui reste libre d'accepter ou de refuser une candidature. À la validation, le Partenaire reçoit un code d'accès personnel et un code PIN, strictement personnels et confidentiels.</p>

<h4>3. Statut du Partenaire</h4>
<p>Le Partenaire agit en <b>professionnel indépendant</b>. Les présentes ne créent <b>aucun contrat de travail</b>, ni mandat de représentation légale, ni société entre les parties. Le Partenaire ne peut ni engager NEBULA, ni encaisser de paiement au nom de NEBULA, ni promettre des prestations non prévues.</p>

<h4>4. Commissions</h4>
<p>La commission directe du Partenaire dépend de son <b>palier mensuel</b> (de 25% à 35% selon le nombre de ventes du mois). Le Partenaire perçoit également une commission de <b>profondeur</b> sur son réseau : <b>10% (Niveau&nbsp;1)</b> sur les ventes de ses recrues directes et <b>5% (Niveau&nbsp;2)</b> sur celles de leurs recrues. Une commission n'est due que lorsque le <b>client a effectivement payé</b> NEBULA. Le versement se fait par Mobile Money sur le numéro déclaré par le Partenaire, après réclamation et validation.</p>

<h4>5. Obligations & éthique</h4>
<p>Le Partenaire s'engage à représenter NEBULA avec honnêteté : pas de fausses promesses, pas de prix inventés, pas de spam ni de pratiques trompeuses, respect de l'image de NEBULA et des personnes contactées. Tout manquement peut entraîner la suspension ou l'exclusion.</p>

<h4>6. Propriété intellectuelle</h4>
<p>Les documents, visuels, vidéos et scripts mis à disposition restent la propriété de NEBULA et sont fournis <b>uniquement</b> pour promouvoir ses offres. Toute autre utilisation, modification dénaturante ou revente est interdite.</p>

<h4>7. Données personnelles (loi béninoise / APDP)</h4>
<p>Les informations collectées (identité, contact, Mobile Money) servent uniquement à la gestion du programme et au versement des commissions. Elles ne sont pas cédées à des tiers à des fins commerciales. Le Partenaire peut demander l'accès, la rectification ou l'effacement de ses données.</p>

<h4>8. Durée & résiliation</h4>
<p>L'adhésion est à durée indéterminée. Chaque partie peut y mettre fin à tout moment. Les commissions dûment acquises sur des ventes déjà payées restent versées. NEBULA peut suspendre un accès en cas de manquement aux présentes.</p>

<h4>9. Modification</h4>
<p>NEBULA peut faire évoluer les présentes conditions et la grille de commissions. Le Partenaire en est informé ; la poursuite de l'activité vaut acceptation de la version en vigueur.</p>

<h4>10. Droit applicable</h4>
<p>Les présentes sont régies par le <b>droit béninois</b>. En cas de différend, les parties privilégient un règlement amiable avant toute action.</p>
"""

# ----------------------------------------------------------------------------
# Base de données (SQLite — mémoire persistante, tout interconnecté)
# ----------------------------------------------------------------------------
@contextlib.contextmanager
def db():
    c = sqlite3.connect(DBF, timeout=30)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()

def init_db():
    with db() as c:
        c.execute("PRAGMA journal_mode=WAL")     # lecteurs + 1 écrivain concurrents
        c.execute("""CREATE TABLE IF NOT EXISTS affiliates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            nom TEXT, prenom TEXT,
            momo_number TEXT, momo_reseau TEXT,
            pin TEXT NOT NULL,
            accent TEXT DEFAULT '#7b5cff',
            actif INTEGER DEFAULT 1,
            created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS leads(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            affiliate_id INTEGER NOT NULL,
            nom TEXT, prenom TEXT, numero TEXT,
            service TEXT, message TEXT,
            status TEXT DEFAULT 'attente',
            paye INTEGER DEFAULT 0,
            montant REAL DEFAULT 0,
            created REAL, updated REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            old_status TEXT, new_status TEXT,
            note TEXT, at REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS notifs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_role TEXT NOT NULL,    -- 'admin' | 'affiliate'
            target_id INTEGER DEFAULT 0,  -- id affilié (0 = admin global)
            lead_id INTEGER,
            text TEXT, lu INTEGER DEFAULT 0, created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS brain_msgs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope TEXT NOT NULL,          -- 'admin' | 'aff'
            scope_id INTEGER DEFAULT 0,   -- id affilié (0 = admin)
            who TEXT,                     -- 'user' | 'nova'
            text TEXT, created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS recruits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parrain_id INTEGER NOT NULL,         -- affilié qui recrute
            nom TEXT, prenom TEXT, numero TEXT,
            momo_number TEXT, momo_reseau TEXT, message TEXT,
            status TEXT DEFAULT 'pending',       -- 'pending' | 'approved' | 'rejected'
            created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS commissions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            beneficiary_id INTEGER NOT NULL,     -- affilié qui touche
            level TEXT,                          -- 'direct' | 'n1' | 'n2'
            amount REAL,
            status TEXT DEFAULT 'due',           -- 'due' | 'claimed' | 'paid' | 'void'
            created REAL, claimed_at REAL, paid_at REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS candidatures(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT, prenom TEXT, email TEXT, numero TEXT, ville TEXT,
            momo_number TEXT, momo_reseau TEXT,
            experience TEXT, motivation TEXT, canaux TEXT,
            parrain_code TEXT DEFAULT '',
            terms_version TEXT, accepted_at REAL, ip TEXT,
            status TEXT DEFAULT 'pending',       -- 'pending' | 'approved' | 'rejected'
            created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS documents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, category TEXT, description TEXT,
            kind TEXT DEFAULT 'note',            -- 'note' (texte) | 'pdf' (fichier) | 'link'
            body TEXT DEFAULT '',                -- contenu HTML pour 'note'
            url TEXT DEFAULT '',                 -- pour 'link'
            filename TEXT DEFAULT '', size INTEGER DEFAULT 0,
            updated REAL, created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS publications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, ptype TEXT DEFAULT 'post',   -- post | image | video | script
            body TEXT DEFAULT '', script TEXT DEFAULT '',
            platforms TEXT DEFAULT '',               -- csv
            media_kind TEXT DEFAULT 'none',          -- none | image | video | link
            media_url TEXT DEFAULT '', filename TEXT DEFAULT '',
            updated REAL, created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope TEXT,                  -- 'general' | 'dm'
            pair TEXT DEFAULT '',        -- pour 'dm' : 'uidA|uidB' trié
            sender_uid TEXT, text TEXT, created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS chat_reads(
            uid TEXT, channel TEXT, last_read REAL,
            PRIMARY KEY(uid, channel))""")
        c.execute("""CREATE TABLE IF NOT EXISTS app_settings(
            k TEXT PRIMARY KEY, v TEXT)""")
init_db()

def migrate():
    with db() as c:
        for col, ddl in [("pseudo", "TEXT DEFAULT ''"), ("parrain_id", "INTEGER DEFAULT 0"), ("photo", "TEXT DEFAULT ''")]:
            try:
                c.execute(f"ALTER TABLE affiliates ADD COLUMN {col} {ddl}")
            except Exception:
                pass
migrate()

# ----------------------------------------------------------------------------
# Sécurité : PIN/mot de passe (PBKDF2) + sessions (cookie signé HMAC)
# ----------------------------------------------------------------------------
def hash_pw(pw: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 120_000)
    return salt.hex() + "$" + dk.hex()

def check_pw(pw: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt_hex), 120_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False

def make_token(role: str, sid: int) -> str:
    body = f"{role}.{sid}.{int(time.time()) + 60*60*24*30}".encode()      # 30 jours
    sig = hmac.new(SECRET, body, hashlib.sha256).digest()[:16]
    return base64.urlsafe_b64encode(body + b"." + sig).decode()

def read_token(tok: str) -> Optional[Tuple[str, int]]:
    try:
        raw = base64.urlsafe_b64decode(tok.encode())
        body, sig = raw.rsplit(b".", 1)
        if not hmac.compare_digest(hmac.new(SECRET, body, hashlib.sha256).digest()[:16], sig):
            return None
        role, sid_s, exp_s = body.decode().split(".")
        if int(exp_s) < time.time():
            return None
        return (role, int(sid_s))
    except Exception:
        return None

def actor(cookie_val: Optional[str]) -> Optional[Tuple[str, int]]:
    if not cookie_val:
        return None
    return read_token(cookie_val)

def set_cookie(resp: Response, role: str, sid: int):
    resp.set_cookie(COOKIE, make_token(role, sid), max_age=60*60*24*30,
                    httponly=True, samesite="lax")

# ----------------------------------------------------------------------------
# Logique métier : rangs, score, RCM (commission)
# ----------------------------------------------------------------------------
def rank_for(n: int) -> Dict[str, Any]:
    cur = RANKS[0]; nxt = None
    for i, r in enumerate(RANKS):
        if n >= r[0]:
            cur = r
            nxt = RANKS[i+1] if i+1 < len(RANKS) else None
    level = RANKS.index(cur)
    if nxt:
        span = nxt[0] - cur[0]
        done = n - cur[0]
        xp_pct = int(min(100, max(0, round(done * 100 / span)))) if span else 100
        to_next = max(0, nxt[0] - n)
    else:
        xp_pct = 100; to_next = 0
    return {
        "label": cur[1], "emoji": cur[2], "level": level, "max_level": len(RANKS) - 1,
        "next_label": nxt[1] if nxt else None, "next_emoji": nxt[2] if nxt else None,
        "xp_pct": xp_pct, "to_next": to_next, "threshold": cur[0],
        "next_threshold": nxt[0] if nxt else None,
    }

def month_start_ts() -> float:
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, 1).timestamp()

def palier_for(ventes_mois: int) -> Dict[str, Any]:
    cur = PALIERS[0]; nxt = None
    for i, p in enumerate(PALIERS):
        if ventes_mois >= p[0]:
            cur = p; nxt = PALIERS[i+1] if i+1 < len(PALIERS) else None
    return {
        "label": cur[1], "emoji": cur[2], "rate": cur[3], "pct": int(round(cur[3] * 100)),
        "next_label": nxt[1] if nxt else None, "next_emoji": nxt[2] if nxt else None,
        "next_pct": int(round(nxt[3] * 100)) if nxt else None,
        "to_next": max(0, nxt[0] - ventes_mois) if nxt else 0,
        "min": cur[0], "next_min": nxt[0] if nxt else None,
    }

def commission_of(service: str, montant: float, rate: float = 0.25) -> int:
    base = montant if montant and montant > 0 else SERVICES.get(service, {}).get("price", 0)
    return int(round(base * rate))

def stats_of(affiliate_id: int) -> Dict[str, Any]:
    with db() as c:
        rows = c.execute("SELECT * FROM leads WHERE affiliate_id=?", (affiliate_id,)).fetchall()
    by_status = {k: 0 for k in STATUSES}
    ms = month_start_ts()
    score = 0; nb_real = 0; ventes = 0; ventes_mois = 0
    for r in rows:
        st = r["status"] or "attente"
        by_status[st] = by_status.get(st, 0) + 1
        score += STATUS_POINTS.get(st, 0)
        if r["paye"]:
            score += PAID_BONUS
            ventes += 1                                   # une VENTE = un client qui a payé
            if (r["updated"] or 0) >= ms:
                ventes_mois += 1
        if st != "annule":
            nb_real += 1
    pal = palier_for(ventes_mois)                         # palier du mois -> taux direct
    rate = pal["rate"]
    rcm = 0; potentiel = 0
    for r in rows:
        com = commission_of(r["service"], r["montant"], rate)
        if r["paye"]:
            rcm += com
        elif (r["status"] or "attente") != "annule":
            potentiel += com
    return {
        "nb_total": len(rows), "nb_real": nb_real, "by_status": by_status,
        "score": score, "ventes": ventes, "ventes_mois": ventes_mois,
        "rcm": rcm, "potentiel": potentiel, "direct_rate": rate,
        "rank": rank_for(ventes), "palier": pal,
    }

def _paid_value(aid: int) -> Tuple[int, int]:
    """(nb ventes payées, valeur totale FCFA) d'un affilié."""
    with db() as c:
        paid = c.execute("SELECT service, montant FROM leads WHERE affiliate_id=? AND paye=1", (aid,)).fetchall()
    val = sum((r["montant"] if r["montant"] else SERVICES.get(r["service"], {}).get("price", 0)) for r in paid)
    return len(paid), int(val)

def network_of(aid: int) -> Dict[str, Any]:
    """Réseau d'un affilié en ARBRE : N1 (recrues directes, 10%), chaque N1 portant ses N2 (5%)."""
    def line(a, rate):
        cnt, val = _paid_value(a["id"])
        return {"name": affiliate_label(a), "code": a["code"], "ventes": cnt, "commission": int(round(val * rate))}
    with db() as c:
        n1 = c.execute("SELECT * FROM affiliates WHERE parrain_id=? AND actif=1 ORDER BY created", (aid,)).fetchall()
    n1_list = []; n1_comm = 0; n2_comm = 0; n2_count = 0
    for a in n1:
        with db() as c:
            kids = c.execute("SELECT * FROM affiliates WHERE parrain_id=? AND actif=1 ORDER BY created", (a["id"],)).fetchall()
        children = [line(k, DEPTH_N2) for k in kids]
        n2_count += len(children)
        n2_comm += sum(x["commission"] for x in children)
        node = line(a, DEPTH_N1); node["children"] = children
        n1_comm += node["commission"]
        n1_list.append(node)
    return {
        "n1": n1_list, "n1_count": len(n1_list), "n2_count": n2_count,
        "n1_commission": n1_comm, "n2_commission": n2_comm, "network_total": n1_comm + n2_comm,
    }

def notify(role: str, target_id: int, text: str, lead_id: Optional[int] = None):
    with db() as c:
        c.execute("INSERT INTO notifs(target_role,target_id,lead_id,text,lu,created) VALUES(?,?,?,?,0,?)",
                  (role, target_id, lead_id, text, time.time()))

def affiliate_label(a: sqlite3.Row) -> str:
    nom = " ".join(x for x in [a["prenom"], a["nom"]] if x).strip()
    return nom or a["code"]

def clean(s: Any, n: int = 200) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]

# ----------------------------------------------------------------------------
# Seed : compte démo pour cliquer tout de suite
# ----------------------------------------------------------------------------
def new_code(c) -> str:
    alpha = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # sans I,O,0,1 ambigus
    while True:
        code = "".join(secrets.choice(alpha) for _ in range(5))
        if not c.execute("SELECT 1 FROM affiliates WHERE code=?", (code,)).fetchone():
            return code

def fmoney(n) -> str:
    return f"{int(round(n or 0)):,}".replace(",", " ")

def generate_commissions(lead: sqlite3.Row):
    """À la vente PAYÉE : crée auto les commissions direct + N1 + N2 et alerte chaque bénéficiaire."""
    entries = []  # (beneficiary_id, level, amount)
    with db() as c:
        if c.execute("SELECT COUNT(*) n FROM commissions WHERE lead_id=? AND status!='void'", (lead["id"],)).fetchone()["n"]:
            return  # idempotent : déjà généré
        aff = c.execute("SELECT * FROM affiliates WHERE id=?", (lead["affiliate_id"],)).fetchone()
        if not aff:
            return
        price = lead["montant"] if lead["montant"] else SERVICES.get(lead["service"], {}).get("price", 0)
        rate = stats_of(aff["id"])["direct_rate"]
        entries.append((aff["id"], "direct", int(round(price * rate))))
        p1 = c.execute("SELECT * FROM affiliates WHERE id=? AND actif=1", (aff["parrain_id"] or 0,)).fetchone()
        if p1:
            entries.append((p1["id"], "n1", int(round(price * DEPTH_N1))))
            p2 = c.execute("SELECT * FROM affiliates WHERE id=? AND actif=1", (p1["parrain_id"] or 0,)).fetchone()
            if p2:
                entries.append((p2["id"], "n2", int(round(price * DEPTH_N2))))
        now = time.time()
        for bid, lvl, amt in entries:
            if amt > 0:
                c.execute("INSERT INTO commissions(lead_id,beneficiary_id,level,amount,status,created) VALUES(?,?,?,?,'due',?)",
                          (lead["id"], bid, lvl, amt, now))
    client = (str(lead["prenom"] or "") + " " + str(lead["nom"] or "")).strip()
    labels = {"direct": "vente directe", "n1": "réseau N1", "n2": "réseau N2"}
    nb = 0
    for bid, lvl, amt in entries:
        if amt > 0:
            nb += 1
            notify("affiliate", bid, f"Commission à réclamer : {fmoney(amt)} F ({labels[lvl]}) sur la vente de {client}.", lead["id"])
    notify("admin", 0, f"Commissions générées sur la vente de {client} — {nb} bénéficiaire(s) à payer.", lead["id"])

def void_commissions(lead_id: int):
    with db() as c:
        c.execute("UPDATE commissions SET status='void' WHERE lead_id=? AND status!='paid'", (lead_id,))

def earnings_of(aid: int) -> Dict[str, int]:
    """Bilan complet (à vie) des commissions d'un affilié, depuis le registre tracé."""
    with db() as c:
        rows = c.execute("SELECT level, amount, status FROM commissions WHERE beneficiary_id=? AND status!='void'", (aid,)).fetchall()
    g = {"generated": 0, "paid": 0, "due": 0, "claimed": 0, "direct": 0, "n1": 0, "n2": 0}
    for r in rows:
        a = r["amount"] or 0
        g["generated"] += a
        g[r["status"]] = g.get(r["status"], 0) + a
        g[r["level"]] = g.get(r["level"], 0) + a
    return {k: int(v) for k, v in g.items()}

async def store_upload(up: UploadFile, prefix: str) -> Tuple[str, int]:
    """Enregistre un fichier uploadé sur le volume et renvoie (nom_stocké, taille)."""
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", (up.filename or "fichier"))[:60]
    name = f"{prefix}_{int(time.time())}_{secrets.token_hex(3)}_{safe}"
    data = await up.read()
    (UP_DIR / name).write_bytes(data)
    return name, len(data)

def seed_content():
    """Documents & publications de départ (modèles NEBULA pro, immédiatement utiles)."""
    now = time.time()
    with db() as c:
        if not c.execute("SELECT COUNT(*) n FROM documents").fetchone()["n"]:
            docs = [
                ("Guide de démarrage du partenaire", "Formation",
                 "Tes 3 premières ventes, pas à pas.",
                 "<h4>Bienvenue dans l'équipe NEBULA</h4><p>Ton métier : présenter nos offres à des commerçants et encaisser des commissions. Pas de stock, pas de capital.</p>"
                 "<h4>1. Récupère ton lien</h4><p>Onglet <b>Mon lien</b> → copie-le. Tout client qui le remplit devient le tien automatiquement.</p>"
                 "<h4>2. Vise les bons commerçants</h4><ul><li>Boutiques de mode, cosmétiques, pâtisseries, bijoux</li><li>Prestataires (coiffure, déco, événementiel)</li><li>Toute personne qui vend déjà sur WhatsApp</li></ul>"
                 "<h4>3. Le bon message</h4><p>« Bonjour, j'aide les commerçants à avoir une <b>vitrine digitale pro + QR code</b> pour vendre mieux sur WhatsApp. Je peux vous montrer un exemple ? »</p>"
                 "<h4>4. Envoie ton lien</h4><p>Le commerçant remplit, NEBULA s'occupe de la réalisation, tu touches ta commission quand il paie. Vise 3 contacts par jour.</p>"),
                ("Vitrine Digitale + QR — fiche produit & argumentaire", "Produits",
                 "Le produit phare à 150 000 F.",
                 "<h4>C'est quoi</h4><p>Un site vitrine moderne (mobile, rapide, élégant) avec galerie, services, témoignages, bouton WhatsApp, + un <b>QR code</b> à coller en boutique et sur les emballages.</p>"
                 "<h4>Prix</h4><p><b>150 000 FCFA</b>. C'est ton produit le plus rémunérateur.</p>"
                 "<h4>Pourquoi le commerçant en a besoin</h4><ul><li>Il paraît 10× plus professionnel qu'un concurrent sans site</li><li>Il partage <b>un seul lien</b> au lieu de répéter prix et photos</li><li>Le QR transforme chaque client en visiteur de sa vitrine</li></ul>"
                 "<h4>Phrase qui marche</h4><p>« Aujourd'hui, un client qui hésite va voir si vous avez une présence sérieuse en ligne. Cette vitrine, c'est votre boutique ouverte 24h/24. »</p>"),
                ("Catalogue Digital + QR — fiche produit & argumentaire", "Produits",
                 "Le produit d'appel facile à vendre à 50 000 F.",
                 "<h4>C'est quoi</h4><p>Un catalogue digital de produits (photos, prix, descriptions) avec QR code. Plus léger que la vitrine, idéal pour démarrer.</p>"
                 "<h4>Prix</h4><p><b>50 000 FCFA</b> — la porte d'entrée parfaite : petit budget, grand effet.</p>"
                 "<h4>Argument clé</h4><p>« Au lieu d'envoyer 20 photos une par une sur WhatsApp, vous envoyez <b>un seul lien</b> où tout est rangé, avec les prix. Vos clients commandent plus vite. »</p>"
                 "<h4>Astuce</h4><p>Beaucoup de commerçants commencent par le catalogue, puis prennent la vitrine. Commence petit, monte ensuite.</p>"),
                ("Répondre aux objections", "Vente",
                 "Les 5 phrases qui débloquent une vente.",
                 "<h4>« C'est trop cher »</h4><p>« Je comprends. Combien vous rapporte <b>un seul</b> nouveau client par semaine ? La vitrine se rembourse en quelques ventes, et elle travaille pour vous tous les jours. »</p>"
                 "<h4>« Je vais réfléchir »</h4><p>« Bien sûr. Pour vous aider à décider : qu'est-ce qui vous retient — le budget, le moment, ou vous voulez voir un exemple ? »</p>"
                 "<h4>« J'ai déjà Facebook »</h4><p>« Parfait, on ne le remplace pas, on le renforce : votre vitrine, c'est l'endroit sérieux où vous envoyez les gens depuis Facebook et WhatsApp. »</p>"
                 "<h4>« Ça marche vraiment ? »</h4><p>Montre un exemple réalisé par NEBULA. Une preuve vaut mille arguments.</p>"
                 "<h4>« Je n'ai pas le temps »</h4><p>« Justement, vous n'avez rien à faire : vous m'envoyez vos photos et infos, NEBULA s'occupe de tout. »</p>"),
                ("Tes commissions expliquées", "Formation",
                 "Paliers, profondeurs, paiement.",
                 "<h4>Ta commission directe (palier du mois)</h4><ul><li><b>STARTER</b> (1 à 4 ventes/mois) : 25%</li><li><b>SILVER</b> (5 à 9 ventes/mois) : 30%</li><li><b>GOLD</b> (10+ ventes/mois) : 35%</li></ul><p>Remis à zéro chaque mois : plus tu vends dans le mois, plus ton % monte.</p>"
                 "<h4>Ton réseau (profondeurs)</h4><p>Tu gagnes aussi <b>10%</b> sur les ventes des partenaires que tu recrutes (N1) et <b>5%</b> sur celles de leurs recrues (N2).</p>"
                 "<h4>Quand es-tu payé ?</h4><p>Dès que ton client a payé NEBULA, ta commission apparaît dans <b>Mes gains</b>. Tu cliques <b>Réclamer</b>, et NEBULA te verse sur ton Mobile Money.</p>"),
            ]
            for t, cat, desc, body in docs:
                c.execute("INSERT INTO documents(title,category,description,kind,body,updated,created) VALUES(?,?,?,'note',?,?,?)",
                          (t, cat, desc, body, now, now))
        if not c.execute("SELECT COUNT(*) n FROM publications").fetchone()["n"]:
            pubs = [
                ("Script d'approche WhatsApp", "script", "WhatsApp",
                 "Bonjour 👋 Je travaille avec NEBULA Agency. J'aide les commerçants comme vous à avoir une vitrine digitale professionnelle (+ QR code) pour vendre plus facilement sur WhatsApp. Je peux vous montrer un exemple, sans engagement ?",
                 "Étape 1 : saluer + qui tu es.\nÉtape 2 : la valeur en 1 phrase (vendre plus facilement).\nÉtape 3 : proposer un exemple (petite demande, facile à accepter).\nÉtape 4 : s'il dit oui → envoie ton lien et un exemple de vitrine."),
                ("Post de présentation — Facebook", "post", "Facebook",
                 "Commerçant(e) à Cotonou ? 📲 Offrez à votre business une VITRINE DIGITALE professionnelle + QR code : vos produits, vos prix, votre WhatsApp — tout au même endroit, accessible 24h/24.\n\nÀ partir de 50 000 FCFA (catalogue) — vitrine complète 150 000 FCFA.\nÉcrivez-moi en privé 👇",
                 ""),
                ("Légende Instagram", "post", "Instagram",
                 "Votre boutique mérite mieux qu'un feed. ✨\nUne vitrine digitale pro + QR code pour transformer vos visiteurs en clients.\n\n#Cotonou #Bénin #commerce #digital #QRcode #NEBULA",
                 ""),
                ("Script de relance (48h sans réponse)", "script", "WhatsApp",
                 "Bonjour, je reviens vers vous 🙂 Avez-vous eu le temps de regarder l'exemple de vitrine que je vous ai envoyé ? Je peux répondre à vos questions ou vous montrer une autre réalisation si vous préférez.",
                 "Reste léger et utile, jamais insistant. Une seule relance polie. Propose de la valeur (un autre exemple), pas de pression."),
            ]
            for t, pt, plat, body, script in pubs:
                c.execute("INSERT INTO publications(title,ptype,body,script,platforms,media_kind,updated,created) VALUES(?,?,?,?,?,'none',?,?)",
                          (t, pt, body, script, plat, now, now))

def seed():
    with db() as c:
        if c.execute("SELECT COUNT(*) n FROM affiliates").fetchone()["n"]:
            return
        # Affilié démo : code DEMO, PIN 1234
        c.execute("""INSERT INTO affiliates(code,nom,prenom,momo_number,momo_reseau,pin,accent,actif,created)
                     VALUES('DEMO','Akpaki','Rodrigue','0190000000','MTN MoMo',?,?,1,?)""",
                  (hash_pw("1234"), "#7b5cff", time.time()))
        aid = c.execute("SELECT id FROM affiliates WHERE code='DEMO'").fetchone()["id"]
        demo = [
            ("Sossou", "Mariam", "0197111111", "vitrine",   "Boutique de pagnes, veut une vitrine", "termine",  1),
            ("Dossou", "Karl",   "0197222222", "catalogue", "Catalogue cosmétiques",                "en_cours", 0),
            ("Adjovi", "Bénédicta","0197333333","avatar_pro","Veut des vidéos avatar IA",            "attente",  0),
        ]
        now = time.time()
        for i, (nom, prenom, num, svc, msg, st, paye) in enumerate(demo):
            c.execute("""INSERT INTO leads(affiliate_id,nom,prenom,numero,service,message,status,paye,created,updated)
                         VALUES(?,?,?,?,?,?,?,?,?,?)""",
                      (aid, nom, prenom, num, svc, msg, st, paye, now - (i+1)*3600, now - (i+1)*1800))
    notify("admin", 0, "Bienvenue dans NEBULA Affiliés — voici un affilié démo (code DEMO).")
seed()
seed_content()

# ----------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------
app = FastAPI(title="NEBULA Affiliés")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=True)
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")

def page(name: str) -> FileResponse:
    return FileResponse(str(HERE / name), media_type="text/html")

@app.get("/", response_class=HTMLResponse)
def home():
    return page("index.html")

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return page("admin.html")

@app.get("/partenaire", response_class=HTMLResponse)
def partner_page():
    return page("partenaire.html")

@app.get("/r/{code}", response_class=HTMLResponse)
def referral_page(code: str):
    return page("lead.html")

@app.get("/rejoindre/{code}", response_class=HTMLResponse)
def recruit_page(code: str):
    return page("rejoindre.html")

@app.get("/devenir", response_class=HTMLResponse)
def devenir_page():
    return page("devenir.html")

# ---- Config publique (catalogue, statuts, réseaux) pour les fronts ----
@app.get("/api/config")
def api_config():
    return {
        "services": SERVICES, "statuses": STATUSES, "reseaux": RESEAUX,
        "commission_rate": COMMISSION_RATE, "momo": {"number": MOMO_NUMBER, "name": MOMO_NAME},
        "whatsapp": WHATSAPP, "ranks": [{"min": r[0], "label": r[1], "emoji": r[2]} for r in RANKS],
        "paliers": [{"min": p[0], "label": p[1], "emoji": p[2], "pct": int(round(p[3] * 100))} for p in PALIERS],
        "depths": {"n1": int(DEPTH_N1 * 100), "n2": int(DEPTH_N2 * 100)},
    }

# =====================  PUBLIC : formulaire de parrainage  ====================
@app.get("/api/affiliate/{code}/public")
def affiliate_public(code: str):
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE code=? AND actif=1", (code.upper(),)).fetchone()
    if not a:
        return JSONResponse({"ok": False, "error": "Lien partenaire introuvable."}, status_code=404)
    return {"ok": True, "code": a["code"], "name": affiliate_label(a)}

@app.post("/api/lead")
async def create_lead(req: Request):
    d = await req.json()
    code = clean(d.get("code"), 12).upper()
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE code=? AND actif=1", (code,)).fetchone()
        if not a:
            return JSONResponse({"ok": False, "error": "Lien partenaire invalide."}, status_code=404)
        nom = clean(d.get("nom"), 80); prenom = clean(d.get("prenom"), 80)
        numero = clean(d.get("numero"), 30); service = clean(d.get("service"), 40)
        message = clean(d.get("message"), 500)
        if not (nom or prenom) or not numero:
            return JSONResponse({"ok": False, "error": "Nom et numéro obligatoires."}, status_code=400)
        if service not in SERVICES:
            service = "autre"
        now = time.time()
        cur = c.execute("""INSERT INTO leads(affiliate_id,nom,prenom,numero,service,message,status,paye,created,updated)
                           VALUES(?,?,?,?,?,?,'attente',0,?,?)""",
                        (a["id"], nom, prenom, numero, service, message, now, now))
        lead_id = cur.lastrowid
    client = (prenom + " " + nom).strip()
    svc = SERVICES[service]["label"]
    notify("admin", 0, f"Nouveau client via {affiliate_label(a)} : {client} — {svc}", lead_id)
    notify("affiliate", a["id"], f"{client} a rempli ton formulaire — en attente de validation.", lead_id)
    return {"ok": True}

@app.post("/api/recruit")
async def create_recruit(req: Request):
    d = await req.json()
    code = clean(d.get("code"), 12).upper()
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE code=? AND actif=1", (code,)).fetchone()
        if not a:
            return JSONResponse({"ok": False, "error": "Lien parrain invalide."}, status_code=404)
        nom = clean(d.get("nom"), 80); prenom = clean(d.get("prenom"), 80)
        numero = clean(d.get("numero"), 30)
        momo = clean(d.get("momo_number"), 30); reseau = clean(d.get("momo_reseau"), 30) or RESEAUX[0]
        msg = clean(d.get("message"), 300)
        if not (nom or prenom) or not numero:
            return JSONResponse({"ok": False, "error": "Nom et numéro obligatoires."}, status_code=400)
        c.execute("""INSERT INTO recruits(parrain_id,nom,prenom,numero,momo_number,momo_reseau,message,status,created)
                     VALUES(?,?,?,?,?,?,?,'pending',?)""",
                  (a["id"], nom, prenom, numero, momo, reseau, msg, time.time()))
    who = (prenom + " " + nom).strip()
    notify("admin", 0, f"Nouvelle recrue : {who} ({numero}) — parrainé(e) par {affiliate_label(a)}")
    notify("affiliate", a["id"], f"{who} veut rejoindre via ton lien — en attente de validation NEBULA.")
    return {"ok": True}

# =============================  AUTH  ========================================
@app.post("/api/admin/login")
async def admin_login(req: Request, resp: Response):
    d = await req.json()
    email = clean(d.get("email"), 120).lower()
    if email in ADMIN_EMAILS and (d.get("password") or "") == ADMIN_PASS:
        set_cookie(resp, "admin", 0)
        return {"ok": True}
    return JSONResponse({"ok": False, "error": "Identifiants incorrects."}, status_code=401)

@app.post("/api/partenaire/login")
async def partner_login(req: Request, resp: Response):
    d = await req.json()
    code = clean(d.get("code"), 12).upper()
    pin = clean(d.get("pin"), 12)
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE code=? AND actif=1", (code,)).fetchone()
    if a and check_pw(pin, a["pin"]):
        set_cookie(resp, "affiliate", a["id"])
        return {"ok": True}
    return JSONResponse({"ok": False, "error": "Code ou PIN incorrect."}, status_code=401)

@app.post("/api/logout")
def logout(resp: Response):
    resp.delete_cookie(COOKIE)
    return {"ok": True}

@app.get("/api/me")
def me(naff_session: Optional[str] = Cookie(default=None)):
    ac = actor(naff_session)
    if not ac:
        return {"role": None}
    role, sid = ac
    if role == "admin":
        return {"role": "admin"}
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE id=? AND actif=1", (sid,)).fetchone()
    if not a:
        return {"role": None}
    return {"role": "affiliate", "code": a["code"], "name": affiliate_label(a)}

# ===========================  ADMIN (Mongazi)  ==============================
def need_admin(naff_session) -> bool:
    ac = actor(naff_session)
    return bool(ac and ac[0] == "admin")

@app.get("/api/admin/overview")
def admin_overview(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        affs = c.execute("SELECT COUNT(*) n FROM affiliates WHERE actif=1").fetchone()["n"]
        leads = c.execute("SELECT * FROM leads").fetchall()
    by_status = {k: 0 for k in STATUSES}
    paid = 0; ca_paye = 0; commissions = 0; rate_cache = {}
    for r in leads:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        if r["paye"]:
            paid += 1
            base = r["montant"] if r["montant"] else SERVICES.get(r["service"], {}).get("price", 0)
            ca_paye += base
            aid = r["affiliate_id"]
            if aid not in rate_cache:
                rate_cache[aid] = stats_of(aid)["direct_rate"]
            commissions += commission_of(r["service"], r["montant"], rate_cache[aid])
    return {
        "affiliates": affs, "leads": len(leads), "by_status": by_status,
        "paid": paid, "ca_paye": ca_paye, "commissions_dues": commissions,
    }

@app.get("/api/admin/affiliates")
def admin_affiliates(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM affiliates ORDER BY created DESC").fetchall()
    out = []
    for a in rows:
        s = stats_of(a["id"])
        out.append({
            "id": a["id"], "code": a["code"], "nom": a["nom"], "prenom": a["prenom"],
            "momo_number": a["momo_number"], "momo_reseau": a["momo_reseau"],
            "actif": a["actif"], "accent": a["accent"],
            "score": s["score"], "rcm": s["rcm"], "potentiel": s["potentiel"],
            "rank": s["rank"], "palier": s["palier"], "ventes": s["ventes"], "ventes_mois": s["ventes_mois"],
            "nb_real": s["nb_real"], "by_status": s["by_status"], "generated": earnings_of(a["id"])["generated"],
        })
    # classement par score décroissant
    out.sort(key=lambda x: x["score"], reverse=True)
    return {"affiliates": out}

@app.post("/api/admin/affiliates")
async def admin_create_affiliate(req: Request, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    nom = clean(d.get("nom"), 80); prenom = clean(d.get("prenom"), 80)
    momo = clean(d.get("momo_number"), 30); reseau = clean(d.get("momo_reseau"), 30) or RESEAUX[0]
    if not (nom or prenom):
        return JSONResponse({"ok": False, "error": "Nom du partenaire requis."}, status_code=400)
    pin = "".join(secrets.choice("0123456789") for _ in range(4))
    with db() as c:
        code = new_code(c)
        c.execute("""INSERT INTO affiliates(code,nom,prenom,momo_number,momo_reseau,pin,accent,actif,created)
                     VALUES(?,?,?,?,?,?,?,1,?)""",
                  (code, nom, prenom, momo, reseau, hash_pw(pin), "#7b5cff", time.time()))
    return {"ok": True, "code": code, "pin": pin}

@app.post("/api/admin/affiliates/{aid}/toggle")
def admin_toggle_affiliate(aid: int, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        a = c.execute("SELECT actif FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"ok": False}, status_code=404)
        c.execute("UPDATE affiliates SET actif=? WHERE id=?", (0 if a["actif"] else 1, aid))
    return {"ok": True}

@app.get("/api/admin/leads")
def admin_leads(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("""SELECT l.*, a.code acode, a.nom anom, a.prenom aprenom
                            FROM leads l JOIN affiliates a ON a.id=l.affiliate_id
                            ORDER BY l.created DESC""").fetchall()
    rate_cache = {}
    out = []
    for r in rows:
        aid = r["affiliate_id"]
        if aid not in rate_cache:
            rate_cache[aid] = stats_of(aid)["direct_rate"]
        out.append({
            "id": r["id"], "nom": r["nom"], "prenom": r["prenom"], "numero": r["numero"],
            "service": r["service"], "service_label": SERVICES.get(r["service"], {}).get("label", r["service"]),
            "message": r["message"], "status": r["status"], "paye": r["paye"],
            "commission": commission_of(r["service"], r["montant"], rate_cache[aid]),
            "created": r["created"], "updated": r["updated"],
            "affiliate": {"code": r["acode"], "name": (str(r["aprenom"] or "") + " " + str(r["anom"] or "")).strip() or r["acode"]},
        })
    return {"leads": out}

@app.post("/api/admin/leads/{lid}/status")
async def admin_set_status(lid: int, req: Request, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    st = clean(d.get("status"), 20)
    if st not in STATUSES:
        return JSONResponse({"ok": False, "error": "Statut inconnu."}, status_code=400)
    with db() as c:
        r = c.execute("SELECT * FROM leads WHERE id=?", (lid,)).fetchone()
        if not r:
            return JSONResponse({"ok": False}, status_code=404)
        old = r["status"]
        c.execute("UPDATE leads SET status=?, updated=? WHERE id=?", (st, time.time(), lid))
        c.execute("INSERT INTO history(lead_id,old_status,new_status,note,at) VALUES(?,?,?,?,?)",
                  (lid, old, st, "", time.time()))
    client = (str(r["prenom"] or "") + " " + str(r["nom"] or "")).strip()
    notify("affiliate", r["affiliate_id"], f"{client} : statut → {STATUSES[st]['label']}", lid)
    return {"ok": True}

@app.post("/api/admin/leads/{lid}/payment")
async def admin_set_payment(lid: int, req: Request, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    paye = 1 if d.get("paye") else 0
    montant = d.get("montant")
    with db() as c:
        r = c.execute("SELECT * FROM leads WHERE id=?", (lid,)).fetchone()
        if not r:
            return JSONResponse({"ok": False}, status_code=404)
        m = float(montant) if (montant is not None and str(montant) != "") else r["montant"]
        c.execute("UPDATE leads SET paye=?, montant=?, updated=? WHERE id=?", (paye, m, time.time(), lid))
        r = c.execute("SELECT * FROM leads WHERE id=?", (lid,)).fetchone()
    if paye:
        generate_commissions(r)      # crée + alerte direct / N1 / N2 automatiquement
    else:
        void_commissions(lid)
    return {"ok": True}

@app.get("/api/admin/notifs")
def admin_notifs(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM notifs WHERE target_role='admin' ORDER BY created DESC LIMIT 50").fetchall()
        unread = c.execute("SELECT COUNT(*) n FROM notifs WHERE target_role='admin' AND lu=0").fetchone()["n"]
    return {"notifs": [dict(r) for r in rows], "unread": unread}

@app.post("/api/admin/notifs/read")
def admin_notifs_read(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        c.execute("UPDATE notifs SET lu=1 WHERE target_role='admin'")
    return {"ok": True}

@app.get("/api/admin/recruits")
def admin_recruits(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("""SELECT r.*, a.code pcode, a.nom pnom, a.prenom pprenom
                            FROM recruits r JOIN affiliates a ON a.id=r.parrain_id
                            WHERE r.status='pending' ORDER BY r.created DESC""").fetchall()
    return {"recruits": [{
        "id": r["id"], "nom": r["nom"], "prenom": r["prenom"], "numero": r["numero"],
        "momo_number": r["momo_number"], "momo_reseau": r["momo_reseau"], "message": r["message"],
        "created": r["created"],
        "parrain": {"code": r["pcode"], "name": (str(r["pprenom"] or "") + " " + str(r["pnom"] or "")).strip() or r["pcode"]},
    } for r in rows]}

@app.post("/api/admin/recruits/{rid}/approve")
def admin_recruit_approve(rid: int, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        r = c.execute("SELECT * FROM recruits WHERE id=? AND status='pending'", (rid,)).fetchone()
        if not r:
            return JSONResponse({"ok": False}, status_code=404)
        pin = "".join(secrets.choice("0123456789") for _ in range(4))
        code = new_code(c)
        c.execute("""INSERT INTO affiliates(code,nom,prenom,momo_number,momo_reseau,pin,accent,actif,created,parrain_id)
                     VALUES(?,?,?,?,?,?,?,1,?,?)""",
                  (code, r["nom"], r["prenom"], r["momo_number"], r["momo_reseau"], hash_pw(pin), "#7b5cff", time.time(), r["parrain_id"]))
        c.execute("UPDATE recruits SET status='approved' WHERE id=?", (rid,))
    who = (str(r["prenom"] or "") + " " + str(r["nom"] or "")).strip()
    notify("affiliate", r["parrain_id"], f"Ta recrue {who} est validée — elle rejoint ton réseau (N1).")
    return {"ok": True, "code": code, "pin": pin}

@app.post("/api/admin/recruits/{rid}/reject")
def admin_recruit_reject(rid: int, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        c.execute("UPDATE recruits SET status='rejected' WHERE id=?", (rid,))
    return {"ok": True}

@app.get("/api/admin/network")
def admin_network(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        affs = c.execute("SELECT * FROM affiliates WHERE actif=1 ORDER BY created").fetchall()
    by_parent: Dict[int, list] = {}
    info: Dict[int, dict] = {}
    for a in affs:
        by_parent.setdefault(a["parrain_id"] or 0, []).append(a)
        s = stats_of(a["id"])
        info[a["id"]] = {"id": a["id"], "name": affiliate_label(a), "code": a["code"],
                         "ventes": s["ventes"], "rank": s["rank"]["label"], "palier": s["palier"]["label"]}
    def build(pid: int, depth: int):
        out = []
        for a in by_parent.get(pid, []):
            node = dict(info[a["id"]])
            node["children"] = build(a["id"], depth + 1) if depth < 8 else []
            out.append(node)
        return out
    return {"roots": build(0, 0), "total": len(affs)}

@app.get("/api/admin/commissions")
def admin_commissions(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("""SELECT cm.*, a.code acode, a.nom anom, a.prenom aprenom, a.momo_number, a.momo_reseau,
                                   l.nom lnom, l.prenom lprenom
                            FROM commissions cm JOIN affiliates a ON a.id=cm.beneficiary_id JOIN leads l ON l.id=cm.lead_id
                            WHERE cm.status IN ('due','claimed') ORDER BY cm.created""").fetchall()
    LBL = {"direct": "Direct", "n1": "N1", "n2": "N2"}
    groups = {}; total_due = 0; total_claimed = 0
    for r in rows:
        bid = r["beneficiary_id"]
        g = groups.get(bid)
        if not g:
            g = {"affiliate_id": bid, "name": (str(r["aprenom"] or "") + " " + str(r["anom"] or "")).strip() or r["acode"],
                 "code": r["acode"], "momo_number": r["momo_number"], "momo_reseau": r["momo_reseau"],
                 "total": 0, "claimed": 0, "has_claim": False, "entries": []}
            groups[bid] = g
        g["total"] += r["amount"]; total_due += r["amount"]
        if r["status"] == "claimed":
            g["claimed"] += r["amount"]; g["has_claim"] = True; total_claimed += r["amount"]
        g["entries"].append({"level": LBL.get(r["level"], r["level"]), "amount": int(r["amount"]), "status": r["status"],
                             "client": (str(r["lprenom"] or "") + " " + str(r["lnom"] or "")).strip()})
    out = sorted(groups.values(), key=lambda g: (not g["has_claim"], -g["total"]))
    for g in out:
        g["total"] = int(g["total"]); g["claimed"] = int(g["claimed"])
    return {"groups": out, "total_due": int(total_due), "total_claimed": int(total_claimed)}

@app.post("/api/admin/commissions/pay")
async def admin_pay(req: Request, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    aff_id = int(d.get("affiliate_id") or 0)
    with db() as c:
        rows = c.execute("SELECT * FROM commissions WHERE beneficiary_id=? AND status IN ('due','claimed')", (aff_id,)).fetchall()
        total = int(sum(x["amount"] for x in rows)); n = len(rows)
        if n:
            c.execute("UPDATE commissions SET status='paid', paid_at=? WHERE beneficiary_id=? AND status IN ('due','claimed')", (time.time(), aff_id))
    if n:
        notify("affiliate", aff_id, f"Paiement reçu : {fmoney(total)} F versés par NEBULA ({n} commission(s)). Merci pour ton travail !")
    return {"ok": True, "paid": n, "total": total}

# ===========================  AFFILIÉ  ======================================
def need_affiliate(naff_session) -> Optional[int]:
    ac = actor(naff_session)
    if ac and ac[0] == "affiliate":
        return ac[1]
    return None

@app.get("/api/partenaire/me")
def partner_me(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE id=? AND actif=1", (aid,)).fetchone()
    if not a:
        return JSONResponse({"error": "auth"}, status_code=401)
    s = stats_of(aid)
    return {
        "code": a["code"], "nom": a["nom"], "prenom": a["prenom"],
        "name": affiliate_label(a), "accent": a["accent"],
        "momo_number": a["momo_number"], "momo_reseau": a["momo_reseau"],
        "photo": photo_url("a" + str(aid)),
        "stats": s, "network": network_of(aid), "earnings": earnings_of(aid),
    }

@app.get("/api/partenaire/leads")
def partner_leads(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    rate = stats_of(aid)["direct_rate"]
    with db() as c:
        rows = c.execute("SELECT * FROM leads WHERE affiliate_id=? ORDER BY created DESC", (aid,)).fetchall()
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "nom": r["nom"], "prenom": r["prenom"], "numero": r["numero"],
            "service": r["service"], "service_label": SERVICES.get(r["service"], {}).get("label", r["service"]),
            "status": r["status"], "paye": r["paye"],
            "commission": commission_of(r["service"], r["montant"], rate),
            "created": r["created"], "updated": r["updated"],
        })
    return {"leads": out}

@app.get("/api/partenaire/commissions")
def partner_commissions(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("""SELECT cm.*, l.nom lnom, l.prenom lprenom, l.service lservice
                            FROM commissions cm JOIN leads l ON l.id=cm.lead_id
                            WHERE cm.beneficiary_id=? AND cm.status!='void' ORDER BY cm.created DESC""", (aid,)).fetchall()
    LBL = {"direct": "Vente directe", "n1": "Réseau N1 · 10%", "n2": "Réseau N2 · 5%"}
    out = []; due = claimed = paid = 0
    for r in rows:
        if r["status"] == "due": due += r["amount"]
        elif r["status"] == "claimed": claimed += r["amount"]
        elif r["status"] == "paid": paid += r["amount"]
        out.append({"id": r["id"], "level": r["level"], "level_label": LBL.get(r["level"], r["level"]),
                    "amount": int(r["amount"]), "status": r["status"], "created": r["created"],
                    "client": (str(r["lprenom"] or "") + " " + str(r["lnom"] or "")).strip(),
                    "service": SERVICES.get(r["lservice"], {}).get("label", r["lservice"])})
    return {"commissions": out, "summary": earnings_of(aid)}

@app.post("/api/partenaire/commissions/claim")
def partner_claim(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM commissions WHERE beneficiary_id=? AND status='due'", (aid,)).fetchall()
        total = int(sum(x["amount"] for x in rows)); n = len(rows)
        if n:
            c.execute("UPDATE commissions SET status='claimed', claimed_at=? WHERE beneficiary_id=? AND status='due'", (time.time(), aid))
        a = c.execute("SELECT * FROM affiliates WHERE id=?", (aid,)).fetchone()
    if n:
        notify("admin", 0, f"{affiliate_label(a)} réclame {fmoney(total)} F ({n} commission(s)) — payer sur {a['momo_reseau']} {a['momo_number']}.")
    return {"ok": True, "claimed": n, "total": total}

@app.post("/api/partenaire/theme")
async def partner_theme(req: Request, naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    accent = clean(d.get("accent"), 9)
    if not re.match(r"^#[0-9a-fA-F]{6}$", accent or ""):
        return JSONResponse({"ok": False, "error": "Couleur invalide."}, status_code=400)
    with db() as c:
        c.execute("UPDATE affiliates SET accent=? WHERE id=?", (accent, aid))
    return {"ok": True}

@app.get("/api/partenaire/notifs")
def partner_notifs(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM notifs WHERE target_role='affiliate' AND target_id=? ORDER BY created DESC LIMIT 50", (aid,)).fetchall()
        unread = c.execute("SELECT COUNT(*) n FROM notifs WHERE target_role='affiliate' AND target_id=? AND lu=0", (aid,)).fetchone()["n"]
    return {"notifs": [dict(r) for r in rows], "unread": unread}

@app.post("/api/partenaire/notifs/read")
def partner_notifs_read(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        c.execute("UPDATE notifs SET lu=1 WHERE target_role='affiliate' AND target_id=?", (aid,))
    return {"ok": True}

# ==================  CANDIDATURE PUBLIQUE « Devenir partenaire »  ============
@app.get("/api/terms")
def api_terms():
    return {"version": TERMS_VERSION, "html": TERMS_HTML}

@app.post("/api/candidature")
async def create_candidature(req: Request):
    d = await req.json()
    if not d.get("accept"):
        return JSONResponse({"ok": False, "error": "Tu dois accepter les conditions générales."}, status_code=400)
    nom = clean(d.get("nom"), 80); prenom = clean(d.get("prenom"), 80)
    numero = clean(d.get("numero"), 30)
    if not (nom or prenom) or not numero:
        return JSONResponse({"ok": False, "error": "Nom et numéro WhatsApp obligatoires."}, status_code=400)
    email = clean(d.get("email"), 120); ville = clean(d.get("ville"), 80)
    momo = clean(d.get("momo_number"), 30); reseau = clean(d.get("momo_reseau"), 30) or RESEAUX[0]
    exp = clean(d.get("experience"), 60); motiv = clean(d.get("motivation"), 600)
    canaux = clean(d.get("canaux"), 200); parrain = clean(d.get("parrain_code"), 12).upper()
    ip = (req.headers.get("x-forwarded-for", "").split(",")[0].strip() or (req.client.host if req.client else ""))[:60]
    with db() as c:
        c.execute("""INSERT INTO candidatures(nom,prenom,email,numero,ville,momo_number,momo_reseau,
                     experience,motivation,canaux,parrain_code,terms_version,accepted_at,ip,status,created)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'pending', ?)""",
                  (nom, prenom, email, numero, ville, momo, reseau, exp, motiv, canaux, parrain,
                   TERMS_VERSION, time.time(), ip, time.time()))
    who = (prenom + " " + nom).strip()
    notify("admin", 0, f"Nouvelle candidature partenaire : {who} ({numero}){' · ville ' + ville if ville else ''} — CGU v{TERMS_VERSION} acceptées.")
    tg_send(f"NEBULA Affiliés — nouvelle candidature partenaire : {who} ({numero}).")
    return {"ok": True}

@app.get("/api/admin/candidatures")
def admin_candidatures(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM candidatures WHERE status='pending' ORDER BY created DESC").fetchall()
    return {"candidatures": [{
        "id": r["id"], "nom": r["nom"], "prenom": r["prenom"], "email": r["email"], "numero": r["numero"],
        "ville": r["ville"], "momo_number": r["momo_number"], "momo_reseau": r["momo_reseau"],
        "experience": r["experience"], "motivation": r["motivation"], "canaux": r["canaux"],
        "parrain_code": r["parrain_code"], "terms_version": r["terms_version"],
        "accepted_at": r["accepted_at"], "created": r["created"],
    } for r in rows]}

@app.post("/api/admin/candidatures/{cid}/approve")
def admin_candidature_approve(cid: int, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        r = c.execute("SELECT * FROM candidatures WHERE id=? AND status='pending'", (cid,)).fetchone()
        if not r:
            return JSONResponse({"ok": False}, status_code=404)
        parrain_id = 0
        if r["parrain_code"]:
            p = c.execute("SELECT id FROM affiliates WHERE code=? AND actif=1", (r["parrain_code"],)).fetchone()
            if p:
                parrain_id = p["id"]
        pin = "".join(secrets.choice("0123456789") for _ in range(4))
        code = new_code(c)
        c.execute("""INSERT INTO affiliates(code,nom,prenom,momo_number,momo_reseau,pin,accent,actif,created,parrain_id)
                     VALUES(?,?,?,?,?,?,?,1,?,?)""",
                  (code, r["nom"], r["prenom"], r["momo_number"], r["momo_reseau"], hash_pw(pin), "#7b5cff", time.time(), parrain_id))
        c.execute("UPDATE candidatures SET status='approved' WHERE id=?", (cid,))
        if parrain_id:
            who = (str(r["prenom"] or "") + " " + str(r["nom"] or "")).strip()
            notify("affiliate", parrain_id, f"Ta recrue {who} est validée — elle rejoint ton réseau (N1).")
    return {"ok": True, "code": code, "pin": pin}

@app.post("/api/admin/candidatures/{cid}/reject")
def admin_candidature_reject(cid: int, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        c.execute("UPDATE candidatures SET status='rejected' WHERE id=?", (cid,))
    return {"ok": True}

# ===========================  DOCUMENTATION (PDF / notes)  ===================
def doc_public(r: sqlite3.Row) -> Dict[str, Any]:
    return {"id": r["id"], "title": r["title"], "category": r["category"], "description": r["description"],
            "kind": r["kind"], "body": r["body"] if r["kind"] == "note" else "",
            "url": r["url"], "size": r["size"], "has_file": bool(r["filename"]),
            "updated": r["updated"], "created": r["created"]}

@app.get("/api/partenaire/documents")
def partner_documents(naff_session: Optional[str] = Cookie(default=None)):
    if need_affiliate(naff_session) is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM documents ORDER BY updated DESC").fetchall()
    return {"documents": [doc_public(r) for r in rows], "categories": DOC_CATEGORIES}

@app.get("/api/admin/documents")
def admin_documents(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM documents ORDER BY updated DESC").fetchall()
    return {"documents": [doc_public(r) for r in rows], "categories": DOC_CATEGORIES}

@app.post("/api/admin/documents")
async def admin_doc_save(
    doc_id: str = Form(""), title: str = Form(...), category: str = Form("Autre"),
    description: str = Form(""), kind: str = Form("note"), body: str = Form(""),
    url: str = Form(""), file: Optional[UploadFile] = File(None),
    naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    title = clean(title, 120)
    if not title:
        return JSONResponse({"ok": False, "error": "Titre requis."}, status_code=400)
    if category not in DOC_CATEGORIES:
        category = "Autre"
    fname = ""; size = 0
    if file is not None and file.filename:
        fname, size = await store_upload(file, "doc")
        kind = "pdf"
    now = time.time()
    with db() as c:
        if doc_id and str(doc_id).isdigit():
            old = c.execute("SELECT * FROM documents WHERE id=?", (int(doc_id),)).fetchone()
            if old:
                nf = fname or old["filename"]; ns = size or old["size"]
                nk = kind if (fname or kind != "pdf") else (old["kind"] if not fname else "pdf")
                if fname and old["filename"]:
                    try: (UP_DIR / old["filename"]).unlink()
                    except Exception: pass
                c.execute("""UPDATE documents SET title=?,category=?,description=?,kind=?,body=?,url=?,filename=?,size=?,updated=? WHERE id=?""",
                          (title, category, clean(description, 300), nk, body, clean(url, 400), nf, ns, now, int(doc_id)))
                return {"ok": True, "id": int(doc_id)}
        cur = c.execute("""INSERT INTO documents(title,category,description,kind,body,url,filename,size,updated,created)
                           VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (title, category, clean(description, 300), kind, body, clean(url, 400), fname, size, now, now))
        new_id = cur.lastrowid
    return {"ok": True, "id": new_id}

@app.post("/api/admin/documents/{did}/delete")
def admin_doc_delete(did: int, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        r = c.execute("SELECT filename FROM documents WHERE id=?", (did,)).fetchone()
        if r and r["filename"]:
            try: (UP_DIR / r["filename"]).unlink()
            except Exception: pass
        c.execute("DELETE FROM documents WHERE id=?", (did,))
    return {"ok": True}

@app.get("/api/doc/{did}")
def serve_doc(did: int, naff_session: Optional[str] = Cookie(default=None)):
    if actor(naff_session) is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        r = c.execute("SELECT * FROM documents WHERE id=?", (did,)).fetchone()
    if not r or not r["filename"]:
        return JSONResponse({"error": "introuvable"}, status_code=404)
    fp = UP_DIR / r["filename"]
    if not fp.exists():
        return JSONResponse({"error": "introuvable"}, status_code=404)
    dl = re.sub(r"[^a-zA-Z0-9._-]", "_", (r["title"] or "document"))[:60] + ".pdf"
    return FileResponse(str(fp), media_type="application/pdf", filename=dl)

# ===========================  PUBLICATION (contenus à poster)  ===============
def pub_public(r: sqlite3.Row) -> Dict[str, Any]:
    return {"id": r["id"], "title": r["title"], "ptype": r["ptype"], "type_label": PUB_TYPES.get(r["ptype"], r["ptype"]),
            "body": r["body"], "script": r["script"],
            "platforms": [p for p in (r["platforms"] or "").split(",") if p],
            "media_kind": r["media_kind"], "media_url": r["media_url"],
            "has_media": bool(r["filename"]), "updated": r["updated"], "created": r["created"]}

@app.get("/api/partenaire/publications")
def partner_publications(naff_session: Optional[str] = Cookie(default=None)):
    if need_affiliate(naff_session) is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM publications ORDER BY updated DESC").fetchall()
    return {"publications": [pub_public(r) for r in rows], "platforms": PLATFORMS}

@app.get("/api/admin/publications")
def admin_publications(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM publications ORDER BY updated DESC").fetchall()
    return {"publications": [pub_public(r) for r in rows], "platforms": PLATFORMS, "types": PUB_TYPES}

@app.post("/api/admin/publications")
async def admin_pub_save(
    pub_id: str = Form(""), title: str = Form(...), ptype: str = Form("post"),
    body: str = Form(""), script: str = Form(""), platforms: str = Form(""),
    media_url: str = Form(""), file: Optional[UploadFile] = File(None),
    naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    title = clean(title, 120)
    if not title:
        return JSONResponse({"ok": False, "error": "Titre requis."}, status_code=400)
    if ptype not in PUB_TYPES:
        ptype = "post"
    plats = ",".join(p for p in clean(platforms, 200).split(",") if p in PLATFORMS)
    media_kind = "none"; murl = clean(media_url, 400)
    if murl:
        media_kind = "video" if ptype == "video" else "link"
    fname = ""
    if file is not None and file.filename:
        fname, _ = await store_upload(file, "pub")
        media_kind = "video" if ptype == "video" else "image"
    now = time.time()
    with db() as c:
        if pub_id and str(pub_id).isdigit():
            old = c.execute("SELECT * FROM publications WHERE id=?", (int(pub_id),)).fetchone()
            if old:
                nf = fname or old["filename"]
                nmk = media_kind if (fname or murl) else old["media_kind"]
                if fname and old["filename"]:
                    try: (UP_DIR / old["filename"]).unlink()
                    except Exception: pass
                c.execute("""UPDATE publications SET title=?,ptype=?,body=?,script=?,platforms=?,media_kind=?,media_url=?,filename=?,updated=? WHERE id=?""",
                          (title, ptype, body, script, plats, nmk, murl or old["media_url"], nf, now, int(pub_id)))
                return {"ok": True, "id": int(pub_id)}
        cur = c.execute("""INSERT INTO publications(title,ptype,body,script,platforms,media_kind,media_url,filename,updated,created)
                           VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (title, ptype, body, script, plats, media_kind, murl, fname, now, now))
        new_id = cur.lastrowid
    return {"ok": True, "id": new_id}

@app.post("/api/admin/publications/{pid}/delete")
def admin_pub_delete(pid: int, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        r = c.execute("SELECT filename FROM publications WHERE id=?", (pid,)).fetchone()
        if r and r["filename"]:
            try: (UP_DIR / r["filename"]).unlink()
            except Exception: pass
        c.execute("DELETE FROM publications WHERE id=?", (pid,))
    return {"ok": True}

@app.get("/api/pub/{pid}/media")
def serve_pub_media(pid: int, naff_session: Optional[str] = Cookie(default=None)):
    if actor(naff_session) is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        r = c.execute("SELECT * FROM publications WHERE id=?", (pid,)).fetchone()
    if not r or not r["filename"]:
        return JSONResponse({"error": "introuvable"}, status_code=404)
    fp = UP_DIR / r["filename"]
    if not fp.exists():
        return JSONResponse({"error": "introuvable"}, status_code=404)
    return FileResponse(str(fp), filename=r["filename"].split("_", 3)[-1])

# ============  PROFILS · CLASSEMENT · MESSAGERIE (bureaux virtuels)  =========
def me_uid(naff_session) -> Optional[str]:
    ac = actor(naff_session)
    if not ac:
        return None
    return "admin" if ac[0] == "admin" else "a" + str(ac[1])

def setting_get(k: str) -> str:
    with db() as c:
        r = c.execute("SELECT v FROM app_settings WHERE k=?", (k,)).fetchone()
    return r["v"] if r else ""

def setting_set(k: str, v: str):
    with db() as c:
        c.execute("INSERT INTO app_settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, v))

def photo_url(who: str) -> str:
    """who = 'admin' ou 'a<id>'. Renvoie l'URL de la photo si elle existe, sinon ''."""
    if who == "admin":
        return "/api/photo/admin" if setting_get("admin_photo") else ""
    if who.startswith("a"):
        try:
            aid = int(who[1:])
        except Exception:
            return ""
        with db() as c:
            r = c.execute("SELECT photo FROM affiliates WHERE id=?", (aid,)).fetchone()
        return f"/api/photo/{aid}" if (r and r["photo"]) else ""
    return ""

def participants_map() -> Dict[str, Dict[str, Any]]:
    with db() as c:
        affs = c.execute("SELECT * FROM affiliates WHERE actif=1 ORDER BY created").fetchall()
    out: Dict[str, Dict[str, Any]] = {"admin": {
        "uid": "admin", "name": "NEBULA Agency", "role": "admin",
        "accent": "#7b5cff", "photo": photo_url("admin"), "sub": "Quartier général"}}
    for a in affs:
        uid = "a" + str(a["id"])
        out[uid] = {"uid": uid, "name": affiliate_label(a), "role": "affiliate",
                    "accent": a["accent"] or "#7b5cff", "photo": photo_url(uid),
                    "sub": rank_for(_paid_value(a["id"])[0])["label"], "aid": a["id"]}
    return out

def dm_pair(u1: str, u2: str) -> str:
    return "|".join(sorted([u1, u2]))

def chan_key(scope: str, pair: str) -> str:
    return "general" if scope == "general" else ("dm:" + pair)

def chat_lastread(uid: str, channel: str) -> float:
    with db() as c:
        r = c.execute("SELECT last_read FROM chat_reads WHERE uid=? AND channel=?", (uid, channel)).fetchone()
    return r["last_read"] if r else 0.0

def chat_mark_read(uid: str, channel: str):
    with db() as c:
        c.execute("INSERT INTO chat_reads(uid,channel,last_read) VALUES(?,?,?) "
                  "ON CONFLICT(uid,channel) DO UPDATE SET last_read=excluded.last_read", (uid, channel, time.time()))

def chat_unread_total(me: str) -> int:
    total = 0
    with db() as c:
        lrg = chat_lastread(me, "general")
        total += c.execute("SELECT COUNT(*) n FROM messages WHERE scope='general' AND created>? AND sender_uid!=?", (lrg, me)).fetchone()["n"]
        pairs = c.execute("SELECT DISTINCT pair FROM messages WHERE scope='dm' AND (pair LIKE ? OR pair LIKE ?)", (me + "|%", "%|" + me)).fetchall()
        for p in pairs:
            lr = chat_lastread(me, "dm:" + p["pair"])
            total += c.execute("SELECT COUNT(*) n FROM messages WHERE scope='dm' AND pair=? AND created>? AND sender_uid!=?", (p["pair"], lr, me)).fetchone()["n"]
    return total

@app.post("/api/me/photo")
async def upload_my_photo(file: UploadFile = File(...), naff_session: Optional[str] = Cookie(default=None)):
    me = me_uid(naff_session)
    if not me:
        return JSONResponse({"error": "auth"}, status_code=401)
    if not file or not file.filename:
        return JSONResponse({"ok": False, "error": "Aucun fichier."}, status_code=400)
    fname, _ = await store_upload(file, "photo")
    if me == "admin":
        old = setting_get("admin_photo")
        if old:
            try: (UP_DIR / old).unlink()
            except Exception: pass
        setting_set("admin_photo", fname)
    else:
        aid = int(me[1:])
        with db() as c:
            r = c.execute("SELECT photo FROM affiliates WHERE id=?", (aid,)).fetchone()
            if r and r["photo"]:
                try: (UP_DIR / r["photo"]).unlink()
                except Exception: pass
            c.execute("UPDATE affiliates SET photo=? WHERE id=?", (fname, aid))
    return {"ok": True, "url": photo_url(me)}

@app.get("/api/photo/{who}")
def serve_photo(who: str, naff_session: Optional[str] = Cookie(default=None)):
    if actor(naff_session) is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    fname = ""
    if who == "admin":
        fname = setting_get("admin_photo")
    else:
        try:
            aid = int(who)
            with db() as c:
                r = c.execute("SELECT photo FROM affiliates WHERE id=?", (aid,)).fetchone()
            fname = r["photo"] if r else ""
        except Exception:
            fname = ""
    if not fname:
        return JSONResponse({"error": "introuvable"}, status_code=404)
    fp = UP_DIR / fname
    if not fp.exists():
        return JSONResponse({"error": "introuvable"}, status_code=404)
    return FileResponse(str(fp))

@app.get("/api/leaderboard")
def api_leaderboard(naff_session: Optional[str] = Cookie(default=None)):
    me = me_uid(naff_session)
    if not me:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        affs = c.execute("SELECT * FROM affiliates WHERE actif=1").fetchall()
    out = []
    for a in affs:
        s = stats_of(a["id"]); e = earnings_of(a["id"]); b = s["by_status"]
        uid = "a" + str(a["id"])
        out.append({
            "uid": uid, "name": affiliate_label(a), "code": a["code"], "photo": photo_url(uid),
            "accent": a["accent"] or "#7b5cff", "rank": s["rank"]["label"], "rank_level": s["rank"]["level"],
            "palier": s["palier"]["label"], "palier_pct": s["palier"]["pct"],
            "ventes": s["ventes"], "ventes_mois": s["ventes_mois"], "score": s["score"],
            "rcm": e["generated"], "paid": e["paid"], "nb_real": s["nb_real"],
            "clients_actifs": (b.get("attente", 0) + b.get("en_cours", 0)), "termine": b.get("termine", 0),
            "is_me": uid == me,
        })
    out.sort(key=lambda x: (x["score"], x["rcm"]), reverse=True)
    for i, r in enumerate(out):
        r["position"] = i + 1
    return {"leaderboard": out, "me": me}

@app.get("/api/chat/contacts")
def chat_contacts(naff_session: Optional[str] = Cookie(default=None)):
    me = me_uid(naff_session)
    if not me:
        return JSONResponse({"error": "auth"}, status_code=401)
    pm = participants_map()
    with db() as c:
        lrg = chat_lastread(me, "general")
        gen_unread = c.execute("SELECT COUNT(*) n FROM messages WHERE scope='general' AND created>? AND sender_uid!=?", (lrg, me)).fetchone()["n"]
        gen_last = c.execute("SELECT text,created FROM messages WHERE scope='general' ORDER BY id DESC LIMIT 1").fetchone()
    contacts = []
    for uid, info in pm.items():
        if uid == me:
            continue
        pr = dm_pair(me, uid)
        with db() as c:
            lr = chat_lastread(me, "dm:" + pr)
            unread = c.execute("SELECT COUNT(*) n FROM messages WHERE scope='dm' AND pair=? AND created>? AND sender_uid!=?", (pr, lr, me)).fetchone()["n"]
            last = c.execute("SELECT text,created FROM messages WHERE scope='dm' AND pair=? ORDER BY id DESC LIMIT 1", (pr,)).fetchone()
        contacts.append({**info, "unread": unread, "last": (last["text"] if last else ""), "last_at": (last["created"] if last else 0)})
    contacts.sort(key=lambda c0: (c0["unread"] == 0, -(c0["last_at"] or 0)))
    return {"me": me, "my": pm.get(me, {"uid": me, "name": "Moi", "photo": "", "accent": "#7b5cff"}),
            "general": {"unread": gen_unread, "last": (gen_last["text"] if gen_last else ""), "last_at": (gen_last["created"] if gen_last else 0)},
            "contacts": contacts}

@app.get("/api/chat/history")
def chat_history(channel: str = "general", naff_session: Optional[str] = Cookie(default=None)):
    me = me_uid(naff_session)
    if not me:
        return JSONResponse({"error": "auth"}, status_code=401)
    if channel == "general":
        scope, pair = "general", ""
    else:
        scope, pair = "dm", dm_pair(me, channel)
    with db() as c:
        if scope == "general":
            rows = c.execute("SELECT * FROM messages WHERE scope='general' ORDER BY id DESC LIMIT 100").fetchall()
        else:
            rows = c.execute("SELECT * FROM messages WHERE scope='dm' AND pair=? ORDER BY id DESC LIMIT 100", (pair,)).fetchall()
    rows = list(reversed(rows))
    pm = participants_map()
    msgs = []
    for r in rows:
        snd = pm.get(r["sender_uid"], {"name": "Ancien partenaire", "photo": "", "accent": "#6b6b86"})
        msgs.append({"id": r["id"], "uid": r["sender_uid"], "name": snd["name"], "photo": snd.get("photo", ""),
                     "accent": snd.get("accent", "#7b5cff"), "text": r["text"], "created": r["created"], "mine": r["sender_uid"] == me})
    chat_mark_read(me, chan_key(scope, pair))
    return {"messages": msgs, "channel": channel}

@app.post("/api/chat/send")
async def chat_send(req: Request, naff_session: Optional[str] = Cookie(default=None)):
    me = me_uid(naff_session)
    if not me:
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    to = clean(d.get("to"), 20) or "general"
    text = clean(d.get("text"), 800)
    if not text:
        return JSONResponse({"ok": False, "error": "Message vide."}, status_code=400)
    pm = participants_map()
    if to == "general":
        scope, pair = "general", ""
    else:
        if to not in pm or to == me:
            return JSONResponse({"ok": False, "error": "Destinataire introuvable."}, status_code=404)
        scope, pair = "dm", dm_pair(me, to)
    with db() as c:
        c.execute("INSERT INTO messages(scope,pair,sender_uid,text,created) VALUES(?,?,?,?,?)", (scope, pair, me, text, time.time()))
    chat_mark_read(me, chan_key(scope, pair))
    return {"ok": True}

@app.get("/api/signals")
def api_signals(naff_session: Optional[str] = Cookie(default=None)):
    me = me_uid(naff_session)
    if not me:
        return JSONResponse({"error": "auth"}, status_code=401)
    if me == "admin":
        with db() as c:
            nun = c.execute("SELECT COUNT(*) n FROM notifs WHERE target_role='admin' AND lu=0").fetchone()["n"]
    else:
        aid = int(me[1:])
        with db() as c:
            nun = c.execute("SELECT COUNT(*) n FROM notifs WHERE target_role='affiliate' AND target_id=? AND lu=0", (aid,)).fetchone()["n"]
    return {"notif_unread": nun, "chat_unread": chat_unread_total(me), "ts": time.time()}

# ===========================  CERVEAU IA « NOVA »  ==========================
NOVA_ADMIN_SYS = (
    "Tu es NOVA, l'intelligence de NEBULA Agency (vitrines digitales + automatisation IA ; "
    "Cotonou, Bénin ; fondateur Mongazi). Tu es le copilote stratégique de Mongazi pour piloter "
    "son réseau de partenaires affiliés. Ton rôle : analyser les performances, dire QUI pousser, "
    "QUI relancer, repérer les clients bloqués, proposer des décisions concrètes et des messages "
    "WhatsApp prêts à envoyer. Tu proposes, Mongazi décide. "
    "Style : français, direct, chaleureux mais pro, chiffré, sans blabla, en puces courtes."
)
NOVA_AFF_SYS = (
    "Tu es NOVA, le coach IA personnel d'un partenaire affilié de NEBULA Agency (Cotonou, Bénin). "
    "Tu l'aides à ramener plus de clients et à monter en rang. Tu le motives, tu lui donnes des "
    "scripts WhatsApp prêts à copier, tu lui dis qui relancer et comment présenter les offres NEBULA "
    "(Vitrine 150 000 F, Catalogue 50 000 F, Fiche Google Maps, QR avis Google, Avatars IA). "
    "Style : français, tutoiement, énergie positive, concret, chiffré, encourageant, réponses courtes. "
    "Tu célèbres ses victoires et tu vises toujours le palier de rang suivant."
)

def brain_context_admin() -> str:
    with db() as c:
        affs = c.execute("SELECT * FROM affiliates ORDER BY created DESC").fetchall()
    lines = []
    for a in affs:
        s = stats_of(a["id"])
        b = s["by_status"]
        lines.append(f"- {affiliate_label(a)} (code {a['code']}) : rang {s['rank']['label']}, "
                     f"{s['nb_real']} clients, score {s['score']}, RCM {s['rcm']} F, "
                     f"attente {b['attente']} / en cours {b['en_cours']} / terminé {b['termine']}")
    return "RÉSEAU D'AFFILIÉS (temps réel) :\n" + ("\n".join(lines) if lines else "(aucun affilié)")

def brain_context_aff(aid: int) -> str:
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE id=?", (aid,)).fetchone()
        leads = c.execute("SELECT * FROM leads WHERE affiliate_id=? ORDER BY created DESC", (aid,)).fetchall()
    s = stats_of(aid); rk = s["rank"]; pal = s["palier"]
    nxt = (f"Encore {rk['to_next']} vente(s) pour le rang {rk['next_label']} {rk['next_emoji']}."
           if rk["next_label"] else "Rang Galaxie (suprême) atteint, bravo.")
    palnxt = (f"Encore {pal['to_next']} vente(s) CE MOIS pour passer {pal['next_label']} ({pal['next_pct']}% en direct)."
              if pal["next_label"] else "Palier GOLD (max) atteint ce mois.")
    cl = [f"- {(str(l['prenom'] or '')+' '+str(l['nom'] or '')).strip()} : "
          f"{SERVICES.get(l['service'], {}).get('label', l['service'])} — {STATUSES[l['status']]['label']}"
          f"{' — PAYÉ' if l['paye'] else ''}" for l in leads]
    return (f"TON PROFIL : {affiliate_label(a)} (code {a['code']}).\n"
            f"RANG (prestige, ventes cumulées) : {rk['label']} {rk['emoji']} — {s['ventes']} ventes au total. {nxt}\n"
            f"PALIER DU MOIS (ta commission DIRECTE) : {pal['label']} {pal['emoji']} = {pal['pct']}% — "
            f"{s['ventes_mois']} ventes ce mois. {palnxt}\n"
            f"Profondeurs réseau (fixes) : N1 = 10%, N2 = 5%. "
            f"RCM gagné {s['rcm']} F, potentiel {s['potentiel']} F.\nTES CLIENTS :\n"
            + ("\n".join(cl) if cl else "(aucun pour l'instant)"))

async def nova_reply(system: str, hist: List[sqlite3.Row]) -> str:
    messages = [{"role": ("assistant" if h["who"] == "nova" else "user"), "content": h["text"]} for h in hist]
    while messages and messages[0]["role"] != "user":
        messages = messages[1:]
    if not messages:
        messages = [{"role": "user", "content": "Bonjour NOVA"}]
    key = anthropic_key()
    if key:
        try:
            async with httpx.AsyncClient(timeout=45) as cli:
                r = await cli.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                             "content-type": "application/json"},
                    json={"model": BRAIN_MODEL, "max_tokens": 800, "system": system, "messages": messages})
            if r.status_code == 200:
                data = r.json()
                txt = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
                if txt:
                    return txt
        except Exception:
            pass
    return ("NOVA tourne en mode local (clé ANTHROPIC_API_KEY absente). "
            "Branche-la dans nebula-affilies/.env pour le cerveau complet.\n\n"
            "En attendant : concentre-toi sur les clients en « Attente » et « En cours », "
            "relance ceux sans nouvelle depuis 48 h, et vise le prochain palier de rang.")

@app.post("/api/brain")
async def brain(req: Request, naff_session: Optional[str] = Cookie(default=None)):
    ac = actor(naff_session)
    if not ac:
        return JSONResponse({"error": "auth"}, status_code=401)
    role, sid = ac
    d = await req.json()
    msg = clean(d.get("message"), 1200)
    if not msg:
        return JSONResponse({"ok": False, "error": "Message vide."}, status_code=400)
    scope = "admin" if role == "admin" else "aff"
    scope_id = 0 if role == "admin" else sid
    with db() as c:
        c.execute("INSERT INTO brain_msgs(scope,scope_id,who,text,created) VALUES(?,?,?,?,?)",
                  (scope, scope_id, "user", msg, time.time()))
        hist = c.execute("SELECT who,text FROM brain_msgs WHERE scope=? AND scope_id=? ORDER BY id DESC LIMIT 12",
                         (scope, scope_id)).fetchall()
    hist = list(reversed(hist))
    ctx = brain_context_admin() if role == "admin" else brain_context_aff(sid)
    fmt_rule = ("\n\nFORMAT DE RÉPONSE : bref (max ~110 mots), ton humain et direct. "
                "INTERDIT : tableaux Markdown, titres #, gras **. "
                "Puces « • » courtes autorisées. Va droit au but.")
    system = (NOVA_ADMIN_SYS if role == "admin" else NOVA_AFF_SYS) + "\n\nDONNÉES TEMPS RÉEL :\n" + ctx + fmt_rule
    reply = await nova_reply(system, hist)
    with db() as c:
        c.execute("INSERT INTO brain_msgs(scope,scope_id,who,text,created) VALUES(?,?,?,?,?)",
                  (scope, scope_id, "nova", reply, time.time()))
    return {"ok": True, "reply": reply}

@app.get("/api/brain/history")
def brain_history(naff_session: Optional[str] = Cookie(default=None)):
    ac = actor(naff_session)
    if not ac:
        return JSONResponse({"error": "auth"}, status_code=401)
    role, sid = ac
    scope = "admin" if role == "admin" else "aff"
    scope_id = 0 if role == "admin" else sid
    with db() as c:
        rows = c.execute("SELECT who,text,created FROM brain_msgs WHERE scope=? AND scope_id=? ORDER BY id DESC LIMIT 30",
                         (scope, scope_id)).fetchall()
    return {"messages": [dict(r) for r in reversed(rows)]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", "8780")), reload=True)
