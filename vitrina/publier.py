"""Publier une page validée sur Cloudflare KV, pour qu'elle ne dépende
plus jamais du réveil de Render.

POURQUOI CE FICHIER EXISTE.
Une page cadeau s'ouvre à minuit, sur le téléphone de quelqu'un qui reçoit un
cadeau. Si elle est servie par un service Render gratuit endormi, la personne
attend une minute devant « APPLICATION LOADING ». Ce n'est pas un site lent,
c'est le cadeau détruit : tout le produit tient dans ce moment d'ouverture.

Un proxy inverse ne règle rien : si Cloudflare interroge Render, la requête
attend quand même que Render se lève. La seule solution est que la page ne
soit pas sur Render du tout.

DONC : au moment de la validation, le HTML fini part dans Cloudflare KV, et
le Worker le sert directement depuis le bord du réseau. Aucun réveil, jamais,
et c'est gratuit (le palier gratuit couvre 1 000 écritures et 100 000 lectures
par jour, là où une vente vaut une écriture).

CE QUI RESTE SUR RENDER, ET C'EST VOULU : la commande, le back-office, la
validation. Le seul qui attend alors, c'est Mongazi, et il prend déjà deux
minutes pour lire son SMS Mobile Money.

Variables d'environnement (si absentes, la publication dort et le serveur
continue de servir la page lui-même, en plus lent) :
  CF_ACCOUNT_ID        identifiant du compte Cloudflare
  CF_KV_NAMESPACE_ID   identifiant de l'espace KV
  CF_API_TOKEN         jeton avec la permission Workers KV Storage · Edit
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 10
PREFIXE = "v:"


def _env(cle, defaut=""):
    return (os.environ.get(cle) or defaut).strip()


def pret():
    """Vrai si les trois variables Cloudflare sont posées."""
    return all(_env(c) for c in ("CF_ACCOUNT_ID", "CF_KV_NAMESPACE_ID", "CF_API_TOKEN"))


def _url(slug):
    return (f"https://api.cloudflare.com/client/v4/accounts/{_env('CF_ACCOUNT_ID')}"
            f"/storage/kv/namespaces/{_env('CF_KV_NAMESPACE_ID')}"
            f"/values/{urllib.parse.quote(PREFIXE + slug, safe='')}")


def publier(slug, html):
    """Pose la page dans Cloudflare KV. Rend True si Cloudflare a accepté.

    N'échoue jamais bruyamment : la validation d'une commande ne doit pas
    tomber parce que Cloudflare a hoqueté. En cas d'échec, la page reste
    servie par le serveur, simplement avec le réveil lent.
    """
    if not pret():
        print("[publier] Cloudflare non configuré, la page reste servie par le serveur")
        return False
    if not slug or not html:
        print("[publier] slug ou html vide, rien à publier")
        return False

    corps = html.encode("utf-8")
    requete = urllib.request.Request(
        _url(slug),
        data=corps,
        headers={
            "Authorization": f"Bearer {_env('CF_API_TOKEN')}",
            "Content-Type": "text/plain; charset=utf-8",
        },
        method="PUT",
    )
    try:
        with urllib.request.urlopen(requete, timeout=TIMEOUT) as r:
            ok = 200 <= r.status < 300
            if ok:
                print(f"[publier] {slug} posée sur Cloudflare ({len(corps)} octets)")
            return ok
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        print(f"[publier] Cloudflare refuse ({e.code}) : {detail}")
        return False
    except Exception as e:
        print(f"[publier] Cloudflare injoignable : {e}")
        return False


def retirer(slug):
    """Retire une page de Cloudflare KV.

    Sert au retrait sous 24 h demandé par la personne visée par une page.
    Tant qu'une page reste dans KV, elle est servie par le bord du réseau :
    la supprimer en base ne suffit PAS, il faut la retirer ici aussi.
    """
    if not pret() or not slug:
        return False
    requete = urllib.request.Request(
        _url(slug),
        headers={"Authorization": f"Bearer {_env('CF_API_TOKEN')}"},
        method="DELETE",
    )
    try:
        with urllib.request.urlopen(requete, timeout=TIMEOUT) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print(f"[publier] retrait impossible : {e}")
        return False
