/*
  Contrôle du GÉNÉRATEUR · décisions 47 à 59.

  Le contrôle général (`_qc.js`) couvre la vitrine, le parcours de commande en
  six étapes, le paiement et le cockpit. Celui-ci ne s'occupe que du panneau :
  ce qui se voit sans cliquer, ce qui bouge quand on règle, et ce qui part vers
  l'écran de commande.

      node piste/_qc_generateur.js      (après « npx vite build »)
*/
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer-core'

const ICI = path.dirname(fileURLToPath(import.meta.url))
const DIST = path.join(ICI, 'dist')
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.woff2': 'font/woff2',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
}

/* ⚠️ Les libelles viennent des DONNEES, jamais d'une copie. « Ateliers de
   couture » est devenu « Couture et mode » le jour ou le moteur a ramene
   quinze metiers de plus, et tous les controles qui l'avaient en dur ont
   casse d'un coup. On lit la source. */
const D = await import('./src/donnees.js')
const M = (cle) => (D.METIERS.find((x) => x.cle === cle) || {}).nom || cle
const V = (cle) => (D.VILLES.find((x) => x.cle === cle) || {}).nom || cle

const ok = []
const ko = []
const dire = (bon, quoi) => (bon ? ok : ko).push(quoi)
const attendre = (ms) => new Promise((r) => setTimeout(r, ms))

const serveur = http.createServer((q, r) => {
  let f = path.join(DIST, decodeURIComponent(q.url.split('?')[0]))
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) f = path.join(DIST, 'index.html')
  r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' })
  r.end(fs.readFileSync(f))
})

