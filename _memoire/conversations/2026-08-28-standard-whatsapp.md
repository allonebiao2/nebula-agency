# LE STANDARD — l'agent WhatsApp qui lit la vraie carte et refuse d'inventer un prix

*2026-08-28. Mongazi : « apparemment possible d'automatiser WhatsApp avec ça,
fais-le », avec un lien vers `anthropic.com/whatsapp-agent-kit`.*

---

## D'abord : le lien n'existe pas

`anthropic.com/whatsapp-agent-kit` est **bloqué par le mandataire réseau**, et la
recherche ne trouve **aucune page Anthropic à cette adresse**. Ce qui circule
sous ce nom est un dépôt communautaire, `whatsapp-agentkit` (Whapi + Anthropic,
en français, « ton agent WhatsApp en moins de 30 minutes avec Claude Code »).
Il est bien réel, et son architecture a été lue : assistant `/build-agent`,
webhook Whapi, SQLite par numéro, huit questions sur le métier.

⚠️ **Il n'a pas été copié, et pour une raison précise** : il fait écrire le
catalogue à la main, dans `config/business.yaml` et `knowledge/`. Chez NEBULA
c'est exactement ce qu'on ne fait pas — voir l'en-tête de `dishes.ts`.

## Ce qui existait déjà, et le trou qui restait

`boutique-ia/` (Vendora) est **déjà** un agent vendeur WhatsApp : 11 500 lignes,
Meta Cloud API, cerveau, relances, transcription, Supabase, paiement MoMo,
tableau de bord. Refaire ça aurait été du gâchis.

Mais Vendora est un **SaaS pour des commerçants qui s'inscrivent**. Les onze
clients NEBULA n'y sont pas : leurs catalogues vivent dans leurs propres
dossiers, et leurs vitrines finissent toutes sur « écrire sur WhatsApp » —
**le seul maillon de toute la chaîne que personne n'a automatisé**. Quelqu'un
répond à la main, le soir, pendant le service.

C'est ce trou que le kit remplit : `whatsapp-agent/`, produit interne, un agent
par client existant.

## Les trois décisions qui font le produit

### 1. Le catalogue est LU, jamais recopié

`lecteurs/braise.py` lit `clients/09-au-braise-dor/experience/data/carte.ts`.
`lecteurs/hillary.py` lit le tableau `PIECES` de `_vitrine_src.html`. Entre les
deux, `lecteurs/js_litteral.py` : un lecteur de littéraux JS/TS écrit à la main,
qui **n'exécute aucun code** (ni `eval`, ni `exec` — un contrôle le vérifie) et
qui avale les clés sans guillemets, les apostrophes, les virgules finales et les
commentaires français.

⚠️ **Le piège du parseur** : `export const CARTE: Cat[] = [` — l'annotation de
type contient un crochet **avant** le `=`. Le premier jet cherchait « le premier
crochet venu » et ne trouvait jamais la déclaration. Il saute désormais
l'annotation jusqu'au `=`, et refuse `==`, `=>`, `<=`.

⚠️ **Une mention n'est pas une déclaration** : `NB_PLATS = CARTE.reduce(...)`
cite `CARTE` sans la déclarer. Partir de la première occurrence rendait un
catalogue vide **sans le dire**.

### 2. Les cinq façons d'avoir un prix

La carte du Braisé d'Or les utilise **toutes**, et les aplatir coûte de l'argent :

| mode | exemple | ce qu'on perdrait |
|---|---|---|
| simple | 3 000 F | — |
| deux tailles | 3 000 / 6 000 F | la grande portion |
| fourchette | de 1 500 à 3 500 F (les sauces) | on annoncerait un prix ferme |
| paliers | glace 1 000 / 1 500 / 2 500 F | **encaisser 1 000 au lieu de 2 500** |
| sur demande | `p: 0` | un total qui ment |

⚠️ La glace porte **à la fois** `p: 1000` et ses trois paliers. Le barème passe
devant le prix d'appel — c'est la leçon du 26 août, portée dans le lecteur.

### 3. LE GARDE-FOU — et le chiffre qui a tout décidé

Le prompt interdit d'inventer un prix. **Ça ne suffit pas.** Avant tout envoi,
`agent/garde_prix.py` relit la réponse, en extrait chaque montant, et le vérifie.

⛔ **Le premier jet était inutile, et il a fallu le mesurer pour le voir.** Il
acceptait un montant s'il était une addition possible d'articles de la carte.
Or, sur la carte du Braisé d'Or, **90 % des montants ronds entre 100 et
18 000 F** sont atteignables en six articles ou moins. Chez Hillary : **2 %**.
Le même contrôle paraissait excellent sur un client et ne valait rien sur
l'autre.

**La correction : l'attachement.** Chaque montant est rattaché au **nom
d'article le plus proche dans sa phrase** et vérifié contre CET article. Un
total n'est admis que s'il combine **au moins deux** articles nommés.

