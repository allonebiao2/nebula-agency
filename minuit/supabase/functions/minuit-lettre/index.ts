import { createClient } from 'jsr:@supabase/supabase-js@2'
import { GABARIT } from '../_shared/gabarit.ts'
import { JETON_FORME, entetes, poser, verdict } from '../_shared/lettre.ts'

/*
  MINUIT · servir une lettre, et la retirer.

  ⚠️ CE FICHIER EST LA SOURCE. Il tourne sur Supabase, mais il vit ICI.
      supabase functions deploy minuit-lettre --no-verify-jwt
  ⛔ `--no-verify-jwt` : celle qui reçoit la lettre n'a pas de compte, pas de
     jeton, et souvent pas beaucoup de réseau. Ce qui protège cette porte,
     c'est que l'adresse ne se devine pas (110 bits tirés au sort).

  DEUX GESTES, ET LE SECOND COMPTE AUTANT QUE LE PREMIER
    GET  /l/<jeton>          → la lettre
    POST /l/<jeton>/retrait  → elle disparaît, sous 24 h devient « tout de
                               suite ». Sans discuter, sans prévenir
                               l'acheteur, sans rembourser (CONDITIONS.md §3).

  ⚠️ LE POUVOIR DE RETIRER APPARTIENT À QUI DÉTIENT LE LIEN, et c'est
    exactement l'ensemble des gens concernés : l'acheteur et celle qui reçoit.
    Personne d'autre ne peut l'avoir sans qu'un des deux le lui ait donné.
    Demander une preuve d'identité à quelqu'un qui veut faire retirer une
    lettre qui parle de lui serait le contraire de ce qu'on a écrit.
*/

const db = () => createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
)

/* Une page nue, sans rien qui ressemble à un formulaire : celle qui arrive ici
   n'a rien à faire, elle a juste besoin de comprendre. */
function page(titre: string, mot: string, code: number): Response {
  const html = `<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>${titre}</title><style>
:root{color-scheme:dark}
body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;
  background:#141019;color:#f4ede0;text-align:center;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
h1{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  font-weight:600;font-size:clamp(22px,6vw,30px);margin:0 0 10px}
p{margin:0;color:#8f86a0;font-size:15px;line-height:1.6;max-width:34ch}
</style></head><body><div><h1>${titre}</h1><p>${mot}</p></div></body></html>`
  return new Response(html, { status: code, headers: entetes() })
}

Deno.serve(async (req: Request) => {
  const url = new URL(req.url)
  const bouts = url.pathname.split('/').filter(Boolean)
  /* L'adresse publique est /l/<jeton> ; la fonction reçoit son propre nom
     devant quand on l'appelle sans passer par le domaine. On prend donc le
     premier bout qui a la forme d'un jeton, et le reste dit le geste. */
  const i = bouts.findIndex((b) => JETON_FORME.test(b))
  const jeton = i >= 0 ? bouts[i] : ''
  const geste = i >= 0 ? (bouts[i + 1] || '') : ''

  if (!jeton) {
    /* ⚠️ Le même message qu'une lettre inconnue : une adresse mal formée ne
       doit pas se distinguer d'une adresse qui n'existe pas, sinon on apprend
       à celui qui cherche comment chercher. */
    return page('Cette lettre n’existe pas.', 'Le lien est peut-être incomplet. Redemande-le à qui te l’a envoyé.', 404)
  }

  const { data, error } = await db().rpc('minuit_lire', { p_jeton: jeton })
  if (error) { console.error('minuit lire', error.message); return page('Un instant.', 'Cette lettre ne peut pas s’ouvrir pour le moment. Réessaie dans un moment.', 503) }
  const l = Array.isArray(data) ? data[0] : data

  /* ── le retrait ──────────────────────────────────────────────────────── */
  if (geste === 'retrait') {
    if (req.method !== 'POST') return page('Retirer cette lettre', 'Écris-nous sur WhatsApp avec ce lien, et elle est retirée sous 24 heures.', 405)
    /* ⛔ Aucune preuve demandée, aucune question posée. On retire même une
       lettre déjà retirée : c'est sans effet, et c'est ce qui permet de
       répondre la même chose à tout le monde. */
    const { error: eR } = await db().rpc('minuit_retirer', { p_jeton: jeton })
    if (eR) { console.error('minuit retrait', eR.message); return page('Un instant.', 'Le retrait n’a pas pu se faire. Écris-nous sur WhatsApp, on le fait à la main.', 503) }
    console.log('minuit · retirée', jeton)
    return page('C’est retiré.', 'Cette lettre n’existe plus. Personne n’a été prévenu.', 200)
  }

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return page('Cette lettre n’existe pas.', 'Le lien est peut-être incomplet.', 405)
  }

  /* ── servir ──────────────────────────────────────────────────────────── */
  switch (verdict(l ?? null)) {
    case 'inconnue':
      return page('Cette lettre n’existe pas.', 'Le lien est peut-être incomplet. Redemande-le à qui te l’a envoyé.', 404)
    case 'retiree':
      /* ⚠️ On ne dit pas « retirée à la demande de quelqu'un » : ce serait
         désigner la personne qui a demandé, à l'acheteur qui la connaît. */
      return page('Cette lettre n’existe plus.', 'Elle a été retirée.', 410)
    case 'expiree':
      return page('Cette lettre a expiré.', 'Une lettre ne reste pas en ligne pour toujours. Celle-ci est partie.', 410)
    case 'attente':
      /* Payée, pas encore confirmée. ⚠️ On ne dit pas « en attente de
         paiement » : celle qui reçoit n'a pas à savoir ce que ça a coûté. */
      return page('Cette lettre n’est pas encore prête.', 'Réessaie dans un moment.', 425)
  }

  /* ⛔ La lettre est REBÂTIE ici, à partir du gabarit et des données. Rien de
     ce qui est servi n'a été écrit par un navigateur. */
  const html = poser(GABARIT, l.donnees)
  return new Response(req.method === 'HEAD' ? null : html, { status: 200, headers: entetes() })
})
