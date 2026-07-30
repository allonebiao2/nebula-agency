# MISE EN LIGNE DES SUPPORTS DE VENTE
## Comment les guides arrivent dans les mains des partenaires

> Document de procédure, à l'usage de Mongazi. Les partenaires n'ont pas besoin de le lire.
>
> Version 1.0 · 2026-07-30

---

## 1. Où vont les documents

L'espace partenaire (`https://partenaires.nebula-agency.online`) contient déjà un module
**Documentation** entièrement fonctionnel : l'admin téléverse, tous les partenaires voient
la mise à jour instantanément, et ils peuvent lire ou télécharger depuis leur téléphone.

**Il n'y a rien à développer.** Il faut téléverser.

| Document | Catégorie dans l'app | Qui y a accès |
|---|---|---|
| Manuel du Partenaire | **Formation** | Tous |
| Guide Catalogue | **Produits** | Tous |
| Guide Vitrine | **Produits** | Tous (après 1ère vente livrée) |
| Guide Outil métier | **Produits** | **Partenaires certifiés uniquement** |
| Arsenal des scripts | **Vente** | Tous |
| Simulateur de commissions | **Vente** (en lien) | Tous |

⚠️ **Le socle commercial (`00`) et l'avis de recrutement (`01`) ne se publient pas dans
l'espace partenaire.** Ce sont des documents internes à l'agence.

---

## 2. Le point de vigilance à traiter en premier

L'espace partenaire contient déjà **5 guides courts**, mis en place au démarrage du programme
(`server.py`, fonction `seed_docs`). Ils ne sont pas faux, mais ils sont maintenant **en
contradiction avec la nouvelle stratégie** sur un point important :

> L'ancien guide présente la Vitrine à 150 000 F comme « ton produit le plus rémunérateur »
> et invite à la pousser en premier.
>
> La stratégie retenue est l'inverse : **on entre par le Catalogue à 50 000 F**, et on monte
> l'escalier. Un partenaire qui attaque à 150 000 F sur un commerçant méfiant perd le client
> et les trois ventes qui auraient suivi.

**Action nécessaire :** retirer ou réécrire les anciens guides au moment où les nouveaux sont
publiés. Deux documents qui disent le contraire l'un de l'autre, c'est pire que pas de
document du tout.

---

## 3. Procédure de publication (15 minutes)

1. Convertir chaque document Markdown en **PDF** (voir §4).
2. Se connecter à l'espace admin.
3. Onglet **Documentation** → **Ajouter un document**.
4. Pour chacun : titre, catégorie (tableau du §1), description en une ligne, fichier PDF.
5. Supprimer ou réécrire les anciens guides contradictoires (§2).
6. Vérifier depuis un compte partenaire que les documents s'ouvrent bien **sur téléphone**.
7. Prévenir les partenaires par la messagerie de l'espace.

**Description à saisir pour chaque document :**

| Document | Description à coller |
|---|---|
| Manuel du Partenaire | Le socle du métier. À lire avant tout le reste. |
| Guide Catalogue | Ton arme d'entrée à 50 000 F. Tu peux la vendre dès aujourd'hui. |
| Guide Vitrine | 150 000 F. Après ta première vente livrée. |
| Guide Outil métier | Réservé : 3 ventes et binôme obligatoire sur tes 3 premiers dossiers. |
| Arsenal des scripts | Tous les messages prêts à copier, du premier contact à la recommandation. |

---

## 4. Conversion en PDF

Deux options, selon le temps disponible.

