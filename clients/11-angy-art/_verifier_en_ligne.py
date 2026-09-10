# -*- coding: utf-8 -*-
"""
ANGY ART — le site EN LIGNE dit-il la même chose que le disque ?

À lancer APRÈS chaque déploiement, depuis le PC :

    python clients/11-angy-art/_verifier_en_ligne.py

⚠️ POURQUOI CET OUTIL EXISTE : une session Claude distante ne peut PAS le
   faire elle-même. Mesuré le 2026-09-10 : le proxy de sortie de
   l'environnement bloque `angyart.online` comme `api.cloudflare.com`
   (code 000, `CONNECT tunnel failed, response 403`). Ce script met donc la
   vérification dans les mains de celui qui a le réseau, et sa sortie se colle
   telle quelle dans la conversation.

Ce qu'il regarde, et pourquoi chaque contrôle existe :

  · LES OCTETS, PAS LE CODE HTTP. ⛔ Un 200 ne prouve rien : le 2026-08-04,
    Cloudflare a servi `error code: 502` DANS un fichier CSS répondant 200,
    bon type et bonne taille. On compare les MD5 au disque.

  · LE DOMAINE CONTRE SON ORIGINE `*.pages.dev`. C'est ce qui désigne un cache
    de zone périmé en trois secondes : si l'origine est à jour et que le
    domaine ne l'est pas, ce n'est pas le déploiement, c'est le cache
    (`python scripts/purger.py angy`). Piège rencontré le 2026-09-10, le jour
    du branchement du domaine.

  · UN FICHIER ABSENT DOIT RÉPONDRE 404. Sans `404.html`, Pages sert l'accueil
    en 200 pour toute adresse inconnue, et ce 200 se met en cache un an.

  · LA MUSIQUE : le fichier répond, il pèse ce qu'il doit peser, la page le
    réclame avec sa marque de version, et le crédit est là.

⚠️ UN VRAI `User-Agent` DE NAVIGATEUR : Cloudflare renvoie 403 à un robot qui
   ne se présente pas comme un navigateur, et on croirait le site cassé.
"""
import hashlib
import os
import re
import sys
import urllib.error
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
DOMAINE = "https://angyart.online"
ORIGINE = "https://angy-art.pages.dev"

# ⚠️ `--base` sert à ESSAYER LE SCRIPT LUI-MÊME contre un serveur local, sur
#    `_dist`. Un contrôle qu'on n'a jamais vu réussir ne prouve rien : c'est
#    ainsi qu'on vérifie que ses comparaisons disent vrai avant de s'y fier.
for _i, _a in enumerate(sys.argv):
    if _a == "--base" and _i + 1 < len(sys.argv):
        DOMAINE = ORIGINE = sys.argv[_i + 1].rstrip("/")

