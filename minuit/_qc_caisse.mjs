/*
  MINUIT · le contrôle de la caisse et de l'adresse.

      node --experimental-strip-types minuit/_qc_caisse.mjs

  ⚠️ Le drapeau n'est pas un caprice : ce fichier importe des `.ts`, que Deno
  lit nativement et que Node 22 refuse sans lui.

  ⚠️ SANS CLÉ, SANS RÉSEAU, SANS BASE. Tout ce qui décide, du prix à
  l'expiration en passant par le retrait, vit dans `_shared/lettre.ts`, en Web
  standard : ce fichier l'essaie sous Node exactement tel qu'il tournera chez
  Deno. Un garde-fou qu'aucun contrôle ne peut atteindre n'est pas un
  garde-fou, c'est une intention.

  ⛔ Il n'importe JAMAIS un `index.ts` de fonction : ils appellent `Deno.serve`
  au chargement, qui n'existe pas ici. On essaie ce qui décide, pas la
  plomberie qui l'entoure.
*/
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import url from 'node:url'

const ICI = path.dirname(url.fileURLToPath(import.meta.url))
const M = await import(path.join(ICI, 'supabase/functions/_shared/lettre.ts'))
const G = await import(path.join(ICI, 'supabase/functions/_shared/gabarit.ts'))

const verts = [], rouges = []
const dit = (b, q, detail = '') => (b ? verts : rouges).push([q, detail])
const lire = (p) => fs.readFileSync(path.join(ICI, p), 'utf8')

/* ═══ 1 · le barème, et le fait qu'il n'y en ait qu'un ═════════════════════ */
console.log('\n== Le barème')

dit(M.PALIERS.length === 4, 'quatre paliers')
dit(M.PALIERS[0].prix === 0 && M.PALIERS[0].pied === true,
    'le palier offert porte le pied viral')
dit(M.PALIERS.slice(1).every((p) => p.pied === false),
    'aucun palier payé ne porte le pied')
dit(M.palier('coffret')?.prix === 10000, 'le Coffret vaut 10 000 F')
dit(M.palier('inconnu') === null, 'un palier inventé n’existe pas')
dit(M.palier(undefined) === null, 'un palier absent n’existe pas')

/* ⛔ DEUX BARÈMES DANS UN DÉPÔT SONT DEUX VÉRITÉS. Le constructeur affiche les
   prix, le serveur les encaisse : on lit LES DEUX CÔTÉS dans les fichiers. */
const creer = lire('creer.html')
const bloc = /var PALIERS = \[(.*?)\];/s.exec(creer)
dit(!!bloc, 'le barème du constructeur se lit dans creer.html')
if (bloc) {
  const cote = [...bloc[1].matchAll(/id:"([a-z]+)".*?prix:(\d+).*?pied:(true|false)/gs)]
    .map((m) => ({ id: m[1], prix: Number(m[2]), pied: m[3] === 'true' }))
  dit(cote.length === M.PALIERS.length,
      'les deux barèmes ont le même nombre de paliers',
      `${cote.length} contre ${M.PALIERS.length}`)
  for (const p of M.PALIERS) {
    const c = cote.find((x) => x.id === p.id)
    dit(!!c && c.prix === p.prix && c.pied === p.pied,
        `« ${p.nom} » dit le même prix des deux côtés`,
        c ? `${c.prix} contre ${p.prix}` : 'absent du constructeur')
  }
}

/* ⛔ Et le constructeur ne doit plus avoir de DEUXIÈME échelle (les occasions
   portaient un « dès 10 000 F » payable 0 F, corrigé le 2026-09-06). */
const occ = /var OCCASIONS = \[(.*?)\];/s.exec(creer)
dit(!!occ && !occ[1].includes('prix'), 'les occasions ne portent aucun prix')

/* ═══ 2 · l'adresse ═══════════════════════════════════════════════════════ */
console.log('\n== L’adresse')

const j1 = M.jeton(), j2 = M.jeton()
dit(M.JETON_FORME.test(j1) && M.JETON_FORME.test(j2), 'un jeton a la forme attendue', j1)
dit(j1 !== j2, 'deux jetons ne se ressemblent pas')

/* ⛔ Elle ne se devine pas : 1000 tirages, aucun doublon, et toutes les
   lettres de l'alphabet finissent par sortir. Un générateur cassé qui rendrait
   toujours « 2222… » passerait les deux contrôles ci-dessus. */
