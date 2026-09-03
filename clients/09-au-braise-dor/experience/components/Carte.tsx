"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ACC, CARTE, NB_PLATS, type Cat, type Plat } from "@/data/carte";
import { fmt, prix } from "@/data/prix";
import { brancherCommande } from "@/data/commande";
import Ardoise from "./Ardoise";
import { WHATSAPP } from "@/data/dishes";
import { allerA } from "./aller";

gsap.registerPlugin(ScrollTrigger);

/**
 * LA CARTE COMPLÈTE, sous l'expérience.
 *
 * ⚠️ ELLE ÉTAIT SOMBRE, ELLE EST DEVENUE CLAIRE (2026-08-12). Mongazi, en
 * défilant : « quand je défile c'est exactement comme la première version, je
 * veux que ça devienne en entièreté comme ma hero actuelle. » Il avait raison :
 * le site racontait deux histoires, la vitrine crème puis l'ancien site braise
 * en dessous. On ne change pas de maison au milieu d'une page.
 * Toutes les couleurs sortent désormais des mêmes jetons que la scène.
 *
 * ⚠️ LES 48 PHOTOS SONT DIFFÉRÉES (`loading="lazy"`). Sur l'ancien site elles
 * étaient posées en fond CSS, que le navigateur ne sait pas différer : il
 * téléchargeait 4,3 Mo avant même qu'on arrive au menu.
 */

type Ligne = {
  cle: string;
  nom: string;
  taille?: string;
  acc?: string;
  /** Ce que le client a demandé dans sa sauce. */
  dedans?: string[];
  unite: number;
  /** ⚠️ BORNE HAUTE, quand le prix est une fourchette. Le prix d'une sauce
   *  dépend de ce qu'on met dedans, et la maison le confirme à la commande :
   *  le panier affiche donc « de X à Y », jamais un total inventé. */
  uniteMax?: number;
  qte: number;
};

