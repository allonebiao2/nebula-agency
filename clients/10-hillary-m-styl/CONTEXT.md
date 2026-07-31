# CLIENT 10 — HILLARY M. STYL

> **Maison de couture · prêt-à-porter & sur-mesure**
> Vitrine avec catalogue commandable et prise de mesures en ligne.
> Créé le 2026-07-31.

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

## 2. Ce qui a été livré

**Fichier :** `vitrine.html` — un seul fichier, 120 Ko, aucune dépendance externe hormis
les polices Google. Logo en base64 WebP, déclaré **une seule fois** en variable CSS.

### Les sections
1. **Héros** avec accueil personnalisé (bonjour / bon après-midi / bonsoir, et le prénom
   du visiteur s'il est déjà venu) et deux portes d'entrée : prêt-à-porter ou sur-mesure
2. **La maison** — quatre piliers : mesures en ligne, retrait ou expédition, normal ou
   express, prévenu quand c'est prêt
3. **Catalogue à deux onglets** — prêt-à-porter (avec tailles) et sur-mesure
4. **Comment ça se passe** — quatre étapes, de la commande à l'essayage
5. **L'atelier** — adresse, horaires, WhatsApp, retrait gratuit

### Le tunnel de commande (au cœur du projet)
Une fiche s'ouvre au clic sur une pièce, avec quatre étapes :

| Étape | Prêt-à-porter | Sur-mesure |
|---|---|---|
| **1** | Choix de la taille (XS → XXL) | **Formulaire de mesures** : 8 mesures, femme ou homme, en centimètres, + tissu et détails souhaités |
| **2** | Retrait atelier (gratuit) ou expédition — **les frais s'affichent par pays** | idem |
| **3** | Délai **normal** ou **express** (avec supplément) | idem |
| **4** | Coordonnées client | idem |

Un **récapitulatif chiffré** se met à jour en direct (pièce + livraison + délai = total),
puis la commande part sur WhatsApp en message structuré, avec toutes les mesures.

**Détails de conception qui comptent :**
- Une mesure laissée vide n'est pas bloquante : elle part en « à prendre ensemble » et le
  message indique combien il en manque. Un client qui ne sait pas mesurer son entrejambe
  ne doit pas abandonner sa commande.
- Les pièces sans prix affichent « sur devis » et le total bascule en « sur devis »
  automatiquement.
- Le prénom est mémorisé localement pour l'accueil personnalisé des visites suivantes.

---

## 3. ⚠️ À CONFIRMER AVANT MISE EN LIGNE

**Rien de tout cela n'a été inventé : les valeurs en place sont des exemples clairement
marqués dans le code, en haut du `<script>`, dans un bloc « ZONE À COMPLÉTER ».**

| # | Information | Pourquoi c'est bloquant |
|---|---|---|
| 1 | **Numéro WhatsApp** (`WHATSAPP`) | Actuellement `22900000000`. **Aucune commande n'arrivera** tant qu'il n'est pas remplacé |
| 2 | **Frais d'expédition par pays** (`LIVRAISON`) | Valeurs provisoires. Un tarif faux coûte de l'argent à la cliente **à chaque commande** |
| 3 | **Délais de confection** (`DELAIS`) | 10-14 jours en normal, 4-6 en express : à valider avec l'atelier |
| 4 | **Le catalogue** (`PIECES`) | 12 modèles d'exemple avec des prix d'exemple. À remplacer par les vraies pièces |
| 5 | **Photos des pièces** | Aucune photo fournie. Les cartes affichent un visuel de substitution élégant marqué « photo à venir » |
| 6 | **Adresse et horaires de l'atelier** (`ATELIER`) | Affichent « à confirmer » |
| 7 | **Prix du supplément express** | 10 000 F par défaut |

**Conseil photo à transmettre à la cliente :** dehors le matin ou en fin d'après-midi, à
l'ombre, sur un fond uni, la pièce portée ou sur mannequin. Format portrait (les cartes
sont en 3:4). C'est ce qui fera la différence entre un catalogue correct et un beau catalogue.

---

## 4. Vérifications passées

- **Aucun débordement horizontal** sur 390 px, 768 px et 1440 px, page et modale ouverte
- **Aucune erreur JavaScript**, aucune requête en échec
- **Toutes les cibles tactiles ≥ 44 px**
- **Aucune image externe** : logo en base64, zéro dépendance qui puisse casser
- Tunnel testé : robe 35 000 + Côte d'Ivoire 12 000 + express 10 000 = **57 000 F** ✅ ·
  retrait atelier gratuit ✅ · bascule femme/homme des mesures ✅ · « sur devis » ✅
- **120 Ko** au total, pensé pour la 3G

---

## 5. Reste à faire

- [ ] Récupérer les 7 informations du §3
- [ ] Intégrer les vraies pièces, prix et photos
- [ ] Générer le **QR code** et l'affiche A4
- [ ] Déployer sur Cloudflare Pages (projet `hillary-m-styl`)
- [ ] Fiche Google Business et avis clients
- [ ] Vérifier le numéro WhatsApp **en envoyant un vrai message dessus** avant diffusion

---

## 6. Offre NEBULA correspondante

Ce projet dépasse le **Catalogue Digital** simple : il embarque un moteur de commande avec
prise de mesures et calcul de frais par pays. Il se situe entre le Catalogue à 50 000 F et
l'**Outil Digital sur mesure**. À chiffrer avec le configurateur du site
(`www.nebula-agency.online`) plutôt qu'au forfait catalogue.

Références de méthode : `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md` (prix et
règles) et `_documents/nebula-agency/vente/05-GUIDE-OUTIL-METIER.md` (cadrage).

---

*NEBULA Agency · Cotonou*
