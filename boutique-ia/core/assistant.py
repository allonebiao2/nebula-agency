"""L'ASSISTANT PERSONNEL — le copilote IA du/de la propriétaire de la boutique.

Distinct du VENDEUR (core/brain.py, qui parle aux CLIENTS) et du MANAGER
(core/manager.py, qui exécute les ordres de gestion : ajoute/modifie produit…).
Ici, la PATRONNE pose des questions et délègue, sur WhatsApp comme dans le
back-office : « combien de commandes aujourd'hui ? », « fais le point de la
semaine », « ce client était comment ? », « quelle heure ? », « où trouver X ? ».

Objectif : devenir SON assistant IA du quotidien (remplacer le réflexe ChatGPT),
et créer une vraie dépendance utile à Vendora.

3 VERROUS (décision produit) :
1. IDENTITÉ — `is_owner()` vérifie que c'est bien la patronne (numéro en liste
   blanche `owner_whatsapp`). Le serveur n'appelle l'assistant QUE pour elle :
   une cliente reste en mode vendeur et ne voit JAMAIS une donnée privée.
2. CHIFFRES RÉELS — tous les nombres (commandes, ventes, clients, RDV) viennent
   de VRAIES requêtes DB via des outils. Le modèle met en forme, n'invente jamais.
3. HONNÊTETÉ — pour le hors-boutique (culture générale, « où acheter »), aide au
   mieux mais reste honnête sur l'incertitude (pas d'adresse/prix inventés).
   L'heure/la date RÉELLES (Bénin) sont injectées, sinon le modèle devine faux.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone

import anthropic

from config import settings
from core import model_config
from db.client import (
    add_agenda_item,
    count_messages_since,
    due_agenda_reminders,
    list_agenda,
    list_appointments,
    list_orders,
    list_recent_conversations,
    load_assistant_history,
    load_history,
    list_products,
    mark_agenda_reminded,
    owner_active_within,
    save_assistant_message,
    set_agenda_status,
)

log = logging.getLogger("boutique-ia.assistant")

MAX_TOOL_TURNS = 4

# Bénin = WAT (UTC+1), pas de changement d'heure. Pour les frontières de "jour".
WAT = timezone(timedelta(hours=1))

_STATUS_FR = {
    "pending": "en attente",
    "paid_pending_validation": "payée (à valider)",
    "confirmed": "confirmée",
    "delivered": "livrée",
    "cancelled": "annulée",
}


# ---------------------------------------------------------------------------
# Verrou n°1 — identité : est-ce bien la patronne qui écrit ?
# ---------------------------------------------------------------------------

def _digits(s) -> str:
    return re.sub(r"\D", "", str(s or ""))


def is_owner(merchant: dict, customer: str | None) -> bool:
    """True si `customer` est le numéro du/de la propriétaire (liste blanche).

    Comparaison robuste sur les 8 derniers chiffres (partie abonné stable, qui
    survit aux formats +229 / 0… / espaces). `owner_whatsapp` peut contenir
    plusieurs numéros séparés par virgule/point-virgule. Vide → jamais owner
    (on reste en mode vendeur : c'est le défaut sûr).
    """
    raw = (merchant or {}).get("owner_whatsapp") or ""
    if not raw or not customer:
        return False
    cust = _digits(customer)
    if len(cust) < 8:
        return False
    cust8 = cust[-8:]
    for part in re.split(r"[,;/ ]+", str(raw)):
        own = _digits(part)
        if len(own) >= 8 and own[-8:] == cust8:
            return True
    return False


# ---------------------------------------------------------------------------
# Verrou n°2 — chiffres réels : helpers GROUNDED (toujours via la base)
# ---------------------------------------------------------------------------

def _to_float(v) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _to_int(v) -> int:
    try:
        return int(float(v or 0))
    except (TypeError, ValueError):
        return 0


def _money(v) -> str:
    return f"{int(round(_to_float(v))):,}".replace(",", " ") + " F CFA"


def _parse_dt(s):
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _now_wat() -> datetime:
    return datetime.now(WAT)


def _period_window(periode: str):
    """(start, end, label) en heure du Bénin. start=None pour « tout »."""
    now = _now_wat()
    today0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
    p = (periode or "").strip().lower()
    if p in ("hier", "yesterday"):
        return today0 - timedelta(days=1), today0, "hier"
    if p in ("semaine", "week", "7j", "7 jours", "cette semaine"):
        return now - timedelta(days=7), now, "7 derniers jours"
    if p in ("mois", "month", "30j", "30 jours", "ce mois"):
        return now - timedelta(days=30), now, "30 derniers jours"
    if p in ("tout", "total", "all", "global"):
        return None, now, "depuis le début"
    return today0, now, "aujourd'hui"  # défaut : aujourd'hui


def _orders_in(orders: list[dict], start, end) -> list[dict]:
    out = []
    for o in orders:
        dt = _parse_dt(o.get("created_at"))
        if dt is None:
            continue
        if start and dt < start:
            continue
        if end and dt > end:
            continue
        out.append(o)
    return out


def _items_label(items) -> str:
    parts = []
    for it in (items or []):
        name = (it.get("produit") or it.get("product") or "?")
        qty = _to_int(it.get("quantite") or it.get("qty") or 1)
        parts.append(f"{qty}× {name}" if qty != 1 else str(name))
    return ", ".join(parts) or "—"


def sales_report(merchant_id: str, periode: str = "aujourd_hui") -> str:
    """Rapport de ventes GROUNDED pour une période (commandes, CA, top produits)."""
    start, end, label = _period_window(periode)
    orders = _orders_in(list_orders(merchant_id, 500), start, end)
    n = len(orders)
    revenue = sum(_to_float(o.get("total")) for o in orders)
    buyers = {o.get("customer_whatsapp") for o in orders if o.get("customer_whatsapp")}

    counter: dict[str, int] = {}
    for o in orders:
        for it in (o.get("items") or []):
            name = (it.get("produit") or it.get("product") or "?")
            counter[name] = counter.get(name, 0) + _to_int(it.get("quantite") or it.get("qty") or 1)
    top = sorted(counter.items(), key=lambda kv: -kv[1])[:3]

    inbound = None
    if start is not None:
        try:
            inbound = count_messages_since(
                start.astimezone(timezone.utc).isoformat(), "customer", merchant_id)
        except Exception:  # noqa: BLE001
            inbound = None

    lines = [f"DONNÉES RÉELLES — {label} :",
             f"- Commandes : {n}",
             f"- Ventes : {_money(revenue)}",
             f"- Clients différents : {len(buyers)}"]
    if inbound is not None:
        lines.append(f"- Messages clients reçus : {inbound}")
    if top:
        lines.append("- Top produits : " + ", ".join(f"{name} (x{q})" for name, q in top))
    if n == 0:
        lines.append("(aucune commande sur cette période)")
    return "\n".join(lines)


def orders_list(merchant_id: str, periode: str = "aujourd_hui", limit: int = 15) -> str:
    """Liste détaillée des commandes d'une période (GROUNDED)."""
    start, end, label = _period_window(periode)
    orders = _orders_in(list_orders(merchant_id, 500), start, end)[:limit]
    if not orders:
        return f"DONNÉES RÉELLES — {label} : aucune commande."
    lines = [f"DONNÉES RÉELLES — commandes {label} ({len(orders)}) :"]
    for o in orders:
        dt = _parse_dt(o.get("created_at"))
        when = dt.astimezone(WAT).strftime("%d/%m %Hh%M") if dt else "?"
        who = o.get("customer_name") or o.get("customer_whatsapp") or "client"
        st = _STATUS_FR.get(o.get("status") or "", o.get("status") or "")
        lines.append(f"- {when} · {who} · {_items_label(o.get('items'))} · "
                     f"{_money(o.get('total'))} · {st}")
    return "\n".join(lines)


def appointments_view(merchant_id: str) -> str:
    """Rendez-vous à venir / récents (GROUNDED)."""
    appts = list_appointments(merchant_id, 20)
    if not appts:
        return "DONNÉES RÉELLES — aucun rendez-vous enregistré."
    lines = ["DONNÉES RÉELLES — derniers rendez-vous :"]
    for a in appts:
        who = a.get("customer_name") or a.get("customer_whatsapp") or "client"
        st = _STATUS_FR.get(a.get("status") or "", a.get("status") or "")
        svc = a.get("service") or "RDV"
        when = a.get("requested_time") or "?"
        lines.append(f"- {svc} · {who} · souhaité : {when} · {st}")
    return "\n".join(lines)


def client_info(merchant_id: str, recherche: str) -> str:
    """Dossier GROUNDED d'un client : commandes, dépense, dernier contact, sujet."""
    q = (recherche or "").strip()
    if not q:
        return "Indiquez le nom ou le numéro du client à chercher."
    qd = _digits(q)
    ql = q.lower()

    orders = list_orders(merchant_id, 500)
    convos = list_recent_conversations(merchant_id, limit=60)

    # Trouver le numéro client correspondant (par numéro, sinon par nom de commande).
    target = None
    if len(qd) >= 6:
        for o in orders:
            if qd[-6:] in _digits(o.get("customer_whatsapp")):
                target = o.get("customer_whatsapp")
                break
        if not target:
            for c in convos:
                if qd[-6:] in _digits(c.get("customer")):
                    target = c.get("customer")
                    break
    if not target:
        for o in orders:
            if ql and ql in (o.get("customer_name") or "").lower():
                target = o.get("customer_whatsapp")
                break
    if not target:
        return (f"Aucun client trouvé pour « {q} ». "
                "Essayez avec son numéro WhatsApp ou le nom exact d'une commande.")

    his_orders = [o for o in orders if o.get("customer_whatsapp") == target]
    spent = sum(_to_float(o.get("total")) for o in his_orders)
    name = next((o.get("customer_name") for o in his_orders if o.get("customer_name")), None) or target

    last_msg, last_when = None, None
    for c in convos:
        if c.get("customer") == target:
            last_msg = c.get("last")
            dt = _parse_dt(c.get("last_at"))
            last_when = dt.astimezone(WAT).strftime("%d/%m %Hh%M") if dt else None
            break
    try:
        nb_msgs = len(load_history(merchant_id, target, limit=200))
    except Exception:  # noqa: BLE001
        nb_msgs = 0

    lines = [f"DONNÉES RÉELLES — client {name} ({target}) :",
             f"- Commandes : {len(his_orders)} · Total dépensé : {_money(spent)}",
             f"- Messages échangés : {nb_msgs}"]
    if his_orders:
        last = his_orders[0]
        dt = _parse_dt(last.get("created_at"))
        when = dt.astimezone(WAT).strftime("%d/%m") if dt else "?"
        st = _STATUS_FR.get(last.get("status") or "", last.get("status") or "")
        lines.append(f"- Dernière commande ({when}) : {_items_label(last.get('items'))} "
                     f"· {_money(last.get('total'))} · {st}")
    if last_msg:
        lines.append(f"- Dernier échange{f' ({last_when})' if last_when else ''} : "
                     f"« {last_msg[:120]} »")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Phase B — Agenda / rappels (ÉCRITURE) : « note-moi… », « rappelle-moi… »
# ---------------------------------------------------------------------------

def _iso_to_utc(value) -> str | None:
    """Normalise un ISO (idéalement en WAT) vers un timestamptz UTC, sinon None."""
    dt = _parse_dt(value)
    return dt.astimezone(timezone.utc).isoformat() if dt else None


def agenda_add(merchant_id: str, titre: str, quand_texte: str | None = None,
               rappel_iso: str | None = None) -> str:
    titre = (titre or "").strip()
    if not titre:
        return "(rien à noter : intitulé manquant)"
    remind_at = _iso_to_utc(rappel_iso)
    row = add_agenda_item(merchant_id, titre, (quand_texte or "").strip() or None, remind_at)
    if not row:
        return "(impossible d'enregistrer dans l'agenda pour l'instant)"
    quand = f" — {quand_texte.strip()}" if (quand_texte or "").strip() else ""
    rappel = " · rappel programmé ✅" if remind_at else ""
    return f"NOTÉ dans l'agenda : « {titre} »{quand}{rappel}"


def agenda_view(merchant_id: str, scope: str = "upcoming") -> str:
    items = list_agenda(merchant_id, "upcoming" if scope not in ("done", "all") else scope)
    if not items:
        return "DONNÉES RÉELLES — agenda vide (rien de prévu)."
    lines = ["DONNÉES RÉELLES — agenda :"]
    for it in items:
        dt = _parse_dt(it.get("remind_at"))
        quand = (dt.astimezone(WAT).strftime("%d/%m %Hh%M") if dt
                 else (it.get("when_text") or "sans date"))
        flag = "✅ " if it.get("status") == "done" else ""
        lines.append(f"- [id={it.get('id')}] {flag}{it.get('title')} ({quand})")
    lines.append("(pour terminer/supprimer un point, utilise son id)")
    return "\n".join(lines)


def agenda_set(merchant_id: str, agenda_id: str, status: str) -> str:
    row = set_agenda_status((agenda_id or "").strip(), merchant_id, status)
    if not row:
        return "(point d'agenda introuvable — vérifie l'id via voir_agenda)"
    verb = "marqué comme fait ✅" if status == "done" else "supprimé"
    return f"« {row.get('title')} » {verb}."


# ---------------------------------------------------------------------------
# Le cerveau de l'assistant — outils (lecture + agenda) + intelligence générale
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "rapport_ventes",
        "description": ("Chiffres de vente RÉELS de la boutique sur une période : nombre de "
                        "commandes, total des ventes, clients, top produits. À appeler pour "
                        "« combien de commandes / de ventes », « fais le point », « bilan »."),
        "input_schema": {
            "type": "object",
            "properties": {
                "periode": {"type": "string",
                            "enum": ["aujourd_hui", "hier", "semaine", "mois", "tout"],
                            "description": "Période voulue (défaut : aujourd_hui)."},
            },
        },
    },
    {
        "name": "liste_commandes",
        "description": ("Liste DÉTAILLÉE des commandes RÉELLES d'une période (date, client, "
                        "articles, montant, statut). À appeler pour « montre les commandes », "
                        "« qui a commandé », « quelles commandes aujourd'hui »."),
        "input_schema": {
            "type": "object",
            "properties": {
                "periode": {"type": "string",
                            "enum": ["aujourd_hui", "hier", "semaine", "mois", "tout"]},
            },
        },
    },
    {
        "name": "info_client",
        "description": ("Dossier RÉEL d'un client : ses commandes, ce qu'il a dépensé, son "
                        "dernier contact et le dernier sujet. À appeler pour « ce client était "
                        "comment », « parle-moi de X », « combien a dépensé X »."),
        "input_schema": {
            "type": "object",
            "properties": {
                "recherche": {"type": "string", "description": "Nom ou numéro du client."},
            },
            "required": ["recherche"],
        },
    },
    {
        "name": "rendez_vous",
        "description": ("Liste RÉELLE des rendez-vous CLIENTS enregistrés (pris par le vendeur). "
                        "À appeler pour « mes rendez-vous clients », « qui vient »."),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "noter_agenda",
        "description": ("Enregistre une note ou un RAPPEL dans l'agenda PERSONNEL du patron. À "
                        "appeler pour « note-moi… », « rappelle-moi… », « ajoute à mon agenda… ». "
                        "Si un moment est donné (demain 15h, lundi, vendredi…), calcule-le à partir "
                        "de la date/heure actuelles et passe-le dans `rappel_iso` (ISO 8601 avec "
                        "fuseau +01:00), EN PLUS de `quand_texte`."),
        "input_schema": {
            "type": "object",
            "properties": {
                "titre": {"type": "string", "description": "Ce qu'il faut retenir / faire."},
                "quand_texte": {"type": "string", "description": "Le moment tel que dit (ex: demain 15h)."},
                "rappel_iso": {"type": "string", "description": "Moment exact ISO 8601 +01:00 si datable."},
            },
            "required": ["titre"],
        },
    },
    {
        "name": "voir_agenda",
        "description": ("Liste l'agenda PERSONNEL du patron (ses notes/rappels). À appeler pour "
                        "« mon agenda », « qu'est-ce que j'ai prévu », « mes rappels », ou avant de "
                        "terminer/supprimer un point (pour avoir son id)."),
        "input_schema": {
            "type": "object",
            "properties": {
                "scope": {"type": "string", "enum": ["upcoming", "done", "all"],
                          "description": "upcoming = à faire (défaut)."},
            },
        },
    },
    {
        "name": "terminer_agenda",
        "description": "Marque un point d'agenda comme FAIT. Utilise l'id exact donné par voir_agenda.",
        "input_schema": {
            "type": "object",
            "properties": {"agenda_id": {"type": "string"}},
            "required": ["agenda_id"],
        },
    },
    {
        "name": "supprimer_agenda",
        "description": "Supprime un point d'agenda. Utilise l'id exact donné par voir_agenda.",
        "input_schema": {
            "type": "object",
            "properties": {"agenda_id": {"type": "string"}},
            "required": ["agenda_id"],
        },
    },
]


