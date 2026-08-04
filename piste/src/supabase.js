/*
  Le strict nécessaire pour lire un carnet. Aucune bibliothèque.

  La clé ci-dessous est PUBLIQUE par conception : c'est la clé « anon » de
  Supabase, faite pour vivre dans un navigateur. Elle ne donne accès à rien
  toute seule. Les carnets n'ont AUCUNE politique de sécurité de niveau ligne,
  donc aucun accès direct : la seule porte est la fonction `piste.carnet`, qui
  rend UN carnet à qui présente son jeton. On ne peut pas lister les autres.

  ⚠️ Ne jamais poser ici une clé « service ». Elle passerait toute la sécurité
  et se lirait dans le paquet JavaScript en trois secondes.
*/

const URL_BASE = 'https://xukduhqqfzogisoimhyo.supabase.co'
const CLE_PUBLIQUE = 'sb_publishable_pOEeVKbTixrVx3BPIaohMg_FigTtoBH'

export async function ouvrirCarnet(jeton) {
  /* ⚠️ La fonction vit dans `public`, pas dans `piste` : PostgREST n'expose
     que `public`, et une fonction rangée ailleurs répond 406 quelle que soit
     l'en-tête envoyée. On ne publie donc QUE cette porte, plutôt que d'ouvrir
     tout le schéma à l'API. */
  const r = await fetch(`${URL_BASE}/rest/v1/rpc/piste_carnet`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      apikey: CLE_PUBLIQUE,
      Authorization: `Bearer ${CLE_PUBLIQUE}`,
    },
    body: JSON.stringify({ p_jeton: jeton }),
  })
  if (!r.ok) throw new Error(`carnet ${r.status}`)
  const l = await r.json()
  return Array.isArray(l) ? l[0] || null : l || null
}
