// LA BOUTIQUE · INA Luxury, une galerie de vitrines, noir et or (les couleurs de la page).
// On avance dans une galerie (le tunnel d'arches d'or) ; à chaque famille, une vitrine où les VRAIES photos des
// produits tournent en carrousel (les meilleures ventes d'abord). Toucher un produit l'ouvre dans le catalogue de la
// page (select), le comptoir du fond mène au panier et à la consultation. Tout est LU dans PRODUCTS, IMG, FAMILIES.
import { THREE } from "./moteur.js";
import { marbre, plaque, degrade, poussiere, ambiance, boiteArrondie } from "./matieres.js";

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fcfa = (n) => (n || 0).toLocaleString("fr-FR").replace(/ | /g, " ") + " F";
const PAS = 5.2;                 // l'écart entre deux vitrines, le long de la galerie
const ZV = (k) => -3.5 - k * PAS;
const XV = (k) => (k % 2 ? 2.55 : -2.55);
const PAR_VITRINE = 12;

export function boutique({ ina, lien, quand }) {
  return async ({ scene, renderer, camera, mobile, calme, outils }) => {
    const { anis, charger } = outils;
    const familles = ina.familles.filter((f) => ina.produits.some((p) => p.f === f.key));
    const nF = familles.length, Zfin = ZV(nF) - 1.2;
    scene.background = new THREE.Color(0x0a0907);
    scene.fog = new THREE.Fog(0x0a0907, 9, 30);
    scene.environment = ambiance(renderer, { mur: 0x2a2116, chaud: 0xffdcaa, lumieres: [[0, 9, 0, 10, 0.4, 10, 2.4], [-9, 4, 0, 0.4, 5, 8, 1.2], [9, 4, 0, 0.4, 5, 8, 1.2]] });
    renderer.toneMappingExposure = 1.05;

    const mSol = new THREE.MeshStandardMaterial({ map: marbre(anis, { rep: 3 }), roughness: 0.18, metalness: 0.15, envMapIntensity: 0.8 });
    const mLaque = new THREE.MeshStandardMaterial({ color: 0x15120d, roughness: 0.35, metalness: 0.25 });
    const mOr = new THREE.MeshStandardMaterial({ color: 0xc9a24e, metalness: 1, roughness: 0.28, envMapIntensity: 1.3 });
    const mOrLum = new THREE.MeshStandardMaterial({ color: 0xe2c47a, emissive: 0xb08a34, emissiveIntensity: 0.65, metalness: 0.9, roughness: 0.3 });

    const L = -Zfin + 8;
    const sol = new THREE.Mesh(new THREE.PlaneGeometry(9, L), mSol);
    sol.rotation.x = -Math.PI / 2; sol.position.set(0, 0, 4 - L / 2); sol.receiveShadow = true; scene.add(sol);
    for (const x of [-4, 4]) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(L, 4.4), mLaque);
      m.position.set(x, 2.2, 4 - L / 2); m.rotation.y = x < 0 ? Math.PI / 2 : -Math.PI / 2; scene.add(m);
    }
    const plaf = new THREE.Mesh(new THREE.PlaneGeometry(9, L), mLaque);
    plaf.rotation.x = Math.PI / 2; plaf.position.set(0, 4.4, 4 - L / 2); scene.add(plaf);
    const fond = new THREE.Mesh(new THREE.PlaneGeometry(9, 4.4), mLaque);
    fond.position.set(0, 2.2, Zfin - 3); scene.add(fond);

    // le tunnel : une arche d'or tous les 2,6 m, qui file vers le fond
    const nA = Math.ceil(L / 2.6);
    const arche = new THREE.TorusGeometry(3.6, 0.03, 10, 96, Math.PI);
    const arches = new THREE.InstancedMesh(arche, mOrLum, nA);
    const mm = new THREE.Matrix4();
    for (let i = 0; i < nA; i++) { mm.makeTranslation(0, 0.8, 3 - i * 2.6); arches.setMatrixAt(i, mm); }
    scene.add(arches);
    // un filet d'or au sol, au milieu (le chemin)
    const chemin = new THREE.Mesh(new THREE.PlaneGeometry(0.04, L), new THREE.MeshBasicMaterial({ color: 0xc9a84c, transparent: true, opacity: 0.55 }));
    chemin.rotation.x = -Math.PI / 2; chemin.position.set(0, 0.003, 4 - L / 2); scene.add(chemin);

    scene.add(new THREE.AmbientLight(0x3b3022, 0.6));
    scene.add(new THREE.HemisphereLight(0x6a5638, 0x0a0806, 0.4));
    // un seul projecteur, qui suit la vitrine regardée (une lumière de plus par vitrine coûterait trop au téléphone)
    const spot = new THREE.SpotLight(0xffe4b8, 90, 12, 0.55, 0.7, 1.5);
    spot.castShadow = !mobile; spot.shadow.mapSize.set(1024, 1024); spot.shadow.bias = -0.0004;
    scene.add(spot, spot.target);

    // ---------- les vitrines ----------
    const vitrines = [];
    const cliquables = [];
    familles.forEach((f, k) => {
      const x = XV(k), z = ZV(k), cote = Math.sign(x);
      const g = new THREE.Group();
      g.position.set(x, 0, z);
      g.rotation.y = cote < 0 ? Math.PI / 2 : -Math.PI / 2;      // la vitrine regarde le milieu de la galerie
      // la niche rétroéclairée
      const niche = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 2.9), new THREE.MeshBasicMaterial({ toneMapped: false,
        map: degrade(anis, [[0, "rgba(255,226,170,.55)"], [0.55, "rgba(120,86,34,.35)"], [1, "rgba(20,16,10,1)"]], { w: 128, h: 128, radial: true }) }));
      niche.position.set(0, 1.75, -1.4); g.add(niche);
      const cadre = new THREE.Mesh(new THREE.TorusGeometry(1.35, 0.045, 12, 96, Math.PI), mOr);
      cadre.position.set(0, 2.0, -1.3); g.add(cadre);
      for (const dx of [-1.35, 1.35]) { const c = new THREE.Mesh(new THREE.BoxGeometry(0.09, 2.0, 0.09), mOr); c.position.set(dx, 1.0, -1.3); g.add(c); }
      // le socle du carrousel
      const socle = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.12, 0.36, 64), new THREE.MeshStandardMaterial({ map: marbre(anis, { rep: 1, base: "#1d1812" }), roughness: 0.25, metalness: 0.1 }));
      socle.position.set(0, 0.18, -0.4); socle.receiveShadow = true; socle.castShadow = true; g.add(socle);
      const bague = new THREE.Mesh(new THREE.TorusGeometry(1.06, 0.018, 10, 96), mOr); bague.rotation.x = Math.PI / 2; bague.position.set(0, 0.36, -0.4); g.add(bague);
      // le nom de la famille, gravé en or
      const nom = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 0.36), new THREE.MeshBasicMaterial({ transparent: true, toneMapped: false,
        map: plaque(anis, { w: 1024, h: 168, fond: null, lignes: [{ t: f.label.toUpperCase(), font: "500 86px 'Cormorant Garamond', Georgia, serif", couleur: "#e2c47a", y: 0.56, espace: "12px" }] }) }));
      nom.position.set(0, 3.62, -1.3); g.add(nom);
      // le carrousel (rempli quand on approche)
      const ronde = new THREE.Group(); ronde.position.set(0, 0.36, -0.4); g.add(ronde);
      scene.add(g);
      const prods = ina.produits.filter((p) => p.f === f.key && ina.img[p.n]);
      const tri = [...prods.filter((p) => p.best), ...prods.filter((p) => p.isnew && !p.best), ...prods.filter((p) => !p.best && !p.isnew)].slice(0, PAR_VITRINE);
      vitrines.push({ f, g, ronde, x, z, cote, prods: tri, total: ina.produits.filter((p) => p.f === f.key).length, charge: false });
    });

    async function remplir(v, k) {
      if (v.charge) return;
      v.charge = true;
      const n = v.prods.length, rayon = n > 8 ? 1.12 : 0.92;
      await Promise.all(v.prods.map(async (p, j) => {
        // détouré (cliente, 26/11 : « les mettre en fond noir ») : le produit seul, debout sur le socle ;
        // sinon la photo dans son cadre d'or
        const libre = !!(ina.detoures && ina.detoures[p.n]);
        const t = await charger(libre ? ina.detoures[p.n] : ina.img[p.n]);
        if (!t) return;
        const a = t.image.width / t.image.height, h = libre ? 0.9 : 0.82, w = Math.min(libre ? 0.62 : 0.66, h * a), h2 = libre ? w / a : h;
        const carte = new THREE.Group();
        if (!libre) {
          const fondB = new THREE.Mesh(new THREE.PlaneGeometry(w + 0.04, h + 0.04), mOr);
          fondB.position.z = -0.004;
          carte.add(fondB);
        }
        const photo = new THREE.Mesh(new THREE.PlaneGeometry(w, h2), new THREE.MeshBasicMaterial({ map: t, toneMapped: false, transparent: libre, alphaTest: libre ? 0.04 : 0 }));
        carte.add(photo);
        const ang = (j / n) * Math.PI * 2;
        carte.position.set(Math.sin(ang) * rayon, libre ? h2 / 2 + 0.01 : 0.42 + h / 2, Math.cos(ang) * rayon);
        carte.rotation.y = ang;
        carte.userData.act = () => quand.produit(p);
        carte.userData.k = k + 1;
        carte.userData.p = p;
        v.ronde.add(carte);
        cliquables.push(carte);
      }));
      lien.moteur && lien.moteur.rafraichir();
    }

    // ---------- le comptoir du fond ----------
    const comptoir = new THREE.Mesh(boiteArrondie(3.2, 1.0, 0.8, 0.08), mLaque);
    comptoir.position.set(0, 0.5, Zfin - 1.6); comptoir.castShadow = true; scene.add(comptoir);
    const liseré = new THREE.Mesh(new THREE.BoxGeometry(3.22, 0.025, 0.82), mOrLum); liseré.position.set(0, 1.0, Zfin - 1.6); scene.add(liseré);
    const enseigne = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 0.9), new THREE.MeshBasicMaterial({ transparent: true, toneMapped: false,
      map: plaque(anis, { w: 1400, h: 370, fond: null, lignes: [
        { t: "INA LUXURY", font: "500 150px 'Cormorant Garamond', Georgia, serif", couleur: "#e2c47a", y: 0.42, espace: "22px" },
        { t: "L'ART DU SOIN, SUBLIMÉ", font: "500 46px 'DM Mono', monospace", couleur: "#d3c7b1", y: 0.82, espace: "10px" }] }) }));
    enseigne.position.set(0, 2.55, Zfin - 2.9); scene.add(enseigne);
    enseigne.userData.act = () => quand.catalogue(); comptoir.userData.act = () => quand.panier();
    cliquables.push(enseigne, comptoir);

    const pous = poussiere(anis, { n: mobile ? 70 : 160, boite: [7, 3.6, -Zfin + 6], centre: [0, 2, Zfin / 2], couleur: "236,205,140", taille: 0.04, opacite: 0.55 });
    if (!calme) scene.add(pous);

    // ---------- les stations ----------
    const nTotal = ina.produits.length;
    const etiq = (n, t) => `<div class="s3d-etiq"><b>${String(n).padStart(2, "0")}</b> ${t}</div>`;
    const stations = [{
      id: "entree", nom: "Entrée", cote: "a-gauche",
      cam: { p: [0, 1.75, 6.2], c: [0, 1.55, -20] }, camM: { p: [0, 1.7, 7], c: [0, 1.1, -20] },
      calque: `<div class="s3d-panneau">${etiq(0, "La boutique")}<h2>INA Luxury</h2>
        <p>L'art du soin, sublimé. ${nTotal} produits en ${nF} vitrines : avancez, touchez un produit pour l'ouvrir.</p>
        <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-aller="1">Entrer dans la boutique</button>
        <button type="button" class="s3d-btn" data-catalogue>Menu</button></div></div>`,
    }];
    vitrines.forEach((v, k) => {
      const prixMin = Math.min(...ina.produits.filter((p) => p.f === v.f.key && p.p).map((p) => p.p));
      const sous = (ina.sous[v.f.key] || []).filter((s) => ina.produits.some((p) => p.f === v.f.key && p.s === s.key));
      // le centre du carrousel (la vitrine est creusée de 0,4 m dans le mur) ; la caméra se tient en face, un peu vers
      // l'entrée, et vise 1 m à côté : la vitrine se pose du côté opposé à la fiche (calcul fait pour les deux murs)
      const cx = v.x + v.cote * 0.4;
      stations.push({
        id: v.f.key, nom: v.f.label, cote: v.cote < 0 ? "a-droite" : "a-gauche",
        cam: { p: [cx - v.cote * 3.15, 1.6, v.z + 1.45], c: [cx, 1.2, v.z - 0.95] },
        camM: { p: [cx - v.cote * 4.3, 1.6, v.z + 0.9], c: [cx, -0.2, v.z] },
        calque: `<div class="s3d-panneau">${etiq(k + 1, "Vitrine")}<h3>${esc(v.f.label)}</h3><p>${esc(v.f.desc || "")}</p>
          <div class="s3d-prix"><span>Produits<b>${v.total}</b></span>${isFinite(prixMin) ? `<span>À partir de<b>${fcfa(prixMin)}</b></span>` : ""}</div>
          ${sous.length ? `<div class="hz-zones">${sous.map((s) => `<button type="button" data-famille="${esc(v.f.key)}" data-sous="${esc(s.key)}">${esc(s.label)}</button>`).join("")}</div>` : ""}
          <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-famille="${esc(v.f.key)}">Voir les ${v.total} produits</button></div></div>`,
      });
    });
    stations.push({
      id: "comptoir", nom: "Le comptoir", cote: "a-gauche",
      cam: { p: [0.4, 1.9, Zfin + 3.4], c: [0.4, 1.4, Zfin - 2.6] }, camM: { p: [0, 2.0, Zfin + 4.4], c: [0, 0.9, Zfin - 2.6] },
      calque: `<div class="s3d-panneau">${etiq(nF + 1, "Le comptoir")}<h3>Votre sélection, votre routine.</h3>
        <p>Votre panier part sur WhatsApp. Vous hésitez ? Mme Sabrina vous oriente vers la routine qui convient à votre peau.</p>
        <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-panier>Mon panier</button>
        <button type="button" class="s3d-btn" data-consultation>Faire ma consultation</button>
        <button type="button" class="s3d-btn" data-catalogue>Menu</button></div></div>`,
    });

    let qualiteBasse = false, kActif = 0, survole = null;
    const ou = new THREE.Vector3();
    const visee = new THREE.Vector3();
    return {
      stations, cliquables,
      surStation(k) {
        kActif = k;
        // on remplit la vitrine regardée et ses voisines, jamais les 6 d'un coup (la 3G de Cotonou)
        for (const j of [k - 1, k, k + 1]) if (vitrines[j - 1]) remplir(vitrines[j - 1], j - 1);
        const v = vitrines[k - 1];
        if (v) { const cx = v.x + v.cote * 0.4; spot.position.set(cx * 0.3, 4.1, v.z + 1.4); visee.set(cx, 1.0, v.z); }
        else { spot.position.set(0, 4.1, Zfin + 1); visee.set(0, 0.8, Zfin - 1.6); }
        spot.target.position.copy(visee);
        lien.moteur && lien.moteur.rafraichir();
      },
      survol(o) {
        if (survole && survole !== o) survole.scale.setScalar(1);
        survole = o && o.userData.p ? o : null;
        if (survole) survole.scale.setScalar(1.08);
        lien.moteur && lien.moteur.rafraichir();
      },
      qualite(q) {
        if (q !== "basse") return;
        qualiteBasse = true;
        spot.castShadow = false;
        scene.remove(pous);
      },
      anime(t, dt, etat) {
        const v = vitrines[kActif - 1];
        if (!v || !v.charge) return false;
        // chaque produit regarde le visiteur : une découpe plate ne se montre jamais par la tranche
        const cp = etat.camera.position;
        v.ronde.children.forEach((c) => { c.getWorldPosition(ou); c.lookAt(cp.x, ou.y, cp.z); });
        if (calme) return false;
        // le carrousel regardé tourne doucement
        v.ronde.rotation.y += dt * 0.22;
        if (!qualiteBasse) pous.userData.animer(dt);
        return true;
      },
    };
  };
}
