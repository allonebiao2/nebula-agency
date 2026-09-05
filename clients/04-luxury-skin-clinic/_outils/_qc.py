# -*- coding: utf-8 -*-
"""
_qc.py — la suite de controle de la vitrine Luxury Skin Clinic.

    python _outils/_qc.py
    python _outils/_qc.py --page cozy.html

Ce que ce controle sait faire, et que les autres ne savaient pas :

⚠️ IL MESURE LE CONTRASTE SUR LES PIXELS RENDUS. Un controle qui lit
   `background-color` est aveugle des qu'un texte est pose sur une photo ou
   sur un degrade : la propriete vaut `rgba(0,0,0,0)` et il conclut que tout
   va bien (lecon Angy Art du 2026-08-08). Ici on masque le texte, on
   photographie ce qu'il y a dessous, et on compare aux vraies couleurs.

⚠️ IL CALCULE LES RECOUVREMENTS AU LIEU DE LES ECHANTILLONNER. Un instrument
   fixe et un texte qui defile se croisent dans une fenetre de quelques
   dizaines de pixels : balayer par paliers passe a cote quatre fois sur cinq
   (lecon Angy Art du 2026-09-04).

⚠️ IL VERIFIE QUE LES BOUTONS SE VOIENT. « Pas de bouton invisible » est une
   exigence de Mongazi (2026-09-05), et c'est exactement le defaut qui avait
   ete trouve sur une capture chez Au Braise d'Or : un bouton dont le fond
   avait ete efface par `clearProps`.
"""
import argparse, json, os, re, sys, io
from playwright.sync_api import sync_playwright

# La console Windows est en cp1252 : sans ca, le rapport plante sur un caractere
# accentue APRES avoir reussi tous ses controles (lecon Au Braise d'Or, 19/08).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERTS, ROUGES = [], []


def ok(m):
    VERTS.append(m)


def ko(m):
    ROUGES.append(m)


def att(cond, m):
    (ok if cond else ko)(m)


# ---------------------------------------------------------------- couleurs
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = rgb[:3]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(l1, l2):
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


def parse_rgb(s):
    n = [float(x) for x in re.findall(r"[\d.]+", s or "")]
    if len(n) < 3:
        return None
    return (n[0], n[1], n[2], n[3] if len(n) > 3 else 1.0)


# ------------------------------------------------------- controles statiques
def controles_fichier(chemin):
    src = io.open(chemin, encoding="utf-8").read()

    # 1. les quatre demandes de Gloria du 2026-09-05
    att("Consultation Peau'" not in src.replace("Consultation Peau — Suivi'", ""),
        "aucune consultation gratuite ne subsiste dans le catalogue")
    att("Diagnostic Capillaire" not in src, "le Diagnostic Capillaire a disparu")
    att("Consultation Capillaire Premium" in src and "p:30000" in src,
        "la Consultation Capillaire Premium est au catalogue a 30 000 F")
    att("Soin Visage Classic" in src and "p:15000" in src,
        "le Soin Visage Classic est au catalogue a 15 000 F")
    att("mercredi" not in src, "plus une seule mention de mercredi")
    att(src.count("du lundi au samedi") >= 4,
        "les nouveaux jours sont dits partout (%d fois)" % src.count("du lundi au samedi"))
    att("ALLOWED_WEEKDAYS=[1,2,3,4,5,6]" in src, "le calendrier ouvre du lundi au samedi")
    att("{value:'09:00'" not in src and "{value:'10:00'" in src,
        "le premier creneau est a 10h, pas avant l'ouverture")

    # 2. ce qui ne doit jamais bouger
    att(src.count("2290167975626") >= 1, "le numero WhatsApp de Gloria est intact")
    att("sk_live_" not in src, "aucune cle secrete dans la page")

    # 3. le formulaire mort ne traine pas
    for mort in ("SKIN_FORM", "HAIR_FORM", "openForm(", "payViaWa"):
        att(mort not in src, "aucune trace de %s (code mort retire)" % mort)

    # 4. les images d'ambiance : les deux cotes lus dans les fichiers
    dossier = os.path.join(RACINE, "assets", "images", "clinic")
    posees = {f[:-5] for f in os.listdir(dossier) if f.endswith(".webp")}
    demandees = set(re.findall(r"assets/images/clinic/([a-z]+)\.webp", src))
    # les quatre familles sont ecrites en gabarit ${g.key}
    if "clinic/${g.key}.webp" in src:
        demandees |= {"visage", "corps", "capillaires", "vip"}
    att(not (posees - demandees),
        "aucune image d'ambiance inutilisee (%s)" % (", ".join(sorted(posees - demandees)) or "aucune"))
    att(not (demandees - posees),
        "aucune image d'ambiance manquante (%s)" % (", ".join(sorted(demandees - posees)) or "aucune"))

    # 5. un croquis par soin
    att(src.count("const ART={") == 1, "la table des croquis existe")
    att(len(re.findall(r"a:'[a-z]+'", src)) == 11, "les onze soins ont leur croquis")

    # 6. les regles de la maison
    att("@media(prefers-reduced-motion:reduce)" in src, "le mouvement reduit est respecte")
    att("photo à venir" not in src.lower(), "aucun texte d'attente sur la page")
    return src



