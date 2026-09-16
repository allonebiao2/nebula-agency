# -*- coding: utf-8 -*-
"""
NEBULA Trader : l'application.

    python -m trading.app                 # agent + interface, ouvre le navigateur
    python -m trading.app --port 8765 --sans-navigateur

Un seul processus, deux fils : l'agent (qui seul parle à MetaTrader 5) et le
serveur web local de l'interface. Fermer la fenêtre de commande arrête tout ;
les positions ouvertes restent protégées par leur stop déposé chez le courtier.
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
import webbrowser


def _port_libre(port: int) -> int:
    for p in range(port, port + 20):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise SystemExit("aucun port libre entre %d et %d" % (port, port + 19))


def main() -> int:
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="NEBULA Trader")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--sans-navigateur", action="store_true")
    ap.add_argument("--sans-agent", action="store_true", help="interface seule (démonstration)")
    a = ap.parse_args()

    import uvicorn

    from .interface.chat import Assistant
    from .interface.serveur import creer_app
    from .live.agent import Agent
    from .live.journal import Journal
    from .noyau import licence
    from .noyau.chemins import dossier_donnees, initialiser

    initialiser()
    journal = Journal()
    agent = Agent(journal, licence_valide=lambda: licence.actuelle().valide)
    assistant = Assistant(agent, journal)
    port = _port_libre(a.port)
    app = creer_app(agent, journal, assistant, port=port)

    adresse = f"http://127.0.0.1:{port}/"
    print("=" * 60)
    print("  NEBULA Trader")
    print(f"  Interface  : {adresse}")
    print(f"  Données    : {dossier_donnees()}")
    print("  Arrêt      : Ctrl+C (les stops restent chez le courtier)")
    print("=" * 60)

    if not a.sans_agent:
        agent.demarrer()
    if not a.sans_navigateur:
        threading.Timer(1.5, lambda: webbrowser.open(adresse)).start()
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
    finally:
        agent.arreter()
    return 0


if __name__ == "__main__":
    sys.exit(main())
