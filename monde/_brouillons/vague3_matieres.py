"""Vague 3 (la vie et les matières) : brouillon à appliquer APRÈS la vague 2. Depuis monde/.
Des matières vraies, calculées sur place (aucun téléchargement, règle 3G) :
- le velours a un vrai reflet de velours (sheen de MeshPhysicalMaterial) ;
- le laiton a une patine (rugosité qui varie, traces de doigts) ;
- le plâtre et le crème ont un grain d'enduit (relief) ;
- le sol poli a des zones plus mates (passage, cire) : un reflet qui n'est pas un miroir parfait ;
- le chêne a le relief de ses veines. """
from pathlib import Path
p = Path("socle/matieres.js"); t = p.read_text(encoding="utf-8")

a = "export const MATIERES = {"
b = """/* LES SURFACES VRAIES (vague 3, 2026-11-14) : un bruit doux calculé sur place, partagé (une texture par usage),
   qui sert de relief ou de rugosité. Le réel vient de l'imperfection : aucune grande surface parfaitement unie. */
const surfaces = new Map();
function bruitDoux(nom, { taille = 256, echelles = [32, 12, 4], forces = [0.55, 0.3, 0.15], base = 0.5, contraste = 1, graineN = 3 } = {}) {
  if (surfaces.has(nom)) return surfaces.get(nom);
  const c = document.createElement('canvas'); c.width = c.height = taille; const g = c.getContext('2d');
  const img = g.createImageData(taille, taille), r = graine(graineN);
  /* des couches de bruit de valeur lissé, raccordées (la texture se répète sans couture) */
  const couches = echelles.map((e) => { const n = Math.max(2, Math.round(taille / e)); return { n, v: Array.from({ length: n * n }, () => r()) }; });
  const lisse = (x) => x * x * (3 - 2 * x);
  for (let y = 0; y < taille; y++) for (let x = 0; x < taille; x++) {
    let v = 0;
    couches.forEach(({ n, v: tab }, k) => {
      const fx = x / taille * n, fy = y / taille * n, ix = Math.floor(fx), iy = Math.floor(fy), tx = lisse(fx - ix), ty = lisse(fy - iy);
      const at = (i, j) => tab[((j % n) * n + (i % n))];
      const a = at(ix, iy) + (at(ix + 1, iy) - at(ix, iy)) * tx, b = at(ix, iy + 1) + (at(ix + 1, iy + 1) - at(ix, iy + 1)) * tx;
      v += (a + (b - a) * ty - 0.5) * forces[k];
    });
    const o = Math.max(0, Math.min(255, Math.round((base + v * contraste) * 255))), i = (y * taille + x) * 4;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = o; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const tx = new THREE.CanvasTexture(c); tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.colorSpace = THREE.NoColorSpace;
  surfaces.set(nom, tx); return tx;
}
const repete = (tx, x, y) => { const c = tx.clone(); c.repeat.set(x, y); c.needsUpdate = true; return c; };

export const MATIERES = {"""
assert a in t, "MATIERES"; t = t.replace(a, b, 1)

remp = {
  "  creme: () => new THREE.MeshStandardMaterial({ color: 0xf4efe6, roughness: 0.92 }),":
  "  creme: () => new THREE.MeshStandardMaterial({ color: 0xf4efe6, roughness: 0.92, bumpMap: repete(bruitDoux('enduit'), 3, 3), bumpScale: 0.6 }),",
  "  platre: () => new THREE.MeshStandardMaterial({ color: 0xf7f3ec, roughness: 0.96 }),":
  "  platre: () => new THREE.MeshStandardMaterial({ color: 0xf7f3ec, roughness: 0.96, bumpMap: repete(bruitDoux('enduit'), 4, 4), bumpScale: 0.7 }),",
  "  laiton: () => new THREE.MeshStandardMaterial({ color: 0xc9a254, roughness: 0.3, metalness: 1 }),":
  "  /* le laiton patiné : une rugosité qui varie (traces, poli inégal), jamais un chrome parfait */\n"
  "  laiton: () => new THREE.MeshStandardMaterial({ color: 0xc9a254, roughness: 1, roughnessMap: repete(bruitDoux('patine', { base: 0.34, contraste: 0.9, echelles: [24, 8, 3] }), 2, 2), metalness: 1 }),",
  "  velours: (couleur = 0xb0105f) => new THREE.MeshStandardMaterial({ color: couleur, roughness: 0.95 }),":
  "  /* le velours boit la lumière de face et la renvoie sur ses bords (le « sheen ») : c'est ce qui le fait velours */\n"
  "  velours: (couleur = 0xb0105f) => new THREE.MeshPhysicalMaterial({ color: couleur, roughness: 0.9, sheen: 1, sheenRoughness: 0.42,\n"
  "    sheenColor: new THREE.Color(couleur).lerp(new THREE.Color(0xffe0ee), 0.45), bumpMap: repete(bruitDoux('enduit'), 6, 6), bumpScale: 0.25 }),",
}
for a, b in remp.items():
    assert a in t, a[:40]; t = t.replace(a, b, 1)

# le chêne : le relief de ses veines (la même image en relief)
a = "    return new THREE.MeshStandardMaterial({ map: t, roughness: 0.55 });\n  },\n  laiton"
b = "    return new THREE.MeshStandardMaterial({ map: t, roughness: 0.55, bumpMap: t, bumpScale: 0.8 });\n  },\n  laiton"
assert a in t, "chene"; t = t.replace(a, b, 1)
# le sol poli : des zones plus mates (passage, cire), un reflet qui n'est pas un miroir
a = "    return new THREE.MeshStandardMaterial({ map: t, roughness: 0.16, metalness: 0, envMapIntensity: 1.3 });"
b = ("    /* la rugosité varie (passage, cire inégale) : le reflet se trouble par endroits, comme un vrai sol poli */\n"
     "    return new THREE.MeshStandardMaterial({ map: t, roughness: 1, roughnessMap: repete(bruitDoux('cire', { base: 0.17, contraste: 0.32, echelles: [64, 20, 6] }), 3, 2), metalness: 0, envMapIntensity: 1.3 });")
assert a in t, "sol"; t = t.replace(a, b, 1)
p.write_text(t, encoding="utf-8")
print("matieres ok")
