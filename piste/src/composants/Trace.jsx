import { useEffect, useRef, useState } from 'react'
import { useRevele } from './Revele.jsx'

/*
  LA TRACE. C'est l'objet du métier, et toutes les animations en sortent.

  Une piste, c'est une trace qu'on relève sur le terrain et qu'on suit jusqu'à
  la porte du commerçant. Ici : le tracé se dessine, les repères se plantent
  dessus, la porte s'ouvre au bout.

  Les repères sont posés par `getPointAtLength` : ils tombent exactement sur la
  courbe, quelle que soit sa forme.
*/

const CHEMIN =
  'M14 268 C 96 272, 104 194, 176 190 S 252 214, 300 154 S 372 62, 462 82 S 548 128, 586 92'

export function TracePiste({ repere = 5, className = '', hauteur = '' }) {
  const hote = useRevele()
  const chemin = useRef(null)
  const [pts, setPts] = useState([])
  const [long, setLong] = useState(1100)

  useEffect(() => {
    const p = chemin.current
    if (!p || typeof p.getTotalLength !== 'function') return
    const L = p.getTotalLength()
    if (!L) return
    setLong(Math.ceil(L))
    const liste = []
    for (let i = 0; i < repere; i++) {
      const k = repere === 1 ? 0.5 : i / (repere - 1)
      const pt = p.getPointAtLength(L * k * 0.985)
      liste.push({ x: pt.x, y: pt.y, k })
    }
    setPts(liste)
  }, [repere])

  return (
    <div ref={hote} className={`trace ${className}`}>
      <svg
        viewBox="-6 -14 618 348"
        className={`w-full ${hauteur}`}
        role="img"
        aria-label="Une trace qui traverse le terrain, avec des repères posés dessus et une porte au bout."
      >
        <path
          ref={chemin}
          d={CHEMIN}
          fill="none"
          stroke="currentColor"
          strokeWidth="3.4"
          strokeLinecap="round"
          strokeDasharray="14 13"
          style={{ '--long': long, strokeDasharray: '14 13' }}
          opacity="0.62"
        />
        {/* Deux groupes : celui du dehors POSE le repère sur la courbe, celui du
            dedans l'anime. Une transformation CSS écrase l'attribut `transform`
            d'un SVG : les mélanger empile tous les repères sur l'origine. */}
        {pts.map((p, i) => {
          const dernier = i === pts.length - 1
          return (
            <g key={i} transform={`translate(${p.x} ${p.y})`}>
              <g className="repere" style={{ '--d': `${420 + i * 300}ms` }}>
                {dernier ? (
                  <g>
                    <path
                      d="M-15 0 L -15 -30 A 15 15 0 0 1 15 -30 L 15 0 Z"
                      fill="currentColor"
                    />
                    <circle cx="7" cy="-14" r="2.6" fill="var(--color-encre)" />
                  </g>
                ) : (
                  <>
                    <path
                      d="M0 0 C -9 -12, -13 -17, -13 -23 A 13 13 0 1 1 13 -23 C 13 -17, 9 -12, 0 0 Z"
                      fill="currentColor"
                    />
                    <circle cx="0" cy="-23" r="5" fill="var(--color-encre)" />
                  </>
                )}
              </g>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

/*
  LE SEMIS. 187 points, un par commerce relevé. 17 colonnes sur 11 lignes,
  exactement 187 : on peut les compter.
*/
export function Semis({ repartition, total }) {
  const ref = useRevele()
  const couleurs = ['bg-braise', 'bg-vertclair', 'bg-creme']
  const suite = []
  repartition.forEach((r, i) => {
    for (let k = 0; k < r.n; k++) suite.push(i)
  })
  while (suite.length < total) suite.push(0)

  return (
    <div ref={ref} className="revele">
      <div
        className="grid gap-[3px] sm:gap-[5px]"
        style={{ gridTemplateColumns: 'repeat(17, minmax(0, 1fr))' }}
        aria-hidden="true"
      >
        {suite.map((c, i) => (
          <span
            key={i}
            className={`point aspect-square rounded-full ${couleurs[c] || couleurs[0]}`}
            style={{ '--d': `${Math.round(i * 5.5)}ms` }}
          />
        ))}
      </div>
      <p className="sr-only">
        {total} points, un par commerce relevé :{' '}
        {repartition.map((r) => `${r.n} ${r.nom}`).join(', ')}.
      </p>
    </div>
  )
}

/* La trace verticale qui relie les étapes. */
export function TraceEtapes({ n = 3 }) {
  const ref = useRevele()
  return (
    <div ref={ref} className="trace absolute left-[19px] top-6 bottom-6 w-px sm:left-[23px]">
      <svg
        viewBox="0 0 2 100"
        preserveAspectRatio="none"
        className="h-full w-full text-braise"
        aria-hidden="true"
      >
        <line
          x1="1"
          y1="0"
          x2="1"
          y2="100"
          stroke="currentColor"
          strokeWidth="2"
          strokeDasharray="4 5"
          style={{ '--long': 100 }}
          opacity="0.65"
        />
      </svg>
    </div>
  )
}

/* Le petit repère utilisé comme puce dans les listes. */
export function Puce({ className = '' }) {
  return (
    <svg viewBox="0 0 26 26" className={`shrink-0 ${className}`} aria-hidden="true">
      <path
        d="M13 24 C 6 14, 3 11, 3 8 A 10 10 0 1 1 23 8 C 23 11, 20 14, 13 24 Z"
        fill="currentColor"
      />
      <circle cx="13" cy="8.5" r="3.6" fill="var(--color-papier)" />
    </svg>
  )
}
