/*
  PISTE · les données de la V1.

  ⚠️ RÈGLE ABSOLUE DE CE FICHIER : rien d'inventé.

  Tout ce qui est chiffré ici est compté dans
  `_documents/nebula-agency/vente/prospection/_donnees.py`, relevé le
  2026-08-03 sur l'annuaire professionnel public GoAfricaOnline.

  Comptes réels vérifiés (python -c "Counter(...)") :
      BJ couture      57      TG couture      54      TOTAL 187
      BJ restaurant   54      TG restaurant   20
      BJ patisserie    2
      dont 13 lignes fixes (5 au Bénin, 8 au Togo) et 1 fiche sans numéro.

  Répartition par zone, elle aussi comptée sur le même fichier :
      Cotonou et environs (Cotonou, Abomey-Calavi, Godomey, Cocotomey)
          couture 57 · restaurant 28 · patisserie 2      = 87
      Autres villes du Bénin (Porto-Novo, Parakou, Bohicon, Ouidah, Abomey,
          Lokossa, Kandi, Natitingou, Dassa-Zoumé, Allada, Adjarra,
          Tori-Bossito, N'Dali, Malanville, Nikki, Covè, Cobly)
          restaurant 26                                   = 26
      Lomé
          couture 53 · restaurant 19                      = 72
      Autres villes du Togo (Bafilo, Kpalimé)
          couture 1 · restaurant 1                        = 2
      Abidjan
          rien. Aucune source ivoirienne n'a encore été relevée.
                                                     TOTAL = 187
*/

export const NEBULA_WHATSAPP = '22996740732'
export const NEBULA_WHATSAPP_JOLI = '+229 96 74 07 32'
export const DATE_RELEVE = '4 août 2026'
export const MINIMUM = 10

/* L'adresse d'où partent les carnets (décision 44). Elle est annoncée AVANT
   l'envoi pour que l'acheteur la reconnaisse et ne la classe pas en
   indésirable. ⚠️ SPF, DKIM et DMARC restent à poser côté DNS. */
export const EMAIL_ENVOI = 'piste@nebula-agency.online'

/* Une commande non payée expire au bout de 24 heures, les fiches retournent
   au stock (décision 28). */
export const HEURES_VALIDITE = 24

/*
  ⚠️ À REMPLIR UNE SEULE FOIS, ICI, PAR MONGAZI.

  Décision 25 : MTN MoMo et Moov Flooz du Bénin, et rien d'autre au lancement.
  Tant qu'un `numero` vaut `null`, l'écran de paiement le dit franchement et
  renvoie sur WhatsApp : PISTE n'affiche jamais un numéro qu'il n'a pas, et un
  faux numéro de paiement coûterait bien plus cher qu'une phrase honnête.

    numero    : les 10 chiffres, format béninois (ex. '0196740732')
    titulaire : le nom qui s'affiche à l'écran de l'acheteur quand il valide
*/
export const MOBILE_MONEY = [
  { cle: 'mtn', operateur: 'MTN MoMo', numero: null, titulaire: null },
  { cle: 'moov', operateur: 'Moov Flooz', numero: null, titulaire: null },
]

export const MOMO_PRET = MOBILE_MONEY.some((m) => m.numero)

/* Le code de commande, décision 26. Ni O ni 0, ni I ni 1 : il se lit à voix
   haute au téléphone sans qu'on se trompe. */
export function nouvelleReference() {
  const A = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
  let s = ''
  for (let i = 0; i < 4; i++) s += A[Math.floor(Math.random() * A.length)]
  return 'PISTE-' + s
}

/* ------------------------------------------------------------------ métiers */

