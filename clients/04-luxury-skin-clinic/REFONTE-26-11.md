# LUXURY CLUB 229 · le chantier du 26/11 (refonte 3D + ajouts de la cliente)

Rang 1 de la zone travaux (`_memoire/TRAVAUX.md`). Tout ce qui a été demandé est ici, mot pour mot quand c'est utile,
pour qu'aucune session ne reparte de zéro.

## 1. Ce que Mongazi a demandé (26/11, /vague)
« La refonte de Luxury [Skin Clinic], sa vitrine ENTIÈREMENT en 3D, 3D scrolling adapté à sa vitrine, dans un salon de
beauté bien beau, bien lumineux, intégrer tout ça à l'intérieur. De plus elle veut des ajouts. » À enchaîner tout de
suite après les étiquettes d'Au Braisé d'Or (livrées le 26/11).

## 2. Les ajouts de la cliente (26/11, message transmis par Mongazi)
### 2.1 Cozy rejoint INA Luxury
- Transférer **tous** les produits de Cozy dans la rubrique produits d'**INA Luxury**.
- Ajouter dans INA les catégories de Cozy : **Hygiène intime**, **Produits raffermissants**, et toutes les autres
  catégories de Cozy. Tous les produits doivent être accessibles depuis INA Luxury, sans passer par Cozy.

### 2.2 L'espace Cozy devient la rubrique de son NOUVEAU DOMAINE (sa formation : l'harmonisation faciale)
Même principe que Luxury Skin Clinic (les clientes consultent les soins et leurs tarifs). Elle présente : les nouvelles
prestations, les descriptions des protocoles, les indications, les tarifs, les informations pour comprendre chaque
prestation. **Ses 3 flyers** (dans `assets/harmonisation/`) en sont le contenu, et elle veut leurs VISUELS sur le site
(« là, les gens vont comprendre exactement de quelle zone on parle »).

**Flyer 1 · FACIAL BALANCING** (`flyer-facial-balancing.jpg`) : « Le facial balancing est la combinaison de ces différentes
techniques pour rajeunir votre visage et le rendre plus frais et beau. »
- Zone supérieure (front + cerne) : 500 000 FCFA
- Milieu du visage (pommette + nez) : 1 000 000 FCFA
- Zone inférieure (lèvre, mâchoire, joue et menton) : 800 000 FCFA
- **Genesis Face** (tout le visage) : 2 200 000 FCFA

**Flyer 2 · HARMONISATION FACIALE · GENESIS HOLLYWOOD** (`flyer-genesis-hollywood.jpg`) : « Le Genesis Hollywood est une
technique qui va permettre de relifter votre peau et votre visage, d'affiner votre visage et d'adoucir vos traits, et de
traiter tout ce qui est rides dynamiques. » Zones montrées : Frontalis (rides du front), zone glabellaire (rides de la
concentration).
- Frontalis + zone glabellaire (rides du front et entre les sourcils) : 300 000 FCFA
- Rhinoplastie (non chirurgicale) : 600 000 FCFA
- Affiner le bas du visage : 200 000 FCFA
- Visage complet : 1 000 000 FCFA

**Flyer 3 · HARMONISATION FACIALE · GENESIS SOFT** (`flyer-genesis-soft.jpg`) : « Le Genesis Soft est une technique qui va
permettre de modifier le volume et d'améliorer son aspect visuel. La perte de volume est très fréquente dès qu'on
commence à prendre de l'âge. »
- Creux infraorbitaire : 300 000 FCFA
- Sillon nasogénien (ride du sourire) : 600 000 FCFA
- Restructuration labiale (lèvres) : 300 000 FCFA
- Redéfinition de la mâchoire et des joues : 2 100 000 à 2 400 000 FCFA (fourchette)
- Note : « Si vous désirez un volume vraiment plus grand, des frais supplémentaires pourraient être appliqués. »

### 2.3 Ses vocaux (25/11, transcrits)
1. « Ce serait parfait si tu arrives à intégrer [les visuels des flyers] sur le site. Là, les gens vont comprendre
   exactement de quelle zone on parle. Amuse-toi et fais-moi ça comme tu peux. » (occupée, hors du Bénin)
2. « C'est le plus gros travail. Les autres, c'est je dois supprimer certaines choses de INA Lux… et ajouter quelques
   nouveaux soins de visage dans Luxury Skin Clinic. » ⏳ **La liste des suppressions dans INA et des nouveaux soins
   visage n'est pas encore donnée** : ne rien supprimer ni inventer avant.
