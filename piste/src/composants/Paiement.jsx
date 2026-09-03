import { useEffect, useState } from 'react'
import {
  EMAIL_ENVOI,
  HEURES_VALIDITE,
  METIERS,
  NEBULA_WHATSAPP,
  NEBULA_WHATSAPP_JOLI,
  SASPAY_PRET,
  VILLES,
} from '../donnees.js'
import { fcfa } from '../prix.js'
import { resteEn } from '../stockage.js'
import { ouvrirPaiement } from '../supabase.js'
import { noterPaiementEnCours } from './Merci.jsx'
import { Bouton, Chiffre } from './Ui.jsx'

/*
  L'écran de paiement (décisions 26, 27, 28).

  Il montre quatre choses et rien d'autre : le code, le montant, le numéro à
  créditer, et le numéro depuis lequel l'acheteur a dit qu'il paierait. Plus le
  temps qu'il lui reste, parce qu'une commande non payée rend ses fiches au
  stock au bout de 24 heures.
*/

/*
  Payer depuis la page (SasPay).

  ⚠️ FERMÉ TANT QUE `SASPAY_PRET` VAUT `false` : voir le commentaire dans
  `donnees.js`. Quand il s'ouvrira, il se posera AU-DESSUS du Mobile Money à la
  main, sans le remplacer. Un moyen de paiement neuf se met à côté de celui qui
  marche.

  ⚠️ Le navigateur n'envoie que la référence : le montant est relu en base par
  le serveur. Et revenir sur le site ne prouve rien — c'est la notification
  signée qui marque la commande payée. Le texte le dit, plutôt que de laisser
  croire qu'un retour vaut quittance.
*/
function EnLigne({ reference, total }) {
  const [etat, setEtat] = useState('pret')
  const [souci, setSouci] = useState('')

  const partir = async () => {
    setEtat('ouvre')
    setSouci('')
    const r = await ouvrirPaiement(reference)
    if (r?.ok && r.url) {
      /* ⚠️ AVANT de partir. L'adresse de retour de SasPay est fixe et ne porte
         aucun paramètre : si le code n'est pas rangé ici, la page de retour ne
         saura pas quelle commande le client vient de payer. */
      noterPaiementEnCours(reference)
      window.location.href = r.url
      return
    }
    setEtat('pret')
    setSouci(
      r?.erreur === 'commande déjà traitée'
        ? 'Cette commande est déjà réglée. Écrivez-nous sur WhatsApp si ce n’est pas le cas.'
        : 'Le paiement en ligne n’a pas répondu. Le Mobile Money ci-dessous marche, lui.'
    )
  }

  return (
    <div className="mt-8 rounded-2xl border-2 border-braise/45 bg-braise/8 p-6">
      <p className="font-display text-[1.2rem] font-bold">Payer maintenant, depuis cette page.</p>
      <p className="mt-2 text-[0.95rem] leading-relaxed text-sable">
        {fcfa(total)} en Mobile Money ou par carte. Dès que le paiement est confirmé, votre
        carnet part tout seul : rien à envoyer, rien à prouver.
      </p>
      <div className="mt-4">
        <Bouton ton="pleinClair" onClick={partir} disabled={etat === 'ouvre'}>
          {etat === 'ouvre' ? 'Un instant…' : 'Payer ' + fcfa(total)}
        </Bouton>
      </div>
      {souci && <p className="mt-3 text-[0.9rem] leading-relaxed text-rougeclair">{souci}</p>}
      <p className="mt-3 text-[0.85rem] leading-relaxed text-sable">
        Vous serez ramené ici après le paiement. Ce retour ne vaut pas reçu : c’est la
        confirmation de l’opérateur qui compte, et elle arrive en quelques secondes.
      </p>
    </div>
  )
}

