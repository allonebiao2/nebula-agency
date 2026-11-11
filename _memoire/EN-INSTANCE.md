# EN INSTANCE · tout ce qui attend

> **La zone unique** des points sur lesquels on doit revenir et des projets en instance (demandée par
> Mongazi le 2026-11-11). Une ligne par point ; le détail vit ailleurs, le renvoi dit où.
> - Une session qui laisse quelque chose en suspens **l'ajoute ici avant de finir**.
> - Un point fait **sort d'ici** (et se raconte dans la conversation du jour).
> - Les lignes marquées « au 2026-09 » viennent de `RESTE-A-FAIRE.md` ou de `CLAUDE.md` : **à revérifier**
>   avant d'agir, elles ont pu bouger.
>
> 🙋 attend une réponse ou un geste de Mongazi · 🤖 Claude peut le faire · 🕰️ plus tard, exprès
>
> Dernière mise à jour : **2026-11-11**.

---

## 1. À reprendre bientôt

| Point | Qui | Renvoi |
|---|---|---|
| **NEBULA REC** : premier vrai usage par Mongazi (raccourci sur le Bureau), dire ce qui manque | 🙋 | `conversations/2026-11-11-nebula-rec.md` |
| **VIDÉO HD** : premier passage sur Colab (cocher ESSAI_10_SECONDES), mesurer le temps par minute de vidéo, vérifier NVENC et `zscale` | 🙋 puis 🤖 | `conversations/2026-11-11-video-hd.md` |
| **MuseHub** se lance encore au démarrage : Windows exige les droits administrateur. Gestionnaire des tâches → Démarrage → MuseHub → Désactiver | 🙋 | `journal/2026-11-11-journal.md` |
| **Icecream Screen Recorder** encore installé (démarrage coupé) : le désinstaller, maintenant que NEBULA REC le remplace ? | 🙋 | |
| **Fichiers non suivis du dépôt PUBLIC**, pas poussés exprès : `_partage/` (vidéos et scripts `.pine` de trading, voix ElevenLabs, captures), `.claude-flow/`, `.swarm/`, `.codex/hooks.json`. Décider : dépôt privé, rangement ou suppression | 🙋 | |
| **Méthode de trading de Mongazi** dans `_archives/partage-2026-09-29/` : seulement sur ce disque, à mettre dans le dépôt privé `nebula-trader` (au 2026-09) | 🙋 accord | `RESTE-A-FAIRE.md` |
| **Mémoire vive du PC** : Chrome (3,2 Go avant nettoyage) et VS Code la saturent ; une seule tâche lourde à la fois. **22 profils Chrome** : en supprimer les inutiles allégerait encore | 🙋 | mémoire `project_disque-pc` |
| **LE MONTEUR** (nom provisoire), l'agent de montage : Mongazi a choisi **B** (l'appli), objectif « tout type de vidéo, avec ou sans rush, 10 000 € minimum ». Vague 1 faite et testée dans le projet **privé** `C:\Users\USER\nebula-montage`. 🙋 **recharger le crédit de l'API Anthropic** (épuisé le 2026-11-11 pendant la relecture : le relecteur et le scénariste en dépendent) · 🙋 **créer le dépôt GitHub privé `nebula-montage`** (la création automatique a été bloquée), choisir le nom, envoyer un vrai rush + un brief. 🤖 vagues 2 à 6 (`PLAN.md` du projet) | 🙋 puis 🤖 | `_knowledge/montage-ia-decortique.md`, mémoire `project_agent-montage` |

---

## 2. Améliorations possibles

### NEBULA REC (`scripts/nebula-rec/`)

Idées notées le 2026-11-11, aucune n'est commencée. Les trois premières sont les plus demandées par un
enregistreur d'écran ; celles marquées « ScreenRec » sont ce que ScreenRec faisait (vu avec REA).

1. **Une zone de l'écran, ou une seule fenêtre** : `gfxcapture` sait déjà viser une fenêtre
   (`window_title`, `hwnd`) et rogner (`crop_left`…) ; il faut un sélecteur de zone à la souris.
2. **La webcam en incrustation** (ScreenRec) : la « HP HD Webcam » par DirectShow, en bulle ronde dans un
   coin, déplaçable.
