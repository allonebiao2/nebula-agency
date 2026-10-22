/**
 * La 3D du film (Three.js par React Three Fiber, rendue image par image par Remotion).
 * ⛔ Aucun `useFrame` : tout bouge par les props, calculées depuis `useCurrentFrame()` (sinon l'image tremble).
 * Les textures sont dessinées ici (canvas) : aucune image venue d'ailleurs, aucune licence.
 */
import React, {useMemo} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useVideoConfig} from 'remotion';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {CIRES, PAPIERS, SCEAUX, type Cire, type Papier, type Sceau} from './donnees';

type V3 = [number, number, number];

/** Le réglage commun : tons ACES, environnement doux pour les reflets, caméra pilotée par props. */
const Regie: React.FC<{camera: V3; vise: V3; fov: number; expo: number; ciel: number}> = ({camera, vise, fov, expo, ciel}) => {
	const {gl, scene, camera: cam} = useThree();
	useMemo(() => {
		gl.toneMapping = THREE.ACESFilmicToneMapping;
		gl.outputColorSpace = THREE.SRGBColorSpace;
				const pm = new THREE.PMREMGenerator(gl);
		scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
	}, [gl, scene]);
	gl.toneMappingExposure = expo;
	scene.environmentIntensity = ciel;
	cam.position.set(...camera);
	(cam as THREE.PerspectiveCamera).fov = fov;
	(cam as THREE.PerspectiveCamera).updateProjectionMatrix();
	cam.lookAt(...vise);
	return null;
};

export const Scene3D: React.FC<{camera: V3; vise?: V3; fov?: number; expo?: number; ciel?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
	camera,
	vise = [0, 0, 0],
	fov = 30,
	expo = 0.9,
	ciel = 0.25,
	children,
	style,
}) => {
	const {width, height} = useVideoConfig();
	return (
		<ThreeCanvas width={width} height={height} shadows gl={{alpha: true, antialias: true, preserveDrawingBuffer: true}} style={{position: 'absolute', inset: 0, ...style}}>
			<Regie camera={camera} vise={vise} fov={fov} expo={expo} ciel={ciel} />
			{children}
		</ThreeCanvas>
	);
};

/**
 * Les lumières du film : une clé chaude (la bougie, la lampe), un contre-jour froid (la nuit), presque pas d'ambiance.
 * `ombre` 0→1 : la force des ombres portées. Les éclats qui volent haut faisaient des taches grises sur l'enveloppe.
 */
export const Lumieres: React.FC<{cle?: number; contre?: number; cleCouleur?: string; position?: V3; ombre?: number}> = ({
	cle = 22,
	contre = 3.5,
	cleCouleur = '#ffd8a8',
	position = [2.0, 3.0, 1.4],
	ombre = 1,
}) => (
	<>
		<ambientLight intensity={0.05} />
		<spotLight position={position} angle={0.5} penumbra={0.9} intensity={cle} decay={1.6} color={cleCouleur} castShadow shadow-mapSize={[2048, 2048]} shadow-bias={-0.0004} shadow-intensity={ombre} />
		<pointLight position={[-2.2, 0.9, -1.6]} intensity={contre} decay={1.6} color="#8fa6ff" />
	</>
);

/* ── Les textures dessinées ── */
const toile = (w: number, h: number, dessin: (g: CanvasRenderingContext2D) => void, srgb = true) => {
	const c = document.createElement('canvas');
	c.width = w;
	c.height = h;
	dessin(c.getContext('2d')!);
	const t = new THREE.CanvasTexture(c);
	if (srgb) t.colorSpace = THREE.SRGBColorSpace;
	t.anisotropy = 8;
	t.needsUpdate = true;
	return t;
};

/** Un papier : sa teinte, ses fibres, un léger nuage. */
export const texturePapier = (papier: Papier, graine = 7) =>
	toile(1024, 640, (g) => {
		const {papier: a, papier2: b} = PAPIERS[papier];
		const grad = g.createLinearGradient(0, 0, 1024, 640);
		grad.addColorStop(0, a);
		grad.addColorStop(1, b);
		g.fillStyle = grad;
		g.fillRect(0, 0, 1024, 640);
		let s = graine;
		const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
		for (let i = 0; i < 2600; i++) {
			g.strokeStyle = `rgba(${papier === 'nuit' ? '255,255,255' : '60,40,30'},${0.02 + rnd() * 0.05})`;
			g.lineWidth = 0.6 + rnd();
			const x = rnd() * 1024, y = rnd() * 640, l = 4 + rnd() * 16, a2 = rnd() * Math.PI;
			g.beginPath();
			g.moveTo(x, y);
			g.lineTo(x + Math.cos(a2) * l, y + Math.sin(a2) * l);
			g.stroke();
		}
	});

