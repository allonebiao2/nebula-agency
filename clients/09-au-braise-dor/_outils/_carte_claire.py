# -*- coding: utf-8 -*-
"""Passe la carte et le pied dans la langue du héros : crème, encre, verre blanc.

Mongazi, en défilant : « quand je défile c'est exactement comme la première
version, je veux que ça devienne en entièreté comme ma hero actuelle. »
Il a raison : le site racontait deux histoires, la vitrine crème puis l'ancien
site braise en dessous. On ne change pas de maison au milieu d'une page.

⚠️ Remplacements CIBLÉS, jamais une réécriture : la logique du panier, de la
fiche et du message WhatsApp ne doit pas être touchée par un changement de
couleur. Le script s'arrête net si un motif est introuvable ou ambigu.
"""
import io
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(ICI, "..", "experience", "components")

CARTE = [
    (
        """ * POURQUOI ELLE EST SOMBRE ALORS QUE L'EXPÉRIENCE EST CLAIRE. C'est le rythme
 * du site : on quitte la vitrine, on entre dans la braise. Un site qui garde
 * le même fond du haut en bas n'a pas de chapitres. Et le sombre est
 * l'identité de cette maison depuis le premier jour : elle vend du feu de bois.""",
        """ * ⚠️ ELLE ÉTAIT SOMBRE, ELLE EST DEVENUE CLAIRE (2026-08-12). Mongazi, en
 * défilant : « quand je défile c'est exactement comme la première version, je
 * veux que ça devienne en entièreté comme ma hero actuelle. » Il avait raison :
 * le site racontait deux histoires, la vitrine crème puis l'ancien site braise
 * en dessous. On ne change pas de maison au milieu d'une page.
 * Toutes les couleurs sortent désormais des mêmes jetons que la scène.""",
    ),
    (
        'className="relative z-10 bg-[#0f0b07] pb-40 pt-20 text-[#f3e9dd]"',
        'className="relative z-10 pb-40 pt-24 text-[color:var(--encre)]"',
    ),
    (
        """      style={{
        backgroundImage:
          "radial-gradient(120% 60% at 50% 0%, rgba(255,120,30,.13), transparent 60%)",
      }}""",
        """      style={{
        background:
          "radial-gradient(100% 46% at 50% 0%, rgba(232,118,58,.11), transparent 62%)," +
          "linear-gradient(180deg, var(--mur-2) 0%, var(--mur) 20%, var(--mur) 100%)",
      }}""",
    ),
    (
        'className="mb-3 text-[0.72rem] font-medium uppercase tracking-[0.32em] text-[#e8a86a]"',
        'className="mb-3 text-[0.72rem] font-medium uppercase tracking-[0.32em] text-[#a8542f]"',
    ),
    (
        '<span className="font-extrabold italic" style={{ color: "#f0c48a" }}>',
        '<span className="font-extrabold italic" style={{ color: "#a8542f" }}>',
    ),
    (
        'className="mx-auto mt-4 max-w-xl text-[0.92rem] leading-relaxed text-[#c9b6a2]"',
        'className="mx-auto mt-4 max-w-xl text-[0.92rem] leading-relaxed text-[color:var(--encre-2)]"',
    ),
    (
        'className="sticky top-0 z-20 mb-10 border-y border-white/10 bg-[#0f0b07]/85 py-3 backdrop-blur"',
        'className="sticky top-0 z-20 mb-12 border-y border-black/[0.07] bg-[color:var(--mur)]/85 py-3 backdrop-blur"',
    ),
    (
        """                filtre === c.id
                  ? { background: "#f0c48a", color: "#241505", borderColor: "#f0c48a" }
                  : { borderColor: "rgba(255,255,255,.16)", color: "#d9c8b5" }""",
        """                filtre === c.id
                  ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                  : { borderColor: "rgba(29,26,23,.18)", color: "#55504a" }""",
    ),
    (
        'className="rounded-full border border-white/20 px-3 py-1 text-[0.65rem] uppercase tracking-[0.2em] text-[#e8a86a]"',
        'className="rounded-full border border-black/15 px-3 py-1 text-[0.65rem] uppercase tracking-[0.2em] text-[#a8542f]"',
    ),
    (
        'className="w-full text-[0.82rem] leading-relaxed text-[#a5947f]"',
        'className="w-full text-[0.82rem] leading-relaxed text-[color:var(--encre-2)]"',
    ),
    (
        'className="ct-item group cursor-pointer overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] transition hover:border-[#f0c48a]/40 hover:bg-white/[0.07]"',
        'className="ct-item group cursor-pointer overflow-hidden rounded-3xl border border-white/80 bg-white/70 shadow-[0_14px_40px_rgba(0,0,0,0.06)] backdrop-blur transition hover:-translate-y-1 hover:shadow-[0_24px_56px_rgba(0,0,0,0.10)]"',
    ),
    (
        'className="relative aspect-[5/4] overflow-hidden bg-[#1c1108]"',
        'className="relative aspect-[5/4] overflow-hidden bg-[#e7e0d8]"',
    ),
    (
        'className="absolute left-2 top-2 rounded-full bg-[#f0c48a] px-2 py-1 text-[0.62rem] font-bold uppercase tracking-wide text-[#241505]"',
        'className="absolute left-2 top-2 rounded-full bg-[#1d1a17] px-2 py-1 text-[0.62rem] font-bold uppercase tracking-wide text-[#f6efe6]"',
    ),
    (
        'className="mt-1 line-clamp-2 text-[0.78rem] leading-snug text-[#a5947f] max-md:hidden"',
        'className="mt-1 line-clamp-2 text-[0.78rem] leading-snug text-[color:var(--encre-2)] max-md:hidden"',
    ),
    (
        'className="mt-3 inline-flex items-center gap-1.5 text-[0.8rem] font-semibold text-[#f0c48a]"',
        'className="mt-3 inline-flex items-center gap-1.5 text-[0.8rem] font-semibold text-[#a8542f]"',
    ),
    (
        'className="fixed inset-x-0 bottom-0 z-40 border-t border-white/10 bg-[#0f0b07]/95 px-4 py-3 backdrop-blur"',
        'className="fixed inset-x-0 bottom-0 z-40 border-t border-black/[0.08] bg-[color:var(--mur)]/95 px-4 py-3 backdrop-blur"',
    ),
    (
        """                    mode === m
                      ? { background: "#f0c48a", color: "#241505" }
                      : { background: "rgba(255,255,255,.08)", color: "#d9c8b5" }""",
        """                    mode === m
                      ? { background: "#1d1a17", color: "#f6efe6" }
                      : { background: "rgba(29,26,23,.07)", color: "#55504a" }""",
    ),
    (
        'className="ml-auto text-[0.85rem] text-[#c9b6a2]"',
        'className="ml-auto text-[0.85rem] text-[color:var(--encre-2)]"',
    ),
    ('<b className="text-[#f3e9dd]">{nb}</b>', '<b className="text-[color:var(--encre)]">{nb}</b>'),
    (
        '<b className="text-[#f3e9dd]">{fmt(total)} F</b>',
        '<b className="text-[color:var(--encre)]">{fmt(total)} F</b>',
    ),
    (
        'className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur-sm"',
        'className="fixed inset-0 z-50 grid place-items-center bg-[#1d1a17]/55 p-4 backdrop-blur-sm"',
    ),
    (
        'className="max-h-[90vh] w-full max-w-md overflow-auto rounded-3xl border border-white/12 bg-[#17100a] text-[#f3e9dd]"',
        'className="max-h-[90vh] w-full max-w-md overflow-auto rounded-3xl border border-white/90 bg-[color:var(--mur)] text-[color:var(--encre)] shadow-[0_40px_90px_rgba(0,0,0,0.22)]"',
    ),
    (
        'className="absolute right-3 top-3 grid h-10 w-10 place-items-center rounded-full bg-black/60 backdrop-blur"',
        'className="absolute right-3 top-3 grid h-10 w-10 place-items-center rounded-full bg-white/85 text-[color:var(--encre)] backdrop-blur"',
    ),
    (
        '{plat.d && <p className="mt-1 text-[0.85rem] text-[#a5947f]">{plat.d}</p>}',
        '{plat.d && <p className="mt-1 text-[0.85rem] text-[color:var(--encre-2)]">{plat.d}</p>}',
    ),
    (
        'className="mb-2 text-[0.75rem] uppercase tracking-widest text-[#e8a86a]"',
        'className="mb-2 text-[0.75rem] uppercase tracking-widest text-[#a8542f]"',
    ),
    (
        """                      grand === g
                        ? { background: "#f0c48a", color: "#241505", borderColor: "#f0c48a" }
                        : { borderColor: "rgba(255,255,255,.16)" }""",
        """                      grand === g
                        ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                        : { borderColor: "rgba(29,26,23,.18)" }""",
    ),
    (
        """                      acc === a
                        ? { background: "#f0c48a", color: "#241505", borderColor: "#f0c48a" }
                        : { borderColor: "rgba(255,255,255,.16)" }""",
        """                      acc === a
                        ? { background: "#1d1a17", color: "#f6efe6", borderColor: "#1d1a17" }
                        : { borderColor: "rgba(29,26,23,.18)" }""",
    ),
    (
        'className="flex items-center gap-3 rounded-full border border-white/16 px-2 py-1.5"',
        'className="flex items-center gap-3 rounded-full border border-black/15 px-2 py-1.5"',
    ),
    (
        """              className="flex-1 rounded-full px-4 py-3 text-[0.9rem] font-bold text-[#241505] transition hover:brightness-105"
              style={{ background: "#f0c48a" }}""",
        """              className="flex-1 rounded-full px-4 py-3 text-[0.9rem] font-bold text-[#f6efe6] transition hover:brightness-125"
              style={{ background: "#1d1a17" }}""",
    ),
]

