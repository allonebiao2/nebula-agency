"""QC du flux de commande Vitrina : paiement Mobile Money declare, alerte
WhatsApp + Telegram, lien de validation a un tap, doublon de reference,
envoi automatique a la cliente.

    cd vitrina && python3 _qc.py

Aucun envoi reel : les deux rails sont remplaces par des mouchards.
"""
import os, sys
import tempfile
SP = tempfile.mkdtemp(prefix="vitrina-qc-")
os.environ["VITRINA_DB"] = SP + "/test.db"
os.environ["VITRINA_ADMIN_KEY"] = "testkey"
os.environ["VITRINA_BASE_URL"] = "http://127.0.0.1:8099"
for f in (SP+"/test.db",):
    if os.path.exists(f): os.remove(f)
sys.path.insert(0, ".")

import notify
envois = []
notify.alerter_mongazi = lambda t: (envois.append(("MONGAZI", t)), {"whatsapp": True, "telegram": True})[1]
notify.prevenir_client = lambda n, t: (envois.append(("CLIENTE " + n, t)), True)[1]

import server
from fastapi.testclient import TestClient
c = TestClient(server.app)
ok = fail = 0
def t(nom, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  OK   {nom}")
    else: fail += 1; print(f"  ROUGE {nom}  {info}")

print("\n=== 1. La cliente commande, avec sa reference de transaction ===")
r = c.post("/api/order", json={"pack":"pro","biz_name":"Chez Maïmouna & Fils <Beauté>",
    "client_name":"Maïmouna","whatsapp":"+229 01 97 08 55 76","network":"MTN MoMo",
    "ref":"MP260827.1432.A81234","html":"<h1>Site de Maimouna</h1>"})
t("commande acceptee", r.status_code == 200, r.text[:200])
oid = r.json()["id"]
t("une alerte est partie", len(envois) == 1)
alerte = envois[0][1]
t("la reference est dans l'alerte", "MP260827.1432.A81234" in alerte)
t("le lien a un tap est dans l'alerte", f"/a/{oid}/" in alerte)
t("le rappel de verifier le SMS y est", "SMS Mobile Money" in alerte)
jeton = server._order_token(oid)

print("\n=== 2. Le lien ouvre une fiche, et NE VALIDE RIEN (robot d'apercu) ===")
r = c.get(f"/a/{oid}/{jeton}")
t("la fiche s'ouvre", r.status_code == 200)
t("la reference est affichee", "MP260827.1432.A81234" in r.text)
t("le nom avec & et <> est echappe", "&amp;" in r.text and "&lt;Beaut" in r.text)
t("noindex pose", 'content="noindex,nofollow"' in r.text)
row = server.db().execute("SELECT status FROM orders WHERE id=?", (oid,)).fetchone()
t("APRES 5 VISITES LA COMMANDE EST TOUJOURS EN ATTENTE", True)
for _ in range(5): c.get(f"/a/{oid}/{jeton}")
row = server.db().execute("SELECT status FROM orders WHERE id=?", (oid,)).fetchone()
t("  -> statut inchange = pending", row["status"] == "pending", f"statut={row['status']}")

print("\n=== 3. Le jeton protege ===")
t("mauvais jeton refuse (403)", c.get(f"/a/{oid}/0000000000000000000000ff").status_code == 403)
t("POST sans jeton ni session refuse", c.post(f"/api/order/{oid}/validate", data={}).status_code == 403)
t("POST mauvais jeton refuse", c.post(f"/api/order/{oid}/validate", data={"token":"x"*24}).status_code == 403)

print("\n=== 4. Mongazi valide depuis WhatsApp : tout part tout seul ===")
envois.clear()
r = c.post(f"/api/order/{oid}/validate", data={"token": jeton}, follow_redirects=False)
t("validation acceptee", r.status_code == 303, r.status_code)
row = server.db().execute("SELECT status,expires FROM orders WHERE id=?", (oid,)).fetchone()
t("la page est EN LIGNE", row["status"] == "live")
t("une echeance a 1 an est posee", bool(row["expires"]))
dest = [e for e in envois if e[0].startswith("CLIENTE")]
t("LA CLIENTE EST PREVENUE AUTOMATIQUEMENT", len(dest) == 1, str(envois))
t("  -> son lien est dans le message", "/v/" in dest[0][1] if dest else False)
t("  -> envoye a son numero", "01 97 08 55 76" in dest[0][0] or "0197085576" in dest[0][0].replace(" ","") if dest else False)
t("Mongazi recoit la confirmation", any(e[0]=="MONGAZI" for e in envois))

print("\n=== 5. La page publique est servie ===")
r = c.get(f"/v/{server.db().execute('SELECT slug FROM orders WHERE id=?', (oid,)).fetchone()['slug']}")
t("page en ligne servie", r.status_code == 200 and "Site de Maimouna" in r.text)
t("plus de bandeau 'en attente'", "attente de validation" not in r.text)

print("\n=== 6. La meme reference reutilisee est signalee ===")
envois.clear()
r2 = c.post("/api/order", json={"pack":"express","biz_name":"Autre","client_name":"Paul",
    "whatsapp":"22997000000","network":"MTN MoMo","ref":"MP260827.1432.A81234","html":"<p>x</p>"})
oid2 = r2.json()["id"]
t("2e commande enregistree quand meme", r2.status_code == 200)
t("ALERTE DOUBLON dans le message", "ATTENTION" in envois[0][1] and "déjà été utilisée" in envois[0][1], envois[0][1][:160])
page2 = c.get(f"/a/{oid2}/{server._order_token(oid2)}").text
t("doublon signale sur la fiche", "Référence déjà vue" in page2)
t("une reference vide ne declenche rien", server._ref_doublon("") == 0)

print("\n=== 7. Cloudflare : la page part au bord du reseau ===")
import publier as P
poses={}; retires=[]
P.publier=lambda slug,html:(poses.__setitem__(slug,html),True)[1]
P.retirer=lambda slug:(retires.append(slug),True)[1]
server.publier=P
envois.clear()
r=c.post("/api/order",json={"pack":"pro","biz_name":"Cadeau","client_name":"Ana",
 "whatsapp":"22990000000","network":"MTN MoMo","ref":"CF-1","html":"<h1>page cadeau</h1>"})
o3=r.json()["id"]; sl3=r.json()["slug"]
envois.clear()
c.post(f"/api/order/{o3}/validate",data={"token":server._order_token(o3)},follow_redirects=False)
t("la page est POSEE sur Cloudflare a la validation", sl3 in poses, str(list(poses)))
t("  -> c'est bien le HTML de la page", poses.get(sl3)=="<h1>page cadeau</h1>")
conf=[e[1] for e in envois if e[0]=="MONGAZI"]
t("l'alerte confirme le service instantane", any("Cloudflare" in x and "instantan" in x for x in conf), str(conf))
c.post(f"/api/order/{o3}/delete", cookies={"vitrina_auth":server._auth_token()}, follow_redirects=False)
t("SUPPRIMER RETIRE AUSSI DU BORD (retrait 24h)", sl3 in retires, str(retires))

print("\n=== 8. Cloudflare absent : rien ne casse, mais on le DIT ===")
P.publier=lambda slug,html:False
envois.clear()
r=c.post("/api/order",json={"pack":"pro","biz_name":"Sans CF","client_name":"B",
 "whatsapp":"22990000001","network":"Moov","ref":"CF-2","html":"<p>z</p>"})
o4=r.json()["id"]; envois.clear()
rv=c.post(f"/api/order/{o4}/validate",data={"token":server._order_token(o4)},follow_redirects=False)
t("la validation reussit quand meme", rv.status_code==303)
row=server.db().execute("SELECT status FROM orders WHERE id=?",(o4,)).fetchone()
t("la page est en ligne malgre tout", row["status"]=="live")
conf=[e[1] for e in envois if e[0]=="MONGAZI"]
t("l'alerte AVERTIT du reveil lent", any("NON publi" in x and "Render" in x for x in conf), str(conf))

print("\n=== 9. Le point de reveil est bon marche ===")
rs=c.get("/sante")
t("/sante repond 200", rs.status_code==200 and rs.json()=={"ok":True})

print("\n=== 10. Aucun rail joignable : la commande survit ===")
import notify as N
N.alerter_mongazi = lambda t: {"whatsapp": False, "telegram": False}
r3 = c.post("/api/order", json={"pack":"pro","biz_name":"Sans reseau","client_name":"Z",
    "whatsapp":"229970000001","network":"Moov","ref":"R-999","html":"<p>y</p>"})
t("commande enregistree malgre l'echec des alertes", r3.status_code == 200)

print(f"\n===== {ok} verts / {fail} rouges =====")
sys.exit(1 if fail else 0)
