"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import Image from "next/image";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CustomEase } from "gsap/CustomEase";
import { DISHES } from "@/data/dishes";
import DishText from "./DishText";
import InfoCard from "./InfoCard";
import Rail from "./Rail";
import { TopBar, BottomNav, Indicator } from "./Chrome";

gsap.registerPlugin(ScrollTrigger, CustomEase);

/**
 * LA SCÈNE.
 *
 * Le principe de la référence : le fond ne bouge JAMAIS. C'est un plateau sur
 * lequel des objets flottent. Tout le mouvement est dans les assiettes, le
 * titre et la carte de verre.
 *
 * Le défilement n'est pas du contenu, c'est un MOTEUR : une piste de N × 100vh
 * qu'on ne voit pas, dont la progression pilote directement la position des
 * assiettes (« scrub »), avec un aimant (« snap ») pour qu'on s'arrête toujours
 * sur un plat et jamais entre deux.
 *
 * ⚠️ Les assiettes sont TOUTES montées en même temps et empilées : on ne
 * démonte pas un plat pour en monter un autre, sinon la transition attend le
 * décodage de l'image et saccade au premier passage.
 */
export default function Experience() {
  const [i, setI] = useState(0);          // le plat courant, entier
  const iRef = useRef(0);
  const scene = useRef<HTMLDivElement>(null);
  const piste = useRef<HTMLDivElement>(null);
  const plats = useRef<(HTMLDivElement | null)[]>([]);
  const lenisRef = useRef<Lenis | null>(null);
  const N = DISHES.length;

  /* ── le moteur : Lenis + ScrollTrigger scrubbé, avec aimant ────── */
  useLayoutEffect(() => {
    const doux = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    CustomEase.create("braise", "0.16,1,0.3,1");

    const lenis = new Lenis({
      duration: doux ? 0 : 1.05,
      smoothWheel: !doux,
      // ⚠️ AU DOIGT ON LAISSE LE NAVIGATEUR. Reprendre l'inertie tactile, c'est
      // casser le défilement sur téléphone : le doigt a déjà sa physique.
      syncTouch: false,
    });
    lenisRef.current = lenis;
    lenis.on("scroll", ScrollTrigger.update);
    const raf = (t: number) => lenis.raf(t * 1000);
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);

    /* ⚠️ CETTE FONCTION DOIT ETRE APPELEE AU MONTAGE, pas seulement au
       defilement. Sans ca, tant que personne n'a scrolle, les quatre assiettes
       restent empilees a l'ecran, toutes visibles, l'une sur l'autre. Le
       defaut ne se voit qu'au premier ecran, celui que tout le monde voit. */
    const poser = (f: number) => {
      plats.current.forEach((el, k) => {
        if (!el) return;
        const d = f - k;
        const a = Math.min(1, Math.abs(d));
        gsap.set(el, {
          yPercent: -d * 118,
          scale: 1 - a * 0.4,
          rotate: d * 5,
          opacity: 1 - Math.pow(a, 1.4),
          zIndex: 10 - Math.round(a * 10),
          pointerEvents: a > 0.5 ? "none" : "auto",
        });
      });
      const n = Math.round(f);
      if (n !== iRef.current) {
        iRef.current = n;
        setI(n);
      }
    };
    poser(0);

    const ctx = gsap.context(() => {
      const st = ScrollTrigger.create({
        trigger: piste.current,
        start: "top top",
        end: "bottom bottom",
        scrub: doux ? false : 0.6,
        snap: doux
          ? undefined
          : {
              snapTo: 1 / (N - 1),
              duration: { min: 0.35, max: 0.9 },   // 0,8 à 1,2 s ressenti
              ease: "power3.inOut",
              inertia: false,
            },
        onUpdate: (self) => poser(self.progress * (N - 1)),
      });
      return () => st.kill();
    }, scene);

    return () => {
      ctx.revert();
      gsap.ticker.remove(raf);
      lenis.destroy();
      lenisRef.current = null;
    };
  }, [N]);

  /* ── aller à un plat : par le carrousel, les points, le clavier ── */
  const aller = useCallback(
    (n: number) => {
      const k = Math.max(0, Math.min(N - 1, n));
      const h = (piste.current?.offsetHeight ?? 0) - window.innerHeight;
      lenisRef.current?.scrollTo((h * k) / (N - 1), { duration: 1.0 });
    },
    [N]
  );

  useEffect(() => {
    const f = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown" || e.key === "PageDown") aller(iRef.current + 1);
      if (e.key === "ArrowUp" || e.key === "PageUp") aller(iRef.current - 1);
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, [aller]);

  /* ── le tilt 3D à la souris, très léger, et jamais au doigt ────── */
  useEffect(() => {
    const el = scene.current;
    if (!el || window.matchMedia("(pointer: coarse)").matches) return;
    const q = plats.current.map((p) =>
      p ? { rx: gsap.quickTo(p, "rotationX", { duration: 0.6, ease: "power2.out" }),
            ry: gsap.quickTo(p, "rotationY", { duration: 0.6, ease: "power2.out" }) }
        : null
    );
    const f = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = (e.clientY / window.innerHeight - 0.5) * 2;
      q.forEach((h) => {
        if (!h) return;
        h.rx(-y * 5);
        h.ry(x * 5);
      });
    };
    el.addEventListener("mousemove", f);
    return () => el.removeEventListener("mousemove", f);
  }, []);

  const plat = DISHES[i];

  return (
    /* ⚠️ `sticky`, PAS `fixed`. Une scène en `fixed` ne se décolle jamais :
       elle serait restée par-dessus les 48 plats, en travers de la carte.
       En `sticky` dans un parent haut de N × 100vh, elle tient l'écran le
       temps du voyage puis rend la main exactement à la fin. */
    <div ref={scene} className="relative" style={{ height: `${N * 100}vh` }}>
      <div ref={piste} className="absolute inset-0" aria-hidden />

      <div
        className="sticky top-0 h-screen overflow-hidden"
        style={{
          background:
            `radial-gradient(120% 90% at 78% 18%, ${plat.wash}, transparent 62%),` +
            "linear-gradient(180deg, var(--mur) 0%, var(--mur-2) 100%)",
          transition: "background 900ms cubic-bezier(.16,1,.3,1)",
        }}
      >
        {/* le mur : une pièce, pas un aplat. Ombre douce venue de la gauche. */}
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(70% 55% at 8% 0%, rgba(255,255,255,.65), transparent 60%)," +
              "radial-gradient(90% 70% at 50% 118%, rgba(0,0,0,.10), transparent 60%)",
          }}
          aria-hidden
        />

        <TopBar />
        <Indicator n={N} actif={i} onAller={aller} />

        {/* ⚠️ `scene-stack` est en `display: contents` sur grand écran : il
            n'existe pas, et l'assiette, le titre et la carte restent posés en
            absolu comme dans la référence. Sur téléphone il devient une
            COLONNE et les trois s'empilent pour de vrai.
            Pourquoi : positionner en pourcentages de hauteur ne marche pas
            quand les blocs, eux, font une hauteur en pixels. À 640 px de haut,
            le titre et la carte se chevauchaient quoi qu'on règle. On
            n'empile pas des boîtes à la main, on laisse le navigateur le
            faire. */}
        <div className="scene-stack">
        <div className="absolute inset-0 grid place-items-center max-md:static max-md:block">
          <div
            className="scene-plat relative"
            style={{ perspective: "1000px" }}
          >
            {DISHES.map((d, k) => (
              <div
                key={d.id}
                ref={(el) => {
                  plats.current[k] = el;
                }}
                className="absolute inset-0 will-change-transform"
                style={{ transformStyle: "preserve-3d" }}
              >
                <div className="assiette-flotte relative h-full w-full">
                  <Image
                    src={d.img}
                    alt={`${d.line1} ${d.line2}`}
                    fill
                    priority={k === 0}
                    sizes="(max-width: 768px) 80vw, 46vw"
                    className="object-contain drop-shadow-[0_25px_50px_rgba(0,0,0,0.18)]"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <DishText dish={plat} />
        <InfoCard dish={plat} />
        </div>
        <Rail actif={i} onAller={aller} />
        <BottomNav />
      </div>
    </div>
  );
}
