/* LE MONDE · le carnet : « ce que vous savez de la maison ».
   Mongazi (2026-11-12) : « on pourrait être tenté de finir par tout choisir, et
   en le faisant on apprendra beaucoup sur la boutique : qui l'a créée, la
   cliente, les réalisations, la vision, absolument tout ».

   Chaque réplique qui apprend quelque chose de vrai sur la maison inscrit un
   SAVOIR au carnet. Le compteur (« 7 sur 12 ») donne envie d'explorer toutes
   les réponses. ⛔ Un savoir n'existe que si sa donnée existe : tant
   qu'Hillary n'a pas raconté son histoire, ce savoir n'est pas au carnet (on
   ne compte pas ce qu'on ne peut pas dire). */
export function creerCarnet({ calque, savoirs, cle = 'monde:carnet', son, toast }) {
  const actifs = savoirs.filter(s => s.texte);
  let appris = new Set();
  try { appris = new Set((JSON.parse(localStorage.getItem(cle)) || []).filter(id => actifs.some(s => s.id === id))); } catch (e) { /* rien */ }

  const bt = document.createElement('button');
  bt.type = 'button'; bt.className = 'bt-carnet';
  bt.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11"/></svg><span class="compte"></span>';
  calque.appendChild(bt);
  const panneau = document.createElement('aside'); panneau.className = 'carnet'; panneau.setAttribute('aria-label', 'Votre carnet'); calque.appendChild(panneau);
  const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function maj() {
    bt.querySelector('.compte').textContent = `${appris.size}/${actifs.length}`;
    bt.setAttribute('aria-label', `Votre carnet : ${appris.size} sur ${actifs.length}`);
    bt.classList.toggle('complet', appris.size === actifs.length);
  }
  function dessiner() {
    const reste = actifs.length - appris.size;
    panneau.innerHTML = `<header><h3>Ce que vous savez de la maison</h3><button type="button" class="x" aria-label="Fermer">×</button></header>
      <div class="carnet-jauge"><i style="width:${Math.round(appris.size / actifs.length * 100)}%"></i></div>
      <p class="carnet-reste">${reste ? `Encore ${reste} chose${reste > 1 ? 's' : ''} à découvrir. Parlez à tout le monde, essayez chaque réponse.` : 'Vous connaissez la maison par cœur.'}</p>
      ${actifs.filter(s => appris.has(s.id)).map(s => `<div class="carnet-savoir"><b>${esc(s.titre)}</b><p>${esc(s.texte)}</p><small>${esc(s.source)}</small></div>`).join('')}
      ${actifs.filter(s => !appris.has(s.id)).map(s => `<div class="carnet-savoir inconnu"><b>?</b><p>${esc(s.indice || 'Quelqu\'un ici le sait.')}</p></div>`).join('')}`;
    panneau.querySelector('.x').onclick = () => panneau.classList.remove('ouvert');
  }
  bt.onclick = () => { panneau.classList.toggle('ouvert'); if (panneau.classList.contains('ouvert')) { dessiner(); son && son.ouvrir(); } };

  function apprendre(id) {
    const s = actifs.find(x => x.id === id);
    if (!s || appris.has(id)) return false;
    appris.add(id);
    try { localStorage.setItem(cle, JSON.stringify([...appris])); } catch (e) { /* rien */ }
    maj(); bt.classList.remove('saute'); void bt.offsetWidth; bt.classList.add('saute');
    toast && toast(`<b>Carnet</b> · ${esc(s.titre)} <small>(${appris.size}/${actifs.length})</small>`, { duree: 2800 });
    if (appris.size === actifs.length && toast) setTimeout(() => toast('<b>Vous connaissez la maison par cœur.</b>', { duree: 5000 }), 1200);
    return true;
  }
  maj();
  return { apprendre, get appris() { return appris; }, total: actifs.length };
}
