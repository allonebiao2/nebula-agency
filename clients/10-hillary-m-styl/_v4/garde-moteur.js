/* ==================================================================
   HILLARY M. STYL — moteur de commande
   NEBULA Agency · 2026
   ==================================================================

   ┌────────────────────────────────────────────────────────────────┐
   │  RÉGLAGES DU SITE — ce que la cliente peut faire évoluer       │
   │                                                                │
   │  1. WHATSAPP  : ✅ FAIT — +229 51 37 47 93                      │
   │  2. EMAIL     : adresse de repli si le client n'a pas WhatsApp │
   │  3. PAYS      : frais d'expédition et jours d'acheminement     │
   │  4. DELAIS    : délais de confection et supplément express     │
   │  5. PIECES    : le vrai catalogue, vrais prix, vraies photos   │
   │  6. ATELIER   : ✅ retrait sur RDV via WhatsApp · délais posés  │
   │  7. MESURES.robe_ovale : liste à valider par l'atelier         │
   │                                                                │
   │  ⚠️ Tester le lien en envoyant un VRAI message avant diffusion. │
   └────────────────────────────────────────────────────────────────┘ */

/* ---------- 1 & 2 · CONTACT ------------------------------------- */
var WHATSAPP = "22951374793";            /* +229 51 37 47 93 — fourni par Mongazi le 2026-08-01 */
/* ⛔ VIDE TANT QU'HILLARY N'A PAS DONNÉ SA VRAIE ADRESSE.
   Une adresse inventée était affichée sur le site EN LIGNE et servait de
   destination réelle au lien « je n'ai pas WhatsApp » : la commande
   partait dans le vide et personne ne le savait. Un contact faux est pire
   que pas de contact. Tant que c'est vide, la ligne « Email » disparaît du
   bloc contact et le lien de repli est remplacé par un appel téléphonique.
   Pour l'activer : écrire l'adresse ici, rien d'autre à toucher. */
var EMAIL    = "";

/* ---------- 6 · ATELIER ----------------------------------------- */
var ATELIER = {
  pays: "bj",
  adresse: "Retrait sur rendez-vous · le point de retrait vous est donné sur WhatsApp",
  /* ⚠️ ACCORDÉ AU CATALOGUE. Ses quatre pièces sont à deux semaines fermes
     et l'express va de 2 à 5 jours selon la pièce : le bloc contact
     annonçait « 7 à 14 jours · 1 à 3 jours », ce qui contredisait chaque
     carte du catalogue. Deux chiffres différents sur la même page, c'est
     le client qui choisit celui qui l'arrange. */
  horaires: "Confection : 2 semaines · 2 à 5 jours en express"
};

/* ---------- 3 · PAYS, FRAIS ET ACHEMINEMENT --------------------- */
/* frais = coût d'expédition en FCFA · achem = jours de transport   */
var PAYS = [
  {id:"bj", nom:"Bénin",           frais:2000,  achem:1},
  {id:"tg", nom:"Togo",            frais:8000,  achem:2},
  {id:"ci", nom:"Côte d'Ivoire",   frais:12000, achem:4},
  {id:"ng", nom:"Nigeria",         frais:12000, achem:4},
  {id:"sn", nom:"Sénégal",         frais:15000, achem:5},
  {id:"bf", nom:"Burkina Faso",    frais:12000, achem:4},
  {id:"ml", nom:"Mali",            frais:15000, achem:5},
  {id:"ne", nom:"Niger",           frais:15000, achem:5},
  {id:"ga", nom:"Gabon",           frais:25000, achem:7},
  {id:"cm", nom:"Cameroun",        frais:22000, achem:6},
  {id:"fr", nom:"France",          frais:35000, achem:8},
  {id:"other", nom:"Autre pays",   frais:null,  achem:10}
];

/* ---------- 4 · DELAIS DE CONFECTION ---------------------------- */
/* ⚠️ 2026-08-06 — LE SUPPLÉMENT EXPRESS N'EST PAS FIXE.
   Hillary facture l'express PAR PIÈCE : +40 000 sur une robe à 100 000,
   +15 000 sur une robe à 30 000. Un supplément unique lui faisait absorber
   l'écart à chaque commande. Chaque pièce porte donc `expPrix` (le prix
   express TOTAL) et `expMin`/`expMax` (son propre délai express).
   Les valeurs de DELAIS ne servent plus que de repli. */
var DELAIS = {
  /* ⚠️ ce sont les valeurs de SECOURS, pour une pièce qui n'apporterait pas
     les siennes. Elles doivent dire la même chose que le catalogue : ses
     quatre pièces sont à deux semaines, express de 2 à 5 jours. */
  normal:  {id:"normal",  nom:"Délai normal",  jmin:14, jmax:14, sup:0,
            desc:"Confection sereine, dans l'ordre des commandes"},
  express: {id:"express", nom:"Délai express", jmin:2, jmax:5,  sup:0,
            desc:"Commande précipitée, passée devant les autres"}
};

/* le supplément express réellement dû, pour la pièce en cours */
function supExpress(p){
  if(!p) return 0;
  if(p.expPrix != null && p.prix != null) return Math.max(0, p.expPrix - p.prix);
  return DELAIS.express.sup;
}

/* ---------- 7 · LES JEUX DE MESURES PAR TYPE DE VÊTEMENT --------
   C'est le cœur de l'outil : les mesures dépendent du VÊTEMENT,
   pas du genre du client.                                          */
