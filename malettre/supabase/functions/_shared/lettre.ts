/*
  MA LETTRE À… · tout ce qui décide, du côté serveur.

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne chez Deno, mais il vit ICI, et il
  s'essaie sous Node : `node malettre/_qc_caisse.mjs`. Un garde-fou qu'aucun
  contrôle ne peut atteindre n'est pas un garde-fou, c'est une intention.

  Rien ici n'appelle le réseau, ne lit un secret, ni ne touche une base : ce
  fichier ne contient que des décisions, pour qu'elles soient toutes essayées.

  ⛔ LE PRIX NE VIENT JAMAIS DU NAVIGATEUR. Le constructeur est un paquet
  statique : ce qu'il annonce se réécrit dans la console en trois secondes.
  Le barème ci-dessous est le seul qui engage la caisse. Un contrôle compare
  ces quatre lignes à celles de `creer.html` et refuse la moindre différence :
  deux barèmes dans un dépôt sont deux vérités, et c'est déjà arrivé le
  2026-09-06 (les occasions portaient un « dès 10 000 F » payable 0 F).

  ⛔ ON NE STOCKE JAMAIS LE HTML ENVOYÉ PAR LE NAVIGATEUR. On stocke les
  DONNÉES, et on rebâtit la lettre à partir du gabarit. Autrement, cette porte
  serait un hébergeur de pages arbitraires sur notre propre domaine : gratuit,
  anonyme, et parfait pour une page qui imite une banque.
*/

/* ── Le barème ──────────────────────────────────────────────────────────── */

export type Palier = {
  id: string
  nom: string
  prix: number
  /* Le pied « Écris la tienne : Ma lettre à… » : la boucle de croissance. Elle
     n'existe qu'au palier offert, et c'est le serveur qui en décide. */
  pied: boolean
  /* Combien de jours la lettre reste joignable. */
  jours: number
  photos: number
  /* Le nom de l'offre en anglais : la page de paiement et le reçu le lisent
     ICI, comme le nom français (« le nom de l'offre vient de la caisse »). */
  en: string
  /* L'habillage (cire, sceau, papier, pluie, phrase à gratter) : décision de
     Mongazi du 2026-10-16, réservé aux offres payantes, sans changer les prix.
     ⛔ Le même droit vit dans `creer.html` (PALIERS) ; un contrôle compare. */
  habillage: boolean
  /* Le code secret (2026-10-21) : promis par La Lettre et Le Coffret seulement.
     ⛔ Le même droit vit dans `creer.html` (PALIERS) ; un contrôle compare. */
  code: boolean
}

export const PALIERS: Palier[] = [
  { id: 'gratuit', nom: 'Gratuit',    prix: 0,     pied: true,  jours: 7,   photos: 1,  en: 'Free',         habillage: false, code: false },
  { id: 'mot',     nom: 'Le Mot',     prix: 2000,  pied: false, jours: 365, photos: 3,  en: 'The Note',     habillage: true,  code: false },
  { id: 'lettre',  nom: 'La Lettre',  prix: 5000,  pied: false, jours: 365, photos: 3,  en: 'The Letter',   habillage: true,  code: true },
  { id: 'coffret', nom: 'Le Coffret', prix: 10000, pied: false, jours: 365, photos: 20, en: 'The Keepsake', habillage: true,  code: true },
]

/* ── Les deux langues (2026-10-16) ─────────────────────────────────────────
   Une liste FERMÉE : tout ce qui n'est pas « en » est du français, la langue
   de toutes les lettres d'avant ce champ. Elle décide des mots du gabarit,
   de la plume, de la page de retour ; jamais d'un prix. */
