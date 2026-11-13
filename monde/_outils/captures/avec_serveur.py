"""Lance le serveur du salon LE TEMPS d'un script de capture, puis l'arrête.

    python monde/_outils/captures/avec_serveur.py monde/_outils/captures/voir_cuisson.py [arguments…]

Pourquoi : sur ce PC (8 Go), Claude Code arrête les tâches de fond quand la mémoire manque (le serveur
et une cuisson Blender l'ont été le 2026-11-13). Un serveur qui ne vit que pendant la mesure ne gêne rien.
"""
import socket, subprocess, sys, time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
serveur = subprocess.Popen([sys.executable, str(RACINE / "monde" / "_servir.py"), "--sans-construire"],
                           cwd=str(RACINE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    t0 = time.time()
    while time.time() - t0 < 30:
        try:
            socket.create_connection(("127.0.0.1", 8765), timeout=1).close(); break
        except OSError:
            time.sleep(0.5)
    sys.exit(subprocess.call([sys.executable, *sys.argv[1:]], cwd=str(RACINE)))
finally:
    serveur.terminate()
    try:
        serveur.wait(timeout=5)
    except subprocess.TimeoutExpired:
        serveur.kill()