const lot = new Set()
const vus = new Set()
for (let i = 0; i < 1000; i++) { const j = M.jeton(); lot.add(j); for (const c of j) vus.add(c) }
dit(lot.size === 1000, 'mille jetons, mille valeurs différentes', `${lot.size} distincts`)
dit(vus.size >= 24, 'le tirage couvre l’alphabet', `${vus.size} caractères vus`)
dit(!/[aeiou01lI]/.test([...vus].join('')),
    'aucune voyelle ni caractère confondable : une adresse ne forme pas un mot')

/*
  ⚠️ LE REJET DE MODULO SE MESURE. L'alphabet fait 28 lettres : sans rejet,
  les octets 252 à 255 se replieraient sur les quatre PREMIÈRES, qui
  sortiraient donc plus souvent que les autres. Ce n'est pas une élégance,
  c'est des bits perdus sur une adresse qui doit être indevinable.

  On donne un tirage connu — quatre octets à rejeter, puis 0, 1, 2… — et on
  exige EXACTEMENT le mot que forment les seuls octets acceptés.
*/
const suite = []
for (let k = 0; k < 40; k++) suite.push(k < 4 ? 252 + k : k - 4)
let pris = 0
const truque = (k) => new Uint8Array(Array.from({ length: k }, () => suite[pris++] ?? 0))
const jt = M.jeton(22, truque)
const attendu = '23456789bcdfghjkmnpqr'
dit(jt.startsWith(attendu), 'les octets hauts sont rejetés, pas repliés sur le début',
    `${jt} au lieu de ${attendu}…`)
dit(M.JETON_FORME.test(jt), 'et le jeton garde sa forme', jt)

/* ⚠️ Une source de hasard qui ne rend QUE des octets rejetés ne doit pas faire
   tourner la boucle pour toujours : un serveur qui ne rend jamais la main ne
   dit rien du tout. */
let leve = false
try { M.jeton(22, (k) => new Uint8Array(k).fill(255)) } catch { leve = true }
dit(leve, 'un hasard qui ne rend rien lève une erreur au lieu de tourner sans fin')

/* ═══ 3 · l'heure ═════════════════════════════════════════════════════════ */
console.log('\n== L’heure')

dit(M.ouvreValide('2027-02-14T00:00') === '2027-02-14T00:00', 'une heure valable passe telle quelle')
dit(M.ouvreValide('') === '', 'pas d’heure, pas de verrou')
dit(M.ouvreValide('2027-02-14') === '', 'une date sans heure est refusée')
dit(M.ouvreValide('2027-02-14T00:00:00Z') === '', 'un instant absolu est refusé')
dit(M.ouvreValide('2027-02-14T25:00') === '', 'une heure impossible est refusée')
/* ⚠️ 31 février : `Date` le reporterait en silence au 3 mars, et la lettre
   s’ouvrirait un autre jour que celui promis à l’acheteur. */
dit(M.ouvreValide('2027-02-31T00:00') === '', 'un 31 février est refusé, pas reporté')
dit(M.ouvreValide('2028-02-29T00:00') === '2028-02-29T00:00', 'un 29 février bissextile passe')
dit(!/[Zz+]/.test(M.ouvreValide('2027-02-14T00:00')),
    'l’heure ne porte aucun fuseau : minuit, c’est minuit chez celle qui lit')

/* ═══ 4 · la vie d'une lettre ═════════════════════════════════════════════ */
console.log('\n== La vie d’une lettre')

const T = Date.parse('2026-09-06T12:00:00Z')
const dans = (j) => new Date(T + j * 86400000).toISOString()

dit(M.verdict(null, T) === 'inconnue', 'une lettre inconnue est inconnue')
dit(M.verdict({ etat: 'attente' }, T) === 'attente', 'une lettre pas encore payée ne se sert pas')
dit(M.verdict({ etat: 'vivante', expire_le: dans(30) }, T) === 'servir', 'une lettre vivante se sert')
dit(M.verdict({ etat: 'vivante', expire_le: dans(-1) }, T) === 'expiree', 'une lettre expirée ne se sert plus')
dit(M.verdict({ etat: 'vivante', expire_le: null }, T) === 'servir', 'sans date de fin, elle se sert')

/* ⛔ LE RETRAIT PASSE AVANT TOUT LE RESTE : c'est la règle de CONDITIONS.md. */
dit(M.verdict({ etat: 'vivante', expire_le: dans(30), retire_le: dans(-1) }, T) === 'retiree',
    'une lettre retirée ne se sert plus, même vivante et payée')
