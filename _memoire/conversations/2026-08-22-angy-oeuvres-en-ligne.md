# 2026-08-22 — Angy Art : ses six œuvres passent en ligne, et un défilement qui punissait les machines lentes

## Ce que Mongazi a demandé

> Y'a des commit des push à faire vérifie les derniers et push, pour Angy art aussi

## 1 · Seize commits qui dormaient dans `main`

Le travail de la session téléphone était bien poussé : **ses six œuvres nommées
et chiffrées**, son vocabulaire, la collection **ÉNERGIES**, le second appel,
les créations personnalisées, et une reprise du défilement lissé.

**Rien n'était en ligne.**

| | avant | après |
|---|---|---|
| les six images | **404** | 200 |
| la page servie | 20 953 octets | **59 976 octets** |

⚠️ **Ce n'est pas un oubli, c'est structurel** : une session en conteneur n'a
**pas les jetons Cloudflare**, parce que `secrets/` est ignoré par git. Elle
peut tout écrire et ne rien publier. C'est le PC de Cotonou qui publie. La
même journée, le même piège s'était produit sur
[Hillary](2026-08-20-hillary-photos-recues.md) et sur
[Au Braisé d'Or](2026-08-19-braise-mise-en-ligne.md) : **un `git push` ne
déploie rien**.

### Vérifié en ligne, pas supposé

Les six fichiers répondent 200 (`alliance-solaire`, `ames-soeurs`, `aura`,
`bonheur-eternel`, `equilibre-des-ames`, `force-silencieuse`), les prix
s'affichent (100 000 · 200 000 · 350 000 · 500 000 FCFA), et `app.js` servi est
**identique octet pour octet** au fichier du disque (MD5).

⚠️ Version bumpée à **`?v=20260822a`** en **27 endroits** : `app.js` a changé,
et nos fichiers portent `Cache-Control: immutable` pour un an.

⚠️ Mes premières recherches dans la page servie ont donné zéro pour « Alliance
solaire » et « Équilibre des âmes » : **elle écrit ses titres avec ses propres
majuscules** (« Alliance Solaire », « L'Équilibre des Âmes »). Chercher une
chaîne exacte dans un texte écrit par quelqu'un d'autre, c'est chercher sa
propre orthographe.

## 2 · Un vrai défaut : le glissement n'était pas cassé, il n'était pas fini

Le contrôle disait : « accueil » ramène en haut sur **téléphone** et sur
**tablette**, mais laisse la page à **284 px** sur **ordinateur**. Et la valeur
changeait d'un essai à l'autre : 467 px la fois précédente.

Une position qui varie fait penser à une course entre deux mécanismes. C'était
plus simple et plus grave : la boucle avançait **d'un cran fixe par image**.

```js
courant += (cible - courant) * 0.095;      // dépend de la cadence
```

À 60 images par seconde, le trajet de 10 318 px est fini en 1,1 s. À 30, il en
faut **plus du double**. La page d'ordinateur, plus chargée en effets, tombe
justement sous les 60.

```js
var dt = dernier ? Math.min(64, ts - dernier) : 16.7;   // le plafond évite
var k  = 1 - Math.pow(1 - 0.095, dt / 16.7);            // le saut après un gel
courant += (cible - courant) * k;
```

⚠️ **Qui payait vraiment ?** Le moteur maison ne tourne que sur pointeur fin :
aucun contrôle mobile ne pouvait voir ce défaut. Or ce sont **les machines
lentes** qui le subissent, et à Cotonou ce sont nos visiteurs. Technique et
commande de recherche dans
[l'apprentissage du jour](../apprentissages/2026-08-22-interpolation-au-temps.md).

## 3 · Deux pannes de contrôle, aucune imputable au site

1. ⛔ **Le serveur de test était mono-tâche.** `Page.goto: Timeout` sur
   `127.0.0.1:8611`, et la suite ne démarrait même pas. Le navigateur garde ses
   connexions ouvertes : l'une bloquait les autres. Passé en
   `ThreadingTCPServer` — **exactement la panne réparée chez Hillary le 17**.
2. ⛔ **Le contrôle pariait sur 1 700 ms.** Il attend maintenant que la page
   **se pose** (immobile trois relevés d'affilée, six secondes au plus).

**150 contrôles verts, 0 en échec.**

## Ce qui reste chez Angélique

- l'**adresse de l'atelier**, de **vrais avis**, **tester le numéro WhatsApp** ;
- la cinquième et la sixième œuvre d'ÉNERGIES à confirmer **en observant** ;
- ⛔ toujours : **aucun prix, aucune dimension, aucun titre inventé** sur une
  mise en situation. Seule elle nomme une pièce.
