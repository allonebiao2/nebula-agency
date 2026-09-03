/* Regarder une page, section par section. Le vert ne prouve pas la beauté. */
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer-core'

const ICI = path.dirname(fileURLToPath(import.meta.url))
const DIST = path.join(ICI, 'dist')
/* ⚠️ Git Bash AVALE un argument qui commence par un dièse : `node _vue.mjs
   "#/cockpit"` arrive ici avec l'argument suivant. On passe donc la route SANS
   dièse (`cockpit`, `carnet/JETON`) et on le remet nous-mêmes. */
const ROUTE = '#/' + String(process.argv[2] || '').replace(/^#?\/?/, '')
const LARGE = Number(process.argv[3]) || 390
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' }

const srv = http.createServer((q, r) => {
  let f = path.join(DIST, decodeURIComponent(q.url.split('?')[0]))
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) f = path.join(DIST, 'index.html')
  r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' })
  r.end(fs.readFileSync(f))
})
await new Promise((r) => srv.listen(0, r))
const base = `http://127.0.0.1:${srv.address().port}`

const THEME = process.argv.includes('--sombre') ? 'sombre' : 'clair'

const nav = await puppeteer.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: 'new',
  args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'],
})
const p = await nav.newPage()
await p.setViewport({ width: LARGE, height: LARGE < 700 ? 844 : 1000 })
/* ⚠️ Aller d'abord sur `/` puis sur `/#/route` ne recharge RIEN : un
   changement de dièse est une navigation dans le même document, et la capture
   montre alors l'accueil en croyant montrer la page demandée. On pose le
   stockage AVANT le chargement et on ouvre l'adresse complète d'un coup. */
/* ⚠️ Le code passé au navigateur ne voit AUCUNE variable de Node : il est
   sérialisé puis évalué là-bas. `THEME` y valait « undefined », et la capture
   montrait le thème clair en croyant montrer le sombre. On passe la valeur en
   ARGUMENT, c'est le seul chemin. */
await p.evaluateOnNewDocument((t) => {
  try {
    localStorage.setItem('piste_cockpit_mdp', '19984')
    localStorage.setItem('piste_theme_cockpit', t)
  } catch (e) {}
}, THEME)
await p.goto(`${base}/${ROUTE}`, { waitUntil: 'networkidle0' })
await new Promise((r) => setTimeout(r, 2500))

if (process.argv.includes('--ouvrir')) {
  await p.evaluate(() => document.querySelector('.dossier-poignee')?.click())
  await new Promise((r) => setTimeout(r, 900))
  await p.evaluate(() => document.querySelector('.dossier')?.scrollIntoView({ block: 'start' }))
  await new Promise((r) => setTimeout(r, 400))
}

/* Capturer un ELEMENT plutot que la page : une page de cockpit fait 13 000 px
   de haut, et la regarder en entier revient a ne rien regarder. */
const cible = process.argv.find((a) => a.startsWith('--element='))
const dossier = path.join(ICI, '_qc_captures')
fs.mkdirSync(dossier, { recursive: true })
const nom = process.argv[4] || 'vue'
if (cible) {
  const sel = cible.slice('--element='.length)
  const el = await p.$(sel)
  if (!el) throw new Error(`element introuvable : ${sel}`)
  await el.evaluate((e) => e.scrollIntoView({ block: 'center' }))
  await new Promise((r) => setTimeout(r, 600))
  await el.screenshot({ path: path.join(dossier, `${nom}.png`) })
} else {
  await p.screenshot({ path: path.join(dossier, `${nom}.png`), fullPage: process.argv.includes('--tout') })
}
console.log('  capture :', path.join(dossier, `${nom}.png`))
await nav.close()
srv.close()
