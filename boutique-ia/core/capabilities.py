"""Registre des CAPACITÉS de l'agent vendeur — « Composez votre vendeur ».

Le commerçant choisit ce que son agent sait faire. Trois couches (cf. grille
validée avec Mongazi) :

- 🟢 SOCLE : toujours actif, même au forfait Démarrage (on ne bride JAMAIS la
  vente de base, sinon agent « bête » sur le forfait éco = résiliation).
- 🔵 MODULES : à la carte, verrouillés par forfait (palier `min_plan`) ET par
  NOMBRE (`MODULE_LIMIT` par forfait). Modèle hybride.
- 🟣 SUPER-POUVOIRS : réservés Empire (notre moat, vendus comme bénéfice).

Ce module est la SOURCE DE VÉRITÉ : le cerveau (`brain`) et les différents flux
(relances, prospection, multi-canal, email, comment-to-DM) lisent
`has_capability(merchant, id)` / `effective_capabilities(merchant)` pour savoir
quoi activer. Pour ne RIEN casser sur les boutiques existantes (colonne
`enabled_capabilities` encore vide), on retombe sur les anciens interrupteurs.
"""
from __future__ import annotations

from config import PLAN_LABELS, normalize_plan

# Rang des forfaits (pour comparer min_plan).
PLAN_RANK = {"demarrage": 0, "business": 1, "empire": 2}

# Nombre de MODULES activables par forfait (-1 = illimité). Socle non compté.
MODULE_LIMIT = {"demarrage": 2, "business": 5, "empire": -1}

# Registre. `group` : socle | module | premium. `min_plan` : palier d'accès.
# `promise` = bénéfice affiché au commerçant (jamais de jargon technique).
CAPABILITIES: list[dict] = [
    # 🟢 SOCLE — toujours inclus
    {"id": "vente", "group": "socle", "min_plan": "demarrage", "icon": "i-store",
     "label": "Vend 24h/24 et prend les commandes",
     "promise": "Répond et vend même quand vous dormez."},
    {"id": "conseil", "group": "socle", "min_plan": "demarrage", "icon": "i-check",
     "label": "Conseille : prix, disponibilité, livraison",
     "promise": "Renseigne vos clients comme un bon vendeur."},
    {"id": "alerte_patron", "group": "socle", "min_plan": "demarrage", "icon": "i-spark",
     "label": "Vous prévient si un client est chaud",
     "promise": "Vous alerte quand c'est sérieux (lead chaud, réclamation)."},

    # 🔵 MODULES — à la carte (verrouillés par forfait)
    {"id": "vocal", "group": "module", "min_plan": "demarrage", "icon": "i-send",
     "label": "Comprend les notes vocales",
     "promise": "Vos clients parlent, il comprend et répond."},
    {"id": "photos", "group": "module", "min_plan": "demarrage", "icon": "i-eye",
     "label": "Envoie les photos des produits",
     "promise": "Montre vos produits, pas seulement les décrit."},
    {"id": "cod", "group": "module", "min_plan": "demarrage", "icon": "i-truck",
     "label": "Paiement à la livraison",
     "promise": "Rassure les hésitants : ils paient en recevant."},
    {"id": "negociation", "group": "module", "min_plan": "demarrage", "icon": "i-target",
     "label": "Marchandage encadré",
     "promise": "Négocie tout seul, sans jamais casser vos prix."},
    {"id": "relances", "group": "module", "min_plan": "business", "icon": "i-rocket",
     "label": "Relances automatiques",
     "promise": "Récupère les clients qui hésitent ou ne paient pas."},
    {"id": "rdv", "group": "module", "min_plan": "business", "icon": "i-flask",
     "label": "Prise de rendez-vous",
     "promise": "Remplit votre agenda tout seul (salons, cliniques…)."},
    {"id": "multicanal", "group": "module", "min_plan": "business", "icon": "i-mail",
     "label": "Messenger + Instagram",
     "promise": "Un seul vendeur, sur tous vos réseaux."},
    {"id": "prospection", "group": "module", "min_plan": "business", "icon": "i-target",
     "label": "Va chercher des clients",
     "promise": "Trouve et contacte de nouveaux acheteurs."},

    # 🟣 SUPER-POUVOIRS — Empire
    {"id": "apprentissage_perso", "group": "premium", "min_plan": "empire", "icon": "i-chart",
     "label": "S'améliore sur VOTRE boutique",
     "promise": "Plus il vend, meilleur il devient pour vous."},
    {"id": "email_pro", "group": "premium", "min_plan": "empire", "icon": "i-mail",
     "label": "Email pro + réponses automatiques",
     "promise": "Vend aussi par email, depuis votre adresse pro."},
    {"id": "comment_to_dm", "group": "premium", "min_plan": "empire", "icon": "i-send",
     "label": "Acquisition sur les réseaux",
     "promise": "Répond en privé à ceux qui commentent vos publications."},
    {"id": "social", "group": "premium", "min_plan": "empire", "icon": "i-spark",
     "label": "Réseaux sociaux gérés",
     "promise": "Crée vos posts qui vendent (Facebook / Instagram)."},
    {"id": "coach", "group": "premium", "min_plan": "empire", "icon": "i-chart",
     "label": "Coach commercial",
     "promise": "Des conseils chiffrés pour vendre plus, chaque semaine."},
]

