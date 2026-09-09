# -*- coding: utf-8 -*-
"""
_llms.py — les deux fichiers que lisent les machines.

    python _outils/_llms.py

Ce qu'ils sont, et pourquoi ils existent :

  /llms.txt    un resume du site en texte brut, pour qu'un assistant qui
               arrive sans contexte sache en dix lignes ce qu'est la maison,
               ce qu'elle vend et ou trouver le reste. (llmstxt.org)

  /tarifs.md   les onze soins et leurs prix, en markdown. Un agent qui compare
               des prestations pour quelqu'un ne rend pas une page, il lit un
               fichier. Un tarif enferme dans du JavaScript ou derriere un
               « nous consulter » est un tarif qui sort des comparaisons.

⚠️ LES DEUX SONT LUS DANS LES PAGES, jamais recopies. Le jour ou Gloria change
   un prix dans `luxury-skin-clinic.html`, on relance cette commande et les
   deux fichiers suivent. Un prix recopie est une deuxieme verite.

⛔ ON N'ECRIT QUE CE QUE LE SITE DIT. Pas d'adresse de rue (Gloria ne l'a
   jamais donnee), pas de note, pas d'avis, pas de delai invente.
"""
import io, os, re, sys, datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAINE = "https://luxuryclub229.com"
GROUPES = {"visage": "Soins du visage", "corps": "Soins du corps",
           "capillaires": "Soins capillaires", "complet": "L'expérience complète"}


def lire(p):
    return io.open(os.path.join(RACINE, p), encoding="utf-8").read()


def soins():
    src = lire("luxury-skin-clinic.html")
    i, j = src.find("const SERVICES=["), src.find("\n];", src.find("const SERVICES=["))
    out = []
    # ⚠️ `d:` est sur la LIGNE SUIVANTE de la fiche : une expression bornée à la
    #    ligne courante ne la voyait jamais, et les descriptions manquaient au
    #    fichier — or c'est la description qui rend une ligne citable.
    for m in re.finditer(r"\{g:'([^']+)',n:'([^']+)'.*?p:(\d+),.*?\n\s*d:\"([^\"]*)\"",
                         src[i:j], re.S):
        out.append({"g": m.group(1), "n": m.group(2).replace("\\'", "'"),
                    "p": int(m.group(3)),
                    "d": m.group(4).replace("\\'", "'")})
    return out


def questions():
    src = lire("luxury-skin-clinic.html")
    i, j = src.find('<section id="questions">'), 0
    if i < 0:
        return []
    j = src.find("</section>", i)
    return [(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", a)).strip(),
             re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", b)).strip())
            for a, b in re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", src[i:j], re.S)]


def fmt(n):
    return "{:,}".format(n).replace(",", " ")


def main():
    s = soins()
    q = questions()
    if len(s) < 5:
        sys.exit("seulement %d soins relevés : le format a bougé" % len(s))
    jour = datetime.date.today().isoformat()
    prix = sorted(x["p"] for x in s if x["p"] > 0)

    # ------------------------------------------------------------ tarifs.md
    t = ["# Tarifs — Luxury Skin Clinic (Luxury Club 229)", "",
         "Clinique esthétique à Cotonou, Bénin. Tous les soins sont réalisés par",
         "Mme Sabrina, esthéticienne diplômée, sur rendez-vous.", "",
         "- Devise : FCFA (XOF)",
         "- Jours et horaires : du lundi au samedi, de 10h à 17h",
         "- Rendez-vous : 24 heures minimum à l'avance, aucun le jour même",
         "- Acompte : 5 100 FCFA, non remboursable, valide le créneau",
         "- Paiement de l'acompte : Mobile Money au 01 67 97 56 26, puis capture sur WhatsApp",
         "- Réservation : %s/luxury-skin-clinic#rdv-booking" % DOMAINE,
         "- Fourchette : %s à %s FCFA" % (fmt(prix[0]), fmt(prix[-1])), ""]
    for g, lab in GROUPES.items():
        liste = [x for x in s if x["g"] == g]
        if not liste:
            continue
        t += ["## " + lab, ""]
        for x in liste:
            t.append("### %s" % x["n"])
            t.append("- Prix : %s FCFA" % fmt(x["p"]))
            if x["d"]:
                t.append("- Description : %s" % x["d"])
            t.append("")
    t += ["---", "", "Dernière mise à jour : %s." % jour,
          "Source : %s/luxury-skin-clinic" % DOMAINE, ""]
    io.open(os.path.join(RACINE, "tarifs.md"), "w", encoding="utf-8", newline="\n").write("\n".join(t))

    # ------------------------------------------------------------- llms.txt
    l = ["# Luxury Club 229", "",
         "> Maison de beauté à Cotonou, Bénin, réunissant trois marques :",
         "> **Luxury Skin Clinic** (clinique esthétique, soins en institut),",
         "> **INA Luxury** (cosmétiques et soins capillaires) et",
         "> **Cozy** (hygiène intime et bien-être).", "",
         "Fondée et dirigée par Ahouangnimon Gloria. Les soins en institut sont",
         "réalisés par Mme Sabrina, esthéticienne diplômée en esthétique médicale",
         "et spécialiste en cosmétologie avancée. Les commandes et les",
         "réservations passent par WhatsApp (+229 01 67 97 56 26).", "",
         "## Les trois univers", "",
         "- [Luxury Skin Clinic](%s/luxury-skin-clinic) : %d soins en institut, de %s à %s FCFA — visage, corps, capillaires et une expérience complète." % (DOMAINE, len(s), fmt(prix[0]), fmt(prix[-1])),
         "- [INA Luxury](%s/ina-luxury) : cosmétiques et soins capillaires, par famille (visage, corps, capillaires, enfant, lèvres) et par routine." % DOMAINE,
         "- [Cozy](%s/cozy) : hygiène intime et bien-être féminin." % DOMAINE, "",
         "## Fichiers utiles", "",
         "- [Tarifs des soins](%s/tarifs.md) : les %d soins et leurs prix, en markdown." % (DOMAINE, len(s)),
         "- [Plan du site](%s/sitemap.xml)" % DOMAINE, ""]
    if q:
        l += ["## Questions fréquentes", ""]
        for a, b in q:
            l.append("### " + a)
            l += ["", b, ""]
    l += ["## Ce que ce site ne dit pas", "",
          "L'adresse exacte de l'institut n'est pas publiée : la clinique se situe",
          "à Cotonou, et le rendez-vous se confirme par WhatsApp. Le site ne",
          "publie aucun avis client ni aucune note.", "",
          "Dernière mise à jour : %s." % jour, ""]
    io.open(os.path.join(RACINE, "llms.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(l))

    print("  tarifs.md : %d soins, de %s à %s FCFA" % (len(s), fmt(prix[0]), fmt(prix[-1])))
    print("  llms.txt  : 3 univers, %d questions reprises de la FAQ visible" % len(q))
    print("  ⚠️ à relancer après tout changement de tarif ou de FAQ.")


if __name__ == "__main__":
    main()
