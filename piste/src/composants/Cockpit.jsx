import { useEffect, useState } from 'react'
import { NEBULA_WHATSAPP_JOLI } from '../donnees.js'
import { fcfa } from '../prix.js'
import {
  ETATS,
  ajouterAuCockpit,
  cockpit,
  csvCommandes,
  joliDelai,
  lienWhatsApp,
  lireMessage,
  majCockpit,
  resteAvantExpiration,
  retirerDuCockpit,
  telecharger,
} from '../etat.js'
import { Bouton, Chiffre } from './Ui.jsx'

/*
  LE COCKPIT DE MONGAZI.

  Il répond à une seule question, celle qu'il se pose chaque matin :
  **qui a payé, et qu'est-ce que je dois livrer aujourd'hui ?**

  ⚠️ CE QU'IL EST, EXACTEMENT. En V1 il n'y a pas de serveur : le cockpit ne
  reçoit rien tout seul. Mongazi colle ici le message WhatsApp que le client
  lui a envoyé, et le cockpit le range **dans son navigateur à lui**. C'est
  écrit à l'écran, en clair, parce qu'un outil qui laisse croire qu'il
  sauvegarde ailleurs finit par perdre les données de quelqu'un.

  Le loquet n'est pas une serrure : il n'y a rien à protéger côté serveur
  puisqu'il n'y a pas de serveur. Il évite seulement qu'un visiteur tombe sur
  cet écran par hasard et croie s'être trompé de site.
*/

const LOQUET = 'piste'

