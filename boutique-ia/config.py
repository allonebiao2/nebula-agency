"""Configuration centralisée Boutique IA — chargée depuis .env.

Réutilise les mêmes credentials Supabase / Telegram que NOVA si tu veux :
copie-colle simplement les valeurs depuis nebula-prospector/.env.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Marque du produit (change ici pour renommer partout) ---
    product_name: str = "Vendora"
    product_tagline: str = "L'agent vendeur doté d'intelligence artificielle pour votre boutique"

    # --- Supabase (mêmes que NOVA possible) ---
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # --- IA : un modèle par tâche (qualité ↔ coût) ---
    anthropic_api_key: str = ""
    # RÈGLE MODÈLES (validée Mongazi) : Sonnet pour TOUT le texte client (réponses
    # du vendeur + rédaction) ; Opus réservé au lourd créatif (visuels, images,
    # back-office luxueux adapté au client + mobile, raisonnement CEO). Jamais Opus
    # sur les réponses client (coût + pas nécessaire) ; Sonnet > Haiku pour vendre.
    # Vendeur WhatsApp face aux clients : Sonnet (qualité de vente = revenu)
    claude_model: str = "claude-sonnet-4-6"
    # Ordres du commerçant (« piloter mon agent ») : Sonnet, raisonnement fiable
    manager_model: str = "claude-sonnet-4-6"
    # Rédaction (emails de prospection, copies de vente) : Sonnet = qualité/coût optimal
    writer_model: str = "claude-sonnet-4-6"
    # Lourd créatif uniquement (visuels/images/back-office, raisonnement CEO) : Opus
    builder_model: str = "claude-opus-4-8"

    # --- Alertes Mongazi (réutilise le bot Telegram NOVA) ---
    telegram_bot_token: str = ""
    telegram_chat_id_mongazi: str = ""

    # --- Essai gratuit (démo sur la page de vente) ---
    free_trial_messages: int = 6              # nb de messages testables avant activation

    # --- Anti-spam : plafond de messages d'UN client / 24h (au-delà → l'agent se tait,
    #     pas d'appel modèle = protection tokens). Très haut → seul l'abus est bloqué. ---
    customer_daily_msg_cap: int = 60

    # --- Abonnement SaaS : comment le commerçant paie pour activer ---
    saas_price_fcfa: int = 5000               # prix mensuel d'activation
    saas_momo_number: str = ""                # TON numéro Mobile Money (Mongazi)
    saas_momo_name: str = "NEBULA Agency"     # nom affiché sur l'écran de paiement
    saas_momo_network: str = "MTN / Moov"     # réseaux acceptés

    # --- WhatsApp (numéro Vendora partagé, type sandbox Twilio) ---
    vendora_whatsapp_number: str = ""   # ex: +14155238886 (numéro sandbox Twilio)
    # Identifiants Twilio — requis UNIQUEMENT pour alerter le patron par WhatsApp
    # (étage 3) + télécharger les vocaux WhatsApp. Le webhook TwiML n'en a pas besoin.
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

    # --- WhatsApp PRODUCTION — Meta Cloud API (Pilier 2, gratuit, sans Twilio) ---
    # Dormant tant que ces vars ne sont pas posées : le sandbox Twilio reste actif.
    whatsapp_token: str = ""              # token d'accès Cloud API (System User, longue durée)
    whatsapp_phone_number_id: str = ""    # ID du numéro WhatsApp (dans Meta)
    whatsapp_verify_token: str = ""       # jeton de vérification du webhook (choisi par nous)
    whatsapp_app_secret: str = ""         # secret de l'app (signature des webhooks, optionnel)
    whatsapp_graph_version: str = "v21.0"

    # --- Messenger + Instagram Direct (inbound, même Graph API que WhatsApp) ---
    # Dormant tant que `messenger_page_token` n'est pas posé : l'agent ne répond
    # ni sur Messenger ni sur Instagram. Le PAGE token couvre les deux (l'IG est
    # rattaché à la Page Facebook). Le jeton de vérif retombe sur celui de WhatsApp.
    messenger_page_token: str = ""        # Page Access Token (longue durée, System User)
    messenger_verify_token: str = ""      # jeton de vérif du webhook (sinon = whatsapp_verify_token)

    # --- Transcription des messages vocaux (booster) — Groq Whisper (gratuit) ---
    groq_api_key: str = ""
    groq_whisper_model: str = "whisper-large-v3-turbo"

    # --- Sécurité admin ---
    admin_token: str = ""
    # Secret pour signer les sessions du back-office commerçant (cookie).
    # Si vide, on retombe sur admin_token. À définir en prod pour plus de robustesse.
    session_secret: str = ""

    # --- Prospection (étage 5) — envoi via Resend (API HTTP, marche sur Railway) ---
    # ⚠️ Railway bloque le SMTP sortant → on N'UTILISE PAS Gmail SMTP en prod.
    resend_api_key: str = ""                          # réutilise la clé NOVA
    email_from_address: str = "contact@nebula-agency.com"  # domaine vérifié sur Resend
    email_from_name: str = "Mongazi · NEBULA Agency"
    email_reply_to: str = ""          # adresse de réponse par défaut (admin/recrutement)
    # (Gmail SMTP gardé en repli local uniquement ; inutile sur Railway)
    gmail_user: str = ""
    gmail_app_password: str = ""
    # Boîte entrante : l'agent ne lit QUE ce libellé Gmail (JAMAIS toute la boîte
    # perso). Un filtre Gmail applique ce libellé aux réponses Vendora. Si le
    # libellé n'existe pas → l'agent ne lit RIEN (sécurité : boîte perso intouchée).
    inbox_mailbox: str = "Vendora"
    gmail_daily_cap: int = 90         # plafond global d'envois/jour (sécurité)
    prospection_admin_daily: int = 60 # quota/jour pour les campagnes admin (recrutement)
    # URL publique (pour le lien de désinscription dans les emails de prospection)
    public_base_url: str = "https://vendora-agent.up.railway.app"

    # --- Abonnement (facturation MoMo direct, cycle automatique) ---
    subscription_days: int = 30      # durée d'un abonnement après validation paiement
    reminder_days: int = 3           # relance quand il reste ≤ N jours

    # --- Recrutement AUTONOME (Vendora se trouve des clients tout seul) ---
    auto_prospection_enabled: bool = False   # interrupteur maître (OFF = sécurité)
    auto_prospection_daily: int = 12         # volume/jour (échauffement ; monter progressivement)
    auto_prospection_hour: int = 9           # heure UTC de lancement quotidien

    env: str = "development"

    def require(self, *keys: str) -> None:
        missing = [k for k in keys if not getattr(self, k, None)]
        if missing:
            raise RuntimeError(
                f"Configuration manquante dans .env : {', '.join(missing)}. "
                f"Voir .env.example."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


# --- Offres (le prix dépend de l'offre choisie) ---
PLAN_PRICES = {
    "demarrage": 5000,
    "business": 15000,
    "empire": 40000,
}
PLAN_LABELS = {
    "demarrage": "Démarrage",
    "business": "Business",
    "empire": "Empire",
}

# Nombre d'ORDRES/jour que le commerçant peut donner à son agent depuis le
# back-office (piloter sa boutique en langage naturel). Vrai différenciateur,
# réellement appliqué côté serveur. -1 = illimité.
PLAN_DAILY_ORDERS = {
    "demarrage": 5,
    "business": 30,
    "empire": -1,   # illimité
}

# Fonctionnalités affichées par forfait sur le back-office (UNIQUEMENT des
# fonctions réelles de Vendora). `live=False` = annoncé « Bientôt » (honnête).
# Les fonctions communes (live aujourd'hui) sont héritées par tous les forfaits.
PLAN_CORE_FEATURES = [
    "Agent vendeur WhatsApp 24h/24 + prise de commande",
    "Catalogue de produits & services illimité",
    "Alerte à chaque commande + client chaud",
    "Back-office + « Composez votre vendeur »",
    "Statistiques de ventes & conversations",
]
PLAN_EXTRA_FEATURES = {
    "demarrage": [
        ("2 super-pouvoirs au choix : vocaux, photos, paiement à la livraison, marchandage", True),
        ("5 ordres/jour pour piloter votre agent", True),
    ],
    "business": [
        ("5 super-pouvoirs au choix : relances auto, rendez-vous, réseaux sociaux (calendrier), photos, marchandage…", True),
        ("30 ordres/jour pour piloter votre agent", True),
        ("Tableau de bord des ventes + support prioritaire", True),
    ],
    "empire": [
        ("Tous les super-pouvoirs + ordres illimités", True),
        ("Coach commercial : conseils chiffrés pour vendre plus", True),
        ("Réseaux sociaux : posts planifiés + images de marque", True),
        ("S'améliore sur VOTRE boutique + accompagnement personnalisé", True),
    ],
}

# Prospection autonome : nb d'emails/jour selon le forfait (vrai différenciateur).
PLAN_PROSPECTION_DAILY = {
    "demarrage": 0,    # non inclus → upsell
    "business": 20,
    "empire": 50,
}

# ── Metering : conversations CLIENTS incluses par forfait (par MOIS calendaire).
# RÈGLE D'OR : le vendeur n'est JAMAIS coupé (soft cap). Ces nombres servent à
# PACKAGER la valeur + déclencher recharge/upgrade, jamais à brider une vente.
# Limites volontairement GÉNÉREUSES (le coût réel par conversation sur Haiku est
# faible) → invisibles pour un usage normal. -1 = illimité (fair-use). Décision
# financière de Mongazi (ajustable ici sans risque : pur affichage + nudge).
PLAN_CONV_INCLUDED = {
    "demarrage": 300,    # ~10 conversations/jour
    "business": 1200,    # ~40/jour
    "empire": -1,        # illimité
}

# Recharges de crédits = conversations SUPPLÉMENTAIRES (modèle prépayé MoMo, sans
# expiration courte → de la valeur, pas une punition). Prix DÉGRESSIF voulu : le
# petit pack coûte plus cher/conversation que le tarif d'un forfait, pour que
# recharger en boucle pousse NATURELLEMENT vers l'upgrade. Montants = à valider
# par Mongazi (financier). Encaissement = MoMo manuel (l'admin crédite après).
CREDIT_PACKS = [
    {"id": "pack100",  "conversations": 100,  "price": 2000},   # 20 F/conv
    {"id": "pack300",  "conversations": 300,  "price": 5000},   # ~16,7 F/conv
    {"id": "pack1000", "conversations": 1000, "price": 12000},  # 12 F/conv (~ tarif Business)
]
CREDIT_PACKS_BY_ID = {p["id"]: p for p in CREDIT_PACKS}


def normalize_plan(plan: str | None) -> str:
    p = (plan or "").strip().lower()
    return p if p in PLAN_PRICES else "demarrage"


def price_for_plan(plan: str | None) -> int:
    return PLAN_PRICES[normalize_plan(plan)]


def daily_orders_for_plan(plan: str | None) -> int:
    """Quota d'ordres/jour du forfait (-1 = illimité)."""
    return PLAN_DAILY_ORDERS[normalize_plan(plan)]


def conv_included_for_plan(plan: str | None) -> int:
    """Conversations clients incluses/mois du forfait (-1 = illimité)."""
    return PLAN_CONV_INCLUDED[normalize_plan(plan)]


def prospection_daily_for_plan(plan: str | None) -> int:
    """Quota d'emails de prospection/jour du forfait (0 = non inclus)."""
    return PLAN_PROSPECTION_DAILY[normalize_plan(plan)]
