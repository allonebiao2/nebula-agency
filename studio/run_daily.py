# -*- coding: utf-8 -*-
"""
NEBULA Studio Quotidien — ORCHESTRATEUR.

1 commande = le contenu du jour, prêt à publier :
   concept (Claude) → vidéo de marque → livraison Telegram + sauvegarde locale.

Usage :
   python run_daily.py            # tout : génère, rend la vidéo, envoie sur Telegram
   python run_daily.py --no-send  # génère + vidéo, sans envoyer (test)
   python run_daily.py --no-video # script seulement (pas de rendu vidéo)

Moteur vidéo : kinetic (défaut, gratuit) ou heygen (STUDIO_VIDEO=heygen, crédits).
"""
import os, sys, json, datetime, pathlib
try:                                   # console Windows = cp1252 → forcer UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import brain

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"

def save(concept, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "concept.json").write_text(
        json.dumps(concept, ensure_ascii=False, indent=2), encoding="utf-8")
    tags = " ".join(concept.get("hashtags", []) or [])
    script_md = (
        f"# {concept.get('brand','')} — {concept.get('format','')}\n"
        f"_{concept.get('date','')} · style {concept.get('visual',{}).get('style','')} · "
        f"{concept.get('platform','')}_\n\n"
        f"## Accroche\n{concept.get('hook','')}\n\n"
        f"## Script (voix off / texte)\n{concept.get('script','')}\n\n"
        f"## Légende\n{concept.get('caption','')}\n\n"
        f"## Hashtags\n{tags}\n\n"
        f"## Appel à l'action\n{concept.get('cta','')}\n\n"
        f"---\n_Pourquoi c'est neuf : {concept.get('freshness_note','')}_\n"
    )
    (out_dir / "script.md").write_text(script_md, encoding="utf-8")
    (out_dir / "caption.txt").write_text(
        (concept.get("caption", "") + "\n\n" + tags).strip(), encoding="utf-8")

def produce_one(idx, count, no_video):
    """Génère 1 post complet (concept + vidéo) dans out/<date>/post-<idx>."""
    concept = brain.generate()                       # relit le ledger → diffère du post précédent
    concept["slot"] = f"{idx}/{count}"
    print(f"  → {concept['brand']} · {concept['format']} · « {concept['hook']} »")
    date = concept.get("date") or datetime.date.today().isoformat()
    out_dir = OUT / date / f"post-{idx}"
    save(concept, out_dir)

    paths = {"video": None, "poster": None, "mp4": None, "webm": None}
    if not no_video:
        engine = os.environ.get("STUDIO_VIDEO", "kinetic").lower()
        try:
            if engine == "heygen":
                print("  • Vidéo (HeyGen, avatar)…")
                import heygen; paths = heygen.render(concept, out_dir)
            else:
                print("  • Vidéo (kinetic, motion design)…")
                import render; paths = render.render(concept, out_dir)
            print(f"    → {paths.get('video')}")
        except Exception as e:
            print("  ⚠ rendu vidéo échoué (le script part quand même) :", e)
    return concept, out_dir, paths

def main():
    no_send = "--no-send" in sys.argv
    no_video = "--no-video" in sys.argv
    count = int(os.environ.get("STUDIO_COUNT", "2"))   # 2 posts / jour par défaut
    for a in sys.argv:                                 # override : --count N
        if a.startswith("--count="):
            count = int(a.split("=", 1)[1])
    brain.load_env()

    last_dir = None
    for i in range(1, count + 1):
        print(f"\n=== POST {i}/{count} ===")
        print("• Concept (Claude)…")
        concept, out_dir, paths = produce_one(i, count, no_video); last_dir = out_dir
        if not no_send:
            print("• Livraison Telegram…")
            try:
                import deliver; deliver.deliver(concept, paths)
            except Exception as e:
                print("  ⚠ livraison échouée :", e)
        else:
            print("• (--no-send) pas d'envoi.")

    base = last_dir.parent if last_dir else OUT
    print(f"\n✓ Terminé. {count} post(s). Dossier du jour : {base}")
    return base

if __name__ == "__main__":
    main()
