/*
  ═══════════════════════════════════════════════════ L'ADAPTATEUR SasPay ═══

  TOUT CE QU'ON NE SAIT PAS ENCORE DE SasPay EST DANS CE SEUL FICHIER.

  ⚠️ POURQUOI IL EST ÉCRIT COMME ÇA. Le jour où il a été écrit, `saspay.me` et
  `docs.saspay.me` étaient injoignables depuis la machine qui l'écrivait (le
  filtre de sortie répond 403 sur ces deux domaines) et rien de leur API n'est
  publié ailleurs. Impossible, donc, de vérifier une seule adresse ni un seul
  nom de champ. Le pari n'est pas « j'ai deviné juste » : c'est **« me tromper
  ne doit rien coûter »**. D'où deux principes tenus partout ici :

    1. Chaque valeur incertaine est un RÉGLAGE, lue dans l'environnement.
       Corriger une adresse ou un en-tête, c'est `supabase secrets set`, pas
       une modification de code, pas un déploiement.
    2. Rien ne se DEVINE sur l'argent. Un montant qu'on ne trouve pas n'est
       jamais remplacé par une valeur par défaut : la notification est gardée
       telle quelle et personne n'est marqué payé. Un montant faux coûte plus
       cher qu'un paiement traité en retard.

  ⚠️ Web standard uniquement (fetch, crypto.subtle, TextEncoder) : ce fichier
  tourne chez Deno sur Supabase ET sous Node dans `_qc_paiement.mjs`. La partie
  qui décide de l'argent est ainsi essayée sans clé, sans réseau et sans base.
*/

/* ------------------------------------------------------------- les réglages */

function env(cle: string, defaut = ''): string {
  const g = globalThis as any
  try {
    if (g.Deno?.env?.get) return g.Deno.env.get(cle) ?? defaut
  } catch (_e) { /* Deno sans permission env : on retombe plus bas */ }
  return g.process?.env?.[cle] ?? defaut
}

export function reglages() {
  return {
    /* ⚠️ À CONFIRMER dans docs.saspay.me — les quatre lignes qui suivent sont
       des hypothèses raisonnables, pas des faits. */
    base:      env('SASPAY_BASE', 'https://api.saspay.me'),
    chemin:    env('SASPAY_CHEMIN_SESSION', '/v1/checkout/sessions'),
    entete:    env('SASPAY_ENTETE_CLE', 'Authorization'),
    prefixe:   env('SASPAY_PREFIXE_CLE', 'Bearer '),
    enteteSig: env('SASPAY_ENTETE_SIGNATURE', 'x-saspay-signature'),

    cle:       env('SASPAY_CLE_SECRETE'),
    secretSig: env('SASPAY_SECRET_WEBHOOK'),

    /* ⛔ LA DEVISE EST UN VERROU, PAS UNE PRÉFÉRENCE. Le tableau de bord vu le
       2026-09-03 proposait « CDF ». PISTE vend en FCFA. 10 000 CDF valent
       environ 2 100 F : encaisser la mauvaise devise sans s'en apercevoir,
       c'est livrer un carnet payé au quart. Ce qui n'est pas dans cette
       devise n'est jamais marqué payé. */
    devise:    env('SASPAY_DEVISE', 'XOF'),

    /* ⚠️ Beaucoup d'API comptent en centimes. Le franc CFA n'a pas de
       décimale, donc ici on attend 1. Si le premier essai réel montre un
       montant cent fois trop grand, ce réglage passe à 100 : c'est le
       refus de paiement qui l'aura dit, en affichant les deux montants. */
    multiple:  Number(env('SASPAY_MONTANT_MULTIPLIE', '1')) || 1,

    retour:    env('SASPAY_RETOUR', 'https://piste.nebula-agency.online/#/merci'),
    annule:    env('SASPAY_ANNULE', 'https://piste.nebula-agency.online/#/paiement'),
  }
}

export type Reglages = ReturnType<typeof reglages>

/* ------------------------------------------- lire une valeur où qu'elle soit */

/*
  Les API enveloppent leur contenu de façons très différentes : `{data:{…}}`,
  `{payment:{…}}`, à plat. On cherche donc en largeur d'abord, sur toute la
  profondeur du message. Chercher est sans risque ; c'est INVENTER qui l'est,
  et rien ici n'invente : quand aucun nom ne répond, on rend `undefined` et
  l'appelant refuse.
*/
export function chercher(objet: unknown, noms: string[]): unknown {
  /* ⚠️ NOM PAR NOM, DANS L'ORDRE DE LA LISTE. Parcourir le message une seule
     fois en cherchant « n'importe lequel de ces noms » rend le premier trouvé
     dans le MESSAGE, pas le premier de la LISTE : un message portant `id` et
     `payment_id` livrait alors l'identifiant d'événement là où on voulait
     celui de la session. La priorité écrite ici doit être celle qui s'applique. */
  for (const nom of noms) {
    const cible = nom.toLowerCase()
    const file: unknown[] = [objet]
    let garde = 0
    while (file.length && garde++ < 2000) {
      const o = file.shift()
      if (!o || typeof o !== 'object') continue
      for (const [k, v] of Object.entries(o as Record<string, unknown>)) {
        if (k.toLowerCase() === cible && v !== null && v !== undefined && v !== '') return v
        if (v && typeof v === 'object') file.push(v)
      }
    }
  }
  return undefined
}