export default function Cockpit() {
  const [ouvert, setOuvert] = useState(() => sessionStorage.getItem('piste:loquet') === '1')
  const [liste, setListe] = useState([])
  const [filtre, setFiltre] = useState('tous')
  const [colle, setColle] = useState('')
  const [erreur, setErreur] = useState('')
  const [annulable, setAnnulable] = useState(null)

  useEffect(() => {
    if (ouvert) setListe(cockpit.lire())
  }, [ouvert])

  /* La suppression doit toujours être annulable : la règle de Boussole vaut
     ici aussi, et une commande perdue c'est un client qui attend son carnet. */
  useEffect(() => {
    if (!annulable) return
    const t = setTimeout(() => setAnnulable(null), 8000)
    return () => clearTimeout(t)
  }, [annulable])

  if (!ouvert) return <Loquet onOuvrir={() => setOuvert(true)} />

  const enregistrer = () => {
    const lu = lireMessage(colle)
    if (!lu.code || !lu.nombre) {
      setErreur(
        "Ce message ne ressemble pas à une commande PISTE : il manque le code ou le nombre de fiches. Collez le message entier, depuis « PISTE · commande » jusqu'à la dernière ligne."
      )
      return
    }
    setErreur('')
    setListe(ajouterAuCockpit(lu))
    setColle('')
  }

  /* ⚠️ Pas de `useMemo` ici : on est APRÈS le retour anticipé du loquet, et un
     hook posé après une sortie conditionnelle change de nombre entre deux
     rendus — React lâche l'erreur #310 et toute l'application disparaît. Ce
     comptage porte sur quelques dizaines de commandes : il n'a rien à
     mémoriser. */
  const visibles = liste.filter((c) => filtre === 'tous' || c.etat === filtre)
  const compte = { tous: liste.length }
  ETATS.forEach((e) => (compte[e.cle] = liste.filter((c) => c.etat === e.cle).length))

  const aLivrer = liste.filter((c) => c.etat === 'payee').length
  const encaisse = liste
    .filter((c) => c.etat === 'payee' || c.etat === 'livree')
    .reduce((s, c) => s + (c.total || 0), 0)

  return (
    <div className="min-h-screen bg-encre pb-24 text-papier">
      <div className="mx-auto w-full max-w-[64rem] px-5 py-10 sm:px-8">
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-braise">
              PISTE · cockpit
            </p>
            <h1 className="mt-2 text-[clamp(1.9rem,6vw,2.8rem)]">
              {aLivrer > 0 ? (
                <>
                  {aLivrer} carnet{aLivrer > 1 ? 's' : ''} à livrer aujourd'hui.
                </>
              ) : (
                'Rien à livrer pour le moment.'
              )}
            </h1>
          </div>
          <div className="text-right">
            <p className="text-[0.72rem] uppercase tracking-[0.16em] text-sourd">Encaissé</p>
            <Chiffre className="text-[1.7rem] text-braise">{fcfa(encaisse)}</Chiffre>
          </div>
        </header>

        <p className="mt-5 rounded-xl border border-traitsombre bg-nuit px-4 py-3 text-[0.86rem] leading-relaxed text-sable">
          Ces commandes sont rangées <b className="text-papier">dans ce navigateur</b>, sur
          cet appareil. Elles ne partent nulle part et personne d'autre ne les voit,
          mais elles ne suivent pas non plus d'un téléphone à l'autre. Sortez le CSV
          régulièrement : c'est votre seule sauvegarde tant que la base n'existe pas.
        </p>

        {/* coller une commande */}
        <section className="mt-8 rounded-2xl border border-traitsombre bg-encre2 p-5">
          <h2 className="text-[1.2rem]">Ranger une commande reçue</h2>
          <p className="mt-1.5 text-[0.89rem] leading-relaxed text-sable">
            Ouvrez WhatsApp, copiez le message du client en entier, collez-le ici.
          </p>
          <textarea
            rows={4}
            value={colle}
            onChange={(e) => setColle(e.target.value)}
            placeholder="PISTE · commande 8C2QB8 …"
            className="mt-3 w-full resize-y rounded-xl border border-traitsombre bg-nuit px-4 py-3 text-papier outline-none placeholder:text-sourd focus:border-braise"
          />
          {erreur && (
            <p className="mt-3 rounded-xl border border-rougeclair/40 bg-rouge/20 px-4 py-3 text-[0.88rem] text-rougeclair" role="alert">
              {erreur}
            </p>
          )}
          <div className="mt-3 flex flex-wrap gap-3">
            <Bouton ton="pleinClair" onClick={enregistrer} disabled={!colle.trim()}>
              Ranger cette commande
            </Bouton>
            {liste.length > 0 && (
              <Bouton
                ton="contourSombre"
                onClick={() =>
                  telecharger(
                    `piste-commandes-${new Date().toISOString().slice(0, 10)}.csv`,
                    csvCommandes(liste)
                  )
                }
              >
                Sortir le CSV ({liste.length})
              </Bouton>
            )}
          </div>
        </section>

        {/* filtres */}
        {liste.length > 0 && (
          <div className="mt-8 flex flex-wrap gap-2">
            {[{ cle: 'tous', nom: 'Toutes' }, ...ETATS].map((e) => (
              <button
                key={e.cle}
                type="button"
                onClick={() => setFiltre(e.cle)}
                aria-pressed={filtre === e.cle}
                className={`min-h-[44px] rounded-full border px-4 text-[0.9rem] font-semibold ${
                  filtre === e.cle
                    ? 'border-braise bg-braise text-encre'
                    : 'border-traitsombre text-sable'
                }`}
              >
                {e.nom} ({compte[e.cle] || 0})
              </button>
            ))}
          </div>
        )}

        {/* la liste */}
        <div className="mt-6 space-y-3">
          {visibles.length === 0 && (
            <div className="rounded-2xl border border-dashed border-traitsombre px-5 py-10 text-center">
              <p className="text-[1.05rem]">
                {liste.length === 0
                  ? 'Aucune commande rangée pour l\'instant.'
                  : 'Aucune commande dans cet état.'}
              </p>
              <p className="mt-2 text-[0.9rem] text-sourd">
                {liste.length === 0
                  ? 'Quand un client envoie sa commande sur WhatsApp, collez son message ci-dessus.'
                  : 'Changez de filtre pour voir les autres.'}
              </p>
            </div>
          )}

          {visibles.map((c) => (
            <Ligne
              key={c.id}
              c={c}
              onEtat={(etat) => setListe(majCockpit(c.id, { etat, [`${etat}Le`]: Date.now() }))}
              onNote={(note) => setListe(majCockpit(c.id, { note }))}
              onRetirer={() => {
                setAnnulable(c)
                setListe(retirerDuCockpit(c.id))
              }}
            />
          ))}
        </div>
      </div>

      {annulable && (
        <div className="fixed inset-x-0 bottom-0 z-50 border-t border-traitsombre bg-nuit px-5 py-3">
          <div className="mx-auto flex max-w-[64rem] flex-wrap items-center justify-between gap-3">
            <p className="text-[0.9rem]">
              Commande <b>{annulable.code}</b> retirée.
            </p>
            <Bouton
              ton="pleinClair"
              onClick={() => {
                setListe(ajouterAuCockpit(annulable))
                setAnnulable(null)
              }}
            >
              Annuler
            </Bouton>
          </div>
        </div>
      )}
    </div>
  )
}