var MESURES = {
  robe_taille: {
    nom: "Robe coupée à la taille",
    champs: [
      {id:"epaules",   g:"Le haut",   l:"Épaules"},
      {id:"carr_dev",  g:"Le haut",   l:"Carrure devant"},
      {id:"poitrine",  g:"Le haut",   l:"Poitrine"},
      {id:"t_taille",  g:"Le haut",   l:"Tour de taille"},
      {id:"l_taille",  g:"Les longueurs", l:"Longueur taille"},
      {id:"l_courte",  g:"Les longueurs", l:"Longueur robe courte"},
      {id:"l_longue",  g:"Les longueurs", l:"Longueur robe longue"},
      {id:"t_manche",  g:"Les manches",   l:"Tour de manche"},
      {id:"l_manche",  g:"Les manches",   l:"Longueur manche"}
    ]
  },
  robe_droite: {
    nom: "Robe droite",
    champs: [
      {id:"epaules",     g:"Le haut", l:"Épaules"},
      {id:"carr_dev",    g:"Le haut", l:"Carrure devant"},
      {id:"poitrine",    g:"Le haut", l:"Poitrine"},
      {id:"t_sous_sein", g:"Le haut", l:"Tour du sous-sein"},
      {id:"t_taille",    g:"Le haut", l:"Tour de taille"},
      {id:"t_ceinture",  g:"Le haut", l:"Tour de ceinture"},
      {id:"t_hanche",    g:"Le haut", l:"Tour de hanche"},
      {id:"l_sous_sein", g:"Les longueurs", l:"Longueur sous-sein"},
      {id:"l_taille",    g:"Les longueurs", l:"Longueur taille"},
      {id:"l_ceinture",  g:"Les longueurs", l:"Longueur ceinture"},
      {id:"l_genou",     g:"Les longueurs", l:"Longueur genou"},
      {id:"l_courte",    g:"Les longueurs", l:"Longueur robe courte"},
      {id:"l_longue",    g:"Les longueurs", l:"Longueur robe longue"},
      {id:"t_manche",    g:"Les manches",   l:"Tour de manche"},
      {id:"l_manche",    g:"Les manches",   l:"Longueur manche"}
    ]
  },
  robe_ovale: {
    nom: "Robe ovale",
    aValider: true,
    champs: [
      {id:"epaules",     g:"Le haut", l:"Épaules"},
      {id:"carr_dev",    g:"Le haut", l:"Carrure devant"},
      {id:"poitrine",    g:"Le haut", l:"Poitrine"},
      {id:"t_sous_sein", g:"Le haut", l:"Tour du sous-sein"},
      {id:"t_taille",    g:"Le haut", l:"Tour de taille"},
      {id:"t_hanche",    g:"Le haut", l:"Tour de hanche"},
      {id:"l_taille",    g:"Les longueurs", l:"Longueur taille"},
      {id:"l_courte",    g:"Les longueurs", l:"Longueur robe courte"},
      {id:"l_longue",    g:"Les longueurs", l:"Longueur robe longue"},
      {id:"t_manche",    g:"Les manches",   l:"Tour de manche"},
      {id:"l_manche",    g:"Les manches",   l:"Longueur manche"}
    ]
  },
  pantalon: {
    nom: "Pantalon",
    champs: [
      {id:"t_taille",   g:"Les tours",     l:"Tour de taille"},
      {id:"t_bassins",  g:"Les tours",     l:"Tour de bassins"},
      {id:"t_cuisse",   g:"Les tours",     l:"Tour de cuisse"},
      {id:"t_genoux",   g:"Les tours",     l:"Tour de genoux"},
      {id:"l_genou",    g:"Les longueurs", l:"Longueur genou"},
      {id:"l_pantalon", g:"Les longueurs", l:"Longueur pantalon"}
    ]
  },
  haut: {
    nom: "Chemise ou haut",
    champs: [
      {id:"epaules",   g:"Le haut", l:"Épaules"},
      {id:"carr_dev",  g:"Le haut", l:"Carrure devant"},
      {id:"carr_dos",  g:"Le haut", l:"Carrure dos"},
      {id:"poitrine",  g:"Le haut", l:"Tour de poitrine"},
      {id:"t_taille",  g:"Le haut", l:"Tour de taille"},
      {id:"l_habit",   g:"Les longueurs", l:"Longueur habit"},
      {id:"t_manche",  g:"Les manches",   l:"Tour de manche"},
      {id:"l_manche",  g:"Les manches",   l:"Longueur manche"}
    ]
  },

  /* Pour une robe bâtie comme deux pièces : un buste ajusté monté sur une
     jupe ample. Hillary demande mot pour mot « ceux d'un pantalon et un
     haut » (2026-08-10). C'est donc l'UNION des deux jeux, sans rien
     réinterpréter, moins le tour de taille qui figurait dans les deux.
     13 mesures au lieu de 14.
     ⚠️ « Longueur pantalon » sur une robe se lit mal pour une cliente :
     à faire reformuler par l'atelier. */
  haut_pantalon: {
    nom: "Robe buste et jupe",
    aValider: true,
    champs: [
      {id:"epaules",    g:"Le haut", l:"Épaules"},
      {id:"carr_dev",   g:"Le haut", l:"Carrure devant"},
      {id:"carr_dos",   g:"Le haut", l:"Carrure dos"},
      {id:"poitrine",   g:"Le haut", l:"Tour de poitrine"},
      {id:"t_taille",   g:"Le haut", l:"Tour de taille"},
      {id:"t_bassins",  g:"Les tours", l:"Tour de bassins"},
      {id:"t_cuisse",   g:"Les tours", l:"Tour de cuisse"},
      {id:"t_genoux",   g:"Les tours", l:"Tour de genoux"},
      {id:"l_habit",    g:"Les longueurs", l:"Longueur habit"},
      {id:"l_genou",    g:"Les longueurs", l:"Longueur genou"},
      {id:"l_pantalon", g:"Les longueurs", l:"Longueur pantalon"},
      {id:"t_manche",   g:"Les manches",   l:"Tour de manche"},
      {id:"l_manche",   g:"Les manches",   l:"Longueur manche"}
    ]
  }
};

var AIDE = "Vous pouvez prendre les mesures vous-même ou inviter quelqu'un à le faire pour vous ou vous aider.";

/* ---------- 5 · LE CATALOGUE ------------------------------------
   cat  : "pap" (prêt-à-porter) ou "sm" (sur-mesure)
   prix : nombre en FCFA, ou null pour « sur devis »
   type : clé de MESURES (sur-mesure) · typeLibre : le client choisit
   jmin/jmax : délai de confection propre à la pièce               */
var TAILLES = ["XS","S","M","L","XL","XXL"];

