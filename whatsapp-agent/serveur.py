"""LE SERVEUR — la porte par laquelle WhatsApp entre.

Bibliothèque standard uniquement : `http.server`, en threads. Un webhook qui
reçoit quelques messages par minute n'a pas besoin d'un serveur d'application,
et le kit s'installe alors partout, y compris là où l'on ne choisit pas
l'hébergement.

⚠️ ON RÉPOND 200 AVANT DE RÉFLÉCHIR. Meta considère un webhook lent comme
tombé et le rejoue. Comme une réponse de Claude prend quelques secondes, on
accuse réception tout de suite et on travaille dans un fil séparé. Le
dédoublonnage par identifiant de message (`memoire.deja_vu`) rattrape les rejeux
qui passeraient quand même.

⚠️ UNE MAISON QUI N'EST PAS PRÊTE NE DÉMARRE PAS. Sans numéro à prévenir,
l'agent ne peut passer la main à personne : il vaut mieux un service qui refuse
de démarrer qu'un agent qui laisse tomber les clients en silence.

    python whatsapp-agent/serveur.py --port 8020
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE_KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE_KIT))

from agent import maison as maisons_mod          # noqa: E402
from agent.memoire import Memoire                # noqa: E402
from agent.service import Service                # noqa: E402
from canaux.console import CanalConsole          # noqa: E402
from canaux.meta import CanalMeta                # noqa: E402
from canaux.twilio import CanalTwilio            # noqa: E402

log = logging.getLogger("whatsapp-agent.serveur")


def _env(cle: str, maison_id: str, defaut: str = "") -> str:
    """`WA_META_TOKEN_BRAISE_DOR` s'il existe, sinon `WA_META_TOKEN`.

    Un déploiement par client dans le cas courant ; plusieurs maisons sur un même
    service quand on veut mutualiser.
    """
    suffixe = maison_id.upper().replace("-", "_")
    return os.environ.get(f"{cle}_{suffixe}") or os.environ.get(cle, defaut)


def construire_canal(maison_id: str):
    """Le canal se choisit par ce qui est configuré, pas par un réglage de plus."""
    lequel = _env("WA_CANAL", maison_id, "").lower()
    meta = CanalMeta(
        jeton=_env("WA_META_TOKEN", maison_id),
        identifiant_numero=_env("WA_META_PHONE_ID", maison_id),
        jeton_verification=_env("WA_META_VERIFY", maison_id),
        secret_app=_env("WA_META_SECRET", maison_id),
        version=_env("WA_META_VERSION", maison_id, "v21.0"),
    )
    twilio = CanalTwilio(
        sid=_env("WA_TWILIO_SID", maison_id),
        jeton=_env("WA_TWILIO_TOKEN", maison_id),
        numero=_env("WA_TWILIO_FROM", maison_id),
    )
    if lequel == "meta" or (not lequel and meta.configure()):
        return meta
    if lequel == "twilio" or (not lequel and twilio.configure()):
        return twilio
    if lequel == "console":
        return CanalConsole(afficher=True)
    return meta  # non configuré : le serveur le dira au démarrage


class Standard:
    """Toutes les maisons servies par ce processus."""

    def __init__(self, racine: Path, base: Path, strict: bool = True):
        self.racine = racine
        self.memoire = Memoire(base)
        self.services: dict[str, Service] = {}
        self.canaux: dict[str, object] = {}
        self.refusees: dict[str, list[str]] = {}

        for m in maisons_mod.toutes(RACINE_KIT / "maisons"):
            prete, manques = m.prete
            if not prete and strict:
                self.refusees[m.id] = manques
                continue
            canal = construire_canal(m.id)
            self.canaux[m.id] = canal
            self.services[m.id] = Service(m, racine, self.memoire, canal)

    def resume(self) -> str:
        lignes = []
        for identifiant, service in self.services.items():
            lignes.append(f"  ✓ {identifiant:12} {len(service.catalogue):3} articles "
                          f"· canal {service.canal.nom} "
                          f"· {'configuré' if service.canal.configure() else 'NON CONFIGURÉ'}")
        for identifiant, manques in self.refusees.items():
            lignes.append(f"  ✗ {identifiant:12} pas démarrée : " + " ; ".join(manques))
        return "\n".join(lignes) or "  (aucune maison)"


class Poignee(BaseHTTPRequestHandler):
    standard: Standard = None  # posé au démarrage

    def log_message(self, format, *args):
        log.info("%s - %s", self.address_string(), format % args)

    # --- utilitaires ------------------------------------------------------
    def _repondre(self, code: int, corps: str = "", type_mime: str = "text/plain") -> None:
        donnees = corps.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{type_mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(donnees)))
        self.end_headers()
        self.wfile.write(donnees)

    def _maison(self, chemin: str) -> str:
        bouts = [b for b in chemin.split("/") if b]
        return bouts[1] if len(bouts) > 1 else ""

    # --- GET ---------------------------------------------------------------
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path in ("/", "/sante"):
            etat = {"maisons": sorted(self.standard.services),
                    "refusees": self.standard.refusees}
            return self._repondre(200, json.dumps(etat, ensure_ascii=False), "application/json")

        if url.path.startswith("/webhook/"):
            identifiant = self._maison(url.path)
            canal = self.standard.canaux.get(identifiant)
            if not isinstance(canal, CanalMeta):
                return self._repondre(404, "maison inconnue ou canal non Meta")
            params = urllib.parse.parse_qs(url.query)
            defi = canal.verifier_abonnement(
                (params.get("hub.mode") or [None])[0],
                (params.get("hub.verify_token") or [None])[0],
                (params.get("hub.challenge") or [None])[0])
            if defi is None:
                return self._repondre(403, "vérification refusée")
            return self._repondre(200, defi)

        self._repondre(404, "rien ici")

    # --- POST --------------------------------------------------------------
    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        identifiant = self._maison(url.path)
        service = self.standard.services.get(identifiant)
        if service is None:
            return self._repondre(404, "maison inconnue")

        longueur = int(self.headers.get("Content-Length") or 0)
        corps = self.rfile.read(longueur) if longueur else b""

        if url.path.startswith("/webhook/"):
            canal = self.standard.canaux[identifiant]
            # ⚠️ `/webhook/` est la porte de Meta, et elle n'est ouverte que si
            # c'est bien un canal Meta qui est derrière. Sans ce test, un
            # déploiement réglé sur « console » ou sur Twilio plantait en 500 sur
            # une méthode que ces canaux n'ont pas — un webhook qui répond 500
            # est un webhook que Meta finit par désabonner.
            if not isinstance(canal, CanalMeta):
                return self._repondre(404, "cette maison n'écoute pas Meta")
            if not canal.verifier_signature(corps, self.headers.get("X-Hub-Signature-256")):
                # ⚠️ Un webhook public sans signature vérifiée, c'est un inconnu
                # qui fait parler l'agent d'un client et dépense ses jetons.
                log.warning("signature refusée sur /webhook/%s", identifiant)
                return self._repondre(403, "signature refusée")
            try:
                charge = json.loads(corps.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return self._repondre(400, "JSON illisible")
            entrants = canal.lire_entrant(charge)

        elif url.path.startswith("/twilio/"):
            champs = {c: v[0] for c, v in
                      urllib.parse.parse_qs(corps.decode("utf-8", "replace")).items()}
            entrants = CanalTwilio.lire_entrant(champs)
        else:
            return self._repondre(404, "rien ici")

        # On accuse réception TOUT DE SUITE, puis on travaille.
        self._repondre(200, "reçu")
        for message in entrants:
            if message.type not in ("text", "button", "interactive") and not message.texte:
                log.info("message %s de type %s : passé à un humain",
                         message.identifiant, message.type)
            threading.Thread(target=self._travailler, args=(service, message),
                             daemon=True).start()

    @staticmethod
    def _travailler(service: Service, message) -> None:
        try:
            service.traiter(message.numero, message.texte,
                            nom_client=message.nom_profil, identifiant=message.identifiant)
        except Exception:  # noqa: BLE001 — un fil qui meurt en silence est pire
            log.exception("échec du traitement du message %s", message.identifiant)


def main() -> int:
    analyseur = argparse.ArgumentParser(description="Le standard WhatsApp de NEBULA.")
    analyseur.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8020")))
    analyseur.add_argument("--racine", default=str(RACINE_KIT.parent),
                           help="La racine du dépôt, où les catalogues sont lus.")
    analyseur.add_argument("--base", default=os.environ.get("WA_BASE", "whatsapp-agent.db"))
    analyseur.add_argument("--tout-de-meme", action="store_true",
                           help="Démarrer même les maisons incomplètes (essais seulement).")
    args = analyseur.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    standard = Standard(Path(args.racine), Path(args.base), strict=not args.tout_de_meme)
    print(f"Le standard écoute sur le port {args.port}\n{standard.resume()}")
    if not standard.services:
        print("\n⛔ Aucune maison prête. Complétez maisons/*.yaml (voir ci-dessus).")
        return 1

    Poignee.standard = standard
    ThreadingHTTPServer(("", args.port), Poignee).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
