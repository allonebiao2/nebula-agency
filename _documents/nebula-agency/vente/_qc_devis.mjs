/**
 * Contrôle qualité du générateur de devis NEBULA.
 *
 *   cd _documents/nebula-agency/vente
 *   NODE_PATH=<dossier avec playwright-core> node _qc_devis.mjs
 *
 * Ce que ça vérifie, dans l'ordre d'importance :
 *   1. L'ARITHMÉTIQUE. Chaque brief doit sortir le montant de la grille.
 *      C'est le seul contrôle qui compte vraiment : un devis faux coûte
 *      un client, une couleur ratée non.
 *   2. L'ACCORD AVEC LE CONFIGURATEUR DU SITE. Le socle §1.2 dit que le prix
 *      d'un outil sort du configurateur. On coche les mêmes options sur la
 *      vraie page du site et on exige le même chiffre, au franc près.
 *   3. Les garde-fous du §6 s'affichent quand il faut.
 *   4. Zéro erreur JS, zéro ressource externe, zéro débordement, cibles ≥ 44 px.
 *
 * Tout doit être vert avant déploiement.
 */

import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

/* playwright-core n'est pas une dépendance du dépôt : on le prend où il est.
   NODE_PATH ne marche pas avec les modules ES, d'où cette résolution à la main. */
async function chargerPlaywright() {
  const pistes = [
    'playwright-core',
    'playwright',
    ...(process.env.PLAYWRIGHT_CORE ? [process.env.PLAYWRIGHT_CORE] : []),
    ...(process.env.NODE_PATH || '').split(':').filter(Boolean)
      .map(d => path.join(d, 'playwright-core', 'index.js'))
  ];
  for (const p of pistes) {
    try {
      const mod = await import(p.startsWith('/') ? pathToFileURL(p).href : p);
      const pw = mod.chromium ? mod : mod.default;   // CommonJS : tout est sous .default
      if (pw && pw.chromium) return pw;
    } catch { /* piste suivante */ }
  }
  console.error('⛔ playwright-core introuvable.\n   npm install playwright-core quelque part, puis :\n' +
                '   NODE_PATH=<ce dossier>/node_modules node _qc_devis.mjs');
  process.exit(2);
}
const { chromium } = await chargerPlaywright();

const ICI = path.dirname(fileURLToPath(import.meta.url));
const PAGE = 'file://' + path.join(ICI, 'generateur-devis.html');
const SITE = 'file://' + path.resolve(ICI, '../../../00-nebula-agency/nebula_agency_v9.html');
const CAPTURES = path.join(ICI, '_captures');

let ok = 0, ko = 0;
const echecs = [];

function verifier(nom, condition, detail = '') {
  if (condition) { ok++; console.log('  ✓ ' + nom); }
  else { ko++; echecs.push(nom + (detail ? ' — ' + detail : '')); console.log('  ✗ ' + nom + (detail ? ' — ' + detail : '')); }
}

function egal(nom, obtenu, attendu) {
  verifier(nom, obtenu === attendu, `obtenu « ${obtenu} », attendu « ${attendu} »`);
}

/* ------------------------------------------------------------------ */

const navigateur = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--no-sandbox']
});

const erreursJS = [];
const externes = [];

const ctx = await navigateur.newContext({ viewport: { width: 390, height: 844 }, locale: 'fr-FR' });
const page = await ctx.newPage();
page.on('pageerror', e => erreursJS.push(String(e)));
page.on('console', m => { if (m.type() === 'error') erreursJS.push('console: ' + m.text()); });
page.on('request', r => { if (!r.url().startsWith('file://') && !r.url().startsWith('data:')) externes.push(r.url()); });

await page.goto(PAGE, { waitUntil: 'networkidle' });

