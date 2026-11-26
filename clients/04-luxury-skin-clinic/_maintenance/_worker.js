// LA MAINTENANCE de luxuryclub229.com (Mongazi, 26/11 : « je ne veux pas qu'elle voie les modifications, coupe la
// visibilité, il faut que ça affiche en maintenance »).
// Toutes les adresses répondent cette page, avec un 503 et un Retry-After : c'est le code d'une indisponibilité
// TEMPORAIRE, Google garde le site dans son index au lieu de le retirer. Le WhatsApp de la maison reste joignable.
// Rouvrir le site = redéployer le livrable normal : python _outils/_dist.py puis wrangler pages deploy _dist.
const PAGE = `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0b0a08">
<title>Luxury Club 229 · Site en maintenance</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;min-height:100svh;display:grid;place-items:center;background:#0b0a08;color:#f3eadb;
  font:400 16px/1.6 Georgia,'Times New Roman',serif;padding:24px;text-align:center}
.carte{max-width:520px;width:100%;border:1px solid rgba(201,168,76,.35);border-radius:22px;padding:44px 28px 36px;
  background:linear-gradient(160deg,#17130d,#0d0b08)}
.mono{font:600 12px/1 system-ui,sans-serif;letter-spacing:.32em;text-transform:uppercase;color:#c9a84c}
h1{font-weight:400;font-size:clamp(30px,7vw,42px);line-height:1.1;margin:18px 0 14px;letter-spacing:.02em}
p{margin:0 0 26px;color:#d3c7b1;font-family:system-ui,sans-serif;font-size:15.5px}
.filet{width:64px;height:1px;background:#c9a84c;margin:0 auto 22px}
a{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 24px;border-radius:999px;
  background:#c9a84c;color:#16120a;text-decoration:none;font:600 15px/1 system-ui,sans-serif}
a:hover{background:#e3cd86}
</style>
</head>
<body>
<main class="carte">
  <div class="mono">Luxury Club 229</div>
  <h1>Notre site fait peau neuve</h1>
  <div class="filet"></div>
  <p>Nous préparons une nouvelle expérience. En attendant, nous restons joignables sur WhatsApp pour vos rendez-vous et vos commandes.</p>
  <a href="https://wa.me/2290167975626">Nous écrire sur WhatsApp</a>
</main>
</body>
</html>`;

export default {
  async fetch(request) {
    const url = new URL(request.url);
    // les robots peuvent lire qu'il ne faut rien indexer pendant la maintenance
    if (url.pathname === "/robots.txt") {
      return new Response("User-agent: *\nDisallow:\n", { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store" } });
    }
    return new Response(PAGE, {
      status: 503,
      headers: {
        "content-type": "text/html; charset=utf-8",
        "retry-after": "86400",
        "cache-control": "no-store",
        "x-robots-tag": "noindex",
      },
    });
  },
};
