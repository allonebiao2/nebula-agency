import json, re, datetime, sys
src = open(sys.argv[1], encoding='utf-8').read()
body = src.split('\n---\n', 1)[1]
def section(name):
    m = re.search(r'^## ' + re.escape(name) + r'\n(.*?)(?=^## |\Z)', body, re.S | re.M)
    return m.group(1)
ov = section('Overview')
head, tail = ov.split('**Key Characteristics:**')
paras = [p.strip() for p in head.split('\n\n') if p.strip() and not p.strip().startswith('**Creative')]
keys = [l[2:].strip() for l in tail.splitlines() if l.startswith('- ')]
rules = []
for sec, tag in [('Colors', 'colors'), ('Typography', 'typography'), ('Layout', 'layout'), ('Elevation & Depth', 'elevation')]:
    for m in re.finditer(r'\*\*(The [^*]+?)\.\*\* (.+)', section(sec)):
        rules.append({"name": m.group(1), "body": m.group(2).strip(), "section": tag})
dd = section("Do's and Don'ts")
DONT = "### Don't:"
dos = [l[2:].replace('**Do** ', 'Do ', 1) for l in dd.split(DONT)[0].splitlines() if l.startswith('- ')]
donts = [l[2:].replace("**Don't** ", "Don't ", 1) for l in dd.split(DONT)[1].splitlines() if l.startswith('- ')]

FLOU = "-webkit-backdrop-filter: blur(12px) saturate(1.2); backdrop-filter: blur(12px) saturate(1.2);"
GLASS = "background: rgba(12,10,14,.46); border: 1px solid rgba(255,255,255,.16); " + FLOU
FONT = "font-family: Archivo, system-ui, sans-serif;"
FOCUS = "outline: 2px solid #fff; outline-offset: 2px;"

