# 2026-07-31 — HILLARY M. STYL (client 10)

## Demande

Mongazi transmet le **logo** de la marque et un cahier des charges : maison de couture avec
**deux catalogues** (prêt-à-porter par tailles / sur-mesure), **formulaire de prise de
mesures**, **frais d'expédition calculés par pays**, **délais normal vs express**, retrait
en atelier et notification du client quand la tenue est prête.

## Le logo

Buste de mannequin ceint d'un ruban magenta, monogramme **H.M.S** en noir, signature
**HILLARY M. STYL** en magenta, sur fond gris uniforme `#CCCCCC`.

**Traitement :** fond rendu transparent par tolérance de 26 sur les 4 coins (76 % des
pixels), recadrage sur la boîte englobante (1007×557), redimensionnement à 620 px, puis
**conversion WebP** (55 Ko contre 158 Ko en PNG).

## Décisions de conception

1. **Palette tirée du logo** : magenta `#E6007E`, noir `#0A0A0A`, crème. Typo **Archivo**
   pour les titres (géométrique large, comme les lettres du logo) + **Manrope** pour le texte.
2. **Le logo n'est déclaré qu'une seule fois**, en variable CSS `--logo`, utilisé par trois
   éléments en `background`. Première version : 681 Ko parce que le data-URI était inliné
   trois fois. **Après correction : 120 Ko.** Sur la 3G béninoise, ce n'est pas un détail.
3. **Catalogue en 2 colonnes sur mobile.** Première version en 1 colonne : une pièce
   remplissait tout l'écran, parcourir 6 modèles devenait pénible. Deux colonnes, comme
   toutes les boutiques de mode.
4. **Une mesure vide ne bloque pas la commande.** Elle part en « à prendre ensemble » et le
   message indique combien il en manque. Un client qui ne sait pas mesurer son entrejambe
   ne doit pas abandonner son panier.
5. **Accueil personnalisé** : moment de la journée + prénom mémorisé en localStorage à la
   première commande.

## Piège de méthode rencontré

Une capture d'écran en **headless simple** (`--window-size=430`) montrait la page débordant
et les boutons coupés. **C'était un artefact** : headless sans émulation ignore le
`meta viewport` et rend la page à 800 px avant de recadrer à 430. La mesure Playwright avec
vraie émulation mobile a montré `scrollWidth === clientWidth` sur les trois formats.

**Leçon : ne jamais conclure à un bug de mise en page depuis une capture headless non
émulée.** Mesurer `scrollWidth` vs `clientWidth` avec Playwright.

---

# VAGUE 2 — le moteur de mesures refait (même jour)

Mongazi envoie un **second cahier des charges, bien plus précis**, en se plaçant du point
de vue du métier de couturier. Un point change tout :

> « Lorsqu'un client choisit le sur-mesure, il doit remplir un formulaire de mesures
> **spécifique au type de vêtement** sélectionné. »

## Ce que ça casse dans la v1

La v1 demandait **8 mesures « femme » ou « homme »**. C'est un raisonnement de développeur,
pas de couturier. **Le genre du client ne détermine rien.** Le vêtement, si :

| Type de vêtement | Mesures |
|---|---|
| Robe coupée à la taille | **9** |
| Robe droite | **15** |
| Robe ovale | **11** ⚠️ à valider |
| Pantalon | **6** |
| Chemise ou haut | **8** |

Le moteur a donc été reconstruit autour d'un dictionnaire `MESURES`, chaque pièce
sur-mesure portant la clé du jeu qui la concerne. La pièce « Création libre » laisse le
client choisir le vêtement lui-même et bascule sur le bon formulaire.

Les champs sont **regroupés** (Le haut · Les longueurs · Les manches). Quinze cases
identiques à la suite, personne ne les remplit.

## Les autres apports de la vague 2

1. **Prix ET délai de confection sur chaque carte** du catalogue — plus besoin d'ouvrir
   la fiche pour savoir si c'est dans le budget et dans les temps.
2. **Délai express corrigé à 1 à 3 jours** (la v1 disait 4 à 6). Normal : 7 à 14.
3. **La date précise de disponibilité s'affiche dès que les options sont validées** :
   « Chez vous au plus tard le vendredi 7 août », ou « Prête à retirer… » selon le mode.
4. **Message d'aide au-dessus des mesures**, mot pour mot celui demandé :
   « Vous pouvez prendre les mesures vous-même ou inviter quelqu'un à le faire pour vous
   ou vous aider. »
5. **WhatsApp ou email** : le client sans WhatsApp n'est plus bloqué, un des deux suffit.
6. **Mobile Money affiché comme seul moyen de règlement**, avec la mention explicite
   qu'aucun paiement ne transite par le site.
7. **Section À propos** ajoutée.
8. **Double notification expliquée dans les 4 étapes** : un message à la confirmation,
   un second quand la tenue est prête.