var PIECES = [
  /* ⚠️ LES VRAIES PIÈCES D'HILLARY, reçues le 2026-08-06.
     Les 12 pièces d'exemple ont disparu : une cliente pouvait commander une
     « Robe Amazone » qui n'existe pas.
       prix    = confection normale        · expPrix = prix express TOTAL
       jmin/jmax = délai normal (jours)    · expMin/expMax = délai express
       type    = jeu de mesures            · img = photo dans assets/images/
     Descriptions réécrites à partir de ses mots, rien d'inventé. */

  {id:"h1", cat:"sm", nom:"Robe de cérémonie", type:"robe_ovale", tag:"Cérémonie",
   img:"piece-ceremonie.webp",
   prix:100000, jmin:14, jmax:14, expPrix:140000, expMin:2, expMax:4,
   eur:150, usd:180, eurExp:210, usdExp:252,
   ds:"Bustier structuré, jupe ample à volants de satin, gele assorti. Deux tie-dye qui se répondent, un de chaque côté. Pour le jour où l'on vous regarde."},

  {id:"h2", cat:"sm", nom:"L'ensemble Mira", type:"robe_ovale", tag:"",
   img:"piece-mira.webp",
   prix:50000, jmin:14, jmax:14, expPrix:75000, expMin:2, expMax:4,
   eur:75, usd:90, eurExp:112, usdExp:135,
   ds:"Haut court à manches ballon et jupe longue à volants étagés. Se porte à une cérémonie, à un cocktail ou à un dîner : c'est la même pièce, ce sont les chaussures qui changent."},

  {id:"h3", cat:"sm", nom:"Ensemble JOSY", type:"robe_ovale", tag:"Fait main",
   img:"piece-josy.webp",
   prix:65000, jmin:14, jmax:14, expPrix:85000, expMin:2, expMax:5,
   eur:100, usd:117, eurExp:127, usdExp:150,
   ds:"Pantalon large en jean, empiècements peints à la main, ceinture corset lacée dans le dos. Entièrement fait à la main, du premier trait au dernier lacet."},

  /* ⚠️ Renommee le 2026-08-10. « Robe de ville » etait le nom que NOUS avions
     donne (deja signale comme a confirmer). Hillary appelle desormais CINQ
     pieces « Robe de ville » : c'est sa categorie. Le descripteur de couleur
     est factuel et provisoire, en attendant ses vrais noms. */
  {id:"h4", cat:"sm", nom:"Robe de ville bleue", type:"robe_ovale", tag:"",
   img:"piece-ville.webp",
   prix:30000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:45, usd:67, eurExp:67, usdExp:81,
   ds:"Dos nu attaché à la nuque, wax à feuillages et panneaux de satin qui s'ouvrent à la marche. La pièce qui va du bureau au dîner sans se changer."},

  /* ── LES TROIS MODELES RECUS LE 2026-08-10 ──────────────────────
     Hillary les nomme TOUS « Robe de ville » : c'est sa catégorie.
     Le descripteur de couleur est PROVISOIRE et factuel (ce que montre
     la photo), le temps qu'elle donne ses vrais noms. Sans lui, la
     commande WhatsApp est ambiguë.
     Les descriptions décrivent ce que la photo montre, rien de plus. */

  {id:"h5", cat:"sm", nom:"Robe de cérémonie violette", type:"haut_pantalon", tag:"Cérémonie",
   img:"piece-violette.webp", img2:"piece-violette-dos.webp",
   prix:40000, jmin:14, jmax:14, expPrix:55000, expMin:2, expMax:4,
   eur:60, usd:72, eurExp:82, usdExp:100,
   ds:"Buste ajusté en uni, manches ballon et jupe longue à volants dans un wax à fougères. Le dos se lace en corset sous une découpe ronde. Le foulard est assorti."},

  {id:"h6", cat:"sm", nom:"Robe Naja", type:"robe_ovale", tag:"",
   img:"piece-orange.webp", img2:"piece-orange-dos.webp",
   prix:35000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:52, usd:63, eurExp:67, usdExp:81,
   ds:"Bustier à découpe sous la poitrine, manches ballon détachées des épaules, jupe courte très ample. Le dos se lace. Semis de motifs blancs sur l'orange."},

  {id:"h7", cat:"sm", nom:"Robe de ville verte", type:"robe_ovale", tag:"",
   img:"piece-verte.webp", img2:"piece-verte-dos.webp",
   prix:35000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:52, usd:63, eurExp:67, usdExp:81,
   ds:"Une seule épaule, nouée sur le côté. La taille descend bas, la jupe est froncée et très ample. Wax à nœuds jaune et brun sur fond sauge."},

  /* ⚠️ Celle-ci est violette elle aussi : le seul descripteur de couleur ne
     suffisait plus. On la distingue par ce qui saute aux yeux, son volant
     de tulle. Nom provisoire, comme les autres. */
  {id:"h8", cat:"sm", nom:"Robe de ville à tulle", type:"haut_pantalon", tag:"",
   img:"piece-tulle.webp", img2:"piece-tulle-dos.webp",
   prix:35000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:52, usd:63, eurExp:67, usdExp:81,
   ds:"Col montant noué derrière la nuque, dos entièrement dégagé, jupe courte et évasée. Un volant de tulle violet dépasse sous le wax à volutes."},

  /* Une CRÉATION LIBRE : ce n'est pas un vêtement inventé, c'est un service.
     Aucun prix (« sur devis »), aucune photo revendiquée : le client décrit
     ce qu'il veut, choisit le type de vêtement, et on en parle. C'était déjà
     là avant, et c'est la porte d'entrée pour tout ce qui n'est pas au
     catalogue — ce qui, chez une couturière, est la majorité du travail. */
  {id:"h9", cat:"sm", nom:"Création libre", typeLibre:true, tag:"Sur devis",
   prix:null, jmin:14, jmax:14, expMin:2, expMax:5,
   ds:"Vous avez un modèle en tête, une photo, une idée. Vous choisissez le vêtement, vous donnez vos mesures, et le prix se décide ensemble avant de commencer."}
];

/* ================================================================
   MOTEUR — rien à modifier en dessous
   ================================================================ */
var $  = function(s,c){return (c||document).querySelector(s);};
var $$ = function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s));};
var esc = function(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});};
var fcfa = function(n){return Number(n).toLocaleString("fr-FR").replace(/ | /g," ")+" F";};

var JOURS = ["dimanche","lundi","mardi","mercredi","jeudi","vendredi","samedi"];
var MOIS  = ["janvier","février","mars","avril","mai","juin","juillet","août",
             "septembre","octobre","novembre","décembre"];

