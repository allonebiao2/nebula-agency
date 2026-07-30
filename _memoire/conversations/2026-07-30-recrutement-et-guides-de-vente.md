# 2026-07-30 — Recrutement commercial + guides de vente des 3 services

## Contexte

Mongazi veut structurer la vente des **3 services phares** de NEBULA (Catalogue, Vitrine,
Outil digital sur mesure). Constat de départ, dans ses mots : « je suis piètre vendeur ».
Objectif : **recruter des vendeurs** et leur donner **un guide de vente complet par service**,
pour qu'ils sachent absolument tout (arguments, besoins clients, méthodologie).

Consigne de travail : avancer **étape par étape**.

## Décisions prises par Mongazi (32 décisions, toutes verrouillées le 2026-07-30)

| Sujet | Décision |
|---|---|
| **Statut des recrues** | **Partenaire commissionné**, branché sur le programme partenaires existant (`nebula-affilies`), pas de salarié |
| **Commission sur l'Outil métier** | **Taux plein 25 / 30 / 35 %**, exactement comme Catalogue et Vitrine (pas de taux réduit) |
| **Zone et volume vague 1** | **Cotonou uniquement, 5 à 10 places** (annonce calée sur 8) |
| **Rôle du partenaire** | **Vente + brief uniquement.** Toute la production reste chez NEBULA |


### Vague 2 de décisions (session du 2026-07-30, après livraison des étapes 0 à 6)

**Argent**
- Encaissement **sur le Mobile Money de Mongazi**, toujours. Virement bancaire accepté selon le client (réputé payé une fois constaté). Le partenaire ne touche jamais d'argent ni ne communique de coordonnées bancaires
- **Catalogue : paiement intégral, jamais échelonné.** Vitrine et Outil : **70 % / 30 %**, solde dû à la mise en ligne. **Solde impayé = site non mis en ligne**
- **Commissions payées en 24 à 72h**, en deux fois sur les projets à tranches, palier compté dès le 1er versement
- **Récurrent : 25 % de chaque abonnement encaissé, renouvellements compris, ACQUIS À VIE** même après départ. Ne compte pas dans le palier. Le réseau ne s'applique pas au récurrent (défaut posé). Pas de commission sur le renouvellement de domaine
- Relance de renouvellement : **rappel automatique + relance du partenaire** → le rappel automatique (n8n + WhatsApp) devient une infrastructure obligatoire puisque le récurrent est à vie

**Offres**
- Catalogue : **20 produits inclus**, +15 000 F par lot de 10
- Vitrine : **une page complète**, +30 000 F par page supplémentaire
- **Domaine offert la 1ère année**, puis 16 000 F/an (coût réel ~16 000 F)
- **Abonnement unique 20 000 F / 6 mois, modifications de contenu comprises** (remplace les 15 000 F)
- QR Google Review vendable par les partenaires, même commission
- **Boussole reste hors du programme partenaires**

**Règles**
- Prospect au **premier qui l'enregistre, 60 jours**
- Un client existant qui rachète → **commission au partenaire d'origine**
- Filleuls : invitation libre, **commission réseau seulement après sa 1ère vente**
- Litige : **on corrige jusqu'à satisfaction**, commission acquise
- Inactif : relance à 2 mois, désactivation à 4 mois (récurrent maintenu)
- Vente libre partout, recrutement limité à Cotonou
- SAV : **partenaire en premier interlocuteur + NEBULA joignable**, mais le partenaire ne promet jamais correction ni délai
- **Pas d'email @nebula-agency.online**, classement **entièrement transparent** (ventes et gains)

**Diagnostic Digital**
- **Gratuit, valeur affichée 25 000 F.** Le partenaire collecte, **Mongazi restitue**

**Recrutement et pilotage**
- Candidatures ouvertes **21 jours**, formation **en visio Google Meet**
- **Point collectif hebdomadaire de 30 min** (seul mécanisme de rétention retenu)
- Objectif **30 ventes sur 90 jours**. Aucune prime, aucune offre de lancement

**Contrat**
- **Contrat d'apporteur d'affaires indépendant**, signé par Mongazi BIAO sous l'enseigne NEBULA Agency, **IFU à compléter, RCCM en cours**
- Exclusivité **de métier** (pas totale) · **non-sollicitation 24 mois** après départ
- CGU en ligne + **charte signée à la main, photo renvoyée sur WhatsApp avant création des accès**

### Livré en complément (vague 2)