/** saisit un brief et rend l'état lu par la page */
async function soumettre(texte) {
  await page.fill('#brief', texte);
  await page.waitForTimeout(60);
  return page.evaluate(() => ({
    prix: document.getElementById('prix-n').textContent.replace(/\s+/g, ' ').trim(),
    total: document.getElementById('barre-v').textContent.replace(/\s+/g, ' ').trim(),
    offres: Array.from(document.querySelectorAll('[data-offre][aria-pressed="true"]')).map(b => b.dataset.offre),
    options: Array.from(document.querySelectorAll('[data-opt][aria-pressed="true"]')).map(b => b.dataset.opt),
    compteurs: Array.from(document.querySelectorAll('#compteurs .cpt')).map(c => ({
      nom: c.querySelector('.nm').textContent, v: c.querySelector('.v').textContent
    })),
    lignes: Array.from(document.querySelectorAll('#lignes .lg')).map(l => ({
      t: l.querySelector('.d').childNodes[0].textContent.trim(),
      m: l.querySelector('.m').textContent.replace(/\s+/g, ' ').trim()
    })),
    alertes: Array.from(document.querySelectorAll('#alertes .al b')).map(b => b.textContent),
    surlignes: Array.from(document.querySelectorAll('#surlignage mark')).map(m => m.textContent),
    cadrage: document.getElementById('cadrage').hidden ? '' : document.getElementById('cadrage').textContent,
    msg: document.getElementById('msg').value,
    fiche: document.getElementById('fiche').value
  }));
}

/* ===================================================================
   1 · L'ARITHMÉTIQUE
   =================================================================== */
console.log('\n1 · L’arithmétique de la grille');

// -- Catalogue : 50 000 F, 20 produits compris, +15 000 F par lot de 10
let r = await soumettre("Elle vend des pagnes et des sacs, elle veut que ses clientes voient les modèles avec les prix et commandent sur WhatsApp. Elle a une trentaine d’articles.");
egal('catalogue détecté', r.offres.join(','), 'catalogue');
egal('30 articles lus', r.compteurs.find(c => /Produits/.test(c.nom))?.v, '30');
egal('catalogue 30 produits = 65 000 F', r.total, '65 000 F');
verifier('le lot supplémentaire est une ligne à part', r.lignes.some(l => /lot/i.test(l.t) && l.m === '15 000 F'));
verifier('le message nomme les produits, pas juste leur nombre', /Vos 30 produits/.test(r.msg),
  (r.msg.split('\n').find(l => /^· Vos/.test(l)) || '').slice(0, 60));

r = await soumettre("Il a 20 produits à mettre en ligne, commandables sur WhatsApp.");
egal('catalogue 20 produits = 50 000 F (aucun lot)', r.total, '50 000 F');

r = await soumettre("Un catalogue de 35 produits commandables.");
egal('catalogue 35 produits = 80 000 F (exemple du socle §1.2)', r.total, '80 000 F');

// -- Vitrine : 150 000 F, 1 page comprise, +30 000 F par page
r = await soumettre("Il veut un vrai site pour être trouvé sur Google, avec ses services, une galerie et les avis de ses clients. Il lui faut aussi une page équipe et une page tarifs.");
egal('vitrine détectée', r.offres.join(','), 'vitrine');
egal('3 pages lues', r.compteurs.find(c => /Pages/.test(c.nom))?.v, '3');
egal('vitrine 3 pages = 210 000 F', r.total, '210 000 F');
verifier('le domaine apparaît en ligne offerte', r.lignes.some(l => /domaine/i.test(l.t) && l.m === 'offert'));

r = await soumettre("Il lui faut un site vitrine pour son entreprise, une seule page suffit.");
egal('vitrine 1 page = 150 000 F', r.total, '150 000 F');

r = await soumettre("Un site vitrine de 4 pages pour son cabinet.");
egal('vitrine 4 pages = 240 000 F (le hub du socle §1.2)', r.total, '240 000 F');

// -- QR Google Review : 30 000 F, sans abonnement
r = await soumettre("Il veut juste que ses clients laissent des avis Google facilement.");
verifier('QR Google Review détecté', r.offres.includes('qr'));
verifier('le QR est annoncé sans abonnement', /sans abonnement/i.test(r.msg));

// -- Outil métier : base 60 000, options du configurateur, ×0,9 / ×1,25
const BRIEF_OUTIL = "Il a trois boutiques, il veut suivre son stock chaque jour, connaître ses dettes et ses marges, un tableau de bord avec des graphiques et un rapport automatique par email chaque fin de mois. Cinq personnes vont l’utiliser.";
r = await soumettre(BRIEF_OUTIL);
egal('outil métier détecté', r.offres.join(','), 'outil');
const attenduOpts = ['jour', 'graph', 'tdb', 'rapport', 'email', 'u-2a5', 'niv-int'];
verifier('les 7 options attendues sont cochées',
  attenduOpts.every(o => r.options.includes(o)),
  'manquantes : ' + attenduOpts.filter(o => !r.options.includes(o)).join(', ') + ' | lues : ' + r.options.join(', '));