export const LANGUES = ['fr', 'en'] as const
export type Langue = typeof LANGUES[number]
export const langueDe = (v: unknown): Langue => (v === 'en' ? 'en' : 'fr')
export const SITE_LETTRES = 'https://malettre.nebula-agency.online'
export const accueilDe = (l: Langue) => SITE_LETTRES + (l === 'en' ? '/en/' : '')
/* Le nom d'une commande tel que l'acheteur le lira (paiement, reçu). */
export function nomOffre(p: Palier, plume: boolean, l: Langue): string {
  const n = l === 'en' ? p.en : p.nom
  return plume ? (l === 'en' ? `${n} + the Quill` : `${n} + la plume`) : n
}

/* ── L'habillage (2026-10-16) ───────────────────────────────────────────────
   Des listes FERMÉES : la première valeur de chacune est celle d'une lettre
   sans habillage (et de toute lettre gratuite). ⛔ Les mêmes listes vivent
   dans `creer.html` (HABILLAGE) ; un contrôle exige qu'elles soient égales. */
export const HABILLAGE = {
  cire: ['bordeaux', 'or', 'nuit', 'sapin', 'rose'],
  sceau: ['initiale', 'coeur', 'colombe', 'couronne'],
  papier: ['creme', 'coton', 'kraft', 'nuit'],
  pluie: ['aucune', 'petales', 'confettis', 'etoiles'],
} as const
export type Habillage = { cire: string; sceau: string; papier: string; pluie: string }
export const SANS_HABILLAGE: Habillage = { cire: 'bordeaux', sceau: 'initiale', papier: 'creme', pluie: 'aucune' }
export function lireHabillage(v: unknown, permis: boolean): Habillage {
  if (!permis || !v || typeof v !== 'object') return { ...SANS_HABILLAGE }
  const h = v as Record<string, unknown>
  const un = (liste: readonly string[], x: unknown) => (liste.includes(String(x)) ? String(x) : liste[0])
  return {
    cire: un(HABILLAGE.cire, h.cire), sceau: un(HABILLAGE.sceau, h.sceau),
    papier: un(HABILLAGE.papier, h.papier), pluie: un(HABILLAGE.pluie, h.pluie),
  }
}

/* « Lui répondre sur WhatsApp » : le numéro de l'ACHETEUR, en format
   international, et seulement s'il a coché la case. ⛔ Jamais un numéro écrit
   ailleurs que dans le champ WhatsApp de la commande : sinon un acheteur
   pourrait poser dans la lettre le numéro de quelqu'un d'autre. */
export function numeroReponse(d: any): string {
  if (d?.repondre !== true) return ''
  const brut = String(d?.whatsapp ?? '')
  let n = brut.replace(/\D/g, '')
  if (/^\s*(\+|00)/.test(brut)) {
    n = n.replace(/^00/, '')               // déjà international
  } else {
    /* L'indicatif est choisi à côté du champ (Bénin, Togo, Côte d'Ivoire…) :
       229 + 0197085576 donne 2290197085576. ⚠️ On ne retire jamais le 01
       béninois (deux formes vivantes, leçon du parc). */
    /* L'indicatif vient d'une liste : tel quel ou rien, jamais « nettoyé ». */
    const ind = String(d?.indicatif ?? '').trim()
    if (!/^\d{1,4}$/.test(ind)) return ''
    n = ind + n
  }
  return /^\d{10,15}$/.test(n) ? n : ''
}

export function palier(id: unknown): Palier | null {
  const s = String(id ?? '')
  return PALIERS.find((p) => p.id === s) ?? null
}

/*
  La plume : l'agent qui écrit la lettre à la place de l'acheteur
  (`_shared/plume.ts`). C'est une OPTION, pas un palier : elle s'ajoute à
  l'offre choisie, et avec l'offre gratuite la lettre coûte 500 F.

  ⛔ Même règle que les paliers : ce prix est le seul qui engage la caisse, et
  un contrôle le compare à celui de `creer.html`.
*/
export const PLUME = { prix: 500 }

/* Le prix d'une commande. Le navigateur dit s'il a pris la plume (un oui ou
   un non), jamais combien elle coûte. */
export function prixTotal(p: Palier, plume: boolean): number {
  return p.prix + (plume ? PLUME.prix : 0)
}

