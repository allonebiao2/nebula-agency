# 2026-11-25 · Les envois du jour, les 10 réponses, le carnet des clients et l'onglet « Chiffres »

Session du mercredi 25/11, de 10 h à 16 h environ. Mongazi envoie depuis son iPhone et transmet les réponses par
captures et transcriptions de vocaux. Numéros et messages complets : dépôt privé `nebula-cap/REPRENDRE-ICI.md`
et `nebula-apercus/prospects-jour/` (jamais ici).

## Les envois
- **21 liens wa.me le matin** : 16 relances des chauds et 5 nouveaux (annonceurs Facebook). Les relances visent les
  « oui » restés bloqués parce qu'on leur demandait des photos (« vous n'avez rien à m'envoyer »).
- Le rythme est choisi par Mongazi : 2 personnes toutes les 5 minutes. Ma recommandation, acceptée : **15 à 20
  relances + 8 nouveaux au plus par jour**, en deux vagues (9 h-11 h et 15 h-17 h). Il n'y a qu'un numéro WhatsApp.
- Les 59 nouveaux en attente sont étalés à 8 par jour, du 26/11 au 4/12 : Bénin d'abord, puis Abidjan et Lomé.
- ⚠️ **Le plan CAP du jour annonçait Omani à 15 h**, mais le rendez-vous avait été reporté au mer. 2/12 (message
  du 23/11). Les 4 tâches Omani ont été déplacées au 2/12.

## Les 10 réponses de Mongazi (règles de travail)
Lien donné = envoyé (je coche moi-même) · une capture par réponse · les produits d'un oui sont pris sur SES pages ·
ordre d'arrivée pour les aperçus · prix au choix + repli 25 000 F payé en une fois · MoMo dans les messages dès
qu'on parle prix · un seul numéro · vagues 9-11 h et 15-17 h · Abidjan et Lomé oui (lien SasPay) · 3 relances puis
dormant. Détail : `nebula-cap/cerveau/Décisions/2026-11-25 · les 10 réponses.md`.

**Règle de prix, ajoutée dans l'après-midi** : « 50 000 F, -20 % = 40 000 F » (20 000 F pour démarrer, 20 000 F à
la mise en ligne), puis **20 000 F tous les 6 mois**, corrections comprises. On peut demander au client s'il
préfère payer 5 000 F par mois ou 20 000 F tous les 6 mois. Cette règle est inscrite dans `Offres et prix.md` du CAP
et dans la fiche de Véga.

## Les réponses de la journée
- **Quesiah** (WhatsApp pro « Benin Beni ») : « pas de budget prévu cette année », « une charge fixe chaque mois,
  non », « je préfère investir et oublier », et elle veut refaire ses photos pro d'abord. Mongazi a répondu en vocal
  avec la formule de 6 mois. J'ai envoyé un récapitulatif écrit : les 20 000 F restants se paient quand ses photos
  pro sont dans le catalogue.
- **Highgameshop** : « donnez-moi jusqu'à demain ». Il avait répondu à 10 h 51, avant la relance de 13 h 12, d'où
  un mot d'excuse.
- **Dayday's Fancy Accessories** (= ElectroniK gadgets, annonceur) : « montrez-moi », puis « je n'ai pas bien
  compris ». Après l'explication « aujourd'hui / avec le catalogue » et un exemple cliquable : « c'est vraiment au
  top ». Il a 3 pubs sponsorisées (montres connectées, tablettes, ventilateurs solaires) et **il a envoyé ses
  produits à Mongazi** : à me transmettre, aperçu promis vendredi après-midi au plus tard.
- **ABD SHOP CHIC** (annonceur) : d'abord une réponse automatique, puis « Possible ». Aperçu promis vendredi
  après-midi au plus tard.
- Une autre session a livré **Semelle Dafrik** (https://semelle-dafrik.pages.dev) et la vitrine offerte de
  **Max · OVRSZ** (https://ovrsz.pages.dev). Les messages sont partis.

## Le carnet des clients et l'onglet « Chiffres » (demande de Mongazi)
- La table `public.nebula_suivi_carnet` a une ligne par événement : contact, relance, réponse, oui, non, objection,
  aperçu, paiement. Elle se remplit avec `suivi/carnet.py note|fiche|stats|remplir|publier`. Mongazi n'a rien à
  remplir : je note à chaque capture.
- L'onglet **« Chiffres »** de https://nebula-suivi.pages.dev montre, sur 24 h, 7 jours et 30 jours :
  - l'entonnoir ;
  - les réponses par source, par métier et par accroche ;
  - ce qui bloque ;
  - les leçons.

  Les chiffres sont calculés sur le PC (`carnet.py publier` → table `nebula_suivi_stats`).
- Chaque envoi est daté à l'heure où il est coché (colonne `envoye_le`, posée par un déclencheur).
- **Première mesure (30 jours, reprise approximative)** : 135 contactés → 44 réponses (33 %) → 23 oui → 8 aperçus →
  0 payé. Google Maps 37 % de réponses, annonceurs Facebook 31 %. Les deux fuites : des oui sans aperçu, et des
  aperçus sans paiement.

## Leçons
1. **« Par mois » fait peur** : annoncer 20 000 F tous les 6 mois, qui reviennent moins cher que 6 × 5 000 F.
2. **Une relance « seulement s'il n'a pas répondu » se vérifie avant de partir** (Highgameshop).
3. **Écrire les liens en entier avec `https://`** : écrit sans, le lien d'Hillary ne s'ouvrait pas dans WhatsApp.
4. **Expliquer par « aujourd'hui / avec le catalogue » + un exemple qu'on peut toucher** : en une minute, le doute
   de Dayday's est devenu « au top ».
5. **Les annonceurs Facebook répondent vite** : 2 oui sur 5 nouveaux en moins de 10 minutes.
