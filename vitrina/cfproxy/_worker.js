// Vitrina · le bord du réseau.
//
// DEUX RÔLES, ET LE PREMIER EST LE PLUS IMPORTANT.
//
// 1. LES PAGES LIVRÉES SONT SERVIES ICI, DEPUIS KV, SANS JAMAIS TOUCHER
//    L'ORIGINE. C'est la raison d'être de ce fichier. Une page cadeau s'ouvre
//    à minuit sur le téléphone de quelqu'un : elle ne peut pas attendre qu'un
//    service Render endormi se réveille pendant une minute.
//
//    ⚠️ Un proxy inverse NE RÈGLE PAS ce problème : si on va chercher la page
//    à l'origine, on attend le réveil de l'origine. Il faut que la page soit
//    déjà là. C'est vitrina/publier.py qui l'y pose au moment de la validation.
//
// 2. Tout le reste (formulaire, commande, back-office) est relayé vers
//    l'origine, qui a le droit de dormir : le seul qui attend alors, c'est
//    Mongazi, et il prend déjà deux minutes pour lire son SMS Mobile Money.
//
// ⚠️ L'ORIGINE N'EST PLUS ÉCRITE EN DUR. La version précédente pointait vers
// une adresse Railway (`vitrina-production-686b.up.railway.app`) abandonnée le
// 1er août 2026 : le worker relayait vers un service qui n'existait plus, et
// rien ne le signalait. Elle se pose maintenant en variable.
//
// À POSER DANS CLOUDFLARE (Paramètres du projet Pages) :
//   Variable   ORIGINE   l'URL du backend, ex https://vitrina.onrender.com
//   Liaison KV PAGES     l'espace KV où publier.py dépose les pages
// Si PAGES n'est pas lié, tout retombe sur l'origine : plus lent, mais rien
// ne casse.

const SLUG_VALIDE = /^[A-Za-z0-9_-]{1,64}$/;

// Une page livrée ne change plus. On la garde longtemps au bord du réseau,
// mais on garde la main : `must-revalidate` permet une purge, et le retrait
// d'une page (demande de la personne visée) reste possible en la supprimant
// de KV puis en purgeant.
const CACHE_PAGE = "public, max-age=300, s-maxage=86400, must-revalidate";

function pageHtml(html, source) {
  return new Response(html, {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": CACHE_PAGE,
      // Une page cadeau porte un prénom et des photos : elle ne doit jamais
      // se retrouver dans un moteur de recherche.
      "x-robots-tag": "noindex, nofollow, noarchive",
      "referrer-policy": "no-referrer",
      "x-content-type-options": "nosniff",
      "x-vitrina-source": source,
    },
  });
}

async function versOrigine(request, origine) {
  const url = new URL(request.url);
  const cible = origine.replace(/\/+$/, "") + url.pathname + url.search;
  const entetes = new Headers(request.headers);
  entetes.delete("host");
  const init = { method: request.method, headers: entetes, redirect: "manual" };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }
  const reponse = await fetch(cible, init);
  // Recopie fidèle, en préservant Set-Cookie (le back-office en dépend).
  const sortie = new Response(reponse.body, reponse);
  sortie.headers.delete("content-encoding");
  sortie.headers.delete("content-length");
  return sortie;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origine = (env && env.ORIGINE) || "";

    // --- 1. Une page livrée ---
    const m = url.pathname.match(/^\/v\/([^/]+)\/?$/);
    if (m) {
      const slug = decodeURIComponent(m[1]);
      if (SLUG_VALIDE.test(slug) && env && env.PAGES) {
        const html = await env.PAGES.get("v:" + slug);
        if (html) {
          // Le chemin qui compte : servi depuis le bord, aucun réveil.
          return pageHtml(html, "kv");
        }
      }
      // Pas dans KV : c'est un aperçu de commande pas encore validée. On va
      // le chercher à l'origine, et c'est acceptable : l'acheteur vient
      // d'envoyer son formulaire, donc l'origine est déjà réveillée.
      if (!origine) {
        return new Response("Page introuvable.", {
          status: 404,
          headers: { "content-type": "text/plain; charset=utf-8" },
        });
      }
      return versOrigine(request, origine);
    }

    // --- 2. Tout le reste ---
    if (!origine) {
      return new Response(
        "ORIGINE n'est pas configurée sur ce projet Cloudflare.",
        { status: 503, headers: { "content-type": "text/plain; charset=utf-8" } },
      );
    }
    return versOrigine(request, origine);
  },
};
