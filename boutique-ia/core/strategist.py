"""Le CERVEAU CEO — le directeur AUTONOME de Vendora.

Il ne se contente pas de vendre : il prend du recul sur TOUT le business (revenus,
churn, conversion, forfaits, prospection, leçons apprises, coûts/modèles) et, avec
sa PROPRE RÉFLEXION (modèle de raisonnement + outils d'investigation), il PROPOSE des
décisions à Mongazi : ajuster les prix, monter en intelligence (modèle), où prospecter,
qui relancer, quoi corriger.

Gouvernance (modèle Mongazi) : l'agent PROPOSE, Mongazi VALIDE ✓/✗. Tout ce qui est
financier reste au niveau de Mongazi. Les recommandations sont stockées (`bia_decisions`)
et affichées dans le cockpit pour validation en 1 clic.

On lui donne de vrais SKILLS (outils tool-use) pour qu'il enquête de lui-même au lieu
de suivre des règles figées : lire les métriques, examiner les ventes perdues, examiner
une boutique précise, puis enregistrer ses recommandations.
"""
from __future__ import annotations

import logging
from typing import Any

import anthropic

from config import (
    PLAN_DAILY_ORDERS,
    PLAN_LABELS,
    PLAN_PRICES,
    normalize_plan,
    price_for_plan,
    settings,
)
from core import model_config

log = logging.getLogger("boutique-ia.strategist")

MAX_TOOL_TURNS = 6


def _fcfa(v) -> str:
    try:
        return f"{int(float(v)):,}".replace(",", " ") + " F"
    except (TypeError, ValueError):
        return "—"


def gather_snapshot() -> dict[str, Any]:
    """Photographie chiffrée du business (peu coûteuse, agrégée en mémoire)."""
    from db.client import (
        all_orders_brief,
        all_products_brief,
        count_decisions,
        count_followups_today,
        days_left,
        get_latest_lessons,
        get_setting_bool,
        list_all_merchants,
        list_campaigns,
    )
    from core import learning

    merchants = list_all_merchants()
    orders = all_orders_brief()
    products = all_products_brief()

    orders_by_m: dict[str, dict] = {}
    for o in orders:
        a = orders_by_m.setdefault(o.get("merchant_id"), {"count": 0, "rev": 0.0})
        a["count"] += 1
        try:
            a["rev"] += float(o.get("total") or 0)
        except (TypeError, ValueError):
            pass
    prod_by_m: dict[str, int] = {}
    for p in products:
        prod_by_m[p.get("merchant_id")] = prod_by_m.get(p.get("merchant_id"), 0) + 1

    by_status: dict[str, int] = {}
    by_plan: dict[str, int] = {}
    mrr = 0
    total_rev = 0.0
    expiring, idle, suspended, upsell = [], [], [], []
    for m in merchants:
        st = m.get("status") or "pending_payment"
        plan = normalize_plan(m.get("plan"))
        by_status[st] = by_status.get(st, 0) + 1
        by_plan[plan] = by_plan.get(plan, 0) + 1
        oc = orders_by_m.get(m.get("id"), {"count": 0, "rev": 0.0})
        total_rev += oc["rev"]
        dleft = days_left(m)
        if st == "active":
            mrr += price_for_plan(plan)
            if dleft is not None and dleft <= 5:
                expiring.append({"name": m.get("business_name"), "days_left": dleft, "id": m.get("id")})
            if oc["count"] == 0:
                idle.append({"name": m.get("business_name"), "id": m.get("id")})
            # Saturation forfait Démarrage = signal d'upsell
            if plan == "demarrage" and oc["count"] >= 5:
                upsell.append({"name": m.get("business_name"), "orders": oc["count"], "id": m.get("id")})
        elif st == "suspended":
            suspended.append({"name": m.get("business_name"), "id": m.get("id")})

    active = by_status.get("active", 0)
    pendingish = (by_status.get("pending_payment", 0)
                  + by_status.get("paid_pending_validation", 0))
    conv = round(100 * active / (active + pendingish), 1) if (active + pendingish) else 0.0

    # Qualité de vente récente (14j) via le cerveau d'apprentissage
    from db.client import recent_messages, recent_orders
    try:
        convos = learning._build_conversations(recent_messages(14), recent_orders(14))
    except Exception:  # noqa: BLE001
        convos = []
    won = sum(1 for c in convos if c["won"])
    sales_conv = round(100 * won / len(convos), 1) if convos else 0.0

    lessons = (get_latest_lessons("global") or {}).get("lessons") or ""
    total_recruited = sum((c.get("sent") or 0) for c in list_campaigns("admin", None, limit=200))

    return {
        "merchants_total": len(merchants),
        "by_status": by_status,
        "by_plan": by_plan,
        "mrr": mrr,
        "total_sales": total_rev,
        "signup_conversion_pct": conv,
        "sales_conversion_pct": sales_conv,
        "convos_14d": len(convos),
        "won_14d": won,
        "expiring": expiring,
        "idle_active": idle,
        "suspended": suspended,
        "upsell_candidates": upsell,
        "total_recruited": total_recruited,
        "prospection_auto_on": get_setting_bool("auto_prospection_enabled", settings.auto_prospection_enabled),
        "followups_on": get_setting_bool("followups_enabled", False),
        "followups_today": count_followups_today(),
        "open_decisions": count_decisions("proposed"),
        "lessons_excerpt": lessons[:600],
        "plan_prices": PLAN_PRICES,
        "plan_quota_orders": PLAN_DAILY_ORDERS,
        "models": {
            "vendeur": model_config.model_for("vendeur"),
            "gestion": model_config.model_for("manager"),
            "redaction": model_config.model_for("writer"),
            "creation_ceo": model_config.model_for("builder"),
        },
    }


