# 2026-09-03 · PISTE encaisse et livre tout seul

*Suite de `2026-09-03-saspay-api-trouvee.md`. Partie de « vérifie, j'ai mis la
clé dans le dossier secret » et finie avec un site qui encaisse la nuit.*

## Ce qui est en ligne

| Morceau | État |
|---|---|
| `paiement.sql` | installé (2 tables + RLS, 4 fonctions) |
| Secrets Supabase | `SASPAY_CLE_SECRETE`, `SASPAY_SECRET_WEBHOOK`, `SASPAY_DEVISE`, `PISTE_JETON_INTERNE` |
| `piste-paiement` · `piste-paiement-recu` · `piste-livrer` | déployées |
| Webhook SasPay | LIVE, actif, 12 abonnements dont `transaction.success` |
| Site | `SASPAY_PRET = true`, déployé, **134 contrôles verts** |

**La chaîne éprouvée contre la fonction réellement déployée** : sans en-tête
`401 horodatage` · horodatage vieux de 2 h `401` · signature fausse `401` ·
signature valable `200` avec écriture au journal.

## Le carnet part tout seul

*« Même si je dors, et qu'il y a des clients, que ça s'encaisse tout seul. »*

`piste-paiement-recu` appelle `piste-livrer` dès qu'un paiement est confirmé.
⚠️ **Il l'appelle, il ne le recopie pas** : choix des fiches, pose du carnet et
courriels restent écrits à un seul endroit.

**La porte interne** (`PISTE_JETON_INTERNE`) ne desserre que deux choses : le
mot de passe du cockpit (un serveur n'en a pas) et le verrou anti-force-brute
(sinon un inconnu tapant des mots de passe au hasard empêcherait un client qui
a **payé** de recevoir sa marchandise). ⛔ Tout le reste est identique. **Une
porte interne n'est pas une porte dérobée.**

⛔ **Un échec de livraison ne fait jamais échouer l'encaissement** : l'argent
est arrivé, la commande reste payée, on répond 200 à SasPay (sinon il rejoue),
et le journal porte la raison. ⚠️ Rejouer est sans danger : `piste_poser_carnet`
refuse une deuxième pose et l'index unique du journal un deuxième événement.

## Ce que le paiement a révélé du reste du produit

⛔ **Un moyen de paiement n'est pas un bouton, c'est une hypothèse dans tout
l'entonnoir.** Trois choses de la dernière étape n'existaient que pour le
rapprochement manuel, dont le **numéro Mobile Money obligatoire** : un client
prêt à payer par carte en dix secondes devait d'abord déclarer un numéro dont
personne ne se servirait.

⛔ **La route `#/merci` n'existait pas.** C'est pourtant l'adresse où SasPay
ramène le client après un paiement réussi : le routeur retombait sur la
vitrine. On payait 4 320 F et on atterrissait sur la page d'accueil, sans un
mot. ⚠️ Le défaut ne venait pas du paiement, il venait de ce que **personne
n'avait suivi le client APRÈS le bouton**.

⛔ **Les quatre étapes de l'écran de paiement disaient encore « faites le
transfert, envoyez une capture » au-dessus d'un bouton Payer.** Trouvé **sur la
capture**, pas par un contrôle : rien n'était cassé, tout était faux.

⛔ **Le brouillon du générateur ne partait jamais.** `ecrire(CLES.brouillon)` et
`lire(CLES.brouillon)` passent la VALEUR là où la fonction attend le nom court
(`CLES[cle]`) : les deux étaient faux **de la même façon**, donc invisibles, et
le brouillon vivait sous la clé littérale `"undefined"`. Mais la ligne qui
l'efface visait la vraie clé, jamais écrite. Un client qui revenait était
renvoyé à la dernière étape avec une configuration périmée.
⚠️ **Deux erreurs symétriques s'annulent et se cachent ; c'est la troisième
ligne, correcte, qui trahit les deux premières.**

⛔ **Trois fonctions n'avaient aucune source dans le dépôt** (`piste-livrer`,
`piste-commande`, `piste-signalement`) : elles n'existaient que déployées, ce
que `PAIEMENT.md` annonçait comme un risque depuis le premier jour.
Rapatriées par `supabase functions download`.

## Le contrôle qui ne voyait qu'une moitié

⚠️ **La passe du QC bascule sur le dépôt à la main pour garder ses anciennes
assertions : elle ne voyait donc JAMAIS l'écran que verra la plupart des
clients.** Même angle mort que `#/merci`. Une **deuxième passe** va désormais
jusqu'à l'écran de paiement par le chemin par défaut, en atterrissant
directement à la dernière étape via le brouillon du générateur.

Trois pannes d'instrument, aucune du site : `Execution context was destroyed`
(navigation pendant l'évaluation), `the page has been closed` (la page du
parcours précédent est fermée à ce stade), et une regex qui ne trouvait rien
parce que **`innerText` rend le texte TEL QU'IL S'AFFICHE** — le titre porte
`text-transform: uppercase`, donc il revient en majuscules.

