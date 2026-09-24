# -*- coding: utf-8 -*-
"""
Le contrôle SEO et GEO d'aubraisedor.com, sur le dossier publié (`experience/out`).

    python _outils/_qc_seo.py

Né de la passe SEO du 2026-09-18 (Mongazi : « que la vitrine sorte en premier quand on cherche
restaurant, restaurant Bénin… »). Ce qu'il garde, et pourquoi chaque point compte :
  · UN titre de niveau 1 par page : la page d'accueil n'en avait AUCUN (le premier titre était
    « SAUCEGOMBO », un nom de plat du carrousel) ;
  · titres et descriptions UNIQUES : deux pages au même titre se disputent la même recherche ;
  · chaque page déclare SA propre adresse canonique, et la 404 aucune (elle héritait de celle de
    l'accueil : elle se déclarait sa copie) ;
  · le sitemap et les pages publiées sont le MÊME ensemble, dans les deux sens ;
  · la FAQ balisée est la FAQ affichée, question pour question (Google sanctionne l'inverse) ;
  · « restaurant », « Cotonou » et « Bénin » dans le texte visible de l'accueil ;
  · `llms.txt` et `carte.md` publiés, et chaque rubrique y a son lien ;
  · ⛔ aucune adresse de rue, aucune note, aucun avis inventés, sur aucune page.
TÉMOIN : le détecteur de H1 est essayé sur une page sans H1, et doit la refuser.
"""
from __future__ import annotations

import html as H
import io
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(ICI, "..", "experience", "out"))
SITE = "https://aubraisedor.com"
ok, ko = [], []


def dire(bon, txt):
    (ok if bon else ko).append(txt)
    print(("  vert  " if bon else "  ROUGE ") + txt)


def h1s(s: str) -> list[str]:
    return [re.sub(r"<[^>]+>", "", H.unescape(x)).strip() for x in re.findall(r"<h1[^>]*>(.*?)</h1>", s, re.S)]


def meta(s: str, nom: str) -> list[str]:
    return [H.unescape(x) for x in re.findall(r'<meta name="%s" content="([^"]*)"' % nom, s)]


