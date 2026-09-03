"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation } from "swiper/modules";
import type { Swiper as SwiperType } from "swiper";
import { DISHES } from "@/data/dishes";
import "swiper/css";
import "swiper/css/navigation";

/**
 * LE CARROUSEL DU BAS.
 *
 * ⚠️ L'ITEM ACTIF EST SURÉLEVÉ, et c'est ça qui fait la référence : il monte
 * de 15 px et pose son socle blanc. Les autres reculent (échelle 0,9,
 * opacité 0,6, pas de socle). Sans cette différence de hauteur, la bande
 * redevient une rangée de vignettes comme partout ailleurs.
 *
 * ⚠️ IL SUIT LA SAUCE COURANTE (2026-08-26). À quatre plats, les quatre
 * miniatures tenaient à l'écran et la question ne se posait pas. À quatorze,
 * la scène avance toute seule toutes les 2,8 s : sans `slideTo`, la miniature
 * surélevée sort du cadre au bout de quatre tours et la bande se met à
 * désigner une sauce qu'on ne voit plus. Un carrousel qui ne suit pas ce
 * qu'il indique est pire qu'une simple liste.
 */
export default function Rail({
  actif,
  onAller,
}: {
  actif: number;
  onAller: (n: number) => void;
}) {
  const sw = useRef<SwiperType | null>(null);

  useEffect(() => {
    // `slideToLoop` n'a pas lieu d'être : la bande n'est pas en boucle, c'est
    // la scène qui l'est. On centre simplement l'actif.
    sw.current?.slideTo(Math.max(0, actif - 1), 420);
  }, [actif]);

  return (
    <div className="rail-bas absolute bottom-[104px] left-1/2 w-[min(64vw,760px)] -translate-x-1/2 transition-[bottom] duration-300 max-md:bottom-[84px] max-md:w-[calc(100%-2.5rem)]">
      <Swiper
        modules={[Navigation]}
        onSwiper={(s) => {
          sw.current = s;
        }}
        slidesPerView={4}
        spaceBetween={8}
        navigation={{ prevEl: ".rail-prec", nextEl: ".rail-suiv" }}
        /* ⚠️ Quatorze miniatures : on en montre plus par écran, sinon la bande
           devient un tunnel où l'on fait défiler à l'aveugle. */
        breakpoints={{
          0: { slidesPerView: 3.4 },
          480: { slidesPerView: 4.4 },
          768: { slidesPerView: 6 },
          1200: { slidesPerView: 7 },
        }}
        /* ⚠️ `!overflow-visible` LAISSAIT LES MINIATURES DÉBORDER SOUS LES
           FLÈCHES. Elles sont posées juste à l'extérieur de la bande
           (`-left-9` / `-right-9`) : tant qu'il y avait quatre plats, rien ne
           dépassait jusque-là. À quatorze, la piste déborde des deux côtés et
           les deux flèches se retrouvaient POSÉES SUR des miniatures, comme
           deux chevrons perdus au milieu de la rangée.
           On coupe donc l'horizontale et on garde la verticale : c'est elle
           qui laisse la miniature active monter de 15 px avec son ombre.
           (`clip` est la seule valeur qui n'oblige pas l'autre axe à devenir
           une zone de défilement — `hidden` aurait rogné l'ombre.) */
        className="!overflow-x-clip !overflow-y-visible"
      >
        {DISHES.map((d, k) => (
          <SwiperSlide key={d.id}>
            <button
              type="button"
              onClick={() => onAller(k)}
              aria-current={k === actif}
              aria-label={`${d.line1} ${d.line2}`}
              className="group flex w-full flex-col items-center rounded-[20px] p-2 transition-all duration-[400ms] ease-out"
              style={{
                transform: k === actif ? "translateY(-15px)" : "scale(.9)",
                opacity: k === actif ? 1 : 0.6,
                background: k === actif ? "rgba(255,255,255,.78)" : "transparent",
                backdropFilter: k === actif ? "blur(14px)" : undefined,
                boxShadow: k === actif ? "0 14px 34px rgba(0,0,0,.10)" : undefined,
              }}
            >
              <span className="relative block h-[64px] w-[64px] overflow-hidden rounded-2xl">
                {d.img ? (
                  <Image src={d.img} alt="" fill sizes="64px" className="object-contain" />
                ) : (
                  /* ⚠️ PAS DE VIGNETTE VIDE. La sauce n'a pas encore sa photo :
                     on pose le même galet d'ardoise qu'au héros, avec son
                     filet de couleur. Le nom est écrit juste dessous, il ne
                     manque donc rien à la lecture. */
                  <span
                    className="absolute inset-1 grid place-items-center rounded-full"
                    style={{
                      background:
                        "radial-gradient(120% 90% at 50% 0%, #3a312a 0%, #241f1b 60%, #1b1714 100%)",
                    }}
                    aria-hidden
                  >
                    <span
                      className="block h-[3px] w-6 rounded"
                      style={{ background: d.tint }}
                    />
                  </span>
                )}
              </span>
              <span className="mt-1.5 block max-w-[84px] truncate text-[10px] font-medium text-[color:var(--encre-2)]">
                {d.line1} {d.line2}
              </span>
            </button>
          </SwiperSlide>
        ))}
      </Swiper>

      <button
        className="rail-prec absolute -left-9 top-1/2 -translate-y-1/2 p-2 text-[color:var(--encre-2)] transition hover:text-[color:var(--encre)] max-md:hidden"
        aria-label="Sauce précédente"
        type="button"
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M15 5l-7 7 7 7" />
        </svg>
      </button>
      <button
        className="rail-suiv absolute -right-9 top-1/2 -translate-y-1/2 p-2 text-[color:var(--encre-2)] transition hover:text-[color:var(--encre)] max-md:hidden"
        aria-label="Sauce suivante"
        type="button"
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
}
