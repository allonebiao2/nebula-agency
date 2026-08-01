# -*- coding: utf-8 -*-
"""
Pose les informations réelles d'Hillary dans la vitrine, avant mise en ligne.
Idempotent : peut être relancé sans dégât. Lecture/écriture strictement en UTF-8
(jamais PowerShell Get-Content/WriteAllText, qui produit du mojibake).
"""
import io, re, sys

SRC = r"C:/Users/USER/nebula-agency/clients/10-hillary-m-styl/vitrine.html"

WA_BRUT    = "22951374793"       # format wa.me, sans + ni espaces
WA_LISIBLE = "+229 51 37 47 93"
SITE       = "https://hillary-m-styl.pages.dev"

with io.open(SRC, encoding="utf-8") as f:
    h = f.read()
avant = h

def sub1(motif, remplacement, etiquette):
    """Remplace exactement une occurrence, ou s'arrête en expliquant pourquoi."""
    global h
    neuf, n = re.subn(motif, remplacement, h, count=1)
    if n != 1:
        # idempotence : si la valeur finale est déjà là, ce n'est pas une erreur
        print(f"   · {etiquette} : déjà posé (ou motif absent)")
        return
    h = neuf
    print(f"   ✓ {etiquette}")

# 1) le numéro WhatsApp — sans lui, aucune commande n'arrive
sub1(r'var WHATSAPP = "22900000000";',
     f'var WHATSAPP = "{WA_BRUT}";', "numéro WhatsApp")

# 2) l'atelier — on ne remplace pas un « à confirmer » par une invention :
#    on n'écrit que ce qui est vrai (le point de retrait se donne sur WhatsApp).
sub1(r'adresse : "Adresse de l\'atelier à confirmer",',
     'adresse : "Retrait sur rendez-vous · le point de retrait vous est donné sur WhatsApp",',
     "adresse de l'atelier")
sub1(r'horaires: "Horaires à confirmer",',
     'horaires: "10 à 14 jours · 4 à 6 jours en express",',
     "délai de confection (remplace les horaires)")
sub1(r'wa_lisible: "Numéro à confirmer"',
     f'wa_lisible: "{WA_LISIBLE}"', "numéro lisible")

# 3) l'étiquette « Horaires » ne décrit plus le contenu de sa carte
sub1(r'<div class="lab">Horaires</div>',
     '<div class="lab">Confection</div>', "étiquette de la carte")

# 4) l'URL canonique et l'aperçu de partage (le site se partage sur WhatsApp)
sub1(r'<meta property="og:type" content="website">',
     f'<meta property="og:url" content="{SITE}">\n'
     f'<link rel="canonical" href="{SITE}">\n'
     '<meta property="og:type" content="website">',
     "URL canonique + og:url")

# 5) le bandeau d'avertissement du haut de script n'a plus lieu d'être
h = h.replace(
    "   ⚠️  ZONE À COMPLÉTER PAR NEBULA AVANT MISE EN LIGNE\n"
    "   Tout ce qui suit est en attente des informations de la cliente.\n"
    "   Ne rien inventer : ces valeurs partent chez de vrais clients.",
    "   RÉGLAGES DE LA BOUTIQUE\n"
    "   Numéro WhatsApp posé le 2026-08-01 (fourni par Mongazi).\n"
    "   Restent des valeurs d'exemple : frais d'expédition, délais, catalogue, photos.")
h = h.replace("// ⚠️ NUMÉRO WHATSAPP — à confirmer avec Hillary avant toute diffusion.\n"
              "//    Format international sans + ni espaces. Ex. Bénin : 229XXXXXXXX\n",
              "// Numéro WhatsApp d'Hillary (format international, sans + ni espaces).\n")
h = h.replace("// ⚠️ COORDONNÉES DE L'ATELIER", "// Coordonnées de l'atelier")

if h == avant:
    print("Aucun changement : tout était déjà en place.")
    sys.exit(0)

with io.open(SRC, "w", encoding="utf-8", newline="") as f:
    f.write(h)

# garde-fous : ce qui doit avoir disparu de la page publique
for interdit in ["22900000000", "à confirmer", "ZONE À COMPLÉTER"]:
    if interdit in h:
        print(f"⚠️  RESTE « {interdit} » dans la page")
        sys.exit(1)
print("OK — vitrine à jour, aucun placeholder public restant.")
