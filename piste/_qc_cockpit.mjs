/*
  PISTE · contrôle du cockpit : la veille, la tonalité, les notifications.

  ⚠️ CE QU'ON VÉRIFIE VRAIMENT
  On ne se contente pas de voir un bouton « Activer le son ». On compte les
  oscillateurs RÉELLEMENT créés par le navigateur, et on vérifie que le
  contexte audio est passé à l'état « running ». Un son qui ne se prouve pas
  est un son dont on découvre l'absence le jour où une commande arrive.

  ⚠️ ET ON VÉRIFIE QU'IL NE SONNE PAS AU PREMIER CHARGEMENT. Une alarme qui
  hurle à chaque ouverture, on l'éteint le deuxième jour, et elle ne sert plus.

  Usage : node _qc_cockpit.mjs <code-du-cockpit>
*/
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer-core'

const ICI = path.dirname(fileURLToPath(import.meta.url))
const DIST = path.join(ICI, 'dist')
const CODE = process.argv[2]
if (!CODE) {
  console.error('  usage : node _qc_cockpit.mjs <code-du-cockpit>')
  process.exit(2)
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
}
const ok = []
const ko = []
const dire = (b, q) => (b ? ok : ko).push(q)

const srv = http.createServer((q, r) => {
  let f = path.join(DIST, decodeURIComponent(q.url.split('?')[0]))
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) f = path.join(DIST, 'index.html')
  r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' })
  r.end(fs.readFileSync(f))
})
await new Promise((r) => srv.listen(0, r))
const base = `http://127.0.0.1:${srv.address().port}`

const nav = await puppeteer.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: 'new',
  args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'],
})
const ctx = nav.defaultBrowserContext()
await ctx.overridePermissions(base, ['notifications'])

const errs = []
const reponses = []
const p = await nav.newPage()

/*
  ⚠️ ON LIT LA RÉPONSE DU SERVEUR, PAS LA PAGE.
  Chercher « un numéro » dans le texte affiché ne prouve rien : le cockpit
  montre EXPRÈS le numéro Mobile Money du client, pour rapprocher les
  paiements. L'invariant à tenir est ailleurs : la liste des commandes ne doit
  jamais transporter de fiche. La marchandise ne sort que par un carnet livré.
*/
p.on('response', async (r) => {
  if (!r.url().includes('/functions/v1/piste-cockpit')) return
  try {
    const t = await r.text()
    const d = JSON.parse(t)
    reponses.push({
      ok: d.ok === true,
      fuite: /"numero"|"fiches"|"fixe"|"dirigeant"/.test(t),
    })
  } catch (e) {}
})
p.on('pageerror', (e) => errs.push(String(e)))
p.on('console', (m) => {
  if (m.type() === 'error') errs.push(m.text())
})
const dodo = (ms) => new Promise((r) => setTimeout(r, ms))

/* On espionne l'audio AVANT que la page ne charge quoi que ce soit. */
await p.evaluateOnNewDocument(() => {
  window.__audio = { oscillateurs: 0, contextes: 0, demarres: 0 }
  const A = window.AudioContext || window.webkitAudioContext
  if (!A) return
  const CreerOsc = A.prototype.createOscillator
  A.prototype.createOscillator = function (...a) {
    window.__audio.oscillateurs++
    const o = CreerOsc.apply(this, a)
    const start = o.start.bind(o)
    o.start = (...b) => {
      window.__audio.demarres++
      return start(...b)
    }
    return o
  }
  window.AudioContext = window.webkitAudioContext = new Proxy(A, {
    construct(cible, args) {
      window.__audio.contextes++
      const c = new cible(...args)
      window.__audio.ctx = c
      return c
    },
  })
})

/* Le code du cockpit, comme s'il avait déjà été saisi une fois. */
await p.goto(base, { waitUntil: 'domcontentloaded' })
await p.evaluate((c) => {
  localStorage.setItem('piste_cockpit_mdp', c)
  localStorage.removeItem('piste_refs_vues_v1')
  localStorage.removeItem('piste_commandes_v1')
}, CODE)

await p.setViewport({ width: 390, height: 844 })
await p.goto(`${base}/#/cockpit`, { waitUntil: 'networkidle0' })

/* La veille interroge un vrai serveur : on ATTEND qu'elle réponde plutôt que
   de compter les secondes. Un contrôle qui mesure trop tôt invente des
   défauts qui n'existent pas. */