function Rebours({ date }) {
  const [t, setT] = useState(() => resteEn(date))
  useEffect(() => {
    const i = setInterval(() => setT(resteEn(date)), 1000)
    return () => clearInterval(i)
  }, [date])

  if (t.fini) {
    return (
      <div className="rounded-2xl border-2 border-rougeclair/40 bg-rougeclair/8 px-5 py-4">
        <p className="font-semibold text-rougeclair">Le délai de 24 heures est passé.</p>
        <p className="mt-1 text-[0.92rem] leading-relaxed text-sable">
          Les fiches sont retournées au stock. Écrivez-nous sur WhatsApp avec votre code :
          si elles sont encore là, on remet la commande en route tout de suite.
        </p>
      </div>
    )
  }
  const large = t.h >= 6
  return (
    <div
      className={`rounded-2xl border-2 px-5 py-4 ${
        large ? 'border-traitsombre bg-encre2' : 'border-braise/50 bg-braise/8'
      }`}
    >
      <p className="text-[0.85rem] text-sable">Il vous reste</p>
      <Chiffre className={`text-[1.7rem] ${large ? 'text-papier' : 'text-braise'}`}>
        {t.texte}
      </Chiffre>
      <p className="mt-1 text-[0.88rem] leading-relaxed text-sable">
        Passé {HEURES_VALIDITE} heures sans paiement, les fiches retournent au stock et
        repartent à la vente. Rien n'est perdu : il suffit de recommencer.
      </p>
    </div>
  )
}

