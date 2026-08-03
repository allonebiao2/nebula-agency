// Contrôle du carnet de prospection : il doit marcher au pouce, dans la rue.
const puppeteer = require('puppeteer-core');
const path = require('path');

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const FICHIER = 'file:///' + path.resolve(__dirname, 'carnet-prospection.html').replace(/\\/g, '/');

(async () => {
  const nav = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox'] });
  const ok = [], ko = [];
  const dire = (bon, quoi) => (bon ? ok : ko).push(quoi);

  for (const [nom, w, h] of [['telephone', 390, 844], ['PC', 1440, 900]]) {
    const page = await nav.newPage();
    const erreurs = [];
    page.on('pageerror', e => erreurs.push(String(e)));
    page.on('console', m => { if (m.type() === 'error') erreurs.push(m.text()); });
    await page.setViewport({ width: w, height: h });
    await page.goto(FICHIER, { waitUntil: 'networkidle0' });

    dire(erreurs.length === 0, `${nom} : ${erreurs.length} erreur(s) JS ${erreurs[0] || ''}`);

    const r = await page.evaluate(() => {
      const cartes = [...document.querySelectorAll('.p')];
      const wa = [...document.querySelectorAll('a.b.w')];
      const petits = [...document.querySelectorAll('a.b, button.e, button.f')]
        .filter(e => { const b = e.getBoundingClientRect(); return b.height > 0 && b.height < 34; });
      return {
        cartes: cartes.length,
        wa: wa.length,
        exempleWa: wa[0] ? wa[0].href : '',
        deborde: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        compte: document.getElementById('compte').textContent,
        petits: petits.length,
        fixesAvecWa: cartes.filter(c => /fixe/i.test(c.textContent) && c.querySelector('a.b.w')).length,
      };
    });

    dire(r.cartes > 150, `${nom} : ${r.cartes} fiches affichées`);
    dire(!r.deborde, `${nom} : aucun débordement horizontal`);
    dire(r.petits === 0, `${nom} : ${r.petits} cible(s) sous 34 px`);
    dire(r.fixesAvecWa === 0, `${nom} : ${r.fixesAvecWa} fixe(s) avec un bouton WhatsApp (doit être 0)`);
    if (nom === 'telephone') {
      dire(/wa\.me\/(229|228)\d+\?text=/.test(r.exempleWa), `lien WhatsApp valide et message pré-rempli`);
      dire(!/50%20000|150%20000/.test(r.exempleWa), `aucun prix dans le message pré-rempli`);
      console.log('   compteur :', r.compte);
      console.log('   exemple  :', decodeURIComponent(r.exempleWa).slice(0, 130).replace(/\n/g, ' / '));
      await page.screenshot({ path: path.join(__dirname, '_qc_telephone.png'), fullPage: false });
    }

    // l'état se garde-t-il ?
    if (nom === 'telephone') {
      await page.click('.p .e[data-v="rdv"]');
      await page.reload({ waitUntil: 'networkidle0' });
      const garde = await page.evaluate(() =>
        !!document.querySelector('.p .e[data-v="rdv"][aria-pressed="true"]'));
      dire(garde, `l'état survit à un rechargement`);
    }
    await page.close();
  }

  await nav.close();
  ok.forEach(x => console.log('  OK  ', x));
  ko.forEach(x => console.log('  KO  ', x));
  console.log(`\n  ${ok.length} contrôles verts, ${ko.length} rouges`);
  process.exit(ko.length ? 1 : 0);
})();
