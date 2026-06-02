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
    # Vendeur WhatsApp face aux clients : léger, rapide, économique (gros volume)
    claude_model: str = "claude-haiku-4-5-20251001"
    # Ordres du commerçant (« piloter mon agent ») : Sonnet, raisonnement fiable
    manager_model: str = "claude-sonnet-4-6"
    # Création / génération du back-office & contenus riches : Opus, qualité max
    builder_model: str = "claude-opus-4-8"

    # --- Alertes Mongazi (réutilise le bot Telegram NOVA) ---
    telegram_bot_token: str = ""
    telegram_chat_id_mongazi: str = ""

    # --- Essai gratuit (démo sur la page de vente) ---
    free_trial_messages: int = 6              # nb de messages testables avant activation

    # --- Abonnement SaaS : comment le commerçant paie pour activer ---
    saas_price_fcfa: int = 5000               # prix mensuel d'activation
    saas_momo_number: str = ""                # TON numéro Mobile Money (Mongazi)
    saas_momo_name: str = "NEBULA Agency"     # nom affiché sur l'écran de paiement
    saas_momo_network: str = "MTN / Moov"     # réseaux acceptés

    # --- WhatsApp (numéro Vendora partagé, type sandbox Twilio) ---
    vendora_whatsapp_number: str = ""   # ex: +14155238886 (numéro sandbox Twilio)
    # Identifiants Twilio — requis UNIQUEMENT pour alerter le patron par WhatsApp
    # (étage 3). Le webhook entrant (TwiML) n'en a pas besoin. Dormant si vides.
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

    # --- Sécurité admin ---
    admin_token: str = ""

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
    "Agent vendeur sur WhatsApp 24h/24",
    "Catalogue de produits & services illimité",
    "Prise de commande automatique",
    "Alerte à chaque nouvelle commande",
    "Back-office de gestion en ligne",
    "Statistiques de ventes & conversations",
    "Techniques de vente (ventes additionnelles, relances)",
]
PLAN_EXTRA_FEATURES = {
    "demarrage": [
        ("5 ordres/jour pour piloter votre agent", True),
    ],
    "business": [
        ("30 ordres/jour pour piloter votre agent", True),
        ("Alerte commande aussi sur votre propre WhatsApp", False),
        ("Support prioritaire", True),
    ],
    "empire": [
        ("Ordres illimités pour piloter votre agent", True),
        ("Alerte commande aussi sur votre propre WhatsApp", False),
        ("Support prioritaire", True),
        ("Numéro WhatsApp dédié à votre boutique", False),
        ("Agent de prospection automatique de clients", False),
        ("Accompagnement personnalisé", True),
    ],
}


def normalize_plan(plan: str | None) -> str:
    p = (plan or "").strip().lower()
    return p if p in PLAN_PRICES else "demarrage"


def price_for_plan(plan: str | None) -> int:
    return PLAN_PRICES[normalize_plan(plan)]


def daily_orders_for_plan(plan: str | None) -> int:
    """Quota d'ordres/jour du forfait (-1 = illimité)."""
    return PLAN_DAILY_ORDERS[normalize_plan(plan)]
