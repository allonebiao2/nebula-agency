"""Alertes Mongazi : WhatsApp (Meta Cloud API) + Telegram, en parallele.

Best-effort absolu : une notification qui echoue ne fait JAMAIS echouer une
commande. Une cliente qui paie doit voir sa commande enregistree meme si
Meta est en panne.

Pourquoi les DEUX rails et pas seulement WhatsApp :
  WhatsApp Cloud API n'autorise un message libre que dans la fenetre de 24 h
  qui suit le dernier message recu du destinataire. Hors de cette fenetre, il
  faut un MODELE approuve par Meta, sinon l'envoi est refuse. Telegram n'a
  aucune limite de ce genre. WhatsApp est donc le rail que Mongazi lit,
  Telegram est le rail qui ne tombe jamais. On garde les deux.

  Quand un modele sera approuve, poser WHATSAPP_TEMPLATE (et au besoin
  WHATSAPP_TEMPLATE_LANG) : l'envoi passe automatiquement en mode modele et
  la fenetre de 24 h cesse d'etre un probleme.

Variables d'environnement (toutes optionnelles, chaque rail dort si vide) :
  WHATSAPP_TOKEN             jeton Cloud API (System User, longue duree)
  WHATSAPP_PHONE_NUMBER_ID   identifiant du numero expediteur dans Meta
  WHATSAPP_GRAPH_VERSION     defaut v21.0
  MONGAZI_WHATSAPP           numero qui recoit les alertes, ex 22961234567
  WHATSAPP_TEMPLATE          nom d'un modele approuve (optionnel)
  WHATSAPP_TEMPLATE_LANG     langue du modele, defaut fr
  TG_TOKEN, TG_CHAT          bot Telegram (deja utilises par server.py)
"""
import json
import os
import re
import urllib.parse
import urllib.request

TIMEOUT = 8


def _env(key, default=""):
    return (os.environ.get(key) or default).strip()


def _digits(num):
    """Un numero WhatsApp est fait de chiffres uniquement, sans + ni espaces."""
    return re.sub(r"\D", "", num or "")


# --------------------------------------------------------------------------
# WhatsApp — Meta Cloud API (gratuit, sans Twilio)
# --------------------------------------------------------------------------

def whatsapp_pret():
    return bool(_env("WHATSAPP_TOKEN") and _env("WHATSAPP_PHONE_NUMBER_ID"))


def envoyer_whatsapp(destinataire, texte):
    """Envoie un message WhatsApp. Rend True si Meta a accepte.

    N'echoue jamais bruyamment : toute erreur est journalisee et rendue False.
    """
    dest = _digits(destinataire)
    if not whatsapp_pret() or not dest:
        print("[notify] WhatsApp non configure, message ignore")
        return False

    version = _env("WHATSAPP_GRAPH_VERSION", "v21.0")
    url = f"https://graph.facebook.com/{version}/{_env('WHATSAPP_PHONE_NUMBER_ID')}/messages"

    modele = _env("WHATSAPP_TEMPLATE")
    if modele:
        # Mode modele : passe meme hors de la fenetre de 24 h.
        # Le modele doit contenir exactement une variable {{1}}.
        charge = {
            "messaging_product": "whatsapp",
            "to": dest,
            "type": "template",
            "template": {
                "name": modele,
                "language": {"code": _env("WHATSAPP_TEMPLATE_LANG", "fr")},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": texte[:1024]}],
                }],
            },
        }
    else:
        charge = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": dest,
            "type": "text",
            "text": {"preview_url": True, "body": texte[:4096]},
        }

    requete = urllib.request.Request(
        url,
        data=json.dumps(charge).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {_env('WHATSAPP_TOKEN')}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(requete, timeout=TIMEOUT) as r:
            return 200 <= r.status < 300
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        # 131047 = hors fenetre de 24 h : c'est le cas normal sans modele.
        print(f"[notify] WhatsApp refuse ({e.code}) : {detail}")
        return False
    except Exception as e:
        print(f"[notify] WhatsApp injoignable : {e}")
        return False


# --------------------------------------------------------------------------
# Telegram — le rail de secours, sans limite de fenetre
# --------------------------------------------------------------------------

def telegram_pret():
    return bool(_env("TG_TOKEN") and _env("TG_CHAT"))


def envoyer_telegram(texte):
    """Envoie en texte BRUT, sans parse_mode.

    Volontaire : avec parse_mode=HTML, un nom d'activite contenant & ou <
    fait echouer tout le message. Ici rien ne peut casser la notification.
    """
    if not telegram_pret():
        print("[notify] Telegram non configure, message ignore")
        return False
    try:
        data = urllib.parse.urlencode({
            "chat_id": _env("TG_CHAT"),
            "text": texte[:4096],
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        with urllib.request.urlopen(
            f"https://api.telegram.org/bot{_env('TG_TOKEN')}/sendMessage",
            data, timeout=TIMEOUT,
        ) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print(f"[notify] Telegram injoignable : {e}")
        return False


# --------------------------------------------------------------------------
# Sorties publiques
# --------------------------------------------------------------------------

def alerter_mongazi(texte):
    """Previent Mongazi sur les deux rails. Rend l'etat de chacun."""
    etat = {
        "whatsapp": envoyer_whatsapp(_env("MONGAZI_WHATSAPP"), texte),
        "telegram": envoyer_telegram(texte),
    }
    if not any(etat.values()):
        # Aucun rail n'a marche : la commande existe quand meme en base et
        # reste visible dans le back-office. On le dit fort dans les logs.
        print(f"[notify] AUCUN RAIL JOIGNABLE, alerte perdue :\n{texte}")
    return etat


def prevenir_client(numero, texte):
    """Previent la cliente sur WhatsApp. Best-effort, jamais bloquant."""
    return envoyer_whatsapp(numero, texte)
