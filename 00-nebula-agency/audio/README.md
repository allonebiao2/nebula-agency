# Audio — Musique d'ambiance NEBULA

## Fichier attendu
`jazz-loop.mp3` — déposer ici un morceau jazz royalty-free, idéalement entre 30s et 2min, qui boucle proprement.

## Sources royalty-free recommandées
- **Pixabay Music** — pixabay.com/music/search/jazz/ (gratuit, sans attribution)
- **FreePD** — freepd.com (domaine public)
- **Free Music Archive** — freemusicarchive.org (filtrer par licence Creative Commons)
- **Bensound** — bensound.com (gratuit avec attribution dans certains cas)

## Comportement attendu
- Démarre au premier clic / scroll / touch (mobile bloque l'autoplay sinon)
- Volume bas par défaut (~0.22 / 22%)
- Bouton flottant bas-droit pour mute/unmute
- La préférence (mute) est sauvée en localStorage : si l'utilisateur coupe, le son reste coupé à sa prochaine visite

## Optimisation
- Format : MP3 128 kbps mono (suffisant pour ambiance)
- Poids cible : < 1 MB
- Outils : ffmpeg, Audacity, online-audio-converter.com