/** La doublure du rabat : un damas d'or sur la cire (les invitations des vidéos de Mongazi). */
const textureDoublure = (cire: Cire) =>
	toile(512, 512, (g) => {
		const c = CIRES[cire];
		g.fillStyle = c.fonce;
		g.fillRect(0, 0, 512, 512);
		g.strokeStyle = 'rgba(224,194,102,.55)';
		g.lineWidth = 2;
		for (let y = -1; y < 9; y++)
			for (let x = -1; x < 9; x++) {
				const cx = x * 64 + (y % 2 ? 32 : 0), cy = y * 64;
				g.beginPath();
				g.ellipse(cx, cy, 14, 22, 0, 0, Math.PI * 2);
				g.moveTo(cx - 22, cy);
				g.quadraticCurveTo(cx, cy - 30, cx + 22, cy);
				g.quadraticCurveTo(cx, cy + 30, cx - 22, cy);
				g.stroke();
			}
	});

/** Le motif du sceau, en hauteur (blanc = relief), lissé : il deviendra de la vraie géométrie. */
const hauteurSceau = (sceau: Sceau, initiale: string) => {
	const c = document.createElement('canvas');
	c.width = c.height = 512;
	const g = c.getContext('2d')!;
	g.fillStyle = '#000';
	g.fillRect(0, 0, 512, 512);
	g.filter = 'blur(5px)';
	g.strokeStyle = g.fillStyle = '#fff';
	g.lineWidth = 34;
	g.beginPath();
	g.arc(256, 256, 226, 0, Math.PI * 2);
	g.stroke();
	g.lineWidth = 6;
	g.setLineDash([16, 12]);
	g.beginPath();
	g.arc(256, 256, 196, 0, Math.PI * 2);
	g.stroke();
	g.setLineDash([]);
	if (sceau === 'marque') {
		/* la marque : le cachet aux trois points (`malettre/logo/cachet.svg`) */
		g.setLineDash([]);
		g.lineWidth = 14;
		g.beginPath();
		g.arc(256, 256, 190, 0, Math.PI * 2);
		g.stroke();
		for (const dx of [-104, 0, 104]) {
			g.beginPath();
			g.arc(256 + dx, 256, 36, 0, Math.PI * 2);
			g.fill();
		}
	} else if (sceau === 'initiale') {
		g.font = '300px Georgia, serif';
		g.textAlign = 'center';
		g.textBaseline = 'middle';
		g.fillText(initiale, 256, 270);
	} else {
		g.translate(256, 256);
		g.scale(11, 11);
		g.translate(-12, -12);
		g.lineWidth = 1.7;
		g.lineJoin = g.lineCap = 'round';
		for (const d of SCEAUX[sceau]) g.stroke(new Path2D(d));
	}
	return g.getImageData(0, 0, 512, 512).data;
};

/** Le même motif, en texture : le bosselage de la face des éclats (le relief vrai ne survit pas à la cassure). */
const textureSceau = (sceau: Sceau, initiale: string) => {
	const h = hauteurSceau(sceau, initiale);
	return toile(
		512,
		512,
		(g) => {
			const img = g.createImageData(512, 512);
			img.data.set(h);
			g.putImageData(img, 0, 0);
		},
		false,
	);
};

/** Le rayon du bord du cachet à l'angle a : la même bosse que `corpsCachet` (la cire a coulé avant le sceau). */
const rayonBord = (a: number) => 1 + 0.045 * Math.sin(a * 5 + 0.7) + 0.03 * Math.sin(a * 11 + 2.1) + 0.02 * Math.sin(a * 17);