components = [
 {"name": "Bouton de verre", "kind": "button", "refersTo": "button-verre",
  "description": "Le bouton par défaut : plat, petit, translucide.",
  "html": "<button class=\"ds-bt\">Retour</button>",
  "css": f".ds-bt {{ min-height: 40px; padding: 0 16px; border-radius: 10px; {FONT} font-weight: 600; font-size: .84rem; letter-spacing: .01em; color: #f6f3ee; {GLASS} cursor: pointer; transition: transform .15s, background .2s; }} .ds-bt:hover {{ background: rgba(12,10,14,.68); }} .ds-bt:focus-visible {{ {FOCUS} }} .ds-bt:active {{ transform: scale(.97); }}"},
 {"name": "Bouton plein magenta", "kind": "button", "refersTo": "button-plein",
  "description": "La seule action pleine d'une vue : Entrer, Je la prends.",
  "html": "<button class=\"ds-bt-plein\">Je la prends · 100 000 F</button>",
  "css": f".ds-bt-plein {{ min-height: 40px; padding: 0 16px; border-radius: 10px; {FONT} font-weight: 600; font-size: .84rem; letter-spacing: .01em; color: #fff; background: rgba(196,0,107,.9); border: 1px solid rgba(255,255,255,.22); cursor: pointer; transition: transform .15s, background .2s; }} .ds-bt-plein:hover {{ background: #e6007e; }} .ds-bt-plein:focus-visible {{ {FOCUS} }} .ds-bt-plein:active {{ transform: scale(.97); }}"},
 {"name": "Bouton express", "kind": "button", "refersTo": "button-express",
  "description": "Action secondaire teintée : verre magenta bordé de magenta clair.",
  "html": "<button class=\"ds-bt-express\">En express · 140 000 F</button>",
  "css": f".ds-bt-express {{ min-height: 40px; padding: 0 16px; border-radius: 10px; {FONT} font-weight: 600; font-size: .84rem; color: #fff; background: rgba(196,0,107,.2); border: 1px solid rgba(255,140,198,.55); {FLOU} cursor: pointer; }} .ds-bt-express:hover {{ background: rgba(196,0,107,.32); }} .ds-bt-express:focus-visible {{ {FOCUS} }}"},
 {"name": "Bouton icône (sac)", "kind": "button", "refersTo": "button-icone",
  "description": "Carré de verre de 40 px, icône SVG au trait 1,8, pastille de compte.",
  "html": "<button class=\"ds-bt-ic\" aria-label=\"Sac\"><svg viewBox=\"0 0 24 24\"><path d=\"M5 8h14l-1 12H6L5 8z\"/><path d=\"M9 8V6a3 3 0 0 1 6 0v2\"/></svg><span class=\"ds-compte\">2</span></button>",
  "css": f".ds-bt-ic {{ position: relative; width: 40px; height: 40px; display: grid; place-items: center; border-radius: 10px; color: #f6f3ee; {GLASS} cursor: pointer; }} .ds-bt-ic svg {{ width: 19px; height: 19px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }} .ds-bt-ic:hover {{ background: rgba(12,10,14,.68); }} .ds-bt-ic:focus-visible {{ {FOCUS} }} .ds-compte {{ position: absolute; top: -5px; right: -5px; min-width: 18px; height: 18px; padding: 0 5px; border-radius: 9px; background: #e6007e; color: #fff; font: 700 .7rem/18px Archivo, system-ui, sans-serif; font-variant-numeric: tabular-nums; }}"},
 {"name": "Sous-titre de conversation", "kind": "custom", "refersTo": "sous-titre-replique",
  "description": "La signature Call of Duty : le nom et la réplique dans deux boîtes noires translucides.",
  "html": "<div class=\"ds-st\"><b>Hillary</b><span>Qu'est-ce qui te ferait plaisir ?</span></div>",
  "css": f".ds-st {{ display: flex; align-items: flex-start; gap: 4px; {FONT} }} .ds-st b {{ flex: none; padding: 4px 8px; border-radius: 4px; background: rgba(0,0,0,.6); color: #ff8cc6; font-weight: 700; font-size: .84rem; letter-spacing: .01em; }} .ds-st span {{ max-width: 46ch; padding: 4px 10px 5px; border-radius: 4px; background: rgba(0,0,0,.55); color: #ececec; font-size: .94rem; line-height: 1.45; }}"},
 {"name": "Réponse en croix", "kind": "chip", "refersTo": "reponse-croix",
  "description": "Une des quatre réponses autour du losange ; point magenta clair si neuve.",
  "html": "<button class=\"ds-ch ds-neuf\">Parle-moi de la maison</button>",
  "css": f".ds-ch {{ position: relative; min-height: 40px; padding: 6px 12px; border-radius: 8px; background: rgba(0,0,0,.5); color: #fff; border: 1px solid rgba(255,255,255,.18); {FONT} font-weight: 600; font-size: .84rem; line-height: 1.25; text-wrap: balance; cursor: pointer; }} .ds-ch:hover, .ds-ch:focus-visible {{ background: rgba(196,0,107,.92); border-color: transparent; outline: none; }} .ds-neuf {{ padding-right: 20px; }} .ds-neuf::after {{ content: ''; position: absolute; top: 7px; right: 7px; width: 6px; height: 6px; border-radius: 50%; background: #ff8cc6; }}"},
 {"name": "Étiquette de repère", "kind": "chip", "refersTo": "etiquette-repere",
  "description": "Le point d'une création et son nom en verre fort.",
  "html": "<button class=\"ds-rep\"><i></i><span>Robe de cérémonie</span></button>",
  "css": f".ds-rep {{ display: inline-flex; align-items: center; gap: 6px; min-height: 40px; padding: 0 0 0 12px; background: none; border: 0; cursor: pointer; }} .ds-rep i {{ width: 14px; height: 14px; border-radius: 50%; border: 2px solid rgba(255,255,255,.95); background: #e6007e; box-shadow: 0 1px 4px rgba(0,0,0,.6); }} .ds-rep span {{ padding: 4px 9px; border-radius: 8px; background: rgba(12,10,14,.68); color: #f6f3ee; {FONT} font-weight: 600; font-size: .74rem; letter-spacing: .01em; border: 1px solid rgba(255,255,255,.16); {FLOU} }} .ds-rep:hover span, .ds-rep:focus-visible span {{ background: rgba(196,0,107,.92); }} .ds-rep:focus-visible {{ {FOCUS} }}"},
 {"name": "Fiche d'une pièce", "kind": "card", "refersTo": "fiche-piece",
  "description": "Panneau de verre : le nom en Bodoni, le genre en magenta clair, les cases de chiffres.",
  "html": "<div class=\"ds-fiche\"><h2>Robe de cérémonie</h2><p><b>Sur-mesure · Cérémonie.</b> Bustier structuré, jupe ample à volants de satin.</p><div class=\"ds-stats\"><div class=\"ds-stat\"><span>Prix</span><strong>100 000 F</strong></div><div class=\"ds-stat ds-express\"><span>Express</span><strong>2 à 4 jours</strong></div></div></div>",
  "css": f".ds-fiche {{ max-width: 420px; padding: 22px 22px 20px; border-radius: 16px; background: rgba(14,12,16,.78); color: #f6f3ee; border: 1px solid rgba(255,255,255,.16); {FLOU} box-shadow: 0 24px 60px rgba(0,0,0,.45); {FONT} }} .ds-fiche h2 {{ margin: 0 0 8px; font: 500 2rem/1.05 'Bodoni Moda', Georgia, serif; letter-spacing: -.005em; color: #fff; }} .ds-fiche p {{ margin: 0 0 14px; color: rgba(246,243,238,.74); font-size: .88rem; line-height: 1.5; }} .ds-fiche p b {{ color: #ff8cc6; }} .ds-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }} .ds-stat {{ padding: 8px 12px; border-radius: 10px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.08); }} .ds-stat span {{ display: block; color: rgba(246,243,238,.74); font-weight: 600; font-size: .7rem; }} .ds-stat strong {{ font-weight: 800; font-size: 1.05rem; color: #fff; font-variant-numeric: tabular-nums; }} .ds-express {{ background: rgba(196,0,107,.32); border-color: rgba(255,140,198,.35); }}"},
 {"name": "Champ de commande", "kind": "input", "refersTo": "champ-commande",
  "description": "Champ en verre clair dans le cadran ; astérisque magenta clair pour un champ requis.",
  "html": "<label class=\"ds-champ\"><span>Prénom<i></i></span><input placeholder=\"Ton prénom\"></label>",
  "css": f".ds-champ {{ display: grid; gap: 4px; {FONT} color: rgba(246,243,238,.74); font-size: .78rem; font-weight: 600; }} .ds-champ i::after {{ content: '*'; color: #ff8cc6; margin-left: .2em; }} .ds-champ input {{ min-height: 40px; padding: 0 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,.22); background: rgba(255,255,255,.08); color: #f6f3ee; font: inherit; font-size: .9rem; }} .ds-champ input::placeholder {{ color: rgba(246,243,238,.55); }} .ds-champ input:focus-visible {{ {FOCUS} }}"},
]

