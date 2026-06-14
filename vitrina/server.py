"""
Vitrina — backend léger (FastAPI + SQLite)
Flux : la cliente crée sa vitrine -> commande (paiement Mobile Money manuel)
-> notif Telegram à Mongazi -> back-office /admin -> validation -> site en ligne.
Aucune clé bancaire. Telegram optionnel (si non configuré, la commande marche quand même).
"""
import os, re, sqlite3, secrets, datetime, urllib.parse, urllib.request, hmac, hashlib
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE = os.path.dirname(os.path.abspath(__file__))

def _load_env():
    p = os.path.join(BASE, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
_load_env()

DB = os.environ.get("VITRINA_DB", os.path.join(BASE, "vitrina.db"))
ADMIN_KEY = os.environ.get("VITRINA_ADMIN_KEY", "mongazi")
TG_TOKEN  = os.environ.get("TG_TOKEN")
TG_CHAT   = os.environ.get("TG_CHAT")
BASE_URL  = os.environ.get("VITRINA_BASE_URL", "http://localhost:8090")
# Compte Mobile Money affiché à la cliente
MOMO_NAME    = os.environ.get("MOMO_NAME", "")
MOMO_NUMBER  = os.environ.get("MOMO_NUMBER", "")
MOMO_NETWORK = os.environ.get("MOMO_NETWORK", "")
PACKS = {"express": 15000, "pro": 25000, "business": 45000}

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE, pack TEXT, price INTEGER,
        biz_name TEXT, client_name TEXT, whatsapp TEXT, email TEXT, network TEXT, ref TEXT,
        html TEXT, status TEXT DEFAULT 'pending', created TEXT, expires TEXT)""")
    cols = [r["name"] for r in c.execute("PRAGMA table_info(orders)").fetchall()]
    for col in ("email", "expires"):
        if col not in cols:
            c.execute(f"ALTER TABLE orders ADD COLUMN {col} TEXT")
    c.commit(); c.close()
init()

def tg(text):
    if not TG_TOKEN or not TG_CHAT:
        print("[Telegram non configure] nouvelle notification (TG off)"); return
    try:
        data = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": text,
            "parse_mode": "HTML", "disable_web_page_preview": "true"}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data, timeout=6)
    except Exception as e:
        print("Telegram err:", e)

def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', (s or 'site').lower()).strip('-')
    return (s or 'site')[:24]

def money(n):
    return f"{n:,}".replace(",", " ") + " F"

app = FastAPI(title="Vitrina")

def _auth_token():
    return hmac.new(ADMIN_KEY.encode(), b"vitrina-admin-v1", hashlib.sha256).hexdigest()

def _is_authed(request: Request):
    return request.cookies.get("vitrina_auth") == _auth_token()

LOGIN_HTML = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Vitrina - Connexion</title>
<style>
body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#15110E;color:#fff;display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0}
.box{background:#fff;color:#15110E;padding:34px;border-radius:18px;width:320px;max-width:88%;box-shadow:0 24px 70px rgba(0,0,0,.45)}
h1{font-size:22px;margin:0 0 4px}h1 span{color:#A77E37}
p{color:#6B6157;font-size:14px;margin:0 0 20px}
input{width:100%;box-sizing:border-box;border:1.5px solid #EAE2D6;border-radius:10px;padding:12px 14px;font-size:15px;margin-bottom:14px}
button{width:100%;background:linear-gradient(135deg,#C79B4E,#A77E37);color:#fff;border:none;border-radius:999px;padding:13px;font-weight:700;font-size:15px;cursor:pointer}
.err{color:#c0392b;font-size:13px;margin-bottom:12px}
</style></head>
<body><form class="box" method="post" action="/admin/login">
<h1>Vitri<span>na</span></h1><p>Back-office - connexion</p>
%ERR%
<input type="password" name="password" placeholder="Mot de passe" autofocus>
<button>Se connecter</button></form></body></html>"""

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form():
    return HTMLResponse(LOGIN_HTML.replace("%ERR%", ""))

@app.post("/admin/login")
def admin_login(password: str = Form("")):
    if password == ADMIN_KEY:
        r = RedirectResponse("/admin", status_code=303)
        r.set_cookie("vitrina_auth", _auth_token(), httponly=True, secure=True, samesite="lax", max_age=2592000)
        return r
    return HTMLResponse(LOGIN_HTML.replace("%ERR%", "<div class='err'>Mot de passe incorrect</div>"), status_code=401)

@app.get("/admin/logout")
def admin_logout():
    r = RedirectResponse("/admin/login", status_code=303)
    r.delete_cookie("vitrina_auth")
    return r

