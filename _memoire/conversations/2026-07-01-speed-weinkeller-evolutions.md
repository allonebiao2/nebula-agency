# 2026-07-01 — Speed × Weinkeller (#07) : grande vague d'évolutions

Session très dense sur le client 07 (hub 2 mondes BY CK). LIVE **https://speed-weinkeller.pages.dev** (`?v=20260701m`). Tout testé (puppeteer/Edge), déployé (Cloudflare Pages), commité + poussé.

## Speed Shopping
- **Refonte UX** : 4 services (Commander depuis la France · Colis FR→BJ · **Colis BJ→FR** ajouté, icône inversée · Conteneur) en grille compacte sous l'accroche, **N.B. ambre « pas de viande »** ; carrousel boutiques réintégré **en bas** ; boutons hero « Commander maintenant »/« Voir nos services » retirés.
- **Typo compacte mobile** (page « trop chargée ») : héros 42→31px, sections resserrées, **carte vol du héros compactée** → les 4 offres remontent (visibles dès le 1er écran). Scopé `.w-speed` (Weinkeller intact).
- **Bouton « Commander » retiré de la nav** (entrée) ; barre mobile du bas = **« Appeler » seul** (WhatsApp retiré, à côté d'Appeler).

## Weinkeller
- **Vrai logo de marque** (blason WEINKELLER by CK, détouré flood-fill → WebP transparent) : loader (grand, animé halo+reflet), nav (44px), favicon/apple/OG régénérés.
- **3 fiches services animées** (nav = services) — animations DISTINCTES : **Commande spéciale** (import FR/DE→BJ, motif route qui se dessine) · **Accompagnement événementiel** (motif flûtes+bulles) · **Bar à domicile** (motif bouteilles sur étagère). Réutilise le moteur `.svc-sheet`, trigger élargi `[data-svc]`, CTA visibles d'emblée, accents or.
- **Bannière provenance** 🇫🇷🇩🇪 « Importées directement de France & d'Allemagne » (drapeaux fondus en dégradé peu opaque + voile côté texte) → **déplacée dans le héros** (haut) ; **carrousel champagnes déplacé en bas** (section « En vedette »). Héros passé en `flex-start` (titre visible).
- **8 catégories** dans la sélection (Vins·Champagnes·Whiskys·Tequila·Rhum·Gin·Pastis·Vodka) ; les 6 sans produit = chip « bientôt » → **état vide « commande spéciale »**.
- **Architecture = drawer DROIT global** ouvert par un **bouton flottant BRILLANT** (or lustré, animé) : à **gauche**, **auto-masqué** quand « Parcourir par catégorie » (#caveOpen) est à l'écran (IO), tout déplié à l'ouverture. + **barre de recherche** de boissons (filtre live nom/marque/catégorie, compteur, clear, Entrée→sélection). `#selection` en pleine largeur.
- **Pop-up coffrets cadeaux** : s'affiche **à chaque visite** (4,5 s après l'entrée, à chaque rechargement — blocage sessionStorage retiré, exit-intent souris-haut + retour d'onglet), **animation d'attention** (pop rebond + halo pulsé + gift qui frétille), garde anti-flicker 6 s.

## Commun (les 2 pages)
- **Bruitage de touché raffiné** (Web Audio synthétisé, accordé par univers : Weinkeller feutré/grave, Speed clair/net ; déblocage iOS, compresseur, débounce). Bug corrigé : `last=-1` pour que le 1er touché sonne.
- **Perf** : audit (60 fps, 0 erreur) ; canvas golddust en `requestIdleCallback` + déjà IO-pause. **Révélations distinctes par zone** Weinkeller (rise/tilt/pour/unfurl/left/blur/zoom + drapeaux qui se posent).
- **Cibles tactiles** corrigées (points coverflow 9→20×40, sub-row/close ≥44).
- **Nettoyage** : mentions « exemple à valider » / « à confirmer » retirées (avis + contact) — rappel des manques fait hors-site.
- **Bloc légal en pied** (2 pages) : bande (alcool/majeurs · articles interdits) + panneau **Informations légales** (confidentialité · conditions & usage acceptable · mentions), contenu adapté par marque.
- **Affiche A4 imprimable + QR** régénérée (`assets/docs/Affiche_BY_CK_A4.pdf`, QR vers URLs live).

## ⚠️ Piège re-rencontré
Bump de version via **PowerShell `Get-Content -Raw`/`WriteAllText` = MOJIBAKE** (accents doublés, « é » cassé). Détecté + corrigé (restore git + refait via **Node fs**). Depuis : tous les bumps/sync passent par Node ou Python UTF-8. Voir [[feedback_affiche-qr-toujours]].

## Reste (infos client à fournir)
Vrais avis · produits des 6 catégories « bientôt » · email Speed réel (contact@speedshopping.com = placeholder) · adresse Maps exacte Weinkeller · horaires · vrais liens réseaux · n° RCCM/IFU pour mentions légales.
