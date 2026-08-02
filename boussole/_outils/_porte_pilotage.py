# -*- coding: utf-8 -*-
"""
Porte le PILOTAGE et la VISITE GUIDÉE sur la version performante de Boussole.

Le problème : ces apports ont été écrits quand tout le JavaScript vivait encore
dans `app.html`. Depuis, `main` l'a sorti dans `assets/js/proto-app.js` et y a
ajouté le mode performance. Fusionner la branche remettrait tout en ligne et
annulerait ce travail.

La solution : ne pas replacer 25 morceaux à la main, mais laisser git faire une
**vraie fusion à trois voies**, séparément sur chaque fichier :

    app.html      base SANS son script   <->  main  <->  branche SANS son script
    proto-app.js  script de la base      <->  main  <->  script de la branche

Puis arbitrer ce que git ne sait pas trancher, avec des règles nommées, et dire
ce qui a été décidé dans chaque cas.

    python boussole/_outils/_porte_pilotage.py            # essai, n'écrit rien
    python boussole/_outils/_porte_pilotage.py --ecrire   # applique
"""
import io, re, subprocess, sys, tempfile, os
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency")
APP = RACINE / "boussole/_proto/app.html"
MOD = RACINE / "boussole/assets/js/proto-app.js"

BASE = "d9bf476"      # avant la séparation des deux lignées
BRANCHE = "59a8d45"   # la pointe : sa palette est déjà celle de main, donc le
# style et la structure fusionnent proprement. Les conflits qui restent sont
# tous dans le code, et chacun est arbitré par une règle explicite plus bas.

RX_SCRIPT = re.compile(r'(<script type="module">)(.*?)(</script>)', re.S)
RX_CONFLIT = re.compile(r"<<<<<<< actuel\n(.*?)=======\n(.*?)>>>>>>> apport\n", re.S)

# Les deux lignées ont recoloré le même code, chacune à sa façon : cela produit
# des conflits qui n'en sont pas. On aligne l'apport sur la convention déjà en
# place (la même table que _orange_nuit.py) AVANT de fusionner.
COULEURS = [
    ("#34d399", "var(--good)"), ("#f6a63c", "var(--acc)"), ("#ffd23f", "var(--acc2)"),
    ("#e11d48", "var(--bad)"),  ("#b98cff", "var(--acc2)"), ("#ff8a3d", "var(--acc)"),
    ("#ffc46a", "var(--acc2)"), ("#14161c", "var(--ink)"),  ("#04121a", "var(--on-acc)"),
    ("#4cc9ff", "var(--acc2)"), ("#ff6ec7", "#ffa347"),     ("#5ad1c8", "#ffa347"),
]
# Deux jetons que la branche définit en boucle sur eux-mêmes : ils ne produisent
# aucune couleur. On garde la valeur déjà retenue dans main.
JETONS = [("--bad2: var(--bad2);", "--bad2: #ff8a96;"),
          ("--bad: var(--bad);", "--bad: #e11d48;")]


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, cwd=RACINE)
    if r.returncode != 0:
        print("  ERREUR git", " ".join(a[:3]), ":", r.stderr.decode(errors="replace")[:200])
        sys.exit(1)
    return r.stdout.decode("utf-8", errors="replace")


def normaliser(txt, jetons=False):
    for vieux, neuf in COULEURS:
        txt = txt.replace(vieux, neuf)
    if jetons:
        for vieux, neuf in JETONS:
            txt = txt.replace(vieux, neuf)
    return txt


def decouper(html):
    """Rend (le html sans son script, le script seul)."""
    m = RX_SCRIPT.search(html)
    if not m:
        return html, ""
    return html[:m.start(2)] + "\n/*__SCRIPT__*/\n" + html[m.end(2):], m.group(2)


def fusion3(nom, base, courant, autre):
    f = []
    for txt in (courant, base, autre):
        t = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                        encoding="utf-8", newline="")
        t.write(txt)
        t.close()
        f.append(t.name)
    r = subprocess.run(["git", "merge-file", "-p",
                        "-L", "actuel", "-L", "base", "-L", "apport", *f],
                       capture_output=True, cwd=RACINE)
    sortie = r.stdout.decode("utf-8", errors="replace")
    for x in f:
        os.unlink(x)
    n = sortie.count("<<<<<<<")
    print(f"  {nom:14} " + ("fusion propre" if not n else f"{n} conflit(s) a arbitrer"))
    return sortie, n


