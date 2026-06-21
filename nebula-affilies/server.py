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
from urllib.parse import quote
from fastapi import FastAPI, Request, Response, Cookie, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

try:
    from dotenv import load_dotenv
    HERE0 = pathlib.Path(__file__).resolve().parent
    load_dotenv(HERE0 / ".env")
    load_dotenv(HERE0.parent / "boutique-ia" / ".env", override=False)   # repli clé Claude (démo)
    load_dotenv(HERE0.parent / "nebula-prospector" / ".env", override=False)   # repli clé Resend (email) en local
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
# Zone de connexion admin PRIVÉE : non listée sur le portail public, URL secrète.
# Modifiable sans toucher au code via la variable d'env NAFF_ADMIN_PATH.
ADMIN_PATH = (os.getenv("NAFF_ADMIN_PATH", "qg-mongazi-x7q2").strip().strip("/")) or "qg-mongazi-x7q2"

# ---- Cerveau IA « NOVA » (Claude) ----
BRAIN_MODEL = os.getenv("NAFF_BRAIN_MODEL", "claude-sonnet-4-6")
def anthropic_key() -> str:
    return os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY") or ""

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
# ---- PALIERS SUPERVISEUR : 2 niveaux seulement, sur les ventes DU MOIS de l'ÉQUIPE ----
# Pour les partenaires « superviseur » (ex : Romaric DJANKAKI). Le palier est déterminé
# par le total de clients du mois de l'équipe entière (lui + ses branches N1+N2), mais le
# taux ne s'applique qu'à SES ventes directes (ses branches lui rapportent toujours 10/5%).
# (seuil mini de ventes d'équipe du mois, label, emoji, taux direct)
PALIERS_SUP: List[Tuple[int, str, str, float]] = [
    (0, "STARTER", "⬜", 0.25),   # 0 à 2 clients d'équipe / mois  → 25%
    (3, "SILVER",  "🟣", 0.40),   # 3+ clients d'équipe / mois     → 40%
]
# ---- Rôles spéciaux (au-delà de la recrue standard) ----
ROLE_LABELS = {"superviseur": "Superviseur"}

# ---- FONDATEUR (Mongazi) : titre + rang FIXES, au sommet du réseau (n'évoluent jamais) ----
FOUNDER_NAME  = os.getenv("NAFF_FOUNDER_NAME", "Mongazi")
FOUNDER_TITLE = os.getenv("NAFF_FOUNDER_TITLE", "Fondateur")
FOUNDER_RANK  = os.getenv("NAFF_FOUNDER_RANK", "Big Bang")   # rang suprême, origine du réseau

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
            text TEXT, lu INTEGER DEFAULT 0, created REAL,
            kind TEXT DEFAULT 'info')""")  # kind: client|vente|recrue|commission|paiement|statut|info
        c.execute("""CREATE TABLE IF NOT EXISTS brain_msgs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope TEXT NOT NULL,          -- 'admin' | 'aff'
            scope_id INTEGER DEFAULT 0,   -- id affilié (0 = admin)
            who TEXT,                     -- 'user' | 'nova'
            text TEXT, created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS agency_chats(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT, question TEXT, answer TEXT, created REAL)""")  # assistant public « NEBULA Agency »
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
        c.execute("""CREATE TABLE IF NOT EXISTS link_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            affiliate_id INTEGER, kind TEXT,   -- 'open' | 'client' | 'partner'
            created REAL)""")
init_db()

def migrate():
    with db() as c:
        for col, ddl in [("pseudo", "TEXT DEFAULT ''"), ("parrain_id", "INTEGER DEFAULT 0"), ("photo", "TEXT DEFAULT ''"),
                         ("direct_rate_override", "REAL DEFAULT 0"), ("email", "TEXT DEFAULT ''"),
                         ("tg_chat", "TEXT DEFAULT ''"), ("tg_token", "TEXT DEFAULT ''"),
                         ("role", "TEXT DEFAULT ''")]:
            try:
                c.execute(f"ALTER TABLE affiliates ADD COLUMN {col} {ddl}")
            except Exception:
                pass
        # leads : provenance (affilie | site) pour distinguer les clients directs du site agence
        for col, ddl in [("source", "TEXT DEFAULT 'affilie'")]:
            try:
                c.execute(f"ALTER TABLE leads ADD COLUMN {col} {ddl}")
            except Exception:
                pass
        for col, ddl in [("kind", "TEXT DEFAULT 'info'"), ("ref_aff", "INTEGER DEFAULT 0")]:
            try:
                c.execute(f"ALTER TABLE notifs ADD COLUMN {col} {ddl}")
            except Exception:
                pass
        for col, ddl in [("email", "TEXT DEFAULT ''")]:
            try:
                c.execute(f"ALTER TABLE recruits ADD COLUMN {col} {ddl}")
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

def palier_sup_for(team_mois: int) -> Dict[str, Any]:
    """Palier d'un SUPERVISEUR : 2 niveaux, déterminés par les clients du mois de
    son équipe entière (lui + branches). Le taux s'applique à ses ventes directes."""
    cur = PALIERS_SUP[0]; nxt = None
    for i, p in enumerate(PALIERS_SUP):
        if team_mois >= p[0]:
            cur = p; nxt = PALIERS_SUP[i+1] if i+1 < len(PALIERS_SUP) else None
    return {
        "label": cur[1], "emoji": cur[2], "rate": cur[3], "pct": int(round(cur[3] * 100)),
        "next_label": nxt[1] if nxt else None, "next_emoji": nxt[2] if nxt else None,
        "next_pct": int(round(nxt[3] * 100)) if nxt else None,
        "to_next": max(0, nxt[0] - team_mois) if nxt else 0,
        "min": cur[0], "next_min": nxt[0] if nxt else None,
        "scope": "team", "team_mois": team_mois,
    }

def commission_of(service: str, montant: float, rate: float = 0.25) -> int:
    base = montant if montant and montant > 0 else SERVICES.get(service, {}).get("price", 0)
    return int(round(base * rate))

def stats_of(affiliate_id: int) -> Dict[str, Any]:
    with db() as c:
        rows = c.execute("SELECT * FROM leads WHERE affiliate_id=?", (affiliate_id,)).fetchall()
        arow = c.execute("SELECT direct_rate_override, role FROM affiliates WHERE id=?", (affiliate_id,)).fetchone()
    override = float(arow["direct_rate_override"]) if (arow and arow["direct_rate_override"]) else 0.0
    role = (arow["role"] or "").strip().lower() if arow else ""
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
    # --- RANG (pour TOUS) : on grimpe sur ses ventes + celles de son équipe (N1+N2) ---
    ventes_rank = team_cumul_count(affiliate_id)          # inclut déjà ses propres ventes
    team_ventes = max(0, ventes_rank - ventes)            # part apportée par les branches
    # --- PALIER du mois -> taux de commission DIRECTE ---
    if role == "superviseur":
        team_mois = team_month_count(affiliate_id)        # clients du mois : lui + ses branches
        pal = palier_sup_for(team_mois)
        rate = pal["rate"]                                # s'applique à SES ventes directes
        paliers_scale = PALIERS_SUP
    else:
        team_mois = None
        pal = palier_for(ventes_mois)                     # palier du mois -> taux direct
        rate = pal["rate"]
        if override > 0:                                  # taux personnalisé fixe (legacy)
            rate = override
            pal = {"label": "SPÉCIAL", "emoji": "★", "rate": override, "pct": int(round(override * 100)),
                   "next_label": None, "next_emoji": None, "next_pct": None, "to_next": 0,
                   "min": 0, "next_min": None}
        paliers_scale = PALIERS
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
        "ventes_rank": ventes_rank, "team_ventes": team_ventes, "team_mois": team_mois,
        "rcm": rcm, "potentiel": potentiel, "direct_rate": rate,
        "rank": rank_for(ventes_rank), "palier": pal,
        "role": role, "role_label": ROLE_LABELS.get(role, ""), "is_supervisor": role == "superviseur",
        "paliers": [{"min": p[0], "label": p[1], "emoji": p[2], "pct": int(round(p[3] * 100))} for p in paliers_scale],
    }

def _paid_value(aid: int) -> Tuple[int, int]:
    """(nb ventes payées, valeur totale FCFA) d'un affilié."""
    with db() as c:
        paid = c.execute("SELECT service, montant FROM leads WHERE affiliate_id=? AND paye=1", (aid,)).fetchall()
    val = sum((r["montant"] if r["montant"] else SERVICES.get(r["service"], {}).get("price", 0)) for r in paid)
    return len(paid), int(val)

def _month_paid_count(aid: int) -> int:
    """Nombre de clients PAYÉS ce mois-ci pour un affilié."""
    ms = month_start_ts()
    with db() as c:
        return c.execute("SELECT COUNT(*) n FROM leads WHERE affiliate_id=? AND paye=1 AND COALESCE(updated,0)>=?",
                         (aid, ms)).fetchone()["n"]

