/*
  PISTE · le garde-barrière de la mise en ligne.

      node _predeploy.js

  Il s'arrête au PREMIER problème. Le principe est celui du `_predeploy.py`
  du client 10 : on ne déploie pas « pour voir ». Un site de vente en ligne
  qui affiche un mauvais numéro de paiement, c'est l'argent d'un client qui
  part chez un inconnu, et ça ne se rattrape pas avec un correctif le
  lendemain.

  Ce qu'il vérifie, dans l'ordre :
    1. les numéros Mobile Money sont confirmés
    2. le paquet se construit
    3. les 95 contrôles qualité sont verts
    4. rien d'inachevé ne traîne dans le paquet livré
    5. le paquet contient bien ce qu'il faut, et rien qui pèse pour rien
*/

import { execSync } from 'node:child_process'
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'

const RACINE = import.meta.dirname
const DIST = join(RACINE, 'dist')

let etape = 0
const titre = (t) => console.log(`\n${++etape}. ${t}`)
const bon = (t) => console.log('   OK  ' + t)

function stop(quoi, remede) {
  console.error('\n⛔ ARRÊT : ' + quoi)
  if (remede) console.error('   → ' + remede)
  console.error('\nRien n\'a été déployé.\n')
  process.exit(1)
}

/* -------------------------------------------------- 1. l'argent d'abord -- */

titre("Les numéros qui reçoivent l'argent")
const donnees = readFileSync(join(RACINE, 'src/donnees.js'), 'utf8')
const { MOMO } = await import('./src/donnees.js')

if (MOMO.aConfirmer) {
  stop(
    'les numéros Mobile Money ne sont pas confirmés (`MOMO.aConfirmer` vaut encore `true`).',
    'Demander à Mongazi les deux numéros MTN MoMo et Moov Flooz, avec le nom du titulaire\n' +
      "     tel qu'il s'affiche à la réception, les écrire dans `src/donnees.js`, puis passer\n" +
      '     `aConfirmer` à false. Tant que ce drapeau est levé, le site fonctionne : il dit que\n' +
      "     le numéro arrive sur WhatsApp. C'est la mise en ligne qui attend, pas le produit."
  )
}
for (const c of MOMO.comptes) {
  if (!c.numero?.trim()) stop(`le compte ${c.reseau} n'a pas de numéro.`)
  if (!c.titulaire?.trim())
    stop(
      `le compte ${c.reseau} n'a pas de titulaire.`,
      "C'est le nom qui s'affiche chez le client quand il envoie l'argent : sans lui, il ne\n" +
        '     peut pas vérifier qu\'il paie la bonne personne.'
    )
  const chiffres = c.numero.replace(/\D/g, '')
  if (chiffres.length !== 10 || !chiffres.startsWith('01'))
    stop(
      `le numéro ${c.reseau} (${c.numero}) ne fait pas 10 chiffres commençant par 01.`,
      "L'ARCEP béninoise impose ce format depuis le 30/11/2024. Un numéro à 8 chiffres est\n" +
        "     un numéro d'avant la réforme : il ne recevra rien."
    )
  bon(`${c.reseau} : ${c.numero} (${c.titulaire})`)
}

/* ------------------------------------------------------ 2. construction -- */

titre('La construction du paquet')
try {
  execSync('npm run build', { cwd: RACINE, stdio: 'pipe' })
  bon('`npm run build` passe')
} catch (e) {
  stop('la construction échoue.\n' + String(e.stdout || e).slice(-1200))
}

/* --------------------------------------------------- 3. contrôle qualité - */

titre('Les contrôles qualité')
try {
  const sortie = execSync('npm run qc', { cwd: RACINE, stdio: 'pipe' }).toString()
  const compte = sortie.match(/(\d+) contrôles verts, (\d+) rouges/)
  bon(`${compte ? compte[1] : '?'} contrôles verts, 0 rouge`)
} catch (e) {
  const sortie = String(e.stdout || '')
  const rouges = sortie.split('\n').filter((l) => l.includes('  KO  '))
  stop('des contrôles sont rouges :\n     ' + rouges.join('\n     '))
}

/* ------------------------------------------- 4. rien d'inachevé en ligne - */

titre('Ce qui ne doit pas partir en ligne')
const INTERDITS = [
  ['à confirmer', 'un « à confirmer » resté dans le texte visible'],
  ['à valider', 'un « à valider » resté dans le texte visible'],
  ['lorem', 'du faux texte'],
  ['TODO', 'un TODO'],
  ['FIXME', 'un FIXME'],
]
const html = readdirSync(DIST)
  .filter((f) => f.endsWith('.html'))
  .map((f) => readFileSync(join(DIST, f), 'utf8'))
  .join('\n')
const js = readdirSync(join(DIST, 'assets'))
  .filter((f) => f.endsWith('.js'))
  .map((f) => readFileSync(join(DIST, 'assets', f), 'utf8'))
  .join('\n')

for (const [motif, quoi] of INTERDITS) {
  const re = new RegExp(motif.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')
  if (re.test(html) || re.test(js)) stop(`${quoi} est parti dans le paquet (« ${motif} »).`)
}
bon('aucun repère de travail en cours dans le paquet')

/* Le stock affiché doit être celui qui est compté, jamais un chiffre écrit à
   la main quelque part : c'est la promesse de la décision 21. */
const { TOTAL_FICHES, STOCK } = await import('./src/donnees.js')
const somme = Object.values(STOCK).reduce((a, b) => a + b, 0)
if (somme !== TOTAL_FICHES) stop(`l'inventaire (${somme}) et le total affiché (${TOTAL_FICHES}) divergent.`)
bon(`l'inventaire et le total affiché disent tous les deux ${TOTAL_FICHES}`)

/* --------------------------------------------------------- 5. le paquet - */

titre('Le paquet livré')
const poids = (d) =>
  readdirSync(d, { withFileTypes: true }).reduce(
    (s, e) => s + (e.isDirectory() ? poids(join(d, e.name)) : statSync(join(d, e.name)).size),
    0
  )
const total = poids(DIST)
if (!html.includes('racine')) stop("le paquet n'a pas de point de montage (`#racine`).")
if (total > 3 * 1024 * 1024)
  stop(`le paquet fait ${(total / 1048576).toFixed(1)} Mo. Au-delà de 3 Mo, on regarde ce qui a grossi.`)
bon(`${(total / 1024).toFixed(0)} Ko au total`)

/* aucune adresse extérieure : la page doit s'afficher entière hors ligne */
const dehors = (js + html).match(/https?:\/\/(?!wa\.me|127\.0\.0\.1|localhost)[a-z0-9.-]+/gi) || []
const inattendues = [...new Set(dehors)].filter(
  (u) => !/nebula-agency\.online|react\.dev|www\.w3\.org|piste\.nebula/i.test(u)
)
if (inattendues.length)
  stop('le paquet appelle des adresses extérieures : ' + inattendues.slice(0, 4).join(', '))
bon('aucune ressource extérieure : la page se charge entière, hors ligne')

console.log(`
✅ PRÊT À DÉPLOYER

   npx wrangler pages deploy ${resolve(DIST)} --project-name piste --branch main

   Puis vérifier en vrai, sur un téléphone :
   · composer une commande de bout en bout et recevoir le message WhatsApp
   · le coller dans le cockpit et le marquer payé
   · ouvrir #/origine et essayer le bouton de retrait
`)
