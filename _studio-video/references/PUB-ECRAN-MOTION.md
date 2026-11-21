# Pub « écran filmé, motion design » · deux références décortiquées, le prompt complet, la version NEBULA

Envoyées par Mongazi le 21/11 vers 0 h 40 : « exactement le même processus que pour le catalogue : décortique, donne le
prompt, crée la vidéo adaptée à NEBULA avec le logo ; vidéo éducative, accroche choquante et urgente, information
capitale ». Deux TikTok de 576 × 1024 à 30 i/s, mesurés (ffprobe, détection de coupes sur la zone de l'écran, planches
à 1 et 4 images/s, transcription Deepgram mot à mot).

## 1. Ce que font les deux références (mesuré)

**A** · « 5.5 is ridiculous at motion » (@motionlovee, 15 s de vidéo + 4 s de fin TikTok ajoutée au téléchargement)
- Un portable posé sur une table noire brillante, filmé de biais dans une pièce sombre ; l'écran éclaire la scène et se
  reflète dans la table.
- À l'écran, une suite de petites animations : logo qui tourne, mot géant orange, points qui dansent, bouton lecture
  sur bleu, motifs qui se transforment, sphère de points, mot qui défile sur vert acide, logo final.
- Le contenu de l'écran change à 1,8 · 5,5 · puis en **rafale de 11,1 à 12,9 s (toutes les 0,2 à 0,5 s, la montée de
  la musique)**, puis le logo final à 15,0 s. Entre deux changements, l'animation ne s'arrête jamais.
- Aucune voix : la musique rythmée commande tout. Titre fixe en haut avec une icône.

**B** · « New Claude Opus 5.5 🤯 » (22,7 s)
- Un écran d'ordinateur devant une baie vitrée sur la ville, le logiciel de montage laissé visible en bas (« c'est moi
  qui l'ai fait »).
- À l'écran, une pub minimaliste de grande marque. Fond noir, **un seul halo de couleur** (vert) flou qui respire
  derrière l'élément du moment. **Un élément par phrase**, et rien d'autre à l'écran :
  - icône de la marque ;
  - téléphone à 9:41 ;
  - écran d'accueil ;
  - liste de produits qui arrivent une à une ;
  - tableau des ventes à 0,00 $ ;
  - deux phrases en blanc, avec un seul mot en couleur ;
  - une notification qui s'allume ;
  - le logo.
- **La voix** : 28 mots seulement, calme, des phrases de 2 à 5 mots et de vrais silences. Elle démarre à 0,7 · 3,1 ·
  4,0 · 5,1 · 9,4 · 11,7 · 13,4 s, puis le nom de la marque à 17,1 s, seul, une fois le logo posé (dès 15 s). Le
  texte : « It starts with something you made. Tap once. You're open. T-shirts, shoes, jackets. Somewhere, someone
  found you. Sell what you make, and hear your first sale. Shopify. »