def _downline_ids(aid: int) -> List[int]:
    """IDs de tout le réseau descendant ACTIF (N1 + N2) d'un affilié."""
    if not aid:                       # aid=0 = client direct (pas un affilié) : pas de descendance
        return []
    ids: List[int] = []
    with db() as c:
        n1 = [r["id"] for r in c.execute("SELECT id FROM affiliates WHERE parrain_id=? AND actif=1", (aid,)).fetchall()]
    ids += n1
    for n1id in n1:
        with db() as c:
            ids += [r["id"] for r in c.execute("SELECT id FROM affiliates WHERE parrain_id=? AND actif=1", (n1id,)).fetchall()]
    return ids

def team_cumul_count(aid: int) -> int:
    """Ventes payées CUMULÉES de l'affilié + tout son réseau (N1+N2). Base du RANG (pour TOUS)."""
    if not aid:
        return 0
    total = _paid_value(aid)[0]
    for did in _downline_ids(aid):
        total += _paid_value(did)[0]
    return total

def team_month_count(aid: int) -> int:
    """Clients payés CE MOIS par l'affilié + tout son réseau (N1+N2). Base du palier SUPERVISEUR."""
    if not aid:
        return 0
    total = _month_paid_count(aid)
    for did in _downline_ids(aid):
        total += _month_paid_count(did)
    return total

def network_of(aid: int) -> Dict[str, Any]:
    """Réseau d'un affilié en ARBRE : N1 (recrues directes, 10%), chaque N1 portant ses N2 (5%)."""
    def line(a, rate):
        cnt, val = _paid_value(a["id"])
        return {"name": affiliate_label(a), "code": a["code"], "ventes": cnt,
                "rank": rank_for(team_cumul_count(a["id"]))["label"], "commission": int(round(val * rate))}
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

def tg_send(chat: Any, text: str):
    """Envoi Telegram OUTBOUND (bot partagé Nova_de_nebula_bot). Silencieux si échec."""
    tok = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not tok or not chat:
        return
    try:
        httpx.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                   json={"chat_id": chat, "text": text, "disable_web_page_preview": True}, timeout=8)
    except Exception:
        pass

def tg_notify(chat: Any, text: str):
    """Envoi non bloquant (thread) pour ne pas ralentir la requête."""
    if chat:
        threading.Thread(target=tg_send, args=(chat, text), daemon=True).start()

def admin_tg_chat() -> str:
    """Chat Telegram de Mongazi (admin) : lié via le cockpit (setting) ou variable d'env."""
    return setting_get("admin_tg_chat") or os.getenv("NAFF_TG_ADMIN_CHAT", "") or os.getenv("NAFF_TG_CHAT", "")

def tg_admin(text: str):
    """Alerte Telegram à l'admin (même bot partagé que les partenaires)."""
    tg_notify(admin_tg_chat(), text)

def notify(role: str, target_id: int, text: str, lead_id: Optional[int] = None, kind: str = "info", ref_aff: int = 0):
    # ref_aff = l'affilié CONCERNÉ par la notif (pour cliquer → sa position dans la pyramide)
    tgchat = ""
    with db() as c:
        c.execute("INSERT INTO notifs(target_role,target_id,lead_id,text,lu,created,kind,ref_aff) VALUES(?,?,?,?,0,?,?,?)",
                  (role, target_id, lead_id, text, time.time(), kind, ref_aff or 0))
        if role == "affiliate" and target_id:
            row = c.execute("SELECT tg_chat FROM affiliates WHERE id=?", (target_id,)).fetchone()
            if row:
                tgchat = row["tg_chat"] or ""
    # Telegram UNIQUEMENT pour les événements importants (pas de bruit : ni statut, ni chat, ni info)
    if kind in ("client", "vente", "commission", "paiement", "recrue"):
        if role == "affiliate" and tgchat:
            tg_notify(tgchat, "🔔 NEBULA — " + text)
        elif role == "admin":
            tg_admin("🔔 NEBULA Agency — " + text)

def affiliate_label(a: sqlite3.Row) -> str:
    nom = " ".join(x for x in [a["prenom"], a["nom"]] if x).strip()
    return nom or a["code"]

def clean(s: Any, n: int = 200) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]

# ---- Anti-doublon par numéro de téléphone -----------------------------------
def phone_key(s: Any) -> str:
    """Forme canonique d'un numéro (Bénin) pour comparer : chiffres seuls, sans
    indicatif 229 ni zéros de tête. '0196999185', '+229 0196999185', '196999185' → même clé."""
    d = re.sub(r"\D", "", str(s or ""))
    if d.startswith("229"):
        d = d[3:]
    return d.lstrip("0")

def phone_is_affiliate(c, *nums) -> bool:
    """True si l'un des numéros correspond déjà à un partenaire ACTIF (anti-doublon)."""
    cand = {k for k in (phone_key(n) for n in nums) if len(k) >= 6}
    if not cand:
        return False
    for row in c.execute("SELECT momo_number FROM affiliates WHERE actif=1").fetchall():
        if phone_key(row["momo_number"]) in cand:
            return True
    return False

def phone_is_pending(c, *nums) -> bool:
    """True si une candidature/recrue EN ATTENTE existe déjà avec ce numéro (anti double-envoi)."""
    cand = {k for k in (phone_key(n) for n in nums) if len(k) >= 6}
    if not cand:
        return False
    for tbl in ("candidatures", "recruits"):
        try:
            for row in c.execute(f"SELECT numero, momo_number FROM {tbl} WHERE status='pending'").fetchall():
                if phone_key(row["numero"]) in cand or phone_key(row["momo_number"]) in cand:
                    return True
        except Exception:
            pass
    return False