| Fichier | Contenu |
|---|---|
| `vente/00-SOCLE-COMMERCIAL.md` **v2** | Réécrit intégralement avec les 32 décisions |
| `vente/08-DIAGNOSTIC-DIGITAL.md` | **La consultation professionnelle** : proposition, préparation, cartographie en 3 temps calée sur le configurateur, **40 questions dans l'ordre**, test du cahier, observations muettes, **grille de détection des automatisations** (14 symptômes → 14 automatisations du stack réel), chiffrage de la douleur, rapport, restitution, 8 erreurs qui tuent un diagnostic, fiche terrain |
| `vente/fiche-diagnostic.html` | Fiche remplie sur le téléphone chez le client : sauvegarde automatique en localStorage, cases à cocher des automatisations, bouton qui envoie le **rapport structuré complet** sur le WhatsApp NEBULA. QC : balises équilibrées, `node --check` OK |
| `vente/09-CONTRAT-PARTENAIRE.md` | **Contrat d'apporteur d'affaires indépendant** en 16 articles + annexe résumée. Non relu par un juriste (suffisant pour la vague 1, à faire relire au-delà de ~30 partenaires) |
| Guides 01 à 07 | Mis à jour : abonnement 20 000 F, lots de produits, pages supplémentaires, domaine offert, 70/30, récurrent, 24-72h, date limite 21 jours, formation visio, blocs « à confirmer » supprimés |

### Reste (ce n'est plus de la décision)
1. Compléter l'**IFU** dans le contrat
2. Passer le site public de 15 000 à **20 000 F** (`00-nebula-agency/nebula_agency_v9.html`)
3. Aligner **NOVA** (`nebula-affilies/server.py`, `agency_brain()`)
4. Retirer les **5 anciens guides seedés** qui poussent la Vitrine en premier (`seed_docs()`)
5. Construire le **rappel automatique de renouvellement** (n8n + WhatsApp)
6. Convertir en PDF et publier dans l'espace partenaire

## Analyse stratégique retenue

1. **Les 3 offres forment un escalier, pas 3 produits.** Catalogue 50 000 F = porte d'entrée
   (un commerçant méfiant dit oui à 50 k, pas à 150 k) → Vitrine 150 000 F = crédibilité →
   Outil métier = contrôle et marge. Un partenaire qui maîtrise l'escalier gagne 3 fois sur
   le même client.
2. **Chaque marche vend une émotion différente** : Catalogue = le temps et les commandes perdues ·
   Vitrine = la crédibilité · Outil = le contrôle et l'argent qui fuit.
3. **Recruter des « conseillers », pas des « vendeurs »**, avec places limitées et sélection
   sur entretien noté. La rareté attire les bons profils.
4. **Garde-fou sur le taux plein Outil métier** (accepté par Mongazi) : pas de baisse de taux,
   mais **binôme obligatoire avec Mongazi sur les 3 premiers dossiers** Outil métier, le
   partenaire gardant 100 % de sa commission. Protège la qualité de livraison sans amputer le gain.

## Livré dans cette session (Étapes 0 à 6 — chantier complet)