const texte = (v: unknown): string => (v === undefined || v === null ? '' : String(v).trim())

/* ------------------------------------------------------- ce qu'on a compris */

export type Notification = {
  evenementId: string
  reference: string        // PISTE-XXXX, si le fournisseur nous la rend
  session: string          // son identifiant à lui
  montant: number | null   // ⚠️ null = introuvable. Jamais 0 par défaut.
  devise: string
  etat: 'paye' | 'echoue' | 'attente' | 'inconnu'
}

const MOTS_PAYE = [
  'paid', 'payé', 'paye', 'payee', 'payée', 'success', 'successful', 'succeeded',
  'completed', 'complete', 'confirmed', 'approved', 'reussi', 'réussi', 'ok',
]
const MOTS_ECHOUE = [
  'failed', 'failure', 'echec', 'échec', 'echoue', 'échoué', 'declined',
  'refused', 'refuse', 'refusé', 'cancelled', 'canceled', 'annule', 'annulé',
  'expired', 'expire', 'expiré', 'error',
]
const MOTS_ATTENTE = [
  'pending', 'attente', 'en_attente', 'processing', 'initiated', 'created',
  'waiting', 'encours', 'en_cours',
]

export function lireEtat(brut: string): Notification['etat'] {
  const s = brut.toLowerCase().replace(/[^a-zà-ÿ_]/g, '')
  if (!s) return 'inconnu'
  if (MOTS_PAYE.some((m) => s === m || s.endsWith('.' + m) || s.includes(m))) return 'paye'
  if (MOTS_ECHOUE.some((m) => s.includes(m))) return 'echoue'
  if (MOTS_ATTENTE.some((m) => s.includes(m))) return 'attente'
  return 'inconnu'
}

export function lireNotification(corps: unknown): Notification {
  const montantBrut = chercher(corps, [
    'amount', 'montant', 'amount_paid', 'montant_paye', 'total', 'value',
  ])
  const n = Number(texte(montantBrut).replace(/\s/g, '').replace(',', '.'))

  return {
    evenementId: texte(chercher(corps, ['event_id', 'eventId', 'id', 'uuid', 'reference_id'])),
    reference: texte(chercher(corps, [
      'merchant_reference', 'reference_marchand', 'external_id', 'externalId',
      'metadata_reference', 'order_id', 'orderId', 'commande', 'reference',
    ])),
    session: texte(chercher(corps, [
      'session_id', 'sessionId', 'checkout_id', 'checkoutId', 'payment_id',
      'paymentId', 'transaction_id', 'transactionId', 'link_id', 'token', 'id',
    ])),
    montant: Number.isFinite(n) && texte(montantBrut) !== '' ? n : null,
    devise: texte(chercher(corps, ['currency', 'devise', 'currency_code'])).toUpperCase(),
    etat: lireEtat(texte(chercher(corps, ['status', 'statut', 'etat', 'state', 'event', 'type']))),
  }
}

/* ⚠️ La référence PISTE et l'identifiant de session sont cherchés dans DEUX
   listes distinctes, et `reference` est cherchée AVANT `id` : sans cet ordre,
   un message qui porte les deux ferait passer l'identifiant du fournisseur
   pour notre code de commande, et aucune commande ne serait jamais retrouvée. */

/* --------------------------------------------------------- la signature ---- */

/*
  ⚠️ SCHÉMA À CONFIRMER. On suppose le plus répandu : HMAC-SHA256 du corps
  BRUT, en hexadécimal ou en base64, dans un en-tête. Deux règles tenues quoi
  qu'il arrive :

  ⛔ On signe le corps REÇU TEL QUEL, jamais un JSON reparsé. `JSON.parse` puis
     `JSON.stringify` change l'ordre et les espaces : la signature ne
     correspondrait plus jamais, et on finirait par « désactiver la
     vérification pour que ça marche ».

  ⛔ Comparaison à temps constant. Comparer deux signatures avec `===` laisse
     fuir, octet par octet, de quoi en fabriquer une bonne.
*/
export async function signer(corpsBrut: string, secret: string): Promise<{ hex: string; b64: string }> {
  const enc = new TextEncoder()
  const cle = await crypto.subtle.importKey(
    'raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'],
  )
  const sig = new Uint8Array(await crypto.subtle.sign('HMAC', cle, enc.encode(corpsBrut)))
  const hex = [...sig].map((b) => b.toString(16).padStart(2, '0')).join('')
  const b64 = btoa(String.fromCharCode(...sig))
  return { hex, b64 }
}

export function memeChaine(a: string, b: string): boolean {
  if (a.length !== b.length) return false
  let d = 0
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i)
  return d === 0
}

