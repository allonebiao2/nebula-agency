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

  /* ── LES 11 MODELES RECUS LES 2026-08-16 ET 17 ──────────────────
     Poses au catalogue le 2026-08-18 sur demande de Mongazi, AVANT
     leurs photos : les pieces sont reelles, les prix sont les siens,
     la commande fonctionne. `photoWa:true` remplace la photo par
     « Photo sur WhatsApp », qui est vrai et actionnable.
     ⚠️ Elles n'entrent NI au heros NI au carrousel tant qu'elles
     n'ont pas d'image : un monogramme en pleine page ne montre rien.
     `python _nouveaux_modeles.py --poser` posera les photos et
     retirera ce drapeau. */
  {id:"h10", cat:"sm", nom:"Robe de ville organza", type:"robe_ovale", tag:"Cérémonie",
   img:"piece-organza.webp", img2:"piece-organza-dos.webp",
   prix:40000, jmin:14, jmax:14, expPrix:55000, expMin:2, expMax:4,
   eur:60, usd:72, eurExp:82, usdExp:100,
   ds:"Manches ballon détachées des épaules, col en organza froncé, découpe à la taille, dos lacé au ruban et jupon d'organza sous un wax rouge."},
  {id:"h11", cat:"sm", nom:"Ensemble Nœud", type:"haut_pantalon", tag:"",
   img:"piece-noeud.webp", img2:"piece-noeud-dos.webp",
   prix:25000, jmin:14, jmax:14, expPrix:35000, expMin:2, expMax:4,
   eur:37, usd:45, eurExp:52, usdExp:63,
   ds:"Haut dos nu à col, noué dans le dos, et pantalon large avec un pan de wax rouge et blanc."},
  {id:"h12", cat:"sm", nom:"Robe Lacée", type:"robe_ovale", tag:"",
   img:"piece-lacee.webp", img2:"piece-lacee-dos.webp",
   prix:35000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:52, usd:63, eurExp:67, usdExp:81,
   ds:"Épaules dénudées à fines bretelles, manches ballon, basque à la taille, dos lacé au ruban."},
  {id:"h13", cat:"sm", nom:"Tailleur Cœurs", type:"haut_pantalon", tag:"Fait main",
   img:"piece-coeurs.webp",
   prix:50000, jmin:14, jmax:14, expPrix:65000, expMin:2, expMax:4,
   eur:75, usd:90, eurExp:99, usdExp:115,
   ds:"Veste cintrée à revers et épaules structurées, pantalon large assorti, wax bordeaux à cœurs."},
  {id:"h14", cat:"sm", nom:"Ensemble Jean", type:"haut_jupe", tag:"",
   img:"piece-jean.webp", img2:"piece-jean-dos.webp",
   prix:35000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:52, usd:63, eurExp:67, usdExp:81,
   ds:"Haut court épaules dénudées à manches ballon, jupe longue à volants montée sur un empiècement en jean."},
  {id:"h15", cat:"sm", nom:"Robe Sirène", type:"robe_droite", tag:"Cérémonie",
   img:"piece-sirene.webp",
   prix:40000, jmin:14, jmax:14, expPrix:55000, expMin:2, expMax:4,
   eur:60, usd:72, eurExp:82, usdExp:100,
   ds:"Fourreau en wax violet, volants bleu roi en bordure et le long de la fente, traîne et foulard assorti."},
  {id:"h16", cat:"sm", nom:"Robe Émeraude", type:"haut_jupe", tag:"",
   img:"piece-emeraude.webp",
   prix:25000, jmin:14, jmax:14, expPrix:35000, expMin:2, expMax:4,
   eur:37, usd:45, eurExp:52, usdExp:63,
   ds:"Coupe courte ajustée, manches longues, grands motifs verts et jaunes cernés de noir."},
  {id:"h17", cat:"sm", nom:"Ensemble Orange", type:"haut_pantalon", tag:"",
   img:"piece-orange-uni.webp",
   prix:35000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:52, usd:63, eurExp:67, usdExp:81,
   ds:"Bustier froncé à lien au cou, découpes sur les côtés, bas long et très ample en tissu uni."},
  {id:"h18", cat:"sm", nom:"Robe Soleil", type:"robe_ovale", tag:"Cérémonie",
   img:"piece-soleil.webp",
   prix:25000, jmin:14, jmax:14, expPrix:35000, expMin:2, expMax:4,
   eur:37, usd:45, eurExp:52, usdExp:63,
   ds:"Épaules drapées à cordons et pompons, ceinture drapée, jupe très ample en bazin teint rouge et or."},
  {id:"h19", cat:"sm", nom:"Robe d'été", type:"robe_ovale", tag:"Plage", photoWa:true,
   prix:35000, jmin:14, jmax:14, expPrix:45000, expMin:2, expMax:4,
   eur:52, usd:63, eurExp:67, usdExp:81,
   ds:"Haut court noué au cou et jupe longue très ample, en bazin teint. La pièce d'été, qui va de la plage au déjeuner."},
  {id:"h20", cat:"sm", nom:"Ensemble Volants", type:"haut_pantalon", tag:"", photoWa:true,
   prix:40000, jmin:14, jmax:14, expPrix:55000, expMin:2, expMax:4,
   eur:60, usd:72, eurExp:82, usdExp:100,
   ds:"Haut court noué devant, manches à trois volants étagés, et pantalon très évasé en jean à empiècements de bazin teint."},

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
  /* Une pièce photographiée des DEUX CÔTÉS montre ses deux vues, l'une
     après l'autre, pendant qu'on la regarde. Voir duoPoser().
     ⚠️ Un seul `alt`, sur la première : la carte est un <button>, chaque
     `alt` s'ajoute à son nom lu à voix haute. Deux vues, une phrase. */
  var duo = !!(p.img && p.img2);
  return '<button class="piece" type="button" data-id="'+p.id+'">'+
    '<div class="ph'+(duo?" duo":"")+'">'+(p.tag?'<span class="tag">'+esc(p.tag)+'</span>':'')+
      (p.img
        ? '<img class="v1" src="assets/images/'+esc(p.img)+'" alt="'+esc(p.nom)+
          ', création Hillary M. Styl'+(duo?", vue de face et de dos":"")+'" loading="lazy" decoding="async">'+
          (duo
            ? '<img class="v2" src="assets/images/'+esc(p.img2)+'" alt="" loading="lazy" decoding="async">'+
              '<span class="vues" aria-hidden="true"><i></i><i></i></span>'
            : '')
        /* ⚠️ PAS de « photo à venir » sur un site en ligne : un texte
           d'attente dit au client que la maison n'est pas prête. Cette carte
           est la « Création libre » — elle n'a pas de photo parce qu'elle n'a
           pas de modèle, et c'est ça qu'il faut écrire. */
        : '<div class="mark"></div><span class="avenir">'+
          (p.photoWa ? 'Photo sur WhatsApp' : 'Votre modèle')+'</span>')+
      '<span class="voile"><span>Commander</span></span></div>'+
    '<div class="bd">'+
      '<h3>'+esc(p.nom)+'</h3>'+
      '<p class="ds">'+esc(p.ds)+'</p>'+
      '<div class="meta"><span class="pr">'+prix+dev+'</span>'+
        '<span class="del">'+HORLOGE+'<span>'+libDelai(p.jmin, p.jmax)+'</span></span></div>'+
    '</div></button>';
}
/* ---------- les pièces à DEUX VUES : la face et le dos -------------
   Hillary envoie certaines pièces en double : une photo de face, une de
   dos. La carte les montre l'une après l'autre, toute seule, pendant
   qu'on la regarde.

   ⚠️ Trois choses qu'on n'a pas le droit d'oublier :
     · hors de l'écran, une carte ne tourne pas. Un observateur ouvre et
       ferme le robinet ; le battement s'arrête quand plus rien n'est vu.
     · onglet en arrière-plan ou écran de commande ouvert : on ne bascule
       pas ET on repousse l'échéance. Sans ce report, toutes les cartes
       rattrapent leur retard d'un coup au retour et basculent ensemble.
     · le va-et-vient est DÉCALÉ d'une carte à l'autre. Synchrones, les
       cartes du catalogue clignoteraient ensemble comme une panne.

   La PREMIÈRE bascule vient vite (1,6 s) : c'est elle qui apprend à la
   cliente que la pièce a un dos. Les suivantes prennent leur temps.
   `prefers-reduced-motion` : rien ne tourne, et le dos reste visible dans
   la fiche de commande (figure « Le dos »). */