# ----------------------------------------------------------------------------
# Email d'accès (Resend) — envoyé automatiquement à la validation
# ----------------------------------------------------------------------------
def esc_html(s: Any) -> str:
    return (str(s if s is not None else "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def public_base() -> str:
    return (os.getenv("NAFF_PUBLIC_BASE") or "https://partenaires.nebula-agency.online").rstrip("/")

def access_email_html(name: str, code: str, pin: str, parrain_name: Optional[str] = None) -> str:
    base = public_base()
    logo = base + "/static/nebula-logo.png"
    hub = f"{base}/p/{code}"
    parr = f'<p style="margin:0 0 14px;color:#5a5a72;font-size:14px">Tu rejoins le réseau de <b style="color:#1a1a2e">{esc_html(parrain_name)}</b>.</p>' if parrain_name else ""
    return f"""<!DOCTYPE html><html><body style="margin:0;background:#0b0b14;font-family:Segoe UI,Arial,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0b0b14;padding:28px 14px">
<tr><td align="center">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:20px;overflow:hidden">
    <tr><td style="background:linear-gradient(135deg,#7b5cff,#22d3ee);padding:34px 30px;text-align:center">
      <img src="{logo}" alt="NEBULA Agency" width="190" style="max-width:70%;height:auto;display:inline-block">
    </td></tr>
    <tr><td style="padding:34px 34px 10px">
      <h1 style="margin:0 0 8px;color:#13132a;font-size:23px">Bienvenue, {esc_html(name)} !</h1>
      <p style="margin:0 0 16px;color:#444;font-size:15px;line-height:1.6">Ta candidature au programme partenaires <b>NEBULA Agency</b> est <b style="color:#16a34a">validée</b>. Voici tes accès personnels — garde-les précieusement.</p>
      {parr}
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 20px;background:#f4f3fb;border:1px solid #e6e4f5;border-radius:14px">
        <tr><td style="padding:18px 22px">
          <div style="color:#7a7a93;font-size:12px;text-transform:uppercase;letter-spacing:1px">Ton code partenaire</div>
          <div style="color:#13132a;font-size:30px;font-weight:800;letter-spacing:3px;font-family:Consolas,monospace">{esc_html(code)}</div>
          <div style="height:10px"></div>
          <div style="color:#7a7a93;font-size:12px;text-transform:uppercase;letter-spacing:1px">Ton code PIN</div>
          <div style="color:#7b5cff;font-size:30px;font-weight:800;letter-spacing:6px;font-family:Consolas,monospace">{esc_html(pin)}</div>
        </td></tr>
      </table>
      <a href="{base}/partenaire" style="display:block;background:#7b5cff;color:#fff;text-decoration:none;text-align:center;padding:15px;border-radius:12px;font-weight:700;font-size:15px">Ouvrir mon espace partenaire</a>
      <p style="margin:18px 0 6px;color:#444;font-size:14px;line-height:1.6"><b>Ton lien unique</b> à partager (clients ET nouvelles recrues) :</p>
      <p style="margin:0 0 18px"><a href="{hub}" style="color:#7b5cff;font-size:14px;word-break:break-all">{hub}</a></p>
      <p style="margin:0 0 6px;color:#444;font-size:14px;line-height:1.6">Tes premiers pas : connecte-toi, complète ta photo, et partage ton lien. Tu gagnes sur tes ventes <b>et</b> sur celles de ton équipe.</p>
    </td></tr>
    <tr><td style="padding:18px 34px 30px;border-top:1px solid #eee">
      <p style="margin:0;color:#9a9ab0;font-size:12px;line-height:1.6">NEBULA Agency · Cotonou, Bénin · Une question ? Réponds simplement à cet email.</p>
    </td></tr>
  </table>
</td></tr></table></body></html>"""

def send_access_email(to: str, name: str, code: str, pin: str, parrain_name: Optional[str] = None) -> Dict[str, Any]:
    """Envoie l'email d'accès via Resend. Ne lève jamais — renvoie {ok, error}."""
    key = os.getenv("RESEND_API_KEY", "")
    to = (to or "").strip()
    if not key or "@" not in to:
        return {"ok": False, "error": "email ou clé Resend indisponible"}
    frm_addr = os.getenv("EMAIL_FROM_ADDRESS", "").strip() or "onboarding@resend.dev"
    frm_name = os.getenv("EMAIL_FROM_NAME", "").strip() or "NEBULA Agency"
    payload = {"from": f"{frm_name} <{frm_addr}>", "to": [to],
               "subject": "Bienvenue chez NEBULA Agency — tes accès partenaire",
               "html": access_email_html(name, code, pin, parrain_name)}
    reply = os.getenv("EMAIL_REPLY_TO", "").strip()
    if reply:
        payload["reply_to"] = reply
    try:
        r = httpx.post("https://api.resend.com/emails",
                       headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                       json=payload, timeout=20)
        if r.status_code in (200, 201):
            return {"ok": True, "id": (r.json() or {}).get("id")}
        return {"ok": False, "error": f"Resend {r.status_code}: {r.text[:160]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

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

def generate_commissions(lead: sqlite3.Row) -> Dict[str, Any]:
    """À la vente PAYÉE : crée auto les commissions direct + N1 + N2, alerte chaque bénéficiaire,
    et RENVOIE le détail complet (qui touche combien, quel %, MoMo) pour l'afficher tout de suite à l'admin."""
    client = (str(lead["prenom"] or "") + " " + str(lead["nom"] or "")).strip() or "ce client"
    price = lead["montant"] if lead["montant"] else SERVICES.get(lead["service"], {}).get("price", 0)
    svc = SERVICES.get(lead["service"], {}).get("label", lead["service"])
    empty = {"client": client, "price": int(price or 0), "service": svc, "lines": [], "total": 0, "already": False}
    entries = []  # (beneficiary_row, level, pct, amount)
    with db() as c:
        if c.execute("SELECT COUNT(*) n FROM commissions WHERE lead_id=? AND status!='void'", (lead["id"],)).fetchone()["n"]:
            return {**empty, "already": True}  # idempotent : déjà généré
        aff = c.execute("SELECT * FROM affiliates WHERE id=?", (lead["affiliate_id"],)).fetchone()
        if not aff:
            return empty                                   # client direct (site) : aucune commission
        rate = stats_of(aff["id"])["direct_rate"]
        entries.append((aff, "direct", rate, int(round(price * rate))))
        p1 = c.execute("SELECT * FROM affiliates WHERE id=? AND actif=1", (aff["parrain_id"] or 0,)).fetchone()
        if p1:
            entries.append((p1, "n1", DEPTH_N1, int(round(price * DEPTH_N1))))
            p2 = c.execute("SELECT * FROM affiliates WHERE id=? AND actif=1", (p1["parrain_id"] or 0,)).fetchone()
            if p2:
                entries.append((p2, "n2", DEPTH_N2, int(round(price * DEPTH_N2))))
        now = time.time()
        for ben, lvl, pct, amt in entries:
            if amt > 0:
                c.execute("INSERT INTO commissions(lead_id,beneficiary_id,level,amount,status,created) VALUES(?,?,?,?,'due',?)",
                          (lead["id"], ben["id"], lvl, amt, now))
    labels = {"direct": "vente directe", "n1": "réseau N1", "n2": "réseau N2"}
    lines = []
    for ben, lvl, pct, amt in entries:
        if amt <= 0:
            continue
        pc = int(round(pct * 100))
        notify("affiliate", ben["id"], f"Commission à réclamer : {fmoney(amt)} F ({labels[lvl]}, {pc}%) sur la vente de {client}.", lead["id"], kind="commission", ref_aff=ben["id"])
        lines.append({"name": affiliate_label(ben), "level": lvl, "level_label": labels[lvl], "pct": pc,
                      "amount": amt, "momo_number": ben["momo_number"] or "", "momo_reseau": ben["momo_reseau"] or "",
                      "beneficiary_id": ben["id"]})
    total = sum(x["amount"] for x in lines)
    if lines:
        detail = " · ".join(f"{x['name']} {fmoney(x['amount'])} F ({x['pct']}%)" for x in lines)
        notify("admin", 0, f"À VERSER sur {client} ({svc}, {fmoney(price)} F) → {detail}", lead["id"], kind="vente", ref_aff=lead["affiliate_id"])
    return {"client": client, "price": int(price or 0), "service": svc, "lines": lines, "total": total, "already": False}

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

def seed_docs():
    """Publie automatiquement les PDF livrés dans le repo (assets/) dans la Documentation,
    visibles côté partenaire ET admin. Idempotent. Pour pousser une nouvelle version d'un PDF :
    remplacer le fichier dans assets/ et bumper sa 'version' ci-dessous."""
    BUNDLED = [
        ("NEBULA_Programme_Partenaires.pdf", "2026-06-21",
         "Brochure du Programme Partenaires (PDF premium)", "Formation",
         "La présentation complète à montrer aux prospects et à garder sous la main : "
         "vision, offres et prix (dont 15 000 F/6 mois d'hébergement), commissions 25-40% + réseau N1/N2, "
         "rangs, et l'exemple chiffré du réseau. 14 pages, prête à partager."),
        ("kit-nebula.pdf", "2026-06-21",
         "Kit NEBULA — l'essentiel du partenaire (PDF)", "Formation",
         "Le kit de démarrage à garder sous la main : qui nous sommes, nos offres, et les arguments "
         "clés pour présenter NEBULA à un commerçant. À partager sans modération."),
    ]
    for fkey, version, title, cat, desc in BUNDLED:
        src = HERE / "assets" / fkey
        if not src.exists():
            continue
        marker = re.sub(r"[^a-zA-Z0-9]", "_", fkey) + "_" + version + ".pdf"
        try:
            with db() as c:
                row = c.execute("SELECT * FROM documents WHERE title=?", (title,)).fetchone()
                if row and row["filename"] == marker:
                    continue  # déjà à jour
                data = src.read_bytes(); size = len(data); now = time.time()
                (UP_DIR / marker).write_bytes(data)
                if row and row["filename"] and row["filename"] != marker:
                    try: (UP_DIR / row["filename"]).unlink()
                    except Exception: pass
                if row:
                    c.execute("UPDATE documents SET category=?,description=?,kind='pdf',filename=?,size=?,updated=? WHERE id=?",
                              (cat, desc, marker, size, now, row["id"]))
                else:
                    c.execute("""INSERT INTO documents(title,category,description,kind,body,url,filename,size,updated,created)
                                 VALUES(?,?,?,'pdf','','',?,?,?,?)""",
                              (title, cat, desc, marker, size, now, now))
        except Exception as e:
            print("seed_docs:", fkey, e)

def seed():
    # Plus de compte démo : la plateforme démarre vide, prête pour de vrais partenaires.
    return
seed()
seed_content()
seed_docs()

# ----------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------
app = FastAPI(title="NEBULA Affiliés")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=True)
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")

def _asset_ver() -> str:
    """Version automatique des assets = empreinte (taille+mtime) de app.js + app.css.
    Change à CHAQUE déploiement où ces fichiers changent → le navigateur refetch tout seul.
    Fini les bugs de cache périmé (barre de message absente, vues vides, classement vide…)."""
    sig = []
    for f in ("app.js", "app.css"):
        try:
            st = (HERE / "static" / f).stat()
            sig.append(f"{int(st.st_mtime)}-{st.st_size}")
        except Exception:
            sig.append("0")
    raw = "|".join(sig)
    return hashlib.md5(raw.encode()).hexdigest()[:10]

ASSET_VER = _asset_ver()
_ASSET_RE = re.compile(r'(app\.(?:js|css)\?v=)[0-9A-Za-z]+')

def _render_html(name: str, request: Optional[Request] = None) -> HTMLResponse:
    """Lit une page HTML, force la version d'asset auto (anti-cache) + injecte BASE/ADMIN_PATH."""
    html = (HERE / name).read_text(encoding="utf-8")
    html = _ASSET_RE.sub(lambda m: m.group(1) + ASSET_VER, html)
    if "{{BASE}}" in html:
        host = (request.headers.get("x-forwarded-host") if request else None) or (request.headers.get("host") if request else None) or "nebula-affilies-production.up.railway.app"
        proto = ((request.headers.get("x-forwarded-proto") if request else None) or "https").split(",")[0].strip()
        html = html.replace("{{BASE}}", f"{proto}://{host}")
    if "{{ADMIN_PATH}}" in html:
        html = html.replace("{{ADMIN_PATH}}", "/" + ADMIN_PATH)
    # HTML jamais figé en cache → le navigateur revalide et voit toujours la dernière version d'asset
    return HTMLResponse(html, headers={"Cache-Control": "no-cache, must-revalidate"})

def page(name: str) -> HTMLResponse:
    return _render_html(name)

def served_page(name: str, request: Request) -> HTMLResponse:
    """Sert une page HTML en injectant l'URL absolue ({{BASE}}) + le chemin admin privé ({{ADMIN_PATH}}) + version d'asset auto."""
    return _render_html(name, request)

@app.get("/", response_class=HTMLResponse)
def home():
    return page("index.html")

# Console NEBULA : dashboard servi UNIQUEMENT à un admin connecté (sinon retour au portail public,
# sans jamais révéler l'URL secrète de connexion). La page de login admin vit sur ADMIN_PATH.
@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return RedirectResponse("/", status_code=302)
    return served_page("admin.html", request)

@app.get("/" + ADMIN_PATH, response_class=HTMLResponse)
def admin_login_page(request: Request):
    return served_page("console.html", request)

@app.get("/partenaire", response_class=HTMLResponse)
def partner_page():
    return page("partenaire.html")

@app.get("/r/{code}", response_class=HTMLResponse)
def referral_page(code: str, request: Request):
    return served_page("lead.html", request)

@app.get("/rejoindre/{code}", response_class=HTMLResponse)
def recruit_page(code: str, request: Request):
    return served_page("rejoindre.html", request)

@app.get("/devenir", response_class=HTMLResponse)
def devenir_page(request: Request):
    return served_page("devenir.html", request)

@app.get("/p/{code}", response_class=HTMLResponse)
def hub_page(code: str, request: Request):
    return served_page("hub.html", request)

# ---- Config publique (catalogue, statuts, réseaux) pour les fronts ----
@app.get("/api/config")
def api_config():
    return {
        "services": SERVICES, "statuses": STATUSES, "reseaux": RESEAUX,
        "commission_rate": COMMISSION_RATE, "momo": {"number": MOMO_NUMBER, "name": MOMO_NAME},
        "whatsapp": WHATSAPP, "ranks": [{"min": r[0], "label": r[1], "emoji": r[2]} for r in RANKS],
        "paliers": [{"min": p[0], "label": p[1], "emoji": p[2], "pct": int(round(p[3] * 100))} for p in PALIERS],
        "paliers_sup": [{"min": p[0], "label": p[1], "emoji": p[2], "pct": int(round(p[3] * 100))} for p in PALIERS_SUP],
        "depths": {"n1": int(DEPTH_N1 * 100), "n2": int(DEPTH_N2 * 100)},
        "founder": {"name": FOUNDER_NAME, "title": FOUNDER_TITLE, "rank": FOUNDER_RANK},
    }

# =====================  PUBLIC : formulaire de parrainage  ====================
@app.get("/api/affiliate/{code}/public")
def affiliate_public(code: str):
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE code=? AND actif=1", (code.upper(),)).fetchone()
    if not a:
        return JSONResponse({"ok": False, "error": "Lien partenaire introuvable."}, status_code=404)
    s = stats_of(a["id"])
    return {"ok": True, "code": a["code"], "name": affiliate_label(a),
            "photo": photo_url("a" + str(a["id"])), "rank": s["rank"]["label"]}

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
    notify("admin", 0, f"Nouveau client via {affiliate_label(a)} : {client} — {svc}", lead_id, kind="client", ref_aff=a["id"])
    notify("affiliate", a["id"], f"{client} a rempli ton formulaire — en attente de validation.", lead_id, kind="client")
    return {"ok": True}

def map_service(raw: str) -> str:
    """Devine la clé SERVICES depuis le libellé libre du formulaire du site."""
    t = (raw or "").lower()
    if "catalog" in t: return "catalogue"
    if "vitrine" in t or "site" in t or "boutique" in t: return "vitrine"
    if "maps" in t or "google" in t or "fiche" in t: return "maps"
    if "avis" in t or "review" in t or "qr" in t: return "review"
    if "avatar" in t and ("pro" in t or "100" in t): return "avatar_pro"
    if "avatar" in t: return "avatar_essentiel"
    return "autre"

@app.post("/api/site-lead")
async def create_site_lead(req: Request):
    """Client DIRECT depuis le site NEBULA Agency (sans affilié). affiliate_id=0, source='site'.
    Notifie l'admin (back-office + Telegram) avec le brief complet."""
    d = await req.json()
    nom = clean(d.get("nom"), 90); numero = clean(d.get("numero"), 30)
    if not nom or not numero:
        return JSONResponse({"ok": False, "error": "Nom et numéro obligatoires."}, status_code=400)
    service = map_service(d.get("service"))
    brief = clean(d.get("message"), 1800)            # le brief complet (déjà mis en forme par le site)
    now = time.time()
    with db() as c:
        cur = c.execute("""INSERT INTO leads(affiliate_id,nom,prenom,numero,service,message,status,paye,created,updated,source)
                           VALUES(0,?,?,?,?,?,'attente',0,?,?,'site')""",
                        (nom, "", numero, service, brief, now, now))
        lead_id = cur.lastrowid
    svc = SERVICES.get(service, {}).get("label", service)
    notify("admin", 0, f"NOUVEAU CLIENT (site) : {nom} ({numero}) — {svc}", lead_id, kind="client")
    # Brief complet en second message Telegram (lisible, hors fil de notif in-app)
    tg_admin(f"📝 Brief de {nom} ({numero}) :\n\n{brief or '(pas de description)'}")
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
        numero = clean(d.get("numero"), 30); email = clean(d.get("email"), 120)
        momo = clean(d.get("momo_number"), 30); reseau = clean(d.get("momo_reseau"), 30) or RESEAUX[0]
        msg = clean(d.get("message"), 300)
        if not (nom or prenom) or not numero:
            return JSONResponse({"ok": False, "error": "Nom et numéro obligatoires."}, status_code=400)
        if phone_is_affiliate(c, numero, momo):
            return JSONResponse({"ok": False, "error": "Ce numéro est déjà partenaire NEBULA. Connecte-toi à ton espace partenaire — pas besoin de t'inscrire à nouveau."}, status_code=409)
        if phone_is_pending(c, numero, momo):
            return JSONResponse({"ok": False, "error": "Une demande avec ce numéro est déjà en cours de validation. Patiente, NEBULA revient vers toi très vite."}, status_code=409)
        c.execute("""INSERT INTO recruits(parrain_id,nom,prenom,numero,email,momo_number,momo_reseau,message,status,created)
                     VALUES(?,?,?,?,?,?,?,?,'pending',?)""",
                  (a["id"], nom, prenom, numero, email, momo, reseau, msg, time.time()))
    who = (prenom + " " + nom).strip()
    notify("admin", 0, f"Nouvelle recrue : {who} ({numero}) — parrainé(e) par {affiliate_label(a)}", kind="recrue", ref_aff=a["id"])
    notify("affiliate", a["id"], f"{who} veut rejoindre via ton lien — en attente de validation NEBULA.", kind="recrue")
    return {"ok": True}

# ==================  TRACKING DU LIEN + QR (carte de visite)  ================
@app.post("/api/track")
async def api_track(req: Request):
    d = await req.json()
    code = clean(d.get("code"), 12).upper()
    kind = clean(d.get("kind"), 12)
    if kind not in ("open", "client", "partner"):
        return JSONResponse({"ok": False}, status_code=400)
    with db() as c:
        a = c.execute("SELECT id FROM affiliates WHERE code=? AND actif=1", (code,)).fetchone()
        if a:
            c.execute("INSERT INTO link_events(affiliate_id,kind,created) VALUES(?,?,?)", (a["id"], kind, time.time()))
    return {"ok": True}

@app.get("/api/qr")
async def api_qr(data: str, size: int = 440):
    size = max(120, min(800, int(size)))
    url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&margin=12&data={quote(data, safe='')}"
    try:
        async with httpx.AsyncClient(timeout=12) as cli:
            r = await cli.get(url)
        return Response(content=r.content, media_type="image/png")
    except Exception:
        return JSONResponse({"error": "qr indisponible"}, status_code=502)

# =============================  AUTH  ========================================
# --- Anti-force brute sur la console admin (limiteur en mémoire, par IP) ---
_LOGIN_FAILS: Dict[str, list] = {}
LOGIN_WINDOW = 900     # fenêtre de 15 min
LOGIN_MAX = 6          # échecs tolérés avant blocage temporaire

def _client_ip(req: Request) -> str:
    return ((req.headers.get("x-forwarded-for", "").split(",")[0].strip()
             or (req.client.host if req.client else "")) or "?")[:60]

def login_locked(ip: str) -> int:
    """Secondes de blocage restantes (0 = pas bloqué)."""
    now = time.time()
    fails = [t for t in _LOGIN_FAILS.get(ip, []) if now - t < LOGIN_WINDOW]
    _LOGIN_FAILS[ip] = fails
    return int(LOGIN_WINDOW - (now - fails[0])) + 1 if len(fails) >= LOGIN_MAX else 0

@app.post("/api/admin/login")
async def admin_login(req: Request, resp: Response):
    ip = _client_ip(req)
    wait = login_locked(ip)
    if wait:
        return JSONResponse({"ok": False, "error": f"Trop de tentatives. Réessaie dans {wait // 60 + 1} min."}, status_code=429)
    d = await req.json()
    email = clean(d.get("email"), 120).lower()
    if email in ADMIN_EMAILS and (d.get("password") or "") == ADMIN_PASS:
        _LOGIN_FAILS.pop(ip, None)
        set_cookie(resp, "admin", 0)
        return {"ok": True}
    _LOGIN_FAILS.setdefault(ip, []).append(time.time())
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

# --- PIN oublié : le partenaire demande, NEBULA (admin) lui renvoie ses accès sur WhatsApp ---
_FORGOT_HITS: Dict[str, list] = {}
@app.post("/api/partenaire/forgot")
async def partner_forgot(req: Request):
    ip = _client_ip(req); now = time.time()
    hits = [t for t in _FORGOT_HITS.get(ip, []) if now - t < 900]
    if len(hits) >= 6:
        return {"ok": True}            # silencieux (anti-spam)
    hits.append(now); _FORGOT_HITS[ip] = hits
    try:
        d = await req.json()
    except Exception:
        d = {}
    query = clean(d.get("query"), 40)
    if query:
        qcode = query.upper().strip(); qd = re.sub(r"\D", "", query)
        with db() as c:
            rows = c.execute("SELECT * FROM affiliates WHERE actif=1").fetchall()
        a = next((r for r in rows if (r["code"] or "").upper() == qcode
                  or (qd and re.sub(r"\D", "", r["momo_number"] or "") == qd)), None)
        if a:
            notify("admin", 0, f"Réinitialisation PIN demandée : {affiliate_label(a)} (code {a['code']}). "
                   f"Va dans Affiliés et clique « Renvoyer accès » sur sa fiche pour régénérer son PIN et l'envoyer sur WhatsApp.", kind="recrue", ref_aff=a["id"])
    return {"ok": True}                # réponse générique (ne révèle pas si le code existe)

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
                rate_cache[aid] = 0 if not aid else stats_of(aid)["direct_rate"]
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
            "ventes_rank": s["ventes_rank"], "team_ventes": s["team_ventes"], "team_mois": s["team_mois"],
            "role": s["role"], "role_label": s["role_label"], "is_supervisor": s["is_supervisor"],
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

@app.post("/api/admin/affiliates/{aid}/reset-pin")
def admin_reset_pin(aid: int, naff_session: Optional[str] = Cookie(default=None)):
    """Régénère un nouveau PIN (l'ancien est haché, donc irrécupérable) — pour ré-envoyer les accès."""
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        a = c.execute("SELECT code FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"ok": False}, status_code=404)
        pin = "".join(secrets.choice("0123456789") for _ in range(4))
        c.execute("UPDATE affiliates SET pin=? WHERE id=?", (hash_pw(pin), aid))
    notify("affiliate", aid, "Tes accès ont été réinitialisés par NEBULA — nouveau PIN envoyé.", kind="info")
    return {"ok": True, "code": a["code"], "pin": pin}

@app.post("/api/admin/affiliates/{aid}/email-access")
def admin_email_access(aid: int, naff_session: Optional[str] = Cookie(default=None)):
    """Envoi (ou renvoi) des accès par EMAIL. Régénère un PIN (l'ancien est haché)."""
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"ok": False}, status_code=404)
        email = clean(a["email"], 120)
        if "@" not in email:
            return {"ok": False, "error": "no_email"}
        pin = "".join(secrets.choice("0123456789") for _ in range(4))
        c.execute("UPDATE affiliates SET pin=? WHERE id=?", (hash_pw(pin), aid))
        pr = c.execute("SELECT nom,prenom FROM affiliates WHERE id=?", (a["parrain_id"] or 0,)).fetchone()
    parrain_name = (str(pr["prenom"] or "") + " " + str(pr["nom"] or "")).strip() if pr else None
    sent = send_access_email(email, affiliate_label(a), a["code"], pin, parrain_name)
    if sent.get("ok"):
        notify("affiliate", aid, "Tes accès viennent de t'être envoyés par email.", kind="info", ref_aff=aid)
    return {"ok": bool(sent.get("ok")), "email": email, "error": sent.get("error")}

@app.post("/api/admin/affiliates/{aid}/delete")
def admin_delete_affiliate(aid: int, naff_session: Optional[str] = Cookie(default=None)):
    """Supprime définitivement un partenaire et ses données liées (clients, commissions, etc.)."""
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        a = c.execute("SELECT code, photo FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"ok": False}, status_code=404)
        c.execute("DELETE FROM leads WHERE affiliate_id=?", (aid,))
        c.execute("DELETE FROM commissions WHERE beneficiary_id=?", (aid,))
        c.execute("DELETE FROM link_events WHERE affiliate_id=?", (aid,))
        c.execute("DELETE FROM recruits WHERE parrain_id=?", (aid,))
        c.execute("DELETE FROM notifs WHERE target_role='affiliate' AND target_id=?", (aid,))
        c.execute("UPDATE affiliates SET parrain_id=0 WHERE parrain_id=?", (aid,))
        c.execute("DELETE FROM affiliates WHERE id=?", (aid,))
    if a["photo"]:
        try: (UP_DIR / a["photo"]).unlink()
        except Exception: pass
    return {"ok": True, "code": a["code"]}

@app.post("/api/admin/affiliates/{aid}/rate")
async def admin_set_rate(aid: int, req: Request, naff_session: Optional[str] = Cookie(default=None)):
    """Fixe un taux de commission directe personnalisé (ex : partenaire privilégié 40%). 0 = retour au système des paliers."""
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    try:
        rate = float(d.get("rate") or 0)
    except Exception:
        rate = 0.0
    if rate > 1:           # accepte 40 (=> 0.40) ou 0.40
        rate = rate / 100.0
    rate = max(0.0, min(0.95, rate))
    with db() as c:
        a = c.execute("SELECT code FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"ok": False}, status_code=404)
        c.execute("UPDATE affiliates SET direct_rate_override=? WHERE id=?", (rate, aid))
    return {"ok": True, "code": a["code"], "rate": rate, "pct": int(round(rate * 100))}

@app.post("/api/admin/affiliates/{aid}/role")
async def admin_set_role(aid: int, req: Request, naff_session: Optional[str] = Cookie(default=None)):
    """Définit le rôle spécial d'un partenaire. 'superviseur' = barème 2 paliers d'équipe
    (Starter 25% <3 clients/mois, Silver 40% dès 3), titre « Superviseur ». '' = recrue standard."""
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    role = clean(d.get("role"), 20).lower()
    if role not in ROLE_LABELS:
        role = ""
    with db() as c:
        a = c.execute("SELECT code FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"ok": False}, status_code=404)
        c.execute("UPDATE affiliates SET role=? WHERE id=?", (role, aid))
    return {"ok": True, "code": a["code"], "role": role, "role_label": ROLE_LABELS.get(role, "")}

@app.post("/api/admin/affiliates/{aid}/edit")
async def admin_edit_affiliate(aid: int, req: Request, naff_session: Optional[str] = Cookie(default=None)):
    """Modifie les infos d'un partenaire (nom, prénom, numéro Mobile Money, réseau)."""
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    d = await req.json()
    fields, vals = [], []
    if d.get("prenom") is not None: fields.append("prenom=?"); vals.append(clean(d.get("prenom"), 80))
    if d.get("nom") is not None: fields.append("nom=?"); vals.append(clean(d.get("nom"), 80))
    if d.get("momo_number") is not None: fields.append("momo_number=?"); vals.append(clean(d.get("momo_number"), 30))
    if d.get("momo_reseau") is not None:
        res = clean(d.get("momo_reseau"), 30)
        fields.append("momo_reseau=?"); vals.append(res if res in RESEAUX else RESEAUX[0])
    if not fields:
        return {"ok": True}
    vals.append(aid)
    with db() as c:
        a = c.execute("SELECT code FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"ok": False}, status_code=404)
        c.execute(f"UPDATE affiliates SET {','.join(fields)} WHERE id=?", vals)
    return {"ok": True, "code": a["code"]}

@app.get("/api/admin/leads")
def admin_leads(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("""SELECT l.*, a.code acode, a.nom anom, a.prenom aprenom
                            FROM leads l LEFT JOIN affiliates a ON a.id=l.affiliate_id
                            ORDER BY l.created DESC""").fetchall()
        # heure de début = 1re fois passé « en cours » (depuis l'historique)
        starts = {r["lead_id"]: r["t"] for r in c.execute(
            "SELECT lead_id, MIN(at) t FROM history WHERE new_status='en_cours' GROUP BY lead_id").fetchall()}
    rate_cache = {}
    out = []
    for r in rows:
        aid = r["affiliate_id"]
        direct = not aid
        if aid not in rate_cache:
            rate_cache[aid] = 0 if direct else stats_of(aid)["direct_rate"]
        aff = ({"code": "", "name": "Client direct (site)", "direct": True} if direct
               else {"code": r["acode"], "name": (str(r["aprenom"] or "") + " " + str(r["anom"] or "")).strip() or r["acode"], "direct": False})
        out.append({
            "id": r["id"], "nom": r["nom"], "prenom": r["prenom"], "numero": r["numero"],
            "service": r["service"], "service_label": SERVICES.get(r["service"], {}).get("label", r["service"]),
            "message": r["message"], "status": r["status"], "paye": r["paye"],
            "commission": 0 if direct else commission_of(r["service"], r["montant"], rate_cache[aid]),
            "montant": int(r["montant"] or 0),
            "source": (r["source"] if "source" in r.keys() else "affilie") or "affilie",
            "created": r["created"], "updated": r["updated"], "started_at": starts.get(r["id"]),
            "affiliate": aff,
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
    if r["affiliate_id"]:        # client d'affilié → on le notifie ; client direct (0) → rien
        notify("affiliate", r["affiliate_id"], f"{client} : statut → {STATUSES[st]['label']}", lid, kind="statut")
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
    breakdown = None
    if paye:
        breakdown = generate_commissions(r)      # crée + alerte direct / N1 / N2 + RENVOIE le détail
    else:
        void_commissions(lid)
    return {"ok": True, "breakdown": breakdown}

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
        if phone_is_affiliate(c, r["numero"], r["momo_number"]):
            c.execute("UPDATE recruits SET status='rejected' WHERE id=?", (rid,))   # doublon : pas de 2e compte
            return JSONResponse({"ok": False, "error": "Ce numéro est déjà un partenaire actif — doublon évité, la demande a été archivée."}, status_code=409)
        pin = "".join(secrets.choice("0123456789") for _ in range(4))
        code = new_code(c)
        try:
            email = clean(r["email"], 120)
        except Exception:
            email = ""
        c.execute("""INSERT INTO affiliates(code,nom,prenom,momo_number,momo_reseau,pin,accent,actif,created,parrain_id,email)
                     VALUES(?,?,?,?,?,?,?,1,?,?,?)""",
                  (code, r["nom"], r["prenom"], r["momo_number"], r["momo_reseau"], hash_pw(pin), "#7b5cff", time.time(), r["parrain_id"], email))
        c.execute("UPDATE recruits SET status='approved' WHERE id=?", (rid,))
        pr = c.execute("SELECT nom,prenom FROM affiliates WHERE id=?", (r["parrain_id"],)).fetchone()
    parrain_name = (str(pr["prenom"] or "") + " " + str(pr["nom"] or "")).strip() if pr else None
    who = (str(r["prenom"] or "") + " " + str(r["nom"] or "")).strip()
    notify("affiliate", r["parrain_id"], f"Ta recrue {who} est validée — elle rejoint ton réseau (N1).", kind="recrue", ref_aff=r["parrain_id"])
    sent = send_access_email(email, who or code, code, pin, parrain_name) if email else {"ok": False}
    return {"ok": True, "code": code, "pin": pin, "email": email, "email_sent": bool(sent.get("ok"))}

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
        comm = c.execute("""SELECT beneficiary_id bid, status, SUM(amount) s FROM commissions
                            WHERE status IN ('due','claimed') GROUP BY beneficiary_id, status""").fetchall()
        leadc = c.execute("SELECT affiliate_id aid, COUNT(*) n, SUM(paye) p FROM leads GROUP BY affiliate_id").fetchall()
    due_by = {}; claimed_by = {}
    for r in comm:
        (due_by if r["status"] == "due" else claimed_by)[r["bid"]] = int(r["s"] or 0)
    clients_n = {r["aid"]: r["n"] for r in leadc}
    clients_p = {r["aid"]: int(r["p"] or 0) for r in leadc}
    by_parent: Dict[int, list] = {}
    info: Dict[int, dict] = {}
    for a in affs:
        by_parent.setdefault(a["parrain_id"] or 0, []).append(a)
        s = stats_of(a["id"])
        due = due_by.get(a["id"], 0); claimed = claimed_by.get(a["id"], 0)
        info[a["id"]] = {"id": a["id"], "name": affiliate_label(a), "code": a["code"],
                         "ventes": s["ventes"], "rank": s["rank"]["label"], "palier": s["palier"]["label"],
                         "due": due, "claimed": claimed, "owed": due + claimed,
                         "clients": clients_n.get(a["id"], 0), "clients_paid": clients_p.get(a["id"], 0),
                         "parrain_id": a["parrain_id"] or 0}
    def build(pid: int, depth: int):
        out = []
        for a in by_parent.get(pid, []):
            node = dict(info[a["id"]])
            node["children"] = build(a["id"], depth + 1) if depth < 8 else []
            out.append(node)
        return out
    return {"roots": build(0, 0), "total": len(affs)}

@app.get("/api/admin/affiliate/{aid}/detail")
def admin_affiliate_detail(aid: int, naff_session: Optional[str] = Cookie(default=None)):
    """Fiche complète d'un affilié pour le tiroir de la pyramide : position réseau,
    commissions à payer, clients à valider, filleuls, chaîne de parrainage."""
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        a = c.execute("SELECT * FROM affiliates WHERE id=?", (aid,)).fetchone()
        if not a:
            return JSONResponse({"error": "introuvable"}, status_code=404)
        p1 = c.execute("SELECT id,code,nom,prenom,parrain_id FROM affiliates WHERE id=?", (a["parrain_id"] or 0,)).fetchone()
        p2 = c.execute("SELECT id,code,nom,prenom FROM affiliates WHERE id=?", (p1["parrain_id"] or 0,)).fetchone() if p1 else None
        pend = c.execute("""SELECT cm.level, cm.amount, cm.status, cm.created, l.nom lnom, l.prenom lprenom
                            FROM commissions cm JOIN leads l ON l.id=cm.lead_id
                            WHERE cm.beneficiary_id=? AND cm.status IN ('due','claimed') ORDER BY cm.created DESC""", (aid,)).fetchall()
        leads = c.execute("SELECT * FROM leads WHERE affiliate_id=? ORDER BY created DESC", (aid,)).fetchall()
        n1 = c.execute("SELECT id,code,nom,prenom FROM affiliates WHERE parrain_id=? AND actif=1 ORDER BY created", (aid,)).fetchall()
        n1_ids = [x["id"] for x in n1]; n2_count = 0; owed_by = {}
        if n1_ids:
            q = ",".join("?" * len(n1_ids))
            n2_count = c.execute(f"SELECT COUNT(*) n FROM affiliates WHERE actif=1 AND parrain_id IN ({q})", n1_ids).fetchone()["n"]
            for r in c.execute(f"SELECT beneficiary_id bid, SUM(amount) s FROM commissions WHERE status IN ('due','claimed') AND beneficiary_id IN ({q}) GROUP BY beneficiary_id", n1_ids).fetchall():
                owed_by[r["bid"]] = int(r["s"] or 0)
    s = stats_of(aid); e = earnings_of(aid); rate = s["direct_rate"]
    LBL = {"direct": "Vente directe", "n1": "Réseau N1 · 10%", "n2": "Réseau N2 · 5%"}
    nm = lambda p, lvl: ({"id": p["id"], "code": p["code"],
                          "name": (str(p["prenom"] or "") + " " + str(p["nom"] or "")).strip() or p["code"], "level": lvl} if p else None)
    pending = [{"level": LBL.get(r["level"], r["level"]), "amount": int(r["amount"]), "status": r["status"],
                "client": (str(r["lprenom"] or "") + " " + str(r["lnom"] or "")).strip(), "created": r["created"]} for r in pend]
    clients = [{"id": l["id"], "name": (str(l["prenom"] or "") + " " + str(l["nom"] or "")).strip() or "Client",
                "service": SERVICES.get(l["service"], {}).get("label", l["service"]),
                "status": l["status"], "status_label": STATUSES.get(l["status"] or "attente", {}).get("label", l["status"]),
                "paye": l["paye"], "montant": int(l["montant"] or 0),
                "commission": commission_of(l["service"], l["montant"], rate)} for l in leads]
    filleuls = [{"id": x["id"], "code": x["code"],
                 "name": (str(x["prenom"] or "") + " " + str(x["nom"] or "")).strip() or x["code"],
                 "owed": owed_by.get(x["id"], 0)} for x in n1]
    return {
        "profile": {"id": a["id"], "name": affiliate_label(a), "code": a["code"],
                    "rank": s["rank"]["label"], "palier": s["palier"]["label"], "palier_pct": s["palier"]["pct"],
                    "rate_pct": int(round(rate * 100)), "photo": photo_url("a" + str(aid)),
                    "role": s["role"], "role_label": s["role_label"], "is_supervisor": s["is_supervisor"],
                    "paliers": s["paliers"], "ventes_rank": s["ventes_rank"], "team_ventes": s["team_ventes"],
                    "team_mois": s["team_mois"], "rate_override": float(a["direct_rate_override"] or 0),
                    "momo_number": a["momo_number"], "momo_reseau": a["momo_reseau"], "email": (a["email"] or ""),
                    "ventes": s["ventes"], "ventes_mois": s["ventes_mois"], "rcm": int(s["rcm"]), "created": a["created"]},
        "parrain": nm(p1, "N1 · 10%"), "grandparrain": nm(p2, "N2 · 5%"),
        "earnings": e,
        "pending": pending,
        "total_due": int(sum(p["amount"] for p in pending if p["status"] == "due")),
        "total_claimed": int(sum(p["amount"] for p in pending if p["status"] == "claimed")),
        "total_owed": int(sum(p["amount"] for p in pending)),
        "clients": clients, "filleuls": filleuls, "n1_count": len(n1), "n2_count": n2_count,
    }

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
        notify("affiliate", aff_id, f"Paiement reçu : {fmoney(total)} F versés par NEBULA ({n} commission(s)). Merci pour ton travail !", kind="paiement")
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
    parrain = None
    if a["parrain_id"]:
        with db() as c:
            p = c.execute("SELECT code,nom,prenom FROM affiliates WHERE id=? AND actif=1", (a["parrain_id"],)).fetchone()
        if p:
            parrain = {"name": (str(p["prenom"] or "") + " " + str(p["nom"] or "")).strip() or p["code"], "code": p["code"]}
    return {
        "code": a["code"], "nom": a["nom"], "prenom": a["prenom"],
        "name": affiliate_label(a), "accent": a["accent"],
        "momo_number": a["momo_number"], "momo_reseau": a["momo_reseau"],
        "photo": photo_url("a" + str(aid)),
        "stats": s, "network": network_of(aid), "earnings": earnings_of(aid),
        "parrain": parrain,
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

@app.get("/api/partenaire/linkstats")
def partner_linkstats(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    ms = month_start_ts()
    out = {"open": 0, "client": 0, "partner": 0, "open_month": 0, "client_month": 0, "partner_month": 0}
    with db() as c:
        rows = c.execute("SELECT kind, created FROM link_events WHERE affiliate_id=?", (aid,)).fetchall()
    for r in rows:
        k = r["kind"]
        if k in ("open", "client", "partner"):
            out[k] += 1
            if (r["created"] or 0) >= ms:
                out[k + "_month"] += 1
    return out

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
        notify("admin", 0, f"{affiliate_label(a)} réclame {fmoney(total)} F ({n} commission(s)) — payer sur {a['momo_reseau']} {a['momo_number']}.", kind="commission", ref_aff=aid)
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

# ----------------------  TELEGRAM (alertes partenaires)  ---------------------
@app.get("/api/partenaire/telegram")
def partner_tg(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        a = c.execute("SELECT tg_chat, tg_token FROM affiliates WHERE id=?", (aid,)).fetchone()
        token = a["tg_token"] or ""
        if not token:
            token = "af" + secrets.token_urlsafe(9)
            c.execute("UPDATE affiliates SET tg_token=? WHERE id=?", (token, aid))
    user = os.getenv("NAFF_TG_BOT_USERNAME", "")
    return {"linked": bool(a["tg_chat"]), "bot": user,
            "link_url": (f"https://t.me/{user}?start={token}" if user else "")}

@app.post("/api/partenaire/telegram/unlink")
def partner_tg_unlink(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        c.execute("UPDATE affiliates SET tg_chat='' WHERE id=?", (aid,))
    return {"ok": True}

@app.get("/api/admin/telegram")
def admin_tg_status(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    token = setting_get("admin_tg_token")
    if not token:
        token = "adm" + secrets.token_urlsafe(9); setting_set("admin_tg_token", token)
    user = os.getenv("NAFF_TG_BOT_USERNAME", "")
    return {"linked": bool(admin_tg_chat()), "bot": user,
            "link_url": (f"https://t.me/{user}?start={token}" if user else "")}

@app.post("/api/admin/telegram/unlink")
def admin_tg_unlink(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    setting_set("admin_tg_chat", "")
    return {"ok": True}

@app.post("/api/telegram/webhook")
async def telegram_webhook(req: Request):
    if req.headers.get("x-telegram-bot-api-secret-token", "") != os.getenv("NAFF_TG_SECRET", "__none__"):
        return JSONResponse({"ok": False}, status_code=403)
    try:
        upd = await req.json()
    except Exception:
        return {"ok": True}
    msg = upd.get("message") or upd.get("edited_message") or {}
    chat = (msg.get("chat") or {}).get("id")
    text = (msg.get("text") or "").strip()
    if not chat:
        return {"ok": True}
    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        token = parts[1].strip() if len(parts) > 1 else ""
        # 1) lien ADMIN (Mongazi) ?
        if token and token == (setting_get("admin_tg_token") or "__none__"):
            setting_set("admin_tg_chat", str(chat))
            tg_send(chat, "✅ Telegram lié à ton cockpit NEBULA Agency, Mongazi !\n\nTu recevras ici en temps réel : nouveaux clients (site + réseau), ventes, commissions et paiements.")
            return {"ok": True}
        a = None
        if token:
            with db() as c:
                a = c.execute("SELECT * FROM affiliates WHERE tg_token=? AND actif=1", (token,)).fetchone()
                if a:
                    c.execute("UPDATE affiliates SET tg_chat=? WHERE id=?", (str(chat), a["id"]))
        if a:
            tg_send(chat, f"✅ Telegram lié à ton compte NEBULA, {affiliate_label(a)} !\n\nTu recevras ici tes alertes en temps réel : nouveaux clients, ventes, commissions, validations. À très vite !")
        else:
            tg_send(chat, "Bonjour 👋 Ce lien d'activation n'est pas valide. Ouvre ton espace NEBULA partenaire → « Alertes Telegram » et clique sur le bouton de liaison.")
    else:
        tg_send(chat, "Bonjour 👋 Je suis l'assistant d'alertes NEBULA. Pour recevoir tes alertes ici, ouvre ton espace partenaire → « Alertes Telegram ».")
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
        if phone_is_affiliate(c, numero, momo):
            return JSONResponse({"ok": False, "error": "Ce numéro est déjà partenaire NEBULA. Connecte-toi à ton espace partenaire — inutile de candidater à nouveau."}, status_code=409)
        if phone_is_pending(c, numero, momo):
            return JSONResponse({"ok": False, "error": "Une candidature avec ce numéro est déjà en cours de validation. Patiente, NEBULA revient vers toi."}, status_code=409)
        c.execute("""INSERT INTO candidatures(nom,prenom,email,numero,ville,momo_number,momo_reseau,
                     experience,motivation,canaux,parrain_code,terms_version,accepted_at,ip,status,created)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'pending', ?)""",
                  (nom, prenom, email, numero, ville, momo, reseau, exp, motiv, canaux, parrain,
                   TERMS_VERSION, time.time(), ip, time.time()))
    who = (prenom + " " + nom).strip()
    notify("admin", 0, f"Nouvelle candidature partenaire : {who} ({numero}){' · ville ' + ville if ville else ''} — CGU v{TERMS_VERSION} acceptées.", kind="recrue")
    tg_admin(f"🔔 NEBULA Affiliés — nouvelle candidature partenaire : {who} ({numero}).")
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
        if phone_is_affiliate(c, r["numero"], r["momo_number"]):
            c.execute("UPDATE candidatures SET status='rejected' WHERE id=?", (cid,))   # doublon : pas de 2e compte
            return JSONResponse({"ok": False, "error": "Ce numéro est déjà un partenaire actif — doublon évité, la candidature a été archivée."}, status_code=409)
        parrain_id = 0; parrain_name = None
        if r["parrain_code"]:
            p = c.execute("SELECT id,nom,prenom FROM affiliates WHERE code=? AND actif=1", (r["parrain_code"],)).fetchone()
            if p:
                parrain_id = p["id"]; parrain_name = (str(p["prenom"] or "") + " " + str(p["nom"] or "")).strip() or None
        pin = "".join(secrets.choice("0123456789") for _ in range(4))
        code = new_code(c)
        email = clean(r["email"], 120)
        c.execute("""INSERT INTO affiliates(code,nom,prenom,momo_number,momo_reseau,pin,accent,actif,created,parrain_id,email)
                     VALUES(?,?,?,?,?,?,?,1,?,?,?)""",
                  (code, r["nom"], r["prenom"], r["momo_number"], r["momo_reseau"], hash_pw(pin), "#7b5cff", time.time(), parrain_id, email))
        c.execute("UPDATE candidatures SET status='approved' WHERE id=?", (cid,))
        if parrain_id:
            who = (str(r["prenom"] or "") + " " + str(r["nom"] or "")).strip()
            notify("affiliate", parrain_id, f"Ta recrue {who} est validée — elle rejoint ton réseau (N1).", kind="recrue", ref_aff=parrain_id)
    name = (str(r["prenom"] or "") + " " + str(r["nom"] or "")).strip() or code
    sent = send_access_email(email, name, code, pin, parrain_name) if email else {"ok": False}
    return {"ok": True, "code": code, "pin": pin, "email": email, "email_sent": bool(sent.get("ok"))}

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
        ids = [r["id"] for r in c.execute("SELECT id FROM affiliates WHERE actif=1").fetchall()]
    tlabel = PUB_TYPES.get(ptype, "Contenu")
    for aid in ids:
        notify("affiliate", aid, f"Nouveau contenu à partager — {tlabel} : « {title} ». Disponible dans l'onglet Publication.", kind="publication")
    return {"ok": True, "id": new_id, "notified": len(ids)}

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
        "uid": "admin", "name": FOUNDER_NAME, "role": "admin", "role_label": "CEO",
        "accent": "#e6c34c", "photo": photo_url("admin"), "sub": FOUNDER_TITLE + " · NEBULA Agency"}}
    for a in affs:
        uid = "a" + str(a["id"])
        arole = (a["role"] or "").strip().lower() if "role" in a.keys() else ""
        out[uid] = {"uid": uid, "name": affiliate_label(a), "role": "affiliate",
                    "role_label": ROLE_LABELS.get(arole, ""),
                    "accent": a["accent"] or "#7b5cff", "photo": photo_url(uid),
                    "sub": rank_for(team_cumul_count(a["id"]))["label"], "aid": a["id"], "code": a["code"]}
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
            "role": s["role"], "role_label": s["role_label"], "is_supervisor": s["is_supervisor"],
            "ventes": s["ventes"], "ventes_mois": s["ventes_mois"], "ventes_rank": s["ventes_rank"], "score": s["score"],
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
        extra = {}
        if info.get("aid"):
            s = stats_of(info["aid"])
            extra = {"rank": s["rank"]["label"], "palier": s["palier"]["label"], "ventes": s["ventes"]}
        contacts.append({**info, **extra, "unread": unread, "last": (last["text"] if last else ""), "last_at": (last["created"] if last else 0)})
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
            top = c.execute("SELECT id,kind,text FROM notifs WHERE target_role='admin' AND lu=0 ORDER BY id DESC LIMIT 1").fetchone()
    else:
        aid = int(me[1:])
        with db() as c:
            nun = c.execute("SELECT COUNT(*) n FROM notifs WHERE target_role='affiliate' AND target_id=? AND lu=0", (aid,)).fetchone()["n"]
            top = c.execute("SELECT id,kind,text FROM notifs WHERE target_role='affiliate' AND target_id=? AND lu=0 ORDER BY id DESC LIMIT 1", (aid,)).fetchone()
    return {"notif_unread": nun, "notif_top": (dict(top) if top else None),
            "chat_unread": chat_unread_total(me), "ts": time.time()}

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

# ===========================  ASSISTANT PUBLIC « NEBULA AGENCY »  ============
# Cerveau propre : répond AU NOM de NEBULA Agency aux questions des visiteurs.
# Persona = NEBULA Agency (on ne met pas en avant que c'est une IA). Branché sur
# le hub public ET dans chaque back-office affilié.
def agency_brain() -> str:
    cat = "\n".join(f"- {v['label']} : {fmoney(v['price'])} FCFA"
                    for k, v in SERVICES.items() if k != "autre" and v.get("price"))
    return (
        "Tu es l'assistant officiel de NEBULA Agency. Tu réponds AU NOM de NEBULA Agency "
        "(dis « nous », « chez NEBULA »). Style : français, chaleureux, professionnel, clair, CONCIS, sans emoji. "
        "Ton rôle : répondre à toutes les questions des visiteurs sur NEBULA Agency, nos services, nos prix, "
        "nos délais, et les guider vers la prise de contact.\n\n"
        "QUI NOUS SOMMES : NEBULA Agency, agence digitale à Cotonou (Bénin), au service de l'Afrique de l'Ouest "
        "francophone. Mission : donner aux commerçants et entrepreneurs une présence digitale professionnelle "
        "(vitrines / sites, catalogues, QR codes) et de l'automatisation par intelligence artificielle, "
        "livrée vite et clé en main.\n\n"
        f"NOS OFFRES & PRIX :\n{cat}\n"
        "- Avatar IA : un assistant qui répond automatiquement aux clients (devis selon les besoins).\n\n"
        "DÉLAI : une vitrine est livrée en 5 à 7 jours en moyenne.\n"
        f"CONTACT / COMMANDER : par WhatsApp au {WHATSAPP}. Invite le visiteur à nous écrire sur WhatsApp pour "
        "démarrer un projet ou obtenir un devis précis.\n\n"
        "RÈGLES STRICTES :\n"
        "- Reste TOUJOURS sur NEBULA Agency et nos services ; si on te pose une question hors sujet, ramène "
        "poliment vers ce que NEBULA peut apporter.\n"
        "- N'invente JAMAIS de prix ni de promesses : utilise seulement les infos ci-dessus ; sinon propose un "
        "devis sur WhatsApp.\n"
        "- Tu te présentes comme « l'assistant de NEBULA Agency ». Inutile de parler de technologie. Si on te "
        "demande explicitement si tu es un robot, réponds simplement que tu es l'assistant virtuel de NEBULA "
        "Agency, là pour aider — sans en faire un sujet et sans prétendre être un humain.\n"
        "- Réponses courtes (2 à 6 phrases), concrètes, et termine souvent par une invitation à passer à "
        "l'action (devis WhatsApp, choisir une offre)."
    )

async def agency_reply(messages: List[dict]) -> str:
    key = anthropic_key()
    if key:
        try:
            async with httpx.AsyncClient(timeout=45) as cli:
                r = await cli.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                             "content-type": "application/json"},
                    json={"model": BRAIN_MODEL, "max_tokens": 600, "system": agency_brain(), "messages": messages})
            if r.status_code == 200:
                data = r.json()
                txt = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
                if txt:
                    return txt
        except Exception:
            pass
    return ("Merci pour votre message ! Pour une réponse précise et rapide, écrivez-nous directement sur "
            f"WhatsApp au {WHATSAPP} — l'équipe NEBULA Agency vous répond avec plaisir.")

_AGENCY_HITS: Dict[str, list] = {}
AGENCY_WINDOW = 900    # 15 min
AGENCY_MAX = 30        # messages max / fenêtre / IP (anti-abus & coûts)

@app.post("/api/agency-chat")
async def agency_chat(req: Request):
    ip = _client_ip(req)
    now = time.time()
    hits = [t for t in _AGENCY_HITS.get(ip, []) if now - t < AGENCY_WINDOW]
    if len(hits) >= AGENCY_MAX:
        return JSONResponse({"ok": False, "reply": "Beaucoup de questions d'un coup ! Réessayez dans quelques "
                             f"minutes, ou écrivez-nous directement sur WhatsApp au {WHATSAPP}."}, status_code=429)
    hits.append(now); _AGENCY_HITS[ip] = hits
    try:
        d = await req.json()
    except Exception:
        d = {}
    raw = d.get("messages") or []
    msgs: List[dict] = []
    for m in raw[-8:]:
        role = "assistant" if m.get("role") == "assistant" else "user"
        content = clean(m.get("content"), 1000)
        if content:
            msgs.append({"role": role, "content": content})
    while msgs and msgs[0]["role"] != "user":
        msgs = msgs[1:]
    if not msgs:
        msgs = [{"role": "user", "content": "Bonjour"}]
    reply = await agency_reply(msgs)
    try:
        with db() as c:
            c.execute("INSERT INTO agency_chats(ip,question,answer,created) VALUES(?,?,?,?)",
                      (ip, msgs[-1]["content"][:500], reply[:2000], now))
    except Exception:
        pass
    return {"ok": True, "reply": reply}

@app.get("/api/admin/agency-chats")
def admin_agency_chats(naff_session: Optional[str] = Cookie(default=None)):
    if not need_admin(naff_session):
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT id,question,answer,created FROM agency_chats ORDER BY id DESC LIMIT 200").fetchall()
        total = c.execute("SELECT COUNT(*) n FROM agency_chats").fetchone()["n"]
    return {"total": total, "chats": [dict(r) for r in rows]}

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