export default function Carte() {
  /* ⚠️ PLUS DE FILTRE, DES ANCRES. Le filtre masquait les sept autres univers :
     choisir « Pizza » faisait disparaître 38 plats. Sur un catalogue, ce qu'on
     cache ne se vend pas. Tout reste affiché, la barre sert à SAUTER, et la
     catégorie active suit le défilement toute seule. */
  const [actif, setActif] = useState<string>(CARTE[0].id);
  const [ouvert, setOuvert] = useState<{ cat: Cat; plat: Plat } | null>(null);
  const [panier, setPanier] = useState<Ligne[]>([]);
  const [mode, setMode] = useState<"place" | "emporter" | "livraison">("place");
  const zone = useRef<HTMLElement>(null);

  const total = useMemo(
    () => panier.reduce((s, l) => s + l.unite * l.qte, 0),
    [panier]
  );
  const totalMax = useMemo(
    () => panier.reduce((s, l) => s + (l.uniteMax ?? l.unite) * l.qte, 0),
    [panier]
  );
  const nb = useMemo(() => panier.reduce((s, l) => s + l.qte, 0), [panier]);

  /* la catégorie affichée dans la barre suit le défilement */
  useEffect(() => {
    const obs = new IntersectionObserver(
      (es) => {
        const vus = es
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (vus[0]) setActif(vus[0].target.id.replace("cat-", ""));
      },
      { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
    );
    CARTE.forEach((c) => {
      const e = document.getElementById("cat-" + c.id);
      if (e) obs.observe(e);
    });
    return () => obs.disconnect();
  }, []);

  function sauter(id: string) {
    allerA("cat-" + id);
  }

  /* ── LE HÉROS COMMANDE PAR ICI ──────────────────────────────────
     ⚠️ Le héros ne sait pas ajouter au panier, et c'est voulu : il DEMANDE
     à la carte d'ouvrir la fiche du plat, et c'est la fiche du menu qui
     s'ouvre, avec ses garnitures, son accompagnement obligatoire et sa
     fourchette. Un second moteur de commande dans le héros aurait fini par
     vendre un autre prix. Voir `data/commande.ts`. */
  useEffect(() => {
    brancherCommande((nom) => {
      for (const c of CARTE) {
        const p = c.items.find((x) => x.n === nom);
        if (p) {
          setOuvert({ cat: c, plat: p });
          return true;
        }
      }
      return false;
    });
    return () => brancherCommande(null);
  }, []);

  /* ── LA BARRE SE SIGNALE QUAND ELLE GROSSIT ─────────────────────
     ⚠️ Une sauce ajoutée depuis le héros tombe dans une barre située tout en
     bas de l'écran : sans un mouvement, on ne voit pas que le geste a marché,
     et on réappuie. Un battement d'une demi-seconde suffit à le dire. */
  /* ⚠️ LA BARRE DU PANIER EST FIXE, ET DEPUIS LE 2026-08-26 ELLE PEUT
     APPARAÎTRE PENDANT QU'ON EST ENCORE SUR LE HÉROS. Elle se posait alors
     par-dessus la barre du bas de la scène et le carrousel des sauces : deux
     rangées de boutons rendues inutilisables par une troisième. Le héros ne
     sait pas ce que fait le panier, mais le corps du document, si. */
  /* ⚠️ ON MESURE LA BARRE, ON NE DEVINE PAS SA HAUTEUR. Premier jet : des
     valeurs en `rem` écrites à la main dans le CSS. Le QC a mesuré **8 px de
     recouvrement** sur la barre du bas en 390 px, parce que la barre passe à
     la ligne sur téléphone et devient plus haute que prévu. Une hauteur
     supposée est une hauteur fausse le jour où le contenu change. */
  const barre = useRef<HTMLDivElement>(null);
  useEffect(() => {
    document.body.classList.toggle("a-panier", nb > 0);
    const el = barre.current;
    if (!nb || !el) {
      document.body.style.removeProperty("--barre-h");
      return;
    }
    const mesurer = () =>
      document.body.style.setProperty("--barre-h", el.offsetHeight + "px");
    mesurer();
    const ro = new ResizeObserver(mesurer);
    ro.observe(el);
    return () => ro.disconnect();
  }, [nb]);

  useEffect(
    () => () => {
      document.body.classList.remove("a-panier");
      document.body.style.removeProperty("--barre-h");
    },
    []
  );

  const nbAvant = useRef(0);
  const [bat, setBat] = useState(false);
  useEffect(() => {
    if (nb > nbAvant.current) {
      setBat(true);
      const t = setTimeout(() => setBat(false), 520);
      nbAvant.current = nb;
      return () => clearTimeout(t);
    }
    nbAvant.current = nb;
  }, [nb]);

  /* les blocs de catégorie se révèlent à l'arrivée, une seule fois */
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>(".ct-bloc").forEach((b) => {
        gsap.fromTo(
          b.querySelectorAll(".ct-item"),
          { autoAlpha: 0, y: 24 },
          {
            autoAlpha: 1,
            y: 0,
            duration: 0.55,
            ease: "power2.out",
            stagger: 0.045,
            clearProps: "all",
            scrollTrigger: { trigger: b, start: "top 82%", once: true },
          }
        );
      });
    }, zone);
    return () => ctx.revert();
  }, []);

  function ajouter(l: Omit<Ligne, "cle">) {
    const cle = [l.nom, l.taille ?? "", l.acc ?? "", (l.dedans ?? []).join(",")].join("|");
    setPanier((p) => {
      const i = p.findIndex((x) => x.cle === cle);
      if (i < 0) return [...p, { ...l, cle }];
      const c = [...p];
      c[i] = { ...c[i], qte: c[i].qte + l.qte };
      return c;
    });
    setOuvert(null);
  }

  function message() {
    const lieu =
      mode === "place" ? "Sur place" : mode === "emporter" ? "À emporter" : "Livraison";
    const lignes = panier
      .map(
        (l) =>
          `• ${l.qte} × ${l.nom}` +
          (l.taille ? ` (${l.taille})` : "") +
          (l.dedans?.length ? ` avec ${l.dedans.join(", ")}` : "") +
          (l.acc ? ` + ${l.acc}` : "") +
          ` — ${prix(l.unite * l.qte, l.uniteMax ? l.uniteMax * l.qte : undefined)}`
      )
      .join("\n");
    /* ⚠️ QUAND IL Y A UNE FOURCHETTE, ON LE DIT. Envoyer « Total : 4 500 F »
       sur une commande dont le prix dépend de ce qu'on met dedans, c'est
       annoncer au client un chiffre que la maison ne tiendra pas. */
    const fourchette = totalMax > total;
    return (
      `Bonjour Au Braisé d'Or, je voudrais commander :\n\n${lignes}\n\n` +
      `Total : ${prix(total, fourchette ? totalMax : undefined)}` +
      (fourchette
        ? `\n(le prix exact dépend de ce que je choisis dedans, merci de me le confirmer)`
        : "") +
      `\nMode : ${lieu}`
    );
  }

  return (
    <section
      ref={zone}
      id="carte"
      className="relative z-10 pb-40 pt-24 text-[color:var(--encre)]"
      style={{
        background:
          "radial-gradient(100% 46% at 50% 0%, rgba(232,118,58,.11), transparent 62%)," +
          "linear-gradient(180deg, var(--mur-2) 0%, var(--mur) 20%, var(--mur) 100%)",
      }}
    >
      <header className="mx-auto mb-10 max-w-5xl px-6 text-center">
        <p className="mb-3 text-[0.72rem] font-medium uppercase tracking-[0.32em] text-[#a8542f]">
          Notre carte
        </p>
        <h2 className="police-titre text-[clamp(2rem,5vw,3.4rem)] font-extralight leading-[1.05]">
          Le feu,{" "}
          <span className="font-extrabold italic" style={{ color: "#a8542f" }}>
            servi à table
          </span>
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-[0.92rem] leading-relaxed text-[color:var(--encre-2)]">
          {NB_PLATS} plats, faits maison. Choisissez, ajoutez, et la commande
          part sur WhatsApp déjà rédigée.
        </p>
      </header>

      {/* LA BARRE DES CATÉGORIES, collante */}
      <div className="sticky top-0 z-20 mb-12 border-y border-black/[0.07] bg-[color:var(--mur)]/85 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-6xl gap-2 overflow-x-auto px-6 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {CARTE.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => sauter(c.id)}
              aria-current={actif === c.id}
              className="shrink-0 rounded-full border px-4 py-2 text-[0.82rem] font-medium transition"
              style={
                actif === c.id
                  ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                  : { borderColor: "rgba(29,26,23,.18)", color: "#55504a" }
              }
            >
              {c.label}
              <span className="ml-1.5 opacity-55">{c.items.length}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6">
        {CARTE.map((c) => (
          <div key={c.id} className="ct-bloc mb-14" id={`cat-${c.id}`}>
            <div className="mb-5 flex flex-wrap items-baseline gap-3">
              <h3 className="police-titre text-[clamp(1.4rem,3vw,2rem)] font-extrabold">
                {c.label}
              </h3>
              <span className="rounded-full border border-black/15 px-3 py-1 text-[0.65rem] uppercase tracking-[0.2em] text-[#a8542f]">
                {c.tag}
              </span>
              {c.note && (
                <p className="w-full text-[0.82rem] leading-relaxed text-[color:var(--encre-2)]">
                  {c.note}
                </p>
              )}
            </div>

            <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-4 max-md:grid-cols-2 max-md:gap-3">
              {c.items.map((p) => (
                <article
                  key={p.n}
                  className="ct-item group cursor-pointer overflow-hidden rounded-3xl border border-white/80 bg-white/70 shadow-[0_14px_40px_rgba(0,0,0,0.06)] backdrop-blur transition hover:-translate-y-1 hover:shadow-[0_24px_56px_rgba(0,0,0,0.10)]"
                  onClick={() => setOuvert({ cat: c, plat: p })}
                >
                  <div className="relative aspect-[5/4] overflow-hidden bg-[#e7e0d8]">
                    {p.img ? (
                      <Image
                        src={p.img}
                        alt={p.n}
                        fill
                        loading="lazy"
                        sizes="(max-width: 768px) 45vw, 260px"
                        className="object-cover transition duration-700 group-hover:scale-[1.05]"
                      />
                    ) : (
                      <Ardoise nom={p.n} />
                    )}
                    {/* ⚠️ LA COULEUR DU TEXTE EST OBLIGATOIRE ICI. Sans elle la
                        pastille héritait de `--encre` (#1d1a17) et posait de
                        l'encre noire sur une pastille noire à 65 % : le prix,
                        seul chiffre que le client cherche, était invisible sur
                        les 52 cartes. Mesuré après correction, texte déclaré
                        contre fond photographié : 13,9:1 à 18:1 selon la photo
                        posée dessous. `_outils/_qc.py` le vérifie par
                        catégorie et refuse en dessous de 4,5:1. */}
                    <span className="absolute bottom-2 right-2 rounded-full bg-black/70 px-2.5 py-1 text-[0.78rem] font-semibold text-[#f6efe6] backdrop-blur">
                      {p.p === 0 ? (
                        "Prix sur demande"
                      ) : p.pMax ? (
                        prix(p.p, p.pMax)
                      ) : p.paliers ? (
                        /* Trois crans ne tiennent pas dans une pastille : on
                           annonce la portée, la fiche donne chaque prix. */
                        prix(p.paliers[0][1], p.paliers[p.paliers.length - 1][1])
                      ) : (
                        <>
                          {fmt(p.p)} F
                          {p.p2 && <small className="ml-1 opacity-90">/ {fmt(p.p2)} F</small>}
                        </>
                      )}
                    </span>
                    {p.joq && (
                      <span className="absolute left-2 top-2 rounded-full bg-[#1d1a17] px-2 py-1 text-[0.62rem] font-bold uppercase tracking-wide text-[#f6efe6]">
                        Signature
                      </span>
                    )}
                  </div>
                  <div className="p-3.5">
                    <p className="police-titre text-[0.95rem] font-bold leading-tight">
                      {p.n}
                    </p>
                    {p.d && (
                      <p className="mt-1 line-clamp-2 text-[0.78rem] leading-snug text-[color:var(--encre-2)] max-md:hidden">
                        {p.d}
                      </p>
                    )}
                    <span className="mt-3 inline-flex items-center gap-1.5 text-[0.8rem] font-semibold text-[#a8542f]">
                      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                        <path d="M12 5v14M5 12h14" />
                      </svg>
                      {p.p === 0 ? "Demander le prix" : "Ajouter"}
                    </span>
                  </div>
                </article>
              ))}
            </div>
          </div>
        ))}
      </div>

      {ouvert && (
        <Fiche
          cat={ouvert.cat}
          plat={ouvert.plat}
          onFermer={() => setOuvert(null)}
          onAjouter={ajouter}
        />
      )}

      {nb > 0 && (
        <div
          ref={barre}
          className={
            "fixed inset-x-0 bottom-0 z-40 border-t border-black/[0.08] bg-[color:var(--mur)]/95 px-4 py-3 backdrop-blur " +
            (bat ? "barre-bat" : "")
          }
        >
          {/* ⚠️ `flex-wrap` : à 390 px, trois pastilles de mode + le total +
              le bouton font 520 px de large. Sans passage à la ligne, la
              barre débordait de l'écran et le bouton sortait du cadre. */}
          <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3">
            <div className="flex gap-1.5">
              {(["place", "emporter", "livraison"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  className="rounded-full px-3 py-1.5 text-[0.72rem] font-medium transition"
                  style={
                    mode === m
                      ? { background: "#1d1a17", color: "#f6efe6" }
                      : { background: "rgba(29,26,23,.07)", color: "#55504a" }
                  }
                >
                  {m === "place" ? "Sur place" : m === "emporter" ? "À emporter" : "Livraison"}
                </button>
              ))}
            </div>
            <p className="ml-auto text-[0.85rem] text-[color:var(--encre-2)]">
              <b className="text-[color:var(--encre)]">{nb}</b> article{nb > 1 ? "s" : ""} ·{" "}
              <b className="text-[color:var(--encre)]">
                {prix(total, totalMax > total ? totalMax : undefined)}
              </b>
            </p>
            <a
              href={`https://wa.me/${WHATSAPP}?text=${encodeURIComponent(message())}`}
              target="_blank"
              rel="noreferrer"
              className="rounded-full px-5 py-2.5 text-center text-[0.85rem] font-semibold text-white transition hover:brightness-110 max-md:w-full"
              style={{ background: "#128040" }}
            >
              Envoyer la commande
            </a>
          </div>
        </div>
      )}
    </section>
  );
}

