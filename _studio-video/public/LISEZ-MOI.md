# Ce dossier reçoit les plans filmés et la musique

Rien de ce qui est ici n'est envoyé sur GitHub (le dépôt est **public**, et ces
fichiers sont lourds). Seule cette note est suivie, pour que le dossier existe.

## Les visages

Tourner d'un coup six « oui » et six « non », comme le dit
`_documents/nebula-agency/marketing/TIKTOK-OUI-NON.md`, puis découper les prises
en fichiers séparés et les poser ici :

```
public/visages/oui-1.mp4
public/visages/non-1.mp4
...
```

Ensuite, dans `src/scripts.ts`, remplacer `plan: null` par le nom du fichier,
sans le `public/` :

```ts
{carte: s1_01, reponse: 'NON', plan: 'visages/non-1.mp4'},
```

Tant que `plan` vaut `null`, la réponse s'affiche en grosses lettres sur fond
noir et la vidéo se rend quand même.

## La musique

Une musique tendue, régulière, **sans paroles** (le document est formel : sur ce
format, on lit). La poser ici, puis l'ajouter dans `src/OuiNon.tsx` :

```tsx
import {Audio, staticFile} from 'remotion';
<Audio src={staticFile('musique.mp3')} volume={0.35} />
```

⚠️ Une musique tirée d'un catalogue commercial ne se met pas dans une vidéo
publiée sans en avoir le droit. Sur TikTok, le son ajouté depuis l'application
est couvert par leur catalogue ; un fichier collé au montage ne l'est pas.
