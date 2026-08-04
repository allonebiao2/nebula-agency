import { useEffect, useState } from 'react'
import {
  DATE_RELEVE,
  EMAIL_ENVOI,
  METIERS,
  MINIMUM,
  NEBULA_WHATSAPP,
  NEBULA_WHATSAPP_JOLI,
  NOMBRE_FIXES,
  REPARTITION,
  STOCK,
  TOTAL_FICHES,
  VILLES,
  ficheExemple,
} from '../donnees.js'
import { BASE, SUPPLEMENTS, PALIERS, calcul, fcfa } from '../prix.js'
import FicheExemple from './FicheExemple.jsx'
import { Compteur, Revele, useRevele } from './Revele.jsx'
import { Bouton, Chiffre, Section, Titre } from './Ui.jsx'
import { Puce, Semis, TracePiste } from './Trace.jsx'

const OFFRE_EXEMPLE =
  'je propose une assurance santé pensée pour les commerçants et leur famille'

/* ------------------------------------------------------------------ héros - */

function Heros({ aller }) {
  return (
    <Section fond="encre" grain interieur="pt-7 pb-16 sm:pt-9 sm:pb-24">
      <div className="flex items-center justify-between gap-4">
        <p className="font-display text-[1.05rem] font-bold tracking-tight">
          PISTE{' '}
          <span className="font-normal text-sable">by NEBULA</span>
        </p>
        <a
          href={`https://wa.me/${NEBULA_WHATSAPP}`}
          target="_blank"
          rel="noopener"
          className="flex min-h-[44px] items-center text-[0.85rem] font-semibold text-sable underline underline-offset-4 hover:text-braise"
        >
          Nous écrire
        </a>
      </div>

      <div className="mt-10 grid gap-10 sm:mt-14 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-8">
        <div>
          <Revele>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-braise">
              Bénin · Togo
            </p>
          </Revele>
          <Revele d={80}>
            <h1 className="mt-4 text-[clamp(2.6rem,10.4vw,4.35rem)]">
              Des commerçants
              <br />à qui parler
              <br />
              <span className="text-braise">demain matin.</span>
            </h1>
          </Revele>
          <Revele d={180}>
            <p className="mt-6 max-w-[34rem] text-[1.05rem] leading-relaxed text-sable sm:text-[1.15rem]">
              Vous dites qui vous cherchez. On vous rend un carnet de commerces
              réels : le nom, le quartier, le numéro au bon format, et le message
              déjà écrit pour chacun. Vous ouvrez sur votre téléphone, vous
              appuyez, la conversation démarre.
            </p>
          </Revele>
          <Revele d={260} className="mt-8 flex flex-wrap gap-3">
            <Bouton ton="pleinClair" onClick={() => aller('#/commander')}>
              Composer ma commande
            </Bouton>
            <Bouton ton="contourSombre" href="#fiche">
              Voir une vraie fiche
            </Bouton>
          </Revele>
          <Revele d={340}>
            <ul className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-[0.88rem] text-sable">
              {[
                `Minimum ${MINIMUM} fiches`,
                `À partir de ${fcfa(BASE)} la fiche`,
                'Livré sous 24 heures',
              ].map((x) => (
                <li key={x} className="flex items-center gap-2">
                  <Puce className="h-4 w-4 text-braise" />
                  {x}
                </li>
              ))}
            </ul>
          </Revele>
        </div>

        <div className="text-braise">
          <TracePiste repere={5} />
          <p className="mt-1 text-center text-[0.8rem] text-sable">
            On relève la trace, on la suit, on arrive à la porte.
          </p>
        </div>
      </div>
    </Section>
  )
}

/* ------------------------------------------------------------------ ruban - */