/* ── L'adresse ──────────────────────────────────────────────────────────── */

/*
  ⛔ ELLE NE SE DEVINE PAS, et c'est la première ligne de `CONDITIONS.md`.
  22 caractères d'un alphabet de 32 font 110 bits tirés au sort : personne ne
  trouve la lettre d'un autre en essayant l'adresse voisine, et personne ne
  balaie l'espace.

  ⚠️ Alphabet sans voyelles et sans les caractères qui se confondent (0/O,
  1/l/I) : une adresse se lit parfois à voix haute, et elle ne doit jamais
  former un mot par accident.
*/
const ALPHABET = '23456789bcdfghjkmnpqrstvwxyz'

export function jeton(taille = 22, hasard?: (n: number) => Uint8Array): string {
  const tirer = hasard ?? ((n: number) => crypto.getRandomValues(new Uint8Array(n)))
  const plafond = 256 - (256 % ALPHABET.length)
  let out = ''
  /* On tire large et on rejette ce qui déborde : le modulo direct favorise le
     début de l'alphabet, ce qui retire des bits sans le dire.
     ⚠️ La boucle est BORNÉE. Une source de hasard qui ne rendrait que des
     octets rejetés la ferait tourner pour toujours, et un serveur qui tourne
     pour toujours ne dit rien : il ne répond plus. Mieux vaut une erreur
     nommée qu'une fonction de bord qui ne rend jamais la main. */
  for (let tour = 0; tour < 64 && out.length < taille; tour++) {
    for (const o of tirer(taille * 2)) {
      if (o >= plafond) continue
      out += ALPHABET[o % ALPHABET.length]
      if (out.length === taille) break
    }
  }
  if (out.length < taille) throw new Error('hasard indisponible')
  return out
}

export const JETON_FORME = /^[23456789bcdfghjkmnpqrstvwxyz]{22}$/

/* ── L'heure d'ouverture ────────────────────────────────────────────────── */

/*
  ⚠️ HEURE DE CALENDRIER, SANS FUSEAU, et c'est tout le sujet : minuit, c'est
  minuit sur le téléphone de celle qui lit. Le serveur ne la convertit donc
  JAMAIS : il la valide, il la range, il la rend telle quelle. La seule chose
  qu'il refuse, c'est une chaîne qui n'a pas la forme d'une date.
*/
export const OUVRE_FORME = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/

export function ouvreValide(v: unknown): string {
  const s = String(v ?? '').trim()
  if (!s) return ''
  if (!OUVRE_FORME.test(s)) return ''
  const [d, h] = s.split('T')
  const [an, mo, jo] = d.split('-').map(Number)
  const [he, mi] = h.split(':').map(Number)
  if (mo < 1 || mo > 12 || jo < 1 || jo > 31 || he > 23 || mi > 59) return ''
  /* Une date qui n'existe pas (31 février) est refusée : Date la reporterait
     en silence au 3 mars, et la lettre s'ouvrirait un autre jour que celui
     qu'on a promis à l'acheteur. */
  const t = new Date(an, mo - 1, jo, he, mi, 0, 0)
  if (t.getMonth() !== mo - 1 || t.getDate() !== jo) return ''
  return s
}

/* ── La vie d'une lettre ────────────────────────────────────────────────── */

export type Ligne = {
  etat: string
  expire_le?: string | null
  retire_le?: string | null
}

export type Verdict = 'servir' | 'inconnue' | 'attente' | 'expiree' | 'retiree'

/*
  ⛔ « retirée » PASSE AVANT TOUT LE RESTE. C'est la règle de `CONDITIONS.md` :
  la demande de la personne visée passe avant le confort de l'acheteur, donc
  avant l'état de sa commande, avant la date, avant tout.
*/
export function verdict(l: Ligne | null, maintenant = Date.now()): Verdict {
  if (!l) return 'inconnue'
  if (l.retire_le) return 'retiree'
  if (l.etat !== 'vivante') return 'attente'
  if (l.expire_le && Date.parse(l.expire_le) <= maintenant) return 'expiree'
  return 'servir'
}