## La décision de conception qui compte le plus

**La date est annoncée sur la BORNE HAUTE du délai, acheminement compris.**

Promettre le jour 8 d'un « 8 à 14 jours » fabrique un client déçu le jour 9. On promet 14,
on livre 10, la cliente est contente. Une vitrine qui ment sur un délai coûte plus cher
qu'une vitrine sans délai du tout.

Corollaire assumé sur l'express : la vitrine dit que l'atelier confirme le délai à la
validation et que **si la charge du moment ne le permet pas, le supplément n'est pas dû**.

## Réorganisation des fichiers — source / construction / livrable

Le livrable pèse 143 Ko dont 75 Ko de logo en base64 : illisible à éditer.

| Fichier | Rôle |
|---|---|
| `_vitrine_src.html` | **la source, c'est elle qu'on édite** (marqueurs `__LOGO_B64__`, `__FAVICON_B64__`) |
| `_build.py` | injecte les images → écrit `vitrine.html` |
| `_qc.py` | **53 contrôles**, doit être vert avant tout déploiement |
| `vitrine.html` | le livrable, **généré, jamais édité à la main** |

C'est la même méthode que Speed/Weinkeller (`_build_bottles.py`, `_apply_cave.py`) :
scripts Python UTF-8, idempotents, jamais d'édition manuelle du fichier lourd.

## QC v2 — 53 contrôles, tous verts

- 0 débordement horizontal sur 390 / 768 / 1440, page **et modale ouverte**
- 0 erreur JS, 0 ressource locale manquante, 0 image externe
- **Cibles tactiles ≥ 44 px** — 6 échecs au premier passage : le logo de la barre (41 px),
  les liens de navigation (23 px) et le lien du pied (15 px). Corrigés en
  `display:inline-flex; min-height:44px`. **Un lien de texte reste un lien de texte à la
  souris, mais c'est une cible ratée au pouce.**
- Mesures par type : **9 / 15 / 11 / 6 / 8**, aucun identifiant en double
- Tunnel prêt-à-porter : 35 000 + 12 000 + 10 000 = **57 000 F**, date à **J+7**
  (3 jours express + 4 d'acheminement Côte d'Ivoire)
- Tunnel sur-mesure : pantalon, retrait, normal → **30 000 F**, J+10, libellé « prête à
  retirer », **4 mesures sur 6 suffisent**, les 2 manquantes signalées dans le message
- Email seul accepté · « sur devis » de bout en bout · avertissement robe ovale affiché

Autre correction visuelle : **le logo disparaissait dans le héros**, ses lettres étant
noires sur fond noir. Posé sur une plaque blanche arrondie plutôt qu'inversé en blanc,
ce qui aurait tué le magenta de la marque.

## ⚠️ Bloquant avant mise en ligne — huit points

Tous regroupés dans un bloc **« ZONE À COMPLÉTER »** en tête du script, détaillés au §6 du
`CONTEXT.md` du client. Les trois plus graves :

1. **Le numéro WhatsApp est un fixe de test.** En l'état, aucune commande n'arrive.
2. **Les frais d'expédition et les jours d'acheminement sont des exemples.** Un tarif faux
   coûte de l'argent à la cliente à chaque commande ; un acheminement faux fausse la date
   annoncée, donc la promesse.
3. **Les mesures de la robe ovale n'ont jamais été fournies.** Onze mesures proposées par
   déduction, signalées en jaune dans l'interface même : « Liste de mesures en cours de
   validation par l'atelier ». Elles ne seront pas inventées en silence.

## Ce qu'un fichier statique ne peut pas faire, et qu'on n'a pas fait semblant de faire

| Demandé | Réalité |
|---|---|
| **Paiement Mobile Money** | La vitrine annonce le mode de règlement, aucun paiement n'y transite. Un vrai encaissement passe par **FedaPay** — clé publique côté client, clé secrète côté n8n, jamais dans le HTML |
| **Notification automatique** | Les deux messages sont aujourd'hui envoyés à la main. L'automatisation, c'est **n8n + Twilio**, avec la commande enregistrée en base |

C'est l'escalier NEBULA appliqué à la lettre : la vitrine d'abord, l'outil ensuite.

## Positionnement commercial

Ce projet dépasse le Catalogue Digital à 50 000 F : il embarque un moteur de commande avec
prise de mesures et calcul de frais par pays. À chiffrer avec le **configurateur** du site,
pas au forfait catalogue.


---

# VAGUE 3 — la direction artistique « LE FIL » (2026-08-01)

## Le verdict de Mongazi

> « Là quand je regarde, malgré ton expertise, je vois un site à 100 $. Je veux que ce soit
> comme un site à 100 000 €, le client doit juste être abasourdi. »

Il avait raison. La v2 était **correcte**, pas **mémorable**. Et la bonne réponse n'était
pas « ajouter des animations » : c'était **trouver l'idée**.

