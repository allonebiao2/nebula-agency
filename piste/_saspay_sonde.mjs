/*
  PISTE · la sonde SasPay.

      node _saspay_sonde.mjs              # cherche la bonne adresse et le bon en-tête
      node _saspay_sonde.mjs --montant=100

  ⚠️ À LANCER DEPUIS LE PC DE COTONOU, PAS DEPUIS UNE SESSION DANS LE NUAGE :
  `saspay.me` y répond 403 au CONNECT. C'est précisément pour ça que cette
  sonde existe : la machine qui a écrit le code ne pouvait pas lire la doc, et
  celle de Mongazi peut appeler l'API.

  CE QU'ELLE FAIT. Elle essaie de créer une vraie session de paiement, et quand
  ça rate elle balaie les adresses et les formes d'en-tête plausibles. Puis elle
  écrit **les commandes `supabase secrets set` à copier** pour figer ce qui a
  marché. Une hypothèse fausse se corrige alors par un réglage, sans toucher au
  code.

  ⚠️ ELLE CRÉE DE VRAIS LIENS DE PAIEMENT, de 100 F par défaut. Personne n'est
  débité : un lien non payé ne prend l'argent de personne, et il se supprime
  depuis le tableau de bord. Mais ils apparaîtront dans « Liens de paiement ».

  ⛔ ELLE N'IMPRIME JAMAIS LA CLÉ, seulement ses quatre derniers caractères.
*/
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ICI = path.dirname(fileURLToPath(import.meta.url))
const arg = (n, d) => (process.argv.find((a) => a.startsWith(`--${n}=`)) || '').split('=')[1] || d
const MONTANT = Number(arg('montant', '100')) || 100
const dodo = (ms) => new Promise((r) => setTimeout(r, ms))

/* ── la clé, depuis secrets/ ou l'environnement ───────────────────────────── */
if (!process.env.SASPAY_CLE_SECRETE) {
  const f = path.join(ICI, '..', 'secrets', 'saspay.env')
  if (fs.existsSync(f)) {
    for (const l of fs.readFileSync(f, 'utf8').split('\n')) {
      const m = l.match(/^\s*([A-Z_]+)\s*=\s*(.*)$/)
      if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim()
    }
  }
}
const CLE = process.env.SASPAY_CLE_SECRETE || ''
if (!CLE) {
  console.log(`
  Aucune clé trouvée.

    secrets/saspay.env  →  SASPAY_CLE_SECRETE=sk_live_...
    ou   SASPAY_CLE_SECRETE=... node _saspay_sonde.mjs

  ⛔ Jamais dans le dépôt : il est public. secrets/ est ignoré par git.
`)
  process.exit(1)
}
console.log(`\n  Clé : …${CLE.slice(-4)}  ·  montant d'essai : ${MONTANT} F\n`)

/* ── ce qu'on essaie ──────────────────────────────────────────────────────── */
const BASES = [
  process.env.SASPAY_BASE || 'https://api.saspay.me',
  'https://app.saspay.me/api',
  'https://saspay.me/api',
]
const CHEMINS = [
  process.env.SASPAY_CHEMIN_SESSION || '/v1/checkout/sessions',
  '/v1/checkout-sessions',
  '/v1/payment-links',
  '/v1/payments',
  '/v1/transactions',
  '/checkout/sessions',
]
const ENTETES = [
  ['Authorization', 'Bearer '],
  ['Authorization', ''],
  ['X-API-KEY', ''],
  ['x-secret-key', ''],
]

const CORPS = {
  amount: MONTANT,
  currency: process.env.SASPAY_DEVISE || 'XOF',
  description: 'PISTE · sonde technique',
  reference: 'PISTE-SOND',
  metadata: { reference: 'PISTE-SOND' },
  success_url: 'https://piste.nebula-agency.online/#/merci',
  cancel_url: 'https://piste.nebula-agency.online/#/paiement',
}

async function essai(base, chemin, [nom, prefixe]) {
  try {
    const rep = await fetch(base.replace(/\/$/, '') + chemin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json',
                 [nom]: prefixe + CLE },
      body: JSON.stringify(CORPS),
    })
    return { code: rep.status, texte: (await rep.text()).slice(0, 300) }
  } catch (e) {
    return { code: 0, texte: String(e.cause?.code || e.message).slice(0, 90) }
  }
}

/*
  ⚠️ LIRE LE CODE DE RETOUR EST TOUT L'INTÉRÊT DE LA SONDE.
    401/403 = l'adresse EXISTE, c'est la clé ou l'en-tête qui ne va pas. C'est
              la meilleure nouvelle possible : on a trouvé la porte.
    422/400 = adresse ET clé bonnes, c'est le CORPS qui ne va pas. Le message
              renvoyé nomme alors le champ manquant : c'est lui qu'il faut
              recopier dans `ouvrirSession`.
    404     = mauvais chemin.
    0       = l'hôte n'existe pas.
*/
/* ⛔ UN 403 D'INTERMÉDIAIRE N'EST PAS UN 403 DE SasPay. Éprouvée depuis une
   session dans le nuage, la sonde a pris le refus du filtre de sortie
   (« Host not in allowlist ») pour la preuve que la porte existait, désigné
   `app.saspay.me` comme gagnant et tendu des `supabase secrets set` fondés sur
   ce rien. Un pare-feu d'entreprise ou un portail wifi produiraient le même
   mirage. On lit donc le CORPS avant de croire le code. */
const MURS = /allowlist|egress|proxy|forbidden by|access denied|cloudflare|blocked|not permitted/i
const mur = (r) => (r.code === 403 || r.code === 407) && MURS.test(r.texte)

