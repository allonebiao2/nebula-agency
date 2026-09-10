# -*- coding: utf-8 -*-
"""
ANGY ART — publier le site, en une seule commande.

    python clients/11-angy-art/_publier.py
    python clients/11-angy-art/_publier.py --vite     # saute le contrôle qualité

⚠️ POURQUOI CE SCRIPT EXISTE : pousser sur GitHub NE MET RIEN EN LIGNE. Ce sont
   deux gestes différents — enregistrer un document ne l'imprime pas. Le
   2026-09-10, la musique d'Angy Art a dormi des heures dans `main` pendant que
   le site servait encore l'ancienne version, et le 2026-08-22 six oeuvres ont
   fait exactement pareil (six images en 404). Une commande unique, c'est une
   étape qu'on ne peut plus oublier à moitié.

⚠️ Une session Claude distante ne peut PAS lancer ceci : le proxy de sortie
   bloque `api.cloudflare.com`. Ce script tourne sur le PC, qui a le réseau et
   les jetons de `secrets/`.

Il enchaîne : récupérer `main` · contrôle qualité · composer `_dist` ·
déployer · purger le cache · vérifier ce qui est réellement servi.
Il s'arrête net à la première étape qui échoue, en disant quoi faire.
"""
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(os.path.dirname(ICI))
PROJET = "angy-art"
VITE = "--vite" in sys.argv


def etape(n, total, titre):
    print("\n" + "=" * 62)
    print("  %d/%d  %s" % (n, total, titre))
    print("=" * 62)


def lancer(cmd, ou=None, stop=None):
    """Exécute et laisse tout s'afficher. Arrête net en cas d'échec."""
    print("  $ " + " ".join(cmd) + "\n")
    try:
        r = subprocess.run(cmd, cwd=ou or RACINE)
    except FileNotFoundError:
        raise SystemExit("\n  ⛔ commande introuvable : %s\n     %s"
                         % (cmd[0], stop or ""))
    if r.returncode != 0:
        raise SystemExit("\n  ⛔ ARRÊT à cette étape (code %d).\n     %s"
                         % (r.returncode, stop or "Corrige, puis relance ce script."))
    return r


def wrangler():
    """⚠️ Sur Windows, l'exécutable s'appelle `wrangler.cmd`. Et `npx wrangler`
       ne marche plus sur ce PC (paquet supprimé avec les node_modules)."""
    for nom in ("wrangler", "wrangler.cmd"):
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    raise SystemExit(
        "  ⛔ wrangler introuvable.\n"
        "     Installe-le une fois pour toutes :  npm install -g wrangler@3\n"
        "     (⚠️ pas `npx wrangler` : il ne marche plus sur ce PC)")


def main():
    total = 5 if VITE else 6
    n = 0

    n += 1
    etape(n, total, "Récupérer ce qui est sur GitHub")
    lancer(["git", "pull", "origin", "main"],
           stop="Un conflit ? Résous-le, puis relance.")

    if not VITE:
        n += 1
        etape(n, total, "Contrôle qualité (quelques minutes)")
        print("  ⚠️ La maison ne déploie pas sur un QC rouge. Pour sauter cette")
        print("     étape en connaissance de cause : --vite\n")
        lancer([sys.executable, "_qc.py"], ou=ICI,
               stop="Le QC est rouge. Ne déploie pas : corrige d'abord.")

    n += 1
    etape(n, total, "Composer ce qui part en ligne")
    print("  ⚠️ Un déploiement Cloudflare est un INSTANTANÉ COMPLET : ce qui")
    print("     manque ici disparaît du site.\n")
    lancer([sys.executable, "_dist.py"], ou=ICI)

    n += 1
    etape(n, total, "Déployer sur Cloudflare Pages")
    lancer([wrangler(), "pages", "deploy", os.path.join(ICI, "_dist"),
            "--project-name=" + PROJET, "--branch=main"],
           stop="Pas connecté ? `wrangler login`, ou pose CLOUDFLARE_API_TOKEN.")

    n += 1
    etape(n, total, "Vider le cache")
    print("  ⚠️ CETTE ÉTAPE N'EST PAS FACULTATIVE. Le 2026-09-10, le cache de")
    print("     zone servait encore l'ancien HTML APRÈS un déploiement réussi.\n")
    r = subprocess.run([sys.executable, os.path.join("scripts", "purger.py"), "angy"],
                       cwd=RACINE)
    if r.returncode != 0:
        print("\n  ⚠️ La purge a échoué (jeton de purge absent ?). Le déploiement,")
        print("     lui, est passé. Si le site montre encore l'ancienne version,")
        print("     c'est le cache : purge à la main depuis le tableau de bord.")

    n += 1
    etape(n, total, "Vérifier ce qui est RÉELLEMENT servi")
    print("  On compare les octets servis à ceux du disque. ⛔ Un 200 ne prouve")
    print("     rien : Cloudflare a déjà servi « error code: 502 » dans un CSS")
    print("     qui répondait 200.\n")
    r = subprocess.run([sys.executable, "_verifier_en_ligne.py"], cwd=ICI)

    print("\n" + "=" * 62)
    if r.returncode == 0:
        print("  ✅ EN LIGNE ET VÉRIFIÉ — https://angyart.online/")
        print("     Le son part au premier contact avec la page.")
    else:
        print("  ⚠️ Déployé, mais la vérification a trouvé quelque chose.")
        print("     Colle ce qui précède dans la conversation.")
    print("=" * 62)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
