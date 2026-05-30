"""Setup Telegram pour NOVA — colle le token et le chat ID dans .env + teste.

Usage :
    python scripts/setup_telegram.py
    python scripts/setup_telegram.py <token> <chat_id>
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"


def update_env(token: str, chat_id: str) -> None:
    """Met à jour ou ajoute TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID_MONGAZI dans .env."""
    if not ENV_PATH.exists():
        ENV_PATH.touch()

    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    updated_token = False
    updated_chat = False
    new_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("TELEGRAM_BOT_TOKEN="):
            new_lines.append(f"TELEGRAM_BOT_TOKEN={token}")
            updated_token = True
        elif stripped.startswith("TELEGRAM_CHAT_ID_MONGAZI="):
            new_lines.append(f"TELEGRAM_CHAT_ID_MONGAZI={chat_id}")
            updated_chat = True
        else:
            new_lines.append(line)

    if not updated_token:
        new_lines.append(f"TELEGRAM_BOT_TOKEN={token}")
    if not updated_chat:
        new_lines.append(f"TELEGRAM_CHAT_ID_MONGAZI={chat_id}")

    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"✓ .env mis à jour ({ENV_PATH})")


def main() -> int:
    print()
    print("🔔  Setup Telegram pour NOVA")
    print("━" * 50)

    # Args en ligne de commande OU prompts interactifs
    if len(sys.argv) == 3:
        token = sys.argv[1].strip()
        chat_id = sys.argv[2].strip()
        print(f"  Token   : ...{token[-8:]}")
        print(f"  Chat ID : {chat_id}")
    else:
        print("\n  1) Va dans Telegram → @BotFather → /newbot pour créer le bot")
        print("  2) Va dans Telegram → @userinfobot pour récupérer ton chat ID\n")
        token = input("  Token du bot (1234567890:ABC...) : ").strip()
        chat_id = input("  Ton chat ID (ex: 123456789) : ").strip()

    if not token or ":" not in token:
        print("  ✗ Token invalide (format attendu : 1234567890:ABC...)")
        return 1
    if not chat_id.isdigit():
        print("  ✗ Chat ID invalide (doit être un nombre entier)")
        return 1

    update_env(token, chat_id)

    # Recharge settings (sinon valeurs cachées)
    print("\n  Envoi du message de test...")
    # Import APRÈS update_env pour que la nouvelle config soit lue
    sys.path.insert(0, str(ROOT))
    from importlib import reload
    import config
    reload(config)
    from alerts.telegram_bot import notify_bootup

    if notify_bootup():
        print("\n  ✓ Message envoyé ! Va voir Telegram. Si tu vois 'NOVA en ligne', c'est gagné 🌌")
        return 0
    else:
        print("\n  ✗ Échec de l'envoi. Vérifie token + chat_id (et que tu as bien envoyé /start à ton bot).")
        return 2


if __name__ == "__main__":
    sys.exit(main())
