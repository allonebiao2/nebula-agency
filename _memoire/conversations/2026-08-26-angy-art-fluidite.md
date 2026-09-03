# Angy Art — le site était vert à 150 contrôles et tournait à quinze images par seconde

*2026-08-26. Client 11. Demande de Mongazi : « vérifie les erreurs sur la
vitrine d'Angy Art, analyse en profondeur et fluidifie tout ».*

---

## Le point de départ, et pourquoi il faut le dire

`python _qc.py` : **150 contrôles verts, 0 en échec.** Le site est juste.

Et pendant ce temps, sur un processeur ralenti six fois (un téléphone d'entrée
de gamme de Cotonou) :

| | avant |
|---|---|
| écart médian entre deux images, ordinateur | **66,7 ms** — quinze images par seconde |
| 95e centile | 183,4 ms |
| images perdues | **85 %** |
| la pire tâche, pendant laquelle la page ne répond plus | **1 557 ms** |

⚠️ **Un QC vert dit que rien n'est cassé. Il ne dit pas que ça glisse.** C'est
la même leçon que le 2026-08-01 (« une vitrine n'est pas finie quand elle
marche »), mesurée cette fois au lieu d'être regardée.

## Le coupable : un calque de grain, invisible et ruineux

`body::after` : `position:fixed`, `inset:-30%` (donc 2,5 fois la surface de la
fenêtre), une texture de bruit, `opacity:.05`, **`mix-blend-mode:overlay`**.

Ce qu'il coûtait, en éteignant un mécanisme à la fois (`_attribuer.py`) :

```
tel quel                                 66,7 ms
sans le grain plein ecran                16,8 ms   (-75 %)
sans le pointeur fin (moteur + curseur)  66,6 ms   ( -0 %)
sans le parallaxe                        66,7 ms   ( -0 %)
sans le flou du carrousel                66,6 ms   ( -0 %)
```

Ce qu'il apportait, mesuré aussi (`_grain_visuel.py`) : **0,90/255 d'écart
moyen** sur le héros, **0,46/255** en milieu de page. Deux morceaux agrandis
trois fois et posés côte à côte sont **indiscernables**.

### ⚠️ Trois précisions qui font toute la valeur du diagnostic

**Ce n'est pas l'image de bruit qui coûte, c'est le MÉLANGE.** Retirer
`background-image` ne change rien ; passer `mix-blend-mode` à `normal` rapporte
autant que supprimer le calque entier. Un calque `fixed` qui couvre la fenêtre
et qui se mélange oblige le navigateur à **recomposer tout l'écran à chaque
image**, au lieu de faire glisser un calque déjà peint.

**Aucun remède de compositing ne le sauve.** `will-change:opacity`,
`transform:translateZ(0)`, `contain:strict`, `isolation:isolate` : quatre
remèdes, trois mesures chacun, tous à 50 ms comme sans remède. On ne garde pas
un mélange plein écran en le « promouvant ».

⛔ **Et mon premier neutralisant mentait** : `*{mix-blend-mode:normal}` ne
touche **pas** les pseudo-éléments. La première passe concluait donc « le
mélange ne coûte rien » alors qu'elle n'avait jamais atteint `body::after`.

## Le reste, trouvé en cherchant

⛔ **`marque.png` : 199 Ko pour être affiché en 57 × 44 px.** Le logo des
pages. Sur une 3G, il était demandé **en deuxième position, à 2 298 ms**, juste
derrière le héros. Deux mille trois cents fois plus de données que de pixels.
→ `marque.webp`, 284 × 220, **9,7 Ko**. ⚠️ `marque.png` **reste** : l'affiche
A4 l'imprime, la vignette de partage et les favicons se composent à partir
d'elle. Deux fichiers, deux métiers.

⛔ **`og.png` : 566 Ko, en PNG.** La règle de la maison est « en JPEG » : c'est
la première impression quand le lien circule sur WhatsApp au Bénin, et **le
défaut le plus cher parce qu'il est invisible depuis le site**.
→ `og.jpg`, qualité 84, **96 Ko** (−83 %).

⚠️ **Deux passes de lecture/écriture entremêlées.** Les deux balayages du
défilement faisaient `getBoundingClientRect()` puis `classList.add()` **dans la
même boucle** : chaque classe posée invalide la mise en page, donc la lecture
suivante force un recalcul complet. Au premier écran il reste une centaine
d'éléments : jusqu'à cent recalculs dans une seule image, exactement quand le
visiteur commence à défiler. On lit tout, **puis** on écrit tout.

⚠️ **« TikTok » mesurait 39 × 44.** La hauteur était réservée (`min-height:44px`),
la largeur non. Une cible se mesure dans les **deux** sens.

⛔ **La barre du haut était à 92 % d'opacité, et on lisait au travers.** Vu sur
une capture du pied de page : la phrase qui passait dessous restait lisible en
filigrane derrière le menu. La règle de Mon Bénin dit qu'une **bande de bord**
a le droit de recouvrir du texte — c'est la seule chose qui l'ait — **mais à
condition d'être vraiment opaque**. Huit pour cent de transparence sans
`backdrop-filter` ne font pas un effet de verre, ils font un fantôme.
→ `background: var(--noir)`, et un contrôle qui **photographie** la bande à
deux hauteurs de défilement différentes : opaque, les deux images sont
identiques. Mesuré après correction : **0/255**.

⚠️ **`/assets/*` est en cache un an, `immutable`.** `app.css` et `app.js` ont
changé sans changer de nom : sans bump du `?v=`, un visiteur déjà venu aurait
gardé la version qui rame pendant un an. 27 marques bumpées.