3. **Le son d'un casque Bluetooth** : « Mixage stéréo » ne prend que les haut-parleurs du PC. Il faut une
   boucle WASAPI (capture de la sortie par défaut, quelle qu'elle soit).
4. **Un micro nettoyé** (ScreenRec, RNNoise) : filtre `arnndn` de ffmpeg avec un modèle `.rnnn`, case
   « réduire le bruit ».
5. **Les clics visibles** et le curseur mis en valeur (halo), pour les tutoriels.
6. **Dessiner sur l'écran** pendant l'enregistrement (flèches, surligneur), effacé d'un raccourci.
7. **Couper le début et la fin** avant de garder le fichier, sans recoder.
8. **Un compte à rebours** 3-2-1 et une **minuterie** (arrêt seul après X minutes).
9. **Une capture d'image** (Ctrl + Alt + S) dans le même dossier.
10. **Le format vertical 9:16** et l'export GIF pour TikTok, Reels, WhatsApp.
11. **« Monter dans LA BOBINE »** : envoyer la vidéo finie à notre éditeur.
12. **Deux écrans** : vérifier sur un vrai PC à deux écrans que « Écran 2 » filme bien le second.
13. **En faire un `.exe`** à donner à d'autres PC (aujourd'hui il faut Python et ffmpeg), voire un produit
    NEBULA : à décider.

---

## 3. Projets en instance

D'après `CLAUDE.md` et la mémoire de Claude au 2026-11-11 : l'état exact est dans le renvoi.

