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
import os, json, time, pathlib, sqlite3, hmac, hashlib, base64, secrets, re, threading
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import FastAPI, Request, Response, Cookie
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

# ---- Rangs (paliers « jeu vidéo », selon le nb de clients ramenés) ----
RANKS: List[Tuple[int, str, str]] = [
    (0,  "Recrue",  "🌱"),
    (1,  "Bronze",  "🥉"),
    (3,  "Argent",  "🥈"),
    (6,  "Or",      "🥇"),
    (10, "Platine", "🔷"),
    (20, "Diamant", "💎"),
    (40, "Légende", "👑"),
]
# Réseaux Mobile Money du Bénin
RESEAUX = ["MTN MoMo", "Moov Money", "Celtiis Cash"]

# ----------------------------------------------------------------------------
# Base de données (SQLite — mémoire persistante, tout interconnecté)
# ----------------------------------------------------------------------------
def db():
    c = sqlite3.connect(DBF, timeout=30)
    c.row_factory = sqlite3.Row
    return c

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
init_db()

def migrate():
    with db() as c:
        for col, ddl in [("pseudo", "TEXT DEFAULT ''")]:
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

def commission_of(service: str, montant: float) -> int:
    base = montant if montant and montant > 0 else SERVICES.get(service, {}).get("price", 0)
    return int(round(base * COMMISSION_RATE))

def stats_of(affiliate_id: int) -> Dict[str, Any]:
    with db() as c:
        rows = c.execute("SELECT * FROM leads WHERE affiliate_id=?", (affiliate_id,)).fetchall()
    by_status = {k: 0 for k in STATUSES}
    score = 0; rcm = 0; potentiel = 0; nb_real = 0
    for r in rows:
        st = r["status"] or "attente"
        by_status[st] = by_status.get(st, 0) + 1
        score += STATUS_POINTS.get(st, 0)
        if r["paye"]:
            score += PAID_BONUS
        if st != "annule":
            nb_real += 1
        com = commission_of(r["service"], r["montant"])
        if r["paye"]:
            rcm += com
        elif st != "annule":
            potentiel += com
    rk = rank_for(nb_real)
    return {
        "nb_total": len(rows), "nb_real": nb_real, "by_status": by_status,
        "score": score, "rcm": rcm, "potentiel": potentiel, "rank": rk,
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
    notify("admin", 0, "👋 Bienvenue dans NEBULA Affiliés — voici un affilié démo (code DEMO).")
seed()

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

# ---- Config publique (catalogue, statuts, réseaux) pour les fronts ----
@app.get("/api/config")
def api_config():
    return {
        "services": SERVICES, "statuses": STATUSES, "reseaux": RESEAUX,
        "commission_rate": COMMISSION_RATE, "momo": {"number": MOMO_NUMBER, "name": MOMO_NAME},
        "whatsapp": WHATSAPP, "ranks": [{"min": r[0], "label": r[1], "emoji": r[2]} for r in RANKS],
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
    notify("admin", 0, f"🎯 Nouveau client via {affiliate_label(a)} : {client} — {svc}", lead_id)
    notify("affiliate", a["id"], f"🎉 {client} a rempli ton formulaire — en attente de validation.", lead_id)
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
    paid = 0; ca_paye = 0; commissions = 0
    for r in leads:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        if r["paye"]:
            paid += 1
            base = r["montant"] if r["montant"] else SERVICES.get(r["service"], {}).get("price", 0)
            ca_paye += base
            commissions += commission_of(r["service"], r["montant"])
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
            "rank": s["rank"], "nb_real": s["nb_real"], "by_status": s["by_status"],
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
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "nom": r["nom"], "prenom": r["prenom"], "numero": r["numero"],
            "service": r["service"], "service_label": SERVICES.get(r["service"], {}).get("label", r["service"]),
            "message": r["message"], "status": r["status"], "paye": r["paye"],
            "commission": commission_of(r["service"], r["montant"]),
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
    notify("affiliate", r["affiliate_id"], f"🔄 {client} : statut → {STATUSES[st]['label']}", lid)
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
    if paye:
        com = commission_of(r["service"], r["montant"])
        client = (str(r["prenom"] or "") + " " + str(r["nom"] or "")).strip()
        notify("affiliate", r["affiliate_id"], f"💸 {client} : paiement reçu — commission +{com:,} F".replace(",", " "), lid)
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
        "stats": s,
    }

@app.get("/api/partenaire/leads")
def partner_leads(naff_session: Optional[str] = Cookie(default=None)):
    aid = need_affiliate(naff_session)
    if aid is None:
        return JSONResponse({"error": "auth"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT * FROM leads WHERE affiliate_id=? ORDER BY created DESC", (aid,)).fetchall()
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "nom": r["nom"], "prenom": r["prenom"], "numero": r["numero"],
            "service": r["service"], "service_label": SERVICES.get(r["service"], {}).get("label", r["service"]),
            "status": r["status"], "paye": r["paye"],
            "commission": commission_of(r["service"], r["montant"]),
            "created": r["created"], "updated": r["updated"],
        })
    return {"leads": out}

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
    s = stats_of(aid); rk = s["rank"]
    nxt = (f"Encore {rk['to_next']} client(s) pour le rang {rk['next_label']} {rk['next_emoji']}."
           if rk["next_label"] else "Rang maximum atteint, bravo.")
    cl = [f"- {(str(l['prenom'] or '')+' '+str(l['nom'] or '')).strip()} : "
          f"{SERVICES.get(l['service'], {}).get('label', l['service'])} — {STATUSES[l['status']]['label']}"
          f"{' — PAYÉ' if l['paye'] else ''}" for l in leads]
    return (f"TON PROFIL : {affiliate_label(a)} (code {a['code']}), rang {rk['label']} {rk['emoji']}, "
            f"{s['nb_real']} clients, score {s['score']}, RCM {s['rcm']} F "
            f"(commission potentielle {s['potentiel']} F). {nxt}\nTES CLIENTS :\n"
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