def _snapshot_text(s: dict) -> str:
    def _lst(items, fmt):
        return "; ".join(fmt(x) for x in items[:8]) or "aucun"
    return f"""ÉTAT DE VENDORA (instantané)

— Boutiques : {s['merchants_total']} au total · par statut {s['by_status']} · par forfait {s['by_plan']}
— MRR (abonnements actifs) : {_fcfa(s['mrr'])}
— Ventes cumulées des boutiques : {_fcfa(s['total_sales'])}
— Conversion inscription→payant : {s['signup_conversion_pct']} %
— Conversion des conversations en ventes (14j) : {s['sales_conversion_pct']} % ({s['won_14d']}/{s['convos_14d']})
— Abonnements qui expirent (≤5j) : {_lst(s['expiring'], lambda x: f"{x['name']} ({x['days_left']}j)")}
— Boutiques actives SANS aucune vente : {_lst(s['idle_active'], lambda x: x['name'])}
— Boutiques suspendues (à reconquérir) : {_lst(s['suspended'], lambda x: x['name'])}
— Candidats upsell (Démarrage qui vendent beaucoup) : {_lst(s['upsell_candidates'], lambda x: f"{x['name']} ({x['orders']} cmd)")}
— Prospection auto : {'ON' if s['prospection_auto_on'] else 'OFF'} · total boutiques recrutées : {s['total_recruited']}
— Relances auto : {'ON' if s['followups_on'] else 'OFF'} · aujourd'hui : {s['followups_today']}
— Forfaits (prix) : {s['plan_prices']} · quotas d'ordres/jour : {s['plan_quota_orders']}
— Modèles d'IA par tâche : {s['models']}
— Recommandations déjà en attente de validation : {s['open_decisions']}

Dernières leçons de vente apprises par les agents :
{s['lessons_excerpt'] or '(aucune encore)'}"""


