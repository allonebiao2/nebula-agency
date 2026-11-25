# -*- coding: utf-8 -*-
"""
LA ZONE TRAVAUX · ce qu'on fabrique pour les clients, en vagues (Mongazi, 2026-11-25).

La source est `_memoire/travaux.json`. `_memoire/TRAVAUX.md` en est construit à chaque commande : on ne l'édite pas à la
main. Les vagues se calculent toutes seules à partir de la file : les rangs 1 à 3 forment la vague 1, 4 à 6 la vague 2,
et ainsi de suite. Rien n'est jamais « bloqué » : s'il manque quelque chose, on avance avec ce qu'on a (produits
d'exemple marqués comme tels, « photo à venir »), on livre, et on complète ensuite.

    python scripts/travaux.py voir                                  # la file, avec les rangs et les vagues
    python scripts/travaux.py rang <travail ou rang> <nouveau rang> # /rang : déplace un travail dans la file
    python scripts/travaux.py ajouter "<client>" "<travail>" [--besoin ".."] [--echeance ".."] [--rang N]
    python scripts/travaux.py livrer <travail ou rang> [--lien URL]  # sort de la file, descend dans « Livrés »
    python scripts/travaux.py ecrire                                # reconstruit TRAVAUX.md
Un travail se désigne par son rang (« 4 ») ou par un bout de son nom (« djibom », « yaz »).
"""
import io
import json
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "_memoire" / "travaux.json"
PAGE = RACINE / "_memoire" / "TRAVAUX.md"
PAR_VAGUE = 3

ENTETE = """# ZONE TRAVAUX · ce qui est à fabriquer, en vagues

> ⚙️ Page CONSTRUITE par `python scripts/travaux.py` à partir de `_memoire/travaux.json` : ne pas l'éditer à la main.
> Mongazi ajoute des travaux avec **`/vague <client> : <travail> ; …`** et change leur place avec
> **`/rang <travail> <position>`** (exemple : `/rang djibom 2`).

Créée le 2026-11-25 à la demande de Mongazi : « crée cette zone, et elle doit fonctionner en vagues ». On y met **ce
qu'on fabrique pour un client** : aperçu, catalogue, vitrine, étiquette, affiche, vidéo. Ce qui attend une décision
va dans `EN-INSTANCE.md`, les messages à envoyer dans NEBULA Suivi. Le détail privé d'un aperçu (numéros compris) est
dans `nebula-apercus/PLAN-APERCUS-25-11.md`.

## Les règles des vagues
1. **Une vague à la fois.** On lance ensemble ses travaux, puis on les finit, on les vérifie (QC, Polaris ou un
   regard sur les captures) et on les livre **avant** d'ouvrir la vague suivante.
2. **3 travaux au plus par vague** : les rangs 1 à 3 forment la vague 1, les rangs 4 à 6 la vague 2, et ainsi de
   suite. On reste à 3 parce que le PC a 8 Go et qu'on fait 3 aperçus par jour.
3. **Ordre d'arrivée** : un nouveau travail va au bout de la file. **Mongazi change l'ordre avec `/rang`.**
4. **Une promesse en retard passe en tête.**
5. **⛔ Rien n'est bloqué** (Mongazi, 25/11 : « ne bloque rien »). S'il manque des photos, une décision ou une mesure,
   on avance avec ce qu'on a : produits d'exemple marqués comme tels, « photo à venir », une taille standard
   proposée. On livre, et on complète dès que l'information arrive.
6. **Un travail livré** descend dans « Livrés », avec son lien et sa date.
"""


def lire():
    return json.load(io.open(DONNEES, encoding="utf-8"))


def ecrire(d):
    json.dump(d, io.open(DONNEES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = [ENTETE]
    F = d["file"]
    for v in range(0, len(F), PAR_VAGUE):
        n = v // PAR_VAGUE + 1
        L.append(f"\n## {'🔨' if n == 1 else '🔜'} Vague {n}{' · EN COURS' if n == 1 else ''}\n")
        L.append("| Rang | Travail | Client | Ce qu'il faut | Échéance |\n|---|---|---|---|---|")
        for i, t in enumerate(F[v:v + PAR_VAGUE], v + 1):
            L.append(f"| {i} | {t['travail']} | {t['client']} | {t.get('besoin', '')} | {t.get('echeance', '')} |")
    if not F:
        L.append("\n## 🔨 Aucune vague en cours : la file est vide.\n")
    L.append("\n## ✅ Livrés\n| Date | Client | Travail | Lien |\n|---|---|---|---|")
    for t in reversed(d["livres"]):
        L.append(f"| {t['date']} | {t['client']} | {t['travail']} | {t.get('lien', '')} |")
    io.open(PAGE, "w", encoding="utf-8").write("\n".join(L) + "\n")


def trouver(F, qui):
    if qui.isdigit():
        i = int(qui) - 1
        if 0 <= i < len(F):
            return i
        sys.exit(f"pas de rang {qui} (la file en compte {len(F)})")
    q = qui.lower()
    t = [i for i, x in enumerate(F) if q in f"{x['client']} {x['travail']}".lower()]
    if len(t) != 1:
        sys.exit(f"« {qui} » désigne {len(t)} travaux : préciser (ou donner le rang)")
    return t[0]


def voir(d):
    F = d["file"]
    for i, t in enumerate(F, 1):
        if (i - 1) % PAR_VAGUE == 0:
            print(f"── Vague {(i - 1) // PAR_VAGUE + 1}{' (en cours)' if i == 1 else ''}")
        print(f"  {i}. {t['client']} · {t['travail']}" + (f" · {t['echeance']}" if t.get("echeance") else ""))
    if not F:
        print("La file est vide.")


if __name__ == "__main__":
    a = sys.argv[1:] or ["voir"]
    opt = lambda n: a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else None
    libres = [x for i, x in enumerate(a) if not x.startswith("--") and not (i and a[i - 1].startswith("--"))]
    d = lire()
    F = d["file"]
    if a[0] == "rang":
        if len(libres) < 3:
            voir(d); sys.exit("\nusage : rang <travail ou rang> <nouveau rang>")
        i = trouver(F, libres[1])
        n = max(1, min(len(F), int(libres[2])))
        t = F.pop(i); F.insert(n - 1, t)
        ecrire(d); print(f"« {t['client']} · {t['travail']} » passe au rang {n} (vague {(n - 1) // PAR_VAGUE + 1}).\n"); voir(d)
    elif a[0] == "ajouter":
        t = {"client": libres[1], "travail": libres[2], "besoin": opt("--besoin") or "", "echeance": opt("--echeance") or ""}
        r = int(opt("--rang")) if opt("--rang") else len(F) + 1
        F.insert(r - 1, t); ecrire(d); voir(d)
    elif a[0] == "livrer":
        i = trouver(F, libres[1]); t = F.pop(i)
        d["livres"].append({"date": date.today().strftime("%d/%m"), "client": t["client"], "travail": t["travail"], "lien": opt("--lien") or ""})
        ecrire(d); print(f"livré : {t['client']} · {t['travail']}\n"); voir(d)
    elif a[0] == "ecrire":
        ecrire(d); print("TRAVAUX.md reconstruit")
    else:
        voir(d)
