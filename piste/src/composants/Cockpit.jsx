import { useEffect, useMemo, useState } from 'react'
import {
  METIERS,
  MOBILE_MONEY,
  NEBULA_WHATSAPP_JOLI,
  VILLES,
  nouvelleReference,
} from '../donnees.js'
import { SUPPLEMENTS, fcfa } from '../prix.js'
import { CLES, ajouter, ecrire, estExpiree, lire, resteEn } from '../stockage.js'
import {
  etatCommandeServeur,
  listerCommandes,
  livrerCarnet,
  motDePasseCockpit,
  poserMotDePasse,
} from '../supabase.js'
import {
  demanderNotifications,
  etatNotifications,
  notifier,
  notificationsPossibles,
  ouvrirLeSon,
  sonPret,
  sonnerCommande,
  sonnerLivraison,
} from '../son.js'
import { Bouton, Chiffre } from './Ui.jsx'
import { Puce } from './Trace.jsx'

/*
  Le cockpit (décisions 27, 28, 32, 34, 39).

  Il répond à une seule question : qui a payé, et qu'est-ce que je livre
  aujourd'hui. Cinq piles : à encaisser (avec leur compte à rebours), à livrer,
  livrées, les signalements de fiches injoignables, et les demandes de métiers
  ou de villes qu'on n'a pas encore.
*/

const ETATS = [
  { cle: 'recue', nom: 'À encaisser', suite: 'Marquer payé', pastille: 'bg-braise/20 text-brique' },
  { cle: 'payee', nom: 'À livrer', suite: 'Marquer livré', pastille: 'bg-vert/15 text-vert' },
  { cle: 'livree', nom: 'Livrées', suite: null, pastille: 'bg-encre/10 text-sourd' },
]

/* Lit une commande collée depuis WhatsApp : la ligne technique d'abord, le
   texte lisible ensuite si elle a été effacée en route. */
export function analyser(texte) {
  const t = String(texte || '')
  const i = t.indexOf('PISTE:{')
  if (i >= 0) {
    const debut = t.indexOf('{', i)
    let profondeur = 0
    for (let k = debut; k < t.length; k++) {
      if (t[k] === '{') profondeur++
      else if (t[k] === '}') {
        profondeur--
        if (profondeur === 0) {
          try {
            const o = JSON.parse(t.slice(debut, k + 1))
            return {
              ref: o.ref,
              date: o.date && o.date.length > 10 ? o.date : new Date().toISOString(),
              metier: o.met || '',
              ville: o.vil || '',
              quartier: o.qua || '',
              n: Number(o.n) || 0,
              options: Array.isArray(o.opt) ? o.opt : [],
              offre: o.offre || '',
              prenom: o.prenom || '',
              nom: o.nom || '',
              email: o.email || '',
              wa: o.wa || '',
              momoNumero: o.momo || '',
              momoOperateur: o.ope || '',
              unitaire: Number(o.unit) || 0,
              total: Number(o.total) || 0,
              etat: 'recue',
            }
          } catch (e) {
            break
          }
        }
      }
    }
  }
  const trouve = (r) => (t.match(r) || [])[1]?.trim() || ''
  const ref = trouve(/Commande\s+(PISTE-[A-Z0-9]{4})/i)
  if (!ref) return null
  const total = Number((trouve(/À PAYER\s*:\s*([\d\s]+)F/i) || '0').replace(/\s/g, ''))
  const nomComplet = trouve(/Nom et prénom\s*:\s*(.+)/i).split(' ')
  return {
    ref: ref.toUpperCase(),
    date: new Date().toISOString(),
    metier: '',
    ville: '',
    quartier: trouve(/Quartier\s*:\s*(.+)/i),
    n: Number(trouve(/Nombre de fiches\s*:\s*(\d+)/i)) || 0,
    options: [],
    offre: trouve(/Ce que je vends\s*:\s*(.+)/i),
    prenom: nomComplet[0] || '',
    nom: nomComplet.slice(1).join(' '),
    email: trouve(/Email\s*:\s*(\S+)/i),
    wa: trouve(/WhatsApp\s*:\s*\+?([\d\s]+)/i).replace(/\s/g, ''),
    momoNumero: trouve(/Je paierai depuis le \+229\s*([\d\s]+)/i).replace(/\s/g, ''),
    momoOperateur: '',
    unitaire: 0,
    total,
    etat: 'recue',
  }
}

/* Lit une demande de métier ou de ville collée depuis WhatsApp. */
function analyserDemande(texte) {
  const t = String(texte || '')
  const i = t.indexOf('DEMANDE:{')
  if (i < 0) return null
  try {
    return JSON.parse(t.slice(t.indexOf('{', i)))
  } catch (e) {
    return null
  }
}

function Rebours({ date }) {
  const [t, setT] = useState(() => resteEn(date))
  useEffect(() => {
    const i = setInterval(() => setT(resteEn(date)), 30000)
    return () => clearInterval(i)
  }, [date])
  if (t.fini) {
    return (
      <span className="rounded-full bg-rouge/12 px-2.5 py-1 text-[0.75rem] font-semibold text-rouge">
        expirée, fiches rendues au stock
      </span>
    )
  }
  return (
    <span
      className={`rounded-full px-2.5 py-1 text-[0.75rem] font-semibold ${
        t.h < 6 ? 'bg-brique/12 text-brique' : 'bg-encre/8 text-sourd'
      }`}
    >
      il reste {t.texte}
    </span>
  )
}