## L'idée

Une maison de couture, c'est **un fil** qui va du mètre-ruban au vêtement fini.
Le site est ce fil qu'on tire. À partir de là, tout se déduit — et **chaque animation
raconte le métier au lieu de décorer la page**.

| | Section | Signature |
|---|---|---|
| — | Ouverture | le fil descend, le monogramme apparaît, deux pans de tissu s'écartent |
| — | Héros | titre à la craie ligne par ligne · **le croquis de la robe se dessine** · mètre-ruban gradué · nappes de lumière |
| 01 | La maison | **la piqûre** : un point de couture se coud d'un pilier à l'autre, l'aiguille suit |
| 02 | Catalogue | **le patron à la craie** : contour pointillé tracé autour de chaque pièce, en cascade |
| 03 | La méthode | **le fil qui relie** les 4 étapes, la perle progresse au défilement |
| 04 | À propos | **le drapé** : le texte se dévoile par plis · les chiffres se comptent |
| 05 | L'atelier | **la coupe** : ligne pointillée traversante, **les ciseaux la suivent**, le titre se révèle |
| — | Modale | le carnet se lève, les champs se posent un à un, **la date se tamponne** |

Permanent : grain de toile · fil de progression · **l'aiguille en guise de curseur** sur
ordinateur, aimantée par les boutons · ruban défilant · barre transparente sur le héros
qui se pose sur fond papier ensuite.

## Ce qui fait vraiment la différence, et ce n'est pas le mouvement

**La typographie.** Passage à **Bodoni Moda**, le didone des magazines de mode, pour tous
les titres. Archivo reste pour les micro-libellés, Manrope pour le texte. Un didone à
gros corps sur fond d'encre, c'est ce qui sépare une page correcte d'une page de maison.

**Le rythme des fonds.** Encre → ruban magenta → papier → papier profond → encre →
papier → encre. Sans alternance, tout se vaut et rien ne ressort.

**Le vide.** Le héros ne remplit pas l'écran ; il respire, et le croquis occupe la moitié
droite en grand écran.

## Ce qui a été refusé

**Des photos générées par IA pour le catalogue.** Une cliente qui commande « Robe Amazone »
sur la photo d'une robe que l'atelier ne fabrique pas, c'est une promesse fausse — et
c'est la maison qui la paiera. Les cartes gardent un visuel de substitution marqué
« photo à venir », et **le héros est construit pour recevoir une vraie photo** le jour où
elle existera. C'est là que le site gagnera son dernier palier.

## Les défauts trouvés en regardant vraiment les captures

1. **La « coupe » du titre cassait à deux lignes.** Le procédé (deux copies du titre
   découpées à 50 % puis écartées) suppose une seule ligne. Sur mobile, le titre passait
   à deux lignes et affichait une bouillie. Refait autrement : ligne de coupe pointillée
   + ciseaux qui traversent, puis révélation du titre par balayage — **robuste quel que
   soit le nombre de lignes**, et le balisage n'a plus de titre en double.
2. **Le survol restait collé après un appui** sur téléphone : le voile noir « Commander »
   restait sur la dernière carte touchée. Enfermé dans `@media (hover:hover) and (pointer:fine)`.
3. **« 45 000 F » se coupait en deux** sur les cartes à 158 px. Le bloc prix + délai
   s'empile désormais sous 620 px, et les cartes ont la même hauteur (`margin-top:auto`).
4. **L'anneau du curseur traînait en haut à gauche** sur ordinateur tant que la souris
   n'avait pas bougé. Il ne s'allume qu'au premier mouvement.
5. **L'icône du mètre-ruban était illisible** à 30 px.
6. Le croquis débordait de l'écran et se dessinait en 5,5 s. Réduit et accéléré.

**Aucun de ces six défauts ne se voit dans le code.** Ils se voient en regardant les
captures, écran par écran.

## Performance — on n'achète pas le luxe avec des images par seconde

- `prefers-reduced-motion` respecté : tout s'arrête pour qui en a besoin
- **sur téléphone**, le grain ne s'anime plus (la texture reste, le repaint disparaît) et
  la troisième nappe de lumière floutée est retirée
- **aucune animation infinie sous un `backdrop-filter`** — la leçon Boussole est
  désormais un **contrôle automatique** de la suite QC
- le fichier passe de 143 à **174 Ko**, tout compris, sans une seule bibliothèque

## QC — 64 contrôles, tous verts

Les 53 contrôles du moteur de commande **passent sans modification** : l'enveloppe a été
refaite, le moteur n'a pas bougé. 11 contrôles ajoutés sur la couche de mouvement :
le rideau se retire bien du DOM, le fil de progression suit le défilement, les 5
signatures se déclenchent, aucune animation infinie sous un `backdrop-filter`, pas de
débordement après l'ouverture.
