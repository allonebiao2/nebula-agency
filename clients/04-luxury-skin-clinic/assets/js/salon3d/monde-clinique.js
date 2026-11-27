// LA CLINIQUE · Luxury Skin Clinic, un salon de beauté en plein jour.
// « Une clinique esthétique, c'est la lumière qu'on approche d'une peau : d'abord pour la lire, ensuite pour la révéler. »
// Le parcours (d'après FIRST PAGE 3D) : l'accueil, le couloir des soins du visage qu'on LONGE, la cabine où la lampe
// descend, le corps, les cheveux, le salon VIP, l'étagère INA, la porte dorée du cabinet privé, le bureau des rendez-vous.
// Les soins, leurs prix et leurs durées sont LUS dans SERVICES (la page) : rien n'est recopié ici.
import { THREE } from "./moteur.js";
import { terrazzo, marbre, chene, platre, plaque, caisson, degrade, feuille, poussiere, ambiance, boiteArrondie, demiLune, graine } from "./matieres.js";

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fcfa = (n) => (n || 0).toLocaleString("fr-FR").replace(/\u202f|\u00a0/g, " ") + " F";
// les portes des soins du visage, des DEUX côtés du couloir en alternance (8 soins depuis le 26/11) :
// k pair au mur du fond (z < 0), k impair au mur d'en face (z > 0), une porte tous les 1,8 m
const XV = (k) => 9 + k * 1.8;
const MUR = (k) => (k % 2 ? -1 : 1);     // +1 : mur du fond (on le regarde vers -z) ; -1 : mur d'en face

