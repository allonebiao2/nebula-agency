"""Vague 2 (rendu) : à appliquer APRÈS l'enregistrement de la vague 1. Depuis monde/."""
from pathlib import Path

# 1 · moteur.js : l'étalonnage de film dans le tone mapping (toutes qualités), la passe « étalonnage » de la haute
#     ne garde que le vignettage et le grain (sinon double étalonnage)
p = Path("socle/moteur.js"); t = p.read_text(encoding="utf-8")
a = "export { THREE };"
b = """export { THREE };

/* L'ÉTALONNAGE DE FILM, DANS LE TONE MAPPING (vague 2, 2026-11-14). Avant : seule la qualité « haute » avait un
   étalonnage (une passe d'image en plus) ; le PC de Mongazi et tous les téléphones (« moyenne », « basse ») n'en
   avaient AUCUN. Ici : l'AgX de three.js (r180) recopié, avec un « look » posé là où Blender pose les siens, dans le
   domaine encodé d'AgX, après la courbe de contraste (ASC CDL : pente, puissance, saturation). Le « Punchy » de
   Blender (1,35 et 1,4) brûle le crème et sature le wax ; dosage plus doux, réglé sur les captures. Coût : quelques
   opérations par pixel dans chaque matière, aucune passe d'image. La passe de sortie de la haute l'utilise aussi. */
export const LOOK = { pente: [1.03, 1.0, 0.955], puissance: 1.16, saturation: 1.16 };
{
  const v = (a) => `vec3(${a.map(x => x.toFixed(4)).join(', ')})`;
  const C = THREE.ShaderChunk, vide = 'vec3 CustomToneMapping( vec3 color ) { return color; }';
  if (C.tonemapping_pars_fragment.includes(vide)) C.tonemapping_pars_fragment = C.tonemapping_pars_fragment.replace(vide, `
vec3 nebulaLook( vec3 val ) {
  float luma = dot( val, vec3( 0.2126, 0.7152, 0.0722 ) );
  val = pow( max( val * ${v(LOOK.pente)}, 0.0 ), vec3( ${LOOK.puissance.toFixed(4)} ) );
  return luma + ${LOOK.saturation.toFixed(4)} * ( val - luma );
}
vec3 CustomToneMapping( vec3 color ) {
  const mat3 AgXInsetMatrix = mat3(
    vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
    vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
    vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 ) );
  const mat3 AgXOutsetMatrix = mat3(
    vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
    vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
    vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 ) );
  const float AgxMinEv = - 12.47393; const float AgxMaxEv = 4.026069;
  color *= toneMappingExposure;
  color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
  color = AgXInsetMatrix * color;
  color = max( color, 1e-10 ); color = log2( color );
  color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
  color = clamp( color, 0.0, 1.0 );
  color = agxDefaultContrastApprox( color );
  color = nebulaLook( color );
  color = AgXOutsetMatrix * color;
  color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
  color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
  return clamp( color, 0.0, 1.0 );
}`);
}"""
assert a in t, "export"; t = t.replace(a, b, 1)
a = "  renderer.toneMapping = THREE.AgXToneMapping;"
b = "  /* `?sans-look` : l'AgX nu d'avant (pour comparer) */\n  renderer.toneMapping = new URLSearchParams(location.search).has('sans-look') ? THREE.AgXToneMapping : THREE.CustomToneMapping;"
assert a in t, "tm"; t = t.replace(a, b, 1)
a = """        float l = dot(col, vec3(0.2126, 0.7152, 0.0722));
        col = mix(vec3(l), col, 1.06);
        col = (col - 0.5) * 1.05 + 0.5;
        col *= vec3(1.02, 1.0, 0.975);
        vec2 d"""
b = """        /* le contraste, la saturation et la chaleur sont DANS le tone mapping (LOOK) : ici, vignettage et grain */
        vec2 d"""
