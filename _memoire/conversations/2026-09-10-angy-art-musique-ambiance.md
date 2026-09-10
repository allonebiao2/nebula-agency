# Angy Art — la musique d'ambiance (2026-09-10)

> Mongazi : « Je veux que tu lui ajoutes ce son sur sa vitrine bien tamisé et
> intégré et incrusté. L'objectif c'est que quand on rentre sur la vitrine le
> son doit se déclencher ou limite dès qu'il y a contact avec la vitrine, et que
> ce soit tamisé et immersif. » Puis : « Il faut que ce soit aussi comme la
> musique posée sur nebula-agency.online. »

Fichier reçu : `iced coffee & jazz lofi vibes`, **Tama's Little Music Shop**,
2 min, 2,16 Mo.

## Les trois décisions

1. **La musique remplace l'ambiance synthétisée** (nappe de trois oscillateurs,
   bruit filtré, gouttes). Deux nappes superposées font de la bouillie : le lofi
   porte déjà sa basse. Le code retiré reste dans git.
2. **Un crédit discret au pied** : « Musique : Tama's Little Music Shop ».
   ✅ **Licence tranchée par Mongazi le soir même** : « c'est écrit sur le titre
   no copyright donc sans souci ». J'avais signalé que « no copyright » sur
   YouTube n'est pas le domaine public ; il a maintenu, c'est sa décision.
   ⚠️ **Le crédit au pied reste posé**, et c'est précisément ce que ces chaînes
   demandent d'ordinaire : la précaution est déjà en place. ⛔ Sujet clos.
3. **Réglage « doux »** : présent mais discret, le piano lisible sur un
   haut-parleur de téléphone.

## Ce que le fichier est devenu — `_son.py`

| | source | en ligne |
|---|---|---|
| durée | 120,1 s | **115,5 s** |
| poids | 2 112 Ko | **677 Ko** (−68 %) |
| forme | stéréo 44,1 kHz 136 kb/s | mono 32 kHz 48 kb/s |
| sonie | −8,2 LUFS | **−11,9 LUFS** |

Format de la maison, celui de Mon Bénin (`benin-mon-pays/_sons_finir.py`), avec
`highpass=80, lowpass=3200, loudnorm=I=-17`. **−17 et non −20** : à Mon Bénin
l'ambiance passe sous une narration, ici la musique est seule.

## ⛔ Le morceau portait un fondu de sortie de quatre secondes

Mis en boucle tel quel, le site se serait **éteint pendant quatre secondes puis
rallumé d'un coup, toutes les deux minutes**.

⚠️ **Ce défaut ne se voit pas dans le débit.** Un premier examen comparait la
taille des trames MP3 — leur complexité — et concluait « aucun fondu, le morceau
est fait pour boucler ». La complexité reste haute quand le niveau s'effondre.
Mesuré au **niveau** : plein à −10 dB jusqu'à 116 s, puis −26,6 à 118 s, −41,7 à
119,5 s. **On mesure ce qu'on entend, pas ce qui code.**

Corrigé **dans le fichier, pas dans le navigateur** : `_son.py` détecte les
bornes de la musique (seuil relatif à la médiane, pas absolu), rogne le silence
de tête et le fondu, puis **referme le morceau sur lui-même par un fondu croisé
de 2 s**. Le raccord passe de **100 % d'écart à 14 %** (la maison tolère 35 %).
Le JavaScript n'a donc besoin que d'un `<audio loop>`.

⚠️ Deux pièges du fondu croisé : `amix` **divise** par le nombre d'entrées
(`normalize=0` obligatoire, sinon le passage sort 6 dB plus bas), et les fondus
doivent être en **`qsin`** — deux rampes linéaires qui se croisent laissent un
trou de 3 dB, parce que c'est la puissance qui s'additionne.

## ⚠️ Le filtre ne fait presque rien, et c'est normal

