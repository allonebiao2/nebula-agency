# 2026-10-22 · MA LETTRE À… : zéro gratuité en ligne, le clic de verre, deux défauts trouvés par les contrôles

Suite de la nuit du 21 (`2026-10-21-malettre-quatre-demandes.md`, section « Le 22 »).

## Les prix, tranchés et publiés

Mongazi : « je ne voudrais que rien soit gratuit », « EN VRAI ZERO GRATUITé car sa peut se contourner en changeant de
navigateur ou de telephone », « l'essai […] censé être à 500 F on met à 1000 F », puis la plume « Coupée » le temps
du chantier, et « ET OUI COMMENCES ».

- **La Carte 1 000 F** remplace l'offre gratuite (7 jours, une photo, notre signature en pied, ni habillage ni
  code) · Le Mot 2 000 · **La Lettre 5 000, 10 photos** · Le Coffret 10 000 · **faire-part 35 000 F** (25 000 avant).
- Les deux grilles changent ensemble (`creer.html`, `supabase/functions/_shared/lettre.ts`), la caisse les compare.
- **La plume coupée en ligne** : `PLUME_OUVERTE` (ouverte seulement sur `localhost` ou `127.0.0.1`, et pas avec
  `?enligne`), note « La plume revient très vite : elle écrira ta lettre une fois ta commande réglée ».
- Vitrine : « Dès 1 000 F » (marqueur `<!--__ENTREE_PRIX__-->`, lu dans le constructeur par le build), plus aucune
  réponse ne promet rien de gratuit. Propagé dans `README.md`, `PAIEMENT.md`, `PRODUCT.md`, `CONDITIONS.md`.
- Zéro lettre en base au moment du changement : aucune commande « gratuit + plume » n'est restée en route (ce qui
  comptait : `malettre-paiement-recu` relit le palier au paiement et refuse un palier inconnu).
- **Publié** : les quatre fonctions d'abord (le serveur qui connaît `carte`), le site juste après. Preuve sans trace :
  une commande vide au palier `carte` répond « lettre vide », au palier `gratuit` « palier inconnu ».

## Ce que les contrôles ont trouvé

1. **Quatre faux échecs, faute de mémoire** (« la commande part vers la caisse ») : Chrome ouvert, 1,5 Go libres.
   Mongazi a fermé Chrome (« J4AI FERMER CHROME ») : 3,2 Go, zéro échec, rien touché.
2. **La FAQ « Comment paie-t-on ? » à 26 mots** (seuil 30) après le retrait de sa phrase sur la gratuité : complétée
   par ce que le parcours fait vraiment (lu dans `paiement.html` et `merci.html`).
3. ⛔ **Les timbres des prix se levaient 389 px trop tard au téléphone.** La sonde de contraste mesurait « THE NOTE »,
   puis « THE CARD », à 2,05:1 un coup sur deux : elle photographiait la barre d'achat. La photo de la mesure fautive
   montrait un grand vide sous « What it costs. ». Cause : la feuille de timbres est à la fois l'objet animé et le
   déclencheur ScrollTrigger ; GSAP mesurait sa boîte couchée (58°, +110 px). Le calcul colle : 110 + ~600 px ×
   (1 − cos 58°) ≈ 390. Même défaut sur la feuille de la plume, les billets, la page de la fin. Correction
   `depuis(el, part)` (place dans la page par `offsetTop`), plus un `ResizeObserver` qui relance
   `ScrollTrigger.refresh()` quand la page change de hauteur. Contrôle ajouté (7 décors, écart ≤ 2 px).
4. ⛔ **La nuit des lettres pouvait rester figée sur sa fin** : `g.to(etat, {p: 1})` partait de la pose déjà peinte ;
   GSAP arrivé tard (PC chargé pendant l'écoute des sons) = une animation de 1 à 1. Corrigé par `fromTo({p: 0})`
   et `immediateRender: false`.

## Le clic de verre

Mongazi : « je veux un bruit qui fait click, comme si c'était du verre qu'on touchait, celui actuel ne fait pas
naturel ». Le clic d'avant mêlait un souffle de bruit filtré et un ton qui glisse : c'est ce qui sonnait synthétique.

- Trois matières en synthèse modale (verre fin, verre épais, cristal), rendues en WAV par Node et **mesurées** avant
  toute écoute : la première version était coupée vers −35 dB (durée portée à cinq fois la plus longue résonance).
- Page d'écoute locale (`http://localhost:8791/`) avec le clic d'avant pour comparer, la même chaîne que le site.
- **Choisi : A, le verre fin.** Posé dans le module de `creer.html` (la vitrine le lit), résonances par récurrence à
  deux pôles, un son de plus à chaque geste jusqu'à six. Mesuré tel qu'il est posé : 320 ms, dominante 3,1 kHz ;
  survol 160 ms, 3,5 kHz ; chaque son meurt seul sous −53 dB.

## En ligne, deux bizarreries qui ne sont pas à nous

- « Blocked a frame with origin "null" » : le script anti-robots que Cloudflare injecte
  (`/cdn-cgi/challenge-platform/scripts/jsd/main`). Absent du dépôt, absent en local, inoffensif.
- La box de Cotonou n'atteignait plus `188.114.96.3` ni `188.114.97.3`, les deux adresses que Cloudflare donne à
  `malettre.nebula-agency.online` ; PISTE et l'agence (`104.21.2.115`, `172.67.129.33`) passaient. Les six
  sous-domaines ont le même réglage (CNAME proxifié vers `*.pages.dev`). Vérifié par
  `curl --resolve malettre.nebula-agency.online:443:172.67.129.33` : le site répond 200. ⏳ À revérifier.

## Contrôles verts publiés

Constructeur 284 · caisse 382 · accueil 322 · langues 52 · faire-part 83.

## La suite

Mongazi : « à la fin tu vas réaliser la vidéo émotionnelle avec un effet wow qui mettra ma lettre en avant et donner
envie d'acheter ». Ses références (`_partage/ma lettre/*.mp4`) sont des invitations de mariage digitales : gros plans
de cachets de cire, enveloppes qui s'ouvrent, téléphone tenu en main dans le noir, accroche « POV » en haut. La pub du
21 finit sur « Gratuite pour commencer » : faux depuis aujourd'hui. Puis le chantier « la plume écrit APRÈS le
paiement ».
