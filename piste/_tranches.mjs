/* La vitrine en tranches d'écran : on regarde ce que le pouce voit vraiment. */
import { chromium } from 'playwright'
import { createServer } from 'node:http'
import { readFile, stat, mkdir } from 'node:fs/promises'
import { extname, join, resolve } from 'node:path'
const DIST = resolve(import.meta.dirname, 'dist')
const SORTIE = resolve(import.meta.dirname, '_captures/tranches')
const TYPES = { '.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.woff2':'font/woff2' }
const srv = createServer(async (req,res)=>{
  const c=decodeURIComponent(req.url.split('?')[0]); let f=join(DIST,c==='/'?'index.html':c)
  try{ if((await stat(f)).isDirectory()) f=join(f,'index.html') }catch{ f=join(DIST,'index.html') }
  try{ res.writeHead(200,{'content-type':TYPES[extname(f)]||'application/octet-stream'}).end(await readFile(f)) }catch{ res.writeHead(404).end('x') }
})
await new Promise(r=>srv.listen(0,'127.0.0.1',r))
const base=`http://127.0.0.1:${srv.address().port}`
await mkdir(SORTIE,{recursive:true})
const nav=await chromium.launch({args:['--no-sandbox'],executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'})
const [,,largeur='390',hauteur='844',route='#/'] = process.argv
const page=await nav.newPage({viewport:{width:+largeur,height:+hauteur}})
await page.goto(base+'/'+route,{waitUntil:'networkidle'})
const total=await page.evaluate(()=>document.body.scrollHeight)
let i=0
for(let y=0;y<total;y+=Math.round(hauteur*0.92)){
  await page.evaluate((yy)=>window.scrollTo({top:yy,behavior:'instant'}),y)
  await page.waitForTimeout(2600)
  await page.screenshot({path:join(SORTIE,`${largeur}-${String(++i).padStart(2,'0')}.png`)})
}
await nav.close();srv.close();console.log(i+' tranches')