NAVIGATEUR = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept": "*/*",
    "Cache-Control": "no-cache",
}

ok, ko = [], []
def bon(m): ok.append(m); print("  [ok] " + m)
def mauvais(m): ko.append(m); print("  [KO] " + m)
def titre(t): print("\n== " + t)


def prendre(url, entetes=None):
    """Renvoie (code, octets, en-têtes). Ne lève pas : un échec est une mesure."""
    e = dict(NAVIGATEUR)
    if entetes:
        e.update(entetes)
    req = urllib.request.Request(url, headers=e)
    # ⚠️ LES NOMS D'EN-TÊTE SONT INSENSIBLES À LA CASSE, et les serveurs ne les
    #    écrivent pas pareil : `http.server` envoie « Content-type », Cloudflare
    #    « content-type ». Un premier jet cherchait « Content-Type » et n'a rien
    #    trouvé — il accusait le serveur d'un défaut qui était dans la sonde.
    def _plat(h):
        return {k.lower(): v for k, v in dict(h or {}).items()}
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(), _plat(r.headers)
    except urllib.error.HTTPError as ex:
        return ex.code, (ex.read() or b""), _plat(ex.headers)
    except Exception as ex:
        return 0, str(ex).encode(), {}


def md5(b):
    return hashlib.md5(b).hexdigest()


def disque(rel):
    p = os.path.join(ICI, rel)
    return open(p, "rb").read() if os.path.exists(p) else None


def main():
    print("\nANGY ART — le site en ligne contre le disque\n  %s" % DOMAINE)

    # ── la page ─────────────────────────────────────────────────────────
    titre("La page d'accueil")
    code, page, ent = prendre(DOMAINE + "/")
    if code != 200:
        mauvais("l'accueil répond %s : rien d'autre n'est mesurable" % (code or "aucune réponse"))
        return 1
    bon("l'accueil répond 200 (%d Ko)" % (len(page) // 1024))

    ref = disque("index.html")
    if ref is None:
        mauvais("index.html est introuvable sur le disque")
    elif md5(page) == md5(ref):
        bon("la page servie est IDENTIQUE au disque (MD5)")
    else:
        mauvais("la page servie DIFFÈRE du disque — déploiement incomplet, "
                "ou cache périmé (essaie `python scripts/purger.py angy`)")

    txt = page.decode("utf-8", "replace")

    # ── les fichiers que la page réclame vraiment ───────────────────────
    # ⚠️ On ne recopie AUCUN chemin : on lit ce que la page demande.
    titre("Les fichiers que la page réclame")
    voulus = []
    for m in re.finditer(r'assets/[A-Za-z0-9_./-]+\.(?:css|js|webp|png|jpg|mp3)(\?v=[0-9a-z]+)?', txt):
        if m.group(0) not in voulus:
            voulus.append(m.group(0))
    # le son est demandé par le script, pas par la page
    js_disque = disque("assets/app.js")
    if js_disque:
        for m in re.finditer(r"assets/sons/[A-Za-z0-9_.-]+\.mp3", js_disque.decode("utf-8", "replace")):
            if m.group(0) not in [v.split("?")[0] for v in voulus]:
                voulus.append(m.group(0))

    manques, differents = [], []
    for rel in voulus:
        nu = rel.split("?")[0]
        c, b, _ = prendre(DOMAINE + "/" + rel)
        if c != 200:
            manques.append("%s (%s)" % (nu, c or "aucune réponse"))
            continue
        d = disque(nu)
        if d is not None and md5(d) != md5(b):
            differents.append(nu)
    bon("les %d fichiers réclamés répondent tous 200" % len(voulus)) if not manques \
        else mauvais("fichier(s) en échec -> " + ", ".join(manques[:4]))
    bon("tous sont identiques au disque (MD5)") if not differents \
        else mauvais("servi(s) différent(s) du disque -> " + ", ".join(differents[:4]))

    # ── la musique ──────────────────────────────────────────────────────
    titre("La musique")
    son_rel = next((v for v in voulus if "/sons/" in v), None)
    if not son_rel:
        mauvais("la page ne réclame aucun fichier de son : la version en ligne "
                "est l'ANCIENNE (celle de l'ambiance synthétisée)")
    else:
        nu = son_rel.split("?")[0]
        c, b, e = prendre(DOMAINE + "/" + nu)
        d = disque(nu)
        if c != 200:
            mauvais("%s répond %s" % (nu, c or "aucune réponse"))
        else:
            bon("le morceau répond 200 (%d Ko)" % (len(b) // 1024))
            if d and md5(d) == md5(b):
                bon("il est identique au fichier du disque (MD5)")
            elif d:
                mauvais("le morceau servi DIFFÈRE du disque")
            ct = (e.get("content-type") or "").lower()
            bon("il est servi comme de l'audio (%s)" % ct) if "audio" in ct \
                else mauvais("type MIME inattendu : %r" % ct)

    js = txt  # la marque de version du son vit dans app.js, pas dans la page
    c, bjs, _ = prendre(DOMAINE + "/assets/app.js")
    sjs = bjs.decode("utf-8", "replace") if c == 200 else ""
    bon("le script en ligne porte bien le nouveau moteur") if "ambiance.mp3" in sjs \
        else mauvais("le script en ligne NE contient PAS `ambiance.mp3` : "
                     "c'est l'ancienne version qui est servie")
    bon("l'ancienne ambiance synthétisée a bien disparu") if "createOscillator" not in sjs \
        else mauvais("`createOscillator` est encore là : l'ancienne ambiance survit")
    bon("le pied crédite la musique") if "Tama" in txt \
        else mauvais("le crédit « Tama's Little Music Shop » manque dans la page servie")

    # ── le cache : le domaine contre son origine ────────────────────────
    titre("Le cache")
    co, po, _ = prendre(ORIGINE + "/")
    if co != 200:
        print("  (l'origine %s répond %s — contrôle sauté)" % (ORIGINE, co))
    elif md5(po) == md5(page):
        bon("le domaine sert exactement ce que sert son origine")
    else:
        mauvais("l'origine et le domaine ne servent PAS la même page : c'est le "
                "CACHE DE ZONE, pas le déploiement -> `python scripts/purger.py angy`")

    # ── un fichier absent ───────────────────────────────────────────────
    titre("Un fichier qui n'existe pas")
    c, _, _ = prendre(DOMAINE + "/ceci-nexiste-pas-" + os.urandom(4).hex() + ".html")
    bon("une adresse inconnue répond 404") if c == 404 \
        else mauvais("une adresse inconnue répond %s : sans 404.html, Pages sert "
                     "l'accueil en 200 et ce 200 se met en cache un an" % c)

    print("\n  %d vert(s), %d rouge(s)" % (len(ok), len(ko)))
    if ko:
        print("\n  À CORRIGER :")
        for m in ko:
            print("    · " + m)
        return 1
    print("  Le site en ligne dit exactement ce que dit le disque.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
