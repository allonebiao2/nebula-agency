/* Boussole — service worker (offline shell). Bumper V à chaque déploiement. */
const V = '20260709d';
const CACHE = 'boussole-' + V;
const ASSETS = [
  './',
  'index.html',
  'manifest.webmanifest',
  'assets/css/app.css?v=' + V,
  'assets/js/app.js?v=' + V,
  'assets/js/config.js',
  'assets/js/icons.js',
  'assets/js/store.js',
  'assets/js/charts.js',
  'assets/js/ui.js',
  'assets/js/supabase.js',
  'assets/js/vendor/supabase.js',
  'assets/fonts/BricolageGrotesque.woff2',
  'assets/icons/icon.svg',
  'assets/icons/logo-mark.png',
  'assets/icons/icon-192.png',
  'assets/icons/icon-512.png',
  'assets/icons/favicon-48.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await Promise.all(ASSETS.map((u) => cache.add(new Request(u, { cache: 'reload' })).catch(() => {})));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Ne jamais intercepter Supabase / cross-origin : réseau direct.
  if (url.origin !== self.location.origin) return;

  // Navigations : réseau d'abord, repli sur le shell hors-ligne.
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(() => caches.match('index.html')));
    return;
  }
  // Assets : cache d'abord, sinon réseau (et on met en cache).
  e.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    try {
      const res = await fetch(req);
      if (res && res.status === 200) { const c = await caches.open(CACHE); c.put(req, res.clone()); }
      return res;
    } catch (err) {
      return cached || Response.error();
    }
  })());
});
