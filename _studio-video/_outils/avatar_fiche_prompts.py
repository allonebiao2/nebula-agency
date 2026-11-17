# Fabrique la fiche « Prompts du mini-Mongazi » (HTML, un bouton Copier par prompt) à partir du fichier qui fait autorité.
# Les prompts ne sont jamais recopiés à la main : ils sont LUS dans
# _documents/nebula-agency/marketing/TIKTOK-MONGAZI-AVATAR.md.
# Usage : python _studio-video/_outils/avatar_fiche_prompts.py <sortie.html>, puis republier la page à la même adresse
# (https://claude.ai/artifact/FJRogAtCUgXEi4NCNHLN6H, outil Artifact avec `url`, après l'avoir lue).
import html, pathlib, re, sys

SRC = pathlib.Path(__file__).resolve().parents[2] / "_documents" / "nebula-agency" / "marketing" / "TIKTOK-MONGAZI-AVATAR.md"
OUT = pathlib.Path(sys.argv[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # la console de Windows est en cp1252

items, cur, dans_code, code, section = [], None, False, [], None
etapes, conseils = [], []
for l in SRC.read_text(encoding="utf-8").splitlines():
    s = l.strip()
    if s.startswith("```"):
        if not dans_code:
            dans_code, code = True, []
        else:
            dans_code = False
            if cur is not None:
                cur["prompt"] = "\n".join(code)
        continue
    if dans_code:
        code.append(l)
        continue
    if l.startswith("## "):
        section, cur = l[3:].strip(), None
        continue
    m = re.match(r"^### ([AM]\d+) · (.+)$", l)
    if m:
        cur = {"code": m.group(1), "titre": m.group(2), "meta": {}, "prompt": None}
        items.append(cur)
        continue
    if section == "La marche à suivre" and re.match(r"^\d+\. ", s):
        etapes.append(s.split(". ", 1)[1])
        continue
    if section == "Bon à savoir" and s.startswith("- "):
        conseils.append(s[2:])
        continue
    m = re.match(r"^- (À joindre|Format|Fichier|Note) : (.+)$", s)
    if m and cur is not None:
        cur["meta"][m.group(1)] = m.group(2)

poses = [i for i in items if i["code"].startswith("A") and i["code"] != "A00"]
modifs = [i for i in items if i["code"].startswith("M")]
assert len(items) == 15 and len(poses) == 12 and len(modifs) == 2, [i["code"] for i in items]
assert all(i["prompt"] for i in items), [i["code"] for i in items if not i["prompt"]]
PARLE = [p["code"] for p in poses][:9]  # A01 à A09 : les poses où il parle (bouche ouverte et yeux fermés)
TOTAL = 1 + len(poses) + len(PARLE) * len(modifs)


def fmt(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", t)


n_pre = 0


def article(it):
    global n_pre
    n_pre += 1
    i, pid = it["code"].lower(), f"t{n_pre}"
    meta = it["meta"]
    lignes = "".join(
        f'<p class="meta"><span class="cle">{k}</span> {fmt(meta[k])}</p>' for k in ("À joindre", "Format", "Fichier") if k in meta)
    if it["code"].startswith("M"):
        fait = '<div class="faits" role="group" aria-label="Poses déjà modifiées">' + "".join(
            f'<label for="fait-{i}-{p.lower()}"><input type="checkbox" id="fait-{i}-{p.lower()}"> {p}</label>' for p in PARLE) + "</div>"
        coche = ""
    else:
        fait = ""
        coche = f'<label class="fait" for="fait-{i}"><input type="checkbox" id="fait-{i}"> Fait</label>'
    etiquette = "Modification · Nano Banana Pro" if it["code"].startswith("M") else "Image · Nano Banana Pro"
    return (f'<article id="{i}"><div class="tete"><div class="tete-g"><span class="code">{it["code"]}</span>'
            f'<h3>{fmt(it["titre"])}</h3></div>{coche}</div>'
            + lignes
            + (f'<p class="note">{fmt(meta["Note"])}</p>' if "Note" in meta else "")
            + f'<div class="bloc"><div class="bloc-tete"><span class="etiquette">{etiquette}</span>'
              f'<button type="button" class="copier" data-cible="{pid}">Copier</button></div>'
              f'<pre id="{pid}">{html.escape(it["prompt"], quote=False)}</pre></div>'
            + fait + "</article>")


def groupe(nom, sous, liste):
    return (f'<section class="groupe"><div class="acte"><h2>{nom}</h2><span class="lumiere">{sous}</span></div>'
            + "".join(article(x) for x in liste) + "</section>")


sauts = "".join(f'<a href="#{x["code"].lower()}" data-id="{x["code"].lower()}">{x["code"]}</a>' for x in items)

CSS = r"""
:root{
  /* La feuille de modèle d'un personnage 3D : fond gris de studio, le violet NEBULA de son sweat en accent. */
  --bg:#f2f1f6; --surface:#ffffff; --sunk:#eeecf4; --fg:#16131f; --muted:#5d5870; --line:#dad6e4;
  --accent:#9333ea; --accent-soft:#f3e9fd; --on-accent:#ffffff; --ok:#26704f;
  --f-display:"Space Grotesk", ui-sans-serif, system-ui, sans-serif;
  --f-text:"Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono:"JetBrains Mono", ui-monospace, Consolas, "SFMono-Regular", monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0e0c14; --surface:#16131f; --sunk:#110f18; --fg:#ebe8f2; --muted:#a29cb3; --line:#2b2639;
  --accent:#c79bff; --accent-soft:#241a35; --on-accent:#120c1c; --ok:#7fd3a6; color-scheme:dark; } }
:root[data-theme="dark"]{
  --bg:#0e0c14; --surface:#16131f; --sunk:#110f18; --fg:#ebe8f2; --muted:#a29cb3; --line:#2b2639;
  --accent:#c79bff; --accent-soft:#241a35; --on-accent:#120c1c; --ok:#7fd3a6; color-scheme:dark; }
body{ background:var(--bg); color:var(--fg); font-family:var(--f-text); font-size:15px; line-height:1.55;
  padding-left:max(16px, env(safe-area-inset-left,0px)); padding-right:max(16px, env(safe-area-inset-right,0px));
  padding-block:28px 64px; }
.page{ max-width:860px; margin:0 auto; display:grid; gap:22px; }
header{ display:grid; gap:14px; }
h1{ font-family:var(--f-display); font-size:clamp(28px,5vw,40px); line-height:1.1; margin:0; text-wrap:balance; letter-spacing:-.01em; }
.sous{ color:var(--muted); margin:0; }
.etapes{ margin:0; padding-left:1.3em; display:grid; gap:6px; max-width:68ch; }
.conseils{ background:var(--accent-soft); border:1px solid var(--accent); border-radius:10px; padding:12px 14px 12px 32px; margin:0; display:grid; gap:4px; }
.compte{ margin:0; font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums; }
.saut{ display:flex; flex-wrap:wrap; gap:6px; }
.saut a{ font-family:var(--f-mono); font-size:12.5px; text-decoration:none; color:var(--fg); border:1px solid var(--line);
  border-radius:999px; padding:3px 9px; background:var(--surface); }
.saut a.fini{ color:var(--muted); text-decoration:line-through; }
.saut a:focus-visible, button:focus-visible, input:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }
.groupe{ display:grid; gap:14px; }
.acte{ display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; margin-top:10px; }
.acte h2{ font-family:var(--f-display); font-size:21px; margin:0; }
.lumiere{ font-size:11.5px; letter-spacing:.06em; text-transform:uppercase; padding:2px 8px; border-radius:999px; border:1px solid currentColor; color:var(--accent); }
article{ background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:16px; display:grid; gap:10px; min-width:0; scroll-margin-top:16px; }
.tete{ display:flex; gap:12px; align-items:flex-start; justify-content:space-between; }
.tete-g{ min-width:0; }
.code{ font-family:var(--f-mono); font-weight:600; font-size:13px; color:var(--accent); }
h3{ font-family:var(--f-display); font-size:18px; line-height:1.25; margin:2px 0 0; text-wrap:balance; }
.meta{ margin:0; font-size:13.5px; color:var(--muted); }
.cle{ display:inline-block; min-width:5.6em; font-size:11.5px; text-transform:uppercase; letter-spacing:.05em; font-weight:600; color:var(--fg); }
.note{ margin:0; font-size:14px; border:1px dashed var(--line); border-radius:8px; padding:8px 12px; }
code{ font-family:var(--f-mono); font-size:.92em; }
.bloc{ display:grid; gap:6px; min-width:0; }
.bloc-tete{ display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; }
.etiquette{ font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); font-weight:600; }
pre{ margin:0; font-family:var(--f-mono); font-size:12.5px; line-height:1.6; white-space:pre-wrap; overflow-wrap:anywhere;
  background:var(--sunk); border:1px solid var(--line); border-radius:8px; padding:10px 12px; }
button.copier{ font:600 13px var(--f-text); color:var(--on-accent); background:var(--accent); border:0; border-radius:8px; padding:7px 14px; cursor:pointer; }
button.copier.ok{ background:var(--ok); }
.fait{ display:flex; align-items:center; gap:6px; font-size:13px; color:var(--muted); white-space:nowrap; cursor:pointer; }
.faits{ display:flex; flex-wrap:wrap; gap:6px 12px; font-family:var(--f-mono); font-size:12.5px; color:var(--muted); }
.faits label{ display:flex; align-items:center; gap:5px; cursor:pointer; }
input[type="checkbox"]{ width:18px; height:18px; accent-color:var(--accent); }
article.fini h3, article.fini .note{ color:var(--muted); }
footer{ font-size:13px; color:var(--muted); }
@media (prefers-reduced-motion: reduce){ *{ transition:none !important; scroll-behavior:auto !important; } }
"""

JS = r"""
(function(){
  var cases = Array.prototype.slice.call(document.querySelectorAll('article input[type="checkbox"]'));
  var compte = document.getElementById('compte');
  function marque(art){
    var c = art.querySelectorAll('input[type="checkbox"]'), tous = c.length > 0;
    for (var i = 0; i < c.length; i++) if (!c[i].checked) tous = false;
    art.classList.toggle('fini', tous);
    var lien = document.querySelector('.saut a[data-id="' + art.id + '"]'); if (lien) lien.classList.toggle('fini', tous);
  }
  function maj(){ compte.textContent = cases.filter(function(c){ return c.checked; }).length + ' / ' + cases.length; }
  cases.forEach(function(cb){
    var k = 'avatar:' + cb.id;
    try { cb.checked = localStorage.getItem(k) === '1'; } catch (e) {}
    cb.addEventListener('change', function(){
      try { localStorage.setItem(k, cb.checked ? '1' : '0'); } catch (e) {}
      marque(cb.closest('article')); maj();
    });
  });
  document.querySelectorAll('article').forEach(marque);
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

page = ("<title>Prompts du mini-Mongazi</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap">\n'
        f"<style>{CSS}</style>\n"
        '<div class="page"><header>'
        "<h1>Le mini-Mongazi</h1>"
        f'<p class="sous">Ton avatar 3D · {TOTAL} images à générer dans Google Flow (Nano Banana Pro) · prompts en anglais</p>'
        '<ol class="etapes">' + "".join(f"<li>{fmt(e)}</li>" for e in etapes) + "</ol>"
        '<ul class="conseils">' + "".join(f"<li>{fmt(c)}</li>" for c in conseils) + "</ul>"
        f'<p class="compte">Faits : <span id="compte">0 / {TOTAL}</span></p>'
        f'<nav class="saut" aria-label="Aller à une image">{sauts}</nav>'
        "</header>"
        + groupe("La fiche", "d'abord, une seule fois", [items[0]])
        + groupe("Les 12 poses", "A01 d'abord, puis les autres", poses)
        + groupe("La bouche et les yeux", "sur A01 à A09", modifs)
        + "<footer>Source : <code>_documents/nebula-agency/marketing/TIKTOK-MONGAZI-AVATAR.md</code>. "
          "On corrige le fichier, puis on refait la page.</footer>"
        f"</div>\n<script>{JS}</script>\n")
OUT.write_text(page, encoding="utf-8")
print(f"{len(items)} prompts, {TOTAL} images → {OUT}")
