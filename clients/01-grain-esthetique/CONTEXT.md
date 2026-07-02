# CONTEXT — Grain d'Esthétique

## Identité
- **Nom** : Grain d'Esthétique — Institut de Beauté
- **Fondatrice** : Jocelyne Aguiar (mère de Mongazi)
- **Secteur** : Esthétique / soins (femmes & hommes — Espace Hommes dédié)
- **Lieu** : Cotonou, Haie-Vive (Lot N 18) — Bénin
- **Produits pros** : Sothys Paris · Sultane de Saba
- **WhatsApp / Tél** : `2290197085576` (01 97 08 55 76) — aussi 01 99 23 71 23 / 01 90 92 68 31
- **Horaires** : Mar–Sam 09h–19h (Lun & Dim fermé) · Sur rendez-vous
- **Réseaux** : avis Google 5★

## Vitrine (en ligne)
- **URL** : https://grain-esthetique-cotonou.netlify.app (Netlify)
- **Source dans le repo** : `grain-esthetique-LIVE.html` (récupérée du live le 2026-06-12 ; ~787 Ko, **images en base64**).
- Mono-fichier HTML/CSS/JS, mobile-first (colonne ~500px), fonts **Cormorant Garamond + Jost**, palette **rose #C4648A / or #D4AF72**, lecteur de musique d'ambiance.
- **Réservation = WhatsApp** : chaque soin a un lien `wa.me/2290197085576?text=…réserver…`. ⚠️ **Ne jamais changer ce numéro/redirection.**

## Promotion Fête des Pères (16–30 juin 2026) — TERMINÉE (retirée du site le 2026-07-02)
> Promo expirée → pastille hero + pop-up auto + flyer base64 **retirés** (validé par Mongazi).
> Le pop-up/mécanique de conversion pourra être réactivé pour une future offre (voir `_edit_promo.py`).
Flyer source : `_partage/flyer fete des pere chez grain desthetique.JPG`. Offres (archive) :
- Soin du visage : ~~30 000~~ → **25 000 F**
- Hydrafacial : ~~60 000~~ → **45 000 F**
- Soin visage + Pédicure & Manucure : ~~45 000~~ → **40 000 F**
- Massage relaxant : ~~15 000~~ → **12 000 F**

## Améliorations livrées (2026-06-12)
Couche **additive** (images, couleurs et liens WhatsApp **inchangés**) :
- **Promo à l'entrée** : badge doré animé dans le hero + **affiche en modale** (ouverture auto 1×/visite) + **boutons RDV** par offre → WhatsApp de base avec message prédéfini.
- **Animations** : révélation au défilement (réutilise `.rv`), zoom doux du hero + fondu du titre, micro-interactions (survol soins, cartes qui se soulèvent, icônes vivantes), focus accessibles, respect « mouvement réduit ».
- **Onglets premium** : nav en verre dépoli + soulignement animé dégradé rose→or, centrés sur PC.
- ❌ Écarté (jugé « moche » par Mongazi) : encadrer la colonne PC avec fond dégradé → revenu au blanc d'origine.

