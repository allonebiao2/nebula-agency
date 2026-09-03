import { useEffect, useMemo, useRef, useState } from 'react'
import {
  METIERS,
  MINIMUM,
  MOBILE_MONEY,
  NEBULA_WHATSAPP,
  VILLES,
  ficheExemple,
  messagePourFiche,
  nouvelleReference,
  stock,
  plurielsListe,
} from '../donnees.js'
import { BASE, SUPPLEMENTS, calcul, fcfa, nombre as jolinombre } from '../prix.js'
import { deposerCommande, marquerVisite } from '../supabase.js'
import { CLES, ajouter, lire } from '../stockage.js'
import FicheExemple from './FicheExemple.jsx'
import Paiement from './Paiement.jsx'
import Demande from './Demande.jsx'
import { Bouton, Chiffre } from './Ui.jsx'
import { Puce } from './Trace.jsx'

const PAYS_TEL = [
  { code: '229', nom: 'Bénin', chiffres: 10, exemple: '01 97 00 00 00' },
  { code: '228', nom: 'Togo', chiffres: 8, exemple: '90 00 00 00' },
  { code: '225', nom: "Côte d'Ivoire", chiffres: 10, exemple: '01 00 00 00 00' },
  { code: 'autre', nom: 'Un autre pays', chiffres: 0, exemple: '' },
]

const QUESTIONS = [
  'Quel métier ?',
  'Quelle ville ?',
  'Quel quartier ?',
  'Combien de fiches ?',
  'Quelles informations en plus ?',
  'Vous vendez quoi ?',
]

const CHAMP =
  'mt-2 block min-h-[52px] w-full rounded-2xl border bg-creme px-4 text-encre placeholder:text-sourd/60'

/* --------------------------------------------------------------- le relevé */

function Detail({ c, sombre = false, compact = false }) {
  const sourd = sombre ? 'text-sable' : 'text-sourd'
  const trait = sombre ? 'border-traitsombre' : 'border-trait'
  return (
    <dl className={`space-y-1.5 ${compact ? 'text-[0.86rem]' : 'text-[0.93rem]'}`}>
      {c.lignes.map((l) => (
        <div key={l.cle} className="flex items-baseline justify-between gap-3">
          <dt className={sourd}>
            {l.nom} <span className="opacity-70">{fcfa(l.unite)} × {l.n}</span>
          </dt>
          <dd className="shrink-0 tabular-nums">{fcfa(l.montant)}</dd>
        </div>
      ))}
      <div className={`flex items-baseline justify-between gap-3 border-t ${trait} pt-2`}>
        <dt className={sourd}>Sous-total</dt>
        <dd className="shrink-0 tabular-nums">{fcfa(c.sousTotal)}</dd>
      </div>
      <div className="flex items-baseline justify-between gap-3">
        <dt className={sourd}>
          Remise au volume{c.taux ? ` (${Math.round(c.taux * 100)} %)` : ''}
        </dt>
        <dd className={`shrink-0 tabular-nums ${c.taux ? 'text-vert' : sourd}`}>
          {c.taux ? '- ' + fcfa(c.remise) : 'aucune'}
        </dd>
      </div>
      <div className={`flex items-baseline justify-between gap-3 border-t ${trait} pt-2.5`}>
        <dt className="font-semibold">À payer</dt>
        <dd>
          <Chiffre className={`text-[1.5rem] ${sombre ? 'text-braise' : 'text-brique'}`}>
            {fcfa(c.total)}
          </Chiffre>
        </dd>
      </div>
      <p className={`${sourd} pt-1 text-[0.84rem]`}>
        Soit {fcfa(c.parFiche)} la fiche.
        {c.suivant
          ? ` À ${c.suivant.seuil} fiches, la remise passe à ${Math.round(
              c.suivant.taux * 100
            )} %.`
          : ''}
      </p>
    </dl>
  )
}

/* ----------------------------------------------------------------- l'étape */

function Etape({ n, titre, aide, children }) {
  return (
    <div>
      <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-brique">
        Question {n} sur 6
      </p>
      <h2 className="mt-3 text-[clamp(1.7rem,6.5vw,2.5rem)]">{titre}</h2>
      {aide && <p className="mt-3 max-w-[38rem] text-[0.98rem] leading-relaxed text-sourd">{aide}</p>}
      <div className="mt-7">{children}</div>
    </div>
  )
}

function Carte({ actif, onClick, titre, dessous, droite, desactive, className = '' }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={actif}
      className={`flex w-full min-h-[64px] items-center justify-between gap-4 rounded-2xl border px-4 py-3.5 text-left transition-colors ${
        desactive
          ? `border-dashed bg-papier2/40 text-sourd ${actif ? 'border-brique' : 'border-trait'}`
          : actif
            ? 'border-brique bg-brique/8 text-encre'
            : 'border-trait bg-creme text-encre hover:border-sourd'
      } ${className}`}
    >
      <span>
        <span className="block font-semibold">{titre}</span>
        {dessous && <span className="mt-0.5 block text-[0.85rem] text-sourd">{dessous}</span>}
      </span>
      {droite && <span className="shrink-0 text-right">{droite}</span>}
    </button>
  )
}

function Resume({ metier, metiersListe, ville, quartier, n, options }) {
  const libelleMetier =
    metiersListe && metiersListe.length > 1 ? plurielsListe(metiersListe) : metier?.nom
  const pris = SUPPLEMENTS.filter((s) => options[s.cle])
  const ligne = (t, v) =>
    v ? (
      <div key={t} className="flex items-baseline justify-between gap-3 text-[0.92rem]">
        <span className="text-sourd">{t}</span>
        <span className="text-right font-semibold">{v}</span>
      </div>
    ) : null
  return (
    <div className="space-y-1.5">
      {ligne(metiersListe && metiersListe.length > 1 ? 'Métiers' : 'Métier', libelleMetier)}
      {ligne('Ville', ville?.nom)}
      {ligne('Quartier', quartier?.trim() || null)}
      {ligne('Fiches', n ? jolinombre(n) : null)}
      {ligne('En plus', pris.length ? pris.map((s) => s.nom.toLowerCase()).join(', ') : null)}
      {!metier && (
        <p className="text-[0.92rem] text-sourd">
          Rien de choisi pour l'instant. Répondez à la première question.
        </p>
      )}
    </div>
  )
}

