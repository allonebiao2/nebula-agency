/* L'HÔTESSE QUI VIENT SALUER · Luxury Club 229 (Mongazi, 26/11 : « l'assistant dès que l'immersion est faite, comme les
 * autres »). Adapté du module commun des aperçus NEBULA (nebula-apercus/_express/_signatures/invite.js).
 *
 * Quand : à la fin de la visite 3D de la page, ou au plus tard 18 s après l'arrivée (jamais avant 6 s), une fois par visite.
 * Jamais par-dessus la porte d'entrée, l'écran de bienvenue, le menu ouvert ou une fenêtre de réservation.
 * Qui : un portrait DESSINÉ (jamais un vrai visage) ; elle n'invente aucun résultat, aucun avis, aucune rareté.
 * « Oui » mène à l'aide de la page : un conseil sur WhatsApp, la consultation INA, la consultation d'harmonisation.
 * La carte est OPAQUE (règle de la maison : seules les bandes de bord passent sur du texte), au-dessus de la barre du bas.
 * Réglage : <script type="application/json" id="invite-cfg">{texte, oui, non, nom, avatar, action, theme, bas}</script>
 */
(function () {
  var cfgEl = document.getElementById('invite-cfg'); if (!cfgEl) return;
  var cfg; try { cfg = JSON.parse(cfgEl.textContent); } catch (e) { return; }
  var cle = 'invite-vue:' + location.pathname, deja = false;
  try { deja = sessionStorage.getItem(cle) === '1'; } catch (e) { /* stockage indisponible : on montre quand même */ }
  if (deja) return;
  var calme = matchMedia('(prefers-reduced-motion: reduce)').matches, t0 = Date.now(), montre = false;
  var sombre = cfg.theme === 'sombre';

  var css = document.createElement('style');
  css.textContent =
    '#invite{position:fixed;z-index:9000;right:22px;bottom:calc(' + (cfg.bas || 0) + 'px + 18px);width:min(390px,calc(100vw - 44px));' +
    'background:' + (sombre ? '#15120d' : '#fbf8f2') + ';color:' + (sombre ? '#f3eadb' : '#1f1e1a') + ';' +
    'border:1px solid ' + (sombre ? 'rgba(226,196,122,.4)' : 'rgba(31,30,26,.1)') + ';border-radius:20px;' +
    'box-shadow:0 24px 60px rgba(0,0,0,.38);padding:16px 16px 14px;display:grid;grid-template-columns:64px 1fr;gap:12px;' +
    'font-family:"Jost",system-ui,sans-serif;transform:translateY(24px) scale(.96);opacity:0;transition:transform .5s cubic-bezier(.2,.9,.2,1.15),opacity .35s}' +
    '#invite.la{transform:none;opacity:1}#invite .iv-av{width:64px;height:64px;border-radius:50%;overflow:hidden;background:#e8e2d6;' +
    'box-shadow:0 0 0 2px ' + (sombre ? '#c9a84c' : '#e6d3a0') + '}' +
    '#invite .iv-av>*{width:100%;height:100%}#invite b{display:block;font:600 12px/1.2 "DM Mono",monospace;letter-spacing:.12em;text-transform:uppercase;' +
    'color:' + (sombre ? '#e2c47a' : '#7d5f18') + ';margin:4px 0 6px}' +
    '#invite p{margin:0;font-size:15px;line-height:1.45;min-height:3em}#invite .iv-act{grid-column:1/-1;display:flex;gap:8px;flex-wrap:wrap}' +
    '#invite button{all:unset;cursor:pointer;min-height:44px;padding:0 18px;border-radius:999px;font:600 14px/1 "Jost",sans-serif;display:inline-grid;place-items:center}' +
    '#invite button:focus-visible{outline:2px solid #c9a84c;outline-offset:3px}' +
    '#invite .iv-oui{background:#c9a84c;color:#1a140a}#invite .iv-oui:hover{background:' + (sombre ? '#f3eadb' : '#1f1e1a') + ';color:' + (sombre ? '#1a140a' : '#fbf8f2') + '}' +
    '#invite .iv-non{border:1px solid ' + (sombre ? 'rgba(226,196,122,.45)' : 'rgba(31,30,26,.25)') + ';font-weight:500}' +
    '#invite .iv-x{position:absolute;top:4px;right:6px;min-height:44px;width:44px;padding:0;font-size:22px;font-weight:400;color:' + (sombre ? '#d3c7b1' : '#55524b') + '}' +
    '@media (max-width:760px){#invite{left:0;right:0;bottom:' + (cfg.bas || 0) + 'px;width:auto;border-radius:20px 20px 0 0;padding:16px 16px 14px}}' +
    /* le portrait animé (commun aux aperçus) */
    '.av{display:block;width:100%;height:100%;border-radius:50%}' +
    '.av .av-yeux{transform-origin:60px 61px;animation:av-cligne 4.6s infinite}' +
    '@keyframes av-cligne{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}' +
    '.av .av-bouche>*{display:none}' +
    '.av[data-e="neutre"] .b-neutre,.av[data-e="sourire"] .b-sourire,.av[data-e="ravi"] .b-ravi{display:inline}' +
    '.parle .av .av-bouche>*{display:none}' +
    '.parle .av .b-parle{display:inline;transform-origin:60px 75.5px;animation:av-parle .22s infinite alternate}' +
    '@keyframes av-parle{from{transform:scaleY(.35)}to{transform:scaleY(1.15)}}' +
    '@media (prefers-reduced-motion:reduce){.av .av-yeux,.parle .av .b-parle{animation:none}}';
  document.head.appendChild(css);

  function agir() {
    var a = cfg.action || {};
    if (a.type === 'clic') { var el = document.querySelector(a.sel); if (el) el.click(); }
    else if (a.type === 'harmo' && window.LC_HARMO && window.LC_HARMO.ouvrir) window.LC_HARMO.ouvrir();
    else if (a.url) window.open(a.url, '_blank', 'noopener');
  }
  // jamais par-dessus ce qui demande déjà l'attention
  function occupe() {
    var g = document.getElementById('welcome-gate');
    if (g && g.offsetParent !== null && getComputedStyle(g).opacity !== '0' && getComputedStyle(g).visibility !== 'hidden') return true;
    if (document.querySelector('.s3d-porte:not(.ouverte)')) return true;
    return !!document.querySelector('.lc-cat-panel.open, .dlg.ouvert, .modal-scrim.show, #consultModal.show, .lc-modal.on, #cartDrawer.open');
  }
  function montrer() {
    if (montre || occupe()) return;
    montre = true; try { sessionStorage.setItem(cle, '1'); } catch (e) {}
    var b = document.createElement('div'); b.id = 'invite'; b.setAttribute('role', 'dialog'); b.setAttribute('aria-label', cfg.nom || "L'hôtesse");
    b.innerHTML = '<span class="iv-av"></span><div><b></b><p aria-live="polite"></p></div>' +
      '<div class="iv-act"><button type="button" class="iv-oui"></button><button type="button" class="iv-non"></button></div>' +
      '<button type="button" class="iv-x" aria-label="Fermer">×</button>';
    var av = b.querySelector('.iv-av');
    if (cfg.avatar) av.innerHTML = cfg.avatar;
    b.querySelector('b').textContent = cfg.nom || '';
    b.querySelector('.iv-oui').textContent = cfg.oui || 'Oui, aidez-moi';
    b.querySelector('.iv-non').textContent = cfg.non || "Je regarde d'abord";
    document.body.appendChild(b);
    requestAnimationFrame(function () { requestAnimationFrame(function () { b.classList.add('la'); }); });
    var p = b.querySelector('p'), visage = av.querySelector('.av'), txt = cfg.texte || 'Bonjour 👋 Je peux vous aider ?', k = 0;
    if (visage) { visage.dataset.e = 'sourire'; av.classList.add('parle'); }
    if (calme) { p.textContent = txt; av.classList.remove('parle'); }
    else {
      var h = setInterval(function () {
        p.textContent = txt.slice(0, ++k);
        if (k >= txt.length) { clearInterval(h); av.classList.remove('parle'); if (visage) visage.dataset.e = 'ravi'; }
      }, 22);
    }
    function partir() { b.classList.remove('la'); removeEventListener('scroll', surDefile); setTimeout(function () { b.remove(); }, 450); }
    // le visiteur REMONTE dans la visite 3D : elle s'efface (27/11 : restée affichée, elle recouvrait la fiche d'une étape)
    function surDefile() { if (dansVisite()) partir(); }
    addEventListener('scroll', surDefile, { passive: true });
    b.querySelector('.iv-oui').addEventListener('click', function () { partir(); agir(); });
    b.querySelector('.iv-non').addEventListener('click', partir);
    b.querySelector('.iv-x').addEventListener('click', partir);
    setTimeout(function () { if (b.isConnected && !b.matches(':hover')) partir(); }, 30000);
  }
  // quand ? JAMAIS PENDANT LA VISITE 3D (26/11 : à 18 s elle venait se poser sur la fiche de chaque soin, au
  // téléphone sur un quart de l'écran) : dès que la visite est derrière le visiteur, ou après 18 s passées hors de la
  // visite (au-dessus d'elle, ou sur une page sans 3D). Jamais avant 6 s.
  // la visite 3D remplit-elle l'écran ?
  function dansVisite() {
    var v = document.querySelector('.s3d');
    if (!v || v.offsetHeight <= innerHeight || v.classList.contains('s3d-sans')) return false;
    var r = v.getBoundingClientRect(), mi = innerHeight * 0.5;
    return r.top < mi && r.bottom > mi;
  }
  function verifier() {
    if (montre) return;
    var dt = Date.now() - t0; if (dt < 6000) return;
    var v = document.querySelector('.s3d');
    if (v && v.offsetHeight > innerHeight && !v.classList.contains('s3d-sans')) {
      var r = v.getBoundingClientRect(), mi = innerHeight * 0.5;
      if (dansVisite()) return;                          // la visite remplit l'écran : on ne la recouvre pas
      if (r.bottom <= mi || dt > 18000) montrer();       // la visite est finie, ou on est ailleurs depuis 18 s
      return;
    }
    if (scrollY > innerHeight * 1.5 || dt > 18000) montrer();
  }
  addEventListener('scroll', verifier, { passive: true });
  setInterval(verifier, 1000);
})();