export const METIERS = [
  {
    cle: 'couture',
    pluriel: 'couture et mode',
    nom: 'Couture et mode',
    court: 'Couture',
    singulier: 'atelier de couture',
    exemple: 'tailleurs, couturieres, brodeurs, pret-a-porter',
  },
  {
    cle: 'restaurant',
    pluriel: 'restaurants, maquis et bars',
    nom: 'Restaurants, maquis et bars',
    court: 'Restaurants',
    singulier: 'restaurant',
    exemple: 'restaurants, maquis, bars, buvettes, traiteurs',
  },
  {
    cle: 'patisserie',
    pluriel: 'pâtisseries et boulangeries',
    nom: 'Pâtisseries et boulangeries',
    court: 'Pâtisseries',
    singulier: 'pâtisserie',
    exemple: 'patissiers, boulangers',
  },
  {
    cle: 'beaute',
    pluriel: 'beauté et bien-être',
    nom: 'Beauté et bien-être',
    court: 'Beauté',
    singulier: 'salon de beauté',
    exemple: 'salons de coiffure, instituts, spas',
  },
  {
    cle: 'alimentation',
    pluriel: 'alimentation et supermarchés',
    nom: 'Alimentation et supermarchés',
    court: 'Alimentation',
    singulier: 'commerce d\'alimentation',
    exemple: 'epiceries, supermarches, poissonneries',
  },
  {
    cle: 'quincaillerie',
    pluriel: 'quincaillerie et bâtiment',
    nom: 'Quincaillerie et bâtiment',
    court: 'Quincaillerie',
    singulier: 'quincaillerie',
    exemple: 'quincailleries, plomberie, vitrerie, batiment',
  },
  {
    cle: 'auto',
    pluriel: 'auto, moto et pièces',
    nom: 'Auto, moto et pièces',
    court: 'Auto',
    singulier: 'garage',
    exemple: 'garages, pieces detachees, vente de motos',
  },
  {
    cle: 'maison',
    pluriel: 'maison et décoration',
    nom: 'Maison et décoration',
    court: 'Maison',
    singulier: 'magasin de décoration',
    exemple: 'ameublement, decoration, produits d\'entretien',
  },
  {
    cle: 'sante',
    pluriel: 'santé et pharmacies',
    nom: 'Santé et pharmacies',
    court: 'Santé',
    singulier: 'cabinet de santé',
    exemple: 'cabinets, pharmacies, veterinaires',
  },
  {
    cle: 'ecole',
    pluriel: 'écoles et formation',
    nom: 'Écoles et formation',
    court: 'Écoles',
    singulier: 'établissement scolaire',
    exemple: 'ecoles, centres de formation',
  },
  {
    cle: 'autre',
    pluriel: 'commerces',
    nom: 'Un autre métier',
    court: 'Autre métier',
    singulier: 'commerce',
    exemple: 'dites-nous lequel, on vous prévient quand c\'est prêt',
    horsStock: true,
  },
]

/* -------------------------------------------------------------------- zones */

export const VILLES = [
  {
    cle: 'cotonou',
    court: 'Cotonou',
    nom: 'Cotonou et ses environs',
    pays: 'Bénin',
    detail: 'Cotonou, Abomey-Calavi, Godomey, Cocotomey',
  },
  {
    cle: 'benin-autres',
    court: 'une autre ville du Bénin',
    nom: 'Autres villes du Bénin',
    pays: 'Bénin',
    detail: 'Porto-Novo, Parakou, Bohicon, Ouidah, Abomey, Lokossa, Kandi…',
  },
  {
    cle: 'lome',
    court: 'Lomé',
    nom: 'Lomé',
    pays: 'Togo',
    detail: 'tous les quartiers, de Bè Klikamé à Agoè',
  },
  {
    cle: 'togo-autres',
    court: 'une autre ville du Togo',
    nom: 'Autres villes du Togo',
    pays: 'Togo',
    detail: 'Kpalimé, Bafilo',
  },
  {
    cle: 'abidjan',
    court: 'Abidjan',
    nom: 'Abidjan',
    pays: "Côte d'Ivoire",
    detail: "aucune source ivoirienne n'a encore été relevée",
    bientot: true,
  },
]

/* L'inventaire, écrit à la main à partir des comptes ci-dessus.
   En V2 il viendra de la base. Clé : `metier|ville`. */