| Fichier | Contenu |
|---|---|
| `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md` | Source de vérité : 3 offres + prix réels, escalier, périmètre partenaire, grille de commissions avec exemples en francs, certification par palier, portfolio de preuves (9 clients), **10 règles « ce qu'on ne promet jamais »**, données de marché, périmètre vague 1, points à verrouiller |
| `_documents/nebula-agency/vente/01-AVIS-DE-RECRUTEMENT.md` | Annonce complète + version WhatsApp/statut + affiche A4 avec QR + version réseaux sociaux + **grille de sélection notée /20** + **script d'entretien 10 questions** avec bons et mauvais signaux + message de bienvenue + plan de diffusion sur 14 jours |
| `_documents/nebula-agency/vente/02-MANUEL-DU-PARTENAIRE.md` | **Étape 2.** Le socle du métier de vendeur : marché et 4 barrières à l'achat, escalier des offres avec exemple à 100 000 F sur un seul client, prospection (liste des 20 noms, 3 terrains de chasse, rythme cible), **méthode de vente en 7 temps** (Viser, Ouvrir, Diagnostiquer, Montrer, Proposer, Lever, Conclure), les 5 phrases qui tuent une vente, le silence après le prix, séquence de relance J+2/J+7/J+21/J+45, checklist du brief et ses 3 pièges, circuit de l'argent et logique du palier, 10 interdits, mots de jargon à traduire, plan des 7 premiers jours, mémo à savoir par cœur, quiz de certification |
| `_documents/nebula-agency/vente/03-GUIDE-CATALOGUE.md` | **Étape 3.** Guide de vente du Catalogue Digital (50 000 F) sur l'anatomie en 12 chapitres : produit en une phrase, journée réelle du commerçant et ses 3 fuites d'argent, 4 moteurs d'achat avec leurs signaux de repérage, portrait-robot + 6 signaux de maturité + à qui ne PAS vendre, 8 questions de diagnostic, pitch flash en 3 variantes (marché / restaurant / vendeuse en ligne), démonstration (quel site pour quel métier, déroulé en 6 gestes, signaux d'achat), prix et calcul de rentabilité avec SES chiffres, **12 objections mot pour mot**, conclusion en 5 gestes, montée en gamme (visite J+21, demande de recommandation, chemin à 107 500 F sur un client), brief et ses 3 pièges, **fiche terrain** à garder en capture d'écran, quiz en 10 questions |
| `_documents/nebula-agency/vente/04-GUIDE-VITRINE.md` | **Étape 4.** Guide de vente de la Vitrine Digitale (150 000 F). Ressort totalement différent du Catalogue : on vend **la crédibilité**, pas le temps gagné. Les 5 humiliations vécues (« vous avez un site ? », le gros contrat perdu sans explication, le concurrent moins bon qui a l'air plus sérieux, la diaspora qui ne peut pas vérifier), 4 moteurs (crédibilité / être trouvé / fierté / clients plus gros), déclencheurs d'achat à repérer dans ses phrases, à qui NE PAS vendre (règle : dans le doute, vendre le Catalogue), **le test Google** avec ses 3 règles absolues (ne jamais rire, ne jamais dire « vous n'existez pas », laisser le silence), 8 questions de diagnostic, démonstration + le geste « lui, il apparaît » à ne faire qu'une fois, prix rapporté à son plus gros client de l'année (jamais comparé au Catalogue), question du budget avant annonce, **12 objections** dont « je préfère commencer par le catalogue » traitée comme une VENTE et non comme une objection, « mon neveu peut le faire » (répondre délai + suivi, jamais compétence), conclusion en plusieurs visites avec suivi J+2/J+5/J+12/J+30, montée en gamme depuis le Catalogue (le chemin le plus rentable) et vers l'Outil métier, brief et ses 3 pièges (avis clients jamais inventés, photos de réalisations, phrase de positionnement écrite à sa place), fiche terrain, quiz |
| `_documents/nebula-agency/vente/05-GUIDE-OUTIL-METIER.md` | **Étape 5.** Guide de vente de l'Outil Digital sur mesure (55 000 à 500 000 F), **accès réservé** (3 ventes + binôme Mongazi sur les 3 premiers dossiers). Principe directeur : sur cette offre le partenaire **ne conclut pas, il détecte, qualifie et passe la main**. Le patron qui ne dort pas bien et ses 4 fuites (dettes oubliées, marge inconnue, stock qui s'évapore, temps du patron), 4 moteurs (contrôle / argent qui fuit / pouvoir grandir / peur de tout perdre), **5 signes d'un vrai dossier** (il en faut 2) + **3 questions qui disqualifient en 2 minutes**, **le test du cahier** avec ses 3 règles (ne jamais dénigrer le cahier), 8 questions de diagnostic dont celle qui donne le cahier des charges, **la règle d'or de la démonstration** (« ce n'est pas ça que vous aurez ») sans laquelle le client est déçu à la livraison, la fourchette expliquée (le configurateur fait le prix, jamais le partenaire de tête), 3 façons honnêtes de rapporter le prix à son argent, 12 objections dont « mon cahier me suffit », « j'ai déjà essayé un logiciel » et les factures normalisées (⚠️ jamais promettre la conformité DGI), **conclure = obtenir le rendez-vous de cadrage**, dossier de qualification en 10 points à rapporter le jour même, acceptation du cycle long (2 à 6 semaines, on continue à vendre des Catalogues pendant ce temps), fiche terrain, quiz |
| `_documents/nebula-agency/vente/06-ARSENAL-SCRIPTS.md` | **Étape 6a.** Tous les messages prêts à copier : 7 règles du message qui marche (court, une seule question, jamais de prix au premier message, jamais 3 messages d'affilée), premier contact (à froid, après boutique, par connaissance commune, annonce à son propre réseau au jour 1), après démonstration, relances J+2/J+7/J+21/J+45 + réveil d'un refus à 3 mois, après-vente (confirmation immédiate, message de mi-parcours, livraison avec les 3 conseils de démarrage, demande d'avis, demande de recommandation), réponses rapides aux questions fréquentes, 5 statuts WhatsApp, script de recrutement d'un filleul, tableau « ce qu'on n'écrit jamais » |
| `_documents/nebula-agency/vente/simulateur-commissions.html` | **Étape 6b.** Page autonome (1 fichier, 0 dépendance, 0 image, marche hors ligne, cibles ≥44px, `prefers-reduced-motion`) : le partenaire entre ses ventes du mois → commission, palier, CA, et surtout **combien de ventes il lui manque pour changer de palier + le bonus rétroactif sur ce qu'il a déjà vendu**. Réseau N1/N2 en option (moyenne 100 000 F, à ajuster après la vague 1). Bouton de partage WhatsApp. QC : balises équilibrées, `node --check` OK, 7 cas de calcul vérifiés conformes au socle. Double usage : motivation des partenaires + démonstration en entretien de recrutement |
| `_documents/nebula-agency/vente/07-MISE-EN-LIGNE.md` | **Étape 6c.** Procédure de publication dans la Documentation de l'espace partenaire (le module existe, rien à développer), catégories à utiliser, conversion PDF (option rapide / option premium à la charte cosmique), ⚠️ **alerte : les 5 anciens guides seedés dans `server.py` contredisent la nouvelle stratégie** (ils poussent la Vitrine en premier alors qu'on entre par le Catalogue) et doivent être retirés ou réécrits, **les 11 points à trancher avant d'ouvrir le recrutement** classés par blocage, ordre de lancement en 8 étapes dont l'ajustement des guides après 30 jours de terrain |
| `_documents/nebula-agency/INDEX.md` | Nouvelle section « Vente & recrutement » |

Tout est ancré sur des données **réelles du dépôt** : grille tarifaire de
`00-nebula-agency/CONTEXT.md`, commissions de `_memoire/affilies/cerveau-affilies.md`,
chiffres de marché de `_memoire/analyse-marche.md`, réalisations de `clients/`.

## Reste à faire

- ~~**Étape 2** : `02-MANUEL-DU-PARTENAIRE.md`~~ **FAIT** (livré ci-dessus)
- ~~**Étape 3** : `03-GUIDE-CATALOGUE.md`~~ **FAIT** (livré ci-dessus)
- ~~**Étape 4** : `04-GUIDE-VITRINE.md`~~ **FAIT** (livré ci-dessus)
- ~~**Étape 5** : `05-GUIDE-OUTIL-METIER.md`~~ **FAIT** (livré ci-dessus)
- ~~**Étape 6** : arsenal de scripts, simulateur de commissions, procédure de mise en ligne~~ **FAIT** (livré ci-dessus)
- **Trancher les 11 points en attente** (détaillés dans `07-MISE-EN-LIGNE.md` §6) — bloquant
- **Conversion HTML premium → PDF** de chaque document (charte cosmique, comme le Playbook Boussole)
- **Retirer ou réécrire les 5 anciens guides seedés** dans `nebula-affilies/server.py` (`seed_docs`),
  qui contredisent la stratégie de l'escalier (ils poussent la Vitrine en premier)
- **Publier les guides** dans la Documentation de l'espace partenaire
- **Ajuster les guides après 30 jours de terrain** avec les objections réellement entendues

## À confirmer par Mongazi avant diffusion aux partenaires

- Procédure d'encaissement client (numéro Mobile Money officiel, acompte, justificatif)
- Existence et montant d'un acompte sur l'Outil métier
- **Délai de paiement des commissions** après réclamation (première question de tout bon vendeur)
- Durée de validité d'un lead déposé par un partenaire
- Date limite de candidature à insérer dans l'annonce
- **Nombre de produits inclus dans les 50 000 F du Catalogue** (question terrain n°1 des vendeurs)
- **Tarif et conditions des modifications après livraison** (ajout de produits, changement de prix)
- **Nombre de pages inclus dans les 150 000 F de la Vitrine** (page unique ou hub multi-pages ?)
- **Ce qui est inclus exactement dans la Vitrine** (galerie, devis, prise de RDV, carte, avis, FAQ)
- **Nom de domaine personnalisé** (type `graindesthetique.com`) : inclus ou en supplément, à quel prix ?
- **Acompte sur l'Outil métier**, et **base de calcul de la commission** sur un projet à tranches
  (montant total, ou sommes réellement encaissées ?)
- **Boussole vendable par un partenaire ?** Beaucoup de dossiers détectés sur le terrain seront des cas
  Boussole et non du sur-mesure. Si oui, à quelle commission ?
- **Délai indicatif** que le partenaire a le droit d'énoncer sur l'Outil métier (aujourd'hui : aucun)
