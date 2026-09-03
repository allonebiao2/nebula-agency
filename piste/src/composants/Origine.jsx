import {
  DATE_RELEVE,
  EMAIL_ENVOI,
  NEBULA_WHATSAPP,
  NEBULA_WHATSAPP_JOLI,
  NOMBRE_FIXES,
  REPARTITION,
  TOTAL_FICHES,
} from '../donnees.js'
import { Bouton, Section, Titre } from './Ui.jsx'
import { Puce } from './Trace.jsx'
import { Revele } from './Revele.jsx'

/*
  Décision 43 : la page qui dit d'où vient la donnée.

  Ce n'est pas une page de mentions légales, c'est un argument de vente. Un
  fichier vendu sous le manteau ne dit jamais d'où il vient, et c'est exactement
  ce qui le rend suspect. Tout ce qui est écrit ici doit rester vrai même quand
  ça n'arrange pas : ce qui est vérifié, ce qui ne l'est pas, et ce qu'on ne
  fera jamais.
*/

const SOURCES = [
  {
    t: 'Les annuaires professionnels publics',
    d: "C'est d'où viennent les 187 premières fiches, relevées le " + DATE_RELEVE + ". Un commerce qui s'inscrit dans un annuaire professionnel demande à être trouvé : c'est le contraire d'une information volée.",
    etat: 'en service',
  },
  {
    t: 'OpenStreetMap',
    d: "La carte libre du monde, alimentée par ses contributeurs. Elle donne la position et souvent le quartier, gratuitement et sans condition d'usage restrictive.",
    etat: 'en service',
  },
  {
    t: 'Les petites annonces : Jiji, CoinAfrique',
    d: 'Un commerçant qui publie une annonce publie aussi son numéro professionnel, pour être appelé. On ne relève que ce qui sert à le joindre pour son commerce.',
    etat: 'en service',
  },
  {
    t: "Facebook, par l'API officielle de Meta",
    d: "Uniquement par l'interface prévue pour ça, avec autorisation. Aucun aspirateur de pages, jamais. NEBULA sait obtenir ces autorisations, elle l'a déjà fait pour WhatsApp.",
    etat: 'à venir',
  },
  {
    t: 'Google Maps',
    d: "L'interface Places de Google exige une carte bancaire active, même sur son palier gratuit. Elle est prévue dans le moteur mais éteinte. OpenStreetMap fait le même travail, gratuitement.",
    etat: 'éteinte',
  },
]

const VRAI = [
  'Le nom du commerce, tel qu\'il est publié.',
  'Son métier, sa ville, et son quartier quand la source l\'indique.',
  'Son numéro professionnel, remis au format qui fonctionne aujourd\'hui : dix chiffres au Bénin depuis 2025, huit au Togo.',
  'Le fait que la ligne soit un fixe ou un mobile, parce qu\'un fixe n\'a pas WhatsApp.',
]

const PAS_SUR = [
  "Qu'un commerce soit toujours ouvert. Un annuaire vieillit, et une boutique peut avoir fermé le mois dernier.",
  /* ⚠️ Cette page est celle où l'on dit ce qu'on ne sait PAS. Elle promettait
     « il est composé avant l'envoi » : c'était faux, personne ne composait.
     Le supplément vérifie trois choses réelles, et aucune ne garantit qu'on
     décroche. C'est écrit tel quel. */
  "Qu'un numéro décroche. Le supplément « le numéro est vérifié » contrôle trois choses : que la ligne appartient à une tranche réellement attribuée par le régulateur, que la fiche a été revue à sa source depuis moins de deux mois, et qu'aucun client ne l'a signalée injoignable. Ça écarte les numéros morts, ça ne promet pas qu'on vous répondra. Si ça ne répond pas, on remplace la fiche gratuitement.",
  "Qu'un commerce n'ait vraiment aucun site, sauf si vous prenez le supplément correspondant : sans lui, l'absence de site est une indication, pas une vérification.",
]

