"""Setup Wizard NOVA — guide Mongazi pas à pas pour tout configurer.

Lancement (depuis le dossier nebula-prospector) :
    python scripts/setup_wizard.py

Ou double-click sur LANCE-MOI.bat à la racine de nebula-prospector/.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
SCHEMA_V1 = ROOT / "db" / "schema.sql"
SCHEMA_V2 = ROOT / "db" / "schema_v2_dashboard.sql"


# ---------------------------------------------------------------------------
# UI helpers (ANSI safe sur Windows 10+)
# ---------------------------------------------------------------------------
class C:
    R = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    VIOLET = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    DIM = "\033[2m"


def title(msg: str) -> None:
    print()
    print(f"{C.VIOLET}{C.BOLD}╔══════════════════════════════════════════════════════════╗{C.R}")
    print(f"{C.VIOLET}{C.BOLD}║  {msg:<56}║{C.R}")
    print(f"{C.VIOLET}{C.BOLD}╚══════════════════════════════════════════════════════════╝{C.R}")


def step(n: int, total: int, msg: str) -> None:
    print(f"\n{C.CYAN}{C.BOLD}[{n}/{total}] {msg}{C.R}")


def ok(msg: str) -> None:
    print(f"  {C.GREEN}✓{C.R} {msg}")


def warn(msg: str) -> None:
    print(f"  {C.YELLOW}⚠{C.R} {msg}")


def err(msg: str) -> None:
    print(f"  {C.RED}✗{C.R} {msg}")


def info(msg: str) -> None:
    print(f"  {C.DIM}{msg}{C.R}")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" {C.DIM}[{default}]{C.R}" if default else ""
    val = input(f"  {C.CYAN}?{C.R} {prompt}{suffix} : ").strip()
    return val or default


def wait_enter(msg: str = "Appuie sur ENTRÉE pour continuer") -> None:
    input(f"\n  {C.DIM}{msg}...{C.R}")


# ---------------------------------------------------------------------------
# Définition des clés à demander
# ---------------------------------------------------------------------------
KEYS = [
    {
        "name": "SUPABASE_URL",
        "label": "URL de ton projet Supabase",
        "example": "https://abcxyz.supabase.co",
        "url": "https://supabase.com/dashboard/project/_/settings/api",
        "help": "Supabase → ton projet → Settings → API → Project URL",
    },
    {
        "name": "SUPABASE_SERVICE_ROLE_KEY",
        "label": "Clé service_role Supabase (SECRÈTE, jamais publique)",
        "example": "eyJhbGciOi...",
        "url": "https://supabase.com/dashboard/project/_/settings/api",
        "help": "Même page → 'service_role' secret → bouton 'Reveal' puis copie",
    },
    {
        "name": "SUPABASE_ANON_KEY",
        "label": "Clé anon Supabase (publique, pour le dashboard navigateur)",
        "example": "eyJhbGciOi...",
        "url": "https://supabase.com/dashboard/project/_/settings/api",
        "help": "Même page → 'anon' public → copie",
    },
    {
        "name": "ANTHROPIC_API_KEY",
        "label": "Clé API Anthropic (Claude)",
        "example": "sk-ant-api03-...",
        "url": "https://console.anthropic.com/settings/keys",
        "help": "Console Anthropic → API Keys → Create Key",
    },
    {
        "name": "GOOGLE_MAPS_API_KEY",
        "label": "Clé Google Maps Platform [OPTIONNEL — laisse vide si tu ne veux pas, on utilisera OpenStreetMap (gratuit)]",
        "example": "AIzaSy... ou vide pour skip",
        "url": "https://console.cloud.google.com/google/maps-apis/credentials",
        "help": ("OPTIONNEL : si tu n'as pas pu obtenir la clé Google (erreur OR_BACR2_44 "
                 "ou pas de carte bancaire), laisse simplement vide et appuie ENTRÉE. "
                 "OpenStreetMap fera le sourcing à la place (100 % gratuit, illimité)."),
        "optional": True,
    },
]


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------
def check_python() -> bool:
    step(1, 7, "Vérification de Python")
    v = sys.version_info
    info(f"Python détecté : {v.major}.{v.minor}.{v.micro}")
    if (v.major, v.minor) < (3, 10):
        err("Python 3.10+ requis. Télécharge sur https://www.python.org/downloads/")
        return False
    ok(f"Python {v.major}.{v.minor} OK")
    return True


def install_deps() -> bool:
    step(2, 7, "Installation des dépendances Python")
    info("Cela prend 1-2 minutes la première fois...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
            check=True,
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r",
             str(ROOT / "requirements.txt"), "--quiet"],
            check=True,
        )
        ok("Dépendances installées")
        return True
    except subprocess.CalledProcessError as e:
        err(f"Échec installation : {e}")
        return False


def load_env() -> dict[str, str]:
    """Charge .env existant en dict (ou vide si pas de fichier)."""
    if not ENV_PATH.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy(ENV_EXAMPLE, ENV_PATH)
            info("Fichier .env créé depuis .env.example")
        else:
            ENV_PATH.touch()
            info("Fichier .env créé (vide)")

    env: dict[str, str] = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def save_env(env: dict[str, str]) -> None:
    """Réécrit .env en conservant les commentaires de .env.example."""
    if ENV_EXAMPLE.exists():
        # Reconstruit en suivant la structure de .env.example
        lines: list[str] = []
        for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                lines.append(line)
                continue
            if "=" in stripped:
                k = stripped.split("=", 1)[0].strip()
                v = env.get(k, "")
                lines.append(f"{k}={v}")
            else:
                lines.append(line)
        ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        ENV_PATH.write_text(
            "\n".join(f"{k}={v}" for k, v in env.items()) + "\n",
            encoding="utf-8",
        )


def is_placeholder(value: str) -> bool:
    """Détecte une valeur vide ou placeholder type 'xxxxx', 'eyJ...xxx'."""
    if not value:
        return True
    v = value.lower()
    return any(t in v for t in ["xxxx", "your_key", "abcdef", "your-key", "..."])


def configure_keys() -> bool:
    step(3, 7, "Configuration des clés API")
    env = load_env()
    missing = [k for k in KEYS if is_placeholder(env.get(k["name"], ""))]

    if not missing:
        ok("Toutes les clés sont déjà configurées dans .env")
        return True

    info(f"{len(missing)} clé(s) à configurer.\n")

    for i, k in enumerate(missing, 1):
        is_optional = k.get("optional", False)
        flag = f" {C.YELLOW}[OPTIONNEL]{C.R}" if is_optional else ""
        print(f"\n  {C.BOLD}--- Clé {i}/{len(missing)} : {k['name']}{flag} ---{C.R}")
        print(f"  {k['label']}")
        print(f"  {C.DIM}Exemple : {k['example']}{C.R}")
        print(f"  {C.CYAN}{k['help']}{C.R}")
        if not is_optional:
            print(f"  J'ouvre la page dans ton navigateur...")
            try:
                webbrowser.open(k["url"])
            except Exception:
                print(f"  Ouvre manuellement : {k['url']}")
            time.sleep(0.5)
        val = ask(f"Colle ici la valeur de {k['name']} (ou ENTRÉE pour skip)")
        if not val:
            if is_optional:
                info(f"Clé {k['name']} skippée (OK, alternative gratuite utilisée).")
            else:
                warn(f"Clé {k['name']} laissée vide → tu ne pourras pas l'utiliser")
        env[k["name"]] = val

    save_env(env)
    ok(".env sauvegardé")
    return True


def apply_schemas() -> bool:
    step(4, 7, "Application des schémas Supabase")
    print("  Les schémas SQL doivent être appliqués dans Supabase SQL Editor.")
    print(f"  {C.CYAN}J'ouvre l'éditeur SQL...{C.R}")
    try:
        webbrowser.open("https://supabase.com/dashboard/project/_/sql/new")
    except Exception:
        pass
    print()
    print(f"  {C.BOLD}Marche à suivre :{C.R}")
    print(f"  1. Dans Supabase SQL Editor, clique 'New query'")
    print(f"  2. Ouvre le fichier {C.CYAN}{SCHEMA_V1.relative_to(ROOT)}{C.R} (Windows : double-click)")
    print(f"  3. Copie TOUT son contenu, colle dans Supabase, clique RUN")
    print(f"  4. Re-clique 'New query'")
    print(f"  5. Même chose avec {C.CYAN}{SCHEMA_V2.relative_to(ROOT)}{C.R}")
    print(f"  6. Dans Supabase, va dans {C.BOLD}Database → Replication{C.R}")
    print(f"     → coche les cases {C.BOLD}agent_events{C.R} et {C.BOLD}agent_state{C.R}")
    wait_enter("Quand c'est fait, appuie sur ENTRÉE")
    return True


def healthcheck() -> bool:
    step(5, 7, "Test des connexions (healthcheck)")
    try:
        # Reload modules avec les nouvelles variables d'env
        result = subprocess.run(
            [sys.executable, "main.py", "healthcheck"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        print(result.stdout)
        if "FAIL" in result.stdout or result.returncode != 0:
            warn("Certains composants ne sont pas OK — vérifie ci-dessus")
            return False
        ok("Tous les composants critiques sont OK")
        return True
    except Exception as e:
        err(f"Erreur healthcheck : {e}")
        return False


def offer_actions() -> None:
    step(6, 7, "Tout est prêt — que veux-tu faire ?")
    print("\n  Choisis une action :")
    print("   1. Lancer le dashboard NOVA (http://localhost:8001)")
    print("   2. Lancer un sourcing test (Google Maps Cotonou)")
    print("   3. Les deux (dashboard en arrière-plan + sourcing test)")
    print("   4. Rien, je veux juste vérifier l'install")
    choice = ask("Ton choix [1-4]", "3")

    if choice in ("1", "3"):
        print(f"\n  {C.GREEN}🚀 Lancement du dashboard...{C.R}")
        print(f"  {C.CYAN}Ouvre dans ton navigateur : http://localhost:8001{C.R}\n")
        if choice == "3":
            # Lancer dashboard en arrière-plan
            import threading
            def _start_uvicorn():
                subprocess.run(
                    [sys.executable, "-m", "uvicorn",
                     "dashboard.server:app", "--host", "127.0.0.1", "--port", "8001"],
                    cwd=str(ROOT),
                )
            t = threading.Thread(target=_start_uvicorn, daemon=True)
            t.start()
            time.sleep(3)
            try:
                webbrowser.open("http://localhost:8001")
            except Exception:
                pass
            run_sourcing_test()
            print(f"\n  {C.GREEN}🌌 Le dashboard tourne sur http://localhost:8001{C.R}")
            print(f"  {C.DIM}Appuie sur Ctrl+C pour arrêter.{C.R}")
            try:
                t.join()
            except KeyboardInterrupt:
                pass
        else:
            try:
                webbrowser.open("http://localhost:8001")
            except Exception:
                pass
            subprocess.run(
                [sys.executable, "-m", "uvicorn",
                 "dashboard.server:app", "--host", "127.0.0.1", "--port", "8001"],
                cwd=str(ROOT),
            )

    elif choice == "2":
        run_sourcing_test()


def run_sourcing_test() -> None:
    # On utilise OpenStreetMap (toujours dispo, gratuit). Si Google Maps key
    # présente, le test Google se fera plus tard via main.py sourcing.
    print(f"\n  {C.CYAN}🔍 Sourcing test : beauté à Cotonou via OpenStreetMap{C.R}\n")
    subprocess.run(
        [sys.executable, "-m", "sourcing.openstreetmap",
         "search", "--city", "Cotonou", "--category", "beauty"],
        cwd=str(ROOT),
    )


def final_summary() -> None:
    step(7, 7, "Récapitulatif")
    print(f"\n  {C.GREEN}{C.BOLD}🌌 NOVA est prête.{C.R}\n")
    print(f"  {C.BOLD}Pour relancer plus tard :{C.R}")
    print(f"   • Dashboard         : {C.CYAN}python -m uvicorn dashboard.server:app --port 8001{C.R}")
    print(f"   • Sourcing complet  : {C.CYAN}python main.py sourcing{C.R}")
    print(f"   • Stats             : {C.CYAN}python main.py stats{C.R}")
    print(f"   • Re-lancer wizard  : {C.CYAN}python scripts/setup_wizard.py{C.R}")
    print(f"\n  {C.DIM}Pour déployer en ligne (24/7) : voir DEPLOY-RAILWAY.md{C.R}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    os.system("")  # Active le support ANSI sur Windows

    title("🌌  NOVA — Setup Wizard NEBULA Prospector")
    print(f"\n  {C.DIM}Je vais te guider pas à pas. Sois patient, ne ferme pas cette fenêtre.{C.R}")

    if not check_python():
        return 1
    if not install_deps():
        return 1
    if not configure_keys():
        return 1
    if not apply_schemas():
        return 1

    healthcheck_ok = healthcheck()
    if not healthcheck_ok:
        warn("Le healthcheck a quelques warnings — tu peux quand même continuer.")
        cont = ask("Continuer quand même ? [o/N]", "n").lower()
        if cont not in ("o", "oui", "y", "yes"):
            return 1

    offer_actions()
    final_summary()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}Wizard interrompu. Tu peux le relancer à tout moment.{C.R}")
        sys.exit(130)
