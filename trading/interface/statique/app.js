/* NEBULA Trader · interface
   Aucune bibliothèque. Tout texte venu du serveur passe par esc() avant d'entrer
   dans la page : le journal et la conversation contiennent du texte libre. */
"use strict";

const JETON = document.querySelector('meta[name="jeton"]').content;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const vue = $("#vue");
let ETAT = {};
let ROUTE = "";
let minuterieVue = null;

// ------------------------------------------------------------------ outils
function esc(v) {
  return String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const nf = (n, d = 2) => (n == null || Number.isNaN(n)) ? "·" :
  new Intl.NumberFormat("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }).format(n);
const signe = (n, d = 2) => n == null ? "·" : (n > 0 ? "+" : "") + nf(n, d);
const pct = (n, d = 2) => n == null ? "·" : nf(n, d) + " %";
const classe = n => n > 0 ? "gain" : n < 0 ? "perte" : "";
function heure(iso) {
  if (!iso) return "·";
  const d = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  return d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}
function dateCourte(iso) {
  if (!iso) return "·";
  const d = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  const auj = new Date();
  if (d.toDateString() === auj.toDateString()) return heure(iso);
  return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "short" }) + " " + heure(iso);
}

async function api(chemin, options = {}) {
  const init = { headers: { "Content-Type": "application/json", "X-Jeton": JETON }, ...options };
  if (options.corps !== undefined) { init.method = init.method || "POST"; init.body = JSON.stringify(options.corps); }
  const r = await fetch(chemin, init);
  let d = null;
  try { d = await r.json(); } catch { /* réponse vide */ }
  if (!r.ok) throw new Error((d && (d.detail || d.erreur || (d.erreurs || []).join("\n"))) || `erreur ${r.status}`);
  return d;
}

function toast(texte, erreur = false) {
  const t = document.createElement("div");
  t.className = "toast" + (erreur ? " erreur" : "");
  t.textContent = texte;
  $("#toasts").append(t);
  setTimeout(() => t.remove(), erreur ? 7000 : 3500);
}

function confirmer({ titre, corps, libelleOk = "Confirmer", danger = false, saisie = null }) {
  const d = $("#dialogue");
  $("#dialogue-titre").textContent = titre;
  $("#dialogue-corps").innerHTML = corps;
  const ok = $("#dialogue-ok");
  ok.textContent = libelleOk;
  ok.className = "btn " + (danger ? "btn-danger" : "btn-primaire");
  const champ = $("#dialogue-saisie-champ"), entree = $("#dialogue-saisie");
  champ.hidden = !saisie;
  entree.value = "";
  if (saisie) {
    $("#dialogue-saisie-libelle").textContent = `Écris ${saisie} pour confirmer`;
    ok.disabled = true;
    entree.oninput = () => { ok.disabled = entree.value.trim().toUpperCase() !== saisie; };
  } else ok.disabled = false;
  d.showModal();
  if (saisie) entree.focus();
  return new Promise(res => { d.onclose = () => res(d.returnValue === "ok"); });
}

function courbeSVG(points, { hauteur = 220, cle = "equite" } = {}) {
  if (!points || points.length < 2) return `<div class="vide">Pas encore assez de points pour tracer une courbe.<br>Elle se remplit à chaque minute où l'agent tourne.</div>`;
  const L = 800, H = hauteur, m = { h: 12, b: 22, g: 4, d: 64 };
  const vals = points.map(p => p[cle] ?? p[1]);
  let min = Math.min(...vals), max = Math.max(...vals);
  if (max === min) { max += 1; min -= 1; }
  const x = i => m.g + (i / (vals.length - 1)) * (L - m.g - m.d);
  const y = v => m.h + (1 - (v - min) / (max - min)) * (H - m.h - m.b);
  const trace = vals.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("");
  const aire = `${trace}L${x(vals.length - 1).toFixed(1)},${H - m.b}L${x(0).toFixed(1)},${H - m.b}Z`;
  const t0 = points[0].ts ?? points[0][0], t1 = points.at(-1).ts ?? points.at(-1)[0];
  // Le tracé s'étire à la largeur disponible ; les libellés restent en HTML,
  // sinon l'étirement du SVG écrase le texte.
  return `<div class="courbe-cadre" style="--h:${H}px">
    <svg class="courbe" viewBox="0 0 ${L} ${H}" preserveAspectRatio="none" role="img" aria-label="Courbe d'équité de ${nf(vals[0])} à ${nf(vals.at(-1))}">
    <defs><linearGradient id="degrade" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="var(--accent)" stop-opacity=".28"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></linearGradient></defs>
    <line class="grille-l" x1="0" x2="${L - m.d}" y1="${y(max)}" y2="${y(max)}" vector-effect="non-scaling-stroke"/><line class="grille-l" x1="0" x2="${L - m.d}" y1="${y(min)}" y2="${y(min)}" vector-effect="non-scaling-stroke"/>
    <path class="aire" d="${aire}"/><path class="ligne" d="${trace}" vector-effect="non-scaling-stroke"/>
    </svg>
    <span class="courbe-max" style="top:${(100 * y(max) / H).toFixed(2)}%">${nf(max, 0)}</span>
    <span class="courbe-min" style="top:${(100 * y(min) / H).toFixed(2)}%">${nf(min, 0)}</span>
    <div class="courbe-dates"><span>${esc(String(t0).slice(0, 10))}</span><span>${esc(String(t1).slice(0, 10))}</span></div>
  </div>`;
}