class OrderIn(BaseModel):
    pack: str = "pro"
    biz_name: str = ""
    client_name: str = ""
    whatsapp: str = ""
    email: str = ""
    network: str = ""
    ref: str = ""
    html: str = ""

@app.get("/api/config")
def config():
    return {"momo_name": MOMO_NAME, "momo_number": MOMO_NUMBER, "momo_network": MOMO_NETWORK, "packs": PACKS}

@app.post("/api/order")
def create_order(o: OrderIn):
    price = PACKS.get(o.pack, 25000)
    slug = slugify(o.biz_name) + "-" + secrets.token_hex(2)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c = db()
    c.execute("""INSERT INTO orders(slug,pack,price,biz_name,client_name,whatsapp,email,network,ref,html,status,created)
                 VALUES(?,?,?,?,?,?,?,?,?,?, 'pending', ?)""",
              (slug, o.pack, price, o.biz_name, o.client_name, o.whatsapp, o.email, o.network, o.ref, o.html, now))
    oid = c.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    c.commit(); c.close()
    tg(f"🟡 <b>Nouvelle commande Vitrina</b>\n"
       f"Activité : {o.biz_name}\nPack : {o.pack.upper()} — {money(price)}\n"
       f"Cliente : {o.client_name} ({o.whatsapp})\nEmail : {o.email or '—'}\n"
       f"Réseau : {o.network}   Réf : {o.ref or '—'}\n\n"
       f"➡️ Ouvrir le back-office : {BASE_URL}/admin")
    return {"ok": True, "id": oid, "slug": slug}

@app.post("/api/order/{oid}/validate")
def validate(oid: int, request: Request):
    if not _is_authed(request): raise HTTPException(403)
    exp = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
    c = db(); c.execute("UPDATE orders SET status='live', expires=? WHERE id=?", (exp, oid)); c.commit(); c.close()
    return RedirectResponse("/admin", status_code=303)

@app.post("/api/order/{oid}/reject")
def reject(oid: int, request: Request):
    if not _is_authed(request): raise HTTPException(403)
    c = db(); c.execute("UPDATE orders SET status='rejected' WHERE id=?", (oid,)); c.commit(); c.close()
    return RedirectResponse("/admin", status_code=303)

@app.post("/api/order/{oid}/delete")
def delete_order(oid: int, request: Request):
    if not _is_authed(request): raise HTTPException(403)
    c = db(); c.execute("DELETE FROM orders WHERE id=?", (oid,)); c.commit(); c.close()
    return RedirectResponse("/admin", status_code=303)

