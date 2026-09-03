import { useEffect, useMemo, useState } from 'react'
import { METIERS, NEBULA_WHATSAPP, estFixe, numeroJoli, international } from '../donnees.js'
import { marquerFiche, ouvrirCarnet, signalerInjoignable } from '../supabase.js'
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

/*
  LES QUATRE RÉPONSES.

  Elles s'appelaient « Écrit · Rendez-vous · Vendu · Non ». Mongazi lui-même
  ne savait pas ce qu'elles voulaient dire : quatre mots posés sans phrase
  autour, dans une page qu'on ouvre debout dans la rue. Si celui qui vend le
  produit ne comprend pas, aucun client ne comprendra.

  Elles disent maintenant ce qui S'EST PASSÉ, à la première personne, comme on
  le raconterait à quelqu'un. Un libellé qui se lit tout seul vaut mieux qu'un
  libellé court avec une légende à côté.
*/
const ETATS = [
  {
    cle: 'ecrit',
    mot: 'J’ai écrit',
    aide: 'Vous les avez contactés. Vous attendez leur réponse.',
    classe: 'bg-[#a86a00] text-creme border-transparent',
  },
  {
    cle: 'rdv',
    mot: 'Il veut me voir',
    aide: 'Ils ont répondu et veulent en parler. C’est votre meilleure piste.',
    classe: 'bg-brique text-creme border-transparent',
  },
  {
    cle: 'vendu',
    mot: 'J’ai vendu',
    aide: 'C’est fait, ils ont acheté. Bravo.',
    classe: 'bg-vert text-creme border-transparent',
  },
  {
    cle: 'non',
    mot: 'Pas intéressé',
    aide: 'Ils ont dit non. La fiche passe en gris, vous ne la reverrez plus en premier.',
    classe: 'bg-rouge text-creme border-transparent',
  },
]

const FILTRES = [
  { cle: '', mot: 'Tout' },
  { cle: 'reste', mot: 'Pas encore contactés' },
  { cle: 'ecrit', mot: 'J’ai écrit' },
  { cle: 'rdv', mot: 'Veulent me voir' },
  { cle: 'vendu', mot: 'Vendus' },
]

/* Les initiales du commerce, comme sur une carte : deux lettres suffisent à
   reconnaître une fiche du coin de l'oeil. */
function initiales(nom) {
  const mots = String(nom || '')
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .split(/\s+/)
    .filter((m) => m.length > 1)
  if (!mots.length) return '??'
  return (mots[0][0] + (mots[1]?.[0] || mots[0][1] || '')).toUpperCase()
}

function cleEtat(jeton) {
  return `piste_carnet_${jeton}`
}

/* ------------------------------------------------------------------ ligne - */