Mesuré à niveau égal : un `lowpass` à 3200 Hz creuse l'aigu de **2,0 dB**, trois
filtres empilés de **2,3 dB**. La source est du lofi : elle n'a presque rien
au-dessus de 4 kHz, et un filtre ne retire pas ce qui n'est pas là.
**Le tamisé vient du volume de lecture** (voir la correction du soir, plus bas :
une première version l'avait mis DANS le fichier, et c'était la faute), le filtre
ne retire que le souffle. ⛔ Ne pas empiler des filtres en croyant feutrer.

⚠️ **La première mesure des bandes mentait** : elle comparait les dB bruts, or la
normalisation baisse tout de 9 dB — toutes les bandes chutaient d'autant et la
mesure disait « le grave aussi a été filtré ». Elle mesurait la normalisation.
On retranche la sonie de chaque fichier avant de comparer.

## ⛔ L'astuce de la maison pour démarrer au contact NE MARCHE PAS

Djambar (client 05) et Au Braisé d'Or (client 09) lancent une lecture **en
sourdine** dès le chargement, avec ce commentaire : « démarre TOUT DE SUITE en
sourdine (autorisé partout) => la piste tourne, bufferisée, prête à être révélée
sans délai ».

Mesuré ici, Chromium la refuse aussi :

```
NotAllowedError: play() failed because the user didn't interact with the document first
```

**Ces deux sites croient bufferiser et ne bufferisent rien.** ⏳ À vérifier chez
eux un jour — ce n'était pas le chantier d'Angélique.

Ce qui marche et ne dépend d'**aucune** politique de lecture automatique :
`preload = 'auto'` puis **`el.load()`** — on télécharge sans jouer. Posé après
l'événement `load`, donc **le premier écran ne paie rien** (le chemin critique du
site est mesuré à 244 Ko).

Résultat mesuré : avant tout geste, `readyState = 4` et la piste est prête,
silencieuse. **Au contact, le son sort en 32 ms.** Sans le préchargement, il
aurait fallu attendre les 677 Ko — invisible sur un serveur local, plusieurs
secondes sur la 3G de Cotonou.

⛔ **Aucun navigateur ne laisse sortir du son sans geste.** « Dès qu'il y a
contact » est le mieux qui existe, et c'est ce que Mongazi avait lui-même écrit
en second. Sur Chrome de bureau, une **molette n'est pas un geste** au sens de la
lecture automatique : il faut un clic ou une touche.

## Le moteur — celui de nebula-agency.online

`<audio loop>` nu, volume en JS, **pas de Web Audio** — et c'est voulu : un
`<audio>` non routé dans Web Audio joue sur iPhone **même en mode silencieux**
(canal média), là où Web Audio est muet (leçon du 2026-05-25). Beaucoup de
téléphones ici vivent en silencieux.

Gestes écoutés : `pointerdown`, `touchstart`, `keydown`, `click`, `scroll`.
Fondu d'entrée **1,2 s** (l'agence est à 0,5 s, Mon Bénin à 2,2 s).
Volume **0,34** ordinateur / **0,40** tactile — une seule constante à changer.

**Deux choses ajoutées à ce que fait l'agence** :
- **`localStorage` (`angy:son`)** : couper reste coupé d'une visite à l'autre.
  L'agence ne mémorise rien. Djambar, Au Braisé d'Or et Hillary le font tous, et
  le README maison le demande.
- **Rien n'est téléchargé** chez qui a coupé, ni en `saveData` / `2g`. 677 Ko
  pris à quelqu'un qui ne veut pas de son, c'est son argent.

⚠️ **Le lecteur entre dans le DOM** (`hidden`). Un `new Audio()` gardé dans une
variable est **invisible pour tout contrôle** : impossible de vérifier qu'il
boucle, que son volume monte, qu'il se tait. Même choix qu'Au Braisé d'Or.

## Deux contrôles retournés, une sonde qui mentait

- ⚠️ **« le son est éteint par défaut »** est devenu faux par construction.
  Retourné en **« le bouton du son dit l'état réel du lecteur »** — il compare
  `aria-pressed` à ce que fait vraiment l'élément. Un contrôle qui devient faux
  ne se supprime pas.
