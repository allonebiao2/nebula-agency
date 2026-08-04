import { useEffect, useMemo, useState } from 'react'
import { METIERS, NEBULA_WHATSAPP, estFixe, numeroJoli, international } from '../donnees.js'
import { marquerFiche, ouvrirCarnet } from '../supabase.js'
import { Bouton } from './Ui.jsx'

/*
  LE CARNET · ce que le client a payé.

  C'est la seule page de PISTE qui compte vraiment : tout le reste sert à
  arriver ici. Elle s'ouvre au pouce, debout, dans la rue, souvent en 3G.

  Trois principes tenus, tous appris du carnet des 187 :

  1. **On travaille dedans, on ne le lit pas.** Un bouton par ligne qui ouvre
     la bonne conversation avec le bon message. L'état de chaque prospect se
     garde dans le téléphone : on ferme, on revient, on reprend où on en était.

  2. **Un fixe n'a pas WhatsApp.** Il n'a donc pas de bouton WhatsApp, il a un
     bouton « Appeler ». Écrire à un fixe, c'est brûler une ligne pour rien.

  3. **Le signalement n'est pas une politesse.** Sans un bouton pour dire
     « injoignable », personne ne réclame : le client pense simplement que la
     donnée est mauvaise, et il ne revient pas.

  Le carnet ne s'écrit jamais dans la base : il la lit. L'avancement reste dans
  le téléphone du client, et un signalement part sur WhatsApp. Une page qui
  n'écrit rien ne peut rien casser.
*/

const ETATS = [
  { cle: 'ecrit', mot: 'Écrit', classe: 'bg-[#a86a00] text-creme border-transparent' },
  { cle: 'rdv', mot: 'Rendez-vous', classe: 'bg-brique text-creme border-transparent' },
  { cle: 'vendu', mot: 'Vendu', classe: 'bg-vert text-creme border-transparent' },
  { cle: 'non', mot: 'Non', classe: 'bg-rouge text-creme border-transparent' },
]

const FILTRES = [
  { cle: '', mot: 'Tout' },
  { cle: 'reste', mot: 'Pas encore faits' },
  { cle: 'rdv', mot: 'Rendez-vous' },
  { cle: 'vendu', mot: 'Vendus' },
]

function cleEtat(jeton) {
  return `piste_carnet_${jeton}`
}

/* ------------------------------------------------------------------ ligne - */

function Ligne({ f, etat, poser, signaler }) {
  const m = METIERS.find((x) => x.cle === f.metier)
  const fixe = estFixe(f.pays, f.numero)
  const tel = international(f.pays, f.numero)
  const lieu = [f.quartier, f.localite].filter(Boolean).join(' · ')

  return (
    <article
      className={`rounded-2xl border bg-creme p-4 transition-opacity duration-200 ${
        etat === 'non' ? 'border-trait opacity-55' : 'border-trait'
      } ${etat === 'vendu' ? 'border-vert' : ''}`}
    >
      <h3 className="text-[1rem] font-semibold leading-tight text-encre">{f.nom}</h3>
      <p className="mt-1 text-[0.8rem] text-sourd">
        {m?.singulier || 'commerce'}
        {lieu && ` · ${lieu}`}
      </p>
      <p className="mt-1.5 font-mono text-[0.9rem] tabular-nums text-encre">
        {numeroJoli(f.pays, f.numero)}
        {fixe && <span className="ml-2 font-sans text-[0.72rem] text-sourd">ligne fixe</span>}
      </p>

      {f.dirigeant && (
        <p className="mt-1 text-[0.82rem] text-encre">
          <span className="text-sourd">Demander </span>
          {f.dirigeant}
        </p>
      )}
      {f.sansSite && (
        <p className="mt-1 text-[0.82rem] font-medium text-brique">
          N'a rien en ligne. C'est le bon moment.
        </p>
      )}

      <div className="mt-3 flex flex-wrap gap-2">
        {fixe ? (
          <Bouton ton="contour" className="flex-1" href={`tel:+${tel}`}>
            Appeler
          </Bouton>
        ) : (
          <>
            <Bouton
              ton="plein"
              className="flex-1"
              href={`https://wa.me/${tel}${
                f.message ? `?text=${encodeURIComponent(f.message)}` : ''
              }`}
              target="_blank"
              rel="noopener"
            >
              Écrire sur WhatsApp
            </Bouton>
            <Bouton ton="contour" className="flex-none px-5" href={`tel:+${tel}`}>
              Appeler
            </Bouton>
          </>
        )}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        {ETATS.map((e) => (
          <button
            key={e.cle}
            type="button"
            aria-pressed={etat === e.cle}
            onClick={() => poser(etat === e.cle ? '' : e.cle)}
            className={`min-h-[44px] rounded-xl border px-3 text-[0.8rem] font-semibold transition-colors duration-150 ${
              etat === e.cle ? e.classe : 'border-trait bg-transparent text-sourd hover:border-sourd'
            }`}
          >
            {e.mot}
          </button>
        ))}
        <button
          type="button"
          onClick={signaler}
          className="ml-auto min-h-[44px] px-2 text-[0.78rem] font-medium text-sourd underline underline-offset-4 hover:text-brique"
        >
          Injoignable ?
        </button>
      </div>
    </article>
  )
}