3. « Tu as pu voir le truc pour les paiements sur le site directement, Mobile Money et tout ? Dis-moi ça va coûter
   combien pour qu'on puisse l'intégrer le plus tôt possible. » ⏳ **Prix à fixer par Mongazi** (techniquement : SasPay,
   déjà branché sur PISTE et MA LETTRE À…, Mobile Money et carte, 61 réseaux, minimum 200 XOF).

## 3. Le plan (dans cet ordre)
**Les références (26/11)** : FIRST PAGE 3D (le parcours de clinique, pour la STRUCTURE) + Vibrant Wellness (la zone
qui s'allume sur un buste, pour l'EFFET), détail Facework (la fiche de soin). Décorticage et prompt complet :
`C:/Users/USER/nebula-apercus/_socle/references/FIRSTPAGE-VIBRANT-clinique-PROMPT.md` (hors dépôt, registre des
références). ⏳ **À faire valider par Mongazi avant la construction (B).** Décidé dans le prompt :
- la clinique est un voyage en 10 stations, de la porte au bureau des rendez-vous ;
- l'harmonisation faciale est une page à part (`harmonisation-faciale.html`, l'ex-Cozy) : le « cabinet privé »
  encre et or, où l'on touche les zones sur **SES visuels de flyers** ;
- le buste de Poly Haven est écarté (un Romain au visage sévère) ;
- tout le décor est fait en code, sans GLB lourd.

- [x] A1 · Cozy → INA (26/11), par `python _outils/_cozy_vers_ina.py`, idempotent :
  - les 7 produits sont LUS dans `cozy.html` et entrent dans une 6e famille « Intime & bien-être », avec ses 3
    catégories sous leurs libellés exacts (Hygiène intime 1, Selfcare 4, Produits raffermissants 2) ;
  - **INA passe de 49 à 56 produits**, et le script refuse d'écrire si un nom manque ou se double ;
  - les besoins de Cozy (libellés en clair) sont devenus des clés de `CONCERNS`, avec ses mots ;
  - `important` est devenu `warn` ;
  - la variante (« Fraise Sucrée ») s'affiche en or clair `#c9a84c` sur la carte noire (l'or foncé ne se lisait pas).
  - Vérifié dans le navigateur : la famille, les 7 cartes, les photos, les badges, la variante.
  - ⚠️ Le QC (`_qc.py --page ina-luxury.html`) n'a pas pu tourner le 26/11 : le PC manquait de mémoire et la page
    ne chargeait pas en 30 s. À relancer seul, sans Chrome ouvert.
  - Reste : `cozy.html` ne doit plus rien vendre (A2).
- [ ] A2 · La nouvelle rubrique (ex-Cozy) : « Harmonisation faciale » (Facial Balancing, Genesis Hollywood, Genesis
      Soft), même principe que la clinique : protocoles, indications, tarifs, les visuels de ses flyers (zones du
      visage), prise de rendez-vous. Le hub (index.html) remplace l'univers Cozy par cette rubrique.
- [ ] A3 · Mettre à jour `llms.txt` / `tarifs.md` (`_outils/_llms.py`) et le balisage (`_outils/_jsonld.py`) : nouveaux tarifs.
- [ ] B · LA REFONTE 3D : la vitrine de la clinique ENTIÈREMENT en 3D au défilement, dans un salon de beauté beau et
      lumineux, tout le contenu dedans (soins, tarifs, rendez-vous). Moteur commun des aperçus (`voyage3d.js`, 4K natif,
      plancher 2x, 60 i/s) + l'assistant qui vient saluer (`invite.js`).
- [ ] C · Publier : `python _outils/_dist.py` puis `wrangler pages deploy _dist --project-name luxury-club-229 --branch main`
      (⛔ jamais le dossier entier), QC `python _outils/_qc.py` vert, contraste mesuré sur les pixels.

## 4. Les règles du site qui restent vraies (voir `CONTEXT.md`)
Publier par `_dist` · contraste mesuré sur les pixels rendus · aucun visage ni soin inventé dans une image GÉNÉRÉE par
nous (les flyers sont ses supports à elle : leurs visuels sont les siens, demandés par elle) · `llms.txt` à relancer après
tout changement de tarif · horaires lundi-samedi 10h-17h · numéro de la maison inchangé.
