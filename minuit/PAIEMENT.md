# MINUIT · la caisse et l'adresse

> Écrit le 2026-09-06, en appliquant les décisions 05, 06 et 09 de l'arrêté
> (`_plans/2026-09-06-minuit-arrete.html`).
>
> **Rien de tout ça n'est encore en ligne.** Le code est écrit, contrôlé
> (`node --experimental-strip-types minuit/_qc_caisse.mjs`, 118 contrôles),
> et il attend six réponses de Mongazi, listées en bas.

---

## 1. Ce que ça change

**Avant** : l'acheteur voyait un numéro Mobile Money, transférait la somme,
revenait coller la référence de son SMS, et Mongazi lisait son SMS avant que
la lettre existe. Deux minutes par vente, sur un ticket de 2 000 F.

**Maintenant** : il appuie sur « Payer 5 000 F », paie sur la page de SasPay
(Mobile Money ou carte), et **la lettre devient joignable toute seule** quand
la notification signée arrive, à trois heures du matin comme à midi.

⛔ **L'écran « colle la référence de ton SMS » est supprimé**, avec le numéro
Mobile Money et le choix du réseau. Il n'y a plus qu'un seul moyen de payer.

---

## 2. Où vit chaque morceau

| Morceau | Où | Ce qu'il fait |
|---|---|---|
| `supabase/lettres.sql` | Supabase, schéma `minuit` | Les lettres, les sessions, le journal des notifications, et les huit portes que seul le `service_role` peut pousser |
| `functions/_shared/lettre.ts` | Deno | **Tout ce qui décide** : le barème, le jeton, l'heure, l'expiration, le retrait, les en-têtes, ce qu'un acheteur a le droit d'envoyer |
| `functions/_shared/saspay.ts` | Deno | **La copie exacte de celle de PISTE**. Un contrôle compare les deux octet par octet |
| `functions/_shared/gabarit.ts` | Deno | `lettre.html`, recopié par `python minuit/_gabarit_ts.py`. **Fichier généré** |
| `functions/minuit-commande/` | Deno | Dépose la lettre, et ouvre son paiement s'il y en a un |
| `functions/minuit-paiement-recu/` | Deno | Le webhook. Vérifie la signature, marque payé, **ouvre la lettre** |
| `functions/minuit-lettre/` | Deno | Sert la lettre à `/l/<jeton>`, dit son état à `/l/<jeton>/etat`, et la retire à `/l/<jeton>/retrait` |
| `paiement.html` | Cloudflare Pages | **La page de paiement** : ce qu'on achète, la somme, et **le lien** |
| `merci.html` | Cloudflare Pages | **La page de retour**, celle que SasPay rappelle |
| `_qc_caisse.mjs` | Node, sans clé ni réseau | 118 contrôles sur tout ce qui décide |

---

## 2 bis. Les deux écrans que voit l'acheteur

**`paiement.html`** — il y arrive à la fin de sa commande. Elle montre pour qui,
l'offre, l'heure d'ouverture s'il en a choisi une, la somme, et **le lien** :
en bouton, **et écrit en clair avec un « Copier »**.

⚠️ **Le lien en clair n'est pas un détail.** À Cotonou on paie souvent depuis le
téléphone de quelqu'un d'autre, ou depuis celui qui porte le compte Mobile
Money. Un bouton qu'on ne peut pas copier oblige à recommencer toute la
commande sur l'autre appareil.

⛔ **Aucun champ sur cette page.** Ni code, ni numéro, ni référence : un
contrôle vérifie qu'elle ne contient **aucun** `input`. Une page de vitrine qui
demande un code Mobile Money est exactement ce qu'on apprend aux gens à ne
jamais faire.

**`merci.html`** — SasPay l'y ramène après le paiement.

⛔ **Elle ne déclare jamais un paiement réussi.** Son adresse se tape à la main :
revenir ne prouve rien. Elle dit « on attend la confirmation », et elle
interroge **l'état de la lettre**, qui, lui, ne ment pas : la lettre ne devient
`vivante` que lorsque la notification signée est arrivée. Quand c'est fait, la
page le dit toute seule et donne l'adresse à envoyer.

⚠️ **L'adresse de retour est propre à chaque commande** (`merci.html?j=<jeton>`)
et **doit être posée à l'appel** : le réglage par défaut de `_shared/saspay.ts`
ramène chez **PISTE**, puisque ce fichier en est la copie exacte. Sans cette
ligne, un acheteur de lettre tomberait sur la page d'un autre produit. Le nom
client par défaut aussi (« Client PISTE » sur un reçu MINUIT).

---

## 3. Les six règles qui tiennent la caisse

