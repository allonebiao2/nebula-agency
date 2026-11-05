# Grille des fonctions NEBULA VOIX

**L'agent d'appel « parfait, total, fluide », fonction par fonction · étape 2 du chantier · 5 novembre 2026**

Un agent vocal complet pour NEBULA VOIX tient en **85 fonctions réparties en huit familles**. **39 sont indispensables au pilote**, 40 sont nécessaires à la revente et 6 peuvent attendre. La combinaison recommandée par le rapport, **Dograh auto-hébergé, Asterisk et VoiceBlender, couvre environ 59 % des fonctions indispensables** (23 points sur 39). **LiveKit (Agents et SIP, sur LiveKit Cloud) en couvre environ 58 %** (22,5 sur 39). Les deux se tiennent au pilote, mais pas pour les mêmes raisons : Dograh apporte la couche produit (résumé, issue de l'appel, base de connaissances, fiche client avant l'appel), LiveKit un cœur de conversation plus fin et l'hébergement. Sur le seul cœur technique (conversation, tâches pendant l'appel, après l'appel), Dograh couvre 77 % des fonctions indispensables, ce qui recoupe les « environ 75 % » du rapport. Ce qui manque au pilote n'est donc pas d'abord technique : **c'est la conformité** (registre des consentements, preuve, liste d'opposition, purge, information), qu'aucun produit ne vend, plus quatre briques à écrire (garde-fou des prix à l'oral, confirmation WhatsApp, alertes, numéros au format +22901). Pour la revente, l'écart se creuse : **Dograh couvre 50 % des fonctions nécessaires, LiveKit 30 %**, parce que LiveKit n'a ni campagnes ni console ; dans les deux cas, la couche agence (plusieurs clients, facturation en FCFA, Mobile Money, audit) est entièrement à écrire.

*Ce document lit la documentation ; il ne remplace ni un déploiement d'essai, ni l'avis d'un avocat inscrit au barreau du Bénin.*

## Comment lire la grille

**Sources.** Le rapport de l'étape 1 (`reports/Agents vocaux appels au Bénin.md`, 4 novembre 2026) et ses notes de recherche (`research_notes/Agents vocaux appels au Bénin/`) font foi ; cette grille ne les contredit pas. Elle les complète par la documentation officielle de Dograh, LiveKit, Pipecat, Vapi et Retell, **relue le 5 novembre 2026**. Chaque affirmation sur un produit porte un code entre parenthèses (par exemple D1, L7, R4) qui renvoie à la liste des références en fin de document. « À vérifier » signale un point que la documentation lue ne confirme pas ; « inférence » signale une déduction de l'auteur.

**Les trois niveaux d'exigence** suivent la feuille de route du rapport (R8) :

- **Pilote** : ce qu'il faut pour la phase 1 du rapport, « le standard qui décroche » (agent entrant 24 h/24 sur un numéro +229 pour un ou deux clients, prise de rendez-vous, transfert vers un humain, journal des appels), plus le socle de conformité que le rapport exige « dès le prototype » (registre des consentements, liste d'opposition, dossier APDP).
- **Revente** : ce qu'il faut pour les phases 2 et 3 (rappel consenti, campagnes, WhatsApp, ligne locale, plusieurs clients facturés en FCFA).
- **Plus tard** : utile, mais ni le pilote ni la revente n'en dépendent.

**Les deux combinaisons comparées dans la synthèse :**

- **A, recommandée par le rapport** : Dograh auto-hébergé sur un serveur dédié, Asterisk relié par ARI comme pont vers une ligne, VoiceBlender pour l'appel WhatsApp sortant (R4).
- **B, l'alternative** : LiveKit Agents et LiveKit SIP sur LiveKit Cloud, la plateforme de départ du rapport (offre Build gratuite, sans carte) (R8).

**Difficulté** de ce qui reste à construire (estimation de l'auteur, pour un développeur, hors délais administratifs) : **faible**, quelques jours ; **moyenne**, une à trois semaines ; **forte**, plus d'un mois ou dépendance d'un tiers (opérateur, Meta, administration).

**La colonne « Réf. »** donne la source qui justifie le besoin ou le niveau (rapport, notes, Code du numérique) ; les sources des affirmations sur les produits sont dans le texte des cellules.

### La grille en chiffres

| Famille | Fonctions | Pilote | Revente | Plus tard |
|---|---:|---:|---:|---:|
| 1 · Conversation | 12 | 10 | 1 | 1 |
| 2 · Tâches pendant l'appel | 14 | 7 | 5 | 2 |
| 3 · Campagnes | 11 | 2 | 7 | 2 |
| 4 · Après l'appel | 9 | 5 | 4 | 0 |
| 5 · Relances | 6 | 1 | 5 | 0 |
| 6 · Plateforme d'agence | 11 | 0 | 10 | 1 |
| 7 · Conformité Bénin | 11 | 7 | 4 | 0 |
| 8 · Exploitation | 11 | 7 | 4 | 0 |
| **Total** | **85** | **39** | **40** | **6** |

## 1 · Conversation

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| C1 | **Latence de bout en bout.** Le temps entre la fin de la phrase de l'appelant et le premier son de l'agent reste sous la seconde perçue. | Pilote | Cible publique : 800 ms de bouche à oreille, le cadre n'ajoute que quelques dizaines de millisecondes (R4). Mesures sur vrais appels : médiane de 1,3 à 1,8 s chez Telnyx, ElevenLabs, Bland, Vapi et Retell, mesure financée par Telnyx (R3). LiveKit : génération anticipée avant la fin du tour et réglages de prise de parole (L13). Pipecat : Smart Turn en 12 ms sur processeur (R4). Dograh : moteur tiré d'un fork de Pipecat (R4), latences par étape dans les événements d'appel (D16) et dans l'export Noveum (D26). | Mesurer depuis Cotonou (1,5 à 2,5 s attendues, non mesuré, R3) ; placer agent, pont téléphonique et terminaison dans la même région, probablement l'Europe (hypothèse, R5) ; voix rapide (ElevenLabs Flash ou v4 Turbo) en vérifiant que l'accent y survit (R5). **Moyenne.** | R3, R4, R5 |
| C2 | **Interruption (barge-in).** L'appelant coupe la parole, l'agent se tait aussitôt et l'écoute ; un simple « hmm » ne l'arrête pas. | Pilote | Dograh : bascule « Allow Interruption » nœud par nœud, VAD Silero ; quand elle est coupée, **le micro de l'appelant est fermé pendant que l'agent parle** (D5). La documentation se contredit sur la valeur par défaut : désactivée selon D5 et D8, activée selon D9 (à vérifier). LiveKit : interruption adaptative qui distingue une vraie interruption d'un acquiescement, reprise de la phrase après une fausse interruption (L1). Pipecat : depuis la 1.15.0, la réponse est annulée si l'appelant reparle avant la fin de son tour (N2). Vapi : réglages de prise et d'arrêt de parole (V8). Retell : sensibilité aux interruptions (RT9). | Régler nœud par nœud. Attention avec Dograh : une annonce non interruptible ferme le micro, donc un « STOP » dit pendant l'annonce est perdu (D5) ; reposer la question de l'opposition juste après l'annonce (inférence). **Faible.** | R4, N2 |
| C3 | **Détection de fin de tour.** L'agent sait quand l'appelant a fini, sans lui couper la parole pendant une pause ni laisser un blanc. | Pilote | LiveKit : détecteur de fin de tour qui prend en charge le français parmi 14 langues, version audio locale sur processeur (R4, N2). Pipecat : Smart Turn v3, libre (BSD-2), 23 langues **dont le français** (P4, lu le 5 novembre 2026 ; le rapport le donnait « à confirmer »). Dograh : le VAD « nourrit » la prise de tour, aucun réglage propre de fin de tour documenté (D5) ; disponibilité de Smart Turn dans son fork : à vérifier. Vapi et Retell : réglages d'attente intégrés (V8, RT9). | Seuils plus patients pour les appelants âgés (N2) ; essais sur le jeu d'appels de Cotonou (EX7). Avec Dograh : brancher Smart Turn si le fork le permet (à vérifier). **Moyenne.** | R4, N2 |
| C4 | **Gestion du silence.** Quand l'appelant se tait, l'agent relance poliment, raccroche proprement après un délai, et aucun appel ne dure sans fin. | Pilote | LiveKit : `user_away_timeout` (15 s par défaut) et état « away » pour déclencher une relance (L3). Pipecat : `user_idle_timeout` et événement `on_user_turn_idle` pour des relances graduées (P1). Vapi : messages de relance sur silence, `silenceTimeoutSeconds` de 5 à 3 600 s, durée maximale de 600 s par défaut (V3, V8). Retell : fréquence des messages de relance quand l'appelant est inactif (RT10). Dograh : délai d'attente de réponse par nœud `wait_for_user_response_timeout` (D8) et avertissements de silence dans les événements (D16) ; relance et durée maximale d'appel non documentées (à vérifier). | Avec Dograh : relance graduée (« Vous êtes toujours là ? »), raccrochage, plafond de durée par appel, si le fork ne les offre pas. **Faible à moyenne.** | N2 |
| C5 | **Reformulation et confirmation.** L'agent répète ce qu'il a compris (date, heure, numéro, nom, montant) et attend un « oui » avant d'agir. | Pilote | Aucune plateforme n'en fait une fonction : c'est du script. Dograh conseille des nœuds non interruptibles pour les « résumés de confirmation » (D5). LiveKit : tâche prête à l'emploi qui recueille des chiffres dits ou tapés (L6). | Scripts de confirmation par secteur ; dates et heures dites comme à Cotonou ; numéros relus par paires et normalisés en +22901 (EX9) ; montants relus seulement s'ils viennent de la carte (C10). **Faible.** | R2, R4 |
| C6 | **Ton, voix et accent.** Une voix chaleureuse, au débit posé, que les Béninois reconnaissent comme proche. | Pilote | Toutes les piles laissent choisir la voix. ElevenLabs a des voix françaises étiquetées « African » (Alimata, Amadou, Ali Alioum) ; le clone d'un comédien béninois se fait sur son propre compte ; usage commercial dès Starter à 6 $ par mois (R5). Dograh : ElevenLabs, Cartesia, Deepgram et d'autres (D15), ton et personnalité dans le nœud global (D9). LiveKit : greffons Deepgram, Cartesia, OpenAI, Google et LiveKit Inference cités sur la page du dépôt (N2). Vapi : ElevenLabs refacturé au prix coûtant ; Retell : ElevenLabs, Cartesia et d'autres (N3). | Test d'écoute à Cotonou ; consigne de ton par maison ; prononciation des noms locaux. **Faible** (moyenne avec le clone d'un comédien). | R5 |
| C7 | **Compréhension du français parlé à Cotonou.** L'agent comprend l'accent, les noms de quartiers, de plats et de personnes, au téléphone en 8 kHz et dans le bruit. | Pilote | Aucun banc d'essai public ne couvre le français béninois au téléphone (R5). Vocabulaire imposé : LiveKit, paramètre `keyterm` du greffon Deepgram Nova-3 (L12) ; Dograh, 14 moteurs de transcription et indices de langue Deepgram Flux (D14), les « keyterms » n'y étant cités qu'en passant (à vérifier) ; ElevenLabs Scribe, mots-clés à 0,08 $ de l'heure (R5). | Constituer le jeu de 50 appels réels enregistrés avec consentement et comparer Deepgram Nova-3, Scribe v2 Realtime et Gladia (R5, R8) ; listes de vocabulaire par maison (Haie-Vive, Agla, Fidjrossè, plats, prénoms). **Moyenne.** | R5, R8, N6 |
| C8 | **Réduction du bruit de fond.** La rue, le marché, la moto ne déclenchent pas l'agent et ne brouillent pas la transcription. | Revente | LiveKit : Krisp activable sur les trunks entrants et les appels sortants (N2). Pipecat : Krisp VIVA, gratuit jusqu'à 10 000 min par mois sur Pipecat Cloud (N2, P5). Vapi : débruitage de la parole de fond (V8). Retell : modes de débruitage, +0,005 $/min (N3, RT9). Dograh : aucune fonction documentée (à vérifier). | Avec Dograh : brancher un débruiteur, RNNoise (libre, cité chez jambonz, N2) ou Krisp sous licence. **Moyenne.** | N2 |
| C9 | **Base de connaissances de la maison.** Horaires, adresse, prestations, prix, conditions : l'agent répond juste, à partir des données de la maison. | Pilote | Dograh : documents de connaissance attachés à chaque nœud (D7). Vapi et Retell : base de connaissances, +0,005 $/min chez Retell (N3). LiveKit : outils et MCP, pas de base intégrée trouvée (L14, à vérifier). Repère de vendeur : 90 à 95 % des questions d'horaires, d'adresse et de tarifs réglées seules (R6). | Lire la carte à la source, comme les lecteurs de LE STANDARD qui « n'exécutent aucun code » (ST) ; une fiche par maison. **Faible.** | R6, ST |
| C10 | **Garde-fou des prix.** Aucun montant absent de la carte de la maison ne sort de la bouche de l'agent. | Pilote | Aucune plateforme. LE STANDARD le fait à l'écrit : il relit chaque réponse avant l'envoi et bloque tout montant que la carte ne porte pas, attaché à l'article nommé (ST). | Le porter à l'oral : relire phrase par phrase avant la synthèse, puisque le texte part en voix au fil de l'eau (R4) ; une chaîne reconnaissance, modèle, synthèse le garde intact, le parole-à-parole l'affaiblit (R5). **Moyenne à forte.** | R4, R5, ST |
| C11 | **Langues : le français d'abord, le fon vers un humain.** L'agent parle français (anglais si besoin) et passe la main dès que l'appelant veut parler fon ou une autre langue locale. | Pilote (parler fon : plus tard) | Aucune synthèse commerciale en fon : MMS-TTS-fon est sous licence non commerciale, et une agence de Dakar n'annonce que 10 à 30 % de résolution en langues locales (R5). Détection de langue : indices de langue Deepgram Flux dans Dograh (D14). Transfert : voir T5. | Règle de bascule dans le prompt global et outil de transfert ; suivre l'IIDiA et « J'aime ma langue », partenaires naturels (R5). **Faible.** | R5 |
| C12 | **Passage de relais entre agents spécialisés.** Un agent d'accueil confie l'appel à un agent « rendez-vous » ou « réclamations » sans que l'appelant le sente. | Plus tard | Dograh : outil « Transfer to Agent », l'agent suivant reçoit l'historique (D23). Vapi : « squads » et passages de relais silencieux (V8). Retell : « Agent Transfer » (RT9). LiveKit : passages de relais et tâches (L14). | Rien d'urgent : un agent par maison suffit au pilote. **Faible.** | aucune |

## 2 · Tâches pendant l'appel

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| T1 | **Prise de rendez-vous dans un agenda.** L'agent lit les créneaux libres, réserve, déplace ou annule, puis confirme. | Pilote | Vapi : outil Google Calendar (disponibilités, création d'événements) et GoHighLevel (V8). Retell : outils Cal.com intégrés (RT9). Dograh : aucun connecteur natif, un seul « cal.com » dans toute sa documentation (N1) ; outil HTTP API et outil MCP (D7, D25). LiveKit : outils de fonction et MCP (L14). | Connecteur Google Agenda ou Cal.com en outil HTTP ou MCP ; règles métier (durée de chaque prestation, pauses, délai minimum) ; une version de Cal.com qui accepte les numéros béninois à 10 chiffres (correctif étiqueté en janvier 2026, R2). **Moyenne.** | R2, R4 |
| T2 | **Fiche client lue avant de parler.** L'agent reconnaît le numéro, salue la personne par son nom et connaît son dernier rendez-vous. | Pilote | Dograh : « Pre-Call Data Fetch », requête POST avant les appels entrants ou sortants dont la réponse JSON devient des variables de l'appel (D6). Retell : fonctions avant l'appel, fiches contacts et mémoire des contacts (RT9). LiveKit : à coder (L14). | Le point d'accès qui répond depuis la fiche client (Supabase, déjà dans la pile NEBULA, ST) ; recherche par numéro normalisé (EX9). **Faible.** | R4 |
| T3 | **Fiche client mise à jour.** Rendez-vous pris, demande, intérêt et opposition sont écrits dans la fiche, pendant ou juste après l'appel. | Pilote | Dograh : nœud webhook en fin d'appel avec modèle de charge utile, identifiants et en-têtes (D8), outil HTTP pendant l'appel (D7). Retell : outils HubSpot, Salesforce, Zendesk et webhook `call_analyzed` signé (RT9). Vapi : outil API Request, Google Sheets, n8n (V8). LiveKit : « data hooks » et outils (L14). | La table des fiches et le récepteur du webhook, protégé par une signature : Dograh ne documente de vérification de signature que pour les webhooks téléphoniques (D12). **Faible.** | R4 |
| T4 | **Outils et fonctions appelés.** Pendant l'appel, l'agent interroge un système (stock, disponibilité, statut d'une commande) et agit (créer, envoyer). | Pilote | Dograh : outils HTTP API, MCP, fin d'appel, transfert (D7, D25). LiveKit : outils de fonction, outils asynchrones, MCP (L14). Pipecat : appels de fonction (N2). Vapi : API Request et Function, paramètres statiques servant de barrière de sécurité (V8). Retell : appel de fonctions (RT9). | Nos points d'accès, authentifiés et rapides ; une liste blanche d'actions par maison. **Faible.** | R4 |
| T5 | **Transfert à froid vers un humain.** L'agent met l'appelant en relation avec un numéro humain et se retire. | Pilote | Dograh : outil de transfert sur Telnyx, Twilio et Asterisk ARI, pas sur les appels web ; musique d'attente, puis l'agent se retire (D2). LiveKit : SIP REFER par `TransferSIPParticipant`, le trunk doit autoriser le transfert (L5). Pipecat : pas de transfert en WebSocket, possible en SIP ou par Daily (P3), 0,20 $ le transfert sur Pipecat Cloud (N2). Vapi : modes « aveugles » (V8). Retell : outil de transfert (RT9). | Un numéro humain joignable par la ligne de l'agent (N2) ; tester le transfert avec la future ligne locale, aux conditions inconnues (R2). **Faible.** | R8, N2 |
| T6 | **Transfert à chaud.** L'agent met l'appelant en attente, présente le cas à l'humain, puis les relie. | Revente | LiveKit : `WarmTransferTask` (bêta, Python) : attente, salle de consultation privée, résumé à l'humain, retour à l'appelant si personne ne répond (L4). Vapi : cinq modes « warm » avec résumé, sur Twilio (V7). Retell : transfert chaud avec résumé (N3). jambonz : transferts avec brief parlé (N1). Dograh : présentation parlée de 25 mots au plus aux deux parties, **sur Twilio seulement**, désactivée par défaut, sans consultation privée (D2). | Avec Dograh sur Asterisk : consultation privée et présentation à écrire côté Asterisk, ou faire passer ces appels par Twilio. **Forte.** | N1, N3 |
| T7 | **Repli quand l'humain ne décroche pas.** Si personne ne répond (nuit, pause), l'agent reprend l'appelant, prend un message et promet un rappel. | Pilote | LiveKit : la tâche de transfert à chaud revient à l'appelant si le destinataire est indisponible (L4). Vapi : mise en attente pendant qu'on appelle un spécialiste, « avec une action de repli » (V8). Dograh : délai d'attente du destinataire réglable, comportement après ce délai non documenté ; si la destination ne se résout pas, l'agent garde l'appelant (D2). | Avec Dograh : vérifier le retour à l'agent après un échec, sinon l'écrire ; prise de message dans la fiche et alerte à la maison. **Moyenne.** | R6 |
| T8 | **DTMF reçu.** L'appelant tape un code, un choix de menu ou un numéro au clavier. | Revente | LiveKit : prise en charge complète, tâche `GetDtmfTask` (chiffres tapés ou dits), détection de serveur vocal (L6). Pipecat : `DTMFAggregator` (P5). Vapi : réglages de saisie au clavier (V8). Retell : capture du DTMF (RT9). Dograh : non documenté (à vérifier dans le fork de Pipecat). | Avec Dograh : faire remonter les touches d'Asterisk jusqu'à l'agent (à vérifier). Utile aussi comme second moyen d'opposition, « tapez 9 » (inférence). **Moyenne.** | N2 |
| T9 | **DTMF envoyé et navigation d'un serveur vocal.** L'agent qui appelle un standard d'entreprise traverse le menu. | Plus tard | LiveKit : envoi de DTMF ; la détection de répondeur passe la main à la navigation quand elle reconnaît un serveur vocal (L6, L7). Pipecat : navigation de menus par IA (P5). Retell : « Press digit » (RT9). Vapi : outil DTMF (V8). Dograh : non documenté. | Seulement pour le B2B vers des numéros impersonnels (R1). **Moyenne.** | R1 |
| T10 | **Détection de répondeur.** Sur un appel sortant, l'agent sait s'il parle à une personne, à une messagerie ou à un serveur vocal. | Revente | Dograh : `detect_voicemail`, nœud de départ seulement, et l'agent **raccroche automatiquement** s'il détecte une messagerie (D8, D9) ; issue `voicemail_detected` (D4). LiveKit : cinq classes (personne, serveur vocal, messagerie, messagerie indisponible, incertain), parole de l'agent suspendue pendant l'analyse (L7). Pipecat : `VoicemailDetector` (P2). Vapi : quatre fournisseurs de détection (V6). Retell : détection activée par défaut sur les nouveaux agents (RT4). VoiceBlender : détection avec repérage du bip (VB). | Mesurer les faux positifs sur les messageries de MTN, Moov et Celtiis, inconnus à ce jour (inférence). **Faible.** | R4 |
| T11 | **Message laissé sur répondeur.** Après le bip, l'agent laisse un message court, identifié, avec le moyen de ne plus être appelé. | Revente | LiveKit : exemple officiel qui laisse un message sur `machine-vm` (L7). Pipecat : message après la fin de l'annonce via `on_voicemail_detected` (P2). Retell : « Leave a message » avec variables (RT4). Vapi : outil Voicemail (V6). Dograh : non, il raccroche (D9). VoiceBlender : repère le bip (VB), dépôt du message à vérifier. | Avec Dograh : à écrire, ou par VoiceBlender. Le message est une prospection par automate : seulement vers des personnes consentantes, avec l'identité de la maison et le moyen de s'opposer (art. 330 et 336, inférence). **Moyenne.** | R1 |
| T12 | **Prise de commande pendant l'appel.** L'agent compose un panier sur la carte réelle, annonce le total, récapitule et transmet au patron. | Revente | Aucune plateforme. LE STANDARD le fait par écrit, carte lue à la source, cinq façons d'avoir un prix (ST). | Porter le moteur de LE STANDARD à l'oral avec le garde-fou C10 ; rappeler le droit de renonciation de 30 jours de la vente à distance (loi 2007-21, art. 5, à faire confirmer) (R1). **Moyenne.** | R1, ST |
| T13 | **Paiement Mobile Money pendant ou juste après l'appel.** L'agent envoie un lien de paiement et vérifie l'encaissement. | Plus tard | Aucune plateforme d'agents vocaux ne parle de Mobile Money (R7). NEBULA encaisse déjà par SasPay et FedaPay sur PISTE et MA LETTRE À… (R7). | Bloqué par le droit plus que par la technique : pendant le délai de renonciation, le vendeur ne peut exiger « aucune contrepartie, notamment le versement d'acompte » (loi 2007-21, art. 6, à faire confirmer par un avocat) (R1, N4). **Moyenne** techniquement. | R1, R7, N4 |
| T14 | **Fin d'appel propre.** L'agent conclut, salue, raccroche et note l'issue. | Pilote | Dograh : nœud et outil de fin d'appel ; une issue fixée par l'outil n'est pas écrasée (D4, D25). LiveKit : `EndCallTool` (L14). Vapi : outil Hang Up (V8). Retell : outil End call (RT9). | Phrases de clôture par maison. **Faible.** | aucune |

## 3 · Campagnes

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| CA1 | **Import de listes.** Charger un fichier de contacts dont les colonnes personnalisent l'appel (prénom, dernier achat). | Revente | Dograh : CSV avec colonne `phone_number`, les autres colonnes deviennent des variables, accueil remplaçable contact par contact (D1). Vapi : CSV jusqu'à 10 000 contacts par campagne (N3). Retell : listes de contacts du Dialer, les « batch calls » sont dépréciés (RT1). LiveKit : rien (N1). | Refuser à l'import tout contact sans consentement valide ou inscrit sur la liste d'opposition (CA7, CA8) ; normaliser en +22901 (EX9) ; garder la source de chaque contact, à dire au premier appel (art. 416, R1). **Moyenne.** | R1, R4 |
| CA2 | **Appels simultanés.** Plusieurs appels en parallèle, sous un plafond. | Revente | Dograh : concurrence réglable, « plafonnée par votre offre téléphonique » (D1). Vapi : 4, 10 ou 30 selon l'offre ; Retell : 20 inclus (R3). LiveKit Cloud : 5 sessions en Build, 20 en Ship (N2). | Plafond par maison (AG6). **Faible.** | R3 |
| CA3 | **Rappels automatiques.** Nouvelle tentative quand personne ne répond, que la ligne est occupée ou qu'une messagerie décroche. | Revente | Dograh : `max_attempts` et `retry_interval_minutes` sur « pas de réponse, occupé, répondeur » (D1). Retell : séquences avec tentatives, délais et double numérotation (RT2). Vapi : nouvelles tentatives seulement en attendant de la concurrence, une heure au plus ; relances sur non-réponse non documentées dans les pages lues (V1, à vérifier). LiveKit : rien. | Plafond de pression par personne, que le Code ne fixe pas (R1) ; arrêt avant 4 appels WhatsApp sans réponse, qui révoquent la permission (R2). **Faible.** | R1, R2 |
| CA4 | **Rappel à l'heure demandée.** « Rappelez-moi demain à 15 h » : l'agent note l'heure et l'appel part à ce moment. | Revente | Retell : « Auto-schedule callbacks », l'agent demande l'heure, la relit, et l'appel part à cette heure, même hors plage (RT2). Dograh : issue `callback_requested` (D4), aucun planificateur documenté. Vapi : appels planifiés par API (V8). | Avec Dograh : extraire l'heure dans une variable de nœud (D7) et planifier un appel par l'API (D25). **Moyenne.** | R8 |
| CA5 | **Plages horaires.** On n'appelle que les jours et aux heures permis. | Revente | Dograh : créneaux par jour avec fuseau horaire de campagne ; sans créneau, il numérote en continu (D1). Vapi : fenêtre planifiable jusqu'à 7 jours (V1). Retell : plage dans le fuseau de chaque contact (RT1). | Une fenêtre NEBULA imposée, que le client ne peut pas élargir : le Code ne fixe aucun horaire, la recherche retient 8 h à 21 h comme fenêtre de bon sens (guide TCPA d'ElevenLabs) (R8) ; jours fériés béninois. **Faible.** | R8 |
| CA6 | **Fuseaux horaires.** Chaque pays appelé à son heure locale. | Plus tard | Retell : fuseau de chaque contact (RT2). Dograh et Vapi : un fuseau par campagne, Vapi conseille de séparer les publics par fuseau (D1, V1). | Une campagne par pays au Togo et en Côte d'Ivoire, dont le fuseau diffère de celui du Bénin (connaissance générale) ; un pays, un dossier de conformité (R1). **Faible.** | R1 |
| CA7 | **Liste d'opposition.** Toute personne qui a dit non n'est plus jamais appelée par aucune campagne de la maison. | Pilote | Retell : l'agent reconnaît la demande, confirme une fois, raccroche et marque le contact, que les campagnes sautent ensuite (RT3). Vapi : webhook avant numérotation qui demande à notre serveur si le contact est éligible (V2). Dograh : issue `do_not_call` (D4) et inscription dans la liste DNC de VICIdial seulement (D18), aucune liste native (N1). LiveKit : rien. | Liste native par maison et globale, contrôlée à l'import et juste avant chaque numérotation, accusé de réception « sans délai » (art. 334, R1). Avec Dograh, ce contrôle avant numérotation n'est pas documenté : il faudra peut-être modifier son code (à vérifier). **Moyenne à forte.** | R1, R4, R8 |
| CA8 | **Registre des consentements.** Pour chaque personne : qui a dit oui, à quoi, pour quelle maison, par quel canal, avec quel texte, quand, et s'il l'a retiré. | Pilote | Aucune plateforme. Retell fait seulement cocher, au lancement d'une campagne, une case qui affirme le respect des consentements (RT1). | Registre horodaté : canal, texte présenté, finalité, maison bénéficiaire, consentement exprès au transfert à l'étranger (art. 392), retrait aussi simple que le don (art. 390) ; relié à l'import (CA1) et à la liste d'opposition (CA7) (R1, R8). **Moyenne.** | R1, R8 |
| CA9 | **Rythme d'appel et disjoncteur.** La cadence s'adapte à la ligne, et la campagne s'arrête seule quand quelque chose casse. | Revente | Dograh : admission au débit ; pause automatique à 50 % d'échecs du pipeline sur 120 s (5 appels au moins) ; pause immédiate sur une erreur 401, 402 ou 403 d'un fournisseur (D1). Retell : cadence et numéros présentés réglables (RT9). | Cadence calée sur les conditions de l'opérateur local, dont beaucoup interdisent les appels automatisés de masse (R1). **Faible.** | R1 |
| CA10 | **Pause, reprise et suivi.** Arrêter, reprendre là où l'on s'était arrêté, suivre l'avancement. | Revente | Dograh : pause, reprise, progression, statuts, résultat par contact (D1). Retell : pause, reprise, analytique de campagne (RT1). Vapi : campagne en lecture seule après création, annulable (V1). | Un écran pour la maison (AP9). **Faible.** | aucune |
| CA11 | **Variantes d'agent (A/B).** Comparer deux scripts sur une même liste. | Plus tard | Dograh : un à cinq couples agent et version, pondérés, par campagne (D19). | Rien. **Faible.** | aucune |

## 4 · Après l'appel

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| AP1 | **Enregistrement.** L'appel est enregistré, réécoutable et téléchargeable. | Pilote | Dograh : chaque exécution porte une adresse d'enregistrement, téléchargeable par un lien à durée limitée (D13). LiveKit Cloud : enregistrements envoyés automatiquement et lisibles dans Agent Insights ; Egress vers notre propre stockage (L8). Pipecat : enregistrement de l'audio (P5). Vapi : stockage Vapi ou S3 à nous (V5). Retell : historique des appels (RT9). | Annonce de l'enregistrement (CF1) ; stockage dans une région déclarée (CF5) ; purge (CF4). **Faible.** | R1 |
| AP2 | **Transcription.** Le texte complet de l'appel, horodaté. | Pilote | Dograh (D13), LiveKit Cloud (L8), Pipecat (P5), Vapi (V5), Retell (RT9). | Rien, sinon la qualité (C7). **Faible.** | aucune |
| AP3 | **Résumé.** Deux lignes qui disent ce qui s'est passé. | Pilote | Dograh : nœud QA après l'appel, résumé d'une à deux phrases dans son invite par défaut (D3). Retell : `call_summary` intégré à chaque appel (RT8). Vapi : résumés et sorties structurées (V4). LiveKit : rien d'intégré trouvé dans les pages lues (L8). | Rien avec Dograh ; avec LiveKit, une passe du modèle après l'appel. **Faible.** | aucune |
| AP4 | **Humeur.** L'état de l'appelant (satisfait, hésitant, fâché). | Revente | Dograh : humeur positive, neutre ou négative dans le QA par défaut (D3). Retell : `user_sentiment`, déduit du texte et non du ton (RT8). Vapi : à définir en sortie structurée (V4). LiveKit : rien. | Alerte à la maison sur les appels « fâchés ». **Faible.** | aucune |
| AP5 | **Issue de l'appel.** Une étiquette unique : rendez-vous pris, rappel demandé, pas intéressé, mauvais numéro, opposition, répondeur. | Pilote | Dograh : issues de départ `qualified`, `not_interested`, `wrong_number`, `voicemail_detected`, `do_not_call`, `callback_requested`, plus des issues propres (50 au plus, par exemple `appointment_booked`), choisies par le modèle à la fin de l'appel (D4). Retell : `call_successful` (RT8). Vapi : sorties structurées (V4). LiveKit : rien. | Une liste d'issues commune à toutes les maisons, pour comparer. **Faible.** | aucune |
| AP6 | **Qualification du prospect.** Champs extraits (intérêt, budget, délai) et note de chaleur. | Revente | Dograh : extraction de variables par nœud (texte, nombre, booléen) (D7). Retell : catégories booléen, sélecteur, texte, nombre (RT8). Vapi : sorties structurées (V4). | Attention : une notation automatique à grande échelle qui « évalue » les personnes appelle très probablement une analyse d'impact (art. 428), et aucun refus ne doit en découler sans humain (art. 401) (R1). **Faible** techniquement. | R1 |
| AP7 | **Notation qualité.** Chaque appel reçoit une note et des étiquettes de défauts. | Revente | Dograh : revue par un modèle, note de 1 à 10, étiquettes `DEAD_AIR`, `USER_FRUSTRATED`, `ASSISTANT_IN_LOOP`, `USER_DETECTS_AI`, échantillonnage réglable (D3). Retell : AI QA (hallucinations, exactitude de la base, latence, humeur), 0,10 $ par appel (N2, RT9). LiveKit : cadre de test avec juges, hors production (L14). | Grille NEBULA : annonce dite ? opposition offerte ? prix exacts ? transfert réussi ? **Faible.** | R1 |
| AP8 | **Journal des appels.** La liste des appels, filtrable, avec écoute, texte, durée, coût et issue. | Pilote | Dograh : page de détail de chaque exécution, liste de toutes les exécutions de l'organisation avec durée, coût et usage (D13). LiveKit Cloud : pages Sessions et Agent Insights, réservées aux administrateurs du projet (L8). Retell : historique des appels (RT9). | Une vue par maison dans notre console (AG1). **Faible.** | R8 |
| AP9 | **Tableaux de bord par client.** Rendez-vous pris, taux de décroché, minutes, coût en FCFA, semaine par semaine. | Revente | Retell : tableaux de bord personnalisés (RT9). Vapi : « Boards » (V8). LiveKit Cloud : trafic, latence et usage des modèles par projet ou par agent (L8). Dograh : aucun tableau de bord documenté au-delà des exécutions (à vérifier dans l'interface). | Tableau de bord client en FCFA, branché sur les exécutions et la facturation (AG4). **Moyenne.** | R4 |

## 5 · Relances

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| RL1 | **Confirmation WhatsApp après l'appel.** La personne reçoit le récapitulatif de son rendez-vous ou de sa demande. | Pilote | Aucune plateforme d'agents vocaux n'envoie de message WhatsApp ; Dograh peut appeler notre émetteur par son nœud webhook (D8). LE STANDARD parle aujourd'hui WhatsApp par Whapi, chemin non officiel qui peut faire suspendre un numéro (ST). | Émetteur par l'API Cloud officielle, chez Meta ou un partenaire (R2) ; hors de la fenêtre de 24 h, un modèle pré-approuvé par Meta est exigé (ST). Un message de confirmation qui ne promeut rien n'est pas une prospection (inférence, R1). **Moyenne.** | R2, ST |
| RL2 | **SMS.** Le même rôle pour ceux qui n'ont pas WhatsApp, nombreux avec 43 % de lignes en 2G (R2). | Revente | Retell : outil et nœud d'envoi de SMS, numéros Twilio (RT9). Vapi : outil SMS intégré (V8). Dograh et LiveKit : rien. | Émetteur SMS (Twilio ou agrégateur, prix au Bénin à vérifier) ; un SMS de prospection exige lui aussi le consentement (art. 332, R1). **Faible.** | R1, R2 |
| RL3 | **Appel WhatsApp sortant sur permission.** L'agent rappelle par WhatsApp quelqu'un qui l'a permis, pour environ 0,0103 $ la minute côté Meta. | Revente | VoiceBlender : seul dépôt libre qui fait l'appel WhatsApp sortant (R4, VB). Dograh : entrant seulement (R4). LiveKit : connecteur réservé à LiveKit Cloud, sortant « dans certaines régions » et sur permission (L16). Meta : permission de 7 jours ou permanente, une demande par 24 h et deux par 7 jours, révocation après 4 appels sortants sans réponse, palier de 2 000 destinataires par jour (R2). | Suivre chaque permission nous-mêmes, la permission temporaire expirant sans webhook (N5) ; compteur d'appels sans réponse ; bascule vers l'appel classique si le réseau ne suit pas (R2). **Forte.** | R2, N5 |
| RL4 | **Appel WhatsApp entrant.** Le client appelle la maison sur WhatsApp, l'agent décroche ; gratuit côté Meta, et cela ouvre une permission de rappel de 7 jours. | Revente | Dograh : appels WhatsApp entrants (R4). Pipecat : réception d'appels WhatsApp (P5). LiveKit : connecteur Cloud (L16). Retell : relié par un outil tiers, wavoice (R2). | Numéro WhatsApp d'entreprise sur l'API Cloud officielle (R2) ; LE STANDARD devra quitter Whapi pour la voix (R2). **Moyenne.** | R2 |
| RL5 | **Séquence multicanal.** Appel, puis message, puis rappel, selon l'issue. | Revente | Retell : séquences du Dialer avec étapes d'appel et de SMS, routage par issue (RT1, RT2). Les autres : rien. | Petit moteur de séquences au-dessus de Dograh et de nos émetteurs. **Moyenne.** | aucune |
| RL6 | **Opposition par message.** Un « STOP » reçu par WhatsApp ou SMS inscrit la personne sur la liste d'opposition. | Revente | Retell : mots-clés d'opposition par SMS (RT3). Les autres : rien. | Lecture des réponses et inscription immédiate (CA7). **Faible.** | R1 |

## 6 · Plateforme d'agence

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| AG1 | **Plusieurs clients cloisonnés.** Chaque maison voit ses agents, numéros, appels et contacts, jamais ceux d'une autre ; NEBULA voit tout. | Revente | Dograh : ressources rattachées à une organisation, une clé API ne touche que la sienne (D25, D12) ; aucun super-administrateur qui gère des organisations clientes n'est documenté (N1). Retell : un espace de travail par client, prévu « pour une agence ou un revendeur », factures séparées (RT5, lu le 5 novembre 2026 ; le rapport, sur la foi d'une revue tierce, ne lui prêtait pas de sous-comptes). Vapi : organisations, 20 $ par organisation au-delà du forfait (R3). LiveKit : projets Cloud (L8). Rapida et QuickVoice : organisations natives (R4). | Console d'agence : créer, suspendre, archiver une maison avec ses quotas, numéros et agents (R4). **Forte.** | R4 |
| AG2 | **Marque blanche.** Logo, couleurs, domaine au nom de la maison ou d'un revendeur. | Revente | Dograh : licence BSD-2 qui permet de rebaptiser l'interface (R4) ; domaine personnalisé de l'instance (D25) ; aucun thème par client documenté (N1). Rapida : marque Rapida obligatoire sans licence commerciale (R4). Synthflow : en contrat Enterprise seulement (R3). | Thème et domaine par maison ou par revendeur. **Moyenne.** | R3, R4 |
| AG3 | **Rôles et droits.** Super-administrateur NEBULA, administrateur de la maison, lecteur. | Revente | Retell : Admin, Developer, Analyst, Viewer et rôles personnalisés (RT5). Vapi : SSO et rôles en offre Premier (R3). Dograh : authentification locale par e-mail et mot de passe (D24), rôles non documentés (à vérifier). | Rôles et périmètres ; inscription publique fermée (D10). **Moyenne.** | R4 |
| AG4 | **Facturation à la minute en FCFA.** Chaque maison paie au tarif convenu, avec une marge sur les coûts réels. | Revente | Dograh : coût de chaque exécution en dollars, par API (D13) ; Paygent applique des grilles de marge mais ne dit rien des moyens de paiement ni des devises (D11). QuickVoice : portefeuille prépayé Stripe (R4). | Moteur de tarification en FCFA (taux du dollar à fixer au jour du calcul, R3). Attention : pour rester hors du régime télécom, vendre « des appels réalisés pour le compte du client, jamais des minutes » (R1) ; l'unité de facture se rédige en conséquence (à faire valider par l'ARCEP ou un avocat). **Moyenne.** | R1, R4, R6 |
| AG5 | **Paiement Mobile Money et portefeuille prépayé.** La maison recharge son solde par MTN MoMo, Moov ou Celtiis Cash. | Revente | Aucune plateforme ni surcouche d'agence : elles facturent par Stripe ou par carte (R3, R7). NEBULA encaisse déjà par SasPay et FedaPay (R7). | Portefeuille, recharge par SasPay, coupure à solde nul (R8). **Moyenne** (circuit déjà connu chez NEBULA). | R7, R8 |
| AG6 | **Quotas et coupure.** Minutes, appels simultanés et numéros plafonnés par maison ; alerte avant épuisement, arrêt à solde nul. | Revente | Dograh : une erreur `QUOTA_EXCEEDED` existe au niveau de l'organisation, son réglage n'est pas documenté (D12, à vérifier). Vapi : à 0 $ sans recharge automatique, aucun appel ne part (N3). | Quotas par maison, alerte à 80 %, coupure propre, jamais au milieu d'un appel. **Moyenne.** | R4 |
| AG7 | **Journal d'audit.** Qui a modifié un agent, importé une liste, exporté des enregistrements, touché à un consentement, et quand. | Revente | Aucune plateforme documentée ; les traces de Dograh décrivent les appels, pas les actions des utilisateurs (D16). | Journal inaltérable des actions, utile au registre des activités (art. 435) et à la preuve (art. 332) (R1). **Moyenne.** | R1 |
| AG8 | **Numéros par client.** Chaque maison a son numéro +229 ou WhatsApp, rattaché à son agent. | Revente | Dograh : configurations téléphoniques, numéros et numéro appelant par défaut, par API (D21) ; domaine SIP géré par organisation (N1). LiveKit : trunks et règles de distribution (L14). | Affectation des numéros et suivi de leurs abonnements (27 $ par mois chez Twilio, R2). **Faible.** | R2 |
| AG9 | **Constructeur d'agents et gabarits par secteur.** Créer un agent sans coder, à partir d'un modèle « institut », « clinique », « restaurant ». | Revente | Dograh : constructeur visuel, nœuds, transitions, nœud global (D9). Retell : « conversation flow » (RT9). Vapi : assistants et squads (V8). LiveKit : Agent Builder (L8). | Gabarits par secteur, dans la logique de « product factory » de NEBULA (ST). **Moyenne.** | R4 |
| AG10 | **Versions et mise en production.** Publier une version, revenir en arrière, tester avant. | Revente | Dograh : workflows publiés, version épinglable dans une campagne (D3, D19). Vapi : versions et configuration en code (V8). LiveKit Cloud : gestion des déploiements (L14). | Règle : aucune publication sans passage au banc d'essai (EX7). **Faible.** | aucune |
| AG11 | **API et webhooks pour les clients.** Une maison branche ses propres outils. | Plus tard | Dograh : clés API par organisation (D25). Retell : webhooks signés par `X-Retell-Signature` (RT9). | Documentation pour les clients. **Faible.** | aucune |

## 7 · Conformité Bénin

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| CF1 | **Annonce de l'appelant et de l'IA.** Dès les premières secondes : la maison pour laquelle on appelle, le caractère automatique, l'enregistrement, et comment dire non. | Pilote | Aucune loi n'oblige à dire « IA », mais les art. 330, 336 et 415 l'imposent en pratique, et ElevenLabs l'exige de ses clients (R1). Phrase proposée par la recherche : « Bonjour, ici l'assistant automatique de la maison X ; cet appel peut être enregistré ; dites STOP pour ne plus être appelé » (R1, à valider). Dograh : phrase fixe dite à la connexion ou audio préenregistré (D6, D22). LiveKit, Vapi, Retell : premier message de l'agent (L14, V8, RT10). | Phrase validée par un avocat, verrouillée (la maison ne peut ni la retirer ni la modifier), contrôlée par le QA (AP7) ; avec Dograh, ne pas fermer le micro pendant l'annonce (C2). **Faible.** | R1 |
| CF2 | **Opposition offerte à chaque appel.** Le moyen de ne plus être appelé est donné à chaque appel, et un « non » est pris en compte tout de suite, avec accusé de réception. | Pilote | Retell : détection de la demande dans toutes les langues, confirmation unique, fin d'appel, contact marqué (RT3). Dograh : issue `do_not_call` choisie à la fin de l'appel (D4), sans prise en compte immédiate. LiveKit : rien. | Outil dédié « opposition », pas une simple consigne ; inscription immédiate dans la liste (CA7) ; accusé de réception par message (art. 333, 334 et 336, R1). **Moyenne.** | R1 |
| CF3 | **Preuve du consentement.** Produire à la demande, pour une personne ou pour l'APDP, la preuve horodatée de son accord. | Pilote | Aucune plateforme. | Export de la preuve tirée du registre (CA8) : texte présenté, canal, horodatage, maison, retrait éventuel, conservés de façon inaltérable ; la charge de la preuve pèse sur celui qui appelle (art. 332 al. 4 et 390, R1). **Moyenne.** | R1 |
| CF4 | **Conservation limitée.** Enregistrements, transcriptions et fiches sont effacés à la date déclarée. | Pilote | LiveKit Cloud : données d'observabilité effacées 30 jours après la session par défaut (L8). Vapi : nettoyage selon la politique de rétention, option « zéro rétention » (V5). Dograh : aucune durée documentée pour les enregistrements, seulement 7 jours pour les journaux techniques (D10). | Purge automatique par maison selon la durée déclarée ; conserver au-delà est une infraction (art. 460-13, R1). **Faible.** | R1 |
| CF5 | **Autorisation APDP de transfert et régions d'hébergement.** Savoir où chaque maillon traite la voix et le texte, et obtenir l'aval de l'APDP avant le premier appel réel. | Pilote | LiveKit Cloud : région de données Union européenne (Francfort) au choix ; modèles servis par LiveKit Inference sans rétention (L8, L9). Dograh : auto-hébergé, donc serveur où l'on veut, mais il envoie aux fournisseurs (modèle, transcription, voix) les données que chaque service exige (D20). | Cartographie des sous-traitants et des pays pour le dossier (art. 409) ; déclaration (art. 405) et autorisation de transfert (art. 391 et 407-6), réponse sous 60 jours prorogeables de 30, le silence valant accord (art. 412) ; consentement exprès au transfert recueilli avec le consentement à l'appel (art. 392) (R1). **Moyenne** (délai administratif). | R1, R8 |
| CF6 | **Aucun numéro masqué, routes légales seulement.** Le numéro affiché est réel et rappelable, et aucun appel ne passe par une route grise ou une passerelle GSM. | Revente | Twilio : présentation du numéro en sortant national « Local (Non-guaranteed) » (R2). LiveKit : numéro appelant choisi à chaque appel (L15), numéro affiché lors d'un transfert réglé sur le trunk (L5). Dograh : numéro appelant par défaut (D21). Retell : rotation des numéros et appels « brandés », aux États-Unis (RT9). | Tester la présentation du numéro sur chaque route ; refuser les routes non-CLI, souvent grises, et toute passerelle SIM (art. 248 : 3 à 5 ans et 500 à 800 millions de FCFA) (R2) ; faire mener le numéro affiché vers l'agent quand on le rappelle ; manier toute rotation de numéros avec prudence au regard de l'art. 336 (inférence). **Moyenne.** | R1, R2 |
| CF7 | **Information complète.** La personne peut connaître ses droits, la durée de conservation, les transferts, la décision automatisée et, pour un contact issu d'une liste, la source de ses coordonnées. | Pilote | Aucune plateforme. | Page d'information par maison, lien envoyé après l'appel (RL1) ; source des données dite au premier appel d'un contact de liste (art. 415 et 416, R1). **Faible.** | R1 |
| CF8 | **Contrat responsable et sous-traitant, registre des activités.** Chaque maison signe un contrat qui fixe qui fait quoi, et NEBULA tient son registre. | Revente | Aucune plateforme : c'est un document juridique. | Contrat type (art. 386) : instructions, sous-traitants ultérieurs et pays, sécurité, sort des enregistrements, partage de la preuve et de la liste d'opposition ; registre (art. 435) (R1, N4). **Faible** techniquement, travail d'avocat. | R1, N4 |
| CF9 | **Aucune décision défavorable sans humain.** L'agent ne refuse jamais seul un crédit, un service ou un contrat. | Revente | Aucune plateforme : c'est une règle de conception. | Règle dans le prompt global et dans le QA ; reprise par un humain (art. 401 et 407-7, R1). **Faible.** | R1 |
| CF10 | **Personnes vulnérables.** Enfant, personne âgée ou malade, personne qui ne comprend pas : l'agent arrête la prospection ou passe la main. | Revente | Aucune plateforme. | Consigne et étiquette de QA ; les exceptions s'y interprètent plus strictement et les peines de l'art. 337 sont doublées (art. 335, R1). **Faible à moyenne.** | R1 |
| CF11 | **Sécurité des données et durcissement.** Accès restreints, chiffrement, données personnelles masquées dans les journaux, aucune porte ouverte. | Pilote | Dograh : télémétrie active par défaut (`ENABLE_TELEMETRY=false` pour la couper), démarrage rapide qui ouvre un tunnel public avec inscription ouverte (`ENABLE_SIGNUP=false` pour la fermer) (R4, D10). LiveKit : masquage des données personnelles, données d'Insights réservées aux administrateurs (L8, L14). Retell : masquage à +0,01 $/min (N3). | Couper la télémétrie et l'inscription, fermer le tunnel, chiffrer les sauvegardes, masquer les numéros dans les journaux (art. 426, R1). **Faible.** | R1, R4 |

## 8 · Exploitation

| N° | Fonction | Niveau | Qui la fait déjà, et comment | À construire nous-mêmes (difficulté) | Réf. |
|---|------------------|------|------------------------------|----------------------|---|
| EX1 | **Disponibilité 24 h/24.** L'agent décroche la nuit, le dimanche, pendant les pics. | Pilote | LiveKit Cloud : service hébergé, 5 sessions simultanées en offre gratuite Build (L11). Dograh : auto-hébergé sur un serveur d'au moins 8 Go de RAM et 4 vCPU, montée en charge par plusieurs workers derrière nginx (R4, N1). Retell : nouvelles tentatives automatiques (RT9). | Serveur dédié, jamais le PC de Cotonou (R4) ; surveillance et redémarrage automatique. **Moyenne.** | R4, R8 |
| EX2 | **Supervision en direct.** Un humain écoute un appel en cours, le reprend ou le coupe. | Revente | Retell : écoute silencieuse, reprise de l'appel, fin d'appel (RT6). Vapi : flux d'écoute en direct et contrôle (parler, transférer, raccrocher) (V8). LiveKit : pensé pour « l'humain avec l'agent » dans une même salle (N2), reprise d'appel non vérifiée. Dograh : non documenté. | Avec Dograh : à écrire, par exemple un pont d'écoute sur Asterisk (à vérifier). **Forte.** | N2 |
| EX3 | **Alertes.** Être prévenu quand l'agent ne répond plus, quand les échecs montent, quand le coût dérape. | Pilote | Retell : règles d'alerte par e-mail ou webhook sur taux de réussite, coût, latence, erreurs (RT7). Dograh : disjoncteur qui met une campagne en pause, sans alerte documentée (D1). LiveKit Cloud : journaux et renvoi des journaux (L14). | Appel de test automatique à heure fixe, alerte à NEBULA et à la maison par WhatsApp ou Telegram. **Faible.** | R8 |
| EX4 | **Reprise après panne.** Si un fournisseur ou le serveur tombe, les appels n'aboutissent pas dans le vide. | Pilote | Vapi : plans de repli pour la voix, la transcription et le modèle (V8). Retell : nouvelles tentatives automatiques et modèles concurrents (RT9). LiveKit : détection des connexions de transcription bloquées (1.8.10), interruption adaptative qui retombe sur le VAD en cas d'erreur (1.8.9) (N2). Dograh : disjoncteur et pause sur erreurs de fournisseur (D1), aucun repli de fournisseur documenté (à vérifier). | Renvoi d'appel vers un humain ou une messagerie si l'agent ne décroche pas (à négocier chez l'opérateur, inférence) ; fournisseur de secours ; sauvegardes testées. **Moyenne.** | N2 |
| EX5 | **Coûts maîtrisés.** Le coût de chaque appel et de chaque maison est connu, la dépense plafonnée. | Pilote | Dograh : coût en dollars de chaque exécution (D13), part de la téléphonie incluse ou non (à vérifier). LiveKit Cloud : usage des modèles par agent (L8). Retell : coût dans l'analytique (RT9). | Conversion en FCFA ; ajout de la téléphonie, qui pèse près de 85 % d'une minute sortante via Twilio (R3) ; plafond mensuel. **Faible.** | R3 |
| EX6 | **Mises à jour et versions figées.** On met à jour après essai, jamais à l'aveugle. | Revente | Dograh publie presque chaque jour, sur un fork de Pipecat (N1) ; Pipecat 1.15.0 a changé un comportement par défaut (R4) ; FreeSWITCH 1.11.3 a apporté des correctifs de sécurité critiques (R4). | Versions figées, montée de version passée au banc d'essai, veille de sécurité sur Asterisk. **Moyenne.** | R4 |
| EX7 | **Banc d'essai.** Avant chaque mise en production, des appels simulés et rejoués notent l'agent. | Pilote | LiveKit : simulations par scénarios, cadre de test avec juges, exécution en intégration continue (L14). Pipecat : scénarios scriptés et simulés (P5). Vapi : simulations (V8). Retell : tests par lots (RT9). Dograh : intégration Tuner (D17), LoopTalk en bêta (N2). Lampline : appelant IA libre qui note bruit, accents, interruptions, latence (R4). | Jeu de 50 appels réels de Cotonou enregistrés avec consentement (R8) ; scénarios par maison. **Moyenne.** | R4, R8 |
| EX8 | **Numéro béninois joignable.** Un +229 qui sonne sur l'agent. | Pilote | Twilio : numéros mobiles +229016 à 27 $ par mois, adresse au Bénin exigée (R2). Dograh : Twilio en entrant (R4). LiveKit : trunk SIP Twilio (N2). | Dossier Twilio (extrait RCCM ou facture à l'adresse de NEBULA, à vérifier) ; un moyen de paiement accepté (R7). **Faible.** | R2, R7 |
| EX9 | **Numéros au format +22901.** Tout numéro est normalisé avant de composer ou de chercher une fiche. | Pilote | Aucune plateforme ; une bibliothèque de validation périmée a déjà refusé des numéros béninois valides (cal.com, R2). | Normaliser en `+22901XXXXXXXX`, préfixer de 01 tout numéro à 8 chiffres, ne jamais retirer le 01 (R2, N5). **Faible.** | R2, N5 |
| EX10 | **Raccordement à une ligne locale.** Brancher l'agent sur un trunk MTN, Moov ou Celtiis, seule voie rentable vers les mobiles. | Revente | Asterisk : enregistrement SIP sortant auprès d'un opérateur (module `res_pjsip_outbound_registration`, AS1), relié à Dograh par ARI (R4). LiveKit : SIP REGISTER non pris en charge, il faut intercaler Asterisk ou FreeSWITCH (R4). | Le contrat opérateur, sans offre publique (R2) ; qualification ARCEP du modèle (R1) ; essais de présentation du numéro (CF6). **Moyenne** techniquement, **forte** commercialement. | R2, R8 |
| EX11 | **Observabilité technique.** Traces, latence par étape, erreurs, pour comprendre un mauvais appel. | Revente | Dograh : traces et événements d'appel avec latences par étape (D16), export Noveum (D26). LiveKit : OpenTelemetry et Agent Insights (L14, L8). Pipecat : métriques de premier octet et d'usage (P5). | Un tri par maison. **Faible.** | aucune |

## 9 · Synthèse

### 9.1 Méthode de notation

Chaque fonction indispensable au pilote (39) et nécessaire à la revente (40) reçoit, pour chaque combinaison, **1 point** si la combinaison la fait nativement ou par un réglage documenté, **0,5 point** si elle la fait en partie, sous réserve, ou si la documentation la laisse « à vérifier », **0 point** s'il faut l'écrire. Pour LiveKit, cadre de développement, « nativement » veut dire que la brique et sa recette sont documentées : le code de l'agent est de toute façon à écrire. La note dit ce que la documentation promet, pas ce qu'un déploiement prouvera. Elle est une estimation de l'auteur, comme les pourcentages du rapport (R4).

### 9.2 Résultat

| Famille | Fonctions « Pilote » | A · Dograh + Asterisk + VoiceBlender | B · LiveKit Agents + SIP (Cloud) |
|---|---:|---:|---:|
| Conversation | 10 | 6 (60 %) | 7 (70 %) |
| Tâches pendant l'appel | 7 | 6 (86 %) | 5,5 (79 %) |
| Campagnes | 2 | 0,5 (25 %) | 0 (0 %) |
| Après l'appel | 5 | 5 (100 %) | 3 (60 %) |
| Relances | 1 | 0 (0 %) | 0 (0 %) |
| Conformité Bénin | 7 | 2,5 (36 %) | 3 (43 %) |
| Exploitation | 7 | 3 (43 %) | 4 (57 %) |
| **Indispensables au pilote** | **39** | **23 (59 %)** | **22,5 (58 %)** |
| dont cœur technique (conversation, tâches, après l'appel) | 22 | 17 (77 %) | 15,5 (70 %) |
| **Nécessaires à la revente** | **40** | **20 (50 %)** | **12 (30 %)** |
| **Ensemble (pilote et revente)** | **79** | **43 (54 %)** | **34,5 (44 %)** |

Pour A, sur les 39 fonctions indispensables : 15 sont entièrement couvertes, 16 en partie, 8 absentes (garde-fou des prix, registre des consentements, confirmation WhatsApp, preuve du consentement, purge, information complète, alertes, normalisation des numéros). Pour B : 17 entièrement, 11 en partie, 11 absentes.

**Trois lectures.**

1. **Pourquoi 59 % et pas les 75 % du rapport.** Les deux chiffres ne mesurent pas la même chose. La grille du rapport pèse tout l'objectif sur 15 critères où la technique et les campagnes comptent beaucoup (R4). Ici, chaque fonction de conformité compte autant qu'une fonction technique, et ce sont justement celles qu'aucun produit ne vend. Sur le seul cœur technique, A est à 77 %, en accord avec le rapport, qui disait déjà que la combinaison n'atteint 85 à 90 % qu'« après développement » et que la couche agence et la conformité restent à écrire dans tous les cas (R4).
2. **Au pilote, A et B se valent ; à la revente, A l'emporte nettement.** Le rapport prototype sur LiveKit Cloud (gratuit, sans carte) et vise Dograh en production (R8) : la grille confirme cet ordre. LiveKit gagne sur la conversation (fin de tour en français, interruption adaptative, gestion du silence), le transfert à chaud et l'hébergement ; Dograh gagne sur tout ce qui fait un produit (résumé, issue de l'appel, base de connaissances, fiche client avant l'appel, campagnes) et, surtout, sur la ligne locale, puisque LiveKit ne sait pas s'enregistrer auprès d'un opérateur (R4).
3. **Ce qui bloque le pilote n'est pas technique.** Sur les 16 points qui manquent à A, 6 relèvent de la conformité (dont le registre et la liste d'opposition) et 1 de la confirmation WhatsApp : ils manquent en entier ou presque, et ce sont eux qui interdisent le premier appel réel. Les 9 points techniques manquants sont pour les deux tiers des demi-points (réglage, mesure) ; seuls le garde-fou des prix, les alertes et la normalisation des numéros sont entièrement à écrire. La phrase du rapport tient : le registre des consentements est l'actif principal (R1).

### 9.3 Détail des 39 fonctions indispensables au pilote

| N° | Fonction | A | B | Ce qui fait la différence |
|---|------------|---:|---:|----------------------|
| C1 | Latence de bout en bout | 0,5 | 0,5 | personne n'a mesuré depuis Cotonou |
| C2 | Interruption | 1 | 1 | LiveKit distingue l'acquiescement |
| C3 | Fin de tour | 0,5 | 1 | détecteur français documenté chez LiveKit seulement |
| C4 | Silence | 0,5 | 1 | relance non documentée chez Dograh |
| C5 | Reformulation | 0,5 | 0,5 | du script dans les deux cas |
| C6 | Ton et voix | 1 | 1 | même choix de voix |
| C7 | Français de Cotonou | 0,5 | 1 | vocabulaire imposé documenté chez LiveKit |
| C9 | Base de connaissances | 1 | 0,5 | documents par nœud chez Dograh |
| C10 | Garde-fou des prix | 0 | 0 | à porter depuis LE STANDARD |
| C11 | Fon vers un humain | 0,5 | 0,5 | règle à écrire |
| T1 | Agenda | 0,5 | 0,5 | aucun connecteur natif |
| T2 | Fiche lue avant l'appel | 1 | 0,5 | « Pre-Call Data Fetch » chez Dograh |
| T3 | Fiche mise à jour | 1 | 0,5 | nœud webhook chez Dograh |
| T4 | Outils et fonctions | 1 | 1 | |
| T5 | Transfert à froid | 1 | 1 | |
| T7 | Repli si personne ne décroche | 0,5 | 1 | retour à l'appelant documenté chez LiveKit (bêta) |
| T14 | Fin d'appel | 1 | 1 | |
| CA7 | Liste d'opposition | 0,5 | 0 | Dograh ne passe que par VICIdial |
| CA8 | Registre des consentements | 0 | 0 | personne |
| AP1 | Enregistrement | 1 | 1 | |
| AP2 | Transcription | 1 | 1 | |
| AP3 | Résumé | 1 | 0 | QA de Dograh |
| AP5 | Issue de l'appel | 1 | 0 | issues de Dograh |
| AP8 | Journal des appels | 1 | 1 | |
| RL1 | Confirmation WhatsApp | 0 | 0 | personne |
| CF1 | Annonce | 1 | 1 | |
| CF2 | Opposition à chaque appel | 0,5 | 0 | issue `do_not_call` chez Dograh |
| CF3 | Preuve du consentement | 0 | 0 | personne |
| CF4 | Conservation limitée | 0 | 0,5 | effacement à 30 jours chez LiveKit Cloud |
| CF5 | APDP et régions | 0,5 | 0,5 | serveur au choix (A), région UE (B) |
| CF7 | Information complète | 0 | 0 | personne |
| CF11 | Sécurité et durcissement | 0,5 | 1 | Dograh livré ouvert, à refermer |
| EX1 | 24 h/24 | 0,5 | 1 | serveur à exploiter (A), hébergé (B) |
| EX3 | Alertes | 0 | 0 | personne dans ces deux piles |
| EX4 | Reprise après panne | 0,5 | 0,5 | aucun repli de fournisseur documenté |
| EX5 | Coûts | 0,5 | 0,5 | coûts en dollars, téléphonie à ajouter |
| EX7 | Banc d'essai | 0,5 | 1 | simulations intégrées chez LiveKit |
| EX8 | Numéro +229 | 1 | 1 | Twilio dans les deux cas |
| EX9 | Numéros au format +22901 | 0 | 0 | personne |
| | **Total** | **23** | **22,5** | |

### 9.4 Ce qui reste à construire, dans l'ordre

L'ordre suit la combinaison A et la feuille de route du rapport : d'abord ce qui doit exister avant le premier appel réel, puis ce qui fait marcher le pilote, puis ce qui permet de revendre.

| Rang | Chantier | Fonctions | Difficulté | Pourquoi à ce rang |
|---:|----------------|---------|------|--------------------|
| 1 | **Dossier APDP** : cartographie des sous-traitants et des pays, déclaration, demande d'autorisation de transfert | CF5 | Moyenne (60 jours, prorogeables de 30) | Le plus long ; aucun appel réel avant (R8) |
| 2 | **Socle consentement et opposition** : registre, preuve opposable, liste native par maison et globale, outil d'opposition pendant l'appel, accusé de réception | CA8, CF3, CA7, CF2 | Moyenne (forte si le contrôle avant numérotation oblige à modifier Dograh) | Exigé « dès le prototype » (R8), cœur de la loi (R1) |
| 3 | **Phrase d'ouverture verrouillée et page d'information** | CF1, CF7 | Faible | Couvre les art. 330, 336 et 415 (R1) |
| 4 | **Hébergement durci** : serveur dédié, télémétrie et inscription coupées, tunnel fermé, sauvegardes, purge automatique | CF11, EX1, CF4, EX4 | Faible à moyenne | Dograh est livré ouvert (R4) |
| 5 | **Numéro +229 et normalisation +22901** | EX8, EX9 | Faible | Être joignable, retrouver la bonne fiche |
| 6 | **Banc d'essai de Cotonou** : 50 appels réels consentis, mesure de la latence, choix de la transcription et de la voix, réglage de la fin de tour | EX7, C1, C3, C7, C6 | Moyenne | Aucun banc public ne couvre le français béninois (R5) |
| 7 | **Garde-fou des prix à l'oral et carte lue à la source** | C10, C9 | Moyenne à forte | Règle maison de LE STANDARD (ST), plus difficile en voix (R4) |
| 8 | **Agenda et fiche client** (Google Agenda ou Cal.com, Supabase) | T1, T2, T3 | Moyenne | La prise de rendez-vous est l'usage du pilote (R8) |
| 9 | **Conversation robuste** : relance sur silence, plafond de durée, repli quand l'humain ne décroche pas, bascule du fon, scripts de confirmation | C4, T7, C11, C5 | Faible à moyenne | Les cas qui font raccrocher un client |
| 10 | **Confirmation WhatsApp par l'API officielle** | RL1 | Moyenne | Le récapitulatif fait foi pour le client |
| 11 | **Alertes et coûts en FCFA** | EX3, EX5 | Faible | Un standard 24 h/24 qui se tait doit se voir |
| 12 | **Couche agence** : console multi-clients, rôles, quotas, journal d'audit | AG1, AG3, AG6, AG7 | Forte | Aucun dépôt ne la livre (R4) |
| 13 | **Facturation en FCFA et portefeuille Mobile Money** | AG4, AG5 | Moyenne (SasPay déjà maîtrisé) | La vraie raison d'écrire sa facturation (R7) |
| 14 | **Tableaux de bord clients, marque blanche, gabarits par secteur** | AP9, AG2, AG9 | Moyenne | Ce que voit l'acheteur |
| 15 | **Campagnes conformes** : plage horaire imposée, rappel à l'heure demandée, message de répondeur, DTMF | CA5, CA4, T11, T8 | Moyenne | Le rappel consenti de la phase 2 (R8) |
| 16 | **WhatsApp et SMS** : appels entrants, suivi des permissions, appel sortant par VoiceBlender, SMS, STOP par message, séquences | RL4, RL3, RL2, RL6, RL5 | Forte | Le canal où loi et économie convergent (R2) |
| 17 | **Ligne locale** : Asterisk enregistré chez MTN, Moov ou Celtiis, présentation du numéro, refus des routes grises | EX10, CF6 | Moyenne techniquement, forte commercialement | Sans elle, le sortant classique n'est jamais rentable (R2) |
| 18 | **Transfert à chaud et supervision en direct sur Asterisk** | T6, EX2 | Forte | Dograh ne les fait qu'avec Twilio, ou pas du tout (D2) |
| 19 | **Prise de commande à l'oral** | T12 | Moyenne | Port du moteur de LE STANDARD (ST) |
| 20 | **Le reste de la revente** : contrat type et registre, règles « humain » et personnes vulnérables, versions figées, débruitage, qualification | CF8, CF9, CF10, EX6, C8, AP6 | Faible à moyenne | Nécessaire, sans urgence technique |

Peuvent attendre : passage de relais entre agents (C12), navigation de serveurs vocaux (T9), paiement pendant l'appel (T13, bloqué par l'art. 6 de la loi 2007-21 tant qu'un avocat n'a pas tranché), fuseaux horaires (CA6), variantes A/B (CA11), API pour les clients (AG11).

### 9.5 Ce que la grille ajoute au rapport

- **Smart Turn parle français** : le README du modèle liste le français parmi ses 23 langues (P4). Le rapport le laissait « à confirmer ».
- **La détection de répondeur de Dograh raccroche**, elle ne laisse pas de message (D9) : le message de répondeur (T11) est à écrire avec la combinaison A.
- **Dograh ferme le micro de l'appelant quand l'interruption est coupée** (D5) : une annonce légale non interruptible fait perdre un « STOP » dit pendant l'annonce. Et sa documentation se contredit sur la valeur par défaut de l'interruption (D5, D8, D9).
- **Retell documente désormais un espace de travail par client** pour les agences, avec facturation séparée (RT5), alors que la revue tierce citée par le rapport ne lui prêtait pas de sous-comptes. La marque blanche, elle, n'y est toujours pas documentée.
- **Deux modèles utiles à recopier** : le webhook « avant numérotation » de Vapi (V2), exactement le crochet qu'il faut pour contrôler consentement et opposition juste avant chaque appel ; la gestion de l'opposition de Retell (RT3), qui confirme une fois, raccroche et marque le contact.
- **LiveKit Cloud efface les données d'observabilité à 30 jours et propose une région de données en Europe** (L8, L9) : deux éléments concrets pour le dossier APDP.
- **Dograh connaît une notion de quota par organisation** (erreur `QUOTA_EXCEEDED`, D12), sans en documenter le réglage.

### 9.6 À vérifier avant d'écrire une ligne

Dans le code de Dograh (version figée) : le DTMF, Smart Turn et le débruitage dans le fork de Pipecat ; les mots-clés imposés à la transcription ; le retour à l'agent après un transfert sans réponse ; un super-administrateur et des rôles ; la durée de conservation des enregistrements ; un crochet avant numérotation dans les campagnes ; le réglage des quotas ; la part de téléphonie dans le coût d'une exécution. Ailleurs : le dépôt d'un message de répondeur par VoiceBlender ; une base de connaissances et la reprise d'appel par un humain chez LiveKit ; les relances sur non-réponse chez Vapi ; le prix d'un SMS vers le Bénin. Et toutes les questions juridiques que le rapport renvoie à l'avocat, à l'APDP et à l'ARCEP (R8).

## Références

Documentation officielle relue le 5 novembre 2026 ; rapport et notes du 4 novembre 2026.

| Code | Source |
|---|----------------------------------|
| R1 | Rapport, § « La loi béninoise interdit l'automate d'appel sans accord prouvé » (Code du numérique, loi 2017-20 ; loi 2007-21), `reports/Agents vocaux appels au Bénin.md` |
| R2 | Rapport, § « Terminer un appel au Bénin coûte quarante fois plus que WhatsApp » (Twilio, Meta, plan de numérotation, passerelles GSM) |
| R3 | Rapport, § « Les plateformes se valent à trois centimes près, pas leur caisse » |
| R4 | Rapport, § « Dograh couvre trois quarts du besoin, la couche agence reste à écrire » |
| R5 | Rapport, § « Aucune voix du marché n'a l'accent de Cotonou, sauf à le cloner » |
| R6 | Rapport, § « Le marché paie 60 à 150 FCFA la minute, moins qu'un appel Twilio » |
| R7 | Rapport, § « Payer en Mobile Money : une carte MoMo à tester, trois portes sans carte » |
| R8 | Rapport, § « Démarrer par l'entrant et le rappel consenti, puis négocier une ligne locale » (architecture cible, feuille de route) |
| N1 | Notes, `depots_github.md` (Dograh, VoiceBlender, jambonz, QuickVoice, Rapida) |
| N2 | Notes, `briques_open_source.md` (LiveKit, Pipecat, Asterisk, FreeSWITCH, coûts) |
| N3 | Notes, `plateformes_saas.md` (Vapi, Retell, Bland, ElevenLabs, Telnyx) |
| N4 | Notes, `cadre_legal_benin.md` |
| N5 | Notes, `telephonie_benin.md` |
| N6 | Notes, `voix_tts_stt.md` |
| ST | `CLAUDE.md` du dépôt, sections « LE STANDARD », « Stack technique » et « Positionnement » |
| D1 | [Dograh, Campaigns](https://docs.dograh.com/core-concepts/campaigns.md) |
| D2 | [Dograh, Call Transfer](https://docs.dograh.com/voice-agent/tools/call-transfer.md) |
| D3 | [Dograh, QA](https://docs.dograh.com/voice-agent/qa.md) |
| D4 | [Dograh, Call Dispositions](https://docs.dograh.com/developer/call-dispositions.md) |
| D5 | [Dograh, Interruption Handling](https://docs.dograh.com/configurations/interruption.md) |
| D6 | [Dograh, Start Call](https://docs.dograh.com/voice-agent/start-call.md) |
| D7 | [Dograh, Agent Node](https://docs.dograh.com/voice-agent/agent.md) |
| D8 | [Dograh, Workflow Definition Schema](https://docs.dograh.com/developer/workflow-schema.md) |
| D9 | [Dograh, Editing a Workflow](https://docs.dograh.com/voice-agent/editing-a-workflow.md) |
| D10 | [Dograh, Environment Variables](https://docs.dograh.com/developer/environment-variables.md) |
| D11 | [Dograh, Paygent Integration](https://docs.dograh.com/integrations/paygent.md) |
| D12 | [Dograh, API Errors](https://docs.dograh.com/api-reference/errors.md) |
| D13 | [Dograh, Calls & Runs](https://docs.dograh.com/core-concepts/calls-and-runs.md) et [Retrieve Agent Run Details](https://docs.dograh.com/api-reference/runs/get-run.md) |
| D14 | [Dograh, Transcriber](https://docs.dograh.com/configurations/transcriber.md) |
| D15 | [Dograh, Voice](https://docs.dograh.com/configurations/voice.md) |
| D16 | [Dograh, Call events](https://docs.dograh.com/configurations/call-events.md) et [Tracing](https://docs.dograh.com/configurations/tracing.md) |
| D17 | [Dograh, Tuner Integration](https://docs.dograh.com/integrations/tuner.md) |
| D18 | [Dograh, VICIdial Integration](https://docs.dograh.com/integrations/telephony/vicidial.md) |
| D19 | [Dograh, Create Campaign](https://docs.dograh.com/api-reference/campaigns/create.md) |
| D20 | [Dograh, Model Configurations](https://docs.dograh.com/configurations/inference-providers.md) |
| D21 | [Dograh, Telephony Configs](https://docs.dograh.com/api-reference/telephony-configs.md) |
| D22 | [Dograh, Pre-recorded Audio](https://docs.dograh.com/voice-agent/pre-recorded-audio.md) |
| D23 | [Dograh, Transfer to Agent](https://docs.dograh.com/voice-agent/tools/transfer-agent.md) |
| D24 | [Dograh, Authentication](https://docs.dograh.com/deployment/authentication.md) |
| D25 | [Dograh, index de la documentation](https://docs.dograh.com/llms.txt) (outils HTTP API, MCP et End Call, clés API, domaine personnalisé, montée en charge) |
| D26 | [Dograh, Noveum Integration](https://docs.dograh.com/integrations/noveum.md) |
| L1 | [LiveKit, Turns overview](https://docs.livekit.io/agents/logic/turns.md) |
| L3 | [LiveKit, Agent sessions](https://docs.livekit.io/agents/logic/sessions.md) |
| L4 | [LiveKit, Agent-assisted warm transfer](https://docs.livekit.io/telephony/features/transfers/warm.md) |
| L5 | [LiveKit, Call forwarding (cold transfer)](https://docs.livekit.io/telephony/features/transfers/cold.md) |
| L6 | [LiveKit, Handling DTMF](https://docs.livekit.io/telephony/features/dtmf.md) |
| L7 | [LiveKit, Answering machine detection](https://docs.livekit.io/telephony/features/answering-machine-detection.md) |
| L8 | [LiveKit, Agent insights](https://docs.livekit.io/testing/observability/insights.md) et [Record audio and video](https://docs.livekit.io/testing/observability/recording.md) |
| L9 | [LiveKit, Data residency](https://docs.livekit.io/testing/observability/data-residency.md) |
| L11 | [LiveKit, tarifs](https://livekit.com/pricing) (via R4 et N2) |
| L12 | [LiveKit, Deepgram STT plugin](https://docs.livekit.io/agents/models/stt/deepgram.md) |
| L13 | [LiveKit, Turn-taking tuning](https://docs.livekit.io/agents/logic/turns/tuning.md) |
| L14 | Index LiveKit : [Agents](https://docs.livekit.io/agents/llms.txt), [Test & Evaluate](https://docs.livekit.io/testing/llms.txt), [Manage & Deploy](https://docs.livekit.io/deploy/llms.txt) (outils, MCP, tâches, `EndCallTool`, simulations, masquage des données, OpenTelemetry, journaux) |
| L15 | [LiveKit, Outbound calls](https://docs.livekit.io/telephony/making-calls/outbound-calls.md) |
| L16 | [LiveKit, WhatsApp connector](https://docs.livekit.io/telephony/connectors/whatsapp.md) (via N1) |
| P1 | [Pipecat, Detecting Idle Users](https://docs.pipecat.ai/pipecat/fundamentals/detecting-user-idle.md) |
| P2 | [Pipecat, Voicemail Detection](https://docs.pipecat.ai/pipecat/fundamentals/voicemail.md) |
| P3 | [Pipecat, Telephony Overview](https://docs.pipecat.ai/pipecat/telephony/overview.md) |
| P4 | [Smart Turn, README](https://github.com/pipecat-ai/smart-turn) |
| P5 | [Pipecat, index de la documentation](https://docs.pipecat.ai/llms.txt) (DTMFAggregator, navigation de menus, Krisp VIVA, enregistrement, transcriptions, métriques, scénarios d'évaluation, WhatsApp) |
| V1 | [Vapi, Campaign scheduling and lifecycle](https://docs.vapi.ai/outbound-campaigns/scheduling-and-lifecycle.md) |
| V2 | [Vapi, Campaign webhooks (pre-dial)](https://docs.vapi.ai/outbound-campaigns/webhooks.md) |
| V3 | [Vapi, Call timeout settings](https://docs.vapi.ai/documentation/assistants/conversation-behavior/call-timeout-settings.md) |
| V4 | [Vapi, Call analysis](https://docs.vapi.ai/assistants/call-analysis.md) |
| V5 | [Vapi, Call recording, logging and transcribing](https://docs.vapi.ai/assistants/call-recording.md) |
| V6 | [Vapi, Voicemail Detection](https://docs.vapi.ai/calls/voicemail-detection.md) et [Voicemail tool](https://docs.vapi.ai/tools/voicemail-tool.md) |
| V7 | [Vapi, Configure warm transfer modes](https://docs.vapi.ai/tools/transfer-call/warm-transfer.md) |
| V8 | [Vapi, index de la documentation](https://docs.vapi.ai/llms.txt) (outils intégrés transfert, raccrochage, SMS, DTMF ; Google Calendar ; relances sur silence ; saisie au clavier ; débruitage ; plans de repli ; écoute et contrôle en direct ; Boards ; simulations ; squads) |
| RT1 | [Retell, Outbound call campaigns (Dialer)](https://docs.retellai.com/dialer/overview.md) |
| RT2 | [Retell, Build a sequence](https://docs.retellai.com/dialer/sequences.md) |
| RT3 | [Retell, Do-not-call requests](https://docs.retellai.com/build/do-not-call.md) |
| RT4 | [Retell, Handle voicemail and IVR](https://docs.retellai.com/build/handle-voicemail.md) |
| RT5 | [Retell, Workspaces](https://docs.retellai.com/accounts/workspace.md) et [Access control](https://docs.retellai.com/accounts/access-control.md) |
| RT6 | [Retell, Monitor live calls](https://docs.retellai.com/features/live-monitoring.md) |
| RT7 | [Retell, Alert rules](https://docs.retellai.com/features/alerting-overview.md) |
| RT8 | [Retell, Post Call Extraction](https://docs.retellai.com/features/post-call-analysis-overview.md) |
| RT9 | [Retell, index de la documentation](https://docs.retellai.com/llms.txt) (Cal.com, HubSpot, « Press digit », DTMF, SMS, débruitage, AI QA, tableaux de bord, historique, contacts, fonctions avant l'appel, fiabilité, webhooks signés, numéros et cadence) |
| RT10 | [Retell, Configure global settings](https://docs.retellai.com/build/conversation-flow/global-setting.md) |
| VB | [VoiceBlender, README](https://github.com/VoiceBlender/voiceblender) (via N1) |
| AS1 | [Asterisk, res_pjsip_outbound_registration](https://docs.asterisk.org/Latest_API/API_Documentation/Module_Configuration/res_pjsip_outbound_registration) |