/* Libellé d'un délai. Ses quatre pièces sont à 2 semaines FERMES : jmin et
   jmax valent 14 tous les deux, et « 14 à 14 jours » se lit comme une erreur
   de la maison. Quand les deux bornes se rejoignent, on n'annonce qu'un
   chiffre. Vu à l'œil sur le catalogue le 2026-08-06. */
function libDelai(a, b){
  a = Number(a); b = Number(b);
  return a === b ? a + " jours" : a + " à " + b + " jours";
}

/* Date de disponibilité — annoncée sur la BORNE HAUTE du délai.
   Promettre le jour 8 d'un « 8 à 14 jours » fabrique un client déçu. */
function dateDispo(jours){
  var d = new Date();
  d.setHours(0,0,0,0);
  d.setDate(d.getDate() + Number(jours||0));
  return d;
}
function dateFr(d){
  return JOURS[d.getDay()]+" "+d.getDate()+" "+MOIS[d.getMonth()]+
         (d.getFullYear()!==new Date().getFullYear()? " "+d.getFullYear() : "");
}

/* ---------- accueil personnalisé -------------------------------- */
var LS = "hms:client";
function memoire(){
  try{ return JSON.parse(localStorage.getItem(LS)||"{}"); }catch(e){ return {}; }
}
function memorise(o){
  try{
    var m = memoire();
    for(var k in o){ if(o[k]) m[k]=o[k]; }
    localStorage.setItem(LS, JSON.stringify(m));
  }catch(e){}
}
(function accueil(){
  var h = new Date().getHours();
  var salut = h<12 ? "Bonjour" : (h<18 ? "Bon après-midi" : "Bonsoir");
  var m = memoire();
  var t = m.prenom
    ? salut+" "+m.prenom+", contente de vous revoir."
    : salut+" — bienvenue chez HILLARY M. STYL.";
  var el = document.getElementById("helloTxt");
  if(el) el.textContent = t;
})();

/* ---------- catalogue ------------------------------------------- */
var HORLOGE = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.6"/><path d="M12 7.4V12l3.1 1.9"/></svg>';

function carte(p){
  var prix = p.prix==null ? "Sur devis" : fcfa(p.prix);
  /* Hillary donne ses prix en trois monnaies. On les affiche tels quels :
     ce sont SES prix, pas une conversion — on ne les recalcule jamais. */
  var dev = (p.eur!=null||p.usd!=null)
    ? '<span class="dev">'+[p.eur!=null?p.eur+" €":null, p.usd!=null?"$"+p.usd:null]
        .filter(Boolean).join(" · ")+'</span>' : '';
  return '<button class="piece" type="button" data-id="'+p.id+'">'+
    '<div class="ph">'+(p.tag?'<span class="tag">'+esc(p.tag)+'</span>':'')+
      (p.img
        ? '<img src="assets/images/'+esc(p.img)+'" alt="'+esc(p.nom)+', création Hillary M. Styl" loading="lazy" decoding="async">'
        /* ⚠️ PAS de « photo à venir » sur un site en ligne : un texte
           d'attente dit au client que la maison n'est pas prête. Cette carte
           est la « Création libre » — elle n'a pas de photo parce qu'elle n'a
           pas de modèle, et c'est ça qu'il faut écrire. */
        : '<div class="mark"></div><span class="avenir">Votre modèle</span>')+
      '<span class="voile"><span>Commander</span></span></div>'+
    '<div class="bd">'+
      '<h3>'+esc(p.nom)+'</h3>'+
      '<p class="ds">'+esc(p.ds)+'</p>'+
      '<div class="meta"><span class="pr">'+prix+dev+'</span>'+
        '<span class="del">'+HORLOGE+'<span>'+libDelai(p.jmin, p.jmax)+'</span></span></div>'+
    '</div></button>';
}
function rendreGrille(cat){
  var g = document.getElementById("grille");
  g.innerHTML = PIECES.filter(function(p){return p.cat===cat;}).map(carte).join("");
}
function compteCat(cat){
  return PIECES.filter(function(p){return p.cat===cat;}).length;
}
function onglet(cat){
  /* ⚠️ un onglet vide ne s'affiche pas, et n'est jamais celui qu'on ouvre.
     Le 2026-08-06, les 4 vraies pièces étaient toutes en sur-mesure : le
     catalogue s'ouvrait sur un « prêt-à-porter » sans une seule pièce. */
  $$(".tab").forEach(function(t){
    var vide = compteCat(t.dataset.onglet) === 0;
    t.hidden = vide;
    t.setAttribute("aria-selected", (!vide && t.dataset.onglet===cat) ? "true":"false");
  });
  var tabs = document.querySelector(".tabs");
  if(tabs) tabs.hidden = $$(".tab").filter(function(t){return !t.hidden;}).length < 2;
  rendreGrille(cat);
}
function premiereCatPleine(){
  var c = ["pap","sm"].filter(function(x){ return compteCat(x) > 0; });
  return c.length ? c[0] : "pap";
}
$$("[data-onglet]").forEach(function(b){
  b.addEventListener("click", function(){
    onglet(b.dataset.onglet);
    if(!b.classList.contains("tab")){
      document.getElementById("catalogue").scrollIntoView({behavior:"smooth", block:"start"});
    }
  });
});
onglet(premiereCatPleine());

/* ---------- état de la commande --------------------------------- */
var etat = null;

function ouvrir(id){
  var p = PIECES.filter(function(x){return x.id===id;})[0];
  if(!p) return;
  var m = memoire();
  etat = {
    piece: p,
    etape: 1,
    taille: null,
    typeMesure: p.type || (p.typeLibre ? null : null),
    mesures: {},
    tissu: "",
    details: "",
    mode: null,          /* "retrait" | "expedition" */
    pays: null,
    delai: null,
    prenom: m.prenom||"", nom: m.nom||"", tel: m.tel||"", mail: m.mail||"",
    ville: m.ville||"", note: ""
  };
  document.getElementById("shTitre").textContent = p.nom;
  document.getElementById("shSub").textContent = (p.cat==="sm" ? "Sur-mesure" : "Prêt-à-porter")+
    " · "+(p.prix==null ? "sur devis" : fcfa(p.prix));
  document.getElementById("ov").classList.add("on");
  document.body.style.overflow = "hidden";
  dessiner();
}
function fermer(){
  document.getElementById("ov").classList.remove("on");
  document.body.style.overflow = "";
  etat = null;
}
document.getElementById("grille").addEventListener("click", function(e){
  var b = e.target.closest ? e.target.closest(".piece") : null;
  if(b) ouvrir(b.dataset.id);
});
document.getElementById("btX").addEventListener("click", fermer);
document.getElementById("ov").addEventListener("click", function(e){ if(e.target===this) fermer(); });
document.addEventListener("keydown", function(e){ if(e.key==="Escape" && etat) fermer(); });

