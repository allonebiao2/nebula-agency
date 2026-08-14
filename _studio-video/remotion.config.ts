import {Config} from '@remotion/cli/config';

// JPEG pour les images intermédiaires : plus rapide, et invisible sur une vidéo
// H.264 de toute façon compressée.
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// ⚠️ Sans ces deux lignes, le rendu échoue sur ce PC avec « Timed out after
// 30000ms while setting up the headless browser ». Le navigateur n'est pas en
// cause : il met simplement plus de 30 s à répondre au démarrage (Windows
// Defender scanne les 113 Mo de Chrome à chaque lancement). On laisse deux
// minutes, et on demande le rendu ANGLE, le plus sûr sous Windows.
Config.setDelayRenderTimeoutInMilliseconds(120000);
Config.setChromiumOpenGlRenderer('angle');
