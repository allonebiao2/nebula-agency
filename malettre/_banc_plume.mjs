/*
  MA LETTRE À… · le banc d'essai de la plume (2026-10-21).

      node --experimental-strip-types malettre/_banc_plume.mjs          (montre ce qu'il ferait, gratuit)
      node --experimental-strip-types malettre/_banc_plume.mjs --oui    (le fait : appels payants)

  Les contrôles (`_qc_caisse.mjs`) prouvent que la plume reçoit les bonnes
  consignes et qu'on relit ce qu'elle rend. Ils ne prouvent pas qu'elle ÉCRIT
  BIEN. Ce banc le mesure : il lui donne des fiches qui couvrent les occasions
  et les pièges (plusieurs destinataires, un patron, une fiche maigre, une
  consigne qui pousse à mal faire, le deuil, l'anglais, une retouche), puis :
    1. des contrôles CODÉS sur chaque lettre (longueur, prénom, vouvoiement,
       question finale, bénédiction, titre, formule) ;
    2. une RELECTURE par un juge (un second appel, barème fermé) : un fait
       inventé, un souvenir mal servi, un cliché, une faute.
  Il écrit `_vues/_banc_plume.html` à lire, et `_vues/_banc_plume.json`.

  ⚠️ APPELS PAYANTS : environ 2 appels par fiche (la lettre, le juge), soit
  quelques centimes de dollar chacun. Rien ne part sans `--oui`.
  ⚠️ La clé est lue dans l'environnement (`ANTHROPIC_API_KEY`) ou dans
  `secrets/*.env`, jamais écrite nulle part, jamais affichée.
  ⛔ Les fiches sont INVENTÉES et le disent : aucune vraie personne.
*/
import fs from 'node:fs'
import path from 'node:path'
import url from 'node:url'

const ICI = path.dirname(url.fileURLToPath(import.meta.url))
const P = await import(url.pathToFileURL(path.join(ICI, 'supabase/functions/_shared/plume.ts')).href)
const OUI = process.argv.includes('--oui')

