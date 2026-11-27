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
    const mSocle = new THREE.MeshStandardMaterial({ map: marbre(anis, { rep: 1, base: "#1d1812" }), roughness: 0.25, metalness: 0.1 });
    // l'ombre de contact d'un produit : sans elle, une découpe posée sur le marbre flotte
    const mOmbre = new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, toneMapped: false,
      map: degrade(anis, [[0, "rgba(0,0,0,.62)"], [0.55, "rgba(0,0,0,.22)"], [1, "rgba(0,0,0,0)"]], { w: 64, h: 64, radial: true }) });
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
      const socle = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.12, 0.36, 64), mSocle);
      socle.position.set(0, 0.18, -0.4); socle.receiveShadow = true; socle.castShadow = true; g.add(socle);
      const bague = new THREE.Mesh(new THREE.TorusGeometry(1.06, 0.018, 10, 96), mOr); bague.rotation.x = Math.PI / 2; bague.position.set(0, 0.36, -0.4); g.add(bague);
      // le second gradin (26/11) : une marche de marbre filetée d'or, à l'arrière du socle, pour les grands flacons
      const marche = new THREE.Mesh(boiteArrondie(1.72, 0.26, 0.46, 0.03), mSocle);
      marche.position.set(0, 0.36 + 0.13, -0.86); marche.castShadow = true; marche.receiveShadow = true; g.add(marche);
      const filet = new THREE.Mesh(new THREE.BoxGeometry(1.72, 0.012, 0.012), mOr); filet.position.set(0, 0.62, -0.63); g.add(filet);
      // le nom de la famille, gravé en or
      const nom = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 0.36), new THREE.MeshBasicMaterial({ transparent: true, toneMapped: false,
        map: plaque(anis, { w: 1024, h: 168, fond: null, lignes: [{ t: f.label.toUpperCase(), font: "500 86px 'Cormorant Garamond', Georgia, serif", couleur: "#e2c47a", y: 0.56, espace: "12px" }] }) }));
      nom.position.set(0, 3.62, -1.3); g.add(nom);
      // le carrousel (rempli quand on approche)
      const ronde = new THREE.Group(); ronde.position.set(0, 0.36, -0.4); g.add(ronde);
      scene.add(g);
      // seuls les produits DÉTOURÉS montent sur l'étalage : une photo sur fond blanc y faisait un carré blanc (26/11) ;
      // les autres restent au catalogue, en dessous
      const avecDetour = ina.detoures && Object.keys(ina.detoures).length;
      const prods = ina.produits.filter((p) => p.f === f.key && (avecDetour ? ina.detoures[p.n] : ina.img[p.n]));
      const tri = [...prods.filter((p) => p.best), ...prods.filter((p) => p.isnew && !p.best), ...prods.filter((p) => !p.best && !p.isnew)].slice(0, PAR_VITRINE);
      vitrines.push({ f, g, ronde, x, z, cote, prods: tri, total: ina.produits.filter((p) => p.f === f.key).length, charge: false });
    });

    // LA HAUTEUR D'UN PRODUIT selon ce qu'il est (26/11 : tout faisait 90 cm, un baume à lèvres aussi grand qu'un
    // flacon) : les pots et les boîtes, larges, sont bas ; les sérums moyens ; les flacons et les gels hauts
    const hauteur = (p, a) => {
      const n = (p.n + " " + (p.s || "")).toLowerCase();
      if (/baume|lip|gloss|jelly|lèvre/.test(n) && a < 0.75) return 0.36;
      if (a >= 0.9) return /kit|coffret|boite|boîte/.test(n) ? 0.34 : 0.3;
      if (/s[ée]rum|huile|drop|goutte/.test(n)) return 0.5;
      return 0.6;
    };
    // LE VOLUME (27/11, Mongazi : « plus de profondeur au niveau des produits, avec du volume ») : une photo plate
    // tournée vers le visiteur restait une découpe. Un flacon, un tube, un pot sont des CYLINDRES : la photo s'enroule
    // sur un vrai cylindre, et son placement (u = ½ + ½ sin θ) reproduit EXACTEMENT la photo vue de face ; une lumière
    // venue du haut à gauche est posée dans les couleurs des sommets (rien à recompiler, aucune lampe de plus) : les
    // bords tournent à l'ombre, un reflet vertical passe comme sur du verre. Un savon, un coffret (des boîtes, déjà
    // photographiés de trois quarts) gardent leur photo, posée sur une plaque d'épaisseur.
    function volume(it, w, h) {
      // les « Beauty Bar » et le Lip Kit (le Savon Noir Papaya est un POT : un cylindre)
      const boite = /(bar|kit)/i.test(it.p.n);
      if (boite) {
        const g = new THREE.Group();
        const face = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: it.t, color: 0xeee5d6,
          toneMapped: false, transparent: true, alphaTest: 0.04 }));
        const plaque = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: it.t, color: 0x2a2219,
          toneMapped: false, transparent: true, alphaTest: 0.3 }));
        plaque.position.set(w * 0.035, -h * 0.012, -Math.min(0.05, w * 0.14));
        g.add(plaque, face);
        return g;
      }
      const seg = 40, r = w / 2;
      // la DEMI-face avant seulement (θ de -90° à +90°) : un dos qui reprenait la découpe faisait, vu de biais, un goulot en
      // double à côté du vrai (le dos d'un flacon n'est jamais visible derrière lui-même)
      const geo = new THREE.CylinderGeometry(r, r, h, seg, 1, true, -Math.PI / 2, Math.PI);
      const pos = geo.attributes.position, uv = geo.attributes.uv, n = pos.count;
      const col = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) {
        const sn = pos.getX(i) / r, cs = pos.getZ(i) / r;     // sin θ, cos θ (θ = 0 : face au visiteur)
        uv.setX(i, 0.5 + 0.5 * sn);
        let b = (0.6 + 0.4 * Math.max(0, cs)) * (1 + 0.1 * -sn);  // les bords à l'ombre, la gauche un peu plus claire
        b += 0.16 * Math.exp(-((sn + 0.42) ** 2) / 0.012);           // le reflet vertical, comme sur du verre
        col[i * 3] = 0.94 * b; col[i * 3 + 1] = 0.9 * b; col[i * 3 + 2] = 0.84 * b;
      }
      geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
      return new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: it.t, vertexColors: true, toneMapped: false,
        alphaTest: 0.45, alphaToCoverage: true }));
    }

    // L'ÉTALAGE (26/11, Mongazi : « relève le niveau ») : fini le cercle de douze produits qui tournaient, se
    // cachaient les uns les autres et passaient par la tranche. Deux gradins, comme dans une vraie boutique : les grands
    // flacons sur la marche du fond, les pots et les petits devant ; chacun à sa taille, espacé, tourné vers le
    // visiteur, posé sur son ombre. Rien ne tourne : la 3D se repose quand rien ne bouge.
    async function remplir(v, k) {
      if (v.charge) return;
      v.charge = true;
      const items = (await Promise.all(v.prods.map(async (p) => {
        const t = await charger(ina.detoures[p.n] || ina.img[p.n]);
        if (!t) return null;
        return { p, t, a: t.image.width / t.image.height };
      }))).filter(Boolean);
      if (!items.length) return;
      // jusqu'à trois produits, une seule rangée, posée SUR la marche et plus grande (sinon la marche reste vide et
      // les produits se perdent sur le socle)
      const echelle = items.length > 3 ? 1.12 : 1.4;
      items.forEach((it) => { it.h = hauteur(it.p, it.a) * echelle; it.w = Math.min(0.56 * echelle, it.h * it.a); });
      // les plus hauts derrière ; à une seule rangée sous quatre produits
      items.sort((x, y) => y.h - x.h || x.p.n.localeCompare(y.p.n, "fr"));
      const deux = items.length > 3;
      const fond = deux ? items.slice(0, Math.ceil(items.length / 2)) : [];
      const devant = deux ? items.slice(fond.length) : items;
      const rangee = (liste, y, z, largeur) => {
        // la plus grande au milieu, les autres de part et d'autre (l'œil part du centre)
        const ordre = [];
        liste.forEach((it, i) => (i % 2 ? ordre.push(it) : ordre.unshift(it)));
        const gap = 0.07, total = ordre.reduce((s, it) => s + it.w, 0) + gap * (ordre.length - 1);
        const e = Math.min(1, largeur / total);
        let x = -total * e / 2;
        ordre.forEach((it) => {
          const w = it.w * e, h = (it.w / it.a) * e;
          const carte = new THREE.Group();
          const photo = volume(it, w, h);
          photo.position.y = h / 2;
          carte.add(photo);
          carte.position.set(x + w / 2, y + 0.004, z);
          carte.userData.act = () => quand.produit(it.p);
          carte.userData.k = k + 1;
          carte.userData.p = it.p;
          v.ronde.add(carte);
          cliquables.push(carte);
          const ombre = new THREE.Mesh(new THREE.PlaneGeometry(w * 1.25, Math.min(0.22, w * 0.55)), mOmbre);
          ombre.rotation.x = -Math.PI / 2; ombre.position.set(x + w / 2, y + 0.003, z);
          v.ronde.add(ombre);
          x += w + gap * e;
        });
      };
      // `ronde` est posé sur le socle (y = 0,36, au centre du socle) : le devant en avant du centre, la marche derrière
      if (deux) { rangee(fond, 0.26, -0.46, 1.6); rangee(devant, 0, 0.4, 1.75); }
      else rangee(devant, 0.26, -0.46, 1.6);
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
        // au téléphone (26/11) : plus près, et visée plus basse, pour que les produits montent au-dessus de la fiche
        camM: { p: [cx - v.cote * 3.75, 1.55, v.z + 0.8], c: [cx, -0.5, v.z] },
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
        // (26/11) les ombres restent : figées, elles ne coûtent presque plus rien, et les couper recompilait toutes les matières (la 3D gelée)
        scene.remove(pous);
      },
      anime(t, dt, etat) {
        const v = vitrines[kActif - 1];
        if (!v || !v.charge) return false;
        // chaque produit regarde le visiteur : une découpe plate ne se montre jamais par la tranche (les ombres, à plat,
        // ne bougent pas)
        const cp = etat.camera.position;
        // aux deux tiers seulement (27/11) : quand la caméra se déplace, on voit la rondeur des flacons
        v.ronde.children.forEach((c) => {
          if (!c.isGroup) return;
          ou.copy(cp); v.ronde.worldToLocal(ou);
          c.rotation.y = Math.atan2(ou.x - c.position.x, ou.z - c.position.z) * 0.68;
        });
        if (calme || qualiteBasse) return false;
        pous.userData.animer(dt);
        return true;
      },
    };
  };
}
