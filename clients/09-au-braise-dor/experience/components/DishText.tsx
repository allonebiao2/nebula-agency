"use client";

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { Dish, lienCommande } from "@/data/dishes";
import { NB_PLATS } from "@/data/carte";

/**
 * LE TITRE EN DEUX LIGNES, la signature de la référence : une ligne fine et
 * très espacée, puis la même police en très gras juste dessous.
 *
 * ⚠️ LES DEUX LIGNES NE SORTENT PAS DU MÊME CÔTÉ. La fine part à gauche, la
 * grasse à droite : c'est ce dédoublement qui donne l'impression que le mot
 * « se déchire » au changement de plat. Les faire sortir ensemble donne un
 * fondu banal, et on perd exactement ce qui se remarque dans la vidéo.
 */
export default function DishText({ dish }: { dish: Dish }) {
  const zone = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      /* ⚠️ `fromTo` et jamais `from` : voir la note dans InfoCard.tsx. Un
         `from` interrompu laisse le titre invisible, et la page vide. */
      const tl = gsap.timeline({ defaults: { clearProps: "all" } });
      tl.fromTo(".dt-kicker", { autoAlpha: 0, y: 20 },
          { autoAlpha: 1, y: 0, duration: 0.45, ease: "power2.out" })
        .fromTo(".dt-l1", { autoAlpha: 0, x: -50 },
          { autoAlpha: 1, x: 0, duration: 0.7, ease: "power3.out" }, 0.1)
        .fromTo(".dt-l2", { autoAlpha: 0, x: 50 },
          { autoAlpha: 1, x: 0, duration: 0.7, ease: "power3.out" }, 0.25)
        .fromTo(".dt-act", { autoAlpha: 0, y: 14, scale: 0.94 },
          { autoAlpha: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.6)", stagger: 0.08 }, 0.4);
    }, zone);
    return () => ctx.revert();
  }, [dish.id]);

  return (
    <div
      ref={zone}
      /* ⚠️ LE TITRE VIT ENTRE L'ASSIETTE ET LA CARTE, pas au centre. Reglé en
         `left`/`right` et non en largeur fixe : « BICYCLETTE » sortait de
         l'écran, coupé au milieu du mot. Un titre coupé, c'est un site cassé. */
      className="scene-txt pointer-events-none absolute left-[46%] right-[calc(5vw+340px)] top-1/2 -translate-y-1/2 max-lg:right-[calc(5vw+296px)]"
    >
      <p className="dt-kicker mb-3 flex items-center gap-2 text-[0.82rem] font-medium tracking-wide text-[color:var(--encre-2)]">
        <span className="inline-block h-3 w-px bg-[color:var(--encre-2)] opacity-60" />
        {dish.kicker}
      </p>

      <h2 className="police-titre leading-[0.94] text-[color:var(--encre)]">
        <span className="dt-l1 block text-[clamp(1.5rem,2.6vw,2.7rem)] font-extralight uppercase tracking-[0.16em]">
          {dish.line1}
        </span>
        <span className="dt-l2 block text-[clamp(1.9rem,3.5vw,3.6rem)] font-extrabold uppercase tracking-[-0.01em]">
          {dish.line2}
        </span>
      </h2>

      <div className="dt-act-zone pointer-events-auto mt-7 flex items-center gap-9">
        <a
          className="dt-act group inline-flex items-center gap-2 text-[0.9rem] font-medium text-[color:var(--encre-2)] transition hover:text-[color:var(--encre)]"
          href="#carte"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden>
            <path d="M8 5v14l11-7z" />
          </svg>
          Voir la carte <span className="opacity-60">· {NB_PLATS} plats</span>
        </a>
        <a
          className="dt-act group inline-flex items-center gap-2 text-[0.9rem] font-medium text-[color:var(--encre-2)] transition hover:text-[color:var(--encre)]"
          href={lienCommande(dish)}
          target="_blank"
          rel="noreferrer"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
            <path d="M6 6h15l-1.5 9h-12z" strokeLinejoin="round" />
            <circle cx="9" cy="20" r="1.4" fill="currentColor" stroke="none" />
            <circle cx="18" cy="20" r="1.4" fill="currentColor" stroke="none" />
            <path d="M3 3h2l1 3" strokeLinecap="round" />
          </svg>
          Commander
        </a>
      </div>
    </div>
  );
}
