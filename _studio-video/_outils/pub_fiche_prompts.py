# Fabrique la fiche « L'AUTRE · les prompts » (HTML, bouton Copier par prompt) à partir du dossier du cerveau.
# Les prompts ne sont jamais recopiés à la main : ils sont LUS dans le fichier qui fait autorité.
# Usage : python _studio-video/_outils/pub_fiche_prompts.py <sortie.html>, puis republier la page à la même adresse
# (https://claude.ai/artifact/GTZdNfrpwPfQXsXNEpLEc5, outil Artifact avec `url`, après l'avoir lue).
import html, pathlib, re, sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "_memoire" / "videos-pub" / "projets" / "01-l-autre.md"
OUT = pathlib.Path(sys.argv[1])

lignes = SRC.read_text(encoding="utf-8").splitlines()

items, courant, etiquette, dans_code, code, section = [], None, None, False, [], None
for l in lignes:
    s = l.strip()
    if s.startswith("```"):
        if not dans_code:
            dans_code, code = True, []
        else:
            dans_code = False
            if courant is not None:
                courant["blocs"].append({"label": etiquette or "IMAGE", "texte": "\n".join(code)})
            etiquette = None
        continue
    if dans_code:
        code.append(l)
        continue
    if l.startswith("## "):
        section = l[3:5]
        courant = None
        if section.startswith("5"):
            break
        continue
    if section not in ("3.", "4."):
        continue
    m = re.match(r"^### (R\d) · (.+)$", l)
    if m:
        t = m.group(2)
        mm = re.match(r"^(.*?)\s*\(([^)]*)\)$", t)
        courant = {"type": "ref", "code": m.group(1), "titre": mm.group(1) if mm else t,
                   "puces": [mm.group(2)] if mm else [], "desc": [], "blocs": []}
        items.append(courant)
        continue
    m = re.match(r"^### (Acte .+?)\s*\((.+)\)$", l)
    if m:
        items.append({"type": "acte", "nom": m.group(1), "lumiere": m.group(2)})
        courant = None
        continue
    if l.startswith("#### "):
        parts = l[5:].split(" · ")
        puces = [p[0].upper() + p[1:].lower() if p.isupper() or p.split(" ")[0].isupper() else p for p in parts[2:]]
        courant = {"type": "plan", "code": parts[0], "titre": parts[1], "puces": puces, "desc": [], "blocs": []}
        items.append(courant)
        continue
    m = re.match(r"^\*\*(IMAGE[^*]*|ANIMATION)\*\*(.*)$", s)
    if m and courant is not None:
        reste = m.group(2).strip()
        if reste.startswith(":"):
            courant["blocs"].append({"note": m.group(1) + " " + reste})
        else:
            etiquette = (m.group(1) + (" " + reste if reste else "")).strip()
        continue
    if courant is not None and s and not s.startswith("---"):
        courant["desc"].append(s)

refs = [i for i in items if i["type"] == "ref"]
plans = [i for i in items if i["type"] == "plan"]
nb_code = sum(1 for i in refs + plans for b in i["blocs"] if "texte" in b)
assert len(refs) == 6 and len(plans) == 22 and nb_code == 46, (len(refs), len(plans), nb_code)