# ---------------------------------------------------------------------------
# Les zones a mesurer, page par page. Le premier bloc (HAUT) est mesure en
# haut de page, les suivants apres un defilement jusqu'a la zone.
# ---------------------------------------------------------------------------
def _h(w, l):
    return [(s, "%d px : %s" % (w, n)) for s, n in l]

HAUT = {}
ZONES = {
  "index.html": [
    ("#brands", [(".brand h2", "nom d'un univers"), (".brand-desc", "texte d'un univers"),
                 (".brand-kicker", "sous-titre d'un univers"), (".brand-enter", "lien Entrer")]),
    ("#bio", [(".hub-bio-inner p", "biographie"), (".hub-bio-inner h2", "titre de la biographie")]),
  ],
  "ina-luxury.html": [
    (".guide", [(".guide-txt b", "titre de l'encart conseil"), (".guide-txt p", "texte de l'encart"),
                (".guide-cta", "bouton de consultation")]),
    (".fam-cards", [(".fam-card h3", "nom d'une famille"), (".fam-card p", "texte d'une famille"),
                    (".fam-card .fc-k", "compte d'une famille"), (".fam-card .fc-go", "lien Decouvrir")]),
  ],
  "cozy.html": [
    (".hero", [(".hero h1", "titre du heros"), (".hero p", "accroche du heros"),
               (".hero-tag", "etiquette du heros"), (".hero-note", "note du heros")]),
    (".cat-band", [(".cb-mot", "phrase de la bande"), (".fpill", "pastille de filtre")]),
    (".grid", [(".card h3", "nom d'un produit"), (".card .price", "prix d'un produit")]),
  ],
}

