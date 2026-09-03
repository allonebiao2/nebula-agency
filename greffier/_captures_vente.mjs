/* On REGARDE la maquette avant de dire qu'elle est finie. 390 et 1440. */
import { chromium } from 'playwright'
import { createServer } from 'node:http'
import { readFile, mkdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'

const ICI = resolve(import.meta.dirname)
const SORTIE = join(ICI, '_captures_vente')
const PAGE = join(ICI, 'vente.html')

/* l'artefact est enveloppe dans un squelette au moment de la publication :
   on refait le meme enveloppement pour capturer ce que le lecteur verra. */
const corps = await readFile(PAGE, 'utf8')
const html = `<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
${corps.match(/<title>[\s\S]*?<\/title>/)?.[0] || ''}
${corps.match(/<style>[\s\S]*?<\/style>/)?.[0] || ''}
</head><body>${corps.replace(/<title>[\s\S]*?<\/title>/, '').replace(/<style>[\s\S]*?<\/style>/, '')}</body></html>`

const srv = createServer((req, res) => {
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }).end(html)
})
await new Promise(r => srv.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${srv.address().port}/`
await mkdir(SORTIE, { recursive: true })

const nav = await chromium.launch({ args: ['--no-sandbox'], executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' })
const soucis = []

for (const [nom, w, h] of [['390', 390, 844], ['1440', 1440, 900]]) {
  const page = await nav.newPage({ viewport: { width: +w, height: +h } })
  page.on('pageerror', e => soucis.push(`${nom} JS: ${String(e).slice(0, 140)}`))
  page.on('console', m => m.type() === 'error' && soucis.push(`${nom} console: ${m.text().slice(0, 140)}`))
  await page.goto(base, { waitUntil: 'networkidle' })
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 380) {
      window.scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 120))
    }
    window.scrollTo({ top: 0, behavior: 'instant' })
  })
  await page.waitForTimeout(2200)

  const r = await page.evaluate(() => {
    const deborde = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
    const petites = [...document.querySelectorAll('summary, details, a[href], button')]
      .filter(e => { const b = e.getBoundingClientRect(); return b.height > 1 && b.height < 44 })
      .map(e => (e.textContent || e.tagName).trim().slice(0, 30))
    const fixeSousTransform = []
    for (const el of document.querySelectorAll('*')) {
      if (getComputedStyle(el).position !== 'fixed') continue
      let p = el.parentElement
      while (p && p !== document.documentElement) {
        const s = getComputedStyle(p)
        if (s.transform !== 'none' || s.filter !== 'none') { fixeSousTransform.push(el.className); break }
        p = p.parentElement
      }
    }
    const police = getComputedStyle(document.querySelector('h1')).fontFamily
    return { deborde, petites, fixeSousTransform, police, hauteur: document.body.scrollHeight }
  })
  if (r.deborde) soucis.push(`${nom} : DEBORDEMENT horizontal`)
  if (r.petites.length) soucis.push(`${nom} : cibles < 44px -> ${r.petites.join(' | ')}`)
  if (r.fixeSousTransform.length) soucis.push(`${nom} : fixed sous transform -> ${r.fixeSousTransform.join(', ')}`)
  if (!/Bodoni/.test(r.police)) soucis.push(`${nom} : la police display n'est PAS chargee (${r.police})`)
  console.log(`${nom} : ${r.hauteur}px de haut, police ${r.police.split(',')[0]}`)

  await page.screenshot({ path: join(SORTIE, `plume-${nom}.png`), fullPage: true })
  // tranches lisibles
  let i = 0
  for (let y = 0; y < r.hauteur; y += Math.round(h * 0.92)) {
    await page.evaluate(yy => window.scrollTo({ top: yy, behavior: 'instant' }), y)
    await page.waitForTimeout(500)
    await page.screenshot({ path: join(SORTIE, `t${nom}-${String(++i).padStart(2, '0')}.png`) })
  }
  await page.close()
}
await nav.close(); srv.close()
console.log(soucis.length ? '\n⛔ ' + soucis.join('\n⛔ ') : '\n✅ aucun souci detecte')
