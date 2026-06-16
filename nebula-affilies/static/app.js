/* ============================================================================
   NEBULA AFFILIÉS — moteur partagé (NA)
   API · icônes · son synthétisé · animations · NOVA (cerveau) · QR · confettis
   ============================================================================ */
const NA = (() => {
  /* ---------- helpers ---------- */
  const el = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstChild; };
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
  const fmt = (n) => (Math.round(n || 0)).toLocaleString('fr-FR').replace(/ |,/g, ' ');
  const ago = (ts) => {
    const s = Math.max(1, Math.floor(Date.now() / 1000 - ts));
    if (s < 60) return "à l'instant";
    if (s < 3600) return `il y a ${Math.floor(s / 60)} min`;
    if (s < 86400) return `il y a ${Math.floor(s / 3600)} h`;
    return `il y a ${Math.floor(s / 86400)} j`;
  };
  async function api(path, opts = {}) {
    const r = await fetch(path, {
      method: opts.method || (opts.body ? 'POST' : 'GET'),
      headers: { 'content-type': 'application/json' },
      credentials: 'same-origin',
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    let data = {}; try { data = await r.json(); } catch (e) { }
    if (!r.ok) throw Object.assign(new Error(data.error || 'Erreur'), { status: r.status, data });
    return data;
  }

  /* ---------- icônes (lignes fines, stroke 1.4) ---------- */
  const P = (d) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  const ICON = {
    grid: P('<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>'),
    users: P('<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><path d="M16 6.5a3 3 0 0 1 0 5.6"/><path d="M18 19c0-2.2-1-3.8-2.6-4.6"/>'),
    folder: P('<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'),
    link: P('<path d="M9 15l6-6"/><path d="M11 6l1-1a4 4 0 0 1 6 6l-1 1"/><path d="M13 18l-1 1a4 4 0 0 1-6-6l1-1"/>'),
    spark: P('<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 14l.6 1.8L21.5 16l-1.9.6L19 18l-.6-1.4L16.5 16l1.9-.2z"/>'),
    bell: P('<path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6"/><path d="M10 19a2 2 0 0 0 4 0"/>'),
    palette: P('<path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-1 2-2s-.6-1.5 0-2 1.5 0 2.5 0A4 4 0 0 0 21 13 9 9 0 0 0 12 3z"/><circle cx="7.5" cy="11" r="1"/><circle cx="12" cy="8" r="1"/><circle cx="16" cy="11" r="1"/>'),
    logout: P('<path d="M14 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-2"/><path d="M18 15l3-3-3-3"/><path d="M21 12H9"/>'),
    copy: P('<rect x="9" y="9" width="11" height="11" rx="2.5"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/>'),
    arrow: P('<path d="M7 17L17 7"/><path d="M8 7h9v9"/>'),
    check: P('<path d="M4 12.5l5 5 11-11"/>'),
    plus: P('<path d="M12 5v14M5 12h14"/>'),
    bolt: P('<path d="M13 3L5 13h6l-1 8 8-10h-6z"/>'),
    sound: P('<path d="M5 9v6h4l5 4V5L9 9z"/><path d="M17 9a4 4 0 0 1 0 6"/>'),
    mute: P('<path d="M5 9v6h4l5 4V5L9 9z"/><path d="M22 9l-5 6M17 9l5 6"/>'),
    music: P('<path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="2.6"/><circle cx="17" cy="16" r="2.6"/>'),
    close: P('<path d="M6 6l12 12M18 6L6 18"/>'),
    send: P('<path d="M5 12l15-7-7 15-2-6z"/>'),
    chart: P('<path d="M4 19V5M4 19h16"/><path d="M8 16l3-4 3 2 4-6"/>'),
    medal: P('<circle cx="12" cy="14" r="5"/><path d="M9 9L7 3M15 9l2-6"/>'),
    phone: P('<rect x="6" y="3" width="12" height="18" rx="3"/><path d="M11 18h2"/>'),
    meteor: P('<circle cx="14" cy="10" r="4.2"/><path d="M10.8 13.2L4 20M8 6.5L5.5 4M13.2 5.4L15 3.6M6.4 12L4.6 11"/>'),
    comet: P('<circle cx="16" cy="8" r="3.3"/><path d="M13.3 10.4L4 19M17 4.2l1.6-1.4M19.3 7l1.4-1.2"/><circle cx="8" cy="15" r="1"/>'),
    planet: P('<circle cx="12" cy="12" r="6"/><ellipse cx="12" cy="12" rx="11" ry="3.6" transform="rotate(-22 12 12)"/>'),
    star: P('<path d="M12 3.5l2.6 5.6 6 .7-4.4 4.1 1.2 6L12 17l-5.4 3 1.2-6L3.4 9.8l6-.7z"/>'),
    supernova: P('<circle cx="12" cy="12" r="2.6"/><path d="M12 2.4v3.4M12 18.2V21.6M2.4 12h3.4M18.2 12h3.4M5.2 5.2l2.3 2.3M16.5 16.5l2.3 2.3M18.8 5.2l-2.3 2.3M7.5 16.5l-2.3 2.3"/>'),
    nebula: P('<path d="M8 15a3.5 3.5 0 0 1 .6-6.9A4.5 4.5 0 0 1 17 8.6a3 3 0 0 1-.5 6.4z"/><circle cx="10.5" cy="11" r="1"/><circle cx="14" cy="12.6" r="1"/>'),
    crown: P('<path d="M4 8l3.5 3L12 5l4.5 6L20 8l-1.5 10h-13z"/><path d="M5.5 18h13"/>'),
    help: P('<circle cx="12" cy="12" r="9"/><path d="M9.3 9.3a2.7 2.7 0 0 1 5.2 1c0 1.8-2.7 2-2.7 3.8"/><path d="M12 17.4v.01"/>'),
    coins: P('<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.66 3.13 3 7 3s7-1.34 7-3V6"/><path d="M5 12c0 1.66 3.13 3 7 3s7-1.34 7-3"/>'),
    doc: P('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 16.5h4"/>'),
    megaphone: P('<path d="M4 10v4a1 1 0 0 0 1 1h2l5 4V6L7 10H5a1 1 0 0 0-1 0z"/><path d="M16 8.5a4 4 0 0 1 0 7"/>'),
    download: P('<path d="M12 3v12"/><path d="M7 11l5 5 5-5"/><path d="M5 21h14"/>'),
    video: P('<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9l5 3-5 3z"/>'),
    edit: P('<path d="M4 20h4l10.5-10.5a2 2 0 0 0-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>'),
    shield: P('<path d="M12 3l7 3v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>'),
    upload: P('<path d="M12 21V9"/><path d="M7 13l5-5 5 5"/><path d="M5 4h14"/>'),
    trash: P('<path d="M4 7h16"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><path d="M6 7l1 13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-13"/>'),
    image: P('<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="8.5" cy="9.5" r="1.8"/><path d="M21 16l-5-5L5 20"/>'),
  };
  const icon = (n) => ICON[n] || '';

  /* ---------- son synthétisé (Web Audio) ---------- */
  const Sound = (() => {
    let ctx, master, comp, started = false;
    let enabled = localStorage.getItem('na_sfx') !== '0';
    let ambientOn = localStorage.getItem('na_amb') === '1';
    let ambient = null;
    const isMobile = matchMedia('(max-width:860px)').matches;
    function ensure() {
      if (ctx) return;
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      ctx = new AC();
      comp = ctx.createDynamicsCompressor();
      master = ctx.createGain(); master.gain.value = isMobile ? 0.5 : 0.32;   // boost mobile
      master.connect(comp); comp.connect(ctx.destination);
      const b = ctx.createBuffer(1, 1, 22050), s = ctx.createBufferSource();  // déblocage iOS
      s.buffer = b; s.connect(ctx.destination); s.start(0);
    }
    function unlock() { ensure(); if (ctx && ctx.state === 'suspended') ctx.resume(); if (ambientOn) startAmbient(); }
    function tone({ f = 440, t = 'sine', d = 0.12, v = 0.3, a = 0.005, g = null, dest = null }) {
      if (!ctx || !enabled) return;
      const o = ctx.createOscillator(), gn = ctx.createGain(), now = ctx.currentTime;
      o.type = t; o.frequency.setValueAtTime(f, now);
      if (g) o.frequency.exponentialRampToValueAtTime(g, now + d);
      gn.gain.setValueAtTime(0, now);
      gn.gain.linearRampToValueAtTime(v, now + a);
      gn.gain.exponentialRampToValueAtTime(0.0001, now + d);
      o.connect(gn); gn.connect(dest || master); o.start(now); o.stop(now + d + 0.02);
    }
    function startAmbient() {
      if (!ctx || ambient) return;
      const g = ctx.createGain(); g.gain.value = 0.0; g.connect(master);
      g.gain.linearRampToValueAtTime(0.05, ctx.currentTime + 3);
      const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 600; lp.connect(g);
      const lfo = ctx.createOscillator(), lfoG = ctx.createGain();
      lfo.frequency.value = 0.06; lfoG.gain.value = 220; lfo.connect(lfoG); lfoG.connect(lp.frequency); lfo.start();
      const oscs = [110, 164.81, 220].map((f, i) => {
        const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f * (i === 2 ? 1.003 : 1);
        o.connect(lp); o.start(); return o;
      });
      ambient = { g, lfo, oscs };
    }
    function stopAmbient() {
      if (!ambient) return; const a = ambient; ambient = null;
      try { a.g.gain.linearRampToValueAtTime(0, ctx.currentTime + 1.2); } catch (e) { }
      setTimeout(() => { try { a.lfo.stop(); a.oscs.forEach(o => o.stop()); } catch (e) { } }, 1400);
    }
    const sfx = {
      click() { tone({ f: 320, g: 440, d: 0.07, v: 0.18, t: 'triangle' }); },
      tab() { tone({ f: 240, g: 620, d: 0.16, v: 0.16, t: 'sine' }); },
      ok() {[0,1,2].forEach(i => setTimeout(() => tone({ f: [523, 659, 784][i], d: 0.18, v: 0.22, t: 'triangle' }), i * 70)); },
      cash() {[0,1].forEach(i => setTimeout(() => tone({ f: [988, 1319][i], d: 0.13, v: 0.2, t: 'square' }), i * 80)); },
      rank() {[0,1,2,3].forEach(i => setTimeout(() => tone({ f: [523, 659, 784, 1047][i], d: 0.28, v: 0.26, t: 'sawtooth' }), i * 110)); },
      err() { tone({ f: 180, g: 90, d: 0.25, v: 0.2, t: 'sawtooth' }); },
      open() { tone({ f: 420, g: 760, d: 0.2, v: 0.18, t: 'sine' }); },
    };
    return {
      unlock, sfx,
      get enabled() { return enabled; },
      get ambient() { return ambientOn; },
      toggle() { enabled = !enabled; localStorage.setItem('na_sfx', enabled ? '1' : '0'); if (enabled) { ensure(); sfx.ok(); } return enabled; },
      toggleAmbient() { ambientOn = !ambientOn; localStorage.setItem('na_amb', ambientOn ? '1' : '0'); ensure(); ambientOn ? startAmbient() : stopAmbient(); return ambientOn; },
    };
  })();
  ['pointerdown', 'keydown', 'touchstart'].forEach(ev => addEventListener(ev, () => Sound.unlock(), { once: true }));

  /* ---------- toast ---------- */
  let toastWrap;
  function toast(msg, kind = '') {
    if (!toastWrap) { toastWrap = el('<div class="toasts"></div>'); document.body.appendChild(toastWrap); }
    const t = el(`<div class="toast ${kind}"><span class="bar"></span><span>${esc(msg)}</span></div>`);
    toastWrap.appendChild(t);
    if (kind === 'bad') Sound.sfx.err(); else if (kind === 'ok') Sound.sfx.ok();
    setTimeout(() => { t.style.transition = 'opacity .4s, transform .4s'; t.style.opacity = '0'; t.style.transform = 'translateY(-10px)'; setTimeout(() => t.remove(), 420); }, 3200);
  }

  /* ---------- count-up ---------- */
  function countUp(node, to, { money = false } = {}) {
    to = Number(to) || 0; const dur = 900, t0 = performance.now();
    function step(t) {
      const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3), val = to * e;
      node.textContent = money ? fmt(val) : Math.round(val).toLocaleString('fr-FR');
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* ---------- reveal au scroll ---------- */
  const io = new IntersectionObserver((ents) => ents.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.12 });
  function reveal(root = document) { root.querySelectorAll('.rv:not(.in)').forEach((n, i) => { n.style.transitionDelay = (i % 6) * 60 + 'ms'; io.observe(n); }); }

  /* ---------- QR (recoloré à l'accent) ---------- */
  function qr(data, size = 220) {
    const acc = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim().replace('#', '') || '7b5cff';
    return `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&margin=8&bgcolor=0b0b12&color=${acc}&data=${encodeURIComponent(data)}`;
  }

  /* ---------- confettis (rank-up / succès) ---------- */
  function celebrate() {
    const cv = el('<canvas class="confetti"></canvas>'); document.body.appendChild(cv);
    const cx = cv.getContext('2d'), W = cv.width = innerWidth, H = cv.height = innerHeight;
    const acc = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#7b5cff';
    const cols = [acc, '#22d3ee', '#36f5a0', '#e6c34c', '#fff'];
    const ps = Array.from({ length: 130 }, () => ({ x: W / 2, y: H * 0.35, vx: (Math.random() - 0.5) * 14, vy: Math.random() * -16 - 4, r: Math.random() * 6 + 3, c: cols[~~(Math.random() * cols.length)], a: 1, rot: Math.random() * 6 }));
    let f = 0;
    (function loop() {
      cx.clearRect(0, 0, W, H); f++;
      ps.forEach(p => { p.vy += 0.5; p.x += p.vx; p.y += p.vy; p.a -= 0.008; p.rot += 0.2; cx.save(); cx.globalAlpha = Math.max(0, p.a); cx.translate(p.x, p.y); cx.rotate(p.rot); cx.fillStyle = p.c; cx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 1.6); cx.restore(); });
      if (f < 140) requestAnimationFrame(loop); else cv.remove();
    })();
    Sound.sfx.rank();
  }

  /* ---------- NOVA (cerveau) ---------- */
  function nova(scopeLabel) {
    const fab = el(`<button class="nova-fab" title="NOVA — ton cerveau IA"><span class="pulse"></span>${icon('spark')}</button>`);
    fab.querySelector('svg').style.cssText = 'width:26px;height:26px;color:#07060e';
    const panel = el(`<div class="nova-panel">
      <div class="nova-head"><div class="orb"></div><div class="grow"><div style="font-family:Space Grotesk;font-weight:700">NOVA</div><div class="faint" style="font-size:.74rem">${esc(scopeLabel)}</div></div><button class="icon-btn close" style="width:34px;height:34px">${icon('close')}</button></div>
      <div class="nova-log"></div>
      <div class="nova-foot"><input placeholder="Demande à NOVA…" /><button class="nova-send">${icon('send')}</button></div>
    </div>`);
    document.body.append(fab, panel);
    const log = panel.querySelector('.nova-log'), input = panel.querySelector('input');
    const add = (who, text) => { const m = el(`<div class="nova-msg ${who === 'nova' ? 'n' : 'u'}">${esc(text)}</div>`); log.appendChild(m); log.scrollTop = log.scrollHeight; return m; };
    let loaded = false, open = false;
    async function load() {
      try { const d = await api('/api/brain/history'); if (!d.messages.length) add('nova', `Salut 👋 Je suis NOVA, ${scopeLabel.toLowerCase()}. Pose-moi une question : « qui relancer ? », « comment atteindre le rang suivant ? »…`); else d.messages.forEach(m => add(m.who, m.text)); } catch (e) { }
      loaded = true;
    }
    async function send() {
      const msg = input.value.trim(); if (!msg) return; input.value = '';
      add('user', msg); Sound.sfx.click();
      const typing = el(`<div class="nova-msg n"><span class="typing"><i></i><i></i><i></i></span></div>`); log.appendChild(typing); log.scrollTop = log.scrollHeight;
      try { const d = await api('/api/brain', { body: { message: msg } }); typing.remove(); add('nova', d.reply); Sound.sfx.open(); }
      catch (e) { typing.remove(); add('nova', "Connexion interrompue. Réessaie."); }
    }
    function toggle() { open = !open; panel.classList.toggle('on', open); if (open) { Sound.sfx.open(); if (!loaded) load(); setTimeout(() => input.focus(), 200); } }
    fab.onclick = toggle; panel.querySelector('.close').onclick = toggle;
    panel.querySelector('.nova-send').onclick = send;
    input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
  }

  /* ---------- didacticiel / guide pas-à-pas ---------- */
  function tour(steps, key) {
    let i = 0;
    const scrim = el('<div class="scrim tour-scrim"></div>');
    scrim.appendChild(el('<div class="card tour-card"><div class="in"></div></div>'));
    document.body.appendChild(scrim);
    const inn = scrim.querySelector('.in');
    function render() {
      const s = steps[i];
      inn.innerHTML = `<div class="flex between" style="margin-bottom:14px"><span class="eyebrow"><span class="dot"></span>Guide · ${i + 1}/${steps.length}</span><button class="icon-btn tx" style="width:32px;height:32px">${icon('close')}</button></div>`
        + `<div class="tour-ic">${icon(s.icon || 'spark')}</div>`
        + `<h2 style="font-size:1.5rem;margin:16px 0 10px">${esc(s.title)}</h2>`
        + `<p style="font-size:14.5px;line-height:1.6;color:var(--muted)">${s.text}</p>`
        + `<div class="flex between" style="margin-top:24px;align-items:center">`
        + `<button class="btn sm ghost tp" ${i === 0 ? 'style="visibility:hidden"' : ''}>← Précédent</button>`
        + `<div class="flex gap8" style="align-items:center">${steps.map((_, k) => `<span class="tour-dot${k === i ? ' on' : ''}"></span>`).join('')}</div>`
        + `<button class="btn sm primary tn">${i === steps.length - 1 ? 'Terminer' : 'Suivant →'}</button></div>`;
      inn.querySelector('.tx').onclick = close;
      inn.querySelector('.tp').onclick = () => { if (i > 0) { i--; render(); Sound.sfx.tab(); } };
      inn.querySelector('.tn').onclick = () => { if (i < steps.length - 1) { i++; render(); Sound.sfx.tab(); } else close(); };
    }
    function close() { scrim.remove(); if (key) localStorage.setItem(key, '1'); }
    scrim.classList.add('on'); render(); Sound.sfx.open();
  }

  return { el, esc, fmt, ago, api, icon, sound: Sound, toast, countUp, reveal, qr, celebrate, nova, tour };
})();