const lire = (c) =>
  c === 0   ? 'hôte injoignable'
: c === 404 ? 'chemin inconnu'
: c === 401 || c === 403 ? '⚑ LA PORTE EXISTE, en-tête ou clé à corriger'
: c === 400 || c === 422 ? '⚑⚑ ADRESSE ET CLÉ BONNES, corps à corriger'
: c >= 200 && c < 300 ? '✅ ÇA PASSE' : `réponse ${c}`

const trouves = []

console.log('  ── 1. quelle adresse répond ─────────────────────────────────')
let base = null
for (const b of BASES) {
  const r = await essai(b, CHEMINS[0], ENTETES[0])
  console.log(`  ${String(r.code).padEnd(4)} ${b.padEnd(28)} ${mur(r) ? '⛔ bloqué par un intermédiaire, pas par SasPay' : lire(r.code)}`)
  if (r.code && r.code !== 404 && !mur(r) && !base) base = b
  if (r.code >= 200 && r.code < 500 && r.code !== 404 && !mur(r)) trouves.push({ b, c: CHEMINS[0], e: ENTETES[0], r })
  await dodo(300)
}
if (!base) base = BASES[0]

console.log(`\n  ── 2. quel chemin, sur ${base} ──`)
let chemin = null
for (const c of CHEMINS) {
  const r = await essai(base, c, ENTETES[0])
  console.log(`  ${String(r.code).padEnd(4)} ${c.padEnd(28)} ${mur(r) ? '⛔ intermédiaire' : lire(r.code)}`)
  if (r.code && r.code !== 404 && !mur(r) && !chemin) chemin = c
  if (r.code >= 200 && r.code < 500 && r.code !== 404 && !mur(r)) trouves.push({ b: base, c, e: ENTETES[0], r })
  await dodo(300)
}

if (chemin) {
  console.log(`\n  ── 3. quelle forme d'en-tête, sur ${chemin} ──`)
  for (const e of ENTETES) {
    const r = await essai(base, chemin, e)
    console.log(`  ${String(r.code).padEnd(4)} ${(e[0] + ': ' + (e[1] || '<clé nue>')).padEnd(28)} ${mur(r) ? '⛔ intermédiaire' : lire(r.code)}`)
    if (r.code >= 200 && r.code < 500 && r.code !== 404 && !mur(r)) trouves.push({ b: base, c: chemin, e, r })
    await dodo(300)
  }
}

/* ── le verdict ───────────────────────────────────────────────────────────── */
const rang = (t) =>
    t.r.code >= 200 && t.r.code < 300 ? 0
  : [400, 422].includes(t.r.code)     ? 1
  : [401, 403].includes(t.r.code)     ? 2
  : 3
trouves.sort((a, b2) => rang(a) - rang(b2))
const g = trouves[0]

if (!g) {
  console.log(`
  ⛔ Rien n'a répondu. Ouvre l'onglet « Développeur » du tableau de bord SasPay :
     il donne l'adresse de base et la forme de l'en-tête. Puis relance avec

       SASPAY_BASE=https://... node _saspay_sonde.mjs
`)
  process.exit(1)
}

console.log(`\n  ══ CE QUI RÉPOND LE MIEUX ══════════════════════════════════\n`)
console.log(`  ${g.b}${g.c}   ·   ${g.e[0]}: ${g.e[1] || '<clé nue>'}`)
console.log(`  ${g.r.code} ${lire(g.r.code)}`)
console.log(`\n  Ce qu'ils ont répondu :\n  ${g.r.texte.replace(/\n/g, '\n  ')}\n`)

/*
  ⛔ ON NE TEND DES COMMANDES QUE SI ON A VRAIMENT PARLÉ À SasPay. Un 401 dit
  qu'une porte existe, pas que c'est la bonne : figer une adresse sur cette
  seule foi, c'est déployer une hypothèse en croyant déployer un fait. La
  première version de cette sonde le faisait, sur un 403 qui venait d'un
  proxy.
*/
const atteint = rang(g) <= 1

if (rang(g) === 1) {
  console.log(`  ⚠️ Adresse et clé bonnes : c'est le CORPS qui ne convient pas, et le
     message ci-dessus nomme sans doute le champ manquant. C'est
     \`ouvrirSession\` (supabase/functions/_shared/saspay.ts, une quinzaine de
     lignes) qu'il faut aligner dessus. Envoie-moi ce message.\n`)
}

if (!atteint) {
  console.log(`  ⛔ AUCUNE COMMANDE À COPIER. ${g.r.code === 401 || g.r.code === 403
    ? "Une porte répond, mais la clé n'a jamais été acceptée : rien ne dit que\n     c'est la bonne adresse."
    : "Rien n'a abouti."}
     Ouvre l'onglet « Développeur » du tableau de bord SasPay, il donne
     l'adresse de base et la forme de l'en-tête, puis relance avec :

       SASPAY_BASE=https://... SASPAY_CHEMIN_SESSION=/... node _saspay_sonde.mjs
`)
  process.exit(1)
}

console.log(`  ── à figer ─────────────────────────────────────────────────\n`)
console.log(`  supabase secrets set SASPAY_BASE=${g.b}`)
console.log(`  supabase secrets set SASPAY_CHEMIN_SESSION=${g.c}`)
console.log(`  supabase secrets set SASPAY_ENTETE_CLE=${g.e[0]}`)
console.log(`  supabase secrets set SASPAY_PREFIXE_CLE='${g.e[1]}'`)
console.log(`  supabase secrets set SASPAY_DEVISE=${CORPS.currency}\n`)
