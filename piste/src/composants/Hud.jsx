import { useEffect, useRef, useState } from 'react'
import { fcfa } from '../prix.js'

/*
  ⚠️ DES COULEURS LITTÉRALES, PAS DES VARIABLES CSS.

  Les barres du tableau de bord sont apparues VIDES : le code composait
  `linear-gradient(90deg, ${couleur}, ${couleur}55)` pour obtenir la même
  teinte en plus transparent. Avec `couleur = 'var(--hud-cyan)'`, ça produit
  `var(--hud-cyan)55`, qui n'est pas une couleur : le navigateur jette le
  dégradé ENTIER, sans rien dire, et il ne reste que le rail gris.

  On ne colle donc jamais une transparence derrière une variable. Les teintes
  du HUD vivent ici, en clair, et les composants les reçoivent telles quelles.
*/
/*
  ⚠️ DEUX PALETTES, PAS UNE.
  Un cyan néon lisible sur du noir devient illisible sur du papier : le
  contraste tombe sous le seuil et le chiffre disparaît. Chaque couleur a donc
  sa version claire (foncée, pour ressortir sur papier) et sa version sombre
  (lumineuse, pour ressortir sur noir).
*/
export const PALETTES = {
  clair: {
    orange: '#a8401f',
    vert: '#16714a',
    cyan: '#0d6d85',
    violet: '#6737c4',
    rouge: '#a3202f',
    fond: '#f4efe6',
  },
  sombre: {
    orange: '#f0854f',
    vert: '#6fd8a4',
    cyan: '#56d6ee',
    violet: '#b48cff',
    rouge: '#ff8090',
    fond: '#0a0806',
  },
}

/* Gardé pour ne rien casser : c'est la palette sombre. */
export const TEINTES = PALETTES.sombre

/*
  LES INSTRUMENTS DU COCKPIT.

  Aucune bibliothèque de graphiques : tout est en SVG écrit à la main. Une
  bibliothèque de courbes pèse plus lourd que tout PISTE réuni, et on n'a
  besoin que de trois formes.

  ⚠️ TOUT CE QUI EST ICI DOIT SUPPORTER LE VIDE. Un cockpit tout neuf n'a
  aucune visite, aucune vente, aucune courbe. Un graphique qui plante sur une
  liste vide, ou qui affiche « NaN », c'est le premier écran que Mongazi verra.
*/

/* ────────────────────────────────────────────────── le compteur qui monte ── */
/*
  Le chiffre part de zéro et monte jusqu'à sa valeur. C'est ce qui donne
  l'impression de jouer, et ça fait REGARDER le chiffre au lieu de le survoler.
  ⚠️ On respecte `prefers-reduced-motion` : sinon on inflige un défilement à
  quelqu'un que le mouvement rend malade, pour de la décoration.
*/
export function Compteur({ valeur, duree = 900, format = (v) => v, className = '' }) {
  const cible = Number(valeur) || 0
  const [v, setV] = useState(cible)
  const precedent = useRef(cible)

  useEffect(() => {
    const doux =
      typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (doux || duree <= 0) {
      setV(cible)
      precedent.current = cible
      return
    }
    const depart = precedent.current
    const debut = performance.now()
    let brut = 0
    const pas = (t) => {
      const a = Math.min(1, (t - debut) / duree)
      /* sortie exponentielle : ça freine à l'arrivée, comme un compteur */
      const e = 1 - Math.pow(1 - a, 4)
      setV(Math.round(depart + (cible - depart) * e))
      if (a < 1) brut = requestAnimationFrame(pas)
      else precedent.current = cible
    }
    brut = requestAnimationFrame(pas)
    return () => cancelAnimationFrame(brut)
  }, [cible, duree])

  return <span className={`hud-chiffre ${className}`}>{format(v)}</span>
}