/** La fiche de commande : taille, accompagnement, quantité. */
function Fiche({
  cat,
  plat,
  onFermer,
  onAjouter,
}: {
  cat: Cat;
  plat: Plat;
  onFermer: () => void;
  onAjouter: (l: Omit<Ligne, "cle">) => void;
}) {
  /* ⚠️ UNE SEULE LISTE DE TAILLES, D'OÙ QU'ELLE VIENNE. Un plat déclare soit
     `paliers` (barème à N crans : la glace se vend à la boule, 1 000 / 1 500 /
     2 500 F), soit `p2` (deux tailles). Les deux finissent dans le même
     tableau et le reste de la fiche ne connaît plus qu'un index. Avant, la
     taille était un booléen `grand` : ajouter un troisième cran demandait de
     retoucher le prix, le libellé envoyé au panier ET le balisage, trois
     endroits où l'on peut oublier le troisième prix sans que rien ne le dise. */
  const paliers: [string, number][] = useMemo(() => {
    if (plat.paliers) return plat.paliers;
    if (!plat.p2) return [];
    const t = plat.tailles ?? ["Normal", "Grand"];
    return [
      [t[0], plat.p],
      [t[1], plat.p2],
    ];
  }, [plat]);
  const [iTaille, setITaille] = useState(0);
  const [acc, setAcc] = useState<string>("");
  const [dedans, setDedans] = useState<string[]>([]);
  const [qte, setQte] = useState(1);
  const accs = cat.acc ? ACC[cat.acc] : null;

  /* ⚠️ DEUX CAS SONT EXACTS, UN SEUL EST UNE FOURCHETTE.
     Mongazi : « quand on met tout dedans, c'est le prix le plus cher ».
     Donc rien dedans = la borne basse, tout dedans = la borne haute, et ces
     deux-là se commandent au franc près. Il n'y a plus qu'entre les deux que
     le prix reste à confirmer — et là on ne l'interpole pas, la maison n'a
     jamais donné le prix d'un ingrédient pris séparément. */
  const garn = plat.garn ?? [];
  const bas = paliers.length ? paliers[iTaille][1] : plat.p;
  const haut = plat.pMax ?? bas;
  const tousDedans = garn.length > 0 && dedans.length === garn.length;
  const rienDedans = garn.length > 0 && dedans.length === 0;
  const uMin = !plat.pMax ? bas : tousDedans ? haut : bas;
  const uMax = !plat.pMax ? bas : rienDedans ? bas : haut;

  /* ⚠️ L'ACCOMPAGNEMENT N'EST PAS FACULTATIF. « Toutes les sauces sont
     servies avec l'accompagnement de votre choix » : une commande sans
     accompagnement arrive incomplète en cuisine, et c'est le restaurant qui
     rappelle le client. */
  const manqueAcc = !!accs && !acc;
  /* ⚠️ PRIX PAS ENCORE DONNÉ PAR LA MAISON (p = 0). On ne met pas au panier
     un article dont on ignore le prix : le total mentirait, et le message
     WhatsApp partirait avec un « 0 F » que personne ne veut lire. La fiche
     pose la question à la place, ce qui est justement ce que le client
     ferait. Le jour où le prix arrive, cette branche s'éteint toute seule. */
  const surDemande = plat.p === 0;

  useEffect(() => {
    const f = (e: KeyboardEvent) => e.key === "Escape" && onFermer();
    window.addEventListener("keydown", f);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", f);
      document.body.style.overflow = "";
    };
  }, [onFermer]);

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-[#1d1a17]/55 p-4 backdrop-blur-sm"
      onClick={onFermer}
      role="dialog"
      aria-modal="true"
      aria-label={`Commander ${plat.n}`}
    >
      <div
        className="max-h-[90vh] w-full max-w-md overflow-auto rounded-3xl border border-white/90 bg-[color:var(--mur)] text-[color:var(--encre)] shadow-[0_40px_90px_rgba(0,0,0,0.22)]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative aspect-[5/3]">
          {plat.img ? (
            <Image src={plat.img} alt={plat.n} fill sizes="440px" className="object-cover" />
          ) : (
            <Ardoise nom={plat.n} grand />
          )}
          <button
            type="button"
            onClick={onFermer}
            aria-label="Fermer"
            className="absolute right-3 top-3 grid h-10 w-10 place-items-center rounded-full bg-white/85 text-[color:var(--encre)] backdrop-blur"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>

        <div className="p-5">
          <h3 className="police-titre text-[1.25rem] font-extrabold">{plat.n}</h3>
          {plat.d && <p className="mt-1 text-[0.85rem] text-[color:var(--encre-2)]">{plat.d}</p>}

          {paliers.length > 0 && (
            <div className="mt-5">
              <p className="mb-2 text-[0.75rem] uppercase tracking-widest text-[#a8542f]">Taille</p>
              {/* ⚠️ `flex-wrap` : à trois crans sur un écran de 360 px, trois
                  boutons sur une ligne coupaient « 2 boules » en deux. */}
              <div className="flex flex-wrap gap-2">
                {paliers.map(([libelle, valeur], k) => (
                  <button
                    key={libelle}
                    type="button"
                    onClick={() => setITaille(k)}
                    className="min-w-[8.5rem] flex-1 rounded-2xl border px-3 py-2.5 text-[0.85rem] font-medium transition"
                    style={
                      iTaille === k
                        ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                        : { borderColor: "rgba(29,26,23,.18)" }
                    }
                  >
                    {libelle} · {fmt(valeur)} F
                  </button>
                ))}
              </div>
            </div>
          )}

          {plat.garn && plat.garn.length > 0 && (
            <div className="mt-5">
              <p className="mb-1 text-[0.75rem] uppercase tracking-widest text-[#a8542f]">
                Ce que vous voulez dedans
              </p>
              {/* ⚠️ ON N'ANNONCE PAS UN PRIX PAR INGRÉDIENT. La maison n'a
                  donné qu'une fourchette : « le prix varie en fonction des
                  éléments entre parenthèses ». Mettre un chiffre en face de
                  chaque case serait l'inventer. On liste, on transmet, la
                  maison confirme. */}
              <p className="mb-2 text-[0.78rem] leading-snug text-[color:var(--encre-2)]">
                {"Sans rien ajouter, c'est "}<b>{fmt(plat.p)} F</b>
                {". Avec tout, c'est "}<b>{fmt(plat.pMax ?? plat.p)} F</b>{"."}
                {dedans.length > 0 && !tousDedans && (
                  <> Entre les deux, la maison vous confirme le prix.</>
                )}
              </p>
              <div className="flex flex-wrap gap-2">
                {plat.garn.map((g) => (
                  <button
                    key={g}
                    type="button"
                    onClick={() =>
                      setDedans((d) =>
                        d.includes(g) ? d.filter((x) => x !== g) : [...d, g]
                      )
                    }
                    aria-pressed={dedans.includes(g)}
                    className="rounded-full border px-3 py-1.5 text-[0.8rem] transition"
                    style={
                      dedans.includes(g)
                        ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                        : { borderColor: "rgba(29,26,23,.18)" }
                    }
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>
          )}

          {accs && (
            <div className="mt-5">
              <p className="mb-2 text-[0.75rem] uppercase tracking-widest text-[#a8542f]">
                Accompagnement <span className="normal-case tracking-normal opacity-70">· à choisir</span>
              </p>
              <div className="flex flex-wrap gap-2">
                {accs.map((a) => (
                  <button
                    key={a}
                    type="button"
                    onClick={() => setAcc(acc === a ? "" : a)}
                    className="rounded-full border px-3 py-1.5 text-[0.8rem] transition"
                    style={
                      acc === a
                        ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                        : { borderColor: "rgba(29,26,23,.18)" }
                    }
                  >
                    {a}
                  </button>
                ))}
              </div>
            </div>
          )}

          {surDemande ? (
            <a
              href={`https://wa.me/${WHATSAPP}?text=${encodeURIComponent(
                `Bonjour Au Braisé d'Or, quel est le prix de : ${plat.n} ?`
              )}`}
              target="_blank"
              rel="noreferrer"
              className="mt-6 flex w-full items-center justify-center gap-2 rounded-full px-4 py-3 text-[0.9rem] font-bold text-white transition hover:brightness-110"
              style={{ background: "#128040" }}
            >
              Demander le prix sur WhatsApp
            </a>
          ) : (
          <div className="mt-6 flex items-center gap-4">
            <div className="flex items-center gap-3 rounded-full border border-black/15 px-2 py-1.5">
              <button type="button" aria-label="Moins" onClick={() => setQte((q) => Math.max(1, q - 1))} className="grid h-8 w-8 place-items-center text-lg">
                −
              </button>
              <span className="w-6 text-center font-semibold">{qte}</span>
              <button type="button" aria-label="Plus" onClick={() => setQte((q) => q + 1)} className="grid h-8 w-8 place-items-center text-lg">
                +
              </button>
            </div>
            <button
              type="button"
              onClick={() =>
                onAjouter({
                  nom: plat.n,
                  taille: paliers.length ? paliers[iTaille][0] : undefined,
                  acc: acc || undefined,
                  dedans: dedans.length ? dedans : undefined,
                  unite: uMin,
                  uniteMax: uMax > uMin ? uMax : undefined,
                  qte,
                })
              }
              disabled={manqueAcc}
              className="flex-1 rounded-full px-4 py-3 text-[0.9rem] font-bold text-[#f6efe6] transition hover:brightness-125 disabled:cursor-not-allowed disabled:opacity-45"
              style={{ background: "#1d1a17" }}
            >
              {manqueAcc
                ? "Choisissez un accompagnement"
                : `Ajouter · ${prix(uMin * qte, uMax > uMin ? uMax * qte : undefined)}`}
            </button>
          </div>
          )}
        </div>
      </div>
    </div>
  );
}
