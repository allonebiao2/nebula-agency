import { useEffect, useMemo, useRef, useState } from 'react'
import {
  METIERS,
  MINIMUM,
  NEBULA_WHATSAPP,
  RESEAUX,
  VILLES,
  ficheExemple,
  stock,
} from '../donnees.js'
import { BASE, SUPPLEMENTS, calcul, fcfa, nombre } from '../prix.js'
import { codeCommande, composerMessage, lienWhatsApp, maCommande } from '../etat.js'
import { Bouton, Chiffre } from './Ui.jsx'
import FicheExemple from './FicheExemple.jsx'

/*
  LE QUESTIONNAIRE — six questions, une par écran sur téléphone.

  Trois règles tenues d'un bout à l'autre :

  1. LE PRIX EST TOUJOURS VISIBLE, et toujours détaillé. Le total ne tombe
     jamais du ciel : on montre la ligne de base, chaque supplément, la
     remise, et le prix par fiche.
  2. ON NE VEND JAMAIS CE QU'ON N'A PAS. Le nombre disponible s'affiche dès
     que le métier et la ville sont choisis, et le curseur est plafonné
     dessus. Zéro disponible : on ne prend pas la commande, on enregistre la
     demande (décision 39).
  3. LE GESTE DU MÉTIER, ici, c'est LE JALON qu'on plante : un repère par
     question franchie.

  ⚠️ La barre de prix est en `position: fixed`. Elle ne doit JAMAIS être
  posée à l'intérieur d'un élément animé par `transform` (`.revele`,
  `.leve`…) : un ancêtre transformé devient le référentiel du `fixed` et la
  barre se met à défiler avec la page. C'est la leçon du FAB de Boussole,
  2026-07-25.
*/

const QUESTIONS = [
  { cle: 'metier', titre: 'Quel métier cherchez-vous ?', sous: 'Le vivier qu\'on va interroger.' },
  { cle: 'ville', titre: 'Dans quelle ville ?', sous: 'Le nombre disponible s\'affiche tout de suite.' },
  { cle: 'quartier', titre: 'Un quartier en particulier ?', sous: 'Facultatif. Ça affine, ça ne change pas le prix.' },
  { cle: 'nombre', titre: 'Combien de fiches ?', sous: `Minimum ${MINIMUM}, plafonné à ce qui existe vraiment.` },
  { cle: 'options', titre: 'Quelles informations en plus ?', sous: 'C\'est ce qui fait monter le prix, et c\'est vous qui choisissez.' },
  { cle: 'offre', titre: 'Vous vendez quoi ?', sous: 'Une phrase suffit. C\'est elle qui écrit le message de chaque fiche.' },
  { cle: 'vous', titre: 'Où on vous envoie tout ça ?', sous: 'Le lien part par email, et on vous prévient sur WhatsApp.' },
]

const VIDE = {
  metier: '',
  metierLibre: '',
  ville: '',
  quartier: '',
  nombre: 20,
  options: { teste: true, message: true },
  offre: '',
  nom: '',
  email: '',
  whatsapp: '',
  momo: '',
  reseau: RESEAUX[0],
}

