# 2026-07-25 — Boussole : PILOTAGE (point mort, trésorerie, score de santé, produits, rythme, rapport)

## Demande
Analyse experte du **Bilan** et des **Statistiques** : que manque-t-il pour que **tout commerçant, quel que soit son domaine**, suive son business de manière générale ET précise ? Puis implémentation.

## Diagnostic
L'existant répondait bien à « **combien j'ai fait ?** ». Il manquait « **est-ce que je vais tenir ?** » et « **que dois-je faire demain ?** ». Vérifié par grep : panier moyen, trésorerie, point mort, valeur du stock, projection = **0 occurrence** avant cette vague.

## 1 — Le point mort (le chiffre que presque aucun commerçant ne connaît)
`pointMort()` : `charges fixes du mois ÷ taux de marge réel` → CA minimum vital, puis `÷ jours ouvrés` → **objectif quotidien de survie**. Détecte **le jour du mois où le point mort a été franchi** (cumul des ventes triées). Jauge dégradée rouge→or→vert au Bilan.
- `tauxMarge()` : marge réelle sur 60 j, repli sur la marge théorique du catalogue, puis 40 %.
- `joursOuverture()` : jours réellement travaillés (30 j glissants), défaut 26.
- ⚠️ distinction clé : **charges fixes** = sorties business **hors achat de marchandise** (`kind !== 'achat'`), le stock étant un coût variable déjà porté par le coût de revient.

## 2 — Trésorerie ≠ bénéfice (la cause n°1 de mort des petits commerces)
`treso()` : encaissé réel (espèces + Mobile Money), **vendu à crédit** (dans le bénéfice mais **pas dans la caisse**), argent dehors (dettes clients), sorties, **cash** et **autonomie en jours de charges**. Avertissement explicite dès qu'il y a du crédit dans le mois.

## 3 — Score de santé /100 (le liant, compréhensible en 2 secondes)
`scoreSante()` = 5 notes sur 20 : **Rentabilité · Trésorerie · Crédits clients · Stock** (ou *Activité* pour les services) **· Suivi** (régularité de saisie). Anneau coloré + libellé (« Fragile, mais rattrapable ») + **la composante qui pénalise le plus**, en clair. Très lisible et addictif (on veut faire monter le score).

## 4 — Le rythme (Statistiques)
- **Panier moyen** + **nombre de ventes** + articles/vente, avec évolution vs période précédente : les 2 KPI les plus universels du commerce, jusque-là absents.
- **Jours forts** (barres lundi→dimanche, meilleur jour en émeraude) et **heures de pointe**.
- **Comparaison** avec la période précédente de même durée (flèche ▲/▼ + bénéfice comparé).

## 5 — Écran « Mes produits » (nouveau, nav + verrou vendeur)
Classement par **bénéfice réellement apporté** (marge × volume) et non par chiffre d'affaires — avec l'alerte clé : **« ton best-seller n'est pas ton meilleur produit »** quand le n°1 en CA ≠ le n°1 en marge. Plus : **règle 20/80** (produits vitaux marqués), **dormants** (invendus 30 j avec l'argent immobilisé), **valeur du stock + rotation mensuelle**. Sélecteur 7 / 30 / 90 jours.

## 6 — Projection, récurrent, fiabilité, rapport
- **Projection fin de mois** : rythme actuel → atterrissage, manque vs objectif, montant/jour requis.
- **Revenu récurrent** : le flag `recurrent` du catalogue était inexploité → CA d'abonnements du mois.
- **Indice de fiabilité** : « noté X jours sur Y » — sans saisie régulière, les stats mentent, et on le dit.
- **Rapport mensuel imprimable/PDF** (essentiel, trésorerie, seuil de rentabilité, où part l'argent, top produits, stock, fiabilité) + **partage WhatsApp** résumé. Répond enfin à la promesse « bilan exportable » du README d'origine.

## 7 — L'IA exploite tout ça
+6 alertes (point mort non atteint après le 15, point mort franchi, trésorerie < 7 jours, dormants), **+8 questions comprises** (point mort, trésorerie, panier, jour fort, dormants, produit qui rapporte, fin de mois, score), chips mis à jour, **+11 phrases de salutation** de pilotage (score, point mort, cash à crédit, autonomie, projection, champion, dormants, panier, rotation, fiabilité).

## 🐛 Bug d'accessibilité trouvé pendant la vague (et corrigé)
Le 12ᵉ item du menu a fait descendre la liste dans la zone des toasts : **un toast recouvrait le bas du tiroir et bloquait les clics** sur « Mes produits » et « Mon équipe » (reproduit : le clic laissait l'écran Réglages affiché). Cause : `.toasts` en `z-index: 70`, au même niveau que le tiroir et **après** lui dans le DOM.
**Correctif** : `.toasts` en **z-index 59** (au-dessus des feuilles 47, sous le voile 60 et le tiroir 70) + `.app.menu-open ~ .toasts { pointer-events: none; opacity: .25 }`. **Test de non-régression ajouté** : les 12 entrées du menu doivent rester cliquables avec un toast affiché (hit-test `elementFromPoint` sur chaque entrée).

Bug cosmétique corrigé au passage : `countUpNums` mangeait l'espace du suffixe (« +17 400F ») → le groupe de chiffres doit **finir sur un chiffre** pour laisser l'espace au suffixe.

## QC
`qc_v10.js` : **33/33 verts** — calculs vérifiés **contre les données brutes** du state (dettes, panier, nombre de ventes), tri par bénéfice décroissant, 20/80, verrou vendeur sur « Mes produits », 4 questions IA, contenu du rapport, anti-blocage du menu. Non-régression **v4 → v9 toutes vertes** (144 vérifications cumulées), 0 erreur console.

## Reste
Vague 2 des transitions · Agenda · exécuter `etat.sql` · déploiement (token Cloudflare absent de l'environnement).

Cf [[2026-07-25-boussole-correctifs-audit-sweep-ui]].
