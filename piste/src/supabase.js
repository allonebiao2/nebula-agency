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

/* Un signalement « injoignable ». Il passe par la fonction serveur, qui pose
   la marque ET prévient Mongazi par courriel : sans alerte, un signalement
   dort dans une table que personne ne regarde. Le repli garde au moins la
   marque si le serveur est indisponible. */
export async function signalerInjoignable(jeton, fiche) {
  try {
    const r = await fetch(`${URL_BASE}/functions/v1/piste-signalement`, {
      method: 'POST',
      keepalive: true,
      headers: {
        'Content-Type': 'application/json',
        apikey: CLE_PUBLIQUE,
        Authorization: `Bearer ${CLE_PUBLIQUE}`,
      },
      body: JSON.stringify({ jeton, fiche }),
    })
    if (r.ok) return
  } catch (e) {}
  marquerFiche(jeton, fiche, 'injoignable')
}

/* ═══════ FABRIQUER ET ENVOYER UN CARNET, depuis le cockpit ═══════
   Mongazi confirme le paiement, et le carnet part : le serveur choisit les
   fiches libres, compose les messages, reserve 90 jours, et envoie le lien au
   client ET a lui. Plus besoin d'etre devant son PC.

   ⚠️ Le mot de passe n'est PAS dans le site : il est demande au moment du clic
   et garde dans ce navigateur seulement. Cette fonction fabrique de la
   marchandise ; sans garde, n'importe qui se ferait livrer en devinant une
   reference. */
const CLE_MDP = 'piste_cockpit_mdp'

export function motDePasseCockpit() {
  try {
    return localStorage.getItem(CLE_MDP) || ''
  } catch (e) {
    return ''
  }
}

export function poserMotDePasse(v) {
  try {
    localStorage.setItem(CLE_MDP, v || '')
  } catch (e) {}
}

export async function livrerCarnet(reference) {
  const motdepasse = motDePasseCockpit()
  if (!motdepasse) return { ok: false, erreur: 'mot de passe' }
  try {
    const r = await fetch(`${URL_BASE}/functions/v1/piste-livrer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: CLE_PUBLIQUE,
        Authorization: `Bearer ${CLE_PUBLIQUE}`,
      },
      body: JSON.stringify({ reference, motdepasse }),
    })
    return await r.json()
  } catch (e) {
    return { ok: false, erreur: 'réseau' }
  }
}

/*
  LIRE LES COMMANDES DEPUIS LE SERVEUR.

  Le cockpit ne lisait que ce navigateur. Une commande passée depuis le
  téléphone d'un client existait en base, déclenchait deux courriels, et
  n'apparaissait jamais ici tant que Mongazi ne recollait pas le message
  WhatsApp à la main. Ce n'était pas une liste, c'était un carnet personnel.
*/
export async function listerCommandes() {
  const motdepasse = motDePasseCockpit()
  if (!motdepasse) return { ok: false, erreur: 'mot de passe' }
  try {
    const r = await fetch(`${URL_BASE}/functions/v1/piste-cockpit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: CLE_PUBLIQUE,
        Authorization: `Bearer ${CLE_PUBLIQUE}`,
      },
      body: JSON.stringify({ motdepasse }),
    })
    return await r.json()
  } catch (e) {
    return { ok: false, erreur: 'réseau' }
  }
}

/* Marquer payé / livré EN BASE, pas seulement dans ce navigateur : sinon
   l'état vu depuis le téléphone contredit celui vu depuis le PC. */