export function expireLe(p: Palier, maintenant = Date.now()): string {
  return new Date(maintenant + p.jours * 86400000).toISOString()
}

/* ── Les en-têtes d'une lettre servie ───────────────────────────────────── */

/*
  ⛔ `X-Robots-Tag` EN PLUS DE LA BALISE. La balise `<meta name="robots">` ne
  vaut que pour de l'HTML lu par un robot qui exécute le HTML ; l'en-tête
  couvre tout le reste, et c'est lui que `CONDITIONS.md` exige.

  ⚠️ `no-store` : une lettre ne doit pas rester dans le cache d'un relais, ni
  dans celui du navigateur d'un téléphone prêté. Le poids ne compte pas ici,
  une lettre se lit une fois.
*/
export function entetes(extra: Record<string, string> = {}): Record<string, string> {
  return {
    'Content-Type': 'text/html; charset=utf-8',
    'X-Robots-Tag': 'noindex, nofollow, noarchive, nosnippet',
    'Referrer-Policy': 'no-referrer',
    'X-Content-Type-Options': 'nosniff',
    'Cache-Control': 'private, no-store, max-age=0',
    ...extra,
  }
}

/* ── Poser les données dans le gabarit ──────────────────────────────────── */

const DEBUT = '/*MALETTRE_DONNEES*/'
const FIN = '/*FIN_MALETTRE_DONNEES*/'

