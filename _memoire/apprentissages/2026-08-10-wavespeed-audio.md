# WaveSpeed — générer des ambiances sonores

*Vérifié le 2026-08-10, sur les huit ambiances de Mon Bénin.*

## Oui, WaveSpeed fait de l'audio

**342 modèles audio sur 979.** Même clé que pour les images
(`secrets/wavespeed.env`), même solde.

## Le bon modèle pour une ambiance : Mirelo SFX 1.6

```
POST https://api.wavespeed.ai/api/v3/mirelo-ai/sfx-1.6/text-to-audio
{
  "text_prompt": "...",     obligatoire, 4 caractères minimum
  "duration": 8,            0,1 à 60 secondes
  "ambience": true,         ⚠️ LE point : recolle la fin sur le début
  "num_samples": 1          1 à 4 variantes
}
```

Puis on interroge `/api/v3/predictions/<id>/result` jusqu'à `completed`, et on
télécharge `outputs[0]`.

**Prix : 0,01 $ la seconde** (`base_price × duration × num_samples`).
Huit ambiances de 8 s = **0,64 $**.

**`ambience: true` est la raison de choisir ce modèle.** Une ambiance qui claque
toutes les huit secondes est pire que pas d'ambiance du tout.

### Les autres, pour mémoire

| Modèle | Prix | Pour quoi |
|---|---|---|
| `sonilo/v1/text-to-sfx` | 0,002 $/s | moins cher, **aucune garantie de boucle** |
| `sonilo/text-to-music` | 0,0025 $/s | de la musique |
| `wavespeed-ai/ace-step/prompt-to-audio` | 0,0002 $/s | musique, très bon marché |
| `kwaivgi/kling-text-to-audio` | 0,035 | effets pour vidéo |
| `bytedance/seed-audio-1.0` | 0,3 | voix parlée |

## Écrire le texte

En **anglais**, le modèle est entraîné dessus. Et surtout : **exclure
explicitement** ce qu'on ne veut pas, sinon il ajoute des voix ou une nappe
musicale.

```
Calm shallow lake water lapping against wooden stilts, a single wooden paddle
dipping slowly, faint creaking wood. No voices, no music.
```

## Les trois contrôles obligatoires

**1. Sont-ils vraiment différents ?** Huit MP3 à débit constant et durée égale
pèsent **exactement pareil** : la taille ne prouve rien. Comparer les **MD5** et
un **profil spectral par bandes** (l'énergie haute fréquence, approchée par la
moyenne des différences entre échantillons successifs). Bon signe : les profils
correspondent aux textes. Chez nous, la Pendjari saturait d'aigus à cause des
cicadas, le Koutammakou était à 49 % de silence.

**2. La boucle est-elle sans couture ?** Comparer la moyenne des **40 premières
millisecondes** à celle des **40 dernières**. Sous 35 % d'écart, c'est propre.
Mesuré : **7,9 %**.

**3. Les niveaux.** Bruts, l'écart entre deux ambiances atteignait un **facteur
15** : le voyage serait passé du quasi-silence au fort. Normaliser :

```
ffmpeg -i brut.mp3 -af "loudnorm=I=-20:TP=-2:LRA=11" -ac 1 -ar 32000 -b:a 48k final.mp3
```

`-20 LUFS` parce que c'est une ambiance de fond, pas une bande-son. Après :
écart ramené à **1,9**, caractère de chacun préservé.

⚠️ **Garder les originaux.** Une régénération coûte de l'argent.

## Côté navigateur

Pour une boucle vraiment sans trou : `fetch` → `decodeAudioData` →
`AudioBufferSourceNode` avec `loop = true`. **Pas un élément `<audio>`**, qui
laisse un micro-trou sur certains navigateurs.

Fondu croisé entre deux lieux : deux `GainNode`, `setTargetAtTime`.

**Le poids décide l'architecture.** 380 Ko de son sur une page de 231 Ko : ils ne
doivent **jamais** être chargés d'avance. Seul le lieu où l'on se trouve
télécharge le sien, et seulement si le son est allumé. À vérifier en écoutant
les requêtes réelles, pas en lisant le code.

## La ligne à ne pas franchir

**Un son généré est une MATIÈRE, pas un document.** Une ambiance fabriquée et
présentée comme « le bruit de Ganvié » est exactement le même mensonge qu'une
photo générée du lieu. Ça s'écrit dans les crédits du site, et un contrôle
vérifie que la phrase est là.