export default function Questionnaire({ onEnvoyee }) {
  const [etape, setEtape] = useState(0)
  const [c, setC] = useState(VIDE)
  const [touche, setTouche] = useState(false)
  const haut = useRef(null)

  const dispo = stock(c.metier, c.ville)
  const horsStock =
    METIERS.find((m) => m.cle === c.metier)?.horsStock ||
    VILLES.find((v) => v.cle === c.ville)?.bientot ||
    (dispo !== null && dispo < MINIMUM)

  const maxi = dispo && dispo >= MINIMUM ? dispo : 500
  const p = useMemo(() => calcul(Math.min(c.nombre, maxi), c.options), [c.nombre, c.options, maxi])

  const maj = (champs) => setC((v) => ({ ...v, ...champs }))

  /* Le curseur ne doit jamais dépasser ce qui existe. */
  useEffect(() => {
    if (dispo && dispo >= MINIMUM && c.nombre > dispo) maj({ nombre: dispo })
  }, [dispo])

  const valide = (i) => {
    switch (i) {
      case 0:
        return !!c.metier && (c.metier !== 'autre' || c.metierLibre.trim().length > 1)
      case 1:
        return !!c.ville
      case 2:
        return true
      case 3:
        return p.n >= MINIMUM
      case 4:
        return true
      case 5:
        return c.offre.trim().length >= 8
      case 6:
        return (
          c.nom.trim().length >= 2 &&
          /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(c.email.trim()) &&
          c.whatsapp.replace(/\D/g, '').length >= 8 &&
          c.momo.replace(/\D/g, '').length >= 8
        )
      default:
        return true
    }
  }

  const avancer = () => {
    if (!valide(etape)) {
      setTouche(true)
      return
    }
    setTouche(false)
    if (etape < QUESTIONS.length - 1) {
      setEtape(etape + 1)
      haut.current?.scrollIntoView({ block: 'start', behavior: 'smooth' })
    } else {
      envoyer()
    }
  }

  const reculer = () => {
    setTouche(false)
    setEtape(Math.max(0, etape - 1))
    haut.current?.scrollIntoView({ block: 'start', behavior: 'smooth' })
  }

  const envoyer = () => {
    const commande = {
      ...c,
      nombre: p.n,
      total: p.total,
      unitaire: p.unitaire,
      code: codeCommande(),
      cree: Date.now(),
    }
    maCommande.poser(commande)
    onEnvoyee(commande)
  }

  const q = QUESTIONS[etape]

  return (
    <div className="bg-papier pb-40 sm:pb-32">
      <div ref={haut} className="scroll-mt-20" />

      {/* les jalons : un repère planté par question franchie */}
      <div className="mx-auto w-full max-w-[52rem] px-5 pt-8 sm:px-8">
        <ol className="flex items-center gap-1.5" aria-label={`Question ${etape + 1} sur ${QUESTIONS.length}`}>
          {QUESTIONS.map((x, i) => (
            <li key={x.cle} className="flex-1">
              <span
                className={`jalon block h-1.5 rounded-full ${
                  i < etape ? 'bg-brique' : i === etape ? 'bg-braise' : 'bg-papier2'
                }`}
                style={{ transform: i === etape ? 'scaleY(1.6)' : 'none' }}
              />
            </li>
          ))}
        </ol>
        <p className="mt-3 text-[0.78rem] font-semibold uppercase tracking-[0.18em] text-sourd">
          Question {etape + 1} sur {QUESTIONS.length}
        </p>
      </div>

      <div className="mx-auto grid w-full max-w-[52rem] gap-8 px-5 py-8 sm:px-8 lg:max-w-[68rem] lg:grid-cols-[1.25fr_0.75fr] lg:gap-12">
        <div>
          <h1 className="text-[clamp(1.8rem,6.4vw,2.9rem)]">{q.titre}</h1>
          <p className="mt-2.5 text-[0.98rem] text-sourd">{q.sous}</p>

          <div className="mt-8">
            {etape === 0 && <EtapeMetier c={c} maj={maj} touche={touche} />}
            {etape === 1 && <EtapeVille c={c} maj={maj} />}
            {etape === 2 && <EtapeQuartier c={c} maj={maj} />}
            {etape === 3 && (
              <EtapeNombre c={c} maj={maj} p={p} dispo={dispo} horsStock={horsStock} maxi={maxi} />
            )}
            {etape === 4 && <EtapeOptions c={c} maj={maj} />}
            {etape === 5 && <EtapeOffre c={c} maj={maj} touche={touche} />}
            {etape === 6 && <EtapeVous c={c} maj={maj} touche={touche} p={p} />}
          </div>

          {touche && !valide(etape) && (
            <p className="mt-5 rounded-xl border border-rouge/30 bg-rouge/8 px-4 py-3 text-[0.9rem] text-rouge" role="alert">
              {messageErreur(etape, c, p)}
            </p>
          )}

          <div className="mt-9 flex flex-wrap gap-3">
            {etape > 0 && (
              <Bouton ton="contour" onClick={reculer}>
                Retour
              </Bouton>
            )}
            <Bouton onClick={avancer} disabled={etape === 3 && horsStock}>
              {etape === QUESTIONS.length - 1 ? 'Voir comment payer' : 'Continuer'}
            </Bouton>
          </div>

          {horsStock && etape >= 1 && <DemandeVivier c={c} />}
        </div>

        {/* le détail du calcul, toujours à l'écran sur grand écran */}
        <aside className="hidden lg:block">
          <div className="sticky top-24 space-y-4">
            <Addition p={p} c={c} dispo={dispo} />
            {etape >= 4 && (
              <FicheExemple
                fiche={ficheExemple(c.metier, c.ville)}
                options={c.options}
                offre={c.offre}
                compacte={etape < 5}
              />
            )}
          </div>
        </aside>
      </div>

      {/* la barre de prix du téléphone — hors de tout élément transformé */}
      <BarrePrix p={p} etape={etape} total={QUESTIONS.length} />
    </div>
  )
}