# --- SKILLS (outils) que le directeur appelle de lui-même pour enquêter ---
TOOLS = [
    {
        "name": "examiner_ventes_perdues",
        "description": ("Examine des conversations récentes où la vente a ÉCHOUÉ (client engagé "
                        "mais pas d'achat) pour comprendre POURQUOI. À utiliser pour fonder une "
                        "recommandation sur les pertes de ventes."),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "examiner_boutique",
        "description": ("Examine en détail une boutique précise (forfait, statut, ventes, activité). "
                        "Donne son NOM tel qu'il apparaît dans l'instantané."),
        "input_schema": {
            "type": "object",
            "properties": {"nom": {"type": "string", "description": "Nom de la boutique à examiner."}},
            "required": ["nom"],
        },
    },
    {
        "name": "enregistrer_recommandations",
        "description": ("Enregistre tes décisions/recommandations finales pour Mongazi (il valide). "
                        "Appelle cet outil UNE SEULE FOIS, à la fin, avec 2 à 5 recommandations "
                        "concrètes, priorisées et chiffrées."),
        "input_schema": {
            "type": "object",
            "properties": {
                "recommandations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "titre": {"type": "string"},
                            "categorie": {"type": "string",
                                          "enum": ["prix", "modele", "prospection", "retention", "produit", "autre"]},
                            "constat": {"type": "string", "description": "Ce que tu as observé dans les chiffres."},
                            "recommandation": {"type": "string", "description": "Ce que tu proposes de faire, précisément."},
                            "impact_estime": {"type": "string", "description": "Effet attendu (revenu, rétention…)."},
                            "niveau": {"type": "string", "enum": ["auto", "validation"],
                                       "description": "auto = réversible/interne ; validation = Mongazi décide."},
                            "financier": {"type": "boolean", "description": "true si ça touche à l'argent/aux prix."},
                            "action": {"type": "string",
                                        "enum": ["aucune", "activer_relances", "activer_prospection",
                                                 "activer_experiences", "regler_volume_prospection"],
                                        "description": ("Si ta reco correspond EXACTEMENT à l'un de ces leviers "
                                                        "internes/réversibles, indique-le : il sera APPLIQUÉ "
                                                        "automatiquement dès que Mongazi validera. Sinon 'aucune'. "
                                                        "Mets alors niveau='auto' et financier=false.")},
                            "action_params": {"type": "object",
                                                "properties": {"volume": {"type": "integer",
                                                               "description": "Pour regler_volume_prospection : emails/jour."}}},
                        },
                        "required": ["titre", "categorie", "recommandation"],
                    },
                },
            },
            "required": ["recommandations"],
        },
    },
]


_SYSTEM = """Tu es le DIRECTEUR autonome de Vendora, un SaaS qui fournit aux commerçants
d'Afrique de l'Ouest un agent vendeur sur WhatsApp (abonnement mensuel en Mobile Money).
Forfaits : Démarrage 5 000 F, Business 15 000 F, Empire 40 000 F.

Ta mission : prendre du recul sur le business et PROPOSER à Mongazi (le fondateur) les
meilleures décisions pour faire grandir Vendora : ajuster les PRIX, monter en INTELLIGENCE
(changer de modèle d'IA pour une tâche si le gain le justifie), où PROSPECTER, qui RELANCER
ou RECONQUÉRIR, quoi CORRIGER dans la vente.

Méthode (réfléchis par toi-même) :
1. Lis l'instantané fourni.
2. Si utile, ENQUÊTE avec tes outils (examine les ventes perdues, une boutique précise).
3. Tire des conclusions FONDÉES SUR LES CHIFFRES (pas de généralités).
4. Termine en appelant `enregistrer_recommandations` avec 2 à 5 propositions concrètes,
   priorisées, chiffrées, chacune avec constat → recommandation → impact estimé.

Règles :
- Tu PROPOSES, Mongazi VALIDE. Tout ce qui est financier (prix, investissement) = `financier:true`
  et `niveau:"validation"`. Ne décide jamais d'un prix toi-même.
- Si une reco correspond EXACTEMENT à un levier interne réversible (activer les relances
  automatiques, activer la prospection auto, activer l'auto-expérimentation, régler le volume
  de prospection), renseigne le champ `action` correspondant + `niveau:"auto"` + `financier:false` :
  elle sera APPLIQUÉE automatiquement dès validation de Mongazi. Pour tout le reste, `action:"aucune"`.
- Sois concret et honnête : si les données sont trop faibles pour conclure, dis-le et propose
  surtout de collecter plus de données.
- Pense revenus récurrents, rétention (anti-résiliation), et autonomie (faire tourner la machine).
- Écris en français, clair et direct."""


