"use client";

import { useLayoutEffect, useRef, useState } from "react";
import gsap from "gsap";
import { Dish, lienCommande } from "@/data/dishes";
import { commander } from "@/data/commande";
import { ACC } from "@/data/carte";

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
          /* ⛔ SURTOUT PAS `clearProps: "all"`, ET C'EST UN DÉFAUT MESURÉ.
             `"all"` ne retire pas « ce que GSAP a posé » : il VIDE L'ATTRIBUT
             `style` de l'élément. Le bouton qui prend la commande porte sa
             couleur en style en ligne : après l'animation il se retrouvait à
             `background-color: rgba(0,0,0,0)` avec un texte crème, sur une
             carte de verre claire — **invisible**, mesuré à 1,1:1.
             ⚠️ Le défaut ne datait pas de la refonte : l'ancien bouton vert
             « Commander sur WhatsApp » avait exactement le même sort. C'est
             la deuxième fois que GSAP fait disparaître le seul bouton qui
             rapporte de l'argent sur cette carte (voir la note du haut).
             On ne nettoie donc que ce que l'animation a réellement touché. */
          clearProps: "opacity,visibility,transform",
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

          {/* ⚠️ ON COMMANDE ICI, ON NE PART PLUS SUR WHATSAPP.
              Demande de Mongazi (2026-08-26) : « on doit pouvoir commander
              directement depuis la hero, ajouter au panier aussi ». Avant, ce
              bouton ouvrait WhatsApp avec une phrase toute faite : le client
              quittait le site avant d'avoir choisi son accompagnement, et la
              maison recevait une commande incomplète.
              Le bouton ouvre maintenant LA FICHE DU MENU — la vraie, avec ses
              garnitures et son accompagnement obligatoire — et la sauce tombe
              dans le même panier que le reste. Voir `data/commande.ts`.
              ⚠️ Le repli WhatsApp reste : si la carte n'est pas encore montée,
              `commander()` renvoie faux et le client n'est pas laissé sans
              rien. */}
          {/* ⚠️ LA COULEUR EST DANS UNE CLASSE, PAS EN STYLE EN LIGNE. Deux
              raisons, et la seconde est une ceinture : une classe survit à
              tout `clearProps`, et elle ne dépend pas de l'ordre des tweens. */}
          <button
            type="button"
            className="ic-item btn-commander inline-flex w-full items-center justify-center gap-2 rounded-full px-4 py-3 text-[0.85rem] font-semibold transition hover:brightness-125"
            onClick={() => {
              if (!commander(dish.nom)) window.open(lienCommande(dish), "_blank");
            }}
          >
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden>
              <path d="M12 5v14M5 12h14" />
            </svg>
            Ajouter au panier
          </button>

          {dish.avis && (
            <p className="ic-item mt-3 text-center text-[0.75rem] text-[color:var(--encre-2)] opacity-75">
              {dish.avis.note.toFixed(1)} ★ · {dish.avis.nombre} avis
            </p>
          )}
        </>
      ) : (
        <div className="text-[0.85rem] leading-[1.6] text-[color:var(--encre-2)]">
          <p className="mb-3">{dish.desc}</p>
          {/* ⚠️ CETTE LISTE ÉTAIT FAUSSE, ET ELLE L'EST RESTÉE LONGTEMPS.
              Elle recopiait les accompagnements des GRILLADES (riz, attiéké,
              aloco…) alors que le héros ne montre que des sauces, qui se
              servent avec le telibo, l'agbéli, le wassa wassa, le foutou.
              Elle est maintenant LUE dans la carte : la maison change sa
              liste, la ligne suit. */}
          <p className="opacity-80">
            Accompagnements au choix : {ACC.sauces.join(", ").toLowerCase()}.
          </p>
        </div>
      )}
    </aside>
  );
}