dit(M.verdict({ etat: 'attente', retire_le: dans(-1) }, T) === 'retiree',
    'le retrait passe avant l’état de la commande')

dit(M.expireLe(M.palier('gratuit'), T) === dans(7), 'une lettre offerte vit sept jours')
dit(M.expireLe(M.palier('lettre'), T) === dans(365), 'une lettre payée vit un an')

/* ═══ 5 · les en-têtes ════════════════════════════════════════════════════ */
console.log('\n== Les en-têtes')

const h = M.entetes()
dit(/noindex/.test(h['X-Robots-Tag']), 'X-Robots-Tag porte noindex')
/* ⛔ L'en-tête EN PLUS de la balise : la balise ne vaut que pour de l'HTML lu
   par un robot qui exécute le HTML. */
dit(/noindex/.test(G.GABARIT), 'et le gabarit porte la balise, en plus')
dit(h['Referrer-Policy'] === 'no-referrer', 'aucun référent ne fuit')
dit(/no-store/.test(h['Cache-Control']), 'une lettre ne reste pas dans un cache')
dit(h['X-Content-Type-Options'] === 'nosniff', 'aucun reniflage de type')

/* ═══ 6 · ce qu'un acheteur a le droit d'envoyer ══════════════════════════ */
console.log('\n== La porte')

const BON = {
  palier: 'lettre', occasion: 'Anniversaire', pour: 'Zara', de: 'Robert',
  titre: 'Joyeux anniversaire', code: '1234', lettre: ['Un mot vrai.'],
  photos: [], depuis: '2024-03-14', ouvre: '2027-02-14T00:00',
}
const bon = M.lireCommande(BON)
dit(bon.ok, 'une commande normale passe', bon.ok ? '' : bon.erreur)
dit(bon.ok && bon.lettre.ouvre === '2027-02-14T00:00', 'l’heure arrive jusqu’à la lettre')
dit(bon.ok && bon.palier.prix === 5000, 'le prix vient du barème, pas du corps')

dit(!M.lireCommande({ ...BON, palier: 'coffret_gratuit' }).ok, 'un palier inventé est refusé')
dit(!M.lireCommande({ ...BON, lettre: [] }).ok, 'une lettre vide est refusée')
dit(!M.lireCommande({ ...BON, lettre: ['   '] }).ok, 'une lettre de blancs est refusée')

/* ⛔ LE PRIX NE VIENT JAMAIS DU NAVIGATEUR. */
const triche = M.lireCommande({ ...BON, prix: 0, total: 0, montant: 1 })
dit(triche.ok && triche.palier.prix === 5000,
    'un prix annoncé par le navigateur est ignoré', String(triche.ok && triche.palier.prix))

/* ⛔ LE PIED VIRAL NON PLUS : sinon il se retire d'un clic dans la console. */
const sanspied = M.lireCommande({ ...BON, palier: 'gratuit', pied: false })
dit(sanspied.ok && sanspied.lettre.pied === true,
    'le pied du palier offert ne se retire pas depuis le navigateur')

/* ⛔ ET JAMAIS LE DRAPEAU D'APERÇU : le seuil EST le produit. */
const apercu = M.lireCommande({ ...BON, apercu: true })
dit(apercu.ok && !('apercu' in apercu.lettre),
    'le drapeau d’aperçu ne franchit jamais la porte')

/* ⛔ LES PHOTOS SONT DES DONNÉES, JAMAIS DES LIENS : un lien distant
   fuiterait l'heure d'ouverture vers un tiers. */
const PIX = 'data:image/jpeg;base64,' + 'A'.repeat(400)
dit(M.lireCommande({ ...BON, photos: [{ src: PIX, legende: 'x' }] }).ok, 'une photo en données passe')
for (const mauvais of [
  'https://exemple.com/p.jpg',
  '//exemple.com/p.jpg',
  'data:text/html;base64,PHNjcmlwdD4=',
  'javascript:alert(1)',
]) {
  dit(!M.lireCommande({ ...BON, photos: [{ src: mauvais }] }).ok,
      `une photo « ${mauvais.slice(0, 28)} » est refusée`)
}
dit(!M.lireCommande({ ...BON, photos: [{ src: 'data:image/jpeg;base64,' + 'A'.repeat(M.BORNES.photo) }] }).ok,
    'une photo trop lourde est refusée')