- ⚠️ **« le lecteur ne précharge rien »** (écrit par moi le matin même) est
  devenu faux l'après-midi, quand le préchargement est devenu le produit.
  Retourné en **« le son ne part qu'après le premier écran »**, ce qui était
  l'exigence réelle depuis le début : l'attribut n'a jamais été le sujet.
- ⚠️ **Ma sonde mentait** : dater le préchargement avec
  `performance.getEntriesByType('resource')` ne trouvait **aucune** entrée pour
  le son alors que `readyState` valait 4 — **le Resource Timing n'expose pas les
  requêtes média**. Le contrôle accusait le site. Les jalons se datent
  maintenant côté Python. *Vérifier sa sonde avant d'accuser le produit.*
- ⚠️ **Une requête annulée n'est pas une ressource manquante** : depuis le
  préchargement, fermer l'onglet pendant le téléchargement fait remonter un
  `net::ERR_ABORTED` que le contrôle des ressources comptait comme un échec. Il
  garde désormais le motif de l'échec, pas seulement l'URL.

## Le garde-fou de publication

`_dist.py` copiait `assets/` en entier, mais **rien ne vérifiait que ce que la
page réclame est bien parti**. Un fichier renommé ou oublié aurait donné un 404
et un site muet, sans un mot — le défaut exact qui a livré le site d'Hillary
muet une fois. Le garde-fou lit le nom dans **les deux** fichiers qui peuvent le
porter (la page et le script, où le chemin est concaténé avec la version), et il
a été vérifié **avec un témoin** : fichier retiré, il refuse.

## Ce qui reste

- ⏳ **Écouter.** Tout ce qui précède est mesuré, rien n'est écouté. Le volume et
  le feutrage sont des paris argumentés.
- ⏳ **Tester sur un vrai téléphone** (leçon du 2026-05-25 : l'émulation ne
  reproduit pas le comportement audio d'iOS/Android). ⚠️ Un iPhone en mode
  silencieux : à vérifier, c'est justement ce que le choix du `<audio>` nu
  cherche à préserver.
- ⏳ **Déployer** : les jetons Cloudflare sont dans `secrets/`, ignoré par git —
  une session en conteneur ne publie pas. C'est le PC de Cotonou.
- ⏳ **La source n'est pas versionnée** (`clients/*/_sources/` est ignoré, le
  dépôt est public). Si elle disparaît, elle se redemande à Mongazi.


---

## ⛔ CORRECTION LE SOIR MÊME : le son était deux fois trop bas

> Mongazi, après écoute : « J'entends un bruit tout bas. Il faut que le son
> sorte bien, qu'on l'entende correctement. »

Il avait raison, et **c'était une faute de conception, pas un réglage à ajuster** :
j'avais atténué **deux fois**, dans le fichier *puis* au volume de lecture.

| | LUFS du fichier | volume | **entendus** |
|---|---|---|---|
| sa source, brute | −8,2 | — | — |
| le site de l'agence (**sa référence**) | −8,9 | 0,35 | **−18,0** |
| ⛔ ce que j'avais livré | −17,4 | 0,34 | **−26,8** |
| ✅ après correction | −11,9 | 0,57 / 0,66 | **−16,7 / −15,5** |

**Presque 9 dB sous sa propre référence.** Le fichier de l'agence n'est pas
normalisé du tout : il est brut, et **seul le volume de lecture le tamise**.

⚠️ **LA RÈGLE QUI MANQUAIT — le tamisé se fait AU VOLUME DE LECTURE, jamais dans
le fichier.** Le volume est une ligne, il s'entend tout de suite et se corrige en
une seconde. Un fichier encodé trop bas, lui, se ré-encode — et surtout, il ne
*paraît* pas fautif : il est « normalisé », donc propre, donc on ne le soupçonne
pas. Normaliser reste utile (prévisibilité, pas de saturation), mais à un niveau
franc : **−11 LUFS**, pas −17.

