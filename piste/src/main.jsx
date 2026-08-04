import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

/* Une seule racine, aucune bibliothèque de routage, aucun appel réseau au
   chargement : tout ce que la page affiche est dans le paquet. */
createRoot(document.getElementById('racine')).render(
  <StrictMode>
    <App />
  </StrictMode>
)
