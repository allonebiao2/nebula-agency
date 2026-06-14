# -*- coding: utf-8 -*-
"""
NEXO — orchestrateur d'automatisations « pur Afrique »
======================================================
Backend FastAPI. Vague 2 : moteur d'exécution RÉEL (HTTP/IA/webhooks).
Vague 3 : comptes utilisateurs + multi-tenant (SQLite) — chacun gère
ses propres automatisations en ligne, avec ses propres webhooks.

Lancement :  uvicorn server:app --port 8770
Sert aussi l'éditeur (index.html) à la racine → même origine.
"""
import os, json, asyncio, time, pathlib, sqlite3, hmac, hashlib, base64, secrets
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

HERE = pathlib.Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
load_dotenv(HERE.parent / "boutique-ia" / ".env", override=False)   # repli clés (démo)

DATA_DIR = pathlib.Path(os.getenv("NEXO_DATA_DIR", str(HERE)))   # volume persistant en prod
DATA_DIR.mkdir(parents=True, exist_ok=True)
DBF = DATA_DIR / "nexo.db"
DATA = DATA_DIR / "data_store.json"       # brique « Enregistrer »
SECRET_FILE = DATA_DIR / "secret.key"
if SECRET_FILE.exists():
    SECRET = SECRET_FILE.read_bytes()
else:
    SECRET = secrets.token_bytes(32); SECRET_FILE.write_bytes(SECRET)
COOKIE = "nexo_session"