/* Le palier décide du nombre de photos, pas le navigateur. */
const trop = M.lireCommande({ ...BON, palier: 'gratuit', photos: Array(5).fill({ src: PIX }) })
dit(trop.ok && trop.lettre.photos.length === 1, 'le palier offert ne garde qu’une photo')

/* Le palier offert n'a pas de code secret : c'est ce qui le distingue. */
const gratuit = M.lireCommande({ ...BON, palier: 'gratuit', code: '1234' })
dit(gratuit.ok && gratuit.lettre.code === '', 'le palier offert n’a pas de code secret')
const code = M.lireCommande({ ...BON, code: 'ab12cd34' })
dit(code.ok && code.lettre.code === '1234', 'un code se ramène à quatre chiffres')

/* ═══ 7 · « </script> » dans le mot d'un acheteur ═════════════════════════ */
console.log('\n== Le mot d’un acheteur')

/*
  ⛔ LES DEUX SÉRIALISEURS DOIVENT RENDRE LE MÊME OCTET. `_injecter.py` protège
  la lettre construite dans le navigateur, `_shared/lettre.ts` protège celle
  que le serveur rebâtit. Deux implémentations d'une même règle sont deux
  vérités : on les passe à la même batterie hostile.
*/
const PIEGES = [
  { lettre: ['fin </script><script>window.__pwn=1</script>'] },
  { titre: '<!-- caché -->' },
  { pour: 'a\u2028b\u2029c' },
  { de: '</SCRIPT >' },
  { lettre: ['<\/script>'], titre: 'déjà échappé' },
  { pour: 'Zara', accents: 'é à ù ç « » — …' },
]
for (const [i, p] of PIEGES.entries()) {
  const ts = M.serialiser(p)
  const py = execFileSync('python3', ['-c',
    'import sys,json;sys.path.insert(0,sys.argv[1]);from _injecter import serialiser;' +
    'print(serialiser(json.loads(sys.argv[2])),end="")',
    ICI, JSON.stringify(p)], { encoding: 'utf8' })
  dit(ts === py, `piège ${i + 1} : Python et TypeScript rendent le même octet`,
      ts === py ? '' : `\n      ts: ${ts}\n      py: ${py}`)
  dit(!ts.includes('</'), `piège ${i + 1} : plus aucune balise fermante`)
  dit(!ts.includes('<!--'), `piège ${i + 1} : plus aucun commentaire HTML`)
  dit(!/[\u2028\u2029]/.test(ts), `piège ${i + 1} : plus aucun séparateur de ligne`)
}

/* ⚠️ Et le fichier qui documente ce piège ne doit pas le contenir : la
   fonction qui neutralise U+2028 les a déjà portés en clair dans ses regex,
   le 2026-09-02 puis le 2026-09-06. Deux fois. */
dit(!/[\u2028\u2029]/.test(lire('supabase/functions/_shared/lettre.ts')),
    'le garde-fou ne contient pas le défaut qu’il empêche')

/* ═══ 8 · la lettre rebâtie ═══════════════════════════════════════════════ */
console.log('\n== La lettre rebâtie')

const pose = M.poser(G.GABARIT, M.lireCommande(BON).lettre)
dit(!pose.includes('/*MINUIT_DONNEES*/'), 'le marqueur a disparu')
dit(pose.includes('"ouvre":"2027-02-14T00:00"'), 'l’heure est dans la page servie')
dit(pose.includes('"pour":"Zara"'), 'le prénom est dans la page servie')
dit(!/<script[^>]+src=/.test(pose), 'aucun script externe')
dit(!/<link/.test(pose), 'aucune feuille externe')

const hostile = M.lireCommande({ ...BON, lettre: ['fin </script><script>window.__pwn=1</script>'] })
const posee = M.poser(G.GABARIT, hostile.lettre)
dit((posee.match(/<\/script>/g) || []).length === (G.GABARIT.match(/<\/script>/g) || []).length,
    'le mot d’un acheteur n’ajoute aucune balise fermante')

/* ⛔ FICHIER GÉNÉRÉ : le gabarit embarqué doit être `lettre.html`, au caractère
   près. Sans ce contrôle, une correction faite dans la lettre ne partirait
   jamais chez les gens, sans un mot. */
dit(G.GABARIT === lire('lettre.html'),
    'le gabarit embarqué est exactement lettre.html',
    `${G.GABARIT.length} contre ${lire('lettre.html').length} octets`)

