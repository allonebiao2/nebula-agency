#!/usr/bin/env python3
"""Relit chaque montant de COMMISSION des documents de vente et le recalcule.

⛔ POURQUOI CE SCRIPT EXISTE (2026-09-11)
Le 2026-08-02, la grille est passée à 30 % / 40 %. Les pourcentages ont été
corrigés partout. Mais **l'ancienne grille survivait en FRANCS** :

    « 1 catalogue = 12 500 F · 1 vitrine = 37 500 F »   (07-MISE-EN-LIGNE)
    « QR Google Review 30 000 F → 7 500 F »             (03-GUIDE-CATALOGUE,
                                                         sous un titre « palier 30 % »)

12 500 est 25 % de 50 000. 37 500 est 25 % de 150 000. 7 500 est 25 % de 30 000.
**Aucune recherche de « 25 % » ne pouvait les trouver**, et ils ont survécu cinq
semaines à toutes les relectures. Un chiffre faux dans un guide de vente coûte
la confiance d'un partenaire le jour où il compare avec son virement.

Usage :  python _documents/nebula-agency/vente/_verifier_montants.py
Sortie :  0 si tout concorde, 1 s'il reste un montant à l'ancienne grille.
"""
import io, os, re, sys

# Les prix du tableau 4.1 du contrat, plus les montants d'exemple des guides.
PRIX = {
    30000:  "QR Google Review",
    50000:  "Catalogue",
    150000: "Vitrine",
    200000: "Outil (exemple 200k)",
    300000: "Outil (exemple 300k)",
    500000: "mois type à 500k",
}
BONS  = {0.30: "30 %", 0.40: "40 %"}
MORTS = {0.25: "25 % (ancienne grille)", 0.35: "35 % (ancienne grille)",
         0.10: "10 % (commission de réseau, supprimée)",
         0.05: "5 % (commission de réseau, supprimée)"}

# ⚠️ PIÈGE ÉVITÉ, ET IL A FAILLI COÛTER LE SCRIPT ENTIER.
# Le premier jet ne signalait un montant que si le mot « commission », « palier »
# ou « vous gagnez » se trouvait à moins de 240 caractères. Il est sorti VERT sur
# la ligne même pour laquelle il avait été écrit :
#
#     « montants recalculés à la main sur 7 cas de figure, tous conformes au
#       socle commercial (1 catalogue = 12 500 F · 1 vitrine = 37 500 F) »
#
# Une commission n'est pas toujours annoncée par le mot commission. Un filtre de
# vocabulaire est une SUPPOSITION sur la façon d'écrire, et un contrôle qui
# suppose ne lit plus. On ne filtre donc PLUS sur le contexte : tout montant qui
# tombe juste sur un taux mort est signalé, et les exceptions sont NOMMÉES une
# par une dans PAS_UNE_COMMISSION, avec leur raison.

# ⚠️ CES MONTANTS NE SONT PAS DES COMMISSIONS, même s'ils tombent juste sur un
# ancien taux. Chacun est nommé avec sa raison : un contrôle qui crie au loup
# dix fois n'est plus relancé par personne, et c'est comme ça qu'un vrai défaut
# passe. Si l'un de ces montants change au socle, il change ici aussi.
PAS_UNE_COMMISSION = {
    5000:  "frais de réactivation d'un site coupé (contrat art. 4.1 et 6.2 bis) ; "
           "vaut par hasard 10 % de 50 000 F",
    25000: "valeur affichée du Diagnostic Digital, qui est offert ; "
           "vaut par hasard 5 % de 500 000 F",
    2500:  "l'abonnement de 20 000 F ramené au mois, dans un script de vente",
    10000: "le gain RÉTROACTIF quand la 3e vente fait passer un mois de 30 % à "
           "40 % sur 2 catalogues déjà vendus : 40 000 - 30 000. C'est juste.",
    75000: "borne basse d'un prix cité en exemple, pas une commission",
}

def montants(t):
    for m in re.finditer(r"(\d{1,3}(?:[   ]\d{3})+)\s*F", t):
        yield int(re.sub(r"\D", "", m.group(1))), m.start(), m.end()

def analyser(chemin):
    t = io.open(chemin, encoding="utf-8").read()
    for montant, deb, fin in montants(t):
        if montant in PRIX or montant > 600000:
            continue                                   # c'est un prix
        if any(abs(montant - p * b) < 1 for p in PRIX for b in BONS):
            continue                                   # déjà juste
        if montant in PAS_UNE_COMMISSION:
            continue                                   # voir la table ci-dessus
        for prix, nom in PRIX.items():
            for taux, libelle in MORTS.items():
                if abs(montant - prix * taux) < 1:
                    ligne = t[:deb].count("\n") + 1
                    yield (ligne, montant, nom, prix, libelle,
                           int(prix * 0.30), int(prix * 0.40),
                           t[max(0, deb-80):fin+40].replace("\n", " ").strip())
                    break
            else:
                continue
            break

def main():
    racine = os.path.dirname(os.path.abspath(__file__))
    defauts = 0
    for f in sorted(os.listdir(racine)):
        if not f.endswith((".md", ".html")) or f.startswith("_"):
            continue
        for (l, montant, nom, prix, libelle, b30, b40, ctx) in analyser(os.path.join(racine, f)):
            defauts += 1
            esp = lambda n: f"{n:,}".replace(",", " ")
            print(f"⛔ {f}:{l}")
            print(f"   {esp(montant)} F = {libelle} de {esp(prix)} F ({nom})")
            print(f"   attendu : {esp(b30)} F à 30 %, {esp(b40)} F à 40 %")
            print(f"   … {ctx} …\n")
    if defauts:
        print(f"{defauts} montant(s) à l'ancienne grille. Rien n'est publiable en l'état.")
    else:
        print("Tous les montants de commission concordent avec la grille 30 % / 40 %.")
    return 1 if defauts else 0

if __name__ == "__main__":
    sys.exit(main())
