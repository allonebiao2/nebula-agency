# Générer des images par API : WaveSpeed + Nano Banana Pro

*Appris le 2026-08-05 en produisant les 13 visuels d'Angy Art (client 11).*

## Ce que c'est, et pourquoi c'est mieux que le navigateur

**WaveSpeed** revend l'accès à presque tous les modèles d'image et de vidéo par une
seule API et un seul solde. On paie à l'image, sans abonnement, sans carte à laisser
sur dix plateformes. **961 modèles** disponibles au 2026-08-05.

La clé vit dans `secrets/wavespeed.env`. ⚠️ **Le dépôt est public** : jamais ailleurs.

```bash
curl -s -H "Authorization: Bearer $WAVESPEED_API_KEY" \
     https://api.wavespeed.ai/api/v3/balance
```

## Les modèles qui comptent, et leur prix

| Modèle | Prix / image | Pour quoi |
|---|---|---|
| `google/nano-banana-pro/text-to-image` | **0,14 $** | le meilleur. Photoréalisme, lumière, matière |
| `google/nano-banana-pro/text-to-image-ultra` | 0,15 $ | idem en 4K |
| `google/nano-banana-2/text-to-image` | 0,07 $ | moitié prix, un cran en dessous |
| `google/nano-banana/text-to-image` | 0,038 $ | l'ancien, correct pour du remplissage |
| `bytedance/seedream-v5.0-pro` | 0,045 $ | bon second, plus graphique |
| `google/imagen4-fast` | 0,018 $ | le moins cher qui tienne debout |

Il existe aussi `/edit` sur chacun (retoucher une image existante) et toute la vidéo.

## L'appel, en trois temps

```python
# 1. on poste
POST https://api.wavespeed.ai/api/v3/google/nano-banana-pro/text-to-image
{"prompt": "...", "aspect_ratio": "4:5", "resolution": "2k"}
# 2. on relit toutes les 3 s
GET https://api.wavespeed.ai/api/v3/predictions/{id}/result
# 3. status == "completed" → data.outputs[0] est une URL à télécharger
```

`aspect_ratio` accepte : `1:1 3:2 2:3 3:4 4:3 4:5 5:4 9:16 16:9 21:9`.
Un rendu prend 15 à 40 s. Compter ~4 min pour dix images.

Script de référence, réutilisable tel quel : `clients/11-angy-art/_gen_images.py`.

## Ce qui fait la différence dans les prompts

**Un socle commun, une variation.** C'est ce qui donne une série au lieu d'une
collection. Chez Angy Art, le socle contenait la lumière (« hard raking light from the
far left at a very low angle »), la palette, et la ligne de négations. Seule une phrase
changeait d'une image à l'autre. Résultat : huit œuvres qui ont l'air photographiées le
même jour par le même photographe.

**Toujours finir par** `No text, no lettering, no signature, no watermark, no logo`.
Sans ça, le modèle invente des lettres, et une fausse signature sur l'œuvre d'une
artiste est une catastrophe.

**Décrire un appareil.** « Shot on a 100mm macro lens, f/5.6 » vaut mieux que
« très détaillé ». Le modèle connaît les optiques.

**Nommer ce qu'on ne veut pas voir dans le cadre** : « hands only, face out of frame »,
« canvases with their backs turned to the camera », « no people ». C'est ce qui permet
de rester honnête (voir plus bas).

## Deux pièges vus en vrai

**Le modèle occidentalise par défaut.** Pour la scène de vernissage d'une artiste
béninoise, il a produit deux fois deux hommes blancs en manteau. Il a fallu écrire
« two West African visitors, a woman in a wax-print dress with a headwrap, dark brown
skin ». À relancer systématiquement : **si le sujet est africain, l'écrire**.

**Les fonds ne sont jamais deux fois les mêmes.** Huit « seamless neutral dark grey
background » ont donné des gris allant du clair au foncé. Un carrousel bariolé.
Remède au tirage plutôt qu'à la génération : un **assombrissement radial** ramène tous
les bords au même noir sans toucher au sujet centré.

```python
m = Image.new("L", (L, H), 0)
ImageDraw.Draw(m).ellipse([L*.02, H*.02, L*.98, H*.98], fill=255)
m = m.filter(ImageFilter.GaussianBlur(min(L, H) * 0.16))
m = m.point(lambda v: 36 + v * 219 // 255)      # les coins gardent 14 %
im = Image.composite(im, Image.new("RGB", (L, H), (10,10,10)), m)
```

Voir `clients/11-angy-art/_pose_images.py`.

## ⛔ La règle qui ne bouge pas

**Une image générée ne devient jamais le catalogue d'un client.** Ambiance, matière,
lieu, texture : autorisé. Une toile présentée comme une œuvre à vendre : jamais.

Chez Angy Art, les 8 visuels du carrousel sont une **préfiguration** : ils portent un
titre et une technique, **aucun prix, aucune dimension, aucune mention « disponible »**,
et le `CONTEXT.md` dit noir sur blanc qu'ils partent à l'arrivée des vraies photos. Un
collectionneur qui écrit pour acheter une pièce qui n'existe pas, c'est l'artiste qui
paie, pas nous.

## Coût réel d'un chantier complet

Angy Art : 20 images générées (dont 2 relances et 10 variantes écartées), **2,80 $**.
Un site entier illustré pour moins de 2 000 F CFA.
