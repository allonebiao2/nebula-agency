# LE PLI · la lettre digitale

> Une lettre digitale, c'est **une enveloppe cachetée qu'on ouvre à l'heure dite.**
> Le sceau, le pli, l'encre qui sèche. Toutes les animations de ce produit sortent
> de cet objet, et d'aucun autre.

Dossier de décision : `_plans/2026-08-27-lepli-dossier.html`
Manuel d'exploitation : `_plans/2026-08-28-lepli-manuel.html`
**L'arrêté (les 12 décisions) : `_plans/2026-09-06-lepli-arrete.html`**
Conditions et retrait : `lepli/CONDITIONS.md`

---

## Ce qui existe, au 2026-09-06

| Brique | État |
|---|---|
| **Le gabarit de la lettre** (`lettre.html`) | ✅ construit, **115 contrôles verts** |
| **Le constructeur** (`creer.html`) | ✅ construit |
| **La sauvegarde du formulaire** | ✅ à chaque frappe, restaurée au retour |
| **L'heure d'ouverture** | ✅ **dans la lettre**, depuis le 2026-09-06 |
| **Les conditions et le retrait** | ✅ écrits, `CONDITIONS.md` |
| **L'encaissement** | ✅ **écrit et contrôlé** (SasPay), ⏳ pas encore branché |
| **L'adresse en ligne** | ✅ **écrite et contrôlée**, ⏳ pas encore déployée |
| **La vidéo de démonstration** | ✅ construite le 2026-09-03, publiable dès que l'adresse existe |

Le manuel disait : *« un gabarit irréprochable, la sauvegarde du formulaire, la
livraison à l'heure choisie, dans cet ordre »*. **Les trois sont faits.**

### La vidéo de démonstration

`_studio-video/`, composition **`lepli-demo`** : 1080x1920, 30 s.
`cd _studio-video && npm run rendu:lepli`.

Les **six signatures ci-dessous sont rejouées en React**, pas photographiées :
une capture ne montre pas un cachet qui se brise. Les couleurs, le texte de la
lettre et le prix y sont lus depuis **ce dossier**, recopiés une seule fois
dans `_studio-video/src/lepli/donnees.ts`.

⚠️ Elle promet « Elle l'ouvre à minuit pile. Pas avant. » **Cette phrase est
vraie depuis le 2026-09-06** : la lettre tient l'heure. Il ne reste que
l'adresse qu'elle affiche (`lepli.nebula-agency.online`), qui doit exister
avant publication.

---

## Les fichiers

| Fichier | Ce que c'est |
|---|---|
| `lettre.html` | **Le produit.** Une lettre, autonome, sans aucun appel réseau |
| `creer.html` | Le constructeur : occasion, écriture, aperçu vivant, commande |
| `paiement.html` | **La page de paiement** : la somme, et **le lien** (bouton + en clair) |
| `merci.html` | **La page de retour**, celle que SasPay rappelle. ⛔ Elle ne prouve rien |
| `_injecter.py` | **Le seul endroit** où l'on écrit des données dans le gabarit |
| `_qc.py` | **145 contrôles**. Vert obligatoire avant toute mise en ligne |
| `_qc_caisse.mjs` | **118 contrôles** sur la caisse, sans clé ni réseau |
| `supabase/` | La base et les trois fonctions de bord. Voir `PAIEMENT.md` |
| `_gabarit_ts.py` | Recopie `lettre.html` dans un module pour les fonctions |
| `PAIEMENT.md` | Où vit chaque morceau, et comment brancher le jour venu |
| `CONDITIONS.md` | Ce qu'on promet, et le retrait sous 24 h. À lire avant de vendre |
| `_voir.py` | Fabrique les captures à REGARDER (390 et 1440) |

```bash
python lepli/_qc.py                                   # les 145 contrôles
node --experimental-strip-types lepli/_qc_caisse.mjs  # les 118 de la caisse
python lepli/_gabarit_ts.py                           # après toute retouche de lettre.html
python lepli/_voir.py                                 # les captures
cd lepli && python -m http.server                     # pour ouvrir creer.html
```

---

## Les six animations, une par section

Toutes tirées de l'objet « enveloppe cachetée », aucune n'est décorative.

| Section | Signature |
|---|---|
| 1 · Le seuil | **Le cachet dort, s'allume à l'heure dite, puis se brise** en trois éclats de cire |
| 2 · Le pli | **Le dépliage** : la feuille s'ouvre, ses deux plis s'effacent |
| 3 · La lettre | **L'encre qui sèche** : flou vers net, ligne après ligne |
| 4 · Les photos | **Le polaroïd qui se développe**, du blanc vers l'image |
| 5 · Le compte | **Les chiffres qui roulent**, avec une sortie qui ralentit |
| 6 · La signature | **Le trait qui s'écrit** (`stroke-dashoffset`) |

---

## Les décisions, et pourquoi

