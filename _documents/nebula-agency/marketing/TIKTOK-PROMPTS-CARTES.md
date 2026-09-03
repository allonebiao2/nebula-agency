# TikTok « OUI / NON » · les cartes de question, fond noir

Deux façons de les fabriquer. **Lisez d'abord le paragraphe suivant**, il évite
de dépenser quatre dollars pour des fautes d'orthographe.

---

## ⚠️ Avant de générer quoi que ce soit

Ces cartes sont **du texte blanc sur du noir**. Un modèle d'image, même le
meilleur, reste une machine à dessiner : il redessine les lettres au lieu de les
écrire. En français il rate régulièrement les accents (« déjà » devient
« deja », « à » devient « a »), il coupe les mots au mauvais endroit, et il
n'accepte pas la correction : une virgule à changer et il faut tout regénérer,
et payer de nouveau.

| | Générateur `_cartes.py` | Modèle d'image |
|---|---|---|
| Texte | **exact, au caractère** | à vérifier à chaque tirage |
| Prix | **0 F** | 0,14 $ la carte, soit ~3,60 $ les 26 |
| Corriger un mot | on relance, 2 secondes | on repaie |
| Format 1080×1920 | **garanti** | à recadrer |

**Servez-vous du générateur pour les questions.** Gardez le modèle d'image pour
ce qu'il fait mieux que nous : une **texture de fond** (une seule image, réutilisée
sous les 26 cartes), ou une carte d'ouverture illustrée.

```bash
python _documents/nebula-agency/marketing/_cartes.py
```

Les cartes tombent dans `_documents/nebula-agency/marketing/tiktok/`, prêtes à
glisser dans CapCut.

---

## Si vous voulez quand même les générer

Méthode : **un socle commun, une seule phrase qui change**. C'est ce qui donne
une série au lieu d'une collection d'images qui ne se ressemblent pas.

### Le socle (à recopier devant chaque question)

```
Vertical 9:16 social media title card, 1080x1920. Pure black background (#000000),
completely plain, no objects, no people, no decoration. A single line of text
centred both horizontally and vertically, in pure white, heavy geometric sans-serif,
large, generous letter spacing, wide margins on both sides. Subtle fine film grain
over the black. Nothing else in the frame: no logo, no watermark, no signature,
no border, no frame, no UI elements, no emoji, no additional text of any kind.
The text must read exactly, with French accents preserved:
```

### Puis la phrase de la question, entre guillemets

⚠️ **Relire chaque image reçue, lettre par lettre**, avant de la monter.

---

## SCRIPT 1 · LE PRIX

```
… socle … "Il faut 500 000 F pour avoir un site ?"
… socle … "Il faut attendre trois mois ?"
… socle … "Il faut savoir se servir d'un ordinateur ?"
… socle … "Donc n'importe qui peut en avoir un ?"
… socle … "Il faut payer quelque chose tous les mois ?"
… socle … "Vous avez déjà livré en retard ?"
… socle … "Vous l'avez dit au client avant ?"
… socle … "Vos clients sont de vrais commerçants d'ici ?"
… socle … "Je peux vous écrire maintenant ?"
```

## SCRIPT 2 · JE N'AI PAS BESOIN DE SITE

```
… socle … "J'ai déjà WhatsApp. J'ai besoin d'un site ?"
… socle … "J'ai déjà une page Facebook. J'ai besoin d'un site ?"
… socle … "Donc un site ne sert à rien ?"
… socle … "Vous répétez vingt fois par jour les mêmes prix ?"
… socle … "Vous renvoyez la même photo dix fois par jour ?"
… socle … "Ça, un lien peut le faire à votre place ?"
… socle … "Et ça coûte moins qu'un carton de marchandise ?"
… socle … "Vous voulez le lien ?"
```

## SCRIPT 3 · LE LOGICIEL MÉTIER

```
… socle … "Vous faites des sites web ?"
… socle … "C'est votre métier principal ?"
… socle … "Vous faites des logiciels ?"
… socle … "Pour les grandes entreprises ?"
… socle … "Pour une vendeuse de tissu au marché ?"
… socle … "Elle a besoin d'un ordinateur ?"
… socle … "Le logiciel lui dit ce qu'elle gagne vraiment ?"
… socle … "Elle le savait avant ?"
```

## La carte de fin

```
… socle … "NEBULA Agency · Cotonou" on the first line and
"Le lien est dans la bio" on a second line, smaller, in warm grey.
```

---

## Le seul endroit où le modèle d'image vaut vraiment son prix

**Une texture de fond, générée UNE fois**, posée sous les 26 cartes. Elle donne
à la série une matière que le noir plat n'a pas, pour 0,14 $ au total.

```
Vertical 9:16 abstract background, 1080x1920. Deep near-black surface, almost
uniform, with a very faint uneven texture like unlit black paper or matte studio
backdrop. An extremely subtle warm light falloff in the upper third, barely
visible. Fine photographic film grain throughout. No objects, no people, no text,
no logo, no watermark, no pattern, no gradient banding. Dark, quiet, cinematic.
```

Puis dans `_cartes.py`, indiquer le fichier obtenu :

```bash
python _cartes.py --fond mon-fond.png
```

---

*NEBULA Agency · Cotonou · écrit le 2026-08-07*
