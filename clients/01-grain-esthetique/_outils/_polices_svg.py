#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LES FONTES, ET LA CONVERSION DU TEXTE EN TRACÉS.

⚠️ POURQUOI ON NE MET PAS DE `<text>` DANS L'AFFICHE SVG.
Un SVG avec du `<text>` dépend d'une fonte. Embarquée en base64 dans une balise
`<style>`, elle marche dans un navigateur, mais Illustrator et une bonne partie
des serveurs d'impression l'ignorent : le texte retombe alors sur une fonte par
défaut, la mise en page se décale, et **ça se découvre une fois les exemplaires
imprimés**. Un imprimeur demande d'ailleurs toujours « les textes vectorisés ».
Donc chaque mot devient un `<path>`. Le fichier ne dépend plus de rien.

⚠️ ET ON NE SE CONTENTE PAS DES LARGEURS D'AVANCE : on passe par **HarfBuzz**,
le moteur qui fait le rendu du texte dans Chrome. Sans lui, pas de crénage : sur
du Cormorant a 30 px, « Va » et « To » s'écartent visiblement.
"""
import io, re, urllib.request
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.varLib import instancer

UA_MODERNE = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CSS = ("https://fonts.googleapis.com/css2"
       "?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,600"
       "&family=Jost:wght@300;400;500;600&display=swap")


class Police:
    """Une face a une graisse précise.

    ⛔ PIÈGE QUI A COÛTÉ UNE PASSE : Google sert Cormorant Garamond et Jost en
       **fontes variables**. Ouvrir le fichier et dessiner les glyphes donne
       l'instance PAR DÉFAUT — pour Cormorant c'est le Light (300), pas le
       Regular que la page affiche. Les lettres sortent plus maigres ET plus
       étroites, donc le décalage **s'accumule le long de la ligne** : au bout
       de « La beauté est un art de vivre » le texte avait glissé de plusieurs
       pixels. Vu sur la carte d'écart : les mots Jost a peine visibles, les
       mots Cormorant complétement dédoublés.
       → on FIGE la fonte a la graisse demandée avant de toucher aux glyphes,
       et HarfBuzz reçoit ce même fichier figé, pas l'original.
    """

    def __init__(self, octets, poids=None):
        tt = TTFont(io.BytesIO(octets))
        if "fvar" in tt and poids is not None:
            axes = {a.axisTag: (a.minValue, a.maxValue) for a in tt["fvar"].axes}
            if "wght" in axes:
                bas, haut = axes["wght"]
                tt = instancer.instantiateVariableFont(
                    tt, {"wght": max(bas, min(haut, poids))}, inplace=False, updateFontNames=False)
        # ⛔ LE DÉFAUT QUI A COÛTÉ LE PLUS CHER : Google sert du **woff2**, et
        #    `save()` le réécrit en woff2 puisque fontTools conserve le format.
        #    **HarfBuzz ne lit pas le woff2** : la face se construit quand même,
        #    et chaque caractére renvoie le glyphe 0. L'affiche se remplissait
        #    de cases « NO GLYPH ».
        #    ⚠️ Et ma vérification de couverture ne le voyait pas : elle lisait
        #    la table cmap avec fontTools, qui répondait « tout est la ». Une
        #    couverture vérifiée sur une bibliothéque ne dit RIEN de ce que
        #    produit l'autre. On vérifie désormais **le résultat de la
        #    composition**, pas la table.
        tt.flavor = None
        tampon = io.BytesIO(); tt.save(tampon); octets = tampon.getvalue()
        self.tt = TTFont(io.BytesIO(octets))
        self.upem = self.tt["head"].unitsPerEm
        self.glyphes = self.tt.getGlyphSet()
        blob = hb.Blob(octets)   # le SFNT figé et déballé, lisible par HarfBuzz
        face = hb.Face(blob)
        self.hb = hb.Font(face)
        self.hb.scale = (self.upem, self.upem)
        self.cmap = self.tt.getBestCmap()
        self._cache = {}

    def couvre(self, texte):
        return [c for c in texte if ord(c) not in self.cmap and c != " "]

    def chemin_glyphe(self, gid):
        if gid not in self._cache:
            nom = self.tt.getGlyphOrder()[gid]
            pen = SVGPathPen(self.glyphes)
            self.glyphes[nom].draw(pen)
            self._cache[gid] = pen.getCommands()
        return self._cache[gid]

    def composer(self, texte, taille, tracking=0.0):
        """Rend (chemins_positionnés, largeur_totale) a la taille demandée.

        `tracking` est en pixels et s'ajoute APRÈS chaque glyphe.
        ⚠️ On ne compte pas le tracking du DERNIER glyphe dans la largeur : CSS
        le compte, ce qui décale d'un demi-espacement tout texte centré. Sur
        « COTONOU · HAIE-VIVE » a .36em, ça fait 2,8 px de travers.
        """
        buf = hb.Buffer()
        buf.add_str(texte)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        k = taille / self.upem
        x, morceaux, notdef = 0.0, [], 0
        infos, poss = buf.glyph_infos, buf.glyph_positions
        for i, (gi, gp) in enumerate(zip(infos, poss)):
            if gi.codepoint == 0:
                notdef += 1
            d = self.chemin_glyphe(gi.codepoint)
            if d:
                dx = x + gp.x_offset * k
                dy = -gp.y_offset * k
                morceaux.append((d, dx, dy, k))
            x += gp.x_advance * k
            if i < len(infos) - 1:
                x += tracking
        # `x` est la largeur DESSINÉE (sans l'espacement du dernier glyphe).
        # `x_css` est celle que CSS annonce, qui le compte : c'est elle qu'il
        # faut comparer a la mesure du navigateur, sinon on s'accuse a tort.
        x_css = x + (tracking if len(infos) > 1 else 0)
        return morceaux, x, notdef, x_css


def charger():
    """Télécharge les woff2 de Google et les ouvre. fontTools les lit
    directement quand `brotli` est installé : pas de conversion intermédiaire."""
    req = urllib.request.Request(CSS, headers={"User-Agent": UA_MODERNE})
    css = urllib.request.urlopen(req, timeout=40).read().decode()
    # ⚠️ Google découpe chaque fonte par jeu de caractéres. On prend le bloc
    #    « latin » : c'est lui qui porte les accents, les guillemets français,
    #    le point médian et le tiret demi-cadratin. La couverture est vérifiée
    #    caractére par caractére plus bas, donc une erreur ici ne passe pas.
    blocs = re.split(r"/\*\s*([\w-]+)\s*\*/", css)
    brut = {}
    for i in range(1, len(blocs), 2):
        sous_ensemble, corps = blocs[i], blocs[i + 1]
        if sous_ensemble != "latin":
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", corps)
        sty = re.search(r"font-style:\s*(\w+)", corps)
        wgt = re.search(r"font-weight:\s*(\d+)", corps)
        u = re.search(r"url\((https://[^)]+)\)", corps)
        if not (fam and sty and wgt and u):
            continue
        cle = (fam.group(1), sty.group(1), int(wgt.group(1)))
        brut[cle] = u.group(1)
    # ⚠️ Google renvoie LE MÊME fichier variable pour toutes les graisses d'une
    #    famille : on ne télécharge qu'une fois, et on fige ensuite.
    cache = {}
    polices = {}
    for cle, url in brut.items():
        if url not in cache:
            cache[url] = urllib.request.urlopen(url, timeout=40).read()
        polices[cle] = Police(cache[url], poids=cle[2])
    return polices


def choisir(polices, famille, style, poids):
    """La face exacte, sinon la plus proche en graisse. ⚠️ Jamais de fausse
    italique ni de faux gras : on prend le vrai fichier ou on échoue."""
    if (famille, style, poids) in polices:
        return polices[(famille, style, poids)]
    memes = [k for k in polices if k[0] == famille and k[1] == style]
    if not memes:
        raise KeyError(f"aucune face {famille} {style} (demandé {poids})")
    return polices[min(memes, key=lambda k: abs(k[2] - poids))]
