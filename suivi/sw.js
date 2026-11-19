// NEBULA Suivi · reçoit les notifications, même application fermée.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("push", e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (_) { d = { titre: "NEBULA", texte: e.data ? e.data.text() : "" }; }
  e.waitUntil(self.registration.showNotification(d.titre || "NEBULA", {
    body: d.texte || "", tag: d.tag || "nebula", renotify: true, icon: "icone-192.png", badge: "icone-192.png",
    // une alerte qui insiste : elle reste à l'écran jusqu'au toucher, et vibre plus longtemps
    requireInteraction: !!d.insiste, vibrate: d.insiste ? [500, 150, 500, 150, 800] : [300, 120, 300], data: { url: d.url || "./" }
  }));
});
self.addEventListener("notificationclick", e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || "./";
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(cs => {
    for (const c of cs) if ("focus" in c) { if ("navigate" in c) c.navigate(url).catch(() => {}); return c.focus(); }
    return self.clients.openWindow(url);
  }));
});
