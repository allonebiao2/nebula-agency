import { useEffect, useState } from 'react'
import { EMAIL_ENVOI, NEBULA_WHATSAPP, NEBULA_WHATSAPP_JOLI } from '../donnees.js'
import { fcfa, nombre, SUPPLEMENTS } from '../prix.js'
import { ouvrirCarnet } from '../supabase.js'
import { Bouton } from './Ui.jsx'

/*
  LE REÇU · pour la comptabilité de l'acheteur (décision 35).

  POURQUOI PAS UN PDF FABRIQUÉ EN JAVASCRIPT
  Une bibliothèque de PDF pèse plus lourd que tout le reste du site réuni, et
  la règle du dépôt est claire : aucune bibliothèque. Le navigateur sait déjà
  fabriquer un PDF : « Imprimer » puis « Enregistrer au format PDF ». C'est un
  vrai PDF, il est parfait, et il coûte zéro octet.

  Cette page est donc pensée POUR le papier : fond blanc, encre noire, aucune
  couleur qui vide une cartouche, et tout ce qui ne s'imprime pas (les boutons)
  disparaît à l'impression.

  ⚠️ CE QUE CE REÇU N'EST PAS. Ce n'est pas une facture normalisée e-MECeF.
  C'est écrit dessus, en toutes lettres. Une entreprise qui a besoin d'une
  facture normalisée doit la demander, et personne ne doit découvrir le
  problème au moment de sa déclaration.
*/

function jolieDate(iso) {
  const MOIS = [
    'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
  ]
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return `${d.getDate()} ${MOIS[d.getMonth()]} ${d.getFullYear()}`
}