- Titre en haut : texte blanc sur cartouche noir arrondi, plus un emoji (l'outil texte de TikTok).

## 2. Comment elles ont été faites (la recette de l'auteur)
1. La pub est **du motion design écrit par Claude** (du code : HTML et CSS animés, rendus en vidéo 16:9).
2. Elle passe sur **un vrai écran**, filmé au téléphone en vertical, dans une belle pièce : nuit et reflets (A) ou
   ville au coucher du soleil (B). L'écran filmé prouve que c'est réel et que c'est fait maison.
3. **Une accroche écrite en haut**, avec un emoji.
4. Le son :
   - A : une musique qui bat, et une coupe sur chaque temps ;
   - B : une voix calme, puis des silences, une musique douce et un petit son pour la vente ;
   - dans B, la marque est dite **en dernier**.
5. La grammaire visuelle de B :
   - chaque élément entre en 0,4 s (fondu, échelle 0,96 → 1, flou → net) et sort quand la phrase suivante commence ;
   - aucun effet gadget ;
   - une seule couleur forte sur du noir.

⛔ On reprend la CONSTRUCTION, jamais leurs images, leur musique, leurs textes ni leurs marques (Claude, Shopify).

## 3. Le prompt complet (pour refaire ce genre de pub, pour n'importe quelle marque)

> Crée une publicité vidéo de 30 à 40 secondes, en 16:9 (1920 × 1080, 30 images/s), dans le style des pubs
> minimalistes des grandes marques tech.
>
> **Le fond et le halo.** Fond presque noir (#07060D). Un seul halo de la couleur de la marque, large et flou, respire
> lentement derrière l'élément du moment : échelle 0,9 → 1,1 et opacité 0,5 → 0,8 sur 4 s. Rien d'autre à l'écran
> que l'élément qui accompagne la phrase dite.
>
> **Le rythme.** Une voix off dit des phrases de 2 à 8 mots, séparées de silences. Chaque phrase fait apparaître UN
> seul élément : il entre en 0,4 s (fondu, échelle 0,96 → 1, flou de 8 px → net) et sort en 0,3 s quand la phrase
> suivante commence. Pas de balayage, pas de rotation, pas de transition gadget.
>
> **Les éléments**, dessinés en HTML et CSS (aucune image générée) :
> - un téléphone arrondi avec l'heure ;
> - des bulles de discussion ;
> - des cartes produits avec leur prix ;
> - un bouton qu'on touche (onde du doigt) ;
> - une carte de commande qui arrive ;
> - un compte à rebours ;
> - le logo à la fin.
>
> **La typographie.** Une sans-serif géométrique (Inter), blanche (#F5F3FF), graisse 600, interlettrage -1 %. Un seul
> mot coloré par phrase, dans la couleur d'accent.
>
> **Le moment fort.** La phrase-clé passe en typographie géante, plein écran, mot par mot sur la voix, sur un fond de
> la couleur du halo.
>
> **La fin.** Écran noir, puis le logo s'allume comme un néon : il scintille, puis sa lumière se stabilise. La voix dit
> le nom de la marque, seul, une fois le logo posé.
>
> **Le son.**
> - La voix au premier plan (-16 LUFS).
> - Une musique douce et minimale en dessous (-28 LUFS).
> - Un petit son par élément : pop pour une bulle, clic pour un toucher, carillon doux pour une commande, souffle pour
>   le grand texte, bourdonnement pour le néon.
>
> **Les livrables.**
> - Le MP4 16:9.
> - Une version verticale 9:16, où ce 16:9 joue sur un écran dans une pièce sombre : la lumière de l'écran déborde sur
>   le mur, et une table brillante la reflète. En haut, une accroche (texte blanc sur cartouche noir arrondi, plus un
>   emoji) ; sous l'écran, les sous-titres mot à mot.

## 4. La version NEBULA

### Le script (voix de Mongazi, ~38 s)
1. Chaque nuit, tu perds des clients…
2. Et tu ne le sais même pas.
3. Minuit. Quelqu'un voit ton statut.
4. Il t'écrit : « C'est combien ? »
5. Tu dors. Il achète ailleurs.
6. Retiens bien ça :
7. le client achète chez celui qui lui montre tout… tout de suite.
8. Mets ta boutique dans son téléphone.
9. Tes produits. Tes prix. Un seul lien.
10. Il choisit. Il appuie.
11. Et la commande arrive sur ton WhatsApp. Déjà écrite.
12. Même à minuit.
13. Noël, c'est dans un mois.
14. Ta boutique dans le téléphone : prête en 48 heures.
15. Écris-moi « CATALOGUE » sur WhatsApp.
16. NEBULA Agency.

L'accroche choc (1-2) ouvre une question (« comment ça, je ne le sais pas ? ») ; la réponse arrive tout de suite (3-5),
avec l'exemple d'ici (le statut, « C'est combien ? »). L'information capitale (7) est le moment fort. La solution est
dite avec l'image simple « ta boutique dans son téléphone », et 12 referme la boucle de minuit. Puis l'urgence (Noël),
une seule action (15), la signature (16).
Tout est vrai : le catalogue envoie bien la commande déjà écrite sur WhatsApp, et 48 h après les photos, les prix et le
premier paiement (le détail se dit dans la conversation, pas dans la pub).

### Plan par plan (16:9, un élément par ligne)
| Ligne | À l'écran |
|---|---|
| 1-2 | Nuit. Une horloge 00:12 en chiffres lumineux dans le halo violet ; « clients » s'efface lettre par lettre |
| 3 | Un téléphone : un statut avec une carte produit dessinée (robe, sac ou parfum en trait) |
| 4 | Une bulle « C'est combien ? » arrive avec un pop, heure 00:12, coches grises |
| 5 | Le téléphone s'éteint ; la bulle glisse et sort ; « ailleurs » en orange |
| 6-7 | **Moment fort** : plein écran violet, texte géant noir mot par mot, « TOUT DE SUITE » en dernier, avec un souffle |
| 8 | Un téléphone, et dedans **un vrai catalogue livré** qui défile (aubraisedor.com) |
| 9 | Trois cartes produits avec leur prix sortent du téléphone, puis une pastille de lien qui brille |
| 10 | Un doigt touche « Commander » (onde, clic) |
| 11-12 | La carte de commande arrive, déjà écrite, heure 00:14 et une petite lune ; carillon doux |
| 13 | « J-34 » géant, quelques étincelles dorées |
| 14 | Un anneau qui se remplit : « 48 h » |
| 15 | Une pastille « CATALOGUE » et le numéro WhatsApp de NEBULA (celui du site) |
| 16 | Noir, puis l'enseigne néon NEBULA (violet) AGENCY (cyan) s'allume en scintillant ; la voix dit le nom une fois l'enseigne posée |

Couleurs :
- nuit #07060D ;
- halo violet #9333EA ;
- mot coloré en cyan #22D3EE ;
- blanc #F5F3FF ;
- orange #FF8A1E seulement pour la perte.

L'enseigne de fin a le même dessin que `_outils/avatar_studio.py`.

### La version TikTok (9:16)
- **L'écran filmé** : le 16:9 joue sur un moniteur fin, dans une pièce sombre. Sa lumière déborde sur le mur, et la
  table noire brillante la reflète (référence A). L'enseigne NEBULA AGENCY en néon est accrochée au mur, au-dessus de
  l'écran.
- Une légère poussée de caméra tout du long. À la ligne 16, la caméra monte vers l'enseigne, qui s'allume en plein.
- **L'accroche du haut** : « Tu vends sur WhatsApp ? 😳 ».
- **Les sous-titres** mot à mot sous l'écran.
- **Option « vraiment filmé »** : Mongazi passe le MP4 16:9 sur sa télé LG, depuis une clé USB et le lecteur de la
  télé (pas de saccade), et filme en vertical dans le noir. On remet ensuite le son propre, calé par corrélation.

### Le son
- La voix de Mongazi, nettoyée (passe-haut, débruitage léger, -16 LUFS).
- Une musique douce sous licence, prise dans nos dossiers, à -28 LUFS.
- Les bruitages de la recette.
- ⛔ Rien de la référence.

### ⛔ Règles
- Aucune image générée par IA.
- Jamais un aperçu de prospect non payé : seulement des sites livrés et finis.
- Pas le logo officiel de WhatsApp : bulle et icône génériques.
- Aucun tiret cadratin.
- Le numéro n'est écrit dans aucun nouveau fichier du dépôt : il est lu dans `src/tiktok-20-11/donnees.ts`.
- On livre le MP4, jamais le projet (licence Remotion).
