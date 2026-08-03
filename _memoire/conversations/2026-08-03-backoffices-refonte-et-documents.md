# 2026-08-03 · Les back-offices : l'écran noir, la refonte, et la zone Documents

> Session terminal, Cotonou. Neuf commits, tous en ligne sur Render.
> Fait suite à la migration Railway → Render + Supabase du 2026-08-02.

---

## Ce qui a été fait, dans l'ordre

| # | Commit | Ce que ça règle |
|---|---|---|
| 1 | `aa3cdc0` | **L'écran noir** : une connexion par requête, pas une par fonction |
| 2 | `81c8742` | Les **photos de profil** (deux défauts, pas un) |
| 3 | `0544842` | Le **WhatsApp qui ouvre la bonne conversation** + email obligatoire |
| 4 | `58d1de3` | **3 questions** qui trient vraiment un candidat |
| 5 | `8a13e10` | **Lisible sur téléphone** + le pooler Supabase qui cassait la lecture |
| 6 | `df8b0f3` | **Refonte vague 1** : la coquille, navigation ÉCRITE et 2 thèmes |
| 7 | `f4c0a1f` | **La zone Documents** porte enfin les vrais documents |
| 8 | `95e3cf3` | L'ordre de lecture des documents |
| 9 | `eef2e2d` | **Document 13** : prospection par métier, Bénin et Togo |

---

## 1. L'écran noir : ce n'était pas le JavaScript

Le cockpit restait noir au chargement. Le réflexe (chercher une erreur JS) était
le mauvais : `/api/admin/affiliates` **n'a jamais répondu**.

**La cause.** Ouvrir une connexion vers Supabase coûte **1,3 s** (7 s la première,
poignée de main TLS comprise). Sur SQLite c'était de l'ordre de la microseconde,
donc le code appelait `db()` librement, y compris dans des fonctions imbriquées.
Après la migration : 1 connexion pour la liste, **puis 2 par partenaire**.
Neuf connexions pour quatre partenaires, soit environ 12 s. Et ça grandit avec le
réseau.

**Le remède, en deux temps** (`dbx.py`) :
1. `ouvrir()` devient **réentrant** : un `with` imbriqué réutilise la connexion.
2. `requete()` tient **une connexion pour toute la requête HTTP**.

Le point 2 est indispensable : le code fait souvent `with db(): lire la liste`,
**puis boucle en dehors du bloc**, donc la connexion est déjà refermée. Ce motif
se répète à douze endroits. Une connexion par requête les répare tous, sans
toucher à un seul appel.

⚠️ On utilise un **ContextVar**, pas un thread-local : Starlette exécute les
fonctions synchrones dans un fil séparé, mais il **recopie le contexte**, donc la
connexion suit la requête jusque dans ce fil.

## 2. Le bug que la réparation a réveillé

Aussitôt : `DuplicatePreparedStatement: prepared statement "_pg3_0" already exists`.

psycopg3 « prépare » automatiquement une requête après **5 exécutions**. Le pooler
de Supabase (port 6543, mode transaction) multiplexe les connexions : la requête
préparée sur un serveur n'existe pas sur le suivant.

**`brut.prepare_threshold = None` est obligatoire avec le pooler.**

Le piège : le bug **n'apparaît qu'au-delà de 5 exécutions de la même requête sur
une connexion**. Il était donc invisible tant qu'on ouvrait une connexion par
appel, et il est sorti **au moment précis où on a corrigé la performance**. Il
faut le remettre dans **tout script** qui parle à Supabase, y compris les
one-shots d'administration (rencontré deux fois aujourd'hui).

## 3. Les photos de profil : deux défauts, pas un

1. Elles étaient écrites sur le disque de Render, **qui s'efface à chaque
   déploiement**. Passées en **base64 dans la base**.
2. Le gabarit fabriquait une URL avec un identifiant faux. Corrigé par
   `uid === 'admin' ? 'admin' : String(uid).replace(/^a/, '')`.

## 4. La candidature

- **WhatsApp** : le bouton ouvrait WhatsApp, pas **la conversation de la personne**.
  Il fallait le numéro au format international sans le zéro initial.
- **L'email devient obligatoire** (il était facultatif), et le candidat reçoit un
  message qui lui dit de surveiller **son WhatsApp et sa boîte mail**.
- **Trois questions ajoutées** au formulaire : le réseau de commerçants qu'il
  connaît déjà, sa disponibilité réelle, et l'outil dont il dispose. Ce sont les
  trois seules qui séparent un candidat sérieux d'un curieux.

## 5. La refonte, vague 1 : la coquille

Références données par Mongazi : **Helios Investments** et **Aura Store**.
Deux fiches écrites pour cadrer : `nebula-affilies/PRODUCT.md` et `DESIGN.md`.

Trois changements qui profitent aux 22 écrans d'un coup :

1. **La navigation porte des MOTS.** Les libellés existaient déjà dans le code,
   ils n'étaient jamais affichés : on ne voyait que des icônes. Une coupe, un
   sablier, un mégaphone ne se devinent pas. Sur PC, colonne de 216 px. Sur
   téléphone, **5 entrées avec leur mot**, le reste sous « Plus ».
