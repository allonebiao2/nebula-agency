# 2026-06-30 — HH Design (#08) livrée + refonte Speed Shopping

## 1) HH Design — nouvelle vitrine immobilière (#08) · LIVE
- **Client** : HH DESIGN, agence **immobilière**, Cotonou. Blanc/doré/noir. Vitrine + QR, galerie + Maps.
  WhatsApp 0167975626 (⚠️ à confirmer — **même n° que client 04 Gloria**). Logo à venir sur WA.
- **Parti-pris TOTALEMENT distinct** (règle d'or) : éditorial architectural luxe — blanc cassé +
  or champagne + noir d'encre, **Marcellus** (display, inédit) + **Manrope**. Hero asymétrique
  (type + façade SVG), **bandeau manifeste noir**, expertise (marqueurs **losange or**), **galerie
  de biens en LIGNES ÉDITORIALES ALTERNÉES** + filtres + lightbox (≠ bento Djambar, ≠ coverflow
  Speed/Weinkeller, ≠ scatter Miss Cakes), approche 01-02-03 (seule séquence numérotée), motion
  architectural (tracés de lignes dorées, **révélations en rideau** clip-path, parallaxe lent).
- **Tech** : page unique `index.html` (CSS/JS inline), galerie = **scènes SVG architecturales**
  placeholders « à valider » (honnêteté : pas de stock déguisé). Assets générés (favicon/OG/QR
  Pillow+segno). Affiche A4 + 2 QR (PDF).
- **QA** : 0 débordement (mobile inclus), 0 erreur, assets 200, AA, focus, reduced-motion complet.
- **LIVE : https://hh-design.pages.dev** · commit `528c79f`.
- **À REMPLACER** : vrai logo, vraies photos de biens, adresse Maps exacte, vrais avis, confirmer n°.

## 2) Speed Shopping — refonte UI/UX (demande client détaillée)
Objectif : plus compact, moins de friction, offre transport clarifiée.
- **Friction** : retiré boutons hero « Commander maintenant » + « Voir nos services » + bandeau CTA
  « Commander sur WhatsApp ». Nav « Commander » → pointe vers `#concept` (les services) au lieu du
  chat WhatsApp générique. FAB conservé (contact). Fiches service = mécanisme de commande (gardées).
- **Compactage** : hero padding réduit (≈525px), h1/sous-titre/trust resserrés, **boutons plus fins**
  (`.btn-lg` 17→13px), cartes services compactes. Aperçu immédiat : services visibles dès le 1er écran.
- **4 services** (réintègre le sens Bénin→France) dans l'ordre : Commander depuis la France · Colis
  France→Bénin · **Colis Bénin→France** (icône inversée `ic-rev`) · Conteneur. Grille `cats-4`.
  Ajouté **4e fiche** `svc-colis-bj` (lecture-avant-action). + **N.B. ambre très visible** « pas de
  viande, ni périssables/argent/inflammables/interdits ».
- **Flux accueil** : Accroche → grille 4 services → … → **carrousel boutiques/catégories réintégré
  TOUT EN BAS** (récupéré de git `896d762`). 
- **LIVE** : https://speed-weinkeller.pages.dev/speed `?v=20260630f`.

## Reste / suites
- HH : domaine custom (action client). Speed : valider textes/tarifs BJ→FR (placeholder « tarif à la
  prise en charge »).
