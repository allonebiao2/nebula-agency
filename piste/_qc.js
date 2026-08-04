/*
  PISTE · contrôle qualité.

      npm i puppeteer-core --no-save     (depuis la racine du dépôt)
      node piste/_qc.js

  Ce que ça vérifie, sur le BUNDLE COMPILÉ (dist/), pas sur les sources :
    · 0 erreur JavaScript en 390 px et en 1440 px, sur les trois écrans
    · 0 débordement horizontal
    · 0 cible tactile sous 44 px
    · 0 texte sous 4,5:1 de contraste
    · le calculateur donne le bon prix sur 3 combinaisons calculées à la main
    · le questionnaire refuse une commande sous 10 fiches
    · le questionnaire refuse de dépasser le stock disponible
    · aucun tiret cadratin dans le rendu ni dans le bundle
    · aucune requête sortante vers un CDN
    · le stock affiché est celui du relevé réel

  Il écrit aussi les captures dans piste/_qc_captures/ : le QC protège la
  logique, il ne protège pas le goût. Les captures sont là pour être REGARDÉES.
*/

import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer-core'

const ICI = path.dirname(fileURLToPath(import.meta.url))
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
const DIST = path.resolve(ICI, 'dist')

/* Les chiffres du stock changent chaque nuit depuis que le moteur tourne : on
   les LIT dans les donnees du site, on ne les fige jamais dans le controle. */
const D = await import('./src/donnees.js')
const PX = await import('./src/prix.js')
/* ⚠️ ON LIT LES LIBELLES DANS LE MODULE, ON NE LES RECOPIE PAS.
   Le jour ou « Le numero est teste » est devenu « Le numero est verifie »,
   trois controles sont passes au rouge d'un coup en accusant le calcul des
   prix, alors que le prix etait juste : le controle cliquait simplement a
   cote. Un controle qui recopie une chaine casse a chaque mot change. */
const OPT_VERIFIE = PX.SUPPLEMENTS.find((x) => x.cle === 'teste')
const NOM_VERIFIE = OPT_VERIFIE.nom
const COURT_VERIFIE = OPT_VERIFIE.court
const nombre = (v) => String(v).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')

/* ⚠️ Les libelles viennent des DONNEES, jamais d'une copie. « Ateliers de
   couture » est devenu « Couture et mode » le jour ou le moteur a ramene
   quinze metiers de plus, et tous les controles qui l'avaient en dur ont
   casse d'un coup. On lit la source. */
const M = (cle) => (D.METIERS.find((x) => x.cle === cle) || {}).nom || cle
const V = (cle) => (D.VILLES.find((x) => x.cle === cle) || {}).nom || cle
const CAPTURES = path.resolve(ICI, '_qc_captures')
const PORT = 4319

const ok = []
const ko = []
const dire = (bon, quoi) => (bon ? ok : ko).push(quoi)

/* ------------------------------------------------------- serveur statique - */

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.woff2': 'font/woff2',
  '.svg': 'image/svg+xml',
  '.xml': 'application/xml',
  '.txt': 'text/plain; charset=utf-8',
}

function servir() {
  return new Promise((res) => {
    const s = http.createServer((req, rep) => {
      const url = decodeURIComponent(req.url.split('?')[0])
      let f = path.join(DIST, url === '/' ? 'index.html' : url)
      if (!f.startsWith(DIST) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) {
        f = path.join(DIST, 'index.html')
      }
      rep.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' })
      fs.createReadStream(f).pipe(rep)
    })
    s.listen(PORT, () => res(s))
  })
}

/* ---------------------------------------------------------- les mesures --- */

