import w from './_worker.js';
let ok=0, ko=0;
const t=(n,c,i='')=>{ c?(ok++,console.log('  OK   '+n)) : (ko++,console.log('  ROUGE '+n+'  '+i)); };

const KV = new Map([['v:cadeau-ab12','<h1>la vraie page</h1>']]);
const env = { ORIGINE:'https://origine.test', PAGES:{ get:async k=>KV.get(k) ?? null } };

// on espionne les appels a l'origine
let versOrigine=[];
globalThis.fetch = async (url,init)=>{ versOrigine.push(url); return new Response('ORIGINE',{status:200}); };

const R=(p,m='GET')=>new Request('https://minuit.test'+p,{method:m});

console.log('\n=== La page livree ne touche JAMAIS l\'origine ===');
versOrigine=[];
let r=await w.fetch(R('/v/cadeau-ab12'), env);
t('servie en 200', r.status===200);
t('c\'est bien le contenu de KV', (await r.text())==='<h1>la vraie page</h1>');
t('AUCUN APPEL A L\'ORIGINE (donc aucun reveil)', versOrigine.length===0, JSON.stringify(versOrigine));
t('marquee comme venant du bord', r.headers.get('x-vitrina-source')==='kv');
t('non indexable (prenom + photos)', /noindex/.test(r.headers.get('x-robots-tag')||''));
t('bon type de contenu', /text\/html/.test(r.headers.get('content-type')||''));

console.log('\n=== L\'apercu (pas encore valide) retombe sur l\'origine ===');
versOrigine=[];
r=await w.fetch(R('/v/pas-encore'), env);
t('relaye vers l\'origine', versOrigine.length===1, JSON.stringify(versOrigine));
t('  -> bonne cible', String(versOrigine[0]).includes('/v/pas-encore'));

console.log('\n=== Le reste passe au backend ===');
versOrigine=[];
await w.fetch(R('/admin'), env);
await w.fetch(R('/api/order','POST'), env);
t('back-office et API relayes', versOrigine.length===2, JSON.stringify(versOrigine));

console.log('\n=== Slug tordu : jamais de lecture KV sauvage ===');
let lus=[];
const envEsp={...env, PAGES:{get:async k=>{lus.push(k);return null;}}};
versOrigine=[];
await w.fetch(R('/v/..%2F..%2Fetc%2Fpasswd'), envEsp);
t('un slug invalide n\'interroge pas KV', lus.length===0, JSON.stringify(lus));
await w.fetch(R('/v/bon-slug'), envEsp);
t('un slug valide interroge KV', lus.length===1 && lus[0]==='v:bon-slug', JSON.stringify(lus));

console.log('\n=== Sans liaison KV : rien ne casse ===');
versOrigine=[];
r=await w.fetch(R('/v/cadeau-ab12'), {ORIGINE:'https://origine.test'});
t('retombe sur l\'origine', versOrigine.length===1);

console.log('\n=== Sans ORIGINE : message clair, pas une page blanche ===');
r=await w.fetch(R('/admin'), {});
t('503 explicite', r.status===503);
t('  -> dit quoi faire', (await r.text()).includes('ORIGINE'));
r=await w.fetch(R('/v/inconnu'), {});
t('page inconnue = 404 franc', r.status===404);

console.log(`\n===== ${ok} verts / ${ko} rouges =====`);
process.exit(ko?1:0);