function Entete({ aller, etape }) {
  return (
    <header className="border-b border-trait bg-creme">
      <div className="mx-auto w-full max-w-[68rem] px-5 py-3.5 sm:px-8">
        <div className="flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => aller('#/')}
            className="flex min-h-[44px] items-center gap-2 font-display text-[1rem] font-bold tracking-tight"
          >
            <Puce className="h-4 w-4 text-brique" />
            PISTE <span className="font-normal text-sourd">by NEBULA</span>
          </button>
          <a
            href={`https://wa.me/${NEBULA_WHATSAPP}`}
            target="_blank"
            rel="noopener"
            className="flex min-h-[44px] items-center text-[0.85rem] font-semibold text-sourd underline underline-offset-4 hover:text-brique"
          >
            Aide
          </a>
        </div>
        <ol className="mt-1 flex items-center gap-1.5" aria-label="Avancement">
          {QUESTIONS.map((q, i) => (
            <li key={q} className="flex-1" title={q}>
              <span
                className={`jalon block h-1.5 rounded-full ${
                  i + 1 < etape ? 'bg-brique' : i + 1 === etape ? 'bg-braise' : 'bg-papier2'
                }`}
              />
              <span className="sr-only">
                {q} {i + 1 < etape ? 'terminé' : i + 1 === etape ? 'en cours' : 'à venir'}
              </span>
            </li>
          ))}
        </ol>
      </div>
    </header>
  )
}

/* --------------------------------------------------------------- l'écran - */

