/* LE MONDE · acheter dans un lieu : la fiche « comme dans un jeu », le sac,
   puis le cadran qui envoie sur WhatsApp.

   ⛔ Les règles sont CELLES DE LA VITRINE, portées à l'identique depuis
   clients/10-hillary-m-styl/_v4/garde-moteur.js (2026-11-12) :
   - prix express = le prix express TOTAL de la pièce, jamais un supplément fixe ;
   - délai de la commande = la borne HAUTE de la pièce la plus lente, + l'acheminement ;
   - frais de livraison comptés UNE fois ; « Autre pays » = à confirmer ;
   - quatre champs obligatoires : prénom, nom, téléphone, lieu de résidence,
     et la ville de livraison en expédition (le pays seul est une zone, pas une adresse) ;
   - une mesure laissée vide part « à prendre ensemble » ;
   - Mobile Money seul : RIEN n'est payé ici.
   Le message WhatsApp a la même forme que celui du site : Hillary le recopie
   dans son carnet, elle ne doit pas avoir deux formats à lire. */
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
/* ⚠️ toLocaleString('fr-FR') sépare les milliers par une espace FINE (U+202F) ou
   insécable (U+00A0) selon le navigateur : on la remplace par une espace simple,
   comme la vitrine, sinon le même prix s'écrit de deux façons. Écrit en codes,
   parce qu'un copier-coller avait changé ces caractères en espaces ordinaires. */
export const fcfa = (n) => Number(n).toLocaleString('fr-FR').replace(/[  ]/g, ' ') + ' F';
const JOURS = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
const MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
export const libDelai = (a, b) => (Number(a) === Number(b) ? `${a} jours` : `${a} à ${b} jours`);
function dateDispo(j) { const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() + Number(j || 0)); return d; }
function dateFr(d) { return `${JOURS[d.getDay()]} ${d.getDate()} ${MOIS[d.getMonth()]}` + (d.getFullYear() !== new Date().getFullYear() ? ` ${d.getFullYear()}` : ''); }

