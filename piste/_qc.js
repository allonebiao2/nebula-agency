/*
  PISTE · le contrôle qualité.

      npm run build && npm run qc

  Deux familles de contrôles, et les deux doivent être vertes :

    LE CALCUL   le barème, l'aller-retour message → cockpit, le stock.
                Ce sont des fonctions pures : on les appelle directement.
    L'ÉCRAN     390 / 768 / 1440, un vrai navigateur, le parcours de
                commande joué du début à la fin.

  Ce qui est vérifié ici n'est pas cosmétique. Un total faux, un lien
  WhatsApp cassé ou un stock qui ment coûtent de l'argent à quelqu'un.
*/

import { createServer } from 'node:http'
import { readFile, stat } from 'node:fs/promises'
import { extname, join, resolve } from 'node:path'
import { chromium } from 'playwright'

import { BASE, PALIERS, SUPPLEMENTS, calcul, fcfa } from './src/prix.js'
import { MINIMUM, MOMO, STOCK, TOTAL_FICHES, estFixe, numeroMasque, stock } from './src/donnees.js'
import { LONGUEUR_CODE, codeCommande, composerMessage, lireMessage } from './src/etat.js'

const DIST = resolve(import.meta.dirname, 'dist')

/*
  Le navigateur. On essaie d'abord celui que Playwright a installé lui-même —
  c'est le cas normal sur le poste de Cotonou. Certaines machines (les
  conteneurs de développement) ont déjà un Chromium ailleurs et une version de
  Playwright qui ne le retrouve pas : on le cherche alors, plutôt que de
  déclarer le contrôle impossible.
*/
async function ouvrirNavigateur() {
  const essais = [undefined, process.env.PLAYWRIGHT_CHROMIUM]
  for (const motif of ['/opt/pw-browsers/chromium-*/chrome-linux/chrome']) {
    const { glob } = await import('node:fs/promises')
    try {
      for await (const trouve of glob(motif)) essais.push(trouve)
    } catch {
      /* `glob` n'existe pas avant Node 22 : on se contente des deux premiers */
    }
  }
  let derniere
  for (const executablePath of essais) {
    if (executablePath === null) continue
    try {
      return await chromium.launch({ args: ['--no-sandbox'], executablePath })
    } catch (e) {
      derniere = e
    }
  }
  throw derniere
}
const ok = []
const ko = []
const dire = (bon, quoi) => (bon ? ok : ko).push(quoi)

/* `fcfa` sépare les milliers par une espace fine insécable (U+202F) et pose
   une insécable (U+00A0) devant le F. Le navigateur les rend telles quelles :
   pour comparer un montant affiché à un montant calculé, il faut ramener
   toutes les espèces d'espaces à la même. */
const memeEspace = (s) => String(s).replace(/[\s  ]/g, ' ')
const contientMontant = (texte, montant) => memeEspace(texte).includes(memeEspace(fcfa(montant)))

/* ------------------------------------------------------- 1. le calcul ---- */

function controlerLeCalcul() {
  /* le barème, à la main */
  const a = calcul(10, {})
  dire(a.total === 1000, `10 fiches nues = ${fcfa(a.total)} (attendu 1 000 F)`)

  const b = calcul(50, { teste: true })
  dire(b.unitaire === 250, `base + numéro testé = ${b.unitaire} F l'unité (attendu 250)`)
  dire(b.taux === 0.1, `50 fiches : remise de ${b.taux * 100} % (attendu 10)`)
  dire(b.total === 11250, `50 fiches testées = ${fcfa(b.total)} (attendu 11 250 F)`)

  const plein = calcul(1, Object.fromEntries(SUPPLEMENTS.map((s) => [s.cle, true])))
  dire(plein.unitaire === 500, `la fiche la plus complète = ${plein.unitaire} F (attendu 500)`)

  dire(calcul(0, {}).total === 0, 'zéro fiche, zéro franc, aucune division par zéro')
  dire(calcul(-5, {}).n === 0, 'un nombre négatif est ramené à zéro')

  /* les paliers ne se chevauchent pas et le plus haut gagne */
  dire(calcul(200, {}).taux === 0.2, '200 fiches : −20 %')
  dire(calcul(499, {}).taux === 0.2, '499 fiches : encore −20 %')
  dire(calcul(500, {}).taux === 0.3, '500 fiches : −30 %')
  dire(
    PALIERS.every((p, i) => i === 0 || p.seuil < PALIERS[i - 1].seuil),
    'les paliers sont rangés du plus haut au plus bas'
  )

  /* le total est toujours la somme des lignes, moins la remise */
  const c = calcul(37, { teste: true, dirigeant: true })
  const somme = c.lignes.reduce((s, l) => s + l.montant, 0)
  dire(somme - c.remise === c.total, 'le total est exactement la somme des lignes moins la remise')

  /* le barème affiché correspond bien à PRODUCT.md §4 */
  dire(BASE === 100, `la base vaut ${BASE} F`)
  const attendus = { teste: 150, sansSite: 100, dirigeant: 100, message: 50 }
  dire(
    SUPPLEMENTS.every((s) => attendus[s.cle] === s.prix),
    'les 4 suppléments sont au prix du socle produit'
  )
}