var DUO_PREMIER = 1600, DUO_PAS = 3600;
var duoDoux = matchMedia("(prefers-reduced-motion: reduce)").matches;
var duoIO = null, duoVus = [], duoBat = null;

function duoTour(){
  var t = Date.now();
  if(document.hidden || document.body.classList.contains("ecran-on")){
    duoVus.forEach(function(el, i){ el.dataset.duoT = t + DUO_PAS + i*450; });
    return;
  }
  duoVus.forEach(function(el){
    if(t < (+el.dataset.duoT || 0)) return;
    /* ⚠️ ON NE BASCULE JAMAIS VERS UNE IMAGE PAS ENCORE ARRIVÉE. La seconde
       vue est en `lazy` : sur une 4G lente elle peut n'être là qu'après la
       première bascule. On révélerait alors du VIDE pendant 3,6 s, et la
       carte semblerait cassée. Tant qu'elle n'est pas peinte, on attend. */
    var v2 = el.querySelector(".v2");
    if(!el.classList.contains("dos") && v2 && !v2.complete){
      el.dataset.duoT = t + 900;
      return;
    }
    el.dataset.duoT = t + DUO_PAS;
    el.classList.toggle("dos");
  });
}
function duoVeiller(){
  if(duoVus.length && !duoBat) duoBat = setInterval(duoTour, 300);
  else if(!duoVus.length && duoBat){ clearInterval(duoBat); duoBat = null; }
}
function duoPoser(){
  /* rendreGrille() refait tout le HTML : les anciennes cartes n'existent
     plus. On repart d'un observateur neuf, jamais on n'en empile deux. */
  if(duoIO){ duoIO.disconnect(); duoIO = null; }
  duoVus.length = 0;
  if(duoDoux){ duoVeiller(); return; }
  var l = $$("#grille .ph.duo");
  if(!l.length){ duoVeiller(); return; }
  if(!window.IntersectionObserver){            /* repli : tout tourne */
    l.forEach(function(el, i){ el.dataset.duoT = Date.now() + DUO_PREMIER + i*900; duoVus.push(el); });
    duoVeiller(); return;
  }
  duoIO = new IntersectionObserver(function(ents){
    ents.forEach(function(e){
      var i = duoVus.indexOf(e.target);
      if(e.isIntersecting){
        if(i < 0){
          e.target.dataset.duoT = Date.now() + DUO_PREMIER + (duoVus.length % 3)*700;
          duoVus.push(e.target);
        }
      }else if(i >= 0){ duoVus.splice(i, 1); }
    });
    duoVeiller();
  }, {threshold:0.4});
  l.forEach(function(el){ duoIO.observe(el); });
}

