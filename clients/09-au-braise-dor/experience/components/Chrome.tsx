"use client";

import { WHATSAPP } from "@/data/dishes";

/** Les boutons flottants du haut : retour, recherche, menu. */
export function TopBar() {
  return (
    <>
      <a
        href="#carte"
        aria-label="Revenir à la carte"
        className="barre-haut absolute left-6 top-6 grid h-14 w-14 place-items-center rounded-[22px] text-white transition hover:brightness-125 max-md:h-12 max-md:w-12"
        style={{
          background: "rgba(30,30,30,.6)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
        }}
      >
        <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
          <path d="M15 5l-7 7 7 7" />
        </svg>
      </a>

      <button
        type="button"
        aria-label="Chercher un plat"
        className="absolute right-24 top-8 grid h-10 w-10 place-items-center text-[color:var(--encre)] opacity-80 transition hover:opacity-100 max-md:right-20 max-md:top-7"
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="11" cy="11" r="6.5" />
          <path d="M16 16l4.5 4.5" />
        </svg>
      </button>

      <a
        href="#carte"
        aria-label="Ouvrir la carte complète"
        className="barre-haut absolute right-6 top-6 grid h-14 w-14 place-items-center rounded-[22px] text-white transition hover:brightness-125 max-md:h-12 max-md:w-12"
        style={{
          background: "rgba(30,30,30,.6)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
        }}
      >
        <svg viewBox="0 0 24 24" className="h-6 w-6" fill="currentColor">
          <circle cx="5" cy="12" r="1.8" />
          <circle cx="12" cy="12" r="1.8" />
          <circle cx="19" cy="12" r="1.8" />
        </svg>
      </a>
    </>
  );
}

/**
 * L'INDICATEUR DE GAUCHE : des points, et le plat courant devient un TRAIT.
 * ⚠️ Ce n'est pas un point plus gros : c'est un trait vertical d'une vingtaine
 * de pixels. C'est ce qui fait lire la pile comme une hauteur, pas comme une
 * liste.
 */
export function Indicator({
  n,
  actif,
  onAller,
}: {
  n: number;
  actif: number;
  onAller: (i: number) => void;
}) {
  return (
    <div className="absolute left-8 top-1/2 flex -translate-y-1/2 flex-col items-center gap-2.5 max-md:left-4">
      {Array.from({ length: n }).map((_, i) => (
        <button
          key={i}
          type="button"
          onClick={() => onAller(i)}
          aria-label={`Aller au plat ${i + 1}`}
          className="grid h-5 w-5 place-items-center"
        >
          <span
            className="block rounded-full transition-all duration-500 ease-out"
            style={{
              width: i === actif ? 3 : 6,
              height: i === actif ? 20 : 6,
              background:
                i === actif ? "var(--encre)" : "rgba(29,26,23,.28)",
            }}
          />
        </button>
      ))}
    </div>
  );
}

/**
 * LA BARRE DU BAS. Quatre icônes plates, et le cinquième bouton est DIFFÉRENT :
 * un cercle blanc surélevé avec son ombre. C'est le point d'appel du brief,
 * et ici il sert à ce qui compte vraiment pour un restaurant : appeler.
 */
export function BottomNav() {
  const I = "h-6 w-6";
  return (
    <nav className="absolute bottom-7 left-1/2 flex -translate-x-1/2 items-end gap-9 max-md:gap-6">
      <a href="#carte" aria-label="La carte" className="text-[color:var(--encre)] opacity-70 transition hover:opacity-100">
        <svg viewBox="0 0 24 24" className={I} fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round">
          <path d="M6 3v8a2 2 0 0 0 4 0V3M8 11v10" />
          <path d="M16 3c-1.5 2-1.5 6 0 8v10" />
        </svg>
      </a>
      <a href="#carte" aria-label="Les boissons" className="text-[color:var(--encre)] opacity-70 transition hover:opacity-100">
        <svg viewBox="0 0 24 24" className={I} fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 4h16l-8 9z" />
          <path d="M12 13v7M8 20h8" />
        </svg>
      </a>



      <a href="#avis" aria-label="Les avis" className="text-[color:var(--encre)] opacity-70 transition hover:opacity-100">
        <svg viewBox="0 0 24 24" className={I} fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round">
          <path d="M4 5h16v11H9l-5 4z" />
        </svg>
      </a>
      <a href="#infos" aria-label="Le restaurant" className="text-[color:var(--encre)] opacity-70 transition hover:opacity-100">
        <svg viewBox="0 0 24 24" className={I} fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round">
          <circle cx="12" cy="8" r="3.4" />
          <path d="M5 20c1.2-3.6 4-5.4 7-5.4s5.8 1.8 7 5.4" />
        </svg>
      </a>
      <a
        href={`https://wa.me/${WHATSAPP}`}
        target="_blank"
        rel="noreferrer"
        aria-label="Nous appeler sur WhatsApp"
        className="pulse relative -mb-1 grid h-14 w-14 place-items-center rounded-full bg-white text-[color:var(--encre)] shadow-[0_16px_36px_rgba(0,0,0,.18)] transition hover:scale-105"
      >
        <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
          <rect x="9" y="3" width="6" height="11" rx="3" />
          <path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
        </svg>
      </a>
    </nav>
  );
}
