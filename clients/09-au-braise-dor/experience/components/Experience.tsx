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
 * LE MOUVEMENT DES ASSIETTES : ELLES ROULENT SUR UN ARC.
 *
 * ⚠️ PREMIÈRE VERSION FAUSSE, et Mongazi l'a vue tout de suite : je faisais
 * monter l'assiette tout droit, du bas vers le haut. La vidéo de référence,
 * relue image par image à 12 centièmes d'intervalle, montre autre chose :
 * **celle qui arrive vient du HAUT À DROITE, descend en tournant sur
 * elle-même, et celle qui part continue vers le BAS À GAUCHE.** Elle roule.
 *
 * D'où les trois mouvements combinés au lieu d'un seul : un déplacement en
 * diagonale (74 % de large, 66 % de haut par plat), une rotation de presque un
 * quart de tour, et l'échelle qui recule. C'est la rotation qui fait la
 * différence : sans elle, une diagonale reste un glissement, et on ne « roule »
 * pas.
 */

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
          xPercent: -d * 74,
          yPercent: d * 66,
          scale: 1 - a * 0.34,
          rotate: d * 88,
          opacity: 1 - Math.pow(a, 1.5),
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

  /* ── LES PLATS DÉFILENT TOUT SEULS ──────────────────────────────
     Demande de Mongazi : « le défilement doit être automatique, sans
     intervention humaine. » Un plat toutes les 5,5 s.

     Quatre garde-fous, et aucun n'est facultatif :
     1. ⛔ RIEN ne bouge si le visiteur a demandé moins d'animations
        (`prefers-reduced-motion`) : pour certains c'est une demande médicale.
     2. ⛔ RIEN ne bouge quand la scène n'est plus à l'écran. Sans ça, le site
        REMONTERAIT tout seul pendant qu'on lit la carte : le pire défaut
        qu'une page puisse avoir.
     3. ⛔ RIEN ne bouge quand l'onglet est en arrière-plan.
     4. ⚠️ ON AVANCE, ON NE BOUCLE PAS. Arrivé au dernier plat, on s'arrête.
        Reboucler obligerait la page à remonter d'elle-même vers le premier
        plat, en travers de quelqu'un qui descend vers le menu. Un site ne se
        bat pas contre le doigt de son visiteur.
     5. Un vrai geste repousse le tour de 12 s : on ne vole pas la main. */
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const TOUR = 5500,
      REPOS = 12000;
    let minuteur = 0 as ReturnType<typeof setTimeout> | 0;
    let reprise = 0 as ReturnType<typeof setTimeout> | 0;

    const visible = () => {
      const el = scene.current?.querySelector(".sticky");
      if (!el) return false;
      const r = el.getBoundingClientRect();
      return r.top > -40 && r.bottom > window.innerHeight * 0.75;
    };

    const tourner = () => {
      minuteur = 0;
      if (document.hidden || !visible()) return relancer();
      if (iRef.current >= N - 1) return;      // arrivé au bout : on s'arrête
      aller(iRef.current + 1);
      relancer();
    };
    const relancer = () => {
      if (minuteur) clearTimeout(minuteur);
      minuteur = setTimeout(tourner, TOUR);
    };
    const repousser = () => {
      if (minuteur) { clearTimeout(minuteur); minuteur = 0; }
      if (reprise) clearTimeout(reprise);
      reprise = setTimeout(relancer, REPOS);
    };

    const surVisibilite = () => {
      if (document.hidden) { if (minuteur) { clearTimeout(minuteur); minuteur = 0; } }
      else relancer();
    };

    document.addEventListener("visibilitychange", surVisibilite);
    window.addEventListener("wheel", repousser, { passive: true });
    window.addEventListener("touchstart", repousser, { passive: true });
    window.addEventListener("keydown", repousser);
    const t0 = setTimeout(relancer, 2200);   // le premier plat se laisse lire

    return () => {
      clearTimeout(t0);
      if (minuteur) clearTimeout(minuteur);
      if (reprise) clearTimeout(reprise);
      document.removeEventListener("visibilitychange", surVisibilite);
      window.removeEventListener("wheel", repousser);
      window.removeEventListener("touchstart", repousser);
      window.removeEventListener("keydown", repousser);
    };
  }, [aller, N]);

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
