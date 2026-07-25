# 2026-07-25 — Boussole proto : édition des ventes, objectifs modifiables, stats par période libre + analyse IA

## Demande de Mongazi (avant d'attaquer l'Agenda)
Compléter le proto « verre de nuit » (`boussole/_proto/app.html`) avec :
1. **Modifier les ventes** (pas seulement supprimer).
2. **Modifier ou supprimer les objectifs**.
3. **Stats de n'importe quel jour / mois / année / période**, sélectionnables, avec **analyse de la période par l'IA Boussole**.

## 1 — Modifier une vente (feuille détail enrichie)
- Nouveau bouton **« Modifier cette vente »** (`.sheet__edit`, ambre) dans la feuille détail, entre le détail et Supprimer.
- **Mode édition** : chaque article passe en ligne `.vedit` avec **steppers − / +** (réutilise `.qtybtn` du catalogue) + montant de ligne live ; **sélecteur de paiement** (Espèces / Mobile Money / Crédit, `seg--pay` émeraude) ; « Nouveau total » recalculé à chaque touche.
- **Garde-fous** : + plafonné au **stock physique restant** (`qty - qty0 >= p.qty` → swoosh) ; quantité 0 = ligne grisée (`is-zero`) et **retirée à l'enregistrement** ; vente vidée → refus (passer par Supprimer) ; **stock ajusté par l'écart** (`p.qty -= (qty - qty0)`, repérage par nom comme `removeSale`).
- Boutons contextuels : Modifier→**Enregistrer les modifications**, Garder→**Annuler** (retour au détail sans rien toucher, draft jeté).

## 2 — Objectifs : modifier / supprimer les projets d'achat
- Chaque cible a désormais **2 boutons** (`.cible__act`) : « + ajouter à l'épargne » + **« Modifier »** (`.cible__mod`).
- La feuille objectifs gagne : champ **« Déjà épargné »** (`data-osep`, affiché en édition, clampé 0..montant) + bouton **« Supprimer cet objectif »** (`data-osdel`) avec la **confirmation douce à 2 touches** (armé 3 s) comme ventes/dépenses.
- Mode `editcible` : renommer, changer le prix, corriger l'épargne. `open()` refactoré en options (withName/withEp/withDel/valeurs pré-remplies).
- Les objectifs de CA jour/semaine/mois restent modifiables via « Modifier l'objectif » (inchangé).

## 3 — Stats par période libre + analyse IA Boussole
- **Chips de période** (`.statchips`, style freqchip or) : Aujourd'hui · Hier · 7 jours · Ce mois · Cette année · Tout · **📅 Choisir…**
- **« Choisir » = feuille** avec seg **Jour / Mois / Année / Période** → inputs natifs `date` / `month` / année numérique / plage Du–Au (`color-scheme: dark`), bornés à aujourd'hui, inversion Du/Au tolérée.
- Moteur : `_statSel` + `statRange()` (10 sortes → {t0,t1,lbl}), agrégats filtrés `caIn/depTotIn/depByCatIn`, **`statBuckets()`** adaptatif (1 jour → contexte des 7 jours qui y mènent ; ≤ 62 jours → barres quotidiennes avec étiquettes espacées ; au-delà → barres mensuelles ; « Tout » borne t0 au 1er enregistrement).
- **`iaVerdictPeriod()`** : verdict gagnant/équilibre/rouge sur la période + **comparaison à la période précédente de même durée** (±X% de ventes, ton taquin) + plus grosse catégorie de sortie + **meilleur jour** de la période. Bannière « ✦ L'IA Boussole · analyse de la période ». « Tout » = verdict global existant.
- KPI (Encaissé/Dépensé/Bénéfice/Marge), donut dépenses et barres = tous filtrés sur la période.

## QC (Playwright headless, serveur local)
Script `qc_proto.js` (scratchpad) : **26/26 verts, 0 erreur console** — édition vente persistée (qté −1, total recalculé, paiement→crédit, nb ventes stable, Annuler sans effet), objectif renommé/montants/épargne + suppression 2 touches, 7 chips, jour précis / mois / année / plage, bannière IA de période, retour « depuis le début ». ⚠️ piège de test : la liste ventes est **triée par ts desc** → comparer par `data-vid`, pas `ventes[0]`.
`node --check` des 2 scripts inline OK.

## Reste (prochaines vagues, inchangé)
Agenda (calendrier business) · comparateur de 2 moments (le socle `caIn`/`statRange` est prêt pour ça) · carnet clients enrichi + relances · onboarding « enfant de 5 ans » · intégration app live.

Cf [[project_boussole-refonte]], [[2026-07-21-boussole-refonte-verre-premium]].
