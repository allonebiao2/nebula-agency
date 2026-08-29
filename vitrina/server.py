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

import notify   # alertes WhatsApp + Telegram (best-effort, jamais bloquant)
import publier  # pose la page sur Cloudflare KV (aucun réveil à l'ouverture)

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
    """Alerte Mongazi sur WhatsApp ET Telegram. Ne leve jamais."""
    try:
        return notify.alerter_mongazi(text)
    except Exception as e:
        print("[notify] echec inattendu:", e)
        return {"whatsapp": False, "telegram": False}

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

def _order_token(oid: int) -> str:
    """Jeton signe propre a une commande, pour agir depuis WhatsApp sans se connecter."""
    return hmac.new(ADMIN_KEY.encode(), f"vitrina-order-{oid}".encode(), hashlib.sha256).hexdigest()[:24]

def _may_act(request: Request, oid: int, token: str = "") -> bool:
    """Autorise soit la session admin, soit le jeton signe du lien."""
    return _is_authed(request) or (bool(token) and hmac.compare_digest(token, _order_token(oid)))

def _ref_doublon(ref: str, sauf_id: int = 0) -> int:
    """Nombre d'AUTRES commandes portant deja cette reference de transaction."""
    ref = (ref or "").strip()
    if not ref:
        return 0
    c = db()
    n = c.execute("SELECT COUNT(*) AS n FROM orders WHERE TRIM(ref)=? AND id<>?",
                  (ref, sauf_id)).fetchone()["n"]
    c.close()
    return n

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

@app.get("/sante")
def sante():
    """Point de réveil. Volontairement le moins cher possible : aucune requête
    en base, aucun rendu. C'est ce que pingue .github/workflows/reveil.yml
    toutes les 10 minutes aux heures ouvrées pour que Render ne s'endorme pas.
    """
    return {"ok": True}

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
    doublons = _ref_doublon(o.ref, sauf_id=oid)
    garde = ""
    if not (o.ref or "").strip():
        # On accepte quand meme : une vente par un partenaire ou en main propre
        # n'a pas de reference. Mais ca doit sauter aux yeux.
        garde += "\n\n*AUCUNE RÉFÉRENCE FOURNIE* : vente hors ligne, ou client qui n'a pas payé."
    if doublons:
        garde = (f"\n\n*ATTENTION* : cette référence a déjà été utilisée sur "
                 f"{doublons} autre(s) commande(s). À vérifier avant de valider.")
    tg("Nouvelle commande Vitrina\n\n"
       f"Activité : {o.biz_name}\n"
       f"Pack : {o.pack.upper()} - {money(price)}\n"
       f"Cliente : {o.client_name} ({o.whatsapp})\n"
       f"Email : {o.email or '-'}\n"
       f"Réseau : {o.network}\n"
       f"Référence : {o.ref or '-'}"
       f"{garde}\n\n"
       f"Vérifie le SMS Mobile Money, PUIS ouvre :\n"
       f"{BASE_URL}/a/{oid}/{_order_token(oid)}")
    return {"ok": True, "id": oid, "slug": slug}

