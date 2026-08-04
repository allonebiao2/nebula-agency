import { useEffect, useMemo, useState } from 'react'
import {
  METIERS,
  MOBILE_MONEY,
  NEBULA_WHATSAPP_JOLI,
  VILLES,
  nouvelleReference,
} from '../donnees.js'
import { SUPPLEMENTS, fcfa } from '../prix.js'
import { ajouter, ecrire, estExpiree, lire, resteEn } from '../stockage.js'
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

export default function Cockpit({ aller }) {
  const [commandes, setCommandes] = useState([])
  const [demandes, setDemandes] = useState([])
  const [signalements, setSignalements] = useState([])
  const [colle, setColle] = useState('')
  const [erreur, setErreur] = useState('')
  const [annulable, setAnnulable] = useState(null)
  const [onglet, setOnglet] = useState('recue')
  const [, rafraichir] = useState(0)

  useEffect(() => {
    setCommandes(lire('commandes'))
    setDemandes(lire('demandes'))
    setSignalements(lire('signalements'))
    const i = setInterval(() => rafraichir((x) => x + 1), 30000)
    return () => clearInterval(i)
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

  const changerEtat = (ref, etat) =>
    majCommandes(
      commandes.map((c) =>
        c.ref === ref
          ? { ...c, etat, [etat === 'payee' ? 'payeeLe' : 'livreeLe']: new Date().toISOString() }
          : c
      )
    )

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
              <Ligne key={c.ref} c={c} onEtat={changerEtat} onRetirer={retirer} />
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

function Ligne({ c, onEtat, onRetirer }) {
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
