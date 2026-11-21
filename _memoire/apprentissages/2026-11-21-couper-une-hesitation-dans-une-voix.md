# Couper une hésitation dans une voix off, sans l'entendre (2026-11-21)

La voix de Mongazi pour la pub « Chaque nuit, tu perds des clients » portait deux « en fait » sur la phrase clé
(« le client en fait il achète chez en fait celui qui… »). Je ne peux pas écouter : la coupe se fait sur des mesures,
et se prouve par une nouvelle transcription.

## La méthode
1. **Transcrire mot à mot** (Deepgram nova-3, `language=fr`) pour situer les mots. ⚠️ Les temps des mots sont
   approximatifs : ils ne disent PAS où couper.
2. **Lire le signal en trames de 5 ms : énergie ET passages par zéro.**
   - Voyelle : énergie forte, moins de 2 000 passages par seconde.
   - Souffle (f, ch, s, la détente d'un t) : plus de 3 000 passages par seconde.
   - Silence ou fermeture d'un t : énergie basse, peu de passages.
   C'est ce qui nomme chaque son.
3. **Entre deux voyelles collées, regarder le spectre.**
   - Un [é] porte de l'énergie entre 1,6 et 2,8 kHz.
   - Un [an] presque pas.
   - Le rapport aigu/grave par trames de 10 ms donne la frontière.
4. **Couper à la fin d'une voyelle et au début de la suivante.** Fondu de sortie de 10 à 12 ms, fondu d'entrée de
   4 à 6 ms, et un vrai petit silence entre les deux. Le fondu enchaîné centré sur un point « creux » ne suffit pas.
5. **Prouver par une nouvelle transcription** : chaque mot de la phrase doit revenir, avec une bonne confiance.

## Ce qui a mordu
- **Première coupe** : « chez » avait disparu. Son [é] ne durait que 40 ms, APRÈS un « ch » de 140 ms. La coupe,
  placée là où l'énergie baissait, tombait dans le « ch ».
- **Le « il » collé au « client »** était entendu « l'achète ». Avec 90 ms de silence avant lui (la virgule de
  l'oral), il revient à 0,95.
- La transcription peut se tromper sur un passage qu'on n'a pas touché (« il l'appuie » pour « il appuie »).
  Comparer avec la transcription de l'original avant d'accuser la coupe.

Outil : rien de neuf, Python, numpy et `wave` sur le WAV 48 kHz mono. La voix montée vit dans
`_studio-video/public/` (ignoré par git : la voix de Mongazi ne va pas dans le dépôt public).