/** Le corps du cachet : une goutte de cire pressée, bord bombé et irrégulier (la cire a coulé avant le sceau). */
const corpsCachet = () => {
	const p: THREE.Vector2[] = [new THREE.Vector2(0, 0.17), new THREE.Vector2(0.62, 0.17), new THREE.Vector2(0.7, 0.2), new THREE.Vector2(0.78, 0.235)];
	for (let i = 0; i <= 12; i++) {
		const a = (i / 12) * Math.PI * 0.5;
		p.push(new THREE.Vector2(0.78 + 0.22 * Math.sin(a), 0.235 * Math.cos(a)));
	}
	const geo = new THREE.LatheGeometry(p.reverse(), 180);
	const pos = geo.attributes.position;
	for (let i = 0; i < pos.count; i++) {
		const x = pos.getX(i), z = pos.getZ(i);
		const r = Math.hypot(x, z);
		if (r < 0.6) continue;
		const a = Math.atan2(z, x);
		const bosse = 1 + 0.045 * Math.sin(a * 5 + 0.7) + 0.03 * Math.sin(a * 11 + 2.1) + 0.02 * Math.sin(a * 17);
		const k = (r - 0.6) / 0.4;
		pos.setX(i, x * (1 + (bosse - 1) * k));
		pos.setZ(i, z * (1 + (bosse - 1) * k));
	}
	geo.computeVertexNormals();
	return geo;
};

/** Le plateau du sceau : une grille fine soulevée par le motif, puis éclairée pour de vrai (normales recalculées). */
const plateauCachet = (sceau: Sceau, initiale: string) => {
	const h = hauteurSceau(sceau, initiale);
	const n = 220;
	const geo = new THREE.PlaneGeometry(1.26, 1.26, n, n);
	geo.rotateX(-Math.PI / 2);
	const pos = geo.attributes.position;
	for (let i = 0; i < pos.count; i++) {
		const x = pos.getX(i), z = pos.getZ(i);
		const u = Math.min(511, Math.max(0, Math.round((x / 1.26 + 0.5) * 511)));
		const v = Math.min(511, Math.max(0, Math.round((z / 1.26 + 0.5) * 511)));
		const val = h[(v * 512 + u) * 4] / 255;
		const r = Math.hypot(x, z);
		const bord = r > 0.62 ? 0 : 1;
		pos.setY(i, 0.17 + val * 0.035 * bord - (r > 0.62 ? 0.02 : 0));
	}
	geo.computeVertexNormals();
	return geo;
};

const masqueRond = () =>
	toile(
		256,
		256,
		(g) => {
			g.fillStyle = '#000';
			g.fillRect(0, 0, 256, 256);
			g.fillStyle = '#fff';
			g.beginPath();
			g.arc(128, 128, 126, 0, Math.PI * 2);
			g.fill();
		},
		false,
	);

/**
 * Les trois éclats (angles vifs, comme ceux du produit), PLEINS : chaque morceau est un secteur du cachet extrudé, aux
 * arêtes arrondies (la cire est tendre), et sa tranche se voit quand il tourne. Les lignes de fracture partent d'un
 * même point décentré et ondulent (une cire casse, elle ne se coupe pas au couteau) ; deux morceaux voisins partagent
 * la même ligne, ils se touchent exactement avant de partir.
 * ⚠️ Avant (2026-10-22, planche du MP4) : chaque triangle de la coque allait au morceau de son angle. Les morceaux
 * étaient creux, vus par leur dessous plat, et leurs bords faisaient des dents de peigne.
 */
const PLANS_ECLATS: [number, number][] = [
	[90, 210],
	[210, 330],
	[330, 450],
];
const JONCTION: [number, number] = [0.05, -0.04];
const fracture = (d: number) => {
	const pts: [number, number][] = [];
	const n = 8;
	for (let i = 0; i <= n; i++) {
		const f = i / n;
		const ang = d + 9 * Math.sin(f * 11 + d) + 5 * Math.sin(f * 23 + d * 2) + (i > 0 && i < n ? (i % 2 ? 3 : -3) : 0);
		const a = (ang * Math.PI) / 180;
		const rb = rayonBord(a) - 0.035;
		pts.push(i === 0 ? JONCTION : [Math.cos(a) * rb * f, Math.sin(a) * rb * f]);
	}
	return pts;
};
const eclatsPleins = () =>
	PLANS_ECLATS.map(([d, f]) => {
		const aller = fracture(d);
		const retour = fracture(f).reverse();
		const a0 = Math.atan2(aller[aller.length - 1][1], aller[aller.length - 1][0]);
		let a1 = Math.atan2(retour[0][1], retour[0][0]);
		while (a1 <= a0) a1 += Math.PI * 2;
		const contour: [number, number][] = [...aller];
		const pas = Math.max(8, Math.round((a1 - a0) / 0.03));
		for (let i = 1; i < pas; i++) {
			const a = a0 + ((a1 - a0) * i) / pas;
			const rb = rayonBord(a) - 0.035;
			contour.push([Math.cos(a) * rb, Math.sin(a) * rb]);
		}
		contour.push(...retour);
		/* la forme : (x, -z) du plan du cachet, extrudée, puis couchée (l'épaisseur monte vers +y) */
		const forme = new THREE.Shape(contour.map(([x, z]) => new THREE.Vector2(x, -z)));
		const geo = new THREE.ExtrudeGeometry(forme, {depth: 0.15, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.035, bevelSegments: 4, curveSegments: 4});
		geo.rotateX(-Math.PI / 2);
		geo.translate(0, 0.035, 0);
		geo.computeVertexNormals();
		return geo;
	});