export default function Recu({ jeton, aller }) {
  const [etat, setEtat] = useState('chargement')
  const [c, setC] = useState(null)

  useEffect(() => {
    let vivant = true
    if (!jeton) {
      setEtat('introuvable')
      return
    }
    ouvrirCarnet(jeton)
      .then((x) => {
        if (!vivant) return
        if (!x) return setEtat('introuvable')
        setC(x)
        setEtat('pret')
      })
      .catch(() => vivant && setEtat('panne'))
    return () => {
      vivant = false
    }
  }, [jeton])

  if (etat !== 'pret') {
    return (
      <main className="mx-auto flex min-h-dvh max-w-[34rem] flex-col justify-center px-5 py-16">
        <h1 className="text-[clamp(1.5rem,6vw,2rem)]">
          {etat === 'chargement' ? 'Un instant…' : 'Ce reçu n’existe pas.'}
        </h1>
        {etat !== 'chargement' && (
          <p className="mt-3 text-[0.95rem] leading-relaxed text-sourd">
            Le lien est peut-être incomplet. Écrivez-nous, on vous le renvoie entier.
          </p>
        )}
      </main>
    )
  }

  const cmd = c.commande || {}
  const cl = c.client || {}
  const options = (cmd.options || []).map((cle) => SUPPLEMENTS.find((s) => s.cle === cle)).filter(Boolean)
  const n = cmd.n || (c.fiches || []).length

  return (
    <main className="recu mx-auto max-w-[46rem] px-5 py-8 sm:px-8 sm:py-12">
      {/* -------------------------------------- ce qui ne s'imprime pas ---- */}
      <div className="sansimpression mb-8 flex flex-wrap items-center gap-3">
        <Bouton onClick={() => window.print()}>Imprimer ou enregistrer en PDF</Bouton>
        <Bouton ton="contour" onClick={() => aller(`#/carnet/${jeton}`)}>
          Revenir à mon carnet
        </Bouton>
      </div>

      <article className="rounded-2xl border border-trait bg-creme p-6 sm:p-9">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-trait pb-5">
          <div>
            <p className="font-display text-[1.15rem] font-bold tracking-tight text-encre">
              PISTE <span className="font-normal text-sourd">by NEBULA</span>
            </p>
            <p className="mt-1 text-[0.8rem] leading-relaxed text-sourd">
              NEBULA Agency · Cotonou, Bénin
              <br />
              {NEBULA_WHATSAPP_JOLI} · {EMAIL_ENVOI}
            </p>
          </div>
          <div className="text-right">
            <p className="text-[0.7rem] font-semibold uppercase tracking-[0.18em] text-brique">
              Reçu
            </p>
            <p className="font-mono text-[1.05rem] font-bold tabular-nums text-encre">
              {c.reference}
            </p>
            <p className="mt-1 text-[0.8rem] text-sourd">{jolieDate(c.cree_le)}</p>
          </div>
        </header>

        <section className="grid gap-5 border-b border-trait py-5 sm:grid-cols-2">
          <div>
            <p className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-sourd">
              Client
            </p>
            <p className="mt-1.5 text-[0.95rem] font-semibold text-encre">
              {[cl.prenom, cl.nom].filter(Boolean).join(' ') || 'Nom à compléter'}
            </p>
            {cl.email && <p className="text-[0.85rem] text-sourd">{cl.email}</p>}
            {(cl.tel || cl.whatsapp) && (
              <p className="font-mono text-[0.85rem] tabular-nums text-sourd">
                +{cl.tel || cl.whatsapp}
              </p>
            )}
          </div>
          <div>
            <p className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-sourd">
              Livré
            </p>
            <p className="mt-1.5 text-[0.95rem] text-encre">
              {cmd.metierNom || 'Fiches'}
              {cmd.villeNom ? ` · ${cmd.villeNom}` : ''}
            </p>
            <p className="text-[0.85rem] text-sourd">
              {nombre(n)} fiches de prospection
            </p>
          </div>
        </section>

        {/* ------------------------------------------------ le détail ------ */}
        <table className="w-full border-collapse py-5 text-[0.9rem]">
          <thead>
            <tr className="border-b border-trait text-left text-[0.72rem] uppercase tracking-[0.14em] text-sourd">
              <th className="py-3 font-semibold">Désignation</th>
              <th className="py-3 text-right font-semibold">Unité</th>
              <th className="py-3 text-right font-semibold">Nombre</th>
              <th className="py-3 text-right font-semibold">Montant</th>
            </tr>
          </thead>
          <tbody className="text-encre">
            <tr className="border-b border-trait/60">
              <td className="py-3">Fiche de prospection</td>
              <td className="py-3 text-right tabular-nums">100 F</td>
              <td className="py-3 text-right tabular-nums">{nombre(n)}</td>
              <td className="py-3 text-right tabular-nums">{fcfa(100 * n)}</td>
            </tr>
            {options.map((o) => (
              <tr key={o.cle} className="border-b border-trait/60">
                <td className="py-3">{o.nom}</td>
                <td className="py-3 text-right tabular-nums">{o.prix} F</td>
                <td className="py-3 text-right tabular-nums">{nombre(n)}</td>
                <td className="py-3 text-right tabular-nums">{fcfa(o.prix * n)}</td>
              </tr>
            ))}
            {cmd.taux > 0 && (
              <tr className="border-b border-trait/60">
                <td className="py-3" colSpan={3}>
                  Remise au volume ({Math.round(cmd.taux * 100)} %)
                </td>
                <td className="py-3 text-right tabular-nums">− {fcfa(cmd.remise || 0)}</td>
              </tr>
            )}
            <tr>
              <td className="pt-4 text-[1rem] font-semibold" colSpan={3}>
                Total réglé
              </td>
              <td className="pt-4 text-right font-display text-[1.4rem] font-bold tabular-nums">
                {fcfa(cmd.total || 0)}
              </td>
            </tr>
          </tbody>
        </table>

        <footer className="mt-6 border-t border-trait pt-5 text-[0.8rem] leading-relaxed text-sourd">
          <p>
            Réglé par Mobile Money. Ces {nombre(n)} fiches sont réservées à ce client seul
            pendant 90 jours à compter de la livraison. Toute fiche injoignable est remplacée
            sans frais, sur simple signalement depuis le carnet.
          </p>
          <p className="mt-3">
            <b className="font-semibold text-encre">Ce document est un reçu, pas une facture
            normalisée.</b>{' '}
            Si votre comptabilité exige une facture normalisée, demandez-la nous : écrivez au{' '}
            {NEBULA_WHATSAPP_JOLI}. Mieux vaut la demander maintenant qu'au moment de votre
            déclaration.
          </p>
        </footer>
      </article>

      <p className="sansimpression mt-6 text-center text-[0.8rem] text-sourd">
        Pour obtenir un PDF : « Imprimer », puis « Enregistrer au format PDF » dans la
        destination.{' '}
        <a
          className="underline underline-offset-4"
          href={`https://wa.me/${NEBULA_WHATSAPP}`}
          target="_blank"
          rel="noopener"
        >
          Un souci ? Écrivez-nous.
        </a>
      </p>
    </main>
  )
}
