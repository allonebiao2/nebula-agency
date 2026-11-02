# Le décodeur vidéo du navigateur a une petite réserve d'images (2026-11-02)

**Où c'est arrivé** : LA BOBINE, « Lire à l'envers » (`labobine/js/inverser.js`).

**Le symptôme** : l'inversion d'une vidéo de 3 secondes attendait pour toujours. Aucune erreur, aucun message :
le QC a simplement expiré au bout de 180 secondes.

**La cause** : pour réécrire une tranche d'images à rebours, le code gardait une trentaine d'images décodées
ouvertes (des `VideoSample` de Mediabunny, donc des `VideoFrame` de WebCodecs). Le décodeur du navigateur, surtout
le décodeur matériel, ne dispose que d'une petite réserve d'images de sortie. Quand toutes sont tenues par le
programme, il attend qu'on en rende une, et le programme attend la suivante : blocage silencieux.

**La règle** : une image décodée se **recopie aussitôt** (dans une toile à nous) **puis se ferme**. On ne garde
ouvertes que celles que le moteur est en train de dessiner. Une tranche à rebours se garde donc en toiles, pas en
images décodées (budget : environ 160 Mo de toiles par tranche).

**Deux détails qui vont avec** :
- `samplesAtTimestamps()` veut des instants **croissants** : on demande la tranche dans l'ordre, on la réécrit à
  l'envers ensuite.
- Il peut rendre **le même objet** pour deux instants voisins : ne le fermer qu'une fois, quand un autre arrive.

**Comment l'avoir trouvé vite** : un essai de dix lignes (importer une vidéo, inverser, attendre 90 s) plutôt que
relancer tout le QC ; il a confirmé le correctif en une minute.
