# Les sons du monde · sources, licences, ce qui manque

> Mongazi, 2026-11-12 : « il doit y avoir des bruits ultra réalistes, ouverture
> de porte… cherche des repos de bruitage libres pour rendre tout encore plus
> immersif ».

## Ce qui est en place (vague 1 bis, 2026-11-12)

19 bruitages **enregistrés**, convertis en MP3 mono 64 kb/s (lisibles par tous
les téléphones, iPhone compris) : **116 Ko en tout**, dans `socle/sons/`.

| Son | Fichier | Où on l'entend | Source |
|---|---|---|---|
| la porte s'ouvre, se referme | `porte-ouvre`, `porte-ferme` | en passant la porte, **placée à la porte** | Kenney *RPG Audio* |
| pas sur sol dur (5 variantes) | `pas-1` à `pas-5` | les tiens, et **ceux des visiteuses, de là où elles marchent** | Kenney *Impact Sounds* |
| froissement de tissu (4) | `tissu-1` à `tissu-4` | quand une visiteuse touche une pièce, quand une pièce entre au sac | Kenney *RPG Audio* |
| cuir, papier | `sac-1`, `sac-2` | le sac qui se remplit | Kenney *RPG Audio* |
| cintre | `cintre-1` | réserve | Kenney *RPG Audio* |
| clic de verre, ouvrir, valider, fermer | `choix-*`, `clic-1`, `ouvrir-1`, `valider-1`, `fermer-1` | l'interface | Kenney *Interface Sounds* |

**Licence** : Creative Commons Zero (CC0), « You may use these assets in
personal and commercial projects ». Les trois fichiers de licence sont rangés
à côté des sons. Aucune attribution n'est exigée ; on crédite quand même.

**Le placement dans l'espace** : chaque son qui a une source (porte, pas d'une
visiteuse, tissu) passe par un panoramique **HRTF** : il s'entend à gauche si la
chose est à ta gauche, plus faible si elle est loin. L'oreille suit la caméra.

## Ce qui reste synthétisé (à remplacer)

| Son | Pourquoi pas encore | La meilleure source |
|---|---|---|
| **la pluie sur la tôle** | aucune boucle CC0 chez Kenney | Freesound (filtre CC0) ou WaveSpeed `mirelo-ai/sfx-1.6` avec `ambience: true` (boucle sans couture, 0,01 $/s, déjà utilisé pour MON BÉNIN) |
| **la rumeur d'une rue de Cotonou** (zems, klaxons lointains, voix) | idem | ⚠️ le mieux : **un vrai enregistrement de 2 minutes à Cotonou**, au téléphone, devant une vitrine. Un son généré « de Cotonou » serait une matière, pas un document (leçon de MON BÉNIN) |
| **la machine à coudre** de l'atelier | idem | Freesound CC0 (il y en a plusieurs), ou **la vraie machine d'Hillary** enregistrée 30 s |
| **le tonnerre** | idem | Freesound CC0 |
| **le ventilateur au plafond**, le bourdonnement de la clim | idem | Freesound CC0 |

## Les banques vérifiées

| Banque | Licence | Usage commercial | Ce qu'il faut |
|---|---|---|---|
| **Kenney** (kenney.nl) | CC0 | oui | rien : téléchargé ✅ |
| **Freesound** (freesound.org) | variable : **ne prendre que CC0** | oui pour CC0 | 🙋 un compte gratuit et une clé d'API pour télécharger par script |
| **Sonniss, « GDC Game Audio Bundle »** (gratuit chaque année) | licence Sonniss : usage commercial permis, sans attribution, **pas de redistribution brute** | oui | des dizaines de Go : à télécharger sur un autre PC |
| **WaveSpeed** `mirelo-ai/sfx-1.6` | généré, à nous | oui | 🙋 recharger le solde |
| ~~BBC Sound Effects~~ | non commercial seulement | ⛔ non | |
| ~~Pixabay~~ | licence Pixabay : pas de redistribution brute | à éviter dans un produit revendu | |

⚠️ **Toujours mesurer un son, jamais l'écouter de confiance** (leçon de MON
BÉNIN) : niveaux normalisés, boucle vérifiée début contre fin.
