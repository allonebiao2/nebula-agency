// Démarrage de la visite de la clinique (luxury-skin-clinic.html).
// La porte est en HTML (premier écran léger) ; three.js ne se charge qu'au premier geste ou quand le navigateur est
// libre. Les actions de la scène appellent les moteurs DÉJÀ dans la page : startBooking (avec son « J'ai lu et
// compris »), les cartes de soins de #soins, la réservation #rdv-booking. Rien n'est dupliqué.
import { installerSon, bruit, mouvement } from "./son.js";

const racine = document.getElementById("visite");
const C = window.LC_CLINIC;
if (racine && C) {
  installerSon({ bouton: racine.querySelector(".s3d-son") });
  // le toucher, dans la scène : une goutte d'eau (26/11)
  racine.querySelector(".s3d-scene").addEventListener("pointerdown", () => bruit.goutte(), { passive: true });
  const porte = racine.querySelector(".s3d-porte");
  const lien = {};
  let ouverte = false, moteurP = null;

  const ouvrir = () => {
    if (ouverte) return;
    ouverte = true;
    porte.classList.add("ouverte");
    porte.setAttribute("aria-hidden", "true");
    bruit.porte();
    setTimeout(() => bruit.carillon(), 900);
    demarrer();
  };
  porte.addEventListener("click", ouvrir);
  porte.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); ouvrir(); } });
  addEventListener("scroll", () => { if (scrollY > 8) ouvrir(); }, { passive: true });
  addEventListener("wheel", ouvrir, { passive: true, once: true });
  addEventListener("touchmove", ouvrir, { passive: true, once: true });

  function demarrer() {
    if (!moteurP) moteurP = charger().catch((e) => { console.warn("[salon3d]", e); racine.classList.add("s3d-sans"); });
    return moteurP;
  }
  const libre = window.requestIdleCallback || ((f) => setTimeout(f, 900));
  if (document.readyState === "complete") libre(demarrer);
  else addEventListener("load", () => libre(demarrer), { once: true });

  // voir un soin : sa carte dans #soins, mise en lumière un instant
  function voir(i) {
    bruit.laiton();
    const b = document.querySelector(`#svcSections [data-book="${i}"]`);
    const carte = b && (b.closest(".svc") || b.parentElement);
    if (!carte) { document.getElementById("soins")?.scrollIntoView({ behavior: "smooth" }); return; }
    carte.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
    carte.style.transition = "box-shadow .4s ease";
    carte.style.boxShadow = "0 0 0 3px #c9a84c";
    setTimeout(() => { carte.style.boxShadow = ""; }, 2200);
  }
  const reserver = (i) => { bruit.laiton(); C.book(i); };
  const creneau = () => { bruit.page(); document.getElementById("rdv-booking")?.scrollIntoView({ behavior: "smooth" }); };

  racine.addEventListener("click", (e) => {
    const t = e.target;
    const r = t.closest("[data-reserver]"); if (r) { reserver(+r.dataset.reserver); return; }
    const v = t.closest("[data-voir]"); if (v) { voir(+v.dataset.voir); return; }
    if (t.closest("[data-rdv]")) { creneau(); return; }
    const al = t.closest("[data-aller]"); if (al && lien.moteur) { bruit.laiton(); lien.moteur.aller(+al.dataset.aller); return; }
    const ai = t.closest("[data-aller-id]"); if (ai && lien.moteur && lien.ST) { bruit.laiton(); lien.moteur.aller(lien.ST[ai.dataset.allerId]); }
  });

  async function charger() {
    const [{ lancer }, { clinique }] = await Promise.all([import("./moteur.js"), import("./monde-clinique.js")]);
    const monde = clinique({
      services: C.services, art: C.art || {}, artFamille: C.artFamille || {}, lien,
      quand: {
        voir, reserver: creneau,
        ina: (p) => { bruit.laiton(); location.href = "ina-luxury.html?q=" + encodeURIComponent(p.n); },
        harmonisation: () => { bruit.or(); location.href = "harmonisation-faciale.html"; },
        son: (nom) => bruit[nom] && bruit[nom](),
      },
    });
    const m = await lancer({ racine, monde, surStation: (k) => { if (k > 0) bruit.bol(); }, surMouvement: mouvement, surSurvol: () => bruit.tinte() });
    if (!m) return;
    lien.moteur = m;
    racine.s3d = lien;
  }
}