export function creerBoutique({ calque, donnees, son, cleStockage = 'monde:panier', imgBase = 'img/', marque = 'HILLARY M. STYL' }) {
  const D = donnees;
  const pieceDe = (id) => D.pieces.find(p => p.id === id) || null;
  let panier = [];
  try { panier = (JSON.parse(localStorage.getItem(cleStockage)) || []).filter(l => pieceDe(l.id)); } catch (e) { panier = []; }
  const sauver = () => { try { localStorage.setItem(cleStockage, JSON.stringify(panier)); } catch (e) { /* rien */ } surChange.forEach(f => f()); };
  const surChange = [];
  const cmd = { mode: null, pays: null, ville: '', repere: '', prenom: '', nom: '', tel: '', residence: '', mail: '', note: '' };
  try { Object.assign(cmd, JSON.parse(localStorage.getItem(cleStockage + ':client')) || {}); cmd.mode = null; cmd.pays = null; } catch (e) { /* rien */ }

  /* ---------- les calculs (portés de la vitrine) ---------- */
  const prixUnite = (l) => { const p = pieceDe(l.id); if (!p || p.prix == null) return null; return l.express && p.expPrix != null ? p.expPrix : p.prix; };
  const prixLigne = (l) => { const u = prixUnite(l); return u == null ? null : u * l.qte; };
  const devise = (l, c) => { const p = pieceDe(l.id); if (!p) return null; const v = l.express ? p[c + 'Exp'] : p[c]; return v == null ? null : v; };
  function totaux() {
    const t = { fcfa: 0, eur: 0, usd: 0, devis: false, eurOk: true, usdOk: true, articles: 0 };
    for (const l of panier) {
      t.articles += l.qte; const v = prixLigne(l); if (v == null) t.devis = true; else t.fcfa += v;
      const e = devise(l, 'eur'); if (e == null) t.eurOk = false; else t.eur += e * l.qte;
      const u = devise(l, 'usd'); if (u == null) t.usdOk = false; else t.usd += u * l.qte;
    }
    return t;
  }
  const frais = () => (cmd.mode !== 'expedition' || !cmd.pays ? 0 : cmd.pays.frais == null ? null : cmd.pays.frais);
  const achem = () => (cmd.mode !== 'expedition' || !cmd.pays ? 0 : cmd.pays.achem || 0);
  const totalCommande = () => { const t = totaux(); if (t.devis) return null; const f = frais(); return f === null ? null : t.fcfa + f; };
  function joursConfection() {
    let j = 0;
    for (const l of panier) {
      const p = pieceDe(l.id); if (!p) continue;
      const v = l.express ? (p.expMax != null ? p.expMax : D.delais.express.jmax)
        : Math.max(p.jmax != null ? p.jmax : D.delais.normal.jmax, D.delais.normal.jmin);
      if (v > j) j = v;
    }
    return j;
  }
  const joursTotal = () => (panier.length ? joursConfection() + achem() : null);
  function libDelaiLigne(l) {
    const p = pieceDe(l.id); if (!p) return '';
    if (l.express) return 'Express, ' + libDelai(p.expMin ?? D.delais.express.jmin, p.expMax ?? D.delais.express.jmax);
    return 'Confection en ' + libDelai(p.jmin, p.jmax);
  }
  const jeuDe = (l) => (l.typeMesure && D.mesures[l.typeMesure]) || null;

  function message() {
    const L = [];
    L.push(`*NOUVELLE COMMANDE — ${marque}*`);
    L.push('_Passée dans le salon 3D_');
    const t = totaux();
    L.push(`_${t.articles}${t.articles > 1 ? ' pièces' : ' pièce'}_`);
    panier.forEach((l, k) => {
      const p = pieceDe(l.id); if (!p) return; const v = prixLigne(l);
      L.push(''); L.push(`*${k + 1}. ${p.nom}*${l.qte > 1 ? ' × ' + l.qte : ''}`);
      L.push(`${p.cat === 'sm' ? 'Sur-mesure' : 'Prêt-à-porter'} · ${libDelaiLigne(l)}`);
      L.push('Prix : ' + (v == null ? 'sur devis' : fcfa(v)));
      if (l.taille) L.push('Taille : ' + l.taille);
      const jeu = jeuDe(l);
      if (p.cat === 'sm' && jeu) {
        L.push('MESURES — ' + jeu.nom);
        if (jeu.aValider) L.push("_(liste de mesures à valider par l'atelier)_");
        const manq = [];
        for (const c of jeu.champs) { const m = l.mesures && l.mesures[c.id]; if (m) L.push(`• ${c.l} : ${m} cm`); else manq.push(c.l); }
        if (manq.length) L.push(`_À prendre ensemble (${manq.length}) :_ ${manq.join(', ')}`);
      } else if (p.cat === 'sm') L.push('_Mesures : à prendre avec vous_');
      if ((l.details || '').trim()) L.push('Détails : ' + l.details.trim());
    });
    L.push(''); L.push('*LIVRAISON*');
    if (cmd.mode === 'retrait') L.push("Retrait à l'atelier — gratuit");
    else {
      const f = frais();
      L.push('Expédition — ' + (cmd.pays ? cmd.pays.nom : '') + (cmd.ville.trim() ? ', ' + cmd.ville.trim() : ''));
      if (cmd.repere.trim()) L.push('Repère : ' + cmd.repere.trim());
      L.push('Frais : ' + (f === null ? 'à confirmer' : fcfa(f)));
    }
    const j = joursTotal();
    if (j != null) { L.push(''); L.push('*DÉLAI*'); L.push('Disponible au plus tard le ' + dateFr(dateDispo(j))); if (panier.length > 1) L.push('_(délai de la pièce la plus longue, tout part ensemble)_'); }
    const tot = totalCommande();
    L.push(''); L.push(`*TOTAL : ${tot == null ? 'sur devis' : fcfa(tot)}*`);
    if (!t.devis && (t.eurOk || t.usdOk)) { const dv = []; if (t.eurOk) dv.push(t.eur + ' €'); if (t.usdOk) dv.push(t.usd + ' $'); L.push(`_(les pièces : ${dv.join(' · ')})_`); }
    L.push('_Règlement par Mobile Money._');
    L.push(''); L.push('*CLIENT*');
    L.push('Nom : ' + cmd.nom.trim()); L.push('Prénom : ' + cmd.prenom.trim());
    L.push('Téléphone : ' + cmd.tel.trim()); L.push('Lieu de résidence : ' + cmd.residence.trim());
    if (cmd.mail.trim()) L.push('Email : ' + cmd.mail.trim());
    if (cmd.note.trim()) { L.push(''); L.push('*Note :* ' + cmd.note.trim()); }
    return L.join('\n');
  }
  const lienWhatsapp = () => `https://wa.me/${D.whatsapp}?text=${encodeURIComponent(message())}`;

  /* ---------- le sac ---------- */
  function ajouter(id, { express = false, typeMesure = null } = {}) {
    const p = pieceDe(id); if (!p) return null;
    const l = { id, qte: 1, express: !!express, typeMesure: typeMesure || p.type || null, mesures: {}, details: '' };
    panier.push(l); sauver(); son && son.sac();
    toast(`<b>${esc(p.nom)}</b> est dans votre sac${express ? ' · express' : ''}`);
    return l;
  }
  function retirer(i) {
    const [l] = panier.splice(i, 1); sauver();
    toast(`${esc(pieceDe(l.id).nom)} retirée du sac`, { annuler: () => { panier.splice(i, 0, l); sauver(); dessinerSac(); } });
  }

  /* ---------- l'interface ---------- */
  const el = (tag, cls, html = '') => { const e = document.createElement(tag); if (cls) e.className = cls; e.innerHTML = html; return e; };
  const zoneToast = el('div', 'toasts'); calque.appendChild(zoneToast);
  function toast(html, { annuler, duree = 3600 } = {}) {
    const t = el('div', 'toast', `<span>${html}</span>`);
    if (annuler) { const b = el('button', 'toast-annuler', 'Annuler'); b.type = 'button'; b.onclick = () => { annuler(); t.remove(); }; t.appendChild(b); }
    zoneToast.appendChild(t); setTimeout(() => { t.classList.add('part'); setTimeout(() => t.remove(), 500); }, duree);
  }

  /* la fiche, « comme dans un jeu » */
  const fiche = el('section', 'fiche'); fiche.setAttribute('role', 'dialog'); fiche.setAttribute('aria-modal', 'true'); calque.appendChild(fiche);
  let resoudreFiche = null;
  function ouvrirFiche(id, { mode = 'libre' } = {}) {
    const p = pieceDe(id); if (!p) return Promise.resolve({ action: 'fermer' });
    if (resoudreFiche) resoudreFiche({ action: 'fermer' });
    son && son.ouvrir();
    const devis = p.prix == null;
    const types = Object.entries(D.mesures);
    const jeu = p.type && D.mesures[p.type];
    fiche.innerHTML = `
      <div class="fiche-cadre">
        <div class="fiche-photo ${p.img2 ? 'a-dos' : ''}">
          ${p.img ? `<img class="face" src="${imgBase}${esc(p.img)}" alt="${esc(p.nom)}">` : `<div class="sans-photo">${esc(marque)}</div>`}
          ${p.img2 ? `<img class="dos" src="${imgBase}${esc(p.img2)}" alt="${esc(p.nom)}, vue de dos">` : ''}
          ${p.img2 ? '<button type="button" class="fiche-tourner">Voir le dos</button>' : ''}
          <span class="fiche-vraie">Photo de la maison</span>
        </div>
        <div class="fiche-infos">
          <h2>${esc(p.nom)}</h2>
          <p class="fiche-ds"><b class="fiche-genre">${esc(p.cat === 'sm' ? 'Sur-mesure' : 'Prêt-à-porter')}${p.tag ? ' · ' + esc(p.tag) : ''}.</b>${p.ds ? ' ' + esc(p.ds) : ''}</p>
          <div class="fiche-stats">
            <div class="stat"><span>Prix</span><b>${devis ? 'Sur devis' : fcfa(p.prix)}</b>${!devis && p.eur ? `<small>${p.eur} € · ${p.usd} $</small>` : ''}</div>
            <div class="stat"><span>Délai</span><b>${libDelai(p.jmin, p.jmax)}</b><small>confection normale</small></div>
            ${p.expMin != null ? `<div class="stat stat-express"><span>Express</span><b>${libDelai(p.expMin, p.expMax)}</b><small>${p.expPrix != null ? fcfa(p.expPrix) : 'sur devis'}</small></div>` : ''}
            <div class="stat"><span>Mesures</span><b>${jeu ? jeu.champs.length : p.typeLibre ? 'Selon le vêtement' : 'Avec vous'}</b><small>${jeu ? esc(jeu.nom) : p.typeLibre ? 'vous choisissez' : 'prises ensemble'}</small></div>
          </div>
          ${p.typeLibre ? `<label class="fiche-type">Quel vêtement ? <select>${types.map(([k, v]) => `<option value="${k}">${esc(v.nom)}</option>`).join('')}</select></label>` : ''}
          <div class="fiche-actions">
            <button type="button" class="bt bt-plein" data-a="normal">${mode === 'presentation' ? 'Je la prends' : 'Ajouter au sac'}${devis ? '' : ' · ' + fcfa(p.prix)}</button>
            ${p.expPrix != null ? `<button type="button" class="bt bt-or" data-a="express">En express · ${fcfa(p.expPrix)}</button>` : ''}
            ${mode === 'presentation' ? '<button type="button" class="bt bt-ligne" data-a="autre">Une autre</button>' : ''}
            <button type="button" class="bt bt-ligne" data-a="fermer">${mode === 'presentation' ? 'Retour' : 'Fermer'}</button>
          </div>
        </div>
      </div>`;
    fiche.classList.add('ouverte'); document.body.classList.add('en-fiche');
    const tourner = fiche.querySelector('.fiche-tourner');
    if (tourner) tourner.onclick = () => { const ph = fiche.querySelector('.fiche-photo'); ph.classList.toggle('dos-visible'); tourner.textContent = ph.classList.contains('dos-visible') ? 'Voir la face' : 'Voir le dos'; son && son.clic(); };
    setTimeout(() => { const b = fiche.querySelector('.bt'); b && b.focus({ preventScroll: true }); }, 60);
    return new Promise((ok) => {
      resoudreFiche = ok;
      fiche.querySelectorAll('[data-a]').forEach(b => b.onclick = () => {
        const sel = fiche.querySelector('.fiche-type select');
        const r = { action: b.dataset.a, typeMesure: sel ? sel.value : null };
        fermerFiche(); son && son.clic();
        if (mode === 'libre' && (r.action === 'normal' || r.action === 'express')) ajouter(id, { express: r.action === 'express', typeMesure: r.typeMesure });
        ok(r);
      });
    });
  }
  function fermerFiche() { fiche.classList.remove('ouverte'); document.body.classList.remove('en-fiche'); resoudreFiche = null; }
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && fiche.classList.contains('ouverte')) { const r = resoudreFiche; fermerFiche(); r && r({ action: 'fermer' }); } });

  /* le sac */
  const btSac = el('button', 'bt-sac', '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8h12l-1 12H7L6 8Z"/><path d="M9 8a3 3 0 0 1 6 0"/></svg><span class="compte">0</span>');
  btSac.type = 'button'; btSac.setAttribute('aria-label', 'Votre sac'); calque.appendChild(btSac);
  const sac = el('aside', 'sac'); sac.setAttribute('aria-label', 'Votre sac'); calque.appendChild(sac);
  btSac.onclick = () => { sac.classList.toggle('ouvert'); if (sac.classList.contains('ouvert')) { dessinerSac(); son && son.ouvrir(); } };
  function majCompte() { const n = totaux().articles; btSac.querySelector('.compte').textContent = n; btSac.classList.toggle('plein', n > 0); btSac.classList.remove('saute'); void btSac.offsetWidth; if (n) btSac.classList.add('saute'); }
  surChange.push(majCompte);
  function dessinerSac() {
    const t = totaux();
    sac.innerHTML = `<header><h3>Votre sac</h3><button type="button" class="x" aria-label="Fermer"><svg class="ic-x" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></header>` +
      (panier.length ? panier.map((l, i) => { const p = pieceDe(l.id); const v = prixLigne(l);
        return `<div class="sac-ligne">${p.img ? `<img src="${imgBase}${esc(p.img)}" alt="">` : '<i></i>'}<div><b>${esc(p.nom)}</b><small>${esc(libDelaiLigne(l))}</small></div><span>${v == null ? 'sur devis' : fcfa(v)}</span><button type="button" data-i="${i}" aria-label="Retirer ${esc(p.nom)}"><svg class="ic-x" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>`; }).join('') +
        `<div class="sac-total"><span>Pièces</span><b>${t.devis ? 'sur devis' : fcfa(t.fcfa)}</b></div>
         <p class="sac-note">La livraison se choisit au comptoir. Rien n'est payé ici : règlement par Mobile Money, après confirmation sur WhatsApp.</p>
         <button type="button" class="bt bt-plein sac-valider">Valider au comptoir</button>`
        : `<p class="sac-vide">Votre sac est vide. Touchez une pièce exposée, ou demandez conseil à Hillary au comptoir.</p>`);
    sac.querySelector('.x').onclick = () => sac.classList.remove('ouvert');
    sac.querySelectorAll('[data-i]').forEach(b => b.onclick = () => { retirer(+b.dataset.i); dessinerSac(); });
    const v = sac.querySelector('.sac-valider'); if (v) v.onclick = () => { sac.classList.remove('ouvert'); boutique.surValider.forEach(f => f()); };
  }

  /* le cadran : le terminal du comptoir */
  const cadran = el('section', 'cadran'); cadran.setAttribute('role', 'dialog'); cadran.setAttribute('aria-modal', 'true'); calque.appendChild(cadran);
  const cle = (k) => cmd[k];
  function manque() {
    const m = [];
    if (!cmd.mode) m.push('le retrait ou l\'expédition');
    if (cmd.mode === 'expedition' && !cmd.pays) m.push('le pays');
    if (cmd.mode === 'expedition' && !cmd.ville.trim()) m.push('la ville de livraison');
    if (!cmd.prenom.trim()) m.push('votre prénom'); if (!cmd.nom.trim()) m.push('votre nom');
    if (!cmd.tel.trim()) m.push('votre numéro'); if (!cmd.residence.trim()) m.push('votre lieu de résidence');
    return m;
  }
  function ouvrirCadran() {
    if (!panier.length) { toast('Votre sac est vide.'); return; }
    son && son.ouvrir();
    const lignesMesures = panier.map((l, i) => {
      const p = pieceDe(l.id), jeu = jeuDe(l);
      if (p.cat !== 'sm') return '';
      if (!jeu) return `<div class="cd-mes"><b>${esc(p.nom)}</b><p class="cd-aide">Hillary prendra vos mesures avec vous.</p></div>`;
      const groupes = {};
      for (const c of jeu.champs) (groupes[c.g || 'Mesures'] = groupes[c.g || 'Mesures'] || []).push(c);
      return `<div class="cd-mes" data-l="${i}"><b>${esc(p.nom)}</b> <small>${esc(jeu.nom)} · ${jeu.champs.length} mesures${jeu.aValider ? ' · liste à valider par l\'atelier' : ''}</small>
        <div class="cd-choix"><label><input type="radio" name="mm${i}" value="ensemble" ${l.modeMesure !== 'maintenant' ? 'checked' : ''}> Hillary me les prend</label>
        <label><input type="radio" name="mm${i}" value="maintenant" ${l.modeMesure === 'maintenant' ? 'checked' : ''}> Je les donne maintenant</label></div>
        <div class="cd-champs" ${l.modeMesure === 'maintenant' ? '' : 'hidden'}>
          <p class="cd-aide">${esc(D.aide_mesures)} Une mesure laissée vide sera prise ensemble.</p>
          ${Object.entries(groupes).map(([g, cs]) => `<fieldset><legend>${esc(g)}</legend>${cs.map(c => `<label>${esc(c.l)}<span><input inputmode="decimal" data-m="${c.id}" value="${esc(l.mesures[c.id] || '')}"> cm</span></label>`).join('')}</fieldset>`).join('')}
        </div></div>`;
    }).join('');
    cadran.innerHTML = `
      <div class="cadran-cadre">
        <header><h2>Votre commande</h2><button type="button" class="x" aria-label="Fermer"><svg class="ic-x" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></header>
        <div class="cd-defile">
          <section><h3>Vos pièces</h3>${panier.map(l => { const p = pieceDe(l.id), v = prixLigne(l); return `<div class="cd-ligne"><span>${esc(p.nom)}<small>${esc(libDelaiLigne(l))}</small></span><b>${v == null ? 'sur devis' : fcfa(v)}</b></div>`; }).join('')}</section>
          ${lignesMesures ? `<section><h3>Vos mesures</h3>${lignesMesures}</section>` : ''}
          <section><h3>Livraison</h3>
            <div class="cd-choix cd-mode"><label><input type="radio" name="mode" value="retrait" ${cmd.mode === 'retrait' ? 'checked' : ''}> Retrait à l'atelier · gratuit</label>
            <label><input type="radio" name="mode" value="expedition" ${cmd.mode === 'expedition' ? 'checked' : ''}> Expédition</label></div>
            <p class="cd-aide cd-retrait" ${cmd.mode === 'retrait' ? '' : 'hidden'}>${esc(D.atelier.adresse)}</p>
            <div class="cd-exp" ${cmd.mode === 'expedition' ? '' : 'hidden'}>
              <label>Pays <select data-c="pays"><option value="">Choisir</option>${D.pays.map(p => `<option value="${p.id}" ${cmd.pays && cmd.pays.id === p.id ? 'selected' : ''}>${esc(p.nom)}${p.frais != null ? ' · ' + fcfa(p.frais) : ' · à confirmer'}</option>`).join('')}</select></label>
              <label><span>Ville de livraison <i>obligatoire</i></span><input data-c="ville" value="${esc(cmd.ville)}" placeholder="Abomey-Calavi"></label>
              <label>Quartier ou point de repère<input data-c="repere" value="${esc(cmd.repere)}" placeholder="derrière la pharmacie"></label>
            </div></section>
          <section><h3>Vous</h3>
            <div class="cd-grille">
              <label><span>Prénom <i>obligatoire</i></span><input data-c="prenom" autocomplete="given-name" value="${esc(cmd.prenom)}"></label>
              <label><span>Nom <i>obligatoire</i></span><input data-c="nom" autocomplete="family-name" value="${esc(cmd.nom)}"></label>
              <label><span>Téléphone <i>obligatoire</i></span><input data-c="tel" type="tel" autocomplete="tel" value="${esc(cmd.tel)}" placeholder="01 00 00 00 00"></label>
              <label><span>Lieu de résidence <i>obligatoire</i></span><input data-c="residence" value="${esc(cmd.residence)}" placeholder="Cotonou, Fidjrossè"><button type="button" class="puce cd-meme" hidden></button></label>
              <label>Email <i>facultatif</i><input data-c="mail" type="email" autocomplete="email" value="${esc(cmd.mail)}"></label>
              <label class="large">Une précision ? <i>facultatif</i><textarea data-c="note" rows="2">${esc(cmd.note)}</textarea></label>
            </div></section>
        </div>
        <footer>
          <div class="cd-recap"></div>
          <p class="cd-promesse">Rien n'est payé ici. Hillary vous écrit dès que la commande est validée, puis vous écrit ou vous appelle dès que la tenue est prête. Règlement par Mobile Money.</p>
          <p class="cd-encore" aria-live="polite"></p>
          <div class="cd-actions"><a class="bt bt-plein cd-envoyer" target="_blank" rel="noopener">Confirmer sur WhatsApp</a><div class="cd-qr" hidden></div></div>
        </footer>
      </div>`;
    cadran.classList.add('ouvert'); document.body.classList.add('en-cadran');
    const $ = (s) => cadran.querySelector(s), $$ = (s) => [...cadran.querySelectorAll(s)];
    $('.x').onclick = fermerCadran;
    $$('[data-c]').forEach(inp => inp.addEventListener('input', () => {
      const k = inp.dataset.c;
      if (k === 'pays') cmd.pays = D.pays.find(p => p.id === inp.value) || null; else cmd[k] = inp.value;
      maj();
    }));
    $$('input[name="mode"]').forEach(r => r.addEventListener('change', () => { cmd.mode = r.value; $('.cd-exp').hidden = cmd.mode !== 'expedition'; $('.cd-retrait').hidden = cmd.mode !== 'retrait'; maj(); }));
    $$('.cd-mes[data-l]').forEach(bloc => {
      const l = panier[+bloc.dataset.l];
      bloc.querySelectorAll('input[type=radio]').forEach(r => r.addEventListener('change', () => { l.modeMesure = r.value; bloc.querySelector('.cd-champs').hidden = r.value !== 'maintenant'; if (r.value !== 'maintenant') l.mesures = {}; sauver(); maj(); }));
      bloc.querySelectorAll('[data-m]').forEach(i => i.addEventListener('input', () => { const v = i.value.replace(',', '.').replace(/[^\d.]/g, ''); if (v) l.mesures[i.dataset.m] = v; else delete l.mesures[i.dataset.m]; sauver(); maj(); }));
    });
    $('.cd-meme').onclick = () => { cmd.residence = cmd.ville.trim(); $('[data-c="residence"]').value = cmd.residence; maj(); };
    function maj() {
      const m = manque(), t = totaux(), f = frais(), tot = totalCommande(), j = joursTotal();
      $('.cd-recap').innerHTML = `<div><span>Pièces</span><b>${t.devis ? 'sur devis' : fcfa(t.fcfa)}</b></div>
        <div><span>Livraison</span><b>${!cmd.mode ? 'à choisir' : cmd.mode === 'retrait' ? 'gratuite' : f === null ? 'à confirmer' : f ? fcfa(f) : 'à choisir'}</b></div>
        <div class="cd-total"><span>Total</span><b>${tot == null ? 'sur devis' : fcfa(tot)}</b></div>
        ${j != null ? `<div class="cd-date"><span>Disponible au plus tard le</span><b>${dateFr(dateDispo(j))}</b></div>` : ''}`;
      const meme = $('.cd-meme');
      meme.hidden = !(cmd.mode === 'expedition' && cmd.ville.trim() && cmd.residence.trim() !== cmd.ville.trim());
      meme.textContent = `J'habite à ${cmd.ville.trim()}`;
      const env = $('.cd-envoyer');
      if (m.length) { env.removeAttribute('href'); env.classList.add('inactif'); env.setAttribute('aria-disabled', 'true'); $('.cd-encore').textContent = 'Encore : ' + m.join(', ') + '.'; $('.cd-qr').hidden = true; }
      else {
        env.href = lienWhatsapp(); env.classList.remove('inactif'); env.removeAttribute('aria-disabled'); $('.cd-encore').textContent = '';
        /* sur ordinateur, un QR pour continuer sur le téléphone */
        if (matchMedia('(pointer: fine) and (min-width: 900px)').matches && window.qrcode) {
          try { const q = window.qrcode(0, 'L'); q.addData(env.href); q.make(); $('.cd-qr').innerHTML = q.createSvgTag({ cellSize: 2, margin: 2 }) + '<small>ou scannez avec votre téléphone</small>'; $('.cd-qr').hidden = false; } catch (e) { $('.cd-qr').hidden = true; }
        }
      }
      try { localStorage.setItem(cleStockage + ':client', JSON.stringify({ prenom: cmd.prenom, nom: cmd.nom, tel: cmd.tel, residence: cmd.residence, mail: cmd.mail })); } catch (e) { /* rien */ }
    }
    $('.cd-envoyer').addEventListener('click', (e) => {
      if (manque().length) { e.preventDefault(); $('.cd-encore').classList.remove('vibre'); void $('.cd-encore').offsetWidth; $('.cd-encore').classList.add('vibre'); return; }
      son && son.valider(); boutique.surEnvoi.forEach(f => f());
    });
    maj();
  }
  function fermerCadran() { cadran.classList.remove('ouvert'); document.body.classList.remove('en-cadran'); }
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && cadran.classList.contains('ouvert')) fermerCadran(); });

  majCompte();
  const boutique = { pieceDe, panier: () => panier, ajouter, ouvrirFiche, fermerFiche, ouvrirCadran, fermerCadran, toast, totaux, message, lienWhatsapp,
    vider() { panier = []; sauver(); }, surValider: [], surEnvoi: [], surChange, cmd };
  return boutique;
}