export const STOCK = {
  'couture|cotonou': 325,
  'couture|benin-autres': 33,
  'couture|lome': 167,
  'couture|togo-autres': 3,
  'couture|abidjan': 0,
  'restaurant|cotonou': 297,
  'restaurant|benin-autres': 121,
  'restaurant|lome': 295,
  'restaurant|togo-autres': 51,
  'restaurant|abidjan': 0,
  'patisserie|cotonou': 94,
  'patisserie|benin-autres': 13,
  'patisserie|lome': 48,
  'patisserie|togo-autres': 3,
  'patisserie|abidjan': 0,
  'beaute|cotonou': 68,
  'beaute|benin-autres': 8,
  'beaute|lome': 57,
  'beaute|togo-autres': 3,
  'beaute|abidjan': 0,
  'alimentation|cotonou': 49,
  'alimentation|benin-autres': 6,
  'alimentation|lome': 46,
  'alimentation|togo-autres': 10,
  'alimentation|abidjan': 0,
  'quincaillerie|cotonou': 128,
  'quincaillerie|benin-autres': 63,
  'quincaillerie|lome': 100,
  'quincaillerie|togo-autres': 8,
  'quincaillerie|abidjan': 0,
  'auto|cotonou': 79,
  'auto|benin-autres': 11,
  'auto|lome': 74,
  'auto|togo-autres': 1,
  'auto|abidjan': 0,
  'maison|cotonou': 92,
  'maison|benin-autres': 3,
  'maison|lome': 47,
  'maison|togo-autres': 1,
  'maison|abidjan': 0,
  'sante|cotonou': 29,
  'sante|benin-autres': 12,
  'sante|lome': 18,
  'sante|togo-autres': 1,
  'sante|abidjan': 0,
  'ecole|cotonou': 58,
  'ecole|benin-autres': 7,
  'ecole|lome': 0,
  'ecole|togo-autres': 0,
  'ecole|abidjan': 0,
  'informatique|cotonou': 0,
  'informatique|benin-autres': 0,
  'informatique|lome': 0,
  'informatique|togo-autres': 0,
  'informatique|abidjan': 0,
  'imprimerie|cotonou': 0,
  'imprimerie|benin-autres': 0,
  'imprimerie|lome': 0,
  'imprimerie|togo-autres': 0,
  'imprimerie|abidjan': 0,
  'hotel|cotonou': 0,
  'hotel|benin-autres': 0,
  'hotel|lome': 0,
  'hotel|togo-autres': 0,
  'hotel|abidjan': 0,
  'immobilier|cotonou': 0,
  'immobilier|benin-autres': 0,
  'immobilier|lome': 0,
  'immobilier|togo-autres': 0,
  'immobilier|abidjan': 0,
  'transport|cotonou': 0,
  'transport|benin-autres': 0,
  'transport|lome': 0,
  'transport|togo-autres': 0,
  'transport|abidjan': 0,
  'services|cotonou': 0,
  'services|benin-autres': 0,
  'services|lome': 0,
  'services|togo-autres': 0,
  'services|abidjan': 0,
  'artisan|cotonou': 0,
  'artisan|benin-autres': 0,
  'artisan|lome': 0,
  'artisan|togo-autres': 0,
  'artisan|abidjan': 0,
  'commerce|cotonou': 0,
  'commerce|benin-autres': 0,
  'commerce|lome': 0,
  'commerce|togo-autres': 0,
  'commerce|abidjan': 0,
}

export function stock(metier, ville) {
  if (!metier || !ville) return null
  return STOCK[metier + '|' + ville] ?? 0
}

export function totalMetier(metier) {
  return VILLES.reduce((s, v) => s + (STOCK[metier + '|' + v.cle] || 0), 0)
}

/* Le grand total affiché sur la vitrine : il est CALCULÉ, jamais écrit en dur,
   pour qu'il ne puisse pas mentir si l'inventaire change. */
export const TOTAL_FICHES = Object.values(STOCK).reduce((a, b) => a + b, 0)

export const REPARTITION = [
  { nom: 'ateliers de couture', n: totalMetier('couture') },
  { nom: 'restaurants, maquis et bars', n: totalMetier('restaurant') },
  { nom: 'pâtisseries et boulangeries', n: totalMetier('patisserie') },
]

/* Lignes fixes comptées sur _donnees.py : 5 au Bénin (préfixe 0121)
   et 8 au Togo (préfixe 22). Elles n'ont pas WhatsApp, on les appelle. */
export const NOMBRE_FIXES = 400

