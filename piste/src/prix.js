/*
  PISTE · le barème.

  Source unique : `piste/PRODUCT.md` §4. Rien n'est arrondi, rien n'est caché,
  et le détail du calcul est rendu ligne par ligne pour être affiché tel quel.
  Un total qui tombe du ciel est un total qu'on ne croit pas.
*/

export const BASE = 100

/* ⚠️ PLAFOND · une fiche coûte entre 100 F et 250 F, jamais plus (Mongazi,
   2026-08-04). Les quatre suppléments réunis valent donc exactement 150 F :
   60 + 40 + 30 + 20. Si un supplément change de prix, la somme doit rester
   à 150, sinon le plafond saute sans que personne s'en aperçoive. */
export const PLAFOND = 250

export const SUPPLEMENTS = [
  /*
    ⚠️ CETTE OPTION A CHANGÉ DE PROMESSE LE 2026-08-04, ET IL FAUT SAVOIR
    POURQUOI AVANT D'Y RETOUCHER.

    Elle disait : « Chaque numéro est composé avant l'envoi. » Personne ne
    pouvait tenir ça : seul le pouce de Mongazi compose, un numéro à la fois.
    Dix commandes de cinquante fiches font cinq cents appels. Ses mots :
    « je ne me vois pas lancer les appels moi-même ».

    Une promesse que le vendeur ne peut pas tenir n'est pas une option, c'est
    une dette. Elle dit maintenant TROIS choses que la machine prouve seule :

      1. le numéro est dans une tranche réellement attribuée par le régulateur
         (ARCEP Bénin, ARCEP Togo, plan ivoirien de 2021 : voir
         `piste.numero_plausible`). Hors de ces tranches, la ligne ne peut pas
         exister ;
      2. la fiche a été revue à sa source il y a moins de soixante jours ;
      3. aucun client ne l'a signalée injoignable, et c'est le signal le plus
         fort : un vrai humain a vraiment essayé.

    Plus la garantie qui existait déjà et qui est ce que l'acheteur veut
    vraiment : si ça ne répond pas, on remplace, gratuitement.

    ⚠️ NE JAMAIS REVENIR À « la ligne sonne ». Aucune de ces trois vérifications
    ne prouve qu'on décrochera. Le jour où un vrai test réseau sera possible
    (une requête opérateur coûte environ 3 F par numéro, mais demande une carte
    bancaire que Mongazi n'a pas), cette option pourra redevenir un vrai test.
  */
  {
    cle: 'teste',
    court: 'le numéro vérifié',
    prix: 60,
    nom: 'Le numéro est vérifié',
    resume: 'Ligne attribuée, fiche revue récemment, jamais signalée morte.',
    detail:
      'Trois contrôles avant l\'envoi : le numéro appartient à une tranche réellement attribuée par le régulateur, la fiche a été revue à sa source il y a moins de deux mois, et aucun client ne l\'a signalée injoignable. Et si malgré tout ça ne répond pas, on la remplace gratuitement.',
  },
  {
    cle: 'sansSite',
    court: "ceux qui n'ont rien en ligne",
    prix: 40,
    nom: "Il n'a rien en ligne",
    resume: 'Ce commerce n\'a ni site, ni page qui tourne.',
    detail:
      'Vérifié un par un. C\'est le commerce le plus facile à convaincre, et personne d\'autre ne vend cette information.',
  },
  {
    cle: 'dirigeant',
    court: "le nom du dirigeant",
    prix: 30,
    nom: 'Le nom du dirigeant',
    resume: 'Pour dire son nom au lieu de dire « bonjour ».',
    detail:
      'Uniquement le nom publié publiquement par le commerce. Rien d\'autre sur la personne : ni âge, ni adresse privée, ni quoi que ce soit de sa vie.',
  },
  {
    cle: 'message',
    court: "le message déjà écrit",
    prix: 20,
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
/* Le contrôle du plafond, fait ici et pas dans un commentaire : une règle qui
   n'est vérifiée nulle part n'est pas une règle. */
export const UNITAIRE_MAX = BASE + SUPPLEMENTS.reduce((s, x) => s + x.prix, 0)

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