function messageErreur(etape, c, p) {
  switch (etape) {
    case 0:
      return c.metier === 'autre'
        ? 'Écrivez le métier que vous cherchez, même approximativement.'
        : 'Choisissez un métier pour continuer.'
    case 1:
      return 'Choisissez une ville pour continuer.'
    case 3:
      return `Il faut au moins ${MINIMUM} fiches pour que ça vaille le coup : en dessous, il n'y a pas assez de monde à qui parler.`
    case 5:
      return 'Une phrase, même courte : sans elle on ne peut pas écrire le message à votre place.'
    case 6:
      return 'Il manque quelque chose : le nom, un email valable, votre WhatsApp, et le numéro depuis lequel vous paierez.'
    default:
      return 'Il manque quelque chose sur cet écran.'
  }
}

/* ------------------------------------------------------------ 1. métier -- */

function EtapeMetier({ c, maj, touche }) {
  return (
    <div className="space-y-3">
      {METIERS.map((m) => (
        <Choix
          key={m.cle}
          actif={c.metier === m.cle}
          onClick={() => maj({ metier: m.cle })}
          titre={m.nom}
          sous={m.exemple}
        />
      ))}
      {c.metier === 'autre' && (
        <div className="rounded-2xl border border-trait bg-creme p-4">
          <label className="block text-[0.88rem] font-semibold" htmlFor="metierLibre">
            Quel métier, précisément ?
          </label>
          <input
            id="metierLibre"
            className={champ(touche && c.metierLibre.trim().length < 2)}
            placeholder="pharmacies, garages, écoles privées…"
            value={c.metierLibre}
            onChange={(e) => maj({ metierLibre: e.target.value })}
          />
          <p className="mt-2 text-[0.84rem] leading-relaxed text-sourd">
            Ce vivier n'existe pas encore. On enregistre votre demande et on vous
            prévient dès qu'il est relevé, et ça nous dit où aller travailler en
            priorité.
          </p>
        </div>
      )}
    </div>
  )
}

/* ------------------------------------------------------------- 2. ville -- */

function EtapeVille({ c, maj }) {
  return (
    <div className="space-y-3">
      {VILLES.map((v) => {
        const n = c.metier ? stock(c.metier, v.cle) : null
        const rien = v.bientot || n === 0
        return (
          <Choix
            key={v.cle}
            actif={c.ville === v.cle}
            onClick={() => maj({ ville: v.cle })}
            titre={v.nom}
            sous={v.detail}
            marque={
              c.metier && !c.metier.startsWith('autre') ? (
                <span
                  className={`whitespace-nowrap rounded-full px-3 py-1 text-[0.8rem] font-semibold ${
                    rien ? 'bg-papier2 text-sourd' : n < MINIMUM ? 'bg-rouge/10 text-rouge' : 'bg-vert/12 text-vert'
                  }`}
                >
                  {rien ? 'bientôt' : `${n} en stock`}
                </span>
              ) : null
            }
          />
        )
      })}
      <p className="text-[0.86rem] leading-relaxed text-sourd">
        Le nombre affiché est celui d'aujourd'hui, et il baisse quand quelqu'un
        achète : une fiche vendue sort du stock 90 jours. On ne vend jamais ce
        qui n'existe pas.
      </p>
    </div>
  )
}

/* ---------------------------------------------------------- 3. quartier -- */