**Option rapide (aujourd'hui).** Convertir le Markdown en PDF simple et lisible.
Le contenu prime sur la mise en forme : un partenaire a besoin de lire, pas d'admirer.

**Option premium (recommandée à terme).** Reprendre l'atelier déjà utilisé pour le
**Playbook Boussole** et les PowerPoints du programme partenaires : mise en page HTML à la
charte cosmique NEBULA, puis export PDF via Chrome headless. Le résultat est un document
dont un partenaire est fier, qu'il peut montrer à un prospect, et qui donne à NEBULA
l'allure d'une vraie maison.

**Contrainte à respecter :** ces PDF sont lus **sur téléphone, en 4G, souvent dehors**.
Taille de police généreuse, contrastes francs, pas de fichier lourd.

---

## 5. Le simulateur de commissions

Fichier : `simulateur-commissions.html`

C'est une page autonome : un seul fichier, aucune dépendance, aucune image, fonctionne hors
ligne une fois ouverte. Le partenaire coche ses ventes du mois et voit sa commission,
son palier, et surtout **combien de ventes il lui manque pour changer de palier et ce que
ça lui rapporterait rétroactivement**.

**Deux usages, et le second vaut plus que le premier :**

1. **Motivation interne.** Un partenaire à 4 ventes le 25 du mois voit noir sur blanc que
   la 5ème lui rapporte sa commission **plus 10 000 F sur ce qu'il a déjà vendu**. Il sort
   la chercher.
2. **Recrutement.** Vous l'ouvrez devant un candidat en entretien, vous entrez 4 catalogues
   et 2 vitrines, et il voit 150 000 F s'afficher. Aucun discours ne fait ça.

**Vérifications faites :** balises équilibrées, JavaScript validé (`node --check`), et les
montants recalculés à la main sur 7 cas de figure, tous conformes au socle commercial
(1 catalogue = 12 500 F · 1 vitrine = 37 500 F · 6 ventes à 500 000 F = 150 000 F).

**Pour le mettre en ligne :** le déposer sur Cloudflare Pages comme les autres pages, ou
simplement le joindre en lien dans la Documentation de l'espace partenaire.

⚠️ **Le montant moyen des ventes du réseau est fixé à 100 000 F** dans le simulateur, à
titre d'estimation. À ajuster quand vous aurez les vrais chiffres de la vague 1.

---

## 6. Avant d'ouvrir le recrutement : les 11 points à trancher

Ces questions sont marquées « à confirmer » dans les guides. Tant qu'elles ne sont pas
tranchées, **les partenaires improviseront**, ce qui est exactement ce que ces documents
sont censés empêcher.

**Bloquant pour n'importe quelle vente**
1. **Procédure d'encaissement** : numéro Mobile Money officiel, acompte ou paiement intégral,
   justificatif remis au client.
2. **Délai de paiement des commissions** après réclamation. C'est la première question de
   tout bon vendeur en entretien.

**Bloquant sur le Catalogue (l'offre la plus vendue)**
3. **Nombre de produits inclus** dans les 50 000 F.
4. **Tarif des modifications** après livraison.

**Bloquant sur la Vitrine**
5. **Nombre de pages incluses** dans les 150 000 F (page unique, ou hub multi-pages ?).
6. **Ce qui est inclus exactement** : galerie, devis, prise de rendez-vous, carte, avis, FAQ.
7. **Nom de domaine personnalisé** (type `graindesthetique.com`) : inclus ou en supplément,
   et à quel prix ?

**Bloquant sur l'Outil métier**
8. **Acompte** : existe-t-il, quel montant, à quel moment ?
9. **Base de calcul de la commission** sur un projet à tranches : montant total, ou sommes
   réellement encaissées ?
10. **Boussole vendable par un partenaire ?** Beaucoup de dossiers détectés sur le terrain
    seront des cas Boussole, pas du sur-mesure. Si oui, à quelle commission ?

**Bloquant pour le recrutement**
11. **Durée de validité d'un lead** déposé par un partenaire, et **date limite de candidature**
    à insérer dans l'annonce.

---

## 7. Ordre de lancement recommandé

| # | Action | Qui | Quand |
|---|---|---|---|
| 1 | Trancher les 11 points du §6 | Mongazi | Avant tout |
| 2 | Répercuter les réponses dans les guides | | 1 heure de travail |
| 3 | Convertir en PDF et publier dans l'espace partenaire | | §3 et §4 |
| 4 | Nettoyer les anciens guides contradictoires | | §2 |
| 5 | Fixer la date limite et publier l'avis de recrutement | Mongazi | Plan de diffusion sur 14 jours |
| 6 | Entretiens avec la grille notée | Mongazi | J+8 à J+11 |
| 7 | Formation de démarrage collective (2h) | Mongazi | J+14 |
| 8 | Ajuster les guides avec ce que le terrain aura appris | | Après 30 jours |

**Le point 8 n'est pas optionnel.** Ces guides sont bons sur le papier. Ce sont les objections
réellement entendues à Dantokpa et à la Haie-Vive qui les rendront redoutables. Demandez à
chaque partenaire, chaque semaine, **la phrase exacte qui l'a bloqué**, et ajoutez-la.

---

*NEBULA Agency · Cotonou, Bénin.*
