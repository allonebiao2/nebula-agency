# CLIENT 10 — HILLARY M. STYL

> **Maison de couture · prêt-à-porter & sur-mesure**
> Vitrine avec catalogue commandable et prise de mesures en ligne.
> Créé le 2026-07-31 · **refonte du moteur de mesures le 2026-07-31 (v2)**.

---

## 1. Identité

| | |
|---|---|
| **Marque** | HILLARY M. STYL (monogramme **H.M.S**) |
| **Métier** | Couture : prêt-à-porter (par tailles) et sur-mesure (aux mesures du client) |
| **Cible** | Femmes et hommes, cérémonies et quotidien |
| **Logo** | Buste de mannequin ceint d'un ruban magenta + monogramme H.M.S |
| **Palette** | Magenta `#E6007E` · noir `#0A0A0A` · crème `#FBFBFC` · rose pâle `#FFE8F4` |
| **Typographie** | Archivo (titres, géométrique comme le logo) + Manrope (texte) |

---

## 2. Les fichiers, et lequel on modifie

| Fichier | Rôle |
|---|---|
| **`_vitrine_src.html`** | **La source. C'est celui-ci qu'on édite.** ≈70 Ko, lisible, avec des marqueurs `__LOGO_B64__` et `__FAVICON_B64__` à la place des images |
| `_build.py` | Injecte les images en base64 et écrit `vitrine.html` |
| `_qc.py` | La suite de contrôle qualité, **53 contrôles**, à passer avant tout déploiement |
| `vitrine.html` | **Le livrable, généré. Ne jamais l'éditer à la main** : la prochaine construction écraserait la modification |

```bash
cd clients/10-hillary-m-styl
python3 _build.py     # source -> vitrine.html (143 Ko)
python3 _qc.py        # doit afficher « TOUT EST VERT »
```

Pourquoi ce détour : le logo pèse 75 Ko une fois en base64. Éditer directement le
livrable revient à travailler dans un fichier où le code utile est noyé — et à risquer
de dupliquer le logo, ce qui avait fait grimper une première version à 681 Ko.

---

## 3. Ce qui a été livré

**Un seul fichier de 143 Ko**, aucune dépendance externe hormis les polices Google.
Logo et favicon en base64, le logo déclaré **une seule fois** en variable CSS `--logo`.