def _exec_tool(merchant_id: str, name: str, args: dict) -> str:
    try:
        if name == "rapport_ventes":
            return sales_report(merchant_id, args.get("periode") or "aujourd_hui")
        if name == "liste_commandes":
            return orders_list(merchant_id, args.get("periode") or "aujourd_hui")
        if name == "info_client":
            return client_info(merchant_id, args.get("recherche") or "")
        if name == "rendez_vous":
            return appointments_view(merchant_id)
        if name == "noter_agenda":
            return agenda_add(merchant_id, args.get("titre") or "",
                              args.get("quand_texte"), args.get("rappel_iso"))
        if name == "voir_agenda":
            return agenda_view(merchant_id, args.get("scope") or "upcoming")
        if name == "terminer_agenda":
            return agenda_set(merchant_id, args.get("agenda_id") or "", "done")
        if name == "supprimer_agenda":
            return agenda_set(merchant_id, args.get("agenda_id") or "", "cancelled")
    except Exception as e:  # noqa: BLE001
        log.exception("outil assistant échoué")
        return f"(impossible de lire cette donnée pour l'instant : {e})"
    return "(outil inconnu)"


def _system(merchant: dict) -> str:
    name = merchant.get("business_name") or "la boutique"
    now = _now_wat()
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"]
    date_fr = f"{jours[now.weekday()]} {now.day} {mois[now.month]} {now.year}, {now:%Hh%M}"
    nb_produits = 0
    try:
        nb_produits = len([p for p in list_products(merchant["id"]) if p.get("available") is not False])
    except Exception:  # noqa: BLE001
        pass

    return f"""Tu es l'ASSISTANT PERSONNEL du/de la propriétaire de la boutique « {name} ».
Tu n'écris PAS à un client : tu parles à la PATRONNE / au PATRON, en privé. Tu es
son copilote IA de confiance, son bras droit. Tu l'aides sur DEUX plans.

1) SA BOUTIQUE — tu connais ses données réelles. Pour TOUT chiffre ou fait sur la
   boutique (commandes, ventes, clients, rendez-vous), tu DOIS appeler l'outil
   correspondant et utiliser SON résultat tel quel. Tu n'inventes JAMAIS un
   chiffre, un nom ou une commande. Le catalogue compte {nb_produits} produit(s) actifs.

2) TOUT LE RESTE — comme un assistant brillant et polyvalent : réponds à ses
   questions générales, donne des idées, explique, calcule, rédige un message ou
   un texte pour elle, conseille-la pour son business. Sois utile, malin, concret.

Date et heure actuelles (Bénin, heure locale) : {date_fr}.
Utilise-les pour toute question d'heure, de date ou de jour.

AGENDA — tu tiens son agenda perso et tu peux le lui rappeler (outils noter_agenda /
voir_agenda / terminer_agenda / supprimer_agenda). Quand il dit « note-moi… »,
« rappelle-moi… », « ajoute à mon agenda… » : appelle noter_agenda. S'il précise
un moment (demain 15h, lundi, samedi…), calcule le moment EXACT à partir de la
date/heure ci-dessus et passe-le en `rappel_iso` (ISO 8601, fuseau +01:00), en plus
de `quand_texte`. Pour terminer ou supprimer un point, appelle d'abord voir_agenda
pour récupérer son id. Confirme toujours brièvement ce que tu as noté.

HONNÊTETÉ (capital) : si tu n'es pas sûr d'un fait précis (une adresse, un prix
ailleurs, une info locale, une actu récente), dis-le simplement et propose
comment le vérifier. Ne fabrique jamais un fait précis : mieux vaut « je ne suis
pas sûr » que de te tromper. C'est ce qui fait qu'elle te fait confiance.

STYLE : WhatsApp — réponses courtes, naturelles, directes, chaleureuses. 1-2
emojis maximum. Pas de markdown lourd (pas de **, pas de #). Pour une liste de
chiffres, des petits tirets suffisent. Va droit au but. Tutoie ou vouvoie selon
elle ; par défaut, reste poli et proche."""


