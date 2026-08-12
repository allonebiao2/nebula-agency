# -*- coding: utf-8 -*-
"""Rend TOUTE la carte accessible depuis le héros, et la structure pour la vente.

Mongazi : « je veux que toute personne qui vient directement à partir de la héros
puisse commander tous les plats, toutes les catégories, tout accessible depuis
cette belle héros section, là ça devient un vrai catalogue optimisé pour la
vente. »

Trois changements, et aucun n'est cosmétique :

1. LE FILTRE DEVENAIT UN MUR. La barre de catégories MASQUAIT les sept autres
   univers : choisir « Pizza » faisait disparaître 38 plats. Pour un catalogue,
   c'est l'inverse de ce qu'on veut. Les chips deviennent des ANCRES : tout
   reste affiché, on saute au bon endroit, et la chip active suit le
   défilement.
2. LE HÉROS NE DISAIT PAS QUE LA CARTE EXISTAIT. Le bouton « … » ouvre
   désormais le tiroir des huit univers, avec le nombre de plats de chacun.
3. L'APPEL À L'ACTION ANNONCE LE NOMBRE. « Voir la carte » devient « Voir la
   carte · 48 plats » : un chiffre vend mieux qu'un verbe.
"""
import io
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(ICI, "..", "experience")


def remplacer(chemin, regles):
    p = os.path.join(EXP, chemin)
    s = io.open(p, encoding="utf-8").read()
    n = 0
    for a, b in regles:
        c = s.count(a)
        if c == 0:
            print("  ARRET : motif ABSENT dans %s : %s" % (chemin, a[:70]))
            return None
        s = s.replace(a, b)
        n += c
    io.open(p, "w", encoding="utf-8").write(s)
    print("  %-28s %d remplacements" % (chemin, n))
    return n


# ── 1 · la carte : ancres + scroll-spy au lieu du filtre ───────────
CARTE = [
    (
        """export default function Carte() {
  const [filtre, setFiltre] = useState<string>("tout");""",
        """export default function Carte() {
  /* ⚠️ PLUS DE FILTRE, DES ANCRES. Le filtre masquait les sept autres univers :
     choisir « Pizza » faisait disparaître 38 plats. Sur un catalogue, ce qu'on
     cache ne se vend pas. Tout reste affiché, la barre sert à SAUTER, et la
     catégorie active suit le défilement toute seule. */
  const [actif, setActif] = useState<string>(CARTE[0].id);""",
    ),
    (
        """  /* les blocs de catégorie se révèlent à l'arrivée, une seule fois */""",
        """  /* la catégorie affichée dans la barre suit le défilement */
  useEffect(() => {
    const obs = new IntersectionObserver(
      (es) => {
        const vus = es
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (vus[0]) setActif(vus[0].target.id.replace("cat-", ""));
      },
      { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
    );
    CARTE.forEach((c) => {
      const e = document.getElementById("cat-" + c.id);
      if (e) obs.observe(e);
    });
    return () => obs.disconnect();
  }, []);

  function sauter(id: string) {
    document.getElementById("cat-" + id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* les blocs de catégorie se révèlent à l'arrivée, une seule fois */""",
    ),
    (
        """  const cats = filtre === "tout" ? CARTE : CARTE.filter((c) => c.id === filtre);

""",
        "",
    ),
    (
        """          {[{ id: "tout", label: "Tout" }, ...CARTE].map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => setFiltre(c.id)}
              className="shrink-0 rounded-full border px-4 py-2 text-[0.82rem] font-medium transition"
              style={
                filtre === c.id
                  ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                  : { borderColor: "rgba(29,26,23,.18)", color: "#55504a" }
              }
            >
              {c.label}
            </button>
          ))}""",
        """          {CARTE.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => sauter(c.id)}
              aria-current={actif === c.id}
              className="shrink-0 rounded-full border px-4 py-2 text-[0.82rem] font-medium transition"
              style={
                actif === c.id
                  ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                  : { borderColor: "rgba(29,26,23,.18)", color: "#55504a" }
              }
            >
              {c.label}
              <span className="ml-1.5 opacity-55">{c.items.length}</span>
            </button>
          ))}""",
    ),
    (
        """        {cats.map((c) => (""",
        """        {CARTE.map((c) => (""",
    ),
]