⚠️ **ET LE QC VALIDAIT LE DÉFAUT.** Le contrôle du volume acceptait
`0,05 < v ≤ 0,55` : il bornait le côté « trop fort » et laissait le côté
« inaudible » grand ouvert. **Un contrôle qui borne un confort doit border les
deux côtés** — le côté qu'on ne surveille pas est celui qui passe. Nouvelle
plage : **0,45 ≤ v ≤ 0,80**, avec le motif écrit des deux bornes.

⚠️ Le `lowpass` passe de 3200 à **5000 Hz** : quand on cherche la présence, on
ne garde pas un feutrage réglé pour la discrétion.

**Ce que la mesure a permis** : la comparaison chiffrée au site de l'agence — la
référence que Mongazi avait lui-même donnée — a transformé « ça doit sortir
mieux » en un écart de 8,8 dB et une cible. Sans elle, j'aurais monté le volume
au jugé, sans savoir si c'était assez.

---

## Mise en ligne, le 2026-09-10 depuis le PC de Cotonou

Le travail avait dormi dans `main` toute l'après-midi : la session distante ne
pouvait pas déployer, son proxy bloquant `api.cloudflare.com`. Le PC l'a fait.

**QC 242 verts**, `_dist` à 48 fichiers pour 8,89 Mo, déploiement Cloudflare
(3 fichiers envoyés, 44 déjà présents), cache de zone vidé, puis **12 contrôles
verts en ligne** : page et morceau **identiques au disque en MD5**, morceau servi
en `audio/mpeg`, script en ligne portant le nouveau moteur, domaine servant la
même chose que son origine `*.pages.dev`, adresse inconnue en 404.

### ⛔ Ce qui a bloqué, et ce que ça apprend

**`wrangler` ne lit pas `secrets/cloudflare.env` tout seul.** Il exige
`CLOUDFLARE_API_TOKEN` dans l'environnement, sinon il s'arrête sur *« In a
non-interactive environment, it's necessary to set a CLOUDFLARE_API_TOKEN »*.

⚠️ **L'arrêt tombait à la pire place** : après le contrôle qualité et après la
composition de `_dist`, c'est-à-dire après tout ce qui coûte des minutes. Un
script « en une seule commande » doit vérifier ce dont il a besoin **avant** de
faire le travail cher, pas au moment de s'en servir. `charger_jeton()` charge
maintenant le fichier, et dit clairement ce qui manque si la clé n'y est pas.

### ⚠️ Et pourquoi ce PC ne voyait même pas `_publier.py`

Au début de la session, `main` local était **en retard de 11 commits** sur
`origin/main`. La commande collée par Mongazi a donc été déclarée inexistante,
recherche à l'appui, alors qu'elle était poussée depuis une heure. **Un `find`
qui ne trouve rien ne prouve rien tant que le `git fetch` n'a pas été fait** :
c'est la règle du 2026-08-27, payée une seconde fois, en sens inverse (le PC a
cette fois nié un travail au lieu de le refaire).

---

## ⛔ « Je n'entends toujours pas le son » — le fondu ne doit pas tenir à une promesse

Mongazi, une fois le site en ligne et vérifié. Le déploiement était bon : les
octets servis étaient ceux du disque. **« Les octets sont bons » ne veut pas
dire « le son se déclenche ».**

### Ce que la mesure a établi

Le fichier est **valide et décodable** (`decodeAudioData` : 115,5 s, mono,
48 kHz) et **servi correctement**, y compris en requêtes par plage (`206`,
`Content-Range` exact) : ni le réseau ni Cloudflare ne sont en cause. Et
`localStorage['angy:son']` était **vide**, donc le son n'avait pas été coupé
par mégarde.

### ⛔ Le défaut

L'élément naît à `volume = 0` et **seul `reussi()` le remonte**. Or `reussi()`
ne tenait qu'au `.then()` de `play()`. Une promesse qui tarde, se perd, ou
court contre la mise en pause d'un onglet caché laisse alors la piste tourner
**à volume zéro pour toujours** : `paused` est faux, le bouton affiche encore
« Écouter la musique », et on n'entend rien.