| Projet | Où il en est | Ce qui le débloque | Renvoi |
|---|---|---|---|
| **NEBULA VOIX** | lancé le 2026-11-05, prototype « Awa » essayé à la voix | la suite du plan ; ⛔ aucun appel à un particulier sans accord préalable prouvé | `nebula-voix/docs/PLAN.md` (dépôt privé) |
| **MA LETTRE À…** | en ligne ; la plume est coupée ; le film n'est pas publiable tant qu'elle l'est ; ouvertures 3D sans constructeur, serveur ni caisse | 🙋 **le premier franc** (La Carte, 1 000 F) ; critères d'arrêt 1er ou 16 décembre | `malettre/CONTEXT.md` |
| **PISTE** | encaisse et livre tout seul | 🙋 **le premier paiement réel** n'a jamais eu lieu | `piste/PAIEMENT.md` |
| **LE STANDARD** | prêt, pas en ligne | 🙋 le numéro d'Au Braisé d'Or, le numéro d'alerte par maison ; 🤖 le premier appel réel au modèle | `whatsapp-agent/README.md` |
| **LA BOBINE** | en ligne, vagues 1 à 3 | 🙋 brancher `labobine.nebula-agency.online` ; secret du webhook SasPay pour ouvrir la vague 4 (Pro) | `labobine/CONTEXT.md` |
| **Boussole** | tout se fait sur le proto | 🤖 Agenda, comparateur de deux périodes, vague 2 des transitions, `etat.sql` dans Supabase, migration proto → prod | `boussole/README.md` |
| **MON BÉNIN** | en ligne, 8 photos empruntées | 🙋 les 2 photos de la Porte, une voix, l'accord écrit des 5 artisans ; cap sur les Vodun Days de janvier | `benin-mon-pays/CE-QUE-TU-DOIS-APPORTER.md` |
| **NEBULA TRADER** | rien de rentable, aucune démo ne tourne ; 0037 Triple EMA ne tient pas | 🙋 enterrer la 0037 ou non ; trois décisions (seuil des séries perdantes, date et chiffre d'arrêt, plafond mensuel) | `_cerveau/DECISIONS.md` (dépôt privé) |
| **PALABRE** | la v1 ne plaît pas | 🙋 la direction ROYAUMES, rien de construit | coffre `NEBULA AGENCY GAME` |
| **n8n** | le VPS n'appartient plus à Mongazi | 🙋 un n8n tourne-t-il ailleurs ? La relance des renouvellements en dépend | `CLAUDE.md` § Stack |
| **Le parc** | 10 sites sur 15 sans `_headers` (au 2026-09) | 🙋 trancher : c'est un déploiement vers dix sites clients | `RESTE-A-FAIRE.md` § LE PARC |
| **Vendora** | acquisition des 10 premières boutiques à Cotonou, « LA priorité » ; Railway coupé | 🙋 | mémoire `project_vendora-acquisition` |
| **En pause** | NEBULA Prospector (depuis le 2026-06-08), Vitrina (hors ligne depuis le 2026-08-01), marque de déploiement du parc, VoiceStudio (moteur pas fini d'installer) | 🕰️ | mémoire de Claude |

### Clients : ce qui attend chez eux

| Client | Ce qui attend | Renvoi |
|---|---|---|
| **Au Braisé d'Or** | ⛔ **deux numéros WhatsApp** dans le site (`index.html` et `dishes.ts`) à trancher ; photo de l'attiéké ; salle, avis, adresse, logo | `clients/09-au-braise-dor/CONTEXT.md` |
| **Hillary M. Styl** | les 11 mesures de la robe ovale et le jeu `haut_pantalon` (Hillary) ; prix en dollar de la Robe de ville bleue ; l'adresse (fiche Google) | `clients/10-hillary-m-styl/CONTEXT.md` |
| **Luxury Club 229** | images de soins (recharger WaveSpeed, `_gen_soins.py`) ; devis tablette 420 000 F à envoyer à Gloria (au 2026-09) ; fiche Google, adresse | `clients/04-luxury-skin-clinic/CONTEXT.md` |
| **Angy Art** | photos des œuvres seules, adresse, avis, tester le numéro ; trancher l'e-mail masqué et les tranches de budget | `clients/11-angy-art/CONTEXT.md` |
| **Miss cakes** | confirmer le numéro WhatsApp ; logo, photos, avis | `CLAUDE.md` |
| **HH Design** | confirmer le numéro ; logo, Instagram, adresse, prix | `CLAUDE.md` |
| **Speed × Weinkeller** | les autres caves (rouges, spiritueux), Eminente, six « prix sur demande » | `CLAUDE.md` |
| **Djambar Team** | vrais avis, photos sans filigrane, fiche Google | `CLAUDE.md` |
| **Little Sun Pearls** (Cédène) | en attente de ses photos | |
| **Grain d'Esthétique** | l'ancien site Netlify à débrancher | `CLAUDE.md` |

### Dans le dépôt (au 2026-09)

- Branche `claude/video-project-analysis-monetization-18oh7b` : un réveil de Render par tâche planifiée,
  pas fusionné exprès. 🙋 le réveil, oui ou non.
- Branches d'avant le 12 août (`continuation-xu5ma7`, `protocole-boussole-memoire-9xy3j4`,
  `repo-discussion-analysis-g8qubx`) : à regarder un jour ou à abandonner.

---

## 4. Vagues futures (plus tard, exprès)

- 🕰️ **NOTRE PROPRE OBSIDIAN, avec REA** (redit par Mongazi le 2026-11-11 : « on doit créer notre propre
  Obsidian, on va utiliser REA pour ça »). C'est **STELLA**, déjà prévue comme **la dernière vague, après
  NEBULA VOIX** : un assistant à lui, à la voix, en 3D, et une mémoire qui reste (notes, liens, graphe,
  recherche, modèles, tags, sur le PC et le téléphone, sans abonnement). `_memoire/`, `_cerveau/` et la
  mémoire de Claude y vivront.
  - **REA** sert à observer comment Obsidian fonctionne : le format du coffre, les fonctions, ce que fait
    chaque écran. ⛔ Obsidian est propriétaire : **on recrée ses fonctions, jamais son code, ses fichiers ni
    sa marque**. Regarder d'abord les logiciels libres (Logseq, SilverBullet, Foam) : adapter peut coûter
    moins que bâtir.
  - Dans un **dépôt PRIVÉ** (la mémoire privée ne passe jamais par ce dépôt public).
  - Renvoi : mémoire de Claude `project_obsidian-maison`.
- 🕰️ **L'annuaire d'entreprises** de MON BÉNIN (un second objet, pas une couche du voyage) : une note est
  due à Mongazi sur ce que perdrait PISTE.