function verrousBarre(verrous) {
  const par = {};
  (verrous || []).forEach(v => { par[v.n] = v; });
  const segments = [1, 2, 3, 4, 5, 6, 7, 8].map(n => {
    const v = par[n];
    return `<i class="verrou ${v ? (v.passe ? "ok" : "non") : ""}" title="${v ? esc(`Q${n} ${v.question}`) : "non évalué"}"></i>`;
  }).join("");
  return `<div class="verrous" aria-hidden="true">${segments}</div>
    <div class="verrous-legende" aria-hidden="true"><span>Thèse</span><span>Stop</span><span>Risque</span><span>R:R</span><span>Annonces</span><span>État</span><span>Discipline</span><span>Marché</span></div>`;
}
function miniVerrous(verrous) {
  const par = {};
  (verrous || []).forEach(v => { par[v.n] = v; });
  return `<span class="mini-verrous" aria-label="${(verrous || []).filter(v => v.passe).length} verrous sur 8 passés">${[1, 2, 3, 4, 5, 6, 7, 8].map(n => `<i class="${par[n] ? (par[n].passe ? "ok" : "non") : ""}"></i>`).join("")}</span>`;
}
function listeVerrous(verrous) {
  return `<ul class="liste-verrous">${(verrous || []).map(v => `<li>
    <span class="marque-v ${v.passe ? "gain" : "perte"}" aria-label="${v.passe ? "passé" : "refusé"}">${v.passe ? "✓" : "✕"}</span>
    <span class="q">${v.maison ? "maison" : "Q" + v.n}</span>
    <span><b>${esc(v.question)}</b><br><span class="d">${esc(v.detail)}</span></span></li>`).join("")}</ul>`;
}
const VERDICTS = { pris: ["Pris", "gain"], refuse: ["Refusé", "perte"], observe: ["Observé", "accent"], echec: ["Échec", "alerte"] };
const etiquetteVerdict = v => { const [t, c] = VERDICTS[v] || [v, ""]; return `<span class="etiquette ${c}">${esc(t)}</span>`; };
function jauge(libelle, valeur, limite, { unite = " %", inverse = false, texte = null } = {}) {
  const ratio = limite ? Math.max(0, Math.min(1, (inverse ? -valeur : valeur) / limite)) : 0;
  const niveau = ratio >= .85 ? "haut" : ratio >= .5 ? "moyen" : "";
  return `<div class="jauge"><div class="jauge-tete"><span>${esc(libelle)}</span><b>${texte ?? `${nf(valeur, unite === " %" ? 2 : 0)}${unite} / ${nf(limite, unite === " %" ? 1 : 0)}${unite}`}</b></div>
    <div class="jauge-piste"><div class="jauge-remplie ${niveau}" style="transform:scaleX(${ratio.toFixed(3)})"></div></div></div>`;
}
function markdownLeger(texte) {
  const lignes = esc(texte).split("\n");
  let html = "", liste = false;
  for (const l of lignes) {
    const g = l.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
    if (/^\s*[-•]\s+/.test(l)) { if (!liste) { html += "<ul>"; liste = true; } html += `<li>${g.replace(/^\s*[-•]\s+/, "")}</li>`; }
    else { if (liste) { html += "</ul>"; liste = false; } if (g.trim()) html += `<p>${g}</p>`; }
  }
  return html + (liste ? "</ul>" : "");
}

// ------------------------------------------------------------------ barre et état
const MODES_TXT = { observation: "Observation", demo: "Démo", reel: "Réel" };
async function rafraichirEtat() {
  try { ETAT = await api("/api/etat"); } catch (e) { $("#connexion span").textContent = "Interface déconnectée de l'agent"; return; }
  const cx = ETAT.connexion || {};
  $("#connexion").innerHTML = `<i class="voyant ${cx.ok ? "ok" : "ko"}"></i><span title="${esc(cx.message)}">${esc(cx.message || "…")}</span>`;
  $$("#modes button").forEach(b => b.setAttribute("aria-checked", String(b.dataset.mode === ETAT.mode)));
  const pause = $("#btn-pause");
  pause.textContent = ETAT.pause ? "Reprendre" : "Pause";
  pause.className = "btn" + (ETAT.pause ? " btn-succes" : "");
  $("#pied-licence").textContent = ETAT.licence?.valide ? `Licence ${ETAT.licence.edition}` : "Évaluation";
  $("#pastille-propositions").hidden = !(ETAT.propositions || []).length;

  const bandeau = $("#bandeau");
  let msg = "", niveau = "alerte";
  if (ETAT.arret_total) { msg = "<b>Arrêt total.</b> Le drawdown maximum a été atteint : l'agent ne prendra plus aucune position avant une reprise manuelle (Risque)."; niveau = "critique"; }
  else if (ETAT.pause) msg = `<b>En pause</b> : ${esc(ETAT.pause)}. Les positions ouvertes gardent leur stop chez le courtier.`;
  else if (ETAT.risque?.disjoncteur) msg = `<b>Disjoncteur</b> : ${esc(ETAT.risque.disjoncteur)}. Plus d'entrée jusqu'à la prochaine période.`;
  else if (cx.ok && ETAT.mode !== "observation" && !ETAT.peut_trader) msg = `<b>Aucun ordre ne part</b> : ${esc(ETAT.raison_mode)}.`;
  bandeau.hidden = !msg;
  bandeau.className = "bandeau " + niveau;
  bandeau.innerHTML = msg;

  if (ROUTE === "tableau") majTableau();
}

$("#modes").addEventListener("click", async e => {
  const b = e.target.closest("button[data-mode]");
  if (!b || b.dataset.mode === ETAT.mode) return;
  const mode = b.dataset.mode;
  let ok = true;
  if (mode === "demo") ok = await confirmer({ titre: "Passer en mode démo ?", corps: "<p>L'agent enverra de <b>vrais ordres</b> au courtier, mais uniquement si le compte branché est un compte <b>démo</b>. S'il détecte un compte réel, il refusera.</p>", libelleOk: "Passer en démo" });
  if (mode === "reel") ok = await confirmer({ titre: "Passer en mode RÉEL ?", danger: true, saisie: "REEL",
    corps: `<p>L'agent engagera <b>de l'argent réel</b>. Conditions vérifiées : licence valide, compte réel branché, plafond de capital défini dans les Réglages.</p><p>Aucune stratégie n'a encore prouvé d'avantage statistique sur quinze ans d'historique. Ne mets en jeu qu'un montant que tu peux perdre entièrement.</p>`, libelleOk: "Engager de l'argent réel" });
  if (!ok) return;
  try {
    const r = await api("/api/commande", { corps: { action: "mode", valeur: mode, confirme: true } });
    if (r && r.ok === false) toast(r.erreur, true); else toast(`Mode ${MODES_TXT[mode]} demandé`);
  } catch (err) { toast(err.message, true); }
  setTimeout(rafraichirEtat, 800);
});
$("#btn-pause").addEventListener("click", async () => {
  try { await api("/api/commande", { corps: { action: ETAT.pause ? "reprendre" : "pause", valeur: "depuis l'interface" } }); } catch (e) { toast(e.message, true); }
  setTimeout(rafraichirEtat, 700);
});
$("#btn-urgence").addEventListener("click", async () => {
  const ok = await confirmer({ titre: "Arrêt d'urgence", danger: true, libelleOk: "Tout fermer",
    corps: "<p>Toutes les positions ouvertes <b>par l'agent</b> seront fermées au prix du marché, puis il sera mis en pause. Tes trades manuels ne sont pas touchés.</p>" });
  if (!ok) return;
  try { await api("/api/commande", { corps: { action: "urgence", confirme: true } }); toast("Arrêt d'urgence envoyé"); } catch (e) { toast(e.message, true); }
  setTimeout(rafraichirEtat, 800);
});
$("#btn-theme").addEventListener("click", () => {
  const t = document.documentElement.dataset.theme === "clair" ? "sombre" : "clair";
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem("nebula-theme", t); } catch { /* stockage indisponible */ }
});
try { const t = localStorage.getItem("nebula-theme"); if (t) document.documentElement.dataset.theme = t; } catch { /* rien */ }