```
« Le tilapia braisé est à 4 500 F. »              ⛔ bloqué (la carte dit 3 000 / 6 000)
« Un tilapia braisé et une salade verte : 4 000 F. » ✅ somme de deux plats nommés
« Le cappuccino est à 600 F et le yaourt à 1 500 F. » ⛔ bloqué : prix croisés
« Une sauce gombo bien garnie, 2 800 F. »          ✅ dans la fourchette
« La glace 4 boules est à 3 000 F. »               ⛔ bloqué : le 4 compte des boules
```

⚠️ **Les mots qui reconnaissent un plat sont calculés depuis les données** : un
mot ne vaut que s'il n'appartient qu'à un article de toute la carte
(55 chez le Braisé d'Or, 20 chez Hillary). « tilapia » oui, « sauce » non.

⚠️ **Les espaces insécables ont failli tout casser.** La carte rend « 3 000 F »
avec une espace fine insécable (U+202F) et une insécable devant le F (U+00A0) —
la bonne typographie de la maison. Le modèle les recopie. Une expression
régulière qui n'accepterait que l'espace ordinaire lirait « 000 F » et
vérifierait un montant qui n'a jamais été écrit. Les quatre séparateurs sont
nommés un par un.

**Quand le garde-fou bloque** : le client reçoit une phrase honnête, sans
promesse de délai ; le patron reçoit **le message que l'agent allait envoyer,
en entier**, et le motif.

## Ce que la suite de contrôles a trouvé, et que la relecture n'avait pas vu

⛔ **Une commande confirmée n'était annoncée à personne.** Le service ne
prévenait la maison que sur `escalades`. Une commande était enregistrée,
récapitulée au client, et le restaurant ne l'apprenait jamais. Trouvé par un
contrôle écrit **par chemin de sortie** (répondre · prévenir · enregistrer · se
taire), pas par fonction.

⛔ **Un webhook réglé sur « console » ou Twilio plantait en 500** sur
`/webhook/` : ces canaux n'ont pas de méthode de signature. Un webhook qui
répond 500 finit désabonné par Meta.

**Doublon de prompt** : les accompagnements étaient écrits deux fois (la note de
rubrique les énumère déjà) — dix lignes payées et mises en cache pour rien, et
deux listes à comparer là où il en faut une.

## La preuve du principe, arrivée toute seule

Pendant la session, `main` a avancé de deux commits, dont
`2d5b1db fix(hillary): « Ensemble Volants » n'a jamais existé`. Ce commit touche
`_vitrine_src.html` — **le fichier que le lecteur d'Hillary lit**.

Après la fusion : **20 pièces → 19**, sans une ligne modifiée dans le kit, et
**146 contrôles toujours verts**. Aucun contrôle ne dit « 20 pièces » : ils
lisent les deux côtés et les comparent.

## Ce qui est vérifié, et ce qui ne l'est pas

**Vérifié ici** : 146 contrôles verts sans clé ni réseau · les deux catalogues
lus dans les vrais fichiers · le garde-fou sur les deux clients · le serveur en
vrai (curl : abonnement 200, mauvais jeton 403, sans signature 403, signature
falsifiée 403, bonne signature 200, maison inconnue 404) · `anthropic` 1.2.0
installé, tous les paramètres utilisés acceptés par la signature du SDK.

⛔ **NON vérifié : un appel réel au modèle.** Ce conteneur n'a **pas de clé
Anthropic** (`ANTHROPIC_API_KEY` absent, pas de CLI `ant`). La boucle, les
outils, le cache et le garde-fou sont éprouvés avec `tests/faux.py`, qui rejoue
des réponses écrites — c'est d'ailleurs la seule façon de vérifier qu'un prix
inventé est bloqué : un vrai modèle refuserait justement de l'inventer le jour
du test. **Le premier essai avec une vraie clé reste à faire**, depuis le PC.

## Ce qui attend Mongazi

1. ⛔ **Le numéro d'Au Braisé d'Or.** Le dépôt en porte **deux** :
   `index.html` → `2290156057157`, `dishes.ts` (le fichier servi) →
   `22956057157`, sans le `01`. L'enseigne affiche `43 99 29 29`. La fiche est
   **vide exprès** ; le serveur refuse de démarrer et dit pourquoi.
2. **Le numéro qui reçoit les alertes**, pour chaque maison.
3. **Par quel client commencer** — Braisé d'Or a le plus à gagner, Hillary a le
   catalogue le plus propre.
4. **Meta ou Twilio** pour le premier essai.

⚠️ **La fenêtre de 24 h, à savoir avant de vendre** : répondre à un client est
toujours permis, mais **prévenir le patron ne l'est pas toujours** — s'il n'a
rien écrit à son propre agent depuis la veille, l'alerte ne part pas. Le kit le
journalise fort et garde l'escalade en base. Une relance hors fenêtre demandera
un modèle pré-approuvé par Meta : ce n'est pas fait, et c'est écrit dans le
README.

## Coût

Sonnet 5 (règle NEBULA : jamais Opus sur du texte client). Socle ≈ 1 800 jetons,
mis en cache. Une conversation de dix messages : **≈ 16 F CFA** cache chaud,
**≈ 33 F** cache froid. Côté Meta, une conversation de service est gratuite
jusqu'à mille par mois.

## Fichiers

`whatsapp-agent/` — 27 fichiers, 3 351 lignes. Détail dans son `README.md`.