**Le seuil EST le produit.** Les cinq références du dossier ont toutes une
barrière. Elle crée l'attente, rend la page privée, et surtout **rend filmable**
en créant un avant/après. Une lettre livrée garde donc toujours son cachet : un
contrôle vérifie que le drapeau d'aperçu ne part jamais dans la commande.

**Aucune police téléchargée.** La pile est système, choisie : Iowan Old Style
(Apple) et Palatino (Windows) sont de vraies faces de correspondance, plus
chaudes que Georgia, et déjà sur la machine. Une lettre doit s'ouvrir dans un
taxi ; on ne fait pas attendre un cadeau derrière un fichier de police.
⛔ Ne pas rajouter Google Fonts.

**Les photos sont des données, jamais des liens.** Une photo distante ferait
dépendre la lettre d'un serveur, et **fuiterait l'heure d'ouverture** vers un
tiers. Le gabarit refuse toute source qui ne commence pas par `data:`.

**`noindex`.** Une lettre est privée. Elle n'a rien à faire dans un moteur.

**Le pied viral n'existe qu'au palier gratuit.** C'est la boucle de croissance :
chaque destinataire est un acheteur possible. Un palier payé le retire.

---

## 🏦 La caisse, en une phrase

Le constructeur envoie **les données** de la lettre à `lepli-commande`, qui en
fixe le prix (⛔ jamais le navigateur), la dépose, et ouvre un paiement SasPay.
La notification signée rend la lettre joignable, seule, à n'importe quelle
heure. `lepli-lettre` la sert à une adresse de **110 bits tirés au sort**, et
la retire à la demande. Tout est dans **`PAIEMENT.md`**.

⛔ **On ne stocke jamais le HTML du navigateur** : une porte publique qui
accepte du HTML et le sert sur notre domaine est un hébergeur de pages
arbitraires, gratuit et anonyme. La lettre est **rebâtie** à partir du gabarit.

---

## 🕛 Le verrou d'heure, et pourquoi il vit DANS la lettre

C'est la fonction qui donne son nom au produit, et **aucun concurrent observé ne
la propose**. Le dossier et le manuel la confiaient tous les deux à n8n. Or n8n
était auto-hébergé sur le VPS Hostinger `72.61.103.56`, et **cette machine
n'appartient plus à Mongazi**. La fonction reposait sur un serveur perdu.

Elle vit donc **dans la lettre**, et c'est mieux :

- elle **ne dépend de rien** : ni serveur, ni réseau, ni compte tiers ;
- elle tient **même si l'acheteur envoie son lien trois jours trop tôt**, ce
  qu'aucune machine à envoyer n'aurait rattrapé ;
- elle retire d'un coup **trois dépendances** : le modèle WhatsApp à faire
  approuver par Meta pour sortir de la fenêtre de 24 h, le coût d'un envoi, et
  le risque le plus grave du produit, celui d'écrire à quelqu'un qui n'a jamais
  donné son numéro.

**Ce qu'on promet, et rien de plus :** le cachet ne se brise pas avant l'heure.
⛔ **On ne promet JAMAIS le secret** : le texte est dans la page, qui sait lire
un code source peut le lire avant l'heure. Une lettre est un cadeau emballé, pas
un coffre-fort. Voir `CONDITIONS.md` §1.

**L'heure est une heure de CALENDRIER, sans fuseau** (`2027-02-14T00:00`) :
minuit, c'est minuit sur le téléphone de celle qui lit. Un instant absolu ferait
s'ouvrir à 22 h à Paris une lettre programmée à minuit depuis Cotonou.

⚠️ **Le garde-fou est dans `ouvrir()`, pas sur le bouton** : le code secret
appelle `ouvrir()` directement, et tout chemin futur y passera aussi.

⚠️ **L'aperçu du constructeur ignore le verrou** : l'acheteur doit voir SES mots
pendant qu'il les tape, c'est là que la vente se fait. Le drapeau d'aperçu ne
part jamais dans la commande, et un contrôle le vérifie.

⚠️ **Chaque verrou a son TÉMOIN dans le QC** (une heure passée, un palier payé) :
sans lui, un verrou resté fermé pour toujours passerait tous les contrôles avec
les honneurs.

---

## ⛔ Les trois pièges, tous rencontrés le jour de l'écriture

### 1 · « </script> » dans le mot d'un acheteur tue la page

Les données atterrissent **dans un bloc `<script>`**. Un acheteur qui écrit la
balise fermante ferme le bloc, et la page entière meurt : plus de titre, plus de
lettre, plus de seuil.

⚠️ **`json.dumps` ne protège pas de ça** : c'est une chaîne JSON parfaitement
valide, et le navigateur cherche la balise fermante **avant** de lire le JSON.

D'où `_injecter.py`, **seul endroit** où l'on sérialise. Il neutralise `</`,
`<!--` et les séparateurs de ligne U+2028 / U+2029.

### 2 · Le commentaire qui explique le piège contenait le piège

