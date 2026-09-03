# -*- coding: utf-8 -*-
"""
VÉRIFIER LE PARC — chaque site en ligne sert-il bien ce qu'il y a dans le dépôt ?

    python scripts/verif_parc.py

⚠️ POURQUOI CE SCRIPT EXISTE. Un `git push` ne déploie rien, et trois clients
ont déjà traîné des jours avec un cran de retard sans que personne le voie. La
tentation est de comparer **la date du dernier déploiement** à celle du dernier
commit : mesuré le 2026-08-29, cette méthode déclarait **sept sites sur quinze
en retard**, et **un seul l'était**. Un commit peut ne toucher qu'un
`CONTEXT.md` ; un déploiement du même jour peut être antérieur au commit.

**Ce qui tranche, c'est le corps servi.** On télécharge la page et on la
compare, octet pour octet, au fichier du dépôt qui est censé la produire.

⚠️ DEUX PIÈGES, TOUS DEUX MESURÉS ICI :

1. **Cloudflare INJECTE une ligne dans le HTML servi** (Web Analytics,
   `challenge-platform`) sur les domaines qui ont l'analytique. La comparaison
   au MD5 échoue alors que les pages sont identiques. On retire ces lignes —
   et **on dit combien on en a retiré**, sinon on masque une vraie différence
   sous prétexte de nettoyage.
2. **Un agent non navigateur reçoit 403** sur `*.pages.dev` (filtrage de bots).
   D'où l'en-tête de navigateur.

⚠️ Et un **200 ne prouve rien** : Cloudflare met les erreurs en cache À LA
PLACE du fichier (2026-08-04). On regarde donc aussi le corps.
"""
import hashlib
import os
import sys
import urllib.request

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

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ce que Cloudflare ajoute lui-même à la page servie
INJECTE = ("static.cloudflareinsights.com", "__CF$cv$params",
           "/cdn-cgi/challenge-platform")

# (nom, url, fichier du dépôt censé être servi ; None = on regarde juste la santé)
SITES = [
    ("Grain d'Esthetique", "https://graindesthetique.com/",
     "clients/01-grain-esthetique/grain-esthetique-LIVE.html"),
    ("Djambar Team", "https://djambarteam.com/",
     "clients/05-saeir-thiam-bijouterie/index.html"),
    ("Miss cakes", "https://miss-cakes.pages.dev/",
     "clients/06-miss-cakes/index.html"),
    ("Speed x Weinkeller", "https://speed-weinkeller.pages.dev/",
     "clients/07-speed-weinkeller-ck/index.html"),
    ("  \\ speed", "https://speed-weinkeller.pages.dev/speed.html",
     "clients/07-speed-weinkeller-ck/speed.html"),
    ("  \\ weinkeller", "https://speed-weinkeller.pages.dev/weinkeller.html",
     "clients/07-speed-weinkeller-ck/weinkeller.html"),
    ("HH Design", "https://hh-design.pages.dev/",
     "clients/08-hh-design/index.html"),
    ("Au Braise d'Or", "https://au-braise-dor.pages.dev/",
     "clients/09-au-braise-dor/experience/out/index.html"),
    ("Hillary M. Styl", "https://hillary-m-styl.pages.dev/",
     "clients/10-hillary-m-styl/vitrine.html"),
    ("Angy Art", "https://angy-art.pages.dev/",
     "clients/11-angy-art/_dist/index.html"),
    ("Mon Benin", "https://mon-benin.pages.dev/", "benin-mon-pays/index.html"),
    ("Boussole", "https://boussole-19d.pages.dev/", "boussole/_dist/index.html"),
    ("  \\ app", "https://boussole-19d.pages.dev/app", "boussole/_dist/app.html"),
    ("NEBULA Agency", "https://www.nebula-agency.online/",
     "00-nebula-agency/nebula_agency_v9.html"),
    # ⚠️ ceux-ci n'ont pas de source comparable dans le dépôt : on regarde
    #    seulement qu'ils répondent et que le corps n'est pas une erreur.
    ("PISTE", "https://piste.nebula-agency.online/", None),
    ("Luxury Club 229", "https://luxuryclub229.com/", None),
    ("Partenaires", "https://partenaires.nebula-agency.online/", None),
]


def sans_injection(txt):
    """Retire ce que Cloudflare ajoute, et dit combien de lignes sont parties."""
    lignes = txt.replace("\r\n", "\n").split("\n")
    gardees = [l for l in lignes if not any(m in l for m in INJECTE)]
    return "\n".join(gardees), len(lignes) - len(gardees)


def main():
    retard, casses = [], []
    for nom, url, local in SITES:
        try:
            r = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(r, timeout=45) as f:
                brut = f.read()
        except Exception as e:
            print(u"  %-20s ⛔ injoignable : %s" % (nom, str(e)[:60]))
            casses.append(nom)
            continue

        servi = brut.decode("utf-8", "replace")
        # ⚠️ un 200 ne prouve rien : Cloudflare met les erreurs EN CACHE
        if "error code" in servi[:2000].lower():
            print(u"  %-20s ⛔ CORPS D'ERREUR SERVI (cache empoisonne ?)" % nom)
            casses.append(nom)
            continue

        if not local:
            print(u"  %-20s ✅ repond, %d Ko (pas de source comparable ici)"
                  % (nom, len(brut) / 1024))
            continue

        p = os.path.join(RACINE, local.replace("/", os.sep))
        if not os.path.exists(p):
            print(u"  %-20s ⚠️  source absente du disque : %s" % (nom, local))
            continue

        a, n = sans_injection(servi)
        b, _ = sans_injection(open(p, "rb").read().decode("utf-8", "replace"))
        if hashlib.md5(a.encode()).hexdigest() == hashlib.md5(b.encode()).hexdigest():
            print(u"  %-20s ✅ identique au depot%s"
                  % (nom, (u"   (%d ligne injectee par Cloudflare)" % n) if n else ""))
        else:
            print(u"  %-20s ⛔ EN RETARD : servi %d o, depot %d o"
                  % (nom, len(servi), len(b)))
            retard.append(nom)

    print("")
    if casses:
        print(u"  ⛔ injoignables ou malades : %s" % ", ".join(casses))
    if retard:
        print(u"  ⛔ %d site(s) a redeployer : %s" % (len(retard), ", ".join(retard)))
        return 1
    if not casses:
        print(u"  ✅ tout le parc sert bien ce qu'il y a dans le depot.")
    return 1 if casses else 0


if __name__ == "__main__":
    sys.exit(main())