await p
  .waitForFunction(() => /La veille tourne/.test(document.body.innerText), { timeout: 30000 })
  .catch(() => {})
await dodo(600)

const a = await p.evaluate(() => {
  const t = document.body.innerText
  return {
    veilleOk: /La veille tourne/.test(t),
    heure: /vérifié à \d\d:\d\d/.test(t),
    boutonSon: [...document.querySelectorAll('button')].some((b) =>
      /Activer le son|Tester la tonalité/.test(b.innerText)
    ),
    audio: { ...window.__audio, etat: window.__audio.ctx?.state || 'aucun' },
    commandes: (document.body.innerText.match(/PISTE-[A-Z0-9]{4}/g) || []).length,
    bandeauArrivees: /vient d’arriver|viennent d’arriver/.test(t),
    debordement: document.documentElement.scrollWidth > window.innerWidth + 1,
    petites: [...document.querySelectorAll('button,a,input,select')].filter((e) => {
      const b = e.getBoundingClientRect()
      return b.height > 0 && b.width > 0 && b.height < 44
    }).length,
  }
})

dire(a.veilleOk, 'la veille annonce qu’elle tourne')
dire(a.heure, 'elle affiche l’heure de la dernière vérification')
dire(a.boutonSon, 'le bouton d’activation du son est là')
dire(a.commandes > 0, `les commandes du serveur arrivent dans le cockpit (${a.commandes} vues)`)
dire(!a.bandeauArrivees, 'AUCUNE alerte au premier chargement (sinon on l’éteint le 2e jour)')
dire(a.audio.demarres === 0, 'AUCUN son avant un geste de l’utilisateur')
dire(!a.debordement, 'aucun débordement horizontal en 390 px')
dire(a.petites === 0, `toutes les cibles font au moins 44 px (${a.petites} trop petites)`)
dire(
  reponses.length > 0 && reponses.every((r) => !r.fuite),
  `la réponse du serveur ne contient AUCUNE fiche ni numéro de vivier (${reponses.length} réponse(s) lue(s))`
)

/* Le geste. C'est le seul moment où un navigateur accepte d'ouvrir l'audio. */
const bouton = await p.evaluateHandle(() =>
  [...document.querySelectorAll('button')].find((b) =>
    /Activer le son|Tester la tonalité/.test(b.innerText)
  )
)
await bouton.asElement()?.click()
await dodo(500)

const b = await p.evaluate(() => ({
  audio: { ...window.__audio, etat: window.__audio.ctx?.state || 'aucun' },
  message: /trois notes qui montent/.test(document.body.innerText),
  libelle: [...document.querySelectorAll('button')].some((x) =>
    /Tester la tonalité/.test(x.innerText)
  ),
}))

dire(b.audio.contextes === 1, `un seul contexte audio créé (${b.audio.contextes})`)
dire(b.audio.etat === 'running', `le contexte audio tourne vraiment (${b.audio.etat})`)
dire(b.audio.demarres >= 6, `la tonalité joue ses 6 notes (${b.audio.demarres} démarrées)`)
dire(b.message, 'le cockpit dit ce qu’on doit entendre')
dire(b.libelle, 'le bouton devient « Tester la tonalité » une fois le son ouvert')

/* Un deuxième appui ne doit pas empiler les contextes audio. */
await bouton.asElement()?.click()
await dodo(400)
const c = await p.evaluate(() => ({ ...window.__audio }))
dire(c.contextes === 1, 'un second appui ne crée pas un second contexte audio')
dire(c.demarres >= 12, `il rejoue la tonalité au second appui (${c.demarres} notes au total)`)

/* Le grand écran doit tenir aussi. */
await p.setViewport({ width: 1440, height: 900 })
await dodo(400)
const d = await p.evaluate(() => ({
  debordement: document.documentElement.scrollWidth > window.innerWidth + 1,
  veille: /La veille tourne/.test(document.body.innerText),
}))
dire(!d.debordement, 'aucun débordement horizontal en 1440 px')
dire(d.veille, 'la veille reste visible sur grand écran')

dire(errs.length === 0, `aucune erreur JavaScript (${errs.length})`)
if (errs.length) errs.slice(0, 4).forEach((e) => console.log('     ' + e.slice(0, 160)))

await nav.close()
srv.close()

console.log('')
ko.forEach((q) => console.log('  KO  ' + q))
console.log(`\n  ${ok.length} contrôles verts, ${ko.length} rouges\n`)
process.exit(ko.length ? 1 : 0)
