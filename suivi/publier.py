# -*- coding: utf-8 -*-
"""Publie NEBULA Suivi sur Cloudflare Pages (projet `nebula-suivi`) : la clé publique Supabase (publique par conception ;
tout est verrouillé par RLS sur les e-mails de Mongazi) et la clé PUBLIQUE des notifications sont posées à la construction.
Les icônes sont dessinées ici. La clé privée des notifications ne quitte pas `secrets/`.

    python suivi/publier.py
"""
import json
import os
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
DIST = ICI / "_dist"
CONFIG_BOUSSOLE = RACINE / "boussole" / "assets" / "js" / "config.js"


def icone(t):
    """Une orbite lumineuse sur la nuit, comme le logo NEBULA."""
    im = Image.new("RGB", (t, t), (6, 7, 19))
    halo = Image.new("RGB", (t, t), (0, 0, 0)); d = ImageDraw.Draw(halo)
    d.ellipse([t * .18, t * .36, t * .82, t * .64], outline=(147, 51, 234), width=max(2, t // 22))
    d.ellipse([t * .26, t * .30, t * .74, t * .70], outline=(79, 111, 255), width=max(2, t // 26))
    halo = halo.filter(ImageFilter.GaussianBlur(t / 60))
    im = Image.blend(im, halo, 0.9)
    d = ImageDraw.Draw(im)
    c, r = t / 2, t * .07
    d.ellipse([c - r, c - r, c + r, c + r], fill=(34, 211, 238))
    d.line([c - t * .2, c, c + t * .2, c], fill=(220, 240, 255), width=max(1, t // 90))
    d.line([c, c - t * .2, c, c + t * .2], fill=(220, 240, 255), width=max(1, t // 90))
    return im


def main():
    cle = re.search(r"SUPABASE_ANON_KEY\s*=\s*'([^']+)'", CONFIG_BOUSSOLE.read_text(encoding="utf-8")).group(1)
    vapid = dict(re.findall(r"^([A-Z_0-9]+)=(.+)$", (RACINE / "secrets" / "suivi.env").read_text(encoding="utf-8"), re.M))
    shutil.rmtree(DIST, ignore_errors=True); DIST.mkdir()
    html = (ICI / "index.html").read_text(encoding="utf-8")
    assert '"__ANON__"' in html and '"__VAPID__"' in html
    (DIST / "index.html").write_text(html.replace('"__ANON__"', '"' + cle + '"').replace('"__VAPID__"', '"' + vapid["VAPID_PUBLIC"].strip() + '"'), encoding="utf-8")
    shutil.copy(ICI / "sw.js", DIST / "sw.js")
    for t in (180, 192, 512):
        icone(t).save(DIST / f"icone-{t}.png")
    (DIST / "manifest.webmanifest").write_text(json.dumps({
        "name": "NEBULA Suivi", "short_name": "NEBULA", "start_url": "./", "scope": "./", "display": "standalone",
        "background_color": "#060713", "theme_color": "#060713", "lang": "fr",
        "icons": [{"src": "icone-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, ensure_ascii=False), encoding="utf-8")
    (DIST / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n  X-Frame-Options: DENY\n  X-Content-Type-Options: nosniff\n"
                                   "  Referrer-Policy: no-referrer\n  Cache-Control: no-cache\n", encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    env = dict(os.environ, **dict(re.findall(r"^(CLOUDFLARE_ACCOUNT_ID|CLOUDFLARE_API_TOKEN)=(.+)$",
                                             (RACINE / "secrets" / "cloudflare.env").read_text(encoding="utf-8"), re.M)))
    env = {k: v.strip() for k, v in env.items()}
    subprocess.run("wrangler pages project create nebula-suivi --production-branch main", shell=True, env=env, capture_output=True)
    r = subprocess.run(f'wrangler pages deploy "{DIST}" --project-name nebula-suivi --branch main --commit-dirty=true',
                       shell=True, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print([l for l in (r.stdout + r.stderr).splitlines() if "complete" in l.lower() or "error" in l.lower()][-1:] or r.returncode)


if __name__ == "__main__":
    main()