def texte_visible(s: str) -> str:
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S)
    return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pages = {}
    for racine, _, fichiers in os.walk(OUT):
        if "index.html" in fichiers and "_next" not in racine:
            rel = os.path.relpath(racine, OUT).replace("\\", "/")
            url = "/" if rel == "." else f"/{rel}/"
            pages[url] = io.open(os.path.join(racine, "index.html"), encoding="utf-8").read()
    indexables = {u: s for u, s in pages.items() if u != "/404/"}
    dire(len(indexables) >= 14, f"{len(indexables)} pages publiées (accueil, carte, 9 rubriques, 3 services)")

    # TÉMOIN : un détecteur de H1 qui laisserait passer une page sans H1 ne garde rien.
    dire(len(h1s("<html><body><h2>Plat</h2></body></html>")) == 0, "TÉMOIN : une page sans H1 est vue sans H1")

    titres, descriptions = {}, {}
    for url, s in sorted(indexables.items()):
        t = [H.unescape(x) for x in re.findall(r"<title>(.*?)</title>", s)]
        d = meta(s, "description")
        c = re.findall(r'<link rel="canonical" href="([^"]*)"', s)
        r = meta(s, "robots")
        dire(len(h1s(s)) == 1, f"{url} : un seul H1 ({len(h1s(s))})")
        dire(len(t) >= 1 and 25 <= len(t[-1]) <= 72, f"{url} : titre de {len(t[-1]) if t else 0} caractères")
        dire(len(d) == 1 and 70 <= len(d[0]) <= 165, f"{url} : description de {len(d[0]) if d else 0} caractères")
        dire(c == [f"{SITE}{url}"], f"{url} : canonique = elle-même ({c})")
        dire(not any("noindex" in x for x in r), f"{url} : indexable")
        titres.setdefault(t[-1] if t else "", []).append(url)
        descriptions.setdefault(d[0] if d else "", []).append(url)
        dire("streetAddress" not in s and "aggregateRating" not in s and '"review"' not in s.lower(),
             f"{url} : ⛔ ni adresse de rue, ni note, ni avis inventés")
    dire(all(len(v) == 1 for v in titres.values()), "tous les titres sont uniques")
    dire(all(len(v) == 1 for v in descriptions.values()), "toutes les descriptions sont uniques")

    # La 404
    p404 = io.open(os.path.join(OUT, "404.html"), encoding="utf-8").read()
    dire(any("noindex" in x for x in meta(p404, "robots")), "404 : noindex")
    dire('rel="canonical"' not in p404, "404 : aucune adresse canonique héritée")

    # Le sitemap, dans les deux sens
    sm = io.open(os.path.join(OUT, "sitemap.xml"), encoding="utf-8").read()
    dans_sm = {u.replace(SITE, "") for u in re.findall(r"<loc>([^<]+)</loc>", sm)}
    dire(dans_sm == set(indexables), f"sitemap = pages publiées ({len(dans_sm)} / {len(indexables)})"
         + ("" if dans_sm == set(indexables) else f" · manquent {set(indexables) - dans_sm} · en trop {dans_sm - set(indexables)}"))

    # L'accueil : le texte, la FAQ visible contre la FAQ balisée
    acc = indexables["/"]
    vis = texte_visible(acc).lower()
    for mot in ("restaurant", "cotonou", "bénin", "braise", "grillades"):
        dire(mot in vis, f"accueil : « {mot} » dans le texte visible")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', acc, re.S).group(1))
    graphe = ld.get("@graph", [ld])
    faq = next((n for n in graphe if n.get("@type") == "FAQPage"), None)
    q_balisees = [q["name"] for q in faq["mainEntity"]] if faq else []
    q_visibles = [re.sub(r"<[^>]+>", "", H.unescape(x)).strip()
                  for x in re.findall(r'<summary[^>]*>.*?<h3[^>]*>(.*?)</h3>', acc, re.S)]
    dire(len(q_balisees) >= 5 and q_balisees == q_visibles,
         f"FAQ : {len(q_balisees)} questions balisées = {len(q_visibles)} questions affichées, dans le même ordre")
    for q in (faq or {}).get("mainEntity", []):
        mots = len(q["acceptedAnswer"]["text"].split())
        dire(25 <= mots <= 75, f"FAQ : réponse de {mots} mots à « {q['name'][:40]}… »")
    resto = next((n for n in graphe if n.get("@type") == "Restaurant"), {})
    dire(resto.get("address", {}).get("addressLocality") == "Cotonou", "Restaurant : Cotonou déclaré")
    dire(bool(resto.get("hasMenu", {}).get("url")), "Restaurant : le menu pointe vers /carte/")

    # Les fichiers pour les IA
    for f in ("llms.txt", "carte.md", "robots.txt"):
        dire(os.path.exists(os.path.join(OUT, f)), f"{f} publié")
    llms = io.open(os.path.join(OUT, "llms.txt"), encoding="utf-8").read()
    manquent = [u for u in indexables if u != "/" and f"{SITE}{u}" not in llms]
    dire(not manquent, f"llms.txt relie chaque page ({'toutes' if not manquent else manquent})")
    rob = io.open(os.path.join(OUT, "robots.txt"), encoding="utf-8").read()
    dire("Disallow: /\n" not in rob and "Sitemap: https://aubraisedor.com/sitemap.xml" in rob,
         "robots.txt : rien d'interdit, le sitemap est déclaré")
    for bot in ("GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Google-Extended"):
        dire(f"User-agent: {bot}" in rob, f"robots.txt : {bot} accueilli")

    # Chaque rubrique est reliée depuis l'accueil
    for url in indexables:
        if url.startswith("/carte/") and url != "/carte/":
            dire(f'href="{url}"' in acc, f"accueil → {url}")

    print(f"\n{len(ok)} verts, {len(ko)} rouges")
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main())
