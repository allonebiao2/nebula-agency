// Démarrage du cabinet privé (harmonisation-faciale.html).
// Le premier écran est la porte, en HTML : rien de lourd. three.js ne se charge qu'au premier geste,
// ou quand le navigateur est libre après le chargement. La fiche (zone, tarif, consultation) est tenue ici.
import { installerSon, bruit } from "./son.js";

const racine = document.getElementById("cabinet");
const H = window.LC_HARMO;
if (racine && H) {
  installerSon({ bouton: racine.querySelector(".s3d-son") });
  const porte = racine.querySelector(".s3d-porte");
  let ouverte = false, moteurP = null;
  const lien = {};

  const ouvrir = () => {
    if (ouverte) return;
    ouverte = true;
    porte.classList.add("ouverte");
    porte.setAttribute("aria-hidden", "true");
    bruit.porte();
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

  // ---------- la fiche : la zone choisie, son tarif, la consultation ----------
  function majFiche(ti, zi) {
    const t = H.donnees[ti], z = t.zones[zi];
    H.choix = { t: ti, z: zi };
    const fiche = racine.querySelector(`.hz-fiche[data-t="${ti}"]`);
    if (fiche) {
      fiche.querySelector(".hz-zone-nom").textContent = z.nom;
      fiche.querySelector(".hz-zone-detail").textContent = z.detail || "";
      fiche.querySelector(".hz-prix").textContent = H.prix(z);
      const fo = fiche.querySelector(".hz-forfait");
      if (fo) fo.textContent = H.forfait ? H.forfait(z) : "";
      fiche.querySelectorAll(".hz-zones button").forEach((b) => b.setAttribute("aria-selected", +b.dataset.z === zi ? "true" : "false"));
      const c = fiche.querySelector("[data-consult]");
      c.dataset.t = ti; c.dataset.z = zi;
    }
    racine.querySelectorAll(".s3d-pt").forEach((p) => p.classList.toggle("choisi", p.dataset.id === `${ti}-${zi}`));
    const recap = racine.querySelector(".hz-recap");
    if (recap) recap.textContent = `Votre choix : ${t.nom} · ${z.nom}, ${H.prix(z)}${z.forfait && H.forfait ? " (ou " + H.forfait(z) + ")" : ""}. Nous vous répondons sur WhatsApp pour fixer le rendez-vous.`;
  }

  racine.addEventListener("click", (e) => {
    const zb = e.target.closest(".hz-zones button");
    if (zb && lien.choisir) { lien.choisir(+zb.dataset.t, +zb.dataset.z); return; }
    const sv = e.target.closest("[data-suivante]");
    if (sv && lien.choisir) {
      const ti = +sv.dataset.suivante, n = H.donnees[ti].zones.length;
      const zi = H.choix && H.choix.t === ti ? (H.choix.z + 1) % n : 1 % n;
      lien.choisir(ti, zi);
      return;
    }
    const al = e.target.closest("[data-aller]");
    if (al && lien.moteur) { lien.moteur.aller(+al.dataset.aller); bruit.laiton(); }
  });

  async function charger() {
    const [{ lancer }, { cabinet }] = await Promise.all([import("./moteur.js"), import("./monde-harmonisation.js")]);
    const monde = cabinet({
      donnees: H.donnees, prix: H.prix, forfait: H.forfait, lien,
      quand: {
        choix: majFiche,
        son: () => bruit.or(),
        consulter: () => { bruit.laiton(); H.ouvrir(); },
        porteOuverte: () => ouverte,
      },
    });
    const m = await lancer({ racine, monde });
    if (!m) return;
    lien.moteur = m;
    racine.s3d = lien;
    racine.classList.add("hz-pret");
  }
}
