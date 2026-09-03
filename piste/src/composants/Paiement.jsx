import { useEffect, useState } from 'react'
import {
  EMAIL_ENVOI,
  HEURES_VALIDITE,
  METIERS,
  MOBILE_MONEY,
  MOMO_PRET,
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
function EnLigne({ reference, total, enLigne = true }) {
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
      <p className="font-display text-[1.2rem] font-bold">
        {enLigne ? 'Payer maintenant, depuis cette page.' : 'Plus rapide : payer en ligne.'}
      </p>
      <p className="mt-2 text-[0.95rem] leading-relaxed text-sable">
        {fcfa(total)} en Mobile Money ou par carte.{' '}
        {enLigne
          ? 'Votre paiement nous arrive tout de suite : pas de capture d’écran à envoyer, pas de virement à rapprocher.'
          : 'Vous avez choisi le dépôt à la main, et il reste possible juste en dessous. Mais depuis cette page, c’est immédiat.'}
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
  const operateur = MOBILE_MONEY.find((m) => m.cle === commande.momoOperateur)

  const copier = async (quoi, texte) => {
    try {
      await navigator.clipboard.writeText(texte)
      setCopie(quoi)
      setTimeout(() => setCopie(''), 2400)
    } catch (e) {
      setCopie('')
    }
  }

  /* ⚠️ LE CHEMIN QUI MARCHE NE DISPARAÎT JAMAIS. Quand le client a choisi de
     payer en ligne, les consignes de dépôt Mobile Money deviennent du bruit :
     elles se replient, mais elles restent à un clic. Quelqu'un dont le
     paiement en ligne échoue ne doit pas avoir à refaire sa commande. */
  const enLigne = commande.moyen !== 'main'
  const blocDepot = (
    <>
        {/* ------------------------------------------------ où l'on crédite */}
        <div className="mt-3 rounded-2xl border border-traitsombre bg-encre2 p-5">
          <p className="text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-sable">
            Le numéro NEBULA à créditer
          </p>
          {MOMO_PRET ? (
            <ul className="mt-3 space-y-3">
              {MOBILE_MONEY.filter((m) => m.numero).map((m) => (
                <li key={m.cle} className="flex flex-wrap items-baseline justify-between gap-3">
                  <span>
                    <Chiffre className="text-[1.35rem] text-papier">{m.numero}</Chiffre>
                    <span className="ml-3 text-[0.9rem] text-sable">{m.operateur}</span>
                  </span>
                  {m.titulaire && (
                    <span className="text-[0.88rem] text-sable">au nom de {m.titulaire}</span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-[0.95rem] leading-relaxed text-sable">
              Le numéro à créditer vous est donné dans la conversation WhatsApp, avec le
              montant exact. On préfère vous l'écrire à la main que l'afficher sur une page :
              c'est de l'argent, et un numéro affiché au mauvais endroit se recopie de
              travers.
            </p>
          )}
          {/* ⚠️ Le numéro qui reçoit l'argent n'est PAS celui sur lequel on nous
              écrit. Le dire ici évite le geste le plus coûteux qui soit : un
              dépôt envoyé au mauvais numéro. */}
          <p className="mt-3 rounded-xl bg-encre px-4 py-3 text-[0.88rem] leading-relaxed text-braise">
            <b className="font-semibold">Attention :</b> le numéro qui reçoit l'argent n'est
            pas le numéro WhatsApp sur lequel vous nous écrivez. N'envoyez rien avant de
            l'avoir reçu dans la conversation.
          </p>
          <p className="mt-3 text-[0.88rem] leading-relaxed text-sable">
            Un seul moyen accepté aujourd'hui : <b className="font-semibold text-papier">MTN
            MoMo</b>, au Bénin. Si
            vous payez depuis un autre pays, écrivez-nous d'abord : ce n'est pas encore
            ouvert.
          </p>
        </div>

        {/* --------------------------------------- depuis quel numéro payer */}
        <div className="mt-3 rounded-2xl border-2 border-braise/45 bg-braise/8 p-5">
          <p className="font-display text-[1.15rem] font-bold">
            Payez bien depuis le numéro que vous avez donné.
          </p>
          <p className="mt-2 text-[0.95rem] leading-relaxed text-sable">
            Vous avez déclaré le{' '}
            <b className="font-semibold text-papier">+229 {commande.momoNumero}</b>
            {operateur ? ` (${operateur.operateur})` : ''}, au nom de{' '}
            <b className="font-semibold text-papier">
              {commande.prenom} {commande.nom}
            </b>
            . C'est ce numéro et ce nom qui s'affichent à la réception : c'est comme ça
            qu'on reconnaît votre paiement parmi les autres. Un envoi depuis un autre
            numéro nous fait perdre du temps, et vous aussi.
          </p>
        </div>
    </>
  )
  const depot = enLigne ? (
    <details className="mt-3 rounded-2xl border border-traitsombre bg-encre2 px-5 py-1">
      <summary className="flex min-h-[52px] cursor-pointer items-center text-[0.95rem] font-semibold text-braise">
        Je préfère payer à la main, par dépôt Mobile Money
      </summary>
      <div className="pb-4">{blocDepot}</div>
    </details>
  ) : (
    blocDepot
  )

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

        {SASPAY_PRET && <EnLigne reference={commande.ref} total={commande.total} enLigne={enLigne} />}

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
              Montant exact à envoyer
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

        {depot}

        {/* ------------------------------------------------- compte à rebours */}
        <div className="mt-3">
          <Rebours date={commande.date} />
        </div>

        {/* ------------------------------------------------------ la marche */}
        <ol className="mt-9 space-y-4">
          {/* ⛔ CES QUATRE ÉTAPES DÉCRIVAIENT LE DÉPÔT À LA MAIN, POINT. Elles
              restaient telles quelles au-dessus d'un bouton « Payer », et
              disaient à quelqu'un qui venait de payer par carte de faire un
              transfert puis d'envoyer une capture d'écran. Le QC ne pouvait
              pas le voir : rien n'était cassé, tout était faux. */}
          {[
            {
              t: 'Envoyez votre commande sur WhatsApp',
              d: "Si la conversation ne s'est pas ouverte toute seule, appuyez sur le bouton plus bas. Le message est déjà écrit, votre code est dedans.",
            },
            enLigne
              ? {
                  t: 'Payez depuis cette page',
                  d: `${fcfa(commande.total)} en Mobile Money ou par carte, sur la page sécurisée de notre opérateur.`,
                }
              : {
                  t: 'Faites le transfert Mobile Money',
                  d: `Le montant exact, ${fcfa(commande.total)}, depuis le numéro que vous avez déclaré.`,
                },
            enLigne
              ? {
                  t: 'Rien à envoyer, rien à prouver',
                  d: "La confirmation de l'opérateur nous arrive toute seule : pas de capture d'écran, pas d'attente.",
                }
              : {
                  t: 'Envoyez la preuve dans la même conversation',
                  d: "Une capture suffit. Mongazi rapproche à la main sur son application, puis marque la commande payée.",
                },
            {
              t: 'Sous 24 heures, votre carnet arrive',
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
          <Bouton
            ton="pleinClair"
            href={`https://wa.me/${NEBULA_WHATSAPP}?text=${encodeURIComponent(commande.texte)}`}
            target="_blank"
            rel="noopener"
          >
            Ouvrir WhatsApp et envoyer
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
