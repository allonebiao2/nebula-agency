# -*- coding: utf-8 -*-
"""
Audit visuel des deux back-offices : le cockpit de Mongazi et l'espace partenaire.

Ne corrige rien. Il regarde, il mesure, il rapporte. Sur trois formats, en se
connectant pour de vrai, il relève :
  · les erreurs JavaScript et les requêtes en échec (invisibles à l'œil)
  · les débordements horizontaux (mesurés, pas devinés : scrollWidth vs clientWidth)
  · les cibles tactiles trop petites (< 44 px)
  · les textes trop pâles pour être lus (contraste)
  · les images sans texte alternatif
  · les animations en boucle sous un backdrop-filter (la leçon de latence Boussole)

    python nebula-affilies/_outils/_audit_ui.py [port]
"""
import sys, json, collections
from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else "8810"
BASE = f"http://127.0.0.1:{PORT}"
ADMIN_PATH = "cockpit-d59fa50d"
FORMATS = [("mobile", 390, 844), ("tablette", 768, 1024), ("bureau", 1440, 900)]

SONDE = """() => {
  const r = { debord: null, petits: [], pales: [], sansAlt: 0, animFlou: [] };
  const de = document.documentElement;
  if (de.scrollWidth > de.clientWidth + 1)
    r.debord = { page: de.scrollWidth, ecran: de.clientWidth };

  const vus = new Set();
  document.querySelectorAll('a,button,[role=button],input,select,summary,.navbtn,.tab').forEach(el => {
    const b = el.getBoundingClientRect();
    if (b.width === 0 || b.height === 0) return;
    if (b.width < 44 || b.height < 44) {
      const t = (el.innerText || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 34);
      const cle = t + Math.round(b.width) + 'x' + Math.round(b.height);
      if (!vus.has(cle)) { vus.add(cle); r.petits.push({ t, w: Math.round(b.width), h: Math.round(b.height) }); }
    }
  });

  /* Compositer AVANT de mesurer : une surface rgba(255,255,255,.04) posée sur du
     noir reste noire. La lire comme du blanc fabrique de faux « textes pâles ».
     On empile donc les fonds translucides jusqu'à un fond opaque. */
  const rgb = c => { const m = (c||'').match(/[\d.]+/g); if (!m) return null;
    return [ +m[0], +m[1], +m[2], m.length > 3 ? +m[3] : 1 ]; };
  const poser = (haut, bas) => haut.slice(0,3).map((v,i) => v*haut[3] + bas[i]*(1-haut[3]));
  const fondReel = el => {
    let pile = [], n = el;
    while (n && n !== document.documentElement) {
      const c = rgb(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0) { pile.push(c); if (c[3] >= .999) break; }
      n = n.parentElement;
    }
    const corps = rgb(getComputedStyle(document.body).backgroundColor) || [0,0,0,1];
    let base = corps.slice(0,3);
    for (let k = pile.length - 1; k >= 0; k--) base = poser(pile[k], base);
    return base;
  };
  const lumRGB = v => { const [x,y,z] = v.map(c => { c = c/255;
      return c <= .03928 ? c/12.92 : Math.pow((c+.055)/1.055, 2.4); });
    return .2126*x + .7152*y + .0722*z; };
  const vusT = new Set();
  document.querySelectorAll('p,span,li,td,label,small,div,b,strong').forEach(el => {
    if (!el.innerText || el.children.length || el.innerText.trim().length < 4) return;
    const s = getComputedStyle(el);
    /* texte en dégradé : la couleur est transparente, il n'y a rien à mesurer */
    if (s.webkitTextFillColor === 'rgba(0, 0, 0, 0)' || s.color === 'rgba(0, 0, 0, 0)') return;
    if (s.visibility === 'hidden' || s.opacity === '0') return;
    const cTexte = rgb(s.color); if (!cTexte) return;
    const fond = fondReel(el);
    const avant = cTexte[3] < 1 ? poser(cTexte, fond) : cTexte.slice(0,3);
    const l1 = lumRGB(avant), l2 = lumRGB(fond);
    const ratio = (Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
    const taille = parseFloat(s.fontSize);
    const mini = (taille >= 24 || (taille >= 18.66 && parseInt(s.fontWeight) >= 700)) ? 3 : 4.5;
    if (ratio < mini) {
      const t = el.innerText.trim().slice(0, 34);
      if (!vusT.has(t)) { vusT.add(t); r.pales.push({ t, ratio: +ratio.toFixed(2), mini,
        couleur: s.color, fond: 'rgb(' + fond.map(Math.round).join(',') + ')' }); }
    }
  });

  document.querySelectorAll('img:not([alt])').forEach(() => r.sansAlt++);

  document.querySelectorAll('*').forEach(el => {
    const s = getComputedStyle(el);
    if (s.animationIterationCount === 'infinite' && s.animationName !== 'none') {
      let p = el.parentElement, flou = false;
      while (p) { const ps = getComputedStyle(p);
        if ((ps.backdropFilter && ps.backdropFilter !== 'none') ||
            (ps.webkitBackdropFilter && ps.webkitBackdropFilter !== 'none')) { flou = true; break; }
        p = p.parentElement; }
      if (flou) r.animFlou.push(s.animationName);
    }
  });
  r.animFlou = [...new Set(r.animFlou)];
  return r;
}"""


