# -*- coding: utf-8 -*-
"""
Fabrique le carnet de prospection à partir de `_donnees.py`.

Deux sorties :
  · `carnet-prospection.html` — le carnet, à ouvrir sur le téléphone. Chaque
    ligne a son bouton WhatsApp avec le message DÉJÀ ÉCRIT pour son métier, et
    son état (à contacter / écrit / rendez-vous / vendu / non). L'état est
    gardé dans le téléphone, on peut fermer et revenir.
  · `prospects-benin-togo.csv` — la même chose pour Excel ou Google Sheets,
    si on veut la partager à plusieurs partenaires.

    python _documents/nebula-agency/vente/prospection/_build.py
"""
import csv, io, sys
from pathlib import Path

ICI = Path(__file__).parent
sys.path.insert(0, str(ICI))
from _donnees import PROSPECTS

INDICATIF = {"BJ": "229", "TG": "228"}
PAYS = {"BJ": "Bénin", "TG": "Togo"}

# Le premier message, écrit pour le métier. Aucun prix : le prix se dit après
# la démonstration, jamais avant (cf. 13-PROSPECTION-BENIN-TOGO.md).
MESSAGES = {
    "couture": ("Bonjour, j'ai vu votre travail, c'est très propre.\n\n"
                "Une question rapide : vos clientes qui vous découvrent, "
                "elles voient vos modèles où ? Vous leur faites défiler la galerie de votre téléphone ?"),
    "restaurant": ("Bonjour, une question rapide : quand quelqu'un vous écrit pour demander "
                   "la carte et les prix, vous répondez comment ?\n\n"
                   "Vous renvoyez les photos une par une ?"),
    "patisserie": ("Bonjour, vos gâteaux donnent envie.\n\n"
                   "Une question : quand une cliente veut commander, elle voit vos modèles "
                   "et vos prix où ? Vous renvoyez des photos à chaque fois ?"),
}
METIER_MOT = {"couture": "Couture", "restaurant": "Restaurant", "patisserie": "Pâtisserie"}


def est_fixe(pays, num):
    """Un fixe n'a pas WhatsApp : on appelle, on n'écrit pas."""
    if pays == "BJ":
        return num.startswith("0121") or num.startswith("0120")
    return num.startswith("22")


def joli(pays, num):
    if not num:
        return ""
    if pays == "BJ":
        return f"{num[0:2]} {num[2:4]} {num[4:6]} {num[6:8]} {num[8:10]}"
    return f"{num[0:2]} {num[2:4]} {num[4:6]} {num[6:8]}"


def main():
    lignes = []
    for nom, pays, ville, quartier, metier, num in PROSPECTS:
        fixe = est_fixe(pays, num) if num else False
        lignes.append({
            "nom": nom, "pays": pays, "ville": ville, "quartier": quartier,
            "metier": metier, "num": num, "fixe": fixe,
            "international": (INDICATIF[pays] + num) if num else "",
        })

    # ---- CSV (point-virgule + BOM : Excel français l'ouvre proprement) ----
    p = ICI / "prospects-benin-togo.csv"
    with io.open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Nom", "Pays", "Ville", "Quartier", "Métier", "Numéro",
                    "Format international", "WhatsApp possible", "État", "Notes"])
        for l in lignes:
            w.writerow([l["nom"], PAYS[l["pays"]], l["ville"], l["quartier"],
                        METIER_MOT[l["metier"]], joli(l["pays"], l["num"]),
                        "+" + l["international"] if l["international"] else "",
                        "non (fixe)" if l["fixe"] else ("oui" if l["num"] else "numéro absent"),
                        "à contacter", ""])
    print(f"  {p.name:32} {len(lignes)} lignes")

    # ---- le carnet ----
    import json
    donnees = json.dumps(lignes, ensure_ascii=False)
    msgs = json.dumps(MESSAGES, ensure_ascii=False)
    html = GABARIT.replace("__DONNEES__", donnees).replace("__MESSAGES__", msgs)
    p = ICI / "carnet-prospection.html"
    io.open(p, "w", encoding="utf-8", newline="").write(html)
    print(f"  {p.name:32} {len(html)//1024} Ko")

    par_pays = {}
    for l in lignes:
        par_pays.setdefault(PAYS[l["pays"]], []).append(l)
    for k, v in par_pays.items():
        metiers = {}
        for l in v:
            metiers[METIER_MOT[l["metier"]]] = metiers.get(METIER_MOT[l["metier"]], 0) + 1
        print(f"    {k} : {len(v)}  ({', '.join(f'{a} {b}' for a, b in sorted(metiers.items()))})")
    fixes = sum(1 for l in lignes if l["fixe"])
    print(f"    dont {fixes} fixes (à appeler, pas de WhatsApp)")
    return 0


