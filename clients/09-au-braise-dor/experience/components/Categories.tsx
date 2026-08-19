"use client";

import { useEffect } from "react";
import Image from "next/image";
import { CARTE, NB_PLATS } from "@/data/carte";
import { allerA } from "./aller";

/**
 * LE TIROIR DES CATÉGORIES, ouvert depuis le héros.
 *
 * Demande de Mongazi : « je veux que toute personne qui vient directement à
 * partir de la héros puisse commander tous les plats, toutes les catégories,
 * tout accessible depuis cette belle héros section. »
 *
 * ⚠️ CE QUI MANQUAIT N'ÉTAIT PAS LE CONTENU, C'ÉTAIT LE CHEMIN. Les 48 plats
 * étaient là, en dessous, mais depuis le premier écran rien ne disait qu'ils
 * existaient ni combien il y en avait. Un visiteur qui ne fait pas défiler ne
 * commande rien. Ici il voit les huit univers, leur nombre de plats, et il
 * atterrit directement dans celui qu'il veut.
 */
export default function Categories({
  ouvert,
  onFermer,
}: {
  ouvert: boolean;
  onFermer: () => void;
}) {
  useEffect(() => {
    if (!ouvert) return;
    const f = (e: KeyboardEvent) => e.key === "Escape" && onFermer();
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, [ouvert, onFermer]);

  function aller(id: string) {
    onFermer();
    // on laisse le tiroir se refermer avant de bouger : sinon on défile
    // derrière un panneau encore ouvert, et on ne voit pas où l'on arrive
    setTimeout(() => allerA("cat-" + id), 180);
  }

  return (
    <div
      className={
        "fixed inset-0 z-[60] transition-opacity duration-300 " +
        (ouvert ? "opacity-100" : "pointer-events-none opacity-0")
      }
      aria-hidden={!ouvert}
    >
      <button
        type="button"
        aria-label="Fermer"
        onClick={onFermer}
        className="absolute inset-0 h-full w-full bg-[#1d1a17]/45 backdrop-blur-sm"
      />
      <div
        className={
          "absolute right-0 top-0 flex h-full w-[min(420px,88vw)] flex-col bg-[color:var(--mur)] shadow-[0_0_80px_rgba(0,0,0,.28)] transition-transform duration-[420ms] " +
          (ouvert ? "translate-x-0" : "translate-x-full")
        }
        style={{ transitionTimingFunction: "cubic-bezier(.16,1,.3,1)" }}
        role="dialog"
        aria-label="Toute la carte"
      >
        <div className="flex items-start justify-between px-6 pb-4 pt-7">
          <div>
            <p className="text-[0.68rem] font-medium uppercase tracking-[0.3em] text-[#a8542f]">
              Toute la carte
            </p>
            <p className="police-titre mt-1 text-[1.6rem] font-extrabold leading-none text-[color:var(--encre)]">
              {NB_PLATS} plats
            </p>
          </div>
          <button
            type="button"
            onClick={onFermer}
            aria-label="Fermer"
            className="grid h-10 w-10 place-items-center rounded-full bg-black/[0.06] text-[color:var(--encre)]"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-auto px-4 pb-8">
          {CARTE.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => aller(c.id)}
              className="mb-2 flex w-full items-center gap-3 rounded-2xl p-2.5 text-left transition hover:bg-black/[0.04]"
            >
              {/* ⚠️ PAS `c.items[0].img` : le premier plat d'un univers peut ne
                  pas avoir de photo (le petit-dejeuner en compte quatre). On
                  prend la premiere photo disponible de l'univers, et s'il n'y
                  en a aucune, la vignette reste un aplat, jamais un lien mort. */}
              <span className="relative block h-14 w-14 shrink-0 overflow-hidden rounded-xl bg-[#e7e0d8]">
                {(() => {
                  const vignette = c.items.find((i) => i.img)?.img;
                  return vignette ? (
                    <Image src={vignette} alt="" fill sizes="56px" className="object-cover" />
                  ) : null;
                })()}
              </span>
              <span className="min-w-0 flex-1">
                <span className="police-titre block text-[1rem] font-extrabold text-[color:var(--encre)]">
                  {c.label}
                </span>
                <span className="block truncate text-[0.78rem] text-[color:var(--encre-2)]">
                  {c.items.length} plat{c.items.length > 1 ? "s" : ""} · {c.tag}
                </span>
              </span>
              <svg viewBox="0 0 24 24" className="h-5 w-5 shrink-0 text-[color:var(--encre-2)]" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M9 5l7 7-7 7" />
              </svg>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