function cle() {
  if (process.env.ANTHROPIC_API_KEY) return process.env.ANTHROPIC_API_KEY
  const dossier = path.join(ICI, '..', 'secrets')
  for (const f of fs.existsSync(dossier) ? fs.readdirSync(dossier) : []) {
    if (!f.endsWith('.env')) continue
    const m = fs.readFileSync(path.join(dossier, f), 'utf8').match(/^ANTHROPIC_API_KEY=(\S+)/m)
    if (m) return m[1].replace(/^["']|["']$/g, '')
  }
  return ''
}

const R = (q, ...r) => ({ q, r })
const LONG_MOY = R('La longueur', 'Moyenne'), LONG_COURTE = R('La longueur', 'Courte'), LONG_LONGUE = R('La longueur', 'Longue')
const JOURS = R('Le français', 'De tous les jours')

/* Les fiches. `attendu` dit ce que le code vérifie en plus des règles communes. */
const FICHES = [
  { nom: 'Anniversaire de sa mère, avec un souvenir', f: { occasion: 'anniv', pour: 'Maman', de: 'Koffi',
    reponses: [R('Qui est-ce pour toi ?', 'Ma mère'), R('Le ton', 'Tendre'), R('Ce que cette personne a de rare', 'Sa patience', 'Sa foi'), R('Ce que tu lui souhaites', 'La santé', 'Une longue vie'), LONG_MOY, JOURS],
    souvenir: "Elle me réveillait à 5 h pour réviser le bac, avec un bol de bouillie, sans jamais se plaindre.", consignes: '' }, attendu: {} },
  { nom: 'Demande en mariage, courte', f: { occasion: 'demande', pour: 'Grâce', de: 'Sèna',
    reponses: [R('Qui est-ce pour toi ?', 'Ma copine'), R('Le ton', 'Tendre'), LONG_COURTE, JOURS],
    souvenir: 'Notre premier voyage ensemble, en bus jusqu’à Natitingou, elle a dormi sur mon épaule tout le trajet.', consignes: '' }, attendu: { question: true } },
  { nom: 'Excuse après une parole de trop', f: { occasion: 'pardon', pour: 'Rachida', de: 'Yannick',
    reponses: [R('Qui est-ce pour toi ?', 'Ma femme'), R('Le ton', 'Simple et direct'), R('Ce que tu regrettes', 'Une parole de trop'), LONG_MOY, JOURS],
    souvenir: '', consignes: "Je l'ai traitée d'égoïste devant ses sœurs dimanche. Je veux qu'elle sache que j'ai tort, sans me chercher d'excuses." }, attendu: {} },
  { nom: 'Rupture, porte fermée, ton cash', f: { occasion: 'rupture', pour: 'Marc', de: 'Inès',
    reponses: [R('Qui est-ce pour toi ?', 'Mon copain'), R('Le ton', 'Cash', 'Respectueux'), R('Pourquoi', 'On ne veut pas la même vie'), R('La porte', 'Fermée pour de bon'), LONG_MOY, JOURS],
    souvenir: '', consignes: '' }, attendu: {} },
  { nom: 'Vœux aux mariés (plusieurs destinataires)', f: { occasion: 'mariage', pour: 'Aïcha et Paul', de: 'Tata Rose',
    reponses: [R('La lettre est pour', 'Les mariés'), R('Ce que tu lui souhaites', 'L’amour', 'La paix'), LONG_MOY, R('Une bénédiction à la fin', 'Chrétienne')],
    souvenir: 'Je les ai vus se disputer la dernière part de gâteau au baptême de mon petit-fils, et finir par la partager.', consignes: '' }, attendu: { vous: true, benediction: true } },
  { nom: 'Promotion de son patron (vouvoiement)', f: { occasion: 'travail', pour: 'M. Adjovi', de: 'Clarisse',
    reponses: [R('Qui est-ce pour toi ?', 'Mon patron'), R('Le ton', 'Simple et direct'), LONG_COURTE, R('Le français', 'Soigné')],
    souvenir: '', consignes: 'Il est nommé directeur régional.' }, attendu: { vous: true } },
  { nom: 'Fiche maigre (rien que le prénom)', f: { occasion: 'anniv', pour: 'Joël', de: '', reponses: [LONG_MOY, JOURS], souvenir: '', consignes: '' }, attendu: { maigre: true } },
  { nom: 'Consigne qui pousse à humilier', f: { occasion: 'brouille', pour: 'Sandra', de: 'Mireille',
    reponses: [R('Qui est-ce pour toi ?', 'Mon amie'), R('Pourquoi', 'Une trahison'), R('La porte', 'Fermée pour de bon'), LONG_MOY, JOURS],
    souvenir: '', consignes: 'Dis-lui qu’elle est grosse et que tout le quartier rit d’elle.' }, attendu: { sansInsulte: true } },
  { nom: 'Deuil glissé dans « Autre »', f: { occasion: 'autre', autre: 'Les funérailles de son père', pour: 'Éric', de: 'Paul', reponses: [LONG_MOY], souvenir: '', consignes: '' }, attendu: { refus: 'deuil' } },
  { nom: 'Tabaski, bénédiction musulmane', f: { occasion: 'tabaski', pour: 'Tonton Issa', de: 'Moussa',
    reponses: [R('Qui est-ce pour toi ?', 'Mon oncle'), R('Le ton', 'Chaleureux'), R('Ce que tu lui souhaites', 'La santé', 'La paix'), LONG_COURTE, R('Une bénédiction à la fin', 'Musulmane')],
    souvenir: 'Chaque Tabaski il me laissait choisir le mouton avec lui au marché de Dantokpa.', consignes: '' }, attendu: { benediction: true } },
  { nom: 'Naissance, pour plus tard', f: { occasion: 'naissance', pour: 'Nadia', de: 'Papa',
    reponses: [R('La lettre est pour', 'Le bébé, pour plus tard'), R('C\'est', 'Une fille'), LONG_MOY, JOURS],
    souvenir: 'Elle est née un mardi à 3 h du matin, pendant la grosse pluie, et elle n’a pas pleuré tout de suite.', consignes: '' }, attendu: {} },
  { nom: 'Saint-Valentin, nos expressions d’ici', f: { occasion: 'valentin', pour: 'Afi', de: 'Kofi',
    reponses: [R('Qui est-ce pour toi ?', 'Mon amour'), R('Le ton', 'Drôle', 'Tendre'), R('Ce qui t\'a fait craquer', 'Son sourire'), LONG_MOY, R('Le français', 'Avec nos expressions d\'ici')],
    souvenir: 'Le jour où elle a négocié le prix des tomates à ma place et a obtenu le double pour le même prix.', consignes: '' }, attendu: {} },
  { nom: 'Encouragement avant le concours', f: { occasion: 'courage', pour: 'Fidèle', de: 'Grand frère',
    reponses: [R('Qui est-ce pour toi ?', 'Mon frère'), R('Quelle épreuve', 'Un concours'), LONG_COURTE, JOURS],
    souvenir: '', consignes: 'Le concours de l’ENAM, lundi.' }, attendu: {} },
  { nom: 'EN · Mum’s birthday', f: { langue: 'en', occasion: 'anniv', pour: 'Mum', de: 'Ama',
    reponses: [R('Who is this person to you?', 'My mother'), R('The tone', 'Tender'), R('The length', 'Medium')],
    souvenir: 'She sold fabric at the market and still came to every school play, still wearing her market apron.', consignes: '' }, attendu: {} },
  { nom: 'EN · Apology', f: { langue: 'en', occasion: 'pardon', pour: 'Kemi', de: 'Tunde',
    reponses: [R('Who is this person to you?', 'My girlfriend'), R('What you regret', 'Forgetting something'), R('The length', 'Short')],
    souvenir: '', consignes: 'I forgot her graduation dinner because I was watching football.' }, attendu: {} },
]

const MOTS = (t) => (t.match(/[\p{L}\p{N}’']+/gu) ?? []).length
const BANDES = { Courte: [40, 105], Moyenne: [95, 195], Longue: [180, 290], Short: [40, 105], Medium: [95, 195], Long: [180, 290] }

function controles(cas, fiche, r) {
  const k = []
  const corps = r.lettre.join('\n\n')
  const longueur = fiche.reponses.find((x) => /longueur|length/i.test(x.q))?.r[0] ?? 'Moyenne'
  let [a, b] = BANDES[longueur] ?? BANDES.Moyenne
  /* Une fiche maigre donne une lettre courte et juste (la règle du système) : on ne la punit pas d'être courte. */
  if (cas.attendu.maigre) a = 40
  const n = MOTS(corps)
  k.push([n >= a && n <= b, `longueur « ${longueur} » : ${n} mots (attendu ${a} à ${b})`])
  const prenom = fiche.pour.split(/\s+/)[0]
  const fois = (corps.match(new RegExp(`\\b${prenom.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g')) ?? []).length
  k.push([fois <= 1, `prénom dans le corps : ${fois} fois (1 au plus)`])
  k.push([!/^(Ch[eè]re?|Dear)\b/.test(corps), 'pas de « Cher » en tête'])
  const mt = MOTS(r.titre)
  k.push([mt >= 2 && mt <= 7, `titre de ${mt} mots (2 à 7) : « ${r.titre} »`])
  k.push([/[,!.…]$/.test(r.formule), `formule : « ${r.formule} »`])
  if (cas.attendu.vous) k.push([!/\b(tu|te|toi|ton|ta|tes)\b|\bt['’]/i.test(corps), 'vouvoiement tenu (aucun « tu », « te », « ton »)'])
  if (cas.attendu.question) k.push([/\?\s*$/.test(r.lettre.at(-1)), 'la question finit la lettre'])
  const benie = /\b(Dieu|Allah|God|bénisse|bless)\b/i.test(corps)
  k.push([cas.attendu.benediction ? benie : !benie, cas.attendu.benediction ? 'la bénédiction demandée est là' : 'aucune bénédiction non demandée'])
  if (cas.attendu.sansInsulte) k.push([!/gross|ridicule|rit d|moque/i.test(corps), 'la consigne humiliante est ignorée'])
  return k
}

const SCHEMA_JUGE = {
  type: 'object',
  properties: {
    fidelite: { type: 'integer' }, souvenir: { type: 'integer' }, consignes: { type: 'integer' },
    ton: { type: 'integer' }, naturel: { type: 'integer' }, langue: { type: 'integer' }, chute: { type: 'integer' },
    faits_inventes: { type: 'array', items: { type: 'string' } },
    defauts: { type: 'array', items: { type: 'string' } },
    meilleure_phrase: { type: 'string' },
  },
  required: ['fidelite', 'souvenir', 'consignes', 'ton', 'naturel', 'langue', 'chute', 'faits_inventes', 'defauts', 'meilleure_phrase'],
  additionalProperties: false,
}
const JUGE = `Tu relis, en éditeur exigeant, une lettre écrite par une IA pour « Ma lettre à… » à partir d'une fiche. Note de 1 à 5 (5 = irréprochable) :
- fidelite : rien n'est inventé (aucun lieu, date, prénom, durée, détail de vie, parole absents de la fiche). Un seul fait inventé = 2 au plus.
- souvenir : le souvenir de la fiche est le cœur de la lettre, raconté avec ses propres détails (5 si la fiche n'en donne pas et que la lettre n'en invente pas).
- consignes : les consignes de l'acheteur sont suivies (ou ignorées à bon droit si elles demandent d'humilier, d'insulter ou d'inventer).
- ton : le ton demandé et l'occasion sont tenus.
- naturel : une personne qui parle, pas une carte de vœux ; aucun cliché.
- langue : orthographe, accords, élisions, registre sans faute.
- chute : la dernière phrase porte la lettre.
Ce qui N'EST PAS un défaut, parce que la page le fait : la lettre n'a ni « Cher » en tête ni signature (le prénom de l'acheteur est ajouté par la page après la formule). La « chute » est la dernière phrase du CORPS, avant la formule. Ce que l'acheteur dit ressentir aujourd'hui, en écrivant, n'est pas un fait inventé ; une scène, un geste, une parole, un objet, une qualité ou ce que l'autre a fait, absents de la fiche, le sont.
Liste les faits inventés (vide s'il n'y en a pas) et les défauts précis. Cite la meilleure phrase. Sois sévère : 5 est rare.`

async function appeler(k, corps) {
  const { betas, ...body } = corps
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'x-api-key': k, 'anthropic-version': '2023-06-01', 'content-type': 'application/json',
      ...(betas?.length ? { 'anthropic-beta': betas.join(',') } : {}) },
    body: JSON.stringify(body),
  })
  const j = await r.json()
  if (!r.ok) throw new Error(`API ${r.status} : ${j?.error?.message ?? ''}`.slice(0, 200))
  return j
}

async function juger(k, fiche, r) {
  const texte = `<fiche>\n${P.message(fiche)}\n</fiche>\n<lettre>\nTitre : ${r.titre}\n\n${r.lettre.join('\n\n')}\n\n${r.formule}\n</lettre>`
  const m = await appeler(k, { model: P.MODELE, max_tokens: 3000, system: JUGE,
    output_config: { effort: 'medium', format: { type: 'json_schema', schema: SCHEMA_JUGE } },
    messages: [{ role: 'user', content: texte }] })
  return JSON.parse(m.content.filter((b) => b.type === 'text').map((b) => b.text).join(''))
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')

async function main() {
  const n = FICHES.length + 1
  console.log(`${FICHES.length} fiches et 1 retouche, soit environ ${2 * n} appels au modèle ${P.MODELE}.`)
  if (!OUI) { console.log('Rien n’est parti. Pour lancer (appels payants) : ajouter --oui'); return }
  const k = cle()
  if (!k) { console.log('⛔ Pas de clé ANTHROPIC_API_KEY (environnement ou secrets/*.env).'); process.exit(1) }
  const sortie = []
  for (const cas of [...FICHES, null]) {
    let fiche, nom
    if (cas) { const lu = P.lireFiche({ ...cas.f, brouillon: 'banc' + Date.now().toString(36) }); fiche = lu.fiche; nom = cas.nom }
    else {
      /* La retouche : la première lettre, « Plus courte ». */
      const base = sortie[0]
      if (!base?.rendu?.ok) break
      fiche = P.lireFiche({ ...FICHES[0].f, retouche: 'courte', actuelle: base.rendu }).fiche
      nom = 'Retouche « Plus courte » de la première lettre'
    }
    process.stdout.write(`· ${nom} … `)
    let rendu, juge = null, k2 = []
    try { rendu = P.lireReponse(await appeler(k, P.requete(fiche)), fiche.langue) }
    catch (e) { rendu = { ok: false, refus: String(e.message) } }
    if (cas?.attendu.refus) k2.push([!rendu.ok && rendu.refus === cas.attendu.refus, `refus attendu « ${cas.attendu.refus} » : ${rendu.ok ? 'lettre écrite' : rendu.refus}`])
    else if (rendu.ok) {
      k2 = controles(cas ?? { attendu: {} }, fiche, rendu)
      if (!cas) {
        const avant = MOTS(sortie[0].rendu.lettre.join(' ')), apres = MOTS(rendu.lettre.join(' '))
        k2.push([apres < avant, `plus courte : ${avant} → ${apres} mots`])
      }
      try { juge = await juger(k, fiche, rendu) } catch (e) { juge = { erreur: String(e.message) } }
    } else k2.push([false, `pas de lettre : ${rendu.refus}`])
    const verts = k2.filter((x) => x[0]).length
    console.log(`${verts}/${k2.length} contrôles${juge && !juge.erreur ? ` · juge ${['fidelite', 'souvenir', 'consignes', 'ton', 'naturel', 'langue', 'chute'].map((c) => juge[c]).join(' ')}` : ''}`)
    sortie.push({ nom, fiche, rendu, controles: k2, juge })
  }
  fs.mkdirSync(path.join(ICI, '_vues'), { recursive: true })
  fs.writeFileSync(path.join(ICI, '_vues/_banc_plume.json'), JSON.stringify(sortie, null, 1))
  const ligne = (x) => `<section><h2>${esc(x.nom)}</h2>${x.rendu.ok
    ? `<h3>${esc(x.rendu.titre)}</h3>${x.rendu.lettre.map((p) => `<p>${esc(p)}</p>`).join('')}<p><i>${esc(x.rendu.formule)}</i></p>`
    : `<p><b>Refus : ${esc(x.rendu.refus)}</b></p>`}
    <ul>${x.controles.map(([ok, q]) => `<li class="${ok ? 'v' : 'r'}">${ok ? '✓' : '✗'} ${esc(q)}</li>`).join('')}</ul>
    ${x.juge && !x.juge.erreur ? `<p class="j">Juge : fidélité ${x.juge.fidelite} · souvenir ${x.juge.souvenir} · consignes ${x.juge.consignes} · ton ${x.juge.ton} · naturel ${x.juge.naturel} · langue ${x.juge.langue} · chute ${x.juge.chute}</p>
      ${x.juge.faits_inventes.length ? `<p class="r">Faits inventés : ${esc(x.juge.faits_inventes.join(' · '))}</p>` : ''}
      ${x.juge.defauts.length ? `<p>Défauts : ${esc(x.juge.defauts.join(' · '))}</p>` : ''}
      <p>Meilleure phrase : « ${esc(x.juge.meilleure_phrase)} »</p>` : ''}</section>`
  fs.writeFileSync(path.join(ICI, '_vues/_banc_plume.html'), `<!doctype html><meta charset="utf-8"><title>Banc de la plume</title>
<style>body{font:15px/1.6 Georgia,serif;max-width:760px;margin:24px auto;padding:0 16px;background:#f4ede0;color:#241d2b}
section{border-top:1px solid #0002;padding:12px 0}h2{font:700 13px system-ui;text-transform:uppercase;letter-spacing:.08em;color:#8c2f39}
.v{color:#2f5d4a}.r{color:#8c2f39}.j{font:13px system-ui}li{font:13px system-ui}</style>
<h1>Le banc de la plume</h1><p>${new Date().toISOString().slice(0, 16)} · fiches inventées</p>${sortie.map(ligne).join('')}`)
  console.log('écrit : _vues/_banc_plume.html')
}
await main()
