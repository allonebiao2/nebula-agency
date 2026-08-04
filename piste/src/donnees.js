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
export const EMAIL = 'piste@nebula-agency.online'
export const ADRESSE = 'piste.nebula-agency.online'
export const DATE_RELEVE = '3 août 2026'
export const MINIMUM = 10
export const EXCLUSIVITE_JOURS = 90

/* ------------------------------------------------ ⛔ À CONFIRMER --------

   LES NUMÉROS QUI REÇOIVENT L'ARGENT.

   Ils ne sont pas encore confirmés par Mongazi, et **un numéro Mobile Money
   faux, c'est un client qui paie un inconnu**. Tant que `aConfirmer` vaut
   `true` :

     · la page de paiement N'AFFICHE AUCUN NUMÉRO. Elle dit la vérité — le
       numéro arrive sur WhatsApp à la seconde où la commande part — et le
       parcours fonctionne quand même, de bout en bout.
     · `node _predeploy.js` REFUSE de préparer une mise en ligne.

   Le jour où les deux numéros sont confirmés : on les écrit ici, on passe
   `aConfirmer` à false, et la page les affiche. Rien d'autre à toucher.

   ⚠️ Depuis le 30/11/2024 l'ARCEP béninoise impose 10 chiffres, préfixe
   `01`. Un numéro à 8 chiffres est un numéro d'avant la réforme.           */

export const MOMO = {
  aConfirmer: true,
  comptes: [
    { reseau: 'MTN MoMo', numero: '', titulaire: '' },
    { reseau: 'Moov Flooz', numero: '', titulaire: '' },
  ],
}

export const RESEAUX = MOMO.comptes.map((c) => c.reseau)

/* ------------------------------------------------------------------ métiers */

export const METIERS = [
  {
    cle: 'couture',
    nom: 'Ateliers de couture',
    court: 'Couture',
    singulier: 'atelier de couture',
    exemple: 'tailleurs, couturières, brodeurs, ateliers de confection',
  },
  {
    cle: 'restaurant',
    nom: 'Restaurants, maquis et bars',
    court: 'Restaurants',
    singulier: 'restaurant',
    exemple: 'restaurants, maquis, bars, buvettes, kebabs',
  },
  {
    cle: 'patisserie',
    nom: 'Pâtisseries et boulangeries',
    court: 'Pâtisseries',
    singulier: 'pâtisserie',
    exemple: 'pâtissiers, boulangers',
  },
  {
    cle: 'autre',
    nom: 'Un autre métier',
    court: 'Autre métier',
    singulier: 'commerce',
    exemple: 'coiffure, quincaillerie, pharmacie, garage, école…',
    horsStock: true,
  },
]

/* -------------------------------------------------------------------- zones */

export const VILLES = [
  {
    cle: 'cotonou',
    nom: 'Cotonou et ses environs',
    pays: 'Bénin',
    detail: 'Cotonou, Abomey-Calavi, Godomey, Cocotomey',
  },
  {
    cle: 'benin-autres',
    nom: 'Autres villes du Bénin',
    pays: 'Bénin',
    detail: 'Porto-Novo, Parakou, Bohicon, Ouidah, Abomey, Lokossa, Kandi…',
  },
  {
    cle: 'lome',
    nom: 'Lomé',
    pays: 'Togo',
    detail: 'tous les quartiers, de Bè Klikamé à Agoè',
  },
  {
    cle: 'togo-autres',
    nom: 'Autres villes du Togo',
    pays: 'Togo',
    detail: 'Kpalimé, Bafilo',
  },
  {
    cle: 'abidjan',
    nom: 'Abidjan',
    pays: "Côte d'Ivoire",
    detail: "aucune source ivoirienne n'a encore été relevée",
    bientot: true,
  },
]

/* L'inventaire, écrit à la main à partir des comptes ci-dessus.
   En V2 il viendra de la base. Clé : `metier|ville`. */
export const STOCK = {
  'couture|cotonou': 57,
  'couture|benin-autres': 0,
  'couture|lome': 53,
  'couture|togo-autres': 1,
  'couture|abidjan': 0,

  'restaurant|cotonou': 28,
  'restaurant|benin-autres': 26,
  'restaurant|lome': 19,
  'restaurant|togo-autres': 1,
  'restaurant|abidjan': 0,

  'patisserie|cotonou': 2,
  'patisserie|benin-autres': 0,
  'patisserie|lome': 0,
  'patisserie|togo-autres': 0,
  'patisserie|abidjan': 0,

  'autre|cotonou': 0,
  'autre|benin-autres': 0,
  'autre|lome': 0,
  'autre|togo-autres': 0,
  'autre|abidjan': 0,
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
export const NOMBRE_FIXES = 13

/* ----------------------------------------------- fiches réelles d'exemple --

   Recopiées telles quelles de `_donnees.py`. Les deux derniers chiffres du
   numéro sont masqués sur la vitrine : la fiche complète appartient à qui
   l'achète, et le commerce n'a pas demandé à voir son numéro affiché en
   entier sur une page de vente.                                              */

export const FICHES = [
  {
    nom: 'BOUBAKAR COUTURE',
    metier: 'couture', ville: 'lome',
    localite: 'Lomé', quartier: 'Hédzranawoé',
    pays: 'TG', numero: '90749679',
  },
  {
    nom: 'ADEBISSI FASHION',
    metier: 'couture', ville: 'cotonou',
    localite: 'Cotonou', quartier: '',
    pays: 'BJ', numero: '0197075503',
  },
  {
    nom: 'COUTURE MA LUMIERE',
    metier: 'couture', ville: 'togo-autres',
    localite: 'Bafilo', quartier: '',
    pays: 'TG', numero: '90114366',
  },
  {
    nom: 'Maquis Le Kédjénou',
    metier: 'restaurant', ville: 'cotonou',
    localite: 'Cotonou', quartier: 'Abokicodji Lazare',
    pays: 'BJ', numero: '0160022929',
  },
  {
    nom: '228 Kebab Kégué',
    metier: 'restaurant', ville: 'lome',
    localite: 'Lomé', quartier: 'Kégué',
    pays: 'TG', numero: '91494444',
  },
  {
    nom: 'Bar Restaurant Les Orchidées You And Me',
    metier: 'restaurant', ville: 'benin-autres',
    localite: 'Porto-Novo', quartier: '',
    pays: 'BJ', numero: '0198101692',
  },
  {
    nom: 'AFRICA BAR CHEZ CORNEILLE',
    metier: 'restaurant', ville: 'togo-autres',
    localite: 'Kpalimé', quartier: '',
    pays: 'TG', numero: '90349592',
  },
  {
    nom: 'Boulangerie-Pâtisserie Pain Ivoir',
    metier: 'patisserie', ville: 'cotonou',
    localite: 'Cotonou', quartier: '',
    pays: 'BJ', numero: '0197483730',
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
export function numeroMasque(pays, numero) {
  const j = numeroJoli(pays, numero)
  return j.slice(0, -2) + '••'
}

export function international(pays, numero) {
  return '+' + INDICATIF[pays] + ' ' + numeroJoli(pays, numero)
}

/* Choisit la fiche d'exemple la plus proche de ce que la personne demande. */
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
    /* Espace insécable avant le « ? » : sans elle, le point d'interrogation
       part seul à la ligne suivante dans une colonne étroite. C'est la règle
       typographique française, et WhatsApp la respecte. */
    'Est-ce que je peux vous en dire deux mots ? Ça prend deux minutes.',
  ].join('\n\n')
}
