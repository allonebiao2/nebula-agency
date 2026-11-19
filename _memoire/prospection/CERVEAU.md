# PROSPECTION · le cerveau du sprint des fêtes

> **Le point d'entrée.** Une session qui reprend lit ce fichier, puis `ROUTINE.md`, et sait quoi faire en 2 minutes.
> Les pièges techniques et commerciaux : `LECONS.md`. Ouvert le 2026-11-18 (Mongazi : « crée une branche dans le
> cerveau autour de ça, ultra optimisée »).
>
> ⛔ **Ce dépôt est PUBLIC** : aucun numéro, aucun nom de prospect associé à ce qu'il a dit. L'état réel vit dans
> Supabase (`piste.prospection`) et dans le suivi privé **hors dépôt** (voir « Les fichiers »). Ici : des chiffres
> agrégés et des renvois, rien d'autre.
>
> ⚡ **REPRISE (état du 19/11 au soir)** : lire d'abord le fichier privé **`C:\Users\USER\nebula-apercus\REPRENDRE-ICI.md`**
> (hors dépôt) : les prospects chauds, la prochaine action de chacun avec son message déjà rédigé, la liste du 20/11 et
> l'avatar. ⛔ **Depuis le 19/11 à 10 h 25, WhatsApp a détecté l'automatisation** : WhatsApp Web est bloqué sur le PC
> (temporairement) et on ne le pilote plus sans un nouveau feu vert de Mongazi. Il m'envoie les captures ou les vocaux,
> je rédige, il envoie de son téléphone. Aucun nouveau numéro pendant le blocage, puis peu par jour et à la main.

---

## 1. Le but

- **Le 18/11 au matin** : 100 000 F CFA avant le dimanche 22 novembre, avec de **nouveaux** clients (Mongazi n'avait
  « rien sur lui »). Il l'avait d'abord posé en dollars : 100 000 $ n'était pas atteignable honnêtement, il l'a su.
- **Le 18/11 vers 17 h 30** (posé en `/goal`) : **1 000 000 F CFA « avant vendredi ou la fin de la semaine »**, soit
  l'équivalent de 20 catalogues. D'où : volume (40 par jour) **et** tickets plus gros (Vitrine 150 000 F pour les
  commerces qui ont besoin de crédibilité : hôtels, salles de fêtes, agences, grandes boutiques).
- Le produit vendu : le **Catalogue Digital à 50 000 F** (payé en entier, abonnement 20 000 F tous les six mois,
  modifications comprises), prix du socle `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md`.

## 2. La chaîne complète

```
Liste locale Google (le numéro est sur la carte)
  google.com/search?q=<métier>+Cotonou&udm=local&hl=fr
        │  lecture JS des cartes div.VkpGBb : nom, note, avis, numéro, bouton « Site Web »
        ▼
python scripts/prospection.py importer <lot.json>     → note de besoin sur 10, doublons écartés par le NUMÉRO
        ▼
python scripts/prospection.py envois 20               → liens web.whatsapp.com/send?phone=…&text=… (accroche v2)
        ▼
WhatsApp Web (Chrome piloté) : un prospect à la fois, ~50 s chacun, clic Envoyer seulement si le texte est là
        ▼
python scripts/prospection.py statut <id> <statut> [note]   ·   relance <id> AAAA-MM-JJ [note]
        ▼
python scripts/prospection.py suivi <fichier.md>      → tableau privé, par statut, avec relances dues
python scripts/prospection.py vcf <fichier.vcf>       → tous les contactés, à importer sur son téléphone
        ▼
Le soir : suivi + vcf envoyés sur SA PROPRE conversation WhatsApp (il voit tout sans moi)
```

Un vocal reçu : menu du message → Télécharger → `python scripts/transcrire.py <fichier.ogg>` (Deepgram, français).

## 3. Les commandes exactes

| Quoi | Commande |
|---|---|
| Ranger un lot de fiches | `python scripts/prospection.py importer <lot.json>` |
| Les meilleurs à contacter | `python scripts/prospection.py liste 25` |
| Les liens des prochains messages | `python scripts/prospection.py envois 20` |
| Changer un statut | `python scripts/prospection.py statut <id> contacte "<note>"` |
| Poser une relance | `python scripts/prospection.py relance <id> 2026-11-20 "<note>"` |
| Combien à chaque étape | `python scripts/prospection.py bilan` |
| Le tableau de suivi (privé) | `python scripts/prospection.py suivi C:/Users/USER/nebula-apercus/SUIVI-PROSPECTS.md` |
| La fiche contact de tous | `python scripts/prospection.py vcf C:/Users/USER/nebula-apercus/Prospects-NEBULA.vcf` |
| Transcrire un vocal | `python scripts/transcrire.py <fichier audio>` |

Statuts : `a_contacter` → `contacte` → `repondu` → `interesse` → `paye`, ou `refus` (pas maintenant, avec date) /
`ne_plus_contacter` / `injoignable` / `ecarte` (a déjà un vrai site).

## 4. Les fichiers

