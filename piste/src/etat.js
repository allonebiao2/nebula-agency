/*
  PISTE · la commande, de sa composition à sa livraison.

  ⚠️ EN V1 IL N'Y A PAS DE SERVEUR. Le site est un paquet statique sur
  Cloudflare Pages. La commande voyage donc par le seul canal qui existe
  déjà et que tout le monde sait ouvrir : **WhatsApp**.

      le client compose  ->  WhatsApp de NEBULA  ->  Mongazi colle le message
      dans son cockpit   ->  il encaisse, il marque payé, il marque livré.

  Le cockpit ne lit donc RIEN à distance : il range ce que Mongazi y colle,
  dans le navigateur de Mongazi. C'est assumé, c'est écrit à l'écran, et
  c'est ce qui permet d'ouvrir sans attendre une base de données.

  Le jour où le moteur de collecte (décision 41) arrive avec sa base, ce
  fichier est le seul à remplacer : tout le reste parle par ces fonctions.
*/

import { METIERS, VILLES, NEBULA_WHATSAPP } from './donnees.js'
import { SUPPLEMENTS, calcul, fcfa } from './prix.js'

/* --------------------------------------------------------------- le code --

   Cinq caractères, sans I, O, 1 ni 0 : ils se dictent au téléphone sans être
   confondus.

   ⚠️ Ils sont TIRÉS AU HASARD, pas dérivés de l'heure. Une première version
   prenait deux caractères dans l'horloge et deux au hasard : 1 024
   possibilités par seconde, et le contrôle qualité a tout de suite montré la
   casse — 400 codes tirés, 342 distincts. Un code en double, c'est une
   commande qui en écrase une autre dans le cockpit, donc un client qui n'est
   jamais livré.

   Six caractères font 1,07 milliard de combinaisons. À dix commandes par
   jour, c'est un doublon tous les quelques siècles — et un caractère de plus
   ne coûte rien à dicter au téléphone.

   La ceinture, en plus des bretelles : `ajouterAuCockpit` ne fusionne deux
   commandes que si le code ET l'email correspondent. Même un doublon ne peut
   donc pas faire disparaître une commande.                                  */

const ALPHABET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
export const LONGUEUR_CODE = 6

function hasard(n) {
  /* `crypto` quand il est là — il l'est dans tous les navigateurs visés et
     dans Node depuis longtemps. `Math.random` sert de filet, pas de norme. */
  const source = globalThis.crypto
  if (source?.getRandomValues) {
    const octets = new Uint8Array(n)
    source.getRandomValues(octets)
    /* 256 n'est pas un multiple de 32 : on ne garde que 5 bits par octet,
       sinon les premières lettres de l'alphabet sortiraient plus souvent. */
    return Array.from(octets, (o) => ALPHABET[o & 31])
  }
  return Array.from({ length: n }, () => ALPHABET[Math.floor(Math.random() * 32)])
}

export function codeCommande() {
  return hasard(LONGUEUR_CODE).join('')
}

/* ------------------------------------------------------- l'expiration ----

   Décision 28 : une commande non payée expire au bout de 24 heures et ses
   fiches retournent au stock. Le compte à rebours s'affiche.                */

export const DUREE_VALIDITE = 24 * 3600 * 1000

export function resteAvantExpiration(cree) {
  return Math.max(0, cree + DUREE_VALIDITE - Date.now())
}

export function joliDelai(ms) {
  if (ms <= 0) return 'expirée'
  const h = Math.floor(ms / 3600000)
  const m = Math.floor((ms % 3600000) / 60000)
  if (h >= 1) return `${h} h ${String(m).padStart(2, '0')}`
  const s = Math.floor((ms % 60000) / 1000)
  return `${m} min ${String(s).padStart(2, '0')}`
}

/* ------------------------------------------------- le message WhatsApp ---

   C'est LE format d'échange de la V1. Il est écrit pour être lu par un
   humain d'abord — c'est un message que le client envoie de sa main, il n'y
   a donc aucun bloc technique dedans. Le cockpit sait le relire parce que
   c'est PISTE qui l'a composé (voir `lireMessage`).

   Toucher à ce format casse le cockpit : les deux vont ensemble.            */

export function detailOptions(options) {
  const pris = SUPPLEMENTS.filter((s) => options[s.cle])
  return pris.length ? pris.map((s) => s.nom.toLowerCase()).join(', ') : 'rien de plus'
}