### Les sections
1. **Héros** avec accueil personnalisé (bonjour / bon après-midi / bonsoir, et le prénom
   du visiteur s'il est déjà venu) et deux portes d'entrée : prêt-à-porter ou sur-mesure
2. **La maison** — quatre piliers : mesures par vêtement, retrait ou expédition,
   normal ou express, prévenu deux fois
3. **Catalogue à deux onglets** — prêt-à-porter et sur-mesure. **Le prix ET le délai de
   confection sont affichés sur chaque carte.** Deux colonnes sur mobile
4. **Comment ça se passe** — quatre étapes, dont la **double notification** (à la
   confirmation de la commande, puis quand la tenue est prête)
5. **À propos** — le métier de la maison
6. **L'atelier** — adresse, horaires, email, WhatsApp, retrait gratuit, règlement Momo

### Le tunnel de commande (le cœur du projet)

Une fiche s'ouvre au clic sur une pièce, avec quatre étapes puis l'envoi.

| Étape | Prêt-à-porter | Sur-mesure |
|---|---|---|
| **1** | Choix de la taille (XS → XXL) | **Formulaire de mesures propre au vêtement** (voir §4) |
| **2** | Retrait atelier (gratuit) ou expédition — **les frais s'affichent par pays** | idem |
| **3** | Délai **normal** ou **express (1 à 3 jours)** → **la date précise de disponibilité s'affiche** | idem |
| **4** | Coordonnées : WhatsApp **ou** email | idem |

Un **récapitulatif chiffré** se met à jour en direct (pièce + livraison + délai = total),
puis la commande part sur WhatsApp en message structuré, avec toutes les mesures.

---

## 4. Le moteur de mesures — ce qui a changé en v2

**Les mesures dépendent du type de vêtement, pas du genre du client.**
C'était l'erreur de la v1, qui demandait 8 mesures « femme » ou « homme ».
Une robe droite en demande 15, un pantalon 6.

| Type de vêtement | Mesures | Détail |
|---|---|---|
| **Robe coupée à la taille** | **9** | Épaules · Carrure devant · Poitrine · Tour de taille · Longueur taille · Longueur robe courte · Longueur robe longue · Tour de manche · Longueur manche |
| **Robe droite** | **15** | les 9 ci-dessus **+** Tour du sous-sein · Tour de ceinture · Tour de hanche · Longueur sous-sein · Longueur ceinture · Longueur genou |
| **Robe ovale** | **11** ⚠️ | **Liste proposée, à valider par l'atelier** (voir §5, point 7) |
| **Pantalon** | **6** | Tour de taille · Tour de bassins · Tour de cuisse · Tour de genoux · Longueur genou · Longueur pantalon |
| **Chemise ou haut** | **8** | Épaules · Carrure devant · Carrure dos · Tour de poitrine · Tour de taille · Longueur habit · Tour de manche · Longueur manche |

Les champs sont **regroupés** (Le haut · Les longueurs · Les manches) pour qu'on ne se
perde pas dans quinze cases identiques.

**Le message d'aide demandé, affiché au-dessus des mesures, mot pour mot :**
> « Vous pouvez prendre les mesures vous-même ou inviter quelqu'un à le faire pour vous
> ou vous aider. »

**Une mesure laissée vide n'est pas bloquante.** Elle part en « à prendre ensemble » et
le message indique combien il en manque. Il faut la moitié des mesures pour avancer :
un client qui ne sait pas mesurer son entrejambe ne doit pas abandonner sa commande,
mais un formulaire vide n'est pas une commande.

La pièce **« Création libre »** laisse le client choisir lui-même le type de vêtement,
et bascule alors sur le bon formulaire.

---

## 5. La date de disponibilité

Dès que le client a choisi son délai, la date exacte s'affiche en vert :

> **CHEZ VOUS AU PLUS TARD LE**
> vendredi 7 août
> *Confection incluse, plus 4 jours d'acheminement vers Côte d'Ivoire.*

Le libellé change selon le mode : « Prête à retirer au plus tard le » en cas de retrait.

**Le calcul est volontairement pessimiste.** La date est annoncée sur la **borne haute**
du délai, acheminement du pays compris. Promettre le jour 8 d'un « 8 à 14 jours »
fabrique un client déçu le jour 9. On promet 14, on livre 10, la cliente est contente.

| | Confection | Acheminement | Annoncé |
|---|---|---|---|
| Normal | borne haute de la pièce | jours du pays | somme des deux |
| Express | **1 à 3 jours** → 3 | jours du pays | somme des deux |

Le délai express affiche un avertissement honnête : il est confirmé par l'atelier à la
validation, et **si la charge du moment ne le permet pas, le supplément n'est pas dû**.

---

## 6. ⚠️ À CONFIRMER AVANT MISE EN LIGNE

**Rien de tout cela n'a été inventé : les valeurs en place sont des exemples clairement
marqués dans `_vitrine_src.html`, en haut du `<script>`, dans un bloc « ZONE À COMPLÉTER ».**

| # | Information | Pourquoi c'est bloquant |
|---|---|---|
| 1 | **Numéro WhatsApp** (`WHATSAPP`) | Actuellement `22900000000`. **Aucune commande n'arrivera** tant qu'il n'est pas remplacé |
| 2 | **Email de repli** (`EMAIL`) | Le client sans WhatsApp passe par là. Adresse d'exemple pour l'instant |
| 3 | **Frais d'expédition et jours d'acheminement par pays** (`PAYS`) | Valeurs provisoires. Un tarif faux coûte de l'argent à la cliente **à chaque commande**, et un acheminement faux fausse la date annoncée |
| 4 | **Délais de confection** (`DELAIS` et `jmin`/`jmax` de chaque pièce) | Normal 7-14 jours, express 1-3 : à valider avec l'atelier |
| 5 | **Le catalogue** (`PIECES`) | 12 modèles d'exemple avec des prix d'exemple. À remplacer par les vraies pièces |
| 6 | **Adresse, horaires de l'atelier** (`ATELIER`) | Affichent « à confirmer » |
| 7 | **Les mesures de la robe ovale** (`MESURES.robe_ovale`) | **Jamais fournies.** 11 mesures proposées par déduction, signalées en jaune dans l'interface : « Liste de mesures en cours de validation par l'atelier » |
| 8 | **Prix du supplément express** | 10 000 F par défaut |

**Conseil photo à transmettre à la cliente :** dehors le matin ou en fin d'après-midi, à
l'ombre, sur un fond uni, la pièce portée ou sur mannequin. Format portrait (les cartes
sont en 3:4). C'est ce qui fera la différence entre un catalogue correct et un beau catalogue.

