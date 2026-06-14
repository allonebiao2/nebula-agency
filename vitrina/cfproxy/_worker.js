// Cloudflare Pages — proxy inverse vers l'app Vitrina (Railway)
// Sert vitrina.nebula-agency.online sans domaine custom Railway (gratuit, sans CB).
const ORIGIN = "https://vitrina-production-686b.up.railway.app";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const target = ORIGIN + url.pathname + url.search;
    const headers = new Headers(request.headers);
    headers.delete("host");
    const init = { method: request.method, headers, redirect: "manual" };
    if (request.method !== "GET" && request.method !== "HEAD") {
      init.body = await request.arrayBuffer();
    }
    const resp = await fetch(target, init);
    // recopie fidèle (préserve Set-Cookie) en retirant les en-têtes de hop
    const out = new Response(resp.body, resp);
    out.headers.delete("content-encoding");
    out.headers.delete("content-length");
    return out;
  }
};
