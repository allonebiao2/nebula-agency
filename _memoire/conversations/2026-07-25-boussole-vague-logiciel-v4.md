# 2026-07-25 — Boussole proto : VAGUE « LOGICIEL » v4 (toutes les corrections de l'audit + animations)

## Demande de Mongazi
Après l'audit « qu'est-ce qui manque pour en faire un logiciel de qualité ? » : **tout corriger sans s'arrêter**, ajouter **plein d'animations au clic, toutes différentes par item**, et un **visuel encore plus stylé**. Commencer par les remarques de l'audit.

## 1 — Données propres (le point critique 🔴 réglé)
- **Fini les données de démo imposées** : `SM` démarre vierge (`{stock:[]}`), `SM.meta {onboarded, demo, activeId, updatedAt}`, TOUS les seeds (ventes/dépenses/cibles/clients/factures/équipe/stock) gated par `SM.meta.demo`. Migration douce : un état existant avec ventes ⇒ `onboarded=true, demo=true`.
- **Toasts + UNDO** : système global `toast(msg,{label,action,tone,ms})` (max 3 empilés, aria-live) ; suppression de vente/dépense/objectif/membre = **« Annuler »** qui restaure tout (stock redéduit, dette client remise, position dans la liste).
- **Export / Import JSON** (Réglages) + « Tout effacer » et « Quitter la démo » à confirmation armée 2 touches.
- **Sync cloud Supabase** : table `boussole_proto_etat` (user_id PK, etat jsonb, updated_at, RLS self — fichier **`_proto/etat.sql`** à exécuter 1 fois). `cloudPull()` au boot (l'appareil le plus récent gagne, marge anti-boucle 5 s) + `cloudPush()` debounce 1,8 s branché dans `smSave`. Statuts affichés dans Réglages (local / non connecté / table à créer / synchronisé).

## 2 — Onboarding + Réglages 🟠
- **Onboarding 4 pas** (overlay `.onb`, logo flottant, dots) : prénom → nom du commerce + activité (achat-revente/fabrique/services) + tel → objectif du jour → **choix « Mes vraies données » (zéro) / « Explorer la démo »**. Patron renommé au prénom, HUD salue par le prénom.
- **Écran Réglages** (`data-nav` via bouton Paramètres du tiroir, route `reglages`, verrouillé aux non-patrons) : identité commerce (nom/prénom/tel/adresse/**IFU/RCCM**), sécurité (code patron), webhook IA, données (export/import/démo/effacer), cloud.
- **Factures officielles** : en-tête = nom du commerce + adresse/tel, pied = IFU/RC (écran + impression PDF + partage), **statut cliquable** brouillon→envoyé→payé.

## 3 — Chaînons métier 🟠
- **Crédit ↔ carnet** : encaisser en Crédit ⇒ feuille « pour qui ? » (clients triés, création rapide, ou sans fiche + avertissement) ⇒ `sale.clientId/clientNom`, **dette auto** (+lastBuy). Édition de vente : sortie du crédit = dette soldée, delta de total = delta de dette, entrée en crédit sans fiche = toast. Suppression = dette effacée (undo la remet).
- **Coût de revient** : capturé à l'encaissement (`sale.cout`), migration rétroactive des anciennes ventes (coût catalogue sinon 55 %), recalculé à l'édition.
- **LES 3 ENVELOPPES** dans le Bilan (concept fondateur README enfin à l'écran) : Relance production (coût des ventes du mois) / Charges du mois (couvertes par la marge, manque affiché) / Bénéfice net. Cartes `--ec` + barres qui se remplissent + liseré doré.
- **Équipe réelle** : `meta.activeId` = qui tient la caisse (avatar header = initiale + couleur rôle, touche → feuille de changement avec code) ; **chaque vente signée** (`par`/`parId`, affiché dans l'historique) ; compteurs équipe = **vraies ventes du mois** (+ montant) ; **PIN hachés** (`pinHash` djb2 salé, migration des clairs, code affiché une seule fois en toast).
- **Verrous par rôle** : vendeur ⇒ bilan/stats/objectifs/carnet/factures/équipe/dépenses/boussole/réglages verrouillés (écran bouclier + code patron, anim refus), accueil masqué (🔒 caisse/objectif) ; gérant ⇒ équipe/réglages.

## 4 — IA Boussole 🟡
- **Alertes proactives** (`computeAlerts`) : ruptures, stock bas, objectif <40 % après 14 h, dettes >7 j, crédits sans fiche, charges non couvertes (dès le 10 du mois), **série de jours à objectif (positive)**. Pastille rouge sur l'onglet Boussole (compte les warn), rafraîchie à chaque `smSave`.
- **Boussole répond** : chat persisté (`SM.chat`, 12 max), questions rapides (chips), **règles locales chiffrées** (jour/hier/semaine/mois, meilleur produit/jour, dettes, stock, objectif, bénéfice/marge, dépenses, enveloppes, ventes par vendeur) + **webhook IA optionnel** (n8n/Claude, POST {question, contexte}, timeout 6 s, repli local). ⚠️ piège regex : « je **dois** » ≠ « doit » → `/doi[st]|récup/`.

## 5 — Finitions + animations ✨
- **Recherche live** ventes & dépenses (filtre DOM sans re-render : le clavier reste ouvert) + **pagination** 40 lignes + « Voir plus ».
- **15 animations de touché, une par famille d'items** (délégué pointerdown, respectent reduced-motion) : vente=ticket qui frémit · dépense=billet qui s'échappe · produit=rebond d'étagère · tuile caisse=caoutchouc · client=carte qui salue · projet=pièce dans la tirelire · document=papier plié · membre=badge scanné · KPI=pouls lumineux · chips=élastique · alerte=écho radar · enveloppe=liquide secoué · vital=enfoncement 3D · bouton=décollage · relance=avion papier.
- **Visuel premium** : liseré dégradé or/émeraude sur panel/ia/env/setgrp (mask composite), titre en **shimmer doré** à l'arrivée, **sparkline** dans le KPI Encaissé, **compteurs animés** (stats + bénéfice bilan), scrollbar dorée, caisse vide = invite catalogue.

## Corrections de bugs au passage
- `bindCaisse` plantait sur catalogue vide (`.pos__grid` null) → le menu restait ouvert.
- Équipe démo pas rechargée quand on choisit la démo depuis l'onboarding (delete SM.equipe + patron renommé conservé).

## QC (Playwright, 2 parcours complets)
`qc_v4.js` : **45 checks verts, 0 erreur console** — parcours A (zéro : onboarding, aucune donnée démo, réglages, PIN haché, verrou vendeuse, mauvais code refusé/bon code OK) + parcours B (démo : crédit→dette auto, vendeur signé, coût capturé, recherche, undo, enveloppes, alertes, chat chiffré, pastille, facture IFU, statut cyclé, sparkline, liseré, 2 animations, switch caisse). + `qc_proto.js` (vague précédente) adapté onboarding : **26/26**. `node --check` OK.
⚠️ Playwright : navbtn animés → `click({force:true})`.

## Reste (vagues suivantes)
Agenda · comparateur 2 moments (socle prêt) · exécuter `etat.sql` dans Supabase pour activer la synchro réelle · relances auto planifiées · PWA du proto (sw scope à part) · intégration app live.

Cf [[2026-07-25-boussole-edition-ventes-objectifs-stats-periodes]], [[project_boussole-refonte]].
