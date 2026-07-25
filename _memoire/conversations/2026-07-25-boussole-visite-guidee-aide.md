# 2026-07-25 — Boussole : COMPRENDRE (visite guidée animée, aide de chaque écran, « à faire maintenant »)

## Demande
Rendre l'outil **très facile à comprendre, même pour un enfant**. Créer un **didacticiel animé à l'entrée** (1re fois) qui présente l'interface, **rejouable à tout moment**. L'utilisateur doit comprendre **tout ce qu'il voit**, **tout ce qu'il touche**, et **savoir ce qu'il a à faire**.

## 1 — La visite guidée animée (9 étapes, sur la VRAIE interface)
Pas une vidéo ni des captures : un **projecteur** sur l'interface réelle.
- **Voile sombre troué** (`clip-path` polygone recalculé sur la cible) : l'élément expliqué reste **éclairé**, tout le reste s'assombrit.
- **Anneau doré pulsant** autour de la cible + **main animée** qui pointe (« tapote ici »).
- **Bulle** avec pictogramme, titre, texte en mots simples, **points de progression**, « Passer » / « Suivant ».
- La visite **navigue vraiment** entre les écrans (accueil → caisse → bilan → boussole), avec temporisation adaptée (900 ms sur la caisse, le temps que le coffre s'ouvre).
- Étapes : bienvenue · les 2 gros boutons · les 3 chiffres du haut · la barre du bas · encaisser · la note sur 100 · poser une question · le menu · c'est tout.
- **Placement de la bulle mesuré APRÈS écriture du texte** (`offsetHeight`) puis recadré : sous la cible, sinon au-dessus, sinon centré — et **toujours clampé dans l'écran**. (C'est le QC qui a attrapé le débordement initial.)
- Déclenchement : **enchaîne l'onboarding** à la 1re inscription, ou au boot tant que `SM.meta.tourDone` est faux.

## 2 — L'aide de chaque écran (bouton « ? » du header)
- Nouveau bouton **« ? »** dans le header (à gauche de l'avatar, `.hdr__right` en flex) → feuille **« à quoi ça sert ? »** de l'écran **où l'on se trouve** (`_curNav`).
- **14 écrans documentés** (`AIDE`) en 3-4 points illustrés, langage enfant : « 1. Touche les produits · 2. Choisis le paiement · 3. Encaisse ».
- Depuis l'aide : **« Revoir la visite guidée »**. Depuis les **Réglages** : bloc « Apprendre à utiliser Boussole » (revoir la visite + aide de l'écran).
- Le « ? » **pulse 3 fois** à la fin de la visite pour qu'on le repère.

## 3 — « À faire maintenant » (savoir quoi faire)
Carte dorée sur l'accueil (`prochaineAction()`), **une seule action à la fois**, par ordre de priorité :
catalogue vide → 1re vente → 1re dépense → **rupture de stock** → **relancer un client qui traîne** → reste X pour l'objectif → saisies irrégulières → point mort non atteint → sinon « regarde ta note de santé ». Elle est **cliquable** et emmène sur le bon écran. Masquée pour un vendeur.

## 4 — `?tour=off`
Paramètre d'URL qui désactive le lancement automatique de la visite : indispensable pour les **démos** et pour les **8 suites QC** (le voile de la visite interceptait tous les clics). Les suites v4→v10 chargent désormais `app.html?tour=off`.

## QC
`qc_v11.js` : **46/46 verts sur mobile ET PC** — visite lancée au 1er démarrage, 9 étapes, projecteur bien positionné sur la cible (comparé au `getBoundingClientRect` réel), trou du voile, main, **bulle jamais hors écran à aucune étape**, navigation réelle entre écrans, mémorisation (`tourDone`), pas de relance après rechargement, aide contextuelle qui **change avec l'écran**, feuille cadrée, relance depuis l'aide et depuis les Réglages, « Passer », carte « à faire » qui emmène au bon endroit.
Non-régression : **v4 → v10 toutes vertes** (190 vérifications cumulées), 0 erreur console.

## Reste
Vague 2 des transitions · Agenda · `etat.sql` à exécuter · déploiement (token Cloudflare).

Cf [[2026-07-25-boussole-pilotage-bilan-stats]].