/* ================================================================== écran = */

export default function Carnet({ jeton, aller }) {
  const [etat, setEtat] = useState('chargement')
  const [carnet, setCarnet] = useState(null)
  const [etats, setEtats] = useState({})
  const [q, setQ] = useState('')
  const [filtre, setFiltre] = useState('')

  useEffect(() => {
    let vivant = true
    if (!jeton) {
      setEtat('introuvable')
      return
    }
    ouvrirCarnet(jeton)
      .then((c) => {
        if (!vivant) return
        if (!c) {
          setEtat('introuvable')
          return
        }
        setCarnet(c)
        setEtat('pret')
      })
      .catch(() => vivant && setEtat('panne'))
    return () => {
      vivant = false
    }
  }, [jeton])

  /* L'avancement vit dans le téléphone du client, jamais dans la base : ce
     n'est pas notre affaire, et ça marche sans réseau. */
  useEffect(() => {
    if (!jeton) return
    try {
      setEtats(JSON.parse(localStorage.getItem(cleEtat(jeton)) || '{}'))
    } catch (e) {
      setEtats({})
    }
  }, [jeton])

  const poser = (nom, v) => {
    setEtats((e) => {
      const suite = { ...e }
      if (v) suite[nom] = v
      else delete suite[nom]
      try {
        localStorage.setItem(cleEtat(jeton), JSON.stringify(suite))
      } catch (err) {}
      return suite
    })
    /* La marque remonte. C'est le SEUL signal qui dise quelles fiches valent
       quelque chose, et il est annoncé au client en toutes lettres plus bas :
       une donnée reprise en silence n'est pas un signal, c'est une prise.
       Si le réseau manque, l'avancement reste quand même dans le téléphone. */
    marquerFiche(jeton, nom, v)
  }

  const fiches = carnet?.fiches || []
  const visibles = useMemo(() => {
    const t = q.trim().toLowerCase()
    return fiches.filter((f) => {
      const e = etats[f.nom] || ''
      if (filtre === 'reste' && e) return false
      if (filtre && filtre !== 'reste' && e !== filtre) return false
      if (t && !`${f.nom} ${f.localite} ${f.quartier || ''}`.toLowerCase().includes(t)) return false
      return true
    })
  }, [fiches, etats, filtre, q])

  const traites = fiches.filter((f) => etats[f.nom]).length
  const vendus = fiches.filter((f) => etats[f.nom] === 'vendu').length

  function signaler(f) {
    const texte = [
      `Bonjour, une fiche de mon carnet ${carnet.reference} est injoignable :`,
      '',
      `${f.nom} · ${numeroJoli(f.pays, f.numero)}`,
      '',
      'Merci de la remplacer.',
    ].join('\n')
    marquerFiche(jeton, f.nom, 'injoignable')
    window.open(`https://wa.me/${NEBULA_WHATSAPP}?text=${encodeURIComponent(texte)}`, '_blank')
  }

  /* ------------------------------------------------------------ les états - */

  if (etat !== 'pret') {
    const messages = {
      chargement: ['Un instant…', 'On ouvre votre carnet.'],
      introuvable: [
        'Ce carnet n’existe pas.',
        'Le lien est peut-être incomplet : ils sont longs et se coupent facilement dans un message. Écrivez-nous, on vous le renvoie entier.',
      ],
      panne: [
        'On n’arrive pas à ouvrir votre carnet.',
        'Vérifiez votre connexion et réessayez. Si ça continue, écrivez-nous : votre carnet n’est pas perdu, il vous appartient.',
      ],
    }
    const [titre, dessous] = messages[etat]
    return (
      <main className="mx-auto flex min-h-dvh max-w-[34rem] flex-col justify-center px-5 py-16">
        <p className="font-display text-[1.05rem] font-bold tracking-tight text-encre">
          PISTE <span className="font-normal text-sourd">by NEBULA</span>
        </p>
        <h1 className="mt-6 text-[clamp(1.6rem,7vw,2.2rem)]">{titre}</h1>
        <p className="mt-3 text-[0.95rem] leading-relaxed text-sourd">{dessous}</p>
        {etat !== 'chargement' && (
          <div className="mt-7 flex flex-wrap gap-3">
            <Bouton href={`https://wa.me/${NEBULA_WHATSAPP}`} target="_blank" rel="noopener">
              Nous écrire
            </Bouton>
            <Bouton ton="contour" onClick={() => aller('#/')}>
              Retour à l'accueil
            </Bouton>
          </div>
        )}
      </main>
    )
  }

  const cmd = carnet.commande || {}

  return (
    <main className="min-h-dvh bg-papier pb-24">
      {/* ------------------------------------------------------------ entête */}
      <header className="sticky top-0 z-20 border-b border-trait bg-papier/97 px-4 pb-3 pt-4 backdrop-blur-[2px] sm:px-6">
        <div className="mx-auto max-w-[52rem]">
          <div className="flex items-baseline justify-between gap-3">
            <p className="font-display text-[0.98rem] font-bold tracking-tight text-encre">
              PISTE <span className="font-normal text-sourd">by NEBULA</span>
            </p>
            <p className="font-mono text-[0.72rem] tabular-nums text-sourd">{carnet.reference}</p>
          </div>

          <p className="mt-1 text-[0.8rem] text-sourd">
            {fiches.length} fiches · {traites} traité{traites > 1 ? 's' : ''} · {vendus} vendu
            {vendus > 1 ? 's' : ''}
          </p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-papier2">
            <div
              className="h-full rounded-full bg-brique transition-[width] duration-300"
              style={{ width: `${fiches.length ? (traites / fiches.length) * 100 : 0}%` }}
            />
          </div>

          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Chercher un nom, un quartier"
            aria-label="Chercher dans le carnet"
            className="mt-3 min-h-[48px] w-full rounded-2xl border border-trait bg-creme px-4 text-[16px] text-encre placeholder:text-sourd/60"
          />
          <div className="mt-2 flex gap-2 overflow-x-auto pb-1">
            {FILTRES.map((f) => (
              <button
                key={f.cle}
                type="button"
                aria-pressed={filtre === f.cle}
                onClick={() => setFiltre(f.cle)}
                className={`min-h-[44px] flex-none rounded-full border px-4 text-[0.82rem] font-semibold transition-colors duration-150 ${
                  filtre === f.cle
                    ? 'border-brique bg-brique text-creme'
                    : 'border-trait bg-transparent text-sourd hover:border-sourd'
                }`}
              >
                {f.mot}
              </button>
            ))}
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[52rem] px-4 pt-5 sm:px-6">
        {/* ------------------------------------------------ ce qu'on a acheté */}
        <div className="rounded-2xl border border-trait bg-papier2/50 p-4 text-[0.85rem] leading-relaxed text-sourd">
          <p className="text-encre">
            <span className="font-semibold">Votre carnet.</span>{' '}
            {cmd.metierNom ? `${cmd.metierNom}` : 'Vos fiches'}
            {cmd.villeNom ? ` à ${cmd.villeNom}` : ''}, {fiches.length} fiches.
          </p>
          <p className="mt-2">
            Une fiche ne répond plus ? Appuyez sur « Injoignable ? » : elle est remplacée sans
            frais, et la remplaçante apparaît dans ce même lien. Ces fiches sont à vous seul
            pendant 90 jours.
          </p>
        </div>

        {/* ----------------------------------------------------- les fiches - */}
        <div className="mt-4 grid gap-3">
          {visibles.length === 0 ? (
            <p className="py-14 text-center text-[0.9rem] text-sourd">
              Rien avec ces filtres. Appuyez sur « Tout » pour revoir votre carnet entier.
            </p>
          ) : (
            visibles.map((f) => (
              <Ligne
                key={f.nom + f.numero}
                f={f}
                etat={etats[f.nom] || ''}
                poser={(v) => poser(f.nom, v)}
                signaler={() => signaler(f)}
              />
            ))
          )}
        </div>

        <div className="mt-9 flex justify-center">
          <Bouton ton="contour" onClick={() => aller(`#/recu/${jeton}`)}>
            Mon reçu
          </Bouton>
        </div>

        <p className="mt-8 text-center text-[0.78rem] leading-relaxed text-sourd">
          Vos marques nous servent à mieux choisir vos prochaines fiches. On ne regarde que
          ça : ce que vous écrivez à un commerce ne nous regarde pas.
          <br />
          <br />
          Gardez ce lien : il est à vous, il ne périme pas, et votre avancement s'y garde.
          <br />
          Perdu ? Écrivez-nous, on vous le renvoie.
        </p>
      </div>
    </main>
  )
}