/* ═══════════════ LA MARCHE À SUIVRE ═══════════════
   Mongazi travaille souvent entre deux rendez-vous, sur son téléphone. Les six
   gestes d'une commande tiennent dans sa tête aujourd'hui parce qu'il n'y en a
   eu que quelques-unes : à dix par jour, ça ne tiendra plus, et ce qui n'est
   écrit nulle part se fait de travers un jour de fatigue.

   Elle est repliée par défaut : quand on connaît, on n'a pas besoin de la
   relire, et elle ne doit pas repousser les commandes vers le bas. */
const GESTES = [
  [
    'La commande arrive',
    'Sur votre WhatsApp, le message commence par « PISTE COMMANDE ». Elle est déjà en base : rien ne se perd. Collez le message ci-dessous pour la ranger ici aussi.',
  ],
  [
    'Vous vérifiez le paiement',
    "Dans MTN MoMo, cherchez le NUMÉRO et le NOM que l'acheteur a déclarés : c'est ce qui s'affiche à la réception, pas la référence. Puis marquez « payée ».",
  ],
  [
    'Vous fabriquez le carnet',
    'Sur votre PC, une commande : python piste/_carnet.py --metier … --ville … --n … --ecrire. Les fiches sont réservées 90 jours pour ce client seul.',
  ],
  [
    'Si « numéro testé » est coché, vous appelez',
    "Chaque numéro, avant l'envoi. Une fiche qui ne répond pas ne part pas : elle est remplacée. L'outil ne peut pas composer à votre place, il vous le rappelle.",
  ],
  [
    'Vous envoyez le lien',
    "L'outil vous rend le lien ET le courriel déjà écrit, dans piste/_carnets/. Envoyez-le par email et par WhatsApp, puis marquez « livrée ».",
  ],
  [
    'Une semaine après, vous relancez',
    "python piste/_carnet.py --relances vous rend un message écrit à partir de SES résultats. C'est aussi ce qui vous dit si vos fiches ont vraiment servi.",
  ],
]

