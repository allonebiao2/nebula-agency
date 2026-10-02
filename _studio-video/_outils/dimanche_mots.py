"""Transcription corrigée → src/dimanche/mots.ts

La transcription vient de Whisper large-v3-turbo, en local (horodatage au mot).
Les corrections ci-dessous ont été tranchées en recoupant avec les sous-titres
CapCut incrustés dans la source (un second transcripteur, indépendant) :
chaque clé est l'indice du jeton Whisper, « » supprime le jeton.

    python _outils/dimanche_mots.py <transcription.json>
"""
import json
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
SORTIE = ICI / "src/dimanche/mots.ts"

CORRECTIONS = {
    81: "une",                                   # « aura toujours une longueur d'avance »
    199: "'ai",                                  # « quand j'ai 100 000 »
    232: "tes", 233: "charges", 234: "sont", 235: "",   # CapCut : « si tes charges sont cent-dix-mille »
    240: "mettras",
    250: "tes", 251: "charges", 252: "",
    265: "rester", 266: "",                      # CapCut : « et il va te rester 30 000 »
    423: "un", 424: "trade,",                    # CapCut : « et j'ai … trade je saute dessus »
    433: "ne", 434: "t'appartient pas.",         # ⚠️ à faire relire : CapCut lit « ce trade là peut »
    509: "exécutes",                             # CapCut : « tu es édit »
    557: "par", 558: "",                         # CapCut : « tu commences par gagner »
    572: "à", 573: "21", 574: "heures.",         # CapCut : « ici nous sommes dimanche à vingt-et-une »
    584: "Trading",                              # CapCut : « membre de trading pour tous »
    648: "par", 649: "",                         # CapCut : « commencent par faire des résultats »
    708: "Trading",
    715: "jeudi",
    721: "organisons",
    750: "trading",
    789: "Trading", 790: "",                     # Whisper : « très bien pour tous »
    839: "au", 843: "mesure.", 844: "", 845: "", 846: "", 847: "",
}

# mots qui prennent le surligneur (comparés en minuscules, sans ponctuation)
CLES = {
    "jamais", "planifier", "réussir", "d'avance", "longueur", "argent", "l'argent",
    "100 000", "400 000", "30 000", "110 000", "épargner", "économiser", "disparaître",
    "improviser", "d'improviser", "week-end", "exécutes", "loi", "universelle", "moins",
    "plus", "dimanche", "trading", "gratuite", "100 %", "21", "heures", "live",
    "majestueux", "formation", "stratégie", "valider", "dévalider", "rigoureusement",
    "analyser", "paires", "planifie", "semaine", "trader",
}
# « trader » et « semaine » reviennent souvent : on ne les surligne qu'aux moments forts
CLES_UNE_FOIS = {"trader", "semaine"}


def main(chemin):
    d = json.load(open(chemin, encoding="utf-8"))
    brut = [w for s in d["segments"] for w in s["words"]]
    jetons = []
    for i, w in enumerate(brut):
        txt = CORRECTIONS.get(i, w["w"].strip())
        jetons.append({"i": i, "t": txt, "s": round(w["s"], 3), "e": round(w["e"], 3)})

    # fusion : apostrophe, trait d'union, ponctuation seule, milliers, pourcentage
    mots = []
    for j in jetons:
        if not j["t"]:
            continue
        t = j["t"]
        colle = t.startswith(("'", "-")) or t in {"?", "%", "!"} or (t.startswith("000") and mots and re.fullmatch(r"\d+", mots[-1]["t"]))
        if colle and mots:
            sep = " " if (t.startswith("000") or t == "%") else ""
            mots[-1]["t"] += sep + t
            mots[-1]["e"] = j["e"]
        else:
            mots.append(dict(j))

    vus = set()
    for m in mots:
        nu = re.sub(r"[.,?!;:]+$", "", m["t"]).lower()
        cle = nu in CLES
        if nu in CLES_UNE_FOIS:
            cle = nu not in vus
            vus.add(nu)
        m["k"] = 1 if cle else 0

    debuts = [j["s"] for j in jetons]
    fins = [j["e"] for j in jetons]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8", newline="\n") as f:
        f.write("// Généré par _outils/dimanche_mots.py — ne pas éditer à la main.\n")
        f.write("// Transcription Whisper corrigée par recoupement avec les sous-titres CapCut.\n\n")
        f.write("export type Mot = {i: number; t: string; s: number; e: number; k: 0 | 1};\n\n")
        f.write("/** Les mots affichés, fusionnés (c'est, 100 000, peut-être…). s/e en secondes. */\n")
        f.write("export const MOTS: Mot[] = [\n")
        for m in mots:
            f.write(f"\t{{i: {m['i']}, t: {json.dumps(m['t'], ensure_ascii=False)}, s: {m['s']}, e: {m['e']}, k: {m['k']}}},\n")
        f.write("];\n\n")
        f.write("/** Début et fin de chaque jeton Whisper, par indice brut : les scènes s'y calent. */\n")
        f.write(f"export const DEBUTS: number[] = {json.dumps(debuts)};\n")
        f.write(f"export const FINS: number[] = {json.dumps(fins)};\n")
    print(len(mots), "mots ·", sum(m["k"] for m in mots), "surlignés →", SORTIE)


if __name__ == "__main__":
    main(sys.argv[1])
