"""LE MONDE · mesurer la marche d'une visiteuse : ses pieds glissent-ils ?

    python monde/_servir.py --sans-construire     (dans un autre terminal)
    python monde/_outils/mesurer_marche.py [afi|senami] [--captures]

Mongazi (2026-11-14) : « la façon de marcher, tout, on doit tout revoir ». On ne juge pas une marche à l'œil
seul : on la fait marcher sur un vrai trajet du salon (avec ses virages) et on mesure, image par image, la
vitesse du pied POSÉ au sol. Un pied posé ne bouge pas : tout ce qui dépasse quelques centimètres par seconde
est du patinage (mesuré au moment le plus lent de chaque demi-foulée). Sortie : la vitesse propre de son animation (mesurée par `habiller.js`), sa vitesse de
croisière, et le patinage (médiane et 90e centile, en m/s). `--captures` : six images de profil dans `_vues/`.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parents[1]
VUES = ICI / "_vues"
BASE = "http://localhost:8765/lieux/hillary-m-styl/"
QUI = next((a for a in sys.argv[1:] if not a.startswith("--")), "afi")

MESURE = """async (qui) => {
  const M = __monde, n = M.pnj.parId[qui], p = n.perso, T = M.moteur.THREE, attendre = (ms) => new Promise(r => setTimeout(r, ms));
  const os = {}; p.racine.traverse(o => { if (o.isBone) for (const k of ['LeftFoot', 'RightFoot']) if (!os[k] && new RegExp(k + '$').test(o.name)) os[k] = o; });
  if (!os.LeftFoot) return { erreur: 'pas de squelette (silhouette de maquette)' };
  M.pnj.annulerAbordage && M.pnj.annulerAbordage(); M.dialogue.fermer(); M.pnj.reglages.conversations = false;
  /* un trajet du salon avec deux virages : de l'entrée vers le comptoir en passant par les expositions */
  const pts = M.plan.points, P = (id) => { const q = pts.find(x => x.id === id); return new T.Vector3(q.x, 0, q.z); };
  /* par le VRAI graphe du salon (ses points de passage), comme elle marche d'elle-même */
  /* elle part de l'exposition de gauche (loin du visiteur, qui est à l'entrée : partir sur lui la faisait repousser) */
  p.racine.position.copy(P('expo_g')); const c = P('comptoir');
  M.pnj.envoyer(qui, c.x + 1.2, c.z + 1.0, () => { n.fin = Infinity; });
  const echant = [], v = new T.Vector3(); let dernier = performance.now();
  const f = () => {
    const now = performance.now(), dt = (now - dernier) / 1000; dernier = now;
    const e = { dt, vitesse: p.st ? p.st.vitesse : null, anim: p.animation ? p.animation() : '', rot: p.racine.rotation.y, pousse: n.pousseeTotale || 0, pos: [p.racine.position.x, p.racine.position.z], pieds: [] };
    for (const b of [os.LeftFoot, os.RightFoot]) { b.getWorldPosition(v); e.pieds.push([v.x, v.y, v.z]); }
    echant.push(e);
  };
  M.moteur.chaqueImage(f);
  const t0 = performance.now();
  while (n.chemin && performance.now() - t0 < 60000) await attendre(50);
  await attendre(600);
  M.moteur.chaqueImage.retirer ? M.moteur.chaqueImage.retirer(f) : null;
  const fin = echant.length;
  /* le patinage : vitesse horizontale du pied quand il est au plus bas (posé) */
  /* Le pied POSÉ : en pleine foulée, la cheville du pied en l'air rase le sol à la même hauteur que celle du pied
     posé, la hauteur ne les distingue pas. Une foulée (deux pas) dure `duree` ; dans chaque fenêtre d'une demi-
     foulée, le pied posé est celui qui va le plus lentement. On garde, pour chaque pied et chaque demi-foulée de
     marche à vitesse de croisière, la plus petite vitesse sur 3 images consécutives : c'est son patinage. */
  const glisse = [], dureeCycle = (p.mesureMarche && p.mesureMarche.duree) || 1.1;
  for (let k = 0; k < 2; k++) {
    const vit = [];
    for (let i = 1; i < fin; i++) {
      const a = echant[i - 1].pieds[k], b = echant[i].pieds[k], dt = echant[i].dt;
      vit.push({ t: echant.slice(0, i + 1).reduce((s, e) => s + e.dt, 0), g: dt > 0 && dt < 0.1 ? Math.hypot(b[0] - a[0], b[2] - a[2]) / dt : null,
                 croisiere: echant[i].anim === 'marcher' && (echant[i].vitesse || 0) > 0.7 * (p.vitesseNaturelle || 1) });
    }
    for (let t0 = 0; t0 < vit[vit.length - 1].t; t0 += dureeCycle / 2) {
      const f = vit.filter(x => x.t >= t0 && x.t < t0 + dureeCycle / 2);
      if (f.length < 5 || !f.every(x => x.croisiere && x.g != null)) continue;
      let m = Infinity; for (let i = 0; i + 2 < f.length; i++) m = Math.min(m, (f[i].g + f[i + 1].g + f[i + 2].g) / 3);
      glisse.push(m);
      /* le contexte de cette demi-foulée : rotation (rad/s) et écart reçu (m) */
      const i0 = vit.indexOf(f[0]) + 1, i1 = vit.indexOf(f[f.length - 1]) + 1, e0 = echant[i0], e1 = echant[i1], d = f[f.length - 1].t - f[0].t;
      (window.__pires = window.__pires || []).push({ t: +t0.toFixed(2), pied: k, glisse: +m.toFixed(3), rot: +(Math.abs(Math.atan2(Math.sin(e1.rot - e0.rot), Math.cos(e1.rot - e0.rot))) / d).toFixed(2), pousse: +(e1.pousse - e0.pousse).toFixed(3), x: +e0.pos[0].toFixed(2), z: +e0.pos[1].toFixed(2) });
    }
  }
  glisse.sort((a, b) => a - b);
  const q = (x, L = glisse) => L.length ? Math.round(L[Math.min(L.length - 1, Math.floor(x * L.length))] * 1000) / 1000 : null;
  const detail = { demi_foulees: glisse.length, pires: (window.__pires || []).sort((a, b) => b.glisse - a.glisse).slice(0, 8) }; window.__pires = [];
  const vmax = Math.max(...echant.map(e => e.vitesse || 0));
  return { qui, mesureMarche: p.mesureMarche || null, vitesseNaturelle: p.vitesseNaturelle || null, pas: p.pas || null,
           croisiere: Math.round(vmax * 1000) / 1000, images: fin, appuis: glisse.length,
           patinage_mediane: q(0.5), patinage_p90: q(0.9), detail, arrivee: n.chemin === null };
}"""


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-angle=d3d11", "--ignore-gpu-blocklist"])
        pg = b.new_context(viewport={"width": 1280, "height": 720}).new_page()
        pg.goto(BASE + "?direct=1&qualite=moyenne&heure=14", wait_until="domcontentloaded")
        pg.wait_for_function("window.__monde !== undefined", timeout=90000)
        pg.wait_for_function(f"(() => {{ const n = __monde.pnj.parId['{QUI}']; return n && n.perso.mesureMarche; }})()", timeout=120000)
        time.sleep(1.5)
        r = pg.evaluate(MESURE, QUI)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        if "--captures" in sys.argv:
            VUES.mkdir(exist_ok=True)
            pg.evaluate("""(qui) => { const M = __monde, n = M.pnj.parId[qui], T = M.moteur.THREE, pts = M.plan.points;
              const P = (id) => { const q = pts.find(x => x.id === id); return new T.Vector3(q.x, 0, q.z); };
              n.perso.racine.position.copy(P('expo_g')); const c = P('comptoir'); M.pnj.envoyer(qui, c.x + 1.2, c.z + 1.0); }""", QUI)
            # la caméra suit la visiteuse de profil, à chaque image (sinon le visiteur la reprend)
            pg.evaluate("""(qui) => { const M = __monde, c = M.moteur.camera;
              M.moteur.chaqueImage(() => { const r = M.pnj.parId[qui].perso.racine.position; c.position.set(r.x + 2.6, 1.3, r.z + 0.4); c.lookAt(r.x, 0.9, r.z); }); }""", QUI)
            for i in range(6):
                time.sleep(0.45)
                pg.screenshot(path=str(VUES / f"marche-{QUI}-{i}.png"))
        b.close()


if __name__ == "__main__":
    main()
