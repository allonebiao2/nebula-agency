# MINUIT · la lettre digitale

> Une lettre digitale, c'est **une enveloppe cachetée qu'on ouvre à l'heure dite.**
> Le sceau, le pli, l'encre qui sèche. Toutes les animations de ce produit sortent
> de cet objet, et d'aucun autre.

Dossier de décision : `_plans/2026-08-27-minuit-dossier.html`
Manuel d'exploitation : `_plans/2026-08-28-minuit-manuel.html`

---

## Ce qui existe, au 2026-09-03

| Brique | État |
|---|---|
| **Le gabarit de la lettre** (`lettre.html`) | ✅ construit, **78 contrôles verts** |
| **Le constructeur** (`creer.html`) | ✅ construit, les 6 écrans du manuel |
| **La sauvegarde du formulaire** | ✅ à chaque frappe, restaurée au retour |
| Commande, paiement déclaré, validation | ✅ déjà dans `vitrina/`, 28 contrôles verts |
| Alertes WhatsApp et Telegram | ✅ dans `vitrina/`, variables à poser |
| **Livraison à l'heure choisie** | ⏳ **reste à faire**, avec n8n |
| **Serveur en ligne** | ⏳ **reste à faire**, un service Render |
| **La vidéo de démonstration** | ✅ construite le 2026-09-03, ⛔ **à ne pas publier encore** |

Le manuel disait : *« un gabarit irréprochable, la sauvegarde du formulaire, la
livraison à l'heure choisie, dans cet ordre »*. Les deux premiers sont faits.

### La vidéo de démonstration

`_studio-video/`, composition **`minuit-demo`** : 1080x1920, 30 s.
`cd _studio-video && npm run rendu:minuit`.

Les **six signatures ci-dessous sont rejouées en React**, pas photographiées :
une capture ne montre pas un cachet qui se brise. Les couleurs, le texte de la
lettre et le prix y sont lus depuis **ce dossier**, recopiés une seule fois
dans `_studio-video/src/minuit/donnees.ts`.

⛔ **Elle n'est pas publiable en l'état.** Elle promet « Elle l'ouvre à minuit
pile. Pas avant. » et affiche `nebula-agency.online/minuit` : les deux lignes
⏳ du tableau ci-dessus. La vidéo est prête, la promesse ne l'est pas.

---

## Les fichiers

| Fichier | Ce que c'est |
|---|---|
| `lettre.html` | **Le produit.** Une lettre, autonome, sans aucun appel réseau |
| `creer.html` | Le constructeur : occasion, écriture, aperçu vivant, paiement |
| `_injecter.py` | **Le seul endroit** où l'on écrit des données dans le gabarit |
| `_qc.py` | 78 contrôles. Vert obligatoire avant toute mise en ligne |
| `_voir.py` | Fabrique les captures à REGARDER (390 et 1440) |

```bash
python minuit/_qc.py       # les 78 contrôles
python minuit/_voir.py     # les captures
cd minuit && python -m http.server   # pour ouvrir creer.html
```

---

## Les six animations, une par section

Toutes tirées de l'objet « enveloppe cachetée », aucune n'est décorative.

| Section | Signature |
|---|---|
| 1 · Le seuil | **Le cachet respire, puis se brise** en trois éclats de cire |
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
- **Chercher un mot au lieu du marqueur.** « MINUIT_DONNEES » figure aussi dans
  le commentaire d'en-tête du gabarit, qui doit rester. Le bon test porte sur
  `/*MINUIT_DONNEES*/`.
- **Une attente fixe est un pari.** La chaîne de l'aperçu fait 260 ms
  d'anti-rebond, plus le chargement de l'iframe, plus 620 ms d'ouverture :
  800 ms donnait **1 passage vert sur 3**. `attendre()` attend l'ÉTAT.
- **Un serveur de test mono-tâche** se bloque dès la seconde requête et fait
  échouer sur un « Timeout » sans rapport. `ThreadingHTTPServer`, toujours.

---

## ⏳ Ce qui reste

1. **La livraison à l'heure choisie** (n8n). C'est la fonction qui donne son nom
   au produit, et **aucun concurrent observé ne la propose**.
2. **Le serveur en ligne** : un service Render, un sous-domaine.
3. **Le risque de détournement**, à traiter **avant la première vente** : adresse
   non devinable, expiration, retrait sous 24 h, conditions d'utilisation.
   Aucune des cinq références du dossier ne le traite.
4. ⛔ **Ne jamais héberger un MP3** : c'est de la contrefaçon. Lien externe, ou rien.
5. Les autres occasions du catalogue (faire-part, naissance, deuil). ⚠️ **Le deuil
   ne se décore pas** : sobriété totale, aucun emoji, et une relecture par
   quelqu'un qui vient d'enterrer un proche avant de le vendre.