/* ------------------------------------------------------------- la ligne -- */

function Ligne({ c, onEtat, onNote, onRetirer }) {
  const [ouvert, setOuvert] = useState(false)
  const etat = ETATS.find((e) => e.cle === c.etat) || ETATS[0]
  const suivant = ETATS[ETATS.findIndex((e) => e.cle === c.etat) + 1]
  const reste = c.etat === 'recue' ? resteAvantExpiration(c.cree) : null
  const perime = reste !== null && reste <= 0

  const teinte = {
    recue: 'border-braise/40',
    payee: 'border-vertclair/40',
    livree: 'border-traitsombre',
  }[c.etat]

  return (
    <article className={`rounded-2xl border bg-encre2 ${teinte}`}>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-3 px-5 py-4">
        <Chiffre className="text-[1.35rem] tracking-[0.1em] text-braise">{c.code}</Chiffre>

        <span
          className={`rounded-full px-3 py-1 text-[0.76rem] font-semibold ${
            c.etat === 'recue'
              ? perime
                ? 'bg-rouge/25 text-rougeclair'
                : 'bg-braise/20 text-braise'
              : c.etat === 'payee'
                ? 'bg-vertclair/15 text-vertclair'
                : 'bg-sable/15 text-sable'
          }`}
        >
          {perime ? 'expirée' : etat.nom}
        </span>

        <div className="min-w-[10rem] flex-1">
          <p className="font-semibold">{c.nom || <span className="text-rougeclair">nom manquant</span>}</p>
          <p className="text-[0.84rem] text-sourd">
            {c.nombre} fiches · {c.metier || '?'} · {c.ville || '?'}
          </p>
        </div>

        <Chiffre className="text-[1.15rem]">{c.total ? fcfa(c.total) : '?'}</Chiffre>

        {suivant && (
          <Bouton ton="pleinClair" className="px-4 text-[0.88rem]" onClick={() => onEtat(suivant.cle)}>
            {etat.suite}
          </Bouton>
        )}

        <button
          type="button"
          onClick={() => setOuvert(!ouvert)}
          aria-expanded={ouvert}
          className="min-h-[44px] px-2 text-[0.88rem] font-semibold text-sable underline underline-offset-4"
        >
          {ouvert ? 'Replier' : 'Détail'}
        </button>
      </div>

      {c.etat === 'recue' && !perime && (
        <p className="border-t border-traitsombre px-5 py-2 text-[0.82rem] text-sourd">
          Expire dans {joliDelai(reste)} si elle n'est pas payée.
        </p>
      )}

      {ouvert && (
        <div className="border-t border-traitsombre px-5 py-4">
          <dl className="grid gap-x-6 gap-y-2 text-[0.88rem] sm:grid-cols-2">
            {[
              ['Email', c.email],
              ['WhatsApp', c.whatsapp],
              ['Paie depuis', c.momo ? `${c.momo} (${c.reseau || '?'})` : ''],
              ['Quartier', c.quartier],
              ['En plus', c.options],
              ['Vend', c.offre],
            ].map(([k, v]) => (
              <div key={k} className="border-b border-traitsombre/70 pb-1.5">
                <dt className="text-[0.74rem] uppercase tracking-[0.12em] text-sourd">{k}</dt>
                <dd className={v ? '' : 'text-rougeclair'}>{v || 'manquant'}</dd>
              </div>
            ))}
          </dl>

          <label className="mt-4 block text-[0.8rem] uppercase tracking-[0.12em] text-sourd" htmlFor={`note-${c.id}`}>
            Note
          </label>
          <input
            id={`note-${c.id}`}
            defaultValue={c.note || ''}
            onBlur={(e) => onNote(e.target.value)}
            placeholder="rapproché sur MoMo le 04/08 · liste préparée · …"
            className="mt-1.5 min-h-[44px] w-full rounded-xl border border-traitsombre bg-nuit px-3.5 py-2 outline-none placeholder:text-sourd focus:border-braise"
          />

          <div className="mt-4 flex flex-wrap gap-3">
            {c.whatsapp && (
              <Bouton
                ton="contourSombre"
                className="text-[0.88rem]"
                href={lienWhatsApp(
                  `Bonjour ${c.nom || ''}, votre commande PISTE ${c.code} est bien reçue.`,
                  String(c.whatsapp).replace(/\D/g, '')
                )}
                target="_blank"
                rel="noopener"
              >
                Écrire au client
              </Bouton>
            )}
            <Bouton ton="nu" onClick={onRetirer}>
              Retirer du cockpit
            </Bouton>
          </div>

          {c.brut && (
            <details className="mt-4">
              <summary className="cursor-pointer text-[0.84rem] text-sourd">
                Le message reçu, tel quel
              </summary>
              <pre className="mt-2 whitespace-pre-wrap rounded-xl border border-traitsombre bg-nuit px-3.5 py-3 font-sans text-[0.82rem] leading-relaxed text-sable">
                {c.brut}
              </pre>
            </details>
          )}
        </div>
      )}
    </article>
  )
}