assert a in t, "etal"; t = t.replace(a, b, 1)
p.write_text(t, encoding="utf-8")
print("moteur ok")

# 2 · moteur.js : le vignettage sans passe d'image pour « moyenne » et « basse » (un dégradé posé par le navigateur
#     au-dessus du canevas, sous l'interface ; AUCUN mix-blend-mode : un mélange plein écran ruine un téléphone)
p = Path("socle/moteur.js"); t = p.read_text(encoding="utf-8")
a = "  if (qualite.halo) monterHalo();"
b = """  if (qualite.halo) monterHalo();
  if (!qualite.cinema) {
    const vignette = document.createElement('div'); vignette.className = 'vignette-film'; vignette.setAttribute('aria-hidden', 'true');
    vignette.style.cssText = 'position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse 75% 70% at 50% 46%, rgba(0,0,0,0) 58%, rgba(10,6,3,.28) 100%)';
    conteneur.appendChild(vignette);
  }"""
assert a in t, "vig"; t = t.replace(a, b, 1)
p.write_text(t, encoding="utf-8")
print("vignette ok")

# 3 · lieu.js : les faisceaux qu'on voit, et la poussière dedans (le soir surtout)
p = Path("lieux/hillary-m-styl/lieu.js"); t = p.read_text(encoding="utf-8")
a = "import { creerPersoVideo } from '../../socle/perso-video.js';"
b = a + "\nimport { creerFaisceaux } from '../../socle/faisceaux.js';"
assert a in t, "import"; t = t.replace(a, b, 1)
a = """    faisceauxCreations.push({ l: faisceau, base: faisceau.intensity });
    if (!params.has('direct')) faisceau.intensity = 0;
  }
}"""
b = """    faisceauxCreations.push({ l: faisceau, base: faisceau.intensity });
    if (!params.has('direct')) faisceau.intensity = 0;
  }
}
/* LES FAISCEAUX QU'ON VOIT (vague 2, 2026-11-14, Mongazi : « le soir, des spots qui découpent les robes dans la
   pénombre, la poussière qui danse dans les faisceaux ») : le cône de chaque projecteur des créations, et des
   grains de poussière qui dérivent dedans (aucun en « basse »). Ils suivent l'allumage un à un et l'heure (un
   souffle le jour, pleinement le soir). */
const faisceauxVus = creerFaisceaux({ moteur, projecteurs: faisceauxCreations.map(f => ({ lumiere: f.l, base: f.base, sol: 0 })),
  nuit: () => nuitCuite, densite: q.nom === 'haute' ? 70 : q.nom === 'moyenne' ? 36 : 0 });"""
assert a in t, "faisceaux"; t = t.replace(a, b, 1)
a = "window.__monde = { persoVideos, "
b = "window.__monde = { faisceauxVus, persoVideos, "
assert a in t, "monde"; t = t.replace(a, b, 1)
p.write_text(t, encoding="utf-8")
print("faisceaux ok")

# 4 · lieu.js : la profondeur de l'air (une brume très légère : les choses lointaines s'adoucissent, comme sur une
#     photo). FogExp2 : quasi rien à 4 m (1 %), un voile à 16 m (≈ 10 %) ; chaude le jour, sombre et chaude le soir.
p = Path("lieux/hillary-m-styl/lieu.js"); t = p.read_text(encoding="utf-8")
a = "const faisceauxVus = creerFaisceaux("
b = """const brume = new THREE.FogExp2(0xd8c9b2, 0.02); scene.fog = brume;
{
  const jour = new THREE.Color(0xd8c9b2), soir = new THREE.Color(0x1c130d);
  moteur.chaqueImage(() => { brume.color.copy(jour).lerp(soir, nuitCuite); brume.density = melanger(0.018, 0.026, nuitCuite); });
}
const faisceauxVus = creerFaisceaux("""
assert a in t, "brume"; t = t.replace(a, b, 1)
p.write_text(t, encoding="utf-8")
print("brume ok")