export async function etatCommandeServeur(reference, etat) {
  const motdepasse = motDePasseCockpit()
  if (!motdepasse) return { ok: false, erreur: 'mot de passe' }
  try {
    const r = await fetch(`${URL_BASE}/functions/v1/piste-cockpit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: CLE_PUBLIQUE,
        Authorization: `Bearer ${CLE_PUBLIQUE}`,
      },
      body: JSON.stringify({ action: 'etat', reference, etat, motdepasse }),
    })
    return await r.json()
  } catch (e) {
    return { ok: false, erreur: 'réseau' }
  }
}

/*
  ══════════════════════════════════════════════════════ CE QU'ON COMPTE ═══

  PISTE ne comptait RIEN. On ne savait pas combien de gens venaient, combien
  configuraient une commande, ni lesquels partaient en route. Impossible, donc,
  de savoir quel métier remplir ensuite ni où les gens abandonnent.

  ⚠️ CE QU'ON NE STOCKE PAS, ET C'EST VOLONTAIRE
    pas d'adresse IP · pas de navigateur · pas de cookie · aucun identifiant
    qui suive quelqu'un d'un jour sur l'autre · aucune donnée personnelle.

  Le jeton de visite est tiré au hasard, vit dans l'ONGLET, et meurt à sa
  fermeture. Il compte des VISITES, pas des personnes, et c'est exactement ce
  que le cockpit affichera : promettre des personnes serait faux.

  Une mesure ne doit jamais faire échouer ce qu'elle mesure : tout est en
  « au mieux », sans await, et une panne réseau ne se voit pas.
*/
const CLE_VISITE = 'piste_visite'

function jetonVisite() {
  try {
    let v = sessionStorage.getItem(CLE_VISITE)
    if (!v) {
      v = [...crypto.getRandomValues(new Uint8Array(9))]
        .map((b) => b.toString(36))
        .join('')
        .slice(0, 12)
      sessionStorage.setItem(CLE_VISITE, v)
    }
    return v
  } catch (e) {
    return 'sans-stockage'
  }
}

/* Une étape franchie une seule fois par visite : sans ça, un client qui change
   trois fois de métier compterait pour trois, et l'entonnoir mentirait. */
const dejaVu = new Set()

export function marquerVisite(etape, extra = {}) {
  const cle = etape + (extra.metier || '') + (extra.ville || '')
  if (etape !== 'commande' && dejaVu.has(cle)) return
  dejaVu.add(cle)
  try {
    appeler(
      'piste_marquer_visite',
      {
        p_visite: jetonVisite(),
        p_etape: etape,
        p_metier: extra.metier || null,
        p_ville: extra.ville || null,
        p_n: extra.n || null,
        p_total: extra.total || null,
      },
      true
    ).catch(() => {})
  } catch (e) {}
}

/* Le tableau de bord du cockpit, en un seul appel. */
export async function lireTableau(jours = 30) {
  const motdepasse = motDePasseCockpit()
  if (!motdepasse) return { ok: false, erreur: 'mot de passe' }
  try {
    const r = await fetch(`${URL_BASE}/functions/v1/piste-cockpit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: CLE_PUBLIQUE,
        Authorization: `Bearer ${CLE_PUBLIQUE}`,
      },
      body: JSON.stringify({ action: 'tableau', jours, motdepasse }),
    })
    return await r.json()
  } catch (e) {
    return { ok: false, erreur: 'réseau' }
  }
}

/*
  ══════════════════════════════════════════ OUVRIR UN PAIEMENT EN LIGNE ═══

  Le navigateur n'envoie QUE la référence. Ni le montant, ni la devise : le
  serveur les relit sur la commande. S'il pouvait les annoncer, on paierait
  100 F pour 10 000 F de fiches.

  ⚠️ Et il ne rend qu'une adresse. Rien de ce qui revient d'ici ne prouve un
  paiement : c'est la notification signée reçue par `piste-paiement-recu` qui
  fait foi. Une page de retour se visite à la main.
*/
export async function ouvrirPaiement(reference) {
  try {
    const r = await fetch(`${URL_BASE}/functions/v1/piste-paiement`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: CLE_PUBLIQUE,
        Authorization: `Bearer ${CLE_PUBLIQUE}`,
      },
      body: JSON.stringify({ reference }),
    })
    return await r.json()
  } catch (e) {
    return { ok: false, erreur: 'réseau' }
  }
}
