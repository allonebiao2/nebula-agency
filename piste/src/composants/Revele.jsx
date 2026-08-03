import { useEffect, useRef, useState } from 'react'

/*
  UN SEUL IntersectionObserver pour toute l'application.
  Chaque élément qui veut se révéler s'y abonne ; la classe `.vu` fait le reste
  en CSS. Aucune boucle, aucun listener de scroll, aucune bibliothèque.
*/

let observateur = null
const abonnes = new WeakMap()

function obtenir() {
  if (observateur) return observateur
  observateur = new IntersectionObserver(
    (entrees) => {
      entrees.forEach((e) => {
        if (!e.isIntersecting) return
        e.target.classList.add('vu')
        const cb = abonnes.get(e.target)
        if (cb) cb()
        observateur.unobserve(e.target)
      })
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }
  )
  return observateur
}

export function useRevele(actif = true) {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el || !actif) return
    if (typeof IntersectionObserver === 'undefined') {
      el.classList.add('vu')
      return
    }
    const o = obtenir()
    o.observe(el)
    return () => o.unobserve(el)
  }, [actif])
  return ref
}

/* Un bloc qui se révèle. `d` = le retard, en millisecondes. */
export function Revele({ as: Balise = 'div', d = 0, className = '', children, ...reste }) {
  const ref = useRevele()
  return (
    <Balise ref={ref} className={`revele ${className}`} style={{ '--d': `${d}ms` }} {...reste}>
      {children}
    </Balise>
  )
}

/* Un compteur qui monte, une seule fois, quand il entre dans l'écran. */
export function Compteur({ jusqua, duree = 1400, className = '' }) {
  const [v, setV] = useState(0)
  const ref = useRevele()
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const doux = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (doux) {
      setV(jusqua)
      return
    }
    let brut = null
    let t0 = null
    const pas = (t) => {
      if (t0 === null) t0 = t
      const k = Math.min(1, (t - t0) / duree)
      setV(Math.round(jusqua * (1 - Math.pow(1 - k, 3))))
      if (k < 1) brut = requestAnimationFrame(pas)
    }
    const o = new MutationObserver(() => {
      if (el.classList.contains('vu')) {
        brut = requestAnimationFrame(pas)
        o.disconnect()
      }
    })
    o.observe(el, { attributes: true, attributeFilter: ['class'] })
    if (el.classList.contains('vu')) {
      brut = requestAnimationFrame(pas)
      o.disconnect()
    }
    return () => {
      o.disconnect()
      if (brut) cancelAnimationFrame(brut)
    }
  }, [jusqua, duree])
  return (
    <span ref={ref} className={`revele ${className}`}>
      {String(v).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}
    </span>
  )
}
