// Démarrage de la boutique INA Luxury en 3D (ina-luxury.html).
// INA a déjà son écran d'accueil : pas de porte ici. three.js se charge au premier geste ou quand le navigateur est
// libre. Les actions de la scène appellent le catalogue de la page (select, panier, consultation) : rien n'est refait.
import { installerSon, bruit, mouvement } from "./son.js";

const racine = document.getElementById("boutique");
const I = window.LC_INA;
if (racine && I) {
  installerSon({ bouton: racine.querySelector(".s3d-son") });
  // le toucher, dans la scène : une goutte d'eau (26/11)
  racine.querySelector(".s3d-scene").addEventListener("pointerdown", () => bruit.goutte(), { passive: true });
  const lien = {};
  let moteurP = null;
  const calme = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function demarrer() {
    if (!moteurP) moteurP = charger().catch((e) => { console.warn("[salon3d]", e); racine.classList.add("s3d-sans"); });
    return moteurP;
  }
  const libre = window.requestIdleCallback || ((f) => setTimeout(f, 900));
  if (document.readyState === "complete") libre(demarrer);
  else addEventListener("load", () => libre(demarrer), { once: true });
  ["pointerdown", "wheel", "touchstart", "keydown"].forEach((t) => addEventListener(t, demarrer, { passive: true, once: true }));

  // ouvrir un produit : sa famille dans le catalogue, puis sa carte mise en lumière
  function produit(p) {
    bruit.laiton();
    I.ouvrir(p.f, p.s);
    setTimeout(() => {
      const carte = [...document.querySelectorAll(".card")].find((c) => {
        const h = c.querySelector("h3");
        return h && h.textContent.trim() === p.n && c.offsetParent;
      });
      if (!carte) return;
      carte.scrollIntoView({ behavior: calme ? "auto" : "smooth", block: "center" });
      carte.style.transition = "box-shadow .4s ease";
      carte.style.boxShadow = "0 0 0 3px #c9a84c";
      setTimeout(() => { carte.style.boxShadow = ""; }, 2400);
    }, 120);
  }
  // « Menu » ouvre le menu commun (menu.js) ; sans lui, on descend au catalogue de la page
  const catalogue = () => { bruit.laiton(); if (window.LCMenu) window.LCMenu.ouvrir(); else document.querySelector(".layout")?.scrollIntoView({ behavior: calme ? "auto" : "smooth" }); };
  const panier = () => { bruit.laiton(); document.getElementById("cartBtn")?.click(); };
  const consultation = () => { bruit.laiton(); document.getElementById("consultBtn")?.click(); };

  racine.addEventListener("click", (e) => {
    const t = e.target;
    const f = t.closest("[data-famille]"); if (f) { bruit.laiton(); I.ouvrir(f.dataset.famille, f.dataset.sous || null); return; }
    if (t.closest("[data-catalogue]")) { catalogue(); return; }
    if (t.closest("[data-panier]")) { panier(); return; }
    if (t.closest("[data-consultation]")) { consultation(); return; }
    const al = t.closest("[data-aller]"); if (al && lien.moteur) { bruit.laiton(); lien.moteur.aller(+al.dataset.aller); }
  });

  async function charger() {
    const [{ lancer }, { boutique }, detoures] = await Promise.all([import("./moteur.js"), import("./monde-ina.js"),
      fetch("assets/images/ina-luxury/_detoures/detoures.json").then((r) => (r.ok ? r.json() : {})).catch(() => ({}))]);
    const monde = boutique({
      ina: { produits: I.produits, img: I.img, familles: I.familles, sous: I.sous, detoures }, lien,
      quand: { produit, catalogue, panier },
    });
    const m = await lancer({ racine, monde, surStation: (k) => { if (k > 0) bruit.bol(); }, surMouvement: mouvement, surSurvol: () => bruit.tinte() });
    if (!m) return;
    lien.moteur = m;
    racine.s3d = lien;
  }
}