export function clinique({ services, art = {}, artFamille = {}, lien, quand }) {
  return async ({ scene, renderer, camera, mobile, calme, outils }) => {
    const { anis, charger } = outils;
    scene.background = new THREE.Color(0xf3eee5);
    scene.fog = new THREE.Fog(0xf3eee5, 16, 40);
    scene.environment = ambiance(renderer, { mur: 0xd8d0c2, chaud: 0xfff4e2 });
    renderer.toneMappingExposure = 1.0;

    // ---------- les matières ----------
    // LA LUMIÈRE, VAGUE 3 (26/11, « 10 000 $ ») : un terrazzo fin (éclats proches du fond, moins nombreux), des murs à la
    // chaux (les nuages du plâtre, vus en grand, faisaient des taches), un plafond blanc chaud au lieu d'un béton gris
    const mTerrazzo = new THREE.MeshStandardMaterial({ map: terrazzo(anis, { rep: 14, n: 1700,
      eclats: ["#dcd4c6", "#cbdad2", "#e2d3b0", "#f7f4ee", "#d3c8b8", "#bcd0c6"] }), roughness: 0.36, envMapIntensity: 0.55 });
    const mPlatre = new THREE.MeshStandardMaterial({ map: platre(anis, { rep: 6, amp: 5, taches: 0.4 }), roughness: 0.95 });
    const mChene = new THREE.MeshStandardMaterial({ map: chene(anis), roughness: 0.62 });
    const mBlanc = new THREE.MeshStandardMaterial({ color: 0xf7f3ec, roughness: 0.4 });
    const mLaiton = new THREE.MeshStandardMaterial({ color: 0xc9a24e, metalness: 1, roughness: 0.32, envMapIntensity: 1.2 });
    const mMenthe = new THREE.MeshStandardMaterial({ color: 0x8fb3a4, roughness: 0.96 });
    const mMarbre = new THREE.MeshStandardMaterial({ map: marbre(anis, { base: "#eeeae2", veine: "rgba(150,138,118,", rep: 1, n: 26 }), roughness: 0.22 });
    const mVerre = new THREE.MeshStandardMaterial({ color: 0xeef3f1, roughness: 0.12, transparent: true, opacity: 0.62, envMapIntensity: 1.1 });
    const mTerre = new THREE.MeshStandardMaterial({ color: 0xd9cbb4, roughness: 0.85 });

    const ajoute = (geo, mat, x, y, z, ombre = true) => {
      const m = new THREE.Mesh(geo, mat);
      m.position.set(x, y, z);
      if (ombre) { m.castShadow = true; m.receiveShadow = true; }
      scene.add(m);
      return m;
    };

    // ---------- le sol, le plafond, les murs ----------
    const sol = new THREE.Mesh(new THREE.PlaneGeometry(80, 34), mTerrazzo);
    sol.rotation.x = -Math.PI / 2; sol.position.set(22, 0, -1); sol.receiveShadow = true; scene.add(sol);
    // le plafond reçoit peu de lumière directe : une pointe d'émission le garde clair, comme un plafond blanc de jour
    const plafond = new THREE.Mesh(new THREE.PlaneGeometry(80, 34), new THREE.MeshStandardMaterial({ map: platre(anis, { rep: 6, base: "#f7f2e9", amp: 3, taches: 0.25 }), roughness: 0.95, emissive: 0xe4dac8, emissiveIntensity: 0.56 }));
    plafond.rotation.x = Math.PI / 2; plafond.position.set(22, 3.6, -1); scene.add(plafond);
    const mur = (w, x, z, ry = 0) => {
      const mat = mPlatre.clone(); mat.map = mPlatre.map.clone(); mat.map.repeat.set(Math.max(1, w / 3), 1.2); mat.map.needsUpdate = true;
      const m = ajoute(new THREE.BoxGeometry(w, 3.6, 0.2), mat, x, 1.8, z, false); m.rotation.y = ry; m.receiveShadow = true; return m;
    };
    mur(12.4, 0, -6.1);                               // le fond de l'accueil
    mur(3.8, 6.1, -4.2, Math.PI / 2);                 // la cloison de droite (avant le couloir)
    mur(3.8, 6.1, 4.2, Math.PI / 2);
    mur(44, 28, -2.5);                                // le mur des portes du couloir
    mur(38, 25, 2.5);                                 // le mur d'en face
    mur(6, 47, 4.6); mur(9, 50.6, 0, Math.PI / 2);    // le hall du fond
    const gauche = mur(12.4, -6.1, 0, Math.PI / 2);   // le mur des baies
    gauche.visible = true;

    // ---------- les baies vitrées : le jour entre par la gauche ----------
    const ciel = new THREE.MeshBasicMaterial({ map: degrade(anis, [[0, "#dfeaf0"], [0.55, "#f2f4ef"], [1, "#fffaf0"]]), toneMapped: false });
    for (const z of [-3.6, 0, 3.6]) {
      const b = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 2.7), ciel);
      b.position.set(-5.98, 1.75, z); b.rotation.y = Math.PI / 2; scene.add(b);
      for (const dz of [-1.32, 1.32]) ajoute(new THREE.BoxGeometry(0.06, 2.8, 0.06), mLaiton, -5.95, 1.75, z + dz, false);
      ajoute(new THREE.BoxGeometry(0.06, 0.06, 2.7), mLaiton, -5.95, 3.12, z, false);
      ajoute(new THREE.BoxGeometry(0.06, 0.06, 2.7), mLaiton, -5.95, 0.38, z, false);
    }
    // les rais de lumière (des plans additifs, animés en opacité seulement)
    const rai = new THREE.MeshBasicMaterial({ map: degrade(anis, [[0, "rgba(255,246,224,.0)"], [0.5, "rgba(255,246,224,.55)"], [1, "rgba(255,246,224,.0)"]], { w: 256, h: 32 }),
      transparent: true, opacity: 0.32, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
    const rais = [];
    for (const z of [-3.6, 0, 3.6]) {
      const r = new THREE.Mesh(new THREE.PlaneGeometry(7, 2.2), rai);
      r.position.set(-2.6, 1.3, z + 0.4); r.rotation.set(0, 0.18, -0.52); scene.add(r); rais.push(r);
    }

    // ---------- la lumière ----------
    scene.add(new THREE.HemisphereLight(0xfffaf0, 0xd9cfbe, 1.15));
    const soleil = new THREE.DirectionalLight(0xfff1d8, 2.4);
    soleil.position.set(-12, 9, 5); soleil.target.position.set(2, 0, -2);
    soleil.castShadow = true;
    soleil.shadow.mapSize.set(mobile ? 1024 : 2048, mobile ? 1024 : 2048);
    Object.assign(soleil.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 30 });
    soleil.shadow.bias = -0.0005; soleil.shadow.normalBias = 0.02;
    scene.add(soleil, soleil.target);
    // les bandeaux lumineux du plafond
    const bandeau = new THREE.MeshBasicMaterial({ color: 0xfff6e6 });
    ajoute(new THREE.BoxGeometry(0.08, 0.03, 9), bandeau, 3.5, 3.57, 0, false);
    ajoute(new THREE.BoxGeometry(41, 0.03, 0.08), bandeau, 27, 3.57, 0, false);

    // ---------- l'accueil : lattes de chêne, miroir rond, comptoir en demi-lune ----------
    const nl = 58, lattes = new THREE.InstancedMesh(new THREE.BoxGeometry(0.06, 3.5, 0.08), mChene, nl);
    const mm = new THREE.Matrix4();
    for (let i = 0; i < nl; i++) { mm.makeTranslation(-3.4 + (i / (nl - 1)) * 6.8, 1.75, -5.94); lattes.setMatrixAt(i, mm); }
    lattes.receiveShadow = true; scene.add(lattes);

    const enseigne = new THREE.Group();
    const disque = new THREE.Mesh(new THREE.CircleGeometry(0.95, 96), new THREE.MeshStandardMaterial({
      map: plaque(anis, { w: 1024, h: 1024, fond: "#f6f2e8", reflet: false, lignes: [
        { t: "LS", font: "500 330px 'Cormorant Garamond', Georgia, serif", couleur: "#a8862f", y: 0.44 },
        { t: "LUXURY SKIN CLINIC", font: "500 62px 'Cormorant Garamond', Georgia, serif", couleur: "#4a3d22", y: 0.7, espace: "10px" },
        { t: "CABINET DE SOINS PRIVÉS", font: "500 30px 'DM Mono', monospace", couleur: "#7d5f18", y: 0.79, espace: "8px" }] }),
      roughness: 0.5 }));
    const anneau = new THREE.Mesh(new THREE.TorusGeometry(0.99, 0.035, 16, 128), new THREE.MeshBasicMaterial({ color: 0xfff2d8 }));
    const halo = new THREE.Mesh(new THREE.CircleGeometry(1.5, 64), new THREE.MeshBasicMaterial({
      map: degrade(anis, [[0, "rgba(255,236,200,.75)"], [0.5, "rgba(255,236,200,.18)"], [1, "rgba(255,236,200,0)"]], { w: 128, h: 128, radial: true }),
      transparent: true, depthWrite: false }));
    halo.position.z = -0.02;
    enseigne.add(halo, disque, anneau);
    enseigne.position.set(0, 2.3, -5.84);
    scene.add(enseigne);

    const comptoir = new THREE.Mesh(demiLune(1.75, 0.5, 1.02, Math.PI * 0.95), mBlanc);
    comptoir.position.set(0, 0, -3.3); comptoir.castShadow = comptoir.receiveShadow = true; scene.add(comptoir);
    const dessus = new THREE.Mesh(demiLune(1.82, 0.62, 0.05, Math.PI * 0.97), mMarbre);
    dessus.position.set(0, 1.04, -3.3); dessus.castShadow = true; scene.add(dessus);
    const nb = 46, bande = new THREE.InstancedMesh(new THREE.BoxGeometry(0.045, 0.86, 0.035), mChene, nb);
    const q = new THREE.Quaternion(), un = new THREE.Vector3(1, 1, 1);
    for (let i = 0; i < nb; i++) {
      const a = -1.35 + (i / (nb - 1)) * 2.7;
      q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), a);
      mm.compose(new THREE.Vector3(Math.sin(a) * 1.77, 0.5, -3.3 + Math.cos(a) * 1.77), q, un);
      bande.setMatrixAt(i, mm);
    }
    bande.castShadow = true; scene.add(bande);
    // sur le comptoir : un vase, un carnet, une lampe de laiton
    ajoute(new THREE.LatheGeometry([[0, 0], [0.09, 0], [0.11, 0.08], [0.07, 0.24], [0.05, 0.3]].map(([a, b]) => new THREE.Vector2(a, b)), 32), mTerre, -0.9, 1.07, -2.2);
    ajoute(new THREE.CylinderGeometry(0.012, 0.012, 0.42, 8), mLaiton, 0.9, 1.28, -2.3);
    ajoute(new THREE.SphereGeometry(0.11, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), mLaiton, 0.9, 1.49, -2.3);

    // ---------- les plantes (feuilles découpées, jamais deux pareilles) ----------
    const r = graine(229);
    function plante(x, z, { haut = 1.7, n = 360, forme = "olivier", taille = [0.07, 0.16], couleur = "#5f7f52" } = {}) {
      const g = new THREE.Group();
      const pot = new THREE.Mesh(new THREE.LatheGeometry([[0, 0], [0.32, 0], [0.38, 0.5], [0.4, 0.56], [0, 0.56]].map(([a, b]) => new THREE.Vector2(a, b)), 40), mTerre);
      pot.castShadow = pot.receiveShadow = true; g.add(pot);
      const tronc = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([[0, 0.5, 0], [0.05, 1.0, 0.02], [-0.04, haut * 0.8, 0.03], [0.02, haut, 0]].map((p) => new THREE.Vector3(...p))), 24, 0.035, 8), new THREE.MeshStandardMaterial({ color: 0x6b5843, roughness: 0.9 }));
      tronc.castShadow = true; g.add(tronc);
      const mf = new THREE.MeshStandardMaterial({ map: feuille(anis, { forme, couleur }), alphaTest: 0.5, side: THREE.DoubleSide, roughness: 0.8 });
      const fs = new THREE.InstancedMesh(new THREE.PlaneGeometry(taille[0], taille[1]), mf, n);
      const e = new THREE.Euler();
      for (let i = 0; i < n; i++) {
        const c = [[0, haut, 0], [0.32, haut * 0.82, 0.1], [-0.3, haut * 0.86, -0.08]][i % 3];
        const p = new THREE.Vector3(c[0] + (r() - 0.5) * 0.7, c[1] + (r() - 0.5) * 0.55, c[2] + (r() - 0.5) * 0.7);
        e.set(r() * 6.28, r() * 6.28, r() * 6.28);
        const s = 0.75 + r() * 0.6;
        mm.compose(p, q.setFromEuler(e), new THREE.Vector3(s, s, s));
        fs.setMatrixAt(i, mm);
      }
      fs.castShadow = true; g.add(fs);
      g.position.set(x, 0, z);
      scene.add(g);
      return g;
    }
    plante(-3.6, -4.8, { haut: 2.0 });
    plante(3.7, -4.8, { haut: 1.25, n: 60, forme: "monstera", taille: [0.36, 0.5], couleur: "#4f7a5c" });

    // ---------- le coin d'attente : banquette menthe, table de marbre ----------
    const banc = ajoute(boiteArrondie(2.6, 0.44, 0.86, 0.14), mMenthe, -4.75, 0.22, 0.4); banc.rotation.y = Math.PI / 2;
    const dos = ajoute(boiteArrondie(2.6, 0.55, 0.2, 0.1), mMenthe, -5.18, 0.7, 0.4); dos.rotation.y = Math.PI / 2;
    ajoute(new THREE.CylinderGeometry(0.46, 0.46, 0.05, 48), mMarbre, -3.4, 0.42, 0.4);
    ajoute(new THREE.CylinderGeometry(0.05, 0.12, 0.4, 24), mLaiton, -3.4, 0.2, 0.4);

    // ---------- la porte de verre de l'entrée (on la passe à la première station) ----------
    for (const x of [-1.6, 1.6]) {
      ajoute(new THREE.BoxGeometry(1.5, 3.0, 0.04), mVerre, x * 1.9, 1.5, 6.1, false);
      ajoute(new THREE.BoxGeometry(0.03, 0.9, 0.05), mLaiton, x * 1.9 - Math.sign(x) * 0.6, 1.3, 6.14, false);
    }

    // ---------- le couloir des soins du visage : une porte de verre et une plaque de laiton par soin ----------
    const visage = services.map((s, i) => ({ s, i })).filter((x) => x.s.g === "visage");
    const cliquables = [];
    const duree = (s) => ((s.meta || []).find((m) => /h|min|séance|semaine/i.test(m[0])) || [""])[0];
    // LES CAISSONS LUMINEUX (26/11, « 10 000 $ ») : huit fois le même panneau de bois et une plaque illisible, c'était le
    // couloir. Chaque soin a maintenant son caisson rétroéclairé à côté de sa porte : son croquis d'or (le même que sa
    // carte), son nom, son prix, sa durée, lisibles d'un coup d'œil. Les croquis et les polices sont chargés AVANT
    // d'être dessinés dans la toile (sinon : le texte dans une police de secours, et un caisson sans dessin).
    const svgImage = (svg) => new Promise((ok) => {
      if (!svg) return ok(null);
      const im = new Image();
      im.onload = () => ok(im); im.onerror = () => ok(null);
      im.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg
        .replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" width="832" height="400" ')
        .replace(/#c9a84c/g, "#a07a28"));
    });
    if (document.fonts && document.fonts.load) {
      await Promise.all(["600 86px 'Cormorant Garamond'", "500 70px 'Jost'", "500 23px 'DM Mono'"]
        .map((f) => document.fonts.load(f).catch(() => null)));
    }
    const croquis = await Promise.all(visage.map(({ s }) => svgImage(art[s.a] || artFamille[s.g] || "")));
    // un or satiné, pas un métal : le laiton poli reflétait le décor et virait au brun-noir selon l'angle
    const mCadre = new THREE.MeshStandardMaterial({ color: 0xc9a050, metalness: 0.3, roughness: 0.4 });
    const haloCaisson = degrade(anis, [[0, "rgba(255,226,170,.5)"], [0.55, "rgba(255,226,170,.12)"], [1, "rgba(255,226,170,0)"]], { w: 128, h: 128, radial: true });
    visage.forEach(({ s, i }, k) => {
      const x = XV(k), m = MUR(k), cx = x + m * 1.2;
      ajoute(new THREE.BoxGeometry(1.24, 2.5, 0.08), mChene, x, 1.25, -m * 2.36, false);
      const porte = ajoute(new THREE.BoxGeometry(1.04, 2.34, 0.04), mVerre, x, 1.19, -m * 2.3, false);
      ajoute(new THREE.BoxGeometry(1.1, 0.03, 0.05), new THREE.MeshBasicMaterial({ color: 0xfff2dc }), x, 2.62, -m * 2.33, false);
      // le cadre de laiton, le caisson, et sa lumière sur le mur
      ajoute(new THREE.BoxGeometry(0.98, 1.33, 0.05), mCadre, cx, 1.45, -m * 2.35, false);
      const cais = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.23), new THREE.MeshBasicMaterial({ toneMapped: false,
        map: caisson(anis, { croquis: croquis[k], sur: "Soin du visage · " + String(2 + k).padStart(2, "0"), nom: s.n, prix: fcfa(s.p), duree: duree(s) }) }));
      cais.position.set(cx, 1.45, -m * 2.318);
      const lumiere = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 2.3), new THREE.MeshBasicMaterial({ map: haloCaisson, transparent: true,
        depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
      lumiere.position.set(cx, 1.45, -m * 2.44);
      if (m < 0) { cais.rotation.y = Math.PI; lumiere.rotation.y = Math.PI; }
      scene.add(cais, lumiere);
      cais.userData.act = porte.userData.act = () => quand.voir(i);
      cais.userData.k = porte.userData.k = 2 + k;
      cliquables.push(cais, porte);
      if (k < visage.length - 2) plante(x + m * 2.3, -m * 1.95, { haut: 0.9, n: 140 });
    });

    // ---------- la cabine : la table de soin et la lampe-loupe qui descend ----------
    const CX = 29.5;
    ajoute(new THREE.BoxGeometry(6, 3.6, 0.2), mPlatre, CX, 1.8, -3.5, false);
    ajoute(boiteArrondie(1.7, 0.55, 0.6, 0.08), mBlanc, CX + 0.4, 0.3, -0.9);
    ajoute(boiteArrondie(2.05, 0.16, 0.78, 0.07), new THREE.MeshStandardMaterial({ color: 0xfbfaf6, roughness: 0.75 }), CX + 0.4, 0.66, -0.9);
    ajoute(boiteArrondie(0.42, 0.12, 0.5, 0.06), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85 }), CX - 0.38, 0.79, -0.9);
    ajoute(new THREE.CylinderGeometry(0.03, 0.03, 2.1, 12), mLaiton, CX - 1.3, 1.05, -1.75);
    const lampe = new THREE.Group();
    const bras = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 1.0, 10), mLaiton);
    bras.rotation.z = Math.PI / 2; bras.position.x = -0.5; lampe.add(bras);
    const tete = new THREE.Mesh(new THREE.TorusGeometry(0.17, 0.035, 16, 64), mBlanc); tete.rotation.x = Math.PI / 2; lampe.add(tete);
    const lentille = new THREE.Mesh(new THREE.CircleGeometry(0.15, 48), new THREE.MeshBasicMaterial({ color: 0xfff6e2, transparent: true, opacity: 0.9 }));
    lentille.rotation.x = -Math.PI / 2; lentille.position.y = -0.02; lampe.add(lentille);
    const lumLampe = new THREE.SpotLight(0xfff3dc, 0, 4, 0.6, 0.6, 1.5);
    lumLampe.position.set(0, -0.03, 0); lumLampe.target.position.set(0, -2, 0); lampe.add(lumLampe, lumLampe.target);
    lampe.position.set(CX - 0.3, 2.15, -1.0);
    scene.add(lampe);
    const vapeur = poussiere(anis, { n: 40, boite: [0.5, 0.9, 0.4], centre: [CX - 0.45, 1.25, -0.9], couleur: "255,255,255", taille: 0.16, opacite: 0.35 });
    vapeur.visible = false; scene.add(vapeur);
    // le chariot et ses flacons
    ajoute(boiteArrondie(0.6, 0.05, 0.42, 0.02), mBlanc, CX + 1.75, 0.78, -1.8);
    ajoute(boiteArrondie(0.6, 0.05, 0.42, 0.02), mBlanc, CX + 1.75, 0.38, -1.8);
    for (let j = 0; j < 4; j++) ajoute(new THREE.LatheGeometry([[0, 0], [0.04, 0], [0.04, 0.12], [0.015, 0.15], [0.015, 0.19], [0, 0.19]].map(([a, b]) => new THREE.Vector2(a, b)), 20),
      [mLaiton, mBlanc, mMenthe, mBlanc][j], CX + 1.55 + j * 0.13, 0.81, -1.8);

    // ---------- le corps et les cheveux ----------
    ajoute(boiteArrondie(1.95, 0.14, 0.72, 0.07), new THREE.MeshStandardMaterial({ color: 0xf1ede4, roughness: 0.85 }), 35.6, 0.72, -1.1);
    for (const x of [34.9, 36.3]) ajoute(new THREE.BoxGeometry(0.06, 0.65, 0.6), mChene, x, 0.33, -1.1);
    for (let j = 0; j < 3; j++) { const t = ajoute(new THREE.CylinderGeometry(0.09, 0.09, 0.5, 24), new THREE.MeshStandardMaterial({ color: [0xffffff, 0xe6f0ec, 0xffffff][j], roughness: 0.95 }), 34.95 + j * 0.2, 0.88, -0.5); t.rotation.x = Math.PI / 2; }
    for (let j = 0; j < 5; j++) { const p = ajoute(new THREE.SphereGeometry(0.075 - j * 0.008, 24, 16), new THREE.MeshStandardMaterial({ color: 0x2a2724, roughness: 0.4 }), 36.3, 0.84 + j * 0.06, -0.6); p.scale.y = 0.45; }
    // le bac du Hair Spa
    ajoute(boiteArrondie(0.75, 0.5, 0.8, 0.12), mMenthe, 39.8, 0.25, -0.6);
    ajoute(boiteArrondie(0.75, 0.6, 0.18, 0.08), mMenthe, 39.8, 0.75, -0.95);
    ajoute(new THREE.LatheGeometry([[0, 0], [0.28, 0], [0.34, 0.16], [0.36, 0.2], [0.33, 0.2], [0.3, 0.17], [0, 0.04]].map(([a, b]) => new THREE.Vector2(a, b)), 48), mBlanc, 39.8, 0.98, -1.55);
    ajoute(new THREE.BoxGeometry(0.5, 0.95, 0.4), mBlanc, 39.8, 0.48, -1.55);
    const robinet = ajoute(new THREE.TorusGeometry(0.12, 0.014, 10, 32, Math.PI), mLaiton, 39.8, 1.25, -1.82); robinet.rotation.y = Math.PI / 2;

    // ---------- le salon VIP : un fauteuil, une bougie ----------
    ajoute(boiteArrondie(1.0, 0.45, 0.9, 0.18), mMenthe, 43.2, 0.3, -1.1);
    ajoute(boiteArrondie(1.0, 0.75, 0.24, 0.12), mMenthe, 43.2, 0.75, -1.5);
    for (const x of [42.65, 43.75]) ajoute(boiteArrondie(0.2, 0.5, 0.86, 0.09), mMenthe, x, 0.58, -1.1);
    ajoute(new THREE.CylinderGeometry(0.28, 0.28, 0.04, 40), mMarbre, 44.35, 0.58, -0.75);
    ajoute(new THREE.CylinderGeometry(0.03, 0.06, 0.56, 16), mLaiton, 44.35, 0.28, -0.75);
    ajoute(new THREE.CylinderGeometry(0.05, 0.05, 0.12, 24), mBlanc, 44.35, 0.66, -0.75);
    const flamme = ajoute(new THREE.SphereGeometry(0.018, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffc46b }), 44.35, 0.745, -0.75, false);
    flamme.scale.y = 1.8;
    const bougie = new THREE.PointLight(0xffb85c, 0.9, 3, 2); bougie.position.set(44.35, 0.85, -0.75); scene.add(bougie);

    // ---------- l'étagère INA : les vraies photos, lues dans ina-luxury.html ----------
    const etag = new THREE.Group();
    for (const y of [0.9, 1.5, 2.1]) {
      const t = new THREE.Mesh(boiteArrondie(2.6, 0.04, 0.34, 0.015), mChene); t.position.y = y; etag.add(t);
      const led = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.012, 0.02), new THREE.MeshBasicMaterial({ color: 0xfff1d6 })); led.position.set(0, y - 0.03, 0.15); etag.add(led);
    }
    const fondEtag = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 2.2), new THREE.MeshStandardMaterial({ color: 0x1a1712, roughness: 0.6 }));
    fondEtag.position.set(0, 1.5, -0.17); etag.add(fondEtag);
    etag.position.set(47, 0, -2.2);
    scene.add(etag);
    let inaCharge = false;
    async function chargerINA() {
      if (inaCharge) return;
      inaCharge = true;
      try {
        const h = await (await fetch("ina-luxury.html", { credentials: "same-origin" })).text();
        const img = JSON.parse(h.match(/const IMG=(\{[\s\S]*?\n\});/)[1]);
        // les produits détourés (cliente, 26/11 : « les mettre en fond noir ») ; sans détourage, la photo garde sa carte
        const det = await fetch("assets/images/ina-luxury/_detoures/detoures.json?v=20261126y").then((r) => (r.ok ? r.json() : {})).catch(() => ({}));
        // les meilleures ventes d'abord (best:1), puis les nouveautés, dans l'ordre du catalogue
        const prods = [...h.matchAll(/\{f:'([^']+)',s:'[^']+',n:(['"])((?:(?!\2).)+)\2,p:\d+[^\n]*/g)].map((m) => ({ f: m[1], n: m[3], best: /best:1/.test(m[0]) }));
        const choix = [...prods.filter((p) => p.best), ...prods.filter((p) => !p.best)].filter((p) => img[p.n]).slice(0, 9);
        choix.forEach(async (p, j) => {
          const libre = !!det[p.n];
          const t = await charger(det[p.n] || img[p.n]);
          if (!t) return;
          const a = t.image.width / t.image.height;
          const hh = libre ? 0.46 : 0.42, w = Math.min(libre ? 0.6 : 0.62, hh * a), h2 = w / a;
          const carte = new THREE.Mesh(new THREE.PlaneGeometry(w, h2), new THREE.MeshBasicMaterial({ map: t, toneMapped: false, transparent: libre, alphaTest: libre ? 0.04 : 0 }));
          // posé SUR la tablette (le dessus du chêne est à y + 0,04)
          carte.position.set(-0.85 + (j % 3) * 0.85, 0.9 + Math.floor(j / 3) * 0.6 + 0.04 + h2 / 2, libre ? 0.04 : 0.02);
          carte.userData.act = () => quand.ina(p);
          carte.userData.k = ST.ina;
          etag.add(carte);
          cliquables.push(carte);
          lien.moteur && lien.moteur.rafraichir();
        });
      } catch (e) { console.warn("[clinique] étagère INA", e); }
    }

    // ---------- la porte dorée du cabinet privé ----------
    const porteOr = new THREE.Group();
    porteOr.add(new THREE.Mesh(boiteArrondie(1.7, 3.0, 0.12, 0.06), mLaiton));
    const vantail = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 2.7), new THREE.MeshStandardMaterial({ map: marbre(anis, { rep: 1 }), roughness: 0.3, metalness: 0.2, emissive: 0x3a2a0c, emissiveIntensity: 0.4 }));
    vantail.position.z = 0.065; porteOr.add(vantail);
    const plaqueOr = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.42), new THREE.MeshBasicMaterial({ toneMapped: false,
      map: plaque(anis, { w: 1024, h: 390, fond: "#16120c", reflet: false, cadre: "rgba(201,168,76,.7)", lignes: [
        { t: "CABINET PRIVÉ", font: "500 46px 'DM Mono', monospace", couleur: "#e2c47a", y: 0.32, espace: "10px" },
        { t: "Harmonisation faciale", font: "500 88px 'Cormorant Garamond', Georgia, serif", couleur: "#f3eadb", y: 0.64 }] }) }));
    plaqueOr.position.set(0, 0.45, 0.075); porteOr.add(plaqueOr);
    const lueur = new THREE.Mesh(new THREE.PlaneGeometry(3.6, 4.4), new THREE.MeshBasicMaterial({
      map: degrade(anis, [[0, "rgba(255,214,140,.55)"], [0.6, "rgba(255,214,140,.1)"], [1, "rgba(255,214,140,0)"]], { w: 128, h: 128, radial: true }),
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
    lueur.position.z = -0.05; porteOr.add(lueur);
    porteOr.position.set(50.45, 1.5, 0); porteOr.rotation.y = -Math.PI / 2;
    scene.add(porteOr);
    vantail.userData.act = plaqueOr.userData.act = () => quand.harmonisation();
    cliquables.push(vantail, plaqueOr);

    // ---------- le bureau des rendez-vous : le carnet ouvert ----------
    ajoute(boiteArrondie(1.6, 0.05, 0.8, 0.02), mBlanc, 47.6, 0.78, 3.4);
    for (const [x, z] of [[46.9, 3.1], [48.3, 3.1], [46.9, 3.7], [48.3, 3.7]]) ajoute(new THREE.CylinderGeometry(0.02, 0.02, 0.76, 10), mLaiton, x, 0.38, z);
    const page = (texte, x) => {
      const p = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.56), new THREE.MeshBasicMaterial({ toneMapped: false,
        map: plaque(anis, { w: 600, h: 800, fond: "#fbf8f1", reflet: false, lignes: texte }) }));
      p.rotation.x = -Math.PI / 2; p.rotation.z = Math.PI; p.position.set(x, 0.828, 3.35);
      scene.add(p); return p;
    };
    const carnet1 = page([{ t: "RENDEZ-VOUS", font: "500 34px 'DM Mono', monospace", couleur: "#7d5f18", y: 0.12, espace: "6px" },
      { t: "Lundi → samedi", font: "500 64px 'Cormorant Garamond', Georgia, serif", couleur: "#1f1e1a", y: 0.3 },
      { t: "10 h - 17 h", font: "500 64px 'Cormorant Garamond', Georgia, serif", couleur: "#1f1e1a", y: 0.42 },
      { t: "24 h à l'avance", font: "400 36px 'Jost', sans-serif", couleur: "#55524b", y: 0.6 },
      { t: "Acompte 5 100 F", font: "400 36px 'Jost', sans-serif", couleur: "#55524b", y: 0.7 }], 47.35);
    const carnet2 = page([{ t: "VOTRE CRÉNEAU", font: "500 34px 'DM Mono', monospace", couleur: "#7d5f18", y: 0.12, espace: "6px" },
      { t: "10 h", font: "400 44px 'Jost', sans-serif", couleur: "#9a9488", y: 0.3 }, { t: "11 h", font: "400 44px 'Jost', sans-serif", couleur: "#9a9488", y: 0.4 },
      { t: "14 h", font: "400 44px 'Jost', sans-serif", couleur: "#9a9488", y: 0.5 }, { t: "16 h", font: "400 44px 'Jost', sans-serif", couleur: "#9a9488", y: 0.6 }], 47.8);
    // la ligne « 10 h » du carnet (30 % du haut de la page, le haut de la page étant côté mur)
    const creneau = ajoute(new THREE.PlaneGeometry(0.36, 0.07), new THREE.MeshBasicMaterial({ color: 0xc9a84c, transparent: true, opacity: 0, depthWrite: false }), 47.8, 0.831, 3.462, false);
    creneau.rotation.x = -Math.PI / 2;
    const stylo = ajoute(new THREE.CylinderGeometry(0.008, 0.008, 0.36, 12), mLaiton, 48.15, 0.838, 3.3, false); stylo.rotation.z = Math.PI / 2; stylo.rotation.y = 0.4;
    carnet1.userData.act = carnet2.userData.act = () => quand.reserver();
    cliquables.push(carnet1, carnet2);
    plante(49.8, 4.2, { haut: 1.1, n: 50, forme: "monstera", taille: [0.3, 0.42], couleur: "#4f7a5c" });

    // ---------- la poussière de lumière dans les rais ----------
    const pous = poussiere(anis, { n: mobile ? 60 : 130, boite: [6, 2.6, 9], centre: [-2.5, 1.6, 0], couleur: "255,244,220", taille: 0.035, opacite: 0.65 });
    if (!calme) scene.add(pous);

    // ---------- les stations ----------
    const g = (k) => services.map((s, i) => ({ s, i })).filter((x) => x.s.g === k);
    const ligneSoin = ({ s, i }) => `<li><span><b>${esc(s.n)}</b><small>${esc(duree(s))}</small></span><em>${fcfa(s.p)}</em>
      <button type="button" class="s3d-btn plein" data-reserver="${i}">Réserver</button></li>`;
    const etiq = (n, t) => `<div class="s3d-etiq"><b>${String(n).padStart(2, "0")}</b> ${t}</div>`;
    const ST = {};
    const stations = [];
    const st = (o) => { ST[o.id] = stations.length; stations.push(o); return o; };

    st({ id: "entree", nom: "Entrée", cote: "a-gauche",
      cam: { p: [0, 1.7, 9.2], c: [0, 1.65, -4] }, camM: { p: [0, 1.6, 10.6], c: [0, -2.7, -4] },
      calque: `<div class="s3d-panneau">${etiq(0, "Luxury Skin Clinic")}<h2>Entrez. Ici, on lit votre peau avant de la soigner.</h2>
        <p>Faites défiler : la visite vous mène des soins à votre rendez-vous.</p>
        <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-aller="1">Commencer la visite</button>
        <button type="button" class="s3d-btn" data-aller-id="rdv">Prendre rendez-vous</button></div></div>` });
    st({ id: "accueil", nom: "Accueil", cote: "a-gauche",
      cam: { p: [-1.25, 1.7, 3.7], c: [-1.25, 1.7, -5] }, camM: { p: [0, 1.6, 4.9], c: [0, -0.95, -4.6] },
      calque: `<div class="s3d-panneau">${etiq(1, "L'accueil")}<h3>Mme Sabrina vous reçoit.</h3>
        <p>Esthéticienne diplômée. Chaque soin est un protocole : un diagnostic, des gestes précis, un suivi.</p>
        <div class="s3d-prix"><span>Horaires<b>Lundi au samedi, 10 h-17 h</b></span><span>Réservation<b>Acompte 5 100 F</b></span></div></div>`,
      points: [{ p: [0.95, 1.2, -1.75], label: "Lundi au samedi, 10 h-17 h", act: () => lien.moteur.aller(ST.rdv) },
               { p: [-1.1, 1.25, -1.8], label: "Sur rendez-vous", act: () => lien.moteur.aller(ST.rdv) }] });
    visage.forEach(({ s, i }, k) => {
      const x = XV(k), m = MUR(k), cx = x + m * 1.2;
      st({ id: "visage-" + k, nom: s.n, cote: "a-gauche",
        // la fiche à gauche : on vise à gauche de la porte, elle se pose à droite de l'écran (et l'inverse)
        // en face du caisson, un peu de biais : il se pose à droite de l'écran, la fiche à gauche ; au téléphone, droit
        // devant et visé plus bas, il monte dans le haut de l'écran, au-dessus de la fiche
        cam: { p: [cx - m * 1.1, 1.55, m * 0.4], c: [cx - m * 0.55, 1.42, -m * 2.4], via: k === 0 ? [{ p: [3.4, 1.65, 1.6], c: [9, 1.55, -0.6] }] : [] },
        // (27/11) un peu plus loin et visé plus haut : le caisson descend sous le bandeau des étapes
        camM: { p: [x + m * 1.2, 1.5, m * 0.3], c: [x + m * 1.2, 0.72, -m * 2.4], via: k === 0 ? [{ p: [3.4, 1.6, 2.2], c: [9, 1.5, -0.6] }] : [] },
        calque: `<div class="s3d-panneau">${etiq(stations.length, "Soins du visage")}<h3>${esc(s.n)}</h3><p>${esc(s.d)}</p>
          <div class="s3d-prix"><span>Tarif<b>${fcfa(s.p)}</b></span>${duree(s) ? `<span>Durée<b>${esc(duree(s))}</b></span>` : ""}</div>
          <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-reserver="${i}">Réserver ce soin</button>
          <button type="button" class="s3d-btn" data-voir="${i}">Le protocole</button></div></div>`,
        // le point, sous le caisson : à côté de la porte il tombait derrière la fiche
        points: [{ p: [cx, 0.62, -m * 2.3], label: "Le protocole", act: () => quand.voir(i) }] });
    });
    const classic = services.findIndex((s) => /classic/i.test(s.n));
    const etapes = classic >= 0 && services[classic].protocol ? services[classic].protocol.items : [];
    st({ id: "cabine", nom: "La cabine", cote: "a-gauche",
      cam: { p: [CX + 1.9, 2.25, 2.1], c: [CX - 0.1, 0.95, -0.9], via: [{ p: [XV(visage.length - 1) + 2.4, 1.7, 1.7], c: [CX, 1.2, -1] }] },
      camM: { p: [CX + 0.9, 3.0, 2.3], c: [CX - 0.1, -0.5, -0.9] },
      calque: `<div class="s3d-panneau">${etiq(stations.length, "La cabine")}<h3>La lampe passe : votre peau se lit.</h3>
        <ol class="s3d-etapes">${etapes.map((e) => `<li>${esc(Array.isArray(e) ? e[0] : e)}</li>`).join("")}</ol>
        ${classic >= 0 ? `<div class="s3d-actions"><button type="button" class="s3d-btn plein" data-reserver="${classic}">Réserver le ${esc(services[classic].n)}</button></div>` : ""}</div>` });
    st({ id: "corps", nom: "Soins du corps", cote: "a-gauche",
      cam: { p: [36.4, 1.95, 2.2], c: [35.4, 0.8, -1.2] }, camM: { p: [35.8, 2.3, 2.4], c: [35.6, -0.8, -1.2] },
      calque: `<div class="s3d-panneau">${etiq(stations.length, "Soins du corps")}<h3>Exfolier, modeler, apaiser.</h3><ul class="s3d-soins">${g("corps").map(ligneSoin).join("")}</ul></div>` });
    st({ id: "cheveux", nom: "Soins capillaires", cote: "a-droite",
      cam: { p: [39.2, 1.95, 2.2], c: [39.9, 0.85, -1.2] }, camM: { p: [39.8, 2.3, 2.4], c: [39.8, -0.8, -1.2] },
      calque: `<div class="s3d-panneau">${etiq(stations.length, "Soins capillaires")}<h3>Un cheveu fort commence au cuir chevelu.</h3><ul class="s3d-soins">${g("capillaires").map(ligneSoin).join("")}</ul></div>` });
    const vip = g("complet")[0];
    if (vip) st({ id: "vip", nom: "Le salon VIP", cote: "a-gauche",
      cam: { p: [44.6, 1.6, 2.0], c: [43.4, 0.8, -1.0] }, camM: { p: [43.6, 1.9, 2.3], c: [43.4, -0.7, -1.0] },
      calque: vip ? `<div class="s3d-panneau">${etiq(stations.length, "Le salon VIP")}<h3>${esc(vip.s.n)}</h3><p>${esc(vip.s.d)}</p>
        <div class="s3d-prix"><span>Tarif<b>${fcfa(vip.s.p)}</b></span></div>
        <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-reserver="${vip.i}">Réserver</button></div></div>` : "" });
    st({ id: "ina", nom: "INA Luxury", cote: "a-gauche",
      cam: { p: [47.6, 1.55, 1.6], c: [47.6, 1.5, -2.4] }, camM: { p: [47, 1.6, 2.4], c: [47, 1.3, -2.4] },
      calque: `<div class="s3d-panneau">${etiq(stations.length, "INA Luxury")}<h3>Prolonger le soin chez soi.</h3>
        <p>Les cosmétiques de la maison, choisis par Mme Sabrina. Touchez un produit pour le voir.</p>
        <div class="s3d-actions"><a class="s3d-btn plein" href="ina-luxury.html">Entrer dans la boutique</a></div></div>` });
    st({ id: "harmonisation", nom: "Cabinet privé", cote: "a-gauche",
      cam: { p: [46.4, 1.65, 0.1], c: [50.4, 1.6, 0] }, camM: { p: [45.6, 1.6, 0], c: [50.4, 0.1, 0] },
      calque: `<div class="s3d-panneau">${etiq(stations.length, "Cabinet privé")}<h3>Harmonisation faciale</h3>
        <p>Facial Balancing, Genesis Hollywood, Genesis Soft : chaque zone du visage et son tarif.</p>
        <div class="s3d-actions"><a class="s3d-btn plein" href="harmonisation-faciale.html">Pousser la porte</a></div></div>` });
    st({ id: "rdv", nom: "Rendez-vous", cote: "a-gauche",
      cam: { p: [47.6, 2.15, 1.6], c: [47.6, 0.8, 3.45] }, camM: { p: [47.6, 2.6, 1.2], c: [47.6, -0.6, 3.45] },
      calque: `<div class="s3d-panneau">${etiq(stations.length, "Le carnet")}<h3>Votre créneau vous attend.</h3>
        <p>Du lundi au samedi, de 10 h à 17 h, 24 h à l'avance. Un acompte de 5 100 F valide la réservation.</p>
        <div class="s3d-actions"><button type="button" class="s3d-btn plein" data-rdv>Choisir mon créneau</button></div></div>` });
    lien.ST = ST;

    let qualiteBasse = false, kActif = 0, tCabine = 0;
    return {
      stations, cliquables,
      surStation(k) {
        kActif = k;
        if (k >= ST.ina - 2) chargerINA();
        vapeur.visible = k === ST.cabine && !calme;
        if (k === ST.cabine && quand.son) quand.son("vapeur");
        if (k === ST.rdv && quand.son) quand.son("page");
      },
      qualite(q) {
        if (q !== "basse") return;
        qualiteBasse = true;
        // (26/11) les ombres restent : figées, elles ne coûtent presque plus rien, et les couper recompilait toutes les matières (la 3D gelée)
        scene.remove(pous);
        rais.forEach((x) => { x.visible = false; });
      },
      anime(t, dt) {
        let vivant = false;
        // la lampe descend quand on est dans la cabine (« la lampe qui passe »)
        const vise = kActif === ST.cabine ? 1 : 0;
        if (Math.abs(tCabine - vise) > 0.001) { tCabine += (vise - tCabine) * Math.min(1, dt * (calme ? 60 : 1.6)); vivant = true; }
        lampe.position.y = 2.15 - 0.85 * tCabine;
        lampe.position.x = CX - 0.3 - 0.25 * Math.sin(tCabine * Math.PI);
        lumLampe.intensity = 6 * tCabine;
        lentille.material.opacity = 0.6 + 0.4 * tCabine;
        if (vapeur.visible) { vapeur.userData.animer(dt * 2.2); vivant = true; }
        // le créneau s'illumine sur le carnet
        const c = creneau.material, cv = kActif === ST.rdv ? 0.55 + 0.25 * Math.sin(t * 2.4) : 0;
        if (Math.abs(c.opacity - cv) > 0.004 || cv) { c.opacity += (cv - c.opacity) * Math.min(1, dt * 4); vivant = true; }
        // la bougie vacille, les rais respirent
        // (on ne redessine en continu que là où quelque chose bouge vraiment : la batterie du téléphone compte)
        if (!calme && kActif === ST.vip) {
          bougie.intensity = 0.8 + Math.sin(t * 7.3) * 0.08 + Math.sin(t * 13.1) * 0.05;
          flamme.scale.y = 1.8 + Math.sin(t * 9) * 0.15;
          vivant = true;
        }
        if (!calme && !qualiteBasse && kActif <= ST.accueil) {
          rai.opacity = 0.28 + Math.sin(t * 0.5) * 0.06; pous.userData.animer(dt);
          vivant = true;
        }
        return vivant;
      },
    };
  };
}
