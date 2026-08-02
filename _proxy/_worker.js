// Relais NEBULA Affiliés (Cloudflare Pages, mode avancé _worker.js).
// partenaires.nebula-agency.online -> app Render, appelée par son vrai nom de service.
// SSL fourni gratuitement par Cloudflare.
// 2026-08-02 : Railway avait fait disparaître l'application (404 Application not found
// sur l'origine elle-même). Bascule vers Render + Supabase, cf nebula-affilies/DEPLOIEMENT.md.
const ORIGIN = "https://nebula-affilies.onrender.com";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const target = ORIGIN + url.pathname + url.search;

    const headers = new Headers(request.headers);
    headers.set("X-Forwarded-Host", url.host);
    headers.set("X-Forwarded-Proto", "https");

    // cf.cacheTtl:0 -> l'edge Cloudflare ne met PAS en cache la réponse de Railway
    // (sinon CSS/JS gelés jusqu'à 4h après chaque mise à jour)
    const init = { method: request.method, headers, redirect: "manual", cf: { cacheTtl: 0, cacheEverything: false } };
    if (request.method !== "GET" && request.method !== "HEAD") init.body = request.body;

    let resp;
    try {
      resp = await fetch(target, init);
    } catch (e) {
      return new Response("Relais indisponible. Reessayez dans un instant.", { status: 502 });
    }
    const out = new Headers(resp.headers);
    // pas de cache navigateur sur les assets actifs : les corrections apparaissent tout de suite
    out.set("Cache-Control", "no-cache, must-revalidate");
    return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: out });
  },
};