function EtapeQuartier({ c, maj }) {
  const ville = VILLES.find((v) => v.cle === c.ville)
  return (
    <div>
      <label className="block text-[0.88rem] font-semibold" htmlFor="quartier">
        Quartier ou repère (facultatif)
      </label>
      <input
        id="quartier"
        className={champ(false)}
        placeholder={ville?.cle === 'lome' ? 'Bè, Agoè, Hédzranawoé…' : 'Akpakpa, Cadjèhoun, Fidjrossè…'}
        value={c.quartier}
        onChange={(e) => maj({ quartier: e.target.value })}
      />
      <p className="mt-3 text-[0.9rem] leading-relaxed text-sourd">
        On sert d'abord les commerces de ce quartier, puis on complète avec le
        reste de la ville s'il n'y en a pas assez. Chaque fiche porte son
        quartier, vous verrez donc exactement d'où elle vient.
      </p>
      <p className="mt-3 text-[0.9rem] leading-relaxed text-sourd">
        Laissez vide si vous voulez toute la ville : c'est le choix qui donne le
        plus de monde à qui parler.
      </p>
    </div>
  )
}

/* ------------------------------------------------------------ 4. nombre -- */

function EtapeNombre({ c, maj, p, dispo, horsStock, maxi }) {
  const rempli = Math.round(((c.nombre - MINIMUM) / Math.max(1, maxi - MINIMUM)) * 100)
  if (horsStock) {
    return (
      <div className="rounded-2xl border border-trait bg-creme p-5">
        <h2 className="text-[1.2rem]">Il n'y a pas encore assez de monde ici.</h2>
        <p className="mt-2 text-[0.93rem] leading-relaxed text-sourd">
          {dispo === 0 || dispo === null
            ? 'Ce vivier n\'a pas encore été relevé.'
            : `Il n'y a que ${dispo} fiche${dispo > 1 ? 's' : ''} disponible${dispo > 1 ? 's' : ''}, et le minimum est de ${MINIMUM}.`}{' '}
          On préfère vous le dire plutôt que de vous vendre une liste creuse.
        </p>
        <p className="mt-3 text-[0.93rem] leading-relaxed text-sourd">
          Laissez-nous votre demande juste en dessous : on vous prévient dès que
          c'est prêt, et vous serez servi le premier.
        </p>
      </div>
    )
  }
  return (
    <div>
      <div className="flex items-end justify-between gap-4">
        <p className="flex items-baseline gap-2">
          <Chiffre className="text-[3.4rem] leading-none text-brique">{nombre(p.n)}</Chiffre>
          <span className="text-[1.1rem] text-sourd">fiches</span>
        </p>
        <p className="text-right text-[0.86rem] text-sourd">
          {dispo} disponibles
          <br />
          aujourd'hui
        </p>
      </div>

      <input
        type="range"
        className="mt-4"
        min={MINIMUM}
        max={maxi}
        step={1}
        value={Math.min(c.nombre, maxi)}
        aria-label="Nombre de fiches"
        style={{
          '--piste-remplie': `linear-gradient(90deg, var(--color-brique) ${rempli}%, var(--color-papier2) ${rempli}%)`,
        }}
        onChange={(e) => maj({ nombre: parseInt(e.target.value, 10) })}
      />

      <div className="flex justify-between text-[0.82rem] text-sourd">
        <span>{MINIMUM} minimum</span>
        <span>{maxi} maximum</span>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {[10, 25, 50, 100, 200].filter((n) => n <= maxi).map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => maj({ nombre: n })}
            className={`min-h-[44px] rounded-full border px-4 text-[0.9rem] font-semibold ${
              p.n === n ? 'border-brique bg-brique text-creme' : 'border-trait bg-creme text-encre'
            }`}
          >
            {n}
          </button>
        ))}
      </div>

      {p.suivant && (
        <p className="mt-5 rounded-xl border border-trait bg-papier2/60 px-4 py-3 text-[0.9rem] leading-relaxed">
          Encore <b>{p.suivant.seuil - p.n} fiches</b> et la remise passe à{' '}
          <b className="text-brique">−{Math.round(p.suivant.taux * 100)} %</b>.
          {p.suivant.seuil > maxi && ' (il faudrait plus de stock que ce qui existe ici aujourd\'hui)'}
        </p>
      )}
    </div>
  )
}