BY_ID: dict[str, dict] = {c["id"]: c for c in CAPABILITIES}
SOCLE_IDS: list[str] = [c["id"] for c in CAPABILITIES if c["group"] == "socle"]
SELECTABLE_IDS: list[str] = [c["id"] for c in CAPABILITIES if c["group"] in ("module", "premium")]

# Bundles recommandés par métier (defaults intelligents → jamais de page blanche).
# Clés = catégories de `prospecting.CATEGORIES`. Filtrés ensuite par forfait + limite.
CATEGORY_RECO: dict[str, list[str]] = {
    "beauty":      ["rdv", "photos", "relances"],
    "fashion":     ["photos", "negociation", "cod"],
    "restaurant":  ["photos", "cod", "relances"],
    "health":      ["rdv", "relances", "photos"],
    "hospitality": ["rdv", "photos", "relances"],
    "office":      ["relances", "prospection", "multicanal"],
    "retail":      ["photos", "cod", "negociation"],
    "events":      ["rdv", "photos", "prospection"],
}
# Pour compléter les créneaux restants (ordre de préférence générique).
_FILLER = ["photos", "cod", "vocal", "negociation", "relances", "rdv",
           "multicanal", "prospection"]


def _rank(plan: str) -> int:
    return PLAN_RANK.get(normalize_plan(plan), 0)


def is_available(cap: dict, plan: str) -> bool:
    """La capacité est-elle accessible à ce forfait (palier) ?"""
    if cap["group"] == "socle":
        return True
    return _rank(plan) >= PLAN_RANK.get(cap["min_plan"], 0)


def module_limit(plan: str) -> int:
    return MODULE_LIMIT.get(normalize_plan(plan), 2)


def parse_caps(value) -> list[str] | None:
    """Décode la colonne `enabled_capabilities`. None = jamais réglée (→ defaults)."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = str(value).split(",")
    out: list[str] = []
    for raw in items:
        cid = str(raw).strip().lower()
        if cid in BY_ID and cid not in out:
            out.append(cid)
    return out


def serialize_caps(ids) -> str:
    """Encode une liste d'ids pour stockage (modules/premium seulement)."""
    out: list[str] = []
    for raw in ids or []:
        cid = str(raw).strip().lower()
        if cid in BY_ID and BY_ID[cid]["group"] in ("module", "premium") and cid not in out:
            out.append(cid)
    return ",".join(out)


def default_capabilities_for(category: str | None, plan: str) -> list[str]:
    """Bundle recommandé (ids modules) pour un métier + forfait, dans la limite."""
    plan = normalize_plan(plan)
    lim = module_limit(plan)
    reco = list(CATEGORY_RECO.get((category or "").strip().lower(), []))
    chosen: list[str] = []
    for cid in reco + _FILLER:
        if lim >= 0 and len(chosen) >= lim:
            break
        cap = BY_ID.get(cid)
        if cap and cap["group"] == "module" and is_available(cap, plan) and cid not in chosen:
            chosen.append(cid)
    return chosen


