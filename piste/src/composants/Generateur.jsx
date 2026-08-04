import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import {
  METIERS,
  VILLES,
  MINIMUM,
  stock,
  fichesApercu,
  numeroMasque,
  messagePourFiche,
} from '../donnees.js'
import { SUPPLEMENTS, calcul, fcfa, nombre, prochainPalier } from '../prix.js'
import { CLES, ajouter, ecrire } from '../stockage.js'
import { Bouton } from './Ui.jsx'

/*
  LE GÉNÉRATEUR · décisions 47 à 59.

  Ce qui est demandé, mot pour mot : « une interface genre générateur qu'on voit
  directement sans perte de temps, comme ça même un enfant puisse comprendre et
  commander ».

  Six écrans successifs, c'étaient six occasions d'abandonner avant de voir un
  prix. Ici tout se règle sur un seul panneau, le prix suit chaque geste, et
  trois VRAIES fiches changent sous les yeux selon ce qu'on choisit.

  Ce qui rend l'outil compréhensible sans connaître un mot technique, ce n'est
  pas une explication : c'est **la phrase en haut qui se réécrit toute seule**.
  On comprend sa propre commande en la lisant.

  Rien n'est inventé ici. Les fiches de l'aperçu sont relevées, leur numéro est
  masqué sur les quatre derniers chiffres : on voit qu'il est vrai et complet,
  on ne peut pas s'en servir.
*/

const PAQUETS = [10, 50, 100]

/* -------------------------------------------------- la phrase qui s'écrit - */

function Phrase({ metier, ville, n, options, dispo }) {
  const m = METIERS.find((x) => x.cle === metier)
  const v = VILLES.find((x) => x.cle === ville)
  const pris = SUPPLEMENTS.filter((s) => options[s.cle])

  /* Chaque morceau apparaît quand il est décidé, et pas avant : la phrase
     raconte l'avancement au lieu de montrer des trous à remplir. */
  const morceaux = []
  if (m && n) morceaux.push({ cle: 'n', fort: true, t: `${nombre(n)} ${m.pluriel}` })
  else if (m) morceaux.push({ cle: 'm', fort: true, t: m.pluriel })
  if (v) morceaux.push({ cle: 'v', t: 'à' }, { cle: 'vn', fort: true, t: v.court })
  if (pris.length) {
    morceaux.push({ cle: 'a', t: ', avec' })
    pris.forEach((s, i) => {
      if (i > 0) morceaux.push({ cle: 'et' + i, t: i === pris.length - 1 ? 'et' : ',' })
      morceaux.push({ cle: s.cle, fort: true, t: s.court })
    })
  }

  return (
    <p
      data-phrase
      className="text-[clamp(1.05rem,4.4vw,1.5rem)] leading-snug font-medium text-encre"
    >
      <span className="text-sourd">Je cherche </span>
      {morceaux.length === 0 ? (
        <span className="text-sourd">…dites-nous quoi, juste en dessous.</span>
      ) : (
        morceaux.map((x, i) => (
          /* ⚠️ L'espace se pose ENTRE les éléments, jamais dedans : un
             `inline-block` avale l'espace qui le termine, et on lisait
             « coutureà Cotonou ». */
          <Fragment key={x.cle}>
            <span
              className={
                x.fort ? 'phrase-mot font-semibold text-brique' : 'phrase-mot text-sourd'
              }
            >
              {x.t}
            </span>
            {i < morceaux.length - 1 ? ' ' : ''}
          </Fragment>
        ))
      )}
      {m && v && dispo >= MINIMUM && <span className="text-sourd">.</span>}
    </p>
  )
}

/* ------------------------------------------------------------- les choix -- */

function Pastille({ actif, desactive, onClick, titre, dessous, droite, compact = false }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={desactive}
      aria-pressed={actif}
      className={`group relative flex min-h-[56px] w-full items-center gap-3 rounded-2xl border text-left ${
        compact ? 'px-3 py-2.5' : 'px-4 py-3'
      } transition-[border-color,background-color,transform] duration-200 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-45 disabled:active:translate-y-0 ${
        actif
          ? 'border-brique bg-creme shadow-[0_0_0_1px_var(--color-brique)]'
          : 'border-trait bg-creme/60 hover:border-sourd'
      }`}
    >
      <span className="min-w-0 flex-1">
        <span
          className={`block font-semibold leading-tight text-encre ${
            compact ? 'text-[0.86rem]' : 'text-[0.98rem]'
          }`}
        >
          {titre}
        </span>
        {dessous && (
          <span className="mt-0.5 block text-[0.78rem] leading-tight text-sourd">{dessous}</span>
        )}
      </span>
      {droite}
    </button>
  )
}