/* ----------------------------------------------------------- 5. options -- */

function EtapeOptions({ c, maj }) {
  const bascule = (cle) => maj({ options: { ...c.options, [cle]: !c.options[cle] } })
  return (
    <div className="space-y-3">
      {SUPPLEMENTS.map((s) => {
        const pris = !!c.options[s.cle]
        return (
          <button
            key={s.cle}
            type="button"
            onClick={() => bascule(s.cle)}
            aria-pressed={pris}
            className={`flex w-full items-start gap-3.5 rounded-2xl border p-4 text-left transition-colors duration-200 ${
              pris ? 'border-brique bg-creme' : 'border-trait bg-papier2/40'
            }`}
          >
            <span
              className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md border-2 ${
                pris ? 'border-brique bg-brique text-creme' : 'border-trait bg-creme'
              }`}
              aria-hidden="true"
            >
              {pris && (
                <svg viewBox="0 0 16 16" className="h-3.5 w-3.5">
                  <path d="M3 8.5l3.4 3.4L13 5" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </span>
            <span className="flex-1">
              <span className="flex flex-wrap items-baseline justify-between gap-x-3">
                <b className="text-[1.02rem] font-semibold">{s.nom}</b>
                <Chiffre className={pris ? 'text-brique' : 'text-sourd'}>+ {nombre(s.prix)} F</Chiffre>
              </span>
              <span className="mt-1 block text-[0.89rem] leading-relaxed text-sourd">{s.detail}</span>
            </span>
          </button>
        )
      })}
      <p className="text-[0.86rem] leading-relaxed text-sourd">
        Une information promise mais introuvable ? On ne vous livre pas la fiche :
        on la remplace par une autre qui l'a. Vous ne payez jamais un supplément
        qui reste vide.
      </p>
    </div>
  )
}

/* ------------------------------------------------------------- 6. offre -- */

function EtapeOffre({ c, maj, touche }) {
  return (
    <div>
      <label className="block text-[0.88rem] font-semibold" htmlFor="offre">
        En une phrase, qu'est-ce que vous proposez à ces commerçants ?
      </label>
      <textarea
        id="offre"
        rows={3}
        className={champ(touche && c.offre.trim().length < 8) + ' resize-y'}
        placeholder="je propose une assurance santé aux commerçants et à leurs employés"
        value={c.offre}
        onChange={(e) => maj({ offre: e.target.value })}
      />
      <p className="mt-3 text-[0.9rem] leading-relaxed text-sourd">
        C'est la question que personne ne pense à poser, et c'est elle qui sépare
        une liste d'un outil de travail : sans elle, impossible d'écrire le
        message à votre place.
      </p>
      {c.offre.trim().length >= 8 && (
        <div className="mt-6 lg:hidden">
          <p className="mb-3 text-[0.78rem] font-semibold uppercase tracking-[0.16em] text-sourd">
            Voilà ce que ça donne
          </p>
          <FicheExemple
            fiche={ficheExemple(c.metier, c.ville)}
            options={{ ...c.options, message: true }}
            offre={c.offre}
          />
        </div>
      )}
    </div>
  )
}

/* -------------------------------------------------------------- 7. vous -- */

function EtapeVous({ c, maj, touche, p }) {
  const mauvaisMail = touche && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(c.email.trim())
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-[0.88rem] font-semibold" htmlFor="nom">
          Votre nom et prénom
        </label>
        <input
          id="nom"
          className={champ(touche && c.nom.trim().length < 2)}
          placeholder="tel qu'il apparaît sur votre compte Mobile Money"
          autoComplete="name"
          value={c.nom}
          onChange={(e) => maj({ nom: e.target.value })}
        />
      </div>

      <div>
        <label className="block text-[0.88rem] font-semibold" htmlFor="email">
          Votre email <span className="font-normal text-sourd">· c'est là qu'arrive le carnet</span>
        </label>
        <input
          id="email"
          type="email"
          inputMode="email"
          autoComplete="email"
          className={champ(mauvaisMail)}
          placeholder="vous@exemple.com"
          value={c.email}
          onChange={(e) => maj({ email: e.target.value })}
        />
      </div>

      <div>
        <label className="block text-[0.88rem] font-semibold" htmlFor="whatsapp">
          Votre WhatsApp <span className="font-normal text-sourd">· on vous prévient aussi là</span>
        </label>
        <input
          id="whatsapp"
          type="tel"
          inputMode="tel"
          autoComplete="tel"
          className={champ(touche && c.whatsapp.replace(/\D/g, '').length < 8)}
          placeholder="+229 01 XX XX XX XX"
          value={c.whatsapp}
          onChange={(e) => maj({ whatsapp: e.target.value })}
        />
      </div>

      <div className="rounded-2xl border border-trait bg-papier2/50 p-4">
        <label className="block text-[0.88rem] font-semibold" htmlFor="momo">
          Le numéro depuis lequel vous paierez
        </label>
        <input
          id="momo"
          type="tel"
          inputMode="tel"
          className={champ(touche && c.momo.replace(/\D/g, '').length < 8)}
          placeholder="le numéro Mobile Money qui enverra l'argent"
          value={c.momo}
          onChange={(e) => maj({ momo: e.target.value })}
        />
        <div className="mt-3 flex flex-wrap gap-2">
          {RESEAUX.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => maj({ reseau: r })}
              aria-pressed={c.reseau === r}
              className={`min-h-[44px] rounded-full border px-4 text-[0.9rem] font-semibold ${
                c.reseau === r ? 'border-brique bg-brique text-creme' : 'border-trait bg-creme'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
        <p className="mt-3 text-[0.85rem] leading-relaxed text-sourd">
          <b className="font-semibold text-encre">Pourquoi ce numéro est obligatoire.</b>{' '}
          Sur l'application Mobile Money, ce qui s'affiche à la réception c'est le
          numéro et le nom de l'expéditeur, jamais un code de commande. Sans lui,
          deux paiements du même montant le même jour sont impossibles à
          distinguer, et c'est votre carnet qui attend.
        </p>
      </div>

      <p className="text-[0.85rem] leading-relaxed text-sourd">
        Aucun compte à créer, aucun mot de passe. Vos coordonnées servent à vous
        livrer et à vous répondre : nous ne les revendons pas, et elles ne
        rentrent jamais dans le stock de PISTE.
      </p>

      <div className="rounded-2xl border border-trait bg-creme p-4">
        <p className="flex flex-wrap items-baseline justify-between gap-2">
          <span className="font-semibold">Total à payer</span>
          <Chiffre className="text-[1.7rem] text-brique">{fcfa(p.total)}</Chiffre>
        </p>
        <p className="mt-1 text-[0.86rem] text-sourd">
          {p.n} fiches à {fcfa(p.unitaire)}
          {p.taux ? `, remise ${Math.round(p.taux * 100)} % déduite` : ''}. Vous ne
          payez rien sur ce site : les instructions arrivent à l'écran suivant.
        </p>
      </div>
    </div>
  )
}

/* ------------------------------------------------------------- addition -- */

function Addition({ p, c, dispo }) {
  const metier = METIERS.find((m) => m.cle === c.metier)
  const ville = VILLES.find((v) => v.cle === c.ville)
  return (
    <div className="rounded-2xl border border-trait bg-creme p-5">
      <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-sourd">
        Le calcul, en entier
      </p>

      {(metier || ville) && (
        <p className="mt-2 text-[0.88rem] text-sourd">
          {c.metierLibre?.trim() || metier?.court || '…'}
          {ville ? ` · ${ville.nom}` : ''}
          {dispo ? ` · ${dispo} en stock` : ''}
        </p>
      )}

      <dl className="mt-4 space-y-2 text-[0.9rem]">
        {p.lignes.map((l) => (
          <div key={l.cle} className="flex items-baseline justify-between gap-3 border-b border-trait/70 pb-2">
            <dt className="text-sourd">
              {l.nom}
              <span className="block text-[0.8rem]">
                {nombre(l.unite)} F × {p.n}
              </span>
            </dt>
            <dd className="tabular-nums font-semibold">{fcfa(l.montant)}</dd>
          </div>
        ))}
        {p.taux > 0 && (
          <div className="flex items-baseline justify-between gap-3 border-b border-trait/70 pb-2 text-vert">
            <dt>Remise {Math.round(p.taux * 100)} % ({p.n} fiches)</dt>
            <dd className="tabular-nums font-semibold">− {fcfa(p.remise)}</dd>
          </div>
        )}
      </dl>

      <div className="mt-4 flex items-baseline justify-between gap-3">
        <span className="font-semibold">Total</span>
        <Chiffre className="text-[1.8rem] text-brique">{fcfa(p.total)}</Chiffre>
      </div>
      <p className="mt-1 text-right text-[0.82rem] text-sourd">
        soit {fcfa(p.parFiche)} la fiche
      </p>
    </div>
  )
}

/* --------------------------------------------------- la barre du pouce --- */

function BarrePrix({ p, etape, total }) {
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-trait bg-creme/97 px-5 py-3 shadow-[0_-8px_30px_-18px_rgb(20_17_14/0.5)] lg:hidden">
      <div className="mx-auto flex max-w-[52rem] items-center justify-between gap-4">
        <div>
          <p className="text-[0.74rem] font-semibold uppercase tracking-[0.14em] text-sourd">
            {p.n} fiches · {fcfa(p.unitaire)} l'unité
          </p>
          <p className="flex items-baseline gap-2">
            <Chiffre className="text-[1.55rem] text-brique">{fcfa(p.total)}</Chiffre>
            {p.taux > 0 && (
              <span className="text-[0.78rem] font-semibold text-vert">
                −{Math.round(p.taux * 100)} %
              </span>
            )}
          </p>
        </div>
        <p className="text-right text-[0.76rem] text-sourd">
          question
          <br />
          {etape + 1} / {total}
        </p>
      </div>
    </div>
  )
}

/* ------------------------------------------- décision 39 : la demande ---- */

function DemandeVivier({ c }) {
  const metier = c.metierLibre?.trim() || METIERS.find((m) => m.cle === c.metier)?.nom || '?'
  const ville = VILLES.find((v) => v.cle === c.ville)?.nom || '?'
  const texte = [
    'PISTE · demande de vivier',
    '',
    `· Métier : ${metier}`,
    `· Ville : ${ville}`,
    '',
    "Prévenez-moi dès que ce vivier est prêt.",
  ].join('\n')
  return (
    <div className="mt-8 rounded-2xl border border-brique/30 bg-papier2/60 p-5">
      <h2 className="text-[1.15rem]">Dites-nous quand même ce que vous cherchez.</h2>
      <p className="mt-2 text-[0.92rem] leading-relaxed text-sourd">
        Chaque demande nous dit où aller relever en premier. Vous serez prévenu dès
        que <b className="text-encre">{metier}</b> à <b className="text-encre">{ville}</b>{' '}
        est prêt, et servi avant tout le monde.
      </p>
      <Bouton className="mt-4" href={lienWhatsApp(texte, NEBULA_WHATSAPP)} target="_blank" rel="noopener">
        Enregistrer ma demande
      </Bouton>
    </div>
  )
}

/* ------------------------------------------------------------- outillage - */

function Choix({ actif, onClick, titre, sous, marque }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={actif}
      className={`flex w-full items-center gap-3.5 rounded-2xl border p-4 text-left transition-colors duration-200 ${
        actif ? 'border-brique bg-creme' : 'border-trait bg-papier2/40'
      }`}
    >
      <span
        className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 ${
          actif ? 'border-brique' : 'border-trait'
        }`}
        aria-hidden="true"
      >
        {actif && <span className="h-3 w-3 rounded-full bg-brique" />}
      </span>
      <span className="flex-1">
        <b className="text-[1.02rem] font-semibold">{titre}</b>
        <span className="mt-0.5 block text-[0.88rem] leading-snug text-sourd">{sous}</span>
      </span>
      {marque}
    </button>
  )
}

function champ(erreur) {
  return `mt-2 min-h-[48px] w-full rounded-xl border bg-creme px-4 py-3 outline-none ${
    erreur ? 'border-rouge' : 'border-trait focus:border-brique'
  }`
}