// ------------------------------------------------------------------ routeur
const ROUTES = {
  "": ["tableau", vueTableau], conversation: ["conversation", vueConversation], risque: ["risque", vueRisque],
  decisions: ["decisions", vueDecisions], trades: ["trades", vueTrades], strategies: ["strategies", vueStrategies],
  reglages: ["reglages", vueReglages], installation: ["installation", vueInstallation],
};
async function naviguer() {
  const cle = location.hash.replace(/^#\/?/, "").split("?")[0];
  const [nom, rendre] = ROUTES[cle] || ROUTES[""];
  ROUTE = nom;
  clearInterval(minuterieVue);
  $$(".nav a[data-route]").forEach(a => a.classList.toggle("actif", a.dataset.route === nom));
  vue.innerHTML = `<div class="vide">Chargement…</div>`;
  window.scrollTo(0, 0);
  try { await rendre(); } catch (e) { vue.innerHTML = `<div class="vide">Impossible de charger cette page : ${esc(e.message)}</div>`; }
  vue.focus({ preventScroll: true });
}
window.addEventListener("hashchange", naviguer);

// ------------------------------------------------------------------ tableau de bord
let periodeCourbe = 30;
async function vueTableau() {
  vue.innerHTML = `
    <div class="entete-vue"><div><h1>Tableau de bord</h1><p class="sous-titre">Ce que l'agent voit, ce qu'il décide, et pourquoi.</p></div>
      <button class="btn" id="btn-analyser">Analyser la dernière bougie</button></div>
    <div class="grille kpi" id="kpi"></div>
    <div class="grille deux" style="margin-top:16px">
      <div class="pile">
        <section class="carte" id="derniere-decision"></section>
        <section class="carte"><div class="carte-tete"><h2>Équité</h2>
          <div class="segmentes" id="periodes">${[[7, "7 j"], [30, "30 j"], [90, "90 j"], [365, "1 an"]].map(([j, t]) => `<button data-j="${j}" aria-pressed="${j === periodeCourbe}">${t}</button>`).join("")}</div></div>
          <div id="courbe"></div></section>
        <section class="carte" id="positions"></section>
      </div>
      <div class="pile">
        <section class="carte" id="prochaine"></section>
        <section class="carte"><div class="carte-tete"><h2>Ce que fait l'agent</h2><span class="discret">en direct</span></div><ul class="flux" id="flux" aria-live="polite"></ul></section>
      </div>
    </div>`;
  $("#btn-analyser").onclick = async () => { await api("/api/commande", { corps: { action: "analyser" } }); toast("Analyse demandée : résultat dans le flux d'ici quelques secondes"); };
  $("#periodes").onclick = e => { const b = e.target.closest("button"); if (!b) return; periodeCourbe = +b.dataset.j; $$("#periodes button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); chargerCourbe(); };
  majTableau(); chargerCourbe(); chargerFlux(); chargerDerniereDecision();
  let tours = 0;
  minuterieVue = setInterval(() => {
    chargerFlux(); chargerDerniereDecision();
    if (++tours % 12 === 0) chargerCourbe();
  }, 5000);
}
function majTableau() {
  const k = $("#kpi");
  if (!k) return;
  const c = ETAT.compte, r = ETAT.risque || {}, lim = r.limites || {};
  const dev = c ? (c.cent ? c.devise_reelle : c.devise) : "";
  k.innerHTML = c ? `
    <div class="carte"><div class="kpi-libelle">Équité</div><div class="kpi-valeur">${nf(c.cent ? c.equite / 100 : c.equite)} <small>${esc(dev)}</small></div><div class="kpi-detail">${esc(c.type_compte)}</div></div>
    <div class="carte"><div class="kpi-libelle">Aujourd'hui</div><div class="kpi-valeur ${classe(r.pnl_jour)}">${pct(r.pnl_jour_pct)}</div><div class="kpi-detail">limite -${nf(lim.perte_max_jour_pct, 1)} % · semaine ${pct(r.pnl_semaine_pct)}</div></div>
    <div class="carte"><div class="kpi-libelle">Drawdown</div><div class="kpi-valeur">${pct(r.drawdown_pct)}</div><div class="kpi-detail">arrêt total à ${nf(lim.drawdown_max_total_pct, 0)} %</div></div>
    <div class="carte"><div class="kpi-libelle">Positions</div><div class="kpi-valeur">${(ETAT.positions || []).length}</div><div class="kpi-detail">${r.trades_jour ?? 0} trade(s) aujourd'hui · ${r.pertes_consecutives ?? 0} perte(s) d'affilée</div></div>`
    : `<div class="carte" style="grid-column:1/-1"><div class="kpi-libelle">Compte</div><div class="kpi-valeur">Non connecté</div><div class="kpi-detail">${esc(ETAT.connexion?.message || "")} · <a href="#/installation">Configurer le compte MT5</a></div></div>`;

  const p = $("#positions");
  if (p) {
    const pos = ETAT.positions || [];
    p.innerHTML = `<div class="carte-tete"><h2>Positions ouvertes</h2><span class="discret">stops déposés chez le courtier</span></div>` + (pos.length ? `<div class="defile-x"><table>
      <thead><tr><th>Sens</th><th class="num">Lots</th><th class="num">Entrée</th><th class="num">Stop</th><th class="num">Objectif</th><th class="num">R</th><th class="num">Résultat</th></tr></thead><tbody>
      ${pos.map(x => `<tr><td><span class="etiquette ${x.sens === "achat" ? "gain" : "perte"}">${esc(x.sens)}</span></td><td class="num">${nf(x.lots)}</td><td class="num mono">${x.prix_entree}</td><td class="num mono">${x.sl}</td><td class="num mono">${x.tp}</td><td class="num ${classe(x.R)}">${signe(x.R)}</td><td class="num ${classe(x.profit)}">${signe(x.profit)}</td></tr>`).join("")}
      </tbody></table></div>` : `<div class="vide">Aucune position. L'agent attend un signal qui passe les 8 verrous.</div>`);
  }
  const pr = $("#prochaine");
  if (pr) {
    const annonces = (ETAT.calendrier || []).slice(0, 4);
    pr.innerHTML = `<div class="carte-tete"><h2>Prochaine analyse</h2><span class="etiquette">${esc(ETAT.timeframe || "H4")}</span></div>
      <div class="kpi-valeur" id="compte-rebours">·</div>
      <div class="kpi-detail">à la clôture de la bougie en cours · stratégies : ${esc((ETAT.strategies_actives || []).join(", ") || "aucune")}</div>
      <h3 style="margin-top:18px">Annonces à fort impact</h3>
      ${ETAT.calendrier_ok ? (annonces.length ? `<ul class="flux">${annonces.map(a => `<li><time>${esc(dateCourte(a.quand))}</time><span class="msg"><span class="type">${esc(a.devise)}</span>${esc(a.titre)}</span></li>`).join("")}</ul>` : `<p class="discret">Rien dans les 72 prochaines heures.</p>`)
        : `<p class="alerte-txt">Calendrier indisponible : l'agent s'abstient d'entrer tant qu'il ne sait pas.</p>`}`;
    majCompteRebours();
  }
}
function majCompteRebours() {
  const el = $("#compte-rebours");
  if (!el || !(ETAT.prochaine_bougie_utc || ETAT.prochaine_bougie)) return;
  // Heure UTC fournie par l'agent : l'heure du serveur du courtier n'est pas celle du PC.
  const fin = new Date(ETAT.prochaine_bougie_utc || ETAT.prochaine_bougie + "Z").getTime();
  const s = Math.max(0, Math.round((fin - Date.now()) / 1000));
  el.textContent = s > 0 ? `${String(Math.floor(s / 3600)).padStart(2, "0")} h ${String(Math.floor(s % 3600 / 60)).padStart(2, "0")} min` : "imminente";
}
setInterval(majCompteRebours, 15000);
async function chargerCourbe() {
  const el = $("#courbe"); if (!el) return;
  el.innerHTML = courbeSVG(await api(`/api/equite?jours=${periodeCourbe}`));
}
async function chargerFlux() {
  const el = $("#flux"); if (!el) return;
  const ev = await api("/api/evenements?limite=40");
  el.innerHTML = ev.length ? ev.map(e => `<li class="${esc(e.niveau)}"><time>${esc(dateCourte(e.ts))}</time><span class="msg"><span class="type">${esc(e.type)}</span>${esc(e.message)}</span></li>`).join("")
    : `<li><time></time><span class="msg">Rien encore. L'agent écrit ici chaque bougie analysée.</span></li>`;
}
async function chargerDerniereDecision() {
  const el = $("#derniere-decision"); if (!el) return;
  const [d] = await api("/api/decisions?limite=1");
  if (!d) {
    el.innerHTML = `<div class="carte-tete"><h2>Dernier signal</h2></div>${verrousBarre([])}
      <p class="sous-titre">Aucune stratégie n'a encore proposé de trade. Quand ce sera le cas, tu verras ici les 8 verrous qu'il doit passer, et celui qui l'a arrêté.</p>`;
    return;
  }
  const passes = d.verrous.filter(v => v.passe).length;
  el.innerHTML = `<div class="carte-tete"><h2>Dernier signal · ${passes} verrou${passes > 1 ? "s" : ""} sur 8</h2>${etiquetteVerdict(d.verdict)}</div>
    ${verrousBarre(d.verrous)}
    <p class="these">${esc((d.sens || "").toUpperCase())} · « ${esc(d.these)} »</p>
    <p class="kpi-detail">${esc(dateCourte(d.ts))} · ${esc(d.strategie)}${d.risque_pct ? ` · risque ${pct(d.risque_pct)}` : ""}${d.motif ? ` · ${esc(d.motif)}` : ""}</p>
    <details><summary class="discret" style="cursor:pointer;margin-top:8px">Voir le détail des verrous</summary>${listeVerrous(d.verrous)}</details>`;
}

// ------------------------------------------------------------------ conversation
async function vueConversation() {
  vue.innerHTML = `<div class="entete-vue"><div><h1>Parler à l'agent</h1><p class="sous-titre">Il répond à partir de son journal et de ses mesures. Il peut rendre le système plus prudent tout seul ; tout ce qui augmente le risque, il te le propose.</p></div><span class="etiquette" id="moteur">…</span></div>
    <div class="conv carte"><div class="fil" id="fil"></div>
      <form class="saisie" id="form-chat">
        <div class="suggestions">${["Pourquoi tu n'as pas tradé ?", "Quel est mon risque en ce moment ?", "Comment se porte la stratégie ?", "Baisse le risque par trade à 0,5 %", "Mets-toi en pause"].map(s => `<button type="button">${esc(s)}</button>`).join("")}</div>
        <div class="zone"><textarea id="message" rows="1" placeholder="Écris à l'agent…" aria-label="Message à l'agent"></textarea><button class="btn btn-primaire" type="submit">Envoyer</button></div>
      </form></div>`;
  const moteur = ETAT.assistant?.cle ? `${ETAT.assistant.modele}` : "répondeur local (sans clé API)";
  $("#moteur").textContent = moteur;
  const d = await api("/api/conversation");
  const fil = $("#fil");
  fil.innerHTML = d.messages.length ? d.messages.map(bulle).join("") : `<div class="bulle agent"><p>Bonjour. Je suis ton agent de trading. Demande-moi ce que je fais, pourquoi, et quel risque je porte. Je ne te promettrai jamais un rendement : je te dirai ce qui est mesuré.</p></div>`;
  afficherPropositions(d.propositions);
  fil.scrollTop = fil.scrollHeight;
  const zone = $("#message");
  zone.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#form-chat").requestSubmit(); } });
  $(".suggestions").onclick = e => { const b = e.target.closest("button"); if (b) { zone.value = b.textContent; $("#form-chat").requestSubmit(); } };
  $("#form-chat").onsubmit = async e => {
    e.preventDefault();
    const texte = zone.value.trim(); if (!texte) return;
    zone.value = "";
    fil.insertAdjacentHTML("beforeend", bulle({ role: "utilisateur", contenu: texte }) + `<div class="bulle agent" id="attente"><span class="ecrit"><i></i><i></i><i></i></span></div>`);
    fil.scrollTop = fil.scrollHeight;
    try {
      const r = await api("/api/chat", { corps: { message: texte } });
      $("#attente")?.remove();
      fil.insertAdjacentHTML("beforeend", bulle({ role: "agent", contenu: r.reponse, moteur: r.moteur }));
      afficherPropositions(r.propositions);
    } catch (err) { $("#attente")?.remove(); toast(err.message, true); }
    fil.scrollTop = fil.scrollHeight;
    rafraichirEtat();
  };
}
function bulle(m) {
  const agent = m.role !== "utilisateur";
  return `<div class="bulle ${agent ? "agent" : "utilisateur"}">${agent ? markdownLeger(m.contenu) : `<p>${esc(m.contenu)}</p>`}${m.moteur ? `<span class="moteur">${esc(m.moteur)}</span>` : ""}</div>`;
}
function afficherPropositions(props) {
  const fil = $("#fil"); if (!fil) return;
  $$(".proposition", fil).forEach(p => p.remove());
  (props || []).forEach(p => {
    const contenu = p.type === "reglages" ? Object.entries(p.contenu).map(([k, v]) => `${k} = ${v}`).join(", ")
      : p.type === "mode" ? `passer en mode ${p.contenu}` : "arrêt d'urgence : tout fermer et mettre en pause";
    fil.insertAdjacentHTML("beforeend", `<div class="proposition" data-id="${esc(p.id)}"><b>L'agent propose</b> : ${esc(contenu)}<br><span class="discret">${esc(p.raison)}</span>
      <div class="actions"><button class="btn btn-primaire btn-petit" data-accepter="1">Confirmer</button><button class="btn btn-petit" data-accepter="0">Refuser</button></div></div>`);
  });
  $$(".proposition", fil).forEach(el => el.onclick = async e => {
    const b = e.target.closest("button[data-accepter]"); if (!b) return;
    try {
      const r = await api(`/api/propositions/${el.dataset.id}`, { corps: { accepter: b.dataset.accepter === "1" } });
      if (r.ok === false) toast(r.erreur || (r.resultat?.erreurs || []).join(" "), true);
      else toast(b.dataset.accepter === "1" ? "Confirmé" : "Refusé");
      el.remove(); rafraichirEtat();
    } catch (err) { toast(err.message, true); }
  });
}

// ------------------------------------------------------------------ risque
async function vueRisque() {
  const cap = await api("/api/capital");
  const r = ETAT.risque || {}, lim = r.limites || {}, c = ETAT.compte;
  const via = cap.viabilite || {};
  const conseil = !c ? "" : c.cent
    ? (c.solde_reel > 600 ? "Au-delà d'environ 500 $, le plafond de lots bride un compte cent : un compte standard devient plus efficace." : "Compte cent : même avec un petit capital, le risque de 1 % reste exact sur presque tous les signaux.")
    : (c.solde_reel < 250 ? "Sous 250 $ sur un compte standard, aucun signal ne tient dans le risque autorisé. Un compte cent chez ton courtier règle le problème sans relever le risque."
      : c.solde_reel < 1000 ? "Entre 250 et 1 000 $, une partie des trades passe au lot minimum, avec un risque relevé jusqu'au plafond du petit compte. Chaque trade concerné le dit." : "Capital suffisant : le risque de 1 % est tenu exactement.");
  vue.innerHTML = `<div class="entete-vue"><div><h1>Risque</h1><p class="sous-titre">Chaque jauge montre où tu en es par rapport à la limite qui arrête l'agent.</p></div>
    ${ETAT.arret_total ? `<button class="btn btn-danger" id="btn-relancer">Lever l'arrêt total</button>` : ""}</div>
    <div class="grille moitie">
      <section class="carte pile"><div class="carte-tete"><h2>Disjoncteurs</h2>${r.disjoncteur ? `<span class="etiquette perte">déclenché</span>` : `<span class="etiquette gain">au repos</span>`}</div>
        ${ETAT.risque ? [
          jauge("Perte du jour", r.pnl_jour_pct, lim.perte_max_jour_pct, { inverse: true }),
          jauge("Perte de la semaine", r.pnl_semaine_pct, lim.perte_max_semaine_pct, { inverse: true }),
          jauge("Perte du mois", r.pnl_mois_pct, lim.perte_max_mois_pct, { inverse: true }),
          jauge("Drawdown (arrêt total)", r.drawdown_pct, lim.drawdown_max_total_pct),
        ].join("") : `<div class="vide">Disponible une fois le compte connecté.</div>`}</section>
      <section class="carte pile"><div class="carte-tete"><h2>Discipline</h2></div>
        ${ETAT.risque ? [
          jauge("Pertes consécutives (pause)", r.pertes_consecutives, lim.pertes_consecutives_max, { unite: "" }),
          jauge("Trades aujourd'hui", r.trades_jour, lim.trades_max_par_jour, { unite: "" }),
          jauge("Trades cette semaine", r.trades_semaine, lim.trades_max_par_semaine, { unite: "" }),
          jauge("Exposition ouverte", r.exposition_pct, lim.exposition_totale_max_pct),
        ].join("") + `<p class="discret">Risque par trade : <b>${nf(lim.risque_par_trade_pct, 1)} %</b> · plafond petit compte <b>${nf(lim.risque_max_petit_compte_pct, 1)} %</b> · martingale, grille et stop élargi : impossibles, pas des réglages.</p>` : ""}</section>
    </div>
    <section class="carte" style="margin-top:16px"><div class="carte-tete"><h2>Trader avec n'importe quel capital</h2><span class="discret">mesuré le ${esc(cap.calcule_le || "·")}</span></div>
      ${c ? `<p><b>Ton compte :</b> ${esc(c.type_compte)} · capital de travail ${nf(c.capital_travail_reel)} ${esc(c.devise_reelle)}. ${esc(conseil)}</p>` : ""}
      <p class="sous-titre">Le lot minimum d'EUR/USD vaut environ 1 $ par pip. Stop médian mesuré sur deux ans : <b>${nf((cap.stop_median_points || 0) / 10, 0)} pips</b>. Trois réponses, appliquées automatiquement : le <b>compte cent</b> (lot 100 fois plus petit), le <b>lot minimum toléré</b> jusqu'au plafond du petit compte, et l'<b>attente</b> d'un signal au stop plus court. Jamais de dépassement.</p>
      ${via.standard ? `<div class="defile-x"><table><thead><tr><th class="num">Capital</th><th class="num">Standard à 1 %</th><th class="num">Standard, plafond</th><th class="num">Compte cent</th></tr></thead><tbody>
        ${via.standard.map((s, i) => `<tr><td class="num">${nf(s.capital, 0)} $</td><td class="num">${nf(100 * s.a_1pct, 0)} %</td><td class="num">${nf(100 * s.au_plafond, 0)} %</td><td class="num gain">${nf(100 * via.cent[i].a_1pct, 0)} %</td></tr>`).join("")}
      </tbody></table></div><p class="discret">Part des signaux réels (deux dernières années) qu'on peut trader sans dépasser le risque.</p>` : `<div class="vide">Mesure absente : lancer <span class="mono">python -m trading.outils.capital</span></div>`}
    </section>`;
  const btn = $("#btn-relancer");
  if (btn) btn.onclick = async () => {
    if (!await confirmer({ titre: "Lever l'arrêt total ?", danger: true, libelleOk: "Reprendre", corps: "<p>Le système a perdu plus que ce que tu avais décidé de tolérer. Le drawdown repartira du niveau actuel. Avant de reprendre, regarde les décisions et les trades qui y ont mené.</p>" })) return;
    await api("/api/commande", { corps: { action: "relancer_apres_arret", confirme: true } }); toast("Arrêt total levé"); setTimeout(rafraichirEtat, 800);
  };
}

// ------------------------------------------------------------------ décisions
async function vueDecisions() {
  const ds = await api("/api/decisions?limite=200");
  vue.innerHTML = `<div class="entete-vue"><div><h1>Décisions</h1><p class="sous-titre">Chaque signal proposé par une stratégie, et ce que les 8 verrous en ont fait. Les refus sont aussi des données : c'est d'eux que l'agent apprendra.</p></div>
    <div class="segmentes" id="filtre">${[["", "Toutes"], ["pris", "Prises"], ["refuse", "Refusées"], ["observe", "Observées"]].map(([v, t], i) => `<button data-v="${v}" aria-pressed="${i === 0}">${t}</button>`).join("")}</div></div>
    <section class="carte" id="liste-decisions"></section>`;
  const rendre = f => {
    const l = ds.filter(d => !f || d.verdict === f);
    $("#liste-decisions").innerHTML = l.length ? l.map(d => `<details class="details-decision"><summary>
      <span class="discret num">${esc(dateCourte(d.ts))}</span>
      <span><b>${esc((d.sens || "").toUpperCase())}</b> ${esc(d.strategie)} ${etiquetteVerdict(d.verdict)}<br><span class="discret">${esc(d.motif || d.these || "")}</span></span>
      ${miniVerrous(d.verrous)}</summary>
      <p class="these">« ${esc(d.these)} »</p>
      <p class="kpi-detail mono">entrée ${d.entree} · stop ${d.stop} · objectif ${d.objectif}${d.lots ? ` · ${d.lots} lot · risque ${pct(d.risque_pct)}` : ""}${d.note ? ` · ${esc(d.note)}` : ""}</p>
      ${listeVerrous(d.verrous)}</details>`).join("") : `<div class="vide">Aucune décision pour l'instant.</div>`;
  };
  rendre("");
  $("#filtre").onclick = e => { const b = e.target.closest("button"); if (!b) return; $$("#filtre button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); rendre(b.dataset.v); };
}

// ------------------------------------------------------------------ trades
async function vueTrades() {
  const d = await api("/api/trades");
  const s = d.stats;
  vue.innerHTML = `<div class="entete-vue"><div><h1>Trades</h1><p class="sous-titre">Les trades réellement exécutés par l'agent sur ce compte.</p></div></div>
    <div class="grille kpi">
      <div class="carte"><div class="kpi-libelle">Trades fermés</div><div class="kpi-valeur">${s.trades}</div><div class="kpi-detail">${s.trades < 100 ? "sous 100, un taux de réussite ne dit rien" : "échantillon exploitable"}</div></div>
      <div class="carte"><div class="kpi-libelle">Réussite</div><div class="kpi-valeur">${s.taux_reussite == null ? "·" : pct(100 * s.taux_reussite, 0)}</div><div class="kpi-detail">${s.gagnants} gagnant(s)</div></div>
      <div class="carte"><div class="kpi-libelle">Espérance</div><div class="kpi-valeur ${classe(s.esperance_R)}">${s.esperance_R == null ? "·" : signe(s.esperance_R, 3) + " R"}</div><div class="kpi-detail">profit factor ${s.profit_factor == null ? "·" : nf(s.profit_factor)}</div></div>
      <div class="carte"><div class="kpi-libelle">Résultat net</div><div class="kpi-valeur ${classe(s.resultat_net)}">${signe(s.resultat_net)}</div><div class="kpi-detail">${s.decisions} décision(s) · ${s.refus} refus</div></div>
    </div>
    <section class="carte" style="margin-top:16px"><div class="carte-tete"><h2>Historique</h2></div>
      ${d.trades.length ? `<div class="defile-x"><table><thead><tr><th>Ouvert</th><th>Sens</th><th>Stratégie</th><th class="num">Lots</th><th class="num">Entrée</th><th class="num">Sortie</th><th>Motif</th><th class="num">R</th><th class="num">Résultat</th></tr></thead><tbody>
      ${d.trades.map(t => `<tr><td>${esc(dateCourte(t.ouvert_le))}</td><td><span class="etiquette ${t.sens === "achat" ? "gain" : "perte"}">${esc(t.sens)}</span></td><td>${esc(t.strategie)}</td><td class="num">${t.lots}</td><td class="num mono">${t.prix_entree}</td><td class="num mono">${t.prix_sortie ?? "ouvert"}</td><td>${esc(t.motif || "")}</td><td class="num ${classe(t.resultat_R)}">${t.resultat_R == null ? "·" : signe(t.resultat_R)}</td><td class="num ${classe(t.resultat_devise)}">${t.resultat_devise == null ? "·" : signe(t.resultat_devise)}</td></tr>`).join("")}
      </tbody></table></div>` : `<div class="vide">Aucun trade exécuté. En mode observation, l'agent décide mais n'envoie rien : regarde l'onglet Décisions.</div>`}</section>`;
}

// ------------------------------------------------------------------ stratégies
async function vueStrategies() {
  const d = await api("/api/strategies");
  vue.innerHTML = `<div class="entete-vue"><div><h1>Stratégies</h1><p class="sous-titre">Chaque stratégie est jugée en walk-forward : réglages choisis sur quatre années, appliqués à l'année suivante sans la connaître, sur quinze ans. Seuls ces résultats hors échantillon comptent.</p></div></div>
    <div class="pile" id="liste-strategies"></div>`;
  $("#liste-strategies").innerHTML = d.catalogue.map(s => {
    const rapports = d.rapports[s.nom] || [];
    return `<section class="carte" data-strategie="${esc(s.nom)}"><div class="carte-tete"><div><h2>${esc(s.libelle)}</h2><p class="sous-titre">${esc(s.these)}</p></div>
      <label class="interrupteur" title="${s.active ? "Désactiver" : "Activer"}"><input type="checkbox" ${s.active ? "checked" : ""} aria-label="Stratégie active"><span></span></label></div>
      ${rapports.length ? `<div class="onglets">${rapports.map((r, i) => `<button class="btn btn-petit" data-i="${i}" aria-pressed="${!!r.correspond_config}">${esc(r.variante === "sans_weekend" ? "positions gardées le week-end" : r.variante === "reference" ? "fermeture du vendredi" : r.variante)}${r.correspond_config ? " · réglage actuel" : ""}</button>`).join("")}</div><div class="rapport"></div>`
        : `<div class="vide">Pas encore de walk-forward : <span class="mono">python -m trading.outils.walkforward --strategie ${esc(s.nom)}</span></div>`}
    </section>`;
  }).join("");
  $$("#liste-strategies section").forEach(sec => {
    const nom = sec.dataset.strategie, rapports = d.rapports[nom] || [];
    const afficher = i => {
      const r = rapports[i], m = r.metriques || {};
      $$(".onglets button", sec).forEach(b => b.setAttribute("aria-pressed", String(+b.dataset.i === i)));
      $(".rapport", sec).innerHTML = `
        <div class="verdict ${r.credible ? "ok" : "non"}">${r.credible ? "<b>Avantage statistiquement distinguable de zéro.</b>" : `<b>Pas d'avantage prouvé.</b> Sur ${m.trades} trades hors échantillon, le résultat reste compatible avec un système qui ne gagne rien.`}</div>
        <div class="metriques">
          <div class="metrique"><span>Trades</span><b>${m.trades}</b></div>
          <div class="metrique"><span>Espérance</span><b class="${classe(m.esperance_R)}">${signe(m.esperance_R, 3)} R</b></div>
          <div class="metrique"><span>Profit factor</span><b>${nf(m.profit_factor)}</b></div>
          <div class="metrique"><span>Réussite</span><b>${pct(100 * m.taux_reussite, 1)}</b></div>
          <div class="metrique"><span>Capital</span><b class="${classe(m.capital_final - m.capital_initial)}">${nf(m.capital_initial, 0)} → ${nf(m.capital_final, 0)}</b></div>
          <div class="metrique"><span>Drawdown max</span><b>${pct(m.drawdown_max_pct, 1)}</b></div>
          <div class="metrique"><span>Série perdante</span><b>${m.serie_perdante_max}</b></div>
          <div class="metrique"><span>Coûts / brut</span><b>${pct(m.couts_pct_du_brut, 0)}</b></div>
        </div>
        <div style="margin-top:14px">${courbeSVG((r.courbe || []).map(([t, e]) => ({ ts: t, equite: e })), { hauteur: 180 })}</div>
        <details style="margin-top:10px"><summary class="discret" style="cursor:pointer">Année par année (${(r.fenetres || []).length} fenêtres) · ${esc(r.couts || "")}</summary>
          <div class="defile-x"><table><thead><tr><th>Test</th><th>Réglages choisis</th><th class="num">Trades appr.</th><th class="num">R appr.</th><th class="num">Trades test</th><th class="num">R test</th><th class="num">Capital</th></tr></thead><tbody>
          ${(r.fenetres || []).map(f => `<tr><td>${esc(String(f.debut_test).slice(0, 4))}</td><td class="mono">${esc(Object.entries(f.parametres || {}).map(([k, v]) => `${k}=${v}`).join(" ") || "non tradée")}</td><td class="num">${f.trades_apprentissage}</td><td class="num">${signe(f.esperance_R_apprentissage)}</td><td class="num">${f.trades_test}</td><td class="num ${classe(f.esperance_R_test)}">${signe(f.esperance_R_test)}</td><td class="num">${nf(f.capital_fin, 0)}</td></tr>`).join("")}
          </tbody></table></div></details>`;
    };
    const courante = Math.max(0, rapports.findIndex(r => r.correspond_config));
    if (rapports.length) { afficher(courante); $(".onglets", sec).onclick = e => { const b = e.target.closest("button"); if (b) afficher(+b.dataset.i); }; }
    $("input[type=checkbox]", sec).onchange = async e => {
      const actives = $$("#liste-strategies section").filter(x => $("input[type=checkbox]", x).checked).map(x => x.dataset.strategie);
      const r0 = rapports.find(r => r.correspond_config) || rapports[0];
      if (e.target.checked && r0 && !r0.credible) {
        const ok = await confirmer({ titre: "Activer une stratégie non prouvée ?", corps: `<p>${esc(nom)} n'a pas montré d'avantage statistique en walk-forward. En mode observation ou démo, c'est sans risque ; en réel, c'est un pari.</p>`, libelleOk: "Activer quand même" });
        if (!ok) { e.target.checked = false; return; }
      }
      try { await api("/api/commande", { corps: { action: "strategies", valeur: actives } }); toast(`Stratégies actives : ${actives.join(", ") || "aucune"}`); } catch (err) { toast(err.message, true); }
    };
  });
}

// ------------------------------------------------------------------ réglages
async function vueReglages() {
  const d = await api("/api/reglages");
  const groupes = {};
  d.reglages.forEach(r => (groupes[r.groupe] ??= []).push(r));
  const modifs = {};
  vue.innerHTML = `<div class="entete-vue"><div><h1>Réglages</h1><p class="sous-titre">Chaque changement repasse par le videur : un réglage dangereux est refusé avec sa raison, et rien n'est enregistré. Les réglages qui augmentent le risque sont signalés.</p></div>
    <button class="btn" id="btn-defaut">Revenir aux valeurs du fichier</button></div>
    <div class="grille deux"><div class="pile" id="groupes"></div>
      <div class="pile"><section class="carte"><div class="carte-tete"><h2>Protections non modifiables</h2></div>
        <ul class="liste-verrous">${d.verrouilles.map(v => `<li><span class="marque-v gain">✓</span><span class="q">verrou</span><span><b>${esc(v.libelle)}</b><br><span class="d">${esc(v.raison)}</span></span></li>`).join("")}</ul></section>
        <section class="carte"><div class="carte-tete"><h2>Historique des changements</h2></div>
        ${d.historique.length ? `<ul class="flux">${d.historique.map(h => `<li><time>${esc(dateCourte(h.ts))}</time><span class="msg"><span class="type">${esc(h.auteur)}</span>${esc(h.cle)} : ${esc(h.avant)} → ${esc(h.apres)}</span></li>`).join("")}</ul>` : `<p class="discret">Aucun changement.</p>`}</section></div></div>
    <div class="barre-enregistrer" id="barre-enr" hidden><span id="resume-modifs"></span><div style="display:flex;gap:8px"><button class="btn" id="btn-annuler">Annuler</button><button class="btn btn-primaire" id="btn-enregistrer">Enregistrer</button></div><div class="erreurs" id="erreurs" style="flex-basis:100%" hidden></div></div>`;
  $("#groupes").innerHTML = Object.entries(groupes).map(([g, rs]) => `<section class="carte"><div class="carte-tete"><h2>${esc(g)}</h2></div>${rs.map(champReglage).join("")}</section>`).join("");
  const maj = () => {
    const n = Object.keys(modifs).length;
    $("#barre-enr").hidden = !n;
    const risques = Object.entries(modifs).filter(([k, v]) => plusRisque(d.reglages.find(r => r.cle === k), v)).length;
    $("#resume-modifs").innerHTML = `${n} changement${n > 1 ? "s" : ""}${risques ? ` · <span class="alerte-txt">${risques} augmente${risques > 1 ? "nt" : ""} le risque</span>` : ""}`;
  };
  $("#groupes").addEventListener("input", e => {
    const el = e.target.closest("[data-cle]"); if (!el) return;
    const r = d.reglages.find(x => x.cle === el.dataset.cle);
    const v = r.type === "bool" ? el.checked : r.type === "choix" || r.type === "heure" ? el.value : Number(el.value);
    if (String(v) === String(r.valeur)) delete modifs[r.cle]; else modifs[r.cle] = v;
    el.closest(".reglage").classList.toggle("modifie", r.cle in modifs || r.modifie);
    maj();
  });
  $("#btn-annuler").onclick = () => vueReglages();
  $("#btn-enregistrer").onclick = async () => {
    const err = $("#erreurs"); err.hidden = true;
    try {
      const r = await api("/api/reglages", { corps: { changements: modifs } });
      if (!r.ok) { err.textContent = r.erreurs.join("\n"); err.hidden = false; return; }
      (r.alertes || []).forEach(a => toast(a, true));
      toast(`${r.changes.length} réglage(s) enregistré(s)`);
      vueReglages();
    } catch (e) { err.textContent = e.message; err.hidden = false; }
  };
  $("#btn-defaut").onclick = async () => {
    if (!await confirmer({ titre: "Revenir aux valeurs du fichier ?", corps: "<p>Tous les changements faits dans l'interface seront retirés. Les valeurs de <span class=\"mono\">config.toml</span> s'appliquent de nouveau.</p>" })) return;
    await api("/api/reglages/reinitialiser", { corps: {} }); toast("Réglages remis par défaut"); vueReglages();
  };
}
function plusRisque(r, v) {
  if (!r) return false;
  if (r.type === "bool") return r.sens === "prudence" && v === false;
  if (typeof v !== "number") return false;
  return (r.sens === "risque" && v > r.valeur) || (r.sens === "prudence" && v < r.valeur);
}
function champReglage(r) {
  let entree;
  if (r.type === "bool") entree = `<label class="interrupteur"><input type="checkbox" data-cle="${esc(r.cle)}" ${r.valeur ? "checked" : ""} aria-label="${esc(r.libelle)}"><span></span></label>`;
  else if (r.type === "choix") entree = `<select data-cle="${esc(r.cle)}" aria-label="${esc(r.libelle)}">${r.choix.map(c => `<option ${c === r.valeur ? "selected" : ""}>${esc(c)}</option>`).join("")}</select>`;
  else if (r.type === "heure") entree = `<input type="time" data-cle="${esc(r.cle)}" value="${esc(r.valeur)}" aria-label="${esc(r.libelle)}">`;
  else entree = `<div class="unite"><input type="number" data-cle="${esc(r.cle)}" value="${esc(r.valeur)}" min="${r.min}" max="${r.max}" step="${r.pas}" aria-label="${esc(r.libelle)}"><span>${esc(r.unite || "")}</span></div>`;
  return `<div class="reglage ${r.modifie ? "modifie" : ""}"><div><b>${esc(r.libelle)}</b>${r.sens === "risque" ? ` <span class="etiquette alerte" title="Augmenter cette valeur augmente le risque">risque</span>` : ""}${r.aide ? `<div class="aide">${esc(r.aide)}</div>` : ""}</div>${entree}</div>`;
}

// ------------------------------------------------------------------ installation
async function vueInstallation() {
  const d = await api("/api/installation");
  const ca = d.compte_application, ia = d.identifiants_actifs;
  vue.innerHTML = `<div class="entete-vue"><div><h1>Compte et licence</h1><p class="sous-titre">Brancher l'agent sur ton compte MetaTrader 5, activer ta licence et l'assistant.</p></div></div>
    <div class="grille moitie">
      <section class="carte"><div class="carte-tete"><h2>Compte MetaTrader 5</h2>${ia.complets ? `<span class="etiquette gain">identifiants complets</span>` : `<span class="etiquette alerte">à configurer</span>`}</div>
        <p class="discret">Actif : ${ia.login ? `compte ${esc(ia.login)} @ ${esc(ia.serveur)} (source : ${esc(ia.source)})` : "aucun"}.${ca ? ` Enregistré dans l'application : ${esc(ca.login)} @ ${esc(ca.serveur)}, mot de passe ${esc(ca.motdepasse)}.` : ""}</p>
        <form class="formulaire" id="form-compte">
          <div class="ligne"><label class="champ"><span>Numéro de compte</span><input name="login" inputmode="numeric" required value="${esc(ca?.login || "")}"></label>
            <label class="champ"><span>Serveur</span><input name="serveur" required placeholder="ex. Deriv-Demo" value="${esc(ca?.serveur || "")}"></label></div>
          <label class="champ"><span>Mot de passe <b>principal</b> (pas celui « investisseur »)</span><input name="motdepasse" type="password" required autocomplete="new-password"></label>
          <label class="champ"><span>Terminal MetaTrader 5</span><select name="terminal"><option value="">Détection automatique</option>${d.terminaux.map(t => `<option ${t === ca?.terminal ? "selected" : ""}>${esc(t)}</option>`).join("")}</select></label>
          <p class="discret">Le mot de passe est chiffré par Windows : seul ce compte utilisateur, sur ce PC, peut le relire. Dans MetaTrader 5, le bouton <b>Trading Algo</b> doit être vert et, dans Outils > Options > Expert Advisors, la case qui <b>désactive</b> le trading par l'API Python doit être <b>décochée</b>.</p>
          <div><button class="btn btn-primaire">Enregistrer et connecter</button></div>
        </form></section>
      <div class="pile">
        <section class="carte"><div class="carte-tete"><h2>Licence</h2>${d.licence.valide ? `<span class="etiquette gain">${esc(d.licence.edition)}</span>` : `<span class="etiquette">évaluation</span>`}</div>
          <p>${d.licence.valide ? `Au nom de <b>${esc(d.licence.titulaire)}</b>${d.licence.expire ? `, valable jusqu'au ${esc(d.licence.expire)}` : ", sans expiration"}.` : "Mode évaluation : observation et compte démo, toutes les fonctions visibles. Le mode réel demande une licence."}</p>
          <form class="formulaire" id="form-licence"><label class="champ"><span>Clé de licence</span><input name="cle" placeholder="NTR1.…" autocomplete="off"></label><div><button class="btn">Activer</button></div></form></section>
        <section class="carte"><div class="carte-tete"><h2>Assistant IA</h2>${d.assistant.cle ? `<span class="etiquette gain">clé enregistrée</span>` : `<span class="etiquette">répondeur local</span>`}</div>
          <p class="discret">Sans clé, l'agent comprend les demandes courantes. Avec une clé Anthropic, il discute librement et explique ses décisions. La clé est chiffrée par Windows.</p>
          <form class="formulaire" id="form-ia"><label class="champ"><span>Clé API Anthropic</span><input name="cle" type="password" placeholder="${d.assistant.cle ? "enregistrée (laisser vide pour la garder)" : "sk-ant-…"}" autocomplete="off"></label>
            <label class="champ"><span>Modèle</span><select name="modele">${d.modeles.map(m => `<option ${m === d.assistant.modele ? "selected" : ""}>${esc(m)}</option>`).join("")}</select></label>
            <div><button class="btn">Enregistrer</button></div></form></section>
        <section class="carte"><div class="carte-tete"><h2>À savoir</h2><span class="discret">v${esc(d.version)}</span></div>
          <p class="discret">Le trading sur marge comporte un risque élevé de perte. Les résultats passés, mesurés ou réels, ne préjugent pas des résultats futurs. NEBULA Trader ne garantit aucun rendement : il garantit que le risque que tu as choisi n'est jamais dépassé.</p></section>
      </div></div>`;
  $("#form-compte").onsubmit = async e => {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    try { await api("/api/installation/compte", { corps: f }); toast("Identifiants enregistrés, connexion en cours"); setTimeout(() => { rafraichirEtat(); vueInstallation(); }, 2500); }
    catch (err) { toast(err.message, true); }
  };
  $("#form-licence").onsubmit = async e => {
    e.preventDefault();
    const r = await api("/api/licence", { corps: { cle: new FormData(e.target).get("cle") } });
    toast(r.raison, !r.valide); if (r.valide) { rafraichirEtat(); vueInstallation(); }
  };
  $("#form-ia").onsubmit = async e => {
    e.preventDefault();
    const f = Object.fromEntries(new FormData(e.target));
    try { await api("/api/assistant", { corps: { cle: f.cle ? f.cle : null, modele: f.modele } }); toast("Assistant enregistré"); rafraichirEtat(); vueInstallation(); }
    catch (err) { toast(err.message, true); }
  };
}

// ------------------------------------------------------------------ démarrage
rafraichirEtat().then(naviguer);
setInterval(rafraichirEtat, 3000);