function Interrupteur({ s, actif, onClick, n }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={actif}
      onClick={onClick}
      className={`flex min-h-[56px] w-full items-center gap-3 rounded-2xl border px-4 py-3 text-left transition-[border-color,background-color] duration-200 ${
        actif ? 'border-brique bg-creme' : 'border-trait bg-creme/60 hover:border-sourd'
      }`}
    >
      <span
        aria-hidden
        className={`relative h-6 w-11 flex-none rounded-full transition-colors duration-200 ${
          actif ? 'bg-brique' : 'bg-trait'
        }`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-creme transition-[left] duration-200 ${
            actif ? 'left-[1.4rem]' : 'left-0.5'
          }`}
        />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-[0.95rem] font-semibold leading-tight text-encre">{s.nom}</span>
        <span className="mt-0.5 block text-[0.78rem] leading-tight text-sourd">{s.resume}</span>
      </span>
      <span
        className={`flex-none text-[0.85rem] font-semibold tabular-nums ${
          actif ? 'text-brique' : 'text-sourd'
        }`}
      >
        +{s.prix} F
        <span className="ml-1 hidden text-[0.7rem] font-normal sm:inline">la fiche</span>
      </span>
    </button>
  )
}

/* ------------------------------------------------------------- l'aperçu --- */

function FicheApercu({ f, offre, avecMessage, retard }) {
  const m = METIERS.find((x) => x.cle === f.metier)
  const [ecrit, setEcrit] = useState('')
  const message = useMemo(
    () => (avecMessage ? messagePourFiche(f, offre) : ''),
    [f, offre, avecMessage]
  )

  /* Le message s'écrit lettre par lettre : c'est l'animation signature de
     l'aperçu, et elle vient du métier. On s'arrête net si la fiche change. */
  useEffect(() => {
    if (!message) {
      setEcrit('')
      return
    }
    const doux = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (doux) {
      setEcrit(message)
      return
    }
    let i = 0
    setEcrit('')
    const t = setInterval(() => {
      i += 3
      setEcrit(message.slice(0, i))
      if (i >= message.length) clearInterval(t)
    }, 16)
    return () => clearInterval(t)
  }, [message])

  return (
    <article
      className="apercu-fiche rounded-2xl border border-trait bg-creme p-4"
      style={{ animationDelay: `${retard}ms` }}
    >
      <p className="text-[0.95rem] font-semibold leading-tight text-encre">{f.nom}</p>
      <p className="mt-1 text-[0.78rem] text-sourd">
        {m?.singulier}
        {(f.quartier || f.localite) && ' · '}
        {[f.quartier, f.localite].filter(Boolean).join(', ')}
      </p>
      <p className="mt-2 font-mono text-[0.85rem] tabular-nums text-encre">
        {numeroMasque(f.pays, f.numero)}
      </p>
      {avecMessage && (
        <p className="mt-3 whitespace-pre-line rounded-xl bg-papier2/70 px-3 py-2 text-[0.78rem] leading-snug text-encre">
          {ecrit}
          <span className="curseur-ecrit" aria-hidden />
        </p>
      )}
    </article>
  )
}

/* ================================================================ panneau = */

export default function Generateur({ aller, onEtat }) {
  const [metier, setMetier] = useState('')
  const [ville, setVille] = useState('')
  const [n, setN] = useState(50)
  const [options, setOptions] = useState({})
  const [offre, setOffre] = useState('')
  const [essai, setEssai] = useState(false)

  /* Demande, quand il n'y a rien à vendre (décision 58) */
  const [contact, setContact] = useState('')
  const [envoyee, setEnvoyee] = useState(false)

  const objetMetier = METIERS.find((m) => m.cle === metier)
  const objetVille = VILLES.find((v) => v.cle === ville)
  const horsCatalogue = !!objetMetier?.horsStock
  const dispo = metier && ville && !horsCatalogue ? stock(metier, ville) : null
  const vide = (metier && horsCatalogue) || (dispo !== null && dispo < MINIMUM)

  /* Le curseur ne dépasse jamais le stock réel : on ne vend pas ce qui n'existe pas. */
  const plafond = dispo && dispo >= MINIMUM ? dispo : 100
  useEffect(() => {
    if (dispo && dispo >= MINIMUM && n > dispo) setN(dispo)
  }, [dispo, n])

  const c = useMemo(() => calcul(n, options), [n, options])
  /* Le prix n'apparaît qu'à partir du premier réglage (décision 50). */
  const prixVisible = !!metier && !vide
  const fiches = useMemo(
    () => (metier ? fichesApercu(metier, ville || 'cotonou', 3) : []),
    [metier, ville]
  )
  const veutMessage = !!options.message
  const offreOk = !veutMessage || offre.trim().length >= 8
  const pret = !!metier && !!ville && !vide && n >= MINIMUM && offreOk

  const champOffre = useRef(null)

  function commander() {
    setEssai(true)
    if (!pret) {
      if (veutMessage && !offreOk) champOffre.current?.focus()
      return
    }
    /* Le générateur ne fait que composer : le récapitulatif, les coordonnées et
       le paiement restent l'écran de commande, qui les tient déjà. */
    ecrire(CLES.brouillon, [{ metier, ville, quartier: '', n, options, offre }])
    aller('#/commander')
  }

  function envoyerDemande() {
    if (contact.trim().length < 5) return
    ajouter(CLES.demandes, {
      reference: 'D-' + Date.now().toString(36).toUpperCase().slice(-5),
      metier: objetMetier?.nom || metier,
      ville: objetVille?.nom || ville,
      contact: contact.trim(),
      date: new Date().toISOString(),
    })
    setEnvoyee(true)
  }

  /* Une seule barre fixe en bas de page, et c'est la vitrine qui la dessine.
     Deux barres collées au même endroit se marcheraient dessus : le générateur
     dit seulement où il en est, et à quoi ressemble le bouton. */
  useEffect(() => {
    if (!onEtat) return
    onEtat({ prixVisible, total: c.total, n, pret, commander })
  }, [onEtat, prixVisible, c.total, n, pret])

  const suivant = prochainPalier(n)

  return (
    <div id="generateur" className="scroll-mt-4">
      {/* -------------------------------------------------- la phrase, en haut */}
      <div className="rounded-t-3xl border border-b-0 border-trait bg-papier2/60 px-5 py-5 sm:px-7">
        <p className="mb-2 text-[0.7rem] font-semibold uppercase tracking-[0.2em] text-brique">
          Composez votre commande
        </p>
        <Phrase metier={metier} ville={ville} n={n} options={options} dispo={dispo} />
      </div>

      <div className="rounded-b-3xl border border-trait bg-creme/40 px-5 py-6 sm:px-7">
        {/* ------------------------------------------------------- 1. le métier */}
        <fieldset>
          <legend className="mb-3 text-[0.82rem] font-semibold text-encre">
            1 · Quel métier vous cherchez ?
          </legend>
          {/* ⚠️ Onze métiers au lieu de trois depuis que le moteur collecte.
              Onze cartes hautes, c'est un panneau qu'on fait défiler avant même
              d'avoir choisi : deux colonnes dès le téléphone, et l'exemple ne
              s'affiche que sur le métier choisi. On garde tout dans un écran. */}
          <div className="grid grid-cols-2 gap-2 lg:grid-cols-3">
            {METIERS.map((m) => (
              <Pastille
                key={m.cle}
                actif={metier === m.cle}
                onClick={() => setMetier(m.cle)}
                titre={m.nom}
                dessous={metier === m.cle ? m.exemple : ''}
                compact
              />
            ))}
          </div>
        </fieldset>

        {/* -------------------------------------------------------- 2. la ville */}
        {metier && !horsCatalogue && (
          <fieldset className="pousse mt-7">
            <legend className="mb-1 text-[0.82rem] font-semibold text-encre">
              2 · Dans quelle ville ?
            </legend>
            <p className="mb-3 text-[0.78rem] text-sourd">
              Le nombre disponible est écrit à droite. On ne vend jamais ce qu'on n'a pas.
            </p>
            <div className="grid gap-2 sm:grid-cols-2">
              {VILLES.map((v) => {
                const d = stock(metier, v.cle)
                const assez = d >= MINIMUM
                return (
                  <Pastille
                    key={v.cle}
                    actif={ville === v.cle}
                    onClick={() => setVille(v.cle)}
                    titre={v.nom}
                    dessous={v.detail}
                    droite={
                      <span className="flex-none text-right">
                        <span
                          className={`block text-[1.05rem] font-bold tabular-nums leading-none ${
                            assez ? 'text-brique' : 'text-sourd'
                          }`}
                        >
                          {assez ? d : '0'}
                        </span>
                        <span className="mt-0.5 block text-[0.66rem] leading-none text-sourd">
                          {assez ? 'disponibles' : 'bientôt'}
                        </span>
                      </span>
                    }
                  />
                )
              })}
            </div>
          </fieldset>
        )}

        {/* ------------------------------ le panneau bascule : rien à vendre ici */}
        {vide && (
          <div className="pousse mt-7 rounded-2xl border border-brique/40 bg-papier2/70 p-5">
            {envoyee ? (
              <>
                <p className="text-[1rem] font-semibold text-encre">C'est noté.</p>
                <p className="mt-2 text-[0.9rem] leading-relaxed text-sourd">
                  On vous prévient dès que{' '}
                  <span className="font-semibold text-encre">
                    {objetMetier?.pluriel || 'ce métier'}
                    {objetVille ? ` à ${objetVille.court}` : ''}
                  </span>{' '}
                  sont prêts. Vous serez servi avant tout le monde.
                </p>
              </>
            ) : (
              <>
                <p className="text-[1rem] font-semibold text-encre">
                  On n'a pas encore ça, et on ne va pas vous le vendre quand même.
                </p>
                <p className="mt-2 text-[0.9rem] leading-relaxed text-sourd">
                  Laissez votre WhatsApp ou votre email : on vous prévient dès que c'est prêt,
                  et vous passez devant.
                </p>
                <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                  <input
                    type="text"
                    inputMode="email"
                    aria-label="Votre WhatsApp ou votre email"
                    placeholder="Votre WhatsApp ou votre email"
                    value={contact}
                    onChange={(e) => setContact(e.target.value)}
                    className="min-h-[52px] flex-1 rounded-2xl border border-trait bg-creme px-4 text-encre placeholder:text-sourd/60"
                  />
                  <Bouton onClick={envoyerDemande} disabled={contact.trim().length < 5}>
                    Prévenez-moi
                  </Bouton>
                </div>
              </>
            )}
          </div>
        )}

        {/* ------------------------------------------------------ 3. le nombre */}
        {metier && ville && !vide && (
          <fieldset className="pousse mt-7">
            <legend className="mb-3 text-[0.82rem] font-semibold text-encre">
              3 · Combien de fiches ?
            </legend>
            <div className="flex gap-2">
              {PAQUETS.filter((p) => p <= plafond).map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setN(p)}
                  aria-pressed={n === p}
                  className={`min-h-[56px] flex-1 rounded-2xl border text-[1.15rem] font-bold tabular-nums transition-[border-color,background-color,transform] duration-200 active:translate-y-px ${
                    n === p
                      ? 'border-brique bg-brique text-creme'
                      : 'border-trait bg-creme/60 text-encre hover:border-sourd'
                  }`}
                >
                  {p}
                </button>
              ))}
              {plafond < 100 && (
                <button
                  type="button"
                  onClick={() => setN(plafond)}
                  aria-pressed={n === plafond}
                  className={`min-h-[56px] flex-1 rounded-2xl border text-[1.15rem] font-bold tabular-nums transition-colors duration-200 ${
                    n === plafond
                      ? 'border-brique bg-brique text-creme'
                      : 'border-trait bg-creme/60 text-encre hover:border-sourd'
                  }`}
                >
                  {plafond}
                </button>
              )}
            </div>

            <div className="mt-4 flex items-baseline justify-between">
              <span className="text-[0.78rem] text-sourd">ou le nombre exact</span>
              <span className="font-display text-[1.6rem] font-bold tabular-nums leading-none text-encre">
                {nombre(n)}
              </span>
            </div>
            <input
              type="range"
              min={MINIMUM}
              max={plafond}
              step={1}
              value={n}
              onChange={(e) => setN(Number(e.target.value))}
              aria-label="Nombre de fiches"
              className="piste mt-2 w-full"
              style={{
                '--piste-remplie': `linear-gradient(90deg,var(--color-brique) ${
                  ((n - MINIMUM) / Math.max(1, plafond - MINIMUM)) * 100
                }%,var(--color-papier2) 0)`,
              }}
            />
            <div className="mt-1 flex justify-between text-[0.72rem] tabular-nums text-sourd">
              <span>{MINIMUM} minimum</span>
              <span>{nombre(plafond)} disponibles</span>
            </div>
            {suivant && suivant.seuil <= plafond && (
              <p className="mt-3 text-[0.78rem] text-sourd">
                À {suivant.seuil} fiches, la remise passe à{' '}
                <span className="font-semibold text-brique">{Math.round(suivant.taux * 100)} %</span>.
              </p>
            )}
          </fieldset>
        )}

        {/* -------------------------------------------------- 4. les suppléments */}
        {metier && ville && !vide && (
          <fieldset className="pousse mt-7">
            <legend className="mb-1 text-[0.82rem] font-semibold text-encre">
              4 · Quelles informations en plus ?
            </legend>
            <p className="mb-3 text-[0.78rem] text-sourd">
              Toutes les fiches ont le même prix de base. C'est ce que vous ajoutez ici qui le fait
              monter, et vous voyez de combien.
            </p>
            <div className="grid gap-2">
              {SUPPLEMENTS.map((s) => (
                <Interrupteur
                  key={s.cle}
                  s={s}
                  n={n}
                  actif={!!options[s.cle]}
                  onClick={() => setOptions((o) => ({ ...o, [s.cle]: !o[s.cle] }))}
                />
              ))}
            </div>

            {/* Obligatoire dès que le message est coché : sans savoir ce qu'il
                vend, on ne peut pas rédiger (décision 57). */}
            {veutMessage && (
              <div className="pousse mt-4 rounded-2xl border border-trait bg-creme p-4">
                <label
                  htmlFor="offre"
                  className="block text-[0.9rem] font-semibold leading-tight text-encre"
                >
                  Vous vendez quoi ?
                </label>
                <p className="mt-1 text-[0.78rem] leading-snug text-sourd">
                  Une phrase suffit. C'est avec elle qu'on écrit le message de chaque fiche, et vous
                  le voyez s'écrire juste en dessous.
                </p>
                <textarea
                  id="offre"
                  ref={champOffre}
                  rows={2}
                  value={offre}
                  onChange={(e) => setOffre(e.target.value)}
                  placeholder="je propose une assurance santé pensée pour les commerçants et leur famille"
                  className="mt-3 block w-full rounded-xl border border-trait bg-papier2/40 px-3 py-2 text-[0.9rem] text-encre placeholder:text-sourd/60"
                />
                {essai && !offreOk && (
                  <p className="mt-2 text-[0.8rem] font-medium text-brique">
                    Écrivez une phrase, même courte. Sans elle, le message ne peut pas être écrit.
                  </p>
                )}
              </div>
            )}
          </fieldset>
        )}

        {/* ------------------------------------------------------- 5. l'aperçu */}
        {metier && !vide && fiches.length > 0 && (
          <div className="pousse mt-8 border-t border-trait pt-6">
            <p className="text-[0.82rem] font-semibold text-encre">
              Voilà ce que vous recevrez.
            </p>
            <p className="mt-1 text-[0.78rem] leading-snug text-sourd">
              Trois vraies fiches relevées, prises dans ce que vous venez de choisir. Les quatre
              derniers chiffres sont masqués tant que rien n'est payé.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              {fiches.map((f, i) => (
                <FicheApercu
                  key={f.nom}
                  f={f}
                  offre={offre}
                  avecMessage={veutMessage}
                  retard={i * 90}
                />
              ))}
            </div>
          </div>
        )}

        {/* ---------------------------------------------- le prix, et le départ */}
        {prixVisible && (
          <div className="pousse mt-8 rounded-2xl bg-encre p-5 text-papier">
            <dl className="space-y-1.5 text-[0.85rem]">
              {c.lignes.map((l) => (
                <div key={l.cle} className="flex items-baseline justify-between gap-4">
                  <dt className="text-sable">
                    {l.nom}
                    <span className="text-sable/60">
                      {' '}
                      · {l.unite} F × {nombre(l.n)}
                    </span>
                  </dt>
                  <dd className="tabular-nums">{fcfa(l.montant)}</dd>
                </div>
              ))}
              {c.taux > 0 && (
                <div className="flex items-baseline justify-between gap-4 text-vertclair">
                  <dt>Remise {Math.round(c.taux * 100)} %</dt>
                  <dd className="tabular-nums">− {fcfa(c.remise)}</dd>
                </div>
              )}
              <div className="flex items-baseline justify-between gap-4 border-t border-traitsombre pt-3 text-[1rem]">
                <dt className="font-semibold">À payer</dt>
                <dd className="font-display text-[1.7rem] font-bold tabular-nums leading-none text-braise">
                  {fcfa(c.total)}
                </dd>
              </div>
            </dl>
            <p className="mt-2 text-right text-[0.75rem] text-sable/70">
              soit {fcfa(c.parFiche)} la fiche
            </p>

            <div className="mt-5 hidden sm:block">
              <Bouton ton="pleinClair" className="w-full" onClick={commander}>
                Commander {nombre(n)} fiches
              </Bouton>
              <p className="mt-2 text-center text-[0.75rem] text-sable/70">
                Vous ne payez rien ici. On vous donne le montant et le numéro à l'écran suivant.
              </p>
            </div>
          </div>
        )}
      </div>

    </div>
  )
}