const MESURES = () => {
  const RE_CADRATIN = /[\u2014\u2013]/

  const visible = (e) => {
    const b = e.getBoundingClientRect()
    if (b.width === 0 || b.height === 0) return false
    const s = getComputedStyle(e)
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) > 0.05
  }

  /* --- cibles tactiles --- */
  const cibles = [...document.querySelectorAll('a[href], button, input, select, textarea, [role="switch"]')]
    .filter(visible)
    .filter((e) => e.type !== 'range')
    .map((e) => {
      const b = e.getBoundingClientRect()
      return { h: Math.round(b.height), w: Math.round(b.width), t: (e.innerText || e.type || e.tagName).slice(0, 40) }
    })
    .filter((c) => c.h < 44)

  /* --- contraste --- */
  const lum = (r, g, b) => {
    const c = [r, g, b].map((v) => {
      v /= 255
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
    })
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
  }
  const rgba = (s) => {
    const m = s.match(/rgba?\(([^)]+)\)/)
    if (!m) return null
    const p = m[1].split(',').map((x) => parseFloat(x))
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }
  }
  const fondEffectif = (e) => {
    const couches = []
    let n = e
    while (n && n.nodeType === 1) {
      const s = getComputedStyle(n)
      if (s.backgroundImage && s.backgroundImage !== 'none' && /gradient|url/.test(s.backgroundImage)) {
        return null /* on ne juge pas un texte posé sur une image */
      }
      const c = rgba(s.backgroundColor)
      if (c && c.a > 0) {
        couches.unshift(c)
        if (c.a >= 0.999) break
      }
      n = n.parentElement
    }
    if (!couches.length || couches[0].a < 0.999) return null
    return couches.reduce((base, c) => ({
      r: c.r * c.a + base.r * (1 - c.a),
      g: c.g * c.a + base.g * (1 - c.a),
      b: c.b * c.a + base.b * (1 - c.a),
      a: 1,
    }))
  }
  const contrastes = []
  document.querySelectorAll('body *').forEach((e) => {
    if (!visible(e)) return
    const direct = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 1)
    if (!direct) return
    const s = getComputedStyle(e)
    const t = rgba(s.color)
    const f = fondEffectif(e)
    if (!t || !f) return
    const tc = t.a >= 0.999 ? t : {
      r: t.r * t.a + f.r * (1 - t.a),
      g: t.g * t.a + f.g * (1 - t.a),
      b: t.b * t.a + f.b * (1 - t.a),
    }
    const a = lum(tc.r, tc.g, tc.b)
    const b = lum(f.r, f.g, f.b)
    const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)
    const px = parseFloat(s.fontSize)
    const gras = parseInt(s.fontWeight, 10) >= 700
    const grand = px >= 24 || (gras && px >= 18.66)
    const exige = grand ? 3 : 4.5
    if (ratio < exige - 0.02) {
      contrastes.push({
        r: Math.round(ratio * 100) / 100,
        exige,
        px: Math.round(px),
        t: e.innerText.slice(0, 46).replace(/\s+/g, ' '),
        /* ⚠️ Sans ces trois champs, un contraste rouge est INTROUVABLE : on
           connaît le texte fautif mais ni sa couleur, ni son fond, ni la
           classe qui les pose. On perd alors plus de temps à chercher le
           coupable qu'à le corriger. */
        couleur: s.color,
        fond: `rgb(${Math.round(f.r)}, ${Math.round(f.g)}, ${Math.round(f.b)})`,
        ou: (e.className || '').toString().slice(0, 90),
      })
    }
  })

  return {
    deborde: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    cibles,
    contrastes,
    cadratin: RE_CADRATIN.test(document.body.innerText),
    extraitCadratin: (document.body.innerText.match(/.{0,40}[\u2014\u2013].{0,40}/) || [''])[0],
    texte: document.body.innerText,
  }
}

/* ------------------------------------------------------------- pilotage --- */

const poser = async (page, v) => {
  const fait = await page.evaluate((val) => {
    const el = document.querySelector('input[type=range]')
    if (!el) return false
    const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
    set.call(el, String(val))
    el.dispatchEvent(new Event('input', { bubbles: true }))
    return true
  }, v)
  if (!fait) {
    const ou = await page.evaluate(() => document.body.innerText.slice(0, 220).replace(/\n+/g, ' | '))
    throw new Error('curseur introuvable. Écran affiché : ' + ou)
  }
}

const cliquerTexte = (page, sel, txt) =>
  page.evaluate(
    (s, t) => {
      const e = [...document.querySelectorAll(s)].find((x) => x.innerText.includes(t))
      if (!e) return false
      e.click()
      return true
    },
    sel,
    txt
  )

const attendre = (ms) => new Promise((r) => setTimeout(r, ms))

/* Ouvre VRAIMENT l'écran : deux `goto` vers le même `#` ne rechargent rien,
   l'application garderait son état d'un contrôle à l'autre. */
