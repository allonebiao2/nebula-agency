# Session 2026-07-13 — Refonte UI Boussole (connexion + app cyberpunk) + affiche/carte Luxury Club 229

## 1. Boussole — nav hamburger-pur (tranche 1, dans l'app live `boussole/`)
Refonte de la navigation demandée (« CCEI ») : suppression de la barre du bas + FAB, **hamburger = menu principal** (tiroir plein écran : 4 sections en gros — Mes Ventes · La Caisse · Bilan & Évolution · Réglages — puis Accueil/Carnet/Stock, puis compte/thème/aide).
- **Accueil** : gros bouton **VENDRE** en tête (dégradé ambre).
- **Réglages → Mon profil** : nouveau **module Photo de profil** (upload → redimensionnement canvas ~256px → base64 dans `profil.photo`, avatar dans le tiroir + carte profil, synchro cloud).
- Label **La Caisse** posé sur l'écran des dépenses (vue analytique à venir).
- Fichiers : `boussole/assets/js/{app.js,ui.js,config.js}`, `boussole/assets/css/app.css`, `index.html`, `sw.js`. Version bumpée `?v=20260712a`. Testé en navigateur headless (boutique démo), 0 erreur console.
- **16 décisions de conception verrouillées** via questions (mémoire d'outil réutilisable) : nav hamburger pur · coûts « les deux » (produit + à la vente + étiquetage dépenses, anti double-compte) · La Caisse = vue analytique au-dessus des dépenses · tri VENDRE = fréquence 30 j + récence · pas de FAB · bandeaux coach franc (chiffre+cause+geste) · états vides qui guident · 4 donuts · bénéfice net = def actuelle (CA − coûts directs − dépenses expl. − charges prorata) · net/produit = marge de contribution (pas d'allocation loyer) · crédit compté à la vente · trésorerie = solde espèces vivant · deltas flèche+%+montant seuil ±3% · 1-2 bandeaux max · seuils équilibrés (concentration 50%/marge 15%/dépense 2×) · santé /100 rentabilité d'abord.

## 2. Boussole — REFONTE v2 « cyberpunk / Liquid Glass » (prototype `boussole/_proto/`, point par point)
Nouvelle direction visuelle demandée par Mongazi, construite **écran par écran dans des fichiers d'aperçu** (non destructif, l'app live reste intacte jusqu'à validation complète). Skills appliqués : ui-ux-pro-max, impeccable, design-taste-frontend.

### `_proto/connexion.html` — écran de connexion complet
- **Fond skyline néon** (images fournies `_partage/image boussole PC/portable.PNG` → converties `boussole/assets/img/skyline-{pc,mobile}.webp`, 9:16 mobile / 16:9 PC via `<picture>`) + overlay noir 70%.
- **Carte Liquid Glass** centrée (backdrop-blur, bordure verre, reflet, ombre interne + portée).
- **Logo compas néon cyan** (SVG) qui pulse + halo (fond « disque noir » corrigé). Exporté en PNG : `boussole/assets/icons/logo-boussole-{neon,flat}.png`.
- Titre « PRENDS LE CONTRÔLE. » (Bricolage Grotesque 800).
- **Champs baby-proof** Liquid Glass (néon cyan au focus) + case « Rester connecté » cochée.
- **Auth complète** : état login/register (vanilla `data-mode`), prénom en inscription, mot de passe oublié, bouton principal (flash émeraude au succès), séparateur OU, **bouton Google**, liens de bascule. Câblé au **vrai client Supabase** du projet (`signInWithPassword`, `signUp` avec `data.prenom`, `signInWithOAuth` Google, `resetPasswordForEmail`) + gestion du retour OAuth.
- **Transition de succès « Découpe de Bande Dessinée »** (remplace un 1er effet glitch) : flash émeraude → carte qui **se désintègre en points demi-teinte CMJ** (mask statique + fondu, léger sur mobile) → **panneau BD à bord d'encre zig-zag** (magenta→violet→cyan + trame) qui balaie → révèle l'accueil. ~0,4-0,5s.
- **Sound design** (Web Audio synthétisé, sans fichier) : whoosh d'ouverture + snap au succès. Baseline mobile appliquée d'office (déverrouillage iOS silent buffer + compresseur + gain boosté mobile).
- Compaction anti-scroll, `align-items: safe center` (logo jamais coupé). Bug attrapé : `.home{display:grid}` écrasait l'attribut `hidden`.

