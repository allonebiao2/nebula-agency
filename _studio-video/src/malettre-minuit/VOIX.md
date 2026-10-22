# MA LETTRE À… · « Minuit pile, pour maman » (16:9, 44 s)

> Décisions de Mongazi (2026-10-22) : **horizontal, « ultra wow »**, 40 à 45 s ; l'émotion d'abord, puis **la
> raison d'utiliser Ma lettre à…** : ce qu'on propose, les autres occasions et les moments où l'on s'en sert,
> avec de l'humour, du choc, de l'émerveillement, et l'envie d'essayer. **La voix est générée par Mongazi**
> (ElevenLabs), **la musique choisie par lui sur Pixabay**. Une animation propre à chaque moment, tirée de ses
> vidéos de référence (`_partage/ma lettre/*.mp4`) et de ce qu'elles inspirent.
>
> ⛔ Rien d'inventé : la lettre lue est une vraie lettre de la plume (fiche inventée, relue) ; chaque promesse
> existe dans le produit (28 occasions réelles, l'habillage, la pluie, la photo, la plume, dès 1 000 F).
> ⛔ Koffi est un personnage, pas un client : la vente est dite par une AUTRE voix (pas de faux témoignage).
> ⚠️ **La plume est coupée en ligne** jusqu'au chantier « la plume écrit après le paiement » : ne pas publier la
> vidéo avant qu'elle soit rouverte, ou enregistrer la variante sans la plume (plus bas).

## Les deux voix

- **Voix 1 · Koffi** (l'histoire) : homme, 25 à 35 ans, chaud, intime, un peu voilé, accent d'Afrique de
  l'Ouest si possible. Il parle bas, la nuit. Stabilité 40 à 50, similarité 75, style 0 à 15, vitesse 0,95.
- **Voix 2 · la narratrice** (la vente) : femme, chaleureuse, un sourire dans la voix, vive sans crier.
  **Alimata**, déjà utilisée pour la vidéo NEBULA, avec ses réglages d'octobre (vitesse 1,08, stabilité 50,
  similarité 75). Elle prononce la marque en français, même en anglais : « Ma lettre à… ».
- **Les balises d'intonation** (syntaxe d'ElevenLabs, vérifiée le 2026-10-22) : entre crochets, **en
  anglais même dans le texte français**, placées juste avant ce qu'elles colorent : `[softly]`, `[quietly]`,
  `[whispers]`, `[sighs]`, `[chuckles]`, `[laughs]`, `[cheeky]`, `[awe]`, `[happily]`, `[excited]`, `[pause]`.
  Les « … » et les retours à la ligne font aussi des pauses, et les MAJUSCULES appuient un mot.
  ⚠️ **Modèle v3 ou v4 obligatoire** (les MP3 d'octobre portent « v4 », c'est bon) : avec un autre modèle,
  les crochets sont LUS à voix haute. Stabilité « Creative » ou « Natural », pas « Robust », qui écrase les
  balises. Si une balise est prononcée, la retirer et régénérer.
- **Une prise par voix et par langue**, en collant les blocs tels quels (les lignes vides font les
  respirations, les « … » les silences). Déposer dans `_partage/ma lettre/voix/` :
  `minuit-fr-koffi.mp3`, `minuit-fr-narratrice.mp3`, `minuit-en-koffi.mp3`, `minuit-en-narratrice.mp3`.
  Je découpe et je place chaque phrase, et je cale l'image dessus.

## Français

**Voix 1 · Koffi** (texte à coller)

```
[quietly] Dans trois secondes… [pause] [softly] ma mère va pleurer.

[softly] Elle a soixante ans ce soir. [sighs] Moi… je suis à Paris.

[quietly] Alors je lui ai écrit une lettre… [pause] [whispers] qui ne s'ouvre qu'à minuit pile.

[softly] Maman… [pause] [chuckles] tu me réveillais à cinq heures… pour réviser le bac…
```