Mesuré exactement ainsi en ligne : `paused:false · volume:0 · currentTime:0`.

**Ce qui rend une musique audible ne doit pas être une promesse.** Le fondu
suit désormais l'événement **`playing`**, celui qui signifie littéralement « du
son sort maintenant ». La promesse reste en second chemin, et `reussi()` ne
s'exécute qu'une fois.

### ⚠️ Ma sonde a menti avant de dire vrai, une fois de plus

Le premier diagnostic accusait le fichier : un `<audio>` neuf, puis un `<audio>`
alimenté par un **blob** sans aucun réseau, se bloquaient tous deux à
`readyState 0`. Cause réelle : **`document.visibilityState === "hidden"`**.
Chrome diffère le chargement média dans un onglet qui n'est pas au premier
plan, et c'est cela que je mesurais. ⚠️ **Un onglet piloté par automatisation
n'est pas au premier plan** : toute mesure de média qui y est faite doit
d'abord lire `visibilityState`, sinon elle accuse le produit à la place de
l'instrument. Même famille que les cinq sondes menteuses du 2026-08-26.

### ⚠️ Le `?v=` a été bumpé, lui

`app.js?v=20260910a` → `20260910b`. Nos assets portent `immutable` un an :
sans ce bump, tous ceux qui avaient ouvert le site aujourd'hui, Mongazi le
premier, seraient restés sur la version silencieuse. `app.css` n'a pas bougé,
donc son `?v=` non plus.

### 🧹 Le MP3 source sorti du dépôt

`git add -A` avait emporté `_partage/iced coffee … [FUVt6vnJcGc].mp3`
(2,1 Mo, le téléchargement brut). `_partage/` est versionné exprès, mais les
**médias bruts dont la forme finale est déjà au dépôt** en sont exclus : deux
autres MP3 y étaient déjà nommés. Celui-ci les rejoint, et le fichier reste sur
le disque. ⚠️ **Le blob demeure dans l'historique** d'un dépôt public : le
retirer vraiment demanderait une réécriture d'historique et un `push --force`,
donc **Mongazi tranche**.

---

## Le défaut pris en flagrant délit dans le navigateur

Mongazi : « vérifie toi-même, tu as accès, t'es dans l'extension ». Fait, sur
le site en ligne, dans son Chrome.

**49,6 secondes de lecture à `volume 0.00`.** Le morceau se charge
(`readyState 4`), démarre (`playing` à 480 ms), la promesse de `play()` se
résout, `timeupdate` défile de 0 à 49,6 s — et le volume ne quitte jamais zéro.
La piste tourne, rien ne sort. C'est le silence, mesuré, pas déduit.

### Ce que la mesure a écarté, définitivement

- **le fichier** : 693 620 octets servis, `audio/mpeg`, `206` avec
  `Content-Range` exact ; contenu = 115,5 s de vraie musique, crête **0,0 dBFS**,
  moyenne **−10,9 dBFS**, **aucun silence au début**, niveau constant sur douze
  tranches de 10 s (−10,4 à −11,6)
- **la sortie audio** : un `AudioContext` a joué 3 s du morceau à travers ses
  haut-parleurs, `running`, 2 canaux, horloge qui avance

### ⛔ Second défaut, découvert par la mesure elle-même

**`requestAnimationFrame` ne tourne pas dans un onglet caché**, donc `fondre()`
n'y progresse jamais et le volume reste à 0. Une page ouverte en arrière-plan
serait revenue muette. `fondre()` pose désormais la valeur d'un coup quand
`document.hidden` : personne ne regarde, personne n'a besoin d'un fondu.

### ⚠️ Ce que l'extension ne peut PAS faire, et il faut le savoir

Le groupe d'onglets de l'extension vit dans une **fenêtre occultée**. Chrome y :

- refuse toute nouvelle activation par clic → `play()` rend `NotAllowedError`
  et `navigator.userActivation.hasBeenActive` reste **false**