## Animations signatures par section (2026-07-02, 2e passe)
- **Une animation différente par section, adaptée à son thème** (au scroll, via `.rv`), + **micro-animation d'icône** :
  - À Propos → **Éclosion** (bloom fondu+flou) · icône fleur qui s'ouvre
  - Visage → **Radiance** (soins qui s'allument, brightness) · étoile qui scintille
  - Corps → **Respiration** (montée lente/douce) · feuille qui se balance
  - Épilation → **Glisse** (translation latérale, façon cire) · goutte qui tombe
  - Mains & Pieds → **Vernis** (révélation gauche→droite, clip-path) · icône qui scintille
  - Soins Avancés → **Élévation** premium (cartes + halo doré) · gemme qui brille
  - Espace Hommes → **Assurance** (montée nette) · **nœud papillon doré** (remplace l'emoji 🎩 résiduel)
- Correctifs : `.hommes-body` reçoit `id="hommessoins"` + ajouté au tableau `ids` du révélateur (ses soins s'animent enfin).
- `prefers-reduced-motion` : tout apparaît sans animation. Script : `_edit_anim.py`.
- QC Playwright : **7/7 animations de contenu distinctes** + **6 icônes distinctes**, nœud papillon OK, Hommes révélé, 0 emoji résiduel, JS OK (le révélateur exécute le nouveau hook).

## Améliorations livrées (2026-07-02) — passe « au max »
Couche **additive** (images, couleurs, **numéro/liens WhatsApp inchangés** — 91 liens Réserver vérifiés) :
- **Promo Fête des Pères expirée retirée** (pastille + pop-up + flyer base64 → −391 Ko ; fichier 787→417 Ko).
- **Tous les emojis → icônes SVG line-art** rose/or (6 sections, horaires, contact ×3, footer ×3, note musique).
  Fini les emojis d'UI (anti-pattern) ; `★` de « 5★ » passé en doré.
- **SEO/social** : meta description, Open Graph + Twitter Card, theme-color, canonical, geo, **JSON-LD BeautySalon**
  (horaires, tel, adresse), favicon SVG de marque, **image de partage `assets/images/og-grain.jpg`** (1200×630, générée du hero).
- **Accessibilité** : nav `<div onclick>` → **7 `<button>`** (clavier), bouton musique = `<button>` + `aria-pressed`,
  alt manquant corrigé, reset CSS boutons (rendu identique).
- **Conversion** : **CTA « Prendre rendez-vous »** (WhatsApp) dans le hero + **bouton WhatsApp flottant** rose/or,
  **badges maisons partenaires** (Sothys Paris · Sultane de Saba), `rel="noopener"` sur les 91 liens.
- Scripts reproductibles : `_edit_promo.py`, `_edit_icons.py`, `_edit_a11y.py`, `_edit_polish.py`, `_build_og.py`.
- QC navigateur (Playwright) desktop+mobile : **0 erreur, 0 404, 11/11 images OK, 93 liens WhatsApp (0 mauvais numéro)**, focus clavier OK.

## Déploiement — MIGRÉ SUR CLOUDFLARE PAGES + DOMAINE (2026-07-02)
- ✅ **LIVE CONFIRMÉ : https://graindesthetique.com** (+ `www`) — 200, **SSL actif**, redirect http→https (301). Site amélioré servi.
  (Statut « custom domain » de l'API Pages restait « pending » alors que le site répondait déjà 200 — l'API retarde, le site marche.)
- ✅ **Domaine acheté par Mongazi : `graindesthetique.com`** (registrar **Hostinger**).
- ✅ **Site amélioré déployé sur Cloudflare Pages** — projet **`grain-esthetique`** → https://grain-esthetique.pages.dev (LIVE, vérifié 200).
  Déploiement = `wrangler pages deploy _dist` (`_dist` = `index.html` [= grain-esthetique-LIVE.html] + `assets/images/og-grain.jpg`).
- ✅ **Meta pointées vers le domaine** : canonical/og/twitter/JSON-LD = `https://graindesthetique.com` (6 remplacements).
- **Domaine branché** : zone `graindesthetique.com` ajoutée à Cloudflare (NS `paul`+`rosemary.ns.cloudflare.com`, changés chez Hostinger).
  Custom domains `graindesthetique.com` + `www` attachés au projet Pages (via API). DNS : **A `2.57.91.91` supprimé** →
  **CNAME `@` → `grain-esthetique.pages.dev` (proxied)**, `www → graindesthetique.com`. ⏳ activation/SSL en cours au 2026-07-02.
- ⚠️ Token `cloudflare.env` = **Pages-only** (ne gère pas le DNS) → les changements DNS/zone = **action Mongazi dans le dashboard**.
- **Ancienne version Netlify** (`grain-esthetique-cotonou.netlify.app`) = OBSOLÈTE → à débrancher une fois le domaine live.

## À faire / décisions
- [ ] Confirmer `https://graindesthetique.com` en ligne + SSL actif (custom domain « active »), puis débrancher/supprimer l'ancien Netlify.
- [ ] Optionnel : vraies photos supplémentaires, vrais avis Google, mini-vidéo institut.

## Liens
- Vitrine source : `grain-esthetique-LIVE.html`
- Assets : `assets/`