@app.post("/api/order/{oid}/validate")
def validate(oid: int, request: Request, token: str = Form("")):
    if not _may_act(request, oid, token): raise HTTPException(403)
    exp = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
    c = db()
    c.execute("UPDATE orders SET status='live', expires=? WHERE id=?", (exp, oid))
    c.commit()
    r = c.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
    c.close()
    if not r:
        raise HTTPException(404)

    # Des que Mongazi valide, le travail part tout seul : la page part au bord
    # du reseau, elle est en ligne, ET la cliente est prevenue. Plus aucun clic
    # apres la decision.
    #
    # La publication sur Cloudflare est ce qui garantit qu'une page ouverte a
    # minuit s'affiche tout de suite. Si elle echoue, la page reste servie par
    # ce serveur : ca marche, mais avec le reveil lent de Render. On ne le tait
    # surtout pas, on le dit dans l'alerte.
    au_bord = publier.publier(r["slug"], r["html"])
    lien = f"{BASE_URL}/v/{r['slug']}"
    envoye = False
    if r["whatsapp"]:
        envoye = notify.prevenir_client(
            r["whatsapp"],
            f"Bonjour {r['client_name']}, votre site est en ligne :\n{lien}\n\n"
            f"Mettez ce lien dans votre bio Instagram et sur WhatsApp.\n\nVitrina by NEBULA")
    tg(f"Validé : {r['biz_name']} est en ligne.\n{lien}\n\n"
       + ("Cliente prévenue automatiquement sur WhatsApp.\n"
          if envoye else
          "ATTENTION : la cliente n'a PAS pu être prévenue automatiquement. "
          "Utilise le bouton WhatsApp du back-office.\n")
       + ("Page servie par Cloudflare : elle s'ouvre instantanément."
          if au_bord else
          "ATTENTION : page NON publiée sur Cloudflare, elle est servie par "
          "Render. Premier visiteur après une pause : environ une minute "
          "d'attente."))
    return RedirectResponse(f"/a/{oid}/{_order_token(oid)}", status_code=303)

@app.post("/api/order/{oid}/reject")
def reject(oid: int, request: Request, token: str = Form("")):
    if not _may_act(request, oid, token): raise HTTPException(403)
    c = db(); c.execute("UPDATE orders SET status='rejected' WHERE id=?", (oid,)); c.commit(); c.close()
    return RedirectResponse(f"/a/{oid}/{_order_token(oid)}", status_code=303)

@app.post("/api/order/{oid}/delete")
def delete_order(oid: int, request: Request):
    if not _is_authed(request): raise HTTPException(403)
    c = db()
    r = c.execute("SELECT slug FROM orders WHERE id=?", (oid,)).fetchone()
    c.execute("DELETE FROM orders WHERE id=?", (oid,)); c.commit(); c.close()
    # ⚠️ Supprimer en base NE SUFFIT PAS : tant que la page est dans KV, le
    # bord du réseau continue de la servir. C'est ce qui rend possible le
    # retrait sous 24 h demandé par la personne visée par une page.
    if r:
        publier.retirer(r["slug"])
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

ACTION_CSS = """
*{box-sizing:border-box}
body{margin:0;background:#15110E;color:#fff;font:16px/1.55 -apple-system,Segoe UI,Roboto,Arial,sans-serif;
padding:18px;display:flex;justify-content:center}
.k{width:100%;max-width:460px}
.c{background:#fff;color:#15110E;border-radius:18px;padding:22px;box-shadow:0 24px 70px rgba(0,0,0,.45)}
h1{font-size:20px;margin:0 0 2px}h1 span{color:#A77E37}
.s{color:#6B6157;font-size:13px;margin:0 0 16px}
dl{margin:0 0 16px;display:grid;grid-template-columns:auto 1fr;gap:7px 14px;font-size:14px}
dt{color:#6B6157}dd{margin:0;font-weight:600;word-break:break-word}
.ref{font-family:ui-monospace,Menlo,Consolas,monospace;background:#F6F1E8;padding:2px 7px;border-radius:6px;display:inline-block}
.warn{background:#FDEBEA;border:1.5px solid #E5A9A2;color:#8E2A20;border-radius:12px;padding:12px 14px;font-size:14px;margin:0 0 16px}
.ok{background:#E8F5EE;border:1.5px solid #9ED2B6;color:#186B45;border-radius:12px;padding:12px 14px;font-size:14px;margin:0 0 16px}
.rappel{background:#FFF7E6;border:1.5px solid #EBCF95;color:#7A5A12;border-radius:12px;padding:12px 14px;font-size:13.5px;margin:0 0 18px}
form{margin:0 0 10px}
button{width:100%;border:none;border-radius:999px;padding:16px;font-size:16px;font-weight:700;cursor:pointer;min-height:52px}
.v{background:linear-gradient(135deg,#2E9E68,#1F8F5C);color:#fff}
.r{background:#fff;color:#C0392B;border:1.5px solid #E5B4AE}
a.lien{display:block;text-align:center;color:#A77E37;font-size:14px;margin-top:14px;text-decoration:none}
.tag{display:inline-block;padding:3px 11px;border-radius:999px;color:#fff;font-size:12px;font-weight:700}
"""