egal('outil = fourchette 300 000 – 420 000 F', r.total, '300 000 – 420 000 F');
verifier('la fourchette est annoncée comme indicative', /fourchette indicative/i.test(r.msg));
verifier('le prix ferme est renvoyé au cadrage', /cadrage/i.test(r.msg));

// -- les bornes du socle : plancher 55 000, plafond 500 000
r = await soumettre("Il veut juste un petit outil pour gérer son cahier, rien de plus.");
verifier('plancher 55 000 F respecté',
  (() => { const m = r.total.match(/^(\d[\d ]*)/); return m && parseInt(m[1].replace(/ /g, ''), 10) >= 55000; })(), r.total);

r = await soumettre("Il veut une application mobile, un cockpit tout-en-un, des factures normalisées, une analyse écrite par IA, la connexion à ses outils existants, des vidéos, un rapport automatique par email, Telegram, une finition premium et plus de 5 utilisateurs, en urgence.");
verifier('plafond 500 000 F respecté', /500 000 F$/.test(r.total), r.total);

/* ===================================================================
   2 · L'ACCORD AVEC LE CONFIGURATEUR DU SITE
   =================================================================== */
console.log('\n2 · L’accord avec le configurateur de nebula-agency.online');

if (!fs.existsSync(SITE.replace('file://', ''))) {
  verifier('site trouvé pour la comparaison', false, SITE);
} else {
  const pSite = await ctx.newPage();
  await pSite.goto(SITE, { waitUntil: 'domcontentloaded' });
  // mêmes options que BRIEF_OUTIL : jour, graphiques, tableau de bord,
  // rapport auto email, email, 2-5 utilisateurs, niveau intermédiaire
  const plage = await pSite.evaluate(() => {
    ['q_fe4', 'q_a2', 'q_r2', 'q_r4', 'q_i2', 'q_u2', 'q_n2'].forEach(id => {
      const el = document.getElementById(id);
      el.checked = true;
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
    return document.getElementById('dm-range').textContent.replace(/\s+/g, ' ').trim();
  });
  egal('le site donne le même chiffre que nous', plage, '300 000 – 420 000 F');
  await pSite.close();
}

/* ===================================================================
   3 · LES GARDE-FOUS DU SOCLE §6
   =================================================================== */
console.log('\n3 · Les garde-fous');

r = await soumettre("Il veut un site vitrine, et il veut être premier sur Google.");
verifier('§6.2 · jamais « premier sur Google »', r.alertes.some(a => /premier sur Google/i.test(a)), r.alertes.join(' | '));

r = await soumettre("Il veut un catalogue de ses produits mais il le veut demain, c’est urgent.");
verifier('§6.1 · jamais moins de 5 à 7 jours', r.alertes.some(a => /5 à 7 jours/i.test(a)), r.alertes.join(' | '));

r = await soumettre("Il veut un outil pour gérer son stock avec des factures normalisées aux normes DGI.");
verifier('§6.4 · jamais la conformité DGI promise', r.alertes.some(a => /facture normalisée/i.test(a)), r.alertes.join(' | '));

r = await soumettre("Il veut un vrai site vitrine pour son entreprise mais il débute et il n’a pas beaucoup d’argent.");
verifier('l’escalier · on redescend vers le Catalogue', r.alertes.some(a => /Catalogue/i.test(a)), r.alertes.join(' | '));

r = await soumettre(BRIEF_OUTIL);
verifier('§6.12 · la fourchette n’est pas un prix ferme', r.alertes.some(a => /pas un prix ferme/i.test(a)), r.alertes.join(' | '));

r = await soumettre("Elle vend des gâteaux et des pâtisseries sur commande, elle veut montrer ses produits.");
verifier('§10 · la preuve du métier est proposée', r.alertes.some(a => /Miss Cakes|Braisé/i.test(a)), r.alertes.join(' | '));

/* la commission ne doit jamais partir chez le client */
r = await soumettre(BRIEF_OUTIL);
verifier('le message client ne contient aucune commission', !/commission/i.test(r.msg));
verifier('en mode NEBULA, la fiche parle périmètre, pas commission',
  /INTERVALLE À ANNONCER/.test(r.fiche) && !/MA COMMISSION/.test(r.fiche));
/* ⚠️ `hidden` ne cache rien si une règle CSS pose un `display`. On mesure donc
   ce que l'œil voit, jamais l'attribut : c'est ce qui avait laissé passer le bug. */
const cacheReel = await page.evaluate(() => {
  const dur = [];
  ['commission', 'cadrage', 'grp-options', 'grp-compteurs', 'legende', 'gain-r', 'barre-a']
    .forEach(id => {
      const el = document.getElementById(id);
      if (el && el.hidden && getComputedStyle(el).display !== 'none') dur.push(id);
    });
  return dur;
});
verifier('un bloc marqué caché est vraiment invisible', cacheReel.length === 0,
  'encore visibles : ' + cacheReel.join(', '));
verifier('en mode NEBULA, la commission ne s’affiche pas',
  await page.evaluate(() => getComputedStyle(document.getElementById('commission')).display === 'none'));
await page.click('.modes button[data-mode="partenaire"]');
await page.waitForTimeout(60);
const fichePartenaire = await page.evaluate(() => ({
  fiche: document.getElementById('fiche').value,
  commissionVisible: getComputedStyle(document.getElementById('commission')).display !== 'none'
}));
verifier('en mode partenaire, la commission revient',
  /MA COMMISSION/.test(fichePartenaire.fiche) && fichePartenaire.commissionVisible);
await page.click('.modes button[data-mode="nebula"]');
await page.waitForTimeout(60);

/* le surlignage : les mots du client sont bien montrés */
r = await soumettre("Elle veut un catalogue de 30 produits commandables sur WhatsApp.");
verifier('les mots déclencheurs sont surlignés', r.surlignes.length >= 3, r.surlignes.join(' | '));
verifier('« catalogue » est surligné', r.surlignes.some(m => /catalogue/i.test(m)), r.surlignes.join(' | '));

/* l'intervalle de cadrage : il sort de deux hypothèses nommées, jamais d'un pourcentage */
r = await soumettre("Madame veut un site pour son institut de beauté.");
egal('site sans nombre de pages = 150 000 à 240 000 F', r.total, '150 000 – 240 000 F');
verifier('l’outil dit ce qu’il reste à demander', /Combien de pages/i.test(r.cadrage), r.cadrage.slice(0, 80));
verifier('le message assume l’intervalle au lieu d’un chiffre sec',
  /je n’ai pas encore/.test(r.msg), (r.msg.split('\n').find(l => /dépend/.test(l)) || '').slice(0, 70));

r = await soumettre("Il lui faut un site vitrine pour son entreprise, une seule page suffit.");
egal('une seule page annoncée ferme le prix', r.total, '150 000 F');

r = await soumettre("Elle veut vendre ses produits sur WhatsApp, avec un bouton de commande.");
egal('catalogue sans nombre de produits = 50 000 à 95 000 F', r.total, '50 000 – 95 000 F');

/* un brief qui dit deux choses : la seconde offre ne doit pas disparaître */
r = await soumettre("Elle a une clinique esthétique de luxe. Elle veut un site pour présenter sa maison, avec ses soins et ses produits que ses clientes puissent commander sur WhatsApp. Elle a trois marques.");
verifier('la seconde offre lue est signalée', r.alertes.some(a => /Il a aussi parlé de/.test(a)),
  r.alertes.join(' | '));
verifier('et elle est chiffrée dans le signalement',
  r.alertes.some(a => /150 000 F|50 000 F/.test(a)), r.alertes.join(' | '));

/* le texte vide ne chiffre rien */
r = await soumettre('');
egal('un champ vide ne propose aucun prix', r.total, 'Rien à chiffrer pour l’instant');

/* la correction manuelle gagne sur la lecture */
await soumettre("Elle veut un catalogue de 30 produits.");
await page.click('[data-offre="vitrine"]');
await page.waitForTimeout(60);
const apres = await page.evaluate(() => document.getElementById('barre-v').textContent.replace(/\s+/g, ' ').trim());
egal('ajouter la vitrine à la main ouvre le périmètre des pages', apres, '215 000 – 305 000 F');

/* ===================================================================
   4 · LA PAGE
   =================================================================== */
console.log('\n4 · La page');

verifier('aucune erreur JavaScript', erreursJS.length === 0, erreursJS.slice(0, 3).join(' | '));
verifier('aucune ressource externe', externes.length === 0, externes.slice(0, 3).join(' | '));

await soumettre(BRIEF_OUTIL);

for (const [l, h, nom] of [[390, 844, 'téléphone'], [768, 1024, 'tablette'], [1440, 900, 'ordinateur']]) {
  await page.setViewportSize({ width: l, height: h });
  await page.waitForTimeout(120);
  const debord = await page.evaluate(() => {
    const trop = [];
    document.querySelectorAll('body *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && (r.right > window.innerWidth + 1 || r.left < -1)) {
        trop.push(el.tagName.toLowerCase() + '.' + (el.className || '').toString().split(' ')[0]);
      }
    });
    return { trop: [...new Set(trop)], scroll: document.documentElement.scrollWidth > window.innerWidth + 1 };
  });
  verifier(`aucun débordement en ${l}px (${nom})`, !debord.scroll && debord.trop.length === 0, debord.trop.slice(0, 4).join(', '));
}

