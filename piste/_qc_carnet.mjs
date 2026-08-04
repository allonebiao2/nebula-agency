import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'
import { fileURLToPath } from 'node:url'; import puppeteer from 'puppeteer-core'
const ICI=path.dirname(fileURLToPath(import.meta.url)), DIST=path.join(ICI,'dist')
const JETON=process.argv[2]
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2'}
const ok=[],ko=[]; const dire=(b,q)=>(b?ok:ko).push(q)
const srv=http.createServer((q,r)=>{let f=path.join(DIST,decodeURIComponent(q.url.split('?')[0]))
 if(!fs.existsSync(f)||fs.statSync(f).isDirectory())f=path.join(DIST,'index.html')
 r.writeHead(200,{'Content-Type':MIME[path.extname(f)]||'application/octet-stream'});r.end(fs.readFileSync(f))})
await new Promise(r=>srv.listen(0,r)); const base=`http://127.0.0.1:${srv.address().port}`
const nav=await puppeteer.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']})
const errs=[]; const p=await nav.newPage()
p.on('pageerror',e=>errs.push(String(e))); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())})
const dodo=ms=>new Promise(r=>setTimeout(r,ms))

// --- un jeton faux ne doit rien ouvrir ---
await p.setViewport({width:390,height:844})
await p.goto(`${base}/#/carnet/CeJetonNexistePasDuTout123456`,{waitUntil:'networkidle0'})
await p.waitForFunction(()=>/n’existe pas|n'existe pas|arrive pas/.test(document.body.innerText),{timeout:25000}).catch(()=>{})
dire(/n’existe pas|n'existe pas/.test(await p.evaluate(()=>document.body.innerText)), `un jeton inconnu n'ouvre aucun carnet`)

// --- le vrai carnet ---
/* Le premier appel a Supabase peut prendre plusieurs secondes au reveil : on
   ATTEND l'affichage au lieu de compter les secondes. Un controle qui mesure
   trop tot invente des defauts qui n'existent pas. */
await p.goto(`${base}/#/carnet/${JETON}`,{waitUntil:'networkidle0'})
await p.waitForSelector('article',{timeout:25000}).catch(()=>{})
await dodo(300)
const r = await p.evaluate(()=>{
  const t=document.body.innerText
  const cartes=[...document.querySelectorAll('article')]
  const wa=[...document.querySelectorAll('a[href^="https://wa.me/"]')]
  const tel=[...document.querySelectorAll('a[href^="tel:"]')]
  const petites=[...document.querySelectorAll('button,a,input')].filter(e=>{const b=e.getBoundingClientRect();return b.height>0&&b.width>0&&b.height<44})
  return {
    fiches:cartes.length,
    ref:/PISTE-TEST/.test(t),
    texte:t.slice(0,400),
    wa:wa.length, tel:tel.length,
    waAvecMessage: wa.filter(a=>a.href.includes('?text=')).length,
    numeroComplet: /\b\d\d \d\d \d\d \d\d\b/.test(t),
    masque: /••/.test(t),
    fixeSansWa: cartes.filter(c=>/ligne fixe/.test(c.innerText) && c.querySelector('a[href^="https://wa.me/"]')).length,
    injoignable: [...document.querySelectorAll('article button')].filter(b=>/Injoignable/.test(b.innerText)).length,
    deborde: document.documentElement.scrollWidth-document.documentElement.clientWidth,
    petites: petites.length,
    cadratin: /[\u2014\u2013]/.test(t),
  }
})
dire(r.fiches===12, `les 12 fiches achetées sont là (${r.fiches})`)
dire(r.ref, `la référence du carnet est affichée`)
dire(r.numeroComplet, `les numéros sont COMPLETS : c'est payé`)
dire(!r.masque, `plus aucun masquage dans le carnet`)
dire(r.wa===10, `10 boutons WhatsApp, un par fiche joignable (${r.wa})`)
dire(r.waAvecMessage===10, `chacun porte le message déjà écrit (${r.waAvecMessage})`)
dire(r.fixeSansWa===0, `aucun bouton WhatsApp sur une ligne fixe (${r.fixeSansWa})`)
dire(r.injoignable===12, `chaque fiche a son bouton « Injoignable ? » (${r.injoignable})`)
dire(r.deborde<=0, `aucun débordement horizontal (${r.deborde} px)`)
dire(r.petites===0, `aucune cible sous 44 px (${r.petites})`)
dire(!r.cadratin, `aucun tiret cadratin`)

// --- l'avancement se garde ---
await p.evaluate(()=>{[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Vendu')?.click()})
await dodo(400)
const avant = await p.evaluate(()=>document.body.innerText.match(/(\d+) vendus?\b/)?.[1])
await p.reload({waitUntil:'networkidle0'})
await p.waitForSelector('article',{timeout:25000}).catch(()=>{})
await dodo(300)
const apres = await p.evaluate(()=>document.body.innerText.match(/(\d+) vendus?\b/)?.[1])
dire(avant==='1'&&apres==='1', `l'avancement survit au rechargement (${avant} puis ${apres})`)

// --- le filtre ---
await p.evaluate(()=>{[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Vendus')?.click()})
await dodo(400)
dire(await p.evaluate(()=>document.querySelectorAll('article').length)===1, `le filtre « Vendus » ne montre que le vendu`)

await p.screenshot({path:path.join(ICI,'_qc_captures','carnet-telephone.png')})
await p.setViewport({width:1440,height:1000})
await p.goto(`${base}/#/carnet/${JETON}`,{waitUntil:'networkidle0'})
await p.waitForSelector('article',{timeout:25000}).catch(()=>{})
await dodo(300)
dire(await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)<=0, `PC : aucun débordement`)
await p.screenshot({path:path.join(ICI,'_qc_captures','carnet-pc.png')})

dire(errs.length===0, `0 erreur JavaScript ${errs[0]||''}`)
await nav.close(); srv.close()
ok.forEach(x=>console.log('  OK  ',x)); ko.forEach(x=>console.log('  KO  ',x))
console.log(`\n  ${ok.length} contrôles verts, ${ko.length} rouges`)
process.exit(ko.length?1:0)
