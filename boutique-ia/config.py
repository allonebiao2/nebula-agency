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

    # --- IA (étage 2) ---
    anthropic_api_key: str = ""
    claude_model: str = "claude-haiku-4-5-20251001"  # léger + rapide + bon marché pour la vente WhatsApp

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


def normalize_plan(plan: str | None) -> str:
    p = (plan or "").strip().lower()
    return p if p in PLAN_PRICES else "demarrage"


def price_for_plan(plan: str | None) -> int:
    return PLAN_PRICES[normalize_plan(plan)]