await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(120);
const petites = await page.evaluate(() => {
  const p = [];
  document.querySelectorAll('button, a.aller, a.btn, input, summary').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.height > 0 && (r.height < 44 || r.width < 30)) {
      p.push((el.textContent || el.id).trim().slice(0, 22) + ` ${Math.round(r.width)}×${Math.round(r.height)}`);
    }
  });
  return p;
});
verifier('toutes les cibles font au moins 44 px de haut', petites.length === 0, petites.slice(0, 5).join(' | '));

/* la barre collante ne doit jamais couper le montant : c'est le seul chiffre
   visible quand on fait défiler, un « 300 000 – 420 … » ne sert à rien */
const barre = await page.evaluate(() => {
  const v = document.getElementById('barre-v');
  return { texte: v.textContent, coupe: v.scrollWidth > v.clientWidth + 1 };
});
verifier('la barre collante affiche le montant en entier', !barre.coupe, barre.texte);

/* les 4 offres restent lisibles côte à côte sur un téléphone */
const cartes = await page.evaluate(() =>
  Array.from(document.querySelectorAll('.offre')).map(o => ({
    t: o.querySelector('.t').textContent,
    coupe: o.querySelector('.p').scrollWidth > o.querySelector('.p').clientWidth + 1
  })));
verifier('aucun prix d’offre n’est tronqué', cartes.every(c => !c.coupe),
  cartes.filter(c => c.coupe).map(c => c.t).join(', '));