function controlerLeStock() {
  const somme = Object.values(STOCK).reduce((a, b) => a + b, 0)
  dire(somme === TOTAL_FICHES, `l'inventaire fait ${somme} fiches, et le total affiché aussi`)
  dire(TOTAL_FICHES === 187, `${TOTAL_FICHES} fiches, comme le carnet du 3 août`)
  dire(stock('couture', 'cotonou') === 57, `couture à Cotonou : ${stock('couture', 'cotonou')}`)
  dire(stock('couture', 'abidjan') === 0, "Abidjan est à zéro : aucune source ivoirienne relevée")
  dire(stock('autre', 'cotonou') === 0, "le métier « autre » n'a pas de stock, il ouvre une demande")
  dire(stock('', '') === null, 'sans métier ni ville, le stock ne prétend rien')

  /* un fixe n'a pas WhatsApp : c'est la règle du carnet, elle doit tenir ici */
  dire(estFixe('BJ', '0121300000') === true, 'un 0121 béninois est reconnu comme fixe')
  dire(estFixe('BJ', '0197075503') === false, 'un 0197 béninois est un mobile')
  dire(estFixe('TG', '22251000') === true, 'un 22 togolais est reconnu comme fixe')
  dire(estFixe('TG', '90749679') === false, 'un 90 togolais est un mobile')

  /* le numéro montré sur la vitrine est amputé de deux chiffres */
  const m = numeroMasque('BJ', '0197075503')
  dire(m.endsWith('••') && !m.includes('03'), `le numéro public est masqué : ${m}`)
}

function controlerLAllerRetour() {
  /* Ce que le client envoie, le cockpit doit savoir le relire. Si ce contrôle
     casse, Mongazi ressaisit ses commandes à la main. */
  const commande = {
    code: codeCommande(),
    metier: 'couture',
    ville: 'cotonou',
    quartier: 'Akpakpa',
    nombre: 45,
    options: { teste: true, message: true },
    offre: 'je propose une assurance santé aux commerçants',
    nom: 'Awa Koudjo',
    email: 'awa@exemple.com',
    whatsapp: '+229 01 96 00 00 00',
    momo: '0196000000',
    reseau: 'MTN MoMo',
  }
  const message = composerMessage(commande)
  const lu = lireMessage(message)
  const p = calcul(45, commande.options)

  dire(lu.code === commande.code, `le code fait l'aller-retour : ${lu.code}`)
  dire(lu.nombre === 45, `le nombre de fiches est relu : ${lu.nombre}`)
  dire(lu.total === p.total, `le total est relu : ${fcfa(lu.total || 0)}`)
  dire(lu.nom === commande.nom, `le nom est relu : ${lu.nom}`)
  dire(lu.email === commande.email, `l'email est relu : ${lu.email}`)
  dire(lu.whatsapp === commande.whatsapp, `le WhatsApp est relu : ${lu.whatsapp}`)
  dire(lu.momo === commande.momo, `le numéro payeur est relu : ${lu.momo}`)
  dire(lu.reseau === 'MTN MoMo', `le réseau est relu : ${lu.reseau}`)
  dire(lu.offre === commande.offre, "la phrase du client est relue")
  dire(/couture/i.test(lu.metier || ''), `le métier est relu : ${lu.metier}`)

  /* un message qui n'est pas une commande ne doit surtout pas passer */
  const bruit = lireMessage('bonjour je voudrais des fiches merci')
  dire(!bruit.code && !bruit.nombre, "un message quelconque n'est pas pris pour une commande")

  /* le code se dicte au téléphone : ni I, ni O, ni 1, ni 0.
     4 000 tirages, c'est plus d'un an de commandes à pleine capacité. */
  const codes = Array.from({ length: 4000 }, () => codeCommande())
  dire(
    codes.every((c) => new RegExp(`^[23456789A-HJ-NP-Z]{${LONGUEUR_CODE}}$`).test(c)),
    "les codes ne contiennent aucun caractère qui se confond à l'oral"
  )
  /* Un code en double, c'est une commande qui en écrase une autre : 20 000
     tirages doivent tenir sans collision, quand la V1 en produira 10 par jour. */
  dire(
    new Set(codes).size === codes.length,
    `${codes.length} codes tirés, ${new Set(codes).size} distincts (aucune collision)`
  )
  /* La répartition ne doit favoriser aucun caractère : un tirage biaisé, ce
     sont des codes qui se ressemblent, donc des collisions plus tôt que prévu.
     On compte sur les 6 positions à la fois (24 000 caractères, 750 attendus
     par lettre) et on tolère 20 % d'écart — quatre fois l'écart-type, donc
     large pour du hasard, mais serré pour un vrai biais. */
  const tirages = {}
  codes.forEach((c) => [...c].forEach((x) => (tirages[x] = (tirages[x] || 0) + 1)))
  const compte = Object.values(tirages)
  const attendu = (codes.length * LONGUEUR_CODE) / 32
  dire(
    Object.keys(tirages).length === 32 &&
      Math.min(...compte) > attendu * 0.8 &&
      Math.max(...compte) < attendu * 1.2,
    `les 32 caractères sortent également (${Math.min(...compte)} à ${Math.max(...compte)} fois, ${attendu} attendues)`
  )
}