def arbitrer(txt, nom):
    """Tranche les conflits restants avec des règles nommées, et dit ce qu'il a fait.

    Une lignée a recoloré et optimisé, l'autre a ajouté des fonctions. Là où
    elles se croisent, git ne peut pas deviner. Ces règles, elles, sont
    explicites :

      - même chose écrite autrement (couleurs, espaces) -> on garde l'existant,
        qui est tokenisé, donc compatible avec le thème clair ;
      - l'apport AJOUTE des lignes -> c'est une fonction demandée, on la prend ;
      - le tiroir 3D -> on garde l'existant : son remplacement appartient à la
        vague des transitions, qui n'est pas ce chantier.
    """
    journal = []
    sans_couleur = lambda s: re.sub(r"(var\(--[a-z0-9-]+\)|#[0-9a-fA-F]{3,8})", "C", s)

    # Les fonctions apportées par le pilotage et la visite guidée. Si un côté
    # les appelle, c'est le nouveau code : compter des lignes ne suffit pas.
    # Sans cette règle, un conflit aurait fait disparaître TOUT l'affichage du
    # score de santé, sans que rien ne le signale.
    NOUVELLES = re.compile(
        r"\b(scoreSante|pointMort|treso|fiabilite|projectionMois|stockValeur|recurrentMois"
        r"|produitsHTML|panierHTML|comparaisonHTML|rythmeHTML|partagerBilanWA|prochaineAction"
        r"|startTour|paintTour|ouvrirAide|joursOuverture|chargesMois|data-rapport)\b"
        # ...et les mêmes notions écrites en français : les questions rapides de
        # l'assistant doivent proposer le point mort et la trésorerie, sinon ces
        # écrans existent sans que personne ne sache les demander.
        r"|Mon point mort|Ma trésorerie|Mon score|Quel produit rapporte|Fin de mois")

    def choisir(m):
        a, b = m.group(1), m.group(2)
        na, nb = a.strip(), b.strip()
        if "drawer3d" in a and "drawer3d" not in b:
            journal.append("tiroir 3D conserve : son remplacement est un autre chantier")
            return a
        if re.sub(r"\s+", " ", na) == re.sub(r"\s+", " ", nb):
            journal.append("difference d'espaces seulement -> existant")
            return a
        if sans_couleur(na) == sans_couleur(nb):
            journal.append("memes lignes, couleurs ecrites autrement -> existant (jetons)")
            return a
        # le coeur du port : l'apport amene une fonction du pilotage
        n_new = len(NOUVELLES.findall(nb)) - len(NOUVELLES.findall(na))
        if n_new > 0:
            noms = sorted(set(NOUVELLES.findall(nb)) - set(NOUVELLES.findall(na)))
            journal.append("apport retenu, il amene : " + ", ".join(noms[:5]))
            return normaliser(b)          # ses couleurs passent aux jetons
        if len(b.splitlines()) > len(a.splitlines()) and (not na or na in nb):
            n = len(b.splitlines()) - len(a.splitlines())
            journal.append(f"l'apport ajoute {n} ligne(s) -> apport")
            return normaliser(b)
        journal.append("A REGARDER : les deux cotes different vraiment -> existant conserve")
        return a

    res = RX_CONFLIT.sub(choisir, txt)
    print(f"  arbitrage de {nom} :")
    for j in journal:
        print("    -", j)
    return res, res.count("<<<<<<<")


def main():
    ecrire = "--ecrire" in sys.argv

    app_base, js_base = decouper(git("show", f"{BASE}:boussole/_proto/app.html"))
    app_br, js_br = decouper(git("show", f"{BRANCHE}:boussole/_proto/app.html"))
    app_br, js_br = normaliser(app_br, jetons=True), normaliser(js_br)
    app_now = io.open(APP, encoding="utf-8").read()
    mod_now = io.open(MOD, encoding="utf-8").read()

    app_now_marque = (RX_SCRIPT.sub(lambda m: m.group(1) + "\n/*__SCRIPT__*/\n" + m.group(3), app_now)
                      if RX_SCRIPT.search(app_now) else app_now)

    print(f"  base {BASE} - apport {BRANCHE}")
    print(f"  script : base {len(js_base)//1024} Ko -> apport {len(js_br)//1024} Ko "
          f"(+{(len(js_br)-len(js_base))//1024} Ko) - module actuel {len(mod_now)//1024} Ko\n")

    neuf_app, c1 = fusion3("app.html", app_base, app_now_marque, app_br)
    neuf_mod, c2 = fusion3("proto-app.js", js_base, mod_now, js_br)

    if c2:
        neuf_mod, c2 = arbitrer(neuf_mod, "proto-app.js")
    if c1:
        neuf_app, c1 = arbitrer(neuf_app, "app.html")

    neuf_app = neuf_app.replace("\n/*__SCRIPT__*/\n", "")

    d = RACINE / "boussole/_dist_fusion"
    if c1 or c2:
        print("\n  Des conflits resistent : rien n'est ecrit.")
        d.mkdir(exist_ok=True)
        io.open(d / "app.html", "w", encoding="utf-8", newline="").write(neuf_app)
        io.open(d / "proto-app.js", "w", encoding="utf-8", newline="").write(neuf_mod)
        return 1

    controles = [
        (neuf_app, 'src="../assets/js/proto-app.js"', "le module externalise"),
        (neuf_app, "perf-lite", "le mode performance adaptatif"),
        (neuf_app, "--acc: #ff8a1e", "la palette Orange & Nuit"),
        (neuf_mod, "pointMort", "le point mort"),
        (neuf_mod, "scoreSante", "le score de sante"),
        (neuf_mod, "startTour", "la visite guidee"),
        (neuf_mod, "treso", "la tresorerie"),
        (neuf_mod, "produitsHTML", "l'ecran produits"),
    ]
    print()
    manque = False
    for txt, motif, quoi in controles:
        ok = motif in txt
        print(("  OK      " if ok else "  MANQUE  ") + quoi)
        manque = manque or not ok
    if manque:
        print("\n  Port incomplet : rien n'est ecrit.")
        return 1

    if not ecrire:
        print("\n  Essai concluant, rien n'a ete ecrit. Pour appliquer :")
        print("      python boussole/_outils/_porte_pilotage.py --ecrire")
        return 0

    io.open(APP, "w", encoding="utf-8", newline="").write(neuf_app)
    io.open(MOD, "w", encoding="utf-8", newline="").write(neuf_mod)
    print(f"\n  Applique. app.html {len(neuf_app)//1024} Ko - proto-app.js {len(neuf_mod)//1024} Ko")
    return 0


if __name__ == "__main__":
    sys.exit(main())