### `_proto/app.html` — shell de l'app (post-login)
- **Header fixe Liquid Glass** : hamburger (encrage BD, lueur cyan au survol) · mini-compas central qui pulse · avatar vide.
- **Drawer « slide-in comics »** : glisse depuis la gauche (0,3s, ease-out-back), overlay flou, fermeture overlay/X/Échap ; PC = largeur fixe 320px (dashboard visible à droite).
- **Menu = profil dynamique** (badge couleur selon rôle : émeraude admin / violet collab, via `ADMIN_EMAILS` + session Supabase, sinon démo) + **boutons néon** avec sons hover (micro-clic 0,03s/15%) + click (double bip). Un seul AudioContext réutilisé (le code fourni en créait un par clic = crash après ~6 → corrigé).
- **8 sections** : Accueil (rouge écarlate) · Catalogue (jaune) · Mes ventes (vert) · Mes dépenses (crimson) · La caisse (cyan) · Le bilan (violet) · Carnet clients (orange) · Mon équipe (bleu électrique). Indicateur actif permanent, élévation au survol, enfoncement `scale(.95)` + flash au clic. Footer Paramètres + Déconnexion (rouge brique → rouge vif, `signOut` Supabase).
- **Contrainte zéro-scroll** : `nav flex:1` centré (profil haut / boutons milieu / footer bas), paddings/gaps `vh`-adaptatifs → tient d'un écran jusqu'à ~500px de haut.

### Supabase / Google OAuth — CONFIGURÉ avec Mongazi (guidage pas à pas)
Provider Google **activé** : identifiant OAuth créé dans Google Cloud (gratuit, sans CB) + collé dans Supabase Auth + redirect URLs (`http://localhost:8790/**`). Callback : `https://xukduhqqfzogisoimhyo.supabase.co/auth/v1/callback`. Reste : redirect URL de prod à ajouter le moment venu.

## 3. Luxury Club 229 (client 04 Gloria) — affiche + carte de visite + QR fonctionnel
Demande initiale enfin traitée. **Hub luxuryclub229.com** (noir & or, logo LC), pas la vitrine Skin Clinic.
- **Affiche A4** + **carte de visite** noir & or, logo `logo-luxury-club-229.png` intégré seamless, 3 univers (INA Luxury · Cozy · Luxury Skin Clinic), WhatsApp +229 01 67 97 56 26, Cotonou, sur RDV. Bien proportionné, **zéro débordement** (vérifié à l'œil sur le rendu).
- **QR régénéré et VÉRIFIÉ par décodage** (`jsqr`) → décode exactement `https://luxuryclub229.com`. Fonctionnel.
- Livrables dans `clients/04-luxury-skin-clinic/assets/docs/` : `Affiche_Luxury_Club_229_A4.{pdf,png,svg}`, `Carte_Visite_Luxury_Club_229.{pdf,png,svg}`, `qr-luxury-club-229.png`.

## 4. Technique / apprentissages
- **Génération print sans navigateur** : composer en **SVG** (logo + QR en base64, texte or via dégradé, tout positionné dans le viewBox = zéro débordement garanti) → **sharp** rend en PNG 300 DPI → **pdfkit** embarque le PNG dans un PDF A4 / carte. Fiable pour du print, indépendant de puppeteer.
- **QR** : lib `qrcode` (encode) + `jsqr` (RE-décode pour VÉRIFIER le lien, pas juste afficher). Contraste quasi-noir sur blanc.
- **Piège logo sur fond** : un halo peint sur tout le fond crée un « carré » derrière une image opaque (le logo masque le halo). Solution : fond plat.
- **puppeteer se fige** après beaucoup de lancements headless dans la session (Chrome coincé) ; `taskkill chrome.exe` aide un temps, sinon basculer sur sharp/SVG. Ne pas lancer le serveur python sans `cd boussole` (sinon l'URL `/_proto/...` ne marche pas).

## Fichiers touchés (principaux)
`boussole/` (app.js, ui.js, config.js, app.css, index.html, sw.js) · `boussole/_proto/{connexion,app}.html` · `boussole/assets/img/skyline-*.webp` · `boussole/assets/icons/logo-boussole-*.png` · `clients/04-luxury-skin-clinic/assets/docs/*` (Luxury Club 229).