app = FastAPI(title="NEXO Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

# ----------------------------------------------------------------------------
# Base de données (SQLite, multi-tenant)
# ----------------------------------------------------------------------------
def db():
    c = sqlite3.connect(DBF)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
            name TEXT, pass TEXT NOT NULL, created REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS workflows(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            name TEXT, graph TEXT, hook TEXT, deployed INTEGER DEFAULT 0, updated REAL)""")
init_db()

def migrate():
    with db() as c:
        for col, ddl in [("plan", "TEXT DEFAULT 'gratuit'"), ("period_end", "REAL"), ("momo_ref", "TEXT")]:
            try:
                c.execute(f"ALTER TABLE users ADD COLUMN {col} {ddl}")
            except Exception:
                pass
migrate()

# ---- Forfaits (facturation Mobile Money — modèle direct, comme Vendora) ----
PLANS = {
    "gratuit": {"label": "Gratuit", "max_workflows": 2, "deploy": False, "price": 0},
    "pro":     {"label": "Pro",     "max_workflows": 9999, "deploy": True, "price": 5000},
}
MOMO_NUMBER = os.getenv("NEXO_MOMO_NUMBER", "0196740732")
MOMO_NAME = os.getenv("NEXO_MOMO_NAME", "BIAO Mongazi Yan Karl")
ADMIN_TOKEN = os.getenv("NEXO_ADMIN_TOKEN", "nexo-admin")
# Comptes FONDATEUR (Mongazi) : accès illimité gratuit, jamais facturés.
OWNERS = set(e.strip().lower() for e in os.getenv(
    "NEXO_OWNERS", "allonebiao@gmail.com,allonebiao2@gmail.com,mongazi@nebula-agency.online").split(",") if e.strip())

def is_owner(u) -> bool:
    try:
        return (u["email"] or "").lower() in OWNERS
    except Exception:
        return False

def plan_of(u) -> str:
    if is_owner(u):
        return "pro"           # fondateur = illimité, sans paiement
    try:
        plan = u["plan"] or "gratuit"
    except Exception:
        plan = "gratuit"
    try:
        pe = u["period_end"]
    except Exception:
        pe = None
    if plan == "pro" and pe and pe < time.time():
        return "gratuit"
    return plan

# ---- Mots de passe ----
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

# ---- Sessions (cookie signé HMAC) ----
def make_token(uid: int) -> str:
    body = f"{uid}.{int(time.time()) + 60*60*24*30}".encode()          # 30 jours
    sig = hmac.new(SECRET, body, hashlib.sha256).digest()[:16]
    return base64.urlsafe_b64encode(body + b"." + sig).decode()

def read_token(tok: str) -> Optional[int]:
    try:
        raw = base64.urlsafe_b64decode(tok.encode())
        body, sig = raw.rsplit(b".", 1)
        if not hmac.compare_digest(hmac.new(SECRET, body, hashlib.sha256).digest()[:16], sig):
            return None
        uid_s, exp_s = body.decode().split(".")
        if int(exp_s) < time.time():
            return None
        return int(uid_s)
    except Exception:
        return None

def current_user(request: Request) -> Optional[sqlite3.Row]:
    tok = request.cookies.get(COOKIE)
    if not tok:
        return None
    uid = read_token(tok)
    if not uid:
        return None
    with db() as c:
        return c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

# ----------------------------------------------------------------------------
# Connecteurs réels (inchangés depuis la V2)
# ----------------------------------------------------------------------------
def _anthropic():
    key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except Exception:
        return None

async def claude_reply(consigne: str, message: str) -> str:
    cli = _anthropic()
    if not cli:
        return "(IA simulée — aucune clé Anthropic) réponse à : " + (message or "(test)")[:80]
    model = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    prompt = f"{consigne or 'Réponds au client de façon utile et brève.'}\n\nMessage du client : {message or '(message de test)'}"
    def _call():
        m = cli.messages.create(model=model, max_tokens=300, messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in m.content if getattr(b, "type", "") == "text").strip()
    try:
        return await asyncio.to_thread(_call)
    except Exception as e:  # noqa: BLE001
        return f"(erreur IA : {e})"

async def send_email(to: str, subject: str, body: str):
    key = os.getenv("RESEND_API_KEY"); frm = os.getenv("EMAIL_FROM_ADDRESS", "onboarding@resend.dev")
    if not key:
        return None, "clé Resend absente"
    try:
        async with httpx.AsyncClient(timeout=15) as cli:
            r = await cli.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {key}"},
                               json={"from": frm, "to": [to], "subject": subject or "(sans objet)", "text": body or ""})
        data = r.json()
        return data.get("id"), (None if r.status_code < 300 else str(data))
    except Exception as e:  # noqa: BLE001
        return None, str(e)

def store_append(table: str, row: Dict[str, Any]):
    try:
        d = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {}
    except Exception:
        d = {}
    d.setdefault(table or "data", []).append({"t": time.time(), **{k: str(v)[:200] for k, v in row.items()}})
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(d[table or "data"])

# ----------------------------------------------------------------------------
# Moteur d'exécution (inchangé)
# ----------------------------------------------------------------------------
LABELS = {
    "trigger-whatsapp": "Message WhatsApp reçu", "trigger-webhook": "Webhook",
    "trigger-facebook": "Prospect Facebook / Messenger",
    "trigger-schedule": "Planifié", "trigger-form": "Formulaire envoyé",
    "action-whatsapp": "Envoyer un WhatsApp", "action-email": "Envoyer un email",
    "action-momo": "Encaisser Mobile Money", "action-ai": "Demander à l'IA (Claude)",
    "action-http": "Appel HTTP / API", "action-db": "Enregistrer (base de données)",
    "action-vendora": "Action Vendora", "logic-if": "Condition (Si / Sinon)",
    "logic-delay": "Attendre (délai)",
}

def _interp(text: str, ctx: Dict[str, Any]) -> str:
    if not text:
        return text
    for k, v in ctx.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text

async def exec_node(node: Dict[str, Any], ctx: Dict[str, Any], log: List[Dict]):
    t = node.get("type", ""); p = node.get("p", {}) or {}; nid = node.get("id"); label = LABELS.get(t, t)
    if t.startswith("trigger"):
        log.append({"cls": "info", "msg": "◆ Déclencheur : " + label, "node": nid})
        if t == "trigger-whatsapp" and not ctx.get("message"):
            ctx["message"] = "Bonjour, je voudrais commander 2 articles."
        return
    log.append({"cls": "run", "msg": "● " + label, "node": nid})
    try:
        if t == "action-http":
            method = (p.get("methode") or "GET").upper(); url = _interp(p.get("url", ""), ctx)
            if not url:
                log.append({"cls": "info", "msg": "   ⚠ URL manquante", "node": nid}); return
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as cli:
                r = await cli.request(method, url)
            ctx["http"] = r.text[:800]; ctx["http_status"] = r.status_code
            log.append({"cls": "ok", "msg": f"   → HTTP {r.status_code} · {len(r.text)} octets reçus", "node": nid})
        elif t == "action-ai":
            reply = await claude_reply(p.get("consigne", ""), ctx.get("message", "") or ctx.get("http", ""))
            ctx["ia"] = reply
            log.append({"cls": "ok", "msg": "   → IA : " + reply[:160].replace("\n", " "), "node": nid})
        elif t == "action-whatsapp":
            msg = _interp(p.get("message", ""), ctx)
            log.append({"cls": "ok", "msg": "   → WhatsApp prêt : « " + (msg[:90] or "(vide)") +
                        " »  (brancher Twilio/Meta pour l'envoi réel)", "node": nid})
        elif t == "action-email":
            to = _interp(p.get("a", ""), ctx); subj = _interp(p.get("objet", ""), ctx)
            mid, err = await send_email(to, subj, ctx.get("ia", "") or "Message automatique NEXO.")
            log.append({"cls": "ok" if mid else "info",
                        "msg": (f"   → Email envoyé à {to} (id {mid[:10]}…)" if mid else f"   → Email simulé pour {to or '?'} ({err})"),
                        "node": nid})
        elif t == "action-momo":
            log.append({"cls": "ok", "msg": f"   → Demande de paiement {p.get('montant','?')} FCFA vers {p.get('numero','?')} enregistrée", "node": nid})
        elif t == "action-db":
            n = store_append(p.get("table", "data"), {"ia": ctx.get("ia", ""), "message": ctx.get("message", ""), "http_status": ctx.get("http_status", "")})
            log.append({"cls": "ok", "msg": f"   → Enregistré dans « {p.get('table','data')} » ({n} lignes)", "node": nid})
        elif t == "action-vendora":
            log.append({"cls": "ok", "msg": "   → Action Vendora : " + (p.get("action", "") or "—"), "node": nid})
        elif t == "logic-if":
            log.append({"cls": "ok", "msg": f"   → Condition « {p.get('condition','')} » → branche OUI", "node": nid})
        elif t == "logic-delay":
            await asyncio.sleep(1.0)
            log.append({"cls": "ok", "msg": f"   → Reprise après délai ({p.get('duree','')})", "node": nid})
        else:
            log.append({"cls": "info", "msg": "   (bloc non exécutable)", "node": nid})
    except Exception as e:  # noqa: BLE001
        log.append({"cls": "err", "msg": f"   ✕ Erreur : {e}", "node": nid})

async def run_graph(graph: Dict[str, Any], start_id: Optional[str] = None, trigger_input: Optional[str] = None) -> List[Dict]:
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    adj: Dict[str, List[Dict]] = {}
    for c in graph.get("conns", []):
        adj.setdefault(c["from"], []).append(c)
    log: List[Dict] = []; ctx: Dict[str, Any] = {"message": trigger_input or ""}
    starts = [start_id] if start_id else [n["id"] for n in graph.get("nodes", []) if n.get("type", "").startswith("trigger")]
    if not starts:
        log.append({"cls": "info", "msg": "⚠ Aucun déclencheur : ajoute par ex. « Message WhatsApp reçu »."}); return log
    log.append({"cls": "info", "msg": "▶ Exécution réelle sur le moteur NEXO…"})
    seen = set(); steps = {"n": 0}
    async def walk(nid: str):
        if nid in seen or steps["n"] > 60:
            return
        seen.add(nid); steps["n"] += 1
        node = nodes.get(nid)
        if not node:
            return
        await exec_node(node, ctx, log)
        outs = adj.get(nid, [])
        if node.get("type") == "logic-if":
            outs = [c for c in outs if c.get("fromPort", "oui") == "oui"] or outs
        for c in outs:
            await walk(c["to"])
    for s in starts:
        await walk(s)
    log.append({"cls": "end", "msg": "✓ Flux terminé."})
    return log

# ----------------------------------------------------------------------------
# API — Auth
# ----------------------------------------------------------------------------
def _user_json(u): return {"id": u["id"], "email": u["email"], "name": u["name"], "plan": plan_of(u)}

@app.post("/api/signup")
async def signup(req: Request):
    b = await req.json()
    email = (b.get("email") or "").strip().lower(); pw = b.get("password") or ""; name = (b.get("name") or "").strip()
    if "@" not in email or len(pw) < 4:
        return JSONResponse({"error": "Email valide et mot de passe (4+ caractères) requis."}, status_code=400)
    with db() as c:
        if c.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            return JSONResponse({"error": "Un compte existe déjà avec cet email."}, status_code=409)
        cur = c.execute("INSERT INTO users(email,name,pass,created) VALUES(?,?,?,?)",
                        (email, name or email.split("@")[0], hash_pw(pw), time.time()))
        uid = cur.lastrowid
        u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    resp = JSONResponse(_user_json(u))
    resp.set_cookie(COOKIE, make_token(uid), httponly=True, samesite="lax", max_age=60*60*24*30, path="/")
    return resp

@app.post("/api/login")
async def login(req: Request):
    b = await req.json(); email = (b.get("email") or "").strip().lower(); pw = b.get("password") or ""
    with db() as c:
        u = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not u or not check_pw(pw, u["pass"]):
        return JSONResponse({"error": "Email ou mot de passe incorrect."}, status_code=401)
    resp = JSONResponse(_user_json(u))
    resp.set_cookie(COOKIE, make_token(u["id"]), httponly=True, samesite="lax", max_age=60*60*24*30, path="/")
    return resp

@app.post("/api/logout")
async def logout():
    resp = JSONResponse({"ok": True}); resp.delete_cookie(COOKIE, path="/"); return resp

@app.get("/api/me")
async def me(request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    return _user_json(u)

# ----------------------------------------------------------------------------
# API — Workflows (multi-tenant)
# ----------------------------------------------------------------------------
def _has_webhook(graph_str):
    try:
        g = json.loads(graph_str or "{}")
        return any(n.get("type") == "trigger-webhook" for n in g.get("nodes", []))
    except Exception:
        return False

@app.get("/api/workflows")
async def list_wf(request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT id,name,updated,deployed,graph FROM workflows WHERE user_id=? ORDER BY updated DESC", (u["id"],)).fetchall()
    return [{"id": r["id"], "name": r["name"], "updated": r["updated"], "deployed": bool(r["deployed"]),
             "webhook": _has_webhook(r["graph"])} for r in rows]

@app.post("/api/workflows")
async def create_wf(request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    b = await request.json()
    plan = plan_of(u); lim = PLANS[plan]["max_workflows"]
    with db() as c:
        n = c.execute("SELECT COUNT(*) AS n FROM workflows WHERE user_id=?", (u["id"],)).fetchone()["n"]
        if n >= lim:
            return JSONResponse({"error": f"Forfait {PLANS[plan]['label']} : limite de {lim} automatisations atteinte. Passez en Pro pour un nombre illimité.",
                                 "upgrade": True}, status_code=402)
        graph = b.get("graph") or {"nodes": [], "conns": []}
        cur = c.execute("INSERT INTO workflows(user_id,name,graph,hook,deployed,updated) VALUES(?,?,?,?,0,?)",
                        (u["id"], (b.get("name") or "Mon automatisation").strip(), json.dumps(graph),
                         secrets.token_urlsafe(9), time.time()))
        wid = cur.lastrowid
        r = c.execute("SELECT * FROM workflows WHERE id=?", (wid,)).fetchone()
    return {"id": r["id"], "name": r["name"], "hook": r["hook"], "graph": json.loads(r["graph"]), "deployed": False}

def _own_wf(c, u, wid):
    return c.execute("SELECT * FROM workflows WHERE id=? AND user_id=?", (wid, u["id"])).fetchone()

@app.get("/api/workflows/{wid}")
async def get_wf(wid: int, request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    with db() as c:
        r = _own_wf(c, u, wid)
    if not r:
        return JSONResponse({"error": "introuvable"}, status_code=404)
    return {"id": r["id"], "name": r["name"], "graph": json.loads(r["graph"] or "{}"), "hook": r["hook"], "deployed": bool(r["deployed"])}

@app.put("/api/workflows/{wid}")
async def save_wf(wid: int, request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    b = await request.json()
    with db() as c:
        r = _own_wf(c, u, wid)
        if not r:
            return JSONResponse({"error": "introuvable"}, status_code=404)
        name = b.get("name", r["name"]); graph = json.dumps(b["graph"]) if "graph" in b else r["graph"]
        c.execute("UPDATE workflows SET name=?,graph=?,updated=? WHERE id=?", (name, graph, time.time(), wid))
    return {"ok": True}

@app.delete("/api/workflows/{wid}")
async def del_wf(wid: int, request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    with db() as c:
        c.execute("DELETE FROM workflows WHERE id=? AND user_id=?", (wid, u["id"]))
    return {"ok": True}

@app.post("/api/workflows/{wid}/deploy")
async def deploy_wf(wid: int, request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    if not PLANS[plan_of(u)]["deploy"]:
        return JSONResponse({"error": "Le déploiement des webhooks (mise en ligne réelle) est réservé au forfait Pro.",
                             "upgrade": True}, status_code=402)
    b = await request.json()
    with db() as c:
        r = _own_wf(c, u, wid)
        if not r:
            return JSONResponse({"error": "introuvable"}, status_code=404)
        graph = b.get("graph") or json.loads(r["graph"] or "{}")
        c.execute("UPDATE workflows SET graph=?,deployed=1,updated=? WHERE id=?", (json.dumps(graph), time.time(), wid))
        hook = r["hook"]
    hooks = []
    for n in graph.get("nodes", []):
        if n.get("type") == "trigger-webhook":
            ch = (n.get("p", {}).get("chemin") or "/webhook").strip()
            if not ch.startswith("/"):
                ch = "/" + ch
            hooks.append(f"/api/hook/{hook}{ch}")
    return {"ok": True, "hooks": hooks, "nodes": len(graph.get("nodes", []))}

# Exécution de test (le front envoie le graphe en cours)
@app.post("/api/run")
async def api_run(req: Request):
    graph = await req.json()
    return {"ok": True, "log": await run_graph(graph)}

# Webhook RÉEL par workflow (token unique)
@app.api_route("/api/hook/{token}/{path:path}", methods=["GET", "POST"])
async def api_hook(token: str, path: str, req: Request):
    with db() as c:
        r = c.execute("SELECT * FROM workflows WHERE hook=? AND deployed=1", (token,)).fetchone()
    if not r:
        return JSONResponse({"ok": False, "error": "Webhook inconnu ou workflow non déployé."}, status_code=404)
    graph = json.loads(r["graph"] or "{}"); want = "/" + path; start = None
    for n in graph.get("nodes", []):
        if n.get("type") == "trigger-webhook":
            ch = (n.get("p", {}).get("chemin") or "/webhook").strip()
            if not ch.startswith("/"):
                ch = "/" + ch
            if ch == want:
                start = n["id"]; break
    if not start:
        return JSONResponse({"ok": False, "error": f"Aucun webhook « {want} » dans ce workflow."}, status_code=404)
    try:
        body = await req.body(); trigger_input = body.decode("utf-8")[:1000] if body else ""
    except Exception:
        trigger_input = ""
    return {"ok": True, "declenche": want, "log": await run_graph(graph, start_id=start, trigger_input=trigger_input)}

# ----------------------------------------------------------------------------
# Templates prêts à l'emploi (Vague 4)
# ----------------------------------------------------------------------------
def _chain(*steps):
    nodes = []; conns = []; prev = None; x = 70
    for i, (t, p) in enumerate(steps):
        nid = "n" + str(i + 1)
        nodes.append({"id": nid, "type": t, "x": x, "y": 160, "p": p})
        if prev:
            conns.append({"from": prev, "fromPort": "out", "to": nid})
        prev = nid; x += 250
    return {"nodes": nodes, "conns": conns}

TEMPLATES = [
    {"id": "reponse-wa", "name": "Réponse WhatsApp automatique", "icon": "whatsapp",
     "desc": "Quand un client écrit, l'IA répond et la conversation est enregistrée.",
     "graph": _chain(("trigger-whatsapp", {}), ("action-ai", {"consigne": "Réponds au client, conseille et prends la commande."}),
                     ("action-whatsapp", {"message": "{{ia}}"}), ("action-db", {"table": "conversations"}))},
    {"id": "suivi-commande", "name": "Suivi de commande", "icon": "store",
     "desc": "Webhook commande → résumé IA → enregistrement → confirmation WhatsApp.",
     "graph": _chain(("trigger-webhook", {"chemin": "/commande"}), ("action-ai", {"consigne": "Résume la commande reçue en une phrase."}),
                     ("action-db", {"table": "commandes"}), ("action-whatsapp", {"message": "Merci ! Votre commande est bien reçue."}))},
    {"id": "rappel-paiement", "name": "Rappel de paiement", "icon": "cash",
     "desc": "Chaque jour, relance par WhatsApp les clients qui doivent payer (Mobile Money).",
     "graph": _chain(("trigger-schedule", {"quand": "Chaque jour à 8h"}), ("action-ai", {"consigne": "Rédige un rappel de paiement poli et bref."}),
                     ("action-whatsapp", {"message": "{{ia}}"}))},
    {"id": "capture-prospect", "name": "Capture de prospect", "icon": "form",
     "desc": "Formulaire rempli → enregistrement du contact → email de bienvenue.",
     "graph": _chain(("trigger-form", {"nom": "Demande de devis"}), ("action-db", {"table": "prospects"}),
                     ("action-email", {"a": "{{message}}", "objet": "Merci pour votre demande"}))},
    {"id": "relance-client", "name": "Relance client silencieux", "icon": "send",
     "desc": "Recontacte un client resté sans réponse, avec un message rédigé par l'IA.",
     "graph": _chain(("trigger-schedule", {"quand": "Chaque jour à 8h"}), ("logic-if", {"condition": "le client n'a pas répondu depuis 2 jours"}),
                     ("action-ai", {"consigne": "Rédige une relance amicale et courte."}), ("action-whatsapp", {"message": "{{ia}}"}))},
]

@app.get("/api/templates")
async def list_templates():
    return [{"id": t["id"], "name": t["name"], "icon": t["icon"], "desc": t["desc"], "graph": t["graph"]} for t in TEMPLATES]

# ----------------------------------------------------------------------------
# L'IA qui CONSTRUIT l'automatisation (Vague 5) — Claude transforme une phrase FR en workflow
# ----------------------------------------------------------------------------
TYPES_SET = set(LABELS.keys())
AI_SYSTEM = (
    "Tu es l'assistant de NEXO, créateur d'automatisations pour commerçants africains. "
    "À partir d'une phrase en français, produis une automatisation en étapes ordonnées. "
    "Blocs disponibles (type → rôle [paramètres]):\n"
    "- trigger-whatsapp : démarre à la réception d'un message WhatsApp\n"
    "- trigger-webhook : démarre quand une URL est appelée [chemin]\n"
    "- trigger-facebook : démarre quand un nouveau prospect arrive de Facebook ou Messenger\n"
    "- trigger-schedule : démarre à une heure planifiée [quand]\n"
    "- trigger-form : démarre quand un formulaire est envoyé [nom]\n"
    "- action-ai : génère une réponse intelligente [consigne]\n"
    "- action-whatsapp : envoie un WhatsApp [message] (utilise {{ia}} pour insérer la réponse de l'IA)\n"
    "- action-email : envoie un email [a, objet]\n"
    "- action-momo : encaisse en Mobile Money [montant, numero]\n"
    "- action-db : enregistre en base [table]\n"
    "- action-http : appelle une API [methode, url]\n"
    "- action-vendora : action dans Vendora [action]\n"
    "- logic-if : condition [condition]\n"
    "- logic-delay : attendre un délai [duree]\n"
    "RÈGLES : la 1re étape DOIT être un déclencheur (trigger-*). Paramètres pertinents en français. "
    'Réponds UNIQUEMENT par du JSON valide, sans texte autour : {"steps":[{"type":"...","p":{...}}, ...]}'
)

async def ai_build_graph(prompt: str) -> Dict[str, Any]:
    cli = _anthropic()
    if not cli:
        raise ValueError("IA indisponible (clé Anthropic absente)")
    model = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    def _call():
        m = cli.messages.create(model=model, max_tokens=700, system=AI_SYSTEM,
                                messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in m.content if getattr(b, "type", "") == "text").strip()
    txt = await asyncio.to_thread(_call)
    s = txt.find("{"); e = txt.rfind("}")
    if s < 0 or e < 0:
        raise ValueError("réponse IA illisible")
    data = json.loads(txt[s:e + 1])
    nodes = []; conns = []; prev = None; x = 70
    for i, st in enumerate(data.get("steps", [])):
        t = st.get("type")
        if t not in TYPES_SET:
            continue
        nid = "n" + str(i + 1)
        nodes.append({"id": nid, "type": t, "x": x, "y": 160, "p": st.get("p", {}) or {}})
        if prev:
            conns.append({"from": prev, "fromPort": "out", "to": nid})
        prev = nid; x += 250
    if not nodes:
        raise ValueError("aucune étape valide générée")
    return {"nodes": nodes, "conns": conns}

@app.post("/api/ai-build")
async def ai_build(request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    b = await request.json(); prompt = (b.get("prompt") or "").strip()
    if not prompt:
        return JSONResponse({"error": "phrase vide"}, status_code=400)
    try:
        return {"ok": True, "graph": await ai_build_graph(prompt)}
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)

# ----------------------------------------------------------------------------
# Facturation (Mobile Money direct)
# ----------------------------------------------------------------------------
@app.get("/api/billing")
async def billing(request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    plan = plan_of(u)
    try:
        pe = u["period_end"] if plan == "pro" else None
    except Exception:
        pe = None
    try:
        ref = u["momo_ref"]
    except Exception:
        ref = None
    label = "Fondateur" if is_owner(u) else PLANS[plan]["label"]
    return {"plan": plan, "label": label, "max_workflows": PLANS[plan]["max_workflows"],
            "deploy": PLANS[plan]["deploy"], "price": PLANS["pro"]["price"], "momo_number": MOMO_NUMBER,
            "momo_name": MOMO_NAME, "period_end": pe, "pending": bool(ref) and plan != "pro"}

@app.post("/api/billing/request")
async def billing_request(request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "non connecté"}, status_code=401)
    b = await request.json(); ref = (b.get("ref") or "").strip()
    if not ref:
        return JSONResponse({"error": "Indiquez l'ID de la transaction Mobile Money."}, status_code=400)
    with db() as c:
        c.execute("UPDATE users SET momo_ref=? WHERE id=?", (ref, u["id"]))
    return {"ok": True, "message": "Paiement enregistré, en attente de validation. Votre forfait Pro sera activé sous peu."}

@app.post("/api/admin/activate")
async def admin_activate(request: Request):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        return JSONResponse({"error": "non autorisé"}, status_code=401)
    b = await request.json(); email = (b.get("email") or "").strip().lower()
    with db() as c:
        u = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not u:
            return JSONResponse({"error": "utilisateur introuvable"}, status_code=404)
        c.execute("UPDATE users SET plan='pro', period_end=?, momo_ref=NULL WHERE id=?", (time.time() + 30 * 86400, u["id"]))
    return {"ok": True, "email": email, "plan": "pro"}

@app.get("/api/admin/pending")
async def admin_pending(request: Request):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        return JSONResponse({"error": "non autorisé"}, status_code=401)
    with db() as c:
        rows = c.execute("SELECT email,name,momo_ref FROM users WHERE momo_ref IS NOT NULL AND momo_ref!=''").fetchall()
    return [{"email": r["email"], "name": r["name"], "ref": r["momo_ref"]} for r in rows]

@app.get("/api/health")
async def health():
    return {"ok": True, "ia": bool(_anthropic()), "email": bool(os.getenv("RESEND_API_KEY"))}

@app.get("/", response_class=HTMLResponse)
async def landing():
    return (HERE / "landing.html").read_text(encoding="utf-8")

@app.get("/app", response_class=HTMLResponse)
async def app_ui():
    return (HERE / "index.html").read_text(encoding="utf-8")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8770")))