- diffère le chargement média (`loadstart` puis `stalled`, `readyState 0`)
- étrangle les minuteurs jusqu'à **geler le moteur de rendu** (une boucle de
  douze `setTimeout` d'une seconde a fait expirer CDP à 45 s)
- n'exécute aucun `requestAnimationFrame`

⚠️ **Toute mesure de média faite là-bas doit d'abord lire `visibilityState`**,
sinon elle accuse le produit à la place de l'instrument — ce qui est arrivé
ici : le premier diagnostic accusait le fichier. Contournement qui marche :
**armer les écouteurs dans un appel, relire dans un appel séparé**, sans jamais
attendre dans la page.

### ⚠️ Et l'explication la plus probable de la plainte initiale

La musique n'était en ligne que **depuis une heure**. Avant le déploiement du
jour, elle dormait dans `main` et le site n'en avait **aucune**. Quand Mongazi
a testé et conclu que c'était raté, il écoutait un site qui n'avait jamais eu
de musique. Les deux défauts ci-dessus étaient bien réels, mais ils l'auraient
mordu **ensuite**.

---

## ⛔ « Sur PC ça marche, sur mobile c'est comme au tout départ »

Mongazi, le même jour. Et c'était vrai : un chemin ne s'ouvrait que sur mobile,
et il fermait tout.

```js
function economie() {
  var c = navigator.connection || navigator.webkitConnection;
  return !!(c && (c.saveData === true || /(^|-)2g$/.test(c.effectiveType || '')));
}
function precharger() { if (joue || refuse || economie()) return; ... }
function demarrer()   { if (joue || refuse || economie()) return; ... }   // ⛔ ICI
```

⚠️ **`navigator.connection` n'existe QUE sur Android.** Sur un PC il est absent,
donc `economie()` rend `false` et la musique part. Sur un téléphone à Cotonou il
rend très souvent `2g` (c'est une **estimation de latence**, pas la vraie radio)
ou `saveData` si l'économiseur est actif : le site refusait alors de jouer
**quel que soit le geste, pour toujours**.

### Mesuré, avant et après, sur le site en ligne

| | téléphone annonçant `2g` | téléphone ordinaire |
|---|---|---|
| avant | **l'élément `<audio>` n'est même pas créé** | joue, `vol 0.66` |
| après | joue, `vol 0.66` | joue, `vol 0.66` |

### La leçon

**Économiser les données de la visiteuse, c'est ne pas télécharger 677 Ko
qu'elle n'a pas demandés. Ce n'est pas lui refuser le son qu'elle vient de
demander en touchant l'écran.** Le garde-fou ne barre plus que `precharger()`.
Sur connexion lente, rien n'est pris en avance et le morceau part au toucher :
le **résultat** est le même partout, seule la mise en tampon s'adapte.

⚠️ **Une intention louable posée au mauvais endroit coupe la fonction.** Le
commentaire d'origine disait « on ne télécharge rien si on ne va pas jouer » :
juste pour le préchargement, faux pour la lecture, et les deux portes
partageaient la même condition.

**QC 242 → 244** : deux contrôles téléphone (connexion lente annoncée,
économiseur de données) qui feignent `navigator.connection` **avant le
chargement**, touchent l'écran, et exigent que ça lise à volume non nul.

### ⚠️ Et un piège de publication découvert au passage

`_publier.py` vérifiait **dans la seconde** qui suit la purge, alors que
`purger.py` dit lui-même de compter une minute : `app.js` a été annoncé
« différent du disque » alors qu'il était juste. ⛔ **Ce n'est pas un faux
positif à ignorer** : un vrai cache empoisonné rend exactement le même rouge.
Le script attend donc la minute et redemande **une seule fois**.

⚠️ **Ma sonde a encore menti d'abord** : une comparaison en PowerShell relisait
le corps en texte puis le ré-encodait en UTF-8, et ce fichier est plein
d'accents et de symboles — elle annonçait 53 115 octets pour 52 502. **On
compare des octets, jamais du texte relu.**