/* ----------------------------------------------- fiches réelles d'exemple --

   Recopiées telles quelles de `_donnees.py`. Les deux derniers chiffres du
   numéro sont masqués sur la vitrine : la fiche complète appartient à qui
   l'achète, et le commerce n'a pas demandé à voir son numéro affiché en
   entier sur une page de vente.                                              */

/* Des fiches VRAIES, relevees le 3 aout 2026 dans le meme annuaire que le
   carnet des 187. Trois par combinaison metier x ville quand elles existent :
   l'apercu du generateur en montre trois qui changent selon ce qu'on choisit
   (decision 51), et il ne montrera jamais une fiche inventee.

   Le numero est affiche partiellement masque tant que rien n'est paye
   (decision 52) : on voit qu'il est vrai et complet, on ne peut pas s'en
   servir. Aucun fixe ici, ils n'ont pas WhatsApp. */
export const FICHES = [
  {
    nom: '1 DESIGNER',
    metier: 'couture', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Face Hôtel du Stade de l’Amitié, Quartier Kouhounou',
    pays: 'BJ', numero: '019506XXXX',
  },
  {
    nom: '2H HOUNTONDJI',
    metier: 'couture', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Alga Mosquée',
    pays: 'BJ', numero: '016672XXXX',
  },
  {
    nom: '3 A',
    metier: 'couture', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Dantokpa Marché',
    pays: 'BJ', numero: '019739XXXX',
  },
  {
    nom: 'AGOSBIL',
    metier: 'couture', ville: 'benin-autres',
    localite: 'Zagnanado', quartier: 'Agonlin houégbo',
    pays: 'BJ', numero: '016478XXXX',
  },
  {
    nom: 'BEAUTE',
    metier: 'couture', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Koutongbé',
    pays: 'BJ', numero: '015914XXXX',
  },
  {
    nom: 'DAV\'S ETS',
    metier: 'couture', ville: 'benin-autres',
    localite: 'Akassato', quartier: '-',
    pays: 'BJ', numero: '019413XXXX',
  },
  {
    nom: '3G(GOLDEN GLOBAL GROUP)',
    metier: 'couture', ville: 'lome',
    localite: 'Lomé', quartier: 'Rue du Bar Plateau',
    pays: 'TG', numero: '9144XXXX',
  },
  {
    nom: 'ABA GROUP INTERNATIONAL',
    metier: 'couture', ville: 'lome',
    localite: 'Lomé', quartier: 'Adidogomé',
    pays: 'TG', numero: '9058XXXX',
  },
  {
    nom: 'ABA SARL U',
    metier: 'couture', ville: 'lome',
    localite: 'Lomé', quartier: 'Adidogomé Wessome',
    pays: 'TG', numero: '9058XXXX',
  },
  {
    nom: 'BABY LUXE',
    metier: 'couture', ville: 'togo-autres',
    localite: 'Tsévié', quartier: 'commune de Tsévié plus précisément a Baktopé avant le lycée de baktopé',
    pays: 'TG', numero: '9304XXXX',
  },
  {
    nom: 'Coututre Dieu Donne',
    metier: 'couture', ville: 'togo-autres',
    localite: 'Sokode', quartier: '24CH+M3V',
    pays: 'TG', numero: '9076XXXX',
  },
  {
    nom: '3-D AMITIE',
    metier: 'restaurant', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Calavi Kpota',
    pays: 'BJ', numero: '015229XXXX',
  },
  {
    nom: 'ACHILLE\'S SAVEURS',
    metier: 'restaurant', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Fifansi',
    pays: 'BJ', numero: '019703XXXX',
  },
  {
    nom: 'ADJIKE SERVICES',
    metier: 'restaurant', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Calavi Kpota',
    pays: 'BJ', numero: '019623XXXX',
  },
  {
    nom: 'ABATCHINOU',
    metier: 'restaurant', ville: 'benin-autres',
    localite: 'Dassa-Zoumé', quartier: 'Agbégbé',
    pays: 'BJ', numero: '019732XXXX',
  },
  {
    nom: 'Abraham',
    metier: 'restaurant', ville: 'benin-autres',
    localite: 'Parakou', quartier: '9J3J+7P3 petit pere - Zongo Nord',
    pays: 'BJ', numero: '019784XXXX',
  },
  {
    nom: 'AGAPE DELICE',
    metier: 'restaurant', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'FJR4+JRG Maison NOUNAGNON Antoine, Bd Tokpota',
    pays: 'BJ', numero: '016902XXXX',
  },
  {
    nom: '228 Kebab Kégué',
    metier: 'restaurant', ville: 'lome',
    localite: 'Lomé', quartier: 'Kégué',
    pays: 'TG', numero: '9149XXXX',
  },
  {
    nom: '228 LOVE',
    metier: 'restaurant', ville: 'lome',
    localite: 'Lomé', quartier: 'Agoè Nyive',
    pays: 'TG', numero: '9305XXXX',
  },
  {
    nom: 'Above all food clinic',
    metier: 'restaurant', ville: 'lome',
    localite: 'Lomé', quartier: '70468969 - Kanyikope',
    pays: 'TG', numero: '7046XXXX',
  },
  {
    nom: 'Alogavi la Casa de Cuba',
    metier: 'restaurant', ville: 'togo-autres',
    localite: 'Agbodrafo', quartier: '6F46+P72',
    pays: 'TG', numero: '9391XXXX',
  },
  {
    nom: 'Auberge Edmonton',
    metier: 'restaurant', ville: 'togo-autres',
    localite: 'Adétikopé', quartier: '8698+WQF',
    pays: 'TG', numero: '9001XXXX',
  },
  {
    nom: 'Bar la colombe',
    metier: 'restaurant', ville: 'togo-autres',
    localite: 'N2', quartier: '6F4H+V4F',
    pays: 'TG', numero: '9036XXXX',
  },
  {
    nom: 'ADO GATEAU',
    metier: 'patisserie', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Hêvié',
    pays: 'BJ', numero: '016169XXXX',
  },
  {
    nom: 'ART GOURMET BY HERMES AGBOTON',
    metier: 'patisserie', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Maromilitaire, Cotonou',
    pays: 'BJ', numero: '019885XXXX',
  },
  {
    nom: 'AU DOUCEUR DE LUCIE',
    metier: 'patisserie', ville: 'cotonou',
    localite: 'Cotonou', quartier: '-',
    pays: 'BJ', numero: '019755XXXX',
  },
  {
    nom: 'AYE ET FILS',
    metier: 'patisserie', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Sedjeko',
    pays: 'BJ', numero: '019788XXXX',
  },
  {
    nom: 'ETS BIDOSSESSI ET FILS',
    metier: 'patisserie', ville: 'benin-autres',
    localite: 'Bohicon', quartier: 'Quartier Honmèho situé enface du Jardin Public',
    pays: 'BJ', numero: '019738XXXX',
  },
  {
    nom: 'ETS ETINCELLE',
    metier: 'patisserie', ville: 'benin-autres',
    localite: 'Bohicon', quartier: 'Quartier Sèhouèho situé en face de la Maison des Soeurs Saint Augustin sur la route de Covè',
    pays: 'BJ', numero: '016984XXXX',
  },
  {
    nom: 'ALADIAH DELICES',
    metier: 'patisserie', ville: 'lome',
    localite: 'Lomé', quartier: 'Attiégou, face rue Koklo Ku Ato',
    pays: 'TG', numero: '7012XXXX',
  },
  {
    nom: 'Au Bon Pain GTA',
    metier: 'patisserie', ville: 'lome',
    localite: 'Lomé', quartier: 'Av. de la Chance',
    pays: 'TG', numero: '9296XXXX',
  },
  {
    nom: 'AU FIN PALAIS',
    metier: 'patisserie', ville: 'lome',
    localite: 'Lomé', quartier: 'Route de Misssion Tové',
    pays: 'TG', numero: '9005XXXX',
  },
  {
    nom: 'Boulangerie Baguette',
    metier: 'patisserie', ville: 'togo-autres',
    localite: 'Agouenyive', quartier: '46GG+5J4',
    pays: 'TG', numero: '9360XXXX',
  },
  {
    nom: 'Boulangerie St Michel',
    metier: 'patisserie', ville: 'togo-autres',
    localite: 'Tsevie', quartier: 'Boloumondji',
    pays: 'TG', numero: '9926XXXX',
  },
  {
    nom: 'Tsévié Délices',
    metier: 'patisserie', ville: 'togo-autres',
    localite: 'Tsevie', quartier: 'C686+32R',
    pays: 'TG', numero: '9702XXXX',
  },
]

