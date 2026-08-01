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
| Guide Vitrine | **Produits** | **Tous, dès l'entrée** (conclure seul : après 1ʳᵉ vente livrée) |
| Guide Outil métier | **Produits** | **Tous, dès l'entrée** (conclure seul : 3 ventes + binôme) |
| Arsenal des scripts | **Vente** | Tous |
| Simulateur de commissions | **Vente** (en lien) | Tous |
| Diagnostic Digital (méthode) | **Formation** | **Partenaires certifiés uniquement** |
| Fiche de diagnostic | **Vente** (en lien) | **Partenaires certifiés uniquement** |
| Contrat partenaire | remis à la formation, **pas publié** | signé avant création des accès |

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
| Guide Vitrine | 150 000 F. Lis-le maintenant. Tu la vends seul après ta première vente livrée. |
| Guide Outil métier | 55 000 à 500 000 F. Lis-le maintenant. Tu conclus seul après 3 ventes, en binôme avant. |
| Arsenal des scripts | Tous les messages prêts à copier, du premier contact à la recommandation. |
| Diagnostic Digital | La consultation qui ouvre les portes. 40 questions et la grille des automatisations. |

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

## 6. Toutes les décisions sont prises

Les 11 points en attente ont été tranchés le 2026-07-30, et 21 autres avec eux.
**Tout est consigné dans `00-SOCLE-COMMERCIAL.md`, qui fait foi.**

### Ce qui reste à faire, et ce n'est plus de la décision

| # | Action | Où |
|---|---|---|
| 1 | **Compléter le numéro IFU** de NEBULA dans le contrat | `09-CONTRAT-PARTENAIRE.md` |
| 2 | ~~Passer l'abonnement à 20 000 F sur le site public~~ **FAIT** (11 occurrences, cohérence `setTier`/`<option>` vérifiée). ⚠️ **pas encore déployé sur Cloudflare** | `00-nebula-agency/nebula_agency_v9.html` |
| 3 | ~~Aligner le cerveau de NOVA~~ **FAIT** : catalogue explicite (il dérivait de `SERVICES`, qui contient encore Fiche Google Maps et Avatar IA, retirés du site). ⚠️ **pas encore déployé sur Railway** | `nebula-affilies/server.py`, `agency_brain()` |
| 4 | ~~Réécrire les 5 guides seedés~~ **FAIT ET MIGRÉ.** `refresh_seeded_docs()` corrige automatiquement les documents déjà en base : idempotente, elle ne touche que ce qui porte encore l'ancien discours et laisse intact tout document ajouté à la main. Testée sur une base simulant la production | `nebula-affilies/server.py`, `refresh_seeded_docs()` |
| 5 | **Rappel de renouvellement** : ~~bloqué~~ **le modèle de données est implémenté et testé** (table `subscriptions`, commission 25 % à l'encaissement, 6 endpoints). Reste le workflow n8n et la variable `NAFF_CRON_KEY` sur Railway | `server.py` + `10-RELANCE-RENOUVELLEMENT.md` |
| 6 | ~~Convertir les documents en PDF~~ **FAIT** : 9 PDF à la charte cosmique dans `vente/pdf/`, régénérables via `_build_pdf.py`. Reste à les **téléverser** dans l'espace partenaire | `vente/pdf/` |

**Il ne reste que trois choses, et deux dépendent de vous :** le déploiement Cloudflare
(identifiants), le numéro IFU, et le téléversement des PDF dans l'espace partenaire.

## 7. Ordre de lancement recommandé

| # | Action | Qui | Quand |
|---|---|---|---|
| 1 | Compléter l'IFU et publier les 6 actions du §6 | Mongazi | Avant tout |
| 2 | ~~Répercuter les décisions dans les guides~~ **FAIT** | | |
| 3 | Convertir en PDF et publier dans l'espace partenaire | | §3 et §4 |
| 4 | Nettoyer les anciens guides contradictoires | | §2 |
| 5 | Publier l'avis de recrutement (candidatures ouvertes 21 jours) | Mongazi | Plan de diffusion sur 14 jours |
| 6 | Entretiens avec la grille notée | Mongazi | J+8 à J+11 |
| 7 | Formation de démarrage en visio Google Meet + signature de la charte et du contrat | Mongazi | J+14 |
| 8 | Ajuster les guides avec ce que le terrain aura appris | | Après 30 jours |

**Le point 8 n'est pas optionnel.** Ces guides sont bons sur le papier. Ce sont les objections
réellement entendues à Dantokpa et à la Haie-Vive qui les rendront redoutables. Demandez à
chaque partenaire, chaque semaine, **la phrase exacte qui l'a bloqué**, et ajoutez-la.

---

*NEBULA Agency · Cotonou, Bénin.*
