# -*- coding: utf-8 -*-
"""
NEBULA Studio Quotidien — CERVEAU créatif (couche d'intelligence).

Rôle : produire CHAQUE jour un concept de contenu publiable TOTALEMENT différent,
inattendu, innovant et professionnel — script + storyboard vidéo + légende.

Garanties de nouveauté ("jamais deux fois pareil") :
  1. Taxonomie riche (24 formats x 3 marques x tons x styles visuels x couleurs).
  2. Registre mémoire (ledger.jsonl) : on évite les formats/angles récents.
  3. Claude (Opus) reçoit l'historique récent et a l'ordre explicite de diverger.

N'a AUCUN secret en dur : les clés viennent de l'environnement (ou des .env voisins).
"""
import os, re, json, random, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
LEDGER = HERE / "ledger.jsonl"

# --------------------------------------------------------------------------- #
#  Chargement des clés (env d'abord, puis .env voisins — jamais committés)
# --------------------------------------------------------------------------- #
def load_env():
    candidates = [
        HERE / ".env",
        HERE.parent / "boutique-ia" / ".env",
        HERE.parent / "nebula-prospector" / ".env",
        HERE.parent / "secrets" / "heygen.env",
    ]
    for f in candidates:
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:        # l'env réel a priorité
                os.environ[k] = v

# --------------------------------------------------------------------------- #
#  Taxonomie créative
# --------------------------------------------------------------------------- #
FORMATS = [
    "Mythe à briser", "Avis impopulaire", "Étude de cas express", "Coulisses",
    "Avant / Après", "Une journée avec…", "Prédiction", "Calcul de ROI chiffré",
    "Tueur d'objection", "Détournement de tendance", "Histoire vraie", "Top 3",
    "Question provocante", "Démonstration en 30s", "L'erreur qui coûte cher",
    "Secret d'initié", "Comparaison choc", "Manifeste", "Statistique qui dérange",
    "Le saviez-vous", "Métaphore visuelle", "Défi de 7 jours", "Coup de gueule",
    "Lettre à un commerçant",
]
# UNE seule marque : NEBULA Agency. Son agent IA s'appelle NOVA.
BRANDS = {
    "NEBULA Agency": "NEBULA Agency crée des vitrines digitales professionnelles "
        "(+ QR code) et des automatisations IA pour les commerçants et PME d'Afrique "
        "de l'Ouest francophone. Son agent IA s'appelle NOVA : il répond aux clients, "
        "prend les commandes et travaille sur WhatsApp 24/7. Promesse : être visible, "
        "paraître pro, vendre plus, gagner du temps, encaisser en Mobile Money. Cotonou, Bénin.",
}
# Sujets de départ (varient l'angle SANS changer de marque)
THEMES = [
    "une vitrine web qui vend, pas juste une jolie page",
    "le QR code qui ramène des clients vers ta boutique",
    "NOVA, l'agent IA de NEBULA sur WhatsApp qui répond et vend 24/7",
    "l'automatisation qui te fait gagner des heures chaque jour",
    "être trouvable en ligne au moment où un client te cherche",
    "passer d'une image amateur à une image vraiment pro",
    "ne plus jamais rater un client qui écrit la nuit",
    "encaisser en Mobile Money sans friction",
    "transformer des vues et des likes en vraies commandes",
    "déléguer le service client à NOVA et se concentrer sur son métier",
]
TONES = ["inspirant", "audacieux", "pédagogue et complice", "premium et sobre",
         "urgent et direct", "optimiste", "provocateur malin", "chaleureux"]
VISUAL_STYLES = ["kinetic", "stat", "quote", "manifesto", "list", "split"]
ACCENTS = [
    ("Violet NEBULA", "#7b5cff"), ("Cyan électrique", "#22d3ee"),
    ("Vert néon", "#36f5a0"), ("Or", "#e6c34c"),
    ("Rose plasma", "#ff5c7a"), ("Bleu glace", "#4cc6ff"),
]
PLATFORMS = ["TikTok", "Reels Instagram", "Statut WhatsApp", "Facebook", "YouTube Shorts"]

# --------------------------------------------------------------------------- #
#  Registre mémoire (anti-répétition)
# --------------------------------------------------------------------------- #
def load_ledger(limit=40):
    if not LEDGER.exists():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out[-limit:]

def append_ledger(entry):
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def choose_axes(recent):
    """Choisit format/marque/ton/style/couleur en évitant ce qui est récent."""
    used_formats = [e.get("format") for e in recent[-8:]]
    fmt_pool = [f for f in FORMATS if f not in used_formats] or FORMATS

    used_themes = [e.get("theme") for e in recent[-6:]]
    theme_pool = [t for t in THEMES if t not in used_themes] or THEMES

    used_styles = [e.get("visual", {}).get("style") for e in recent[-3:]]
    style_pool = [s for s in VISUAL_STYLES if s not in used_styles] or VISUAL_STYLES

    # couleur d'accent : différente des 2 derniers posts (donc les 2 posts du jour diffèrent)
    last_accents = [e.get("accent") for e in recent[-2:]]
    accent_pool = [a for a in ACCENTS if a[1] not in last_accents] or ACCENTS
    accent = random.choice(accent_pool)

    return {
        "format": random.choice(fmt_pool),
        "brand": "NEBULA Agency",
        "theme": random.choice(theme_pool),
        "tone": random.choice(TONES),
        "style": random.choice(style_pool),
        "accent_name": accent[0],
        "accent": accent[1],
        "platform": random.choice(PLATFORMS),
    }