const INDICATIF = { BJ: '229', TG: '228' }

/* Même règle que le carnet du 2026-08-03 : un fixe n'a pas WhatsApp. */
export function estFixe(pays, numero) {
  if (!numero) return false
  if (pays === 'BJ') return numero.startsWith('0121') || numero.startsWith('0120')
  return numero.startsWith('22')
}

export function numeroJoli(pays, numero) {
  if (!numero) return ''
  const n = numero
  return pays === 'BJ'
    ? `${n.slice(0, 2)} ${n.slice(2, 4)} ${n.slice(4, 6)} ${n.slice(6, 8)} ${n.slice(8, 10)}`
    : `${n.slice(0, 2)} ${n.slice(2, 4)} ${n.slice(4, 6)} ${n.slice(6, 8)}`
}

/* Sur la vitrine : deux chiffres masqués. Dans le carnet livré : tout. */
/* Les fiches d'aperçu portent un numéro COUPÉ à la source : ses quatre
   derniers chiffres n'existent nulle part dans le site (voir `_stock.py`).
   Un masque qui n'existe qu'à l'écran ne masque rien, il décore. */
export function numeroMasque(pays, numero) {
  return numeroJoli(pays, numero).replace(/X/g, '•')
}

export function international(pays, numero) {
  return '+' + INDICATIF[pays] + ' ' + numeroJoli(pays, numero)
}