/* ---------- calculs --------------------------------------------- */
function fraisLivraison(){
  if(!etat || etat.mode!=="expedition" || !etat.pays) return 0;
  return etat.pays.frais==null ? null : etat.pays.frais;
}
function joursAcheminement(){
  if(!etat || etat.mode!=="expedition" || !etat.pays) return 0;
  return etat.pays.achem||0;
}
function totalCommande(){
  if(!etat) return null;
  if(etat.piece.prix==null) return null;                 /* sur devis */
  var f = fraisLivraison();
  if(f===null) return null;                              /* pays « autre » */
  var sup = (etat.delai && etat.delai.id === "express") ? supExpress(etat.piece) : 0;
  return etat.piece.prix + f + sup;
}
function joursTotal(){
  if(!etat || !etat.delai) return null;
  /* borne haute du délai de confection propre à la pièce, ajustée
     par le mode de délai choisi, plus l'acheminement */
  var conf = etat.delai.id==="express"
    ? (etat.piece.expMax != null ? etat.piece.expMax : etat.delai.jmax)
    : Math.max(etat.piece.jmax, etat.delai.jmin);
  return conf + joursAcheminement();
}

/* ---------- rendu ----------------------------------------------- */
function dessiner(){
  if(!etat) return;
  $$("#prog i").forEach(function(i,k){ i.classList.toggle("on", k < etat.etape); });
  var bd = document.getElementById("shBd");
  var ft = document.getElementById("shFt");
  var e  = etat.etape;

  if(e===1)      bd.innerHTML = vue1();
  else if(e===2) bd.innerHTML = vue2();
  else if(e===3) bd.innerHTML = vue3();
  else if(e===4) bd.innerHTML = vue4();
  else           bd.innerHTML = vue5();

  ft.innerHTML = pied();
  brancher();
  document.querySelector(".sheet").scrollTop = 0;
  document.getElementById("ov").scrollTop = 0;
}

/* --- étape 1 : taille ou mesures --- */
function vue1(){
  var p = etat.piece;
  if(p.cat==="pap"){
    return '<div class="stitle">Votre taille</div>'+
      '<div class="sdesc">Choisissez la taille qui vous correspond. En cas de doute, prenez la plus grande : une retouche à la baisse est gratuite à l\'atelier.</div>'+
      '<div class="tailles">'+TAILLES.map(function(t){
        return '<button class="taille'+(etat.taille===t?" sel":"")+'" type="button" data-taille="'+t+'">'+t+'</button>';
      }).join("")+'</div>'+
      '<div class="mes" style="margin-top:20px"><div class="fd full"><label for="f_det">Une précision sur votre commande ?</label>'+
      '<textarea id="f_det" placeholder="Couleur souhaitée, longueur de manche, occasion…">'+esc(etat.details)+'</textarea></div></div>';
  }
  /* sur-mesure */
  var h = '';
  if(p.typeLibre){
    h += '<div class="stitle">Quel vêtement ?</div>'+
      '<div class="sdesc">Les mesures demandées dépendent du vêtement. Choisissez d\'abord le type.</div>'+
      '<div class="fd" style="margin-bottom:18px"><label for="f_type">Type de vêtement</label><select id="f_type">'+
        '<option value="">— Choisir —</option>'+
        Object.keys(MESURES).map(function(k){
          return '<option value="'+k+'"'+(etat.typeMesure===k?" selected":"")+'>'+esc(MESURES[k].nom)+'</option>';
        }).join("")+
      '</select></div>';
    if(!etat.typeMesure) return h;
  }
  var jeu = MESURES[etat.typeMesure];
  if(!jeu) return h || '<div class="sdesc">Type de vêtement introuvable.</div>';

  /* La seconde vue, quand la pièce en a une. Elle se montre ICI, au moment
     où la cliente entre ses mesures : c'est là qu'elle a besoin de voir
     comment la pièce est bâtie derrière (un laçage, un dos nu, un volant). */
  if(p.img2){
    h += '<figure class="dosvue">'+
         '<img src="assets/images/'+esc(p.img2)+'" alt="'+esc(p.nom)+', vu de dos" '+
         'loading="lazy" decoding="async">'+
         '<figcaption>Le dos</figcaption></figure>';
  }

  /* le nom du vêtement descend dans la ligne de description : en didone,
     le tiret cadratin est un cheveu, et « Vos mesures — Robe droite » cassait mal */
  h += '<div class="stitle">Vos mesures</div>'+
       '<div class="sdesc"><b style="color:var(--encre)">'+esc(jeu.nom)+'</b> · '+
       jeu.champs.length+' mesures, en centimètres. Un ruban de couturière suffit.</div>'+
       '<div class="aide"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/></svg>'+
       '<p>'+esc(AIDE)+'</p></div>';
  if(jeu.aValider){
    h += '<div class="warn"><strong>Liste de mesures en cours de validation par l\'atelier.</strong> '+
         'Nous vous rappellerons pour confirmer ou compléter ces mesures avant de couper.</div>';
  }
  h += '<div class="mes">';
  var groupe = null;
  jeu.champs.forEach(function(c){
    if(c.g!==groupe){ groupe=c.g; h += '<div class="mes-hd">'+esc(groupe)+'</div>'; }
    h += '<div class="fd cm"><label for="m_'+c.id+'">'+esc(c.l)+'</label><div class="ipw">'+
         '<input id="m_'+c.id+'" type="number" inputmode="decimal" min="1" max="300" step="0.5" '+
         'data-mes="'+c.id+'" placeholder="—" value="'+esc(etat.mesures[c.id]||"")+'"><span class="unit">cm</span></div></div>';
  });
  h += '<div class="fd full"><label for="f_tissu">Tissu souhaité</label>'+
       '<input id="f_tissu" type="text" placeholder="Wax, bazin, satin… ou « à conseiller »" value="'+esc(etat.tissu)+'"></div>'+
       '<div class="fd full"><label for="f_det">Le modèle et les détails</label>'+
       '<textarea id="f_det" placeholder="Longueur, col, manches, doublure, occasion… Vous pouvez aussi nous envoyer une photo sur WhatsApp après la commande.">'+esc(etat.details)+'</textarea></div>'+
       '</div>'+
       '<div class="momo"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 10h6M9 14h6M12 7v10"/></svg>'+
       '<span>Une mesure que vous ne savez pas prendre ? Laissez-la vide : elle partira en « à prendre ensemble » et nous vous appellerons.</span></div>';
  return h;
}

