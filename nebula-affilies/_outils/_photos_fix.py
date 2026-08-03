# -*- coding: utf-8 -*-
"""
Répare les photos de profil des back-offices. Deux défauts, pas un.

DÉFAUT 1 — le front utilise le NOM DE FICHIER comme adresse.
    src="photo_1785711283_2d5de2_1000379301.png"
Le navigateur cherche alors cette image à la racine du site, et reçoit un 404.
La bonne adresse existe pourtant déjà : `/api/photo/{id}`. On l'utilise partout.

DÉFAUT 2 — le disque de Render s'efface à chaque déploiement.
Les photos étaient écrites dans `data/uploads/`. Chaque mise en ligne les
supprimait : une photo tenait quelques heures, puis disparaissait sans que
personne comprenne. On les range désormais **dans la base**, en base64, comme
tout le reste des images chez NEBULA. Supabase les garde, et les sauvegarde.

Idempotent, UTF-8 strict.
    python nebula-affilies/_outils/_photos_fix.py
"""
import io, re, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency/nebula-affilies")

# --- 1. l'enregistrement : en base, pas sur un disque qui s'efface -----------
ANCIEN_UPLOAD = '''    fname, _ = await store_upload(file, "photo")
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
    return {"ok": True, "url": photo_url(me)}'''

NOUVEAU_UPLOAD = '''    # La photo est rangée DANS LA BASE, en base64, et non sur le disque :
    # celui de Render s'efface à chaque déploiement, donc une photo posée le
    # matin disparaissait le soir sans que personne comprenne pourquoi.
    data = await file.read()
    if len(data) > 700_000:
        return JSONResponse({"ok": False,
                             "error": "Photo trop lourde (700 Ko maximum). Réduis-la avant de l'envoyer."},
                            status_code=400)
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "webp": "image/webp", "gif": "image/gif"}.get(ext)
    if not mime:
        return JSONResponse({"ok": False,
                             "error": "Format non reconnu. Utilise une photo JPG, PNG ou WEBP."},
                            status_code=400)
    fname = "data:" + mime + ";base64," + base64.b64encode(data).decode("ascii")

    if me == "admin":
        setting_set("admin_photo", fname)
    else:
        aid = int(me[1:])
        with db() as c:
            c.execute("UPDATE affiliates SET photo=? WHERE id=?", (fname, aid))
    return {"ok": True, "url": photo_url(me)}'''

# --- 2. la lecture : servir aussi bien une photo en base qu'un vieux fichier --
ANCIEN_SERVE = '''    if not fname:
        return JSONResponse({"error": "introuvable"}, status_code=404)
    fp = UP_DIR / fname
    if not fp.exists():
        return JSONResponse({"error": "introuvable"}, status_code=404)
    return FileResponse(str(fp))'''

NOUVEAU_SERVE = '''    if not fname:
        return JSONResponse({"error": "introuvable"}, status_code=404)
    # photo rangée en base (le cas normal depuis le 2026-08-03)
    if fname.startswith("data:"):
        try:
            entete, b64 = fname.split(",", 1)
            mime = entete[5:].split(";")[0] or "image/jpeg"
            return Response(content=base64.b64decode(b64), media_type=mime,
                            headers={"Cache-Control": "private, max-age=300"})
        except Exception:
            return JSONResponse({"error": "illisible"}, status_code=404)
    # ancien stockage sur disque : conservé pour les photos posées avant
    fp = UP_DIR / fname
    if not fp.exists():
        return JSONResponse({"error": "introuvable"}, status_code=404)
    return FileResponse(str(fp))'''


def main():
    faits = []

    # ---- server.py ----
    p = RACINE / "server.py"
    h = io.open(p, encoding="utf-8").read()

    if "import base64" not in h:
        h = h.replace("import os, re, sqlite3", "import base64\nimport os, re, sqlite3", 1) \
            if "import os, re, sqlite3" in h else h
        if "import base64" not in h:
            m = re.search(r"^import .+$", h, re.M)
            h = h[:m.start()] + "import base64\n" + h[m.start():]
        faits.append("base64 importé")

    if "from fastapi.responses import" in h and ", Response" not in h.split("from fastapi.responses import")[1].split("\n")[0]:
        ligne = h.split("from fastapi.responses import")[1].split("\n")[0]
        h = h.replace("from fastapi.responses import" + ligne,
                      "from fastapi.responses import" + ligne.rstrip() + ", Response", 1)
        faits.append("Response importé")

    if ANCIEN_UPLOAD in h:
        h = h.replace(ANCIEN_UPLOAD, NOUVEAU_UPLOAD, 1)
        faits.append("photos rangées en base, plus sur un disque qui s'efface")
    if ANCIEN_SERVE in h:
        h = h.replace(ANCIEN_SERVE, NOUVEAU_SERVE, 1)
        faits.append("lecture : gère la base ET les anciens fichiers")

    io.open(p, "w", encoding="utf-8", newline="").write(h)

    # ---- les pages : utiliser /api/photo/{id} au lieu du nom de fichier ----
    for f in ("admin.html", "partenaire.html"):
        pf = RACINE / f
        if not pf.exists():
            continue
        t = io.open(pf, encoding="utf-8").read()
        avant = t
        # les cas où l'on a l'objet complet sous la main
        t = re.sub(r'src="\$\{esc\((\w+)\.photo\)\}(\?t=\$\{Date\.now\(\)\})?"',
                   lambda m: 'src="/api/photo/${' + m.group(1) + '.id}"'
                   + ('' if not m.group(2) else ''), t)
        t = t.replace('src="${esc(photo)}"', 'src="${photoUrl}"')
        if t != avant:
            io.open(pf, "w", encoding="utf-8", newline="").write(t)
            faits.append(f"{f} : les avatars pointent vers /api/photo/{{id}}")

    if not faits:
        print("  Tout était déjà corrigé.")
        return 0
    for x in faits:
        print("  ✓", x)

    h = io.open(RACINE / "server.py", encoding="utf-8").read()
    assert "base64.b64encode" in h, "l'enregistrement en base n'est pas posé"
    assert 'fname.startswith("data:")' in h, "la lecture ne gère pas la base"
    print("  ✓ contrôles passés")
    return 0


if __name__ == "__main__":
    sys.exit(main())