function Ruban() {
  const mots = [
    `${TOTAL_FICHES} commerces relevés le ${DATE_RELEVE}`,
    'Bénin et Togo',
    'toute fiche injoignable est remplacée',
    '90 jours pour vous seul',
    'livré sous 24 heures',
  ]
  return (
    <div className="overflow-hidden bg-brique py-3 text-creme select-none" aria-hidden="true">
      <div className="ruban">
        {[0, 1].map((k) => (
          <div key={k} className="flex shrink-0 items-center">
            {mots.map((m) => (
              <span
                key={m}
                className="flex items-center gap-4 whitespace-nowrap px-4 text-[0.82rem] font-semibold uppercase tracking-[0.14em]"
              >
                {m}
                <span className="text-creme/55">·</span>
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

/* --------------------------------------------------- ce que vous recevez - */

const RECU = [
  {
    n: '01',
    titre: 'Le carnet, dans votre téléphone',
    texte:
      "Une page privée qui n'appartient qu'à vous. Un commerce, un bouton : WhatsApp s'ouvre sur la bonne conversation, avec le bon message. Vous marquez où vous en êtes, vous fermez, vous reprenez le lendemain au même endroit.",
  },
  {
    n: '02',
    titre: 'Le même travail pour votre ordinateur',
    texte:
      "Un fichier qui s'ouvre dans Excel ou dans Google Sheets, pour le donner à votre équipe et suivre qui fait quoi.",
  },
  {
    n: '03',
    titre: 'Le message, déjà écrit',
    texte:
      'Vous nous dites en une phrase ce que vous vendez. Chaque message est rédigé à partir de cette phrase et du métier du commerçant. Vous appuyez, vous envoyez.',
  },
]

function CeQueVousRecevez() {
  return (
    <Section fond="papier" interieur="py-20 sm:py-28">
      <Titre sur="Ce que vous recevez">
        Pas un fichier.
        <br />
        Un carnet de travail.
      </Titre>
      <div className="relative mt-12 grid gap-8 sm:gap-10 lg:grid-cols-3">
        {RECU.map((r, i) => (
          <Revele key={r.n} d={i * 120} className="relative">
            <div className="flex items-baseline gap-3">
              <Chiffre className="text-[2.6rem] text-brique/25">{r.n}</Chiffre>
              <h3 className="text-[1.35rem] leading-tight">{r.titre}</h3>
            </div>
            <p className="mt-3 text-[0.98rem] leading-relaxed text-sourd">{r.texte}</p>
          </Revele>
        ))}
      </div>
    </Section>
  )
}

/* ------------------------------------------------------------------ preuve */

function Preuve({ aller }) {
  return (
    <Section fond="encre2" grain interieur="py-20 sm:py-28">
      <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
        <div>
          <Titre sur="La preuve" sombre>
            <Compteur jusqua={TOTAL_FICHES} className="text-braise" /> commerces.
            <br />
            Comptez les points.
          </Titre>
          <p className="mt-6 max-w-[32rem] text-[1.02rem] leading-relaxed text-sable">
            Le {DATE_RELEVE}, {TOTAL_FICHES} commerces du Bénin et du Togo ont été
            relevés et rendus dans ce format exact, en une heure. PISTE, c'est cette
            heure automatisée, et vendue.
          </p>
          <ul className="mt-6 space-y-1.5 text-[0.95rem] text-sable">
            {REPARTITION.map((r, i) => (
              <li key={r.nom} className="flex items-center gap-3">
                <span
                  className={`h-2.5 w-2.5 shrink-0 rounded-full ${
                    ['bg-braise', 'bg-vertclair', 'bg-creme'][i]
                  }`}
                />
                <Chiffre className="w-10 text-papier">{r.n}</Chiffre>
                {r.nom}
              </li>
            ))}
          </ul>
          <div className="mt-8 rounded-2xl border border-traitsombre bg-encre/60 p-5">
            <p className="text-[0.9rem] leading-relaxed text-sable">
              <b className="font-semibold text-papier">D'où ça vient.</b> Un annuaire
              professionnel public, consulté ce jour-là. Un annuaire vieillit : un numéro
              peut avoir changé, un commerce peut avoir fermé. C'est pour ça que la ligne
              est composée avant de vous être envoyée, et que toute fiche injoignable est
              remplacée sans frais.
            </p>
            <button
              type="button"
              onClick={() => aller('#/donnees')}
              className="mt-3 flex min-h-[44px] items-center text-[0.9rem] font-semibold text-braise underline underline-offset-4"
            >
              Lire d'où viennent nos données
            </button>
            <p className="mt-3 text-[0.9rem] leading-relaxed text-sable">
              <b className="font-semibold text-papier">{NOMBRE_FIXES} de ces numéros</b>{' '}
              sont des lignes fixes : elles n'ont pas WhatsApp, on les appelle. C'est
              écrit sur la fiche, vous ne le découvrez pas en écrivant dans le vide.
            </p>
          </div>
        </div>
        <div>
          <Semis repartition={REPARTITION} total={TOTAL_FICHES} />
          <p className="mt-4 text-center text-[0.8rem] text-sable">
            17 colonnes, 11 lignes. Un point par commerce relevé.
          </p>
        </div>
      </div>
    </Section>
  )
}

/* -------------------------------------------------------------- la fiche - */

function LaFiche() {
  const [metier, setMetier] = useState('couture')
  const fiche = ficheExemple(metier, metier === 'patisserie' ? 'cotonou' : 'lome')
  const dispos = METIERS.filter((m) => !m.horsStock)

  return (
    <Section fond="papier2" id="fiche" interieur="py-20 sm:py-28">
      <div className="grid gap-12 lg:grid-cols-[1fr_0.95fr] lg:items-start lg:gap-16">
        <div>
          <Titre sur="Avant de payer">
            Voici exactement
            <br />
            ce que vous recevez.
          </Titre>
          <p className="mt-6 text-[1.02rem] leading-relaxed text-sourd">
            Pas une maquette. Un commerce réel, relevé le {DATE_RELEVE}, affiché avec
            les quatre informations en plus déjà cochées. Choisissez un métier, la
            fiche change.
          </p>

          <div className="mt-6 flex flex-wrap gap-2">
            {dispos.map((m) => (
              <button
                key={m.cle}
                type="button"
                onClick={() => setMetier(m.cle)}
                aria-pressed={metier === m.cle}
                className={`min-h-[44px] rounded-full border px-4 text-[0.9rem] font-semibold transition-colors ${
                  metier === m.cle
                    ? 'border-brique bg-brique text-creme'
                    : 'border-trait bg-creme text-sourd hover:border-sourd'
                }`}
              >
                {m.court}
              </button>
            ))}
          </div>

          <div className="mt-8 rounded-2xl border border-trait bg-creme p-5">
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-sourd">
              Ce que vend l'acheteur, dans cet exemple
            </p>
            <p className="mt-2 text-[0.98rem] leading-relaxed">« {OFFRE_EXEMPLE} »</p>
            <p className="mt-2 text-[0.82rem] text-sourd">
              C'est la phrase que vous écrivez à la sixième question. C'est elle qui
              fabrique le message de chaque fiche.
            </p>
          </div>
        </div>

        <FicheExemple
          key={metier}
          fiche={fiche}
          offre={OFFRE_EXEMPLE}
          options={{ teste: true, sansSite: true, dirigeant: true, message: true }}
        />
      </div>
    </Section>
  )
}

/* ---------------------------------------------------------------- le prix - */

function Prix({ aller }) {
  const demo = calcul(24, { teste: true, message: true })
  return (
    <Section fond="papier" interieur="py-20 sm:py-28">
      <div className="grid gap-12 lg:grid-cols-[0.95fr_1.05fr] lg:gap-16">
        <div>
          <Titre sur="Le prix">
            Toutes les fiches
            <br />
            au même prix de base.
          </Titre>
          <p className="mt-6 text-[1.02rem] leading-relaxed text-sourd">
            {fcfa(BASE)} la fiche : le nom du commerce, son métier, sa ville, son
            quartier, son numéro au bon format. Ce sont les informations en plus qui
            font monter le prix, et c'est vous qui les choisissez.
          </p>

          <div className="mt-8 space-y-2.5">
            <div className="flex items-baseline justify-between gap-4 rounded-2xl border border-encre/15 bg-creme px-4 py-3.5">
              <div>
                <p className="font-semibold">La fiche de base</p>
                <p className="text-[0.85rem] text-sourd">
                  Nom, métier, ville, quartier, numéro au bon format
                </p>
              </div>
              <Chiffre className="shrink-0 text-[1.25rem]">{fcfa(BASE)}</Chiffre>
            </div>
            {SUPPLEMENTS.map((s, i) => (
              <Revele
                key={s.cle}
                d={i * 90}
                className="flex items-baseline justify-between gap-4 rounded-2xl border border-trait bg-creme/60 px-4 py-3.5"
              >
                <div>
                  <p className="font-semibold">{s.nom}</p>
                  <p className="text-[0.85rem] text-sourd">{s.resume}</p>
                </div>
                <Chiffre className="shrink-0 text-[1.15rem] text-brique">
                  + {fcfa(s.prix)}
                </Chiffre>
              </Revele>
            ))}
          </div>

          <p className="mt-5 text-[0.95rem] text-sourd">
            Une fiche va donc de {fcfa(100)} à {fcfa(500)}.
          </p>
        </div>

        <div>
          <div className="rounded-2xl border border-encre/15 bg-encre p-6 text-papier sm:p-7">
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-braise">
              Un exemple, calculé devant vous
            </p>
            <p className="mt-3 text-[0.95rem] text-sable">
              24 fiches, avec le numéro testé et le message déjà écrit.
            </p>
            <dl className="mt-5 space-y-2 text-[0.95rem]">
              {demo.lignes.map((l) => (
                <div key={l.cle} className="flex items-baseline justify-between gap-3">
                  <dt className="text-sable">
                    {l.nom}{' '}
                    <span className="text-sable/70">
                      {fcfa(l.unite)} × {l.n}
                    </span>
                  </dt>
                  <dd className="tabular-nums">{fcfa(l.montant)}</dd>
                </div>
              ))}
              <div className="flex items-baseline justify-between gap-3 border-t border-traitsombre pt-3">
                <dt className="text-sable">Remise au volume</dt>
                <dd className="tabular-nums text-sable">
                  {demo.taux ? '- ' + fcfa(demo.remise) : 'aucune sous 50 fiches'}
                </dd>
              </div>
              <div className="flex items-baseline justify-between gap-3 border-t border-traitsombre pt-3">
                <dt className="font-semibold">À payer</dt>
                <dd>
                  <Chiffre className="text-[1.6rem] text-braise">{fcfa(demo.total)}</Chiffre>
                </dd>
              </div>
            </dl>
            <p className="mt-4 text-[0.85rem] text-sable">
              Soit {fcfa(demo.parFiche)} la fiche. Jamais un total qui tombe du ciel :
              le calcul reste affiché pendant que vous cochez.
            </p>
          </div>

          <div className="mt-6 rounded-2xl border border-trait bg-creme p-5">
            <p className="font-semibold">Plus vous en prenez, moins la fiche coûte</p>
            <ul className="mt-3 flex flex-wrap gap-2">
              {[...PALIERS].reverse().map((p) => (
                <li
                  key={p.seuil}
                  className="rounded-full border border-trait px-3.5 py-1.5 text-[0.88rem]"
                >
                  <b className="font-semibold">{p.seuil} fiches</b> :{' '}
                  <span className="text-brique">- {Math.round(p.taux * 100)} %</span>
                </li>
              ))}
            </ul>
          </div>

          <Bouton className="mt-6 w-full sm:w-auto" onClick={() => aller('#/commander')}>
            Composer ma commande
          </Bouton>
        </div>
      </div>
    </Section>
  )
}

/* ------------------------------------------------------------ engagements - */

const ENGAGEMENTS = [
  {
    t: 'Sous 24 heures',
    d: "À partir du moment où votre paiement est confirmé. Pas « dans la semaine » : le lendemain vous travaillez.",
  },
  {
    t: 'Injoignable, donc remplacée',
    d: "Un numéro qui ne répond plus ? Vous le signalez depuis votre carnet, une autre fiche prend sa place, sans frais et sans discussion.",
  },
  {
    t: '90 jours pour vous seul',
    d: "Une fiche qui vous est vendue ne repart chez personne d'autre pendant trois mois, quel que soit le secteur de l'autre acheteur.",
  },
  {
    t: 'Vous revenez ? Que du nouveau',
    d: "Si vous recommandez le même métier, PISTE se souvient de ce que vous avez déjà reçu et ne vous le revend pas.",
  },
  {
    t: 'Le lien de votre carnet est à vous, à vie',
    d: "Vous l'avez payé, vous le gardez. Six mois plus tard vous le rouvrez et vous retrouvez votre avancement là où vous l'aviez laissé. Perdu ? Un message sur WhatsApp et il repart.",
  },
  {
    t: 'Vous payez par Mobile Money, à la main',
    d: "MTN MoMo ou Moov Flooz, au Bénin. Aucun paiement ne se fait sur ce site : on vous donne le numéro et le montant exact, vous envoyez, on vérifie. Une commande non payée reste valable 24 heures, ensuite les fiches retournent au stock.",
  },
]

const JAMAIS = [
  {
    t: 'Aucune donnée de personne privée',
    d: "PISTE relève des entreprises : le nom du commerce, son métier, son adresse, son numéro professionnel, et le nom du dirigeant quand le commerce le publie lui-même. Ni âge, ni revenus, ni habitudes, ni rien de la vie privée de qui que ce soit.",
  },
  {
    t: "On ne vend jamais ce qu'on n'a pas",
    d: "Le nombre disponible s'affiche dès que vous choisissez un métier et une ville. Si on n'a rien, c'est écrit : au lieu de vous vendre du vide, on prend votre demande et on vous prévient le jour où ces fiches existent.",
  },
  {
    t: 'Un commerce qui veut disparaître disparaît',
    d: "Il écrit, il sort de la base, et il ne revient dans aucune livraison. La liste est revérifiée à chaque commande.",
  },
]

function Engagements() {
  const ref = useRevele()
  return (
    <Section fond="encre" grain interieur="py-20 sm:py-28">
      <div ref={ref} className="revele">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <Titre sur="Nos engagements" sombre>
            Ce sur quoi
            <br />
            on s'engage.
          </Titre>
          <span
            className="tampon mt-2 rounded-xl border-2 border-braise px-4 py-2 text-[0.8rem] font-bold uppercase tracking-[0.14em] text-braise"
            style={{ '--d': '520ms' }}
          >
            réservé 90 jours
          </span>
        </div>

        <div className="mt-12 grid gap-x-10 gap-y-8 sm:grid-cols-2">
          {ENGAGEMENTS.map((e, i) => (
            <Revele key={e.t} d={i * 90}>
              <div className="flex gap-3">
                <Puce className="mt-1 h-5 w-5 shrink-0 text-braise" />
                <div>
                  <h3 className="text-[1.15rem]">{e.t}</h3>
                  <p className="mt-1.5 text-[0.95rem] leading-relaxed text-sable">{e.d}</p>
                </div>
              </div>
            </Revele>
          ))}
        </div>

        <h3 className="mt-16 text-[clamp(1.5rem,5vw,2.2rem)]">Et ce qu'on ne fera jamais.</h3>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {JAMAIS.map((j, i) => (
            <Revele
              key={j.t}
              d={i * 90}
              className="rounded-2xl border border-traitsombre bg-encre2/70 p-5"
            >
              <p className="font-semibold text-braise">{j.t}</p>
              <p className="mt-2 text-[0.92rem] leading-relaxed text-sable">{j.d}</p>
            </Revele>
          ))}
        </div>
      </div>
    </Section>
  )
}

/* ------------------------------------------------------------------ stock - */

function Stock({ aller }) {
  const metiers = METIERS.filter((m) => !m.horsStock)
  return (
    <Section fond="papier" interieur="py-20 sm:py-28">
      <Titre sur="Le stock, aujourd'hui">
        Ce qui existe vraiment,
        <br />
        et rien d'autre.
      </Titre>
      <p className="mt-6 max-w-[42rem] text-[1.02rem] leading-relaxed text-sourd">
        Ces nombres sont ceux du relevé du {DATE_RELEVE}. Ils descendent au fur et à
        mesure des ventes, parce qu'une fiche vendue est réservée 90 jours à son
        acheteur.
      </p>

      <div className="mt-10 overflow-x-auto">
        <table className="w-full min-w-[34rem] border-collapse text-left">
          <caption className="sr-only">
            Nombre de fiches disponibles par métier et par ville
          </caption>
          <thead>
            <tr className="border-b border-encre/20">
              <th scope="col" className="py-3 pr-4 text-[0.8rem] font-semibold uppercase tracking-[0.12em] text-sourd">
                Ville
              </th>
              {metiers.map((m) => (
                <th
                  key={m.cle}
                  scope="col"
                  className="py-3 px-2 text-right text-[0.8rem] font-semibold uppercase tracking-[0.12em] text-sourd"
                >
                  {m.court}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {VILLES.map((v) => (
              <tr key={v.cle} className="border-b border-trait align-top">
                <th scope="row" className="py-4 pr-4 font-normal">
                  <span className="block font-semibold">{v.nom}</span>
                  <span className="block text-[0.82rem] text-sourd">
                    {v.pays} · {v.detail}
                  </span>
                </th>
                {metiers.map((m) => {
                  const n = STOCK[m.cle + '|' + v.cle] || 0
                  return (
                    <td key={m.cle} className="py-4 px-2 text-right">
                      {n >= MINIMUM ? (
                        <Chiffre className="text-[1.3rem] text-vert">{n}</Chiffre>
                      ) : n > 0 ? (
                        <span className="text-[0.85rem] text-sourd">
                          <Chiffre className="text-[1.05rem]">{n}</Chiffre>
                          <span className="block">sous le minimum</span>
                        </span>
                      ) : (
                        <span className="text-[0.85rem] text-sourd">
                          {v.bientot ? 'bientôt' : 'rien'}
                        </span>
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border-2 border-brique/30 bg-creme p-5">
          <p className="font-semibold">Abidjan : rien pour l'instant.</p>
          <p className="mt-2 text-[0.94rem] leading-relaxed text-sourd">
            Aucune source ivoirienne n'a encore été relevée. On préfère l'écrire noir
            sur blanc plutôt que vous laisser commander du vide. Choisissez quand même
            Abidjan dans le questionnaire : on enregistre votre demande, et c'est elle
            qui décide de l'ordre du travail.
          </p>
        </div>
        <div className="rounded-2xl border border-trait bg-creme p-5">
          <p className="font-semibold">Votre métier n'est pas dans la liste ?</p>
          <p className="mt-2 text-[0.94rem] leading-relaxed text-sourd">
            Coiffure, quincaillerie, pharmacie, garage, école : rien n'est encore relevé
            pour ces métiers. Dites-le dans le questionnaire, à la première question. On
            vous prévient le jour où c'est prêt, sans rien vous promettre entretemps.
          </p>
          <Bouton ton="contour" className="mt-4" onClick={() => aller('#/commander')}>
            Demander un métier
          </Bouton>
        </div>
      </div>

      <Bouton className="mt-10" onClick={() => aller('#/commander')}>
        Composer ma commande
      </Bouton>
    </Section>
  )
}

/* -------------------------------------------------------------- fin + pied */

function Fin({ aller }) {
  return (
    <>
      <Section fond="nuit" grain interieur="py-20 text-center sm:py-28">
        <Revele>
          <h2 className="mx-auto max-w-[24rem] text-[clamp(2.2rem,8vw,3.8rem)]">
            Six questions.
            <br />
            <span className="text-braise">Le prix devant vous.</span>
          </h2>
        </Revele>
        <Revele d={120}>
          <p className="mx-auto mt-6 max-w-[34rem] text-[1.02rem] leading-relaxed text-sable">
            Vous composez, vous voyez le calcul se faire, vous voyez la fiche que vous
            allez recevoir. Vous ne payez qu'après. Ça prend deux minutes.
          </p>
        </Revele>
        <Revele d={200} className="mt-9 flex flex-wrap justify-center gap-3">
          <Bouton ton="pleinClair" onClick={() => aller('#/commander')}>
            Composer ma commande
          </Bouton>
          <Bouton
            ton="contourSombre"
            href={`https://wa.me/${NEBULA_WHATSAPP}`}
            target="_blank"
            rel="noopener"
          >
            Parler à quelqu'un
          </Bouton>
        </Revele>
      </Section>

      <footer className="bg-nuit pb-12 text-sable">
        <div className="mx-auto w-full max-w-[68rem] border-t border-traitsombre px-5 pt-10 sm:px-8">
          <div className="flex flex-wrap items-start justify-between gap-8">
            <div>
              <p className="font-display text-[1.1rem] font-bold text-papier">
                PISTE <span className="font-normal text-sable">by NEBULA</span>
              </p>
              <p className="mt-2 max-w-[26rem] text-[0.9rem] leading-relaxed">
                NEBULA Agency · Cotonou, Bénin. On conçoit l'outil métier de chaque
                secteur. PISTE est le nôtre : trouver à qui parler.
              </p>
            </div>
            <div className="text-[0.9rem]">
              <button
                type="button"
                onClick={() => aller('#/donnees')}
                className="flex min-h-[44px] items-center font-semibold text-braise underline underline-offset-4"
              >
                D'où viennent nos données
              </button>
              <a
                className="flex min-h-[44px] items-center underline underline-offset-4 hover:text-braise"
                href={`https://wa.me/${NEBULA_WHATSAPP}`}
                target="_blank"
                rel="noopener"
              >
                WhatsApp {NEBULA_WHATSAPP_JOLI}
              </a>
              <a
                className="flex min-h-[44px] items-center underline underline-offset-4 hover:text-braise"
                href="https://www.nebula-agency.online"
                target="_blank"
                rel="noopener"
              >
                nebula-agency.online
              </a>
            </div>
          </div>
          <p className="mt-8 text-[0.82rem] leading-relaxed text-sable/75">
            PISTE ne relève que des informations publiées publiquement par des
            entreprises. Un commerce qui demande à sortir de la base en sort, et ne
            revient dans aucune livraison : écrivez au numéro ci-dessus. Les carnets
            partent de {EMAIL_ENVOI} : ajoutez cette adresse à vos contacts pour qu'elle
            ne tombe pas dans vos courriers indésirables.
          </p>
        </div>
      </footer>
    </>
  )
}

/* ------------------------------------------------------------------ barre - */

function BarreMobile({ aller }) {
  const [vue, setVue] = useState(false)
  useEffect(() => {
    const surScroll = () => setVue(window.scrollY > 620)
    surScroll()
    window.addEventListener('scroll', surScroll, { passive: true })
    return () => window.removeEventListener('scroll', surScroll)
  }, [])
  return (
    <div
      className={`fixed inset-x-0 bottom-0 z-40 border-t border-traitsombre bg-encre/97 px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 transition-opacity duration-300 lg:hidden ${
        vue ? 'opacity-100' : 'pointer-events-none opacity-0'
      }`}
    >
      <Bouton ton="pleinClair" className="w-full" onClick={() => aller('#/commander')}>
        Composer ma commande
      </Bouton>
    </div>
  )
}

/* ------------------------------------------------------------------------- */

export default function Vitrine({ aller }) {
  return (
    <>
      <Heros aller={aller} />
      <Ruban />
      <CeQueVousRecevez />
      <Preuve aller={aller} />
      <LaFiche />
      <Prix aller={aller} />
      <Engagements />
      <Stock aller={aller} />
      <Fin aller={aller} />
      <div className="h-20 lg:hidden" aria-hidden="true" />
      <BarreMobile aller={aller} />
    </>
  )
}
