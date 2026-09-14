# Fabriquer un post NEBULA à partir d'une référence trouvée ailleurs

*2026-09-14. Né du post 18 « C'est après le carrefour », fabriqué depuis une
référence Tempos Digital. La méthode vaut pour n'importe quelle image qu'on
trouve belle et dont on veut le savoir-faire sans voler la marque.*

---

## Le principe

**On hérite du MÉTIER, jamais de la MARQUE.** Une référence donne une façon de
composer, de dessiner, d'aérer. Elle ne donne ni son sujet, ni ses mots, ni ses
couleurs. Le prompt-maître de la maison appelle ça `MODE B`, et c'est la seule
chose qui empêche un post NEBULA de sortir aux couleurs de quelqu'un d'autre.

---

## Les six temps, dans l'ordre

### 1. Mesurer la référence, ne jamais l'estimer à l'œil

```python
from PIL import Image
from collections import Counter
im = Image.open("reference.jpg").convert("RGB")
print(im.size, im.size[0] / im.size[1])            # format réel
for rgb, n in Counter(im.resize((216, 270)).getdata()).most_common(5):
    print("#%02X%02X%02X" % rgb, round(100 * n / (216 * 270), 1), "%")
```

Sur la référence Tempos, ça a donné le chiffre qui explique tout le style :
**le fond occupe 80,2 % de la surface**. Ce n'est pas « un fond sombre », c'est
**du vide**, et c'est le vide qui fait le style. À l'œil, on aurait retenu le
personnage et on aurait rempli le cadre.

⚠️ **Le format aussi se mesure.** La référence était en 4:5 ; notre statut
WhatsApp est en 9:16. Reprendre la mise en page sans reprendre le format donne
un dessin écrasé.

### 2. Nommer en UNE phrase ce que la référence fait, et qui est copiable

Pour Tempos : *« un dessin au trait blanc sur du vide noir, une seule couleur
vive, et UN FIL continu de cette couleur qui relie les deux choses dont parle
le post. »*

⚠️ **S'il n'y a pas un mécanisme nommable, il n'y a rien à hériter.** « C'est
joli » ne se transmet pas à un modèle. « Un fil continu qui relie A à B » se
transmet, et c'est lui qu'on redessinera différemment à chaque post.

### 3. Choisir la couleur d'accent PAR LE CONTRASTE, pas au goût

C'est le temps que tout le monde saute, et c'est celui qui décide si le post se
voit dehors.

```python
def lum(h):
    h = h.lstrip("#"); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in c]
    return .2126*c[0] + .7152*c[1] + .0722*c[2]
def ratio(a, b):
    la, lb = lum(a), lum(b); return (max(la,lb)+.05) / (min(la,lb)+.05)
```

Mesuré le 2026-09-14, sur le fond NEBULA `#070A14` :

| couleur | contraste |
|---|---|
| **cyan `#3FD8E6`** | **11,46:1** |
| ambre `#F6A63C` | 9,82:1 |
| bleu `#4A7DFF` | 5,33:1 |
| violet `#9B5CFF` | 5,05:1 |
| *(le vert de Tempos sur SON fond)* | *14,85:1* |

Le violet est pourtant la couleur « primaire » de la marque. **Il aurait fait un
post illisible** : un statut WhatsApp se regarde **dehors, écran à moitié
éteint**. On prend donc celle qui s'approche le plus du punch de la référence,
et ici c'est le **cyan**. La marque décide de la palette, la mesure décide
laquelle on prend dedans.

### 4. Refuser la couleur de la référence EN TOUTES LETTRES

⛔ **C'est le piège numéro un.** La couleur de la référence est la chose la plus
saillante de l'image jointe : le modèle la reprend tout seul, et le post sort aux
couleurs du concurrent.

Il ne suffit pas de nommer la nôtre. Il faut écrire le refus :

```
There is NO green anywhere in this image. Not one pixel.
```

### 5. Ordre des pièces jointes : LE LOGO D'ABORD

Inversés, le modèle traite le logo comme un modèle de style et **la marque
disparaît**. Règle déjà écrite dans le prompt-maître, elle vaut d'être répétée à
chaque envoi parce qu'elle ne se voit pas quand elle est violée : le post sort
beau, simplement il n'est pas de nous.

### 6. Garder l'ancre de série, changer tout le reste

Le label « LE SAVIEZ-VOUS ? » ne bouge jamais : ni le texte, ni la place, ni la
casse, ni la taille. **C'est la répétition d'une position qui fait une série**,
pas la beauté d'un post.

---

## Ce qui décide du SUJET, et c'est là que se gagne la valeur

Une belle image sur un sujet tiède ne sert à rien. Trois critères, et les trois
ensemble :

1. **C'est vrai, et c'est vérifiable sans chiffre.** ⛔ Aucune statistique
   inventée, jamais. Le post 18 repose sur « au Bénin, une adresse est un repère,
   pas une rue » : personne ne peut le contester, et **aucun nombre n'est avancé**.
2. **Ça nous appartient.** Un sujet local que les modèles étrangers ne
   connaissent pas vaut mieux qu'une vérité générale sur le digital. C'est la
   « valeur différente » : elle vient du terrain, pas du prompt.
3. **L'émotion arrive en DEUX temps.** On rit à l'accroche, on comprend au corps
   de texte. Post 18 : on rit de « C'EST APRÈS LE CARREFOUR LÀÀÀÀÀ… », puis
   « celui qui se perd ne vous rappelle pas » fait le vertige. Une seule des deux
   moitiés, et le post est soit une blague, soit un reproche.

⚠️ **Et la règle qui prime sur tout : on ne se moque JAMAIS du commerçant.** Le
personnage qui galère, c'est nous tous, et le dessin est de son côté. Un post qui
rit **du** client ferme la porte que toute la rubrique essaie d'ouvrir.

⚠️ **Le sujet le plus fort est souvent celui dont on ne peut PAS donner le
chiffre.** Post 18 parle de clients perdus que personne n'a jamais comptés :
écrire « vous perdez 3 clients par semaine » aurait détruit la seule chose que ce
post a de vrai.

---

## Où ça vit

- La direction artistique complète, ses 8 marqueurs et ses 3 pièges :
  `_documents/nebula-agency/marketing/PROMPTS-POSTS-LE-SAVIEZ-VOUS.md` **§10**
- Le post 18 et sa légende : le **§11** du même fichier
- Le prompt prêt à coller : `marketing/PROMPT-DU-JOUR-CARREFOUR.txt`
- La référence mesurée : `marketing/references/REF-trait-et-nuit.jpg`
- Le logo à joindre en premier : `nebula-affilies/static/nebula-logo.png`

**Pour un nouveau post dans cette direction**, on ne touche qu'au bloc `CONTENT`
du prompt et à la description de la scène. Tout le reste, y compris le verrou de
marque et le refus du vert, se recopie tel quel.