def _legacy_caps(merchant: dict) -> list[str]:
    """Repli pour les boutiques d'avant ce système (colonne vide) : ne rien régresser."""
    ids = ["vocal", "photos"]  # historiquement toujours actifs
    if merchant.get("cod_enabled"):
        ids.append("cod")
    if merchant.get("negotiation_enabled"):
        ids.append("negociation")
    if merchant.get("auto_prospect_enabled"):
        ids.append("prospection")
    return ids


def effective_capabilities(merchant: dict) -> set[str]:
    """Capacités RÉELLEMENT actives = socle + (choix ∩ accessibles), plafonné.

    Source de vérité unique pour tout le code. Robuste : si la colonne n'a jamais
    été réglée, on retombe sur les anciens interrupteurs (aucune régression).
    """
    plan = normalize_plan(merchant.get("plan"))
    chosen = parse_caps(merchant.get("enabled_capabilities"))
    if chosen is None:
        chosen = _legacy_caps(merchant)
    active: list[str] = []
    for cid in chosen:
        cap = BY_ID.get(cid)
        if cap and cap["group"] in ("module", "premium") and is_available(cap, plan):
            if cid not in active:
                active.append(cid)
    lim = module_limit(plan)
    if lim >= 0:
        active = active[:lim]
    return set(SOCLE_IDS) | set(active)


def has_capability(merchant: dict, cap_id: str) -> bool:
    return cap_id in effective_capabilities(merchant)


def selectable_for_plan(plan: str) -> list[dict]:
    """Liste pour l'UI : chaque capacité activable + `available` (sinon cadenas)."""
    plan = normalize_plan(plan)
    out = []
    for c in CAPABILITIES:
        if c["group"] in ("module", "premium"):
            out.append({**c, "available": is_available(c, plan)})
    return out


def sanitize_selection(plan: str, ids) -> list[str]:
    """Filtre un choix utilisateur → ids valides, accessibles au forfait, plafonnés.

    À utiliser AVANT d'enregistrer (la grille est appliquée côté serveur, jamais
    confiance au navigateur).
    """
    plan = normalize_plan(plan)
    lim = module_limit(plan)
    out: list[str] = []
    for raw in ids or []:
        cid = str(raw).strip().lower()
        cap = BY_ID.get(cid)
        if cap and cap["group"] in ("module", "premium") and is_available(cap, plan) and cid not in out:
            out.append(cid)
    if lim >= 0:
        out = out[:lim]
    return out


def capabilities_context(merchant: dict) -> dict:
    """Données prêtes pour le template « Composez votre vendeur »."""
    plan = normalize_plan(merchant.get("plan"))
    active = effective_capabilities(merchant)

    def _row(c: dict) -> dict:
        return {"id": c["id"], "label": c["label"], "promise": c["promise"],
                "icon": c.get("icon") or "i-check",
                "available": is_available(c, plan),
                "enabled": c["id"] in active,
                "min_plan": c["min_plan"],
                "min_plan_label": PLAN_LABELS.get(c["min_plan"], c["min_plan"])}

    socle = [{"id": c["id"], "label": c["label"], "promise": c["promise"],
              "icon": c.get("icon") or "i-check"}
             for c in CAPABILITIES if c["group"] == "socle"]
    modules = [_row(c) for c in CAPABILITIES if c["group"] == "module"]
    premium = [_row(c) for c in CAPABILITIES if c["group"] == "premium"]
    used = sum(1 for c in (modules + premium) if c["enabled"])
    lim = module_limit(plan)
    return {"plan": plan, "plan_label": PLAN_LABELS.get(plan, plan),
            "limit": lim, "unlimited": lim < 0, "used": used,
            "socle": socle, "modules": modules, "premium": premium}