function Fiche({ f, rang, total, etat, poser, signaler, metierNom }) {
  const [ouvert, setOuvert] = useState(false)
  const m = METIERS.find((x) => x.cle === f.metier)
  const fixe = estFixe(f.pays, f.numero)
  const tel = international(f.pays, f.numero)
  const lieu = [f.quartier, f.localite].filter(Boolean).join(' · ')
  const marque = ETATS.find((e) => e.cle === etat)

  /*
    OUVRIR WHATSAPP MARQUE « J'ai écrit », mais SEULEMENT si rien n'est encore
    marqué : on n'écrase jamais un « J'ai vendu » parce que la personne a
    rouvert la conversation. Sans ça, le seul signal d'apprentissage de PISTE
    dépendait d'un second geste que personne ne fait debout dans la rue.
  */
  const jeContacte = () => {
    if (!etat) poser('ecrit')
    setOuvert(true)
  }

  return (
    <article className="dossier" data-ouvert={ouvert ? 'oui' : 'non'}>
      <div className={`dossier-carte ${etat === 'non' ? 'opacity-60' : ''}`}>
        <div className="dossier-trame" aria-hidden="true" />

        {/* la bande du haut : un document numéroté, pas une ligne de liste */}
        <div className="dossier-bande">
          <span className="truncate">{m?.singulier || metierNom || 'commerce'}</span>
          <span className="flex-none font-mono tabular-nums tracking-normal">
            {String(rang).padStart(2, '0')}/{String(total).padStart(2, '0')}
          </span>
        </div>

        {/* ⚠️ Le corps entier ouvre la fiche : dans la rue, au pouce, viser une
            petite flèche ne marche pas. */}
        <button
          type="button"
          className="dossier-poignee"
          aria-expanded={ouvert}
          onClick={() => setOuvert((o) => !o)}
        >
          <div className="flex min-w-0 items-center gap-3 px-3.5 pb-3 pt-3.5">
            <span className="dossier-initiales" aria-hidden="true">
              {initiales(f.nom)}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-[1.02rem] font-semibold leading-tight text-encre">
                {f.nom}
              </span>
              {lieu && <span className="mt-0.5 block text-[0.8rem] text-sourd">{lieu}</span>}
              <span className="mt-1 block font-mono text-[0.92rem] tabular-nums text-encre">
                {numeroJoli(f.pays, f.numero)}
                {fixe && (
                  <span className="ml-2 font-sans text-[0.7rem] text-sourd">ligne fixe</span>
                )}
              </span>
            </span>
          </div>

          <div className="flex items-center justify-between gap-2 px-3.5 pb-3">
            {marque ? (
              <span
                className={`rounded-lg px-2.5 py-1 text-[0.74rem] font-semibold ${marque.classe}`}
              >
                {marque.mot}
              </span>
            ) : (
              <span className="text-[0.76rem] text-sourd">Pas encore contacté</span>
            )}
            <span className="flex items-center gap-1.5 text-[0.76rem] font-semibold text-brique">
              {ouvert ? 'Replier' : 'Voir la fiche'}
              <svg
                viewBox="0 0 12 12"
                aria-hidden="true"
                className={`h-3 w-3 transition-transform duration-300 ${ouvert ? 'rotate-180' : ''}`}
              >
                <path
                  d="M2 4.2 6 8.2l4-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
          </div>
        </button>

        {/* Les deux gestes qui rapportent restent TOUJOURS visibles : les
            cacher derrière une ouverture reviendrait à cacher ce qu'on vend. */}
        <div className="flex flex-wrap gap-2 px-3.5 pb-3.5">
          {fixe ? (
            <Bouton ton="contour" className="flex-1" href={`tel:+${tel}`} onClick={jeContacte}>
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
                onClick={jeContacte}
              >
                Écrire sur WhatsApp
              </Bouton>
              <Bouton
                ton="contour"
                className="flex-none px-5"
                href={`tel:+${tel}`}
                onClick={jeContacte}
              >
                Appeler
              </Bouton>
            </>
          )}
        </div>

        {/* ─────────────────────────────────────────── le dos de la fiche ── */}
        <div className="dossier-dos">
          <div className="dossier-dedans">
            <div className="dossier-perfore px-3.5 pb-4 pt-3.5">
              <dl className="dossier-releve">
                <dt>Commerce</dt>
                <dd>{f.nom}</dd>

                <dt>Métier</dt>
                <dd>{m?.singulier || metierNom || 'commerce'}</dd>

                <dt>Où</dt>
                <dd>{lieu || 'non précisé'}</dd>

                <dt>Numéro</dt>
                <dd className="font-mono tabular-nums">
                  {numeroJoli(f.pays, f.numero)}
                  {fixe && <span className="ml-2 font-sans text-sourd">ligne fixe</span>}
                </dd>

                {f.dirigeant && (
                  <>
                    <dt>Demander</dt>
                    <dd>{f.dirigeant}</dd>
                  </>
                )}
                {f.sansSite && (
                  <>
                    <dt>Sur internet</dt>
                    <dd className="font-medium text-brique">
                      Rien du tout. C’est le bon moment pour les approcher.
                    </dd>
                  </>
                )}
              </dl>

              {fixe && (
                <p className="mt-3.5 rounded-xl bg-papier2/60 px-3 py-2.5 text-[0.82rem] leading-relaxed text-sourd">
                  C’est un numéro fixe : il n’a pas WhatsApp. On l’appelle, on ne lui écrit
                  pas.
                </p>
              )}

              {f.message && !fixe && (
                <div className="mt-3.5">
                  <p className="text-[0.66rem] font-bold uppercase tracking-[0.09em] text-sourd">
                    Le message qui partira
                  </p>
                  <p className="mt-1.5 whitespace-pre-line rounded-xl bg-braise/10 px-3 py-2.5 text-[0.84rem] leading-relaxed text-encre">
                    {f.message}
                  </p>
                  <p className="mt-1.5 text-[0.78rem] text-sourd">
                    Il s’écrit tout seul dans WhatsApp. Vous pouvez le changer avant
                    d’envoyer.
                  </p>
                </div>
              )}
            </div>

            {/* ─────────────────────────── les quatre réponses, expliquées ── */}
            <div className="dossier-perfore bg-papier2/35 px-3.5 pb-4 pt-3.5">
              <p className="text-[0.9rem] font-semibold text-encre">
                Où en êtes-vous avec ce commerce ?
              </p>
              <p className="mt-1 text-[0.82rem] leading-relaxed text-sourd">
                Appuyez sur ce qui s’est passé. Ça reste dans votre téléphone, même sans
                réseau, et ça nous aide à mieux choisir vos prochaines fiches.
              </p>

              <div className="mt-3 grid gap-2">
                {ETATS.map((e) => {
                  const actif = etat === e.cle
                  return (
                    <button
                      key={e.cle}
                      type="button"
                      aria-pressed={actif}
                      onClick={() => poser(actif ? '' : e.cle)}
                      className={`flex min-h-[52px] items-start gap-3 rounded-xl border px-3 py-2.5 text-left transition-colors duration-150 ${
                        actif ? e.classe : 'border-trait bg-creme hover:border-sourd'
                      }`}
                    >
                      <span
                        aria-hidden="true"
                        className={`mt-0.5 grid h-5 w-5 flex-none place-items-center rounded-full border-2 ${
                          actif ? 'border-creme bg-creme/25' : 'border-trait'
                        }`}
                      >
                        {actif && (
                          <svg viewBox="0 0 12 12" className="h-3 w-3">
                            <path
                              d="M2.5 6.3 5 8.7l4.5-5"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </svg>
                        )}
                      </span>
                      <span className="min-w-0">
                        <span className="block text-[0.9rem] font-semibold">{e.mot}</span>
                        <span
                          className={`mt-0.5 block text-[0.78rem] leading-snug ${
                            actif ? 'opacity-90' : 'text-sourd'
                          }`}
                        >
                          {e.aide}
                        </span>
                      </span>
                    </button>
                  )
                })}
              </div>

              {etat && (
                <button
                  type="button"
                  onClick={() => poser('')}
                  className="mt-2 min-h-[44px] px-1 text-[0.8rem] font-medium text-sourd underline underline-offset-4 hover:text-brique"
                >
                  Effacer ma réponse
                </button>
              )}
            </div>

            <div className="px-3.5 pb-4 pt-3">
              <button
                type="button"
                onClick={signaler}
                className="min-h-[44px] text-[0.82rem] font-medium text-sourd underline underline-offset-4 hover:text-brique"
              >
                Ce numéro ne répond plus ?
              </button>
              <p className="mt-1 text-[0.78rem] leading-relaxed text-sourd">
                Dites-le nous : on la remplace sans rien vous facturer, et la remplaçante
                apparaît dans ce même carnet.
              </p>
            </div>
          </div>
        </div>
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
    signalerInjoignable(jeton, f.nom)
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
            Ces fiches sont à vous seul pendant 90 jours.
          </p>
        </div>

        {/*
          ⚠️ CE BLOC EST LE PLUS IMPORTANT DE LA PAGE.
          Le carnet arrive chez des gens qui n'ont jamais fait de démarchage.
          Sans ces trois phrases, ils voyaient une liste de numéros et quatre
          mots qu'ils ne comprenaient pas. Un outil qu'il faut deviner n'est
          pas un outil, c'est un devoir.
        */}
        <ol className="mt-3 grid gap-2.5 rounded-2xl border border-trait bg-creme p-4">
          {[
            [
              'Appuyez sur « Écrire sur WhatsApp ».',
              'La conversation s’ouvre toute seule, avec le message déjà écrit. Vous n’avez qu’à envoyer.',
            ],
            [
              'Dites ce qui s’est passé.',
              'Ouvrez la fiche et appuyez sur « J’ai écrit », « Il veut me voir », « J’ai vendu » ou « Pas intéressé ». C’est comme ça que vous savez où vous en êtes.',
            ],
            [
              'Fermez quand vous voulez.',
              'Votre avancement reste dans ce téléphone, même sans réseau. Revenez par le même lien, tout y est.',
            ],
          ].map(([titre, dessous], i) => (
            <li key={titre} className="flex gap-3">
              <span
                aria-hidden="true"
                className="grid h-6 w-6 flex-none place-items-center rounded-full bg-brique text-[0.76rem] font-bold text-creme"
              >
                {i + 1}
              </span>
              <span className="min-w-0">
                <span className="block text-[0.9rem] font-semibold text-encre">{titre}</span>
                <span className="mt-0.5 block text-[0.84rem] leading-relaxed text-sourd">
                  {dessous}
                </span>
              </span>
            </li>
          ))}
        </ol>

        {/* ----------------------------------------------------- les fiches - */}
        <div className="mt-4 grid gap-3">
          {visibles.length === 0 ? (
            <p className="py-14 text-center text-[0.9rem] text-sourd">
              Rien avec ces filtres. Appuyez sur « Tout » pour revoir votre carnet entier.
            </p>
          ) : (
            visibles.map((f, i) => (
              <Fiche
                key={f.nom + f.numero}
                f={f}
                rang={i + 1}
                total={visibles.length}
                metierNom={cmd.metierNom}
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
