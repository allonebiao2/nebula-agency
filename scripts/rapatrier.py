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

def git(*a, silencieux=False):
    r = subprocess.run(["git"] + list(a), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0 and not silencieux:
        print(f"  ⛔ git {' '.join(a)} : {(r.stderr or '').strip()[:200]}")
    return (r.stdout or "").strip()

# les chemins qui exigent un regard humain avant d'être fusionnés
SENSIBLE = re.compile(
    r"(vente/|CONTRAT|SOCLE|server\.py|_worker\.js|secrets/|CLAUDE\.md)", re.I)


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
    """Vérifie qu'une fusion passerait sans conflit, sans rien modifier."""
    base = git("merge-base", "main", nom)
    if not base:
        return False, "base introuvable"
    arbre = git("merge-tree", base, "main", nom, silencieux=True)
    if "<<<<<<<" in arbre or "CONFLICT" in arbre:
        return False, "conflits"
    return True, "propre"


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

    liste = branches_en_retard()
    if args.branche:
        liste = [b for b in liste if b["nom"].endswith(args.branche)]
        if not liste:
            print(f"  Aucune branche ne correspond à « {args.branche} ».")
            return 1

    if not liste:
        print("  ✅ Rien ne traîne : tout est déjà dans `main`.")
        return 0

    print(f"\n  {len(liste)} branche(s) ne sont pas dans `main` :\n")
    for b in liste:
        ok, etat = fusion_propre(b["nom"])
        marque = "✅" if ok else "⚠️ "
        print(f"  {marque} {b['nom'][7:]:<48} {b['date']}  "
              f"{len(b['commits'])} commit(s)  {len(b['fichiers'])} fichier(s)  [{etat}]")
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