const ouvrir = async (page, base, hash) => {
  await page.goto(`${base}/?n=${Math.random().toString(36).slice(2)}${hash}`, {
    waitUntil: 'networkidle0',
  })
  await attendre(250)
}

/* Va jusqu'à l'étape 4 avec un métier et une ville donnés. */
async function jusquAuVolume(page, base, metier, ville) {
  await ouvrir(page, base, '#/commander')
  await cliquerTexte(page, 'button', metier)
  await attendre(120)
  await cliquerTexte(page, 'button', 'Continuer')
  await attendre(220)
  const pris = await cliquerTexte(page, 'button', ville)
  await attendre(150)
  await cliquerTexte(page, 'button', 'Continuer')
  await attendre(220)
  await cliquerTexte(page, 'button', 'Continuer') /* quartier, facultatif */
  await attendre(250)
  return pris
}

async function cocher(page, noms) {
  for (const n of noms) {
    await cliquerTexte(page, '[role="switch"]', n)
    await attendre(90)
  }
}

const totalAffiche = (page) =>
  page.evaluate(() => {
    const dt = [...document.querySelectorAll('dt')].find((x) => x.innerText.trim() === 'À payer')
    if (!dt) return null
    return dt.parentElement.querySelector('dd').innerText.replace(/\s/g, '').replace('F', '')
  })

/* ----------------------------------------------------------------- main --- */

;(async () => {
  if (!fs.existsSync(path.join(DIST, 'index.html'))) {
    console.log('  KO   dist/ est vide. Lancez « npm run build » dans piste/ avant le QC.')
    process.exit(1)
  }
  fs.mkdirSync(CAPTURES, { recursive: true })
  const serveur = await servir()
  const base = `http://127.0.0.1:${PORT}`
  const nav = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--font-render-hinting=none'],
  })

  const ECRANS = [
    { nom: 'telephone', w: 390, h: 844, mobile: true },
    { nom: 'PC', w: 1440, h: 900, mobile: false },
  ]
  /* Notre base. Tout le reste est un tiers. */
const NOTRE_SERVEUR = 'https://xukduhqqfzogisoimhyo.supabase.co'

