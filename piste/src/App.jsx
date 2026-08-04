import { useCallback, useEffect, useState } from 'react'
import Vitrine from './composants/Vitrine.jsx'
import Questionnaire from './composants/Questionnaire.jsx'
import Cockpit from './composants/Cockpit.jsx'
import Origine from './composants/Origine.jsx'

/*
  Trois écrans, une adresse. Le routage passe par le `#` : Cloudflare Pages sert
  un seul fichier, aucune règle de réécriture à poser, et un lien partagé
  retombe toujours sur quelque chose.

  Les ancres internes de la vitrine (#fiche) ne sont pas des routes : seules
  celles qui commencent par `#/` en sont.
*/

const ROUTES = {
  '#/': 'vitrine',
  '#/commander': 'commander',
  '#/donnees': 'origine',
  '#/cockpit': 'cockpit',
}

function lireRoute() {
  if (typeof window === 'undefined') return 'vitrine'
  const h = window.location.hash
  if (!h.startsWith('#/')) return null
  return ROUTES[h.replace(/\/$/, '') || '#/'] || 'vitrine'
}

export default function App() {
  const [route, setRoute] = useState(() => lireRoute() || 'vitrine')

  useEffect(() => {
    const surHash = () => {
      const r = lireRoute()
      if (r) setRoute(r)
    }
    window.addEventListener('hashchange', surHash)
    return () => window.removeEventListener('hashchange', surHash)
  }, [])

  const aller = useCallback((h) => {
    if (window.location.hash === h) {
      const r = lireRoute()
      if (r) setRoute(r)
      window.scrollTo(0, 0)
      return
    }
    window.location.hash = h
    window.scrollTo(0, 0)
  }, [])

  if (route === 'commander') return <Questionnaire aller={aller} />
  if (route === 'origine') return <Origine aller={aller} />
  if (route === 'cockpit') return <Cockpit aller={aller} />
  return <Vitrine aller={aller} />
}
