import { useEffect, useRef, useState } from 'react'

/*
  LE RELIEF · la scène 3D du héros (décision 77).

  POURQUOI SANS BIBLIOTHÈQUE
  Three.js pèse une quarantaine de kilo-octets compressés, et la règle du dépôt
  est claire : aucune bibliothèque. Surtout, l'acheteur de PISTE est souvent en
  3G sur un téléphone modeste. Quarante kilo-octets pour une décoration, c'est
  une seconde d'attente avant de voir la promesse.

  Alors c'est de la VRAIE 3D, faite avec ce que le navigateur sait déjà faire :
  `perspective` et `rotateX` posent un sol qui fuit vers l'horizon, `translateZ`
  décolle la trace au-dessus de ce sol, et chaque repère projette son ombre à sa
  verticale. Le pointeur fait tourner la scène. Coût : zéro octet de plus, et
  ça tient les 60 images par seconde sur un appareil d'entrée de gamme.

  CE QUI L'ÉTEINT, ET C'EST VOULU
  · `prefers-reduced-motion`
  · moins de 4 cœurs, ou une mémoire déclarée sous 4 Go
  · un écran de moins de 640 px de large : on garde le sol, on coupe la
    poursuite du pointeur, qui n'a aucun sens au doigt.
*/

const CHEMIN =
  'M18 270 C 96 274, 104 196, 172 192 S 244 216, 292 156 S 360 66, 444 86 S 520 126, 552 96'

/* Les repères, en fraction de la longueur du tracé. */
const JALONS = [0.06, 0.3, 0.55, 0.78, 0.97]

function appareilModeste() {
  if (typeof navigator === 'undefined') return true
  try {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return true
    const c = navigator.hardwareConcurrency
    if (c && c < 4) return true
    const m = navigator.deviceMemory
    if (m && m < 4) return true
  } catch (e) {}
  return false
}

export default function Relief() {
  const scene = useRef(null)
  const chemin = useRef(null)
  const [pts, setPts] = useState([])
  const [bout, setBout] = useState(null)
  const [vivant, setVivant] = useState(false)
  const [doux, setDoux] = useState(false)

  useEffect(() => {
    setDoux(appareilModeste())
    const t = setTimeout(() => setVivant(true), 60)
    return () => clearTimeout(t)
  }, [])

  /* Les repères tombent exactement sur la courbe, quelle qu'elle soit.

     ⚠️ Ils sont dessinés DANS le SVG, pas à côté. La première version les
     posait en `position: absolute` par-dessus, ce qui obligeait à convertir les
     coordonnées du dessin en pourcentages de la scène. Deux systèmes de
     coordonnées, une couche 3D entre les deux, et des repères qui flottaient à
     côté de la courbe sans qu'on les voie. Dans le SVG, il n'y a rien à
     convertir : le point EST sur la courbe. */
  useEffect(() => {
    const p = chemin.current
    if (!p || typeof p.getTotalLength !== 'function') return
    const L = p.getTotalLength()
    if (!L) return
    setPts(
      JALONS.map((k) => {
        const pt = p.getPointAtLength(L * k)
        return { k, x: pt.x, y: pt.y }
      })
    )
    const f = p.getPointAtLength(L)
    setBout({ x: f.x, y: f.y })
  }, [])

  /* La poursuite du pointeur. Une seule écriture par image, sur `transform`
     uniquement : jamais une propriété de mise en page, sinon le navigateur
     recalcule tout à chaque mouvement de souris. */
  useEffect(() => {
    if (doux) return
    const el = scene.current
    if (!el || window.innerWidth < 640) return
    let brut = { x: 0, y: 0 }
    let pose = { x: 0, y: 0 }
    let image = 0
    const bouger = (e) => {
      const r = el.getBoundingClientRect()
      brut.x = ((e.clientX - r.left) / r.width - 0.5) * 2
      brut.y = ((e.clientY - r.top) / r.height - 0.5) * 2
    }
    const tourner = () => {
      /* on suit de loin : un décor qui colle au pointeur donne le tournis */
      pose.x += (brut.x - pose.x) * 0.06
      pose.y += (brut.y - pose.y) * 0.06
      el.style.setProperty('--tx', `${(-pose.x * 5).toFixed(2)}deg`)
      el.style.setProperty('--ty', `${(pose.y * 3.5).toFixed(2)}deg`)
      image = requestAnimationFrame(tourner)
    }
    window.addEventListener('pointermove', bouger, { passive: true })
    image = requestAnimationFrame(tourner)
    return () => {
      window.removeEventListener('pointermove', bouger)
      cancelAnimationFrame(image)
    }
  }, [doux])

  return (
    <div
      ref={scene}
      className={`relief ${vivant ? 'relief-vivant' : ''} ${doux ? 'relief-doux' : ''}`}
      aria-hidden="true"
    >
      <div className="relief-monde">
        {/* ---------------------------------------------------------- le sol */}
        <div className="relief-sol">
          <div className="relief-quadrillage" />
          <div className="relief-horizon" />
        </div>

        {/* ------------------------------------------- la trace, au-dessus - */}
        <svg className="relief-trace" viewBox="0 0 600 300" fill="none">
          <defs>
            <linearGradient id="relief-degrade" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0%" stopColor="#a8401f" />
              <stop offset="55%" stopColor="#f0854f" />
              <stop offset="100%" stopColor="#ffc39a" />
            </linearGradient>
          </defs>
          {/* l'ombre de la trace, posée au sol */}
          <path className="relief-ombre" d={CHEMIN} />
          <path className="relief-fil" ref={chemin} d={CHEMIN} stroke="url(#relief-degrade)" />

          {/* les repères : ils se plantent SUR la courbe, un par un */}
          {pts.map((p, i) => (
            <g key={p.k} className="relief-jalon" style={{ '--d': `${820 + i * 190}ms` }}>
              <ellipse className="relief-tache" cx={p.x} cy={p.y + 26} rx="9" ry="3" />
              <line className="relief-tige" x1={p.x} y1={p.y} x2={p.x} y2={p.y + 24} />
              <circle className="relief-halo" cx={p.x} cy={p.y} r="10" />
              <circle className="relief-tete" cx={p.x} cy={p.y} r="5.5" />
            </g>
          ))}

          {/* la porte, exactement au bout de la trace */}
          {bout && (
            <g className="relief-porte">
              <circle className="relief-lueur" cx={bout.x} cy={bout.y} r="26" />
              <path
                className="relief-battant"
                d={`M${bout.x - 13} ${bout.y + 22} L${bout.x - 13} ${bout.y - 6}
                    A 13 13 0 0 1 ${bout.x + 13} ${bout.y - 6}
                    L${bout.x + 13} ${bout.y + 22} Z`}
              />
            </g>
          )}
        </svg>

      </div>
    </div>
  )
}