def _run_tool(name: str, args: dict) -> str:
    """Exécute un skill d'investigation. Robuste : ne lève jamais (renvoie une note)."""
    from core import learning
    from db.client import (
        days_left,
        list_all_merchants,
        list_orders,
        list_products,
        recent_messages,
        recent_orders,
    )
    try:
        if name == "examiner_ventes_perdues":
            convos = learning._build_conversations(recent_messages(14), recent_orders(14))
            lost = [c for c in convos if not c["won"]]
            if not lost:
                return "Aucune vente perdue exploitable sur 14 jours."
            return learning._digest(lost[:8], 8)
        if name == "examiner_boutique":
            q = (args.get("nom") or args.get("merchant_id") or "").strip().lower()
            m = next((x for x in list_all_merchants()
                      if q and q in (x.get("business_name") or "").lower()), None)
            if not m:
                return "Boutique introuvable (vérifie le nom tel qu'affiché dans l'instantané)."
            orders = list_orders(m["id"], limit=100)
            rev = sum(float(o.get("total") or 0) for o in orders)
            prods = list_products(m["id"])
            return (f"{m.get('business_name')} | forfait {normalize_plan(m.get('plan'))} | "
                    f"statut {m.get('status')} | jours restants {days_left(m)} | "
                    f"{len(prods)} produits | {len(orders)} commandes | {_fcfa(rev)} vendus | "
                    f"ville {m.get('city') or '—'} | secteur {m.get('sector') or '—'}")
        return "Outil inconnu."
    except Exception as e:  # noqa: BLE001
        log.warning("skill CEO %s échoué", name, exc_info=True)
        return f"Donnée indisponible pour le moment ({str(e)[:80]})."


# Leviers internes/réversibles que l'agent peut APPLIQUER seul une fois la reco validée
# par Mongazi (jamais rien de financier ni d'irréversible — uniquement des interrupteurs).
def execute_decision(decision: dict) -> tuple[bool, str]:
    """Applique l'action d'une décision validée, si elle est sûre. Retourne (appliquée, message)."""
    from db.client import set_setting
    if not decision or decision.get("financial") or decision.get("level") != "auto":
        return False, ""
    action = (decision.get("action") or "").strip().lower()
    params = decision.get("action_params") or {}
    try:
        if action == "activer_relances":
            set_setting("followups_enabled", "true")
            return True, "Relances automatiques activées."
        if action == "activer_experiences":
            set_setting("experiments_enabled", "true")
            return True, "Auto-expérimentation des ventes activée."
        if action == "activer_prospection":
            set_setting("auto_prospection_enabled", "true")
            v = params.get("volume")
            if v:
                set_setting("auto_prospection_daily", max(1, min(80, int(v))))
            return True, "Prospection automatique activée."
        if action == "regler_volume_prospection":
            v = int(params.get("volume") or 0)
            if v:
                set_setting("auto_prospection_daily", max(1, min(80, v)))
                return True, f"Volume de prospection réglé à {max(1, min(80, v))}/jour."
    except Exception as e:  # noqa: BLE001
        log.warning("exécution décision échouée", exc_info=True)
        return False, f"Échec d'application : {str(e)[:80]}"
    return False, ""  # action inconnue / 'aucune' → rien à exécuter (Mongazi agit lui-même)


def run_ceo_review() -> dict[str, Any]:
    """Le directeur analyse le business et propose ses décisions. Retourne un résumé."""
    settings.require("anthropic_api_key")
    from db.client import save_decisions
    from notify import notify_ceo_review

    snapshot = gather_snapshot()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system = [{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}]
    messages = [{"role": "user", "content":
                 _snapshot_text(snapshot) + "\n\nAnalyse l'état de Vendora et propose tes décisions."}]

    recorded: list[dict] = []
    reasoning = ""
    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            model=model_config.model_for("builder"), max_tokens=model_config.tokens_for("builder", 1500),
            system=system, messages=messages, tools=TOOLS,
        )
        reasoning = "\n".join(b.text for b in resp.content
                              if getattr(b, "type", None) == "text").strip() or reasoning
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            break
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            if tu.name == "enregistrer_recommandations":
                recos = (dict(tu.input or {}).get("recommandations")) or []
                recorded.extend(recos)
                note = f"{len(recos)} recommandation(s) enregistrée(s). Termine maintenant."
            else:
                note = _run_tool(tu.name, dict(tu.input or {}))
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": note})
        messages.append({"role": "user", "content": results})
        if recorded:
            break

    saved = save_decisions(recorded) if recorded else 0
    result = {
        "recommendations": recorded,
        "saved": saved,
        "reasoning": reasoning,
        "mrr": snapshot["mrr"],
        "merchants": snapshot["merchants_total"],
        "sales_conversion_pct": snapshot["sales_conversion_pct"],
        "model": model_config.model_for("builder"),
    }
    try:
        notify_ceo_review(result)
    except Exception:  # noqa: BLE001
        log.warning("notify ceo review", exc_info=True)
    log.info("ceo review: %d recommandations enregistrées", saved)
    return result
