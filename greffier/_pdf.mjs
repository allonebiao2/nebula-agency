/* Le PDF A4 : un procès-verbal se signe sur papier. C'est la moitié du produit. */
import { chromium } from 'playwright'
import { createServer } from 'node:http'
import { readFile, mkdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'

const ICI = resolve(import.meta.dirname)
const corps = await readFile(join(ICI, 'maquette.html'), 'utf8')
const html = `<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
${corps.match(/<title>[\s\S]*?<\/title>/)?.[0] || ''}
${corps.match(/<style>[\s\S]*?<\/style>/)?.[0] || ''}
</head><body>${corps.replace(/<title>[\s\S]*?<\/title>/, '').replace(/<style>[\s\S]*?<\/style>/, '')}</body></html>`

const srv = createServer((_, res) => res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }).end(html))
await new Promise(r => srv.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${srv.address().port}/`
await mkdir(join(ICI, '_captures'), { recursive: true })

const nav = await chromium.launch({ args: ['--no-sandbox'], executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' })
const page = await nav.newPage({ viewport: { width: 1200, height: 1600 } })
await page.goto(base, { waitUntil: 'networkidle' })

/* la charte du client se change vraiment ? on le prouve en image */
await page.evaluate(() => window.scrollTo(0, 0))
await page.waitForTimeout(400)
await page.locator('.pastille[data-c="indigo"]').click()
await page.waitForTimeout(700)
const charte = await page.evaluate(() => ({
  attribut: document.documentElement.getAttribute('data-charte'),
  accent: getComputedStyle(document.documentElement).getPropertyValue('--accent-vif').trim(),
  presse: document.querySelector('.pastille[data-c="indigo"]').getAttribute('aria-pressed'),
}))
console.log('charte indigo :', JSON.stringify(charte))
await page.screenshot({ path: join(ICI, '_captures', 'charte-indigo.png'), clip: { x: 0, y: 0, width: 1200, height: 950 } })

/* retour au vert, puis le PDF */
await page.locator('.pastille[data-c=""]').click()
await page.waitForTimeout(400)
await page.emulateMedia({ media: 'print' })
await page.pdf({
  path: join(ICI, 'compte-rendu-specimen.pdf'),
  format: 'A4',
  printBackground: true,
  margin: { top: '14mm', bottom: '14mm', left: '16mm', right: '16mm' },
})
await nav.close(); srv.close()
console.log('PDF écrit')
