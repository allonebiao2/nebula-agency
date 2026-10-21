# 2026-10-21 · MA LETTRE À… : le point de reprise terminé, la pub en images

Mongazi : « TERMINE LE PLI, EN ATTENDANT » (pendant que les calculs de trading tournent).
Le point de reprise du 2026-10-17 (sept étapes, `malettre/CONTEXT.md`) a été suivi dans l'ordre.

## Ce qui a été fait

1. **Le code secret réservé à La Lettre et au Coffret** (commit `beed2ed`) : droit `code` dans les deux
   barèmes (`creer.html`, `_shared/lettre.ts`), comparés par la caisse. Sans lui, La Lettre n'était que
   Le Mot plus cher.
2. **« Retirer cette lettre »** dans le pied de `lettre.html` : seulement sur une lettre servie à
   `/l/<jeton>`, en deux temps, `POST …/retrait`, repli WhatsApp. ⚠️ Le seuil de poids (61 440 octets)
   a obligé à compacter les textes anglais dans un objet `RX` : **la lettre est à 61 372, il reste
   68 octets**.
3. **Le relais `/l/*`** : `malettre/_relais.js` devient `_dist/_worker.js`. En mode avancé, Cloudflare
   Pages n'applique plus `_headers` : le relais pose lui-même les en-têtes.
4. **Le ménage nocturne** des lettres expirées : `_menage.py` + `.github/workflows/malettre-menage.yml`
   (`malettre_menage()` existait et rien ne l'appelait). Essayé avant branchement : il le dit, sort à 0.
5. **`PAIEMENT.md`** : relais, ménage, règle du code, étape de publication, nombres du jour.
6. **Les critères d'arrêt** étaient écrits depuis le dossier du 27/08 : recopiés dans le `CONTEXT.md`.
   ⚠️ **Conflit de calendrier, à trancher par Mongazi** : ils demandent huit semaines de publication et
   200 lettres gratuites, or rien n'est en ligne et le 1er décembre est dans six semaines.
7. **La pub (vague 5), en images** : six compositions Remotion `malettre-*` (30 s FR et EN, deux coupes
   de 15 s par langue), sept plans tirés de l'enveloppe cachetée. **Le plan de la plume montre le vrai
   constructeur**, photographié par `_studio-video/_outils/malettre_captures.py` : la fiche de la lettre
   d'exemple d'Afi, ses puces cochées une à une, puis la lettre que la vraie plume a écrite à partir de
   cette fiche. Planches regardées en 390 de large (FR et EN), défauts corrigés (enveloppe anonyme grise,
   téléphone trop petit, clignement entre deux plans, papier qui grisait en reculant, accroche anglaise).

**Contrôles, tous verts** : `_qc.py` 276 · caisse 327 · accueil 239 · langues 52 · faire-part 83.

## Ce qu'on a appris

- **Une capture d'élément sous un en-tête collant le photographie avec lui** : l'en-tête se pose sur
  la fiche. On le photographie à part et on le rend `static` pendant les captures.
- **Une fiche a des choix d'office** (la longueur, le français) : cliquer une puce déjà cochée la
  DÉCOCHE. Le script de captures lit `aria-pressed` avant de cliquer.
- Un lien de lettre **n'a pas d'aperçu d'image** (`lettre.html` n'en porte aucune, exprès) : la pub ne lui
  en invente pas.

## Ce qui attend Mongazi

- **Les six MP3 ElevenLabs** (`_studio-video/src/malettre/VOIX.md`) → caler et rendre la pub.
- **Trancher les critères d'arrêt** (garder la date, ou huit semaines après la mise en ligne).
- Le feu vert de mise en ligne, brancher la caisse et la plume (`malettre/PAIEMENT.md`).