/* ⛔ ET LA COPIE DE SASPAY DOIT ÊTRE CELLE DE PISTE, au caractère près : deux
   caisses qui divergent, c'est une caisse qui n'est plus essayée. */
const a = lire('supabase/functions/_shared/saspay.ts')
const b = fs.readFileSync(path.join(ICI, '../piste/supabase/functions/_shared/saspay.ts'), 'utf8')
dit(a === b, 'la caisse est exactement celle de PISTE', `${a.length} contre ${b.length} octets`)

/* ═══ 9 · ce que le SQL promet ════════════════════════════════════════════ */
console.log('\n== Le schéma')

const sql = lire('supabase/lettres.sql')
dit(/CREATE SCHEMA IF NOT EXISTS minuit/.test(sql), 'MINUIT a son propre schéma')
dit(!/DROP /i.test(sql), 'le fichier ne détruit rien : il est rejouable')
for (const f of ['minuit_deposer', 'minuit_lire', 'minuit_paiement_attendu',
                 'minuit_paiement_session', 'minuit_paiement_par_session',
                 'minuit_paiement_journal', 'minuit_ouvrir', 'minuit_retirer'])
  dit(sql.includes(`FUNCTION public.${f}(`), `la porte ${f} existe`)
dit(/REVOKE ALL ON FUNCTION/.test(sql) && /GRANT EXECUTE ON FUNCTION %s TO service_role/.test(sql),
    'aucune porte n’est ouverte au navigateur')
dit(/ENABLE ROW LEVEL SECURITY/.test(sql), 'les tables sont fermées')
dit(/minuit_evenement_unique/.test(sql), 'un renvoi de notification ne paie pas deux fois')
/* ⛔ Le HTML du navigateur n'est stocké nulle part. */
dit(!/\bhtml\b\s+text/.test(sql), 'la base ne garde aucun HTML d’acheteur')

/* ═══ 10 · ce que les fonctions promettent ════════════════════════════════ */
console.log('\n== Les fonctions de bord')

const cmd = lire('supabase/functions/minuit-commande/index.ts')
const recu = lire('supabase/functions/minuit-paiement-recu/index.ts')
const serv = lire('supabase/functions/minuit-lettre/index.ts')

dit(!/p_prix:\s*(d|Number)/.test(cmd) && /p_prix: palier.prix/.test(cmd),
    'le dépôt écrit le prix du barème, pas celui du corps')
dit(/offert \? 'vivante' : 'attente'/.test(cmd),
    'une lettre offerte est vivante tout de suite')
/* ⚠️ On mesure l'APPEL, pas le mot : la ligne d'import porte « ouvrirSession »
   tout en haut du fichier, et une sonde qui la lisait accusait un code sain. */
dit(cmd.indexOf('await ouvrirSession(') > cmd.indexOf('if (offert) return'),
    'une lettre offerte n’ouvre aucun paiement')
dit(/verifierSignature/.test(recu) && /horodatageFrais/.test(recu),
    'la notification est signée ET fraîche, deux contrôles')
dit(/await req.text\(\)/.test(recu) && !/JSON.stringify\(await req/.test(recu),
    'le corps brut n’est jamais reparsé avant la signature')
dit(/minuit_retirer/.test(serv), 'le retrait est une porte, pas une intention')
dit(/verdict\(/.test(serv), 'servir une lettre passe par la décision commune')

/* ⚠️ Le service_role ne doit jamais fuiter vers le navigateur. */
for (const [nom, src] of [['commande', cmd], ['paiement-recu', recu], ['lettre', serv]])
  dit(!/Access-Control-Allow-Origin[^\n]*\*[^\n]*SERVICE/i.test(src)
      && (src.match(/SERVICE_ROLE_KEY/g) || []).length <= 2,
      `${nom} : la clé de service ne sert qu’à parler à la base`)

/* ═══ le compte ═══════════════════════════════════════════════════════════ */
for (const [q, d] of verts) console.log('  [ok]', q, d ? `· ${d}` : '')
for (const [q, d] of rouges) console.log('  [KO]', q, d ? `· ${d}` : '')
console.log(`\n${verts.length} contrôles verts, ${rouges.length} en échec`)
if (rouges.length) {
  console.log('\nA REPRENDRE :')
  for (const [q, d] of rouges) console.log('  -', q, d ? `(${d})` : '')
  process.exit(1)
}
console.log('Tout est vert.')
