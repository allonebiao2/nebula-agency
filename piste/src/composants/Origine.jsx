import { DATE_RELEVE, EMAIL, NEBULA_WHATSAPP_JOLI, TOTAL_FICHES } from '../donnees.js'
import { Section, Titre } from './Ui.jsx'
import { Revele } from './Revele.jsx'
import { lienWhatsApp } from '../etat.js'
import { Bouton } from './Ui.jsx'

/*
  D'OÙ VIENT LA DONNÉE — décision 43.

  Une page qui dit franchement d'où vient la donnée, ce qui est vérifié, ce
  qui ne l'est pas, et comment un commerce s'en retire. Elle n'est pas
  décorative : c'est elle qu'on montrera le jour où quelqu'un demandera des
  comptes, et c'est elle qui donne à un acheteur méfiant une raison de nous
  croire.
*/

export default function Origine() {
  const retrait = [
    'PISTE · retrait de mon commerce',
    '',
    '· Nom du commerce :',
    '· Ville :',
    '· Numéro publié :',
    '',
    'Je demande le retrait de ce commerce de la base PISTE.',
  ].join('\n')

  return (
    <>
      <Section fond="encre" grain interieur="pt-20 pb-14 sm:pt-28 sm:pb-20">
        <Revele as="p" className="text-[0.72rem] font-semibold uppercase tracking-[0.22em] text-braise">
          Transparence
        </Revele>
        <Revele as="h1" d={80} className="mt-4 max-w-[20ch] text-[clamp(2.2rem,8vw,4rem)]">
          D'où vient la donnée.
        </Revele>
        <Revele as="p" d={160} className="mt-6 max-w-[42rem] leading-relaxed text-sable">
          Vous achetez une liste de commerces à contacter. Vous avez le droit de
          savoir comment elle a été faite, et les commerces qui y figurent ont le
          droit d'en sortir. Cette page dit les deux, sans détour.
        </Revele>
      </Section>

      <Section fond="papier" interieur="py-16 sm:py-20">
        <div className="grid gap-12 lg:grid-cols-[0.85fr_1.15fr] lg:gap-16">
          <div>
            <Titre sur="Les sources">Ce qu'on relève.</Titre>
            <p className="mt-5 leading-relaxed text-sourd">
              Uniquement ce qu'un commerce a lui-même rendu public pour être
              trouvé par ses clients.
            </p>
          </div>

          <div className="space-y-4">
            {[
              ['Les annuaires professionnels publics', `C'est la source des ${TOTAL_FICHES} fiches de départ, relevées le ${DATE_RELEVE}. Un commerce s'y inscrit lui-même pour être appelé.`],
              ['OpenStreetMap', 'La carte libre : nom, activité, position. Ce que les commerçants et les contributeurs y ont déposé.'],
              ['Les petites annonces', "Jiji, CoinAfrique : le commerçant y publie son numéro pour vendre. C'est une invitation à le contacter."],
              ['L\'interface officielle de Meta', "Pour les pages professionnelles, et uniquement par l'interface officielle. Jamais en aspirant les pages."],
            ].map(([t, d], i) => (
              <Revele key={t} d={i * 70} className="rounded-2xl border border-trait bg-creme p-5">
                <h3 className="text-[1.05rem]">{t}</h3>
                <p className="mt-2 text-[0.9rem] leading-relaxed text-sourd">{d}</p>
              </Revele>
            ))}
          </div>
        </div>
      </Section>

      <Section fond="papier2" interieur="py-16 sm:py-20">
        <div className="grid gap-10 lg:grid-cols-2 lg:gap-14">
          <div>
            <Titre sur="Ce qui est vérifié">On vous le dit fiche par fiche.</Titre>
            <ul className="mt-6 space-y-3">
              {[
                ['Le nom, le métier, la ville', 'Relevés à la source et remis en forme à la main.'],
                ['Le quartier', 'Quand le commerce l\'a publié. Sinon la case reste vide : on ne le devine pas.'],
                ['Le numéro, au bon format', 'Remis aux normes du pays. Un fixe est marqué comme fixe : il n\'a pas WhatsApp, on l\'appelle.'],
                ['Le numéro qui sonne encore', 'C\'est un supplément payant, et c\'est le seul moyen honnête de le dire : le tester coûte du temps, donc il se paie.'],
              ].map(([t, d]) => (
                <li key={t} className="border-b border-trait pb-3">
                  <b className="font-semibold">{t}</b>
                  <span className="mt-0.5 block text-[0.9rem] leading-relaxed text-sourd">{d}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <Titre sur="Ce qui ne l'est pas">Et ce qu'on ne collecte jamais.</Titre>
            <ul className="mt-6 space-y-3">
              {[
                ['Aucune donnée de vie privée', 'Ni âge, ni revenus, ni situation familiale, ni centres d\'intérêt. L\'entreprise, et le nom du dirigeant quand lui-même l\'a publié.'],
                ['Aucun scraping des réseaux sociaux', 'Facebook, Instagram, LinkedIn, TikTok : l\'interface officielle ou rien.'],
                ['Aucun `robots.txt` ignoré', 'Ce qu\'un site demande de ne pas relever n\'est pas relevé. Une requête par seconde au maximum.'],
                ['Aucune case remplie au hasard', 'Une information manquante reste vide, et si elle vous a été facturée, la fiche est remplacée.'],
              ].map(([t, d]) => (
                <li key={t} className="border-b border-trait pb-3">
                  <b className="font-semibold">{t}</b>
                  <span className="mt-0.5 block text-[0.9rem] leading-relaxed text-sourd">{d}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      <Section fond="laterite" grain interieur="py-16 sm:py-20">
        <div className="max-w-[44rem]">
          <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-creme/70">
            Vous êtes un commerce
          </p>
          <h2 className="mt-3 text-[clamp(1.9rem,6vw,3rem)]">
            Vous voulez sortir de la base ? C'est un message.
          </h2>
          <p className="mt-5 leading-relaxed text-creme/85">
            Écrivez-nous, et votre commerce disparaît de la base et de toute
            livraison future. Pas de formulaire de trois pages, pas de motif à
            justifier. La liste des retraits est vérifiée à chaque commande :
            un commerce sorti ne peut pas revenir par une nouvelle collecte.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Bouton ton="plein" className="bg-encre text-papier hover:bg-nuit" href={lienWhatsApp(retrait)} target="_blank" rel="noopener">
              Demander le retrait sur WhatsApp
            </Bouton>
            <Bouton ton="plein" className="bg-creme/15 text-creme hover:bg-creme/25" href={`mailto:${EMAIL}?subject=${encodeURIComponent('Retrait de mon commerce de la base PISTE')}`}>
              Écrire par email
            </Bouton>
          </div>
          <p className="mt-5 text-[0.86rem] text-creme/70">
            {EMAIL} · {NEBULA_WHATSAPP_JOLI}
          </p>
        </div>
      </Section>

      <Section fond="papier" interieur="py-16 sm:py-20">
        <div className="max-w-[44rem]">
          <Titre sur="Ce que vous en faites">Ce qu'on vous demande, à vous.</Titre>
          <p className="mt-5 leading-relaxed text-sourd">
            Ces numéros sont ceux de professionnels, publiés pour être appelés au
            sujet de leur activité. Restez sur ce terrain-là : présentez-vous,
            dites ce que vous vendez, et acceptez un non. Ce sont les mêmes
            commerçants que nous relèverons pour quelqu'un d'autre dans trois
            mois, et leur patience est un bien commun.
          </p>
          <p className="mt-4 leading-relaxed text-sourd">
            Une fiche achetée est à vous : vous ne la revendez pas, vous ne la
            rediffusez pas. C'est ce qui rend l'exclusivité de 90 jours possible.
          </p>
        </div>
      </Section>
    </>
  )
}
