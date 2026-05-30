/* ===== LUXURY CLUB 229 — Catalogue global =====
   Recherche cross-marque (INA Luxury + Cozy + Luxury Skin Clinic).
   Charge automatiquement les catalogues des 2 autres pages via fetch.
   Aucune duplication de données : la vérité reste dans chaque fichier source.

   Usage sur chaque page :
     <script src="assets/js/global-catalog.js"></script>
     <script>
       LC.initGlobalCatalog({localBrand:'ina', localItems:PRODUCTS});
       LC.globalCatalogPromise.then(cat => { ... });
     </script>
*/
(function(){
  const LC = window.LC = window.LC || {};
  if(LC.globalCatalogPromise)return;

  const BRAND_META = {
    ina:    {label:'INA Luxury',     short:'INA',    url:'ina-luxury.html',         color:'#c9a84c', kind:'produit'},
    cozy:   {label:'Cozy',           short:'COZY',   url:'cozy.html',               color:'#d99aa9', kind:'produit'},
    clinic: {label:'Skin Clinic',    short:'CLINIC', url:'luxury-skin-clinic.html', color:'#7fb6a4', kind:'prestation'}
  };
  LC.BRAND_META = BRAND_META;

  /* Normalise un item en provenance d'un des 3 catalogues vers un format unifié */
  function normalize(item, brand){
    let name, price, sub, tags, desc, isStockOut=false, isNew=!!item.isnew, isBest=!!item.best;
    if(brand==='ina'){
      name = item.n;
      price = (item.p==null)?null:item.p;
      sub = item.s || item.f || '';
      tags = item.c || [];
      desc = item.d || '';
      isStockOut = item.stock===0;
    } else if(brand==='cozy'){
      name = item.n + (item.variant?' — '+item.variant:'');
      price = (item.p==null)?null:item.p;
      sub = item.cat || '';
      tags = item.c || [];
      desc = item.d || '';
    } else if(brand==='clinic'){
      name = item.n;
      price = (item.p==null||item.p===0)?null:item.p;
      sub = item.g || '';
      tags = item.c || [];
      desc = item.d || '';
    }
    return {
      brand,
      name,
      price,
      sub,
      tags,
      desc,
      isNew,
      isBest,
      isStockOut,
      isFree: brand==='clinic' && item.tier==='Gratuite',
      tier: item.tier || null,
      raw: item
    };
  }

  /* Diacritique-insensitive lowercase */
  function norm(s){return (s||'').toString().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');}

  /* Filtre un item par requête multi-mots (AND) */
  function matches(item, q){
    if(!q)return true;
    const hay = norm([item.name, item.sub, item.desc, (item.tags||[]).join(' ')].join(' | '));
    return q.split(/\s+/).filter(Boolean).every(w => hay.includes(w));
  }

  /* Extrait un array JS d'une chaîne HTML : "const NAME=[ ... ];" */
  function extractArray(html, varDecl){
    const i = html.indexOf(varDecl);
    if(i<0)return [];
    const start = html.indexOf('[', i);
    if(start<0)return [];
    let depth=0, inStr=null, esc=false, end=-1;
    for(let k=start;k<html.length;k++){
      const ch=html[k];
      if(esc){esc=false;continue;}
      if(inStr){
        if(ch==='\\'){esc=true;continue;}
        if(ch===inStr)inStr=null;
        continue;
      }
      if(ch==="'"||ch==='"'||ch==='`'){inStr=ch;continue;}
      if(ch==='['){depth++;}
      else if(ch===']'){depth--;if(depth===0){end=k+1;break;}}
    }
    if(end<0)return [];
    const code = html.substring(start,end);
    try{
      // eslint-disable-next-line no-new-func
      return (new Function('return '+code))();
    } catch(e){
      console.warn('[LC catalog] parse failed for', varDecl, e);
      return [];
    }
  }

  async function fetchPageItems(brand){
    const meta = BRAND_META[brand];
    if(!meta)return [];
    try{
      const res = await fetch(meta.url, {credentials:'same-origin', cache:'default'});
      if(!res.ok)throw new Error('HTTP '+res.status);
      const html = await res.text();
      const varName = brand==='clinic' ? 'const SERVICES=' : 'const PRODUCTS=';
      const arr = extractArray(html, varName);
      return arr.map(it => normalize(it, brand));
    } catch(e){
      console.warn('[LC catalog] fetch failed for', brand, e);
      return [];
    }
  }

  /* Init : à appeler dans chaque page avec son catalogue local déjà parsé.
     Évite de re-fetch la page courante. */
  LC.initGlobalCatalog = function(opts){
    const localBrand = opts.localBrand;
    const localItems = (opts.localItems||[]).map(it => normalize(it, localBrand));
    const otherBrands = Object.keys(BRAND_META).filter(b => b!==localBrand);

    LC.globalCatalogPromise = Promise.all(otherBrands.map(fetchPageItems))
      .then(lists => {
        const all = [].concat(localItems, ...lists);
        LC.globalCatalog = all;
        return all;
      });

    /* Catalogue local immédiat (pour ne pas bloquer la 1ère frappe) */
    LC.localCatalog = localItems;
  };

  LC.matches = matches;
  LC.norm = norm;
})();