1. ⛔ **Le prix ne vient jamais du navigateur.** Le constructeur est un paquet
   statique : ce qu'il annonce se réécrit dans la console en trois secondes.
   Le barème de `_shared/lettre.ts` est le seul qui engage la caisse, et un
   contrôle le compare à celui de `creer.html`. **Deux barèmes sont deux
   vérités**, et on l'a payé une fois : les occasions portaient un « dès
   10 000 F » qu'on prenait au palier gratuit.

2. ⛔ **On ne stocke jamais le HTML envoyé par le navigateur.** On stocke les
   **données**, et la lettre est rebâtie à partir du gabarit à chaque lecture.
   Autrement cette porte serait un hébergeur de pages arbitraires sur notre
   propre domaine : gratuit, anonyme, et parfait pour une page qui imite une
   banque.

3. ⛔ **Le pied viral et le code secret sont des décisions du serveur.** Sinon
   le pied se retire d'un clic dans la console, et la boucle de croissance
   avec.

4. ⛔ **Le retrait passe avant tout le reste.** Avant l'état de la commande,
   avant la date, avant le remboursement. Une lettre payée puis retirée reste
   retirée, et le journal le dit.

5. ⛔ **Une lettre offerte ne passe pas par la caisse.** Elle est vivante tout
   de suite, et on rend son adresse.

6. ⛔ **Le brouillon ne s'efface qu'après une réponse heureuse.** L'acheteur
   quitte la page pour payer : un réseau qui tombe ne doit rien lui coûter de
   plus qu'un bouton à retoucher.

---

## 4. Brancher, le jour venu

```bash
# 0. la base, une seule fois, dans l'éditeur SQL de Supabase
#    → le contenu de minuit/supabase/lettres.sql

# 1. les secrets. ⛔ JAMAIS dans le dépôt, il est PUBLIC.
supabase secrets set SASPAY_CLE_SECRETE=…        # déjà posé pour PISTE
supabase secrets set SASPAY_SECRET_WEBHOOK=…     # déjà posé pour PISTE
supabase secrets set MINUIT_SITE=https://minuit.nebula-agency.online

# 2. le gabarit, à refaire À CHAQUE modification de lettre.html
python minuit/_gabarit_ts.py

# 3. les fonctions
cd minuit
supabase functions deploy minuit-commande
supabase functions deploy minuit-paiement-recu --no-verify-jwt
supabase functions deploy minuit-lettre        --no-verify-jwt

# 4. dans le tableau de bord SasPay, onglet « Webhooks », déclarer :
#    https://xukduhqqfzogisoimhyo.supabase.co/functions/v1/minuit-paiement-recu

# 5. les contrôles, avant tout
python minuit/_qc.py                                   # 127
node --experimental-strip-types minuit/_qc_caisse.mjs  # 118
```

⛔ **`--no-verify-jwt` n'est pas une négligence.** SasPay n'a pas de jeton
Supabase à présenter, et celle qui reçoit une lettre n'a pas de compte. Ce qui
protège le webhook, c'est **la signature vérifiée** ; ce qui protège la lettre,
c'est **une adresse de 110 bits tirés au sort**.

### L'adresse publique

`minuit-lettre` répond sur son adresse Supabase. Pour que le lien soit court et
lisible dans un message WhatsApp, un relais Cloudflare fait passer
`minuit.nebula-agency.online/l/*` vers la fonction, exactement comme le domaine
des partenaires passe par `nebula-partenaires`.

⚠️ **Une seule adresse.** La leçon de Mon Bénin : le site a longtemps répondu à
deux adresses sans en nommer aucune.

---

## 5. Ce qui reste, et qui n'appartient qu'à Mongazi

| Ce qu'il faut | Pourquoi ça bloque |
|---|---|
| **Le compte qui encaisse** | Celui de PISTE, ou un second. Un seul suffit tant que les libellés distinguent les deux produits. |
| **Le sous-domaine** | L'adresse est la première chose qu'on voit du produit. |
| **La commission SasPay** | Sur un ticket à 2 000 F, le taux décide de la marge. Écrit nulle part. |
| **Le premier franc** | Comme pour PISTE : le seul essai qui prouve le dernier maillon, celui qui relie une notification à une commande. |

Et deux choses qui ne dépendent de personne, mais qui ne sont pas faites :

- ⏳ **Le ménage des lettres expirées.** `minuit_menage()` existe et vide les
  photos d'une lettre expirée ; rien ne l'appelle encore. Une tâche planifiée
  quotidienne suffit (GitHub Actions le fait déjà gratuitement pour PISTE).
- ⏳ **Le lien « retirer cette lettre »** n'est pas dans le pied de la lettre :
  la porte existe, le bouton non. Pour l'instant le retrait passe par WhatsApp,
  ce que `CONDITIONS.md` décrit déjà.