export async function verifierSignature(
  corpsBrut: string, enteteRecu: string, secret: string,
): Promise<boolean> {
  if (!secret) return false
  const brut = (enteteRecu || '').trim()
  if (!brut) return false

  /* ⛔ NE PAS DÉCOUPER SUR « = » POUR RETIRER UN PRÉFIXE. Une signature base64
     se TERMINE par « = » (bourrage) : garder « le dernier morceau » la vidait
     entièrement, et toute signature base64 valable était refusée. On ne retire
     un préfixe que s'il RESSEMBLE à un préfixe, c'est-à-dire une courte
     étiquette (« sha256 », « v1 », « t ») suivie du signe. */
  const candidats = new Set<string>([brut])
  for (const bout of brut.split(/[,\s]+/)) {
    if (!bout) continue
    candidats.add(bout)
    const m = bout.match(/^[A-Za-z0-9_-]{1,12}=(.+)$/)
    if (m) candidats.add(m[1])
  }

  const { hex, b64 } = await signer(corpsBrut, secret)
  for (const c of candidats) {
    if (memeChaine(c.toLowerCase(), hex) || memeChaine(c, b64)) return true
  }
  return false
}

/* ------------------------------------------------- ouvrir une session chez eux */

export type Session = { ok: true; session: string; url: string; brut: unknown }
                    | { ok: false; erreur: string; brut?: unknown }

/*
  ⚠️ LE CORPS ENVOYÉ EST LA SEULE CHOSE QUI DEVRA VRAIMENT ÊTRE RELUE dans la
  doc SasPay : quinze lignes, ci-dessous. Tout le reste (adresse, en-tête,
  lecture de la réponse, signature) s'ajuste par réglage.
*/
export async function ouvrirSession(
  r: Reglages,
  a: { reference: string; montant: number; description: string; client?: { nom?: string; email?: string; tel?: string } },
): Promise<Session> {
  if (!r.cle) return { ok: false, erreur: 'clé absente' }

  const corps = {
    amount: a.montant * r.multiple,
    currency: r.devise,
    description: a.description,
    reference: a.reference,            // notre code, qu'on espère voir revenir
    metadata: { reference: a.reference },
    customer: {
      name: a.client?.nom || undefined,
      email: a.client?.email || undefined,
      phone: a.client?.tel || undefined,
    },
    success_url: r.retour,
    cancel_url: r.annule,
  }

  let rep: Response
  try {
    rep = await fetch(r.base.replace(/\/$/, '') + r.chemin, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        [r.entete]: r.prefixe + r.cle,
      },
      body: JSON.stringify(corps),
    })
  } catch (e) {
    return { ok: false, erreur: 'réseau : ' + String(e) }
  }

  const txt = await rep.text()
  let json: unknown = null
  try { json = JSON.parse(txt) } catch (_e) { /* certains rendent du texte */ }

  if (!rep.ok) {
    /* On rend le corps de l'erreur : c'est lui qui dira quel champ manque, et
       c'est comme ça que les hypothèses ci-dessus se corrigent en une fois. */
    return { ok: false, erreur: `HTTP ${rep.status} · ${txt.slice(0, 400)}`, brut: json }
  }

  const url = texte(chercher(json, [
    'checkout_url', 'checkoutUrl', 'payment_url', 'paymentUrl', 'redirect_url',
    'redirectUrl', 'link', 'lien', 'url',
  ]))
  const session = texte(chercher(json, [
    'session_id', 'sessionId', 'checkout_id', 'checkoutId', 'payment_id',
    'paymentId', 'transaction_id', 'id', 'token',
  ]))

  if (!url) return { ok: false, erreur: 'aucune adresse de paiement dans la réponse', brut: json }
  return { ok: true, session: session || a.reference, url, brut: json }
}

/* ---------------------------------------------------- décider, en un endroit */

export type Attendu = { existe: boolean; etat: string; total: number }
export type Decision = { payer: boolean; agi: string }

/*
  ⚠️ LES GARDES DE LA CAISSE SONT ICI, ET NULLE PART AILLEURS. La fonction de
  bord ne fait que lire la base, appeler ceci, et obéir. C'est ce qui permet de
  les essayer sans clé, sans réseau et sans base (`node _qc_paiement.mjs`) :
  une règle qui décide de l'argent et qu'aucun contrôle ne peut atteindre n'est
  pas une règle, c'est une intention.
*/
export function decider(n: Notification, cmd: Attendu | null, r: Reglages): Decision {
  if (!cmd?.existe) return { payer: false, agi: 'commande inconnue' }
  if (n.etat !== 'paye') return { payer: false, agi: 'rien · ' + n.etat }

  if (n.devise && n.devise !== r.devise) {
    return { payer: false, agi: `refus · devise ${n.devise} au lieu de ${r.devise}` }
  }

  const attendu = Number(cmd.total) || 0
  const recu = n.montant === null ? null : n.montant / r.multiple
  if (recu === null || Math.abs(recu - attendu) > 0.5) {
    return { payer: false, agi: `refus · montant ${recu ?? 'illisible'} au lieu de ${attendu}` }
  }

  if (cmd.etat === 'payee' || cmd.etat === 'livree') return { payer: false, agi: 'déjà payée' }
  return { payer: true, agi: 'payee' }
}