def fmt(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", t)

def ident(code):
    return code.lower().replace(" ", "-")

def libelle(label, est_ref, puces):
    if est_ref:
        return "Image · Nano Banana Pro" + (" · joindre R4 et la modifier" if any("MODIFIANT" in p for p in puces) else "")
    if label.startswith("IMAGE A"):
        return "Image A · la première image"
    if label.startswith("IMAGE B"):
        return "Image B · la dernière image : joindre A et la modifier"
    if label.startswith("IMAGE"):
        return "Image · Nano Banana Pro"
    if "B en dernière" in label:
        return "Animation · Veo 3.1 · A en première image, B en dernière"
    return "Animation · Veo 3.1 · Frames to Video"

corps, sauts, n_pre = [], [], 0
for it in items:
    if it["type"] == "acte":
        cls = "neon" if "plate" in it["lumiere"] else "film"
        corps.append(f'<div class="acte"><h2>{fmt(it["nom"])}</h2><span class="lumiere {cls}">{fmt(it["lumiere"])}</span></div>')
        continue
    est_ref = it["type"] == "ref"
    i = ident(it["code"])
    sauts.append(f'<a href="#{i}" data-id="{i}">{html.escape(it["code"])}</a>')
    desc = " ".join(it["desc"])
    joindre = ""
    m = re.search(r"Références : ([^.]+)\.", desc)
    if m:
        joindre = m.group(1).replace(", ", " · ")
        desc = (desc[:m.start()] + desc[m.end():]).strip()
    puces = "".join(
        f'<span class="puce{" fort" if not p.startswith("garder") and not p.startswith("format") else ""}">{fmt(p)}</span>'
        for p in it["puces"])
    blocs = []
    for b in it["blocs"]:
        if "note" in b:
            blocs.append(f'<p class="note">{fmt(b["note"].replace("IMAGE", "Image", 1))}</p>')
            continue
        n_pre += 1
        pid = f"t{n_pre}"
        blocs.append(
            f'<div class="bloc"><div class="bloc-tete"><span class="etiquette">{fmt(libelle(b["label"], est_ref, it["puces"]))}</span>'
            f'<button type="button" class="copier" data-cible="{pid}">Copier</button></div>'
            f'<pre id="{pid}">{html.escape(b["texte"], quote=False)}</pre></div>')
    fichier = "" if est_ref else f'<p class="fichier">Enregistre la meilleure prise : <code>{html.escape(it["code"].replace(" ", "-"))}.mp4</code></p>'
    corps.append(
        f'<article id="{i}"><div class="tete"><div class="tete-g"><span class="code">{html.escape(it["code"])}</span>'
        f'<h3>{fmt(it["titre"])}</h3>{f"<div class=\"puces\">{puces}</div>" if puces else ""}</div>'
        f'<label class="fait" for="fait-{i}"><input type="checkbox" id="fait-{i}"> Fait</label></div>'
        + (f'<p class="desc">{fmt(desc)}</p>' if desc else "")
        + (f'<p class="joindre">À joindre : <strong>{html.escape(joindre)}</strong></p>' if joindre else "")
        + "".join(blocs) + fichier + "</article>")

CSS = r"""
:root{
  /* Une feuille de tournage : la nuit du téléphone (bleu), la lampe (ambre), le néon (vert plat). */
  --bg:#f1f3f7; --surface:#ffffff; --sunk:#eceff5; --fg:#131823; --muted:#566073; --line:#d6dbe4;
  --accent:#2c59d6; --accent-soft:#e5ecfd; --on-accent:#ffffff; --lamp:#94560a; --neon:#26704f;
  --f-display:"Space Grotesk", ui-sans-serif, system-ui, sans-serif;
  --f-text:"Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono:"JetBrains Mono", ui-monospace, Consolas, "SFMono-Regular", monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0b0f16; --surface:#121822; --sunk:#0d121a; --fg:#e6eaf1; --muted:#9aa3b4; --line:#243040;
  --accent:#8aa9ff; --accent-soft:#17223a; --on-accent:#0b0f16; --lamp:#f0b45e; --neon:#7fd3a6; color-scheme:dark; } }
:root[data-theme="dark"]{
  --bg:#0b0f16; --surface:#121822; --sunk:#0d121a; --fg:#e6eaf1; --muted:#9aa3b4; --line:#243040;
  --accent:#8aa9ff; --accent-soft:#17223a; --on-accent:#0b0f16; --lamp:#f0b45e; --neon:#7fd3a6; color-scheme:dark; }
body{ background:var(--bg); color:var(--fg); font-family:var(--f-text); font-size:15px; line-height:1.55;
  padding-left:max(16px, env(safe-area-inset-left,0px)); padding-right:max(16px, env(safe-area-inset-right,0px));
  padding-block:28px 64px; }
.page{ max-width:860px; margin:0 auto; display:grid; gap:22px; }
header{ display:grid; gap:14px; }
h1{ font-family:var(--f-display); font-size:clamp(28px,5vw,40px); line-height:1.1; margin:0; text-wrap:balance; letter-spacing:-.01em; }
.sous{ color:var(--muted); margin:0; }
.etapes{ margin:0; padding-left:1.3em; display:grid; gap:6px; max-width:68ch; }
.essai{ background:var(--accent-soft); border:1px solid var(--accent); border-radius:10px; padding:12px 14px; margin:0; }
.essai a{ color:var(--accent); font-weight:600; }
.compte{ margin:0; font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums; }
.saut{ display:flex; flex-wrap:wrap; gap:6px; }
.saut a{ font-family:var(--f-mono); font-size:12.5px; text-decoration:none; color:var(--fg); border:1px solid var(--line);
  border-radius:999px; padding:3px 9px; background:var(--surface); }
.saut a.fini{ color:var(--muted); text-decoration:line-through; }
.saut a:focus-visible, button:focus-visible, .fait input:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }
.acte{ display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; margin-top:10px; }
.acte h2{ font-family:var(--f-display); font-size:21px; margin:0; }
.lumiere{ font-size:11.5px; letter-spacing:.06em; text-transform:uppercase; padding:2px 8px; border-radius:999px; border:1px solid currentColor; }
.lumiere.film{ color:var(--lamp); } .lumiere.neon{ color:var(--neon); }
article{ background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:16px; display:grid; gap:12px; min-width:0; scroll-margin-top:16px; }
.tete{ display:flex; gap:12px; align-items:flex-start; justify-content:space-between; }
.tete-g{ min-width:0; }
.code{ font-family:var(--f-mono); font-weight:600; font-size:13px; color:var(--accent); }
h3{ font-family:var(--f-display); font-size:18px; line-height:1.25; margin:2px 0 0; text-wrap:balance; }
.puces{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }
.puce{ font-size:12px; color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:1px 8px; }
.puce.fort{ color:var(--accent); border-color:var(--accent); }
.desc, .joindre, .note, .fichier{ margin:0; }
.joindre, .fichier{ font-size:13.5px; color:var(--muted); }
.note{ font-size:14px; border:1px dashed var(--line); border-radius:8px; padding:8px 12px; }
code{ font-family:var(--f-mono); font-size:.92em; }
.bloc{ display:grid; gap:6px; min-width:0; }
.bloc-tete{ display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; }
.etiquette{ font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); font-weight:600; }
pre{ margin:0; font-family:var(--f-mono); font-size:12.5px; line-height:1.6; white-space:pre-wrap; overflow-wrap:anywhere;
  background:var(--sunk); border:1px solid var(--line); border-radius:8px; padding:10px 12px; }
button.copier{ font:600 13px var(--f-text); color:var(--on-accent); background:var(--accent); border:0; border-radius:8px; padding:7px 14px; cursor:pointer; }
button.copier.ok{ background:var(--neon); }
.fait{ display:flex; align-items:center; gap:6px; font-size:13px; color:var(--muted); white-space:nowrap; cursor:pointer; }
.fait input{ width:18px; height:18px; accent-color:var(--accent); }
article.fini h3, article.fini .desc{ color:var(--muted); }
footer{ font-size:13px; color:var(--muted); }
@media (prefers-reduced-motion: reduce){ *{ transition:none !important; scroll-behavior:auto !important; } }
"""

JS = r"""
(function(){
  var cases = Array.prototype.slice.call(document.querySelectorAll('.fait input'));
  var compte = document.getElementById('compte');
  function marque(cb){
    var art = cb.closest('article'); art.classList.toggle('fini', cb.checked);
    var lien = document.querySelector('.saut a[data-id="' + art.id + '"]'); if (lien) lien.classList.toggle('fini', cb.checked);
  }
  function maj(){ compte.textContent = cases.filter(function(c){ return c.checked; }).length + ' / ' + cases.length; }
  cases.forEach(function(cb){
    var k = 'lautre:' + cb.id;
    try { cb.checked = localStorage.getItem(k) === '1'; } catch (e) {}
    marque(cb);
    cb.addEventListener('change', function(){
      try { localStorage.setItem(k, cb.checked ? '1' : '0'); } catch (e) {}
      marque(cb); maj();
    });
  });
  maj();
  document.querySelectorAll('button.copier').forEach(function(b){
    b.addEventListener('click', function(){
      var pre = document.getElementById(b.getAttribute('data-cible'));
      var ok = function(){ b.textContent = 'Copié'; b.classList.add('ok'); setTimeout(function(){ b.textContent = 'Copier'; b.classList.remove('ok'); }, 1600); };
      var repli = function(){ var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Sélectionné : Ctrl+C'; };
      if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(pre.textContent).then(ok, repli); } else { repli(); }
    });
  });
})();
"""

page = ("<title>« L'AUTRE » · les prompts</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap">\n'
        f"<style>{CSS}</style>\n"
        '<div class="page"><header>'
        "<h1>« L'AUTRE » · les prompts</h1>"
        '<p class="sous">La pub vidéo de NEBULA · dessin animé 2D · 9:16 · environ 1 min · Google Flow</p>'
        '<ol class="etapes">'
        "<li><strong>Les références R0 à R5</strong>, une seule fois, dans Nano Banana Pro. <strong>R0, l'image de style, d'abord</strong> : joins-la à tout le reste, c'est elle qui garde le même dessin.</li>"
        "<li><strong>Pour chaque plan</strong> : l'image dans Nano Banana Pro (9:16, avec R0, les fiches des personnages présents et R3), puis l'animation dans Veo 3.1, mode Frames to Video, l'image en première image, 6 s (durée fixe), 2 à 3 prises. <strong>Une seule voix par clip</strong> : chaque prompt dit qui parle.</li>"
        "<li><strong>Enregistre la meilleure prise</strong> sous le nom du plan (<code>P01.mp4</code>, <code>P02.mp4</code>…) dans le dossier <code>_partage/pub-l-autre/</code>.</li>"
        "</ol>"
        '<p class="essai">Commence par <a href="#p02">P02</a> : c\'est le test de la voix et de l\'accent. S\'il sonne faux, on corrige avant de faire les autres. '
        "Pour changer une réplique, ne touche qu'au texte entre guillemets.</p>"
        '<p class="compte">Faits : <span id="compte">0</span></p>'
        f'<nav class="saut" aria-label="Aller à un plan">{"".join(sauts)}</nav>'
        "</header>"
        '<div class="acte"><h2>Les références</h2><span class="lumiere film">une seule fois</span></div>'
        + "".join(corps) +
        "<footer>Source : <code>_memoire/videos-pub/projets/01-l-autre.md</code> (le dossier complet, avec le montage, la carte et la publication).</footer>"
        f"</div>\n<script>{JS}</script>\n")
OUT.write_text(page, encoding="utf-8")
print(f"{len(refs)} références, {len(plans)} plans, {nb_code} prompts → {OUT}")