side = {
 "schemaVersion": 2,
 "generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
 "title": "Design System: LE MONDE · le salon HILLARY M. STYL",
 "extensions": {
  "colorMeta": {
   "marque-vif": {"role": "primary", "displayName": "Magenta H.M.S vif", "canonical": "#e6007e", "tonalRamp": ["#3a0020", "#5c0033", "#850049", "#b00061", "#e6007e", "#ff4fa3", "#ff8cc6", "#ffd3e8"]},
   "marque-profond": {"role": "primary", "displayName": "Magenta H.M.S profond", "canonical": "#c4006b", "tonalRamp": ["#2e0019", "#4d002a", "#73003f", "#9a0054", "#c4006b", "#e04593", "#f28cbf", "#fbd2e6"]},
   "magenta-texte": {"role": "primary", "displayName": "Magenta clair sur verre", "canonical": "#ff8cc6", "tonalRamp": ["#4a1530", "#7a2552", "#ad3a78", "#de5a9f", "#ff8cc6", "#ffa9d4", "#ffc8e3", "#ffe8f3"]},
   "verre": {"role": "neutral", "displayName": "Verre fumé", "canonical": "rgba(12, 10, 14, .46)"},
   "verre-fort": {"role": "neutral", "displayName": "Verre fort", "canonical": "rgba(12, 10, 14, .68)"},
   "verre-panneau": {"role": "neutral", "displayName": "Verre de panneau", "canonical": "rgba(14, 12, 16, .78)"},
   "verre-formulaire": {"role": "neutral", "displayName": "Verre de formulaire", "canonical": "rgba(14, 12, 16, .86)"},
   "verre-clair": {"role": "neutral", "displayName": "Verre clair", "canonical": "rgba(255, 255, 255, .1)"},
   "filet": {"role": "neutral", "displayName": "Filet blanc", "canonical": "rgba(255, 255, 255, .16)"},
   "texte": {"role": "neutral", "displayName": "Crème", "canonical": "#f6f3ee", "tonalRamp": ["#2a2825", "#46433f", "#65615b", "#87827b", "#aaa59d", "#cdc8c0", "#e6e2db", "#f6f3ee"]},
   "texte-doux": {"role": "neutral", "displayName": "Crème douce", "canonical": "rgba(246, 243, 238, .74)"},
   "encre": {"role": "neutral", "displayName": "Encre", "canonical": "#0e0c10", "tonalRamp": ["#0e0c10", "#1c1920", "#2b2731", "#3d3844", "#57515f", "#77717f", "#a19ca8", "#d6d3da"]},
   "boite-sous-titre": {"role": "neutral", "displayName": "Boîte de sous-titre", "canonical": "rgba(0, 0, 0, .55)"},
   "texte-sous-titre": {"role": "neutral", "displayName": "Texte de sous-titre", "canonical": "#ececec"},
   "voix-hillary": {"role": "secondary", "displayName": "Voix d'Hillary", "canonical": "#ff8cc6"},
   "voix-afi": {"role": "secondary", "displayName": "Voix d'Afi", "canonical": "#8fc3ff"},
   "voix-senami": {"role": "secondary", "displayName": "Voix de Sènami, repère de personne", "canonical": "#ffc061"},
   "menthe": {"role": "secondary", "displayName": "Menthe (Maman Sènami, porte, fait)", "canonical": "#9be3b7"},
   "mur-taupe": {"role": "neutral", "displayName": "Mur taupe expresso (scène)", "canonical": "#4b3d37"},
   "plafond-expresso": {"role": "neutral", "displayName": "Plafond expresso (scène)", "canonical": "#2b2421"},
   "faisceau-ambre": {"role": "neutral", "displayName": "Faisceau ambré (scène)", "canonical": "#ffcf96"}
  },
  "typographyMeta": {
   "display": {"displayName": "Bodoni de la maison", "purpose": "Le nom d'une création, en tête de fiche et dans le sac. Rien d'autre."},
   "headline": {"displayName": "Titre de panneau", "purpose": "Sac, carnet, commande."},
   "title": {"displayName": "Carte de titre", "purpose": "Le lieu à l'entrée, le total de la commande."},
   "body": {"displayName": "Réplique", "purpose": "Sous-titres de conversation, 46ch au plus."},
   "body-sm": {"displayName": "Texte de panneau", "purpose": "Description d'une pièce."},
   "label": {"displayName": "Libellé", "purpose": "Boutons, réponses, options, invites."},
   "label-sm": {"displayName": "Petit libellé", "purpose": "Étiquettes de repère, heure."},
   "caption": {"displayName": "Légende chiffrée", "purpose": "Pastilles de compte, titre court de l'objectif, intitulés des cases. 11 px au moins."}
  },
  "glass": [
   {"name": "flou", "value": "blur(12px) saturate(1.2)", "purpose": "Le flou d'arrière-plan de tout morceau de verre."},
   {"name": "filet", "value": "1px solid rgba(255,255,255,.16)", "purpose": "La bordure de tout morceau de verre."}
  ],
  "shadows": [
   {"name": "panneau-fiche", "value": "0 24px 60px rgba(0,0,0,.45)", "purpose": "La fiche d'une pièce."},
   {"name": "panneau-lateral", "value": "0 20px 50px rgba(0,0,0,.45)", "purpose": "Le sac et le carnet."},
   {"name": "panneau-commande", "value": "0 30px 70px rgba(0,0,0,.5)", "purpose": "Le cadran de commande."},
   {"name": "point-repere", "value": "0 1px 4px rgba(0,0,0,.6)", "purpose": "Le point d'un repère."},
   {"name": "texte-nu", "value": "0 1px 3px rgba(0,0,0,.8)", "purpose": "Ombre de texte pour tout texte posé sans boîte sur la scène."},
   {"name": "voile-fiche", "value": "rgba(0,0,0,.28)", "purpose": "Voile derrière la fiche."},
   {"name": "voile-commande", "value": "rgba(0,0,0,.4)", "purpose": "Voile derrière la commande."},
   {"name": "voile-croix", "value": "rgba(0,0,0,.16)", "purpose": "Voile pendant les réponses en croix."}
  ],
  "motion": [
   {"name": "ease-pose", "value": "cubic-bezier(.2, .8, .2, 1)", "purpose": "Une carte qui se pose, sans rebond."},
   {"name": "options-pose", "value": "opacity .2s, transform .25s ease-pose, depuis translateY(6px) scale(.98)", "purpose": "Apparition de la carte d'options."},
   {"name": "objectif-repli", "value": "max-width .3s, opacity .5s, transform .5s ; repli après 6000 ms", "purpose": "L'objectif se replie en une ligne."},
   {"name": "arrivee-sortie", "value": "opacity .6s", "purpose": "La carte Entrer s'efface."},
   {"name": "pression", "value": "transform: scale(.97) en .15s", "purpose": "Retour tactile d'un bouton."},
   {"name": "reduit", "value": "prefers-reduced-motion: reduce, transitions supprimées", "purpose": "Toujours honoré."}
  ],
  "breakpoints": [
   {"name": "telephone", "value": "560px"},
   {"name": "fiche-feuille", "value": "720px"}
  ]
 },
 "components": components,
 "narrative": {
  "northStar": "Le verre fumé devant la vitrine",
  "overview": "\n\n".join(paras),
  "keyCharacteristics": keys,
  "rules": rules,
  "dos": dos,
  "donts": donts
 }
}
open(sys.argv[2], 'w', encoding='utf-8').write(json.dumps(side, ensure_ascii=False, indent=2) + '\n')
print(len(rules), len(dos), len(donts), len(keys), len(components), len(paras))