| Fichier | Où | Ce qu'il porte |
|---|---|---|
| La méthode et les réponses types | `_documents/nebula-agency/vente/PROSPECTION-GOOGLE-MAPS.md` (public) | où chercher, note de besoin, accroche, exemples par métier, situations |
| La base | Supabase, `piste.prospection` (RLS, aucun accès public) | chaque fiche, son statut, ses notes, sa relance |
| Le suivi lisible | `C:\Users\USER\nebula-apercus\SUIVI-PROSPECTS.md` (**hors dépôt**) | le tableau du jour, avec numéros |
| Les aperçus, PDF et vocaux | `C:\Users\USER\nebula-apercus\` (**hors dépôt**) | le PDF d'un prospect, les pages extraites, les vocaux (à supprimer après transcription) |
| La routine | `_memoire/prospection/ROUTINE.md` | la journée type en cases à cocher |
| Les leçons | `_memoire/prospection/LECONS.md` | tout ce qui a mordu le 18/11 |
| La mémoire automatique | `feedback_prospection-whatsapp`, `project_sprint-fetes-2026`, `project_statuts-quotidiens` | ses consignes, l'état privé, les statuts quotidiens |

## 5. Les consignes de Mongazi (ses mots)

- **Feu vert général** : « tu as feu vert pour envoyer les messages, je les valide déjà, et feu vert pour leur
  répondre aussi, fais-moi juste toujours le point ». « Je valide toutes tes actions et messages futurs. »
- **L'accroche** : « mets-toi dans la peau d'un expert vendeur, accrocheur, avec plus de 60 années d'expérience, tu
  dois les choquer et les intriguer… élever le niveau tout en parlant moins et de la manière la plus humaine
  possible ». Donc 3 lignes, un compliment précis et vrai, un fait vrai qui dérange, une question. Jamais de mensonge.
- **Avec ceux qui répondent** : « toujours chaleureux, professionnel et ultra humain ».
- **Creuser** : « chercher à savoir comment il veut le travail, creuser sur le client ».
- **Un intéressé** remplit la fiche **https://www.nebula-agency.online/#order** : elle arrive sur son WhatsApp sous
  la forme « NOUVELLE COMMANDE … NEBULA AGENCY » (cherche « NOUVELLE COMMANDE »). Ensuite : « encore poser quelques questions et essayer de savoir
  s'il veut des choses en plus, agis comme un super vendeur avec plus de 40 ans d'expérience ».
- **Les vocaux et les blocages** : « fais toujours savoir quand il y a des notes vocales ou des hics où je dois
  intervenir, ne te limite jamais à cause de ça ». On écrit **« BESOIN DE TOI »**, et on continue le reste.
- **Le rythme** : 40 premiers messages par jour (« on doit atteindre l'objectif »), risque de blocage connu de lui.
- **Aucun groupe** : « ne mets plus dans les groupes ». Les partenaires : « ils foutent rien, je ne compte plus sur
  eux, je n'ai que toi ».
- **Le paiement** : Mobile Money, au numéro de Mongazi (dans sa mémoire locale, jamais sur GitHub : ce dépôt est public), « mais il faut déjà bien lui expliquer, qu'il comprenne et
  tout ». On explique d'abord (ce qu'il reçoit, prix, abonnement, délai), le numéro vient après.
- **Ranger** : chaque prospect enregistré en contact « Prospect <nom> » (synchronisé sur son téléphone) et dans la
  liste WhatsApp **« Prospects fêtes 2026 »**. « Enregistre tout ce à qui tu as écrit avec leurs noms, état… je
  pourrai tout savoir même si je ne suis pas là. »
- **Les méfiants** (déjà arnaqués) : aperçu d'abord avec leurs vrais produits, paiement seulement si ça leur plaît.
- **Les statuts du jour** : des posts chaque jour pour le statut WhatsApp et TikTok, faits dans **Google Flow** (il y
  est déjà connecté). **Pinterest = inspiration seulement** : on ne reprend jamais l'image d'un autre.

## 6. Où on en est (agrégé, le 18/11 vers 17 h 45)

| | |
|---|---|
| Fiches en base | 54, dans 9 métiers (pâtisserie, parfumerie, traiteur, déco événementielle, mode, cosmétiques, bijouterie, chaussures) |
| Premiers contacts | 31 (28 notés en base à cette heure) |
| Vraies réponses humaines | 8 (les réponses automatiques ne comptent pas) |
| Intéressés | 4 : une bijouterie très notée (dit « ok », explication et paiement envoyés), une pâtisserie de 30 ans (aperçu promis), un grill de 68 avis (a tenté un appel vidéo), une restauratrice méfiante (aperçu d'abord) |
| Encaissé | **0 F** |

Le détail nominatif, avec numéros et relances : `C:\Users\USER\nebula-apercus\SUIVI-PROSPECTS.md`, refait par
`python scripts/prospection.py suivi …`, et envoyé chaque soir sur sa propre conversation WhatsApp.

## 7. Ce qui attend (dans cet ordre)

1. ⏰ **L'aperçu promis à une pâtisserie de 30 ans, jeudi 19 au matin** (son PDF de 23 pages est hors dépôt,
   PyMuPDF installé le 18/11 pour en tirer pages et textes).
2. Les relances dues le 19/11 (les 4 intéressés), puis le 20/11 (tous les contactés sans vraie réponse).
3. 40 premiers contacts par jour, en ajoutant des commerces à plus gros ticket (Vitrine 150 000 F).
4. Les statuts WhatsApp et TikTok du jour (Google Flow).
5. L'objectif : 1 000 000 F CFA avant la fin de la semaine. Rien n'est encaissé tant qu'un paiement n'est pas reçu.