/* ------------------------------------------------------- 2. le serveur --- */

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.woff2': 'font/woff2',
  '.svg': 'image/svg+xml',
}

function servir(racine) {
  return new Promise((resoudre) => {
    const serveur = createServer(async (req, res) => {
      const chemin = decodeURIComponent(req.url.split('?')[0])
      let fichier = join(racine, chemin === '/' ? 'index.html' : chemin)
      try {
        if ((await stat(fichier)).isDirectory()) fichier = join(fichier, 'index.html')
      } catch {
        fichier = join(racine, 'index.html')
      }
      try {
        const contenu = await readFile(fichier)
        res.writeHead(200, { 'content-type': TYPES[extname(fichier)] || 'application/octet-stream' })
        res.end(contenu)
      } catch {
        res.writeHead(404).end('non trouvé')
      }
    })
    serveur.listen(0, '127.0.0.1', () => resoudre({ serveur, port: serveur.address().port }))
  })
}

/* --------------------------------------------------------- 3. l'écran ---- */

/* Les cibles doivent faire 44 px : on s'en sert au pouce, debout, dans la rue.
   Les liens posés au fil d'une phrase en sont exemptés — les agrandir casserait
   l'interligne du texte. */
const MESURER_CIBLES = `(() => {
  const petites = []
  for (const el of document.querySelectorAll('button, a[href], input[type=range], summary')) {
    const b = el.getBoundingClientRect()
    /* 1 px ou moins : l'élément est masqué aux voyants (le lien d'évitement du
       clavier, par exemple). Il reprend sa taille quand il prend le focus. */
    if (b.width <= 1 || b.height <= 1) continue
    const style = getComputedStyle(el)
    if (style.display === 'inline') continue
    if (el.closest('p, li, dd, pre')) continue
    if (b.height < 44) petites.push((el.textContent || el.tagName).trim().slice(0, 40) + ' → ' + Math.round(b.height) + 'px')
  }
  return petites
})()`

/* Deux leçons du dépôt, vérifiées automatiquement :
   · aucune animation infinie sous un backdrop-filter (latence, Boussole 2026-07-21)
   · aucun position:fixed sous un ancêtre transformé (le FAB, Boussole 2026-07-25) */
