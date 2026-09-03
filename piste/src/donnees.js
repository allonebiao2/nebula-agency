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

  Décision 25, corrigée le 2026-08-04 : MTN MoMo du Bénin, et rien d'autre.
  Tant qu'un `numero` vaut `null`, l'écran de paiement le dit franchement et
  renvoie sur WhatsApp : PISTE n'affiche jamais un numéro qu'il n'a pas, et un
  faux numéro de paiement coûterait bien plus cher qu'une phrase honnête.

    numero    : les 10 chiffres, format béninois (ex. '0196740732')
    titulaire : le nom qui s'affiche à l'écran de l'acheteur quand il valide
*/
export const MOBILE_MONEY = [
  /* ⚠️ MTN SEUL pour l'instant (Mongazi, 2026-08-04). Moov Flooz a été retiré :
     annoncer un moyen de paiement qu'on ne peut pas encaisser, c'est promettre
     un virement qui n'arrivera jamais. On le remettra le jour où le compte
     existe, pas avant. */
  {
    cle: 'mtn',
    operateur: 'MTN MoMo',
    numero: '01 96 74 07 32',
    titulaire: 'BIAO Mongazi Yan Karl',
  },
]

/* ⚠️ LE NUMÉRO DE DÉPÔT N'EST PAS LE NUMÉRO WHATSAPP. Celui sur lequel on écrit
   à NEBULA et celui qui reçoit l'argent sont deux numéros différents. Tant que
   le numéro de dépôt n'est pas posé ici, il est donné à la main dans la
   conversation WhatsApp, et le site ne l'invente pas. */
export const MOMO_DEPOT = '0196740732'
export const MOMO_DEPOT_JOLI = '01 96 74 07 32'
export const MOMO_TITULAIRE = 'BIAO Mongazi Yan Karl'

export const MOMO_PRET = MOBILE_MONEY.some((m) => m.numero)

/*
  ⚠️ LE PAIEMENT EN LIGNE (SasPay) EST FERMÉ TANT QUE CE DRAPEAU EST `false`.

  Décision 27 : jusqu'ici, Mongazi regarde son application Mobile Money et
  rapproche lui-même. SasPay permettrait au client de payer depuis la page, et
  à la commande de se marquer « payée » toute seule.

  ✅ OUVERT LE 2026-09-03, sur décision de Mongazi. Le doute qui tenait ce
  drapeau fermé portait sur la devise : le tableau de bord montrait des
  montants en CDF. Il est levé, et pas sur parole — SasPay a accepté et rendu
  de vraies sessions en XOF, dont une de 4 320 F pour une commande réelle.

  ⚠️ CE QUI RESTE NON PROUVÉ : que la notification de paiement se rattache
  toute seule à la commande. SasPay n'envoie ni notre référence ni le numéro
  de session, seulement le sien ; le lien se refait en relisant la session de
  checkout, et ça ne se vérifie qu'au premier vrai paiement.

  ⚠️ CE QUE ÇA COÛTE SI ÇA RATE, et c'est pour ça qu'on peut ouvrir : l'argent
  arrive quand même chez SasPay, et tout est écrit dans
  `piste.paiement_evenement`. Le pire cas, c'est le rapprochement à la main,
  exactement ce qui se fait aujourd'hui. Rien n'est perdu et rien n'est promis
  de faux : la page de retour dit en toutes lettres qu'elle n'est pas un reçu.

  ⛔ TANT QUE LE PREMIER PAIEMENT N'A PAS ÉTÉ VU BOUT EN BOUT, regarder le
  journal après chaque commande payée en ligne :
      select recu_le, reference, montant, etat_lu, agi
        from piste.paiement_evenement order by id desc limit 10;
  Une ligne « sans commande » veut dire que quelqu'un a payé et que personne
  n'a été prévenu.

  ⚠️ Le chemin Mobile Money à la main NE DISPARAÎT PAS quand ce drapeau passe
  à `true` : il reste dessous, en second. Un moyen de paiement neuf se met à
  côté de celui qui marche, jamais à sa place.
*/
export const SASPAY_PRET = true

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
    pluriel: 'ateliers de couture',
    nom: 'Couture et mode',
    court: 'Couture',
    singulier: 'atelier de couture',
    exemple: 'tailleurs, couturières, brodeurs, prêt-à-porter',
  },
  {
    cle: 'restaurant',
    pluriel: 'restaurants',
    nom: 'Restaurants, maquis et bars',
    court: 'Restaurants',
    singulier: 'restaurant',
    exemple: 'restaurants, maquis, bars, buvettes, traiteurs',
  },
  {
    cle: 'patisserie',
    pluriel: 'pâtisseries',
    nom: 'Pâtisseries et boulangeries',
    court: 'Pâtisseries',
    singulier: 'pâtisserie',
    exemple: 'patissiers, boulangers',
  },
  {
    cle: 'beaute',
    pluriel: 'salons de beauté',
    nom: 'Beauté et bien-être',
    court: 'Beauté',
    singulier: 'salon de beauté',
    exemple: 'salons de coiffure, instituts, spas',
  },
  {
    cle: 'alimentation',
    pluriel: 'commerces d\'alimentation',
    nom: 'Alimentation et supermarchés',
    court: 'Alimentation',
    singulier: 'commerce d\'alimentation',
    exemple: 'épiceries, supermarchés, poissonneries',
  },
  {
    cle: 'quincaillerie',
    pluriel: 'quincailleries',
    nom: 'Quincaillerie et bâtiment',
    court: 'Quincaillerie',
    singulier: 'quincaillerie',
    exemple: 'quincailleries, plomberie, vitrerie, bâtiment',
  },
  {
    cle: 'auto',
    pluriel: 'garages',
    nom: 'Auto, moto et pièces',
    court: 'Auto',
    singulier: 'garage',
    exemple: 'garages, pièces détachées, vente de motos',
  },
  {
    cle: 'maison',
    pluriel: 'magasins de décoration',
    nom: 'Maison et décoration',
    court: 'Maison',
    singulier: 'magasin de décoration',
    exemple: 'ameublement, décoration, produits d\'entretien',
  },
  {
    cle: 'sante',
    pluriel: 'pharmacies',
    nom: 'Santé et pharmacies',
    court: 'Santé',
    singulier: 'cabinet de santé',
    exemple: 'cabinets, pharmacies, vétérinaires',
  },
  {
    cle: 'ecole',
    pluriel: 'écoles',
    nom: 'Écoles et formation',
    court: 'Écoles',
    singulier: 'établissement scolaire',
    exemple: 'écoles, centres de formation',
  },
  {
    cle: 'informatique',
    pluriel: 'cybercafés',
    nom: 'Informatique et cybercafés',
    court: 'Informatique',
    singulier: 'commerce informatique',
    exemple: 'cybercafés, vente de matériel, téléphonie',
  },
  {
    cle: 'imprimerie',
    pluriel: 'imprimeries',
    nom: 'Imprimerie et communication',
    court: 'Imprimerie',
    singulier: 'imprimerie',
    exemple: 'imprimeries, agences de communication',
  },
  {
    cle: 'hotel',
    pluriel: 'hôtels',
    nom: 'Hôtels et tourisme',
    court: 'Hôtels',
    singulier: 'hôtel',
    exemple: 'hôtels, auberges, tourisme',
  },
  {
    cle: 'immobilier',
    pluriel: 'agences immobilières',
    nom: 'Immobilier',
    court: 'Immobilier',
    singulier: 'agence immobilière',
    exemple: 'agences et promoteurs immobiliers',
  },
  {
    cle: 'transport',
    pluriel: 'transporteurs',
    nom: 'Transport et voyage',
    court: 'Transport',
    singulier: 'société de transport',
    exemple: 'transporteurs, courrier, agences de voyage',
  },
  {
    cle: 'services',
    pluriel: 'sociétés de services',
    nom: 'Services aux entreprises',
    court: 'Services aux entreprises',
    singulier: 'société de services',
    exemple: 'nettoyage, gardiennage, comptabilité, assurance',
  },
  {
    cle: 'artisan',
    pluriel: 'artisans',
    nom: 'Artisans et art',
    court: 'Artisans',
    singulier: 'artisan',
    exemple: 'artisans, galeries d\'art, articles de sport',
  },
  {
    cle: 'commerce',
    pluriel: 'commerces',
    nom: 'Commerces divers',
    court: 'Commerces divers',
    singulier: 'commerce',
    exemple: 'import-export, negoce, commerces divers',
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
    detail: 'Cocody, Yopougon, Treichville, Plateau, Marcory, Abobo…',
  },
  {
    cle: 'ci-autres',
    court: "une autre ville de Côte d'Ivoire",
    nom: "Autres villes de Côte d'Ivoire",
    pays: "Côte d'Ivoire",
    detail: 'Bouaké, Yamoussoukro, San-Pédro, Korhogo…',
  },
]

/* L'inventaire, écrit à la main à partir des comptes ci-dessus.
   En V2 il viendra de la base. Clé : `metier|ville`. */
