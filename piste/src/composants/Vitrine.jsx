import {
  DATE_RELEVE,
  EXCLUSIVITE_JOURS,
  METIERS,
  MINIMUM,
  NEBULA_WHATSAPP_JOLI,
  REPARTITION,
  TOTAL_FICHES,
  VILLES,
  ficheExemple,
} from '../donnees.js'
import { BASE, PALIERS, SUPPLEMENTS, fcfa, nombre } from '../prix.js'
import { Bouton, Chiffre, Section, Titre } from './Ui.jsx'
import { Compteur, Revele, useRevele } from './Revele.jsx'
import { COULEURS_SEMIS, Puce, Semis, TraceEtapes, TracePiste } from './Trace.jsx'
import FicheExemple from './FicheExemple.jsx'

/*
  LA VITRINE.

  Une section, un geste, et jamais deux fois le même — chacun sort de la
  phrase du métier : « une piste, c'est une trace qu'on relève sur le terrain
  et qu'on suit jusqu'à la porte du commerçant ».

    héros ......... la trace qui se dessine
    ruban ......... ce qui a été relevé, qui défile
    la preuve ..... le semis : 187 points, un par commerce
    la fiche ...... la fiche qu'on relève du sol, ligne à ligne
    le chemin ..... la trace verticale et les repères qu'on plante
    le barème ..... le tampon qu'on pose sur le prix
    la garantie ... la porte qui s'ouvre
*/

export default function Vitrine({ onCommander }) {
  return (
    <>
      <Heros onCommander={onCommander} />
      <Ruban />
      <Preuve />
      <CeQueVousRecevez />
      <Chemin />
      <Bareme onCommander={onCommander} />
      <Garantie />
      <CeQuOnNeFaitPas />
      <Questions />
      <Final onCommander={onCommander} />
    </>
  )
}

/* ------------------------------------------------------------- 1. héros -- */

function Heros({ onCommander }) {
  return (
    <Section fond="encre" grain interieur="pt-24 pb-16 sm:pt-32 sm:pb-24" id="haut">
      <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <Revele as="p" className="mb-5 text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-braise">
            PISTE by NEBULA
          </Revele>

          <Revele as="h1" d={80} className="text-[clamp(2.6rem,10vw,5rem)]">
            Des commerçants
            <br />
            à qui parler
            <br />
            <span className="text-braise">demain matin.</span>
          </Revele>

          <Revele as="p" d={200} className="mt-6 max-w-[36rem] text-[1.05rem] leading-relaxed text-sable sm:text-[1.15rem]">
            Vous nous dites qui vous cherchez. On vous rend un carnet de commerces
            réels : le nom, le quartier, le numéro au bon format, et le message
            déjà écrit pour chacun. Vous ouvrez au téléphone, vous appuyez,
            WhatsApp s'ouvre sur la bonne conversation.
          </Revele>

          <Revele d={300} className="mt-8 flex flex-wrap gap-3">
            <Bouton ton="pleinClair" onClick={onCommander}>
              Composer ma commande
            </Bouton>
            <Bouton ton="contourSombre" href="#preuve">
              Voir une vraie fiche
            </Bouton>
          </Revele>

          <Revele d={400} className="mt-9 flex flex-wrap items-center gap-x-7 gap-y-3 text-[0.86rem] text-sable">
            <span>
              À partir de <b className="text-papier">{fcfa(BASE)}</b> la fiche
            </span>
            <span className="hidden h-4 w-px bg-traitsombre sm:block" />
            <span>
              Minimum <b className="text-papier">{MINIMUM} fiches</b>
            </span>
            <span className="hidden h-4 w-px bg-traitsombre sm:block" />
            <span>
              Livré <b className="text-papier">sous 24 heures</b>
            </span>
          </Revele>
        </div>

        <div className="text-braise">
          <TracePiste repere={5} hauteur="h-48 sm:h-64 lg:h-72" />
          <Revele as="p" d={1100} className="mt-2 text-center text-[0.82rem] text-sourd">
            Du relevé sur le terrain jusqu'à la porte du commerçant.
          </Revele>
        </div>
      </div>
    </Section>
  )
}

/* ------------------------------------------------------------- 2. ruban -- */