const MESURER_PIEGES = `(() => {
  const infiniSousFlou = []
  const fixeSousTransform = []

  for (const el of document.querySelectorAll('*')) {
    const s = getComputedStyle(el)

    if (s.backdropFilter !== 'none' && s.webkitBackdropFilter !== 'none') {
      for (const enfant of el.querySelectorAll('*')) {
        const e = getComputedStyle(enfant)
        if (e.animationName !== 'none' && e.animationIterationCount === 'infinite') {
          infiniSousFlou.push(e.animationName)
        }
      }
    }

    if (s.position === 'fixed') {
      let p = el.parentElement
      while (p && p !== document.documentElement) {
        const ps = getComputedStyle(p)
        if (ps.transform !== 'none' || ps.filter !== 'none' || ps.perspective !== 'none') {
          fixeSousTransform.push((el.className || el.tagName) + ' sous ' + (p.className || p.tagName))
          break
        }
        p = p.parentElement
      }
    }
  }
  return { infiniSousFlou, fixeSousTransform }
})()`

async function controlerLEcran(base) {
  const nav = await ouvrirNavigateur()

  for (const [nom, w, h] of [['telephone', 390, 844], ['tablette', 768, 1024], ['PC', 1440, 900]]) {
    const page = await nav.newPage({ viewport: { width: w, height: h } })
    const erreurs = []
    const dehors = []
    page.on('pageerror', (e) => erreurs.push(String(e).slice(0, 160)))
    page.on('console', (m) => m.type() === 'error' && erreurs.push(m.text().slice(0, 160)))
    page.on('request', (r) => {
      if (!r.url().startsWith(base) && !r.url().startsWith('data:')) dehors.push(r.url())
    })

    for (const [route, titre] of [['#/', 'accueil'], ['#/origine', 'origine'], ['#/commander', 'commander']]) {
      await page.goto(base + '/' + route, { waitUntil: 'networkidle' })
      await page.waitForTimeout(220)
      const deborde = await page.evaluate(
        () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
      )
      dire(!deborde, `${nom} · ${titre} : aucun débordement horizontal`)
    }

    await page.goto(base + '/#/', { waitUntil: 'networkidle' })
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(900)

    /* Le débordement se mesure DEUX fois : au chargement, et une fois la page
       parcourue. Une carte animée en 3D peut être inoffensive dans un état et
       pousser la page de côté dans l'autre. */
    const debordeApres = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
    )
    dire(!debordeApres, `${nom} : aucun débordement après avoir parcouru la page`)

    const petites = await page.evaluate(MESURER_CIBLES)
    dire(petites.length === 0, `${nom} : ${petites.length} cible(s) sous 44 px ${petites.slice(0, 2).join(' | ')}`)

    const pieges = await page.evaluate(MESURER_PIEGES)
    dire(
      pieges.infiniSousFlou.length === 0,
      `${nom} : ${pieges.infiniSousFlou.length} animation(s) infinie(s) sous un backdrop-filter`
    )
    dire(
      pieges.fixeSousTransform.length === 0,
      `${nom} : ${pieges.fixeSousTransform.length} position:fixed sous un ancêtre transformé ${pieges.fixeSousTransform[0] || ''}`
    )

    dire(erreurs.length === 0, `${nom} : ${erreurs.length} erreur(s) JS ${erreurs[0] || ''}`)
    dire(dehors.length === 0, `${nom} : ${dehors.length} requête(s) hors du site ${dehors[0] || ''}`)

    if (nom === 'telephone') {
      /* la barre de prix doit vraiment rester collée au pouce */
      await page.goto(base + '/#/commander', { waitUntil: 'networkidle' })
      const avant = await page.locator('.fixed.bottom-0').boundingBox()
      await page.evaluate(() => window.scrollBy(0, 400))
      await page.waitForTimeout(260)
      const apres = await page.locator('.fixed.bottom-0').boundingBox()
      dire(
        avant && apres && Math.abs(avant.y - apres.y) < 2,
        'téléphone : la barre de prix ne défile pas avec la page'
      )
    }

    await page.close()
  }

  /* ------------------------------------------- le parcours, joué en entier */

  const page = await nav.newPage({ viewport: { width: 390, height: 844 } })
  const erreurs = []
  page.on('pageerror', (e) => erreurs.push(String(e).slice(0, 160)))
  await page.goto(base + '/#/commander', { waitUntil: 'networkidle' })

  const continuer = async () => {
    await page.getByRole('button', { name: /^Continuer$/ }).click()
    await page.waitForTimeout(160)
  }

  /* on ne passe pas une question sans y répondre */
  await continuer()
  dire(
    await page.getByRole('alert').isVisible(),
    'on ne peut pas sauter la première question sans choisir un métier'
  )

  await page.getByRole('button', { name: /Ateliers de couture/ }).click()
  await continuer()

  const badge = await page.getByRole('button', { name: /Cotonou et ses environs/ }).textContent()
  dire(/57 en stock/.test(badge), `le stock réel s'affiche sur la ville : ${badge.match(/\d+ en stock/) || '—'}`)
  const abidjan = await page.getByRole('button', { name: /Abidjan/ }).textContent()
  dire(/bientôt/.test(abidjan), "Abidjan est marqué « bientôt », il n'est pas vendable")

  await page.getByRole('button', { name: /Cotonou et ses environs/ }).click()
  await continuer()
  await continuer() /* le quartier est facultatif */

  const curseur = page.locator('input[type=range]')
  dire(
    (await curseur.getAttribute('min')) === String(MINIMUM),
    `le curseur ne descend pas sous ${MINIMUM} fiches`
  )
  dire(
    (await curseur.getAttribute('max')) === '57',
    `le curseur est plafonné au stock réel (${await curseur.getAttribute('max')})`
  )

  await page.getByRole('button', { name: /^50$/ }).click()
  await page.waitForTimeout(120)
  const barre = await page.locator('.fixed.bottom-0').textContent()
  const attendu = calcul(50, { teste: true, message: true })
  dire(contientMontant(barre, attendu.total), `la barre affiche le bon total : ${fcfa(attendu.total)}`)

  await continuer()
  await continuer() /* les suppléments par défaut */

  await page.getByLabel(/qu'est-ce que vous proposez/i).fill(
    'je propose une assurance santé aux commerçants et à leurs employés'
  )
  await page.waitForTimeout(200)
  const apercu = await page.textContent('body')
  dire(
    /Je vous écris au sujet de/.test(apercu),
    "le message pré-écrit se montre avant de payer, avec la phrase du client"
  )
  await continuer()

  await page.getByLabel('Votre nom et prénom').fill('Awa Koudjo')
  await page.getByLabel(/Votre email/).fill('awa@exemple.com')
  await page.getByLabel(/Votre WhatsApp/).fill('+229 0196000000')
  await page.getByLabel(/numéro depuis lequel vous paierez/).fill('0196000000')
  await page.getByRole('button', { name: /Voir comment payer/ }).click()
  await page.waitForTimeout(300)

  const paiement = await page.textContent('body')
  dire(/Code de commande/.test(paiement), 'l\'écran de paiement affiche le code de commande')
  dire(contientMontant(paiement, attendu.total), `l'écran de paiement affiche le même total : ${fcfa(attendu.total)}`)
  dire(/Valable encore/.test(paiement), 'le compte à rebours des 24 heures est affiché')

  const lien = await page.getByRole('link', { name: /Envoyer sur WhatsApp/ }).getAttribute('href')
  dire(/^https:\/\/wa\.me\/229\d{8,}\?text=/.test(lien), 'le lien WhatsApp est bien formé')
  const texte = decodeURIComponent(lien.split('?text=')[1])
  const relu = lireMessage(texte)
  dire(
    relu.code && relu.nombre === 50 && relu.total === attendu.total,
    'le message envoyé est relisible par le cockpit, avec le bon total'
  )
  dire(
    /awa@exemple\.com/.test(texte) && /Awa Koudjo/.test(texte),
    'le message porte les coordonnées du client'
  )

  /* ⛔ le contrôle qui protège l'argent de quelqu'un */
  if (MOMO.aConfirmer) {
    const chiffres = paiement.match(/\b\d{8,10}\b/g) || []
    const inconnus = chiffres.filter((n) => n !== '0196000000')
    dire(
      inconnus.length === 0,
      `aucun numéro Mobile Money non confirmé n'est affiché (${inconnus.slice(0, 2).join(', ') || 'aucun'})`
    )
    dire(
      /donné sur WhatsApp/.test(paiement),
      'la page dit franchement que le numéro de paiement arrive sur WhatsApp'
    )
  }

  /* la commande se retrouve après un rechargement : on ne perd pas un panier */
  await page.reload({ waitUntil: 'networkidle' })
  await page.waitForTimeout(200)
  dire(
    /Code de commande/.test(await page.textContent('body')),
    'la commande survit à un rechargement de la page'
  )

  dire(erreurs.length === 0, `parcours : ${erreurs.length} erreur(s) JS ${erreurs[0] || ''}`)

  /* --------------------------------------------------------- le cockpit -- */

  await page.goto(base + '/#/cockpit', { waitUntil: 'networkidle' })
  dire(
    /Réservé/.test(await page.textContent('body')),
    'le cockpit ne s\'ouvre pas tout seul à un visiteur'
  )
  await page.getByLabel('mot de passage').fill('piste')
  await page.getByRole('button', { name: 'Entrer' }).click()
  await page.waitForTimeout(200)
  const ouvert = await page.textContent('body')
  dire(
    /Ranger une commande reçue/.test(ouvert) && !/Réservé/.test(ouvert),
    "le cockpit s'ouvre avec le mot de passage"
  )

  await page.locator('textarea').fill(texte)
  await page.getByRole('button', { name: /Ranger cette commande/ }).click()
  await page.waitForTimeout(220)
  const apresRangement = await page.textContent('body')
  dire(/Awa Koudjo/.test(apresRangement), 'la commande collée apparaît dans le cockpit')
  dire(/Marquer payé/.test(apresRangement), 'la commande arrive à l\'état « reçue »')

  await page.getByRole('button', { name: 'Marquer payé' }).click()
  await page.waitForTimeout(160)
  dire(
    /Marquer livré/.test(await page.textContent('body')),
    'une commande payée attend maintenant sa livraison'
  )
  await page.getByRole('button', { name: 'Marquer livré' }).click()
  await page.waitForTimeout(160)
  const livree = await page.textContent('body')
  dire(!/Marquer/.test(livree), 'une commande livrée n\'a plus d\'action en attente')

  await page.getByRole('button', { name: 'Détail' }).click()
  await page.getByRole('button', { name: /Retirer du cockpit/ }).click()
  await page.waitForTimeout(160)
  dire(
    /Annuler/.test(await page.textContent('body')),
    'toute suppression est annulable'
  )
  await page.getByRole('button', { name: 'Annuler' }).click()
  await page.waitForTimeout(200)
  dire(/Awa Koudjo/.test(await page.textContent('body')), 'la commande retirée revient si on annule')

  /* le cockpit ne prend pas n'importe quoi pour une commande */
  await page.locator('textarea').fill('bonjour je veux des fiches')
  await page.getByRole('button', { name: /Ranger cette commande/ }).click()
  await page.waitForTimeout(160)
  dire(
    await page.getByRole('alert').isVisible(),
    'un message qui n\'est pas une commande est refusé, avec une explication'
  )

  /* Coller deux fois le même message ne doit pas créer deux commandes : c'est
     le geste le plus naturel du monde quand on ne sait plus si on l'a fait. */
  await page.locator('textarea').fill(texte)
  await page.getByRole('button', { name: /Ranger cette commande/ }).click()
  await page.waitForTimeout(220)
  const doublons = await page.locator('article').count()
  dire(doublons === 1, `coller deux fois le même message donne ${doublons} commande, pas deux`)

  /* Le cockpit a crashé une fois sur un hook posé après un retour anticipé
     (React #310) : le contrôle ne s'en apercevait qu'à un délai d'attente
     épuisé, 30 secondes plus tard et sans dire pourquoi. Plus jamais. */
  dire(erreurs.length === 0, `cockpit : ${erreurs.length} erreur(s) JS ${erreurs[0] || ''}`)

  await page.close()
  await nav.close()
}

/* -------------------------------------------------------------- départ --- */

const { serveur, port } = await servir(DIST)
const base = `http://127.0.0.1:${port}`

try {
  controlerLeCalcul()
  controlerLeStock()
  controlerLAllerRetour()
  await controlerLEcran(base)
} catch (e) {
  ko.push('le contrôle s\'est interrompu : ' + String(e).split('\n')[0])
} finally {
  serveur.close()
}

console.log('')
ok.forEach((x) => console.log('  OK  ', x))
if (ko.length) {
  console.log('')
  ko.forEach((x) => console.log('  KO  ', x))
}
console.log(`\n  ${ok.length} contrôles verts, ${ko.length} rouges`)
if (!ko.length) console.log('  TOUT EST VERT\n')
process.exit(ko.length ? 1 : 0)
