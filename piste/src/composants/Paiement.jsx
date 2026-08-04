import { useEffect, useState } from 'react'
import {
  EMAIL,
  METIERS,
  MOMO,
  NEBULA_WHATSAPP_JOLI,
  VILLES,
} from '../donnees.js'
import { fcfa } from '../prix.js'
import {
  composerMessage,
  detailOptions,
  joliDelai,
  lienWhatsApp,
  maCommande,
  resteAvantExpiration,
} from '../etat.js'
import { Bouton, Chiffre } from './Ui.jsx'

/*
  L'ÉCRAN DU PAIEMENT.

  Il ne prend pas d'argent. Il donne les quatre choses de la décision 26 —
  le numéro, le montant, le code de commande, et le rappel du numéro depuis
  lequel le client paiera — puis il pousse la commande sur le WhatsApp de
  NEBULA, écrite, prête à envoyer.

  ⚠️ Tant que `MOMO.aConfirmer` est vrai, AUCUN NUMÉRO N'EST AFFICHÉ. Le
  parcours reste entier : le numéro arrive sur WhatsApp à la seconde où la
  commande part. Afficher un numéro non confirmé, c'est envoyer l'argent
  d'un client chez un inconnu — on ne prend pas ce risque pour gagner un
  écran.
*/

export default function Paiement({ commande, onRecommencer }) {
  const [reste, setReste] = useState(() => resteAvantExpiration(commande.cree))
  const [copie, setCopie] = useState(false)

  useEffect(() => {
    const t = setInterval(() => setReste(resteAvantExpiration(commande.cree)), 1000)
    return () => clearInterval(t)
  }, [commande.cree])

  const message = composerMessage(commande)
  const metier = commande.metierLibre?.trim() || METIERS.find((m) => m.cle === commande.metier)?.nom
  const ville = VILLES.find((v) => v.cle === commande.ville)?.nom
  const expiree = reste <= 0

  const copier = async () => {
    try {
      await navigator.clipboard.writeText(message)
      setCopie(true)
      setTimeout(() => setCopie(false), 2600)
    } catch {
      /* le presse-papier peut être refusé : le message reste lisible à l'écran,
         et le bouton WhatsApp fonctionne de toute façon. */
    }
  }

  return (
    <div className="bg-papier">
      <div className="mx-auto w-full max-w-[46rem] px-5 py-12 sm:px-8 sm:py-16">
        <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-brique">
          Plus qu'une étape
        </p>
        <h1 className="mt-3 text-[clamp(2rem,7vw,3.2rem)]">
          Votre commande est composée.
        </h1>
        <p className="mt-4 leading-relaxed text-sourd">
          Rien n'a été payé et rien n'a été envoyé pour l'instant. Envoyez-la sur
          notre WhatsApp, elle est déjà écrite, puis payez par Mobile Money.
          Votre carnet part sous 24 heures.
        </p>

        {/* le code, gros, dictable au téléphone */}
        <div className="mt-8 overflow-hidden rounded-2xl border border-trait bg-encre text-papier">
          <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-5">
            <div>
              <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-braise">
                Code de commande
              </p>
              <Chiffre className="mt-1 block text-[2.6rem] leading-none tracking-[0.14em]">
                {commande.code}
              </Chiffre>
            </div>
            <div className="text-right">
              <p className="text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-braise">
                À payer
              </p>
              <Chiffre className="mt-1 block text-[2.2rem] leading-none">
                {fcfa(commande.total)}
              </Chiffre>
            </div>
          </div>
          <div
            className={`border-t border-traitsombre px-6 py-3 text-[0.88rem] ${
              expiree ? 'bg-rouge/20 text-rougeclair' : 'text-sable'
            }`}
            role={expiree ? 'alert' : undefined}
          >
            {expiree ? (
              <>
                Cette commande a expiré : les fiches sont retournées au stock.
                Recomposez-la, il n'y a rien à annuler.
              </>
            ) : (
              <>
                Valable encore <b className="text-papier">{joliDelai(reste)}</b>. Passé
                ce délai, les fiches retournent au stock.
              </>
            )}
          </div>
        </div>

        {/* 1. envoyer */}
        <Etape n={1} titre="Envoyez la commande sur WhatsApp">
          <p className="text-[0.93rem] leading-relaxed text-sourd">
            Le message est déjà rédigé. Vous n'avez qu'à appuyer sur envoyer :
            c'est ce qui nous permet de vous répondre avec le numéro de paiement
            et de préparer votre liste.
          </p>
          <pre className="mt-4 max-h-64 overflow-auto whitespace-pre-wrap rounded-xl border border-trait bg-creme px-4 py-3 font-sans text-[0.86rem] leading-relaxed">
            {message}
          </pre>
          <div className="mt-4 flex flex-wrap gap-3">
            <Bouton href={lienWhatsApp(message)} target="_blank" rel="noopener">
              Envoyer sur WhatsApp
            </Bouton>
            <Bouton ton="contour" onClick={copier}>
              {copie ? 'Copié ✓' : 'Copier le message'}
            </Bouton>
          </div>
        </Etape>

        {/* 2. payer */}
        <Etape n={2} titre="Payez par Mobile Money">
          {MOMO.aConfirmer ? (
            <div className="rounded-xl border border-brique/30 bg-papier2/60 px-4 py-4">
              <p className="text-[0.93rem] leading-relaxed">
                <b className="font-semibold">Le numéro vous est donné sur WhatsApp</b>, à
                l'instant où votre commande arrive. Nous ne l'affichons pas sur cette
                page : un numéro de paiement affiché au mauvais endroit, c'est de
                l'argent qui part chez quelqu'un d'autre.
              </p>
              <p className="mt-3 text-[0.93rem] leading-relaxed text-sourd">
                Réponse en quelques minutes aux heures ouvrables, et au plus tard
                dans la matinée pour une commande de la nuit.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {MOMO.comptes.map((cpt) => (
                <div
                  key={cpt.reseau}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-trait bg-creme px-4 py-3"
                >
                  <span className="text-[0.88rem] font-semibold uppercase tracking-[0.12em] text-sourd">
                    {cpt.reseau}
                  </span>
                  <Chiffre className="text-[1.3rem]">{cpt.numero}</Chiffre>
                  <span className="text-[0.86rem] text-sourd">{cpt.titulaire}</span>
                </div>
              ))}
            </div>
          )}

          <ul className="mt-4 space-y-2 text-[0.92rem] leading-relaxed">
            <li className="flex gap-2.5">
              <span className="text-brique">·</span>
              <span>
                Montant exact : <b>{fcfa(commande.total)}</b>. Un montant arrondi nous
                fait chercher.
              </span>
            </li>
            <li className="flex gap-2.5">
              <span className="text-brique">·</span>
              <span>
                Payez depuis le <b>{commande.momo}</b> ({commande.reseau}) : c'est ce
                numéro qui s'affiche chez nous à la réception, et c'est comme ça
                qu'on vous reconnaît.
              </span>
            </li>
            <li className="flex gap-2.5">
              <span className="text-brique">·</span>
              <span>
                Mettez <b>{commande.code}</b> en motif si votre application le
                permet. Si elle ne le permet pas, ce n'est pas grave.
              </span>
            </li>
          </ul>
        </Etape>

        {/* 3. recevoir */}
        <Etape n={3} titre="Recevez votre carnet sous 24 heures" dernier>
          <p className="text-[0.93rem] leading-relaxed text-sourd">
            Un email part à <b className="text-encre">{commande.email}</b> avec votre
            lien privé, et un message sur WhatsApp vous prévient. Surveillez les
            deux, et regardez vos indésirables, c'est là que les emails aiment se
            cacher.
          </p>
          <p className="mt-3 text-[0.93rem] leading-relaxed text-sourd">
            Le lien est à vous à vie : votre avancement s'y garde, et vous le
            retrouvez six mois plus tard. Perdu l'email ? Écrivez-nous sur
            WhatsApp avec votre code, on vous le renvoie.
          </p>
        </Etape>

        {/* le récapitulatif */}
        <div className="mt-10 rounded-2xl border border-trait bg-papier2/50 p-5">
          <h2 className="text-[1.1rem]">Ce que vous recevrez</h2>
          <dl className="mt-4 grid gap-x-6 gap-y-2.5 text-[0.92rem] sm:grid-cols-2">
            {[
              ['Métier', metier],
              ['Ville', ville],
              ['Quartier', commande.quartier?.trim() || 'toute la ville'],
              ['Nombre de fiches', `${commande.nombre}`],
              ['En plus', detailOptions(commande.options)],
              ['Vous vendez', commande.offre],
            ].map(([k, v]) => (
              <div key={k} className="flex flex-col border-b border-trait/70 pb-2">
                <dt className="text-[0.78rem] uppercase tracking-[0.12em] text-sourd">{k}</dt>
                <dd className="font-semibold">{v}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-4 text-[0.86rem] leading-relaxed text-sourd">
            Une fiche injoignable est remplacée sans frais. Les fiches livrées
            sortent du stock 90 jours : personne d'autre ne les reçoit pendant ce
            temps.
          </p>
        </div>

        <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-3 text-[0.88rem] text-sourd">
          <button type="button" className="min-h-[44px] font-semibold text-brique underline underline-offset-4" onClick={onRecommencer}>
            Modifier ma commande
          </button>
          <span>
            Une question : {NEBULA_WHATSAPP_JOLI} · {EMAIL}
          </span>
        </div>
      </div>
    </div>
  )
}

function Etape({ n, titre, children, dernier = false }) {
  return (
    <section className={`relative mt-10 pl-12 sm:pl-14 ${dernier ? '' : 'pb-2'}`}>
      <span className="absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full bg-brique sm:h-11 sm:w-11">
        <Chiffre className="text-[1rem] text-creme sm:text-[1.15rem]">{n}</Chiffre>
      </span>
      {!dernier && (
        <span className="absolute left-[17px] top-11 bottom-0 w-px bg-trait sm:left-[21px] sm:top-14" aria-hidden="true" />
      )}
      <h2 className="text-[1.3rem] sm:text-[1.55rem]">{titre}</h2>
      <div className="mt-3">{children}</div>
    </section>
  )
}
