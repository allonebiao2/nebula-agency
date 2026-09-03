"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import Image from "next/image";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CustomEase } from "gsap/CustomEase";
import { DISHES } from "@/data/dishes";
import Ardoise from "./Ardoise";
import DishText from "./DishText";
import InfoCard from "./InfoCard";
import Rail from "./Rail";
import { TopBar, BottomNav, Indicator } from "./Chrome";
import Categories from "./Categories";

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
 * pas. Ce mouvement-là n'a pas bougé d'un pixel : c'est son MOTEUR qui a
 * changé.
 */

/**
 * ⚠️⚠️ LE DÉFILEMENT N'EST PLUS LE MOTEUR (2026-08-26). C'est le changement
 * le plus important de ce fichier, et il vient d'une demande de Mongazi :
 * « je veux que TOUTES les sauces soient dans le carrousel de la hero, et que
 * ce carrousel avance tout seul et beaucoup plus vite ».
 *
 * L'ancienne scène était une piste de N × 100vh que le défilement parcourait
 * (« scrub » + aimant). À quatre plats, cela faisait 400vh : un beau voyage.
 * À QUATORZE SAUCES, cela ferait **1 400vh** — quatorze écrans à traverser
 * avant d'atteindre la carte. Sur un catalogue de restaurant, c'est un mur.
 * Et une cadence « beaucoup plus rapide » aurait fait DÉFILER LA PAGE toute
 * seule à toute vitesse, ce qui n'est pas un carrousel, c'est une fuite.
 *
 * Donc : la scène tient sur UN écran, et l'index des assiettes est piloté par
 * un tween sur un simple nombre. Le défilement redevient ce qu'il doit être —
 * la façon d'aller à la carte.
 *
 * ✅ Trois choses tombent d'elles-mêmes avec ce changement :
 *   - la vieille crainte « rebouler ferait REMONTER la page » n'existe plus,
 *     puisque avancer ne touche plus au défilement. La boucle est franche,
 *     sans le tour de respiration qu'il avait fallu ajouter le 2026-08-21 ;
 *   - le carrousel tourne dans les deux sens par le chemin le plus court :
 *     de la 14e à la 1re, on avance d'un cran, on ne recule pas de treize ;
 *   - on peut enfin COMMANDER depuis le héros sans que la scène se dérobe
 *     sous le doigt (voir `pause`).
 *
 * ⚠️ Lenis reste, et ce n'est pas un oubli : `components/aller.ts` passe par
 * `window.__lenis` pour sauter aux catégories du menu. Un `scrollIntoView`
 * lancé à côté de Lenis s'arrête en chemin (mesuré en ligne : le saut vers
 * « Cocktails » restait à 7 382 px de sa cible).
 */

/** Une sauce toutes les 2,8 s. ⚠️ C'était 5,5 s : « beaucoup plus vite ». */
const TOUR = 2800;
/** La durée d'un passage. Plus court que 0,62 s, la rotation devient un saut. */
const GLISSE = 0.62;
/** Un vrai geste repousse le tour : on ne vole pas la main de quelqu'un qui
 *  est en train de choisir sa sauce. */
const REPOS = 7000;
/**
 * ⚠️ COMBIEN D'ASSIETTES RESTENT VIVANTES AUTOUR DE LA COURANTE.
 * À quatre plats, on pouvait tout repositionner à chaque image. À quatorze,
 * c'est 14 × 7 propriétés par image pour douze assiettes invisibles. Au-delà
 * de cette fenêtre, l'assiette est RANGÉE une fois pour toutes (opacité 0) et
 * on ne la retouche plus tant qu'elle ne revient pas.
 */
const FENETRE = 2;

const N = DISHES.length;

/** L'écart le plus court sur un anneau : de la 14e à la 1re, c'est +1. */
function ecart(vers: number, depuis: number) {
  let d = vers - depuis;
  while (d > N / 2) d -= N;
  while (d < -N / 2) d += N;
  return d;
}

const modN = (x: number) => ((x % N) + N) % N;