/* --- étape 2 : retrait ou expédition --- */
function vue2(){
  var h = '<div class="stitle">Retrait ou expédition ?</div>'+
    '<div class="sdesc">Le retrait à l\'atelier est gratuit et permet l\'essayage. L\'expédition est facturée selon votre pays.</div>'+
    '<div class="opts">'+
      '<button class="opt'+(etat.mode==="retrait"?" sel":"")+'" type="button" data-mode="retrait">'+
        '<span class="rd"></span><span class="tx"><b>Retrait à l\'atelier</b>'+
        '<span>'+esc(ATELIER.adresse)+' · essayage et retouche sur place</span></span>'+
        '<span class="pz">Gratuit</span></button>'+
      '<button class="opt'+(etat.mode==="expedition"?" sel":"")+'" type="button" data-mode="expedition">'+
        '<span class="rd"></span><span class="tx"><b>Expédition</b>'+
        '<span>Nous envoyons la tenue chez vous</span></span>'+
        '<span class="pz" id="pzExp">Selon pays</span></button>'+
    '</div>';

  if(etat.mode==="expedition"){
    h += '<div class="fd" style="margin-top:16px"><label for="f_pays">Votre pays</label><select id="f_pays">'+
      '<option value="">— Choisir votre pays —</option>'+
      PAYS.map(function(p){
        return '<option value="'+p.id+'"'+(etat.pays&&etat.pays.id===p.id?" selected":"")+'>'+esc(p.nom)+
          (p.frais==null? " (frais à confirmer)" : " — "+fcfa(p.frais))+'</option>';
      }).join("")+'</select></div>';
    if(etat.pays && etat.pays.frais===null){
      h += '<div class="warn" style="margin-top:14px">Nous n\'expédions pas encore automatiquement vers ce pays. '+
           'Envoyez-nous quand même la commande : nous vous donnerons le tarif exact avant tout règlement.</div>';
    }
    h += '<div class="fd" style="margin-top:12px"><label for="f_ville">Ville de livraison</label>'+
         '<input id="f_ville" type="text" placeholder="Cotonou, Abidjan, Dakar…" value="'+esc(etat.ville)+'"></div>';
  }
  if(etat.mode==="retrait"){
    h += '<div class="momo" style="margin-top:16px"><svg viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>'+
         '<span><strong>'+esc(ATELIER.adresse)+'</strong><br>'+esc(ATELIER.horaires)+'</span></div>';
  }
  return h;
}

/* --- étape 3 : délai + date de disponibilité --- */
function vue3(){
  var p = etat.piece;
  var h = '<div class="stitle">Quand la voulez-vous ?</div>'+
    '<div class="sdesc">Cette pièce demande normalement '+libDelai(p.jmin, p.jmax)+' de confection.</div>'+
    '<div class="opts">'+
      opt3(DELAIS.normal, "Confection en "+libDelai(p.jmin, p.jmax))+
      opt3(DELAIS.express, "Votre tenue en "
        +libDelai(p.expMin != null ? p.expMin : DELAIS.express.jmin,
                  p.expMax != null ? p.expMax : DELAIS.express.jmax)
        +" maximum")+
    '</div>';

  if(etat.delai){
    var j = joursTotal();
    var d = dateDispo(j);
    var motLivr = etat.mode==="expedition" ? "Chez vous au plus tard le" : "Prête à retirer au plus tard le";
    var det = etat.mode==="expedition" && joursAcheminement()
      ? "Confection incluse, plus "+joursAcheminement()+" jour"+(joursAcheminement()>1?"s":"")+" d'acheminement vers "+esc(etat.pays?etat.pays.nom:"")+"."
      : "Vous pouvez venir l'essayer à l'atelier ce jour-là.";
    h += '<div class="dispo"><svg viewBox="0 0 24 24"><path d="M4.5 5.5h15v14h-15z"/><path d="M4.5 10h15M8.5 3v4M15.5 3v4"/><path d="M9 15l2 2 4-4"/></svg>'+
      '<div><b>'+motLivr+'</b><p>'+dateFr(d)+'</p><small>'+det+'</small></div></div>';
    if(etat.delai.id==="express"){
      h += '<div class="warn" style="margin-top:14px">Le délai express fait passer votre commande devant les autres. '+
           'Il est confirmé par l\'atelier à la validation : si la charge du moment ne le permet pas, nous vous prévenons '+
           'immédiatement et le supplément n\'est pas dû.</div>';
    }
  }
  return h;
}
function opt3(d, sous){
  var sd = d.id==="express" ? supExpress(etat.piece) : 0;
  return '<button class="opt'+(etat.delai&&etat.delai.id===d.id?" sel":"")+'" type="button" data-delai="'+d.id+'">'+
    '<span class="rd"></span><span class="tx"><b>'+esc(d.nom)+'</b><span>'+esc(sous)+'</span></span>'+
    '<span class="pz">'+(sd? "+ "+fcfa(sd) : "Inclus")+'</span></button>';
}