Le commentaire de `creer.html` qui documentait ce danger était écrit **avec la
balise littérale**. Il fermait donc lui-même le bloc, et tout le script du
constructeur était mort. Le QC l'a vu ; l'œil, non.

### 3 · Le garde-fou contenait le défaut qu'il devait empêcher

La fonction qui neutralise U+2028 / U+2029 les portait **en clair** dans ses
expressions régulières. Or ce sont des fins de ligne pour JavaScript : elles
cassaient la syntaxe du fichier.

> **La règle qui en sort :** `node --check` sur le script en ligne avant d'écrire.
> Un fichier qui contient sa propre documentation d'un piège doit être vérifié
> **comme s'il contenait le piège**, parce que c'est souvent le cas.

---

## ⚠️ Les contrôles qui ont menti avant de dire vrai

Quatre sondes ont accusé un produit sain. À relire avant d'ajouter un contrôle.

- **`inner_text` renvoie le texte RENDU.** `.pour` et le libellé du compte sont
  en `text-transform: uppercase` : la sonde lisait « ZARA » et « JOURS ENSEMBLE »
  et concluait à une erreur. On lit `text_content` quand c'est le contenu qui
  compte.
- **Chercher un mot au lieu du marqueur.** « LEPLI_DONNEES » figure aussi dans
  le commentaire d'en-tête du gabarit, qui doit rester. Le bon test porte sur
  `/*LEPLI_DONNEES*/`.
- **Une attente fixe est un pari.** La chaîne de l'aperçu fait 260 ms
  d'anti-rebond, plus le chargement de l'iframe, plus 620 ms d'ouverture :
  800 ms donnait **1 passage vert sur 3**. `attendre()` attend l'ÉTAT.
- **Un serveur de test mono-tâche** se bloque dès la seconde requête et fait
  échouer sur un « Timeout » sans rapport. `ThreadingHTTPServer`, toujours.
- **Deux instantanés ne mesurent pas un compte à rebours.** Il change une fois
  par seconde : deux lectures peuvent tomber dans la même. On échantillonne.

---

## ⛔ Les trois défauts trouvés le 2026-09-06, tous invisibles au QC vert

1. **L'heure n'existait nulle part.** Elle était demandée à l'acheteur, promise
   sur l'écran final (« elle la recevra le 14 février à 00:00 ») et n'entrait
   dans aucune lettre. ⚠️ **Aucun contrôle ne pouvait le voir** : on ne mesure
   pas l'absence d'une chose dont personne n'a écrit qu'elle devait exister.
2. **Deux échelles de prix.** Les occasions portaient un « dès 10 000 F »
   appliqué nulle part : on prenait « Demande en mariage · dès 10 000 F » au
   palier gratuit, et on partait à 0 F. **L'occasion décide du ton, le palier
   décide du prix.**
3. **Le palier gratuit passait par la caisse.** `aller(p.prix === 0 ?
   "e-paiement" : "e-paiement")` : deux branches identiques, donc l'intention
   avait été écrite puis perdue. Une lettre offerte affichait « Envoie
   exactement cette somme, au franc près » au-dessus d'un numéro Mobile Money.

Et un quatrième, de contraste : **le seuil n'était mesuré par rien**, alors
qu'une lettre programmée ne montre que lui, parfois pendant des heures. Le même
gris tient 4,8:1 sur le papier et tombe à **3,09:1** sur la nuit du seuil,
mesuré. → `--gris-nuit`, et quatre contrôles qui le mesurent.

---

## ⏳ Ce qui reste

Les douze décisions sont prises : `_plans/2026-09-06-lepli-arrete.html`.

1. **Brancher la caisse.** Elle est écrite, contrôlée, et pas déployée : la
   marche à suivre tient en cinq commandes dans **`PAIEMENT.md`**. ⛔ Pas de
   Render avec le SQLite de `vitrina/` : son disque s'efface à chaque
   déploiement, c'est ce qui avait fait disparaître les deux PDF des
   partenaires. Un déploiement, et les lettres payées n'existent plus.
2. **Le ménage des lettres expirées** : `lepli_menage()` existe, rien ne
   l'appelle encore. Une tâche quotidienne suffit.
3. **Le lien « retirer cette lettre »** dans le pied de la lettre : la porte
   existe, le bouton non. Le retrait passe par WhatsApp en attendant.
4. **Le faire-part avec confirmation**, pour **novembre** (saison des mariages
   et retour de la diaspora), pas pour février.
5. ⛔ **Ne jamais héberger un MP3** : c'est de la contrefaçon. Lien externe, ou rien.
6. Le deuil, **après** relecture par quelqu'un qui vient d'enterrer un proche.

### Les six réponses qui n'appartiennent qu'à Mongazi

Le compte qui encaisse · le sous-domaine · un n8n ailleurs, oui ou non · la
commission SasPay · qui relit le deuil · le premier franc encaissé pour de vrai.