/* les deux thèmes tiennent */
fs.mkdirSync(CAPTURES, { recursive: true });
for (const theme of ['dark', 'light']) {
  await page.evaluate(t => document.documentElement.setAttribute('data-theme', t), theme);
  await page.waitForTimeout(150);
  const contraste = await page.evaluate(() => {
    const c = getComputedStyle(document.body);
    return { fond: c.backgroundColor, txt: c.color };
  });
  verifier(`thème ${theme} appliqué`, contraste.fond !== contraste.txt, JSON.stringify(contraste));
  await page.screenshot({ path: path.join(CAPTURES, `devis-390-${theme}.png`), fullPage: true });
}

await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
await page.setViewportSize({ width: 1440, height: 900 });
await page.waitForTimeout(150);
await page.screenshot({ path: path.join(CAPTURES, 'devis-1440-dark.png'), fullPage: true });

/* les polices sont bien celles qu'on a embarquées */
const polices = await page.evaluate(async () => {
  await document.fonts.ready;
  return { chargees: [...document.fonts].map(f => f.family), h1: getComputedStyle(document.querySelector('h1')).fontFamily };
});
verifier('Syne, Inter et JetBrains Mono sont embarquées',
  ['Syne', 'Inter', 'JetBrains Mono'].every(f => polices.chargees.includes(f)), polices.chargees.join(', '));
verifier('le titre est bien en Syne', /Syne/.test(polices.h1), polices.h1);

/* ------------------------------------------------------------------ */
await navigateur.close();

console.log('\n' + '─'.repeat(56));
console.log(`${ok} contrôles verts, ${ko} rouges`);
if (ko) { console.log('\nÀ CORRIGER :'); echecs.forEach(e => console.log('  · ' + e)); process.exit(1); }
console.log('Tout est vert. Captures dans _captures/.');
