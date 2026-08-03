/*
  Les briques communes. Toutes les cibles font au moins 48 px de haut : on s'en
  sert au pouce, debout, dans la rue.
*/

const BASE =
  'inline-flex min-h-[48px] items-center justify-center gap-2 rounded-full px-6 text-[0.95rem] font-semibold leading-none transition-[transform,background-color,border-color,color] duration-200 active:translate-y-px disabled:cursor-not-allowed disabled:opacity-45 disabled:active:translate-y-0'

const TONS = {
  plein: 'bg-brique text-creme hover:bg-laterite',
  pleinClair: 'bg-braise text-encre hover:bg-[#f5975f]',
  contour: 'border border-trait bg-transparent text-encre hover:border-encre',
  contourSombre: 'border border-traitsombre bg-transparent text-papier hover:border-sable',
  nu: 'bg-transparent text-sourd hover:text-encre underline underline-offset-4 px-2',
}

export function Bouton({ ton = 'plein', className = '', comme, ...reste }) {
  const Balise = comme || (reste.href ? 'a' : 'button')
  const props = Balise === 'button' && !reste.type ? { type: 'button' } : {}
  return <Balise className={`${BASE} ${TONS[ton]} ${className}`} {...props} {...reste} />
}

export function Section({
  fond = 'papier',
  id,
  className = '',
  interieur = '',
  grain = false,
  children,
}) {
  const fonds = {
    encre: 'bg-encre text-papier',
    encre2: 'bg-encre2 text-papier',
    nuit: 'bg-nuit text-papier',
    papier: 'bg-papier text-encre',
    papier2: 'bg-papier2 text-encre',
    laterite: 'bg-brique text-creme',
  }
  return (
    <section
      id={id}
      className={`relative ${grain ? 'grain' : ''} ${fonds[fond]} ${className}`}
    >
      <div className={`relative mx-auto w-full max-w-[68rem] px-5 sm:px-8 ${interieur}`}>
        {children}
      </div>
    </section>
  )
}

export function Titre({ sur, children, className = '', sombre = false }) {
  return (
    <header className={className}>
      {sur && (
        <p
          className={`mb-3 text-[0.72rem] font-semibold uppercase tracking-[0.22em] ${
            sombre ? 'text-braise' : 'text-brique'
          }`}
        >
          {sur}
        </p>
      )}
      <h2 className="text-[clamp(2rem,7.6vw,3.6rem)]">{children}</h2>
    </header>
  )
}

export function Chiffre({ children, className = '' }) {
  return (
    <span className={`font-display font-bold tabular-nums tracking-tight ${className}`}>
      {children}
    </span>
  )
}