**Voix 2 · la narratrice** (texte à coller)

```
[happily] Ça, c'est Ma lettre à…

[softly] Une lettre scellée… qui s'ouvre à l'heure que TU choisis.

[cheeky] Et avant l'heure ? [pause] Impossible de l'ouvrir. [chuckles] Même en insistant.

[excited] Tu l'écris… ou la plume l'écrit avec toi, à partir de tes souvenirs.

[awe] La cire, le sceau, le papier, ta photo… et une pluie d'étoiles à l'ouverture.

[softly] Pour la Saint-Valentin… [whispers] à minuit pile, avant tout le monde.

[cheeky] Pour t'excuser… [pause] sans qu'on te raccroche au nez. [chuckles]

[softly] Pour une demande… quand la voix tremble.

[cheeky] Ou la soirée entre potes : l'heure, le lieu… [pause] et qui ramène les boissons. [laughs]

[excited] Ma lettre à… Dès mille francs.

[happily] Tape un prénom : ta lettre commence.
```

## Le film, moment par moment (le plan d'avant les voix)

> ✅ **Rendu le 2026-10-22** sur les voix de Mongazi : le film suit ces textes, mais il dure **56 s** (la parole seule
> en fait 41). Le minutage réel est dans `minutage.json`, le déroulé final dans `_studio-video/README.md`
> § « Minuit pile ».

| Temps | Voix | À l'écran, et l'animation propre au moment |
|---|---|---|
| 0:00-0:03 | K : Dans trois secondes… ma mère va pleurer. | Cotonou, une chambre noire, un téléphone s'allume : **23:59:57**, qui se fige |
| 0:03-0:09 | K : Elle a soixante ans ce soir. Moi, je suis à Paris. Alors je lui ai écrit une lettre… qui ne s'ouvre qu'à minuit pile. | Retour en arrière : Paris sous la pluie, les mots à la bougie, **le cachet pressé (fumée)**, l'enveloppe qui s'envole et traverse le ciel jusqu'à Cotonou |
| 0:09-0:12 | (silence : tic-tac, cœur) | Le temps repart : 58, 59… |
| 0:12-0:15 | (la musique éclate) | **MINUIT** : la cire s'embrase, gerbe de lumière, plongée dans l'écran, **le cachet éclate**, pluie d'étoiles, **la carte sort de l'enveloppe** et monte |
| 0:15-0:19 | K : Maman… tu me réveillais à cinq heures pour réviser le bac… | La lettre se déplie, l'encre sèche ; la ligne lue s'allume, « je voulais être le premier… dès minuit » brille |
| 0:19-0:21 | N : Ça, c'est Ma lettre à… | **Le cachet se change en monogramme d'or embossé** (la marque) |
| 0:21-0:24 | N : Une lettre scellée, qui s'ouvre à l'heure que tu choisis. | Une horloge dont l'aiguille se pose sur l'heure choisie ; le cadran devient le cachet |
| 0:24-0:27 | N : Et avant l'heure ? Impossible de l'ouvrir. Même en insistant. | Un doigt tapote le cachet, qui dit non (il tremble, résiste) ; le compte à rebours, imperturbable |
| 0:27-0:30 | N : Tu l'écris… ou la plume l'écrit avec toi, à partir de tes souvenirs. | Les puces de la fiche se cochent, la plume écrit toute seule, l'encre court |
| 0:30-0:32 | N : La cire, le sceau, le papier, ta photo… et une pluie d'étoiles. | L'enveloppe change d'habit à chaque mot (5 cires, 4 sceaux, 4 papiers), une photo glisse dedans, les trois pluies éclatent |
| 0:32-0:34 | N : Pour la Saint-Valentin… à minuit pile, avant tout le monde. | Cire rose, sceau cœur ; 00:00, les pétales |
| 0:34-0:36 | N : Pour t'excuser… sans qu'on te raccroche au nez. | Un appel « raccroché » (rouge), puis la lettre glisse sous la porte, cire de nuit |
| 0:36-0:38 | N : Pour une demande… quand la voix tremble. | Les alliances, la lettre qui finit sur la question seule ; le texte tremble puis se pose |
| 0:38-0:40 | N : Ou la soirée entre potes : l'heure, le lieu… et qui ramène les boissons. | Papier kraft, confettis ; une liste qui se coche : l'heure ✓, le lieu ✓, les boissons… ? |
| en fond | | Les autres occasions défilent dans le ciel (Tabaski, Noël, Nouvel an, Fête des pères, Naissance, Réussite, Retraite…) |
| 0:40-0:44 | N : Ma lettre à… Dès mille francs. Tape un prénom : ta lettre commence. | Le champ du site, « maman » tapé lettre à lettre → « Ma lettre à maman », **Dès 1 000 F**, l'adresse, by NEBULA Agency, le cachet frappé sur la carte finale |