export default function Origine({ aller }) {
  return (
    <div className="bg-papier">
      <header className="border-b border-trait bg-creme">
        <div className="mx-auto flex w-full max-w-[68rem] items-center justify-between gap-4 px-5 py-3.5 sm:px-8">
          <button
            type="button"
            onClick={() => aller('#/')}
            className="flex min-h-[44px] items-center gap-2 font-display text-[1rem] font-bold tracking-tight"
          >
            <Puce className="h-4 w-4 text-brique" />
            PISTE <span className="font-normal text-sourd">by NEBULA</span>
          </button>
          <Bouton ton="nu" onClick={() => aller('#/commander')}>
            Composer ma commande
          </Bouton>
        </div>
      </header>

      <Section fond="encre" grain interieur="py-16 sm:py-24">
        <p className="text-[0.72rem] font-semibold uppercase tracking-[0.22em] text-braise">
          En clair
        </p>
        <h1 className="mt-4 max-w-[22ch] text-[clamp(2.2rem,8.4vw,4rem)]">
          D'où viennent nos données.
        </h1>
        <p className="mt-6 max-w-[40rem] text-[1.05rem] leading-relaxed text-sable">
          Un fichier vendu sous le manteau ne dit jamais d'où il vient : c'est justement ce
          qui le rend suspect. Cette page dit tout, y compris ce qui ne nous arrange pas.
          Lisez-la avant d'acheter, pas après.
        </p>
      </Section>

      <Section fond="papier" interieur="py-16 sm:py-24">
        <Titre sur="Les sources">Ce qu'on relève, et où.</Titre>
        <div className="mt-10 space-y-4">
          {SOURCES.map((s, i) => (
            <Revele
              key={s.t}
              d={i * 80}
              className="rounded-2xl border border-trait bg-creme p-5 sm:p-6"
            >
              <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                <h2 className="text-[1.2rem]">{s.t}</h2>
                <span
                  className={`rounded-full px-3 py-1 text-[0.75rem] font-semibold ${
                    s.etat === 'en service'
                      ? 'bg-vert/12 text-vert'
                      : 'bg-papier2 text-sourd'
                  }`}
                >
                  {s.etat}
                </span>
              </div>
              <p className="mt-2 text-[0.96rem] leading-relaxed text-sourd">{s.d}</p>
            </Revele>
          ))}
        </div>
        <p className="mt-6 max-w-[46rem] text-[0.94rem] leading-relaxed text-sourd">
          Le moteur qui relève respecte le fichier <code className="font-semibold">robots.txt</code>{' '}
          de chaque source et ne dépasse jamais une demande par seconde. Il n'entre nulle part où
          on ne lui a pas ouvert la porte.
        </p>
      </Section>

      <Section fond="papier2" interieur="py-16 sm:py-24">
        <div className="grid gap-10 lg:grid-cols-2 lg:gap-14">
          <div>
            <h2 className="text-[clamp(1.6rem,5.4vw,2.4rem)]">Ce qui est vrai.</h2>
            <ul className="mt-5 space-y-3">
              {VRAI.map((v) => (
                <li key={v} className="flex gap-3 text-[0.98rem] leading-relaxed">
                  <Puce className="mt-1 h-4 w-4 shrink-0 text-vert" />
                  {v}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="text-[clamp(1.6rem,5.4vw,2.4rem)]">
              Ce dont on n'est <span className="text-brique">pas</span> sûr.
            </h2>
            <ul className="mt-5 space-y-3">
              {PAS_SUR.map((v) => (
                <li key={v} className="flex gap-3 text-[0.98rem] leading-relaxed text-sourd">
                  <Puce className="mt-1 h-4 w-4 shrink-0 text-brique" />
                  {v}
                </li>
              ))}
            </ul>
            <p className="mt-5 rounded-2xl border border-trait bg-creme p-5 text-[0.94rem] leading-relaxed">
              C'est pour ça que la garantie existe : une fiche injoignable se signale d'un
              bouton depuis votre carnet, et elle est remplacée sous 24 heures, sans frais et
              sans discussion. Le signalement sert aussi à nous : il nous dit quelles sources
              vieillissent mal.
            </p>
          </div>
        </div>
      </Section>

      <Section fond="encre" grain interieur="py-16 sm:py-24">
        <Titre sur="Les interdits" sombre>
          Ce qu'on ne fera jamais.
        </Titre>
        <div className="mt-10 grid gap-4 sm:grid-cols-3">
          {[
            {
              t: 'Aucune donnée de personne privée',
              d: "PISTE relève des entreprises. Le nom du commerce, son métier, son adresse, son numéro professionnel, et le nom du dirigeant quand le commerce le publie lui-même. Ni âge, ni revenus, ni habitudes, ni situation de famille, ni rien qui relève de la vie privée de qui que ce soit.",
            },
            {
              t: 'Aucun aspirateur de réseaux sociaux',
              d: "Ni Facebook, ni Instagram, ni LinkedIn, ni TikTok par la porte de derrière. L'interface officielle de Meta ou rien du tout.",
            },
            {
              t: 'Aucune fiche inventée pour faire le nombre',
              d: "Si le vivier ne suffit pas, le moteur s'étend un peu aux communes voisines, et il l'écrit sur la fiche. Il ne baisse jamais son exigence tout seul, et il alerte plutôt que de livrer du remplissage.",
            },
          ].map((j, i) => (
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
      </Section>

      <Section fond="papier" interieur="py-16 sm:py-24">
        <div className="grid gap-10 lg:grid-cols-[1fr_0.9fr] lg:gap-14">
          <div>
            <Titre sur="Droit à l'oubli">
              Un commerce demande
              <br />à disparaître ? Il disparaît.
            </Titre>
            <p className="mt-6 text-[1.02rem] leading-relaxed text-sourd">
              Si vous êtes commerçant et que vous ne voulez pas figurer dans PISTE, écrivez au
              numéro ci-contre ou à {EMAIL_ENVOI} avec le nom de votre commerce. Vous sortez de
              la base, et vous n'apparaissez dans aucune livraison future : la liste est
              revérifiée à chaque commande. Vous n'avez rien à justifier, et ça ne coûte rien.
            </p>
            <p className="mt-4 text-[1.02rem] leading-relaxed text-sourd">
              Si des acheteurs ont déjà reçu votre fiche avant votre demande, on ne peut pas la
              leur retirer de la main. On peut vous dire combien, et quand. On préfère l'écrire
              plutôt que de laisser croire à un effacement total qui n'existe pas.
            </p>
            <Bouton
              className="mt-7"
              href={`https://wa.me/${NEBULA_WHATSAPP}?text=${encodeURIComponent(
                'Bonjour, je suis commerçant et je souhaite ne pas figurer dans PISTE. Le nom de mon commerce est : '
              )}`}
              target="_blank"
              rel="noopener"
            >
              Demander à sortir de la base
            </Bouton>
          </div>

          <div className="rounded-2xl border border-trait bg-creme p-6">
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-sourd">
              Le relevé du {DATE_RELEVE}, en chiffres
            </p>
            <dl className="mt-4 space-y-2.5 text-[0.96rem]">
              {[
                ['Commerces relevés', TOTAL_FICHES],
                ...REPARTITION.map((r) => [r.nom, r.n]),
                ['dont lignes fixes, sans WhatsApp', NOMBRE_FIXES],
              ].map(([t, v]) => (
                <div key={t} className="flex items-baseline justify-between gap-4">
                  <dt className="text-sourd">{t}</dt>
                  <dd className="font-display font-bold tabular-nums">{v}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-5 text-[0.9rem] leading-relaxed text-sourd">
              Ces nombres sont comptés sur le fichier de relevé, pas estimés. Ils bougent à
              chaque vente, parce qu'une fiche vendue est réservée 90 jours à son acheteur.
            </p>
            <p className="mt-4 text-[0.9rem] leading-relaxed text-sourd">
              Une question ? {NEBULA_WHATSAPP_JOLI}.
            </p>
          </div>
        </div>

        <Bouton className="mt-12" onClick={() => aller('#/commander')}>
          Composer ma commande
        </Bouton>
      </Section>
    </div>
  )
}