PIED = [
    (
        'className="relative z-10 border-t border-white/10 bg-[#0b0805] px-6 py-14 text-[#c9b6a2]"',
        'className="relative z-10 border-t border-black/[0.07] bg-[color:var(--mur-2)] px-6 py-16 text-[color:var(--encre-2)]"',
    ),
    (
        'className="police-titre mb-3 text-[1.05rem] font-extrabold text-[#f3e9dd]"',
        'className="police-titre mb-3 text-[1.05rem] font-extrabold text-[color:var(--encre)]"',
    ),
    ('<b className="text-[#e8a86a]">', '<b className="text-[#a8542f]">'),
    (
        'className="mx-auto mt-12 max-w-5xl border-t border-white/10 pt-6 text-[0.76rem] text-[#8a7a68]"',
        'className="mx-auto mt-12 max-w-5xl border-t border-black/[0.08] pt-6 text-[0.76rem] text-[color:var(--encre-2)] opacity-75"',
    ),
]


def passer(fichier, regles):
    p = os.path.join(EXP, fichier)
    s = io.open(p, encoding="utf-8").read()
    n = 0
    for a, b in regles:
        c = s.count(a)
        if c == 0:
            # Un motif absent, c'est une regle ecrite pour un code qui a change :
            # on s'arrete plutot que de repeindre a moitie.
            print("  ARRET : motif ABSENT : %s" % a[:74])
            return None
        if c > 1:
            print("     (motif present %d fois, tous remplaces)" % c)
        s = s.replace(a, b)
        n += c
    io.open(p, "w", encoding="utf-8").write(s)
    print("  %-12s %d remplacements" % (fichier, n))
    return n


if __name__ == "__main__":
    ok = True
    for f, r in (("Carte.tsx", CARTE), ("Pied.tsx", PIED)):
        if passer(f, r) is None:
            ok = False
    sys.exit(0 if ok else 1)