/* --- étape 4 : coordonnées + récapitulatif --- */
function vue4(){
  var h = '<div class="stitle">Vos coordonnées</div>'+
    '<div class="sdesc">Pour vous confirmer la commande et vous prévenir dès que la tenue est prête.</div>'+
    '<div class="mes">'+
      '<div class="fd"><label for="f_prenom">Prénom</label><input id="f_prenom" type="text" value="'+esc(etat.prenom)+'" placeholder="Votre prénom"></div>'+
      '<div class="fd"><label for="f_nom">Nom</label><input id="f_nom" type="text" value="'+esc(etat.nom)+'" placeholder="Votre nom"></div>'+
      '<div class="fd"><label for="f_tel">Numéro WhatsApp</label><input id="f_tel" type="tel" inputmode="tel" value="'+esc(etat.tel)+'" placeholder="+229 01 …"></div>'+
      '<div class="fd"><label for="f_mail">Email <span style="font-weight:500;text-transform:none">(si vous n\'avez pas WhatsApp)</span></label><input id="f_mail" type="email" inputmode="email" value="'+esc(etat.mail)+'" placeholder="vous@gmail.com"></div>'+
      '<div class="fd full"><label for="f_note">Un mot pour l\'atelier ?</label><textarea id="f_note" placeholder="Optionnel">'+esc(etat.note)+'</textarea></div>'+
    '</div>'+
    '<div class="momo"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 10h6M9 14h6M12 7v10"/></svg>'+
    '<span><strong>Règlement par Mobile Money uniquement.</strong> Le numéro vous sera communiqué au message de confirmation. Aucun paiement ne se fait sur ce site.</span></div>'+
    recap()+
    '<div class="err" id="err"></div>';
  return h;
}

function recap(){
  var p = etat.piece;
  var lignes = [];
  lignes.push(["Pièce", p.nom]);
  if(p.cat==="pap" && etat.taille) lignes.push(["Taille", etat.taille]);
  if(p.cat==="sm" && etat.typeMesure){
    var jeu = MESURES[etat.typeMesure];
    var remplies = jeu.champs.filter(function(c){return etat.mesures[c.id];}).length;
    lignes.push(["Mesures", remplies+" / "+jeu.champs.length+" renseignées"]);
  }
  lignes.push(["Prix de la pièce", p.prix==null ? "Sur devis" : fcfa(p.prix)]);
  if(etat.mode==="retrait") lignes.push(["Retrait atelier","Gratuit"]);
  if(etat.mode==="expedition"){
    var f = fraisLivraison();
    lignes.push(["Expédition "+(etat.pays?etat.pays.nom:""), f===null ? "À confirmer" : fcfa(f)]);
  }
  if(etat.delai){
    var _s = etat.delai.id==="express" ? supExpress(etat.piece) : 0;
    lignes.push([etat.delai.nom, _s ? fcfa(_s) : "Inclus"]);
  }
  var j = joursTotal();
  if(j!=null) lignes.push(["Disponible le", dateFr(dateDispo(j))]);

  var t = totalCommande();
  return '<div class="recap">'+
    lignes.map(function(l){return '<div class="li"><span>'+esc(l[0])+'</span><span>'+esc(l[1])+'</span></div>';}).join("")+
    '<div class="tt"><span>Total</span><span>'+(t==null ? "Sur devis" : fcfa(t))+'</span></div></div>';
}

/* --- étape 5 : envoi --- */
function vue5(){
  return '<div class="fin">'+
    '<div class="ck"><svg viewBox="0 0 24 24"><path d="M4 12.5l5.5 5.5L20 7"/></svg></div>'+
    '<h3>Votre commande est prête à partir</h3>'+
    '<p>Le bouton ci-dessous ouvre WhatsApp avec votre commande déjà écrite : la pièce, vos mesures, '+
    'la livraison, le délai et le total. Vous n\'avez qu\'à appuyer sur envoyer.</p>'+
    recap()+
    '<a class="alt" id="altMail" href="#">Je n\'ai pas WhatsApp — envoyer par email</a>'+
    '</div>';
}

/* --- pied de modale --- */
function pied(){
  var e = etat.etape;
  if(e===5){
    return '<button class="bt g" type="button" data-nav="prec">Retour</button>'+
      '<a class="bt w" id="btWa" href="#" target="_blank" rel="noopener">'+
      '<svg viewBox="0 0 24 24" fill="#fff"><path d="M12 2a10 10 0 00-8.6 15L2 22l5.2-1.4A10 10 0 1012 2zm5.6 14.2c-.2.7-1.2 1.3-1.9 1.4-.5.1-1.1.2-3.2-.7-2.7-1.1-4.4-3.8-4.5-4-.1-.2-1.1-1.4-1.1-2.7s.7-1.9 1-2.2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.7 1.2 1.6 2 1.1.9 2 1.2 2.3 1.4.3.1.4.1.6-.1l.9-1c.2-.2.3-.2.6-.1l2 .9c.3.1.4.2.5.3.1.2.1.9-.1 1.6z"/></svg>'+
      'Envoyer sur WhatsApp</a>';
  }
  var libelle = e===4 ? "Vérifier ma commande" : "Continuer";
  return (e>1 ? '<button class="bt g" type="button" data-nav="prec">Retour</button>' : '')+
    '<button class="bt p" type="button" data-nav="suiv"'+(peutAvancer()?"":" disabled")+'>'+libelle+'</button>';
}

function peutAvancer(){
  var e = etat.etape, p = etat.piece;
  if(e===1){
    if(p.cat==="pap") return !!etat.taille;
    if(!etat.typeMesure) return false;
    var jeu = MESURES[etat.typeMesure];
    /* au moins la moitié des mesures : le reste se prend ensemble */
    var n = jeu.champs.filter(function(c){return etat.mesures[c.id];}).length;
    return n >= Math.ceil(jeu.champs.length/2);
  }
  if(e===2){
    if(etat.mode==="retrait") return true;
    if(etat.mode==="expedition") return !!etat.pays;
    return false;
  }
  if(e===3) return !!etat.delai;
  if(e===4) return !!(etat.prenom.trim() && (etat.tel.trim() || etat.mail.trim()));
  return true;
}