def reply(merchant: dict, question: str, history: list[dict] | None = None) -> str:
    """Réponse de l'assistant personnel à la patronne. `history` optionnel
    (liste [{role:'user'|'assistant', content}]) pour un fil multi-tours."""
    settings.require("anthropic_api_key")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    merchant_id = merchant["id"]

    system = [{"type": "text", "text": _system(merchant),
               "cache_control": {"type": "ephemeral"}}]
    messages: list[dict] = []
    for h in (history or []):
        role = "assistant" if h.get("role") == "assistant" else "user"
        content = (h.get("content") or "").strip()
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": (question or "").strip() or "Bonjour"})

    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            model=model_config.model_for("manager"),
            max_tokens=model_config.tokens_for("manager", 700),
            system=system, messages=messages, tools=TOOLS,
        )
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            text = "\n".join(b.text for b in resp.content
                             if getattr(b, "type", None) == "text").strip()
            return text or "Je suis là 🙂 Que voulez-vous savoir ?"
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            note = _exec_tool(merchant_id, tu.name, dict(tu.input or {}))
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": note})
        messages.append({"role": "user", "content": results})

    # Dernier tour sans outil pour conclure proprement.
    resp = client.messages.create(
        model=model_config.model_for("manager"),
        max_tokens=model_config.tokens_for("manager", 500),
        system=system, messages=messages,
    )
    text = "\n".join(b.text for b in resp.content
                     if getattr(b, "type", None) == "text").strip()
    return text or "Je suis là 🙂 Que voulez-vous savoir ?"