# --------------------------------------------------------------------------- #
#  Génération du concept via Claude
# --------------------------------------------------------------------------- #
SYSTEM = """Tu es le Directeur de Création d'un studio de contenu haut de gamme \
(niveau agence à 40 000 $). Tu écris pour le marché de l'Afrique de l'Ouest \
francophone (Bénin, Togo, Côte d'Ivoire…). Ton français est impeccable, vivant, \
sans clichés corporate, sans emoji dans les textes destinés à l'écran. \
Tu crées des contenus courts (format vertical, 12 à 22 secondes) qui ARRÊTENT le \
scroll dès la première seconde et donnent envie d'agir. Tu réponds UNIQUEMENT par \
un objet JSON valide, rien d'autre.

Règle de marque ABSOLUE : la marque est TOUJOURS « NEBULA Agency ». Son agent IA \
s'appelle « NOVA » (sur WhatsApp). N'invente JAMAIS un autre nom de marque ni un \
autre nom d'agent (jamais « Vendora », « AXIO », etc.)."""

PROMPT_TMPL = """Crée le contenu du jour. Il doit être PROFESSIONNEL, INATTENDU et \
TOTALEMENT DIFFÉRENT de tout ce qui a déjà été fait (voir l'historique).

Contraintes imposées pour aujourd'hui :
- Marque : {brand} (la SEULE marque ; agent IA = NOVA)
  ({brand_desc})
- Sujet de départ : {theme}
- Format éditorial : « {format} »
- Ton : {tone}
- Plateforme cible : {platform}
- Style visuel de la vidéo : « {style} »  (kinetic = typographie animée ; stat = \
gros chiffre révélé ; quote = phrase forte ; manifesto = déclarations fortes en \
majuscules ; list = liste animée ; split = avant/après)

HISTORIQUE RÉCENT À NE PAS RÉPÉTER (angles, titres déjà sortis) :
{history}

Écris un contenu neuf, surprenant, mémorable. Le script doit pouvoir être lu en \
voix off ET fonctionner en texte à l'écran. Donne une vraie idée, une vraie \
accroche, un vrai bénéfice concret (chiffres réalistes si pertinent), un appel à \
l'action clair vers la marque.

Réponds par CE JSON exactement (5 à 7 scènes, chaque scène = un plan de la vidéo) :
{{
  "title": "titre interne court",
  "hook": "la toute première phrase qui arrête le scroll (max 9 mots)",
  "script": "le script complet publiable, 45-90 mots, paragraphes courts",
  "caption": "la légende du post (1-3 phrases, accrocheuse)",
  "hashtags": ["#...", "#...", "#...", "#...", "#..."],
  "cta": "l'appel à l'action final (max 8 mots)",
  "scenes": [
    {{"kicker": "petit label en haut (2-3 mots)", "line": "le gros texte du plan (max 7 mots, percutant)", "sub": "sous-texte optionnel (max 12 mots)"}}
  ],
  "freshness_note": "en 1 phrase, pourquoi ce contenu est différent des précédents"
}}"""

def _extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text).strip().rstrip("`").strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("Pas de JSON dans la réponse du modèle.")
    return json.loads(m.group(0))

def generate(model=None):
    load_env()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY introuvable (env ou .env voisin).")
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    model = model or os.environ.get("STUDIO_MODEL", "claude-opus-4-8")

    recent = load_ledger()
    axes = choose_axes(recent)
    history = "\n".join(
        f"- {e.get('date','?')} · {e.get('brand','?')} · {e.get('format','?')} · "
        f"{e.get('title','')} — {e.get('hook','')}"
        for e in recent[-14:]
    ) or "(aucun historique : c'est le tout premier contenu)"

    prompt = PROMPT_TMPL.format(
        brand=axes["brand"], brand_desc=BRANDS[axes["brand"]], theme=axes["theme"],
        format=axes["format"], tone=axes["tone"], platform=axes["platform"],
        style=axes["style"], history=history,
    )
    msg = client.messages.create(
        model=model, max_tokens=2000, temperature=1.0,
        system=SYSTEM, messages=[{"role": "user", "content": prompt}],
    )
    raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    data = _extract_json(raw)

    today = datetime.date.today().isoformat()
    concept = {
        "date": today,
        "brand": axes["brand"],
        "theme": axes["theme"],
        "format": axes["format"],
        "tone": axes["tone"],
        "platform": axes["platform"],
        "accent": axes["accent"],
        "accent_name": axes["accent_name"],
        "title": data.get("title", "").strip(),
        "hook": data.get("hook", "").strip(),
        "script": data.get("script", "").strip(),
        "caption": data.get("caption", "").strip(),
        "hashtags": data.get("hashtags", []),
        "cta": data.get("cta", "").strip(),
        "freshness_note": data.get("freshness_note", "").strip(),
        "visual": {"style": axes["style"], "scenes": data.get("scenes", [])},
        "model": model,
    }
    append_ledger({
        "date": today, "brand": concept["brand"], "theme": axes["theme"],
        "format": concept["format"], "title": concept["title"], "hook": concept["hook"],
        "accent": axes["accent"], "visual": {"style": axes["style"]},
    })
    return concept

if __name__ == "__main__":
    c = generate()
    print(json.dumps(c, ensure_ascii=False, indent=2))