function MarcheASuivre() {
  const [ouvert, setOuvert] = useState(false)
  return (
    <section className="mt-4 overflow-hidden rounded-2xl border border-trait bg-creme/60">
      <button
        type="button"
        onClick={() => setOuvert((o) => !o)}
        aria-expanded={ouvert}
        className="flex min-h-[52px] w-full items-center justify-between gap-3 px-5 text-left"
      >
        <span className="text-[0.95rem] font-semibold text-encre">
          Marche à suivre · les 6 gestes d'une commande
        </span>
        <span className="flex-none text-[0.85rem] font-semibold text-brique">
          {ouvert ? 'Replier' : 'Dérouler'}
        </span>
      </button>

      {ouvert && (
        <ol className="divide-y divide-trait border-t border-trait">
          {GESTES.map(([titre, dessous], i) => (
            <li key={titre} className="flex items-start gap-3.5 px-5 py-3.5">
              <span className="mt-0.5 flex-none font-display text-[0.95rem] font-bold tabular-nums leading-none text-brique">
                {i + 1}
              </span>
              <span className="min-w-0">
                <span className="block text-[0.92rem] font-semibold leading-tight text-encre">
                  {titre}
                </span>
                <span className="mt-0.5 block text-[0.84rem] leading-snug text-sourd">
                  {dessous}
                </span>
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}

/* ------------------------------------------------------------------------- */

/*
  LA BARRE DE VEILLE.

  Une alerte qu'on ne peut pas vérifier ne rassure personne : on finit par
  garder l'onglet ouvert « au cas où » sans jamais savoir si ça marche. Cette
  barre dit trois choses en un coup d'oeil : le serveur répond ou non, le son
  est ouvert ou non, les notifications sont autorisées ou non. Et elle laisse
  ESSAYER la tonalité tout de suite, plutôt que d'attendre une vraie commande
  pour découvrir qu'on n'entend rien.
*/
function Veille({ veille, son, notifs, onSon, onNotifs }) {
  const [teste, setTeste] = useState('')

  const etats = {
    ok: { p: 'bg-vert', t: 'La veille tourne' },
    attente: { p: 'bg-sable', t: 'Premier contact…' },
    panne: { p: 'bg-rouge', t: 'Le serveur ne répond pas' },
    verrouille: { p: 'bg-rouge', t: 'Cockpit bloqué 15 minutes' },
  }
  const e = etats[veille.etat] || etats.attente

  /* Un seul geste, un seul son. Ouvrir le contexte audio ET jouer la tonalité,
     dans cet ordre, parce que l'ouverture n'est possible QUE pendant un geste
     de l'utilisateur. */
  const essayer = () => {
    const ouvert = ouvrirLeSon()
    if (ouvert) onSon()
    const joue = ouvert && sonnerCommande()
    setTeste(
      joue
        ? 'Vous devez entendre trois notes qui montent, deux fois. Si vous n’entendez rien, montez le volume et vérifiez que le téléphone n’est pas en silencieux.'
        : "Le son n'a pas pu s'ouvrir sur cet appareil."
    )
    setTimeout(() => setTeste(''), 9000)
  }

  return (
    <div className="mt-6 rounded-2xl border border-trait bg-creme p-4 sm:p-5">
      <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
        <span className="inline-flex items-center gap-2 text-[0.94rem] font-semibold">
          <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${e.p}`} aria-hidden="true" />
          {e.t}
        </span>
        {veille.quand && (
          <span className="text-[0.86rem] text-sourd">
            vérifié à{' '}
            {veille.quand.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>

      <p className="mt-2.5 text-[0.92rem] leading-relaxed text-sourd">
        Le cockpit interroge le serveur toutes les 30 secondes. Une commande passée depuis
        le téléphone d'un client arrive ici toute seule, avec une tonalité.
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-2.5">
        <Bouton ton="nu" onClick={essayer}>
          {son ? 'Tester la tonalité' : 'Activer le son'}
        </Bouton>

        {notificationsPossibles() && notifs !== 'granted' && (
          <Bouton ton="nu" onClick={onNotifs} disabled={notifs === 'denied'}>
            {notifs === 'denied' ? 'Notifications refusées' : 'Autoriser les notifications'}
          </Bouton>
        )}
        {notifs === 'granted' && (
          <span className="text-[0.86rem] text-vert">Notifications autorisées</span>
        )}
      </div>

      {teste && <p className="mt-3 text-[0.9rem] text-encre">{teste}</p>}

      {notifs === 'denied' && (
        <p className="mt-3 text-[0.88rem] leading-relaxed text-sourd">
          Votre navigateur les a bloquées. Pour les rétablir : appuyez sur le cadenas à
          gauche de l'adresse, puis autorisez les notifications pour ce site. Le son, lui,
          continue de marcher.
        </p>
      )}
      {!son && (
        <p className="mt-3 text-[0.88rem] leading-relaxed text-sourd">
          Aucun navigateur ne joue un son avant que vous ayez touché la page. Appuyez une
          fois sur « Activer le son » : ensuite, ça sonne tout seul.
        </p>
      )}
    </div>
  )
}

export default function Cockpit({ aller }) {
  const [commandes, setCommandes] = useState([])
  const [demandes, setDemandes] = useState([])
  const [signalements, setSignalements] = useState([])
  const [colle, setColle] = useState('')
  const [erreur, setErreur] = useState('')
  const [annulable, setAnnulable] = useState(null)
  const [onglet, setOnglet] = useState('recue')
  const [, rafraichir] = useState(0)

  const [son, setSon] = useState(false)
  const [notifs, setNotifs] = useState(() => etatNotifications())
  const [veille, setVeille] = useState({ quand: null, etat: 'attente' })
  const [nouvelles, setNouvelles] = useState([])

  useEffect(() => {
    setCommandes(lire('commandes'))
    setDemandes(lire('demandes'))
    setSignalements(lire('signalements'))
    const i = setInterval(() => rafraichir((x) => x + 1), 30000)
    return () => clearInterval(i)
  }, [])

  /*
    LE SON NE PEUT PAS S'OUVRIR TOUT SEUL.
    Aucun navigateur ne joue quoi que ce soit avant un geste de l'utilisateur :
    un contexte audio créé au chargement naît muet. On l'ouvre donc au PREMIER
    clic ou toucher, une seule fois, puis on retire l'écouteur.
    ⚠️ Sur PC la molette ne compte pas comme un geste ; sur mobile un toucher
    compte. C'est pour ça qu'il y a aussi un bouton « Tester la tonalité » :
    sans geste explicite, on ne peut RIEN promettre.
  */
  useEffect(() => {
    if (sonPret()) {
      setSon(true)
      return
    }
    const ouvrir = () => {
      if (ouvrirLeSon()) setSon(true)
    }
    const evts = ['pointerdown', 'touchstart', 'keydown']
    evts.forEach((e) => document.addEventListener(e, ouvrir, { once: true, passive: true }))
    return () => evts.forEach((e) => document.removeEventListener(e, ouvrir))
  }, [])

  /*
    LA VEILLE : le cockpit interroge le serveur toutes les 30 secondes.

    Avant, il ne lisait que CE navigateur. Une commande passée depuis le
    téléphone d'un client existait en base, déclenchait deux courriels, et
    n'apparaissait jamais ici tant que Mongazi ne recollait pas le message
    WhatsApp à la main.

    ⚠️ La première réponse ne sonne PAS : au premier chargement, tout est
    « nouveau ». Une alarme qui hurle à chaque ouverture, on l'éteint le
    deuxième jour, et elle ne sert plus jamais à rien.
  */
  useEffect(() => {
    if (!motDePasseCockpit()) return
    let vivant = true
    let premiere = true

    const connues = () => {
      try {
        return new Set(JSON.parse(localStorage.getItem(CLES.refsVues) || '[]'))
      } catch (e) {
        return new Set()
      }
    }
    const retenir = (set) => {
      try {
        localStorage.setItem(CLES.refsVues, JSON.stringify([...set].slice(0, 400)))
      } catch (e) {}
    }

    const regarder = async () => {
      const r = await listerCommandes()
      if (!vivant) return
      if (!r?.ok) {
        setVeille({ quand: new Date(), etat: r?.verrouille ? 'verrouille' : 'panne' })
        return
      }
      setVeille({ quand: new Date(), etat: 'ok' })

      const vues = connues()
      const arrivees = (r.commandes || []).filter((c) => !vues.has(c.ref))
      for (const c of r.commandes || []) vues.add(c.ref)
      retenir(vues)

      /* On fusionne : le serveur fait foi sur ce qu'il connaît, le local
         garde ce qui n'a été collé qu'ici. */
      setCommandes((avant) => {
        const parRef = new Map(avant.map((c) => [c.ref, c]))
        for (const c of r.commandes || []) {
          const d = parRef.get(c.ref)
          parRef.set(c.ref, d ? { ...c, ...d, lienCarnet: d.lienCarnet || c.lienCarnet } : c)
        }
        const liste = [...parRef.values()].sort(
          (x, y) => new Date(y.date || 0) - new Date(x.date || 0)
        )
        ecrire('commandes', liste)
        return liste
      })

      if (premiere) {
        premiere = false
        return
      }
      if (!arrivees.length) return

      setNouvelles((n) => [...arrivees, ...n].slice(0, 8))
      sonnerCommande()
      const c = arrivees[0]
      notifier(
        arrivees.length === 1 ? `Commande ${c.ref} · ${fcfa(c.total)}` : `${arrivees.length} nouvelles commandes`,
        arrivees.length === 1
          ? `${[c.prenom, c.nom].filter(Boolean).join(' ') || 'Un client'} · ${c.n} fiches`
          : arrivees.map((x) => x.ref).join(', ')
      )
    }

    regarder()
    const i = setInterval(regarder, 30000)
    return () => {
      vivant = false
      clearInterval(i)
    }
  }, [])

  const majCommandes = (l) => {
    setCommandes(l)
    ecrire('commandes', l)
  }
  const majDemandes = (l) => {
    setDemandes(l)
    ecrire('demandes', l)
  }
  const majSignalements = (l) => {
    setSignalements(l)
    ecrire('signalements', l)
  }

  /* Fabriquer le carnet et l'envoyer. Le mot de passe est demandé une fois et
     gardé dans CE navigateur : il n'est pas dans le site, parce que cette
     fonction fabrique de la marchandise. */
  async function livrer(c) {
    let mdp = motDePasseCockpit()
    if (!mdp) {
      mdp = window.prompt(
        [
          'Code du cockpit PISTE (5 chiffres).',
          '',
          'Ce n’est pas un code Google ni un code reçu par SMS : c’est le code que',
          'vous avez choisi, celui qui autorise la fabrication d’un carnet.',
          '',
          'Il n’est demandé qu’une fois par appareil. Au bout de 10 essais ratés, le',
          'cockpit se bloque 15 minutes, puis rouvre tout seul.',
        ].join(String.fromCharCode(10))
      )
      if (!mdp) return
      poserMotDePasse(mdp.trim())
    }
    setErreur('')
    majCommandes(commandes.map((x) => (x.ref === c.ref ? { ...x, enCours: true } : x)))
    const r = await livrerCarnet(c.ref)
    if (r?.ok) {
      majCommandes(
        commandes.map((x) =>
          x.ref === c.ref
            ? { ...x, enCours: false, etat: 'livree', lienCarnet: r.lien, livreeLe: new Date().toISOString() }
            : x
        )
      )
      sonnerLivraison()
      return
    }
    majCommandes(commandes.map((x) => (x.ref === c.ref ? { ...x, enCours: false } : x)))
    /* Le verrou et le mauvais code sont deux choses différentes. On efface le
       code enregistré quand il est FAUX, jamais quand le compteur a simplement
       mordu : sinon un verrou ferait oublier un code pourtant bon. */
    if (r?.verrouille) {
      setErreur(r.erreur + ' Votre code reste enregistré, rien à retaper.')
      return
    }
    if (r?.erreur === 'mot de passe') {
      poserMotDePasse('')
      setErreur(
        'Code refusé. Ce n’est pas un code Google : c’est le code à 5 chiffres du ' +
          'cockpit. Il vous sera redemandé.'
      )
      return
    }
    setErreur(
      r?.libres !== undefined
        ? `Pas assez de fiches libres : ${r.libres} disponibles. Le moteur collecte chaque nuit, ou proposez une autre ville.`
        : `La fabrication a échoué : ${r?.erreur || 'raison inconnue'}. La commande n'a pas bougé, vous pouvez réessayer.`
    )
  }

  /* L'état change ici ET en base. Sinon une commande marquée payée sur le PC
     réapparaît « à encaisser » sur le téléphone, et on encaisse deux fois. */
  const changerEtat = (ref, etat) => {
    majCommandes(
      commandes.map((c) =>
        c.ref === ref
          ? { ...c, etat, [etat === 'payee' ? 'payeeLe' : 'livreeLe']: new Date().toISOString() }
          : c
      )
    )
    etatCommandeServeur(ref, etat)
  }

  const retirer = (ref) => {
    const c = commandes.find((x) => x.ref === ref)
    const i = commandes.findIndex((x) => x.ref === ref)
    majCommandes(commandes.filter((x) => x.ref !== ref))
    setAnnulable({ type: 'commande', c, i })
  }

  const annuler = () => {
    if (!annulable) return
    if (annulable.type === 'commande') {
      const l = [...commandes]
      l.splice(annulable.i, 0, annulable.c)
      majCommandes(l)
    }
    setAnnulable(null)
  }

  useEffect(() => {
    if (!annulable) return
    const t = setTimeout(() => setAnnulable(null), 9000)
    return () => clearTimeout(t)
  }, [annulable])

  const ranger = () => {
    const d = analyserDemande(colle)
    if (d) {
      if (demandes.some((x) => x.email === d.email && x.metier === d.metier)) {
        setErreur('Cette demande est déjà rangée.')
        return
      }
      setErreur('')
      setColle('')
      majDemandes([d, ...demandes])
      setOnglet('demandes')
      return
    }
    const o = analyser(colle)
    if (!o) {
      setErreur(
        "Rien de reconnaissable là-dedans. Collez le message entier reçu sur WhatsApp, de la première à la dernière ligne."
      )
      return
    }
    if (commandes.some((c) => c.ref === o.ref)) {
      setErreur(`La commande ${o.ref} est déjà dans la liste.`)
      return
    }
    setErreur('')
    setColle('')
    majCommandes([o, ...commandes])
    setOnglet('recue')
  }

  const compteurs = useMemo(() => {
    const vivantes = commandes.filter((c) => c.etat === 'recue' && !estExpiree(c))
    const expirees = commandes.filter((c) => estExpiree(c))
    const aLivrer = commandes.filter((c) => c.etat === 'payee')
    const encaisse = commandes
      .filter((c) => c.etat !== 'recue')
      .reduce((s, c) => s + (c.total || 0), 0)
    return { vivantes, expirees, aLivrer, encaisse }
  }, [commandes])

  const exporter = () => {
    const entete = [
      'Code', 'Reçue le', 'Prénom', 'Nom', 'Métier', 'Ville', 'Quartier', 'Fiches',
      'Informations en plus', 'Ce que le client vend', 'Email', 'WhatsApp',
      'Numéro Mobile Money', 'Opérateur', 'Prix la fiche', 'Total', 'État',
    ]
    const lignes = commandes.map((c) => [
      c.ref,
      (c.date || '').slice(0, 10),
      c.prenom,
      c.nom,
      METIERS.find((m) => m.cle === c.metier)?.nom || c.metier,
      VILLES.find((v) => v.cle === c.ville)?.nom || c.ville,
      c.quartier,
      c.n,
      (c.options || []).map((o) => SUPPLEMENTS.find((s) => s.cle === o)?.nom || o).join(' + '),
      c.offre,
      c.email,
      '+' + c.wa,
      c.momoNumero ? '+229 ' + c.momoNumero : '',
      MOBILE_MONEY.find((m) => m.cle === c.momoOperateur)?.operateur || '',
      c.unitaire,
      c.total,
      estExpiree(c) ? 'Expirée' : ETATS.find((e) => e.cle === c.etat)?.nom || c.etat,
    ])
    const csv =
      '﻿' +
      [entete, ...lignes]
        .map((r) => r.map((v) => `"${String(v ?? '').replace(/"/g, '""')}"`).join(';'))
        .join('\r\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `piste-commandes-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const ONGLETS = [
    ...ETATS.map((e) => ({
      cle: e.cle,
      nom: e.nom,
      n: commandes.filter((c) => c.etat === e.cle && (e.cle !== 'recue' || !estExpiree(c))).length,
    })),
    { cle: 'expirees', nom: 'Expirées', n: compteurs.expirees.length },
    { cle: 'signalements', nom: 'Injoignables', n: signalements.filter((s) => !s.remplacee).length },
    { cle: 'demandes', nom: 'Demandes', n: demandes.filter((d) => d.etat === 'attente').length },
  ]

  const visibles =
    onglet === 'expirees'
      ? compteurs.expirees
      : commandes.filter((c) => c.etat === onglet && !estExpiree(c))

  return (
    <div className="min-h-screen bg-papier pb-28">
      <header className="border-b border-trait bg-creme">
        <div className="mx-auto flex w-full max-w-[68rem] items-center justify-between gap-4 px-5 py-3.5 sm:px-8">
          <button
            type="button"
            onClick={() => aller('#/')}
            className="flex min-h-[44px] items-center gap-2 font-display text-[1rem] font-bold tracking-tight"
          >
            <Puce className="h-4 w-4 text-brique" />
            PISTE <span className="font-normal text-sourd">· cockpit</span>
          </button>
          <Bouton ton="nu" onClick={exporter} disabled={!commandes.length}>
            Exporter en CSV
          </Bouton>
        </div>
      </header>

      <div className="mx-auto w-full max-w-[68rem] px-5 py-8 sm:px-8 sm:py-12">
        <h1 className="text-[clamp(1.8rem,6vw,2.6rem)]">Qui a payé, qu'est-ce que je livre.</h1>

        {/* ⚠️ Cet encadré disait « ce cockpit vit dans CE navigateur ». Ce
            n'est plus vrai depuis le 2026-08-04 : la commande part AUSSI en
            base au moment où l'acheteur file sur WhatsApp. Un cockpit qui
            décrit un fonctionnement périmé fait travailler de travers. */}
        <div className="mt-6 rounded-2xl border-2 border-brique/30 bg-creme p-5">
          <p className="font-semibold">Ce tableau est votre copie de travail.</p>
          <p className="mt-1.5 text-[0.94rem] leading-relaxed text-sourd">
            Chaque commande part en base au moment où l'acheteur file sur WhatsApp : elle
            n'est jamais perdue, même si vous ne voyez pas passer son message. Ici, vous
            gardez la vôtre : collez le message reçu au {NEBULA_WHATSAPP_JOLI} ci-dessous, il
            se range tout seul avec son prix, son code et ses coordonnées.
          </p>
        </div>

        <Veille
          veille={veille}
          son={son}
          notifs={notifs}
          onSon={() => setSon(true)}
          onNotifs={async () => setNotifs(await demanderNotifications())}
        />

        {/* Ce qui vient d'arriver, en clair. La tonalité prévient ; ce bandeau
            dit QUOI, parce qu'un son seul oblige à chercher. */}
        {nouvelles.length > 0 && (
          <div className="mt-4 rounded-2xl border-2 border-vert/40 bg-vert/5 p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <p className="font-semibold text-vert">
                {nouvelles.length === 1
                  ? 'Une commande vient d’arriver'
                  : `${nouvelles.length} commandes viennent d’arriver`}
              </p>
              <Bouton ton="nu" onClick={() => setNouvelles([])}>
                J’ai vu
              </Bouton>
            </div>
            <ul className="mt-3 space-y-1.5">
              {nouvelles.map((c) => (
                <li key={c.ref} className="text-[0.94rem] leading-relaxed">
                  <span className="font-semibold">{c.ref}</span>{' '}
                  <span className="text-sourd">
                    · {[c.prenom, c.nom].filter(Boolean).join(' ') || 'client sans nom'} ·{' '}
                    {c.n} fiches · {fcfa(c.total)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <MarcheASuivre />

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {[
            {
              t: 'À encaisser',
              v: compteurs.vivantes.length,
              s: fcfa(compteurs.vivantes.reduce((a, c) => a + (c.total || 0), 0)),
            },
            { t: 'À livrer sous 24 h', v: compteurs.aLivrer.length, s: 'carnets à envoyer' },
            { t: 'Encaissé', v: null, s: fcfa(compteurs.encaisse) },
          ].map((k) => (
            <div key={k.t} className="rounded-2xl border border-trait bg-creme p-5">
              <p className="text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-sourd">
                {k.t}
              </p>
              <p className="mt-1">
                {k.v !== null && <Chiffre className="text-[2rem] text-encre">{k.v}</Chiffre>}
                <span className={`text-[0.95rem] text-sourd ${k.v !== null ? 'ml-2' : ''}`}>
                  {k.s}
                </span>
              </p>
            </div>
          ))}
        </div>

        <div className="mt-8 rounded-2xl border border-trait bg-creme p-5">
          <label className="block">
            <span className="font-semibold">Coller ce qui arrive sur WhatsApp</span>
            <textarea
              value={colle}
              onChange={(e) => setColle(e.target.value)}
              rows={4}
              placeholder="Une commande ou une demande, collée en entier. Le cockpit reconnaît les deux."
              className="mt-2 block w-full rounded-xl border border-trait bg-papier px-4 py-3 text-[0.95rem] leading-relaxed placeholder:text-sourd/60"
            />
          </label>
          {erreur && <p className="mt-2 text-[0.9rem] text-rouge">{erreur}</p>}
          <Bouton className="mt-3" onClick={ranger} disabled={!colle.trim()}>
            Ranger
          </Bouton>
        </div>

        <div className="mt-10 flex flex-wrap items-center gap-2">
          {ONGLETS.map((e) => (
            <button
              key={e.cle}
              type="button"
              onClick={() => setOnglet(e.cle)}
              aria-pressed={onglet === e.cle}
              className={`min-h-[44px] rounded-full border px-4 text-[0.88rem] font-semibold transition-colors ${
                onglet === e.cle
                  ? 'border-brique bg-brique text-creme'
                  : 'border-trait text-sourd hover:border-sourd'
              }`}
            >
              {e.nom} ({e.n})
            </button>
          ))}
        </div>

        {/* ------------------------------------------------- les signalements */}
        {onglet === 'signalements' && (
          <Signalements
            liste={signalements}
            commandes={commandes}
            onAjouter={(s) => majSignalements(ajouter('signalements', s))}
            onRemplacee={(id) =>
              majSignalements(
                signalements.map((s) =>
                  s.id === id ? { ...s, remplacee: !s.remplacee, le: new Date().toISOString() } : s
                )
              )
            }
          />
        )}

        {/* ------------------------------------------------------ les demandes */}
        {onglet === 'demandes' && (
          <div className="mt-5 space-y-3">
            {!demandes.length && (
              <p className="rounded-2xl border border-dashed border-trait px-5 py-10 text-center text-sourd">
                Aucune demande. Chaque demande reçue dit où relever ensuite : c'est la
                meilleure carte de ce qu'il faut collecter.
              </p>
            )}
            {demandes.map((d, i) => (
              <article key={d.date + i} className="rounded-2xl border border-trait bg-creme p-5">
                <div className="flex flex-wrap items-baseline justify-between gap-3">
                  <div>
                    <p className="font-semibold">
                      {d.metier} · {d.ville}
                    </p>
                    <p className="mt-1 text-[0.92rem] text-sourd">
                      {d.prenom} {d.nom} · {d.email} · +{d.tel}
                    </p>
                  </div>
                  <span className="text-[0.85rem] text-sourd">{(d.date || '').slice(0, 10)}</span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Bouton
                    ton="contour"
                    className="px-5"
                    href={`https://wa.me/${d.tel}`}
                    target="_blank"
                    rel="noopener"
                  >
                    Prévenir sur WhatsApp
                  </Bouton>
                  <Bouton
                    ton="nu"
                    onClick={() =>
                      majDemandes(
                        demandes.map((x, k) =>
                          k === i ? { ...x, etat: x.etat === 'faite' ? 'attente' : 'faite' } : x
                        )
                      )
                    }
                  >
                    {d.etat === 'faite' ? 'Remettre en attente' : 'Marquer prévenu'}
                  </Bouton>
                </div>
              </article>
            ))}
          </div>
        )}

        {/* ------------------------------------------------------ les commandes */}
        {onglet !== 'signalements' && onglet !== 'demandes' && (
          <div className="mt-5 space-y-3">
            {!visibles.length && (
              <p className="rounded-2xl border border-dashed border-trait px-5 py-10 text-center text-sourd">
                {commandes.length
                  ? 'Rien dans cette pile.'
                  : "Aucune commande ici pour l'instant. Collez la première au-dessus."}
              </p>
            )}
            {visibles.map((c) => (
              <Ligne key={c.ref} c={c} onEtat={changerEtat} onRetirer={retirer} onLivrer={livrer} />
            ))}
          </div>
        )}
      </div>

      {annulable && (
        <div className="fixed inset-x-0 bottom-0 z-50 px-4 pb-[max(1rem,env(safe-area-inset-bottom))]">
          <div className="mx-auto flex w-full max-w-[34rem] items-center justify-between gap-4 rounded-2xl bg-encre px-5 py-3.5 text-papier shadow-[0_18px_50px_-18px_rgb(20_17_14/0.7)]">
            <span className="text-[0.92rem]">Commande {annulable.c?.ref} retirée.</span>
            <button
              type="button"
              onClick={annuler}
              className="min-h-[44px] shrink-0 font-semibold text-braise underline underline-offset-4"
            >
              Annuler
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

/* ------------------------------------------------------------------------- */

function Ligne({ c, onEtat, onRetirer, onLivrer }) {
  const [ouvert, setOuvert] = useState(false)
  const expiree = estExpiree(c)
  const etat = ETATS.find((e) => e.cle === c.etat) || ETATS[0]
  const metier = METIERS.find((m) => m.cle === c.metier)?.nom || c.metier || 'métier non lu'
  const ville = VILLES.find((v) => v.cle === c.ville)?.nom || c.ville || 'ville non lue'
  const suivant = ETATS[ETATS.findIndex((e) => e.cle === c.etat) + 1]

  return (
    <article className={`rounded-2xl border bg-creme p-5 ${expiree ? 'border-rouge/30' : 'border-trait'}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <Chiffre className="text-[1.05rem]">{c.ref}</Chiffre>
            <span className={`rounded-full px-2.5 py-1 text-[0.75rem] font-semibold ${etat.pastille}`}>
              {etat.nom}
            </span>
            {c.etat === 'recue' && <Rebours date={c.date} />}
          </div>
          <p className="mt-1 text-[0.93rem] text-sourd">
            {(c.prenom || c.nom) && (
              <b className="font-semibold text-encre">
                {c.prenom} {c.nom} ·{' '}
              </b>
            )}
            {metier} · {ville}
            {c.quartier ? ` · ${c.quartier}` : ''} · {c.n} fiches
          </p>
          {c.momoNumero && (
            <p className="mt-0.5 text-[0.9rem] text-sourd">
              paiera depuis le <b className="font-semibold text-encre">+229 {c.momoNumero}</b>
              {MOBILE_MONEY.find((m) => m.cle === c.momoOperateur)
                ? ` (${MOBILE_MONEY.find((m) => m.cle === c.momoOperateur).operateur})`
                : ''}
            </p>
          )}
        </div>
        <Chiffre className="text-[1.4rem] text-brique">{fcfa(c.total)}</Chiffre>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {/* ⚠️ LE GESTE QUI COMPTE. Vous confirmez le paiement, le serveur
            fabrique le carnet, réserve les fiches 90 jours et envoie le lien au
            client ET à vous. Plus besoin d'être devant son PC. */}
        {c.etat === 'payee' && !c.lienCarnet && (
          <Bouton className="px-5" onClick={() => onLivrer(c)} disabled={c.enCours}>
            {c.enCours ? 'Fabrication…' : 'Fabriquer et envoyer le carnet'}
          </Bouton>
        )}
        {c.lienCarnet && (
          <Bouton ton="contour" className="px-5" href={c.lienCarnet} target="_blank" rel="noopener">
            Voir le carnet livré
          </Bouton>
        )}

        {/* Le lien du carnet part par email tout seul. Ce bouton l'envoie AUSSI
            sur le WhatsApp du client, en un clic : la conversation s'ouvre avec
            le message déjà écrit. Un clic vaut mieux qu'un copier-coller, et
            c'est le seul geste qui reste manuel. */}
        {c.etat === 'payee' && c.wa && (
          <Bouton
            ton="contour"
            className="px-5"
            href={`https://wa.me/${String(c.wa).replace(/\D/g, '')}?text=${encodeURIComponent(
              [
                `Bonjour ${c.prenom || ''},`.trim(),
                '',
                `Votre carnet PISTE est prêt : ${c.n} fiches.`,
                'Il vient de partir sur votre email, et le voici aussi ici :',
                '',
                '[COLLEZ LE LIEN DU CARNET ICI]',
                '',
                'Ouvrez-le sur votre téléphone, appuyez sur une fiche, la',
                'conversation démarre. Une fiche injoignable ? Le bouton est',
                'dans le carnet, on la remplace sans frais.',
                '',
                'NEBULA Agency',
              ].join(String.fromCharCode(10))
            )}`}
            target="_blank"
            rel="noopener"
          >
            Envoyer sur son WhatsApp
          </Bouton>
        )}
        {suivant && !expiree && (
          <Bouton className="px-5" onClick={() => onEtat(c.ref, suivant.cle)}>
            {etat.suite}
          </Bouton>
        )}
        {expiree && (
          <Bouton className="px-5" onClick={() => onEtat(c.ref, 'payee')}>
            Elle a payé quand même
          </Bouton>
        )}
        {c.etat !== 'recue' && (
          <Bouton
            ton="contour"
            className="px-5"
            onClick={() => onEtat(c.ref, c.etat === 'livree' ? 'payee' : 'recue')}
          >
            Revenir en arrière
          </Bouton>
        )}
        <Bouton ton="contour" className="px-5" onClick={() => setOuvert((v) => !v)}>
          {ouvert ? 'Replier' : 'Le détail'}
        </Bouton>
        <Bouton ton="nu" onClick={() => onRetirer(c.ref)}>
          Retirer
        </Bouton>
      </div>

      {ouvert && (
        <dl className="mt-4 space-y-1.5 border-t border-trait pt-4 text-[0.92rem]">
          {[
            ['Reçue le', (c.date || '').slice(0, 10)],
            ['Email', c.email],
            ['WhatsApp', c.wa ? '+' + c.wa : ''],
            ['Mobile Money', c.momoNumero ? '+229 ' + c.momoNumero : ''],
            [
              'Informations en plus',
              (c.options || [])
                .map((o) => SUPPLEMENTS.find((s) => s.cle === o)?.nom || o)
                .join(', ') || 'aucune',
            ],
            ['Ce que le client vend', c.offre],
            ['Prix la fiche', c.unitaire ? fcfa(c.unitaire) : ''],
          ]
            .filter(([, v]) => v)
            .map(([t, v]) => (
              <div key={t} className="flex flex-wrap justify-between gap-3">
                <dt className="text-sourd">{t}</dt>
                <dd className="text-right font-medium">{v}</dd>
              </div>
            ))}
          <div className="flex flex-wrap gap-2 pt-2">
            {c.wa && (
              <Bouton
                ton="contour"
                className="px-5"
                href={`https://wa.me/${c.wa}`}
                target="_blank"
                rel="noopener"
              >
                Écrire au client
              </Bouton>
            )}
            {c.email && (
              <Bouton
                ton="contour"
                className="px-5"
                href={`mailto:${c.email}?subject=${encodeURIComponent(
                  'Votre carnet PISTE ' + c.ref
                )}`}
              >
                Envoyer le carnet par email
              </Bouton>
            )}
          </div>
        </dl>
      )}
    </article>
  )
}

/* --------------------------------------------------------- les injoignables */

function Signalements({ liste, commandes, onAjouter, onRemplacee }) {
  const [ref, setRef] = useState('')
  const [commerce, setCommerce] = useState('')

  const ajouterSignalement = () => {
    if (!commerce.trim()) return
    onAjouter({
      id: nouvelleReference() + '-' + Date.now(),
      ref: ref.trim().toUpperCase(),
      commerce: commerce.trim(),
      date: new Date().toISOString(),
      remplacee: false,
    })
    setRef('')
    setCommerce('')
  }

  return (
    <div className="mt-5">
      <div className="rounded-2xl border border-trait bg-creme p-5">
        <p className="font-semibold">Une fiche signalée injoignable</p>
        <p className="mt-1.5 text-[0.93rem] leading-relaxed text-sourd">
          Le client signale depuis son carnet ou sur WhatsApp. Notez-la ici, remplacez-la, et
          la remplaçante part dans le même lien sous 24 heures. Ces signalements disent aussi
          quelles sources vieillissent mal.
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-[10rem_1fr_auto]">
          <input
            value={ref}
            onChange={(e) => setRef(e.target.value)}
            placeholder="PISTE-XXXX"
            aria-label="Code de la commande"
            list="codes-commandes"
            className="min-h-[48px] rounded-xl border border-trait bg-papier px-4 placeholder:text-sourd/60"
          />
          <datalist id="codes-commandes">
            {commandes.map((c) => (
              <option key={c.ref} value={c.ref} />
            ))}
          </datalist>
          <input
            value={commerce}
            onChange={(e) => setCommerce(e.target.value)}
            placeholder="Nom du commerce injoignable"
            aria-label="Nom du commerce"
            className="min-h-[48px] rounded-xl border border-trait bg-papier px-4 placeholder:text-sourd/60"
          />
          <Bouton onClick={ajouterSignalement} disabled={!commerce.trim()}>
            Noter
          </Bouton>
        </div>
      </div>

      <div className="mt-3 space-y-3">
        {!liste.length && (
          <p className="rounded-2xl border border-dashed border-trait px-5 py-10 text-center text-sourd">
            Aucun signalement. Tant mieux.
          </p>
        )}
        {liste.map((s) => (
          <article
            key={s.id}
            className={`flex flex-wrap items-center justify-between gap-3 rounded-2xl border bg-creme p-5 ${
              s.remplacee ? 'border-vert/35' : 'border-trait'
            }`}
          >
            <div>
              <p className="font-semibold">{s.commerce}</p>
              <p className="mt-0.5 text-[0.9rem] text-sourd">
                {s.ref ? s.ref + ' · ' : ''}
                signalée le {(s.date || '').slice(0, 10)}
                {s.remplacee ? ' · remplacée' : ''}
              </p>
            </div>
            <Bouton
              ton={s.remplacee ? 'contour' : 'plein'}
              className="px-5"
              onClick={() => onRemplacee(s.id)}
            >
              {s.remplacee ? 'Annuler le remplacement' : 'Marquer remplacée'}
            </Bouton>
          </article>
        ))}
      </div>
    </div>
  )
}