def converse(merchant: dict, question: str, channel: str = "whatsapp") -> str:
    """Point d'entrée des DEUX canaux (WhatsApp owner + back-office) : charge la
    mémoire de fil, répond, puis mémorise le tour. Ne lève jamais (repli gracieux)
    pour que le patron reçoive toujours une réponse d'assistant."""
    merchant_id = merchant["id"]
    q = (question or "").strip()
    try:
        history = load_assistant_history(merchant_id, limit=10)
    except Exception:  # noqa: BLE001
        history = []
    try:
        text = reply(merchant, q, history=history)
    except Exception:  # noqa: BLE001
        log.exception("assistant converse échoué")
        text = "Désolé, j'ai eu un petit souci pour traiter ça 🙏 Reformulez en un mot ?"
    try:
        save_assistant_message(merchant_id, "user", q, channel)
        save_assistant_message(merchant_id, "assistant", text, channel)
    except Exception:  # noqa: BLE001
        pass
    return text


def run_assistant_reminders() -> dict:
    """Pousse les rappels d'agenda échus au patron — UNIQUEMENT dans la fenêtre
    WhatsApp 24h (conversation de service = gratuit/conforme Meta). Hors fenêtre,
    le rappel reste en attente (il partira au prochain message du patron)."""
    from core import whatsapp_meta
    from db.client import get_merchant, get_setting_bool

    if not get_setting_bool("assistant_reminders_enabled", True):
        return {"sent": 0, "skipped": 0, "off": True}
    if not whatsapp_meta.configured():
        return {"sent": 0, "skipped": 0, "no_wa": True}

    sent = skipped = 0
    for item in due_agenda_reminders(50):
        mid = item.get("merchant_id")
        merchant = get_merchant(mid) if mid else None
        owner = (merchant or {}).get("owner_whatsapp")
        if not merchant or not owner or merchant.get("status") == "suspended":
            skipped += 1
            continue
        if not owner_active_within(mid, 24):  # hors fenêtre 24h → on attend
            skipped += 1
            continue
        when = (item.get("when_text") or "").strip()
        body = f"⏰ Rappel : {item.get('title')}" + (f" ({when})" if when else "")
        ok = False
        try:
            ok = whatsapp_meta.send_text(owner, body)
        except Exception:  # noqa: BLE001
            log.warning("envoi rappel agenda échoué", exc_info=True)
        if ok:
            mark_agenda_reminded(item["id"])
            sent += 1
        else:
            skipped += 1
    return {"sent": sent, "skipped": skipped}