/* ────────────────────────────────────────────────────────── une statistique ─ */
export function Stat({ titre, valeur, dessous, ton = 'orange', format, jauge }) {
  return (
    <div className="hud-panneau hud-entre">
      <p className="hud-etiquette">{titre}</p>
      <p className={`mt-1.5 text-[clamp(1.5rem,6.5vw,2.1rem)] font-black leading-none hud-lueur-${ton}`}>
        <Compteur valeur={valeur} format={format} />
      </p>
      {jauge !== undefined && (
        <div className="hud-jauge mt-2.5">
          <div
            className="hud-jauge-fond"
            style={{ width: `${Math.max(0, Math.min(100, jauge))}%` }}
          />
        </div>
      )}
      {dessous && <p className="mt-2 text-[0.78rem] leading-snug text-[var(--hud-sourd)]">{dessous}</p>}
    </div>
  )
}

/* ──────────────────────────────────────────────────────────────── la courbe ─ */
/*
  Une courbe par série, dessinée dans le MÊME repère : sinon deux séries d'ordre
  de grandeur différent se superposent et ne veulent plus rien dire. On note
  donc le maximum affiché, en clair, au-dessus.
*/
export function Courbe({ points, series, hauteur = 150, fond = PALETTES.sombre.fond }) {
  const [survol, setSurvol] = useState(-1)
  const L = 720
  const H = hauteur
  const marge = { h: 6, b: 20 }
  const n = points.length

  const maxi = Math.max(
    1,
    ...series.flatMap((s) => points.map((p) => Number(p[s.cle]) || 0))
  )
  const x = (i) => (n <= 1 ? L / 2 : (i / (n - 1)) * L)
  const y = (v) => marge.h + (1 - (Number(v) || 0) / maxi) * (H - marge.h - marge.b)

  const chemin = (cle) =>
    points.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(p[cle]).toFixed(1)}`).join(' ')
  const aire = (cle) =>
    `${chemin(cle)} L${x(n - 1).toFixed(1)} ${H - marge.b} L${x(0).toFixed(1)} ${H - marge.b} Z`

  const jourLisible = (j) => {
    const d = new Date(j + 'T00:00:00')
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
  }
  const i = survol >= 0 ? survol : n - 1
  const actif = points[i]

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <div className="flex flex-wrap gap-x-4 gap-y-1.5">
          {series.map((s) => (
            <span key={s.cle} className="flex items-center gap-1.5 text-[0.74rem]">
              <span
                aria-hidden="true"
                className="h-2 w-2 rounded-full"
                style={{ background: s.couleur, boxShadow: `0 0 10px ${s.couleur}` }}
              />
              <span className="text-[var(--hud-sourd)]">{s.nom}</span>
              {actif && (
                <span className="hud-chiffre font-bold" style={{ color: s.couleur }}>
                  {s.format ? s.format(actif[s.cle]) : Number(actif[s.cle]) || 0}
                </span>
              )}
            </span>
          ))}
        </div>
        <span className="hud-etiquette">{actif ? jourLisible(actif.jour) : ''}</span>
      </div>

      <svg
        viewBox={`0 0 ${L} ${H}`}
        className="mt-3 w-full"
        style={{ height: H }}
        role="img"
        aria-label={`Évolution sur ${n} jours. Maximum ${maxi}.`}
        onMouseLeave={() => setSurvol(-1)}
      >
        <defs>
          {series.map((s) => (
            <linearGradient key={s.cle} id={`grad-${s.cle}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={s.couleur} stopOpacity="0.34" />
              <stop offset="100%" stopColor={s.couleur} stopOpacity="0" />
            </linearGradient>
          ))}
        </defs>

        {/* la ligne du bas, pour que la courbe ait un sol */}
        <line
          x1="0" y1={H - marge.b} x2={L} y2={H - marge.b}
          stroke="rgba(240,133,79,0.2)" strokeWidth="1"
        />

        {series.map((s) => (
          <g key={s.cle}>
            <path className="hud-aire" d={aire(s.cle)} fill={`url(#grad-${s.cle})`} />
            <path
              className="hud-trace"
              d={chemin(s.cle)}
              fill="none"
              stroke={s.couleur}
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ '--long': L * 1.6, filter: `drop-shadow(0 0 6px ${s.couleur}88)` }}
            />
            {i >= 0 && (
              <circle
                cx={x(i)} cy={y(points[i][s.cle])} r="4"
                fill={s.couleur} stroke={fond} strokeWidth="2"
              />
            )}
          </g>
        ))}

        {/* le repère vertical suit le doigt ou la souris */}
        {i >= 0 && (
          <line
            x1={x(i)} y1={marge.h} x2={x(i)} y2={H - marge.b}
            stroke="rgba(255,248,242,0.25)" strokeWidth="1" strokeDasharray="3 4"
          />
        )}

        {/* des zones invisibles : viser un point de courbe au doigt est perdu
            d'avance, viser une colonne entière ne l'est pas */}
        {points.map((p, k) => (
          <rect
            key={p.jour}
            x={n <= 1 ? 0 : x(k) - L / (2 * (n - 1))}
            y="0"
            width={n <= 1 ? L : L / (n - 1)}
            height={H}
            fill="transparent"
            onMouseEnter={() => setSurvol(k)}
            onTouchStart={() => setSurvol(k)}
          />
        ))}
      </svg>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────── l'entonnoir ─ */