# ------------------------------------------------------- controles navigateur
JS_MESURES = r"""
() => {
  const vu = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'
           && parseFloat(s.opacity) > .05;
  };
  const res = {debord: [], cibles: [], anim: [], boutons: []};

  // 1. debordement horizontal
  const doc = document.documentElement;
  res.debordDoc = doc.scrollWidth - doc.clientWidth;
  // ⚠️ un element PLUS LARGE que son parent ne deborde pas de la page si un
  //    ancetre le rogne (`overflow:hidden`). C'est le cas de l'image du heros,
  //    qui est agrandie par un `transform` : elle depasse dans le calcul et
  //    nulle part a l'ecran. On regarde donc si quelqu'un la coupe.
  const rogne = el => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX;
      if (o === 'hidden' || o === 'clip' || o === 'auto' || o === 'scroll') return true;
    }
    return false;
  };
  document.querySelectorAll('body *').forEach(el => {
    if (!vu(el)) return;
    const r = el.getBoundingClientRect();
    if (r.right > innerWidth + 1.5 && getComputedStyle(el).position !== 'fixed' && !rogne(el))
      res.debord.push({t: el.tagName + '.' + (el.className || '').toString().slice(0, 40),
                       d: Math.round(r.right - innerWidth)});
  });

  // 2. cibles tactiles : tout ce qui se touche fait au moins 44 px
  document.querySelectorAll('a,button,input,select,[role=button]').forEach(el => {
    if (!vu(el)) return;
    const r = el.getBoundingClientRect();
    // le piege a robots du formulaire est pose a -9999 px : il est « visible »
    // au sens du CSS et pourtant personne ne le touchera jamais
    if (r.right < 0 || r.left > innerWidth) return;
    const dansPhrase = el.tagName === 'A' && el.closest('p,li,small');
    // une case a cocher enveloppee d'un <label> se touche PAR SON LABEL :
    // c'est lui la cible, et c'est lui qu'on mesure
    let parLabel = false;
    if (el.tagName === 'INPUT' && (el.type === 'checkbox' || el.type === 'radio')) {
      const lab = el.closest('label');
      if (lab) {
        const lr = lab.getBoundingClientRect();
        parLabel = lr.height >= 43.5 && lr.width >= 43.5;
      }
    }
    if (!dansPhrase && !parLabel && (r.height < 43.5 || r.width < 43.5))
      res.cibles.push({t: ((el.textContent || el.getAttribute('aria-label') || '').trim()
                        || (el.tagName + (el.id ? '#' + el.id : '') + (el.type ? '[' + el.type + ']' : ''))).slice(0, 40),
                       w: Math.round(r.width), h: Math.round(r.height)});
  });

  // 3. animation infinie sous un backdrop-filter
  document.querySelectorAll('*').forEach(el => {
    const s = getComputedStyle(el);
    const bd = s.backdropFilter || s.webkitBackdropFilter || 'none';
    if (bd !== 'none' && s.animationIterationCount.split(',').some(v => v.trim() === 'infinite'))
      res.anim.push(el.tagName + '.' + (el.className || '').toString().slice(0, 40));
  });

  // 4. les boutons ont-ils un fond ou une bordure ? (pas de bouton fantome)
  document.querySelectorAll('a.btn-dark,a.btn-line,a.btn-gold,button.svc-book,button.rdv-submit,'
    + 'button.regl-confirm,a.book-top,button.lc-cat-btn,button.rdv-day-toggle').forEach(el => {
    if (!vu(el)) return;
    const s = getComputedStyle(el);
    const fond = s.backgroundColor, img = s.backgroundImage, bord = s.borderTopWidth;
    const transparent = (fond === 'rgba(0, 0, 0, 0)' || fond === 'transparent')
                        && img === 'none' && parseFloat(bord) < 0.5;
    res.boutons.push({t: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 30),
                      fantome: transparent, couleur: s.color, fond: fond});
  });
  return res;
}
"""