/* ---------- branchements ---------------------------------------- */
function brancher(){
  var bd = document.getElementById("shBd");

  $$(".taille", bd).forEach(function(b){
    b.addEventListener("click", function(){ etat.taille = b.dataset.taille; dessiner(); });
  });
  $$("[data-mode]", bd).forEach(function(b){
    b.addEventListener("click", function(){
      etat.mode = b.dataset.mode;
      if(etat.mode==="retrait"){ etat.pays = null; }
      dessiner();
    });
  });
  $$("[data-delai]", bd).forEach(function(b){
    b.addEventListener("click", function(){ etat.delai = DELAIS[b.dataset.delai]; dessiner(); });
  });
  $$("[data-mes]", bd).forEach(function(i){
    i.addEventListener("input", function(){
      var v = i.value.trim();
      if(v) etat.mesures[i.dataset.mes] = v; else delete etat.mesures[i.dataset.mes];
      majSuiv();
    });
  });

  var ty = document.getElementById("f_type");
  if(ty) ty.addEventListener("change", function(){ etat.typeMesure = ty.value||null; etat.mesures = {}; dessiner(); });

  var pa = document.getElementById("f_pays");
  if(pa) pa.addEventListener("change", function(){
    etat.pays = PAYS.filter(function(p){return p.id===pa.value;})[0] || null;
    dessiner();
  });

  lie("f_tissu","tissu"); lie("f_det","details"); lie("f_ville","ville");
  lie("f_prenom","prenom"); lie("f_nom","nom"); lie("f_tel","tel");
  lie("f_mail","mail"); lie("f_note","note");

  $$("[data-nav]", document.getElementById("shFt")).forEach(function(b){
    b.addEventListener("click", function(){
      if(b.dataset.nav==="prec"){
        etat.etape = Math.max(1, etat.etape-1);
      }else{
        if(!peutAvancer()) return;
        if(etat.etape===4){
          memorise({prenom:etat.prenom.trim(), nom:etat.nom.trim(), tel:etat.tel.trim(),
                    mail:etat.mail.trim(), ville:etat.ville.trim()});
        }
        etat.etape = Math.min(5, etat.etape+1);
      }
      dessiner();
    });
  });

  var wa = document.getElementById("btWa");
  if(wa) wa.href = "https://wa.me/"+WHATSAPP+"?text="+encodeURIComponent(message());
  /* le repli pour qui n'a pas WhatsApp : par email si la maison en a une,
     par téléphone sinon. Jamais un lien qui ne mène nulle part. */
  var al = document.getElementById("altMail");
  if(al){
    if(EMAIL){
      al.href = "mailto:"+EMAIL+"?subject="+encodeURIComponent("Commande — "+etat.piece.nom)+
                "&body="+encodeURIComponent(message());
      al.textContent = "Je n'ai pas WhatsApp — envoyer par email";
    } else {
      al.href = "tel:+"+WHATSAPP;
      al.textContent = "Je n'ai pas WhatsApp — appeler l'atelier";
    }
  }
}
function lie(id, cle){
  var el = document.getElementById(id);
  if(!el) return;
  el.addEventListener("input", function(){ etat[cle] = el.value; majSuiv(); });
}
function majSuiv(){
  var b = document.querySelector('[data-nav="suiv"]');
  if(b) b.disabled = !peutAvancer();
}

/* ---------- le message de commande ------------------------------ */
function message(){
  var p = etat.piece, L = [];
  L.push("*NOUVELLE COMMANDE — HILLARY M. STYL*");
  L.push("");
  L.push("*Pièce :* "+p.nom+" ("+(p.cat==="sm"?"sur-mesure":"prêt-à-porter")+")");
  L.push("*Prix :* "+(p.prix==null ? "sur devis" : fcfa(p.prix)));

  if(p.cat==="pap" && etat.taille) L.push("*Taille :* "+etat.taille);

  if(p.cat==="sm" && etat.typeMesure){
    var jeu = MESURES[etat.typeMesure];
    L.push("");
    L.push("*MESURES — "+jeu.nom+"*");
    if(jeu.aValider) L.push("_(liste de mesures à valider par l'atelier)_");
    var manquantes = [];
    jeu.champs.forEach(function(c){
      if(etat.mesures[c.id]) L.push("• "+c.l+" : "+etat.mesures[c.id]+" cm");
      else manquantes.push(c.l);
    });
    if(manquantes.length){
      L.push("");
      L.push("_À prendre ensemble ("+manquantes.length+") :_ "+manquantes.join(", "));
    }
    if(etat.tissu.trim())   L.push(""), L.push("*Tissu :* "+etat.tissu.trim());
  }
  if(etat.details.trim()){ L.push(""); L.push("*Modèle et détails :* "+etat.details.trim()); }

  L.push("");
  L.push("*LIVRAISON*");
  if(etat.mode==="retrait"){
    L.push("Retrait à l'atelier — gratuit");
  }else{
    var f = fraisLivraison();
    L.push("Expédition — "+(etat.pays?etat.pays.nom:"")+(etat.ville.trim()? ", "+etat.ville.trim() : ""));
    L.push("Frais : "+(f===null ? "à confirmer" : fcfa(f)));
  }
  if(etat.delai){
    L.push("");
    L.push("*DÉLAI*");
    var _se = etat.delai.id==="express" ? supExpress(etat.piece) : 0;
    L.push(etat.delai.nom+(_se? " (+ "+fcfa(_se)+")" : ""));
    var j = joursTotal();
    if(j!=null) L.push("Disponible au plus tard le "+dateFr(dateDispo(j)));
  }

  var t = totalCommande();
  L.push("");
  L.push("*TOTAL : "+(t==null ? "sur devis" : fcfa(t))+"*");
  L.push("_Règlement par Mobile Money._");

  L.push("");
  L.push("*CLIENT*");
  L.push((etat.prenom.trim()+" "+etat.nom.trim()).trim());
  if(etat.tel.trim())  L.push("WhatsApp : "+etat.tel.trim());
  if(etat.mail.trim()) L.push("Email : "+etat.mail.trim());
  if(etat.ville.trim())L.push("Ville : "+etat.ville.trim());
  if(etat.note.trim()){ L.push(""); L.push("*Note :* "+etat.note.trim()); }

  return L.join("\n");
}

/* ---------- remplissages simples -------------------------------- */
document.getElementById("an").textContent = new Date().getFullYear();
document.getElementById("adr").textContent  = ATELIER.adresse;
document.getElementById("hor").textContent  = ATELIER.horaires;
(function(){
  var m = document.getElementById("mail");
  if(!m) return;
  var ligne = m.closest(".coord");
  if(EMAIL){ m.innerHTML = '<a href="mailto:'+EMAIL+'">'+EMAIL+'</a>'; }
  else if(ligne){ ligne.remove(); }   /* pas d'adresse : pas de ligne */
})();
document.getElementById("waBas").href =
  "https://wa.me/"+WHATSAPP+"?text="+encodeURIComponent("Bonjour HILLARY M. STYL, j'ai une question avant de commander.");


/* ================================================================== */