2. **Deux thèmes**, sombre par défaut, clair d'un clic, mémorisé. Le clair existe
   pour **le téléphone en plein soleil à Cotonou**, pas pour la mode. ⚠️ Les
   couleurs de statut changent de **valeur** entre les thèmes, pas d'opacité : un
   vert clair sur blanc est illisible.
3. **Les mots du lecteur.** « Affiliés » → « Mes partenaires », « Réseau » → « Qui
   a recruté qui », « Paiements » → « À payer », « Publication » → « À partager ».

⚠️ **Vagues 2 et suivantes non faites** : les écrans eux-mêmes (compteurs avec
tendance, vrais tableaux avec pastilles de statut, états vides qui enseignent).
Mongazi a demandé « tout, écran par écran ».

## 6. La zone Documents, refaite entièrement

**Ce qu'il y avait** : 7 entrées. Cinq notes écrites en dur dans le code, et deux
PDF **dont les fichiers avaient déjà disparu** avec le disque de Render. On
cliquait, il ne se passait rien.

**Le piège en le réparant** : **trois** mécanismes concurrents recréaient ces
documents à chaque démarrage.
- `_SEED_DOCS` + `seed_content()` : les 5 notes si la table est vide
- `refresh_seeded_docs()` : les réécrivait à **chaque** démarrage
- `seed_docs()` : recopiait les 2 PDF **sur le disque volatil**

Supprimer les lignes en base n'aurait donc rien réglé : elles seraient revenues au
redémarrage suivant. Les trois sont remplacés par **un seul**,
`publier_documents()`, idempotent : il compare une version, ne réécrit que si elle
change, retire ce qu'il a lui-même posé et qui n'est plus au programme, et **ne
touche jamais** à un document ajouté à la main depuis le cockpit (marqueur
`url = 'nebula:socle'`).

**Ce qu'il y a maintenant** : les **10 documents** que tout partenaire doit avoir,
en PDF, **rangés dans la base en base64**, dans l'ordre de lecture.

| Ordre | Document | Catégorie |
|---|---|---|
| 1 | Le manuel du partenaire | Formation |
| 2 | Ton contrat de partenaire | Juridique |
| 3 | Vendre le Catalogue (50 000 F) | Produits |
| 4 | Vendre la Vitrine (150 000 F) | Produits |
| 5 | Vendre l'Outil sur mesure | Produits |
| 6 | Tous les messages prêts à envoyer | Vente |
| 7 | Au téléphone | Vente |
| 8 | La visite chez le commerçant | Vente |
| 9 | Trouver des clients : Bénin et Togo | Vente |
| 10 | L'annonce à partager | Marketing |

**Volontairement exclus, ils restent internes** : `00-SOCLE-COMMERCIAL` (les
décisions et les marges) et `01-AVIS-DE-RECRUTEMENT` (le dossier de sélection).

Détail : l'ordre d'affichage suit `updated DESC`. Les dix partageaient la même
seconde et sortaient **à l'envers**. Chacun reçoit maintenant une date
**volontaire**, calculée sur sa version et son rang.

Vérifié en vrai, avec un compte partenaire : connexion 200, les 10 documents
visibles, le contrat se télécharge en 205 Ko, `%PDF` en en-tête, nom de fichier
propre.

## 7. Document 13 · prospection par métier, Bénin et Togo

L'arsenal (`06`) donnait un message à froid **générique**. Il manquait le message
écrit **pour un métier précis**, et **le Togo n'apparaissait nulle part** dans les
13 documents de vente.

Écrit : l'annonce publique refaite, le premier message pour un restaurant, pour un
salon de couture, pour un particulier, où les trouver à Cotonou et à Lomé, et ce
que le Togo change.

⚠️ **Le paiement depuis le Togo est marqué À VÉRIFIER, pas affirmé.** Même monnaie
(franc CFA), T-Money (Togocom) et Flooz (Moov Africa) existent, mais **comment
l'argent arrive concrètement sur un compte béninois n'a pas été testé**. Le
document dit de tester un transfert de 1 000 F avant de promettre quoi que ce soit
à un client togolais.

Au passage : `_build_pdf.py` avait le chemin de Chrome **écrit en dur en Linux**
(`/opt/pw-browsers/…`). Il ne tournait donc pas depuis Cotonou. Il cherche
maintenant le navigateur au lieu de le supposer.

---

## Ce qui reste

- **Refonte vagues 2+** : les écrans eux-mêmes, écran par écran (demandé, pas fait)
- **Tester un transfert d'argent Togo → Bénin**, et le noter dans le document 13
- Confirmer le numéro de Romaric (8 chiffres, l'ARCEP en impose 10 depuis le
  30/11/2024)
- 4 commits non fusionnés sur `claude/github-repo-context-nisd2r` (prompts
  marketing et recrutement, conflits à trancher à la main)
- **Mongazi doit changer** le mot de passe Supabase et les clés Anthropic/Resend :
  elles ont transité par la conversation

## Liens

- [[2026-08-02-ai-seo-site-agence]]
- `nebula-affilies/PRODUCT.md` · `nebula-affilies/DESIGN.md` · `DEPLOIEMENT.md`
- `_memoire/affilies/cerveau-affilies.md`
- `_documents/nebula-agency/vente/13-PROSPECTION-BENIN-TOGO.md`