## English

**Voice 1 · Koffi** (text to paste)

```
[quietly] In three seconds… [pause] [softly] my mother is going to cry.

[softly] She turns sixty tonight. [sighs] And I'm… in Paris.

[quietly] So I wrote her a letter… [pause] [whispers] that only opens at midnight, on the dot.

[softly] Mum… [pause] [chuckles] I still think of those mornings when you woke me at five to revise…
```

**Voice 2 · the narrator** (text to paste)

```
[happily] This is Ma lettre à…

[softly] A sealed letter… that opens at the moment YOU choose.

[cheeky] And before the time? [pause] It won't open. [chuckles] No matter how hard they try.

[excited] Write it yourself… or let the Quill write it with you, from your memories.

[awe] The wax, the seal, the paper, your photo… and a shower of stars when it opens.

[softly] For Valentine's Day… [whispers] at midnight, before anyone else.

[cheeky] To say sorry… [pause] without getting hung up on. [chuckles]

[softly] For a proposal… when your voice shakes.

[cheeky] Or the party with your friends: the time, the place… [pause] and who's bringing the drinks. [laughs]

[excited] Ma lettre à… From one thousand francs.

[happily] Type a name: your letter begins.
```

## Variante sans la plume (si la vidéo sort avant qu'elle soit rouverte)

Remplacer la ligne de la plume par : `[softly] Tu l'écris avec tes mots… [pause] et on l'ouvre avec le cœur.`
(EN : `[softly] You write it in your own words… [pause] and they open it with their heart.`)

## La musique : à choisir sur Pixabay

> ✅ **Choisies par Mongazi** (deux morceaux) : « Emotional piano » de nastelbom (n° 598096) et « Afrobeat music loop,
> positive vibes » de sonican (n° 481253), lus dans `_partage/`.

Le film change d'humeur à 0:19 : **l'émotion** (l'histoire), puis **l'élan joyeux** (la vente, l'humour). Deux
façons de faire :

1. **Un seul morceau** qui monte : début au piano, retenu, puis une montée qui éclate et reste lumineuse et
   entraînante. Mots à taper : `emotional uplifting cinematic`, `inspiring piano build`, `heartfelt uplifting`.
2. **Deux morceaux** : un piano émotionnel pour 0:00-0:19 (`emotional piano cinematic`, `sentimental piano`),
   et un morceau joyeux, léger, rythmé pour 0:19-0:44 (`happy acoustic upbeat`, `feel good uplifting`,
   `afrobeat light instrumental` si tu veux une couleur d'ici, sans voix).

- **Tempo** : lent pour l'émotion (60 à 80 BPM), plus vif pour la suite (100 à 120 BPM).
- **À éviter** : les voix et paroles, la batterie lourde, les « drops » électroniques, ce qui couvre la voix.
- ⚠️ Éviter les morceaux déclarés à **Content ID** (réclamation sur YouTube).
- **Déposer** dans `_partage/ma lettre/musique/`, avec le lien Pixabay de chaque morceau (pour le crédit).