GABARIT = r"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Carnet de prospection · Bénin et Togo · NEBULA</title>
<style>
  :root{
    --encre:#14131a; --papier:#f6f4ef; --sourd:#6d6a7d; --trait:#e2ded4;
    --carte:#fffdf9; --accent:#5b3df5; --bien:#0a7d4f; --attente:#9a6400; --non:#a3202f;
  }
  @media (prefers-color-scheme: dark){
    :root{ --encre:#eeecf5; --papier:#111017; --sourd:#9c99ae; --trait:#282634;
           --carte:#191824; --accent:#9d86ff; --bien:#3ddb95; --attente:#f0b23f; --non:#ff7085; }
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--papier);color:var(--encre);
       font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
       padding-bottom:env(safe-area-inset-bottom)}
  header{position:sticky;top:0;z-index:5;background:var(--papier);
         border-bottom:1px solid var(--trait);padding:12px 14px 10px}
  h1{margin:0 0 2px;font-size:1.05rem;letter-spacing:-.01em}
  .sous{color:var(--sourd);font-size:.8rem;margin-bottom:9px}
  .avance{height:6px;border-radius:99px;background:var(--trait);overflow:hidden;margin-bottom:10px}
  .avance i{display:block;height:100%;background:var(--accent);width:0;transition:width .3s ease-out}
  input[type=search]{width:100%;padding:11px 12px;border:1px solid var(--trait);border-radius:11px;
    background:var(--carte);color:var(--encre);font-size:16px;margin-bottom:8px}
  .filtres{display:flex;gap:6px;overflow-x:auto;padding-bottom:2px;-webkit-overflow-scrolling:touch}
  .f{flex:0 0 auto;min-height:36px;padding:7px 13px;border-radius:99px;border:1px solid var(--trait);
     background:transparent;color:var(--sourd);font-size:.82rem;font-weight:600;cursor:pointer}
  .f[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:#fff}
  main{padding:12px 14px 40px;max-width:820px;margin:0 auto}
  .p{background:var(--carte);border:1px solid var(--trait);border-radius:13px;padding:12px 13px;margin-bottom:9px}
  .p[data-etat=vendu]{border-color:var(--bien)}
  .p[data-etat=non]{opacity:.5}
  .nom{font-weight:650;line-height:1.25;margin-bottom:2px}
  .lieu{color:var(--sourd);font-size:.79rem;margin-bottom:9px}
  .tel{font-variant-numeric:tabular-nums;letter-spacing:.02em}
  .actes{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:9px}
  .b{flex:1 1 auto;min-height:44px;display:inline-flex;align-items:center;justify-content:center;gap:6px;
     padding:0 14px;border-radius:11px;border:1px solid var(--trait);background:transparent;
     color:var(--encre);font-size:.85rem;font-weight:600;text-decoration:none;cursor:pointer}
  .b.w{background:var(--accent);border-color:var(--accent);color:#fff}
  .etats{display:flex;gap:5px;flex-wrap:wrap}
  .e{min-height:34px;padding:5px 10px;border-radius:9px;border:1px solid var(--trait);
     background:transparent;color:var(--sourd);font-size:.76rem;font-weight:600;cursor:pointer}
  .e[aria-pressed=true]{color:#fff;border-color:transparent}
  .e[data-v=ecrit][aria-pressed=true]{background:var(--attente)}
  .e[data-v=rdv][aria-pressed=true]{background:var(--accent)}
  .e[data-v=vendu][aria-pressed=true]{background:var(--bien)}
  .e[data-v=non][aria-pressed=true]{background:var(--non)}
  .vide{text-align:center;color:var(--sourd);padding:40px 20px}
  .avert{background:var(--carte);border:1px solid var(--trait);border-left:none;
         border-radius:13px;padding:12px 13px;margin-bottom:14px;font-size:.82rem;color:var(--sourd)}
  .avert b{color:var(--encre)}
  @media print{ header{position:static} .actes,.etats,.filtres,input[type=search]{display:none} }
</style></head><body>

<header>
  <h1>Carnet de prospection</h1>
  <div class="sous" id="compte"></div>
  <div class="avance"><i id="barre"></i></div>
  <input type="search" id="q" placeholder="Chercher un nom, une ville, un quartier" autocomplete="off">
  <div class="filtres" id="filtres"></div>
</header>

<main>
  <div class="avert">
    <b>Avant d'écrire, regardez 10 secondes s'il a déjà une page Facebook ou un site.</b>
    Ces numéros viennent d'un annuaire consulté le 3 août 2026 : certains ont pu changer,
    certains commerces ont pu fermer. Le premier contact sert aussi à vérifier.
    Les <b>fixes</b> n'ont pas WhatsApp, on les appelle.
  </div>
  <div id="liste"></div>
</main>

<script>
const P = __DONNEES__;
const MSG = __MESSAGES__;
const CLE = 'nebula_prospection_v1';
const MOT = {couture:'Couture', restaurant:'Restaurant', patisserie:'Pâtisserie'};
let etats = {};
try { etats = JSON.parse(localStorage.getItem(CLE) || '{}'); } catch(e) { etats = {}; }
const cle = p => p.nom + '|' + p.ville;
let fPays = '', fMetier = '', fEtat = '', q = '';

function garder(){ try { localStorage.setItem(CLE, JSON.stringify(etats)); } catch(e){} }

function lien(p){
  const t = encodeURIComponent(MSG[p.metier] || MSG.restaurant);
  return 'https://wa.me/' + p.international + '?text=' + t;
}

function visibles(){
  const t = q.trim().toLowerCase();
  return P.filter(p => {
    if (fPays && p.pays !== fPays) return false;
    if (fMetier && p.metier !== fMetier) return false;
    const e = etats[cle(p)] || '';
    if (fEtat === 'reste' && e) return false;
    if (fEtat && fEtat !== 'reste' && e !== fEtat) return false;
    if (t && !(p.nom + ' ' + p.ville + ' ' + p.quartier).toLowerCase().includes(t)) return false;
    return true;
  });
}

function dessiner(){
  const l = visibles();
  const boite = document.getElementById('liste');
  boite.innerHTML = '';
  if (!l.length){ boite.innerHTML = '<div class="vide">Rien avec ces filtres.</div>'; }
  l.forEach(p => {
    const e = etats[cle(p)] || '';
    const d = document.createElement('div');
    d.className = 'p'; if (e) d.dataset.etat = e;
    const lieu = [p.quartier, p.ville].filter(Boolean).join(' · ');
    let actes = '';
    if (!p.num) {
      actes = '<span class="b" style="cursor:default;color:var(--sourd)">Numéro à trouver</span>';
    } else if (p.fixe) {
      actes = '<a class="b" href="tel:+' + p.international + '">Appeler (fixe)</a>';
    } else {
      actes = '<a class="b w" href="' + lien(p) + '" target="_blank" rel="noopener">Écrire sur WhatsApp</a>'
            + '<a class="b" href="tel:+' + p.international + '">Appeler</a>';
    }
    d.innerHTML =
      '<div class="nom">' + p.nom + '</div>' +
      '<div class="lieu">' + MOT[p.metier] + (lieu ? ' · ' + lieu : '') +
        (p.num ? ' · <span class="tel">+' + p.international + '</span>' : '') + '</div>' +
      '<div class="actes">' + actes + '</div>' +
      '<div class="etats">' +
        ['ecrit:Écrit','rdv:Rendez-vous','vendu:Vendu','non:Non'].map(x => {
          const [v, mot] = x.split(':');
          return '<button class="e" data-v="' + v + '" aria-pressed="' + (e === v) + '">' + mot + '</button>';
        }).join('') +
      '</div>';
    d.querySelectorAll('.e').forEach(b => b.onclick = () => {
      const v = b.dataset.v;
      if (etats[cle(p)] === v) delete etats[cle(p)]; else etats[cle(p)] = v;
      garder(); dessiner();
    });
    boite.appendChild(d);
  });
  const traites = P.filter(p => etats[cle(p)]).length;
  const vendus = P.filter(p => etats[cle(p)] === 'vendu').length;
  document.getElementById('compte').textContent =
    l.length + ' affichés sur ' + P.length + ' · ' + traites + ' traités · ' + vendus + ' vendus';
  document.getElementById('barre').style.width = (traites / P.length * 100) + '%';
}

const FILTRES = [
  ['pays','','Tout'], ['pays','BJ','Bénin'], ['pays','TG','Togo'],
  ['metier','couture','Couture'], ['metier','restaurant','Restaurants'],
  ['etat','reste','Pas encore faits'], ['etat','rdv','Rendez-vous'], ['etat','vendu','Vendus'],
];
const zone = document.getElementById('filtres');
FILTRES.forEach(([type, val, mot]) => {
  const b = document.createElement('button');
  b.className = 'f'; b.textContent = mot; b.dataset.type = type; b.dataset.val = val;
  b.onclick = () => {
    if (type === 'pays') fPays = (fPays === val ? '' : val);
    if (type === 'metier') fMetier = (fMetier === val ? '' : val);
    if (type === 'etat') fEtat = (fEtat === val ? '' : val);
    if (type === 'pays' && val === '') { fPays = ''; fMetier = ''; fEtat = ''; }
    majFiltres(); dessiner();
  };
  zone.appendChild(b);
});
function majFiltres(){
  zone.querySelectorAll('.f').forEach(b => {
    const t = b.dataset.type, v = b.dataset.val;
    const on = (t === 'pays' && v === '') ? (!fPays && !fMetier && !fEtat)
             : (t === 'pays' ? fPays === v : t === 'metier' ? fMetier === v : fEtat === v);
    b.setAttribute('aria-pressed', on);
  });
}
document.getElementById('q').oninput = ev => { q = ev.target.value; dessiner(); };
majFiltres(); dessiner();
</script>
</body></html>
"""

if __name__ == "__main__":
    sys.exit(main())
