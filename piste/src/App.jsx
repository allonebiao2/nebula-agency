import { useEffect, useState } from 'react'
import {
  ADRESSE,
  EMAIL,
  MINIMUM,
  NEBULA_WHATSAPP_JOLI,
  TOTAL_FICHES,
} from './donnees.js'
import { BASE, fcfa } from './prix.js'
import { allerA, maCommande, routeCourante } from './etat.js'
import { Bouton } from './composants/Ui.jsx'
import Vitrine from './composants/Vitrine.jsx'
import Questionnaire from './composants/Questionnaire.jsx'
import Paiement from './composants/Paiement.jsx'
import Origine from './composants/Origine.jsx'
import Cockpit from './composants/Cockpit.jsx'

/*
  L'APPLICATION.

  Routage par ancre : un paquet statique n'a pas de serveur pour réécrire les
  URL, et `#/commander` marche partout, sans règle de redirection, y compris
  quand quelqu'un colle le lien dans WhatsApp.

    #/            la vitrine
    #/commander   le questionnaire, puis l'écran de paiement
    #/origine     d'où vient la donnée
    #/cockpit     le suivi des commandes de Mongazi
*/

export default function App() {
  const [route, setRoute] = useState(routeCourante)
  const [commande, setCommande] = useState(() => maCommande.lire())

  useEffect(() => {
    const bouge = () => {
      setRoute(routeCourante())
      window.scrollTo({ top: 0, behavior: 'auto' })
    }
    addEventListener('hashchange', bouge)
    return () => removeEventListener('hashchange', bouge)
  }, [])

  const commander = () => {
    setCommande(null)
    maCommande.effacer()
    allerA('commander')
  }

  if (route === 'cockpit') return <Cockpit />

  return (
    <>
      <Entete route={route} onCommander={commander} />
      <main id="contenu">
        {route === 'accueil' && <Vitrine onCommander={commander} />}
        {route === 'origine' && <Origine />}
        {route === 'commander' &&
          (commande ? (
            <Paiement
              commande={commande}
              onRecommencer={() => {
                setCommande(null)
                maCommande.effacer()
              }}
            />
          ) : (
            <Questionnaire onEnvoyee={setCommande} />
          ))}
      </main>
      <Pied />
    </>
  )
}

/* -------------------------------------------------------------- l'entête - */

function Entete({ route, onCommander }) {
  const [pose, setPose] = useState(false)

  useEffect(() => {
    const auScroll = () => setPose(scrollY > 24)
    auScroll()
    addEventListener('scroll', auScroll, { passive: true })
    return () => removeEventListener('scroll', auScroll)
  }, [])

  return (
    <header
      className={`sticky top-0 z-30 border-b transition-colors duration-300 ${
        pose ? 'border-traitsombre bg-encre/95 backdrop-blur' : 'border-transparent bg-encre'
      }`}
    >
      <a
        href="#contenu"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-braise focus:px-4 focus:py-2 focus:text-encre"
      >
        Aller au contenu
      </a>
      <div className="mx-auto flex h-16 w-full max-w-[68rem] items-center justify-between gap-4 px-5 sm:px-8">
        <a
          href="#/"
          className="flex min-h-[44px] items-center gap-2.5 text-papier"
          aria-label="PISTE by NEBULA, accueil"
        >
          <svg viewBox="0 0 32 32" className="h-7 w-7 shrink-0" aria-hidden="true">
            <path
              d="M4 25C10 25 9 8 17 8s7 12 10 12"
              fill="none"
              stroke="var(--color-braise)"
              strokeWidth="2.6"
              strokeLinecap="round"
              strokeDasharray="4 4"
            />
            <circle cx="27" cy="20" r="3.2" fill="var(--color-braise)" />
          </svg>
          <span className="font-display text-[1.15rem] font-bold tracking-tight">
            PISTE <span className="text-sourd">by NEBULA</span>
          </span>
        </a>

        <nav className="flex items-center gap-1 sm:gap-3">
          <a
            href="#/origine"
            className={`hidden min-h-[44px] items-center px-3 text-[0.9rem] sm:flex ${
              route === 'origine' ? 'text-braise' : 'text-sable hover:text-papier'
            }`}
          >
            D'où vient la donnée
          </a>
          {route !== 'commander' && (
            <Bouton ton="pleinClair" className="px-5 text-[0.88rem]" onClick={onCommander}>
              Commander
            </Bouton>
          )}
        </nav>
      </div>
    </header>
  )
}

/* ---------------------------------------------------------------- le pied */

function Pied() {
  return (
    <footer className="border-t border-traitsombre bg-nuit text-sable">
      <div className="mx-auto w-full max-w-[68rem] px-5 py-12 sm:px-8">
        <div className="grid gap-8 sm:grid-cols-[1.3fr_1fr_1fr]">
          <div>
            <p className="font-display text-[1.2rem] font-bold text-papier">
              PISTE <span className="text-sourd">by NEBULA</span>
            </p>
            <p className="mt-3 max-w-[28rem] text-[0.9rem] leading-relaxed">
              Des commerçants à qui parler demain matin. {TOTAL_FICHES} fiches en
              stock, à partir de {fcfa(BASE)} la fiche, minimum {MINIMUM} fiches,
              livré sous 24 heures.
            </p>
          </div>

          <div>
            <p className="text-[0.74rem] font-semibold uppercase tracking-[0.16em] text-sourd">
              Le service
            </p>
            <ul className="mt-3 space-y-2 text-[0.9rem]">
              <li>
                <a className="hover:text-papier" href="#/commander">
                  Composer une commande
                </a>
              </li>
              <li>
                <a className="hover:text-papier" href="#/origine">
                  D'où vient la donnée
                </a>
              </li>
              <li>
                <a className="hover:text-papier" href="#bareme">
                  Le barème
                </a>
              </li>
            </ul>
          </div>

          <div>
            <p className="text-[0.74rem] font-semibold uppercase tracking-[0.16em] text-sourd">
              Nous joindre
            </p>
            <ul className="mt-3 space-y-2 text-[0.9rem]">
              <li>
                <a className="hover:text-papier" href={`https://wa.me/${NEBULA_WHATSAPP_JOLI.replace(/\D/g, '')}`} target="_blank" rel="noopener">
                  WhatsApp {NEBULA_WHATSAPP_JOLI}
                </a>
              </li>
              <li>
                <a className="hover:text-papier" href={`mailto:${EMAIL}`}>
                  {EMAIL}
                </a>
              </li>
              <li>Cotonou, Bénin</li>
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-between gap-3 border-t border-traitsombre pt-6 text-[0.82rem] text-sourd">
          <p>
            {ADRESSE} · un produit NEBULA Agency
          </p>
          <p>
            Un commerce veut sortir de la base ?{' '}
            <a className="text-braise underline underline-offset-4" href="#/origine">
              C'est un message
            </a>
            .
          </p>
        </div>
      </div>
    </footer>
  )
}
