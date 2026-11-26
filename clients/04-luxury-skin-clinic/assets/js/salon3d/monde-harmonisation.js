// LE CABINET PRIVÉ · harmonisation faciale (l'ex-Cozy). Encre et or, les couleurs de ses flyers.
// Ses trois flyers sont posés dans des cadres dorés, sous un projecteur chacun. On touche une zone : elle s'allume
// SUR SON VISUEL (le reste se voile), la caméra s'approche (Vibrant Wellness) et la fiche donne la zone et son tarif
// (Facework). ⛔ Aucun visage n'est inventé : les visages sont ceux de ses flyers, à sa demande.
import { THREE } from "./moteur.js";
import { marbre, plaque, poussiere, ambiance, boiteArrondie, degrade } from "./matieres.js";

const FW = 1.62, FH = 2.88;            // le flyer (900 × 1600)
const R = 5.6, CENTRE = [0, 0, 1];     // l'arc des trois cadres
const PAS_ARC = 0.62;                // l'écart entre deux cadres sur l'arc (3,5 m)

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

export function cabinet({ donnees, prix, forfait = () => "", lien, quand }) {
  return async ({ scene, renderer, camera, mobile, calme, outils }) => {
    const { anis, charger } = outils;
    scene.background = new THREE.Color(0x0c0a07);
    scene.fog = new THREE.Fog(0x0c0a07, 10, 24);
    scene.environment = ambiance(renderer, { mur: 0x2a2116, chaud: 0xffdcaa, lumieres: [[0, 9, 0, 10, 0.4, 10, 2.2], [-9, 4, 0, 0.4, 5, 8, 1.4], [9, 4, 0, 0.4, 5, 8, 1.4]] });
    renderer.toneMappingExposure = 1.05;

    // ---------- la pièce ----------
    const sol = new THREE.Mesh(new THREE.PlaneGeometry(44, 44),
      new THREE.MeshStandardMaterial({ map: marbre(anis, { rep: 3 }), roughness: 0.2, metalness: 0.15, envMapIntensity: 0.8 }));
    sol.rotation.x = -Math.PI / 2; sol.receiveShadow = true; scene.add(sol);

    const mur = new THREE.Mesh(new THREE.CylinderGeometry(9.6, 9.6, 7.5, 96, 1, true, Math.PI - 1.35, 2.7),
      new THREE.MeshStandardMaterial({ color: 0x1b150e, roughness: 0.55, metalness: 0.25, side: THREE.BackSide }));
    mur.position.set(CENTRE[0], 3.75, CENTRE[2]); scene.add(mur);
    // les filets d'or du mur (une latte tous les 7°)
    const filet = new THREE.MeshStandardMaterial({ color: 0xc9a84c, emissive: 0x8a6a22, emissiveIntensity: 0.45, metalness: 0.9, roughness: 0.35 });
    const nf = 38, lattes = new THREE.InstancedMesh(new THREE.BoxGeometry(0.035, 7.5, 0.035), filet, nf);
    const mm = new THREE.Matrix4(), q = new THREE.Quaternion();
    for (let i = 0; i < nf; i++) {
      const a = Math.PI - 1.33 + (i / (nf - 1)) * 2.66;
      q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), a);
      mm.compose(new THREE.Vector3(CENTRE[0] + Math.sin(a) * 9.5, 3.75, CENTRE[2] + Math.cos(a) * 9.5), q, new THREE.Vector3(1, 1, 1));
      lattes.setMatrixAt(i, mm);
    }
    scene.add(lattes);

    scene.add(new THREE.AmbientLight(0x3b3022, 0.55));
    scene.add(new THREE.HemisphereLight(0x6a5638, 0x0a0806, 0.35));

    // ---------- les trois cadres ----------
    const orMetal = new THREE.MeshStandardMaterial({ color: 0xb48c3c, metalness: 0.95, roughness: 0.3, envMapIntensity: 1.3 });
    const socleMat = new THREE.MeshStandardMaterial({ map: marbre(anis, { rep: 1, base: "#1d1812" }), roughness: 0.25, metalness: 0.1 });
    const cadres = [];
    // les cadres se répartissent sur l'arc, autant qu'il y a de techniques (4 depuis le 26/11)
    const ANGLES = donnees.map((_, i) => (i - (donnees.length - 1) / 2) * PAS_ARC);
    for (let i = 0; i < donnees.length; i++) {
      const a = ANGLES[i];
      const P = new THREE.Vector3(CENTRE[0] + R * Math.sin(a), 1.95, CENTRE[2] - R * Math.cos(a));
      const n = new THREE.Vector3(-Math.sin(a), 0, Math.cos(a));
      const droite = new THREE.Vector3(Math.cos(a), 0, Math.sin(a));
      const g = new THREE.Group();
      g.position.copy(P); g.rotation.y = -a;
      const cadre = new THREE.Mesh(boiteArrondie(FW + 0.24, FH + 0.24, 0.09, 0.05), orMetal);
      cadre.castShadow = true; g.add(cadre);
      const fond = new THREE.Mesh(new THREE.PlaneGeometry(FW + 0.08, FH + 0.08), new THREE.MeshBasicMaterial({ color: 0x0b0906 }));
      fond.position.z = 0.047; g.add(fond);
      const flyerMat = new THREE.MeshBasicMaterial({ color: 0x222222, toneMapped: false });
      const flyer = new THREE.Mesh(new THREE.PlaneGeometry(FW, FH), flyerMat);
      flyer.position.z = 0.05; g.add(flyer);
      // le voile qui allume la zone choisie
      const toile = document.createElement("canvas");
      toile.width = 450; toile.height = 800;
      const voileTex = new THREE.CanvasTexture(toile);
      voileTex.colorSpace = THREE.SRGBColorSpace;
      const voile = new THREE.Mesh(new THREE.PlaneGeometry(FW, FH),
        new THREE.MeshBasicMaterial({ map: voileTex, transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
      voile.position.z = 0.056; g.add(voile);
      // le pied et le socle
      const pied = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.5, 16), orMetal);
      pied.position.set(0, -FH / 2 - 0.37, -0.02); g.add(pied);
      const socle = new THREE.Mesh(boiteArrondie(1.5, 0.28, 0.62, 0.05), socleMat);
      socle.position.set(0, -1.95 + 0.14, 0); socle.castShadow = true; socle.receiveShadow = true; g.add(socle);
      // la plaque gravée du socle
      const pl = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.16), new THREE.MeshStandardMaterial({
        map: plaque(anis, { w: 1024, h: 150, fond: "#b8954a", lignes: [{ t: donnees[i].nom.toUpperCase(), font: "500 74px 'Cormorant Garamond', Georgia, serif", couleur: "#2a1d0a", y: 0.55, espace: "8px" }] }),
        metalness: 0.7, roughness: 0.35 }));
      pl.position.set(0, -1.95 + 0.14, 0.315); g.add(pl);
      scene.add(g);
      g.updateMatrixWorld(true);

      // un projecteur par cadre
      const spot = new THREE.SpotLight(0xffe2b4, mobile ? 55 : 70, 14, 0.4, 0.75, 1.6);
      spot.position.copy(P).addScaledVector(n, 2.6).add(new THREE.Vector3(0, 3.1, 0));
      spot.target.position.copy(P);
      if (i === 1 && !mobile) { spot.castShadow = true; spot.shadow.mapSize.set(1024, 1024); spot.shadow.bias = -0.0004; }
      scene.add(spot, spot.target);
      // le faisceau, à peine visible
      const cone = new THREE.Mesh(new THREE.ConeGeometry(1.35, 3.4, 40, 1, true),
        new THREE.MeshBasicMaterial({ map: degrade(anis, [[0, "rgba(255,226,170,.0)"], [1, "rgba(255,226,170,.55)"]]), transparent: true, opacity: 0.07, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide }));
      cone.position.copy(spot.position).lerp(P, 0.5);
      cone.lookAt(P); cone.rotateX(Math.PI / 2);
      scene.add(cone);

      cadres.push({ g, P, n, droite, flyerMat, voile, toile, voileTex, src: donnees[i].flyer, charge: false, anim: 0, rects: [] });
    }

    // le flyer en texture, à pleine définition (900 × 1600 : il est net jusqu'à 1,6 fois sa taille à l'écran)
    const chargerFlyer = async (c) => {
      if (c.charge) return;
      c.charge = true;
      const t = await charger(c.src);
      if (t) { c.flyerMat.map = t; c.flyerMat.color.set(0xffffff); c.flyerMat.needsUpdate = true; lien.moteur && lien.moteur.rafraichir(); }
    };
    cadres.forEach(chargerFlyer);

    // ---------- le profil tracé au fil d'or (l'entrée) ----------
    const prof = [[0.30, 1.40], [0.05, 1.45], [-0.18, 1.33], [-0.26, 1.15], [-0.285, 1.03], [-0.255, 0.98], [-0.272, 0.93], [-0.365, 0.80],
      [-0.30, 0.76], [-0.287, 0.73], [-0.315, 0.70], [-0.286, 0.676], [-0.303, 0.65], [-0.266, 0.615], [-0.292, 0.56], [-0.24, 0.50],
      [-0.08, 0.47], [-0.10, 0.30], [-0.13, 0.05]].map(([x, y]) => new THREE.Vector3(x * 1.25, y * 1.25, 0));
    const tube = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(prof, false, "centripetal"), 420, 0.016, 8, false);
    const filOr = new THREE.MeshStandardMaterial({ color: 0xe2c47a, emissive: 0xc9a84c, emissiveIntensity: 0.95, metalness: 1, roughness: 0.25 });
    const profil = new THREE.Mesh(tube, filOr);
    const oeil = new THREE.Mesh(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(new THREE.Vector3(-0.255, 1.205, 0), new THREE.Vector3(-0.215, 1.18, 0), new THREE.Vector3(-0.17, 1.2, 0)), 24, 0.008, 6), filOr);
    const groupeProfil = new THREE.Group();
    groupeProfil.add(profil, oeil);
    // la sculpture est posée sur le piédestal de la consultation, au centre du cabinet
    groupeProfil.scale.setScalar(0.92);
    groupeProfil.position.set(1.85, 0.92, 3.7);
    scene.add(groupeProfil);
    const nTrace = tube.index.count;
    let trace = calme ? 1 : 0;
    tube.setDrawRange(0, calme ? nTrace : 0);
    oeil.visible = calme;

    // ---------- la console de consultation ----------
    // un piédestal rond, marbre et bague d'or, qui porte la sculpture et la carte de consultation
    const pied3 = new THREE.Group();
    const fut = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.56, 0.9, 64), socleMat);
    fut.position.y = 0.45; fut.castShadow = true; fut.receiveShadow = true;
    const bague = new THREE.Mesh(new THREE.TorusGeometry(0.505, 0.018, 12, 96), orMetal);
    bague.rotation.x = Math.PI / 2; bague.position.y = 0.905;
    const bague2 = bague.clone(); bague2.position.y = 0.06; bague2.scale.setScalar(1.11);
    pied3.add(fut, bague, bague2);
    pied3.position.set(1.6, 0, 3.6);
    scene.add(pied3);
    const carte = new THREE.Mesh(new THREE.PlaneGeometry(0.86, 0.345), new THREE.MeshStandardMaterial({
      map: plaque(anis, { w: 1024, h: 410, fond: "#c9a84c", cadre: "rgba(42,29,10,.55)", lignes: [
        { t: "CONSULTATION", font: "600 96px 'Cormorant Garamond', Georgia, serif", couleur: "#2a1d0a", y: 0.46, espace: "6px" },
        { t: "TOUCHEZ POUR DEMANDER", font: "500 40px 'DM Mono', monospace", couleur: "#3d2b10", y: 0.76, espace: "6px" }] }),
      metalness: 0.6, roughness: 0.35 }));
    // la carte, posée contre le fût, tournée vers le visiteur
    carte.position.set(1.6, 0.52, 3.6 + 0.575); carte.rotation.x = -0.16;
    carte.userData.act = () => quand.consulter();
    carte.userData.k = 4;
    scene.add(carte);

    // ---------- la poussière d'or ----------
    const pous = poussiere(anis, { n: mobile ? 70 : 150, boite: [12, 4.5, 9], centre: [0, 2.2, -0.5], couleur: "236,205,140", taille: mobile ? 0.06 : 0.045, opacite: 0.6 });
    if (!calme) scene.add(pous);

    // ---------- le voile : la zone choisie s'allume, le reste se tait ----------
    function dessinerVoile(c, rects, k) {
      const g = c.toile.getContext("2d"), W = c.toile.width, H = c.toile.height;
      g.clearRect(0, 0, W, H);
      g.fillStyle = "rgba(6,5,3,.64)";
      g.fillRect(0, 0, W, H);
      const e = 0.9 + 0.1 * k;
      for (const [x0, y0, x1, y1] of rects) {
        const cx = ((x0 + x1) / 2) * W, cy = ((y0 + y1) / 2) * H, w = (x1 - x0) * W * e, h = (y1 - y0) * H * e;
        g.globalCompositeOperation = "destination-out";
        g.beginPath(); g.roundRect(cx - w / 2, cy - h / 2, w, h, 12); g.fill();
        g.globalCompositeOperation = "source-over";
        g.strokeStyle = `rgba(244,221,158,${0.4 + 0.6 * k})`;
        g.lineWidth = 2.4; g.setLineDash([7, 6]);
        g.beginPath(); g.roundRect(cx - w / 2, cy - h / 2, w, h, 12); g.stroke();
      }
      g.setLineDash([]);
      c.voileTex.needsUpdate = true;
    }

    let choix = { t: -1, z: 0 };
    const ici = new THREE.Vector3();
    function choisir(ti, zi, avecSon = true) {
      const c = cadres[ti], z = donnees[ti].zones[zi];
      choix = { t: ti, z: zi };
      // une zone d'une autre technique : on va d'abord devant son cadre (surStation la rallumera)
      if (lien.moteur && lien.moteur.station() !== ti + 1) { quand.choix(ti, zi); lien.moteur.aller(ti + 1); return; }
      c.rects = z.r; c.anim = 0;
      cadres.forEach((o, j) => { if (j !== ti) o.voileVise = 0; });
      c.voileVise = 1;
      // s'approcher de la zone (la caméra glisse vers son centre)
      const u = z.r.reduce((s, r) => s + (r[0] + r[2]) / 2, 0) / z.r.length;
      const v = z.r.reduce((s, r) => s + (r[1] + r[3]) / 2, 0) / z.r.length;
      ici.set((u - 0.5) * FW, (0.5 - v) * FH, 0.06).applyMatrix4(c.g.matrixWorld);
      const st = cle(stations[ti + 1]);
      const cible = ici.clone();
      if (mobile) cible.y -= 0.62; else cible.addScaledVector(c.droite, -0.62);
      const pos = cible.clone().addScaledVector(c.n, mobile ? 3.0 : 2.0);
      if (!calme && lien.moteur) lien.moteur.approcher(
        [pos.x - st.p[0], pos.y - st.p[1], pos.z - st.p[2]],
        [cible.x - st.c[0], cible.y - st.c[1], cible.z - st.c[2]]);
      if (avecSon && quand.son) quand.son();
      quand.choix(ti, zi);
      lien.moteur && lien.moteur.rafraichir();
    }
    lien.choisir = choisir;
    lien.choix = () => choix;

    // ---------- les stations ----------
    const camTech = (i) => {
      const c = cadres[i];
      if (mobile) {
        const cib = c.P.clone(); cib.y -= 0.95;
        const p = cib.clone().addScaledVector(c.n, 4.6);
        return { p: p.toArray(), c: cib.toArray() };
      }
      const cib = c.P.clone().addScaledVector(c.droite, -0.95);
      const p = cib.clone().addScaledVector(c.n, 3.35);
      return { p: p.toArray(), c: cib.toArray() };
    };
    const cle = (s) => (mobile && s.camM ? s.camM : s.cam);

    const ficheTech = (t, i) => {
      const z = t.zones[0];
      return `<div class="s3d-panneau hz-fiche" data-t="${i}">
        <div class="s3d-etiq"><b>0${i + 1} / 0${donnees.length}</b> Cabinet privé</div>
        <h2 class="hz-titre" style="font-size:clamp(30px,3.2vw,46px)">${esc(t.nom)}</h2>
        <p class="hz-texte">${esc(t.texte)}</p>
        <div class="hz-zones" role="tablist" aria-label="Les zones de ${esc(t.nom)}">${t.zones.map((zz, j) =>
          `<button type="button" role="tab" data-t="${i}" data-z="${j}" aria-selected="${j ? "false" : "true"}">${esc(zz.nom)}</button>`).join("")}</div>
        <div class="s3d-prix"><span>Zone<b class="hz-zone-nom">${esc(z.nom)}</b><span class="hz-zone-detail">${esc(z.detail || "")}</span></span>
          <span>Tarif<b class="hz-prix">${esc(prix(z))}</b></span>${t.zones.some((x) => x.forfait) ? `<span>Forfait<b class="hz-forfait">${esc(forfait(z))}</b></span>` : ""}</div>
        ${t.note ? `<p class="hz-note">${esc(t.note)}</p>` : ""}
        <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-consult data-t="${i}" data-z="0">Demander ma consultation</button>
          <button type="button" class="s3d-btn" data-suivante="${i}">Zone suivante</button></div>
      </div>`;
    };

    const stations = [
      { id: "entree", nom: "Entrée", cote: "a-gauche",
        cam: { p: [0, 1.62, 8.6], c: [0, 1.55, 2.4] }, camM: { p: [0, 1.5, 9.8], c: [0, 1.35, 2.4] },
        calque: `<div class="s3d-panneau"><div class="s3d-etiq"><b>Cabinet privé</b></div>
          <h2>${["", "Une technique", "Deux techniques", "Trois techniques", "Quatre techniques", "Cinq techniques"][donnees.length] || donnees.length + " techniques"}.<br>Une lecture, zone par zone.</h2>
          <p>Touchez une zone sur le visuel : elle s'allume, et son tarif s'affiche.</p>
          <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-aller="1">Entrer dans le cabinet</button>
          <a class="s3d-btn" href="#techniques">Voir tous les tarifs</a></div></div>` },
      ...donnees.map((t, i) => {
        const c = camTech(i);
        return { id: t.id, nom: t.nom, cote: "a-gauche", cam: c, camM: c,
          calque: ficheTech(t, i),
          points: t.zones.map((z, j) => {
            const pin = z.pin || [(z.r[0][0] + z.r[0][2]) / 2, (z.r[0][1] + z.r[0][3]) / 2];
            const w = new THREE.Vector3((pin[0] - 0.5) * FW, (0.5 - pin[1]) * FH, 0.07).applyMatrix4(cadres[i].g.matrixWorld);
            return { id: `${i}-${j}`, p: w.toArray(), label: z.nom, act: () => choisir(i, j) };
          }) };
      }),
      { id: "consultation", nom: "Consultation", cote: "a-gauche",
        cam: { p: [0, 2.35, 6.4], c: [0, 1.35, -2.2] }, camM: { p: [0, 2.6, 8.2], c: [0, 1.1, -2.2] },
        calque: `<div class="s3d-panneau"><div class="s3d-etiq"><b>${String(donnees.length + 1).padStart(2, "0")}</b> Votre consultation</div>
          <h2>Une zone vous parle&nbsp;?</h2>
          <p class="hz-recap">Choisissez une zone, puis écrivez-nous : nous vous répondons sur WhatsApp pour fixer le rendez-vous.</p>
          <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-consult>Demander ma consultation</button>
          <a class="s3d-btn" href="luxury-skin-clinic.html">Les soins de la clinique</a></div></div>` },
    ];
    // les cadres eux-mêmes se touchent : on va à leur station
    cadres.forEach((c, i) => {
      c.voile.userData.act = () => { if (lien.moteur && lien.moteur.station() !== i + 1) lien.moteur.aller(i + 1); };
    });

    let qualiteBasse = false, kEntree = 0;
    return {
      stations,
      cliquables: [carte, ...cadres.map((c) => c.voile)],
      surStation(k) {
        kEntree = k;
        if (k >= 1 && k <= donnees.length) {
          const ti = k - 1;
          choisir(ti, choix.t === ti ? choix.z : 0, false);
        } else {
          cadres.forEach((o) => { o.voileVise = 0; });
          lien.moteur && lien.moteur.approcher(null);
        }
        if (k === 0 && trace < 1 && quand.entree) quand.entree();
      },
      qualite(q) {
        if (q !== "basse") return;
        qualiteBasse = true;
        // (26/11) les ombres restent : figées, elles ne coûtent presque plus rien, et les couper recompilait toutes les matières (la 3D gelée)
        scene.remove(pous);
      },
      anime(t, dt) {
        let vivant = false;
        // le fil d'or se trace à l'entrée, puis le profil respire
        if (trace < 1 && quand.porteOuverte && quand.porteOuverte()) {
          trace = Math.min(1, trace + dt / 2.6);
          const n = Math.floor((nTrace / 3) * (1 - Math.pow(1 - trace, 3))) * 3;
          tube.setDrawRange(0, n);
          if (trace > 0.62) oeil.visible = true;
          vivant = true;
        }
        const devantProfil = kEntree === 0 || kEntree === donnees.length + 1;
        if (!calme && devantProfil) { groupeProfil.rotation.y = Math.sin(t * 0.35) * 0.22; vivant = vivant || !qualiteBasse; }
        // le voile de chaque cadre
        for (const c of cadres) {
          const m = c.voile.material, vise = c.voileVise || 0;
          if (Math.abs(m.opacity - vise) > 0.004) { m.opacity += (vise - m.opacity) * Math.min(1, dt * 6); vivant = true; }
          if (vise && c.anim < 1) {
            c.anim = calme ? 1 : Math.min(1, c.anim + dt / 0.45);
            dessinerVoile(c, c.rects, 1 - Math.pow(1 - c.anim, 3));
            vivant = true;
          }
        }
        if (!qualiteBasse && !calme && vivant) pous.userData.animer(dt);
        return vivant;
      },
    };
  };
}