function rendreGrille(cat){
  var g = document.getElementById("grille");
  g.innerHTML = PIECES.filter(function(p){return p.cat===cat;}).map(carte).join("");
  duoPoser();
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

/* ==================================================================
   LE PANIER ET LA COMMANDE
   ==================================================================
   Refait le 2026-08-16, demandé par Mongazi : « un panier comme pour
   madame Luxury, histoire que les clientes voient ce qu'elles
   commandent et les prix ».

   Avant, une cliente qui voulait deux robes envoyait deux messages
   WhatsApp. L'atelier recevait deux commandes sans savoir qu'elles
   allaient ensemble : même cliente, une seule livraison, un seul
   règlement. Maintenant : on configure chaque pièce, elle tombe dans
   le panier, et une seule commande part.

   ⚠️ AUCUN PRIX N'EST STOCKÉ DANS LE PANIER. On garde l'identifiant de
   la pièce et les choix de la cliente ; le prix est relu dans PIECES à
   chaque affichage. Un panier oublié une semaine dans le navigateur ne
   peut donc pas ressortir avec un prix périmé.

   ⚠️ LE DÉLAI D'UNE COMMANDE EST CELUI DE SA PIÈCE LA PLUS LENTE. Tout
   part ensemble. Annoncer la pièce la plus rapide fabriquerait une
   cliente déçue, exactement comme annoncer la borne basse d'un délai.
   ================================================================== */

function pieceDe(id){
  return PIECES.filter(function(x){ return x.id === id; })[0] || null;
}

var PKEY  = "hms:panier";
var panier = [];
try{
  var _lu = JSON.parse(localStorage.getItem(PKEY));
  /* on jette les lignes dont la pièce n'existe plus au catalogue */
  if(_lu && _lu.length) panier = _lu.filter(function(l){ return !!pieceDe(l.id); });
}catch(e){ panier = []; }

function sauvePanier(){
  try{ localStorage.setItem(PKEY, JSON.stringify(panier)); }catch(e){}
}

/* ---------- prix et totaux -------------------------------------- */
function prixUnite(l){
  var p = pieceDe(l.id);
  if(!p || p.prix == null) return null;                 /* sur devis */
  return (l.express && p.expPrix != null) ? p.expPrix : p.prix;
}
function prixLigne(l){
  var u = prixUnite(l);
  return u == null ? null : u * l.qte;
}
/* ses prix en euros et en dollars, tels qu'elle les donne, jamais recalculés */
function deviseUnite(l, cle){
  var p = pieceDe(l.id);
  if(!p) return null;
  var v = l.express ? p[cle + "Exp"] : p[cle];
  return v == null ? null : v;
}
function totaux(){
  var t = {fcfa:0, eur:0, usd:0, devis:false, eurOk:true, usdOk:true, articles:0};
  panier.forEach(function(l){
    t.articles += l.qte;
    var v = prixLigne(l);
    if(v == null) t.devis = true; else t.fcfa += v;
    var e = deviseUnite(l, "eur"); if(e == null) t.eurOk = false; else t.eur += e * l.qte;
    var u = deviseUnite(l, "usd"); if(u == null) t.usdOk = false; else t.usd += u * l.qte;
  });
  return t;
}

var cmd = {
  actif:false, etape:1, mode:null, pays:null, ville:"",
  prenom:"", nom:"", tel:"", mail:"", note:""
};

function fraisLivraison(){
  if(cmd.mode !== "expedition" || !cmd.pays) return 0;
  return cmd.pays.frais == null ? null : cmd.pays.frais;   /* null = tarif au cas par cas */
}
function joursAcheminement(){
  if(cmd.mode !== "expedition" || !cmd.pays) return 0;
  return cmd.pays.achem || 0;
}
function totalCommande(){
  var t = totaux();
  if(t.devis) return null;
  var f = fraisLivraison();
  if(f === null) return null;
  return t.fcfa + f;
}
/* la borne HAUTE de la pièce la plus lente */
function joursConfection(){
  var j = 0;
  panier.forEach(function(l){
    var p = pieceDe(l.id); if(!p) return;
    var v = l.express
      ? (p.expMax != null ? p.expMax : DELAIS.express.jmax)
      : Math.max(p.jmax != null ? p.jmax : DELAIS.normal.jmax, DELAIS.normal.jmin);
    if(v > j) j = v;
  });
  return j;
}
function joursTotal(){
  if(!panier.length) return null;
  return joursConfection() + joursAcheminement();
}
/* vrai quand la commande mélange une pièce pressée et une pièce normale :
   la cliente doit savoir que tout part à la date la plus tardive */
function melangeDelais(){
  var e = false, n = false;
  panier.forEach(function(l){ if(l.express) e = true; else n = true; });
  return e && n;
}

/* ---------- ce qui décrit une ligne, en mots -------------------- */
function libLigne(l){
  var p = pieceDe(l.id), out = [];
  if(!p) return "";
  out.push(p.cat === "sm" ? "Sur-mesure" : "Prêt-à-porter");
  if(l.taille) out.push("Taille " + l.taille);
  if(p.cat === "sm" && l.typeMesure && MESURES[l.typeMesure]){
    var jeu = MESURES[l.typeMesure];
    var n = jeu.champs.filter(function(c){ return l.mesures[c.id]; }).length;
    out.push(n + " / " + jeu.champs.length + " mesures");
  }
  return out.join(" · ");
}
function libDelaiLigne(l){
  var p = pieceDe(l.id);
  if(!p) return "";
  if(l.express){
    return "Express, " + libDelai(p.expMin != null ? p.expMin : DELAIS.express.jmin,
                                  p.expMax != null ? p.expMax : DELAIS.express.jmax);
  }
  return "Confection en " + libDelai(p.jmin, p.jmax);
}

/* ==================================================================
   LA FICHE D'UNE PIÈCE — deux étapes, puis le panier
   ================================================================== */
var etat = null;

function ouvrir(id, cle){
  var p = pieceDe(id);
  if(!p) return;
  var ligne = cle ? panier.filter(function(x){ return x.cle === cle; })[0] : null;
  etat = {
    piece: p,
    etape: 1,
    cle: ligne ? ligne.cle : null,          /* on modifie une ligne existante */
    taille: ligne ? ligne.taille : null,
    typeMesure: ligne ? ligne.typeMesure : (p.type || null),
    mesures: ligne ? JSON.parse(JSON.stringify(ligne.mesures || {})) : mesuresConnues(p.type),
    tissu: ligne ? ligne.tissu : "",
    details: ligne ? ligne.details : "",
    express: ligne ? !!ligne.express : null,
    qte: ligne ? ligne.qte : 1
  };
  cmd.actif = false;
  document.getElementById("shTitre").textContent = p.nom;
  document.getElementById("shSub").textContent =
    (p.cat === "sm" ? "Sur-mesure" : "Prêt-à-porter") + " · " +
    (p.prix == null ? "sur devis" : fcfa(p.prix));
  montrerModale();
  dessiner();
}

/* Une cliente qui commande deux vêtements du même type ne va pas
   remesurer son tour de taille. On reprend ce qu'elle a déjà donné,
   champ par champ, et elle corrige si besoin. */
function mesuresConnues(type){
  var out = {};
  if(!type || !MESURES[type]) return out;
  var champs = MESURES[type].champs.map(function(c){ return c.id; });
  panier.forEach(function(l){
    Object.keys(l.mesures || {}).forEach(function(k){
      if(champs.indexOf(k) >= 0 && !out[k]) out[k] = l.mesures[k];
    });
  });
  return out;
}

function montrerModale(){
  /* le tiroir et la fiche ne se superposent jamais : le tiroir est au-dessus
     dans l'ordre d'empilement, il masquerait la fiche */
  fermerPanier();
  document.getElementById("ov").classList.add("on");
  document.body.style.overflow = "hidden";
  parDessus(true);
}
/* ⚠️ Le bouton du son est en `position:fixed`, en bas à gauche. Il se posait
   sur « Retour » dans la fiche et sur « Vider le panier » dans le tiroir : un
   élément flottant finit toujours par recouvrir quelque chose. On l'efface
   pendant qu'un écran de commande est ouvert. */
function parDessus(on){
  document.body.classList.toggle("ecran-on", !!on);
  /* ⚠️ LE BOUTON DU SON CHANGE DE PARENT, PAS SEULEMENT DE STYLE.
     Il vit désormais dans la barre du haut, qui porte `z-index:50` et crée
     donc un CONTEXTE D'EMPILEMENT : depuis l'intérieur, il ne peut pas
     passer au-dessus de la fiche (z-index 120), quelle que soit la valeur
     qu'on lui écrive. Un `z-index:130` sur un enfant d'un parent à 50 vaut
     50. On le sort donc de la barre le temps de la commande — la maison
     exige qu'on puisse couper le son en donnant ses mesures — et on l'y
     remet en refermant. Déplacer un nœud ne perd pas ses écouteurs. */
  var bt = document.querySelector(".sonbt");
  if(!bt) return;
  if(on){
    document.body.appendChild(bt);
  }else{
    var barre = document.querySelector(".nav-d");
    if(barre) barre.insertBefore(bt, barre.firstChild);
  }
}
function fermer(){
  document.getElementById("ov").classList.remove("on");
  document.body.style.overflow = "";
  etat = null; cmd.actif = false;
  parDessus(false);
}

document.getElementById("grille").addEventListener("click", function(e){
  var b = e.target.closest ? e.target.closest(".piece") : null;
  if(b) ouvrir(b.dataset.id);
});
document.getElementById("btX").addEventListener("click", fermer);
document.getElementById("ov").addEventListener("click", function(e){ if(e.target === this) fermer(); });
document.addEventListener("keydown", function(e){
  if(e.key !== "Escape") return;
  if(etat || cmd.actif) fermer();
  else if(panOuvert()) fermerPanier();
});

/* ---------- le rendu de la modale ------------------------------- */
function nbEtapes(){ return cmd.actif ? 3 : 2; }
function etapeCourante(){ return cmd.actif ? cmd.etape : (etat ? etat.etape : 1); }

function dessiner(){
  if(!etat && !cmd.actif) return;
  var prog = document.getElementById("prog");
  var n = nbEtapes(), e = etapeCourante();
  prog.innerHTML = new Array(n + 1).join("<i></i>");
  $$("#prog i").forEach(function(i, k){ i.classList.toggle("on", k < e); });

  var bd = document.getElementById("shBd");
  var ft = document.getElementById("shFt");

  if(cmd.actif){
    bd.innerHTML = e === 1 ? vueLivraison() : (e === 2 ? vueCoord() : vueEnvoi());
  }else{
    bd.innerHTML = e === 1 ? vueMesures() : vueDelai();
  }
  ft.innerHTML = pied();
  brancher();
  var sh = document.querySelector(".sheet");
  if(sh) sh.scrollTop = 0;
  document.getElementById("ov").scrollTop = 0;
}

/* --- pièce, étape 1 : taille ou mesures --- */
function vueMesures(){
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

/* --- pièce, étape 2 : le délai propre à la pièce --- */
function vueDelai(){
  var p = etat.piece;
  var h = '<div class="stitle">Quand la voulez-vous ?</div>'+
    '<div class="sdesc">Cette pièce demande normalement '+libDelai(p.jmin, p.jmax)+' de confection. '+
    'Le délai se choisit pièce par pièce : c\'est le prix de l\'express qui change d\'une pièce à l\'autre.</div>'+
    '<div class="opts">'+
      optDelai(false, "Confection en "+libDelai(p.jmin, p.jmax), p)+
      optDelai(true, "Votre tenue en "+libDelai(p.expMin != null ? p.expMin : DELAIS.express.jmin,
                                                p.expMax != null ? p.expMax : DELAIS.express.jmax)+" maximum", p)+
    '</div>';

  if(etat.express !== null){
    var u = prixUnite({id:p.id, express:etat.express, qte:1});
    h += '<div class="recap" style="margin-top:18px">'+
      '<div class="li"><span>'+esc(p.nom)+'</span><span>'+(u==null?"Sur devis":fcfa(u))+'</span></div>'+
      '<div class="li"><span>Quantité</span><span>'+
        '<button class="qbt" type="button" data-qte="-1" aria-label="Retirer un exemplaire">−</button>'+
        '<b class="qn">'+etat.qte+'</b>'+
        '<button class="qbt" type="button" data-qte="1" aria-label="Ajouter un exemplaire">+</button>'+
      '</span></div>'+
      '<div class="tt"><span>Cette pièce</span><span>'+(u==null?"Sur devis":fcfa(u*etat.qte))+'</span></div></div>';
    if(etat.express){
      h += '<div class="warn" style="margin-top:14px">Le délai express fait passer votre commande devant les autres. '+
           'Il est confirmé par l\'atelier à la validation : si la charge du moment ne le permet pas, nous vous prévenons '+
           'immédiatement et le supplément n\'est pas dû.</div>';
    }
  }
  return h;
}
function optDelai(ex, sous, p){
  var sup = ex ? supExpress(p) : 0;
  var nom = ex ? DELAIS.express.nom : DELAIS.normal.nom;
  return '<button class="opt'+(etat.express===ex?" sel":"")+'" type="button" data-exp="'+(ex?"1":"0")+'">'+
    '<span class="rd"></span><span class="tx"><b>'+esc(nom)+'</b><span>'+esc(sous)+'</span></span>'+
    '<span class="pz">'+(sup ? "+ "+fcfa(sup) : "Inclus")+'</span></button>';
}

/* ==================================================================
   LA COMMANDE — livraison, coordonnées, envoi
   ================================================================== */
function ouvrirCommande(){
  if(!panier.length) return;
  var m = memoire();
  cmd.actif = true; cmd.etape = 1;
  cmd.prenom = cmd.prenom || m.prenom || "";
  cmd.nom    = cmd.nom    || m.nom    || "";
  cmd.tel    = cmd.tel    || m.tel    || "";
  cmd.mail   = cmd.mail   || m.mail   || "";
  cmd.ville  = cmd.ville  || m.ville  || "";
  etat = null;
  fermerPanier();
  var t = totaux();
  document.getElementById("shTitre").textContent = "Votre commande";
  document.getElementById("shSub").textContent =
    t.articles + (t.articles > 1 ? " pièces" : " pièce") + " · " + (t.devis ? "sur devis" : fcfa(t.fcfa));
  montrerModale();
  dessiner();
}

function vueLivraison(){
  var h = '<div class="stitle">Comment la recevoir ?</div>'+
    '<div class="sdesc">Retrait à l\'atelier ou expédition. Une seule livraison pour toute la commande.</div>'+
    '<div class="opts">'+
      '<button class="opt'+(cmd.mode==="retrait"?" sel":"")+'" type="button" data-mode="retrait">'+
        '<span class="rd"></span><span class="tx"><b>Retrait à l\'atelier</b>'+
        '<span>'+esc(ATELIER.adresse)+' · essayage et retouche sur place</span></span>'+
        '<span class="pz">Gratuit</span></button>'+
      '<button class="opt'+(cmd.mode==="expedition"?" sel":"")+'" type="button" data-mode="expedition">'+
        '<span class="rd"></span><span class="tx"><b>Expédition</b>'+
        '<span>Nous envoyons la tenue chez vous</span></span>'+
        '<span class="pz">Selon pays</span></button>'+
    '</div>';

  if(cmd.mode === "expedition"){
    h += '<div class="fd" style="margin-top:16px"><label for="f_pays">Votre pays</label><select id="f_pays">'+
      '<option value="">— Choisir votre pays —</option>'+
      PAYS.map(function(p){
        return '<option value="'+p.id+'"'+(cmd.pays&&cmd.pays.id===p.id?" selected":"")+'>'+esc(p.nom)+
          (p.frais==null? " (frais à confirmer)" : " — "+fcfa(p.frais))+'</option>';
      }).join("")+'</select></div>';
    if(cmd.pays && cmd.pays.frais === null){
      h += '<div class="warn" style="margin-top:14px">Nous n\'expédions pas encore automatiquement vers ce pays. '+
           'Envoyez-nous quand même la commande : nous vous donnerons le tarif exact avant tout règlement.</div>';
    }
    h += '<div class="fd" style="margin-top:12px"><label for="f_ville">Ville de livraison</label>'+
         '<input id="f_ville" type="text" placeholder="Cotonou, Abidjan, Dakar…" value="'+esc(cmd.ville)+'"></div>';
  }
  if(cmd.mode === "retrait"){
    h += '<div class="momo" style="margin-top:16px"><svg viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>'+
         '<span><strong>'+esc(ATELIER.adresse)+'</strong><br>'+esc(ATELIER.horaires)+'</span></div>';
  }

  var j = joursTotal();
  if(j != null && cmd.mode){
    var mot = cmd.mode === "expedition" ? "Chez vous au plus tard le" : "Prête à retirer au plus tard le";
    var det = cmd.mode === "expedition" && joursAcheminement()
      ? "Confection incluse, plus "+joursAcheminement()+" jour"+(joursAcheminement()>1?"s":"")+" d'acheminement vers "+esc(cmd.pays?cmd.pays.nom:"")+"."
      : "Vous pouvez venir l'essayer à l'atelier ce jour-là.";
    h += '<div class="dispo"><svg viewBox="0 0 24 24"><path d="M4.5 5.5h15v14h-15z"/><path d="M4.5 10h15M8.5 3v4M15.5 3v4"/><path d="M9 15l2 2 4-4"/></svg>'+
      '<div><b>'+mot+'</b><p>'+dateFr(dateDispo(j))+'</p><small>'+det+'</small></div></div>';
    if(panier.length > 1){
      h += '<div class="warn" style="margin-top:14px">Cette date est celle de la pièce la plus longue à confectionner : '+
           'toute la commande part ensemble.'+
           (melangeDelais() ? ' Vous avez une pièce en express et une en délai normal : dites-le nous si vous préférez deux envois séparés.' : '')+
           '</div>';
    }
  }
  return h;
}

function vueCoord(){
  return '<div class="stitle">Vos coordonnées</div>'+
    '<div class="sdesc">Pour vous confirmer la commande et vous prévenir dès que la tenue est prête.</div>'+
    '<div class="mes">'+
      '<div class="fd"><label for="f_prenom">Prénom</label><input id="f_prenom" type="text" value="'+esc(cmd.prenom)+'" placeholder="Votre prénom"></div>'+
      '<div class="fd"><label for="f_nom">Nom</label><input id="f_nom" type="text" value="'+esc(cmd.nom)+'" placeholder="Votre nom"></div>'+
      '<div class="fd"><label for="f_tel">Numéro WhatsApp</label><input id="f_tel" type="tel" inputmode="tel" value="'+esc(cmd.tel)+'" placeholder="+229 01 …"></div>'+
      '<div class="fd"><label for="f_mail">Email <span style="font-weight:500;text-transform:none">(si vous n\'avez pas WhatsApp)</span></label><input id="f_mail" type="email" inputmode="email" value="'+esc(cmd.mail)+'" placeholder="vous@gmail.com"></div>'+
      '<div class="fd full"><label for="f_note">Un mot pour l\'atelier ?</label><textarea id="f_note" placeholder="Optionnel">'+esc(cmd.note)+'</textarea></div>'+
    '</div>'+
    '<div class="momo"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 10h6M9 14h6M12 7v10"/></svg>'+
    '<span><strong>Règlement par Mobile Money uniquement.</strong> Le numéro vous sera communiqué au message de confirmation. Aucun paiement ne se fait sur ce site.</span></div>'+
    recapCommande()+
    '<div class="err" id="err"></div>';
}

function vueEnvoi(){
  return '<div class="fin">'+
    '<div class="ck"><svg viewBox="0 0 24 24"><path d="M4 12.5l5.5 5.5L20 7"/></svg></div>'+
    '<h3>Votre commande est prête à partir</h3>'+
    '<p>Le bouton ci-dessous ouvre WhatsApp avec votre commande déjà écrite : chaque pièce, vos mesures, '+
    'la livraison, le délai et le total. Vous n\'avez qu\'à appuyer sur envoyer.</p>'+
    recapCommande()+
    '<a class="alt" id="altMail" href="#">Je n\'ai pas WhatsApp — envoyer par email</a>'+
    '</div>';
}

/* le récapitulatif : chaque pièce, puis la livraison, puis le total */
function recapCommande(){
  var h = '<div class="recap">';
  panier.forEach(function(l){
    var p = pieceDe(l.id); if(!p) return;
    var v = prixLigne(l);
    h += '<div class="li"><span>'+esc(p.nom)+(l.qte>1?' × '+l.qte:'')+
         '<em>'+esc(libLigne(l))+' · '+esc(libDelaiLigne(l))+'</em></span>'+
         '<span>'+(v==null?"Sur devis":fcfa(v))+'</span></div>';
  });
  if(cmd.mode === "retrait") h += '<div class="li"><span>Retrait à l\'atelier</span><span>Gratuit</span></div>';
  if(cmd.mode === "expedition"){
    var f = fraisLivraison();
    h += '<div class="li"><span>Expédition '+esc(cmd.pays?cmd.pays.nom:"")+'</span><span>'+
         (f === null ? "À confirmer" : fcfa(f))+'</span></div>';
  }
  var j = joursTotal();
  if(j != null && cmd.mode) h += '<div class="li"><span>Disponible le</span><span>'+dateFr(dateDispo(j))+'</span></div>';

  var t = totalCommande();
  h += '<div class="tt"><span>Total</span><span>'+(t==null?"Sur devis":fcfa(t))+'</span></div>';
  var d = totaux();
  if(!d.devis && (d.eurOk || d.usdOk)){
    var dev = [];
    if(d.eurOk) dev.push(d.eur+" €");
    if(d.usdOk) dev.push(d.usd+" $");
    h += '<div class="li dev"><span>Les pièces, en devises</span><span>'+dev.join(" · ")+'</span></div>';
  }
  return h + '</div>';
}

/* ---------- pied de modale -------------------------------------- */
function pied(){
  var e = etapeCourante();
  if(cmd.actif){
    if(e === 3){
      return '<button class="bt g" type="button" data-nav="prec">Retour</button>'+
        '<a class="bt w" id="btWa" href="#" target="_blank" rel="noopener">'+
        '<svg viewBox="0 0 24 24" fill="#fff"><path d="M12 2a10 10 0 00-8.6 15L2 22l5.2-1.4A10 10 0 1012 2zm5.6 14.2c-.2.7-1.2 1.3-1.9 1.4-.5.1-1.1.2-3.2-.7-2.7-1.1-4.4-3.8-4.5-4-.1-.2-1.1-1.4-1.1-2.7s.7-1.9 1-2.2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.7 1.2 1.6 2 1.1.9 2 1.2 2.3 1.4.3.1.4.1.6-.1l.9-1c.2-.2.3-.2.6-.1l2 .9c.3.1.4.2.5.3.1.2.1.9-.1 1.6z"/></svg>'+
        'Envoyer sur WhatsApp</a>';
    }
    return '<button class="bt g" type="button" data-nav="prec">'+(e===1?"Au panier":"Retour")+'</button>'+
      '<button class="bt p" type="button" data-nav="suiv"'+(peutAvancer()?"":" disabled")+'>'+
      (e===2?"Vérifier ma commande":"Continuer")+'</button>';
  }
  var libelle = etat.etape === 2 ? (etat.cle ? "Mettre à jour le panier" : "Ajouter au panier") : "Continuer";
  return (etat.etape > 1 ? '<button class="bt g" type="button" data-nav="prec">Retour</button>' : '')+
    '<button class="bt p" type="button" data-nav="suiv"'+(peutAvancer()?"":" disabled")+'>'+libelle+'</button>';
}

function peutAvancer(){
  if(cmd.actif){
    if(cmd.etape === 1){
      if(cmd.mode === "retrait") return true;
      if(cmd.mode === "expedition") return !!cmd.pays;
      return false;
    }
    if(cmd.etape === 2) return !!(cmd.prenom.trim() && (cmd.tel.trim() || cmd.mail.trim()));
    return true;
  }
  var p = etat.piece;
  if(etat.etape === 1){
    if(p.cat === "pap") return !!etat.taille;
    if(!etat.typeMesure) return false;
    var jeu = MESURES[etat.typeMesure];
    /* au moins la moitié des mesures : le reste se prend ensemble */
    var n = jeu.champs.filter(function(c){ return etat.mesures[c.id]; }).length;
    return n >= Math.ceil(jeu.champs.length / 2);
  }
  return etat.express !== null;
}

/* ---------- branchements ---------------------------------------- */
function brancher(){
  var bd = document.getElementById("shBd");

  $$(".taille", bd).forEach(function(b){
    b.addEventListener("click", function(){ etat.taille = b.dataset.taille; dessiner(); });
  });
  $$("[data-mode]", bd).forEach(function(b){
    b.addEventListener("click", function(){
      cmd.mode = b.dataset.mode;
      if(cmd.mode === "retrait") cmd.pays = null;
      dessiner();
    });
  });
  $$("[data-exp]", bd).forEach(function(b){
    b.addEventListener("click", function(){ etat.express = b.dataset.exp === "1"; dessiner(); });
  });
  $$("[data-qte]", bd).forEach(function(b){
    b.addEventListener("click", function(){
      etat.qte = Math.max(1, Math.min(10, etat.qte + Number(b.dataset.qte)));
      dessiner();
    });
  });
  $$("[data-mes]", bd).forEach(function(i){
    i.addEventListener("input", function(){
      var v = i.value.trim();
      if(v) etat.mesures[i.dataset.mes] = v; else delete etat.mesures[i.dataset.mes];
      majSuiv();
    });
  });

  var ty = document.getElementById("f_type");
  if(ty) ty.addEventListener("change", function(){
    etat.typeMesure = ty.value || null;
    etat.mesures = mesuresConnues(etat.typeMesure);
    dessiner();
  });

  var pa = document.getElementById("f_pays");
  if(pa) pa.addEventListener("change", function(){
    cmd.pays = PAYS.filter(function(p){ return p.id === pa.value; })[0] || null;
    dessiner();
  });

  lieEtat("f_tissu","tissu"); lieEtat("f_det","details");
  lieCmd("f_ville","ville"); lieCmd("f_prenom","prenom"); lieCmd("f_nom","nom");
  lieCmd("f_tel","tel"); lieCmd("f_mail","mail"); lieCmd("f_note","note");

  $$("[data-nav]", document.getElementById("shFt")).forEach(function(b){
    b.addEventListener("click", function(){
      if(b.dataset.nav === "prec"){
        if(cmd.actif){
          if(cmd.etape === 1){ fermer(); ouvrirPanier(); return; }
          cmd.etape--;
        }else{
          etat.etape = Math.max(1, etat.etape - 1);
        }
      }else{
        if(!peutAvancer()) return;
        if(cmd.actif){
          if(cmd.etape === 2){
            memorise({prenom:cmd.prenom.trim(), nom:cmd.nom.trim(), tel:cmd.tel.trim(),
                      mail:cmd.mail.trim(), ville:cmd.ville.trim()});
          }
          cmd.etape = Math.min(3, cmd.etape + 1);
        }else{
          if(etat.etape === 2){ validerPiece(); return; }
          etat.etape = 2;
        }
      }
      dessiner();
    });
  });

  var wa = document.getElementById("btWa");
  if(wa) wa.href = "https://wa.me/"+WHATSAPP+"?text="+encodeURIComponent(message());
  var al = document.getElementById("altMail");
  if(al){
    if(EMAIL){
      al.href = "mailto:"+EMAIL+"?subject="+encodeURIComponent("Commande — HILLARY M. STYL")+
                "&body="+encodeURIComponent(message());
      al.textContent = "Je n'ai pas WhatsApp — envoyer par email";
    }else{
      al.href = "tel:+"+WHATSAPP;
      al.textContent = "Je n'ai pas WhatsApp — appeler l'atelier";
    }
  }
}
function lieEtat(id, cle){
  var el = document.getElementById(id);
  if(!el) return;
  el.addEventListener("input", function(){ etat[cle] = el.value; majSuiv(); });
}
function lieCmd(id, cle){
  var el = document.getElementById(id);
  if(!el) return;
  el.addEventListener("input", function(){ cmd[cle] = el.value; majSuiv(); });
}
function majSuiv(){
  var b = document.querySelector('[data-nav="suiv"]');
  if(b) b.disabled = !peutAvancer();
}

/* ---------- la pièce tombe dans le panier ----------------------- */
function validerPiece(){
  var l = {
    cle: etat.cle || (etat.piece.id + "-" + Date.now()),
    id: etat.piece.id,
    taille: etat.taille,
    typeMesure: etat.typeMesure,
    mesures: etat.mesures,
    tissu: etat.tissu,
    details: etat.details,
    express: !!etat.express,
    qte: etat.qte
  };
  var i = -1;
  panier.forEach(function(x, k){ if(x.cle === l.cle) i = k; });
  if(i >= 0) panier[i] = l; else panier.push(l);
  sauvePanier();
  fermer();
  majPastille();
  ouvrirPanier();
}

/* ==================================================================
   LE TIROIR DU PANIER
   ================================================================== */
function panOuvert(){
  var p = document.getElementById("pan");
  return !!p && p.classList.contains("on");
}
function ouvrirPanier(){
  rendrePanier();
  document.getElementById("pan").classList.add("on");
  document.getElementById("panOv").classList.add("on");
  document.getElementById("pan").setAttribute("aria-hidden","false");
  document.body.style.overflow = "hidden";
  parDessus(true);
}
function fermerPanier(){
  var p = document.getElementById("pan");
  if(!p) return;
  p.classList.remove("on");
  p.setAttribute("aria-hidden","true");
  document.getElementById("panOv").classList.remove("on");
  if(!document.getElementById("ov").classList.contains("on")){
    document.body.style.overflow = "";
    parDessus(false);
  }
}
function majPastille(){
  var n = totaux().articles;
  var b = document.getElementById("panN");
  if(!b) return;
  b.textContent = n;
  b.classList.toggle("on", n > 0);
}

function rendrePanier(){
  var bd = document.getElementById("panBd");
  var ft = document.getElementById("panFt");
  if(!bd || !ft) return;

  if(!panier.length){
    bd.innerHTML = '<div class="pan-vide">'+
      '<svg viewBox="0 0 24 24"><path d="M6 8h12l-1 12H7L6 8z"/><path d="M9.5 8V6.5a2.5 2.5 0 015 0V8"/></svg>'+
      '<p>Votre panier est vide.</p>'+
      '<span>Choisissez une pièce dans les créations, donnez vos mesures, et elle se posera ici.</span></div>';
    ft.innerHTML = '<button class="bt g" type="button" data-pan="fermer">Voir les créations</button>';
    majPastille();
    return;
  }

  bd.innerHTML = panier.map(function(l){
    var p = pieceDe(l.id);
    if(!p) return "";
    var v = prixLigne(l);
    var img = p.img
      ? '<img class="pl-img" src="assets/images/'+esc(p.img)+'" alt="" loading="lazy" decoding="async">'
      : '<span class="pl-img pl-mono" aria-hidden="true">'+esc(p.nom.charAt(0))+'</span>';
    return '<div class="pl">'+img+
      '<div class="pl-i">'+
        '<h4>'+esc(p.nom)+'</h4>'+
        '<div class="pl-d">'+esc(libLigne(l))+'</div>'+
        '<div class="pl-d">'+(l.express
            ? '<b class="pl-ex">Express</b> · '+esc(libDelai(pieceDe(l.id).expMin != null ? pieceDe(l.id).expMin : DELAIS.express.jmin,
                                                             pieceDe(l.id).expMax != null ? pieceDe(l.id).expMax : DELAIS.express.jmax))
            : esc(libDelaiLigne(l)))+'</div>'+
        '<div class="pl-c">'+
          '<span class="qty">'+
            '<button type="button" data-moins="'+esc(l.cle)+'" aria-label="Retirer un exemplaire">−</button>'+
            '<b>'+l.qte+'</b>'+
            '<button type="button" data-plus="'+esc(l.cle)+'" aria-label="Ajouter un exemplaire">+</button>'+
          '</span>'+
          '<button class="pl-mod" type="button" data-mod="'+esc(l.cle)+'">Modifier</button>'+
          '<button class="pl-rm" type="button" data-rm="'+esc(l.cle)+'">Retirer</button>'+
        '</div>'+
      '</div>'+
      '<div class="pl-p">'+(v==null?"Sur devis":fcfa(v))+'</div>'+
    '</div>';
  }).join("");

  var t = totaux();
  var dev = [];
  if(!t.devis && t.eurOk) dev.push(t.eur+" €");
  if(!t.devis && t.usdOk) dev.push(t.usd+" $");
  ft.innerHTML =
    '<div class="pan-t"><span>Sous-total</span><b>'+(t.devis?"Sur devis":fcfa(t.fcfa))+'</b></div>'+
    (dev.length ? '<div class="pan-dev">soit '+dev.join(" · ")+'</div>' : '')+
    '<div class="pan-note">La livraison se choisit à l\'étape suivante. '+
    'Le règlement se fait par Mobile Money, jamais sur ce site.</div>'+
    '<button class="bt p" type="button" data-pan="commander">Commander '+
      (t.articles>1 ? "ces "+t.articles+" pièces" : "cette pièce")+'</button>'+
    '<button class="bt g" type="button" data-pan="vider">Vider le panier</button>';
  majPastille();
}

document.addEventListener("click", function(e){
  var c = e.target.closest ? e.target.closest("[data-pan],[data-rm],[data-mod],[data-plus],[data-moins]") : null;
  if(!c) return;
  if(c.dataset.pan === "fermer"){ fermerPanier(); return; }
  if(c.dataset.pan === "commander"){ ouvrirCommande(); return; }
  if(c.dataset.pan === "vider"){
    if(panier.length && confirm("Vider entièrement votre panier ?")){
      panier = []; sauvePanier(); rendrePanier();
    }
    return;
  }
  if(c.dataset.rm){
    panier = panier.filter(function(l){ return l.cle !== c.dataset.rm; });
    sauvePanier(); rendrePanier(); return;
  }
  if(c.dataset.mod){
    var l = panier.filter(function(x){ return x.cle === c.dataset.mod; })[0];
    if(l){ fermerPanier(); ouvrir(l.id, l.cle); }
    return;
  }
  if(c.dataset.plus || c.dataset.moins){
    var cle = c.dataset.plus || c.dataset.moins;
    var d = c.dataset.plus ? 1 : -1;
    panier.forEach(function(x){
      if(x.cle === cle) x.qte = Math.max(1, Math.min(10, x.qte + d));
    });
    sauvePanier(); rendrePanier();
  }
});

(function(){
  var b = document.getElementById("btPan");
  if(b) b.addEventListener("click", function(){ panOuvert() ? fermerPanier() : ouvrirPanier(); });
  var x = document.getElementById("panX");
  if(x) x.addEventListener("click", fermerPanier);
  var ov = document.getElementById("panOv");
  if(ov) ov.addEventListener("click", fermerPanier);
  majPastille();
})();

/* ==================================================================
   LE MESSAGE DE COMMANDE
   ================================================================== */
function message(){
  var L = [];
  L.push("*NOUVELLE COMMANDE — HILLARY M. STYL*");
  var t = totaux();
  L.push("_"+t.articles+(t.articles>1?" pièces":" pièce")+"_");

  panier.forEach(function(l, k){
    var p = pieceDe(l.id); if(!p) return;
    var v = prixLigne(l);
    L.push("");
    L.push("*"+(k+1)+". "+p.nom+"*"+(l.qte>1?" × "+l.qte:""));
    L.push((p.cat==="sm"?"Sur-mesure":"Prêt-à-porter")+" · "+libDelaiLigne(l));
    L.push("Prix : "+(v==null?"sur devis":fcfa(v)));
    if(l.taille) L.push("Taille : "+l.taille);
    if(p.cat==="sm" && l.typeMesure && MESURES[l.typeMesure]){
      var jeu = MESURES[l.typeMesure];
      L.push("MESURES — "+jeu.nom);
      if(jeu.aValider) L.push("_(liste de mesures à valider par l'atelier)_");
      var manquantes = [];
      jeu.champs.forEach(function(c){
        if(l.mesures[c.id]) L.push("• "+c.l+" : "+l.mesures[c.id]+" cm");
        else manquantes.push(c.l);
      });
      if(manquantes.length) L.push("_À prendre ensemble ("+manquantes.length+") :_ "+manquantes.join(", "));
    }
    if((l.tissu||"").trim())   L.push("Tissu : "+l.tissu.trim());
    if((l.details||"").trim()) L.push("Détails : "+l.details.trim());
  });

  L.push("");
  L.push("*LIVRAISON*");
  if(cmd.mode === "retrait"){
    L.push("Retrait à l'atelier — gratuit");
  }else{
    var f = fraisLivraison();
    L.push("Expédition — "+(cmd.pays?cmd.pays.nom:"")+(cmd.ville.trim()? ", "+cmd.ville.trim() : ""));
    L.push("Frais : "+(f===null ? "à confirmer" : fcfa(f)));
  }

  var j = joursTotal();
  if(j != null){
    L.push("");
    L.push("*DÉLAI*");
    L.push("Disponible au plus tard le "+dateFr(dateDispo(j)));
    if(panier.length > 1) L.push("_(délai de la pièce la plus longue, tout part ensemble)_");
  }

  var tot = totalCommande();
  L.push("");
  L.push("*TOTAL : "+(tot==null ? "sur devis" : fcfa(tot))+"*");
  if(!t.devis && (t.eurOk || t.usdOk)){
    var dev = [];
    if(t.eurOk) dev.push(t.eur+" €");
    if(t.usdOk) dev.push(t.usd+" $");
    L.push("_(les pièces : "+dev.join(" · ")+")_");
  }
  L.push("_Règlement par Mobile Money._");

  L.push("");
  L.push("*CLIENT*");
  L.push((cmd.prenom.trim()+" "+cmd.nom.trim()).trim());
  if(cmd.tel.trim())  L.push("WhatsApp : "+cmd.tel.trim());
  if(cmd.mail.trim()) L.push("Email : "+cmd.mail.trim());
  if(cmd.ville.trim())L.push("Ville : "+cmd.ville.trim());
  if(cmd.note.trim()){ L.push(""); L.push("*Note :* "+cmd.note.trim()); }

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


/* ==================================================================
   LES SONS D'ATELIER
   ==================================================================
   Direction « atelier réel », choisie par Mongazi le 2026-08-11 :
   on entend l'acier, le tissu, la machine. Hillary vend du fait-main,
   un son trop poli dirait le contraire.

   Six sons seulement, ceux qui portent le sens. Un site où chaque
   geste sonne devient fatigant en deux minutes, et on peut toujours
   en ajouter, jamais retirer une habitude.

   ⚠️ Rien ne sonne avant un geste : aucun navigateur ne l'autorise, et
      quelqu'un peut ouvrir le site au bureau.
   ⚠️ Silence d'amorçage iOS, sinon la sortie ne s'ouvre jamais.
   ⚠️ Un verrou par son : sur un clic rapide, dix déclenchements
      empilés font une bouillie.
   ================================================================== */
var Atelier = (function(){
  var SONS = ["ouvrir","fiche","mesure","etape","couper","envoyer"];
  var VOL  = 0.30;              /* bas : un son d'interface se sent
                                   plus qu'il ne s'écoute */
  var ctx = null, maitre = null, tampons = {}, dernier = {};
  var muet = false, pret = false;

  try { muet = localStorage.getItem("hms:muet") === "1"; } catch(e){}

  function mobile(){
    return matchMedia("(hover: none), (max-width: 900px)").matches;
  }

  function volume(){ return mobile() ? VOL * 1.6 : VOL; }

  function demarrer(){
    if(ctx) return;
    var AC = window.AudioContext || window.webkitAudioContext;
    if(!AC) return;
    ctx = new AC();

    /* le silence d'amorçage : iOS n'ouvre la sortie qu'après un vrai son */
    var s0 = ctx.createBufferSource();
    s0.buffer = ctx.createBuffer(1, 1, 22050);
    s0.connect(ctx.destination); s0.start(0);

    maitre = ctx.createGain();
    maitre.gain.value = muet ? 0 : volume();
    var comp = ctx.createDynamicsCompressor();
    maitre.connect(comp); comp.connect(ctx.destination);

    SONS.forEach(function(n){
      fetch("assets/sons/" + n + ".mp3")
        .then(function(r){ if(!r.ok) throw 0; return r.arrayBuffer(); })
        .then(function(ab){
          return new Promise(function(ok, non){ ctx.decodeAudioData(ab, ok, non); });
        })
        .then(function(b){ tampons[n] = b; })
        .catch(function(){});
    });
    pret = true;
  }

  function jouer(nom){
    if(!pret || muet || !ctx || !tampons[nom]) return;
    var t = ctx.currentTime;
    if(dernier[nom] && t - dernier[nom] < 0.06) return;   /* le verrou */
    dernier[nom] = t;
    var s = ctx.createBufferSource();
    s.buffer = tampons[nom];
    s.connect(maitre);
    s.start(0);
  }

  var bt = null;
  function majBouton(){
    if(!bt) return;
    bt.setAttribute("aria-pressed", muet ? "true" : "false");
    bt.setAttribute("title", muet ? "Remettre le son" : "Couper le son");
  }

  function basculer(){
    muet = !muet;
    try { localStorage.setItem("hms:muet", muet ? "1" : "0"); } catch(e){}
    if(maitre && ctx){
      maitre.gain.cancelScheduledValues(ctx.currentTime);
      maitre.gain.setTargetAtTime(muet ? 0 : volume(), ctx.currentTime, 0.06);
    }
    majBouton();
    return muet;
  }

  function poserBouton(){
    bt = document.createElement("button");
    bt.type = "button";
    bt.className = "sonbt";
    bt.setAttribute("aria-pressed", muet ? "true" : "false");
    bt.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true">' +
      '<path class="hp" d="M4 9v6h4l5 4V5L8 9H4z"/>' +
      '<path class="on1" d="M16.5 8.5a5 5 0 010 7"/>' +
      '<path class="on2" d="M19 6a8.5 8.5 0 010 12"/>' +
      '<path class="off" d="M17 9.5l5 5M22 9.5l-5 5"/>' +
      '</svg><span class="vhs">Son</span>';
    bt.addEventListener("click", function(){ demarrer(); basculer(); });
    /* ⚠️ IL N'EST PLUS POSÉ SUR LA PAGE. En `position:fixed` en bas à gauche,
       il recouvrait le PREMIER MOT de tout texte qui passait par là : « 04 »
       dans le processus, « Conçu par » dans le pied, « Saison 2026 », le
       « On » d'un titre de section — onze endroits mesurés à 390, 768 ET
       1440 px, vus par Mongazi le 2026-08-21. La règle de la maison est
       nette : un instrument flottant ne recouvre jamais du texte, seules les
       bandes de bord en ont le droit. La barre du haut EST une bande de bord,
       opaque, et il y devient un bouton comme les autres.
       ⚠️ Il redevient flottant PENDANT UNE COMMANDE (`body.ecran-on`) : la
       barre passe alors derrière le voile, et la maison exige qu'on puisse
       couper le son en donnant ses mesures. Le couloir de 78 px des deux
       pieds de page l'y attend déjà. */
    var barre = document.querySelector(".nav-d");
    if(barre) barre.insertBefore(bt, barre.firstChild);
    else document.body.appendChild(bt);
    majBouton();
  }

  /* le premier geste réel ouvre la sortie audio */
  ["pointerdown","keydown","touchstart"].forEach(function(ev){
    window.addEventListener(ev, demarrer, { once:true, passive:true });
  });

  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", poserBouton);
  } else { poserBouton(); }

  return { jouer: jouer, demarrer: demarrer };
})();

/* --- où chaque son se déclenche ---------------------------------- */
(function(){
  function J(n){ return function(){ Atelier.jouer(n); }; }

  /* 1 · le rideau se fend : deux lames d'acier qui s'écartent.
     Il ne sonne que si un geste a déjà eu lieu, donc au retour sur le
     site et non à la toute première visite. C'est la règle, pas un
     défaut : aucun navigateur n'autorise le son avant un geste. */
  setTimeout(J("ouvrir"), 250);

  /* 2 · une pièce s'ouvre : le tissu qu'on soulève */
  document.addEventListener("click", function(e){
    var c = e.target.closest && e.target.closest(".piece");
    if(c){ Atelier.demarrer(); setTimeout(J("fiche"), 40); }
  }, true);

  /* 3 · une mesure entrée : le petit claquement du ruban */
  document.addEventListener("input", function(e){
    if(e.target && e.target.matches && e.target.matches("[data-mes]")) J("mesure")();
  }, true);

  /* 4 · l'étape suivante : trois ou quatre points de machine
     5 · la validation : le coup de ciseaux dans le tissu */
  document.addEventListener("click", function(e){
    var b = e.target.closest && e.target.closest("[data-nav]");
    if(!b || b.getAttribute("data-nav") !== "suiv") return;
    if(b.hasAttribute("disabled")) return;
    J(typeof cmd !== "undefined" && cmd.actif && cmd.etape === 2 ? "couper" : "etape")();
  }, true);

  /* 6 · la commande part : le fil qu'on noue */
  document.addEventListener("click", function(e){
    var a = e.target.closest && e.target.closest("#btWa");
    if(a) J("envoyer")();
  }, true);
})();
