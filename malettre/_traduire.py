# -*- coding: utf-8 -*-
"""MA LETTRE À… · fabrique les pages anglaises à partir des pages françaises.

    python malettre/_traduire.py

Le français est la SOURCE : on n'édite jamais `en/*.html`. Le dictionnaire
`i18n/en.txt` dit, phrase par phrase, ce que devient chaque morceau.

⛔ IL REFUSE D'ÉCRIRE si une phrase française du dictionnaire est introuvable
dans sa page : une phrase changée en français et oubliée ici donnerait une
page anglaise à moitié française, sans un mot. Le contrôle des restes
(`_qc_langues.py`) cherche ensuite tout ce qui serait resté en français.
⛔ Les prix et les droits ne passent pas par ici : seuls les mots changent,
et la caisse recalcule tout.
"""
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
DICO = ICI / "i18n" / "en.txt"
SORTIE = ICI / "en"
PAGES = ["creer.html", "paiement.html", "merci.html"]


def lire_dico(chemin=DICO):
    """{section: [(fr, en), ...]} dans l'ordre du fichier."""
    sections, cour, fr = {}, None, None
    for n, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        if ligne.startswith("== "):
            cour = ligne[3:].strip()
            sections.setdefault(cour, [])
        elif ligne.startswith("FR: "):
            if fr is not None:
                sys.exit("⛔ %s:%d : deux FR de suite" % (chemin.name, n))
            fr = ligne[4:]
        elif ligne.startswith("EN: "):
            if fr is None or cour is None:
                sys.exit("⛔ %s:%d : EN sans FR" % (chemin.name, n))
            sections[cour].append((fr, ligne[4:], n))
            fr = None
        elif ligne.strip() and not ligne.startswith("#"):
            sys.exit("⛔ %s:%d : ligne inattendue : %r" % (chemin.name, n, ligne[:60]))
    if fr is not None:
        sys.exit("⛔ %s : un FR sans EN à la fin" % chemin.name)
    return sections


def traduire(texte, paires, nom):
    manquent = []
    for fr, en, n in paires:
        if fr not in texte:
            manquent.append("ligne %d : %s" % (n, fr[:70]))
            continue
        texte = texte.replace(fr, en)
    if manquent:
        sys.exit("⛔ %s : %d phrase(s) introuvable(s), rien n'est écrit :\n  %s"
                 % (nom, len(manquent), "\n  ".join(manquent)))
    return texte


def main():
    dico = lire_dico()
    SORTIE.mkdir(exist_ok=True)
    for nom in PAGES:
        if nom not in dico:
            sys.exit("⛔ aucune section « %s » dans %s" % (nom, DICO.name))
        en = traduire((ICI / nom).read_text(encoding="utf-8"), dico[nom], nom)
        (SORTIE / nom).write_text(en, encoding="utf-8")
        print("en/%s : %d phrases, %d octets" % (nom, len(dico[nom]), len(en.encode("utf-8"))))


if __name__ == "__main__":
    main()
