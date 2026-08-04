# -*- coding: utf-8 -*-
"""
Vide le cache Cloudflare. Le bouton de secours du parc.

POURQUOI CET OUTIL EXISTE
  Le 2026-08-04, PISTE est apparu entièrement sans style : texte noir sur
  blanc, police par défaut. La feuille de style répondait 200, avec le bon type
  et la bonne taille, mais son contenu était « error code: 502 ». Pendant un
  déploiement, Cloudflare avait reçu un 502 passager de l'origine et l'avait mis
  en cache À LA PLACE du fichier, avec un `Cache-Control` d'un an.

  Il n'existait alors aucun moyen de purger : le jeton de zone lisait la zone
  mais n'avait pas la permission « Zone · Cache Purge ». Le seul remède était de
  changer les noms des fichiers compilés. Ce script existe pour qu'on n'en soit
  plus jamais réduit là.

USAGE
    python scripts/purger.py                       tous les sites du parc
    python scripts/purger.py piste                 un seul
    python scripts/purger.py --verifier            regarde sans rien purger
"""
import io, json, sys, urllib.error, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
API = "https://api.cloudflare.com/client/v4"

# Les hôtes servis par Cloudflare pour NEBULA. Un site absent d'ici ne se
# purge pas : c'est volontaire, on ne devine pas les adresses.
SITES = {
    "piste": "piste.nebula-agency.online",
    "agence": "www.nebula-agency.online",
    "agence-apex": "nebula-agency.online",
    "partenaires": "partenaires.nebula-agency.online",
    "vendora": "vendora.nebula-agency.online",
}
ZONE = "nebula-agency.online"

# ⚠️ Cloudflare renvoie 403 a un robot qui ne se presente pas comme un
# navigateur. On verifie ce que voit un VISITEUR, pas ce que voit un script.
NAVIGATEUR = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "fr",
}


def jeton():
    f = RACINE / "secrets/cloudflare-zone.env"
    if not f.exists():
        raise SystemExit("  secrets/cloudflare-zone.env introuvable.")
    for l in io.open(f, encoding="utf-8"):
        if l.startswith("CLOUDFLARE_PURGE_TOKEN="):
            return l.split("=", 1)[1].strip()
    raise SystemExit(
        "  CLOUDFLARE_PURGE_TOKEN absent de secrets/cloudflare-zone.env.\n"
        "  Il faut un jeton Cloudflare portant « Zone · Cache Purge · Purge ».\n"
        "  Le jeton de zone existant ne suffit pas : il ne sait que LIRE."
    )


def appeler(chemin, t, corps=None):
    r = urllib.request.Request(
        API + chemin,
        data=json.dumps(corps).encode() if corps else None,
        headers={"Authorization": f"Bearer {t}", "Content-Type": "application/json"},
        method="POST" if corps else "GET",
    )
    try:
        with urllib.request.urlopen(r, timeout=25) as rep:
            return json.load(rep)
    except urllib.error.HTTPError as e:
        return json.load(e)


def zone_id(t):
    d = appeler(f"/zones?name={ZONE}", t)
    r = d.get("result") or []
    if not r:
        raise SystemExit(f"  zone {ZONE} introuvable : {str(d.get('errors'))[:120]}")
    return r[0]["id"]


def verifier(hote):
    """Un 200 ne prouve RIEN : c'est le CORPS qu'il faut regarder.

    Le jour de la panne, tous les en-têtes étaient parfaits : 200, text/css,
    49 Ko. Seule la lecture du contenu montrait « error code: 502 »."""
    import re

    try:
        with urllib.request.urlopen(
            urllib.request.Request(f"https://{hote}/", headers=NAVIGATEUR),
            timeout=20,
        ) as rep:
            html = rep.read().decode("utf-8", "replace")
    except Exception as e:
        return f"page injoignable · {e}"

    soucis = []
    for u in set(re.findall(r'(?:href|src)="(/assets/[^"]+)"', html)):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(f"https://{hote}{u}", headers=NAVIGATEUR), timeout=20
            ) as rep:
                debut = rep.read(200).decode("utf-8", "replace")
        except Exception as e:
            soucis.append(f"{u} : {e}")
            continue
        if "error code" in debut.lower() or "<html" in debut.lower():
            soucis.append(f"{u} : sert une ERREUR ({debut.strip()[:40]})")
    return "sain" if not soucis else " · ".join(soucis)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    seul_verifier = "--verifier" in sys.argv
    cibles = {k: v for k, v in SITES.items() if not args or k in args}
    if not cibles:
        raise SystemExit(f"  connus : {', '.join(SITES)}")

    if seul_verifier:
        print()
        for nom, hote in cibles.items():
            print(f"  {nom:<14} {verifier(hote)}")
        return 0

    t = jeton()
    z = zone_id(t)
    print()
    for nom, hote in cibles.items():
        d = appeler(f"/zones/{z}/purge_cache", t, {"hosts": [hote]})
        if not d.get("success"):
            # certains jetons n'autorisent que la purge par fichier
            d = appeler(f"/zones/{z}/purge_cache", t, {"files": [f"https://{hote}/"]})
        etat = "vidé" if d.get("success") else f"REFUSÉ · {str(d.get('errors'))[:80]}"
        print(f"  {nom:<14} {hote:<38} {etat}")
    print("\n  Comptez une minute avant de reverifier : la purge se propage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
