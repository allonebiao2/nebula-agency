/*
  PISTE · ce qui se garde, et où.

  ⚠️ La V1 n'a pas de serveur. Tout vit dans le navigateur qui a servi à écrire.
  Concrètement : une commande passée sur le téléphone du client ne remonte PAS
  toute seule dans le cockpit de Mongazi. C'est pour ça que la commande part
  entièrement rédigée sur WhatsApp, avec une ligne technique que le cockpit sait
  relire et ranger. Ce n'est pas un contournement, c'est le contrat de la V1, et
  l'interface le dit à voix haute des deux côtés.
*/

import { HEURES_VALIDITE } from './donnees.js'

export const CLES = {
  /* Ce que le generateur a compose, transmis a l'ecran de commande. */
  brouillon: 'piste_brouillon_v1',
  commandes: 'piste_commandes_v1',
  demandes: 'piste_demandes_v1',
  signalements: 'piste_signalements_v1',
  /* Les references deja vues, pour ne sonner QUE sur ce qui est nouveau. */
  refsVues: 'piste_refs_vues_v1',
}

export function lire(cle) {
  try {
    const l = JSON.parse(localStorage.getItem(CLES[cle]) || '[]')
    return Array.isArray(l) ? l : []
  } catch (e) {
    return []
  }
}

export function ecrire(cle, liste) {
  try {
    localStorage.setItem(CLES[cle], JSON.stringify(liste))
  } catch (e) {
    /* navigation privée ou stockage plein : l'écran reste juste, rien n'est
       perdu côté client puisque tout est aussi parti sur WhatsApp. */
  }
}

export function ajouter(cle, objet) {
  const l = lire(cle)
  l.unshift(objet)
  ecrire(cle, l)
  return l
}

/* --------------------------------------------------------- le compte à rebours */

export function echeance(dateISO) {
  return new Date(new Date(dateISO).getTime() + HEURES_VALIDITE * 3600 * 1000)
}

export function resteEn(dateISO, maintenant = Date.now()) {
  const ms = echeance(dateISO).getTime() - maintenant
  if (ms <= 0) return { fini: true, ms: 0, h: 0, m: 0, s: 0, texte: 'expirée' }
  const s = Math.floor(ms / 1000)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return {
    fini: false,
    ms,
    h,
    m,
    s: sec,
    texte: h > 0 ? `${h} h ${String(m).padStart(2, '0')} min` : `${m} min ${String(sec).padStart(2, '0')} s`,
  }
}

/* Une commande non payée passée depuis plus de 24 heures est expirée : ses
   fiches sont retournées au stock. On ne la supprime pas, on l'affiche telle
   quelle dans le cockpit, parce qu'une commande expirée est une information. */
export function estExpiree(c, maintenant = Date.now()) {
  return c.etat === 'recue' && resteEn(c.date, maintenant).fini
}