/* -------------------------------------------------------------- loquet --- */

function Loquet({ onOuvrir }) {
  const [mot, setMot] = useState('')
  const [rate, setRate] = useState(false)
  const essayer = (e) => {
    e.preventDefault()
    if (mot.trim().toLowerCase() === LOQUET) {
      sessionStorage.setItem('piste:loquet', '1')
      onOuvrir()
    } else {
      setRate(true)
    }
  }
  return (
    <div className="flex min-h-screen items-center justify-center bg-encre px-5 text-papier">
      <form onSubmit={essayer} className="w-full max-w-[22rem]">
        <p className="text-[0.72rem] font-semibold uppercase tracking-[0.2em] text-braise">
          PISTE · cockpit
        </p>
        <h1 className="mt-2 text-[2rem]">Réservé.</h1>
        <p className="mt-3 text-[0.9rem] leading-relaxed text-sable">
          Cet écran sert à suivre les commandes. Si vous cherchez à commander,
          c'est <a className="text-braise underline underline-offset-4" href="#/commander">par ici</a>.
        </p>
        <input
          type="password"
          value={mot}
          onChange={(e) => {
            setMot(e.target.value)
            setRate(false)
          }}
          placeholder="mot de passage"
          aria-label="mot de passage"
          className={`mt-5 min-h-[48px] w-full rounded-xl border bg-nuit px-4 py-3 outline-none placeholder:text-sourd ${
            rate ? 'border-rougeclair' : 'border-traitsombre focus:border-braise'
          }`}
        />
        {rate && <p className="mt-2 text-[0.86rem] text-rougeclair">Ce n'est pas ça.</p>}
        <Bouton ton="pleinClair" className="mt-4 w-full" comme="button" type="submit">
          Entrer
        </Bouton>
        <p className="mt-6 text-[0.8rem] leading-relaxed text-sourd">
          Un loquet, pas une serrure : les commandes sont rangées dans ce
          navigateur, il n'y a rien à voler ailleurs. Une question :{' '}
          {NEBULA_WHATSAPP_JOLI}.
        </p>
      </form>
    </div>
  )
}
