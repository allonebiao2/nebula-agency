/*
  LA BOBINE · le barème. ⛔ LE PRIX NE VIENT JAMAIS DU NAVIGATEUR : il est lu ici, à partir du seul identifiant
  d'offre que le client envoie. Prix décidés par Mongazi le 2026-11-02.
  Les crédits paieront l'IA qui tourne sur un serveur (voix de synthèse, vidéo générée : vagues 4 et 5) ;
  l'IA qui tourne sur l'appareil (sous-titres, détourage, bruit) reste gratuite.
*/
export const OFFRES = {
  'pro-mois': { total: 1500, jours: 31, credits: 100, nom: 'LA BOBINE Pro · 1 mois' },
  'pro-an': { total: 12000, jours: 366, credits: 1200, nom: 'LA BOBINE Pro · 1 an' },
} as const

export type IdOffre = keyof typeof OFFRES
export type Offre = { id: IdOffre; total: number; jours: number; credits: number; nom: string }

/** L'offre demandée, ou null. ⛔ `Object.hasOwn` : « __proto__ » ou « constructor » ne sont pas des offres. */
export function lireOffre(id: unknown): Offre | null {
  if (typeof id !== 'string' || !Object.hasOwn(OFFRES, id)) return null
  return { id: id as IdOffre, ...OFFRES[id as IdOffre] }
}

export const REFERENCE_FORME = /^LB-[A-Z0-9]{10}$/

/** Une référence de commande imprévisible : LB- suivi de 10 caractères tirés au sort. */
export function nouvelleReference(): string {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  const octets = crypto.getRandomValues(new Uint8Array(10))
  return 'LB-' + Array.from(octets, (o) => alphabet[o % alphabet.length]).join('')
}
