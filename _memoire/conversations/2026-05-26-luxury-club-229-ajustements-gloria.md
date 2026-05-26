# Luxury Club 229 — 4 ajustements Gloria

## Date : 2026-05-26
## Sujet principal
Série d'évolutions demandées par Gloria sur la vitrine `luxuryskinclinic.netlify.app`,
toutes adressant des frictions de conversion concrètes côté clientes.

## Ce qu'on a fait

### 1. Disponibilité Mme Sabrina réduite à mercredi/samedi
Gloria : « je suis dispo mercredi et samedi pour le moment ».
Adapté **5 endroits** dans `luxury-skin-clinic.html` :
- Bandeau RDV haut de page (entête conversion)
- Ligne RDV sous chaque fiche soin (9 soins concernés via `kind:'book'`)
- Point 1 du règlement clinique (modal obligatoire)
- 2 messages WhatsApp générés (VIP + standard) — « Jour souhaité : mercredi
  ou samedi » au lieu de « Date à définir ensemble »
- Récap modal (« Mercredi ou samedi — à confirmer avec la clinique »)

Volontairement gardé l'adverbe « actuellement » dans 2 endroits pour signaler
le caractère temporaire. 5 occurrences groupées, élargir = 1 grep.

### 2. Carte adresse après réservation
Gloria : « Après la réservation d'une prestation contrairement à un produit
j'aimerais qu'il y ait ce message ».

Ajouté un bloc adresse luxe doré dans le modal de remerciement
(`#lcThanksModal`), affiché **conditionnellement** :
- Titre typed-typewriter : « Merci pour votre réservation ✨ »
- Carte semi-opaque backdrop-blur, bordure dorée, charte luxe
- Adresse rédigée propre : « Akpakpa Suru Lere — Von en face de la
  poissonnerie Saint-Paul. 2ᵉ rue à droite, 1ʳᵉ maison à étage carrelée
  marron à votre droite. Nous sommes au 1ᵉʳ étage, porte à gauche. »
- 2 CTA dorés : `tel:+22967975626` (Appeler · 67 97 56 26) +
  `https://www.google.com/maps/search/?api=1&query=Luxury+Skin+Clinic+Cotonou`
- Animation : fade-in + slide après la fin du typewriter

Architecture JS : `lcConfirmOrder` accepte désormais `opts.thanks={text,address}`.
Booking pass `{text:LC_BOOK_THANKS, address:true}`. Diagnostic capillaire et
Consultation Peau gratuite gardent le message générique sans adresse
(rendez-vous à distance).

### 3. Simplification du français des routines INA Luxury
Gloria : « le français là est déjà compliqué pour eux ».

Intro routines reformulée selon ses mots exacts :
> Deux gammes disponibles : **Luxury** (gamme médicale) et **Skin** (gamme
> semi-médicale). La différence se situe au niveau de la concentration des
> actifs. Choisissez selon vos besoins et votre budget.

Appliqué aux 3 endroits (HTML statique + JS visage + JS corps adapté).
Sous-titres des tiers Skin allégés : « Gamme semi-médicale · plus abordable »
→ « Gamme semi-médicale » (×4). « plus abordable » retiré du desc
`body-skin` aussi.

### 4. Correction Routine Acné — tier Skin
Gloria : « Routine acné skin (je m'étais trompé) — les deux produits présents
là-bas sont : Rose Purifiant Sérum, Acné Control Crème ».

Remplacé `items:['Serum Azelaic','Reti Rose Crème']` par
`items:['Rose Purifiant Sérum','Acné Control Crème']` dans la routine Acné
tier Skin. Tier Luxury inchangé (Glass Skin Crème + Glass Skin Boost Crème).

**Rose Purifiant Sérum** ajouté comme nouveau produit Visage/Sérums :
`p:null, todo:1, isnew:1, c:['acne','grasses']`. Descriptif provisoire pro
en attendant les vraies infos. Le système gère gracieusement : affiche
« Prix à définir » + bouton « Demander le prix » WhatsApp + placeholder R doré.

### 5. Instagram cross-marque
Gloria a fourni `https://www.instagram.com/luxuryclub229?igsh=N2RzdzBxZzFnYXN3&utm_source=qr`.

Remplacement de 7 occurrences (4 barres flottantes sur les 4 pages + 3 modales
de remerciement) basculées de `@inaluxury` vers `@luxuryclub229`. Aria-labels
mis à jour. TikTok inchangé (toujours `@inaluxury` — à demander à Gloria
si elle a un compte TikTok cross-marque équivalent).

## Ce que j'ai appris
- **Architecture des thanks modals déjà en place** : `lcConfirmOrder` était
  prévu pour être étendu — le pattern `opts.thanks={text,address}` s'intègre
  proprement, sans dupliquer la mécanique typewriter+particles existante.
- **JS partage scope entre `<script>` classiques d'un même HTML** : `const`
  défini en top-level d'un script inline est accessible dans un autre script
  inline IIFE de la même page. C'est ce qui permet à `LC_BOOK_THANKS` (défini
  haut du script principal) d'être passé à `lcConfirmOrder` (IIFE bas de page).
- **Patterns « gracieux dégradé »** : un produit avec `p:null` + `todo:1`
  affiche automatiquement « Prix à définir » + bouton WA « Demander le prix »
  + placeholder couleur. Pas besoin de gérer ces cas un par un quand on
  ajoute un produit incomplet.

## Décisions prises
- **Période transitoire Sabrina** signalée par « actuellement » et « pour le
  moment » plutôt que des dates dures — supportable jusqu'à la prochaine
  modif sans tomber dans l'obsolescence.
- **Carte adresse réservée aux réservations en personne** (pas pour les
  questionnaires distance comme Consultation Peau gratuite ou Diagnostic
  Capillaire) — sinon spam de bruit visuel sur des flux qui n'amènent pas
  forcément à venir physiquement.
- **Vocabulaire « plus abordable » retiré partout** — Gloria veut une intro
  plus neutre qui parle de concentration d'actifs (factuel) plutôt que de
  positionnement prix.

## À appliquer dans NEBULA
- **Pattern carte adresse post-confirmation** : exportable à tout institut /
  prestataire physique futur (esthétique, médical, services). 1 carte
  doré-luxe avec adresse + CTA tel + CTA Google Maps. Code source dans
  `luxury-skin-clinic.html` lignes ~1773-1798 (CSS) + ~1859-1875 (HTML).
- **Pattern `opts.thanks={text,address}`** sur `lcConfirmOrder` : module
  réutilisable pour différencier les confirmations selon le type d'action
  (réservation physique vs demande à distance).

## À demander à Gloria
- Rose Purifiant Sérum : prix, taille (30 ml ?), photo, description complète
  (actifs, résultats, conseils d'utilisation, INCI)
- Confirmation que `67975626` est bien le numéro d'assistance dédié (différent
  du `+229 01 67 97 56 26` du WhatsApp Business)
- Compte TikTok cross-marque éventuel (pour faire la même bascule
  qu'Instagram)
- Référencement Google Business Profile pour avoir un vrai pin Google Maps
  au lieu d'une recherche par nom

## Prochaine étape
Attente des infos Rose Purifiant Sérum pour compléter la fiche. En parallèle,
le déploiement Netlify auto-redéploie sur push : vérifier en prod mobile
le rendu de la carte adresse et le tap sur `tel:` / Google Maps.
