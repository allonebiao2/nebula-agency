# -*- coding: utf-8 -*-
"""
RAPATRIER — ramène dans `main` tout ce qui traîne sur les branches.

Pourquoi ce script existe : Claude Code sur téléphone, sur le web ou sur une
autre machine travaille sur des branches `claude/…` qui n'arrivent JAMAIS dans
`main` toutes seules. Le 2026-08-02, neuf branches s'étaient accumulées, dont
une qui portait toute la refonte des commissions. Personne ne l'aurait su sans
aller regarder.

    python scripts/rapatrier.py              # regarde et rapporte, ne touche à rien
    python scripts/rapatrier.py --fusionner  # ramène tout dans main
    python scripts/rapatrier.py --fusionner --branche claude/xxx   # une seule

Ce script ne pousse jamais tout seul : il prépare, montre, et laisse le dernier
mot. Après une fusion, il rappelle ce qu'il reste à faire (dispatch mémoire,
déploiement).
"""
import subprocess, sys, argparse, re

# La console de Windows est en cp1252 et ne sait pas ecrire les symboles du
# depot : sans cette ligne, l'outil MEURT en affichant son propre diagnostic.
# Vu le 2026-09-03 : rapatrier.py annoncait « le dossier de travail n'est pas
# propre » et se tuait sur le symbole qui precede la phrase. Un outil qui
# meurt en annoncant un probleme est pire qu'un outil absent.
for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def git(*a, silencieux=False):
    r = subprocess.run(["git"] + list(a), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0 and not silencieux:
        print(f"  ⛔ git {' '.join(a)} : {(r.stderr or '').strip()[:200]}")
    return (r.stdout or "").strip()

# les chemins qui exigent un regard humain avant d'être fusionnés
SENSIBLE = re.compile(
    r"(vente/|CONTRAT|SOCLE|server\.py|_worker\.js|secrets/|CLAUDE\.md)", re.I)

# ─────────────────────────────────────────────────────────────────────────────
# LES BRANCHES DÉJÀ JUGÉES, ET POURQUOI.
#
# ⚠️ POURQUOI CETTE LISTE EXISTE. Sans elle, ce script rappelle les mêmes
# branches à chaque session, et chaque session refait l'enquête depuis zéro :
# ouvrir le diff, comprendre ce que ça ajoute, décider. Une décision qu'on ne
# note pas est une décision qu'on reprend.
#
# ⛔ ET SURTOUT : `--fusionner` sans `--branche` fusionnait TOUT ce qui passe
# sans conflit. Trois de ces branches passent sans conflit et ne doivent
# pourtant jamais rentrer — dont une qui rapatrierait `fly.toml` et
# `railway.json`, la configuration abandonnée. « Sans conflit » ne veut pas
# dire « inoffensif ».
#
# Écarté n'est pas supprimé : les branches restent sur GitHub, et
# `--branche <nom>` force la fusion de celle qu'on nomme, en connaissance de
# cause. Pour retirer une branche d'ici, il faut avoir réglé sa raison.
# ─────────────────────────────────────────────────────────────────────────────
ECARTEES = {
    "claude/github-repo-context-nisd2r":
        "PÉRIMÉE : supprimerait 30 790 lignes de `main`, tout PISTE compris",
    "claude/nebula-recruitment-video-jis1c1":
        "le nom ment : elle n'ajoute pas de vidéo mais `fly.toml` et "
        "`railway.json`, la configuration abandonnée",
    "claude/commission-structure-pdf-6z8lof":
        "PDF et PPTX de commissions au barème d'AVANT la grille unique du "
        "2026-08-02 : un partenaire finirait par le recevoir",
    "claude/nebula-agency-redesign-bpVr2":
        "la refonte de mai, antérieure au site en ligne ; elle réécrit "
        "`nebula_agency_v5_FINAL` et renommerait le site en v7",
    "claude/latest-repo-update-mlju2l":
        "modifie `cercle/src/` et ajoute un plan de semaine de juin périmé",
    # celles-ci sont en conflit ET portent du commercial d'avant la grille
    "claude/nebula-agency-pricing-grid-4wnr2z":
        "affiche des forfaits d'avant la grille unique du 2026-08-02",
    "claude/nebula-quote-generator-kmr4i6":
        "générateur de devis d'avant la grille unique du 2026-08-02",
}


def ecartee(nom):
    """`nom` arrive en `origin/claude/…` : on juge sur la partie stable."""
    return ECARTEES.get(nom[7:] if nom.startswith("origin/") else nom)


def main_en_retard():
    """`main` local est-il derrière `origin/main` ?

    ⛔ LA PANNE DU 2026-08-27, ET ELLE A COÛTÉ UNE JOURNÉE DE TRAVAIL EN DOUBLE.
    Ce script excluait `origin/main` de son inventaire (voir la ligne juste en
    dessous) : il ne surveillait que les branches `claude/…`. Or une session
    lancée depuis le téléphone pousse DIRECTEMENT dans `main`. Ce jour-là, le
    PC de Cotonou a refait de zéro les six photos de sauces d'Au Braisé d'Or —
    outils compris — alors que le travail dormait dans `main` depuis la veille,
    fait autrement et mieux documenté.

    ⚠️ « Rien ne traîne sur les branches » ne veut pas dire « je suis à jour ».
    """
    git("fetch", "origin", "--prune", silencieux=True)
    commits = git("log", "--oneline", "main..origin/main").splitlines()
    if not commits:
        return 0
    print("\n  ⛔ `main` LOCAL EST EN RETARD DE %d COMMIT(S) SUR origin/main.\n"
          % len(commits))
    for c in commits[:12]:
        print("     " + c)
    if len(commits) > 12:
        print("     … et %d autres" % (len(commits) - 12))
    print("\n     Avant de travailler :  git merge origin/main")
    print("     Sinon on refait ce qui est déjà fait — c'est arrivé le 27/08.\n")
    return len(commits)


def branches_en_retard():
    git("fetch", "origin", "--prune", silencieux=True)
    sortie = []
    for b in git("branch", "-r", "--format=%(refname:short)").splitlines():
        b = b.strip()
        if not b or b.endswith("/HEAD") or b == "origin/main":
            continue
        commits = git("log", "--oneline", f"main..{b}").splitlines()
        if not commits:
            continue
        fichiers = git("diff", "--name-only", f"main...{b}").splitlines()
        sortie.append({
            "nom": b,
            "commits": commits,
            "fichiers": [f for f in fichiers if f],
            "date": git("log", "-1", "--format=%ci", b)[:10],
            "sensibles": [f for f in fichiers if SENSIBLE.search(f)],
        })
    sortie.sort(key=lambda x: x["date"], reverse=True)
    return sortie


def fusion_propre(nom):
    """Vérifie qu'une fusion passerait sans conflit, sans rien modifier.

    ⚠️ ON LIT LE CODE DE SORTIE, PAS LE TEXTE. La forme ancienne de
    `git merge-tree` IMPRIME LE CONTENU DES FICHIERS fusionnés : y chercher la
    chaîne « CONFLICT » ou « <<<<<<< » accuse toute branche qui contient ces
    mots quelque part dans son code ou sa documentation.

    Mesuré le 2026-08-28 : la branche du Standard WhatsApp était déclarée « en
    conflit » à cause d'un `ON CONFLICT(...) DO UPDATE` — l'upsert SQLite — dans
    `whatsapp-agent/agent/memoire.py`, alors que `main` en était l'ANCÊTRE
    DIRECT et que la fusion était une simple avance rapide. Les vingt autres
    branches étaient jugées correctement : le défaut n'accuse que celles qui
    parlent de conflits, et ce sont justement celles qui touchent à git ou à
    SQLite. Une branche saine écartée pour cette raison, c'est du travail perdu.

    La forme moderne (`--write-tree`, git ≥ 2.38) rend **0** quand c'est propre
    et **1** quand ça conflit : c'est un verdict, pas une lecture. Sur un git
    plus ancien, on ne devine pas — on le dit, et la branche n'est pas fusionnée
    automatiquement.
    """
    base = git("merge-base", "main", nom)
    if not base:
        return False, "base introuvable"
    r = subprocess.run(
        ["git", "merge-tree", "--write-tree", "--name-only", "main", nom],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        return True, "propre"
    if r.returncode == 1:
        return False, "conflits"
    return False, "indécidable (git < 2.38) : à vérifier à la main"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fusionner", action="store_true")
    ap.add_argument("--branche", default=None)
    args = ap.parse_args()

    if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        print("⛔ Il faut être sur `main`. Faire : git checkout main")
        return 1
    if git("status", "--porcelain"):
        print("⛔ Le dossier de travail n'est pas propre. Commiter ou ranger d'abord.")
        return 1

    # ⚠️ D'ABORD `main` lui-même : une branche oubliée coûte une fusion, un
    #    `main` en retard coûte le travail refait deux fois.
    retard = main_en_retard()

    liste = branches_en_retard()
    if args.branche:
        liste = [b for b in liste if b["nom"].endswith(args.branche)]
        if not liste:
            print(f"  Aucune branche ne correspond à « {args.branche} ».")
            return 1

    if not liste:
        if retard:
            print("  Aucune branche ne traîne, mais `main` local est en retard : "
                  "faire `git merge origin/main` avant de commencer.")
            return 1
        print("  ✅ Rien ne traîne : tout est déjà dans `main`.")
        return 0

    print(f"\n  {len(liste)} branche(s) ne sont pas dans `main` :\n")
    for b in liste:
        ok, etat = fusion_propre(b["nom"])
        jugee = ecartee(b["nom"])
        marque = "⛔" if jugee else ("✅" if ok else "⚠️ ")
        print(f"  {marque} {b['nom'][7:]:<48} {b['date']}  "
              f"{len(b['commits'])} commit(s)  {len(b['fichiers'])} fichier(s)  [{etat}]")
        if jugee:
            # la décision est écrite : personne ne refait l'enquête
            print(f"        ⛔ écartée : {jugee}")
            print()
            continue
        for c in b["commits"][:3]:
            print(f"        {c}")
        if len(b["commits"]) > 3:
            print(f"        … et {len(b['commits']) - 3} de plus")
        if b["sensibles"]:
            print(f"        ⚠️  touche du sensible : {', '.join(sorted(set(b['sensibles']))[:4])}")
        print()

    if not args.fusionner:
        print("  Rien n'a été modifié. Pour rapatrier :")
        print("      python scripts/rapatrier.py --fusionner")
        print("      python scripts/rapatrier.py --fusionner --branche <nom>\n")
        return 0

    faits, refuses = [], []
    for b in liste:
        # ⛔ UNE BRANCHE ÉCARTÉE NE RENTRE PAS PAR UN `--fusionner` GLOBAL.
        #    Il faut la nommer avec `--branche`, ce qui est un geste conscient.
        jugee = ecartee(b["nom"])
        if jugee and not args.branche:
            refuses.append((b["nom"], "écartée : " + jugee))
            print(f"  ⛔ écartée : {b['nom'][7:]}")
            continue
        ok, etat = fusion_propre(b["nom"])
        if not ok:
            refuses.append((b["nom"], etat)); continue
        r = subprocess.run(["git", "merge", b["nom"], "--no-edit", "-m",
                            f"merge: rapatriement de {b['nom'][7:]} dans main"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            faits.append(b["nom"]); print(f"  ✓ fusionné : {b['nom'][7:]}")
        else:
            subprocess.run(["git", "merge", "--abort"], capture_output=True)
            refuses.append((b["nom"], "échec"))
            print(f"  ⛔ refusé : {b['nom'][7:]}")

    print()
    if faits:
        print(f"  {len(faits)} branche(s) rapatriée(s). Il reste à :")
        print("    1. relire  : git diff --stat origin/main..HEAD")
        print("    2. pousser : git push origin main")
        print("    3. dispatcher la mémoire (journal, CONTEXT, CLAUDE.md)")
        print("    4. redéployer ce qui est concerné (voir CLAUDE.md § Infrastructure)")
    if refuses:
        print(f"\n  {len(refuses)} à traiter à la main :")
        for n, e in refuses:
            print(f"    · {n[7:]} ({e})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
