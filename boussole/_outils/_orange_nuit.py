# -*- coding: utf-8 -*-
"""
Transplante l'identité « ORANGE & NUIT » sur la version PERFORMANTE de Boussole.

Pourquoi une transplantation et pas une fusion : l'identité a été construite sur
une lignée où tout le JavaScript vivait ENCORE dans `app.html`. Depuis, `main` a
sorti ces 238 Ko dans `assets/js/proto-app.js` et ajouté le mode performance
adaptatif. Fusionner les deux branches remettrait tout le code en ligne et
annulerait la fluidité sur les appareils modestes.

On prend donc ce qui vaut le coup, et rien d'autre :
  1. le CSS complet de la branche (jetons + palette orange, thèmes sombre ET clair)
  2. auquel on RECOLLE le bloc `.perf-lite` que `main` a ajouté depuis
  3. les couleurs que le JavaScript génère lui-même, remplacées par les mêmes
     jetons, dans le module externalisé

Idempotent : relançable sans dégât. UTF-8 strict.
    python boussole/_outils/_orange_nuit.py
"""
import io, re, subprocess, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency")
APP = RACINE / "boussole/_proto/app.html"
MOD = RACINE / "boussole/assets/js/proto-app.js"
BRANCHE = "origin/claude/protocole-boussole-memoire-9xy3j4"

# Les couleurs que le JS écrit lui-même, telles que la branche les a remplacées.
# Déduites en comparant son JS à celui d'avant, pas inventées.
COULEURS_JS = [
    ("#34d399", "var(--good)"),     # émeraude
    ("#f6a63c", "var(--acc)"),      # or ambre  → orange signature
    ("#ffd23f", "var(--acc2)"),     # jaune
    ("#e11d48", "var(--bad)"),      # rouge
    ("#b98cff", "var(--acc2)"),     # violet    → orange chaud
    ("#ff8a3d", "var(--acc)"),
    ("#ffc46a", "var(--acc2)"),
    ("#14161c", "var(--ink)"),      # surface opaque
    ("#04121a", "var(--on-acc)"),   # encre sur aplat
    ("#4cc9ff", "var(--acc2)"),     # cyan      → orange
    ("#ff6ec7", "#ffa347"),         # rose      → orange pâle
    ("#5ad1c8", "#ffa347"),         # turquoise → orange pâle
]

# Deux jetons de la branche se référencent eux-mêmes : ils ne produisent rien.
# On leur donne la valeur cohérente avec le couple good/good2 de chaque thème.
CORRECTIONS = [
    ("--bad2: var(--bad2);", "--bad2: #ff8a96;"),   # sombre : variante plus claire
    ("--bad: var(--bad);",   "--bad: #e11d48;"),    # clair  : rouge lisible sur blanc
]


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, cwd=RACINE)
    if r.returncode != 0:
        print("  ⛔ git", " ".join(a), ":", r.stderr.decode(errors="replace")[:200])
        sys.exit(1)
    return r.stdout.decode("utf-8", errors="replace")


def bloc_style(html):
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    if not m:
        print("  ⛔ pas de bloc <style> trouvé"); sys.exit(1)
    return m


def main():
    app = io.open(APP, encoding="utf-8").read()
    if "--acc: #ff8a1e" in app:
        print("  Identité déjà transplantée, rien à faire.")
        return 0

    # 1. le CSS de la branche
    css_branche = bloc_style(git("show", f"{BRANCHE}:boussole/_proto/app.html")).group(1)
    for vieux, neuf in CORRECTIONS:
        if vieux in css_branche:
            css_branche = css_branche.replace(vieux, neuf)
            print(f"  ✓ jeton réparé : {vieux.strip()} → {neuf.strip()}")

    # 2. le mode performance de main, qui n'existe pas dans la branche
    m_actuel = bloc_style(app)
    css_actuel = m_actuel.group(1)
    i = css_actuel.find("/* ===================== MODE PERFORMANCE ADAPTATIF")
    if i == -1:
        print("  ⛔ bloc « MODE PERFORMANCE ADAPTATIF » introuvable : on n'écrase rien.")
        sys.exit(1)
    perf = css_actuel[i:]
    print(f"  ✓ mode performance adaptatif préservé ({len(perf)} octets)")

    neuf_css = css_branche.rstrip() + "\n\n" + perf.lstrip()
    app = app[:m_actuel.start(1)] + neuf_css + app[m_actuel.end(1):]

    # garde-fous : on ne casse pas ce qui fait tourner l'app
    assert 'src="../assets/js/proto-app.js"' in app, "le module externalisé a disparu"
    assert "perf-lite" in app, "le mode performance a disparu"
    assert "--acc: #ff8a1e" in app, "la palette orange n'est pas là"
    io.open(APP, "w", encoding="utf-8", newline="").write(app)
    print(f"  ✓ app.html : identité posée ({len(app)//1024} Ko)")

    # 3. les couleurs générées par le JavaScript
    mod = io.open(MOD, encoding="utf-8").read()
    total = 0
    for vieux, neuf in COULEURS_JS:
        n = mod.count(vieux)
        if n:
            mod = mod.replace(vieux, neuf); total += n
    io.open(MOD, "w", encoding="utf-8", newline="").write(mod)
    print(f"  ✓ proto-app.js : {total} couleur(s) passées aux jetons")

    reste = re.findall(r"#(?:f6a63c|34d399|4cc9ff|b98cff|ffd23f)", mod, re.I)
    print(f"  {'✓' if not reste else '⚠️ '} anciennes couleurs restantes dans le module : {len(reste)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