/*
  ⛔ LE JUMEAU DE `malettre/_injecter.py`, ET IL DOIT RENDRE LE MÊME OCTET.
  Les données d'une lettre sont écrites par un acheteur et atterrissent DANS un
  bloc <script>. `JSON.stringify` ne protège pas de « </script> » : c'est une
  chaîne JSON parfaitement valide, et le navigateur cherche la balise fermante
  AVANT de lire le JSON.

  Deux implémentations d'une même règle sont deux vérités : `_qc_caisse.mjs`
  passe la même batterie hostile aux deux et exige le même résultat.
*/
export function serialiser(donnees: unknown): string {
  return JSON.stringify(donnees)
    .replace(/<\//g, '<\\/')
    .replace(/<!--/g, '<\\!--')
    .replace(/\u2028/g, '\\u2028')
    .replace(/\u2029/g, '\\u2029')
}

export function poser(gabarit: string, donnees: unknown): string {
  const a = gabarit.indexOf(DEBUT)
  const b = gabarit.indexOf(FIN)
  if (a < 0 || b < 0) throw new Error('gabarit sans marqueur MALETTRE_DONNEES')
  return gabarit.slice(0, a) + serialiser(donnees) + gabarit.slice(b + FIN.length)
}

/* ── Ce qu'un acheteur a le droit d'envoyer ─────────────────────────────── */

export type Lettre = {
  occasion: string
  pour: string
  de: string
  titre: string
  code: string
  lettre: string[]
  photos: { src: string; legende: string }[]
  depuis: string
  ouvre: string
  /* La formule de fin, juste avant la signature (« Avec tout mon cœur, »).
     Elle suit l'occasion : une lettre de rupture ne se signe pas « avec tout
     mon cœur ». */
  formule: string
  pied: boolean
  lien: string
  langue: Langue
  habillage: Habillage
  /* La phrase à gratter : réservée aux offres payantes, comme l'habillage. */
  gratter: string
  /* Le numéro de l'acheteur pour « Lui répondre », ou rien. */
  repondre: string
}

/* Un mot d'acheteur n'a pas de raison de faire dix mille signes, et une lettre
   n'a pas de raison de peser trois mégaoctets. Les bornes sont larges : elles
   arrêtent l'abus, pas l'enthousiasme. */
export const BORNES = {
  texte: 200,
  lignes: 40,
  ligne: 1200,
  photo: 900_000,   /* une photo réduite à 900 px pèse ~120 Ko en base64 */
  total: 4_000_000,
}

const texte = (v: unknown, max = BORNES.texte) => String(v ?? '').slice(0, max).trim()

export type Refus = { ok: false; erreur: string }
export type Accord = { ok: true; lettre: Lettre; palier: Palier; plume: boolean; prix: number }

/*
  ⛔ TOUT CE QUI ARRIVE EST HOSTILE JUSQU'À PREUVE DU CONTRAIRE, y compris ce
  que notre propre constructeur envoie : entre lui et cette porte, il y a un
  navigateur, et un navigateur s'édite.
*/
export function lireCommande(d: any): Accord | Refus {
  const p = palier(d?.palier)
  if (!p) return { ok: false, erreur: 'palier inconnu' }

  const lignes = (Array.isArray(d?.lettre) ? d.lettre : [])
    .map((l: unknown) => texte(l, BORNES.ligne))
    .filter(Boolean)
    .slice(0, BORNES.lignes)
  if (!lignes.length) return { ok: false, erreur: 'lettre vide' }

  /* ⛔ Les photos sont des DONNÉES, jamais des liens. Une source distante
     ferait dépendre la lettre d'un serveur et FUITERAIT L'HEURE D'OUVERTURE
     vers un tiers, qui est exactement ce qu'on vend. Le gabarit le refuse déjà
     côté navigateur : une vérification côté navigateur n'est pas une
     vérification. */
  const photos: { src: string; legende: string }[] = []
  for (const ph of Array.isArray(d?.photos) ? d.photos : []) {
    const src = String(ph?.src ?? '')
    if (!/^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(src)) {
      return { ok: false, erreur: 'photo qui n’est pas une donnée' }
    }
    if (src.length > BORNES.photo) return { ok: false, erreur: 'photo trop lourde' }
    photos.push({ src, legende: texte(ph?.legende) })
    if (photos.length >= p.photos) break
  }

  const code = String(d?.code ?? '').replace(/\D/g, '').slice(0, 4)
  const langue = langueDe(d?.langue)

  const lettre: Lettre = {
    occasion: texte(d?.occasion),
    pour: texte(d?.pour) || (langue === 'en' ? 'you' : 'toi'),
    de: texte(d?.de),
    titre: texte(d?.titre),
    /* Le code secret n'est porté que par les offres qui le promettent (La Lettre,
       Le Coffret) : envoyé avec une autre offre, il est retiré, comme l'habillage. */
    code: p.code ? code : '',
    lettre: lignes,
    photos,
    depuis: /^\d{4}-\d{2}-\d{2}$/.test(String(d?.depuis ?? '')) ? String(d.depuis) : '',
    ouvre: ouvreValide(d?.ouvre),
    formule: texte(d?.formule, 60),
    /* ⛔ Le pied vient du PALIER, jamais du navigateur : sinon la boucle de
       croissance se retire d'un clic dans la console, gratuitement. */
    pied: p.pied,
    lien: accueilDe(langue),
    langue,
    /* ⛔ L'habillage vient du PALIER autant que du navigateur : une lettre
       gratuite qui en arriverait vêtue le perd ici, comme le prix. */
    habillage: lireHabillage(d?.habillage, p.habillage),
    gratter: p.habillage ? texte(d?.gratter, 80) : '',
    repondre: numeroReponse(d),
  }

  /* ⛔ Et JAMAIS le drapeau d'aperçu : le seuil EST le produit, une lettre
     livrée garde toujours son cachet. Il n'est même pas lu ici. */

  const poids = JSON.stringify(lettre).length
  if (poids > BORNES.total) return { ok: false, erreur: 'lettre trop lourde' }

  /* ⚠️ Seul un vrai « true » vaut la plume : une chaîne « false » ou « 0 »
     envoyée par un navigateur bricolé ne doit rien coûter, ni rien offrir. */
  const plume = d?.plume === true
  return { ok: true, lettre, palier: p, plume, prix: prixTotal(p, plume) }
}
