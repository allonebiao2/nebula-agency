/*
  PISTE · le barème.

  Source unique : `piste/PRODUCT.md` §4. Rien n'est arrondi, rien n'est caché,
  et le détail du calcul est rendu ligne par ligne pour être affiché tel quel.
  Un total qui tombe du ciel est un total qu'on ne croit pas.
*/

export const BASE = 100

export const SUPPLEMENTS = [
  {
    cle: 'teste',
    prix: 150,
    nom: 'Le numéro est testé',
    resume: 'La ligne sonne, et le compte WhatsApp existe.',
    detail:
      'Chaque numéro est composé avant l\'envoi. S\'il ne répond plus, la fiche ne part pas : elle est remplacée par une autre.',
  },
  {
    cle: 'sansSite',
    prix: 100,
    nom: "Il n'a rien en ligne",
    resume: 'Ce commerce n\'a ni site, ni page qui tourne.',
    detail:
      'Vérifié un par un. C\'est le commerce le plus facile à convaincre, et personne d\'autre ne vend cette information.',
  },
  {
    cle: 'dirigeant',
    prix: 100,
    nom: 'Le nom du dirigeant',
    resume: 'Pour dire son nom au lieu de dire « bonjour ».',
    detail:
      'Uniquement le nom publié publiquement par le commerce. Rien d\'autre sur la personne : ni âge, ni adresse privée, ni quoi que ce soit de sa vie.',
  },
  {
    cle: 'message',
    prix: 50,
    nom: 'Le message déjà écrit',
    resume: 'Rédigé pour ce commerce, à partir de ce que vous vendez.',
    detail:
      'Vous appuyez sur le bouton, WhatsApp s\'ouvre, le message est dedans. Vous n\'avez plus qu\'à envoyer.',
  },
]

/* Remise au volume. Le premier palier atteint gagne, du plus haut au plus bas. */
export const PALIERS = [
  { seuil: 500, taux: 0.3 },
  { seuil: 200, taux: 0.2 },
  { seuil: 50, taux: 0.1 },
]

export function palier(n) {
  return PALIERS.find((p) => n >= p.seuil) || null
}

export function prochainPalier(n) {
  const suivants = [...PALIERS].reverse().filter((p) => n < p.seuil)
  return suivants[0] || null
}

/*
  Rend TOUT le calcul, pas seulement le total.

  { lignes, unitaire, sousTotal, taux, remise, total, parFiche }
*/
export function calcul(nombre, options = {}) {
  const n = Math.max(0, Math.round(nombre || 0))
  const choisis = SUPPLEMENTS.filter((s) => options[s.cle])

  const lignes = [
    { cle: 'base', nom: 'La fiche de base', unite: BASE, n, montant: BASE * n },
    ...choisis.map((s) => ({
      cle: s.cle,
      nom: s.nom,
      unite: s.prix,
      n,
      montant: s.prix * n,
    })),
  ]

  const unitaire = BASE + choisis.reduce((s, x) => s + x.prix, 0)
  const sousTotal = unitaire * n
  const p = palier(n)
  const taux = p ? p.taux : 0
  const remise = Math.round(sousTotal * taux)
  const total = sousTotal - remise

  return {
    n,
    lignes,
    unitaire,
    sousTotal,
    taux,
    remise,
    total,
    parFiche: n > 0 ? Math.round(total / n) : 0,
    suivant: prochainPalier(n),
  }
}

/* 12345 devient « 12 345 F ». Espace insécable fine avant le F. */
export function fcfa(v) {
  return String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' F'
}

export function nombre(v) {
  return String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}