function Ruban() {
  const mots = [
    'ateliers de couture', 'Cotonou', 'maquis', 'Lomé', 'pâtisseries',
    'Porto-Novo', 'bars', 'Abomey-Calavi', 'brodeurs', 'Kégué',
    'restaurants', 'Hédzranawoé', 'boulangeries', 'Parakou', 'kebabs',
    'Godomey', 'buvettes', 'Bohicon', 'confection', 'Kpalimé',
  ]
  const suite = [...mots, ...mots]
  return (
    <div className="overflow-hidden border-y border-traitsombre bg-nuit py-3" aria-hidden="true">
      <div className="ruban gap-8 text-[0.8rem] uppercase tracking-[0.2em] text-sourd">
        {suite.map((m, i) => (
          <span key={i} className="flex shrink-0 items-center gap-8">
            {m}
            <span className="h-1 w-1 rounded-full bg-brique" />
          </span>
        ))}
      </div>
    </div>
  )
}

/* ----------------------------------------------------------- 3. preuve --- */

function Preuve() {
  return (
    <Section fond="papier" id="preuve" interieur="py-20 sm:py-28">
      <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:gap-16">
        <div>
          <Titre sur="La preuve, pas la promesse">
            {TOTAL_FICHES} commerces
            <br />
            déjà relevés.
          </Titre>
          <p className="mt-6 max-w-[34rem] leading-relaxed text-sourd">
            Le {DATE_RELEVE}, {TOTAL_FICHES} commerces du Bénin et du Togo ont été
            relevés un par un dans un annuaire professionnel public, remis en forme
            et livrés dans ce format exact. Ce n'est pas une maquette : c'est le
            stock avec lequel PISTE ouvre.
          </p>

          <dl className="mt-8 space-y-3">
            {REPARTITION.map((r) => (
              <Revele as="div" key={r.nom} className="flex items-baseline gap-4 border-b border-trait pb-3">
                <dd className="w-16 shrink-0">
                  <Chiffre className="text-[1.7rem] text-brique">
                    <Compteur jusqua={r.n} />
                  </Chiffre>
                </dd>
                <dt className="text-[0.95rem] text-sourd">{r.nom}</dt>
              </Revele>
            ))}
          </dl>

          <p className="mt-6 text-[0.86rem] leading-relaxed text-sourd">
            Chaque point du semis est un commerce. Vous pouvez les compter :
            17 colonnes, {TOTAL_FICHES} points, pas un de plus.
          </p>
        </div>

        <div className="self-center">
          <Semis repartition={REPARTITION} total={TOTAL_FICHES} />
          <div className="mt-6 grid gap-2 text-[0.84rem] text-sourd sm:grid-cols-3">
            {REPARTITION.map((r, i) => (
              <span key={r.nom} className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${COULEURS_SEMIS[i]}`} />
                {r.nom}
              </span>
            ))}
          </div>
        </div>
      </div>

      <Revele className="mt-14 grid gap-4 sm:grid-cols-3">
        {[
          ['Où', 'Cotonou et ses environs, les autres villes du Bénin, Lomé. Abidjan ouvre dès qu\'une source ivoirienne aura été relevée pour de vrai.'],
          ['Ce qui est vérifié', 'Le nom, le métier, la ville, le quartier quand il est publié, et le numéro remis au bon format.'],
          ['Ce qui ne l\'est pas', 'Qu\'un numéro sonne encore aujourd\'hui : ça, c\'est un supplément, et il est testé un par un avant l\'envoi.'],
        ].map(([t, d], i) => (
          <div key={t} className="rounded-2xl border border-trait bg-creme p-5" style={{ '--d': `${i * 90}ms` }}>
            <h3 className="text-[1.05rem]">{t}</h3>
            <p className="mt-2 text-[0.89rem] leading-relaxed text-sourd">{d}</p>
          </div>
        ))}
      </Revele>
    </Section>
  )
}

/* --------------------------------------------------- 4. ce que vous avez - */

function CeQueVousRecevez() {
  const fiche = ficheExemple('couture', 'cotonou')
  return (
    <Section fond="papier2" interieur="py-20 sm:py-28">
      <div className="grid gap-12 lg:grid-cols-[1fr_0.92fr] lg:gap-16">
        <div>
          <Titre sur="Ce que vous recevez">
            Un carnet,
            <br />
            pas un fichier.
          </Titre>
          <p className="mt-6 leading-relaxed text-sourd">
            Un fichier, on le télécharge et on ne l'ouvre plus. Un carnet, on
            l'ouvre au téléphone dans la rue : on appuie, WhatsApp s'ouvre sur la
            bonne conversation avec le bon message, on marque où on en est, et on
            reprend le lendemain là où on s'est arrêté.
          </p>

          <ul className="mt-8 space-y-4">
            {[
              ['Le carnet en ligne', 'Un lien privé qui n\'appartient qu\'à vous. Il marche au téléphone, il garde votre avancement, et il est à vous à vie.'],
              ['Le fichier CSV', 'Le même contenu, pour votre tableur ou votre logiciel. Les deux, pas l\'un ou l\'autre.'],
              ['Le message déjà écrit', 'Rédigé pour CE commerce, à partir de son métier et de ce que vous vendez. Vous appuyez, vous envoyez.'],
              ['Le bouton « injoignable »', 'Un numéro qui ne répond plus ? Vous le signalez depuis le carnet, la remplaçante arrive dans le même lien sous 24 heures. Sans frais.'],
            ].map(([t, d], i) => (
              <Revele as="li" key={t} d={i * 90} className="flex gap-3.5">
                <Puce className="mt-0.5 h-5 w-5 text-brique" />
                <span>
                  <b className="font-semibold">{t}</b>
                  <span className="mt-0.5 block text-[0.92rem] leading-relaxed text-sourd">{d}</span>
                </span>
              </Revele>
            ))}
          </ul>
        </div>

        <div>
          <FicheExemple
            fiche={fiche}
            options={{ teste: true, sansSite: false, dirigeant: false, message: true }}
            offre="je propose une assurance santé aux commerçants"
          />
        </div>
      </div>
    </Section>
  )
}

/* ----------------------------------------------------------- 5. chemin --- */

function Chemin() {
  const etapes = [
    ['Vous dites qui vous cherchez', 'Six questions : le métier, la ville, le quartier, combien de fiches, ce que vous voulez en plus, et ce que vous vendez. Le prix se construit sous vos yeux, ligne par ligne.'],
    ['Vous payez par Mobile Money', 'MTN MoMo ou Moov Flooz. Vous recevez le numéro, le montant et votre code de commande. Rien à saisir sur ce site : aucune carte, aucun compte à créer.'],
    ['Vous recevez votre carnet', 'Sous 24 heures, un email avec votre lien privé. Vous ouvrez au téléphone et vous commencez à écrire.'],
  ]
  return (
    <Section fond="encre2" grain interieur="py-20 sm:py-28">
      <Titre sur="Comment ça se passe" sombre>
        Trois étapes,
        <br />
        et vous écrivez.
      </Titre>

      <div className="relative mt-12">
        <TraceEtapes n={etapes.length} />
        <ol className="space-y-8">
          {etapes.map(([t, d], i) => (
            <Revele as="li" key={t} d={i * 140} className="relative flex gap-5">
              <span className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-braise sm:h-12 sm:w-12">
                <Chiffre className="text-[1.05rem] text-encre sm:text-[1.2rem]">{i + 1}</Chiffre>
              </span>
              <div className="pt-1.5">
                <h3 className="text-[1.25rem] sm:text-[1.5rem]">{t}</h3>
                <p className="mt-2 max-w-[40rem] text-[0.95rem] leading-relaxed text-sable">{d}</p>
              </div>
            </Revele>
          ))}
        </ol>
      </div>

      <Revele className="mt-12 rounded-2xl border border-traitsombre bg-nuit p-6">
        <p className="text-[0.95rem] leading-relaxed text-sable">
          <b className="text-papier">Une seule promesse de délai : 24 heures.</b> Le
          dimanche aussi. Si la liste n'est pas prête, elle n'est pas prête : on
          vous le dit, on ne vous fait pas attendre en silence.
        </p>
      </Revele>
    </Section>
  )
}

/* ----------------------------------------------------------- 6. barème --- */

function Bareme({ onCommander }) {
  return (
    <Section fond="papier" interieur="py-20 sm:py-28" id="bareme">
      <div className="max-w-[38rem]">
        <Titre sur="Le barème">
          {fcfa(BASE)} la fiche.
          <br />
          Le reste, vous le choisissez.
        </Titre>
        <p className="mt-6 leading-relaxed text-sourd">
          Toutes les fiches ont le même prix de base. Ce sont les informations en
          plus qui font monter le prix, et c'est vous qui les cochez. Vous voyez le
          calcul se faire : jamais un total qui tombe du ciel.
        </p>
      </div>

      <div className="mt-12 grid gap-6 lg:grid-cols-[0.85fr_1.15fr] lg:gap-12">
        <Revele className="relative self-start overflow-hidden rounded-2xl border border-trait bg-encre p-7 text-papier">
          <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-braise">
            La base
          </p>
          <p className="mt-3 flex items-baseline gap-2">
            <Chiffre className="text-[3.4rem] leading-none">{nombre(BASE)}</Chiffre>
            <span className="text-[1.2rem] text-sable">F la fiche</span>
          </p>
          <p className="mt-4 text-[0.92rem] leading-relaxed text-sable">
            Le nom du commerce, son métier, sa ville, son quartier, et son numéro
            au bon format. C'est le minimum pour appeler quelqu'un : en dessous,
            ce n'est plus une fiche.
          </p>
          {/* le tampon reste DANS la carte : posé à cheval sur le bord, la
              carte le tranchait net et ça se lisait comme un défaut, pas comme
              un geste. */}
          <span
            className="tampon absolute right-5 bottom-5 rounded-lg border-2 border-braise px-3 py-1.5 text-[0.72rem] font-bold uppercase tracking-[0.14em] text-braise"
            style={{ '--d': '520ms' }}
          >
            tarif au 03·08
          </span>
        </Revele>

        <div className="space-y-3">
          {SUPPLEMENTS.map((s, i) => (
            <Revele
              key={s.cle}
              d={i * 80}
              className="flex flex-wrap items-start justify-between gap-x-5 gap-y-2 rounded-2xl border border-trait bg-creme p-5"
            >
              <div className="min-w-[14rem] flex-1">
                <h3 className="text-[1.1rem]">{s.nom}</h3>
                <p className="mt-1.5 text-[0.89rem] leading-relaxed text-sourd">{s.detail}</p>
              </div>
              <span className="whitespace-nowrap rounded-full bg-papier2 px-3.5 py-1.5">
                <Chiffre className="text-[1.05rem] text-brique">+ {nombre(s.prix)} F</Chiffre>
              </span>
            </Revele>
          ))}

          <Revele className="rounded-2xl border border-trait bg-papier2/70 p-5">
            <h3 className="text-[1.05rem]">Remise au volume</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              {[...PALIERS].reverse().map((p) => (
                <span key={p.seuil} className="rounded-full border border-trait bg-creme px-3.5 py-1.5 text-[0.86rem]">
                  {p.seuil} fiches <b className="text-brique">−{Math.round(p.taux * 100)} %</b>
                </span>
              ))}
            </div>
            <p className="mt-3 text-[0.86rem] leading-relaxed text-sourd">
              Une fiche va donc de {fcfa(BASE)} à{' '}
              {fcfa(BASE + SUPPLEMENTS.reduce((s, x) => s + x.prix, 0))} selon ce que
              vous demandez. Minimum {MINIMUM} fiches par commande.
            </p>
          </Revele>
        </div>
      </div>

      <Revele className="mt-10">
        <Bouton onClick={onCommander}>Calculer mon prix</Bouton>
      </Revele>
    </Section>
  )
}

/* -------------------------------------------------------- 7. garantie ---- */

/* La porte est le geste de cette section : elle porte donc la révélation
   elle-même, au lieu d'être enveloppée dans un fondu générique qui ferait
   deux animations pour un seul propos. */
function Porte({ d = 0, children }) {
  const ref = useRevele()
  return (
    /*
      ⚠️ LE CADRE EST OBLIGATOIRE, ce n'est pas une décoration.

      Une porte fermée, c'est `perspective(700px) rotateY(-72deg)` : la boîte
      que le navigateur lui calcule fait alors près de 5 000 px de large, et
      elle pousse TOUTE LA PAGE de côté tant que personne n'a fait défiler
      jusqu'ici. Sur téléphone, ça donne une page qui glisse latéralement sans
      raison visible.

      Le cadre en `overflow-hidden` rend cette géométrie inoffensive, et c'est
      d'ailleurs plus juste : une porte s'ouvre DANS son encadrement.
    */
    <div className="overflow-hidden rounded-2xl">
      <div
        ref={ref}
        className="porte rounded-2xl border border-creme/25 bg-creme/8 p-7"
        style={{ '--d': `${d}ms` }}
      >
        {children}
      </div>
    </div>
  )
}

function Garantie() {
  return (
    <Section fond="laterite" grain interieur="py-20 sm:py-28">
      <div className="grid gap-10 lg:grid-cols-2 lg:gap-16">
        <Porte>
          <div>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-creme/70">
              La garantie
            </p>
            <h2 className="mt-3 text-[clamp(1.8rem,5.5vw,2.6rem)]">
              Une fiche injoignable
              <br />
              est remplacée.
            </h2>
            <p className="mt-5 leading-relaxed text-creme/85">
              Un numéro qui ne répond plus, un commerce qui a fermé ? Vous appuyez
              sur le bouton dans votre carnet. La remplaçante apparaît dans le même
              lien sous 24 heures, et vous ne payez rien de plus.
            </p>
            <p className="mt-4 text-[0.9rem] leading-relaxed text-creme/70">
              Ce bouton n'est pas une politesse. Sans lui, personne ne réclame :
              on se dit juste que la donnée est mauvaise, et on ne revient pas.
              Il nous dit aussi quelles sources vieillissent mal.
            </p>
          </div>
        </Porte>

        <Porte d={180}>
          <div>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-creme/70">
              L'exclusivité
            </p>
            <h2 className="mt-3 text-[clamp(1.8rem,5.5vw,2.6rem)]">
              {EXCLUSIVITE_JOURS} jours
              <br />
              rien qu'à vous.
            </h2>
            <p className="mt-5 leading-relaxed text-creme/85">
              Une fiche que vous achetez sort du stock pendant {EXCLUSIVITE_JOURS} jours,
              pour tout le monde et tous secteurs confondus. Personne d'autre ne
              l'achète pendant ce temps.
            </p>
            <p className="mt-4 text-[0.9rem] leading-relaxed text-creme/70">
              Et si vous recommandez le même métier dans la même ville, vous
              recevez du nouveau : PISTE se souvient de ce qu'il vous a déjà
              livré.
            </p>
          </div>
        </Porte>
      </div>
    </Section>
  )
}

/* ------------------------------------------------- 8. ce qu'on ne fait pas */

function CeQuOnNeFaitPas() {
  const interdits = [
    ['Aucune donnée de personne privée', 'Ni âge, ni revenus, ni habitudes, ni centres d\'intérêt. L\'entreprise, et le nom du dirigeant quand lui-même l\'a publié. Rien d\'autre.'],
    ['Aucun scraping des réseaux sociaux', 'Ni Facebook, ni Instagram, ni LinkedIn, ni TikTok aspirés en douce. L\'interface officielle ou rien.'],
    ['Le droit à l\'oubli, pour de vrai', 'Un commerce nous écrit, il disparaît de la base et de toute livraison future. La liste est vérifiée à chaque commande.'],
    ['Jamais de fiche remplie au hasard', 'Une information qui manque reste vide. Elle n\'est jamais devinée pour faire joli, et si elle vous a été facturée, la fiche est remplacée.'],
  ]
  return (
    <Section fond="papier2" interieur="py-20 sm:py-28">
      <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
        <div>
          <Titre sur="Ce qu'on ne fait pas">
            D'où vient
            <br />
            la donnée.
          </Titre>
          <p className="mt-6 leading-relaxed text-sourd">
            Annuaires professionnels publics, OpenStreetMap, petites annonces
            publiées par les commerçants eux-mêmes. Ce sont des informations que
            le commerce a lui-même rendues publiques pour être trouvé, et nous les
            rassemblons et nous les remettons en forme.
          </p>
          <p className="mt-4 text-[0.9rem] leading-relaxed text-sourd">
            Vous achetez un carnet de prospection professionnelle, pas un fichier
            de particuliers. La différence n'est pas cosmétique : elle décide de
            ce que nous acceptons de collecter.
          </p>
          <p className="mt-6">
            <a className="font-semibold text-brique underline underline-offset-4" href="#/origine">
              Lire la page complète sur l'origine des données
            </a>
          </p>
        </div>

        <ul className="grid gap-3 sm:grid-cols-2">
          {interdits.map(([t, d], i) => (
            <Revele as="li" key={t} d={i * 80} className="rounded-2xl border border-trait bg-creme p-5">
              <h3 className="text-[1.02rem]">{t}</h3>
              <p className="mt-2 text-[0.89rem] leading-relaxed text-sourd">{d}</p>
            </Revele>
          ))}
        </ul>
      </div>
    </Section>
  )
}

/* ------------------------------------------------------- 9. questions ---- */

function Questions() {
  const qr = [
    ['Combien de fiches au minimum ?', `${MINIMUM}. En dessous, il n'y a pas assez de monde à qui parler pour se faire une idée.`],
    ['Et si le métier que je cherche n\'est pas dans la liste ?', 'Vous nous le dites au moment de composer votre commande, et on vous prévient quand ce vivier est prêt. Chaque demande nous dit où aller relever en priorité.'],
    ['Est-ce que je peux voir avant de payer ?', 'Vous voyez une vraie fiche, avec un vrai commerce, avant de payer un franc. C\'est plus haut sur cette page, et c\'est aussi dans le questionnaire.'],
    ['Je paie comment ?', 'MTN MoMo ou Moov Flooz, au Bénin. Aucun paiement ne se fait sur ce site : vous recevez le numéro, le montant et votre code de commande, et vous payez depuis votre téléphone.'],
    ['Si je ne paie pas tout de suite ?', 'La commande tient 24 heures. Passé ce délai les fiches retournent au stock, et il n\'y a rien à annuler : elle s\'éteint toute seule.'],
    ['Qu\'est-ce que je fais avec ces numéros ?', 'Vous écrivez à des professionnels au sujet de leur activité. Restez sur ce terrain-là, présentez-vous, et acceptez un non : ce sont les mêmes commerçants qu\'on relèvera pour quelqu\'un d\'autre dans trois mois.'],
  ]
  return (
    <Section fond="papier" interieur="py-20 sm:py-28">
      <Titre sur="Les questions qu'on nous pose">Bonnes questions.</Titre>
      <div className="mt-10 grid gap-3 lg:grid-cols-2">
        {qr.map(([q, r], i) => (
          <Revele
            as="details"
            key={q}
            d={i * 60}
            className="group rounded-2xl border border-trait bg-creme px-5 open:bg-papier2/60"
          >
            <summary className="flex min-h-[56px] cursor-pointer list-none items-center justify-between gap-4 py-4 font-semibold marker:content-none">
              {q}
              <span className="shrink-0 text-brique transition-transform duration-300 group-open:rotate-45" aria-hidden="true">
                <svg viewBox="0 0 20 20" className="h-5 w-5">
                  <path d="M10 4v12M4 10h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </span>
            </summary>
            <p className="pb-5 text-[0.93rem] leading-relaxed text-sourd">{r}</p>
          </Revele>
        ))}
      </div>
    </Section>
  )
}

/* ---------------------------------------------------------- 10. final ---- */

function Final({ onCommander }) {
  return (
    <Section fond="encre" grain interieur="py-20 text-center sm:py-28">
      <Revele as="h2" className="mx-auto max-w-[26ch] text-[clamp(2.1rem,7vw,3.6rem)]">
        Demain matin, vous avez{' '}
        <span className="text-braise">
          <Compteur jusqua={30} /> conversations
        </span>{' '}
        à ouvrir.
      </Revele>
      <Revele as="p" d={120} className="mx-auto mt-6 max-w-[42rem] leading-relaxed text-sable">
        Composez votre commande en six questions. Le prix se calcule devant vous,
        vous voyez une vraie fiche, et vous ne payez qu'ensuite.
      </Revele>
      <Revele d={220} className="mt-9 flex flex-wrap justify-center gap-3">
        <Bouton ton="pleinClair" onClick={onCommander}>
          Composer ma commande
        </Bouton>
        <Bouton ton="contourSombre" href={`https://wa.me/${NEBULA_WHATSAPP_JOLI.replace(/\D/g, '')}`} target="_blank" rel="noopener">
          Poser une question sur WhatsApp
        </Bouton>
      </Revele>
      <Revele as="p" d={300} className="mt-8 text-[0.86rem] text-sourd">
        {METIERS.filter((m) => !m.horsStock).length} métiers ·{' '}
        {VILLES.filter((v) => !v.bientot).length} zones · {TOTAL_FICHES} fiches en stock
        aujourd'hui
      </Revele>
    </Section>
  )
}