def mesure_contraste(page, sel, nom, seuil=None, indice=0):
    """Contraste MESURE sur les pixels reellement rendus sous le texte."""
    # ⚠️ on amene l'element AU MILIEU de la fenetre avant de mesurer : au bord,
    #    il passe sous la barre du haut ou sous la bande de bord, et c'est
    #    l'ombre de l'instrument qu'on mesure au lieu du fond de la page
    #    (deux faux rouges a 2,10:1, le 2026-09-05).
    page.evaluate("""([s, i]) => {
        const e = document.querySelectorAll(s)[i];
        if (!e) return;
        const r = e.getBoundingClientRect();
        if (r.top < 120 || r.bottom > innerHeight - 120)
            scrollTo({top: Math.max(0, r.top + scrollY - innerHeight / 2), behavior: 'instant'});
    }""", [sel, indice])
    # la revelation d'une carte dure 550 ms : mesurer avant, c'est mesurer une
    # opacite intermediaire et accuser un bouton parfaitement lisible (3,29:1
    # releve sur un bouton qui vaut 16,6:1 une fois pose).
    page.wait_for_timeout(800)
    infos = page.evaluate(
        """([s, i]) => {
            const els = document.querySelectorAll(s);
            const el = els[i];
            if (!el) return null;
            const r = el.getBoundingClientRect();
            if (r.width < 2 || r.height < 2) return null;
            const st = getComputedStyle(el);
            const taille = parseFloat(st.fontSize);
            const gras = (parseInt(st.fontWeight, 10) || 400) >= 600;
            // ⚠️ on LIT la couleur avant de la rendre transparente : poser le
            // drapeau ici ferait relire `transparent` a la mesure suivante
            // (la sonde se mesurait elle-meme, 2026-09-05).
            return {x: r.x, y: r.y, w: r.width, h: r.height,
                    couleur: st.color, taille: taille, gras: gras};
        }""", [sel, indice])
    if not infos:
        return None
    # on ramene la boite DANS la fenetre : un clip qui deborde fait echouer la
    # capture, et c'est l'instrument qui aurait tort, pas la page
    vw, vh = page.viewport_size["width"], page.viewport_size["height"]
    x0, y0 = max(0.0, infos["x"]), max(0.0, infos["y"])
    x1, y1 = min(vw, infos["x"] + infos["w"]), min(vh, infos["y"] + infos["h"])
    if x1 - x0 < 3 or y1 - y0 < 3:
        return None

    if not page.evaluate("() => !!document.getElementById('qc-cache-css')"):
        page.add_style_tag(content="[data-qc-cache]{color:transparent!important;"
                                   "text-shadow:none!important;-webkit-text-fill-color:transparent!important;}")
        page.evaluate("() => {const t=[...document.querySelectorAll('style')].pop(); if(t) t.id='qc-cache-css';}")
    page.evaluate("([s, i]) => {const e = document.querySelectorAll(s)[i]; if(e) e.setAttribute('data-qc-cache','1');}",
                  [sel, indice])
    png = page.screenshot(clip={"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0})
    page.evaluate("() => document.querySelectorAll('[data-qc-cache]').forEach(e => e.removeAttribute('data-qc-cache'))")

    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    px = list(im.convert("RGB").getdata())
    lums = sorted(lum(p) for p in px)
    n = len(lums)
    bas, haut = lums[int(n * .1)], lums[int(n * .9)]
    c = parse_rgb(infos["couleur"])
    lt = lum(c)
    pire = min(contraste(lt, bas), contraste(lt, haut))
    if seuil is None:
        gros = infos["taille"] >= 24 or (infos["taille"] >= 18.66 and infos["gras"])
        seuil = 3.0 if gros else 4.5
    if pire >= seuil:
        ok("%s : contraste mesure %.2f:1 (seuil %.1f)" % (nom, pire, seuil))
    else:
        # un controle NOMME ce qui manque : la boite, la couleur du texte et le
        # fond reellement photographie, sinon on cherche a l'aveugle
        ko("%s : contraste mesure %.2f:1 (seuil %.1f) — texte %s sur un fond de "
           "luminance %.3f a %.3f, boite %dx%d en (%d,%d)"
           % (nom, pire, seuil, infos["couleur"], bas, haut,
              round(x1 - x0), round(y1 - y0), round(x0), round(y0)))
    return pire


def recouvrements(page):
    """Un recouvrement se CALCULE : on resout l'intervalle de defilement ou un
    instrument fixe croise un texte qui defile."""
    return page.evaluate(r"""
    () => {
      const fixes = [];
      document.querySelectorAll('body *').forEach(el => {
        const s = getComputedStyle(el);
        if (s.position !== 'fixed') return;
        if (s.visibility === 'hidden' || s.display === 'none' || parseFloat(s.opacity) < .05) return;
        if (s.pointerEvents === 'none') return;      // le curseur suit la souris, il ne recouvre rien
        const r = el.getBoundingClientRect();
        if (r.width < 8 || r.height < 8) return;
        // une bande de bord traverse l'ecran : elle a le droit, si elle est opaque
        const bande = r.width >= innerWidth - 2;
        fixes.push({el, r, bande, nom: el.tagName + '.' + (el.className || '').toString().slice(0, 30)});
      });
      // ⚠️ ce qui est POSE SUR une bande de bord fait partie de la bande : les
      //    pastilles sociales ne flottent plus au milieu des titres depuis
      //    qu'elles ont un socle opaque. Les exclure ici, c'est mesurer la
      //    situation reelle et non le nombre d'elements `fixed`.
      const bandes = fixes.filter(f => f.bande);
      const flottants = fixes.filter(f => !f.bande && !bandes.some(b =>
        f.r.top >= b.r.top - 2 && f.r.bottom <= b.r.bottom + 2));
      const conflits = [];
      const course = document.documentElement.scrollHeight - innerHeight;
      const y0 = scrollY;
      document.querySelectorAll('h1,h2,h3,p,li,span.svc-cat,.svc-price,.eyebrow,.rdv-flabel,label')
        .forEach(t => {
          const s = getComputedStyle(t);
          if (s.position === 'fixed' || s.position === 'absolute') return;
          if (!t.textContent.trim()) return;
          const r = t.getBoundingClientRect();
          if (r.width < 4 || r.height < 4) return;
          const hautDoc = r.top + y0;          // position dans le document
          flottants.forEach(f => {
            // chevauchement horizontal ?
            if (r.right < f.r.left || r.left > f.r.right) return;
            // le texte croise l'instrument quand  f.top < hautDoc - S + r.height  et  f.bottom > hautDoc - S
            const sMin = hautDoc + r.height - f.r.bottom;
            const sMax = hautDoc - f.r.top;
            const a = Math.max(0, Math.min(sMin, sMax)), b = Math.min(course, Math.max(sMin, sMax));
            if (b > a + 1) conflits.push({texte: t.textContent.trim().slice(0, 40), fixe: f.nom,
                                          de: Math.round(a), a: Math.round(b)});
          });
        });
      return conflits;
    }""")


def controles_navigateur(chemin, largeurs=(390, 1440)):
    url = "file:///" + chemin.replace("\\", "/")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in largeurs:
            mobile = w < 700
            ctx = b.new_context(viewport={"width": w, "height": 844 if mobile else 900},
                                is_mobile=mobile, has_touch=mobile,
                                device_scale_factor=1)
            page = ctx.new_page()
            erreurs, echecs = [], []
            page.on("pageerror", lambda e: erreurs.append(str(e)))
            page.on("requestfailed", lambda r: echecs.append(r.url.split("/")[-1]))
            page.goto(url)
            page.wait_for_timeout(2600)
            try:
                page.click("#welcome-gate", timeout=1200)
            except Exception:
                pass
            page.wait_for_timeout(1200)

            att(not erreurs, "%d px : aucune erreur JavaScript%s" % (w, (" — " + erreurs[0][:90]) if erreurs else ""))
            att(not echecs, "%d px : aucune ressource en echec%s" % (w, (" — " + ", ".join(echecs[:3])) if echecs else ""))

            m = page.evaluate(JS_MESURES)
            att(m["debordDoc"] <= 1, "%d px : la page ne deborde pas (%d px)" % (w, m["debordDoc"]))
            att(not m["debord"], "%d px : aucun bloc ne sort de l'ecran%s"
                % (w, (" — " + m["debord"][0]["t"]) if m["debord"] else ""))
            att(not m["cibles"], "%d px : toutes les cibles font 44 px%s"
                % (w, (" — %s (%dx%d)" % (m["cibles"][0]["t"], m["cibles"][0]["w"], m["cibles"][0]["h"]))
                   if m["cibles"] else ""))
            att(not m["anim"], "%d px : aucune animation infinie sous un backdrop-filter%s"
                % (w, (" — " + m["anim"][0]) if m["anim"] else ""))

            fantomes = [x for x in m["boutons"] if x["fantome"]]
            att(not fantomes, "%d px : aucun bouton fantome (%d boutons verifies)%s"
                % (w, len(m["boutons"]), (" — " + fantomes[0]["t"]) if fantomes else ""))

            conflits = recouvrements(page)
            att(not conflits, "%d px : aucun instrument flottant ne croise du texte%s"
                % (w, (" — « %s » sous %s" % (conflits[0]["texte"], conflits[0]["fixe"])) if conflits else ""))

            # --- contrastes MESURES, zone par zone ---
            page.evaluate("() => scrollTo({top:0, behavior:'instant'})")
            page.wait_for_timeout(700)
            clinique = os.path.basename(chemin) == "luxury-skin-clinic.html"
            for sel, nom in ([(".hero h1", "%d px : titre du heros" % w),
                             (".hero h1 em", "%d px : italique du heros" % w),
                             (".hero-sub", "%d px : accroche du heros" % w),
                             (".hero-badge", "%d px : badge du heros" % w),
                             (".hero .btn-dark", "%d px : bouton « Prendre rendez-vous »" % w),
                             (".hero .btn-line", "%d px : bouton « Decouvrir les soins »" % w),
                             (".exp-txt b", "%d px : nom de Mme Sabrina" % w),
                             (".exp-txt p", "%d px : fonction de Mme Sabrina" % w),
                             (".exp-seal", "%d px : sceau du heros" % w),
                             (".back-hub", "%d px : lien Accueil" % w),
                             (".book-top", "%d px : bouton Reserver de la barre" % w)] if clinique else []):
                mesure_contraste(page, sel, nom)

            for cible, liste in ZONES.get(os.path.basename(chemin), [("#manifeste", [(".mf-head h2", "titre du manifeste"),
                                                 (".mf-p h3", "titre d'un pilier"),
                                                 (".mf-p p", "texte d'un pilier"),
                                                 (".mf-n", "numero d'un pilier")]),
                                 (".rdv-banner", [(".rdv-banner-in p", "texte du bandeau RDV"),
                                                  (".rdv-banner-cta", "lien du bandeau RDV")]),
                                 (".ruban", [(".ruban-piste span", "mots du ruban")]),
                                 ("#svcSections .sec-band", [(".sec-band-in h2", "titre d'une bande"),
                                                             (".sec-band-in p", "texte d'une bande"),
                                                             (".sec-band-in .eyebrow", "etiquette d'une bande")]),
                                 ("#svcSections .svc", [(".svc h3", "nom d'un soin"),
                                                        (".svc-price", "prix d'un soin"),
                                                        (".svc-d", "description d'un soin"),
                                                        (".svc-cat", "famille d'un soin"),
                                                        (".sc-badge", "badge de preoccupation"),
                                                        (".svc-meta span", "meta d'un soin"),
                                                        (".svc-acc-btn", "bouton du protocole"),
                                                        (".svc-book", "bouton « Reserver ce soin »"),
                                                        (".svc-rdv span", "ligne des horaires"),
                                                        (".svc-by", "mention « realise par »")]),
                                 ("#rdv-booking", [(".rdv-title", "titre du rendez-vous"),
                                                   (".rdv-intro", "intro du rendez-vous"),
                                                   (".rdv-label", "etape du rendez-vous"),
                                                   (".rdv-day-date", "date d'un jour"),
                                                   (".rdv-day-weekday", "jour de la semaine"),
                                                   (".rdv-day-toggle", "bouton « autres dates »"),
                                                   (".rdv-days-help", "aide des jours"),
                                                   (".rdv-flabel", "libelle d'un champ"),
                                                   (".rdv-acompte-steps li", "etape de l'acompte"),
                                                   (".rdv-ack-list li", "ligne du reglement"),
                                                   (".rdv-submit", "bouton « Reserver le rendez-vous »"),
                                                   (".rdv-validation", "note de validation")]),
                                 (".final", [(".final-card h2", "titre final"),
                                             (".final-card p", "texte final"),
                                             (".final-card .btn-gold", "bouton final")]),
                                 ("footer", [(".foot-meta", "pied de page")])]):
                page.evaluate("""(s) => {
                    const e = document.querySelector(s);
                    if (e) scrollTo({top: Math.max(0, e.getBoundingClientRect().top + scrollY - 120),
                                     behavior: 'instant'});
                }""", cible)
                page.wait_for_timeout(1500)
                for sel, nom in liste:
                    mesure_contraste(page, sel, "%d px : %s" % (w, nom))

            # --- les SURVOLS : un bouton qui change de fond change de contraste ---
            # (c'est ainsi qu'on a trouve le 3,29:1 du 2026-09-05 : le fond
            #  passait en or et le texte restait creme)
            for sel, nom in ([(".hero .btn-dark", "bouton du heros survole"),
                             (".svc-book", "bouton « Reserver ce soin » survole"),
                             (".book-top", "bouton Reserver de la barre survole")] if clinique else []):
                try:
                    el = page.query_selector(sel)
                    if el:
                        el.scroll_into_view_if_needed()
                        page.wait_for_timeout(400)
                        el.hover()
                        page.wait_for_timeout(500)
                        mesure_contraste(page, sel, "%d px : %s" % (w, nom))
                        page.mouse.move(2, 2)
                        page.wait_for_timeout(200)
                except Exception as e:
                    ko("%d px : %s — impossible a survoler (%s)" % (w, nom, str(e)[:60]))

            # la bande de bord doit etre VRAIMENT opaque
            opac = page.evaluate("""() => {
                const d = document.querySelector('.lc-dock');
                if (!d) return null;
                const s = getComputedStyle(d);
                const m = (s.backgroundColor.match(/[\\d.]+/g) || []);
                return m.length > 3 ? parseFloat(m[3]) : 1;
            }""")
            att(opac == 1, "%d px : la bande de bord est vraiment opaque (%s)" % (w, opac))

            ctx.close()
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default="luxury-skin-clinic.html")
    a = ap.parse_args()
    chemin = os.path.join(RACINE, a.page)
    if a.page == "luxury-skin-clinic.html":
        controles_fichier(chemin)
    controles_navigateur(chemin)

    print("")
    for m in ROUGES:
        print(u"  ROUGE  " + m)
    print(u"  %d verts, %d rouges" % (len(VERTS), len(ROUGES)))
    if not ROUGES:
        print(u"  tout est vert.")
    sys.exit(1 if ROUGES else 0)


if __name__ == "__main__":
    main()