export function composerMessage(c) {
  const metier = METIERS.find((m) => m.cle === c.metier)
  const ville = VILLES.find((v) => v.cle === c.ville)
  const p = calcul(c.nombre, c.options)

  const lignes = [
    `PISTE · commande ${c.code}`,
    '',
    'CE QUE JE CHERCHE',
    `· Métier : ${c.metierLibre?.trim() || metier?.nom || '?'}`,
    `· Ville : ${ville?.nom || '?'}`,
    `· Quartier : ${c.quartier?.trim() || 'peu importe'}`,
    `· Nombre : ${p.n} fiches`,
    `· En plus : ${detailOptions(c.options)}`,
    `· Je vends : ${c.offre?.trim() || '(à préciser)'}`,
    '',
    `À PAYER : ${fcfa(p.total)}`,
    `· ${fcfa(p.unitaire)} la fiche × ${p.n}${p.taux ? `, remise ${Math.round(p.taux * 100)} %` : ''}`,
    '',
    'MOI',
    `· Nom : ${c.nom?.trim() || '?'}`,
    `· Email : ${c.email?.trim() || '?'}`,
    `· WhatsApp : ${c.whatsapp?.trim() || '?'}`,
    `· Je paierai depuis le : ${c.momo?.trim() || '?'} (${c.reseau || 'MTN MoMo'})`,
  ]
  return lignes.join('\n')
}

export function lienWhatsApp(texte, numero = NEBULA_WHATSAPP) {
  return `https://wa.me/${numero}?text=${encodeURIComponent(texte)}`
}

/* ------------------------------------------------------- la relecture ----

   Le cockpit reçoit le message tel que le client l'a envoyé, collé depuis
   WhatsApp. On relit ligne par ligne. Rien n'est deviné : ce qui manque
   reste vide, et le cockpit le montre en rouge plutôt que d'inventer.       */

const CHAMPS = [
  ['metier', /^·\s*Métier\s*:\s*(.+)$/i],
  ['ville', /^·\s*Ville\s*:\s*(.+)$/i],
  ['quartier', /^·\s*Quartier\s*:\s*(.+)$/i],
  ['offre', /^·\s*Je vends\s*:\s*(.+)$/i],
  ['nom', /^·\s*Nom\s*:\s*(.+)$/i],
  ['email', /^·\s*Email\s*:\s*(.+)$/i],
  ['whatsapp', /^·\s*WhatsApp\s*:\s*(.+)$/i],
]

export function lireMessage(texte) {
  const t = String(texte || '').replace(/\r/g, '')
  const lu = {}

  const code = t.match(new RegExp(`commande\\s+([23456789A-HJ-NP-Z]{${LONGUEUR_CODE}})\\b`, 'i'))
  if (code) lu.code = code[1].toUpperCase()

  for (const [cle, re] of CHAMPS) {
    const l = t.split('\n').map((x) => x.trim()).find((x) => re.test(x))
    if (l) lu[cle] = l.match(re)[1].trim()
  }

  const nb = t.match(/·\s*Nombre\s*:\s*([\d\s]+)\s*fiches?/i)
  if (nb) lu.nombre = parseInt(nb[1].replace(/\s/g, ''), 10)

  const total = t.match(/À PAYER\s*:\s*([\d\s]+)\s*F/i)
  if (total) lu.total = parseInt(total[1].replace(/\s/g, ''), 10)

  const opts = t.match(/·\s*En plus\s*:\s*(.+)/i)
  if (opts) lu.options = opts[1].trim()

  const momo = t.match(/·\s*Je paierai depuis le\s*:\s*(.+?)\s*(?:\((.+)\))?$/im)
  if (momo) {
    lu.momo = momo[1].trim()
    if (momo[2]) lu.reseau = momo[2].trim()
  }

  lu.brut = t.trim()
  return lu
}

/* ------------------------------------------------------- le rangement ----

   `localStorage`, avec un préfixe. Deux tiroirs seulement :
     piste:commande  la commande en cours du client, pour qu'il la retrouve
     piste:cockpit   la liste de Mongazi, sur SA machine
                                                                             */

const TIROIRS = { commande: 'piste:commande', cockpit: 'piste:cockpit' }