⚠️ Un contrôle accroché à un **titre** devient rouge dès que le titre change
selon le contexte : viser un repère stable.

## Les pièges d'outillage de la journée

⛔ **Un fichier `.env` réécrit par PowerShell passe en CRLF**, le lecteur JS
coupait sur `'
'`, le `'
'` restait collé, et comme `.` ne traverse pas un
retour chariot le `$` n'accrochait plus rien : **aucune ligne lue**,
`Bearer undefined` envoyé, et SasPay répondant « Clé API invalide » sur six
routes. ⚠️ Le message accusait la clé, le coupable était un octet invisible.
**La même clé envoyée par `curl` répondait 200 : quand un outil échoue et qu'un
autre réussit sur la même donnée, le défaut est dans l'outil.**

⚠️ **Cloudflare refuse la signature par défaut de Python** sur
`api.supabase.com` : `403 error code 1010`. Un `User-Agent` ordinaire suffit.

⚠️ **Les listes de l'API SasPay sont paginées et le `limit` est ignoré** : 61
réseaux annoncés, 20 rendus. J'ai failli affirmer que le Togo n'était pas
couvert. **Vérifier `count` et `next` avant de conclure sur une liste.**

## Ce que couvre vraiment SasPay (vérifié sur les 61 réseaux)

| Pays | Réseaux actifs, en XOF |
|---|---|
| Bénin | MTN, Moov, Celtiis |
| Togo | Mixx (Yas), Moov, Togocel |
| Côte d'Ivoire | MTN, Moov, Orange, Wave, Djamo |

Les trois pays du vivier sont couverts. ⚠️ **Le Togo n'a pas MTN** (l'opérateur
n'y est pas présent) : Moov, Mixx et Togocel.

⚠️ **Montant minimum : 200 XOF**, mesuré (100 F refusé). Sans conséquence, PISTE
vend au minimum 1 000 F.

⚠️ **Lien de paiement ≠ session de checkout.** Le lien est **réutilisable** à
montant fixe, la session est **à usage unique** au montant de la commande.
Seule la seconde relie un paiement à une commande, et c'est elle que le site
crée, une par commande. La page « Liens de paiement » du tableau de bord reste
donc vide, et c'est normal.

## ⏳ Ce qui reste

⛔ **Le premier paiement réel n'a pas eu lieu.** C'est le seul essai qu'aucune
simulation ne remplace : il prouvera le dernier maillon, celui qui relie une
notification à une commande (`referenceParTransaction`, non vérifié car il
demande un vrai encaissement).

⏳ **Mongazi demande de supprimer totalement l'ancien chemin** (dépôt Mobile
Money à la main + passage par WhatsApp). ⚠️ **Recommandation posée : faire le
test à 200 F d'abord.** Retirer le chemin qui marche avant que le nouveau ait
encaissé une fois, c'est se retrouver sans aucun moyen de vendre si un maillon
casse — et un client qui paie sans rien recevoir, sans que personne soit
prévenu.

⚠️ **Tant que le premier paiement n'a pas été vu bout en bout**, surveiller :

```sql
select recu_le, reference, montant, etat_lu, agi
  from piste.paiement_evenement order by id desc limit 10;
```

## ⛔ Fin de journée : l'ancien chemin est supprimé

« Il n'y a qu'une seule possibilité, l'ancien on la supprime. » Retiré : le
numéro Mobile Money, l'opérateur, la consigne sur le nom du compte, le numéro
NEBULA à créditer, la capture d'écran — **et la redirection WhatsApp**.

⛔ **Elle faisait sortir le client du tunnel juste avant qu'il paie.** Elle
n'avait de sens que pour le dépôt à la main, où c'est là qu'il recevait le
numéro à créditer. WhatsApp reste comme recours, plus comme étape.

⚠️ **Les mots héritent de l'ancien monde** : « montant exact **à envoyer** » et
« **sous 24 heures** » venaient du virement manuel. Rien ne les vérifiait —
les données se régénèrent, les phrases non.

⚠️ **Les contrôles qui exigeaient l'ancien chemin ont été RETOURNÉS, pas
supprimés** : ils vérifient maintenant son absence. Un contrôle qu'on efface
parce qu'il est rouge ne protège plus rien.

**QC 128 verts, 0 rouge.** Déployé et vérifié : le bundle servi est celui
construit ici, « Continuer vers le paiement » présent, « Envoyer ma commande
sur WhatsApp » et « créditer » absents.

⚠️ **Le domaine a répondu `000` pendant 45 s au moment de vérifier**, alors que
l'origine `piste-uex.pages.dev` répondait 200 : réseau local, pas déploiement.
Vérifier par l'origine avant de conclure qu'un site est cassé.

⏳ **Le premier paiement réel n'a toujours pas eu lieu**, et le filet n'est plus
le client qui envoie sa capture : c'est Mongazi qui regarde le journal.

