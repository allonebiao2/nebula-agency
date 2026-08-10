# 2026-08-09/10 · MON BÉNIN, l'expérience du pays

**En ligne : https://dev.mon-benin.pages.dev** · dossier `benin-mon-pays/`

## Ce que Mongazi a demandé

Une page qui met le Bénin en valeur « comme personne ne l'avait fait avant » :
faire découvrir le pays aux Béninois, donner envie à ceux qui n'y sont jamais
venus, montrer sa capacité à construire des expériences hors du commun, et se
faire repérer par des institutions ou des entreprises. Plus tard, des commerces
viendront dessus, avec l'histoire de leur fondateur.

Il a envoyé **quatre vidéos** (dont deux fois le même fichier, md5 identique) et
un prompt écrit pour une maison de couture, à adapter.

## La phrase

**« Ce n'est pas un site sur le Bénin. C'est un voyage au Bénin qui dure sept
minutes. »**

## Le refus qui définit le projet

La référence principale est **« GLOBETROTTER »**, un vrai site de destinations
(Highlands, Sahara, Dolomites, Maldives). Elle a un bouton **« HASARD »** qui
téléporte au sort : la preuve, écrite dans son interface, que c'est un
**catalogue**. On a pris son savoir-faire et refusé sa structure. Ici l'ordre des
lieux est le sens.

⚠️ Mongazi a ensuite **redemandé explicitement le bouton « au hasard »**, en
demandant que le héros soit « exactement comme ça à 100 % ». C'est fait, et
signalé une fois, pas deux.

## Les 13 décisions du 2026-08-10

Nom **MON BÉNIN** + « sept cents kilomètres » en signature · départ **à la
Porte** · cible **diaspora afro-descendante** · **bilingue FR/EN dès la
sortie** · **11 lieux** (les 8 + Porto-Novo « retourner », Grand-Popo « mêler »,
Dassa « compter ») · photos **sous licence, à chercher** · **sons générés
(WaveSpeed)** · voix **plus tard** · haltes **oui, Mongazi demande l'accord des
5 artisans** · annuaire **en objet SÉPARÉ, même identité** · PISTE **note
d'abord** · **dev maintenant, vrai domaine plus tard** · cap sur les **Vodun
Days de janvier**.

## Ce qui est construit

**Huit stations** dans l'ordre réel de la latitude, de la Porte du Non-Retour
(km 0) au fleuve Niger (km 617), avec **un verbe d'interaction différent par
lieu** : tenir, remonter, choisir, pagayer, frotter, descendre, attendre,
arriver.

**Le portail**, relevé image par image sur la référence : deux cercles
concentriques, le nom en très grand très espacé, le filet, la région et le
kilomètre, les flèches, « partager » à la verticale à gauche, « découvrir ce
lieu » au centre, « au hasard » et son bouton rond doré à droite. **Le lieu
suivant arrive PAR LE CERCLE** : l'iris part exactement du rayon du cercle
intérieur, mesuré sur l'élément rendu.

**Huit ambiances sonores générées avec WaveSpeed**, une par lieu.

## Ce qui a été appris

### La police distante était une faute
La page chargeait Fraunces chez Google et le test s'est **bloqué** dessus.
Contraire à la promesse « 3 s en 3G ». Bodoni Moda est désormais servi en local
(repris du dossier Hillary), et un contrôle vérifie qu'**aucune requête ne sort**.

### Un élément fixe finit toujours par recouvrir du contenu
Réserver une marge ne suffit pas : un `fixed` est ancré au viewport. Règle :
**un instrument flottant ne recouvre jamais du texte, seules les bandes de bord
en ont le droit, et alors elles doivent être vraiment opaques.**

### Un compteur qui contredit son étiquette
La jauge interpolait en continu : elle affichait **3** en face de « km 0 » et
**166** en face de « km 98 ».

### Vérifier en photographiant, pas en lisant le CSS
Le contrôle d'opacité de la barre lisait une chaîne CSS et échouait pour une
mauvaise raison. Refait en photographiant la barre pendant qu'un motif clair
défile dessous.

### Le son : mesurer, jamais écouter de confiance
Les huit MP3 pesaient **exactement 64 592 octets**. Normal à débit constant,
mais ça ne prouve rien. Comparés par **MD5 et profil spectral** : bien
différents, et leurs profils correspondent aux textes. Le **raccord de boucle**
mesuré à 7,9 %. Les **niveaux** avaient un **facteur 15** d'écart, ramené à 1,9
par normalisation à ‑20 LUFS.

### Deux défauts de CSS qui ne se voient qu'à l'œil
`inline-flex` **supprime l'espace** entre ses éléments : la marque se lisait
« MONBÉNIN ». Et d'anciennes règles `.barre-b span` **aplatissaient le menu
hamburger à un seul trait**.

### L'alias d'un déploiement Cloudflare a du retard
`dev.mon-benin.pages.dev` accuse quelques secondes de retard sur l'URL immuable
du déploiement. Ça a fait croire deux fois à une publication ratée, dont un faux
404 sur les sons.

## L'état

**91 contrôles verts, 0 échec.** Zéro erreur JS, zéro requête vers un tiers,
aucun débordement en 390 / 768 / 1440. **189 Ko la page sans les sons**, 48 Ko
par ambiance chargée à l'arrivée sur son lieu.

## Ce qui reste

Les 3 nouveaux lieux et leurs verbes · l'anglais complet · les photos (deux par
lieu, **en portrait**) · les voix · l'annuaire · **la note due à Mongazi** sur
ce que perdrait PISTE contre ce que gagnerait l'annuaire.
