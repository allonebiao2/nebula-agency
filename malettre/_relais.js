// MA LETTRE À… · le relais des lettres (Cloudflare Pages, mode avancé).
// `_dist.py` le copie en `_dist/_worker.js`. ⛔ On édite CE fichier, jamais la copie.
//
//   /l/<jeton>            → la lettre, servie par la fonction `malettre-lettre`
//   /l/<jeton>/retrait    → POST : la retirer (le bouton du pied de la lettre)
//   /l/<jeton>/etat       → l'état, lu par la page « merci »
//   tout le reste         → les fichiers du site (env.ASSETS)
//
// ⚠️ EN MODE AVANCÉ, `_headers` peut ne pas s'appliquer à ce que le relais rend :
// le relais pose donc LUI-MÊME les en-têtes de sécurité sur chaque réponse
// (2026-10-21), et `noindex` + `no-referrer` sur toute lettre.
// ⚠️ La forme du jeton est celle du serveur (`JETON_FORME`, `_shared/lettre.ts`) :
// une adresse mal formée part au site, qui rend sa page « Cette lettre n'est pas ici ».

const FONCTION = "https://xukduhqqfzogisoimhyo.supabase.co/functions/v1/malettre-lettre";
const LETTRE = /^\/l\/([23456789bcdfghjkmnpqrstvwxyz]{22})(?:\/(retrait|etat))?\/?$/;
const SECURITE = {
  "X-Frame-Options": "SAMEORIGIN",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
};

// ⛔ SUPABASE SERT TOUT HTML EN `text/plain`, AVEC `Content-Security-Policy: default-src 'none'; sandbox`
// et un cookie de SON domaine (mesuré le 2026-10-21 sur la fonction déployée) : c'est sa défense contre les
// pages d'hameçonnage hébergées sur `supabase.co`. Recopiée telle quelle, la lettre s'affichait en code
// source, scripts bloqués. Le relais ne garde donc que les en-têtes choisis ci-dessous et rend leur type
// aux pages ; il en a le droit parce que tout ce qui passe ici est bâti par NOTRE fonction sur NOTRE gabarit,
// le texte de l'acheteur neutralisé par `_injecter` (autorisé par Mongazi le 2026-10-21).
const GARDES = ["cache-control", "x-robots-tag", "referrer-policy", "x-content-type-options"];

function venueDeLaFonction(resp, geste) {
  const h = new Headers();
  for (const k of GARDES) { const v = resp.headers.get(k); if (v) h.set(k, v); }
  h.set("Content-Type", geste === "etat" ? "application/json; charset=utf-8" : "text/html; charset=utf-8");
  return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: h });
}

function avecEntetes(resp, lettre) {
  const h = new Headers(resp.headers);
  for (const [k, v] of Object.entries(SECURITE)) if (!h.has(k)) h.set(k, v);
  if (lettre) {
    h.set("X-Robots-Tag", "noindex, nofollow, noarchive");
    h.set("Referrer-Policy", "no-referrer");
    h.set("Cache-Control", "private, no-store, max-age=0");
  }
  return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: h });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const m = LETTRE.exec(url.pathname);
    if (!m) return avecEntetes(await env.ASSETS.fetch(request), false);
    const cible = FONCTION + "/" + m[1] + (m[2] ? "/" + m[2] : "");
    const init = { method: request.method, headers: { "Accept-Language": request.headers.get("Accept-Language") || "" },
                   redirect: "manual" };
    if (request.method !== "GET" && request.method !== "HEAD") init.body = await request.arrayBuffer();
    let resp;
    try {
      resp = venueDeLaFonction(await fetch(cible, init), m[2]);
    } catch (e) {
      // ⛔ jamais l'accueil à la place d'une lettre : une page claire, en deux langues
      resp = new Response("<!DOCTYPE html><meta charset=utf-8><title>Un instant</title>" +
        "<p>Cette lettre ne peut pas s'ouvrir pour le moment. Réessaie dans un moment.</p>" +
        "<p lang=en>This letter cannot open right now. Try again in a little while.</p>",
        { status: 503, headers: { "Content-Type": "text/html; charset=utf-8" } });
    }
    return avecEntetes(resp, true);
  },
};