---

## 7. Les limites honnêtes du statique

Deux demandes ne peuvent pas être tenues par un fichier HTML seul. Elles sont
**préparées** dans la vitrine, mais elles demandent la couche automatisation :

| Demande | Où on en est |
|---|---|
| **Paiement Mobile Money** | La vitrine dit clairement « règlement par Mobile Money, le numéro vous sera communiqué à la confirmation ». Aucun paiement ne transite par le site. Un vrai encaissement en ligne passe par **FedaPay** (clé publique côté client, clé secrète côté n8n) |
| **Notification automatique du client** | Les deux messages (confirmation, puis « c'est prêt ») sont aujourd'hui envoyés à la main. L'automatisation, c'est **n8n + Twilio WhatsApp**, avec la commande enregistrée en base |

C'est exactement l'escalier NEBULA : la vitrine d'abord, l'outil ensuite.

---

## 8. Vérifications passées — `python3 _qc.py`, 53 contrôles verts

- **Aucun débordement horizontal** sur 390 px, 768 px et 1440 px, page et modale ouverte
- **Toutes les cibles tactiles ≥ 44 px** (y compris le logo de la barre et les liens du pied)
- **Aucune erreur JavaScript**, aucune ressource locale manquante
- **Aucune image externe** : logo et favicon en base64, zéro dépendance qui puisse casser
- Nombre de mesures vérifié pour les 5 types : **9 / 15 / 11 / 6 / 8**, sans identifiant en double
- Tunnel prêt-à-porter : robe 35 000 + Côte d'Ivoire 12 000 + express 10 000 = **57 000 F** ✅
  date annoncée à **J+7** (3 jours express + 4 d'acheminement) ✅
- Tunnel sur-mesure : pantalon, retrait atelier, délai normal → **30 000 F**, date à J+10,
  libellé « prête à retirer » ✅, **4 mesures sur 6 suffisent** pour avancer ✅,
  les 2 manquantes apparaissent en « à prendre ensemble » dans le message ✅
- **Email seul** (sans WhatsApp) accepté à l'étape 4 ✅
- Pièce sans prix : total « sur devis » de bout en bout ✅
- Robe ovale : l'avertissement de validation s'affiche ✅

---

## 9. Reste à faire

- [ ] Récupérer les 8 informations du §6 — **le numéro WhatsApp d'abord**
- [ ] Faire valider les mesures de la **robe ovale** par l'atelier
- [ ] Intégrer les vraies pièces, prix et photos
- [ ] Générer le **QR code** et l'affiche A4
- [ ] Déployer sur Cloudflare Pages (projet `hillary-m-styl`)
- [ ] Fiche Google Business et avis clients
- [ ] Vérifier le numéro WhatsApp **en envoyant un vrai message dessus** avant diffusion

---

## 10. Offre NEBULA correspondante

Ce projet dépasse le **Catalogue Digital** simple : il embarque un moteur de commande avec
prise de mesures par type de vêtement, calcul de frais par pays et date de disponibilité.
Il se situe entre le Catalogue à 50 000 F et l'**Outil Digital sur mesure**. À chiffrer
avec le configurateur du site (`www.nebula-agency.online`) plutôt qu'au forfait catalogue.

Références de méthode : `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md` (prix et
règles) et `_documents/nebula-agency/vente/05-GUIDE-OUTIL-METIER.md` (cadrage).

---

*NEBULA Agency · Cotonou*
