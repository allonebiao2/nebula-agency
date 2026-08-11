/**
 * EXTRAIT LA CARTE DU SITE ACTUEL VERS LE PROJET NEXT.
 *
 * ⚠️ POURQUOI UN SCRIPT ET PAS UNE RECOPIE À LA MAIN. La carte fait 48 plats
 * avec leurs prix, leurs deuxièmes tailles et leurs descriptions. Recopier
 * tout ça, c'est s'offrir une faute de prix, et une faute de prix se paie à
 * chaque commande, tous les jours, sans que personne la voie.
 *
 * Le tableau `CATS` et la table `PHOTO` sont lus directement dans
 * `index.html`, évalués, puis réécrits en TypeScript.
 *
 *   node _outils/_extraire_carte.js
 */
const fs = require("fs");
const path = require("path");

const RACINE = path.join(__dirname, "..");
const s = fs.readFileSync(path.join(RACINE, "index.html"), "utf8");

/** Découpe le littéral qui suit `nom`, en comptant les accolades. */
function bloc(nom, ouvre) {
  const i = s.indexOf(nom);
  if (i < 0) throw new Error("introuvable dans index.html : " + nom);
  const d = s.indexOf(ouvre, i);
  const [a, b] = ouvre === "[" ? ["[", "]"] : ["{", "}"];
  let p = 0,
    j = d;
  for (; j < s.length; j++) {
    if (s[j] === a) p++;
    else if (s[j] === b) {
      p--;
      if (!p) break;
    }
  }
  return s.slice(d, j + 1);
}

// les icônes sont des chaînes SVG définies plus haut dans le fichier : on ne
// les veut pas ici, on les neutralise le temps de l'évaluation
const FIRE = "", GRILL = "", DROP = "", LEAF = "", CUP = "", GLASS = "", BURGER = "", PIZZA = "";
void [FIRE, GRILL, DROP, LEAF, CUP, GLASS, BURGER, PIZZA];

const CATS = eval("(" + bloc("var CATS=", "[") + ")");
const PHOTO = eval("(" + bloc("var PHOTO=", "{") + ")");

const BS = String.fromCharCode(92);
const esc = (t) =>
  String(t || "")
    .split(BS)
    .join(BS + BS)
    .split('"')
    .join(BS + '"');

let out = `/**
 * LA CARTE COMPLÈTE — ${CATS.reduce((n, c) => n + c.items.length, 0)} plats, ${CATS.length} catégories.
 *
 * ⚠️ FICHIER GÉNÉRÉ, NE PAS ÉDITER À LA MAIN.
 * Source : le tableau \`CATS\` de \`../../index.html\`, qui reste la vérité.
 * Régénérer :  node _outils/_extraire_carte.js
 */

export type Plat = {
  n: string;
  d?: string;
  p: number;
  p2?: number;
  joq?: boolean;
  img: string;
};

export type Cat = {
  id: string;
  label: string;
  tag: string;
  note?: string;
  acc?: "grillades" | "sauces";
  items: Plat[];
};

/** Les accompagnements au choix, repris tels quels du site. */
export const ACC: Record<string, string[]> = {
  grillades: ["Riz", "Attiéké", "Aloco", "Frites", "Pommes sautées", "Pomme vapeur", "Pâte rouge", "Bomiwo", "Akassa", "Igname frit"],
  sauces: ["Riz", "Attiéké", "Pâte noire", "Agbéli", "Pâte de manioc", "Pâte de maïs", "Piron", "Akassa", "Pommes sautées", "Frites"],
};

export const CARTE: Cat[] = [
`;

CATS.forEach((c) => {
  const acc =
    c.id === "grillades" ? '\n    acc: "grillades",' : c.id === "sauces" ? '\n    acc: "sauces",' : "";
  out += `  {
    id: "${c.id}",
    label: "${esc(c.label)}",
    tag: "${esc(c.tag)}",${c.note ? `\n    note: "${esc(c.note)}",` : ""}${acc}
    items: [
`;
  c.items.forEach((it) => {
    const k = PHOTO[it.n.toLowerCase()];
    if (!k) console.warn("  ⚠️ pas de photo pour :", it.n);
    out += `      { n: "${esc(it.n)}"`;
    if (it.d) out += `, d: "${esc(it.d)}"`;
    out += `, p: ${it.p}`;
    if (it.p2) out += `, p2: ${it.p2}`;
    if (it.joq) out += `, joq: true`;
    out += `, img: "/carte/${k}.webp" },\n`;
  });
  out += "    ],\n  },\n";
});
out += "];\n\nexport const NB_PLATS = CARTE.reduce((n, c) => n + c.items.length, 0);\n";

const dst = path.join(RACINE, "experience", "data", "carte.ts");
fs.mkdirSync(path.dirname(dst), { recursive: true });
fs.writeFileSync(dst, out, "utf8");
console.log(
  CATS.length + " catégories, " +
    CATS.reduce((n, c) => n + c.items.length, 0) + " plats → " + dst
);
