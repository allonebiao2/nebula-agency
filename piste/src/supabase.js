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

/* Une seule fonction pour appeler la base. Les trois portes publiques ne
   savent faire qu'une chose chacune, et aucune ne sait lister quoi que ce
   soit : ni les carnets, ni les commandes, ni les retours. */
async function appeler(porte, corps, garderEnVie = false) {
  return fetch(`${URL_BASE}/rest/v1/rpc/${porte}`, {
    method: 'POST',
    keepalive: garderEnVie,
    headers: {
      'Content-Type': 'application/json',
      apikey: CLE_PUBLIQUE,
      Authorization: `Bearer ${CLE_PUBLIQUE}`,
    },
    body: JSON.stringify(corps),
  })
}

/* La commande, deposee au moment ou l'acheteur part sur WhatsApp.

   ⚠️ `keepalive` n'est pas un detail : sans lui, ouvrir WhatsApp met la page en
   arriere-plan et le navigateur ANNULE la requete. C'est exactement comme ca
   que le prospect Angelique a ete perdu par le site de l'agence le 4 aout. On
   ne refait pas la meme erreur ici. */
export async function deposerCommande(reference, client, commande) {
  const corps = JSON.stringify({ reference, client, commande })
  const options = {
    method: 'POST',
    keepalive: true,
    headers: {
      'Content-Type': 'application/json',
      apikey: CLE_PUBLIQUE,
      Authorization: `Bearer ${CLE_PUBLIQUE}`,
    },
    body: corps,
  }

  /* La fonction serveur enregistre la commande ET envoie les deux courriels :
     un a Mongazi, pour qu'il la voie AUSSI dans sa boite mail et pas seulement
     sur son WhatsApp, et un a l'acheteur avec ce qu'il doit payer.
     La cle d'envoi vit en base, cote serveur : elle ne peut pas partir ici. */
  try {
    const r = await fetch(`${URL_BASE}/functions/v1/piste-commande`, options)
    if (r.ok) return true
  } catch (e) {
    /* on tombe sur le filet ci-dessous */
  }

  /* ⚠️ LE FILET. Si la fonction serveur est indisponible, la commande passe
     quand meme par la porte directe : elle sera sans courriel, mais elle
     EXISTERA. Perdre un courriel est ennuyeux, perdre une commande ne l'est
     pas : c'est exactement ce qui est arrive au site de l'agence le 4 aout. */
  try {
    const r = await appeler('piste_commander', {
      p_reference: reference,
      p_client: client,
      p_commande: commande,
    }, true)
    return r.ok
  } catch (e) {
    return false
  }
}

/* Une marque du carnet. Le client sait que ca remonte : c'est ecrit dans le
   carnet, en toutes lettres. Une donnee reprise en silence n'est pas un
   signal, c'est une prise. */
export async function marquerFiche(jeton, fiche, marque) {
  try {
    await appeler('piste_marquer', { p_jeton: jeton, p_fiche: fiche, p_marque: marque }, true)
  } catch (e) {}
}
