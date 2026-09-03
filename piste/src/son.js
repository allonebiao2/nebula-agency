/*
  PISTE · la tonalité du cockpit.

  Aucun fichier audio : tout est synthétisé. Un mp3 de notification, c'est un
  chargement de plus, un 404 possible, et une seconde de retard au moment où on
  a justement besoin d'être prévenu tout de suite.

  ⚠️ TROIS PRÉCAUTIONS, APPRISES À NOS DÉPENS

  1. AUCUN NAVIGATEUR NE JOUE UN SON AVANT UN GESTE DE L'UTILISATEUR.
     Un `AudioContext` créé au chargement naît « suspended » et reste muet.
     On l'ouvre donc au PREMIER geste (clic, toucher, touche), pas avant.
     ⚠️ Sur PC, la molette ne compte pas comme un geste ; sur mobile, un
     toucher compte.

  2. iOS EXIGE UN TAMPON SILENCIEUX pour se dérouiller. Sans ce buffer d'une
     image jouée au premier geste, tout ce qui suit reste inaudible sur iPhone,
     alors que le code paraît parfait.

  3. LE HAUT-PARLEUR D'UN TÉLÉPHONE EST FAIBLE. Un niveau réglé à l'oreille sur
     un PC est inaudible dehors, dans la rue, à Cotonou. D'où le gain plus fort
     sur mobile, et un compresseur pour que ça porte sans saturer.
*/

let ctx = null
let sortie = null
let deverrouille = false

/* Le téléphone a un petit haut-parleur : il lui faut plus de niveau. */
const surMobile = () =>
  typeof navigator !== 'undefined' &&
  (/Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (navigator.maxTouchPoints > 1 && /Mac/i.test(navigator.platform || '')))

function creer() {
  if (ctx) return ctx
  const A = window.AudioContext || window.webkitAudioContext
  if (!A) return null
  ctx = new A()

  /* Le compresseur fait porter le son sans le faire saturer : c'est lui qui
     rend la tonalité audible sur un haut-parleur de téléphone. */
  const comp = ctx.createDynamicsCompressor()
  comp.threshold.value = -22
  comp.knee.value = 24
  comp.ratio.value = 10
  comp.attack.value = 0.003
  comp.release.value = 0.22

  sortie = ctx.createGain()
  sortie.gain.value = surMobile() ? 0.85 : 0.5
  sortie.connect(comp)
  comp.connect(ctx.destination)
  return ctx
}

/* Le tampon silencieux d'iOS. Sans lui, un iPhone reste muet pour toujours. */
function tamponSilencieux() {
  if (!ctx) return
  const b = ctx.createBuffer(1, 1, 22050)
  const s = ctx.createBufferSource()
  s.buffer = b
  s.connect(ctx.destination)
  s.start(0)
}

/* À appeler UNE fois, au premier geste. Rien avant ne peut fonctionner. */
export function ouvrirLeSon() {
  if (deverrouille) return true
  const c = creer()
  if (!c) return false
  tamponSilencieux()
  if (c.state === 'suspended') c.resume()
  deverrouille = c.state === 'running'
  return deverrouille
}

export function sonPret() {
  return deverrouille && ctx && ctx.state === 'running'
}

/* Une note. `type` triangle plutôt que sine : ça porte mieux sur un petit
   haut-parleur sans devenir agressif comme une onde carrée. */
function note(hz, debut, duree, volume = 1) {
  if (!ctx) return
  const t = ctx.currentTime + debut
  const o = ctx.createOscillator()
  const g = ctx.createGain()
  o.type = 'triangle'
  o.frequency.setValueAtTime(hz, t)

  /* Une attaque douce évite le « clac » du début, une extinction
     exponentielle évite celui de la fin. */
  g.gain.setValueAtTime(0.0001, t)
  g.gain.exponentialRampToValueAtTime(volume, t + 0.012)
  g.gain.exponentialRampToValueAtTime(0.0001, t + duree)

  o.connect(g)
  g.connect(sortie)
  o.start(t)
  o.stop(t + duree + 0.05)
}

/*
  UNE COMMANDE VIENT D'ARRIVER.
  Trois notes qui montent : ça s'entend comme une bonne nouvelle, et ça se
  distingue d'une notification de téléphone ordinaire. Répété deux fois, parce
  qu'un seul carillon passe inaperçu quand on n'est pas devant l'écran.
*/
export function sonnerCommande() {
  if (!sonPret()) return false
  const motif = [
    [660, 0.0, 0.16],
    [880, 0.13, 0.16],
    [1320, 0.26, 0.42],
  ]
  for (const rep of [0, 0.62]) {
    for (const [hz, d, duree] of motif) note(hz, rep + d, duree, rep ? 0.6 : 0.8)
  }
  return true
}

/* Un carnet vient de partir : deux notes qui descendent, ça se pose. */
export function sonnerLivraison() {
  if (!sonPret()) return false
  note(1046, 0, 0.14, 0.7)
  note(698, 0.12, 0.34, 0.7)
  return true
}

/* Quelque chose a échoué : une note basse, brève, sans dramatiser. */
export function sonnerErreur() {
  if (!sonPret()) return false
  note(233, 0, 0.22, 0.55)
  return true
}

/*
  LA NOTIFICATION DU SYSTÈME, en plus du son.
  Le son ne sert que si l'onglet est ouvert quelque part. La notification, elle,
  s'affiche même quand PISTE est derrière une autre fenêtre : c'est elle qui
  prévient vraiment. On ne demande la permission qu'au moment où elle sert.
*/
export function notificationsPossibles() {
  return typeof window !== 'undefined' && 'Notification' in window
}

export function etatNotifications() {
  if (!notificationsPossibles()) return 'impossible'
  return Notification.permission /* default | granted | denied */
}

export async function demanderNotifications() {
  if (!notificationsPossibles()) return 'impossible'
  if (Notification.permission === 'granted') return 'granted'
  if (Notification.permission === 'denied') return 'denied'
  try {
    return await Notification.requestPermission()
  } catch (e) {
    return 'denied'
  }
}

export function notifier(titre, corps) {
  if (!notificationsPossibles() || Notification.permission !== 'granted') return false
  try {
    const n = new Notification(titre, {
      body: corps,
      icon: '/favicon.svg',
      badge: '/favicon.svg',
      tag: 'piste-commande' /* une seule à la fois, pas une pile */,
      renotify: true,
    })
    n.onclick = () => {
      window.focus()
      n.close()
    }
    return true
  } catch (e) {
    return false
  }
}