def _esc(v):
    return (str(v or "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))

@app.get("/a/{oid}/{token}", response_class=HTMLResponse)
def action_page(oid: int, token: str):
    """Fiche d'une commande, ouverte depuis WhatsApp ou Telegram.

    LECTURE SEULE. C'est deliberé : WhatsApp et Telegram vont chercher un
    apercu de chaque lien envoye. Si cette adresse validait la commande, leur
    robot la validerait tout seul avant meme que Mongazi la voie. Rien ne
    change ici ; seuls les POST ci-dessous agissent.
    """
    if not hmac.compare_digest(token, _order_token(oid)):
        raise HTTPException(403, "Lien invalide")
    c = db(); r = c.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone(); c.close()
    if not r:
        raise HTTPException(404, "Commande introuvable")

    doublons = _ref_doublon(r["ref"], sauf_id=oid)
    etat = {"pending": ("En attente", "#d39a1f"), "live": ("En ligne", "#1f8f5c"),
            "rejected": ("Refusé", "#c0392b")}.get(r["status"], (r["status"], "#888"))

    bloc = ""
    if doublons:
        bloc += (f"<div class=warn><b>Référence déjà vue.</b> Cette référence apparaît sur "
                 f"{doublons} autre(s) commande(s). Vérifie le SMS avant de valider.</div>")

    if r["status"] == "pending":
        bloc += ("<div class=rappel><b>Avant de valider :</b> ouvre ton SMS Mobile Money et "
                 "vérifie que la somme est bien arrivée. Tant que tu n'as pas validé, "
                 "rien n'est envoyé à la cliente.</div>")
        actions = (
            f"<form method=post action='/api/order/{oid}/validate'>"
            f"<input type=hidden name=token value='{_esc(token)}'>"
            f"<button class=v>Valider et mettre en ligne</button></form>"
            f"<form method=post action='/api/order/{oid}/reject'>"
            f"<input type=hidden name=token value='{_esc(token)}'>"
            f"<button class=r>Refuser</button></form>")
    elif r["status"] == "live":
        bloc += "<div class=ok><b>Commande validée.</b> Le site est en ligne et la cliente a été prévenue.</div>"
        actions = ""
    else:
        actions = ""

    wa = re.sub(r"\D", "", r["whatsapp"] or "")
    msg = urllib.parse.quote(f"Bonjour {r['client_name']}, votre site est en ligne : {BASE_URL}/v/{r['slug']}")

    return HTMLResponse(f"""<!DOCTYPE html><html lang=fr><head><meta charset=UTF-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<meta name=robots content="noindex,nofollow">
<title>Commande {oid} - Vitrina</title><style>{ACTION_CSS}</style></head><body><div class=k><div class=c>
<h1>Vitri<span>na</span></h1>
<p class=s>Commande {oid} &middot; <span class=tag style="background:{etat[1]}">{etat[0]}</span></p>
<dl>
<dt>Activité</dt><dd>{_esc(r['biz_name'])}</dd>
<dt>Pack</dt><dd>{_esc((r['pack'] or '').upper())} &middot; {money(r['price'])}</dd>
<dt>Cliente</dt><dd>{_esc(r['client_name'])}</dd>
<dt>WhatsApp</dt><dd>{_esc(r['whatsapp'])}</dd>
<dt>Réseau</dt><dd>{_esc(r['network'] or '-')}</dd>
<dt>Référence</dt><dd><span class=ref>{_esc(r['ref'] or '-')}</span></dd>
<dt>Reçue le</dt><dd>{_esc(r['created'])}</dd>
</dl>
{bloc}
{actions}
<a class=lien href="{BASE_URL}/v/{_esc(r['slug'])}" target=_blank>Voir la page de la cliente</a>
<a class=lien href="https://wa.me/{wa}?text={msg}" target=_blank>Écrire à la cliente sur WhatsApp</a>
</div></div></body></html>""")

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
