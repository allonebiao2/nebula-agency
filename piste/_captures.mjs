/* Les captures : on REGARDE, section par section, en 390 et en 1440.
   Six défauts sont passés au travers de 53 contrôles verts sur la vitrine
   Hillary. Le vert ne remplace pas l'œil. */
import { chromium } from 'playwright'
import { createServer } from 'node:http'
import { readFile, stat, mkdir } from 'node:fs/promises'
import { extname, join, resolve } from 'node:path'

const DIST = resolve(import.meta.dirname, 'dist')
const SORTIE = resolve(import.meta.dirname, '_captures')
const TYPES = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.woff2':'font/woff2' }

const srv = createServer(async (req,res)=>{
  const c = decodeURIComponent(req.url.split('?')[0])
  let f = join(DIST, c === '/' ? 'index.html' : c)
  try { if ((await stat(f)).isDirectory()) f = join(f,'index.html') } catch { f = join(DIST,'index.html') }
  try { res.writeHead(200,{'content-type':TYPES[extname(f)]||'application/octet-stream'}).end(await readFile(f)) }
  catch { res.writeHead(404).end('x') }
})
await new Promise(r=>srv.listen(0,'127.0.0.1',r))
const base = `http://127.0.0.1:${srv.address().port}`
await mkdir(SORTIE, { recursive: true })

const chemins = []
for (const m of ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome']) chemins.push(m)
const nav = await chromium.launch({args:['--no-sandbox'], executablePath: chemins[0]})

for (const [nom, w, h] of [['390', 390, 844], ['1440', 1440, 900]]) {
  const page = await nav.newPage({ viewport: { width: w, height: h } })
  for (const [route, titre] of [['#/','accueil'], ['#/origine','origine']]) {
    await page.goto(base + '/' + route, { waitUntil: 'networkidle' })
    // dérouler doucement pour déclencher toutes les révélations
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 400) {
        window.scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 110))
      }
      window.scrollTo({ top: 0, behavior: 'instant' })
    })
    await page.waitForTimeout(1500)
    await page.screenshot({ path: join(SORTIE, `${titre}-${nom}.png`), fullPage: true })
  }
  // le questionnaire, écran par écran
  await page.goto(base + '/#/commander', { waitUntil: 'networkidle' })
  await page.screenshot({ path: join(SORTIE, `q1-metier-${nom}.png`), fullPage: true })
  await page.getByRole('button', { name: /Ateliers de couture/ }).click()
  await page.getByRole('button', { name: /^Continuer$/ }).click()
  await page.waitForTimeout(200)
  await page.screenshot({ path: join(SORTIE, `q2-ville-${nom}.png`), fullPage: true })
  await page.getByRole('button', { name: /Cotonou et ses environs/ }).click()
  await page.getByRole('button', { name: /^Continuer$/ }).click()
  await page.waitForTimeout(150)
  await page.getByRole('button', { name: /^Continuer$/ }).click()
  await page.waitForTimeout(200)
  await page.screenshot({ path: join(SORTIE, `q4-nombre-${nom}.png`), fullPage: true })
  await page.getByRole('button', { name: /^50$/ }).click()
  await page.getByRole('button', { name: /^Continuer$/ }).click()
  await page.waitForTimeout(200)
  await page.screenshot({ path: join(SORTIE, `q5-options-${nom}.png`), fullPage: true })
  await page.getByRole('button', { name: /^Continuer$/ }).click()
  await page.getByLabel(/qu'est-ce que vous proposez/i).fill('je propose une assurance santé aux commerçants et à leurs employés')
  await page.waitForTimeout(600)
  await page.screenshot({ path: join(SORTIE, `q6-offre-${nom}.png`), fullPage: true })
  await page.getByRole('button', { name: /^Continuer$/ }).click()
  await page.waitForTimeout(200)
  await page.getByLabel('Votre nom et prénom').fill('Awa Koudjo')
  await page.getByLabel(/Votre email/).fill('awa@exemple.com')
  await page.getByLabel(/Votre WhatsApp/).fill('+229 0196000000')
  await page.getByLabel(/numéro depuis lequel vous paierez/).fill('0196000000')
  await page.screenshot({ path: join(SORTIE, `q7-vous-${nom}.png`), fullPage: true })
  await page.getByRole('button', { name: /Voir comment payer/ }).click()
  await page.waitForTimeout(400)
  await page.screenshot({ path: join(SORTIE, `paiement-${nom}.png`), fullPage: true })
  // le cockpit
  await page.goto(base + '/#/cockpit', { waitUntil: 'networkidle' })
  await page.getByLabel('mot de passage').fill('piste')
  await page.getByRole('button', { name: 'Entrer' }).click()
  await page.waitForTimeout(300)
  await page.screenshot({ path: join(SORTIE, `cockpit-vide-${nom}.png`), fullPage: true })
  await page.close()
}
await nav.close(); srv.close()
console.log('captures dans _captures/')