## ⛔ ET TROIS DE MES PROPRES CONTRÔLES MENTAIENT

C'est la partie qu'il faut retenir, parce qu'elle a failli coûter une journée.

**1. « Le premier écran télécharge 1 920 Ko »** — mesuré sur `localhost`, où la
bande passante est infinie. Or **le seuil de `loading="lazy"` de Chrome grandit
avec la vitesse de la connexion** : en local il chargeait les six photos du
carrousel situées à 3 500 px du haut. **Sur une vraie 3G, les mêmes secondes ne
téléchargent que 794 Ko et le carrousel ne bouge pas.** Le différé fonctionne.
J'ai failli réécrire tout le carrousel pour un défaut qui n'existait pas.
→ le contrôle mesure désormais **sur une 3G émulée**, jamais en local.

**2. « Ce n'est pas un vrai `<dialog>` »** — ma sonde prenait « le premier
bouton dont le texte parle de demande » et tombait sur un bouton qui fait
DÉFILER vers une section. Aucune modale ne s'ouvrait, et le contrôle suivant,
« Échap referme la modale », passait **dans le vide**. Il y a bien trois vrais
`<dialog>`. → on vise `[data-modale]`, et on ne teste la fermeture que si
quelque chose s'était ouvert.

**3. « Le lien NEBULA Agency fait 89 × 15 »** — c'est un lien **dans une
phrase** (« Site conçu par … , Cotonou »), et la règle des 44 px l'exempte
explicitement. Un contrôle qui crie au loup finit par ne plus être lu.

**4. « La barre n'est pas opaque : 233/255 »** — sur une barre parfaitement
opaque. Le test tournait sur la page **bridée en 3G** : entre les deux photos,
la police du menu finissait de charger et le texte de la barre se redessinait.
Ce n'était pas le fond que je mesurais, c'était un changement de police.
→ page neuve, sans bridage, après `document.fonts.ready`. Résultat : **0/255**.

**5. « Le premier écran pèse 753 Ko »… puis 242, puis 210.** Le contrôle
sommait « tout ce qui est arrivé en neuf secondes » : selon que le différé
avait eu le temps de démarrer, le même site donnait trois réponses. → il
compte désormais **le chemin critique** : les octets reçus **avant que l'image
du héros soit décodée**. Deux exécutions de suite : **244 Ko**, au kilo-octet
près.

⚠️ Cinq sondes fausses ici, trois sur le Braisé d'Or le même jour.
**Avant d'annoncer un défaut : « et si c'était ma mesure ? »** Et le signe qui
ne trompe pas : un contrôle qui donne trois réponses différentes sur un site
qui n'a pas bougé mesure autre chose que ce qu'il croit.

## Le résultat

Tout ci-dessous est mesuré **processeur ralenti ×6**, c'est-à-dire sur un
téléphone d'entrée de gamme, pas sur cette machine.

| ordinateur 1440 | avant | grain retiré | + lecture/écriture séparées |
|---|---|---|---|
| écart médian | 66,7 ms | 33,3 ms | **16,7 ms — 60 i/s** |
| 95e centile | 183,4 ms | 50,1 ms | **49,9 ms** |
| images perdues | 85 % | 54 % | **27 %** |
| tâches longues | 32, la pire à **1 557 ms** | 12, la pire à 73 ms | **1**, la pire à 137 ms |

| téléphone 390 | avant | après |
|---|---|---|
| écart médian | 16,7 ms | 16,7 ms |
| 95e centile | 49,9 ms | **16,8 ms** |
| pire image | 233,3 ms | **33,4 ms** |
| images perdues | 13,2 % | **5,0 %** |
| tâches longues | 6, la pire à 215 ms | **0** |

| poids | avant | après |
|---|---|---|
| premier écran sur 3G | 794 Ko | **242 Ko** |
| vignette de partage | 566 Ko PNG | **96 Ko JPEG** |
| logo des pages | 199 Ko | **9,7 Ko** |

`_qc.py` reste à **150 verts**. Nouveaux instruments, gardés dans le dossier du
client : `_fluidite.py` (le site se chronomètre lui-même), `_attribuer.py`
(éteindre un mécanisme à la fois), `_audit.py` (**22 contrôles** sur ce que le
QC ne regarde pas).

## ⏳ Ce qui n'est PAS réglé, et qu'il faut dire

**Une tâche longue intermittente au tout bas de la page.** Sur le site en
ligne, téléphone, processeur ×6 : **815 ms une fois sur trois**, vers
y ≈ 11 700, là où entrent la citation et la section « Demander une visite »
avec `visite.webp` (148 Ko). Les deux autres essais donnent 173 ms et 100 ms.
Ce n'est pas reproductible, c'est en bas de page, et la médiane reste à
16,7 ms avec 5 % d'images perdues : je ne l'ai pas chassée plus loin.

**Le levier identifié, pas encore tiré : `srcset`.** Un seul fichier sert le
téléphone et l'ordinateur, donc il est dimensionné pour le plus grand. Mesuré
sur le site en ligne : `temps-1..4` font 780 px de large pour **326 px
d'affichage réel** sur un téléphone (×2,4), `ames-soeurs` 1 536 px pour 700
(×2,2). ⚠️ **Attention à la mesure** : les cartes du carrousel sont mises à
l'échelle (`scale(.45)` à `.6`) quand elles ne sont pas actives, donc un
rapport « ×4,9 » sur `situ-3` mesure une carte réduite, pas un vrai
surdimensionnement. La vraie économie est sur les images fixes des sections.