/**
 * LE CACHET. `lueur` 0→1 l'allume (minuit) ; `ecrase` 0→1 le fait naître sous le sceau (la cire s'étale) ;
 * `eclat` 0→1 le brise en trois et projette les morceaux vers la caméra.
 */
export const Cachet3D: React.FC<{
	cire?: Cire;
	sceau?: Sceau;
	initiale?: string;
	lueur?: number;
	ecrase?: number;
	eclat?: number;
	position?: V3;
	rotation?: V3;
	echelle?: number;
	brillance?: number;
}> = ({cire = 'bordeaux', sceau = 'coeur', initiale = 'K', lueur = 0, ecrase = 1, eclat = 0, position = [0, 0, 0], rotation = [0, 0, 0], echelle = 1, brillance = 0.55}) => {
	const corps = useMemo(corpsCachet, []);
	const plateau = useMemo(() => plateauCachet(sceau, initiale), [sceau, initiale]);
	const masque = useMemo(masqueRond, []);
	const c = CIRES[cire];
	const morceauxPleins = useMemo(eclatsPleins, []);
	const bosselage = useMemo(() => {
		const tx = textureSceau(sceau, initiale);
		tx.repeat.set(1 / 1.26, 1 / 1.26);
		tx.offset.set(0.5, 0.5);
		return tx;
	}, [sceau, initiale]);
	/* l'étalement : la cire naît petite et haute, puis s'écrase et s'étale sous le sceau */
	const sx = 0.55 + 0.45 * ecrase, sy = 1.6 - 0.6 * ecrase;
	if (eclat > 0) {
		/* brisé : trois morceaux pleins, projetés vers la caméra en tournant */
		return (
			<group position={position} rotation={rotation} scale={echelle}>
				{[0, 1, 2].map((k) => {
					const milieu = ((PLANS_ECLATS[k][0] + PLANS_ECLATS[k][1]) / 2) * (Math.PI / 180);
					const e = eclat;
					const dx = Math.cos(milieu) * e * 2.6, dz = Math.sin(milieu) * e * 2.6;
					return (
						<group key={k} position={[dx, e * 1.6 + e * e * 2.2, dz]} rotation={[e * (k - 1) * 2.4, e * 3 * (k + 1), e * (1 - k) * 1.8]}>
							<mesh geometry={morceauxPleins[k]} castShadow receiveShadow>
								{/* la face (et le dessous) : la cire lustrée, le sceau en bosselage ; la tranche : la cire mate */}
								<meshPhysicalMaterial attach="material-0" color={c.cire} roughness={0.4} clearcoat={brillance} clearcoatRoughness={0.22} sheen={0.3} sheenColor={c.lumiere} emissive={c.lumiere} emissiveIntensity={lueur * 0.6} bumpMap={bosselage} bumpScale={3} />
								<meshPhysicalMaterial attach="material-1" color={c.cire} roughness={0.62} sheen={0.45} sheenColor={c.lumiere} emissive={c.lumiere} emissiveIntensity={lueur * 0.4} />
							</mesh>
						</group>
					);
				})}
			</group>
		);
	}
	return (
		<group position={position} rotation={rotation} scale={echelle}>
			<group scale={[sx, sy, sx]}>
				<mesh geometry={corps} castShadow receiveShadow>
					<meshPhysicalMaterial color={c.cire} roughness={0.42} clearcoat={brillance} clearcoatRoughness={0.22} sheen={0.3} sheenColor={c.lumiere} emissive={c.lumiere} emissiveIntensity={lueur * 0.55} side={THREE.DoubleSide} />
				</mesh>
				<mesh geometry={plateau} castShadow receiveShadow>
					<meshPhysicalMaterial color={c.cire} roughness={0.38} clearcoat={brillance} clearcoatRoughness={0.2} sheen={0.3} sheenColor={c.lumiere} emissive={c.lumiere} emissiveIntensity={lueur * 0.75} alphaMap={masque} alphaTest={0.5} side={THREE.DoubleSide} />
				</mesh>
			</group>
		</group>
	);
};

