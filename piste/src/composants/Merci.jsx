import { NEBULA_WHATSAPP, NEBULA_WHATSAPP_JOLI } from '../donnees.js'
import { Bouton, Section } from './Ui.jsx'

/*
  LA PAGE DE RETOUR APRÈS UN PAIEMENT EN LIGNE (`#/merci`).

  ⛔ ELLE NE DIT JAMAIS « PAIEMENT CONFIRMÉ ». Revenir ici ne prouve rien : la
  page de SasPay renvoie le navigateur trois secondes après un paiement
  réussi, mais un client peut aussi arriver ici en tapant l'adresse, ou revenir
  en arrière. Ce qui fait foi, c'est la notification signée reçue par
  `piste-paiement-recu`. Annoncer une quittance qu'on n'a pas, c'est promettre
  un carnet qui ne partira pas.

  ⚠️ POURQUOI CETTE PAGE EXISTE. Sans elle, `SASPAY_RETOUR` renvoyait sur
  `#/merci`, que le routeur ne connaissait pas : il retombait silencieusement
  sur la vitrine. Le client payait 4 320 F et se retrouvait sur la page
  d'accueil, sans un mot, sans son code. C'est le genre de trou qui fait
  écrire « j'ai payé ??? » sur WhatsApp.

  ⚠️ LA RÉFÉRENCE NE VIENT PAS DE SASPAY. Leur adresse de retour est fixe et
  ne porte aucun paramètre : c'est le site qui a rangé le code juste avant de
  partir payer. S'il manque (autre navigateur, stockage vidé), la page reste
  juste et n'invente pas de code.
*/

const CLE = 'piste_paiement_en_cours'

export function noterPaiementEnCours(reference) {
  try {
    sessionStorage.setItem(CLE, reference)
    /* ⚠️ Les deux : un paiement Mobile Money peut ouvrir l'application de
       l'opérateur et ramener le client dans un ONGLET NEUF, où la session est
       vide. Le `localStorage` survit à ça. */
    localStorage.setItem(CLE, reference)
  } catch (e) {}
}

function referenceEnCours() {
  try {
    return sessionStorage.getItem(CLE) || localStorage.getItem(CLE) || ''
  } catch (e) {
    return ''
  }
}

export default function Merci({ aller }) {
  const reference = referenceEnCours()
  const wa = `https://wa.me/${NEBULA_WHATSAPP}?text=${encodeURIComponent(
    reference
      ? `Bonjour, je viens de payer la commande ${reference} en ligne.`
      : 'Bonjour, je viens de payer une commande en ligne.'
  )}`

  return (
    <Section fond="encre" grain interieur="max-w-2xl py-20">
      <p className="font-display text-[0.85rem] uppercase tracking-[0.2em] text-braise">
        PISTE
      </p>
      <h1 className="mt-3 font-display text-[2rem] font-bold leading-tight">
        Merci. Votre paiement est parti.
      </h1>

      {reference ? (
        <p className="mt-5 text-[1.05rem] leading-relaxed text-sable">
          Commande <strong className="text-braise">{reference}</strong>.
        </p>
      ) : null}

      <p className="mt-5 text-[1.05rem] leading-relaxed text-sable">
        Nous attendons la confirmation de l’opérateur. Elle arrive en général en
        quelques secondes. Dès qu’elle est là, votre commande passe en « payée » et
        le carnet vous est envoyé.
      </p>

      <div className="mt-8 rounded-2xl border-2 border-braise/45 bg-braise/8 p-6">
        <p className="font-semibold">Cette page n’est pas un reçu.</p>
        <p className="mt-2 text-[0.95rem] leading-relaxed text-sable">
          Revenir ici ne prouve pas que le paiement a abouti : seule la confirmation
          de l’opérateur compte. Si quelque chose vous semble anormal, écrivez-nous,
          on regarde tout de suite.
        </p>
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Bouton ton="pleinClair" href={wa}>
          Écrire sur WhatsApp ({NEBULA_WHATSAPP_JOLI})
        </Bouton>
        <Bouton onClick={() => aller('#/')}>Retour à l’accueil</Bouton>
      </div>
    </Section>
  )
}