/*
  Il répond à la question de Mongazi mot pour mot : « combien de personnes
  viennent, combien achètent ». Chaque barre est un pourcentage de la
  PREMIÈRE : c'est la seule lecture qui montre où les gens s'arrêtent.
*/
export function Entonnoir({ etapes, comparable = true }) {
  const base = Math.max(1, etapes[0]?.n || 0)
  return (
    <div className="grid gap-2.5">
      {etapes.map((e, i) => {
        /* ⚠️ Une étape peut dépasser la première quand les deux mesures n'ont
           pas le même âge : les commandes existent depuis des jours, le
           comptage des visites depuis quelques heures. Afficher « 1300 % »
           rend tout l'écran suspect. On écrit un tiret, et on dit pourquoi
           juste au-dessus. */
        const brut = Math.round(((e.n || 0) / base) * 100)
        const part = !comparable || brut > 100 ? null : brut
        return (
          <div key={e.nom}>
            <div className="flex items-baseline justify-between gap-3">
              <span className="text-[0.84rem] text-[var(--hud-texte)]">{e.nom}</span>
              <span className="flex items-baseline gap-2">
                <Compteur
                  valeur={e.n}
                  className={`text-[1.05rem] font-bold hud-lueur-${e.ton || 'orange'}`}
                />
                {i > 0 && part !== null && (
                  <span className="hud-chiffre text-[0.72rem] text-[var(--hud-sourd)]">
                    {part}%
                  </span>
                )}
              </span>
            </div>
            <div className="hud-jauge mt-1.5">
              <div
                className="hud-jauge-fond"
                style={{
                  width: `${Math.max(2, Math.min(100, brut))}%`,
                  background: `linear-gradient(90deg, ${e.couleur}, ${e.couleur}55)`,
                  boxShadow: `0 0 14px ${e.couleur}99`,
                  animationDelay: `${i * 0.09}s`,
                }}
              />
            </div>
            {e.dessous && (
              <p className="mt-1 text-[0.74rem] text-[var(--hud-sourd)]">{e.dessous}</p>
            )}
          </div>
        )
      })}
    </div>
  )
}

/* ───────────────────────────────────────────────── un classement en barres ── */
export function Classement({ lignes, vide, nomDe, couleur = TEINTES.cyan }) {
  if (!lignes.length) {
    return <p className="text-[0.82rem] leading-relaxed text-[var(--hud-sourd)]">{vide}</p>
  }
  const maxi = Math.max(1, ...lignes.map((l) => l.n))
  return (
    <div className="grid gap-2">
      {lignes.map((l, i) => (
        <div key={l.cle}>
          <div className="flex items-baseline justify-between gap-3">
            <span className="truncate text-[0.84rem]">{nomDe ? nomDe(l.cle) : l.cle}</span>
            <span className="hud-chiffre flex-none text-[0.86rem] font-bold" style={{ color: couleur }}>
              {l.n}
            </span>
          </div>
          <div className="hud-jauge mt-1">
            <div
              className="hud-jauge-fond"
              style={{
                width: `${(l.n / maxi) * 100}%`,
                background: `linear-gradient(90deg, ${couleur}, ${couleur}44)`,
                boxShadow: `0 0 12px ${couleur}88`,
                animationDelay: `${i * 0.06}s`,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

export const enFcfa = (v) => fcfa(v)
