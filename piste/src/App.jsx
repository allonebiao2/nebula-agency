import { useCallback, useEffect, useState } from 'react'
import Vitrine from './composants/Vitrine.jsx'
import Questionnaire from './composants/Questionnaire.jsx'
import Cockpit from './composants/Cockpit.jsx'
import Origine from './composants/Origine.jsx'
import Carnet from './composants/Carnet.jsx'
import Recu from './composants/Recu.jsx'
import { marquerVisite } from './supabase.js'

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

/* Le carnet d'un client : `#/carnet/<jeton>`. Le jeton reste dans le `#`,
   qui n'est JAMAIS envoyé au serveur. Le lien est donc privé par construction,
   sans compte ni mot de passe (décisions 24, 29 et 33). */
export function lireJeton(h) {
  const m = (h || '').match(/^#\/(?:carnet|recu)\/([A-Za-z0-9_-]{8,})/)
  return m ? m[1] : ''
}

function lireRoute(h) {
  if (typeof window === 'undefined') return 'vitrine'
  if (!h || !h.startsWith('#/')) return null
  if (h.startsWith('#/carnet')) return 'carnet'
  if (h.startsWith('#/recu')) return 'recu'
  return ROUTES[h.replace(/\/$/, '') || '#/'] || 'vitrine'
}

export default function App() {
  /* On garde le HASH, pas seulement la route.

     ⚠️ Garder la route seule cachait un vrai défaut : passer d'un lien de
     carnet à un autre laisse la route sur « carnet », donc React ne redessine
     pas, donc le carnet affiché reste l'ancien. Un client qui suit deux liens
     à la suite voyait le premier carnet, ou pire, une erreur. */
  const [hash, setHash] = useState(() =>
    typeof window === 'undefined' ? '#/' : window.location.hash || '#/'
  )
  const route = lireRoute(hash) || 'vitrine'

  useEffect(() => {
    const surHash = () => {
      if (window.location.hash.startsWith('#/')) setHash(window.location.hash)
    }
    window.addEventListener('hashchange', surHash)
    return () => window.removeEventListener('hashchange', surHash)
  }, [])

  /* ⚠️ On ne compte PAS les passages dans le cockpit : c'est l'écran de
     Mongazi, pas celui d'un visiteur. Le compter gonflerait l'entonnoir avec
     nos propres visites, et l'entonnoir servirait à se mentir. */
  useEffect(() => {
    if (route === 'cockpit') return
    marquerVisite(route === 'carnet' ? 'carnet' : 'arrivee')
  }, [route])

  const aller = useCallback((h) => {
    if (window.location.hash === h) {
      setHash(h)
      window.scrollTo(0, 0)
      return
    }
    window.location.hash = h
    window.scrollTo(0, 0)
  }, [])

  if (route === 'carnet') return <Carnet jeton={lireJeton(hash)} aller={aller} />
  if (route === 'recu') return <Recu jeton={lireJeton(hash)} aller={aller} />
  if (route === 'commander') return <Questionnaire aller={aller} />
  if (route === 'origine') return <Origine aller={aller} />
  if (route === 'cockpit') return <Cockpit aller={aller} />
  return <Vitrine aller={aller} />
}