def auditer(page, nom, url, erreurs, reseau):
    """Si la connexion nous a déjà amenés là, on ne renavigue pas :
    deux navigations vers la même adresse s'annulent l'une l'autre."""
    if not page.url.rstrip("/").endswith(url.rstrip("/").split("/")[-1]) or url.endswith("/"):
        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
        except Exception as e:
            if "interrupted by another navigation" not in str(e):
                erreurs.append(f"[{nom}] navigation {url} : {str(e)[:100]}")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1600)
    return page.evaluate(SONDE)


def main():
    resultats = collections.OrderedDict()
    erreurs, reseau = [], []

    with sync_playwright() as p:
        nav = p.chromium.launch()
        for nom_f, w, h_ in FORMATS:
            ctx = nav.new_context(viewport={"width": w, "height": h_},
                                  device_scale_factor=2, is_mobile=(w < 500),
                                  has_touch=(w < 500))
            page = ctx.new_page()
            page.on("pageerror", lambda e: erreurs.append(f"[{nom_f}] {str(e)[:160]}"))
            page.on("console", lambda m: erreurs.append(f"[{nom_f}] console: {m.text[:160]}")
                    if m.type == "error" else None)
            page.on("response", lambda r: reseau.append(f"[{nom_f}] {r.status} {r.url[-70:]}")
                    if r.status >= 400 else None)

            # connexion admin
            page.goto(f"{BASE}/{ADMIN_PATH}", wait_until="networkidle", timeout=45000)
            try:
                page.fill("#a-email", "allonebiao2@gmail.com")
                page.fill("#a-pass", "dylanfurax")
                page.click("#a-go")
                page.wait_for_timeout(3000)
            except Exception as e:
                erreurs.append(f"[{nom_f}] connexion admin impossible : {str(e)[:120]}")

            resultats[f"{nom_f} · cockpit"] = auditer(page, nom_f, f"{BASE}/admin", erreurs, reseau)
            resultats[f"{nom_f} · devenir"] = auditer(page, nom_f, f"{BASE}/devenir", erreurs, reseau)

            # espace partenaire, connecté avec le compte de Romaric
            ctx2 = nav.new_context(viewport={"width": w, "height": h_},
                                   device_scale_factor=2, is_mobile=(w < 500), has_touch=(w < 500))
            pg2 = ctx2.new_page()
            pg2.on("pageerror", lambda e: erreurs.append(f"[{nom_f}/part] {str(e)[:160]}"))
            pg2.on("console", lambda m: erreurs.append(f"[{nom_f}/part] console: {m.text[:160]}")
                   if m.type == "error" else None)
            pg2.on("response", lambda r: reseau.append(f"[{nom_f}/part] {r.status} {r.url[-70:]}")
                   if r.status >= 400 else None)
            pg2.goto(f"{BASE}/", wait_until="networkidle", timeout=45000)
            try:
                pg2.fill("#p-code", "RBNXF"); pg2.fill("#p-pin", "0067"); pg2.click("#p-go")
                pg2.wait_for_timeout(3000)
            except Exception as e:
                erreurs.append(f"[{nom_f}] connexion partenaire impossible : {str(e)[:120]}")
            resultats[f"{nom_f} · espace partenaire"] = auditer(pg2, nom_f, f"{BASE}/partenaire", erreurs, reseau)
            ctx2.close()
            ctx.close()
        nav.close()

    print("\n" + "=" * 66)
    print("  AUDIT DES BACK-OFFICES")
    print("=" * 66)
    for cle, r in resultats.items():
        soucis = []
        if r["debord"]:
            soucis.append(f"DÉBORDEMENT {r['debord']['page']}px dans {r['debord']['ecran']}px")
        if r["petits"]:
            soucis.append(f"{len(r['petits'])} cible(s) < 44px")
        if r["pales"]:
            soucis.append(f"{len(r['pales'])} texte(s) trop pâle(s)")
        if r["sansAlt"]:
            soucis.append(f"{r['sansAlt']} image(s) sans alt")
        if r["animFlou"]:
            soucis.append(f"{len(r['animFlou'])} animation(s) sous un flou")
        print(f"\n  {cle}")
        print("     " + ("✅ rien à signaler" if not soucis else " · ".join(soucis)))
        for x in r["petits"][:5]:
            print(f"       petit : « {x['t']} » {x['w']}×{x['h']}")
        for x in r["pales"][:5]:
            print(f"       pâle  : « {x['t']} » contraste {x['ratio']} (mini {x['mini']})")
        for a in r["animFlou"][:4]:
            print(f"       anim sous flou : {a}")

    print("\n" + "-" * 66)
    print(f"  Erreurs JavaScript : {len(erreurs)}")
    for e in dict.fromkeys(erreurs[:14]):
        print("    ·", e)
    print(f"  Requêtes en échec : {len(reseau)}")
    for r in dict.fromkeys(reseau[:10]):
        print("    ·", r)

    with open(r"C:/Users/USER/AppData/Local/Temp/claude/audit_ui.json", "w", encoding="utf-8") as f:
        json.dump({"resultats": resultats, "erreurs": erreurs, "reseau": reseau}, f,
                  ensure_ascii=False, indent=1)
    print("\n  détail complet : audit_ui.json")


if __name__ == "__main__":
    main()