/** Une lueur : un disque au dégradé radial, en mélange additif (la « bloom » sans post-traitement). */
const textureHalo = () =>
	toile(256, 256, (g) => {
		const r = g.createRadialGradient(128, 128, 0, 128, 128, 128);
		r.addColorStop(0, 'rgba(255,255,255,1)');
		r.addColorStop(0.25, 'rgba(255,255,255,.45)');
		r.addColorStop(1, 'rgba(255,255,255,0)');
		g.fillStyle = r;
		g.fillRect(0, 0, 256, 256);
	});

export const Halo3D: React.FC<{position: V3; taille: number; couleur: string; force: number}> = ({position, taille, couleur, force}) => {
	const tex = useMemo(textureHalo, []);
	if (force <= 0.001) return null;
	return (
		<sprite position={position} scale={[taille, taille, 1]}>
			<spriteMaterial map={tex} color={couleur} transparent opacity={force} blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
		</sprite>
	);
};

/** Des étincelles qui jaillissent d'un point (déterministes : graine + temps). */
export const Etincelles3D: React.FC<{t: number; origine: V3; n?: number; couleur?: string; vitesse?: number}> = ({t, origine, n = 70, couleur = '#ffd89a', vitesse = 3.2}) => {
	const tex = useMemo(textureHalo, []);
	if (t <= 0 || t > 2.2) return null;
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const a = (i * 137.5 * Math.PI) / 180;
				const el = ((i * 61) % 100) / 100;
				const v = vitesse * (0.4 + ((i * 37) % 100) / 100);
				const x = origine[0] + Math.cos(a) * Math.cos(el) * v * t;
				const z = origine[2] + Math.sin(a) * Math.cos(el) * v * t;
				const y = origine[1] + Math.sin(el * 1.4) * v * t - 2.4 * t * t;
				const vie = Math.max(0, 1 - t / (1 + ((i * 13) % 10) / 10));
				return (
					<sprite key={i} position={[x, y, z]} scale={[0.07 * vie + 0.02, 0.07 * vie + 0.02, 1]}>
						<spriteMaterial map={tex} color={couleur} transparent opacity={vie} blending={THREE.AdditiveBlending} depthWrite={false} toneMapped={false} />
					</sprite>
				);
			})}
		</>
	);
};

/**
 * L'ENVELOPPE. Le papier, les plis du dos, le rabat articulé (`ouvre` 0→1) qui découvre sa doublure damassée,
 * la carte qui sort (`sort` 0→1). Le cachet se pose sur la pointe du rabat (`cachet`).
 */
