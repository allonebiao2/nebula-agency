import {
  DATE_RELEVE,
  METIERS,
  estFixe,
  messagePourFiche,
  numeroMasque,
  VILLES,
} from '../donnees.js'
import { SUPPLEMENTS } from '../prix.js'
import { useRevele } from './Revele.jsx'

const INDICATIF = { BJ: '+229', TG: '+228' }

function Croix() {
  return (
    <svg viewBox="0 0 16 16" className="h-4 w-4 shrink-0" aria-hidden="true">
      <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

function Coche() {
  return (
    <svg viewBox="0 0 16 16" className="h-4 w-4 shrink-0" aria-hidden="true">
      <path
        d="M3 8.5l3.4 3.4L13 5"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

/*
  La fiche telle qu'elle arrive dans le carnet, avec un VRAI commerce relevé le
  3 août 2026. Les deux derniers chiffres du numéro sont masqués : la fiche
  entière appartient à qui l'achète, et ce commerce n'a pas demandé à voir son
  numéro affiché en entier sur une page de vente.
*/
export default function FicheExemple({ fiche, options = {}, offre = '', compacte = false }) {
  const ref = useRevele()
  const metier = METIERS.find((m) => m.cle === fiche.metier)
  const ville = VILLES.find((v) => v.cle === fiche.ville)
  const fixe = estFixe(fiche.pays, fiche.numero)
  const lieu = [fiche.quartier, fiche.localite].filter(Boolean).join(' · ')
  const message = messagePourFiche(fiche, offre)

  const etat = (s, pris) => (
    <div
      key={s.cle}
      className={`ligne-relevee flex gap-2.5 rounded-xl border px-3 py-2.5 text-[0.86rem] ${
        pris
          ? 'border-vert/35 bg-vert/8 text-encre'
          : 'border-trait bg-papier2/60 text-sourd'
      }`}
      style={{ '--d': `${240 + SUPPLEMENTS.indexOf(s) * 110}ms` }}
    >
      <span className={pris ? 'mt-0.5 text-vert' : 'mt-0.5 text-sourd'}>
        {pris ? <Coche /> : <Croix />}
      </span>
      <span>
        <b className="font-semibold">{s.nom}</b>
        <span className="block">
          {pris ? s.detail : 'Non pris. Cette ligne reste vide dans votre carnet.'}
        </span>
      </span>
    </div>
  )

  return (
    <div ref={ref} className="revele leve">
      <article className="overflow-hidden rounded-2xl border border-trait bg-creme shadow-[0_18px_50px_-24px_rgb(20_17_14/0.55)]">
        <div className="border-b border-trait bg-papier2/70 px-4 py-2.5 text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-sourd">
          Fiche {fiche.metier === 'patisserie' ? 'pâtisserie' : metier.court.toLowerCase()} ·{' '}
          {ville?.pays}
        </div>

        <div className="px-4 pt-4 pb-3 sm:px-5">
          <h3 className="ligne-relevee text-[1.35rem] leading-tight sm:text-[1.6rem]">
            {fiche.nom}
          </h3>
          <p
            className="ligne-relevee mt-1 text-[0.92rem] text-sourd"
            style={{ '--d': '90ms' }}
          >
            {metier.nom.replace(/s$/, '')} · {lieu || fiche.localite}
          </p>

          <div
            className="ligne-relevee mt-3 flex flex-wrap items-center gap-x-3 gap-y-1.5"
            style={{ '--d': '160ms' }}
          >
            <span className="font-display text-[1.15rem] font-semibold tabular-nums tracking-tight">
              {INDICATIF[fiche.pays]} {numeroMasque(fiche.pays, fiche.numero)}
            </span>
            <span
              className={`rounded-full px-2.5 py-1 text-[0.72rem] font-semibold ${
                fixe ? 'bg-papier2 text-sourd' : 'bg-vert/12 text-vert'
              }`}
            >
              {fixe ? 'ligne fixe : on appelle' : 'WhatsApp'}
            </span>
          </div>
          <p className="mt-1 text-[0.76rem] text-sourd">
            Deux chiffres masqués ici. Le numéro entier part avec votre carnet.
          </p>
        </div>

        {!compacte && (
          <div className="space-y-1.5 px-4 pb-4 sm:px-5">
            {SUPPLEMENTS.map((s) => etat(s, !!options[s.cle]))}
          </div>
        )}

        {options.message && (
          <div className="border-t border-trait bg-papier2/50 px-4 py-4 sm:px-5">
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-sourd">
              Le message, déjà écrit
            </p>
            <div className="mt-2 whitespace-pre-line rounded-xl border border-trait bg-creme px-3.5 py-3 text-[0.9rem] leading-relaxed">
              {message}
            </div>
            <p className="mt-2 text-[0.78rem] text-sourd">
              {options.dirigeant
                ? "Le nom du dirigeant se pose juste après « Bonjour ». PISTE ne l'affiche pas ici : il n'a pas été relevé pour cet exemple, et une donnée inventée n'a rien à faire sur cette page."
                : 'Écrit à partir du métier du commerçant et de la phrase que vous nous donnez.'}
            </p>
          </div>
        )}

        <div className="border-t border-trait px-4 py-3.5 sm:px-5" aria-hidden="true">
          <div className="flex gap-2">
            <span className="flex min-h-[44px] flex-1 items-center justify-center rounded-xl bg-brique px-4 text-[0.9rem] font-semibold text-creme opacity-70">
              {fixe ? 'Appeler' : 'Écrire sur WhatsApp'}
            </span>
            <span className="flex min-h-[44px] items-center justify-center rounded-xl border border-trait px-4 text-[0.9rem] font-semibold text-sourd">
              Appeler
            </span>
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {['Écrit', 'Rendez-vous', 'Vendu', 'Non'].map((e) => (
              <span
                key={e}
                className="rounded-lg border border-trait px-2.5 py-1 text-[0.75rem] font-semibold text-sourd"
              >
                {e}
              </span>
            ))}
          </div>
        </div>
      </article>

      <p className="mt-3 text-[0.8rem] leading-relaxed text-sourd">
        Commerce réel, relevé le {DATE_RELEVE} dans un annuaire professionnel public.
        Sur cette page les boutons ne font rien : ce commerçant n'a pas à recevoir
        des messages d'essai. Dans votre carnet, ils ouvrent WhatsApp et le
        téléphone.
      </p>
    </div>
  )
}