/* Choisit la fiche d'exemple la plus proche de ce que la personne demande. */
/* Les fiches de l'apercu du generateur : celles du metier ET de la ville
   choisis d'abord, puis celles du metier seul, puis n'importe lesquelles.
   On complete plutot que de rendre une liste vide : l'apercu ne doit jamais
   se retrouver a zero pendant qu'on regle. Aucune fiche n'est inventee. */
export function fichesApercu(metier, ville, combien = 3) {
  const pris = new Set()
  const sortie = []
  const prendre = (liste) => {
    for (const f of liste) {
      if (sortie.length >= combien) return
      if (pris.has(f.nom)) continue
      pris.add(f.nom)
      sortie.push(f)
    }
  }
  prendre(FICHES.filter((f) => f.metier === metier && f.ville === ville))
  prendre(FICHES.filter((f) => f.metier === metier))
  prendre(FICHES.filter((f) => f.ville === ville))
  prendre(FICHES)
  return sortie
}

export function ficheExemple(metier, ville) {
  return (
    FICHES.find((f) => f.metier === metier && f.ville === ville) ||
    FICHES.find((f) => f.metier === metier) ||
    FICHES.find((f) => f.ville === ville) ||
    FICHES[0]
  )
}

/* Le message qui accompagne chaque fiche, écrit à partir de la phrase de
   l'acheteur et du métier du commerçant. C'est un vrai message, pas une
   maquette : c'est exactement ce que le carnet contient.

   ⚠️ La salutation reste « Bonjour, » dans cet exemple. Le nom du dirigeant
   se pose exactement là quand le supplément est pris, mais PISTE n'affiche
   pas un nom qu'il n'a pas relevé : ce serait une fausse donnée. */
export function messagePourFiche(fiche, offre) {
  const m = METIERS.find((x) => x.cle === fiche.metier)
  const lieu = [fiche.quartier, fiche.localite].filter(Boolean).join(', ')
  const phrase = (offre || '').trim().replace(/[.\s]+$/, '')
  return [
    'Bonjour,',
    `Je vous écris au sujet de ${fiche.nom}, votre ${m.singulier} à ${lieu}.`,
    phrase
      ? `${phrase.charAt(0).toUpperCase()}${phrase.slice(1)}.`
      : 'Je vous écris au sujet de ce que je propose aux commerces comme le vôtre.',
    'Est-ce que je peux vous en dire deux mots ? Ça prend deux minutes.',
  ].join('\n\n')
}