export const STOCK = {
  'couture|cotonou': 325,
  'couture|benin-autres': 33,
  'couture|lome': 167,
  'couture|togo-autres': 3,
  'couture|abidjan': 330,
  'couture|ci-autres': 46,
  'restaurant|cotonou': 297,
  'restaurant|benin-autres': 121,
  'restaurant|lome': 295,
  'restaurant|togo-autres': 51,
  'restaurant|abidjan': 165,
  'restaurant|ci-autres': 23,
  'patisserie|cotonou': 94,
  'patisserie|benin-autres': 13,
  'patisserie|lome': 48,
  'patisserie|togo-autres': 3,
  'patisserie|abidjan': 52,
  'patisserie|ci-autres': 25,
  'beaute|cotonou': 68,
  'beaute|benin-autres': 8,
  'beaute|lome': 57,
  'beaute|togo-autres': 3,
  'beaute|abidjan': 186,
  'beaute|ci-autres': 7,
  'alimentation|cotonou': 49,
  'alimentation|benin-autres': 6,
  'alimentation|lome': 46,
  'alimentation|togo-autres': 10,
  'alimentation|abidjan': 218,
  'alimentation|ci-autres': 57,
  'quincaillerie|cotonou': 128,
  'quincaillerie|benin-autres': 63,
  'quincaillerie|lome': 100,
  'quincaillerie|togo-autres': 8,
  'quincaillerie|abidjan': 246,
  'quincaillerie|ci-autres': 38,
  'auto|cotonou': 79,
  'auto|benin-autres': 11,
  'auto|lome': 74,
  'auto|togo-autres': 1,
  'auto|abidjan': 138,
  'auto|ci-autres': 11,
  'maison|cotonou': 92,
  'maison|benin-autres': 3,
  'maison|lome': 47,
  'maison|togo-autres': 1,
  'maison|abidjan': 119,
  'maison|ci-autres': 7,
  'sante|cotonou': 29,
  'sante|benin-autres': 12,
  'sante|lome': 18,
  'sante|togo-autres': 1,
  'sante|abidjan': 105,
  'sante|ci-autres': 6,
  'ecole|cotonou': 66,
  'ecole|benin-autres': 10,
  'ecole|lome': 116,
  'ecole|togo-autres': 6,
  'ecole|abidjan': 102,
  'ecole|ci-autres': 42,
  'informatique|cotonou': 17,
  'informatique|benin-autres': 1,
  'informatique|lome': 53,
  'informatique|togo-autres': 9,
  'informatique|abidjan': 17,
  'informatique|ci-autres': 21,
  'imprimerie|cotonou': 141,
  'imprimerie|benin-autres': 22,
  'imprimerie|lome': 133,
  'imprimerie|togo-autres': 2,
  'imprimerie|abidjan': 189,
  'imprimerie|ci-autres': 10,
  'hotel|cotonou': 37,
  'hotel|benin-autres': 8,
  'hotel|lome': 44,
  'hotel|togo-autres': 36,
  'hotel|abidjan': 10,
  'hotel|ci-autres': 24,
  'immobilier|cotonou': 83,
  'immobilier|benin-autres': 13,
  'immobilier|lome': 101,
  'immobilier|togo-autres': 4,
  'immobilier|abidjan': 136,
  'immobilier|ci-autres': 12,
  'transport|cotonou': 116,
  'transport|benin-autres': 12,
  'transport|lome': 62,
  'transport|togo-autres': 1,
  'transport|abidjan': 190,
  'transport|ci-autres': 2,
  'services|cotonou': 404,
  'services|benin-autres': 32,
  'services|lome': 269,
  'services|togo-autres': 9,
  'services|abidjan': 541,
  'services|ci-autres': 49,
  'artisan|cotonou': 39,
  'artisan|benin-autres': 1,
  'artisan|lome': 58,
  'artisan|togo-autres': 1,
  'artisan|abidjan': 99,
  'artisan|ci-autres': 15,
  'commerce|cotonou': 39,
  'commerce|benin-autres': 69,
  'commerce|lome': 49,
  'commerce|togo-autres': 1,
  'commerce|abidjan': 143,
  'commerce|ci-autres': 8,
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
export const NOMBRE_FIXES = 2248

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
    nom: '2Y STORE',
    metier: 'couture', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Grand carrefour de KOUMASSI non loin du 6ème arrondissement',
    pays: 'CI', numero: '070749XXXX',
  },
  {
    nom: '3 PETITS MECS',
    metier: 'couture', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Non loin de la Mosquée - Maroc',
    pays: 'CI', numero: '075940XXXX',
  },
  {
    nom: '7 CAMICIE',
    metier: 'couture', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Bd. VGE, Orca deco, 2eme étage - Zone 4 C',
    pays: 'CI', numero: '077777XXXX',
  },
  {
    nom: 'AB FASHION',
    metier: 'couture', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Quartier Colas',
    pays: 'CI', numero: '054696XXXX',
  },
  {
    nom: 'ABOU GONAISE',
    metier: 'couture', ville: 'ci-autres',
    localite: 'Bouaké', quartier: 'Commerce',
    pays: 'CI', numero: '075972XXXX',
  },
  {
    nom: 'ADAM\'S COUTURE',
    metier: 'couture', ville: 'ci-autres',
    localite: 'Abengourou', quartier: 'Face auto-école de l\'est',
    pays: 'CI', numero: '014250XXXX',
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
    nom: '100 % LIVE',
    metier: 'restaurant', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Vridi Cité - Zone Industrielle Vridi',
    pays: 'CI', numero: '050450XXXX',
  },
  {
    nom: '1ST CHOISE RESTAURANT',
    metier: 'restaurant', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Carrefour colombe, Près de l\'école la colombe',
    pays: 'CI', numero: '056482XXXX',
  },
  {
    nom: '237 Lounge-Bar',
    metier: 'restaurant', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Cocody - Cité des Arts - Cocody',
    pays: 'CI', numero: '077784XXXX',
  },
  {
    nom: '2 SANS 3',
    metier: 'restaurant', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Carrefour Moossou',
    pays: 'CI', numero: '010215XXXX',
  },
  {
    nom: '25/8 Terrasse',
    metier: 'restaurant', ville: 'ci-autres',
    localite: 'Yamoussoukro', quartier: 'RP5Q+V3M',
    pays: 'CI', numero: '078995XXXX',
  },
  {
    nom: 'A L\'AVIKAM',
    metier: 'restaurant', ville: 'ci-autres',
    localite: 'Yamoussoukro', quartier: '-',
    pays: 'CI', numero: '057609XXXX',
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
  {
    nom: 'A D E A L',
    metier: 'patisserie', ville: 'abidjan',
    localite: 'Abidjan', quartier: '-',
    pays: 'CI', numero: '070707XXXX',
  },
  {
    nom: 'ACIMAK PRESTATION',
    metier: 'patisserie', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Près du groupe scolaire Gandhi',
    pays: 'CI', numero: '076895XXXX',
  },
  {
    nom: 'AFFOUET GOURMET',
    metier: 'patisserie', ville: 'abidjan',
    localite: 'Bingerville', quartier: 'Feh Késsé',
    pays: 'CI', numero: '056654XXXX',
  },
  {
    nom: 'Au meilleur des pains',
    metier: 'patisserie', ville: 'ci-autres',
    localite: 'Gagnoa', quartier: '43J4+XFH, Unnamed Road',
    pays: 'CI', numero: '054600XXXX',
  },
  {
    nom: 'Boulangerie',
    metier: 'patisserie', ville: 'ci-autres',
    localite: 'Koun-Fao', quartier: 'FPRW+3CC',
    pays: 'CI', numero: '076767XXXX',
  },
  {
    nom: 'BOULANGERIE BAGUETTE DÉLICIEUSE',
    metier: 'patisserie', ville: 'ci-autres',
    localite: 'Gagnoa', quartier: '4366+2W8',
    pays: 'CI', numero: '015050XXXX',
  },
  {
    nom: '2A COIFFURE ET TRESSE',
    metier: 'beaute', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Akpakpa, Sénandé',
    pays: 'BJ', numero: '019517XXXX',
  },
  {
    nom: '3AB',
    metier: 'beaute', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: '-',
    pays: 'BJ', numero: '014698XXXX',
  },
  {
    nom: 'ABEWO BEAUTY',
    metier: 'beaute', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Sénandé',
    pays: 'BJ', numero: '016262XXXX',
  },
  {
    nom: 'ARVEA BEAUTY',
    metier: 'beaute', ville: 'benin-autres',
    localite: 'Parakou', quartier: '-',
    pays: 'BJ', numero: '019019XXXX',
  },
  {
    nom: 'BEN MASSAGE',
    metier: 'beaute', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'GJ2P+PXJ, Unnamed Road',
    pays: 'BJ', numero: '019614XXXX',
  },
  {
    nom: 'DRUKENLOKO',
    metier: 'beaute', ville: 'benin-autres',
    localite: 'Come', quartier: 'BP 251',
    pays: 'BJ', numero: '016121XXXX',
  },
  {
    nom: '3BI(Bernice Beauty Bar and Institute)',
    metier: 'beaute', ville: 'lome',
    localite: 'Lomé', quartier: 'En face de ISDI, non loin de la Rue Djapotado, Rue Djapotado',
    pays: 'TG', numero: '9133XXXX',
  },
  {
    nom: 'ACCESS BARS',
    metier: 'beaute', ville: 'lome',
    localite: 'Lomé', quartier: 'A côté de l\'ancienne Ecole Américaine',
    pays: 'TG', numero: '9349XXXX',
  },
  {
    nom: 'AFRICA BLACK BEAUTY',
    metier: 'beaute', ville: 'lome',
    localite: 'Lomé', quartier: 'Sagbado',
    pays: 'TG', numero: '9350XXXX',
  },
  {
    nom: 'AURORA BEAUTY',
    metier: 'beaute', ville: 'togo-autres',
    localite: 'Assahoun', quartier: 'Assahoun',
    pays: 'TG', numero: '9913XXXX',
  },
  {
    nom: 'DOSTAL MANUCURE PEDICURE',
    metier: 'beaute', ville: 'togo-autres',
    localite: 'Kara', quartier: 'En face de l\'immeuble LUFTHANSA',
    pays: 'TG', numero: '2450XXXX',
  },
  {
    nom: 'Empreinte D',
    metier: 'beaute', ville: 'togo-autres',
    localite: 'Baguida', quartier: 'Rue de la Paroisse',
    pays: 'TG', numero: '9014XXXX',
  },
  {
    nom: '4e DIMENSION',
    metier: 'beaute', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Carrefour ancien Ambassade de Chine - Angré 7è tranche',
    pays: 'CI', numero: '074914XXXX',
  },
  {
    nom: 'A ESTHETIQUE',
    metier: 'beaute', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Imm. Kaladji',
    pays: 'CI', numero: '050596XXXX',
  },
  {
    nom: 'A+ESTHETIQUE',
    metier: 'beaute', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Avocatier',
    pays: 'CI', numero: '058689XXXX',
  },
  {
    nom: 'ASHLEY BEAUTE',
    metier: 'beaute', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Quartier Impérial',
    pays: 'CI', numero: '074810XXXX',
  },
  {
    nom: 'BEKANTY BEAUTE',
    metier: 'beaute', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Quartier Seweke',
    pays: 'CI', numero: '050581XXXX',
  },
  {
    nom: 'BERNADETTE COIFFURE',
    metier: 'beaute', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Quartier Château',
    pays: 'CI', numero: '010189XXXX',
  },
  {
    nom: 'AGRIPACK STORE',
    metier: 'alimentation', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Agla Hlazouto 1er Pont',
    pays: 'BJ', numero: '019735XXXX',
  },
  {
    nom: 'ARITA FOODS AFRICA - AFA BENIN',
    metier: 'alimentation', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'En face du CEB, non loin de la mairie',
    pays: 'BJ', numero: '016202XXXX',
  },
  {
    nom: 'AVI PISCIL BENIN',
    metier: 'alimentation', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: '-',
    pays: 'BJ', numero: '019611XXXX',
  },
  {
    nom: 'ETS MABEL',
    metier: 'alimentation', ville: 'benin-autres',
    localite: 'Ifangni', quartier: 'Ganmi Maison AGOGNON',
    pays: 'BJ', numero: '019555XXXX',
  },
  {
    nom: 'FLOCON SARL',
    metier: 'alimentation', ville: 'benin-autres',
    localite: 'Abomey', quartier: 'Abomey-calavi',
    pays: 'BJ', numero: '016183XXXX',
  },
  {
    nom: 'LEREEL PRODUCTION',
    metier: 'alimentation', ville: 'benin-autres',
    localite: 'Sékou', quartier: '-',
    pays: 'BJ', numero: '014483XXXX',
  },
  {
    nom: 'A. PRINTEMPS',
    metier: 'alimentation', ville: 'lome',
    localite: 'Lomé', quartier: 'Rue de l\'Entente',
    pays: 'TG', numero: '9949XXXX',
  },
  {
    nom: 'AFRI FOOD',
    metier: 'alimentation', ville: 'lome',
    localite: 'Lomé', quartier: 'Nationale N°2, Agbodrafo, BP 13534',
    pays: 'TG', numero: '9001XXXX',
  },
  {
    nom: 'Aura',
    metier: 'alimentation', ville: 'lome',
    localite: 'Lomé', quartier: '10, Avenue Sylvanus, Olympio, Adawlato Opposite Hotel du Golfe',
    pays: 'TG', numero: '9908XXXX',
  },
  {
    nom: 'Amadou CAMARA',
    metier: 'alimentation', ville: 'togo-autres',
    localite: 'Kande', quartier: '-',
    pays: 'TG', numero: '9391XXXX',
  },
  {
    nom: 'Ampia Kado Shop',
    metier: 'alimentation', ville: 'togo-autres',
    localite: 'Dapaong', quartier: 'V623+62P',
    pays: 'TG', numero: '9090XXXX',
  },
  {
    nom: 'Ave - Maria',
    metier: 'alimentation', ville: 'togo-autres',
    localite: 'Atakpame', quartier: '-',
    pays: 'TG', numero: '9036XXXX',
  },
  {
    nom: '2AB',
    metier: 'alimentation', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Non loin de l\'Eglise Sainte Monique - Plateau Dokui',
    pays: 'CI', numero: '070744XXXX',
  },
  {
    nom: 'AB CENTER',
    metier: 'alimentation', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Carrefour AB center, route Abatta - Akouedo',
    pays: 'CI', numero: '014250XXXX',
  },
  {
    nom: 'AIM SIKA SHOP',
    metier: 'alimentation', ville: 'abidjan',
    localite: 'Abidjan', quartier: '- - Angré 8è tranche',
    pays: 'CI', numero: '010364XXXX',
  },
  {
    nom: 'ALIMENTATION DU LAC',
    metier: 'alimentation', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Quartier Lac',
    pays: 'CI', numero: '070835XXXX',
  },
  {
    nom: 'BALLO & FRERES',
    metier: 'alimentation', ville: 'ci-autres',
    localite: 'Bouaké', quartier: 'Grand Marché',
    pays: 'CI', numero: '070769XXXX',
  },
  {
    nom: 'BENKADI',
    metier: 'alimentation', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Cité Poro, au carrefour de la ruche',
    pays: 'CI', numero: '070763XXXX',
  },
  {
    nom: 'A. G. ET FILS',
    metier: 'quincaillerie', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Sèmè C/SB Maison Gahou Aguiar',
    pays: 'BJ', numero: '019374XXXX',
  },
  {
    nom: 'ACOTRAC COMPAGNIE',
    metier: 'quincaillerie', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Tori Dévounkan',
    pays: 'BJ', numero: '015889XXXX',
  },
  {
    nom: 'AD GROUP',
    metier: 'quincaillerie', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Togoudo',
    pays: 'BJ', numero: '019739XXXX',
  },
  {
    nom: 'A. R. AGNIDE ET FILS',
    metier: 'quincaillerie', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Kandevie',
    pays: 'BJ', numero: '019090XXXX',
  },
  {
    nom: 'AKATEC',
    metier: 'quincaillerie', ville: 'benin-autres',
    localite: 'Bohicon', quartier: 'Non loin de l\'OCBN',
    pays: 'BJ', numero: '019726XXXX',
  },
  {
    nom: 'APES',
    metier: 'quincaillerie', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Agata au bord du goudron juste avant le carrefour, quittant le carrefour Hounsa pour agata.',
    pays: 'BJ', numero: '019676XXXX',
  },
  {
    nom: 'A.BRUXELLES',
    metier: 'quincaillerie', ville: 'lome',
    localite: 'Lomé', quartier: '228',
    pays: 'TG', numero: '9285XXXX',
  },
  {
    nom: 'AD ET FRERES',
    metier: 'quincaillerie', ville: 'lome',
    localite: 'Lomé', quartier: 'Rue Kéyidzi 99 HDN, Vers Lomé II',
    pays: 'TG', numero: '9036XXXX',
  },
  {
    nom: 'AKWAABA',
    metier: 'quincaillerie', ville: 'lome',
    localite: 'Lomé', quartier: '74, Rue du Passage des Boeufs, Akodésséwa Kpota, BP 12913',
    pays: 'TG', numero: '9091XXXX',
  },
  {
    nom: 'BE CLEVER',
    metier: 'quincaillerie', ville: 'togo-autres',
    localite: 'Songo M\'boké', quartier: '772G+2RV, Unnamed Road',
    pays: 'TG', numero: '9021XXXX',
  },
  {
    nom: 'Chez Ali',
    metier: 'quincaillerie', ville: 'togo-autres',
    localite: 'Temedja', quartier: '90159410',
    pays: 'TG', numero: '9280XXXX',
  },
  {
    nom: 'Cimao',
    metier: 'quincaillerie', ville: 'togo-autres',
    localite: 'Mango', quartier: '37',
    pays: 'TG', numero: '9027XXXX',
  },
  {
    nom: '2AA GROUPE PLOMBERIE',
    metier: 'quincaillerie', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Boulevard Latrille , Angre 7e tranche',
    pays: 'CI', numero: '070000XXXX',
  },
  {
    nom: '2AAGROUP SERVICE CI',
    metier: 'quincaillerie', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Remblais rue H 180',
    pays: 'CI', numero: '054557XXXX',
  },
  {
    nom: 'A PLUS ENGINEERING AND CONTRACTING',
    metier: 'quincaillerie', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Marcory rue Paul Langevin Orca Mall 6eme étage',
    pays: 'CI', numero: '050094XXXX',
  },
  {
    nom: 'BAMBA MERCI',
    metier: 'quincaillerie', ville: 'ci-autres',
    localite: 'Yamoussoukro', quartier: 'Habitat',
    pays: 'CI', numero: '010214XXXX',
  },
  {
    nom: 'BAT QG',
    metier: 'quincaillerie', ville: 'ci-autres',
    localite: 'Bouaké', quartier: 'Bat-qg',
    pays: 'CI', numero: '070392XXXX',
  },
  {
    nom: 'BAT-QG',
    metier: 'quincaillerie', ville: 'ci-autres',
    localite: 'Bouaké', quartier: 'Belle ville konankro',
    pays: 'CI', numero: '070392XXXX',
  },
  {
    nom: '@DECO',
    metier: 'auto', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Ste Rita C/N°1341',
    pays: 'BJ', numero: '019596XXXX',
  },
  {
    nom: 'AHOUANSOU YÊHOUENOU ET FILS',
    metier: 'auto', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Ekpê',
    pays: 'BJ', numero: '019716XXXX',
  },
  {
    nom: 'ARB-GALAXIE Sarl',
    metier: 'auto', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Ilot 0017',
    pays: 'BJ', numero: '019615XXXX',
  },
  {
    nom: 'A à Z MOTORS',
    metier: 'auto', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'PK 11',
    pays: 'BJ', numero: '019872XXXX',
  },
  {
    nom: 'AUTODELIVERY BENIN Sarl',
    metier: 'auto', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Von face ciné IRE-AKARI, Quartier Ayimlonfidé',
    pays: 'BJ', numero: '016193XXXX',
  },
  {
    nom: 'BOUKARI & FILS',
    metier: 'auto', ville: 'benin-autres',
    localite: 'Parakou', quartier: 'Rue Diamond Bank',
    pays: 'BJ', numero: '016605XXXX',
  },
  {
    nom: 'A DIEU LA FORCE',
    metier: 'auto', ville: 'lome',
    localite: 'Lomé', quartier: 'Route Nationale N°1, A Côté de l\'Imm. AK GTA, Massohoen, BP 7448',
    pays: 'TG', numero: '9926XXXX',
  },
  {
    nom: 'ACHETERAUTO AO TOGO',
    metier: 'auto', ville: 'lome',
    localite: 'Lomé', quartier: 'Minamadou',
    pays: 'TG', numero: '9356XXXX',
  },
  {
    nom: 'AFRICAVMAUTO.COM',
    metier: 'auto', ville: 'lome',
    localite: 'Lomé', quartier: 'Port Autonome de Lomé',
    pays: 'TG', numero: '9210XXXX',
  },
  {
    nom: 'JAMBES BUSINESS ONLINE 2',
    metier: 'auto', ville: 'togo-autres',
    localite: 'Tsévié', quartier: 'Tsevié Boloumondji',
    pays: 'TG', numero: '9958XXXX',
  },
  {
    nom: '4 ROUES',
    metier: 'auto', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'YOPOUGON',
    pays: 'CI', numero: '076852XXXX',
  },
  {
    nom: 'AFRICA BUILDERS GROUP',
    metier: 'auto', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Angré, grand carrefour du Mahou, en bordure de route',
    pays: 'CI', numero: '055565XXXX',
  },
  {
    nom: 'AFRIKA-IRAN',
    metier: 'auto', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Immeuble Banque UBA - Sable',
    pays: 'CI', numero: '055558XXXX',
  },
  {
    nom: 'ACCESS BOUBA',
    metier: 'auto', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Bardot Marché',
    pays: 'CI', numero: '050441XXXX',
  },
  {
    nom: 'APSONIC',
    metier: 'auto', ville: 'ci-autres',
    localite: 'Bouaké', quartier: 'Dar-es-salam, Grand marché',
    pays: 'CI', numero: '075767XXXX',
  },
  {
    nom: 'APSONIC MOTOR',
    metier: 'auto', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Bardot, Marché',
    pays: 'CI', numero: '054508XXXX',
  },
  {
    nom: '2AG ENTENTE',
    metier: 'maison', ville: 'cotonou',
    localite: 'Cotonou', quartier: '-',
    pays: 'BJ', numero: '019369XXXX',
  },
  {
    nom: 'AFRIQUE MEUBLE',
    metier: 'maison', ville: 'cotonou',
    localite: 'Cotonou', quartier: '-',
    pays: 'BJ', numero: '019797XXXX',
  },
  {
    nom: 'ALIBERT PRODUCTS NIGERIA LIMITED',
    metier: 'maison', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Av. Mgr Steinmetz, face zoom service',
    pays: 'BJ', numero: '019416XXXX',
  },
  {
    nom: 'ATC LES ARTS',
    metier: 'maison', ville: 'benin-autres',
    localite: 'Ketou', quartier: 'Massafe',
    pays: 'BJ', numero: '019581XXXX',
  },
  {
    nom: 'BRISHOP',
    metier: 'maison', ville: 'benin-autres',
    localite: 'Adjarra', quartier: 'Porto-Novo précisément à Gbôdjê',
    pays: 'BJ', numero: '016614XXXX',
  },
  {
    nom: 'TOUT COMME CHEZ VOUS JUSTE BE',
    metier: 'maison', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'St Pierre Paul',
    pays: 'BJ', numero: '019733XXXX',
  },
  {
    nom: 'ADRIANO\'S',
    metier: 'maison', ville: 'lome',
    localite: 'Lomé', quartier: 'Baguida, près du CEG',
    pays: 'TG', numero: '9826XXXX',
  },
  {
    nom: 'AFRICA MODERN DESIGN-AMD',
    metier: 'maison', ville: 'lome',
    localite: 'Lomé', quartier: 'Bd. Jean-Paul II face à la FTF, à côté de la pharmacie Aphoteka',
    pays: 'TG', numero: '9167XXXX',
  },
  {
    nom: 'AFROBATCH',
    metier: 'maison', ville: 'lome',
    localite: 'Lomé', quartier: 'Non loin du Collège des Plateaux',
    pays: 'TG', numero: '9370XXXX',
  },
  {
    nom: 'GALERIE BELLA QUEEN',
    metier: 'maison', ville: 'togo-autres',
    localite: 'Agou', quartier: 'AGOE-CARREFOUR BLEU, VOIE COOPECFI, ANGLE-RUE 2eme VON À DROITE.',
    pays: 'TG', numero: '9338XXXX',
  },
  {
    nom: '3K HOME',
    metier: 'maison', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Pont Soro - Angré 8è tranche',
    pays: 'CI', numero: '075801XXXX',
  },
  {
    nom: 'ABASS SALANNI',
    metier: 'maison', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Ligne 11, Face au marché poulets',
    pays: 'CI', numero: '070973XXXX',
  },
  {
    nom: 'ABBEY DECO RIDEAU',
    metier: 'maison', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Près de la station OILIBYA - Banco 2',
    pays: 'CI', numero: '070718XXXX',
  },
  {
    nom: 'ETS HD',
    metier: 'maison', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Près de la plage Felix Houphouet Boigny',
    pays: 'CI', numero: '070757XXXX',
  },
  {
    nom: 'GALERIE BERNO',
    metier: 'maison', ville: 'ci-autres',
    localite: 'Yamoussoukro', quartier: '220 Logements derrière la BICICI',
    pays: 'CI', numero: '050596XXXX',
  },
  {
    nom: 'GALERIE DE LA FONDATION \'\'LUMIERE DU SAHEL\'\'',
    metier: 'maison', ville: 'ci-autres',
    localite: 'Yamoussoukro', quartier: 'Dioulabougou',
    pays: 'CI', numero: '056612XXXX',
  },
  {
    nom: 'C. ALPHONSE TODESSAVI',
    metier: 'sante', ville: 'cotonou',
    localite: 'Cotonou', quartier: '-',
    pays: 'BJ', numero: '019711XXXX',
  },
  {
    nom: 'CABINET DE CONSEIL TECHNICO ECONOMIQUE DE ELEVAGES - 2CT2E',
    metier: 'sante', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Agassa-godomey, 3 Km from misséssinto crossroad',
    pays: 'BJ', numero: '019684XXXX',
  },
  {
    nom: 'CABINET MEDICAL SAINT PIERRE ET PAUL',
    metier: 'sante', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Agori',
    pays: 'BJ', numero: '016906XXXX',
  },
  {
    nom: 'CABINET DE CARDIOLOGUE COEUR SANTE',
    metier: 'sante', ville: 'benin-autres',
    localite: 'Port-novo', quartier: 'Rue Avant L\'Ecole Normale Supérieure, En Venant du Carrefour Nadjo',
    pays: 'BJ', numero: '016959XXXX',
  },
  {
    nom: 'CABINET VETERINAIRE',
    metier: 'sante', ville: 'benin-autres',
    localite: 'Ndali', quartier: 'BP 22',
    pays: 'BJ', numero: '012362XXXX',
  },
  {
    nom: 'CLINIQUE DEA VETERINAIRE CONSEIL',
    metier: 'sante', ville: 'benin-autres',
    localite: 'Parakou', quartier: 'BP 345',
    pays: 'BJ', numero: '012361XXXX',
  },
  {
    nom: 'cabinet cardiologique myosotis',
    metier: 'sante', ville: 'lome',
    localite: 'Lomé', quartier: '01 bp 4021 - Agbalepedogan',
    pays: 'TG', numero: '9001XXXX',
  },
  {
    nom: 'Cabinet Veterinaire Dr. Ribereau',
    metier: 'sante', ville: 'lome',
    localite: 'Lomé', quartier: '07 BP 14389',
    pays: 'TG', numero: '9368XXXX',
  },
  {
    nom: 'Centre Vétérinaire Saint Marie-Antoine de la cité',
    metier: 'sante', ville: 'lome',
    localite: 'Lomé', quartier: '589R+77W, N2',
    pays: 'TG', numero: '9944XXXX',
  },
  {
    nom: 'VETO-NEGOCES',
    metier: 'sante', ville: 'togo-autres',
    localite: 'Cinkassé', quartier: 'Derrière la station Total de City-Center Hôtel, Gbatmanou',
    pays: 'TG', numero: '9360XXXX',
  },
  {
    nom: 'AIC (ASSOCIATION IVOIRIENNE DE CHIRURGIE)',
    metier: 'sante', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Au sein du CHU',
    pays: 'CI', numero: '077701XXXX',
  },
  {
    nom: 'BIOMEXUS',
    metier: 'sante', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Rue Ministre - Riviera Palmeraie',
    pays: 'CI', numero: '070755XXXX',
  },
  {
    nom: 'CABINET D\'EXPLOITATION CARDIOLOGIQUE JOSEPH MARTINE',
    metier: 'sante', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'En face de Rifat - Riviéra 2',
    pays: 'CI', numero: '054619XXXX',
  },
  {
    nom: 'CABINET BANDAMAN',
    metier: 'sante', ville: 'ci-autres',
    localite: 'Katiola', quartier: 'Bedekaha, non loin de l\'hotel hambol',
    pays: 'CI', numero: '050504XXXX',
  },
  {
    nom: 'CLINIQUE VETERINAIRE DE BONOUA',
    metier: 'sante', ville: 'ci-autres',
    localite: 'Bonoua', quartier: 'Paris village',
    pays: 'CI', numero: '074806XXXX',
  },
  {
    nom: 'D. M. VET',
    metier: 'sante', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Quartier Chateau, Koffiville',
    pays: 'CI', numero: '070801XXXX',
  },
  {
    nom: 'ALEPH',
    metier: 'ecole', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Zoundja, vons face Hotel Tibi libi',
    pays: 'BJ', numero: '016703XXXX',
  },
  {
    nom: 'AMERICAN BASED INTERTIONAL SCOOL COTON',
    metier: 'ecole', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Akpakpa Sodjeatin',
    pays: 'BJ', numero: '019930XXXX',
  },
  {
    nom: 'CEFOPRE REHOBOTH-FORMATION',
    metier: 'ecole', ville: 'cotonou',
    localite: 'Cotonou', quartier: '-',
    pays: 'BJ', numero: '019682XXXX',
  },
  {
    nom: 'ASUNOES (ECOLE DES SOURDS DE LOUHO)',
    metier: 'ecole', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Quartier LOUHO',
    pays: 'BJ', numero: '016291XXXX',
  },
  {
    nom: 'COLLEGE ALFRED NOBEL',
    metier: 'ecole', ville: 'benin-autres',
    localite: 'Sèmè-Podji', quartier: 'Commune',
    pays: 'BJ', numero: '019533XXXX',
  },
  {
    nom: 'COMPLEXE SCOLAIRE CHRETIEN BILINGUE BEREE',
    metier: 'ecole', ville: 'benin-autres',
    localite: 'Ouidah', quartier: 'Pahou Mahuklo',
    pays: 'BJ', numero: '019757XXXX',
  },
  {
    nom: 'Adavon Private School Laique',
    metier: 'ecole', ville: 'lome',
    localite: 'Lomé', quartier: '-',
    pays: 'TG', numero: '9079XXXX',
  },
  {
    nom: 'Agbozo -Kpedji',
    metier: 'ecole', ville: 'lome',
    localite: 'Lomé', quartier: '46RQ+WVR, Rue Dagbati - Amoutive',
    pays: 'TG', numero: '9747XXXX',
  },
  {
    nom: 'ALITO ECOLE',
    metier: 'ecole', ville: 'lome',
    localite: 'Lomé', quartier: 'Rue de l\'Entente, non loin de la Pharmacie Deo Gracias',
    pays: 'TG', numero: '9134XXXX',
  },
  {
    nom: 'CET (COLLEGE D\'ENSEIGNEMENT TECHNIQUE DE KANTE)',
    metier: 'ecole', ville: 'togo-autres',
    localite: 'Kantè', quartier: 'Route de Atoloté, à 2km de la Gendarmerie, non loin du chateau d\'eau à l\'Ouest, Kantè Centre',
    pays: 'TG', numero: '2661XXXX',
  },
  {
    nom: 'COLLEGE PRIVE LAIC EXCELLENCE',
    metier: 'ecole', ville: 'togo-autres',
    localite: 'Dapaong', quartier: 'Korbongou, S/C BP19',
    pays: 'TG', numero: '9136XXXX',
  },
  {
    nom: 'COMPLEXE SCOLAIRE CHRIST ROI',
    metier: 'ecole', ville: 'togo-autres',
    localite: 'Aného', quartier: 'Landjo',
    pays: 'TG', numero: '9020XXXX',
  },
  {
    nom: '2IS (INSTITUT INTERNATIONAL DES SPECIALITES)',
    metier: 'ecole', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Non loin de la poste du toit rouge - Nouveau quartier',
    pays: 'CI', numero: '070795XXXX',
  },
  {
    nom: 'ACADEMIE INTERNATIONALE PIERRE ET MARIE CURIE',
    metier: 'ecole', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Route abatta, au carrefour cyber - Riviera Faya',
    pays: 'CI', numero: '070754XXXX',
  },
  {
    nom: 'CENTRE EDUCATION VERT OLIVE',
    metier: 'ecole', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Non loin de la clinique espoir - Paillet',
    pays: 'CI', numero: '010256XXXX',
  },
  {
    nom: 'AFRICA SCHOOL',
    metier: 'ecole', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Quartier zimbaboué',
    pays: 'CI', numero: '050633XXXX',
  },
  {
    nom: 'Akakobenankro',
    metier: 'ecole', ville: 'ci-autres',
    localite: 'Koun-Fao', quartier: 'FPMX+6M3, sous-préfecture de tienkoikro, département de',
    pays: 'CI', numero: '070893XXXX',
  },
  {
    nom: 'CLUB UNESCO PAIX ET DEVELOPPEMENT',
    metier: 'ecole', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Rue Mory, cité Poro, Quartier Bardot',
    pays: 'CI', numero: '070777XXXX',
  },
  {
    nom: 'LA PASSION DE LA TECHNOLOGIE',
    metier: 'informatique', ville: 'benin-autres',
    localite: 'Ifangni', quartier: 'Tchaada Centre deuxième von après le centre de santé de TCHAADA',
    pays: 'BJ', numero: '016625XXXX',
  },
  {
    nom: 'AJAS WIFI ZONE',
    metier: 'informatique', ville: 'lome',
    localite: 'Lomé', quartier: '57GX+VW7',
    pays: 'TG', numero: '9002XXXX',
  },
  {
    nom: 'ARISTO LA MERVEILLE',
    metier: 'informatique', ville: 'lome',
    localite: 'Lomé', quartier: 'Adidogomé - Amadahomé Lomé amadahomé',
    pays: 'TG', numero: '9053XXXX',
  },
  {
    nom: 'BANZAI',
    metier: 'informatique', ville: 'lome',
    localite: 'Lomé', quartier: 'BP. 8314',
    pays: 'TG', numero: '2320XXXX',
  },
  {
    nom: 'BLACK MARKET SOKODÉ',
    metier: 'informatique', ville: 'togo-autres',
    localite: 'Sokode', quartier: 'Unnamed Road',
    pays: 'TG', numero: '9142XXXX',
  },
  {
    nom: 'Bonne auberge',
    metier: 'informatique', ville: 'togo-autres',
    localite: 'Sokode', quartier: 'N1',
    pays: 'TG', numero: '9002XXXX',
  },
  {
    nom: 'CYBER WIFI JVDS COMPANY',
    metier: 'informatique', ville: 'togo-autres',
    localite: 'Sokode', quartier: 'Rue en face du camp des gardiens de préfecture',
    pays: 'TG', numero: '9058XXXX',
  },
  {
    nom: '@RM',
    metier: 'informatique', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Assavon',
    pays: 'CI', numero: '014222XXXX',
  },
  {
    nom: 'AZITO CONNEXION',
    metier: 'informatique', ville: 'abidjan',
    localite: 'Abidjan', quartier: '8W67+44P, Ruelles lauriers 16 - Yopougon',
    pays: 'CI', numero: '070802XXXX',
  },
  {
    nom: 'Bouba Lux',
    metier: 'informatique', ville: 'abidjan',
    localite: 'Abidjan', quartier: '- - Cocody',
    pays: 'CI', numero: '070896XXXX',
  },
  {
    nom: 'AirNET',
    metier: 'informatique', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: '00225',
    pays: 'CI', numero: '078822XXXX',
  },
  {
    nom: 'BEKA WORK',
    metier: 'informatique', ville: 'ci-autres',
    localite: 'Bouaké', quartier: 'Air France 2',
    pays: 'CI', numero: '070791XXXX',
  },
  {
    nom: 'BOUTIQUE MOOV DIABO',
    metier: 'informatique', ville: 'ci-autres',
    localite: 'Diabo', quartier: 'DIABO 45',
    pays: 'CI', numero: '014150XXXX',
  },
  {
    nom: '+Com',
    metier: 'imprimerie', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: '-',
    pays: 'BJ', numero: '016933XXXX',
  },
  {
    nom: '10GITAL COM',
    metier: 'imprimerie', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Cotonou, Benin - kouhounou',
    pays: 'BJ', numero: '016447XXXX',
  },
  {
    nom: '2AT SOLUTIONS',
    metier: 'imprimerie', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Fidjrosse',
    pays: 'BJ', numero: '019641XXXX',
  },
  {
    nom: 'A DIEU LE DERNIER MOT',
    metier: 'imprimerie', ville: 'benin-autres',
    localite: 'Dassa-Zoumé', quartier: 'Carré',
    pays: 'BJ', numero: '016098XXXX',
  },
  {
    nom: 'AFRICONTACT',
    metier: 'imprimerie', ville: 'benin-autres',
    localite: 'Sèmè-Podji', quartier: 'Lot 223 PK10 Marina',
    pays: 'BJ', numero: '016780XXXX',
  },
  {
    nom: 'AFRIKADESIGNERS',
    metier: 'imprimerie', ville: 'benin-autres',
    localite: 'Adjarra', quartier: '-',
    pays: 'BJ', numero: '014143XXXX',
  },
  {
    nom: '228 AGENCE TIDOCOM',
    metier: 'imprimerie', ville: 'lome',
    localite: 'Lomé', quartier: 'Derrière le terrain de football LIMINUS Baguida',
    pays: 'TG', numero: '9039XXXX',
  },
  {
    nom: '228MARKET',
    metier: 'imprimerie', ville: 'lome',
    localite: 'Lomé', quartier: 'Route de la Nationale 1, face Dispensaire d’Agoè',
    pays: 'TG', numero: '9921XXXX',
  },
  {
    nom: '2A MULTIMEDIA',
    metier: 'imprimerie', ville: 'lome',
    localite: 'Lomé', quartier: 'Av de la Chance',
    pays: 'TG', numero: '9002XXXX',
  },
  {
    nom: 'ANGEL\'S DIGI-MARKETING',
    metier: 'imprimerie', ville: 'togo-autres',
    localite: 'Dapaong', quartier: 'Au quartier worgou',
    pays: 'TG', numero: '9803XXXX',
  },
  {
    nom: 'COMPASSION SARL U',
    metier: 'imprimerie', ville: 'togo-autres',
    localite: 'Agbodrafo', quartier: 'Baguida',
    pays: 'TG', numero: '9387XXXX',
  },
  {
    nom: '100 TASH COMMUNICATION',
    metier: 'imprimerie', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Abidjan, En face de YOPOUGON CNPS - Keneya',
    pays: 'CI', numero: '010341XXXX',
  },
  {
    nom: '100TASH COMMUNICATION',
    metier: 'imprimerie', ville: 'abidjan',
    localite: 'Abidjan', quartier: '-',
    pays: 'CI', numero: '010341XXXX',
  },
  {
    nom: '123DESIGN',
    metier: 'imprimerie', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Hibiscus',
    pays: 'CI', numero: '074820XXXX',
  },
  {
    nom: '2M-CI SARL',
    metier: 'imprimerie', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Motobe, Juste après le pont',
    pays: 'CI', numero: '010210XXXX',
  },
  {
    nom: 'A95 print',
    metier: 'imprimerie', ville: 'ci-autres',
    localite: 'Yamoussoukro', quartier: 'RPH6+27V',
    pays: 'CI', numero: '074914XXXX',
  },
  {
    nom: 'AGBOVILLE MEDIA',
    metier: 'imprimerie', ville: 'ci-autres',
    localite: 'Agboville', quartier: '-',
    pays: 'CI', numero: '070704XXXX',
  },
  {
    nom: 'AUBERGE ALISSATIN',
    metier: 'hotel', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Non loin de l\'Ecole Publique de Togba',
    pays: 'BJ', numero: '019922XXXX',
  },
  {
    nom: 'AUBERGE AWADJIDJE',
    metier: 'hotel', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Nouveau Site: Agoua Gan, Togba',
    pays: 'BJ', numero: '019744XXXX',
  },
  {
    nom: 'AUBERGE BEAU SEJOUR-ABS',
    metier: 'hotel', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Dèkoungbé',
    pays: 'BJ', numero: '015397XXXX',
  },
  {
    nom: 'AUBERGE CHEZ BERN',
    metier: 'hotel', ville: 'benin-autres',
    localite: 'Ouidah', quartier: 'Quartier Tovè 2',
    pays: 'BJ', numero: '016687XXXX',
  },
  {
    nom: 'AUBERGE DE DASSA-ZOUME',
    metier: 'hotel', ville: 'benin-autres',
    localite: 'Dassa-Zoumé', quartier: 'En face du Rond Point',
    pays: 'BJ', numero: '012253XXXX',
  },
  {
    nom: 'AUBERGE DE LA FIERTE',
    metier: 'hotel', ville: 'benin-autres',
    localite: 'Bohicon', quartier: 'Seme District',
    pays: 'BJ', numero: '012251XXXX',
  },
  {
    nom: '100 pas',
    metier: 'hotel', ville: 'lome',
    localite: 'Lomé', quartier: 'Bp0001',
    pays: 'TG', numero: '9088XXXX',
  },
  {
    nom: 'AHOME MAISON D\'HOTES DE LOME',
    metier: 'hotel', ville: 'lome',
    localite: 'Lomé', quartier: '120 Rue Missahoé',
    pays: 'TG', numero: '9344XXXX',
  },
  {
    nom: 'AUBERGE AKPABTOU',
    metier: 'hotel', ville: 'lome',
    localite: 'Lomé', quartier: 'Route de Kpalimé',
    pays: 'TG', numero: '9694XXXX',
  },
  {
    nom: 'ALEXIS AUBERGE',
    metier: 'hotel', ville: 'togo-autres',
    localite: 'Kpalime', quartier: '-',
    pays: 'TG', numero: '9123XXXX',
  },
  {
    nom: 'Auberge Ali Bawa',
    metier: 'hotel', ville: 'togo-autres',
    localite: 'Agouenyive', quartier: '-',
    pays: 'TG', numero: '9199XXXX',
  },
  {
    nom: 'AUBERGE BABADE',
    metier: 'hotel', ville: 'togo-autres',
    localite: 'Aného', quartier: 'Route Nationale N°2, Liaison Cotonou-Lomé, A l\'Entrée du Qrtier Habitat',
    pays: 'TG', numero: '9218XXXX',
  },
  {
    nom: 'AUBERGE CHEZ MARIO',
    metier: 'hotel', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Rive du Lac Bakré - Île Boulay',
    pays: 'CI', numero: '078943XXXX',
  },
  {
    nom: 'Kouakou ets frères',
    metier: 'hotel', ville: 'abidjan',
    localite: 'Abidjan', quartier: '8XFW+HXP, BP 01 - Cocody',
    pays: 'CI', numero: '014249XXXX',
  },
  {
    nom: 'L\'Auberge du Touriste',
    metier: 'hotel', ville: 'abidjan',
    localite: 'Abidjan', quartier: '225)21267848 - Marcory',
    pays: 'CI', numero: '075884XXXX',
  },
  {
    nom: 'Auberge Akwaba, Krinjabo',
    metier: 'hotel', ville: 'ci-autres',
    localite: 'Krindjabo', quartier: '9QVV+JJH',
    pays: 'CI', numero: '050614XXXX',
  },
  {
    nom: 'AUBERGE C\'EST CA QU\'ON FAIT',
    metier: 'hotel', ville: 'ci-autres',
    localite: 'Assinie', quartier: '-',
    pays: 'CI', numero: '050573XXXX',
  },
  {
    nom: 'AUBERGE CEST CA QUON FAIT',
    metier: 'hotel', ville: 'ci-autres',
    localite: 'Assinie', quartier: 'Mafia',
    pays: 'CI', numero: '010117XXXX',
  },
  {
    nom: '01 BIS BENIN IMMOBILIER',
    metier: 'immobilier', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Calavi en face du portail principal du campus. Rue entre le restaurant Chawarma et la mosquée',
    pays: 'BJ', numero: '019541XXXX',
  },
  {
    nom: '2R BENIN REALISATION',
    metier: 'immobilier', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Cocotomey',
    pays: 'BJ', numero: '016651XXXX',
  },
  {
    nom: 'ACCES PROPERTIES',
    metier: 'immobilier', ville: 'cotonou',
    localite: 'Cotonou', quartier: '-',
    pays: 'BJ', numero: '016142XXXX',
  },
  {
    nom: 'AGENCE JAIME LOCATION',
    metier: 'immobilier', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: '-',
    pays: 'BJ', numero: '016934XXXX',
  },
  {
    nom: 'AKA immobilier Services',
    metier: 'immobilier', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'FJWH+PGX, Donoukin Lissessa',
    pays: 'BJ', numero: '016284XXXX',
  },
  {
    nom: 'ALAYE SERVICE',
    metier: 'immobilier', ville: 'benin-autres',
    localite: 'Tchaourou', quartier: 'Gobi-aledji maison ALAYE',
    pays: 'BJ', numero: '019610XXXX',
  },
  {
    nom: '4TUNA',
    metier: 'immobilier', ville: 'lome',
    localite: 'Lomé', quartier: 'S/C BP 1659',
    pays: 'TG', numero: '7034XXXX',
  },
  {
    nom: 'A DIEU LA GLOIRE IMMOBILIER',
    metier: 'immobilier', ville: 'lome',
    localite: 'Lomé', quartier: '0000',
    pays: 'TG', numero: '9252XXXX',
  },
  {
    nom: 'A-Z IMMOBILIER SARLU',
    metier: 'immobilier', ville: 'lome',
    localite: 'Lomé', quartier: 'Près du lycée Avédji',
    pays: 'TG', numero: '9013XXXX',
  },
  {
    nom: 'AGENCE IMMOBILIERE QEDEM',
    metier: 'immobilier', ville: 'togo-autres',
    localite: 'Kpalimé', quartier: 'Atakpamé Kondji non loin de Oando',
    pays: 'TG', numero: '9748XXXX',
  },
  {
    nom: 'AGISMA-IMMO TOGO',
    metier: 'immobilier', ville: 'togo-autres',
    localite: 'Agbodrafo', quartier: 'Route Lomé-Aného, Kouevikopé',
    pays: 'TG', numero: '7068XXXX',
  },
  {
    nom: 'BETGD la GRÂCE',
    metier: 'immobilier', ville: 'togo-autres',
    localite: 'Adétikopé', quartier: '-',
    pays: 'TG', numero: '9787XXXX',
  },
  {
    nom: '3B INGENIERIE INTERNATIONAL',
    metier: 'immobilier', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Riviera Faya',
    pays: 'CI', numero: '074796XXXX',
  },
  {
    nom: 'A&B Habitats et divers',
    metier: 'immobilier', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Bp 100 Abidjan cocody rivera faya',
    pays: 'CI', numero: '074811XXXX',
  },
  {
    nom: 'ABIDJANMAISON.COM',
    metier: 'immobilier', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Cité des arts',
    pays: 'CI', numero: '054666XXXX',
  },
  {
    nom: '3A CORPORATE GROUPS',
    metier: 'immobilier', ville: 'ci-autres',
    localite: 'Bouaké', quartier: '-',
    pays: 'CI', numero: '058411XXXX',
  },
  {
    nom: 'AFRIK CASA HOTEL',
    metier: 'immobilier', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Balmer',
    pays: 'CI', numero: '070978XXXX',
  },
  {
    nom: 'AGENCE CREATIVE IMMOBILIERE',
    metier: 'immobilier', ville: 'ci-autres',
    localite: 'Assinie-Mafia', quartier: 'Non loin de l\'atelier espoir',
    pays: 'CI', numero: '078750XXXX',
  },
  {
    nom: '2MORROW TRIP',
    metier: 'transport', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Rue Houdou Ali derrière pharmacie fidjrossè plage, Fidjrossè',
    pays: 'BJ', numero: '016682XXXX',
  },
  {
    nom: 'A-TRAVEL',
    metier: 'transport', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Missebo',
    pays: 'BJ', numero: '016737XXXX',
  },
  {
    nom: 'ADEF CENTER',
    metier: 'transport', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Au niveau du carrefour Paraná',
    pays: 'BJ', numero: '019492XXXX',
  },
  {
    nom: 'AL MOUBARAK AMC0',
    metier: 'transport', ville: 'benin-autres',
    localite: 'Sèmè-Podji', quartier: 'ÎLOT 50 DJEFFA HOUEDOME GBAGO PARCELLE H',
    pays: 'BJ', numero: '015154XXXX',
  },
  {
    nom: 'BENIN TICKET XPRESS',
    metier: 'transport', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: '2229',
    pays: 'BJ', numero: '016604XXXX',
  },
  {
    nom: 'CHITOUSON-SERVICES',
    metier: 'transport', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Non loin du Carrefour Leon Bourgine',
    pays: 'BJ', numero: '019717XXXX',
  },
  {
    nom: 'AD MOUB TOURS & SERVICES',
    metier: 'transport', ville: 'lome',
    localite: 'Lomé', quartier: 'Rue à coté Direction, Quartier Leo 200',
    pays: 'TG', numero: '9393XXXX',
  },
  {
    nom: 'AFRICA - TOURISTS',
    metier: 'transport', ville: 'lome',
    localite: 'Lomé', quartier: '1583, Bd. du 13 Janvier',
    pays: 'TG', numero: '2336XXXX',
  },
  {
    nom: 'AL HADJOU ARAFA',
    metier: 'transport', ville: 'lome',
    localite: 'Lomé', quartier: 'Agoè-Carréfour Bleu',
    pays: 'TG', numero: '9122XXXX',
  },
  {
    nom: 'ABC VOYAGES',
    metier: 'transport', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Non loin de la Pharmacie Ananeraie, Oasis - Ananeraie',
    pays: 'CI', numero: '075812XXXX',
  },
  {
    nom: 'ABSSOVOYAGE',
    metier: 'transport', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Après l’ancienne banque SIB à gauche, immeuble la Vida, Rez de chaussée - Résidentiel',
    pays: 'CI', numero: '070753XXXX',
  },
  {
    nom: 'AC GROUP',
    metier: 'transport', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Carrefour Bluetooth angré',
    pays: 'CI', numero: '076762XXXX',
  },
  {
    nom: 'MAHANAÏM SARL',
    metier: 'transport', ville: 'ci-autres',
    localite: 'Korhogo', quartier: '-',
    pays: 'CI', numero: '074725XXXX',
  },
  {
    nom: '.KMS SECURITE',
    metier: 'services', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'FIDJROSSE',
    pays: 'BJ', numero: '019760XXXX',
  },
  {
    nom: '01 BIS BENIN NETTOYAGE',
    metier: 'services', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: 'Calavi en face du portail principal du campus. Rue entre le restaurant Chawarma et la mosquée',
    pays: 'BJ', numero: '019541XXXX',
  },
  {
    nom: '2SC',
    metier: 'services', ville: 'cotonou',
    localite: 'Cotonou', quartier: '01 - Saint-Jean',
    pays: 'BJ', numero: '016500XXXX',
  },
  {
    nom: 'A2A Expertises',
    metier: 'services', ville: 'benin-autres',
    localite: 'Depo', quartier: 'Ms Jacob, Lot 2027 Qtier - kouhounou',
    pays: 'BJ', numero: '016636XXXX',
  },
  {
    nom: 'Agence d\'assurance ALEPH-MGF',
    metier: 'services', ville: 'benin-autres',
    localite: 'Agblangandan', quartier: '9G9C+VF9, Unnamed Road',
    pays: 'BJ', numero: '016621XXXX',
  },
  {
    nom: 'AGMSTRADING',
    metier: 'services', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Porto-novo',
    pays: 'BJ', numero: '019550XXXX',
  },
  {
    nom: 'A703 GROUP',
    metier: 'services', ville: 'lome',
    localite: 'Lomé', quartier: '227, Rue. Mont Adamano, Immeuble 227, 40m de MIFA',
    pays: 'TG', numero: '7035XXXX',
  },
  {
    nom: 'AAC Sarl (AFRIQUE AUDIT CONSEIL)',
    metier: 'services', ville: 'lome',
    localite: 'Lomé', quartier: 'Avédji',
    pays: 'TG', numero: '9084XXXX',
  },
  {
    nom: 'ABICA PHIL ET CO TOGO SAS-U',
    metier: 'services', ville: 'lome',
    localite: 'Lomé', quartier: '-',
    pays: 'TG', numero: '9116XXXX',
  },
  {
    nom: 'Agence GTAC2A-IARDT ET VIE',
    metier: 'services', ville: 'togo-autres',
    localite: 'Kara', quartier: 'N.16',
    pays: 'TG', numero: '9849XXXX',
  },
  {
    nom: 'Agence GTAC2A-IARDT ET VIE',
    metier: 'services', ville: 'togo-autres',
    localite: 'Sokode', quartier: '-',
    pays: 'TG', numero: '9849XXXX',
  },
  {
    nom: 'ARCHI BIO',
    metier: 'services', ville: 'togo-autres',
    localite: 'Pya', quartier: 'A côté de Donou',
    pays: 'TG', numero: '7020XXXX',
  },
  {
    nom: '2BK SECURITE',
    metier: 'services', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Face star 11 - Angré Djibi',
    pays: 'CI', numero: '050508XXXX',
  },
  {
    nom: '2DS GROUP',
    metier: 'services', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Route d\'Abatta, non loin de l\'école Jules Vernes - Riviera Faya',
    pays: 'CI', numero: '078821XXXX',
  },
  {
    nom: '2ETS',
    metier: 'services', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Angré chateau',
    pays: 'CI', numero: '070813XXXX',
  },
  {
    nom: '2A CONSULTING ET SERVICES',
    metier: 'services', ville: 'ci-autres',
    localite: 'Bonoua', quartier: 'Yaou',
    pays: 'CI', numero: '075963XXXX',
  },
  {
    nom: 'AGENCE COULIBALY SERVICE',
    metier: 'services', ville: 'ci-autres',
    localite: 'Daloa', quartier: 'Quartier Commerce, non loin de Orange CI',
    pays: 'CI', numero: '070710XXXX',
  },
  {
    nom: 'AGENCE DORONE',
    metier: 'services', ville: 'ci-autres',
    localite: 'Korhogo', quartier: 'Petit Paris, Imm Yaya',
    pays: 'CI', numero: '010229XXXX',
  },
  {
    nom: 'AFRICAN ART',
    metier: 'artisan', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Zogbo',
    pays: 'BJ', numero: '016187XXXX',
  },
  {
    nom: 'AFRICAN WINK & AFRICAN WINK\'S BAZAAR',
    metier: 'artisan', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'A Côté de Sopai, Delice, face Ambassade d\'Angola, juste avant le Crux',
    pays: 'BJ', numero: '019534XXXX',
  },
  {
    nom: 'ANS PERSONNALISATION',
    metier: 'artisan', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Agla pharmacie Saint Michel archange',
    pays: 'BJ', numero: '019610XXXX',
  },
  {
    nom: 'MOUVEMENT SPORTIF',
    metier: 'artisan', ville: 'benin-autres',
    localite: 'Bohicon', quartier: '-',
    pays: 'BJ', numero: '016675XXXX',
  },
  {
    nom: 'AFRIC BEAUTY',
    metier: 'artisan', ville: 'lome',
    localite: 'Lomé', quartier: 'Rue du Commerce',
    pays: 'TG', numero: '9260XXXX',
  },
  {
    nom: 'AIGLE DECOR',
    metier: 'artisan', ville: 'lome',
    localite: 'Lomé', quartier: '-',
    pays: 'TG', numero: '9013XXXX',
  },
  {
    nom: 'ARCANDIA',
    metier: 'artisan', ville: 'lome',
    localite: 'Lomé', quartier: 'Angle Rue Tapounté et Rue Doulassamé',
    pays: 'TG', numero: '2338XXXX',
  },
  {
    nom: 'BIG-BANG MAISON DE SCULPTURE SUR BOIS Sarl-U',
    metier: 'artisan', ville: 'togo-autres',
    localite: 'Agbodrafo', quartier: 'Rue de l’Auberge du Lac, Maison BIG-BANG Kpessi',
    pays: 'TG', numero: '9338XXXX',
  },
  {
    nom: '2A DESIGN',
    metier: 'artisan', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Deux plateaux Aghien',
    pays: 'CI', numero: '014233XXXX',
  },
  {
    nom: 'A COMME ART',
    metier: 'artisan', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Val doyen',
    pays: 'CI', numero: '070726XXXX',
  },
  {
    nom: 'AFRICAN EUROPEAN GLOBAL ARTWORK',
    metier: 'artisan', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Treichville, avenue 16',
    pays: 'CI', numero: '077999XXXX',
  },
  {
    nom: 'ASSAKRO DESIGN',
    metier: 'artisan', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Village Artisanat',
    pays: 'CI', numero: '050580XXXX',
  },
  {
    nom: 'BATIKIER BLO',
    metier: 'artisan', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Village des Artisans',
    pays: 'CI', numero: '070946XXXX',
  },
  {
    nom: 'BRUCE. KI\'ART',
    metier: 'artisan', ville: 'ci-autres',
    localite: 'Yamoussoukro', quartier: '-',
    pays: 'CI', numero: '077736XXXX',
  },
  {
    nom: 'AFRICAIN OBJECTS',
    metier: 'commerce', ville: 'cotonou',
    localite: 'Abomey-Calavi', quartier: '-',
    pays: 'BJ', numero: '015835XXXX',
  },
  {
    nom: 'ANIMAH',
    metier: 'commerce', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Godomey N\'gbeho C/25',
    pays: 'BJ', numero: '015201XXXX',
  },
  {
    nom: 'ARRE GROUP',
    metier: 'commerce', ville: 'cotonou',
    localite: 'Cotonou', quartier: '-',
    pays: 'BJ', numero: '016636XXXX',
  },
  {
    nom: 'CDR GROUP INTERNATIONAL',
    metier: 'commerce', ville: 'benin-autres',
    localite: 'Parakou', quartier: 'Zongo-Nord',
    pays: 'BJ', numero: '016418XXXX',
  },
  {
    nom: 'DEMA ET FILS',
    metier: 'commerce', ville: 'benin-autres',
    localite: 'Sakété', quartier: 'Quartier Ararom',
    pays: 'BJ', numero: '019594XXXX',
  },
  {
    nom: 'DREAMLAND-DCFC.SARL',
    metier: 'commerce', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: 'Kpota-Sandodo',
    pays: 'BJ', numero: '016712XXXX',
  },
  {
    nom: 'ADAD AND MJ Sarl',
    metier: 'commerce', ville: 'lome',
    localite: 'Lomé', quartier: 'Non loin de Limousine, Avedji',
    pays: 'TG', numero: '9604XXXX',
  },
  {
    nom: 'AFRICALIGHT001',
    metier: 'commerce', ville: 'lome',
    localite: 'Lomé', quartier: 'Mson Apowota, derrière le site de CETEF TOGO 2000',
    pays: 'TG', numero: '9300XXXX',
  },
  {
    nom: 'AFRIQUE EMERGENCE IMMOBILIERE',
    metier: 'commerce', ville: 'lome',
    localite: 'Lomé', quartier: 'Marché décaw2w2',
    pays: 'TG', numero: '2074XXXX',
  },
  {
    nom: 'AFRICA MARTINO BUSINESS',
    metier: 'commerce', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Star 10 - Angré 9è tranche',
    pays: 'CI', numero: '070900XXXX',
  },
  {
    nom: 'AK COMPAGNIE',
    metier: 'commerce', ville: 'abidjan',
    localite: 'Bingerville', quartier: 'Carrefour BCEAO, Abatta',
    pays: 'CI', numero: '076936XXXX',
  },
  {
    nom: 'BAT-IMMOBILIER',
    metier: 'commerce', ville: 'abidjan',
    localite: 'Abidjan', quartier: 'Deux plateaux, carrefour macaci',
    pays: 'CI', numero: '010243XXXX',
  },
  {
    nom: 'AFRI TRADING',
    metier: 'commerce', ville: 'ci-autres',
    localite: 'Grand-Bassam', quartier: 'Mockeyville',
    pays: 'CI', numero: '050671XXXX',
  },
  {
    nom: 'AFRICNEDI (AFRIQUE CONSTRUCTION NEGOCE ET DISTRIBUTION)',
    metier: 'commerce', ville: 'ci-autres',
    localite: 'Bouaké', quartier: 'Av. Felix Houphouet Boigny, Dar es Salam',
    pays: 'CI', numero: '050521XXXX',
  },
  {
    nom: 'AG FOODS',
    metier: 'commerce', ville: 'ci-autres',
    localite: 'San-Pédro', quartier: 'Quartier Lac',
    pays: 'CI', numero: '050143XXXX',
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

/* ─────────────── PLUSIEURS MÉTIERS À LA FOIS (décision 81) ───────────────
   Un grossiste en boissons veut les restaurants ET les alimentations. Un
   fournisseur de matériel veut les salons de beauté ET les hôtels. Obliger à
   commander deux fois, c'est facturer deux fois le minimum de dix fiches pour
   rien, et perdre la vente.

   Toutes les fonctions ci-dessous acceptent donc une LISTE de métiers. Une
   liste vide veut dire « rien de choisi », jamais « tout ». */

export function stockMulti(metiers, ville) {
  return (metiers || []).reduce((t, m) => t + stock(m, ville), 0)
}

export function totalMetierMulti(metiers) {
  return (metiers || []).reduce((t, m) => t + totalMetier(m), 0)
}

/* Les fiches de l'aperçu quand plusieurs métiers sont choisis : on ALTERNE
   entre eux au lieu de vider le premier. Trois cartes de trois métiers
   différents montrent mieux ce qu'on achète que trois cartes du même. */
export function fichesApercuMulti(metiers, ville, combien = 3) {
  const l = (metiers || []).filter(Boolean)
  if (l.length === 0) return []
  if (l.length === 1) return fichesApercu(l[0], ville, combien)

  const paniers = l.map((m) => fichesApercu(m, ville, combien))
  const pris = new Set()
  const sortie = []
  for (let tour = 0; tour < combien && sortie.length < combien; tour++) {
    for (const panier of paniers) {
      if (sortie.length >= combien) break
      const f = panier[tour]
      if (f && !pris.has(f.nom)) {
        pris.add(f.nom)
        sortie.push(f)
      }
    }
  }
  /* s'il manque encore quelque chose, on complète sans jamais rendre vide */
  for (const panier of paniers) {
    for (const f of panier) {
      if (sortie.length >= combien) break
      if (!pris.has(f.nom)) {
        pris.add(f.nom)
        sortie.push(f)
      }
    }
  }
  return sortie
}

/* La phrase : « ateliers de couture et restaurants », jamais « couture,
   restaurant ». On écrit comme on parle. */
export function plurielsListe(metiers) {
  const noms = (metiers || [])
    .map((c) => (METIERS.find((m) => m.cle === c) || {}).pluriel)
    .filter(Boolean)
  if (noms.length === 0) return ''
  if (noms.length === 1) return noms[0]
  return noms.slice(0, -1).join(', ') + ' et ' + noms[noms.length - 1]
}
