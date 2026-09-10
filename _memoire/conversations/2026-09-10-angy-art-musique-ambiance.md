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
   ⏳ « No copyright music » sur YouTube n'est pas le domaine public :
   **la licence exacte reste à confirmer par Mongazi avant mise en ligne**.
3. **Réglage « doux »** : présent mais discret, le piano lisible sur un
   haut-parleur de téléphone.

## Ce que le fichier est devenu — `_son.py`

| | source | en ligne |
|---|---|---|
| durée | 120,1 s | **115,5 s** |
| poids | 2 112 Ko | **677 Ko** (−68 %) |
| forme | stéréo 44,1 kHz 136 kb/s | mono 32 kHz 48 kb/s |
| sonie | −8,2 LUFS | **−17,4 LUFS** |

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
**Le tamisé vient du niveau** (−17 LUFS et le volume de lecture), le filtre ne
retire que le souffle. ⛔ Ne pas empiler des filtres en croyant feutrer.

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
- ⏳ **Confirmer la licence** du morceau.
- ⏳ **Déployer** : les jetons Cloudflare sont dans `secrets/`, ignoré par git —
  une session en conteneur ne publie pas. C'est le PC de Cotonou.
- ⏳ **La source n'est pas versionnée** (`clients/*/_sources/` est ignoré, le
  dépôt est public). Si elle disparaît, elle se redemande à Mongazi.
