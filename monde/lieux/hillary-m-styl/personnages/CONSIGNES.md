# Les visiteuses · les consignes exactes de leurs images

> Les premières images (2026-11-12, matin) ont été faites sans garder leurs
> consignes. Celles-ci sont gardées mot pour mot : une image se refait à
> l'identique, ou se corrige d'une seule ligne.

## LES ÂGES (Mongazi, 2026-11-12 : « on doit appliquer les âges aussi dorénavant »)

Hillary a **26 ans** (un fait). Les visiteuses sont inventées, leurs âges tiennent
leurs répliques :

| Qui | Âge | Pourquoi ce chiffre |
|---|---|---|
| **Hillary** | **26 ans** | dit par Mongazi |
| **Afi** | **29 ans** | « J'ai grandi à Akpakpa, ça fait dix ans que je suis partie » : partie à 19 ans, pour ses études à Paris |
| **Sènami** | **21 ans** | fan du TikTok d'Hillary, étudiante ; **une adulte, pas une adolescente** |
| **Maman Sènami** | **47 ans** | mère d'une fille de 21 ans ; **pas une grand-mère** |

⚠️ **Le piège** : les générateurs vieillissent les mères et rajeunissent les filles.
La première Maman Sènami faisait 60-65 ans, la première Sènami 16-17. Chaque
consigne dit donc l'âge **et** ce qu'il ne faut pas montrer (rides profondes,
cheveux gris, visage d'adolescente).

## Les règles communes (les mêmes que B1 pour Hillary)

Vue de face en pied, pose A pour Mixamo, fond gris clair uni, pas d'ombre portée,
rien dans les mains (le téléphone et le sac sont ajoutés dans le salon).

## Sènami, 21 ans

```
Full body front view of a 21-year-old Beninese woman, clearly a young adult university student, not a teenager: adult face and adult body proportions. Photorealistic 3D video game character reference. Light brown skin, natural, no skin lightening. Height 1.64 m, slim build. Long box braids gathered up in a high bun, small gold hoop earrings. Cropped short-sleeve top in colorful wax print fabric, high-waisted blue jeans, white sneakers. Pose for 3D rigging: A-pose, arms straight and held 45 degrees away from the body, palms facing down, fingers slightly spread and visible, legs straight and slightly apart, feet flat on the ground and visible. Neutral face, mouth closed, eyes open looking straight ahead. Nothing in the hands, no bag, no phone. Plain light grey background, soft even studio lighting, no cast shadows, orthographic-like camera, the whole body visible from head to feet, centered, sharp focus.
```

## Maman Sènami, 47 ans

```
Full body front view of a 47-year-old Beninese woman who looks her age and no older: a youthful mature face, smooth skin with only faint smile lines, no deep wrinkles, no grey hair, elegant and dignified. Photorealistic 3D video game character reference. Very dark brown skin, natural, no skin lightening. Height 1.62 m, average build. Long boubou dress in green and yellow wax print fabric with a matching gele head wrap, gold bracelets, brown leather sandals. Pose for 3D rigging: A-pose, arms straight and held 45 degrees away from the body, palms facing down, fingers slightly spread and visible, legs straight and slightly apart, feet flat on the ground and visible. Neutral face, mouth closed, eyes open looking straight ahead. Nothing in the hands, no bag. Plain light grey background, soft even studio lighting, no cast shadows, orthographic-like camera, the whole body visible from head to feet, centered, sharp focus.
```

Commande : `python scripts/image_cf.py "<consigne>" --modele flux-2-dev --largeur 1024 --hauteur 1024 --sortie <fichier>.jpg`