;(async () => {
  if (!fs.existsSync(path.join(DIST, 'index.html'))) {
    console.log('  KO   dist/ est vide. Lancez « npx vite build » dans piste/ avant le contrôle.')
    process.exit(1)
  }
  await new Promise((r) => serveur.listen(0, r))
  const base = `http://127.0.0.1:${serveur.address().port}`
  const nav = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox'],
  })

  const erreurs = []
  const page = await nav.newPage()
  page.on('pageerror', (e) => erreurs.push(String(e)))
  page.on('console', (m) => {
    if (m.type() === 'error') erreurs.push(m.text())
  })

  const ouvrir = async () => {
    await page.goto(`${base}/?n=${Math.random().toString(36).slice(2)}`, {
      waitUntil: 'networkidle0',
    })
    await attendre(300)
  }
  const clic = async (txt, sel = 'button') => {
    const fait = await page.evaluate(
      (s, t) => {
        const e = [...document.querySelectorAll(s)].find(
          (x) => x.innerText.trim().startsWith(t) && !x.disabled
        )
        if (!e) return false
        e.click()
        return true
      },
      sel,
      txt
    )
    await attendre(260)
    return fait
  }
  /* Deux pieges evites ici.
     1. La vitrine porte DEJA une section de bareme avec les mots « A payer » :
        tout ce qui concerne le generateur se lit dans `#generateur`, sinon on
        mesure le voisin.
     2. Le CSS met certains libelles en CAPITALES, et `innerText` rend le texte
        transforme. Les expressions sont donc insensibles a la casse. */
  const texte = () =>
    page.evaluate(() => document.getElementById('generateur')?.innerText || '')
  const texteBarre = () =>
    page.evaluate(() =>
      [...document.querySelectorAll('div')]
        .filter(
          (e) =>
            getComputedStyle(e).position === 'fixed' &&
            e.getBoundingClientRect().bottom >= window.innerHeight - 2
        )
        .map((e) => e.innerText.replace(/\s+/g, ' ').trim())
        .join(' || ')
    )
  const lireTotal = () =>
    page.evaluate(() => {
      const g = document.getElementById('generateur')
      const dt = [...(g?.querySelectorAll('dt') || [])].find(
        (x) => x.innerText.trim().toLowerCase() === 'à payer'
      )
      if (!dt) return null
      const dd = dt.parentElement.querySelector('dd')
      return dd ? dd.innerText.replace(/[\s  ]/g, '').replace('F', '') : null
    })
  const phrase = () =>
    page.evaluate(() => {
      const p = document.querySelector('#generateur [data-phrase]')
      return (p?.innerText || '').replace(/\s+/g, ' ').trim()
    })

  /* ------------------------------------------- 1. il est là sans qu'on clique */
  await page.setViewport({ width: 390, height: 844 })
  await ouvrir()

  const surLePremierEcran = await page.evaluate(() => {
    const g = document.getElementById('generateur')
    if (!g) return null
    const b = g.getBoundingClientRect()
    return { haut: Math.round(b.top), visible: b.top < window.innerHeight }
  })
  dire(!!surLePremierEcran, `le générateur existe sur la vitrine, sans aucun clic`)
  dire(
    surLePremierEcran?.visible,
    `sur téléphone, le haut du générateur dépasse dans le premier écran (à ${surLePremierEcran?.haut} px)`
  )

  /* la phrase, avant tout réglage */
  let t = await texte()
  dire(/Je cherche/.test(await phrase()), `la phrase « Je cherche… » accueille le visiteur`)
  dire(!/à payer/i.test(t), `aucun prix n'est affiché avant le premier réglage`)

  /* ------------------------------------------------ 2. le prix dès le réglage */
  await clic(M('couture'))
  t = await texte()
  const P = (cle) => (D.METIERS.find((x) => x.cle === cle) || {}).pluriel || cle
  dire(
    new RegExp(P('couture'), 'i').test(await phrase()),
    `la phrase se réécrit avec le métier choisi (« ${P('couture')} »)`
  )
  dire(/Dans quelle ville/.test(t), `la question suivante apparaît sur le même panneau`)

  await clic(V('cotonou'))
  t = await texte()
  dire(/Je cherche.*Cotonou/.test(await phrase()), `la phrase porte maintenant la ville`)
  dire(/à payer/i.test(t), `le prix apparaît dès que le réglage suffit`)

  /* 50 fiches par défaut, aucune option : 100 x 50 = 5 000, remise 10 % = 4 500 */
  let total = await lireTotal()
  dire(total === '4500', `50 fiches sans option = 4 500 F, remise 10 % comprise (lu : ${total})`)

  /* ------------------------------------------------------- 3. les trois fiches */
  const apercu = await page.evaluate(() => {
    const c = [...document.querySelectorAll('.apercu-fiche')]
    return {
      nb: c.length,
      masques: c.filter((x) => /••/.test(x.innerText)).length,
      noms: c.map((x) => x.querySelector('p')?.innerText.trim()),
    }
  })
  dire(apercu.nb === 3, `trois fiches d'aperçu sont montrées (${apercu.nb})`)
  dire(
    apercu.masques === 3,
    `les trois numéros sont partiellement masqués (${apercu.masques} sur ${apercu.nb})`
  )

  const { FICHES, stock: stockDeja } = D
  const toutesVraies = apercu.noms.every((n) => FICHES.some((f) => f.nom === n))
  dire(toutesVraies, `les trois fiches sont de VRAIS commerces relevés`)

  /* elles changent quand la ville change */
  await clic(V('lome'))
  const apresLome = await page.evaluate(() =>
    [...document.querySelectorAll('.apercu-fiche')].map((x) => x.querySelector('p')?.innerText.trim())
  )
  dire(
    apresLome.join('|') !== apercu.noms.join('|'),
    `les fiches changent quand on change de ville`
  )
  const lomeOk = apresLome.every((n) => FICHES.some((f) => f.nom === n && f.ville === 'lome'))
  dire(lomeOk, `et ce sont bien des commerces de Lomé`)

  /* -------------------------------------------------------- 4. les paquets ---- */
  const paquets = await page.evaluate(() =>
    [...document.querySelectorAll('button')]
      .map((x) => x.innerText.trim())
      .filter((x) => ['10', '50', '100'].includes(x))
  )
  dire(paquets.length >= 2, `les paquets à appuyer sont proposés (${paquets.join(', ')})`)
  /* La regle, elle, ne bouge pas : on ne propose JAMAIS d'appuyer sur un
     nombre qu'on ne peut pas livrer. Le stock de couture a Lome change chaque
     nuit, alors on le lit au lieu de le figer. */
  const dispoLome = stockDeja('couture', 'lome')
  const trop = paquets.filter((p) => Number(p) > dispoLome)
  dire(
    trop.length === 0,
    `aucun paquet ne dépasse le stock réel de ${dispoLome} à Lomé${trop.length ? ' · ' + trop.join(',') : ''}`
  )

  await clic('10')
  total = await lireTotal()
  /* 10 fiches sans option : 100 x 10 = 1 000, aucune remise sous 50 */
  dire(total === '1000', `10 fiches sans option = 1 000 F, sans remise (lu : ${total})`)

  /* ------------------------------------------- 5. les suppléments et le message */
  await page.evaluate(() => {
    const e = [...document.querySelectorAll('[role="switch"]')].find((x) =>
      x.innerText.includes('Le numéro est testé')
    )
    e?.click()
  })
  await attendre(260)
  total = await lireTotal()
  /* (100 + 150) x 10 = 2 500, aucune remise */
  dire(total === '2500', `avec le numéro testé, 10 fiches = 2 500 F (lu : ${total})`)
  t = await texte()
  dire(/le numéro testé/.test(await phrase()), `la phrase dit maintenant l'option choisie`)

  await page.evaluate(() => {
    const e = [...document.querySelectorAll('[role="switch"]')].find((x) =>
      x.innerText.includes('Le message déjà écrit')
    )
    e?.click()
  })
  await attendre(300)
  t = await texte()
  dire(/Vous vendez quoi/.test(t), `cocher le message ouvre « vous vendez quoi ? »`)

  await clic('Commander')
  await attendre(400)
  dire(
    /Écrivez une phrase/.test(await texte()),
    `sans la phrase, la commande est refusée avec une explication`
  )

  await page.evaluate(() => {
    const t = document.querySelector('#offre')
    const set = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set
    set.call(t, 'je propose une assurance santé pensée pour les commerçants')
    t.dispatchEvent(new Event('input', { bubbles: true }))
  })
  await attendre(2800)
  const messageEcrit = await page.evaluate(() =>
    [...document.querySelectorAll('.apercu-fiche')].filter((x) =>
      /assurance santé/.test(x.innerText)
    ).length
  )
  dire(messageEcrit === 3, `le message s'écrit dans les trois fiches (${messageEcrit})`)

  /* -------------------------------------------- 6. le stock vide, et la demande */
  /* On CHERCHE une combinaison sous le minimum au lieu d'en supposer une : le
     moteur collecte chaque nuit, et « Autres villes du Bénin » etait vide ce
     matin, plein ce soir. Un controle qui fige une donnee vivante ment. */
  const { MINIMUM: MINI } = await import('./src/donnees.js')
  const stockDe = stockDeja
  let creux = null
  for (const m of D.METIERS.filter((x) => !x.horsStock).map((x) => x.cle)) {
    for (const v of D.VILLES.map((x) => x.cle)) {
      if (!creux && stockDe(m, v) < MINI) creux = [M(m), V(v)]
    }
  }
  dire(!!creux, `une combinaison sous le minimum existe et se teste${creux ? ` (${creux.join(' · ')})` : ''}`)

  await ouvrir()
  await clic(creux[0])
  await clic(creux[1])
  t = await texte()
  dire(/on ne va pas vous le vendre/i.test(t), `sans stock, le panneau bascule en « prévenez-moi »`)
  dire(!/à payer/i.test(t), `et aucun prix n'est affiché pour ce qu'on n'a pas`)

  await page.evaluate(() => {
    const e = document.querySelector('input[aria-label="Votre WhatsApp ou votre email"]')
    const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
    set.call(e, 'adjoa@exemple.com')
    e.dispatchEvent(new Event('input', { bubbles: true }))
  })
  await attendre(200)
  await clic('Prévenez-moi')
  dire(/C'est noté/.test(await texte()), `la demande est enregistrée et confirmée`)

  /* ------------------------------------- 7. « Un autre métier » n'est pas vendu */
  await ouvrir()
  await clic(M('autre'))
  t = await texte()
  dire(/on ne va pas vous le vendre/i.test(t), `un métier non relevé bascule aussi en demande`)

  /* -------------------------------- 8. de la vitrine au récapitulatif, direct - */
  await ouvrir()
  await clic(M('restaurant'))
  await clic(V('cotonou'))
  await clic('10')
  const avantDepart = await lireTotal()
  await clic('Commander')
  await attendre(700)
  t = await page.evaluate(() => document.body.innerText)
  const surRecap = /Votre prénom/.test(t) || /Envoyer ma commande sur WhatsApp/.test(t)
  dire(surRecap, `« Commander » mène DIRECTEMENT au récapitulatif, sans reposer les 6 questions`)
  dire(
    /Restaurants|restaurant/.test(t) && /Cotonou/.test(t),
    `le récapitulatif porte bien ce qui a été réglé dans le générateur`
  )
  /* Le prix ne doit pas bouger d'un ecran a l'autre. On compare des chiffres
     sans espaces : `fcfa()` compose en typographie francaise, avec une espace
     FINE INSECABLE entre les milliers, qu'aucune expression ecrite avec des
     espaces ordinaires ne retrouve. */
  const plat = t.replace(/[\s  ]/g, '')
  dire(
    plat.includes(avantDepart + 'F'),
    `et le même prix qu'affichait le générateur (${avantDepart} F)`
  )

  /* ------------------------------------------------ 9. la forme, aux deux tailles */
  for (const [nom, w, h] of [
    ['téléphone', 390, 844],
    ['PC', 1440, 1000],
  ]) {
    await page.setViewport({ width: w, height: h })
    await ouvrir()
    await clic(M('couture'))
    await clic(V('cotonou'))
    const forme = await page.evaluate(() => {
      const petites = [...document.querySelectorAll('#generateur button, #generateur input, #generateur textarea')]
        .filter((e) => {
          const b = e.getBoundingClientRect()
          return b.height > 0 && b.width > 0 && b.height < 44 && e.type !== 'range'
        })
        .map((e) => `${e.innerText?.slice(0, 20) || e.type} ${Math.round(e.getBoundingClientRect().height)}px`)
      return {
        deborde: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        petites,
        cadratin: /[\u2014\u2013]/.test(document.body.innerText),
      }
    })
    dire(forme.deborde <= 0, `${nom} : aucun débordement horizontal (${forme.deborde} px)`)
    dire(
      forme.petites.length === 0,
      `${nom} : aucune cible sous 44 px dans le générateur${
        forme.petites.length ? ' · ' + forme.petites.join(', ') : ''
      }`
    )
    dire(!forme.cadratin, `${nom} : aucun tiret cadratin`)
    await page.screenshot({
      path: path.join(ICI, '_qc_captures', `generateur-${nom}.png`),
      fullPage: false,
    })
  }

  /* la barre du bas, sur téléphone seulement */
  await page.setViewport({ width: 390, height: 844 })
  await ouvrir()
  await clic(M('couture'))
  await clic(V('cotonou'))
  const nbFixes = await page.evaluate(
    () =>
      [...document.querySelectorAll('div')].filter(
        (e) =>
          getComputedStyle(e).position === 'fixed' &&
          e.getBoundingClientRect().bottom >= window.innerHeight - 2
      ).length
  )
  const tb = await texteBarre()
  dire(nbFixes === 1, `une seule barre collée en bas, jamais deux (${nbFixes})`)
  dire(
    /à payer/i.test(tb) && /Commander/.test(tb),
    `elle porte le prix ET le bouton · « ${tb} »`
  )

  dire(erreurs.length === 0, `0 erreur JavaScript sur tout le parcours ${erreurs[0] || ''}`)

  await nav.close()
  serveur.close()

  ok.forEach((x) => console.log('  OK  ', x))
  ko.forEach((x) => console.log('  KO  ', x))
  console.log(`\n  ${ok.length} contrôles verts, ${ko.length} rouges`)
  process.exit(ko.length ? 1 : 0)
})()