export default function Experience() {
  const [i, setI] = useState(0);
  const [carteOuverte, setCarteOuverte] = useState(false);
  /**
   * ⚠️ LES IMAGES N'ARRIVENT PAS TOUTES EN MÊME TEMPS. Les quatorze découpes
   * pèsent ensemble plus de 2 Mo : les monter d'un coup, c'est refaire la
   * faute des fonds CSS de l'ancien site (4,3 Mo avant même le menu). On ne
   * monte que celles qu'on a approchées, et la liste ne fait que grandir :
   * une assiette déjà chargée ne se recharge jamais.
   */
  const [vus, setVus] = useState<number[]>(() =>
    Array.from(new Set([0, 1, 2, modN(-1)]))
  );

  const iRef = useRef(0);
  /** La position continue sur l'anneau. Le tween tire dessus, `poser` la lit. */
  const fRef = useRef({ v: 0 });
  const scene = useRef<HTMLDivElement>(null);
  const plats = useRef<(HTMLDivElement | null)[]>([]);
  const lenisRef = useRef<Lenis | null>(null);
  const tween = useRef<gsap.core.Tween | null>(null);
  /** Vrai quand quelqu'un regarde ou touche : la scène attend. */
  const pause = useRef(false);
  const visible = useRef(true);

  /* ── poser les assiettes à une position donnée ─────────────────── */
  const poser = useCallback((f: number) => {
    plats.current.forEach((el, k) => {
      if (!el) return;
      const d = ecart(k, f) * -1; // >0 : l'assiette est déjà passée
      const loin = Math.abs(d) > FENETRE + 0.25;
      if (loin) {
        // ⚠️ RANGÉE UNE SEULE FOIS. Sans ce garde, on réécrivait sept
        // propriétés par image sur douze assiettes qu'on ne voit pas.
        if (el.dataset.gare === "1") return;
        el.dataset.gare = "1";
        gsap.set(el, { opacity: 0, pointerEvents: "none", zIndex: 0 });
        return;
      }
      el.dataset.gare = "0";
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
    const n = modN(Math.round(f));
    if (n !== iRef.current) {
      iRef.current = n;
      setI(n);
    }
  }, []);

  /* ── aller à une sauce, par le chemin le plus court ─────────────── */
  const aller = useCallback(
    (n: number) => {
      const doux = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const cible = fRef.current.v + ecart(modN(n), fRef.current.v);
      tween.current?.kill();
      if (doux) {
        fRef.current.v = modN(cible);
        poser(fRef.current.v);
        return;
      }
      tween.current = gsap.to(fRef.current, {
        v: cible,
        duration: GLISSE,
        ease: "braise",
        overwrite: true,
        onUpdate: () => poser(fRef.current.v),
        onComplete: () => {
          // on ramène la position dans [0, N[ : sans ça, elle dérive à
          // l'infini et les comparaisons finissent par perdre en précision.
          fRef.current.v = modN(cible);
          poser(fRef.current.v);
        },
      });
    },
    [poser]
  );

  /* ── Lenis : le défilement de la page, et rien de plus ──────────── */
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
    /* ⚠️ LENIS TIENT LE DÉFILEMENT DE TOUTE LA PAGE. Un `scrollIntoView` lancé
       ailleurs se bat contre lui et s'arrête en chemin. On expose donc
       l'instance, et tout ce qui veut déplacer la page passe par elle. */
    (window as unknown as { __lenis?: Lenis }).__lenis = lenis;
    lenis.on("scroll", ScrollTrigger.update);
    const raf = (t: number) => lenis.raf(t * 1000);
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);

    /* ⚠️ POSER AU MONTAGE, PAS SEULEMENT AU PREMIER MOUVEMENT. Sans cet appel,
       les quatorze assiettes restent empilées à l'écran, toutes visibles,
       l'une sur l'autre. Le défaut ne se voit qu'au premier écran, celui que
       tout le monde voit. */
    poser(0);

    return () => {
      gsap.ticker.remove(raf);
      lenis.destroy();
      delete (window as unknown as { __lenis?: Lenis }).__lenis;
      lenisRef.current = null;
    };
  }, [poser]);

  /* ── la fenêtre d'images suit la sauce courante ─────────────────── */
  useEffect(() => {
    setVus((v) => {
      const s = new Set(v);
      for (let k = -1; k <= 2; k++) s.add(modN(i + k));
      return s.size === v.length ? v : Array.from(s);
    });
  }, [i]);

  /* ── la scène ne tourne que si elle est à l'écran ───────────────── */
  useEffect(() => {
    const el = scene.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => {
        visible.current = e.isIntersecting;
      },
      { threshold: 0.35 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  /* ── LES SAUCES DÉFILENT TOUT SEULES, VITE ──────────────────────
     Quatre garde-fous, et aucun n'est facultatif :
     1. ⛔ RIEN ne bouge si le visiteur a demandé moins d'animations
        (`prefers-reduced-motion`) : pour certains c'est une demande médicale.
     2. ⛔ RIEN ne bouge quand la scène n'est plus à l'écran, ni quand
        l'onglet est en arrière-plan : une scène qui tourne dans le vide,
        c'est de la batterie prise à quelqu'un qui lit la carte.
     3. ⛔ RIEN ne bouge tant qu'une fiche de commande est ouverte. La fiche
        bloque le défilement du corps : c'est ce signal qu'on lit. Sans ça,
        la sauce changerait DERRIÈRE la fiche pendant qu'on choisit son
        accompagnement, et on ajouterait au panier autre chose que ce qu'on
        regardait.
     4. ⚠️ RIEN ne bouge sous le curseur ou sous le doigt. À 2,8 s, une scène
        qui avance pendant qu'on vise « Ajouter » rend le bouton inatteignable.
        C'est la contrepartie de la vitesse demandée.
     5. Un vrai geste repousse le tour de 7 s. */
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let minuteur = 0 as ReturnType<typeof setTimeout> | 0;
    let reprise = 0 as ReturnType<typeof setTimeout> | 0;

    const bloque = () =>
      document.hidden ||
      !visible.current ||
      pause.current ||
      document.body.style.overflow === "hidden";

    const relancer = (sup = 0) => {
      if (minuteur) clearTimeout(minuteur);
      minuteur = setTimeout(tourner, TOUR + sup);
    };
    function tourner() {
      minuteur = 0;
      if (bloque()) return relancer();
      aller(iRef.current + 1);
      relancer();
    }
    const repousser = () => {
      if (minuteur) {
        clearTimeout(minuteur);
        minuteur = 0;
      }
      if (reprise) clearTimeout(reprise);
      reprise = setTimeout(() => relancer(), REPOS);
    };

    const surVisibilite = () => {
      if (document.hidden) {
        if (minuteur) {
          clearTimeout(minuteur);
          minuteur = 0;
        }
      } else relancer();
    };

    document.addEventListener("visibilitychange", surVisibilite);
    window.addEventListener("keydown", repousser);
    const t0 = setTimeout(() => relancer(), 1400); // la 1re sauce se laisse lire

    return () => {
      clearTimeout(t0);
      if (minuteur) clearTimeout(minuteur);
      if (reprise) clearTimeout(reprise);
      document.removeEventListener("visibilitychange", surVisibilite);
      window.removeEventListener("keydown", repousser);
    };
  }, [aller]);

  /* ── clavier : GAUCHE / DROITE ──────────────────────────────────
     ⚠️ Plus HAUT / BAS : ces deux touches doivent redéfiler la page, comme
     partout ailleurs. Les prendre au héros, c'était emprisonner le visiteur
     dans le premier écran. */
  useEffect(() => {
    const f = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") aller(iRef.current + 1);
      if (e.key === "ArrowLeft") aller(iRef.current - 1);
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, [aller]);

  /* ── le doigt : on fait glisser les assiettes ───────────────────
     ⚠️ `touch-action: pan-y` sur la zone : le geste horizontal est à nous,
     le vertical reste au navigateur. Sans ça, on vole le défilement de la
     page à quelqu'un qui voulait juste descendre voir la carte. */
  useEffect(() => {
    const el = scene.current;
    if (!el) return;
    let x0 = 0,
      y0 = 0,
      actif = false;

    const bas = (e: PointerEvent) => {
      if ((e.target as HTMLElement).closest("button,a,input,[role=dialog]")) return;
      actif = true;
      x0 = e.clientX;
      y0 = e.clientY;
      pause.current = true;
    };
    const haut = (e: PointerEvent) => {
      pause.current = false;
      if (!actif) return;
      actif = false;
      const dx = e.clientX - x0;
      const dy = e.clientY - y0;
      // un geste horizontal franc, et pas un début de défilement vertical
      if (Math.abs(dx) > 44 && Math.abs(dx) > Math.abs(dy) * 1.4) {
        aller(iRef.current + (dx < 0 ? 1 : -1));
      }
    };
    const perdu = () => {
      actif = false;
      pause.current = false;
    };

    el.addEventListener("pointerdown", bas);
    window.addEventListener("pointerup", haut);
    window.addEventListener("pointercancel", perdu);
    return () => {
      el.removeEventListener("pointerdown", bas);
      window.removeEventListener("pointerup", haut);
      window.removeEventListener("pointercancel", perdu);
    };
  }, [aller]);

  /* ── le tilt 3D à la souris, très léger, et jamais au doigt ────── */
  useEffect(() => {
    const el = scene.current;
    if (!el || window.matchMedia("(pointer: coarse)").matches) return;
    const q = plats.current.map((p) =>
      p
        ? {
            rx: gsap.quickTo(p, "rotationX", { duration: 0.6, ease: "power2.out" }),
            ry: gsap.quickTo(p, "rotationY", { duration: 0.6, ease: "power2.out" }),
          }
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
  const vu = (k: number) => vus.includes(k);

  return (
    /* ⚠️ UN SEUL ÉCRAN, PLUS UNE PISTE DE N × 100vh. Voir la note du haut :
       à quatorze sauces, la piste aurait fait quatorze écrans de haut. */
    <div
      ref={scene}
      /* ⚠️ UN REPÈRE POUR LE CONTRÔLE, ET RIEN D'AUTRE. Sans lui, vérifier
         « la scène avance-t-elle toute seule ? » revenait à photographier
         l'écran et à comparer deux images — un contrôle qui échoue au hasard.
         Le numéro de la sauce courante est écrit là, `_outils/_qc.py` le lit. */
      data-sauce={i}
      className="relative h-screen overflow-hidden"
      style={{
        background:
          `radial-gradient(120% 90% at 78% 18%, ${plat.wash}, transparent 62%),` +
          "linear-gradient(180deg, var(--mur) 0%, var(--mur-2) 100%)",
        transition: "background 900ms cubic-bezier(.16,1,.3,1)",
        touchAction: "pan-y",
      }}
      /* ⚠️ ON NE MET PAS EN PAUSE PARCE QUE LA SOURIS EST « QUELQUE PART ».
         Premier jet : `onPointerEnter` sur la scène. Or la scène fait tout
         l'écran, et la souris d'un visiteur est TOUJOURS quelque part
         dessus : le carrousel ne repartait jamais sur un ordinateur, et on
         aurait conclu qu'il est cassé. On ne s'arrête que là où l'on vise
         quelque chose : la carte de verre (le bouton « Ajouter au panier »)
         et la bande des miniatures. Au doigt, c'est `pointerdown` qui s'en
         charge. */
      onPointerOver={(e) => {
        if (window.matchMedia("(pointer: coarse)").matches) return;
        pause.current = !!(e.target as HTMLElement).closest(".scene-carte,.rail-bas");
      }}
      onPointerLeave={() => {
        pause.current = false;
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

      <TopBar onCarte={() => setCarteOuverte(true)} />
      <Indicator n={N} actif={i} onAller={aller} />

      {/* ⚠️ `scene-stack` est en `display: contents` sur grand écran : il
          n'existe pas, et l'assiette, le titre et la carte restent posés en
          absolu comme dans la référence. Sur téléphone il devient une
          COLONNE et les trois s'empilent pour de vrai. */}
      <div className="scene-stack">
        {/* ⚠️ `pointer-events-none` : ce conteneur fait tout l'écran et il est
            posé APRÈS les boutons du haut. Sans ça il les recouvre et il avale
            leurs clics. Le défaut est invisible à l'œil : le bouton s'affiche,
            s'illumine au survol, et ne fait rien. */}
        <div className="pointer-events-none absolute inset-0 grid place-items-center max-md:static max-md:block">
          <div className="scene-plat relative" style={{ perspective: "1000px" }}>
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
                  {d.img ? (
                    vu(k) && (
                      <Image
                        src={d.img}
                        alt={`${d.line1} ${d.line2}`}
                        fill
                        priority={k === 0}
                        sizes="(max-width: 768px) 80vw, 46vw"
                        className="object-contain drop-shadow-[0_25px_50px_rgba(0,0,0,0.18)]"
                      />
                    )
                  ) : (
                    /* ⚠️ LA MAISON N'A PAS ENCORE ENVOYÉ CETTE PHOTO. On écrit
                       le nom sur une ardoise ronde, à la place de l'assiette :
                       la sauce reste visible, cliquable et commandable. Un
                       cadre vide, lui, dirait que le site est en travaux. */
                    <Ardoise nom={d.nom} forme="assiette" teinte={d.tint} />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <DishText dish={plat} />
        <InfoCard dish={plat} />
      </div>

      <Rail actif={i} onAller={aller} />
      <Categories ouvert={carteOuverte} onFermer={() => setCarteOuverte(false)} />
      <BottomNav />
    </div>
  );
}