@app.get("/v/{slug}", response_class=HTMLResponse)
def view(slug: str):
    c = db(); r = c.execute("SELECT * FROM orders WHERE slug=?", (slug,)).fetchone(); c.close()
    if not r: raise HTTPException(404, "Site introuvable")
    html = r["html"]
    if r["status"] != "live":
        html = ("<div style='position:fixed;top:0;left:0;right:0;background:#15110E;color:#fff;"
                "text-align:center;padding:9px;font:600 13px sans-serif;z-index:99999'>"
                "&#9203; Aper&#231;u &mdash; en attente de validation du paiement</div>") + html
    return HTMLResponse(html)

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    if not _is_authed(request):
        return RedirectResponse("/admin/login", status_code=303)
    c = db(); rows = c.execute("SELECT * FROM orders ORDER BY id DESC").fetchall(); c.close()
    total = len(rows)
    pending = sum(1 for r in rows if r["status"] == "pending")
    live = sum(1 for r in rows if r["status"] == "live")
    revenue = sum(r["price"] for r in rows if r["status"] == "live")
    cards = "".join([
        f"<div class=kpi><div class=n>{total}</div><div class=l>Commandes</div></div>",
        f"<div class=kpi><div class=n style='color:#d39a1f'>{pending}</div><div class=l>En attente</div></div>",
        f"<div class=kpi><div class=n style='color:#1f8f5c'>{live}</div><div class=l>En ligne</div></div>",
        f"<div class=kpi><div class=n>{money(revenue)}</div><div class=l>Encaiss&eacute; (valid&eacute;)</div></div>",
    ])
    trs = []
    for r in rows:
        badge = {"pending":"#d39a1f","live":"#1f8f5c","rejected":"#c0392b"}.get(r["status"], "#888")
        label = {"pending":"En attente","live":"En ligne","rejected":"Refus&eacute;"}.get(r["status"], r["status"])
        wa = re.sub(r'[^0-9]', '', r["whatsapp"] or "")
        actions = ""
        if r["status"] == "pending":
            actions = (f"<form method=post action='/api/order/{r['id']}/validate' style='display:inline'>"
                       f"<button class='b ok'>Valider le paiement</button></form> "
                       f"<form method=post action='/api/order/{r['id']}/reject' style='display:inline'>"
                       f"<button class='b no'>Refuser</button></form>")
        elif r["status"] == "live":
            msg = urllib.parse.quote(f"Bonjour {r['client_name']}, votre site est en ligne : {BASE_URL}/v/{r['slug']}")
            actions = (f"<a class='b live' target=_blank href='{BASE_URL}/v/{r['slug']}'>Voir le site</a> "
                       f"<a class='b wa' target=_blank href='https://wa.me/{wa}?text={msg}'>Pr&eacute;venir la cliente</a>")
            if r["email"]:
                esub = urllib.parse.quote("Votre site est en ligne")
                ebody = urllib.parse.quote(f"Bonjour {r['client_name']},\n\nVotre site est en ligne : {BASE_URL}/v/{r['slug']}\nMettez ce lien dans votre bio Instagram et WhatsApp.\n\nVitrina")
                actions += f" <a class='b' style='background:#555;color:#fff' target=_blank href='mailto:{r['email']}?subject={esub}&body={ebody}'>Email</a>"
        actions += f" <form method=post action='/api/order/{r['id']}/delete' style='display:inline' onsubmit='return confirm(\"Supprimer cette commande ?\")'><button class='b' style='background:#999;color:#fff'>Suppr.</button></form>"
        trs.append(
            f"<tr><td>#{r['id']}<br><small>{r['created']}</small></td>"
            f"<td><b>{r['biz_name']}</b><br><a target=_blank href='{BASE_URL}/v/{r['slug']}'>aper&ccedil;u</a></td>"
            f"<td>{r['pack'].upper()}<br><b>{money(r['price'])}</b></td>"
            f"<td>{r['client_name']}<br><small>{r['whatsapp']}</small><br><small>{r['email'] or ''}</small></td>"
            f"<td>{r['network']}<br><small>{r['ref'] or '—'}</small></td>"
            f"<td><span class=tag style='background:{badge}'>{label}</span>{('<br><small>échéance ' + r['expires'] + '</small>') if (r['status']=='live' and r['expires']) else ''}</td>"
            f"<td>{actions}</td></tr>")
    page = f"""<!DOCTYPE html><html lang=fr><head><meta charset=UTF-8>
<meta name=viewport content='width=device-width,initial-scale=1'><title>Back-office Vitrina</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#F4F0EA;color:#15110E;padding:24px}}
h1{{font-size:24px;margin-bottom:4px}}.sub{{color:#6B6157;margin-bottom:22px;font-size:14px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}}
.kpi{{background:#fff;border:1px solid #E6DFD4;border-radius:14px;padding:18px}}
.kpi .n{{font-size:26px;font-weight:700}}.kpi .l{{font-size:12px;color:#6B6157;margin-top:2px}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden;border:1px solid #E6DFD4}}
th,td{{text-align:left;padding:12px 14px;font-size:13.5px;border-bottom:1px solid #F0EAE0;vertical-align:top}}
th{{background:#FAF6F0;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#8a7d70}}
small{{color:#9a8d80}}a{{color:#A77E37}}
.tag{{color:#fff;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700}}
.b{{display:inline-block;border:none;border-radius:8px;padding:8px 12px;font-size:12.5px;font-weight:600;cursor:pointer;text-decoration:none;margin:2px 0}}
.b.ok{{background:#1f8f5c;color:#fff}}.b.no{{background:#fff;color:#c0392b;border:1px solid #e3b4ad}}
.b.live{{background:#15110E;color:#fff}}.b.wa{{background:#25D366;color:#fff}}
@media(max-width:760px){{.kpis{{grid-template-columns:repeat(2,1fr)}}table{{font-size:12px}}}}
</style></head><body>
<h1>Back-office Vitrina <a href='/admin/logout' style='float:right;font-size:13px;font-weight:400;color:#A77E37'>Se d&eacute;connecter</a></h1><div class=sub>Tu vois chaque commande ici. Valide le paiement re&ccedil;u &rarr; le site passe en ligne &rarr; pr&eacute;viens la cliente.</div>
<div class=kpis>{cards}</div>
<table><tr><th>Commande</th><th>Activit&eacute;</th><th>Pack</th><th>Cliente</th><th>Paiement</th><th>Statut</th><th>Action</th></tr>
{''.join(trs) if trs else '<tr><td colspan=7 style="padding:30px;text-align:center;color:#9a8d80">Aucune commande pour le moment.</td></tr>'}
</table></body></html>"""
    return HTMLResponse(page)

# Fichiers statiques (index.html, creer.html, exemple-beaute.html) — à la fin pour ne pas masquer les routes
app.mount("/", StaticFiles(directory=BASE, html=True), name="static")
