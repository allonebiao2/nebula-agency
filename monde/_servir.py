"""LE MONDE · le serveur local, pour voir et pour tester (jamais en ligne).

    python monde/_servir.py            # construit, puis sert sur http://localhost:8765/
    python monde/_servir.py --sans-construire

Il sert le dossier monde/ tel quel, plus la route /api/meteo, qui fait EN
LOCAL ce que fera le relais Cloudflare en ligne : demander la météo de
Cotonou à MET Norway, une fois toutes les 10 minutes, et la garder en cache.
⚠️ MET Norway exige qu'on s'identifie : un nom d'application et un site,
jamais une adresse personnelle.

Il écoute sur toutes les interfaces : un téléphone sur le même Wi-Fi peut
ouvrir l'adresse affichée (ex. http://192.168.1.20:8765/lieux/hillary-m-styl/).
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ICI = Path(__file__).resolve().parent
PORT = 8765
COTONOU = (6.37, 2.39)
UA = "NEBULA-Monde/0.1 https://nebula-agency.online"
_cache = {"t": 0.0, "corps": b""}


def meteo() -> bytes:
    if time.time() - _cache["t"] < 600 and _cache["corps"]:
        return _cache["corps"]
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={COTONOU[0]}&lon={COTONOU[1]}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    d = json.load(urllib.request.urlopen(req, timeout=15))
    ts = d["properties"]["timeseries"][0]["data"]
    i = ts["instant"]["details"]
    corps = json.dumps({
        "symbole": (ts.get("next_1_hours") or ts.get("next_6_hours") or {}).get("summary", {}).get("symbol_code", "clearsky"),
        "temp": i.get("air_temperature"), "humidite": i.get("relative_humidity"), "nuages": i.get("cloud_area_fraction"),
        "maj": d["properties"]["meta"]["updated_at"], "source": "MET Norway (CC BY 4.0)",
    }).encode()
    _cache.update(t=time.time(), corps=corps)
    return corps


class Gestionnaire(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/api/meteo"):
            try:
                corps, code = meteo(), 200
            except Exception as e:  # hors ligne : le salon prend un ciel clair
                corps, code = json.dumps({"erreur": str(e)}).encode(), 502
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)
            return
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/lieux/hillary-m-styl/")
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, *a):
        pass


def ip_locale() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--sans-construire" not in sys.argv:
        subprocess.run([sys.executable, str(ICI / "_construire.py")], check=True)
    Gestionnaire.extensions_map.update({".js": "text/javascript", ".mjs": "text/javascript", ".webp": "image/webp", ".woff2": "font/woff2", ".json": "application/json"})
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), partial(Gestionnaire, directory=str(ICI)))
    print(f"Le salon : http://localhost:{PORT}/lieux/hillary-m-styl/")
    print(f"Au téléphone (même Wi-Fi) : http://{ip_locale()}:{PORT}/lieux/hillary-m-styl/")
    srv.serve_forever()
