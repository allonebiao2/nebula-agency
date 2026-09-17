# -*- coding: utf-8 -*-
"""
La carte : **où, dans la journée et dans quel état de marché, 2 R tombe avant 1 R ?**

    python -m trading.recherche.carte --base EURUSD --tf M5
    python -m trading.recherche.carte --base NAS100 --tf M1 --schema atr14x2

Avant d'écrire une règle, on mesure ce qu'il y a à prendre. Chaque barre permise est étiquetée
(`etiquettes.py`), puis regroupée par caractéristique (`caracteristiques.py`). Pour chaque case on
lit trois choses :

  · **le taux d'objectif** : la part des minutes où 2 R serait tombé avant le stop ;
  · **le point mort de la case** : le taux qu'il aurait fallu pour que l'espérance soit nulle, coûts
    et sorties de fin de journée compris. Ce n'est PAS 33 % : c'est ce que disent les trades ;
  · **l'excès** (taux − point mort) et son z, qui dit si l'écart tient debout vu le nombre de barres.

⚠️ Une carte n'est pas un résultat de stratégie : les barres se chevauchent (une minute sur deux
raconte le même mouvement), donc son z est optimiste. Elle sert à CHOISIR où chercher. Ce qui compte
ensuite se mesure en walk-forward, une position à la fois, et s'inscrit au registre.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from . import banc, caracteristiques, etiquettes, scelle
from .lancer import DOSSIER

SORTIE = DOSSIER / "carte"


def excedent(R: np.ndarray, objectif: np.ndarray) -> dict:
    """Le taux d'objectif, le point mort de l'échantillon, leur écart et son z."""
    n = len(R)
    if n < 30 or not objectif.any() or objectif.all():
        return {"n": int(n), "taux": float(objectif.mean()) if n else float("nan"), "z": float("nan")}
    p0 = banc.point_mort_objectif(R, objectif)
    p = float(objectif.mean())
    z = (p - p0) / np.sqrt(max(p0 * (1 - p0) / n, 1e-18))
    return {"n": int(n), "taux": round(p, 4), "point_mort": round(p0, 4),
            "exces": round(p - p0, 4), "z": round(float(z), 2),
            "esperance_R": round(float(R.mean()), 4)}


def plafond(achat: etiquettes.Etiquettes, vente: etiquettes.Etiquettes) -> dict:
    """**Le plafond de toute stratégie directionnelle**, à ce schéma de stop.

    Sur chaque barre on regarde ce qui serait arrivé dans les DEUX sens. Un devin qui choisirait
    toujours le bon sens gagnerait « au moins un des deux ». Ce nombre borne tout ce qu'une règle,
    un modèle ou une intuition pourront jamais obtenir ici : si le plafond est à 45 %, viser 70 %
    n'a pas de sens sur ce schéma, il faut changer de stop ou d'unité de temps, pas de règle.
    """
    v = achat.valides() & vente.valides()
    if not v.any():
        return {"barres": 0}
    a, b = achat.objectif()[v], vente.objectif()[v]
    ra, rb = achat.R[v], vente.R[v]
    return {"barres": int(v.sum()),
            "plafond_objectif": round(float((a | b).mean()), 4),
            "les_deux": round(float((a & b).mean()), 4),
            "aucun": round(float((~a & ~b).mean()), 4),
            "plafond_esperance_R": round(float(np.maximum(ra, rb).mean()), 4),
            "achat": round(float(a.mean()), 4), "vente": round(float(b.mean()), 4)}


def balayage_stops(base: str, tf: str, points_liste=None) -> list[dict]:
    """**La question qui précède toutes les autres** : à quelle taille de stop l'objectif de Mongazi
    est-il seulement ATTEIGNABLE ?

    Deux forces opposées, mesurées ici et pas supposées :
      · un stop serré rend 2 R facile à toucher dans la journée (le plafond monte) ;
      · un stop serré fait payer le spread en proportion (le point mort monte aussi).
    La bonne zone, s'il en existe une, est celle où le plafond dépasse 50 % ET où le coût en R reste
    petit. Si aucune ligne ne le fait, aucune règle ne le fera : il faudra changer d'unité de temps.
    """
    if points_liste is None:
        points_liste = ([20, 30, 50, 80, 120, 200, 300, 500] if base.upper() == "EURUSD"
                        else [150, 250, 400, 700, 1200, 2000, 3500])
    lignes = []
    for serie in scelle.series_decouverte(base, tf):
        cout_R = float(np.median(serie.couts_prix()) / serie.point)
        for pts in points_liste:
            stop = etiquettes.stops_points(serie, pts)
            if pts * serie.point < serie.stop_min_prix - 1e-12:
                continue                       # plus court que le minimum du courtier : impossible
            a = etiquettes.etiqueter(serie, stop_dist=stop, sens=+1, schema=f"{pts}pts")
            v = etiquettes.etiqueter(serie, stop_dist=stop, sens=-1, schema=f"{pts}pts")
            pl = plafond(a, v)
            va = a.valides()
            p0 = banc.point_mort_objectif(a.R[va], a.objectif()[va]) if va.any() else float("nan")
            lignes.append({"base": base, "tf": tf, "source": serie.source, "stop_points": pts,
                           "cout_aller_retour_R": round(2 * cout_R / pts, 4),
                           "point_mort": round(float(p0), 4), **pl,
                           "duree_mediane_barres": int(np.median(a.duree[va])) if va.any() else None})
            d = lignes[-1]
            print(f"  {base} {tf} stop {pts:>5d} pts : plafond {100 * d['plafond_objectif']:5.1f} %  "
                  f"point mort {100 * d['point_mort']:5.1f} %  coût {d['cout_aller_retour_R']:.3f} R  "
                  f"durée médiane {d['duree_mediane_barres']} barres  (n={d['barres']})", flush=True)
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / f"plafonds_{base}_{tf}.json").write_text(
        json.dumps(lignes, ensure_ascii=False, default=str), encoding="utf-8")
    return lignes


def balayage_limites(base: str, tf: str, stops=None, retraits=(0.25, 0.5, 1.0), expiration: int = 30) -> list[dict]:
    """Le plafond quand on entre sur un RETOUR de prix, pas au marché.

    Mécanisme réel des scalpers : attendre un meilleur prix rapproche l'objectif en valeur absolue.
    Si le plafond monte vraiment, c'est là qu'il faut chercher ; s'il ne monte pas, l'idée est morte
    et on ne la repassera pas en boucle sous dix habillages différents.
    """
    lignes = []
    for serie in scelle.series_decouverte(base, tf):
        pts = stops or ([30, 50, 80] if base.upper() == "EURUSD" else [700, 1200, 2000])
        for p in pts:
            stop = etiquettes.stops_points(serie, p)
            for k in retraits:
                retrait = stop * k
                a = etiquettes.etiqueter_limite(serie, stop_dist=stop, retrait=retrait, sens=+1,
                                                expiration=expiration)
                v = etiquettes.etiqueter_limite(serie, stop_dist=stop, retrait=retrait, sens=-1,
                                                expiration=expiration)
                va, vv = a.valides(), v.valides()
                p0 = banc.point_mort_objectif(a.R[va], a.objectif()[va]) if va.any() else float("nan")
                # ⛔ PIÈGE MESURÉ : le plafond « au moins un des deux sens » ne vaut RIEN ici.
                # À 0,5 R de retrait, les deux ordres sont des miroirs exacts (objectif à ±1,5 d,
                # stop à ∓1,5 d) : quand les deux sont servis, l'un gagne forcément, et le plafond
                # affiche 99 %. Ce n'est pas un avantage, c'est une tautologie de sélection.
                # Le seul plafond honnête rapporte les réussites au nombre d'ordres POSÉS.
                n_permis = int(np.count_nonzero(masque_entree(serie.base, serie.temps)))
                gagne = int(np.count_nonzero(a.objectif() | v.objectif()))
                d = {"base": base, "tf": tf, "source": serie.source, "stop_points": p,
                     "retrait_R": k, "expiration": expiration, "point_mort": round(float(p0), 4),
                     "ordres_poses": n_permis,
                     "plafond_par_ordre_pose": round(gagne / max(n_permis, 1), 4),
                     "servis_achat": int(va.sum()), "servis_vente": int(vv.sum()),
                     "part_servie": round(float(va.mean()), 4),
                     "objectif_achat": round(float(a.objectif()[va].mean()), 4) if va.any() else None,
                     "objectif_vente": round(float(v.objectif()[vv].mean()), 4) if vv.any() else None,
                     "esperance_achat_R": round(float(a.R[va].mean()), 4) if va.any() else None,
                     "esperance_vente_R": round(float(v.R[vv].mean()), 4) if vv.any() else None}
                lignes.append(d)
                print(f"  {base} {tf} limite stop {p:>5d} pts, retrait {k:.2f} R : servi "
                      f"{100 * d['part_servie']:4.1f} %  objectif achat "
                      f"{100 * (d['objectif_achat'] or 0):5.1f} % / vente "
                      f"{100 * (d['objectif_vente'] or 0):5.1f} %  (point mort "
                      f"{100 * d['point_mort']:5.1f} %)  espérance {d['esperance_achat_R']} / "
                      f"{d['esperance_vente_R']} R", flush=True)
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / f"limites_{base}_{tf}.json").write_text(json.dumps(lignes, ensure_ascii=False, default=str),
                                                      encoding="utf-8")
    return lignes


def par_caracteristique(e: etiquettes.Etiquettes, X: dict[str, np.ndarray],
                        *, minimum: int = 200) -> dict:
    """Pour chaque caractéristique, l'état de chaque case."""
    valides = e.valides()
    R, obj = e.R[valides], e.objectif()[valides]
    out = {"_global": excedent(R, obj)}
    for nom, valeurs in X.items():
        idx, bords = caracteristiques.cases(valeurs[valides], nom)
        if nom == "minute_ny":                      # une case par quart d'heure
            idx = (valeurs[valides] // 15).astype(np.int64)
            bords = np.arange(0, 1441, 15, dtype=float)
        lignes = []
        for k in np.unique(idx):
            if k < 0:
                continue
            m = idx == k
            if m.sum() < minimum:
                continue
            borne = (float(bords[k]), float(bords[min(k + 1, len(bords) - 1)])) if len(bords) > k else None
            lignes.append({"case": int(k), "de": borne[0] if borne else None,
                           "a": borne[1] if borne else None, **excedent(R[m], obj[m])})
        if lignes:
            out[nom] = lignes
    return out


def plafonds_par_caracteristique(achat: etiquettes.Etiquettes, vente: etiquettes.Etiquettes,
                                 X: dict[str, np.ndarray], *, minimum: int = 500) -> list[dict]:
    """Le plafond, case par case. **C'est ici que se décide où chercher.**

    Le plafond global d'un schéma peut être à 45 % et cacher des moments à 70 % : ce sont ces
    moments-là qui peuvent porter l'objectif de Mongazi. À l'inverse, une case dont le plafond est
    sous 50 % est définitivement hors de portée, quelle que soit la règle qu'on y écrira.
    """
    v = achat.valides() & vente.valides()
    if not v.any():
        return []
    a, b = achat.objectif()[v], vente.objectif()[v]
    haut = a | b
    lignes = []
    for nom, valeurs in X.items():
        vals = valeurs[v]
        if nom == "minute_ny":
            idx = (vals // 15).astype(np.int64)
            bords = np.arange(0, 1441, 15, dtype=float)
        else:
            idx, bords = caracteristiques.cases(vals, nom)
        for k in np.unique(idx):
            if k < 0:
                continue
            m = idx == k
            n = int(m.sum())
            if n < minimum:
                continue
            lignes.append({"caracteristique": nom, "case": int(k),
                           "de": float(bords[min(k, len(bords) - 1)]),
                           "a": float(bords[min(k + 1, len(bords) - 1)]), "n": n,
                           "plafond": round(float(haut[m].mean()), 4),
                           "achat": round(float(a[m].mean()), 4),
                           "vente": round(float(b[m].mean()), 4)})
    return sorted(lignes, key=lambda x: -x["plafond"])


def meilleures(cartes: dict, *, minimum: int = 500, combien: int = 25) -> list[dict]:
    """Les cases qui dépassent leur point mort, les plus solides d'abord."""
    lignes = []
    for cle, contenu in cartes.items():
        sens, schema, nom = cle.split("|") if "|" in cle else (cle, "", "")
        for carac, cases in contenu.items():
            if carac.startswith("_"):
                continue
            for c in cases:
                if c["n"] >= minimum and c.get("exces", -1) > 0:
                    lignes.append({"sens": sens, "schema": schema, "caracteristique": carac, **c})
    return sorted(lignes, key=lambda x: -x["z"])[:combien]


def planche(titre: str, lignes: list[tuple[str, float, float, int]], chemin) -> None:
    """Une bande par case : l'excès au-dessus du point mort, vert vers le haut, rouge vers le bas."""
    import cv2
    h_ligne, largeur = 26, 1000
    img = np.full((h_ligne * (len(lignes) + 2), largeur, 3), 250, np.uint8)
    cv2.putText(img, titre, (12, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1, cv2.LINE_AA)
    zero = 560
    echelle = 2200.0                      # 1 point de pourcentage d'excès = 22 pixels
    for i, (nom, exces, taux, n) in enumerate(lignes):
        y = h_ligne * (i + 2)
        cv2.putText(img, f"{nom[:44]:44s} {100 * taux:5.1f}%  n={n:>7d}", (12, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (60, 60, 60), 1, cv2.LINE_AA)
        x = int(zero + exces * echelle)
        couleur = (80, 170, 60) if exces > 0 else (60, 60, 210)
        cv2.rectangle(img, (min(zero, x), y - 10), (max(zero, x), y - 2), couleur, -1)
    cv2.line(img, (zero, h_ligne), (zero, img.shape[0]), (150, 150, 150), 1)
    cv2.imwrite(str(chemin), img)


def dresser(base: str, tf: str, schemas=("atr14x2", "atr14x4", "atr60x4"), *, minimum: int = 200) -> dict:
    SORTIE.mkdir(parents=True, exist_ok=True)
    cartes: dict[str, dict] = {}
    resumes, plafonds = [], []
    for serie in scelle.series_decouverte(base, tf):
        etiquette_source = f"{serie.source}:{str(serie.temps[0])[:7]}→{str(serie.temps[-1])[:7]}"
        X = caracteristiques.construire(serie)
        for schema in schemas:
            deux = etiquettes.deux_sens(serie, schema)
            for sens, e in deux.items():
                cle = f"{'achat' if sens > 0 else 'vente'}|{schema}|{etiquette_source}"
                cartes[cle] = par_caracteristique(e, X, minimum=minimum)
                resumes.append({"cle": cle, **e.resume()})
                print(f"  {cle:52s} {e.resume()}", flush=True)
            pl = plafond(deux[1], deux[-1])
            cases_hautes = plafonds_par_caracteristique(deux[1], deux[-1], X)
            plafonds.append({"schema": schema, "source": etiquette_source, **pl,
                             "cases_hautes": cases_hautes[:20]})
            print(f"    PLAFOND {schema:9s} : un devin parfait atteindrait {100 * pl['plafond_objectif']:.1f} % "
                  f"de 2 R (les deux sens gagnent {100 * pl['les_deux']:.1f} %, aucun "
                  f"{100 * pl['aucun']:.1f} %)", flush=True)
            for c in cases_hautes[:3]:
                print(f"       plus haute case : {c['caracteristique']:24s} [{c['de']:.3g} ; {c['a']:.3g}] "
                      f"plafond {100 * c['plafond']:.1f} %  (achat {100 * c['achat']:.1f} %, "
                      f"vente {100 * c['vente']:.1f} %, n={c['n']})", flush=True)
        del X
    fichier = SORTIE / f"carte_{base}_{tf}.json"
    fichier.write_text(json.dumps({"base": base, "tf": tf, "resumes": resumes, "plafonds": plafonds,
                                   "meilleures": meilleures(cartes), "cartes": cartes},
                                  ensure_ascii=False, default=str), encoding="utf-8")
    top = meilleures(cartes)
    if top:
        planche(f"{base} {tf} : exces au-dessus du point mort",
                [(f"{t['sens'][:3]} {t['schema']} {t['caracteristique']} [{t['de']:.2f};{t['a']:.2f}]",
                  t["exces"], t["taux"], t["n"]) for t in top],
                SORTIE / f"carte_{base}_{tf}.png")
    print(f"\n  {fichier}")
    return_plafond = max((p.get("plafond_objectif", 0) for p in plafonds), default=0)
    print(f"  PLAFOND LE PLUS HAUT, tous schémas : {100 * return_plafond:.1f} % de 2 R avec un devin "
          f"parfait (objectif de Mongazi : plus de 50 %)")
    for t in top[:15]:
        print(f"    z={t['z']:6.2f}  {t['sens']:5s} {t['schema']:8s} {t['caracteristique']:24s} "
              f"[{t['de']:.3g} ; {t['a']:.3g}]  taux {100 * t['taux']:.1f} % "
              f"(point mort {100 * t['point_mort']:.1f} %)  n={t['n']}")
    return {"fichier": str(fichier), "meilleures": top}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="EURUSD")
    p.add_argument("--tf", default="M5")
    p.add_argument("--schemas", nargs="*", default=["atr14x2", "atr14x4", "atr60x4"])
    p.add_argument("--minimum", type=int, default=200)
    p.add_argument("--plafonds", action="store_true", help="balayage des tailles de stop (à faire en premier)")
    p.add_argument("--limites", action="store_true", help="plafond des entrées sur retour de prix")
    a = p.parse_args()
    if a.limites:
        balayage_limites(a.base, a.tf)
    elif a.plafonds:
        balayage_stops(a.base, a.tf)
    else:
        dresser(a.base, a.tf, tuple(a.schemas), minimum=a.minimum)
    return 0


if __name__ == "__main__":
    sys.exit(main())