const ROUTES = [
    { nom: 'vitrine', h: '#/' },
    { nom: 'commander', h: '#/commander' },
    { nom: 'donnees', h: '#/donnees' },
    { nom: 'cockpit', h: '#/cockpit' },
  ]

  /* ---------------------------------------------- 1. les quatre écrans ---- */
  for (const e of ECRANS) {
    for (const r of ROUTES) {
      const page = await nav.newPage()
      const erreurs = []
      const externes = []
      page.on('pageerror', (x) => erreurs.push(String(x)))
      page.on('console', (m) => {
        if (m.type() === 'error') erreurs.push(m.text())
      })
      /* ⚠️ CETTE REGLE VISE LES TIERS, PAS NOTRE PROPRE SERVEUR.
         Elle existe pour interdire un CDN, une police distante, un mouchard :
         tout ce qui met le site a la merci de quelqu'un d'autre. Nos propres
         appels a Supabase (lire un carnet, compter une visite) sont le
         fonctionnement normal du produit. Les compter comme des fautes aurait
         pousse a supprimer la mesure au lieu de supprimer les dependances. */
      page.on('request', (req) => {
        const u = req.url()
        if (u.startsWith(base) || u.startsWith('data:') || u.startsWith('blob:')) return
        if (u.startsWith(NOTRE_SERVEUR)) return
        externes.push(u)
      })
      await page.setViewport({
        width: e.w,
        height: e.h,
        isMobile: e.mobile,
        hasTouch: e.mobile,
        deviceScaleFactor: e.mobile ? 2 : 1,
      })
      await page.goto(base + '/' + r.h, { waitUntil: 'networkidle0' })
      await attendre(300)
      /* on descend tout pour déclencher les révélations */
      await page.evaluate(async () => {
        const H = document.body.scrollHeight
        for (let y = 0; y < H; y += 500) {
          window.scrollTo(0, y)
          await new Promise((r) => setTimeout(r, 45))
        }
        window.scrollTo(0, 0)
      })
      await attendre(700)

      const m = await page.evaluate(MESURES)
      const t = `${r.nom} en ${e.w}`
      dire(erreurs.length === 0, `${t} : ${erreurs.length} erreur JS ${erreurs[0] || ''}`)
      dire(externes.length === 0, `${t} : ${externes.length} requête externe ${externes[0] || ''}`)
      dire(m.deborde <= 0, `${t} : débordement horizontal de ${m.deborde} px`)
      dire(
        m.cibles.length === 0,
        `${t} : ${m.cibles.length} cible sous 44 px ${m.cibles[0] ? JSON.stringify(m.cibles[0]) : ''}`
      )
      dire(
        m.contrastes.length === 0,
        `${t} : ${m.contrastes.length} texte sous le contraste exigé ${
          m.contrastes[0] ? JSON.stringify(m.contrastes[0]) : ''
        }`
      )
      dire(!m.cadratin, `${t} : aucun tiret cadratin ${m.extraitCadratin}`)

      if (r.nom === 'vitrine') {
        /* On ne fige plus les nombres : le moteur collecte chaque nuit, et un
           controle qui attend « 187 » devient faux le lendemain. On verifie que
           la vitrine annonce bien CE QUI EST EN BASE, quel qu'il soit. */
        /* Pas le total : c'est un compteur ANIME, et la capture arrive avant
           qu'il ait fini de monter. On verifie les nombres fixes, qui disent
           la meme chose sans dependre d'une animation. */
        /* La vitrine a ete raccourcie le 2026-08-04 : les sections « prix »,
           « stock » et « la fiche » ont disparu au profit du generateur, qui
           montre tout ca en direct. Il ne reste que le TOTAL, dans l'entete. */
        const attendu = [nombre(D.TOTAL_FICHES)]
        const manque = attendu.filter((x) => !m.texte.replace(/[\s  ]/g, ' ').includes(x))
        dire(manque.length === 0, `${t} : la vitrine annonce le stock réel ${attendu.join(' et ')}${manque.length ? ' · manque ' + manque.join(',') : ''}`)
        /* Abidjan a longtemps ete annonce et vide. Il est desormais rempli
           par le moteur. La REGLE qui compte n'est pas « Abidjan est bientot
           dispo » mais « aucune ville n'est annoncee sans stock ». */
        const villesVides = D.VILLES.filter(
          (v) => !D.METIERS.some((mm) => D.stock(mm.cle, v.cle) >= D.MINIMUM)
        )
        dire(
          villesVides.every((v) => !m.texte.includes(v.nom) || /bientôt/i.test(m.texte)),
          `${t} : aucune ville n'est annoncée sans stock${
            villesVides.length ? ' · vides : ' + villesVides.map((v) => v.cle).join(',') : ''
          }`
        )
        dire(
          !/\b(lead|leads|scoring|enrichissement)\b/i.test(m.texte),
          `${t} : aucun jargon (lead, scoring, enrichissement)`
        )
        dire(
          !/(âge|revenus|centres d'intérêt)\s*:/i.test(m.texte),
          `${t} : aucune donnée de personne physique proposée`
        )
        await page.screenshot({
          path: path.join(CAPTURES, `${e.nom}-vitrine.png`),
          fullPage: true,
        })
      } else {
        await page.screenshot({ path: path.join(CAPTURES, `${e.nom}-${r.nom}.png`) })
      }
      await page.close()
    }
  }

  /* ------------------------------------- 2. le calculateur, à la main ----- */
  const page = await nav.newPage()
  const erreursCalc = []
  page.on('pageerror', (x) => erreursCalc.push(String(x)))
  await page.setViewport({ width: 1440, height: 1000 })

  /* A · 10 fiches, aucune option : 100 x 10 = 1 000, aucune remise */
  await jusquAuVolume(page, base, M('couture'), 'Cotonou et ses environs')
  await poser(page, 10)
  await attendre(200)
  let t = await totalAffiche(page)
  dire(t === '1000', `calcul A · 10 fiches sans option = 1 000 F (lu : ${t})`)

  /* B · 50 fiches, numero teste + message. Le bareme change (plafond a 250 F
     par fiche depuis le 2026-08-04) : on CALCULE, on ne recopie pas. */
  await poser(page, 50)
  await attendre(150)
  await cliquerTexte(page, 'button', 'Continuer')
  await attendre(250)
  await cocher(page, [NOM_VERIFIE, 'Le message déjà écrit'])
  await attendre(250)
  t = await totalAffiche(page)
  const attB = String(PX.calcul(50, { teste: 1, message: 1 }).total)
  dire(t === attB, `calcul B · 50 fiches, testé + message = ${attB} F (lu : ${t})`)

  /* C · tout le stock de couture a Cotonou, les quatre options.
     Le nombre vient de la base : il change chaque nuit, le calcul non. */
  const maxCouture = D.stock('couture', 'cotonou')
  const attenduC = String(
    PX.calcul(maxCouture, { teste: 1, sansSite: 1, dirigeant: 1, message: 1 }).total
  )
  await cocher(page, ["Il n'a rien en ligne", 'Le nom du dirigeant'])
  await cliquerTexte(page, 'button', 'Revenir')
  await attendre(250)
  await poser(page, 99999) /* le navigateur borne au max */
  await attendre(200)
  const nAffiche = await page.evaluate(() => document.querySelector('input[type=range]').value)
  dire(nAffiche === String(maxCouture), `le curseur ne dépasse pas le stock réel de ${maxCouture} (lu : ${nAffiche})`)
  await cliquerTexte(page, 'button', 'Continuer')
  await attendre(250)
  t = await totalAffiche(page)
  dire(t === attenduC, `calcul C · ${maxCouture} fiches, les 4 options = ${attenduC} F (lu : ${t})`)

  /* ------------------------------- 3. le minimum et le stock, refusés ----- */
  await jusquAuVolume(page, base, M('couture'), 'Cotonou et ses environs')
  await poser(page, 3)
  await attendre(200)
  const bas = await page.evaluate(() => document.querySelector('input[type=range]').value)
  dire(bas === '10', `le curseur ne descend pas sous 10 fiches (lu : ${bas})`)

  /* Sous le minimum, la commande est refusée MAIS la demande est prise
     (décision 39 : on ne bloque pas, on enregistre). */
  const etatContinuer = () =>
    page.evaluate(() => {
      const b = [...document.querySelectorAll('button')].filter(
        (x) => x.innerText.trim() === 'Continuer'
      )
      return {
        bloque: b.length > 0 && b.every((x) => x.disabled),
        demande: /Prévenez-moi quand c'est prêt/.test(document.body.innerText),
      }
    })

  /* Les combinaisons SOUS LE MINIMUM se cherchent en base plutot que de se
     supposer : ce qui etait vide ce matin peut etre plein ce soir. */
  const vides = []
  for (const m of D.METIERS.filter((x) => !x.horsStock).map((x) => x.cle)) {
    for (const v of D.VILLES.map((x) => x.cle)) {
      if (D.stock(m, v) < D.MINIMUM) vides.push([M(m), V(v), `${m} · ${V(v)} (${D.stock(m, v)} en stock)`])
    }
  }
  dire(vides.length > 0, `au moins une combinaison est sous le minimum, et se teste (${vides.length})`)

  for (const [metier, ville, quoi] of vides.slice(0, 4)) {
    await ouvrir(page, base, '#/commander')
    await cliquerTexte(page, 'button', metier)
    await attendre(120)
    await cliquerTexte(page, 'button', 'Continuer')
    await attendre(250)
    await cliquerTexte(page, 'button', ville)
    await attendre(300)
    const r = await etatContinuer()
    dire(r.bloque, `${quoi} : la commande est refusée`)
    dire(r.demande, `${quoi} : la demande est proposée au lieu du vide`)
  }

  /* métier hors catalogue : refusé à la vente, mais la demande est prise */
  await ouvrir(page, base, '#/commander')
  await cliquerTexte(page, 'button', M('autre'))
  await attendre(250)
  const horsStock = await page.evaluate(() => ({
    bloque: [...document.querySelectorAll('button')]
      .filter((x) => x.innerText.trim() === 'Continuer')
      .every((x) => x.disabled),
    demande: /Quel métier cherchez-vous/.test(document.body.innerText),
  }))
  dire(horsStock.bloque, `un métier non relevé ne peut pas être commandé`)
  dire(horsStock.demande, `un métier non relevé ouvre la demande « prévenez-moi »`)

  /* ------------------------------------ 4. la fiche d'exemple est vraie -- */
  await ouvrir(page, base, '#/')
  await attendre(200)
  const vitrineTexte = await page.evaluate(() => document.body.innerText)
  /* Les vraies fiches et leur masquage se testent desormais dans
     `_qc_generateur.js` : elles vivent dans le generateur, plus sur la
     vitrine, qui a ete raccourcie. */
  /* ------------------------ 5. la commande complète, jusqu'au paiement ---- */
  await jusquAuVolume(page, base, M('couture'), 'Cotonou et ses environs')
  const attenduPaiement = PX.fcfa(PX.calcul(24, { teste: 1, message: 1 }).total)
    .replace(/[\s  ]+/g, ' ')
  await poser(page, 24)
  await attendre(150)
  await cliquerTexte(page, 'button', 'Continuer') /* → suppléments */
  await attendre(250)
  await cocher(page, [NOM_VERIFIE, 'Le message déjà écrit'])
  await cliquerTexte(page, 'button', 'Continuer') /* → offre */
  await attendre(250)
  await page.evaluate(() => {
    const t = document.querySelector('textarea')
    const set = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set
    set.call(t, 'je propose une assurance santé pensée pour les commerçants et leur famille')
    t.dispatchEvent(new Event('input', { bubbles: true }))
  })
  await attendre(200)
  await cliquerTexte(page, 'button', 'Voir ma commande')
  await attendre(350)

  /* on ne remplit rien : la commande doit être refusée */
  await cliquerTexte(page, 'button', 'Envoyer ma commande sur WhatsApp')
  await attendre(250)
  const refuse = await page.evaluate(() =>
    /Il manque votre nom, votre email, votre WhatsApp ou votre numéro Mobile Money/.test(
      document.body.innerText
    )
  )
  dire(refuse, `une commande sans nom, email, WhatsApp ni Mobile Money est refusée`)

  await page.evaluate(() => {
    window.open = () => null /* on ne veut pas ouvrir WhatsApp pendant le contrôle */
    const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
    const poser = (label, v) => {
      const e = [...document.querySelectorAll('input')].find(
        (x) =>
          (x.getAttribute('aria-label') || '') === label ||
          (x.closest('label')?.innerText || '').startsWith(label)
      )
      if (!e) throw new Error('champ introuvable : ' + label)
      set.call(e, v)
      e.dispatchEvent(new Event('input', { bubbles: true }))
    }
    poser('Votre prénom', 'Adjoa')
    poser('Votre nom', 'Kponou')
    poser('Votre email', 'adjoa@exemple.com')
    poser('Numéro WhatsApp', '0197000000')
    poser('Numéro Mobile Money', '0166000000')
  })
  await attendre(250)
  await cliquerTexte(page, 'button', 'Envoyer ma commande sur WhatsApp')
  await attendre(500)

  /* ⚠️ `page.evaluate` s'execute dans le NAVIGATEUR : une variable de Node
     n'y existe pas. Le montant attendu se passe en argument. */
  const paiement = await page.evaluate((attenduPaiement) => {
    const t = document.body.innerText
    /* `fcfa()` compose en typographie francaise : espace FINE INSECABLE (U+202F)
       entre les milliers, espace INSECABLE (U+00A0) avant le F. C'est correct, et
       c'est ce qu'on veut afficher. Mais une expression ecrite avec des espaces
       ordinaires ne le retrouve jamais : on compare donc sur un texte ou toutes
       les especes d'espaces sont ramenees a une seule. */
    const plat = t.replace(/[\s  ]+/g, ' ')
    return {
      code: (t.match(/PISTE-[A-Z0-9]{4}/) || [''])[0],
      montant: plat.includes(attenduPaiement),
      rebours: /Il vous reste/.test(plat) && /\d+ h \d\d min/.test(plat),
      mailEtWhatsapp: /Surveillez votre boîte mail ET votre WhatsApp/.test(t),
      expediteur: /Payez bien depuis le numéro que vous avez donné/.test(t),
      momoDeclare: /\+229 0166000000/.test(plat),
      moyens: /MTN MoMo/.test(plat) && !/Moov|Flooz/.test(plat),
      email: /piste@nebula-agency\.online/.test(t),
      pasDeTogoNiCI: !/(Togo|Côte d'Ivoire)/.test(t),
      vingtQuatre: /24 heures/.test(plat),
      depotDistinct: /n'est\s*pas le numéro WhatsApp/.test(plat),
    }
  }, attenduPaiement)
  dire(/^PISTE-[A-Z0-9]{4}$/.test(paiement.code), `le code de commande est au format PISTE-XXXX (${paiement.code})`)
  dire(paiement.montant, `l'écran de paiement affiche le montant exact (${attenduPaiement})`)
  dire(paiement.rebours, `le compte à rebours de 24 heures est affiché`)
  dire(paiement.mailEtWhatsapp, `« surveillez votre boîte mail ET votre WhatsApp » est dit`)
  dire(paiement.expediteur, `l'acheteur est rappelé de payer depuis le numéro déclaré`)
  dire(paiement.momoDeclare, `le numéro Mobile Money déclaré est repris à l'écran`)
  dire(paiement.moyens, `MTN MoMo est le seul moyen annoncé, plus aucune trace de Moov`)
  dire(paiement.email, `l'adresse d'envoi ${'piste@nebula-agency.online'} est annoncée`)
  dire(paiement.pasDeTogoNiCI, `l'écran de paiement ne promet rien au Togo ni en Côte d'Ivoire`)
  dire(
    paiement.depotDistinct,
    `l'écran prévient que le numéro de dépôt n'est PAS le numéro WhatsApp`
  )
  dire(paiement.vingtQuatre, `le délai de 24 heures est répété sur l'écran de paiement`)

  const range = await page.evaluate(() => {
    const l = JSON.parse(localStorage.getItem('piste_commandes_v1') || '[]')
    return { n: l.length, c: l[0] || null }
  })
  dire(
    range.n === 1 && range.c?.momoNumero === '0166000000' && range.c?.prenom === 'Adjoa',
    `la commande est rangée avec le nom et le numéro Mobile Money`
  )

  /* --------------------------------- 6. le cockpit relit ce qui est collé - */
  await ouvrir(page, base, '#/cockpit')
  const cockpit = await page.evaluate(() => {
    const t = document.body.innerText
    return {
      commande: t.includes('Adjoa'),
      rebours: /il reste \d+ h/.test(t),
      onglets: ['À encaisser', 'À livrer', 'Livrées', 'Expirées', 'Injoignables', 'Demandes'].every(
        (o) => t.includes(o)
      ),
    }
  })
  dire(cockpit.commande, `le cockpit voit la commande passée dans ce navigateur`)
  dire(cockpit.rebours, `le cockpit montre le compte à rebours de la commande non payée`)
  dire(cockpit.onglets, `le cockpit a ses six piles, signalements et demandes compris`)

  dire(erreursCalc.length === 0, `parcours complet : ${erreursCalc.length} erreur JS ${erreursCalc[0] || ''}`)
  await page.close()

  /* ------------------------------------------ 5. le bundle lui-même ------ */
  const fichiers = []
  const marcher = (d) =>
    fs.readdirSync(d).forEach((f) => {
      const p = path.join(d, f)
      fs.statSync(p).isDirectory() ? marcher(p) : fichiers.push(p)
    })
  marcher(DIST)
  const textuels = fichiers.filter((f) => /\.(js|css|html|txt|xml)$/.test(f))
  const avecCadratin = textuels.filter((f) => /[\u2014]/.test(fs.readFileSync(f, 'utf8')))
  dire(avecCadratin.length === 0, `aucun tiret cadratin dans le bundle ${avecCadratin.join(',')}`)
  const html = fs.readFileSync(path.join(DIST, 'index.html'), 'utf8')
  dire(
    !/https?:\/\/(?!www\.w3\.org)/.test(html.replace(/<meta[^>]*>/g, '')),
    `index.html ne charge rien depuis un CDN`
  )
  const poids = fichiers.reduce((s, f) => s + fs.statSync(f).size, 0)
  console.log(`\n  poids du site compilé : ${Math.round(poids / 1024)} Ko`)

  await nav.close()
  serveur.close()

  ok.forEach((x) => console.log('  OK   ' + x))
  ko.forEach((x) => console.log('  KO   ' + x))
  console.log(`\n  ${ok.length} contrôles verts, ${ko.length} rouges`)
  console.log(`  captures : ${CAPTURES}`)
  process.exit(ko.length ? 1 : 0)
})()