# ── 2 · le héros : le tiroir des catégories ────────────────────────
EXPERIENCE = [
    (
        'import { TopBar, BottomNav, Indicator } from "./Chrome";',
        'import { TopBar, BottomNav, Indicator } from "./Chrome";\nimport Categories from "./Categories";',
    ),
    (
        "  const [i, setI] = useState(0);          // le plat courant, entier",
        "  const [i, setI] = useState(0);          // le plat courant, entier\n  const [carteOuverte, setCarteOuverte] = useState(false);",
    ),
    ("        <TopBar />", "        <TopBar onCarte={() => setCarteOuverte(true)} />"),
    (
        "        <Rail actif={i} onAller={aller} />",
        "        <Rail actif={i} onAller={aller} />\n        <Categories ouvert={carteOuverte} onFermer={() => setCarteOuverte(false)} />",
    ),
]

# ── 3 · les boutons du haut et l'appel à l'action ──────────────────
CHROME = [
    (
        """/** Les boutons flottants du haut : retour, recherche, menu. */
export function TopBar() {""",
        """/** Les boutons flottants du haut : retour, recherche, et LA CARTE.
 *  ⚠️ Le bouton « … » n'est plus décoratif : il ouvre les huit univers. Un
 *  bouton qui ne fait rien sur le premier écran d'un restaurant, c'est une
 *  vente perdue. */
export function TopBar({ onCarte }: { onCarte: () => void }) {""",
    ),
    (
        """      <a
        href="#carte"
        aria-label="Ouvrir la carte complète"
        className="barre-haut absolute right-6 top-6 grid h-14 w-14 place-items-center rounded-[22px] text-white transition hover:brightness-125 max-md:h-12 max-md:w-12\"""",
        """      <button
        type="button"
        onClick={onCarte}
        aria-label="Ouvrir la carte complète"
        className="barre-haut absolute right-6 top-6 grid h-14 w-14 place-items-center rounded-[22px] text-white transition hover:brightness-125 max-md:h-12 max-md:w-12\"""",
    ),
    (
        """        <svg viewBox="0 0 24 24" className="h-6 w-6" fill="currentColor">
          <circle cx="5" cy="12" r="1.8" />
          <circle cx="12" cy="12" r="1.8" />
          <circle cx="19" cy="12" r="1.8" />
        </svg>
      </a>""",
        """        <svg viewBox="0 0 24 24" className="h-6 w-6" fill="currentColor">
          <circle cx="5" cy="12" r="1.8" />
          <circle cx="12" cy="12" r="1.8" />
          <circle cx="19" cy="12" r="1.8" />
        </svg>
      </button>""",
    ),
]

# ── 4 · l'appel à l'action annonce le nombre de plats ──────────────
TEXTE = [
    ('import { Dish, lienCommande } from "@/data/dishes";',
     'import { Dish, lienCommande } from "@/data/dishes";\nimport { NB_PLATS } from "@/data/carte";'),
    ("          Voir la carte\n        </a>",
     "          Voir la carte <span className=\"opacity-60\">· {NB_PLATS} plats</span>\n        </a>"),
]

if __name__ == "__main__":
    ok = True
    for f, r in (
        ("components/Carte.tsx", CARTE),
        ("components/Experience.tsx", EXPERIENCE),
        ("components/Chrome.tsx", CHROME),
        ("components/DishText.tsx", TEXTE),
    ):
        if remplacer(f, r) is None:
            ok = False
    sys.exit(0 if ok else 1)
