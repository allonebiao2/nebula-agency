import { useState } from 'react'
import { METIERS, NEBULA_WHATSAPP, VILLES } from '../donnees.js'
import { ajouter } from '../stockage.js'
import { Bouton } from './Ui.jsx'

/*
  Décision 39 : quand un métier ou une ville n'existe pas encore, le site
  n'oppose pas une porte fermée. Il enregistre la demande et prévient quand
  c'est prêt. Chaque demande dit à NEBULA où investir le prochain relevé.

  Ce n'est pas une vente. On ne prend ni argent ni engagement de date : on prend
  un contact et un besoin.
*/

const champ =
  'mt-2 block min-h-[52px] w-full rounded-2xl border bg-creme px-4 text-encre placeholder:text-sourd/60'

export default function Demande({ metier, ville, metierLibre, onMetierLibre, compacte }) {
  const [prenom, setPrenom] = useState('')
  const [nom, setNom] = useState('')
  const [email, setEmail] = useState('')
  const [tel, setTel] = useState('')
  const [essai, setEssai] = useState(false)
  const [envoye, setEnvoye] = useState(false)

  const nomMetier =
    metier === 'autre'
      ? metierLibre.trim()
      : METIERS.find((m) => m.cle === metier)?.nom || ''
  const nomVille = VILLES.find((v) => v.cle === ville)?.nom || ''

  const emailOk = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(email.trim())
  const telOk = tel.replace(/\D/g, '').length >= 8
  const pret = nomMetier.length >= 3 && emailOk && telOk && prenom.trim() && nom.trim()

  const envoyer = () => {
    if (!pret) {
      setEssai(true)
      return
    }
    const d = {
      date: new Date().toISOString(),
      metier: nomMetier,
      ville: nomVille || 'pas encore choisie',
      prenom: prenom.trim(),
      nom: nom.trim(),
      email: email.trim(),
      tel: tel.replace(/\D/g, ''),
      etat: 'attente',
    }
    ajouter('demandes', d)
    setEnvoye(true)
    const texte = [
      'Demande PISTE : prévenez-moi quand ce sera prêt',
      '',
      `Métier : ${d.metier}`,
      `Ville : ${d.ville}`,
      `Nom : ${d.prenom} ${d.nom}`,
      `Email : ${d.email}`,
      `WhatsApp : +${d.tel}`,
      '',
      'DEMANDE:' + JSON.stringify(d),
    ].join('\n')
    window.open(
      `https://wa.me/${NEBULA_WHATSAPP}?text=${encodeURIComponent(texte)}`,
      '_blank',
      'noopener'
    )
  }

  if (envoye) {
    return (
      <div className="mt-5 rounded-2xl border-2 border-vert/40 bg-vert/8 p-5">
        <p className="font-semibold">C'est noté.</p>
        <p className="mt-1.5 text-[0.94rem] leading-relaxed text-sourd">
          On vous prévient sur WhatsApp et par email dès que{' '}
          {nomMetier.toLowerCase()}
          {nomVille ? ` à ${nomVille.toLowerCase()}` : ''} est prêt. Aucune date promise :
          ce sont les demandes reçues qui décident de l'ordre du travail, et la vôtre
          vient d'y entrer.
        </p>
      </div>
    )
  }

  return (
    <div className="mt-5 rounded-2xl border-2 border-brique/35 bg-brique/6 p-5">
      <p className="font-display text-[1.15rem] font-bold">
        {compacte ? 'Prévenez-moi quand ce sera prêt' : "Ce n'est pas encore relevé."}
      </p>
      <p className="mt-1.5 text-[0.94rem] leading-relaxed text-sourd">
        PISTE ne vend jamais ce qu'il n'a pas. Laissez-nous de quoi vous joindre : on vous
        écrit le jour où ces fiches existent, et votre demande décide de l'ordre du
        travail.
      </p>

      <div className="mt-5 space-y-4">
        {metier === 'autre' && (
          <label className="block">
            <span className="text-[0.85rem] font-semibold text-sourd">
              Quel métier cherchez-vous ?
            </span>
            <input
              value={metierLibre}
              onChange={(e) => onMetierLibre(e.target.value)}
              placeholder="coiffure, quincaillerie, pharmacie, garage, école…"
              className={`${champ} ${essai && nomMetier.length < 3 ? 'border-rouge' : 'border-trait'}`}
            />
          </label>
        )}
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-[0.85rem] font-semibold text-sourd">Votre prénom</span>
            <input
              value={prenom}
              onChange={(e) => setPrenom(e.target.value)}
              autoComplete="given-name"
              className={`${champ} ${essai && !prenom.trim() ? 'border-rouge' : 'border-trait'}`}
            />
          </label>
          <label className="block">
            <span className="text-[0.85rem] font-semibold text-sourd">Votre nom</span>
            <input
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              autoComplete="family-name"
              className={`${champ} ${essai && !nom.trim() ? 'border-rouge' : 'border-trait'}`}
            />
          </label>
        </div>
        <label className="block">
          <span className="text-[0.85rem] font-semibold text-sourd">Votre email</span>
          <input
            type="email"
            inputMode="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="vous@exemple.com"
            className={`${champ} ${essai && !emailOk ? 'border-rouge' : 'border-trait'}`}
          />
        </label>
        <label className="block">
          <span className="text-[0.85rem] font-semibold text-sourd">
            Votre WhatsApp, avec l'indicatif du pays
          </span>
          <input
            inputMode="tel"
            autoComplete="tel"
            value={tel}
            onChange={(e) => setTel(e.target.value)}
            placeholder="229 01 97 00 00 00"
            className={`${champ} ${essai && !telOk ? 'border-rouge' : 'border-trait'}`}
          />
        </label>
      </div>

      {essai && !pret && (
        <p className="mt-3 text-[0.9rem] text-rouge">
          Il manque de quoi vous joindre : prénom, nom, email et WhatsApp.
        </p>
      )}
      <Bouton className="mt-5 w-full sm:w-auto" onClick={envoyer}>
        Prévenez-moi quand c'est prêt
      </Bouton>
    </div>
  )
}
