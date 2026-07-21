# 2026-07-21 — Boussole : pivot « verre de nuit » premium (retrait Spider-Verse) + vagues 1-2

## Décision de direction (Mongazi)
Après un essai de skin **Spider-Verse comic** (retiré), demande claire : **améliorer le visuel ET les capacités du proto Boussole actuel** (`boussole/_proto/app.html` + `connexion.html`), avec :
- **Style professionnel premium glassmorphism**, unique, « qui donne envie de naviguer et de ne pas s'en aller ».
- **Simple sur PC et mobile**, fluide et rapide.
- Utilisable « par un enfant de 5 ans ».
- Le produit s'appelle **Boussole** (pas Spider-Verse).

Capacités attendues (liste Mongazi) : renseigner ventes/dépenses · catalogue produits · stats + en ajouter · objectifs · paramètres · **bilan journalier/mensuel** · **agenda** · **comparer des moments** · **Boussole (IA) qui taquine, donne les résultats et des conseils** · **supprimer ventes/dépenses** · clients (n°, nom/prénom, descriptif) + **relances perso/prédéfinies** · **devis & factures normalisés**. Améliorer l'existant en restant ultra simple.

## Réponses au questionnaire (4 questions)
1. **Palette** = Or ambre + émeraude (ADN Boussole).
2. **Navigation** = Barre basse 5 onglets (mobile) / rail latéral gauche (PC), le tiroir garde les 11 sections.
3. **Agenda** = calendrier business + rappels/échéances + RDV manuels (les 3).
4. **Priorité après socle** = Vendre & Dépenser.

## Retrait Spider-Verse (commits `8dee50a`, `+1`)
Suppression totale : bloc CSS `data-skin=sv`, script d'activation, attribut html, fichier `spiderverse.html`, `Anton.woff2`. Nettoyage des commentaires hérités (Spider-Verse / Spider-Manager) et du prénom démo « Miles » → « Boss ». `node --check` des modules OK.

## Vague 1 — socle « verre de nuit » (commit `b7e2776`)
- **Recolorisation complète** cyan néon `#38f0ff` → **or ambre `#f6a63c` + émeraude `#34d399`** (script Python UTF-8, 0 reste froid). Touches froides gardées en micro-accents (mint caisse `#2fd4c2`, sky factures).
- **Fond** : la grille cyber en fuite (coûteuse) → **3 halos aurore lents** (ambre/émeraude/teal) + poussières réchauffées.
- **Barre principale 5 onglets** (`.tabbar`) : Accueil · Caisse · Bilan · **Boussole** · Menu. Verre de nuit, **mobile en bas / rail latéral gauche ≥1024px**, état actif synchronisé avec le routeur (`setActiveTab` appelé dans `showSection`). Contenu + FAB relevés au-dessus.
- **Nouvel écran Boussole** (`boussoleHTML`) = copilote branché sur l'IA locale existante (`iaBanner`/`iaVerdict`) + KPI encaissé/dépensé + phrase taquine.
- **connexion** : carte/logo/titre/champs/bouton principal en or, balayage de succès or, **bouton Google intact**.

## Correctif LATENCE (commit `perf`)
Cause : les **halos animés en continu** sous **7 surfaces en `backdrop-filter` permanent** (header, tabbar, cartes vitales, KPI, panneaux, bénéfice héro, étiquette) → recalcul de flou à chaque frame. **Fix** : flou réservé au **tiroir + voiles (transitoires)** ; le reste passe en **verre simulé** (dégradés opaques). Connexion : flou carte 24→14, **lueur logo statique** (filtre au lieu d'animation infinie), fond **statique sur mobile**. Reste 6 occurrences `backdrop-filter` = uniquement `.drawer`/`.scrim`/`.sheet-scrim` (ouverts ponctuellement).

## Vague 2 — Vendre & Dépenser (commit `a6da3c7`)
- **Ventes** : chaque vente **cliquable** → feuille **détail** (articles, paiement, total) + **Supprimer** (restitue le stock physique par nom) avec **confirmation douce à 2 touches** (bouton s'arme 3 s puis désarme). FAB « Encaisser » → caisse.
- **Dépenses** : touche une sortie → la feuille s'ouvre en **mode Modifier** (montant, libellé, catégorie, type dépense/achat, récurrence+fréquence, poche perso pré-remplis) ; **Supprimer** visible même confirmation douce. Saisie rapide (FAB +) inchangée. Refactor `setCat/setKind/setRec/setPerso/resetSheet/openEdit`.
- CSS : `.vdetail`, `.sheet__del` (armé = pulsation), `.sheet__keep`, `.fab--green`, `.is-going`.

## Déploiement (preview, prod intacte)
`wrangler pages deploy . --project-name boussole --branch proto` → **https://proto.boussole-19d.pages.dev/_proto/connexion** (alias) ; prod `boussole-19d.pages.dev` non touchée. ⚠️ Cloudflare redirige `.html`→URL propre (308) : donner le lien **sans `.html`**. Vérifs live 200 à chaque vague.

## Reste (vagues suivantes)
- **Agenda** (calendrier business CA/dépenses/bénéfice par jour + tap = détail & comparaison ; rappels/échéances ; RDV manuels).
- **Comparateur** de périodes (2 moments).
- **Carnet clients enrichi** (n°, nom/prénom, descriptif) + **relances perso/prédéfinies**.
- Bilan journalier/mensuel affiné · ajout de stats · paramètres · onboarding « enfant de 5 ans ».
- Intégration finale dans l'app live [[project-boussole]].

## Méthode / garde-fous
- Édits via **scripts Python UTF-8** (jamais PowerShell Set-Content = mojibake) ; `node --check` du module inline à chaque vague ; vérif 200 live.
- **Perf d'abord** : pas de `backdrop-filter` permanent sous des animations de fond.
Cf [[project_boussole-refonte]], [[project_boussole]], [[feedback-grandes-taches]], [[feedback-cache-bust-assets]] (ici pas de ?v= car proto).
