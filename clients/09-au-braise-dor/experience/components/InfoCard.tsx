"use client";

import { useLayoutEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Dish, lienCommande } from "@/data/dishes";

/**
 * ⚠️ ICI ON N'UTILISE PLUS `gsap.from()`, ET C'EST UNE LEÇON PAYÉE.
 *
 * `from()` pose l'état de DÉPART sur l'élément (ici `autoAlpha: 0`, donc
 * `visibility: hidden`) et compte sur la fin du tween pour le rendre visible.
 * Si quoi que ce soit interrompt le tween — un re-rendu de React, un contexte
 * qui se replie, une seconde animation sur la même cible — **l'élément reste
 * caché pour toujours**. C'est arrivé au bouton « Commander sur WhatsApp » :
 * la carte s'affichait complète, sauf le seul bouton qui rapporte de l'argent.
 *
 * `fromTo()` écrit l'état d'arrivée explicitement, et `clearProps` retire les
 * styles en ligne à la fin. Une interruption laisse alors l'interface DANS SON
 * ÉTAT NORMAL, pas invisible.
 */

/**
 * LA CARTE DE VERRE, à droite.
 *
 * ⚠️ CE QUI CHANGE PAR RAPPORT À LA VIDÉO, ET POURQUOI. La référence affiche
 * dans le carré coloré une NOTE (« 4.9 ★ »), un nom de chef et « 96 likes ».
 * Ce restaurant existe : inventer une note, un chef et un compteur de likes,
 * c'est fabriquer un faux avis sur une vraie maison. Le carré porte donc **le
 * prix** — vrai, et de toute façon la première chose qu'un client cherche.
 * Les champs `chef` et `avis` existent dans les données : le jour où le
 * restaurant les donne, ils s'affichent ici sans toucher au code.
 *
 * Le compteur monte de 0 au prix en 0,6 s, comme la note monte dans la vidéo.
 */
export default function InfoCard({ dish }: { dish: Dish }) {
  const zone = useRef<HTMLDivElement>(null);
  const [onglet, setOnglet] = useState<"apercu" | "detail">("apercu");

  useLayoutEffect(() => {
    setOnglet("apercu");
    const ctx = gsap.context(() => {
      gsap.fromTo(
        zone.current,
        { autoAlpha: 0, x: 80 },
        { autoAlpha: 1, x: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" }
      );
      gsap.fromTo(
        ".ic-item",
        { autoAlpha: 0, y: 16 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.5,
          ease: "power2.out",
          stagger: 0.09,
          delay: 0.12,
          clearProps: "all",
        }
      );
      // le comptage du prix
      const el = zone.current?.querySelector<HTMLSpanElement>(".ic-prix");
      if (el) {
        const o = { v: 0 };
        gsap.to(o, {
          v: dish.price,
          duration: 0.6,
          ease: "power2.out",
          delay: 0.15,
          onUpdate: () => {
            el.textContent = Math.round(o.v).toLocaleString("fr-FR");
          },
        });
      }
    }, zone);
    return () => ctx.revert();
  }, [dish.id, dish.price]);

  return (
    <aside
      ref={zone}
      className="scene-carte absolute right-[5vw] top-1/2 w-[320px] -translate-y-1/2 rounded-3xl p-5 max-lg:w-[280px]"
      style={{
        background: "var(--verre)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        border: "1px solid var(--verre-brd)",
        boxShadow: "var(--ombre)",
      }}
    >
      <div className="ic-item ic-onglets mb-4 flex items-center gap-3 text-[0.78rem] font-medium">
        <button
          type="button"
          onClick={() => setOnglet("apercu")}
          className={
            onglet === "apercu"
              ? "text-[color:var(--encre)] underline underline-offset-[6px]"
              : "text-[color:var(--encre-2)] opacity-60"
          }
        >
          Aperçu
        </button>
        <span className="h-3 w-px bg-black/15" />
        <button
          type="button"
          onClick={() => setOnglet("detail")}
          className={
            onglet === "detail"
              ? "text-[color:var(--encre)] underline underline-offset-[6px]"
              : "text-[color:var(--encre-2)] opacity-60"
          }
        >
          Le plat
        </button>
      </div>

      {onglet === "apercu" ? (
        <>
          <div className="ic-item ic-prix-bloc mb-4 flex items-start gap-4">
            <div
              className="grid h-[74px] w-[74px] shrink-0 place-items-center rounded-2xl text-center"
              style={{ background: dish.tint }}
            >
              <div>
                <span className="police-titre block text-[1.35rem] font-extrabold leading-none text-white">
                  <span className="ic-prix">0</span>
                </span>
                <span className="mt-1 block text-[0.62rem] font-medium uppercase tracking-widest text-white/85">
                  francs
                </span>
              </div>
            </div>
            <div className="pt-1">
              <p className="police-titre text-[0.98rem] font-extrabold text-[color:var(--encre)]">
                {dish.cat}
              </p>
              <p className="text-[0.78rem] text-[color:var(--encre-2)] opacity-80">
                {/* ⚠️ TROIS CAS, PAS DEUX. Une sauce n'a ni « format unique »
                    ni « grand format » : son prix monte avec ce qu'on met
                    dedans, et le carré n'en montre que la borne basse. Sans
                    cette ligne, le héros annoncerait 1 500 F pour un plat qui
                    peut en coûter 3 500. */}
                {dish.priceMax
                  ? `Jusqu'à ${dish.priceMax.toLocaleString("fr-FR")} F selon ce que vous mettez dedans`
                  : dish.price2
                    ? `Aussi en grand format, ${dish.price2.toLocaleString("fr-FR")} F`
                    : "Format unique"}
              </p>
            </div>
          </div>

          <p className="ic-item ic-desc mb-5 text-[0.85rem] leading-[1.55] text-[color:var(--encre-2)]">
            {dish.desc}
          </p>

          {dish.chef && (
            <p className="ic-item mb-4 text-[0.8rem] text-[color:var(--encre-2)]">
              <b className="text-[color:var(--encre)]">{dish.chef}</b>
              {dish.chefRole ? ` · ${dish.chefRole}` : ""}
            </p>
          )}

          <a
            className="ic-item inline-flex w-full items-center justify-center gap-2 rounded-full px-4 py-3 text-[0.85rem] font-semibold text-white transition hover:brightness-110"
            style={{ background: "#128040" }}
            href={lienCommande(dish)}
            target="_blank"
            rel="noreferrer"
          >
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden>
              <path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5.1-1.3A10 10 0 1 0 12 2m0 2a8 8 0 1 1-4.2 14.8l-.3-.2-2.6.7.7-2.5-.2-.3A8 8 0 0 1 12 4" />
            </svg>
            Commander sur WhatsApp
          </a>

          {dish.avis && (
            <p className="ic-item mt-3 text-center text-[0.75rem] text-[color:var(--encre-2)] opacity-75">
              {dish.avis.note.toFixed(1)} ★ · {dish.avis.nombre} avis
            </p>
          )}
        </>
      ) : (
        <div className="text-[0.85rem] leading-[1.6] text-[color:var(--encre-2)]">
          <p className="mb-3">{dish.desc}</p>
          <p className="opacity-80">
            Accompagnements au choix : riz, attiéké, aloco, frites, pommes
            sautées ou vapeur, pâte rouge, Bomiwo, Akassa, igname frit.
          </p>
        </div>
      )}
    </aside>
  );
}