export const Enveloppe3D: React.FC<{
	papier?: Papier;
	cire?: Cire;
	ouvre?: number;
	sort?: number;
	position?: V3;
	rotation?: V3;
	echelle?: number;
	children?: React.ReactNode;
	carte?: THREE.Texture | null;
}> = ({papier = 'creme', cire = 'bordeaux', ouvre = 0, sort = 0, position = [0, 0, 0], rotation = [0, 0, 0], echelle = 1, children, carte}) => {
	const tex = useMemo(() => texturePapier(papier), [papier]);
	const doublure = useMemo(() => textureDoublure(cire), [cire]);
	const L = 2.6, H = 1.6;
	const rabat = useMemo(() => {
		const s = new THREE.Shape();
		s.moveTo(-L / 2, 0);
		s.lineTo(L / 2, 0);
		s.lineTo(0, -H * 0.54);
		s.closePath();
		return new THREE.ShapeGeometry(s);
	}, []);
	/* la poche : tout le dos, sauf l'échancrure en V que le rabat vient couvrir */
	const poche = useMemo(() => {
		const s = new THREE.Shape();
		s.moveTo(-L / 2, -H / 2);
		s.lineTo(L / 2, -H / 2);
		s.lineTo(L / 2, H / 2);
		s.lineTo(0, H / 2 - H * 0.5);
		s.lineTo(-L / 2, H / 2);
		s.closePath();
		const g = new THREE.ShapeGeometry(s);
		const uv = g.attributes.uv, pos = g.attributes.position;
		for (let i = 0; i < pos.count; i++) uv.setXY(i, pos.getX(i) / L + 0.5, pos.getY(i) / H + 0.5);
		return g;
	}, []);
	/* les plis des côtés et du bas, tracés à peine */
	const plis = useMemo(() => {
		const pts = [new THREE.Vector3(-L / 2, -H / 2, 0), new THREE.Vector3(0, -0.02, 0), new THREE.Vector3(L / 2, -H / 2, 0)];
		return new THREE.BufferGeometry().setFromPoints(pts);
	}, []);
	const angle = -Math.PI * 0.94 * ouvre;
	return (
		<group position={position} rotation={rotation} scale={echelle}>
			{/* le fond (l'intérieur de la face avant), un peu plus sombre : c'est l'intérieur */}
			<mesh position={[0, 0, -0.012]} castShadow receiveShadow>
				<boxGeometry args={[L, H, 0.006]} />
				<meshStandardMaterial map={tex} roughness={0.9} color="#d8cbb4" />
			</mesh>
			{/* la carte, ENTRE le fond et la poche : elle sort par le haut */}
			<mesh position={[0, -0.04 + sort * 1.3, -0.005]} castShadow receiveShadow>
				<boxGeometry args={[L * 0.9, H * 0.86, 0.004]} />
				<meshStandardMaterial map={carte ?? tex} roughness={0.85} color={carte ? '#ffffff' : '#fbf7ef'} />
			</mesh>
			{/* la poche, échancrée en V */}
			<mesh geometry={poche} position={[0, 0, 0.002]} castShadow receiveShadow>
				<meshStandardMaterial map={tex} roughness={0.9} side={THREE.DoubleSide} />
			</mesh>
			<lineSegments geometry={plis} position={[0, 0, 0.004]}>
				<lineBasicMaterial color="#b9a88c" transparent opacity={0.55} />
			</lineSegments>
			{/* le rabat, articulé sur le bord haut ; sa doublure se découvre en s'ouvrant */}
			<group position={[0, H / 2, 0.006]} rotation={[angle, 0, 0]}>
				<mesh geometry={rabat} castShadow>
					<meshStandardMaterial map={tex} roughness={0.9} side={THREE.FrontSide} />
				</mesh>
				<mesh geometry={rabat} position={[0, 0, -0.002]} rotation={[0, Math.PI, 0]} scale={[-1, 1, 1]}>
					<meshStandardMaterial map={doublure} roughness={0.6} metalness={0.15} side={THREE.FrontSide} />
				</mesh>
				<group position={[0, -H * 0.5 + 0.02, 0.012]}>{children}</group>
			</group>
		</group>
	);
};

/** Deux alliances d'or entrelacées (la demande). */
export const Alliances3D: React.FC<{tour: number; position?: V3; echelle?: number}> = ({tour, position = [0, 0, 0], echelle = 1}) => (
	<group position={position} scale={echelle} rotation={[0.35, tour, 0.15]}>
		<mesh rotation={[0.3, 0, 0.6]} castShadow>
			<torusGeometry args={[0.5, 0.075, 64, 200]} />
			<meshPhysicalMaterial color="#e2b65a" metalness={1} roughness={0.16} clearcoat={0.4} />
		</mesh>
		<mesh position={[0.42, 0.02, 0]} rotation={[1.2, 0.4, 0]} castShadow>
			<torusGeometry args={[0.43, 0.065, 64, 200]} />
			<meshPhysicalMaterial color="#f0cf86" metalness={1} roughness={0.14} clearcoat={0.4} />
		</mesh>
	</group>
);

/** Un plan de sol qui ne prend que l'ombre (le reste est le fond 2D, derrière). */
export const SolOmbre: React.FC<{y?: number; force?: number}> = ({y = 0, force = 0.45}) => (
	<mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, y - 0.001, 0]} receiveShadow>
		<planeGeometry args={[30, 30]} />
		<shadowMaterial opacity={force} />
	</mesh>
);