function lire(tiroir, defaut) {
  try {
    const brut = localStorage.getItem(TIROIRS[tiroir])
    return brut ? JSON.parse(brut) : defaut
  } catch {
    return defaut
  }
}

function ecrire(tiroir, valeur) {
  try {
    localStorage.setItem(TIROIRS[tiroir], JSON.stringify(valeur))
    return true
  } catch {
    /* navigation privée, quota plein : on n'a pas le droit de casser la page
       pour si peu. La commande vit alors le temps de l'onglet. */
    return false
  }
}

export const maCommande = {
  lire: () => lire('commande', null),
  poser: (c) => ecrire('commande', c),
  effacer: () => {
    try {
      localStorage.removeItem(TIROIRS.commande)
    } catch {
      /* rien à faire */
    }
  },
}

/* --------------------------------------------------------- le cockpit ----

   Une commande y vit trois états, dans cet ordre, et jamais à l'envers :
     recue -> payee -> livree
   Plus deux sorties : `expiree` (24 h sans paiement) et `annulee`.          */

export const ETATS = [
  { cle: 'recue', nom: 'Reçue', suite: 'Marquer payé' },
  { cle: 'payee', nom: 'Payée', suite: 'Marquer livré' },
  { cle: 'livree', nom: 'Livrée', suite: null },
]

export const cockpit = {
  lire: () => {
    const l = lire('cockpit', [])
    return Array.isArray(l) ? l : []
  },
  poser: (liste) => ecrire('cockpit', liste),
}

export function ajouterAuCockpit(commande) {
  const liste = cockpit.lire()
  /* On ne fusionne que si le code ET l'email correspondent : coller deux fois
     le même message ne crée pas de doublon, mais deux clients différents ne
     peuvent jamais s'écraser l'un l'autre, même sur un code en double. */
  const deja = liste.findIndex(
    (c) => c.code && c.code === commande.code && (c.email || '') === (commande.email || '')
  )
  const fiche = {
    id: commande.id || `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    etat: 'recue',
    cree: Date.now(),
    ...commande,
  }
  if (deja >= 0) liste[deja] = { ...liste[deja], ...fiche, id: liste[deja].id }
  else liste.unshift(fiche)
  cockpit.poser(liste)
  return liste
}

export function majCockpit(id, champs) {
  const liste = cockpit.lire().map((c) => (c.id === id ? { ...c, ...champs } : c))
  cockpit.poser(liste)
  return liste
}

export function retirerDuCockpit(id) {
  const liste = cockpit.lire().filter((c) => c.id !== id)
  cockpit.poser(liste)
  return liste
}

/* Le CSV du cockpit : Mongazi doit pouvoir sortir ses commandes de PISTE
   sans demander la permission à personne. Point-virgule et BOM, sinon Excel
   francophone colle tout dans la première colonne et mange les accents. */
export function csvCommandes(liste) {
  const enTete = [
    'code', 'etat', 'recue_le', 'nom', 'email', 'whatsapp', 'momo', 'reseau',
    'metier', 'ville', 'quartier', 'nombre', 'options', 'total_fcfa', 'note',
  ]
  const cel = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
  const lignes = liste.map((c) =>
    [
      c.code, c.etat, new Date(c.cree).toISOString().slice(0, 16).replace('T', ' '),
      c.nom, c.email, c.whatsapp, c.momo, c.reseau, c.metier, c.ville,
      c.quartier, c.nombre, c.options, c.total, c.note,
    ]
      .map(cel)
      .join(';')
  )
  return '﻿' + enTete.join(';') + '\n' + lignes.join('\n')
}

export function telecharger(nom, contenu, type = 'text/csv;charset=utf-8') {
  const url = URL.createObjectURL(new Blob([contenu], { type }))
  const a = document.createElement('a')
  a.href = url
  a.download = nom
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}

/* --------------------------------------------------------- les routes ----

   Routage par ancre : un paquet statique n'a pas de serveur pour réécrire
   les URL, et `#/commander` marche partout sans règle de redirection.       */

export const ROUTES = ['accueil', 'commander', 'origine', 'cockpit']

export function routeCourante() {
  const h = (location.hash || '').replace(/^#\/?/, '').split('?')[0]
  return ROUTES.includes(h) ? h : 'accueil'
}

export function allerA(route) {
  location.hash = route === 'accueil' ? '#/' : `#/${route}`
}