export default function Questionnaire({ aller }) {
  const [etape, setEtape] = useState(1)
  const [metier, setMetier] = useState('')
  /* Le générateur peut envoyer PLUSIEURS métiers. Les six étapes de secours de
     cet écran n'en gèrent qu'un : `metier` reste le premier, et `metiersListe`
     porte l'ensemble pour l'affichage et pour le message WhatsApp. Sans ça, un
     client qui commande restaurants + alimentations verrait « Restaurants »
     tout court sur son récapitulatif, et se demanderait ce qu'il a payé. */
  const [metiersListe, setMetiersListe] = useState([])
  const [metierLibre, setMetierLibre] = useState('')
  const [ville, setVille] = useState('')
  const [quartier, setQuartier] = useState('')
  const [n, setN] = useState(MINIMUM)
  const [options, setOptions] = useState({})
  const [offre, setOffre] = useState('')

  const [prenom, setPrenom] = useState('')
  const [nom, setNom] = useState('')
  const [email, setEmail] = useState('')
  const [codePays, setCodePays] = useState('229')
  const [autreCode, setAutreCode] = useState('')
  const [tel, setTel] = useState('')
  /* ⚠️ COMMENT LE CLIENT PAIE, choisi AVANT qu'on lui demande quoi que ce soit.
     Tout ce formulaire avait été écrit sur une seule hypothèse : le client
     paiera à la main, et il faudra reconnaître son versement parmi ceux du
     jour. Trois choses n'existaient que pour ça — le numéro Mobile Money
     OBLIGATOIRE, la consigne d'écrire son nom comme sur son compte, et le
     choix de l'opérateur. Pour qui paie en ligne, les trois sont du bruit, et
     le premier était un mur : un client prêt à payer par carte en dix secondes
     devait d'abord déclarer un numéro dont personne ne se servirait. */
  const [moyen, setMoyen] = useState('ligne')
  const [momoOperateur, setMomoOperateur] = useState('mtn')
  const [momoNumero, setMomoNumero] = useState('')
  const [memeNumero, setMemeNumero] = useState(false)

  /* Ce que le générateur a composé sur la vitrine. On reprend au
     récapitulatif : reposer les six questions à quelqu'un qui vient de tout
     régler, c'est lui faire refaire son travail (décision 54). Si rien n'a été
     composé, l'écran garde ses six étapes et fonctionne seul. */
  const [reprise] = useState(() => {
    try {
      const b = lire('brouillon')[0]
      /* Le générateur envoie une LISTE de métiers depuis le 2026-08-04.
         On accepte les deux formes : l'ancienne clé `metier` reste lue pour
         qu'un brouillon déjà posé dans un navigateur ne se perde pas. */
      const l = b && (b.metiers || (b.metier ? [b.metier] : []))
      if (!b || !l || l.length === 0 || !b.ville) return null
      localStorage.removeItem(CLES.brouillon)
      /* ⚠️ Et l'ancienne clé « undefined », laissée par les navigateurs qui
         ont visité le site avant cette correction : sans ce ménage elle y
         resterait pour toujours. */
      localStorage.removeItem('undefined')
      return b
    } catch (e) {
      return null
    }
  })

  const [essai, setEssai] = useState(false)
  const [commande, setCommande] = useState(null)

  useEffect(() => {
    if (!reprise) return
    const l = reprise.metiers || (reprise.metier ? [reprise.metier] : [])
    setMetiersListe(l)
    setMetier(l[0] || '')
    setVille(reprise.ville)
    setQuartier(reprise.quartier || '')
    setN(reprise.n)
    setOptions(reprise.options || {})
    setOffre(reprise.offre || '')
    setEtape(7)
  }, [reprise])
  /* « Il a configuré » = il a choisi un métier ET une ville. Avant ça, il
     regarde ; après, il compose vraiment une commande. C'est le seul point de
     l'entonnoir qui distingue un passant d'un acheteur potentiel. */
  useEffect(() => {
    if (metier && ville) marquerVisite('configure', { metier, ville, n })
  }, [metier, ville])

  const haut = useRef(null)

  const dispo = useMemo(() => stock(metier, ville), [metier, ville])
  const c = useMemo(() => calcul(n, options), [n, options])
  const objetMetier = METIERS.find((m) => m.cle === metier)
  const objetVille = VILLES.find((v) => v.cle === ville)

  useEffect(() => {
    if (dispo == null) return
    if (dispo >= MINIMUM && n > dispo) setN(dispo)
    if (dispo >= MINIMUM && n < MINIMUM) setN(MINIMUM)
  }, [dispo])

  useEffect(() => {
    haut.current?.scrollIntoView({ block: 'start' })
    if (typeof window !== 'undefined') window.scrollTo(0, 0)
  }, [etape])

  const pays = PAYS_TEL.find((p) => p.code === codePays)
  const telChiffres = tel.replace(/\D/g, '')

  /* ⚠️ DEUX RÈGLES DIFFÉRENTES, ET C'EST VOULU (Mongazi, 2026-08-04).

     Le compte WhatsApp d'un Béninois peut être resté enregistré sous son
     ANCIEN numéro à 8 chiffres, celui d'avant la réforme ARCEP. C'est le cas
     de Mongazi lui-même. Exiger 10 chiffres là, c'est refuser un vrai client
     dont le WhatsApp fonctionne parfaitement.

     Le Mobile Money, lui, porte TOUJOURS le préfixe 01 : dix chiffres, sans
     exception. Un dépôt vers 8 chiffres n'arrive nulle part.

     On accepte donc 8 ou 10 pour le WhatsApp, et on complète le Mobile Money
     au lieu de refuser bêtement quelqu'un qui a tapé son ancien numéro. */
  /* ⚠️ ON N'AJOUTE RIEN AU NUMÉRO DE PAIEMENT. La première version complétait
     un numéro de 8 chiffres en « 01 » + les 8. C'est faux comme principe : le
     préfixe du Bénin peut passer à 02 un jour, et surtout, compléter en silence
     le numéro depuis lequel quelqu'un va envoyer de l'argent, c'est exactement
     la sorte de service rendu qui fait perdre de l'argent à quelqu'un.
     On compte les chiffres, on dit ce qui manque, en rouge, et on le laisse
     corriger lui-même. */
  const momoChiffres = (memeNumero && codePays === '229' ? telChiffres : momoNumero).replace(/\D/g, '')
  const momoManque = codePays === '229' ? 10 - momoChiffres.length : 0

  const emailOk = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(email.trim())
  const telOk =
    codePays === 'autre'
      ? /^\d{1,4}$/.test(autreCode.replace(/\D/g, '')) && telChiffres.length >= 6
      : codePays === '229'
        ? telChiffres.length === 8 || telChiffres.length === 10
        : telChiffres.length === pays.chiffres
  const momoOk = momoChiffres.length === 10
  const nomOk = prenom.trim().length >= 2 && nom.trim().length >= 2

  const peutAvancer = () => {
    if (etape === 1) return !!metier && !objetMetier?.horsStock
    if (etape === 2) return !!ville && dispo >= MINIMUM
    if (etape === 3) return true
    if (etape === 4) return n >= MINIMUM && n <= dispo
    if (etape === 5) return true
    if (etape === 6) return offre.trim().length >= 8
    /* ⚠️ Le numéro Mobile Money n'est exigé QUE pour le dépôt à la main : c'est
       lui, et lui seul, qui sert au rapprochement. */
    if (etape === 7) return nomOk && emailOk && telOk && (moyen === 'main' ? momoOk : true)
    return false
  }

  const suivant = () => {
    if (!peutAvancer()) {
      setEssai(true)
      return
    }
    setEssai(false)
    setEtape((e) => Math.min(7, e + 1))
  }
  const precedent = () => {
    setEssai(false)
    setEtape((e) => Math.max(1, e - 1))
  }

  /* ------------------------------------------------------------ la commande */

  const numeroComplet =
    codePays === 'autre' ? autreCode.replace(/\D/g, '') + telChiffres : codePays + telChiffres

  const texteCommande = (ref) => {
    const pris = SUPPLEMENTS.filter((s) => options[s.cle])
    const ope = MOBILE_MONEY.find((m) => m.cle === momoOperateur)
    /* ⚠️ LES TROIS PREMIERS MOTS DOIVENT TOUT DIRE. WhatsApp montre le debut du
       message dans la liste des conversations : Mongazi doit savoir que c'est
       une commande PISTE, combien de fiches et combien ca rapporte, SANS
       ouvrir la conversation. Un message qui commence par « Bonjour » oblige a
       entrer pour comprendre, et une commande peut attendre des heures. */
    return [
      `PISTE COMMANDE · ${n} fiches · ${fcfa(c.total)}`,
      `Reference ${ref}`,
      '',
      `Métier : ${metiersListe.length > 1 ? plurielsListe(metiersListe) : objetMetier?.nom}`,
      `Ville : ${objetVille?.nom} (${objetVille?.pays})`,
      `Quartier : ${quartier.trim() || 'pas de préférence'}`,
      `Nombre de fiches : ${n}`,
      `Informations en plus : ${
        pris.length ? pris.map((s) => s.nom.toLowerCase()).join(', ') : 'aucune, la fiche de base'
      }`,
      `Ce que je vends : ${offre.trim()}`,
      '',
      'Le calcul',
      ...c.lignes.map((l) => `${l.nom} : ${fcfa(l.unite)} × ${l.n} = ${fcfa(l.montant)}`),
      `Sous-total : ${fcfa(c.sousTotal)}`,
      `Remise au volume : ${
        c.taux ? `- ${fcfa(c.remise)} (${Math.round(c.taux * 100)} %)` : 'aucune'
      }`,
      `À PAYER : ${fcfa(c.total)} (${fcfa(c.parFiche)} la fiche)`,
      '',
      'Qui je suis',
      `Nom et prénom : ${prenom.trim()} ${nom.trim()}`,
      `Email : ${email.trim()}`,
      `WhatsApp : +${numeroComplet}`,
      moyen === 'main'
        ? `Je paierai depuis le +229 ${momoChiffres} (${ope?.operateur})`
        : 'Je paierai EN LIGNE (Mobile Money ou carte)',
      '',
      'Je fais le dépôt et je vous envoie la capture.',
      '',
      'Référence de traitement, à ne pas modifier :',
      'PISTE:' +
        JSON.stringify({
          v: 2,
          ref,
          met: metier,
          vil: ville,
          qua: quartier.trim(),
          n,
          opt: pris.map((s) => s.cle),
          offre: offre.trim(),
          prenom: prenom.trim(),
          nom: nom.trim(),
          email: email.trim(),
          wa: numeroComplet,
          moyen,
          momo: moyen === 'main' ? momoChiffres : '',
          ope: moyen === 'main' ? momoOperateur : '',
          unit: c.unitaire,
          total: c.total,
          date: new Date().toISOString(),
        }),
    ].join('\n')
  }

  const envoyer = () => {
    if (!peutAvancer()) {
      setEssai(true)
      return
    }
    const ref = nouvelleReference()
    const texte = texteCommande(ref)
    const enr = {
      ref,
      date: new Date().toISOString(),
      metier,
      metiers: metiersListe.length ? metiersListe : [metier],
      ville,
      quartier: quartier.trim(),
      n,
      options: SUPPLEMENTS.filter((s) => options[s.cle]).map((s) => s.cle),
      offre: offre.trim(),
      prenom: prenom.trim(),
      nom: nom.trim(),
      email: email.trim(),
      wa: numeroComplet,
      moyen,
      momoNumero: moyen === 'main' ? momoChiffres : '',
      momoOperateur: moyen === 'main' ? momoOperateur : '',
      unitaire: c.unitaire,
      total: c.total,
      etat: 'recue',
    }
    ajouter('commandes', enr)
    /* La commande part AUSSI en base, et pas seulement dans ce navigateur.
       Sans ça, le cockpit ne voyait que les commandes passées depuis l'appareil
       de Mongazi : ce n'était pas une liste, c'était un carnet personnel. Une
       commande passée depuis le téléphone d'un client n'existait nulle part.
       C'est exactement comme ça que le prospect Angélique a été perdu par le
       site de l'agence le 4 août. */
    deposerCommande(
      ref,
      {
        prenom: prenom.trim(),
        nom: nom.trim(),
        email: email.trim(),
        whatsapp: numeroComplet,
        moyen,
        momo: moyen === 'main' ? momoChiffres : '',
        operateur: moyen === 'main' ? momoOperateur : '',
      },
      {
        metier,
        metiers: metiersListe.length ? metiersListe : [metier],
        ville,
        quartier: quartier.trim(),
        n,
        options: enr.options,
        offre: offre.trim(),
        unitaire: c.unitaire,
        total: c.total,
      }
    )
    marquerVisite('commande', { metier, ville, n, total: c.total })
    setCommande({ ...enr, texte })
    window.open(
      `https://wa.me/${NEBULA_WHATSAPP}?text=${encodeURIComponent(texte)}`,
      '_blank',
      'noopener'
    )
  }

  if (commande) return <Paiement commande={commande} aller={aller} />

  const fiche = ficheExemple(metier || 'couture', ville || 'lome')
  const villeIndispo = !!ville && dispo < MINIMUM

  return (
    <div className="min-h-screen bg-papier pb-40 lg:pb-16">
      <Entete aller={aller} etape={etape} />

      <div ref={haut} className="mx-auto w-full max-w-[68rem] px-5 pt-8 sm:px-8 sm:pt-12">
        <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:gap-14">
          <div>
            {/* ---------------------------------------------------- 1. métier */}
            {etape === 1 && (
              <Etape
                n={1}
                titre="Quel métier vous cherchez ?"
                aide="C'est ce qui décide de qui se retrouve dans votre carnet."
              >
                <div className="space-y-2.5">
                  {METIERS.map((m) => (
                    <Carte
                      key={m.cle}
                      actif={metier === m.cle}
                      onClick={() => setMetier(m.cle)}
                      titre={m.nom}
                      dessous={m.exemple}
                    />
                  ))}
                </div>
                {objetMetier?.horsStock && (
                  <Demande
                    metier="autre"
                    ville={ville}
                    metierLibre={metierLibre}
                    onMetierLibre={setMetierLibre}
                  />
                )}
              </Etape>
            )}

            {/* ----------------------------------------------------- 2. ville */}
            {etape === 2 && (
              <Etape
                n={2}
                titre="Dans quelle ville ?"
                aide={`Le nombre disponible s'affiche à droite de chaque ville. Il faut au moins ${MINIMUM} fiches pour commander : en dessous, on prend votre demande au lieu de vous vendre du vide.`}
              >
                <div className="space-y-2.5">
                  {VILLES.map((v) => {
                    const d = stock(metier, v.cle)
                    const assez = d >= MINIMUM
                    return (
                      <Carte
                        key={v.cle}
                        actif={ville === v.cle}
                        onClick={() => setVille(v.cle)}
                        desactive={!assez}
                        titre={v.nom}
                        dessous={
                          assez
                            ? `${v.pays} · ${v.detail}`
                            : `${v.pays} · appuyez pour être prévenu quand ce sera prêt`
                        }
                        droite={
                          assez ? (
                            <>
                              <Chiffre className="text-[1.35rem] text-vert">{d}</Chiffre>
                              <span className="block text-[0.78rem] text-sourd">disponibles</span>
                            </>
                          ) : d > 0 ? (
                            <span className="text-[0.8rem] text-sourd">
                              {d} seulement,
                              <br />
                              sous le minimum
                            </span>
                          ) : (
                            <span className="text-[0.8rem] text-sourd">
                              {v.bientot ? 'bientôt' : 'rien pour ce métier'}
                            </span>
                          )
                        }
                      />
                    )
                  })}
                </div>
                {villeIndispo && (
                  <>
                    <div className="mt-5 rounded-2xl border border-trait bg-papier2/70 p-5 text-[0.94rem] leading-relaxed">
                      <p className="font-semibold">
                        {dispo === 0
                          ? `Rien à ${objetVille?.nom.toLowerCase()} pour ce métier aujourd'hui.`
                          : `Il n'y a que ${dispo} fiche${dispo > 1 ? 's' : ''} ici.`}
                      </p>
                      <p className="mt-1.5 text-sourd">
                        La commande commence à {MINIMUM} fiches. Choisissez une autre ville, ou
                        laissez-nous vous prévenir : c'est exactement comme ça qu'on décide où
                        relever ensuite.
                      </p>
                    </div>
                    <Demande metier={metier} ville={ville} metierLibre="" onMetierLibre={() => {}} compacte />
                  </>
                )}
              </Etape>
            )}

            {/* -------------------------------------------------- 3. quartier */}
            {etape === 3 && (
              <Etape
                n={3}
                titre="Un quartier précis ?"
                aide="Facultatif, et ça ne change pas le prix. On sert d'abord les commerces du quartier demandé, puis on complète avec le reste de la ville."
              >
                <label className="block">
                  <span className="text-[0.85rem] font-semibold text-sourd">Quartier ou zone</span>
                  <input
                    value={quartier}
                    onChange={(e) => setQuartier(e.target.value)}
                    placeholder={
                      ville === 'lome' ? 'Adidogomé, Bè Klikamé, Agoè…' : 'Fidjrossè, Agla, Godomey…'
                    }
                    className={`${CHAMP} border-trait`}
                  />
                </label>
                <p className="mt-3 text-[0.88rem] leading-relaxed text-sourd">
                  Le quartier n'est pas connu pour toutes les fiches : il figure sur celles où
                  l'annuaire l'indiquait. Laissez vide si toute la ville vous va.
                </p>
              </Etape>
            )}

            {/* --------------------------------------------------- 4. combien */}
            {etape === 4 && (
              <Etape
                n={4}
                titre="Combien de fiches ?"
                aide={`Au minimum ${MINIMUM}. Au maximum ${dispo}, parce que c'est tout ce qui existe pour ${objetMetier?.court.toLowerCase()} à ${objetVille?.nom.toLowerCase()}.`}
              >
                <div className="rounded-2xl border border-trait bg-creme p-5">
                  <div className="flex items-end justify-between gap-4">
                    <Chiffre className="text-[3.4rem] leading-none text-encre">{n}</Chiffre>
                    <span className="pb-2 text-[0.9rem] text-sourd">sur {dispo} disponibles</span>
                  </div>
                  <input
                    type="range"
                    min={MINIMUM}
                    max={Math.max(MINIMUM, dispo)}
                    value={n}
                    onChange={(e) => setN(Number(e.target.value))}
                    aria-label="Nombre de fiches"
                    className="mt-3"
                    style={{
                      '--piste-remplie': `linear-gradient(90deg, var(--color-brique) ${
                        ((n - MINIMUM) / Math.max(1, dispo - MINIMUM)) * 100
                      }%, var(--color-papier2) 0)`,
                    }}
                  />
                  <div className="mt-1 flex justify-between text-[0.8rem] text-sourd">
                    <span>{MINIMUM}</span>
                    <span>{dispo}</span>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {[10, 25, 50, dispo]
                      .filter((v, i, a) => v <= dispo && v >= MINIMUM && a.indexOf(v) === i)
                      .map((v) => (
                        <button
                          key={v}
                          type="button"
                          onClick={() => setN(v)}
                          className={`min-h-[44px] rounded-full border px-4 text-[0.88rem] font-semibold transition-colors ${
                            n === v
                              ? 'border-brique bg-brique text-creme'
                              : 'border-trait text-sourd hover:border-sourd'
                          }`}
                        >
                          {v === dispo ? `tout (${v})` : v}
                        </button>
                      ))}
                  </div>
                </div>
                <div className="mt-5 rounded-2xl border border-trait bg-papier2/60 p-5 lg:hidden">
                  <Detail c={c} />
                </div>
              </Etape>
            )}

            {/* ----------------------------------------------- 5. suppléments */}
            {etape === 5 && (
              <Etape
                n={5}
                titre="Quelles informations en plus ?"
                aide={`La fiche de base coûte ${fcfa(BASE)} et contient déjà le nom, le métier, la ville, le quartier et le numéro au bon format. Le reste se coche ici, et le prix bouge sous vos yeux.`}
              >
                <div className="space-y-2.5">
                  {SUPPLEMENTS.map((s) => {
                    const pris = !!options[s.cle]
                    return (
                      <button
                        key={s.cle}
                        type="button"
                        role="switch"
                        aria-checked={pris}
                        onClick={() => setOptions((o) => ({ ...o, [s.cle]: !o[s.cle] }))}
                        className={`flex w-full min-h-[64px] items-start gap-3.5 rounded-2xl border px-4 py-4 text-left transition-colors ${
                          pris ? 'border-brique bg-brique/8' : 'border-trait bg-creme hover:border-sourd'
                        }`}
                      >
                        <span
                          className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md border-2 ${
                            pris ? 'border-brique bg-brique text-creme' : 'border-sourd/50'
                          }`}
                          aria-hidden="true"
                        >
                          {pris && (
                            <svg viewBox="0 0 16 16" className="h-4 w-4">
                              <path
                                d="M3 8.5l3.4 3.4L13 5"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2.4"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              />
                            </svg>
                          )}
                        </span>
                        <span className="flex-1">
                          <span className="flex flex-wrap items-baseline justify-between gap-x-3">
                            <span className="font-semibold">{s.nom}</span>
                            <Chiffre className="text-brique">+ {fcfa(s.prix)} la fiche</Chiffre>
                          </span>
                          <span className="mt-1 block text-[0.88rem] leading-relaxed text-sourd">
                            {s.detail}
                          </span>
                        </span>
                      </button>
                    )
                  })}
                </div>
                <p className="mt-4 text-[0.88rem] leading-relaxed text-sourd">
                  Si l'information n'existe pas pour un commerce, la fiche ne vous est pas livrée :
                  elle est remplacée par une autre qui l'a. Vous ne payez jamais une case vide.
                </p>
                <div className="mt-5 rounded-2xl border border-trait bg-papier2/60 p-5 lg:hidden">
                  <Detail c={c} />
                </div>
              </Etape>
            )}

            {/* -------------------------------------------------- 6. l'offre */}
            {etape === 6 && (
              <Etape
                n={6}
                titre="Vous vendez quoi ?"
                aide="Une phrase suffit. C'est elle qui sert à écrire le message de chaque fiche : sans elle, on ne peut pas écrire à votre place."
              >
                <label className="block">
                  <span className="text-[0.85rem] font-semibold text-sourd">
                    En une phrase, ce que vous proposez à ces commerçants
                  </span>
                  <textarea
                    value={offre}
                    onChange={(e) => setOffre(e.target.value)}
                    rows={4}
                    maxLength={240}
                    placeholder="je propose une assurance santé pensée pour les commerçants et leur famille"
                    className="mt-2 block w-full rounded-2xl border border-trait bg-creme px-4 py-3 leading-relaxed text-encre placeholder:text-sourd/60"
                  />
                </label>
                <div className="mt-1.5 flex justify-between text-[0.82rem] text-sourd">
                  <span>{offre.trim().length < 8 ? 'Au moins quelques mots.' : 'Ça suffit.'}</span>
                  <span>{offre.length}/240</span>
                </div>
                {offre.trim().length >= 8 && (
                  <div className="mt-6">
                    <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-sourd">
                      Voilà le message que ça donne
                    </p>
                    <div className="mt-2 whitespace-pre-line rounded-2xl border border-trait bg-creme px-4 py-3.5 text-[0.93rem] leading-relaxed">
                      {messagePourFiche(fiche, offre)}
                    </div>
                    <p className="mt-2 text-[0.84rem] text-sourd">
                      Réécrit pour chaque commerce du carnet, avec son nom et son métier.
                    </p>
                  </div>
                )}
                {essai && offre.trim().length < 8 && (
                  <p className="mt-4 text-[0.9rem] text-rouge">
                    Écrivez au moins quelques mots : c'est ce qui fabrique vos messages.
                  </p>
                )}
              </Etape>
            )}

            {/* ----------------------------------------------- 7. la commande */}
            {etape === 7 && (
              <div>
                <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-brique">
                  Dernière étape
                </p>
                <h2 className="mt-3 text-[clamp(1.7rem,6.5vw,2.5rem)]">
                  Qui vous êtes, et comment vous payez.
                </h2>
                <p className="mt-3 max-w-[38rem] text-[0.98rem] leading-relaxed text-sourd">
                  Tout est obligatoire, et rien n'est de trop : le carnet part par email et
                  les échanges passent par WhatsApp.
                  {moyen === 'main'
                    ? " C'est votre numéro Mobile Money qui permet de reconnaître votre paiement parmi ceux du jour."
                    : ' Le paiement se fait sur la page suivante.'}
                </p>

                <div className="mt-7 space-y-5">
                  {/* --------------------------------------- comment vous payez */}
                  <div className="rounded-2xl border border-trait bg-papier2/70 p-5">
                    <p className="font-semibold">Comment voulez-vous payer ?</p>
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      {[
                        {
                          cle: 'ligne',
                          titre: 'Payer en ligne',
                          dit: 'Mobile Money ou carte, depuis cette page. Votre paiement nous arrive tout de suite.',
                        },
                        {
                          cle: 'main',
                          titre: 'Dépôt Mobile Money',
                          dit: 'Vous transférez sur notre numéro, et nous rapprochons votre versement à la main.',
                        },
                      ].map((o) => (
                        <button
                          key={o.cle}
                          type="button"
                          onClick={() => setMoyen(o.cle)}
                          aria-pressed={moyen === o.cle}
                          className={`min-h-[44px] rounded-2xl border p-4 text-left transition-colors ${
                            moyen === o.cle
                              ? 'border-brique bg-brique text-creme'
                              : 'border-trait bg-creme text-encre hover:border-sourd'
                          }`}
                        >
                          <span className="block font-semibold">{o.titre}</span>
                          <span
                            className={`mt-1 block text-[0.85rem] leading-relaxed ${
                              moyen === o.cle ? 'text-creme/85' : 'text-sourd'
                            }`}
                          >
                            {o.dit}
                          </span>
                        </button>
                      ))}
                    </div>
                    {moyen === 'ligne' && (
                      <p className="mt-4 text-[0.85rem] leading-relaxed text-sourd">
                        Selon votre pays : MTN, Moov, Celtiis au Bénin · Moov, Mixx, Togocel au
                        Togo · MTN, Moov, Orange, Wave, Djamo en Côte d'Ivoire. Ou une carte
                        bancaire.
                      </p>
                    )}
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <label className="block">
                      <span className="text-[0.85rem] font-semibold text-sourd">Votre prénom</span>
                      <input
                        value={prenom}
                        onChange={(e) => setPrenom(e.target.value)}
                        autoComplete="given-name"
                        aria-invalid={essai && prenom.trim().length < 2}
                        className={`${CHAMP} ${
                          essai && prenom.trim().length < 2 ? 'border-rouge' : 'border-trait'
                        }`}
                      />
                    </label>
                    <label className="block">
                      <span className="text-[0.85rem] font-semibold text-sourd">Votre nom</span>
                      <input
                        value={nom}
                        onChange={(e) => setNom(e.target.value)}
                        autoComplete="family-name"
                        aria-invalid={essai && nom.trim().length < 2}
                        className={`${CHAMP} ${
                          essai && nom.trim().length < 2 ? 'border-rouge' : 'border-trait'
                        }`}
                      />
                    </label>
                  </div>
                  {moyen === 'main' && (
                    <p className="text-[0.85rem] leading-relaxed text-sourd">
                      Écrivez-les comme ils apparaissent sur votre compte Mobile Money : c'est ce
                      nom qui s'affiche à la réception du paiement.
                    </p>
                  )}

                  <label className="block">
                    <span className="text-[0.85rem] font-semibold text-sourd">Votre email</span>
                    <input
                      type="email"
                      inputMode="email"
                      autoComplete="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="vous@exemple.com"
                      aria-invalid={essai && !emailOk}
                      className={`${CHAMP} ${essai && !emailOk ? 'border-rouge' : 'border-trait'}`}
                    />
                    {essai && !emailOk && (
                      <span className="mt-1.5 block text-[0.85rem] text-rouge">
                        Il manque une adresse email valable.
                      </span>
                    )}
                  </label>

                  <div>
                    <span className="text-[0.85rem] font-semibold text-sourd">
                      Votre numéro WhatsApp
                    </span>
                    <div className="mt-2 flex gap-2">
                      <select
                        value={codePays}
                        onChange={(e) => setCodePays(e.target.value)}
                        aria-label="Pays du numéro WhatsApp"
                        className="min-h-[52px] shrink-0 rounded-2xl border border-trait bg-creme px-3 text-encre"
                      >
                        {PAYS_TEL.map((p) => (
                          <option key={p.code} value={p.code}>
                            {p.code === 'autre' ? 'Autre' : '+' + p.code} · {p.nom}
                          </option>
                        ))}
                      </select>
                      {codePays === 'autre' && (
                        <input
                          inputMode="numeric"
                          value={autreCode}
                          onChange={(e) =>
                            setAutreCode(e.target.value.replace(/\D/g, '').slice(0, 4))
                          }
                          placeholder="indicatif"
                          aria-label="Indicatif du pays"
                          className="min-h-[52px] w-24 rounded-2xl border border-trait bg-creme px-3 text-encre placeholder:text-sourd/60"
                        />
                      )}
                      <input
                        inputMode="tel"
                        autoComplete="tel"
                        value={tel}
                        onChange={(e) => setTel(e.target.value)}
                        placeholder={pays.exemple || 'votre numéro'}
                        aria-label="Numéro WhatsApp"
                        aria-invalid={essai && !telOk}
                        className={`min-h-[52px] w-full rounded-2xl border bg-creme px-4 text-encre placeholder:text-sourd/60 ${
                          essai && !telOk ? 'border-rouge' : 'border-trait'
                        }`}
                      />
                    </div>
                    {essai && !telOk && (
                      <span className="mt-1.5 block text-[0.85rem] text-rouge">
                        {codePays === 'autre'
                          ? "Indiquez l'indicatif du pays et le numéro."
                          : codePays === '229'
                            ? 'Un numéro béninois fait 10 chiffres, ou 8 si votre WhatsApp est resté sur votre ancien numéro.'
                            : `Un numéro ${pays.nom} fait ${pays.chiffres} chiffres.`}
                      </span>
                    )}
                  </div>

                  {/* ------------------------------------------- mobile money */}
                  {moyen === 'main' && (
                  <div className="rounded-2xl border border-trait bg-papier2/70 p-5">
                    <p className="font-semibold">Depuis quel numéro allez-vous payer ?</p>
                    <p className="mt-1.5 text-[0.88rem] leading-relaxed text-sourd">
                      À la réception d'un transfert, ce qui s'affiche c'est le numéro et le nom de
                      l'expéditeur, pas votre code de commande. Sans ce numéro, deux commandes du
                      même montant le même jour sont impossibles à distinguer.
                    </p>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {MOBILE_MONEY.map((m) => (
                        <button
                          key={m.cle}
                          type="button"
                          onClick={() => setMomoOperateur(m.cle)}
                          aria-pressed={momoOperateur === m.cle}
                          className={`min-h-[44px] rounded-full border px-4 text-[0.9rem] font-semibold transition-colors ${
                            momoOperateur === m.cle
                              ? 'border-brique bg-brique text-creme'
                              : 'border-trait bg-creme text-sourd hover:border-sourd'
                          }`}
                        >
                          {m.operateur}
                        </button>
                      ))}
                    </div>

                    {codePays === '229' && (
                      <label className="mt-4 flex min-h-[44px] cursor-pointer items-center gap-3 text-[0.92rem]">
                        <input
                          type="checkbox"
                          checked={memeNumero}
                          onChange={(e) => setMemeNumero(e.target.checked)}
                          className="h-5 w-5 accent-[#a8401f]"
                        />
                        Je paierai depuis mon numéro WhatsApp
                      </label>
                    )}

                    {!(memeNumero && codePays === '229') && (
                      <label className="mt-4 block">
                        <span className="text-[0.85rem] font-semibold text-sourd">
                          Numéro Mobile Money, 10 chiffres, Bénin
                        </span>
                        <div className="mt-2 flex gap-2">
                          <span className="flex min-h-[52px] shrink-0 items-center rounded-2xl border border-trait bg-creme px-4 font-semibold text-sourd">
                            +229
                          </span>
                          <input
                            inputMode="tel"
                            value={momoNumero}
                            onChange={(e) => setMomoNumero(e.target.value)}
                            placeholder="01 97 00 00 00"
                            aria-label="Numéro Mobile Money"
                            aria-invalid={essai && !momoOk}
                            className={`min-h-[52px] w-full rounded-2xl border bg-creme px-4 text-encre placeholder:text-sourd/60 ${
                              essai && !momoOk ? 'border-rouge' : 'border-trait'
                            }`}
                          />
                        </div>
                        {essai && !momoOk && (
                          <span className="mt-1.5 block text-[0.85rem] text-rouge">
                            {momoManque > 0
                              ? `Il manque ${momoManque} chiffre${momoManque > 1 ? 's' : ''} : un numéro Mobile Money en fait 10.`
                              : `Il y a ${-momoManque} chiffre${momoManque < -1 ? 's' : ''} de trop : un numéro Mobile Money en fait 10.`}
                          </span>
                        )}
                      </label>
                    )}

                    <p className="mt-4 text-[0.85rem] leading-relaxed text-sourd">
                      Un seul moyen accepté pour le dépôt à la main : MTN MoMo, au Bénin. Si
                      vous payez depuis un autre pays, choisissez « Payer en ligne » plus haut.
                    </p>
                  </div>
                  )}
                </div>

                <div className="mt-8 rounded-2xl border border-trait bg-creme p-5">
                  <p className="font-semibold">Ce qui se passe ensuite</p>
                  <ol className="mt-3 space-y-2.5 text-[0.93rem] leading-relaxed text-sourd">
                    {(moyen === 'ligne'
                      ? [
                          "Votre commande part sur le WhatsApp de NEBULA, déjà rédigée. Vous n'avez qu'à appuyer.",
                          'Sur la page suivante, vous payez en ligne : Mobile Money ou carte.',
                          'Votre paiement nous arrive tout de suite, sans que vous ayez à envoyer une capture.',
                          'Sous 24 heures, le lien privé de votre carnet arrive par email, et vous êtes prévenu sur WhatsApp.',
                        ]
                      : [
                          "Votre commande part sur le WhatsApp de NEBULA, déjà rédigée. Vous n'avez qu'à appuyer.",
                          'Vous recevez le numéro à créditer, vous faites le transfert du montant exact.',
                          'Le paiement est rapproché à la main, puis marqué payé.',
                          'Sous 24 heures, le lien privé de votre carnet arrive par email, et vous êtes prévenu sur WhatsApp.',
                        ]
                    ).map((t, i) => (
                      <li key={i} className="flex gap-3">
                        <Chiffre className="shrink-0 text-brique">{i + 1}</Chiffre>
                        <span>{t}</span>
                      </li>
                    ))}
                  </ol>
                  <p className="mt-4 text-[0.88rem] leading-relaxed text-sourd">
                    {moyen === 'ligne'
                      ? "Le paiement se fait sur la page sécurisée de notre opérateur : nous ne voyons jamais votre code ni votre numéro de carte. Votre commande reste valable 24 heures, ensuite les fiches retournent au stock."
                      : "Aucun paiement ne se fait sur ce site, et rien de ce que vous écrivez ici ne part sur un serveur : tout passe par la conversation WhatsApp. Votre commande reste valable 24 heures, ensuite les fiches retournent au stock."}
                  </p>
                </div>

                <div className="mt-8 lg:hidden">
                  <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-sourd">
                    Votre commande
                  </p>
                  <div className="mt-2 rounded-2xl border border-trait bg-creme p-5">
                    <Resume
                      metier={objetMetier}
                      metiersListe={metiersListe}
                      ville={objetVille}
                      quartier={quartier}
                      n={n}
                      options={options}
                    />
                    <div className="mt-4 border-t border-trait pt-4">
                      <Detail c={c} />
                    </div>
                  </div>
                </div>

                <div className="mt-8">
                  <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-sourd">
                    Une fiche telle que vous allez la recevoir
                  </p>
                  <div className="mt-3 max-w-[30rem]">
                    <FicheExemple fiche={fiche} offre={offre} options={options} />
                  </div>
                </div>

                <Bouton className="mt-8 w-full sm:w-auto" onClick={envoyer}>
                  Envoyer ma commande sur WhatsApp
                </Bouton>
                {essai && !peutAvancer() && (
                  <p className="mt-3 text-[0.9rem] text-rouge">
                    {moyen === 'main'
                      ? 'Il manque votre nom, votre email, votre WhatsApp ou votre numéro Mobile Money.'
                      : 'Il manque votre nom, votre email ou votre WhatsApp.'}
                  </p>
                )}
              </div>
            )}

            {/* --------------------------------------------------- navigation */}
            {etape < 7 && (
              <div className="mt-9 hidden gap-3 lg:flex">
                {etape > 1 && (
                  <Bouton ton="contour" onClick={precedent}>
                    Revenir
                  </Bouton>
                )}
                <Bouton onClick={suivant} disabled={!peutAvancer()}>
                  {etape === 6 ? 'Voir ma commande' : 'Continuer'}
                </Bouton>
              </div>
            )}
            {etape === 7 && (
              <div className="mt-6 hidden lg:flex">
                <Bouton ton="contour" onClick={precedent}>
                  Revenir
                </Bouton>
              </div>
            )}
          </div>

          {/* --------------------------------------------- le relevé, à côté */}
          <aside className="hidden lg:block">
            <div className="sticky top-8 rounded-2xl border border-trait bg-creme p-6">
              <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-sourd">
                Votre commande, en direct
              </p>
              <div className="mt-4">
                <Resume
                  metier={objetMetier}
                  metiersListe={metiersListe}
                  ville={objetVille}
                  quartier={quartier}
                  n={etape >= 4 ? n : null}
                  options={options}
                />
              </div>
              {etape >= 4 ? (
                <div className="mt-5 border-t border-trait pt-5">
                  <Detail c={c} />
                </div>
              ) : (
                <p className="mt-5 border-t border-trait pt-5 text-[0.9rem] leading-relaxed text-sourd">
                  Le calcul apparaît dès que vous aurez dit combien de fiches vous voulez. Il
                  restera affiché, ligne par ligne, jusqu'au bout.
                </p>
              )}
            </div>
          </aside>
        </div>
      </div>

      {/* ------------------------------------------- la barre du téléphone -- */}
      {etape < 7 && (
        <div className="fixed inset-x-0 bottom-0 z-40 border-t border-trait bg-creme px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 lg:hidden">
          {etape >= 4 && (
            <div className="mb-2.5 flex items-baseline justify-between gap-3">
              <span className="text-[0.85rem] text-sourd">
                {n} fiches × {fcfa(c.unitaire)}
                {c.taux ? `, remise ${Math.round(c.taux * 100)} %` : ''}
              </span>
              <Chiffre className="text-[1.35rem] text-brique">{fcfa(c.total)}</Chiffre>
            </div>
          )}
          <div className="flex gap-2.5">
            {etape > 1 && (
              <Bouton ton="contour" onClick={precedent} className="px-5">
                Revenir
              </Bouton>
            )}
            <Bouton onClick={suivant} disabled={!peutAvancer()} className="flex-1">
              {etape === 6 ? 'Voir ma commande' : 'Continuer'}
            </Bouton>
          </div>
        </div>
      )}
    </div>
  )
}
