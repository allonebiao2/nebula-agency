"use client";

import Image from "next/image";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation } from "swiper/modules";
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
 */
export default function Rail({
  actif,
  onAller,
}: {
  actif: number;
  onAller: (n: number) => void;
}) {
  return (
    <div className="absolute bottom-[104px] left-1/2 w-[min(60vw,640px)] -translate-x-1/2 max-md:bottom-[92px] max-md:w-[calc(100%-2.5rem)]">
      <Swiper
        modules={[Navigation]}
        slidesPerView={4}
        spaceBetween={8}
        navigation={{ prevEl: ".rail-prec", nextEl: ".rail-suiv" }}
        breakpoints={{ 0: { slidesPerView: 3 }, 768: { slidesPerView: 4 } }}
        className="!overflow-visible"
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
                boxShadow:
                  k === actif ? "0 14px 34px rgba(0,0,0,.10)" : undefined,
              }}
            >
              <span className="relative block h-[64px] w-[64px] overflow-hidden rounded-2xl">
                <Image
                  src={d.img}
                  alt=""
                  fill
                  sizes="64px"
                  className="object-contain"
                />
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
        aria-label="Plat précédent"
        type="button"
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M15 5l-7 7 7 7" />
        </svg>
      </button>
      <button
        className="rail-suiv absolute -right-9 top-1/2 -translate-y-1/2 p-2 text-[color:var(--encre-2)] transition hover:text-[color:var(--encre)] max-md:hidden"
        aria-label="Plat suivant"
        type="button"
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
}