export default function Paiement({ commande, aller }) {
  const [copie, setCopie] = useState('')
  const metier = METIERS.find((m) => m.cle === commande.metier)
  const ville = VILLES.find((v) => v.cle === commande.ville)

  const copier = async (quoi, texte) => {
    try {
      await navigator.clipboard.writeText(texte)
      setCopie(quoi)
      setTimeout(() => setCopie(''), 2400)
    } catch (e) {
      setCopie('')
    }
  }

  /* ⛔ LE DÉPÔT MOBILE MONEY À LA MAIN EST RETIRÉ (Mongazi, 2026-09-03). Il ne
     reste qu'un seul moyen de payer : en ligne. Ce qui l'accompagnait — le
     numéro NEBULA à créditer, la consigne de payer depuis le numéro déclaré,
     l'envoi de la preuve sur WhatsApp — n'avait de sens que pour le
     rapprochement manuel, et le rapprochement se fait tout seul.
     ⚠️ WhatsApp reste, mais comme moyen de NOUS JOINDRE, plus comme étape du
     tunnel : on ne fait plus sortir un client juste avant qu'il paie. */
  return (
    <div className="min-h-screen bg-encre text-papier">
      <div className="mx-auto w-full max-w-[46rem] px-5 py-12 sm:px-8 sm:py-16">
        <div className="porte">
          <p className="text-[0.72rem] font-semibold uppercase tracking-[0.22em] text-braise">
            Commande enregistrée
          </p>
          <h1 className="mt-4 text-[clamp(2rem,8vw,3.2rem)]">
            Reste à payer,
            <br />
            <span className="text-braise">et c'est à vous.</span>
          </h1>
        </div>

        {SASPAY_PRET && <EnLigne reference={commande.ref} total={commande.total} />}

        {/* ------------------------------------------------ code et montant */}
        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-traitsombre bg-encre2 p-5">
            <p className="text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-sable">
              Votre code de commande
            </p>
            <Chiffre className="mt-1 block text-[1.75rem] text-papier">{commande.ref}</Chiffre>
            <button
              type="button"
              onClick={() => copier('ref', commande.ref)}
              className="mt-2 flex min-h-[44px] items-center text-[0.85rem] font-semibold text-braise underline underline-offset-4"
            >
              {copie === 'ref' ? 'Copié' : 'Copier le code'}
            </button>
          </div>
          <div className="rounded-2xl border border-traitsombre bg-encre2 p-5">
            <p className="text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-sable">
              Montant à payer
            </p>
            <Chiffre className="mt-1 block text-[1.75rem] text-braise">
              {fcfa(commande.total)}
            </Chiffre>
            <button
              type="button"
              onClick={() => copier('montant', String(commande.total))}
              className="mt-2 flex min-h-[44px] items-center text-[0.85rem] font-semibold text-braise underline underline-offset-4"
            >
              {copie === 'montant' ? 'Copié' : 'Copier le montant'}
            </button>
          </div>
        </div>

        {/* ------------------------------------------------- compte à rebours */}
        <div className="mt-3">
          <Rebours date={commande.date} />
        </div>

        {/* ------------------------------------------------------ la marche */}
        <ol className="mt-9 space-y-4">
          {[
            {
              t: 'Payez depuis cette page',
              d: `${fcfa(commande.total)} en Mobile Money ou par carte, sur la page sécurisée de notre opérateur.`,
            },
            {
              t: 'Rien à envoyer, rien à prouver',
              d: "La confirmation de l'opérateur nous arrive toute seule. Pas de capture d'écran, pas d'attente.",
            },
            {
              t: 'Votre carnet arrive, en quelques minutes',
              d: `Un lien privé qui n'appartient qu'à vous, à ouvrir sur votre téléphone. Il reste valable à vie : vous y retrouvez votre avancement six mois plus tard.`,
            },
          ].map((e, i) => (
            <li key={e.t} className="flex gap-4">
              <Chiffre className="shrink-0 text-[1.5rem] text-braise">{i + 1}</Chiffre>
              <div>
                <p className="font-semibold">{e.t}</p>
                <p className="mt-1 text-[0.93rem] leading-relaxed text-sable">{e.d}</p>
              </div>
            </li>
          ))}
        </ol>

        {/* ------------------------------------------------ mail ET whatsapp */}
        <div className="mt-8 rounded-2xl border border-traitsombre bg-encre2 p-6">
          <p className="font-display text-[1.2rem] font-bold">
            Surveillez votre boîte mail ET votre WhatsApp.
          </p>
          <p className="mt-2 text-[0.95rem] leading-relaxed text-sable">
            Le lien de votre carnet part par email à{' '}
            <b className="font-semibold text-papier">{commande.email}</b>, depuis{' '}
            <b className="font-semibold text-papier">{EMAIL_ENVOI}</b>. Regardez aussi vos
            courriers indésirables, et marquez cette adresse comme fiable. Tout le reste,
            la confirmation du paiement et vos questions, passe par WhatsApp au{' '}
            <b className="font-semibold text-papier">+{commande.wa}</b>.
          </p>
        </div>

        <div className="mt-9 flex flex-wrap gap-3">
          {/* ⚠️ WHATSAPP RESTE, MAIS IL NE FAIT PLUS AVANCER LA COMMANDE. Ce
              n'est plus « envoyez votre commande » (le serveur l'a déjà), c'est
              « écrivez-nous si quelque chose cloche ». Le ton principal passe
              donc au bouton de paiement, et celui-ci devient secondaire. */}
          <Bouton
            ton="contourSombre"
            href={`https://wa.me/${NEBULA_WHATSAPP}?text=${encodeURIComponent(commande.texte)}`}
            target="_blank"
            rel="noopener"
          >
            Un souci ? Écrivez-nous
          </Bouton>
          <Bouton ton="contourSombre" onClick={() => copier('tout', commande.texte)}>
            {copie === 'tout' ? 'Copié' : 'Copier le récapitulatif'}
          </Bouton>
        </div>

        <p className="mt-6 text-[0.88rem] leading-relaxed text-sable">
          Un souci ? Le numéro de NEBULA est le {NEBULA_WHATSAPP_JOLI}. Gardez votre code{' '}
          {commande.ref} sous la main : c'est avec lui qu'on retrouve votre commande.
        </p>
        <p className="mt-3 text-[0.88rem] leading-relaxed text-sable">
          {metier?.nom} · {ville?.nom} · {commande.n} fiches · {fcfa(commande.unitaire)} la
          fiche.
        </p>

        <button
          type="button"
          onClick={() => aller('#/')}
          className="mt-10 flex min-h-[44px] items-center text-[0.9rem] font-semibold text-sable underline underline-offset-4 hover:text-braise"
        >
          Revenir au site
        </button>
      </div>
    </div>
  )
}
