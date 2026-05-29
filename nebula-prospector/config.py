"""Configuration centralisée chargée depuis .env."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
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

    # --- Vague 1 ---
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""           # exposée au navigateur (dashboard)
    anthropic_api_key: str = ""
    google_maps_api_key: str = ""

    # --- Vague 2 ---
    hunter_api_key: str = ""

    # --- Vague 3 ---
    resend_api_key: str = ""
    email_from_address: str = ""
    email_from_name: str = ""
    email_reply_to: str = ""

    # --- Vague 4 ---
    imap_host: str = ""
    imap_port: int = 993
    imap_user: str = ""
    imap_password: str = ""

    # --- Vague 5 ---
    telegram_bot_token: str = ""
    telegram_chat_id_mongazi: str = ""

    # --- Opérationnel ---
    max_emails_per_day: int = 25
    min_delay_between_emails_seconds: int = 120
    sourcing_max_results_per_query: int = 60

    target_countries: str = "BJ,TG,CI,SN,BF"
    target_cities: str = "Cotonou,Lomé,Abidjan,Dakar,Ouagadougou,Porto-Novo,Parakou"

    claude_model_fast: str = "claude-sonnet-4-6"
    claude_model_deep: str = "claude-opus-4-7"

    env: str = "development"
    log_level: str = "INFO"

    @property
    def target_countries_list(self) -> list[str]:
        return [c.strip() for c in self.target_countries.split(",") if c.strip()]

    @property
    def target_cities_list(self) -> list[str]:
        return [c.strip() for c in self.target_cities.split(",") if c.strip()]

    def require(self, *keys: str) -> None:
        """Lève si une clé est manquante. À appeler au début d'un module."""
        missing = [k for k in keys if not getattr(self, k, None)]
        if missing:
            raise RuntimeError(
                f"Configuration manquante dans .env : {', '.join(missing)}. "
                f"Voir .env.example pour les instructions."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
