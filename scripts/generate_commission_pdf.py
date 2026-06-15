#!/usr/bin/env python3
"""
NEBULA Agency — Générateur PDF Structure de Commissions
PDF ultra stylé pour présentation aux partenaires
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Flowable
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.colors import HexColor, white, black
import math

# ─── Palette NEBULA ───────────────────────────────────────────────
NEBULA_DARK    = HexColor('#0A0A1A')
NEBULA_PURPLE  = HexColor('#6C3CE1')
NEBULA_VIOLET  = HexColor('#8B5CF6')
NEBULA_PINK    = HexColor('#EC4899')
NEBULA_CYAN    = HexColor('#06B6D4')
NEBULA_GOLD    = HexColor('#F59E0B')
NEBULA_SILVER  = HexColor('#94A3B8')
NEBULA_GREEN   = HexColor('#10B981')
NEBULA_LIGHT   = HexColor('#F8FAFC')
NEBULA_CARD    = HexColor('#1E1B4B')
NEBULA_CARD2   = HexColor('#13111F')
NEBULA_BORDER  = HexColor('#3730A3')
NEBULA_MUTED   = HexColor('#64748B')
STARTER_COLOR  = HexColor('#3B82F6')
SILVER_COLOR   = HexColor('#94A3B8')
GOLD_COLOR     = HexColor('#F59E0B')


# ─── Flowables personnalisés ───────────────────────────────────────

class GradientRect(Flowable):
    """Rectangle avec dégradé simulé"""
    def __init__(self, w, h, color1, color2, radius=8):
        Flowable.__init__(self)
        self.w, self.h = w, h
        self.color1, self.color2 = color1, color2
        self.radius = radius

    def draw(self):
        steps = 40
        for i in range(steps):
            t = i / steps
            r = self.color1.red + t * (self.color2.red - self.color1.red)
            g = self.color1.green + t * (self.color2.green - self.color1.green)
            b = self.color1.blue + t * (self.color2.blue - self.color1.blue)
            self.canv.setFillColor(colors.Color(r, g, b))
            strip_h = self.h / steps
            y = self.h - (i + 1) * strip_h
            if i == 0:
                self.canv.roundRect(0, y, self.w, strip_h + self.radius, self.radius, fill=1, stroke=0)
            elif i == steps - 1:
                self.canv.roundRect(0, 0, self.w, strip_h + self.radius, self.radius, fill=1, stroke=0)
            else:
                self.canv.rect(0, y, self.w, strip_h + 1, fill=1, stroke=0)


class HeroHeader(Flowable):
    """En-tête hero avec fond dégradé et titre"""
    def __init__(self, w, h=110):
        Flowable.__init__(self)
        self.w, self.h = w, h

    def draw(self):
        c = self.canv
        # Fond dégradé violet → bleu foncé
        steps = 60
        for i in range(steps):
            t = i / steps
            r = NEBULA_DARK.red + t * (NEBULA_CARD.red - NEBULA_DARK.red)
            g = NEBULA_DARK.green + t * (NEBULA_CARD.green - NEBULA_DARK.green)
            b = NEBULA_DARK.blue + t * (NEBULA_CARD.blue - NEBULA_DARK.blue)
            strip_h = self.h / steps
            y = i * strip_h
            c.setFillColor(colors.Color(r, g, b))
            c.rect(0, y, self.w, strip_h + 1, fill=1, stroke=0)

        # Cercles décoratifs
        c.setFillColor(HexColor('#6C3CE130'))
        c.setStrokeColor(HexColor('#00000000'))
        c.circle(self.w * 0.85, self.h * 0.7, 55, fill=1, stroke=0)
        c.circle(self.w * 0.1, self.h * 0.2, 30, fill=1, stroke=0)

        c.setFillColor(HexColor('#EC489920'))
        c.circle(self.w * 0.75, self.h * 0.15, 25, fill=1, stroke=0)

        # Badge NEBULA
        badge_x, badge_y = 20, self.h - 32
        c.setFillColor(NEBULA_PURPLE)
        c.roundRect(badge_x, badge_y, 120, 20, 10, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(badge_x + 14, badge_y + 6, 'NEBULA AGENCY')

        # Titre principal
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 22)
        c.drawString(20, self.h - 58, 'PROGRAMME DE PARTENARIAT')

        c.setFillColor(NEBULA_VIOLET)
        c.setFont('Helvetica-Bold', 20)
        c.drawString(20, self.h - 82, 'STRUCTURE DES COMMISSIONS 2025')

        # Sous-titre
        c.setFillColor(NEBULA_SILVER)
        c.setFont('Helvetica', 10)
        c.drawString(20, self.h - 100, 'Guide complet pour nos partenaires vendeurs  •  Afrique de l\'Ouest')

        # Ligne décorative
        c.setStrokeColor(NEBULA_PURPLE)
        c.setLineWidth(2)
        c.line(20, self.h - 108, self.w - 20, self.h - 108)


class TierCard(Flowable):
    """Carte de niveau (STARTER / SILVER / GOLD)"""
    def __init__(self, w, h, title, rate, color, icon_char, subtitle, features):
        Flowable.__init__(self)
        self.w, self.h = w, h
        self.title = title
        self.rate = rate
        self.color = color
        self.icon_char = icon_char
        self.subtitle = subtitle
        self.features = features

    def draw(self):
        c = self.canv
        # Fond carte sombre
        c.setFillColor(NEBULA_CARD2)
        c.roundRect(0, 0, self.w, self.h, 10, fill=1, stroke=0)

        # Bordure colorée en haut
        c.setFillColor(self.color)
        c.roundRect(0, self.h - 5, self.w, 5, 3, fill=1, stroke=0)
        c.rect(0, self.h - 8, self.w, 5, fill=1, stroke=0)

        # Icône cercle
        cx = self.w / 2
        c.setFillColor(self.color)
        c.setFillAlpha(0.15)
        c.circle(cx, self.h - 32, 22, fill=1, stroke=0)
        c.setFillAlpha(1)
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(cx, self.h - 37, self.icon_char)

        # Titre niveau
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 13)
        c.drawCentredString(cx, self.h - 62, self.title)

        # Taux en grand
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 30)
        c.drawCentredString(cx, self.h - 95, self.rate)

        c.setFillColor(NEBULA_SILVER)
        c.setFont('Helvetica', 8)
        c.drawCentredString(cx, self.h - 107, 'sur vos ventes directes')

        # Ligne séparatrice
        c.setStrokeColor(self.color)
        c.setStrokeAlpha(0.3)
        c.setLineWidth(0.5)
        c.line(10, self.h - 115, self.w - 10, self.h - 115)
        c.setStrokeAlpha(1)

        # Condition
        c.setFillColor(NEBULA_LIGHT)
        c.setFont('Helvetica', 8)
        c.drawCentredString(cx, self.h - 128, self.subtitle)

        # Features
        y = self.h - 148
        for feat in self.features:
            c.setFillColor(self.color)
            c.setFont('Helvetica-Bold', 9)
            c.drawString(12, y, '✓')
            c.setFillColor(NEBULA_LIGHT)
            c.setFont('Helvetica', 8)
            c.drawString(24, y, feat)
            y -= 16


class NetworkTree(Flowable):
    """Arbre de réseau dessiné"""
    def __init__(self, w, h=260):
        Flowable.__init__(self)
        self.w = w
        self.h = h

    def draw_node(self, c, x, y, name, role, color, size=36, is_highlight=False):
        """Dessine un nœud avec nom et rôle"""
        # Halo si highlight
        if is_highlight:
            c.setFillColor(color)
            c.setFillAlpha(0.2)
            c.circle(x, y, size + 6, fill=1, stroke=0)
            c.setFillAlpha(1)

        # Cercle principal
        c.setFillColor(color)
        c.circle(x, y, size, fill=1, stroke=0)

        # Bordure blanche
        c.setStrokeColor(white)
        c.setStrokeAlpha(0.6)
        c.setLineWidth(1.5)
        c.circle(x, y, size, fill=0, stroke=1)
        c.setStrokeAlpha(1)

        # Initiales
        initials = ''.join([w[0] for w in name.split()[:2]]).upper()
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', size // 2 + 2)
        c.drawCentredString(x, y - (size // 4), initials)

        # Nom sous le nœud
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(x, y - size - 12, name)

        # Rôle
        c.setFillColor(color)
        c.setFont('Helvetica', 7.5)
        c.drawCentredString(x, y - size - 24, role)

    def draw_arrow(self, c, x1, y1, x2, y2, color, label='', pct=''):
        """Dessine une flèche entre deux nœuds avec étiquette"""
        c.setStrokeColor(color)
        c.setStrokeAlpha(0.7)
        c.setLineWidth(1.8)
        c.line(x1, y1, x2, y2)
        c.setStrokeAlpha(1)

        # Étiquette avec fond
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            tw = 52
            th = 14
            c.setFillColor(NEBULA_DARK)
            c.roundRect(mx - tw/2, my - th/2, tw, th, 5, fill=1, stroke=0)
            c.setStrokeColor(color)
            c.setStrokeAlpha(0.5)
            c.setLineWidth(0.5)
            c.roundRect(mx - tw/2, my - th/2, tw, th, 5, fill=0, stroke=1)
            c.setStrokeAlpha(1)
            c.setFillColor(color)
            c.setFont('Helvetica-Bold', 7)
            c.drawCentredString(mx, my - 3, label)

    def draw(self):
        c = self.canv

        # Fond carte
        c.setFillColor(NEBULA_CARD2)
        c.roundRect(0, 0, self.w, self.h, 10, fill=1, stroke=0)

        # Titre
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 13)
        c.drawCentredString(self.w / 2, self.h - 22, "L'ARBRE DE RÉSEAU — EXEMPLE SHAD")
        c.setFillColor(NEBULA_SILVER)
        c.setFont('Helvetica', 8)
        c.drawCentredString(self.w / 2, self.h - 36, 'Chaque recrutement étend votre réseau et vos revenus passifs')

        # Positions des nœuds
        # Niveau 0 — Marc (le recruteur de Shad)
        marc_x, marc_y = self.w / 2, self.h - 80
        # Niveau 1 — Shad
        shad_x, shad_y = self.w / 2, self.h - 148
        # Niveau 2 — Paul et Mia
        paul_x, paul_y = self.w * 0.3, self.h - 210
        mia_x, mia_y = self.w * 0.7, self.h - 210
        # Niveau 3 — Kofi (recruté par Paul)
        kofi_x, kofi_y = self.w * 0.2, self.h - 250
        # (on ne dessine pas de niveau 3 pour Mia ici pour simplifier)

        # Connexions
        self.draw_arrow(c, marc_x, marc_y - 28, shad_x, shad_y + 28,
                        NEBULA_VIOLET, 'N1 → 5%')
        self.draw_arrow(c, shad_x - 10, shad_y - 28, paul_x + 18, paul_y + 24,
                        STARTER_COLOR, 'N1 → 5%')
        self.draw_arrow(c, shad_x + 10, shad_y - 28, mia_x - 18, mia_y + 24,
                        NEBULA_PINK, 'N1 → 5%')
        self.draw_arrow(c, paul_x - 8, paul_y - 22, kofi_x + 10, kofi_y + 22,
                        NEBULA_GREEN, 'N2 → 3%')

        # Légende niveaux à droite
        lx = self.w * 0.88
        levels = [
            ('N0', 'Vos ventes', GOLD_COLOR, marc_y + 5),
            ('N1', '+5% / vente', NEBULA_VIOLET, shad_y + 5),
            ('N2', '+3% / vente', STARTER_COLOR, paul_y + 5),
            ('N3', '+2% / vente', NEBULA_GREEN, kofi_y + 5),
        ]

        # Nœuds
        self.draw_node(c, marc_x, marc_y, 'Marc', 'Votre recruteur', NEBULA_VIOLET, 24)
        self.draw_node(c, shad_x, shad_y, 'SHAD', 'SILVER — 30%', GOLD_COLOR, 30, is_highlight=True)
        self.draw_node(c, paul_x, paul_y, 'Paul', 'STARTER — 25%', STARTER_COLOR, 22)
        self.draw_node(c, mia_x, mia_y, 'Mia', 'STARTER — 25%', NEBULA_PINK, 22)
        self.draw_node(c, kofi_x, kofi_y, 'Kofi', 'STARTER — 25%', NEBULA_GREEN, 18)

        # Badge "VOUS" sur Shad
        c.setFillColor(GOLD_COLOR)
        c.roundRect(shad_x + 25, shad_y + 18, 32, 14, 5, fill=1, stroke=0)
        c.setFillColor(NEBULA_DARK)
        c.setFont('Helvetica-Bold', 7)
        c.drawCentredString(shad_x + 41, shad_y + 23, 'VOUS')


class EarningsBar(Flowable):
    """Barre de gains illustrée"""
    def __init__(self, w, h, name, color, amount, pct, sources):
        Flowable.__init__(self)
        self.w, self.h = w, h
        self.name = name
        self.color = color
        self.amount = amount
        self.pct = pct  # pourcentage de la barre max
        self.sources = sources  # liste de (label, montant, couleur)

    def draw(self):
        c = self.canv
        # Fond
        c.setFillColor(NEBULA_CARD2)
        c.roundRect(0, 0, self.w, self.h, 8, fill=1, stroke=0)

        # Nom
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(14, self.h - 22, self.name)

        # Montant total
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 14)
        c.drawRightString(self.w - 14, self.h - 22, self.amount)

        # Barre de progression
        bar_x, bar_y = 14, self.h - 38
        bar_w = self.w - 28
        bar_h = 10

        c.setFillColor(NEBULA_CARD)
        c.roundRect(bar_x, bar_y, bar_w, bar_h, 5, fill=1, stroke=0)

        fill_w = bar_w * self.pct
        c.setFillColor(self.color)
        c.roundRect(bar_x, bar_y, fill_w, bar_h, 5, fill=1, stroke=0)

        # Détail sources
        y = self.h - 58
        for label, montant, col in self.sources:
            # Puce colorée
            c.setFillColor(col)
            c.circle(22, y + 4, 4, fill=1, stroke=0)
            c.setFillColor(NEBULA_SILVER)
            c.setFont('Helvetica', 8)
            c.drawString(30, y, label)
            c.setFillColor(white)
            c.setFont('Helvetica-Bold', 8)
            c.drawRightString(self.w - 14, y, montant)
            y -= 16


class CommissionFlowDiagram(Flowable):
    """Diagramme montrant comment l'argent circule sur une vente"""
    def __init__(self, w, h=180):
        Flowable.__init__(self)
        self.w = w
        self.h = h

    def draw(self):
        c = self.canv
        c.setFillColor(NEBULA_CARD2)
        c.roundRect(0, 0, self.w, self.h, 10, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(self.w / 2, self.h - 22, 'RÉPARTITION SUR UNE VENTE DE 150 000 FCFA')

        # Vente totale
        box_w = 120
        cy = self.h - 60

        def draw_box(x, y, w, h, label, amount, color):
            c.setFillColor(color)
            c.roundRect(x, y - h/2, w, h, 6, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont('Helvetica-Bold', 7)
            c.drawCentredString(x + w/2, y + h/2 - 12, label)
            c.setFont('Helvetica-Bold', 9)
            c.drawCentredString(x + w/2, y - h/2 + 6, amount)

        def draw_h_arrow(x1, y, x2, color):
            c.setStrokeColor(color)
            c.setLineWidth(1.5)
            c.line(x1, y, x2, y)
            # Pointe flèche
            c.setFillColor(color)
            c.setStrokeColor(color)
            pts = [x2, y, x2 - 6, y + 4, x2 - 6, y - 4]
            p = c.beginPath()
            p.moveTo(x2, y)
            p.lineTo(x2 - 6, y + 4)
            p.lineTo(x2 - 6, y - 4)
            p.close()
            c.drawPath(p, fill=1, stroke=0)

        # Boîte client
        draw_box(10, cy, 85, 44, 'CLIENT PAIE', '150 000 F', NEBULA_MUTED)
        draw_h_arrow(95, cy, 115, NEBULA_SILVER)

        # Boîte vendeur (SILVER)
        draw_box(115, cy + 25, 90, 36, 'VENDEUR SILVER', '45 000 F (30%)', GOLD_COLOR)
        draw_h_arrow(95, cy + 25, 115, GOLD_COLOR)

        # Boîte N1
        draw_box(115, cy - 5, 90, 36, 'RECRUTEUR N1', '7 500 F (5%)', NEBULA_VIOLET)

        # Boîte N2
        draw_box(115, cy - 35, 90, 36, 'RECRUTEUR N2', '4 500 F (3%)', STARTER_COLOR)

        # Boîte Mongazi/NEBULA
        draw_box(115, cy - 65, 90, 36, 'NEBULA AGENCY', '93 000 F (62%)', NEBULA_PINK)

        # Flèches
        draw_h_arrow(95, cy - 5, 115, NEBULA_VIOLET)
        draw_h_arrow(95, cy - 35, 115, STARTER_COLOR)
        draw_h_arrow(95, cy - 65, 115, NEBULA_PINK)

        # Légende bas
        c.setFillColor(NEBULA_SILVER)
        c.setFont('Helvetica', 7)
        c.drawCentredString(self.w / 2, 10,
            'N3 : 3 000 F (2%) — non représenté ici pour simplifier')


# ─── Construction du document ─────────────────────────────────────

def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=12*mm, bottomMargin=18*mm,
        title='NEBULA Agency — Structure des Commissions 2025',
        author='NEBULA Agency',
    )

    W = A4[0] - 36*mm  # largeur utile
    styles = getSampleStyleSheet()

    # Styles personnalisés
    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    ST = {
        'title': s('t', fontName='Helvetica-Bold', fontSize=18, textColor=white,
                   alignment=TA_CENTER, spaceAfter=4),
        'h2': s('h2', fontName='Helvetica-Bold', fontSize=13, textColor=white,
                spaceAfter=6, spaceBefore=12),
        'h3': s('h3', fontName='Helvetica-Bold', fontSize=10, textColor=NEBULA_VIOLET,
                spaceAfter=4, spaceBefore=8),
        'body': s('b', fontName='Helvetica', fontSize=9, textColor=NEBULA_LIGHT,
                  spaceAfter=4, leading=14),
        'small': s('sm', fontName='Helvetica', fontSize=8, textColor=NEBULA_SILVER,
                   spaceAfter=2, leading=12),
        'highlight': s('hl', fontName='Helvetica-Bold', fontSize=10,
                       textColor=GOLD_COLOR, spaceAfter=4),
        'center': s('c', fontName='Helvetica', fontSize=9, textColor=NEBULA_LIGHT,
                    alignment=TA_CENTER, spaceAfter=4),
        'badge': s('ba', fontName='Helvetica-Bold', fontSize=8,
                   textColor=NEBULA_DARK, backColor=GOLD_COLOR,
                   alignment=TA_CENTER, spaceAfter=4),
    }

    story = []

    # ─────────────────────────────────────────────────────────────────
    # PAGE 1 — HERO + TIERS
    # ─────────────────────────────────────────────────────────────────

    story.append(HeroHeader(W, 112))
    story.append(Spacer(1, 14))

    # Intro
    intro_data = [[
        Paragraph(
            '<b>Bienvenue dans le programme de partenariat NEBULA Agency.</b><br/>'
            'En rejoignant notre réseau, vous vendez des vitrines digitales à des PME africaines '
            'et touchez des commissions immédiates sur chaque vente — plus des revenus passifs '
            'sur les ventes de votre réseau. Plus vous vendez, plus votre taux monte.',
            ParagraphStyle('intro', fontName='Helvetica', fontSize=9,
                           textColor=NEBULA_LIGHT, leading=14)
        )
    ]]
    intro_tbl = Table(intro_data, colWidths=[W])
    intro_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_CARD),
        ('ROUNDEDCORNERS', [8]),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(intro_tbl)
    story.append(Spacer(1, 16))

    # ─── Section 1 — Les 3 paliers ───
    # Titre section
    sec1_title = [[Paragraph('01 — VOS PALIERS DE COMMISSION',
                             ParagraphStyle('st', fontName='Helvetica-Bold', fontSize=11,
                                            textColor=white))]]
    sec1_t = Table(sec1_title, colWidths=[W])
    sec1_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_PURPLE),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(sec1_t)
    story.append(Spacer(1, 10))

    # Cards des paliers
    card_h = 195
    gap = 8
    cw = (W - 2 * gap) / 3

    tiers_data = [[
        TierCard(cw, card_h, 'STARTER', '25%', STARTER_COLOR, '★',
                 '0 → 2 ventes / mois',
                 ['Commission immédiate', 'Paiement en 48h', 'Formation offerte']),
        TierCard(cw, card_h, 'SILVER', '30%', SILVER_COLOR, '◆',
                 '3 → 6 ventes / mois',
                 ['Commission +5 pts', 'Badge partenaire', 'Support prioritaire']),
        TierCard(cw, card_h, 'GOLD', '35%', GOLD_COLOR, '♛',
                 '7+ ventes / mois',
                 ['Commission max', 'Bonus trimestriel', 'Accès VIP NEBULA']),
    ]]
    tiers_tbl = Table(tiers_data, colWidths=[cw, cw, cw],
                      rowHeights=[card_h])
    tiers_tbl.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('COLPADDING', (0, 0), (-1, -1), gap // 2),
    ]))
    story.append(tiers_tbl)
    story.append(Spacer(1, 16))

    # ─── Section 2 — Réseau 3 niveaux ───
    sec2_title = [[Paragraph('02 — REVENUS DE RÉSEAU (NIVEAUX N1 → N3)',
                             ParagraphStyle('st', fontName='Helvetica-Bold', fontSize=11,
                                            textColor=white))]]
    sec2_t = Table(sec2_title, colWidths=[W])
    sec2_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_PURPLE),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(sec2_t)
    story.append(Spacer(1, 10))

    # Tableau des niveaux réseau
    net_headers = ['Niveau', 'Relation', 'Commission', 'Sur une vente de 150 000 F']
    net_rows = [
        ['N1', 'Personne que vous avez recrutée', '5 %', '7 500 FCFA'],
        ['N2', 'Personne recrutée par votre N1', '3 %', '4 500 FCFA'],
        ['N3', 'Personne recrutée par votre N2', '2 %', '3 000 FCFA'],
    ]
    net_colors = [NEBULA_VIOLET, STARTER_COLOR, NEBULA_GREEN]
    net_data = [net_headers] + net_rows
    net_tbl = Table(net_data, colWidths=[30*mm, 65*mm, 30*mm, W - 125*mm])
    net_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NEBULA_CARD),
        ('TEXTCOLOR', (0, 0), (-1, 0), NEBULA_VIOLET),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 1), (0, 1), NEBULA_VIOLET),
        ('TEXTCOLOR', (0, 2), (0, 2), STARTER_COLOR),
        ('TEXTCOLOR', (0, 3), (0, 3), NEBULA_GREEN),
        ('BACKGROUND', (0, 1), (-1, 1), NEBULA_CARD2),
        ('BACKGROUND', (0, 2), (-1, 2), HexColor('#111125')),
        ('BACKGROUND', (0, 3), (-1, 3), NEBULA_CARD2),
        ('TEXTCOLOR', (0, 1), (-1, -1), NEBULA_LIGHT),
        ('TEXTCOLOR', (2, 1), (2, 1), NEBULA_VIOLET),
        ('TEXTCOLOR', (2, 2), (2, 2), STARTER_COLOR),
        ('TEXTCOLOR', (2, 3), (2, 3), NEBULA_GREEN),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.3, NEBULA_BORDER),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(net_tbl)
    story.append(Spacer(1, 10))

    # Note
    note_data = [[Paragraph(
        '💡 <b>Ces commissions de réseau s\'accumulent automatiquement</b> — '
        'chaque fois qu\'un membre de votre réseau fait une vente, vous êtes crédité '
        'sans rien faire de plus. C\'est votre revenu passif.',
        ParagraphStyle('note', fontName='Helvetica', fontSize=8.5,
                       textColor=NEBULA_LIGHT, leading=13)
    )]]
    note_t = Table(note_data, colWidths=[W])
    note_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#1a1040')),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEAFTER', (0, 0), (0, -1), 3, NEBULA_VIOLET),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(note_t)

    # ─────────────────────────────────────────────────────────────────
    # PAGE 2 — EXEMPLE SHAD
    # ─────────────────────────────────────────────────────────────────
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # Header page 2
    pg2_head = [[Paragraph(
        'EXEMPLE CONCRET — LE RÉSEAU DE SHAD',
        ParagraphStyle('ph', fontName='Helvetica-Bold', fontSize=14,
                       textColor=white, alignment=TA_CENTER)
    )]]
    pg2_t = Table(pg2_head, colWidths=[W])
    pg2_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_CARD),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LINEABOVE', (0, 0), (-1, 0), 3, NEBULA_PURPLE),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(pg2_t)
    story.append(Spacer(1, 14))

    # Contexte
    ctx_data = [[Paragraph(
        '<b>Ce mois-ci :</b> Shad fait <b>5 ventes</b> (palier SILVER → 30%) • '
        'Paul fait <b>3 ventes</b> (STARTER → 25%) • '
        'Mia fait <b>2 ventes</b> (STARTER → 25%) • '
        'Kofi fait <b>2 ventes</b> (STARTER → 25%)',
        ParagraphStyle('ctx', fontName='Helvetica', fontSize=9,
                       textColor=NEBULA_LIGHT, leading=14)
    )]]
    ctx_t = Table(ctx_data, colWidths=[W])
    ctx_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0f0b24')),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('ROUNDEDCORNERS', [6]),
        ('LINEABOVE', (0, 0), (-1, 0), 2, GOLD_COLOR),
    ]))
    story.append(ctx_t)
    story.append(Spacer(1, 14))

    # ─── Arbre réseau ───
    story.append(NetworkTree(W, 270))
    story.append(Spacer(1, 16))

    # ─── Ce que Shad gagne ───
    sec3_title = [[Paragraph('03 — CE QUE SHAD GAGNE CE MOIS',
                             ParagraphStyle('st', fontName='Helvetica-Bold', fontSize=11,
                                            textColor=white))]]
    sec3_t = Table(sec3_title, colWidths=[W])
    sec3_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#854d0e')),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(sec3_t)
    story.append(Spacer(1, 10))

    shad_rows = [
        ['Source', 'Calcul', 'Montant'],
        ['Ses 5 ventes directes (SILVER 30%)', '5 × 45 000 FCFA', '225 000 FCFA'],
        ['Ventes de Paul — N1 (5%)', '3 × 7 500 FCFA', '22 500 FCFA'],
        ['Ventes de Mia — N1 (5%)', '2 × 7 500 FCFA', '15 000 FCFA'],
        ['Ventes de Kofi — N2 (3%)', '2 × 4 500 FCFA', '9 000 FCFA'],
        ['TOTAL SHAD', '', '271 500 FCFA'],
    ]
    shad_tbl = Table(shad_rows, colWidths=[W * 0.5, W * 0.27, W * 0.23])
    shad_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NEBULA_CARD),
        ('TEXTCOLOR', (0, 0), (-1, 0), NEBULA_VIOLET),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, 1), NEBULA_CARD2),
        ('BACKGROUND', (0, 2), (-1, 2), HexColor('#111125')),
        ('BACKGROUND', (0, 3), (-1, 3), NEBULA_CARD2),
        ('BACKGROUND', (0, 4), (-1, 4), HexColor('#111125')),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#3d2c00')),
        ('TEXTCOLOR', (0, 1), (-1, -2), NEBULA_LIGHT),
        ('TEXTCOLOR', (0, -1), (-1, -1), GOLD_COLOR),
        ('TEXTCOLOR', (2, 1), (2, -2), NEBULA_GREEN),
        ('TEXTCOLOR', (2, -1), (2, -1), GOLD_COLOR),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.3, NEBULA_BORDER),
        ('LINEBELOW', (0, -2), (-1, -2), 1, GOLD_COLOR),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(shad_tbl)
    story.append(Spacer(1, 14))

    # ─── Ce que Marc gagne ───
    sec4_title = [[Paragraph('04 — CE QUE MARC GAGNE GRÂCE À SHAD',
                             ParagraphStyle('st', fontName='Helvetica-Bold', fontSize=11,
                                            textColor=white))]]
    sec4_t = Table(sec4_title, colWidths=[W])
    sec4_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#3730A3')),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(sec4_t)
    story.append(Spacer(1, 10))

    marc_rows = [
        ['Source', 'Calcul', 'Montant'],
        ['Ventes de Shad — N1 (5%)', '5 × 7 500 FCFA', '37 500 FCFA'],
        ['Ventes de Paul — N2 (3%)', '3 × 4 500 FCFA', '13 500 FCFA'],
        ['Ventes de Mia — N2 (3%)', '2 × 4 500 FCFA', '9 000 FCFA'],
        ['Ventes de Kofi — N3 (2%)', '2 × 3 000 FCFA', '6 000 FCFA'],
        ['TOTAL MARC', '', '66 000 FCFA'],
    ]
    marc_tbl = Table(marc_rows, colWidths=[W * 0.5, W * 0.27, W * 0.23])
    marc_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NEBULA_CARD),
        ('TEXTCOLOR', (0, 0), (-1, 0), NEBULA_VIOLET),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, 1), NEBULA_CARD2),
        ('BACKGROUND', (0, 2), (-1, 2), HexColor('#111125')),
        ('BACKGROUND', (0, 3), (-1, 3), NEBULA_CARD2),
        ('BACKGROUND', (0, 4), (-1, 4), HexColor('#111125')),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#1e1b4b')),
        ('TEXTCOLOR', (0, 1), (-1, -2), NEBULA_LIGHT),
        ('TEXTCOLOR', (0, -1), (-1, -1), NEBULA_VIOLET),
        ('TEXTCOLOR', (2, 1), (2, -2), NEBULA_GREEN),
        ('TEXTCOLOR', (2, -1), (2, -1), NEBULA_VIOLET),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.3, NEBULA_BORDER),
        ('LINEBELOW', (0, -2), (-1, -2), 1, NEBULA_VIOLET),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(marc_tbl)

    # ─────────────────────────────────────────────────────────────────
    # PAGE 3 — FLUX + RÉCAP MONGAZI + CTA
    # ─────────────────────────────────────────────────────────────────
    story.append(PageBreak())

    pg3_head = [[Paragraph(
        'FLUX D\'UNE VENTE & PART NEBULA',
        ParagraphStyle('ph', fontName='Helvetica-Bold', fontSize=14,
                       textColor=white, alignment=TA_CENTER)
    )]]
    pg3_t = Table(pg3_head, colWidths=[W])
    pg3_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_CARD),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LINEABOVE', (0, 0), (-1, 0), 3, NEBULA_PINK),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(pg3_t)
    story.append(Spacer(1, 14))

    # ─── Tableau Mongazi garde ───
    sec5_title = [[Paragraph('05 — CE QUE NEBULA GARDE SUR CHAQUE VENTE',
                             ParagraphStyle('st', fontName='Helvetica-Bold', fontSize=11,
                                            textColor=white))]]
    sec5_t = Table(sec5_title, colWidths=[W])
    sec5_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#831843')),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(sec5_t)
    story.append(Spacer(1, 10))

    mong_rows = [
        ['Configuration', 'Taux sortis (vendeur + réseau)', 'NEBULA garde'],
        ['Vendeur GOLD seul (aucun recruteur)', '35% (GOLD uniquement)', '97 500 FCFA (65%)'],
        ['Vendeur SILVER + 2 niveaux réseau', '38% (30+5+3)', '93 000 FCFA (62%)'],
        ['Vendeur STARTER + 3 niveaux réseau', '35% (25+5+3+2)', '97 500 FCFA (65%)'],
    ]
    mong_tbl = Table(mong_rows, colWidths=[W * 0.38, W * 0.35, W * 0.27])
    mong_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NEBULA_CARD),
        ('TEXTCOLOR', (0, 0), (-1, 0), NEBULA_PINK),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BACKGROUND', (0, 1), (-1, 1), NEBULA_CARD2),
        ('BACKGROUND', (0, 2), (-1, 2), HexColor('#111125')),
        ('BACKGROUND', (0, 3), (-1, 3), NEBULA_CARD2),
        ('TEXTCOLOR', (0, 1), (-1, -1), NEBULA_LIGHT),
        ('TEXTCOLOR', (2, 1), (2, -1), NEBULA_PINK),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.3, NEBULA_BORDER),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(mong_tbl)
    story.append(Spacer(1, 14))

    # ─── Récap visuel gains barres ───
    sec6_title = [[Paragraph('06 — RÉCAP VISUEL DES GAINS DU MOIS',
                             ParagraphStyle('st', fontName='Helvetica-Bold', fontSize=11,
                                            textColor=white))]]
    sec6_t = Table(sec6_title, colWidths=[W])
    sec6_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_PURPLE),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(sec6_t)
    story.append(Spacer(1, 10))

    bar_h = 105
    bw = (W - 8) / 2

    bars_data = [[
        EarningsBar(bw, bar_h, 'SHAD gagne', GOLD_COLOR, '271 500 FCFA', 1.0, [
            ('5 ventes directes (30%)', '225 000 FCFA', GOLD_COLOR),
            ('Réseau Paul N1 (5%)', '22 500 FCFA', NEBULA_VIOLET),
            ('Réseau Mia N1 (5%)', '15 000 FCFA', NEBULA_PINK),
            ('Réseau Kofi N2 (3%)', '9 000 FCFA', NEBULA_GREEN),
        ]),
        EarningsBar(bw, bar_h, 'MARC gagne (passif)', NEBULA_VIOLET, '66 000 FCFA', 0.24, [
            ('Shad N1 (5%)', '37 500 FCFA', GOLD_COLOR),
            ('Paul N2 (3%)', '13 500 FCFA', STARTER_COLOR),
            ('Mia N2 (3%)', '9 000 FCFA', NEBULA_PINK),
            ('Kofi N3 (2%)', '6 000 FCFA', NEBULA_GREEN),
        ]),
    ]]
    bars_tbl = Table(bars_data, colWidths=[bw, bw])
    bars_tbl.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('COLPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(bars_tbl)
    story.append(Spacer(1, 16))

    # ─── Simulation projection ───
    sec7_title = [[Paragraph('07 — SIMULATION : CONSTRUISEZ VOS REVENUS',
                             ParagraphStyle('st', fontName='Helvetica-Bold', fontSize=11,
                                            textColor=white))]]
    sec7_t = Table(sec7_title, colWidths=[W])
    sec7_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_PURPLE),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(sec7_t)
    story.append(Spacer(1, 10))

    proj_rows = [
        ['Scénario', 'Vos ventes', 'Revenu direct', 'Revenu réseau*', 'TOTAL MOIS'],
        ['Débutant', '2 ventes', '60 000 F', '+ 15 000 F', '75 000 FCFA'],
        ['Actif', '5 ventes', '150 000 F', '+ 45 000 F', '195 000 FCFA'],
        ['Champion', '10 ventes', '350 000 F', '+ 120 000 F', '470 000 FCFA'],
        ['GOLD Élite', '15 ventes', '787 500 F', '+ 200 000 F', '987 500 FCFA'],
    ]
    proj_tbl = Table(proj_rows,
                     colWidths=[W * 0.2, W * 0.15, W * 0.22, W * 0.2, W * 0.23])
    proj_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NEBULA_CARD),
        ('TEXTCOLOR', (0, 0), (-1, 0), NEBULA_VIOLET),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BACKGROUND', (0, 1), (-1, 1), NEBULA_CARD2),
        ('BACKGROUND', (0, 2), (-1, 2), HexColor('#111125')),
        ('BACKGROUND', (0, 3), (-1, 3), NEBULA_CARD2),
        ('BACKGROUND', (0, 4), (-1, 4), HexColor('#3d2c00')),
        ('TEXTCOLOR', (0, 1), (-1, -2), NEBULA_LIGHT),
        ('TEXTCOLOR', (0, -1), (-1, -1), GOLD_COLOR),
        ('TEXTCOLOR', (4, 1), (4, -1), NEBULA_GREEN),
        ('TEXTCOLOR', (3, 1), (3, -1), NEBULA_CYAN),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, NEBULA_BORDER),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(proj_tbl)

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        '* Revenu réseau estimatif basé sur un réseau de 4 personnes actives en moyenne.',
        ParagraphStyle('note', fontName='Helvetica', fontSize=7.5,
                       textColor=NEBULA_MUTED)
    ))
    story.append(Spacer(1, 16))

    # ─── CTA Final ───
    cta_data = [[
        Paragraph(
            'REJOIGNEZ LE RÉSEAU NEBULA AGENCY',
            ParagraphStyle('ctah', fontName='Helvetica-Bold', fontSize=13,
                           textColor=white, alignment=TA_CENTER)
        ),
        Paragraph(
            'WhatsApp : +229 97 XX XX XX',
            ParagraphStyle('ctac', fontName='Helvetica-Bold', fontSize=10,
                           textColor=NEBULA_GREEN, alignment=TA_CENTER)
        ),
    ]]

    cta_inner = [[
        Paragraph(
            '🚀  <b>REJOIGNEZ LE RÉSEAU NEBULA AGENCY</b><br/>'
            '<font size="9" color="#94A3B8">Vendez des vitrines digitales, construisez votre réseau, '
            'encaissez des commissions dès votre première vente.<br/>'
            'Inscription gratuite — Formation incluse — Paiement en 48h</font>',
            ParagraphStyle('ctai', fontName='Helvetica', fontSize=10,
                           textColor=white, alignment=TA_CENTER, leading=16)
        ),
    ]]
    cta_t = Table(cta_inner, colWidths=[W])
    cta_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NEBULA_PURPLE),
        ('TOPPADDING', (0, 0), (-1, -1), 18),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ROUNDEDCORNERS', [10]),
        ('LINEABOVE', (0, 0), (-1, 0), 2, NEBULA_GOLD),
        ('LINEBELOW', (0, -1), (-1, -1), 2, NEBULA_PINK),
    ]))
    story.append(cta_t)
    story.append(Spacer(1, 10))

    # Footer
    footer_data = [[
        Paragraph('NEBULA Agency — Cotonou, Bénin — Afrique de l\'Ouest',
                  ParagraphStyle('f', fontName='Helvetica', fontSize=7.5,
                                 textColor=NEBULA_MUTED, alignment=TA_CENTER)),
        Paragraph('Document confidentiel — Réservé aux partenaires',
                  ParagraphStyle('f2', fontName='Helvetica', fontSize=7.5,
                                 textColor=NEBULA_MUTED, alignment=TA_CENTER)),
    ]]
    foot_t = Table(footer_data, colWidths=[W / 2, W / 2])
    foot_t.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, NEBULA_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(foot_t)

    # ─── Build ────────────────────────────────────────────────────────
    def on_first_page(canv, doc):
        pass  # header géré en flowable

    def on_later_pages(canv, doc):
        # Petit logo en haut à droite
        canv.saveState()
        canv.setFillColor(NEBULA_PURPLE)
        canv.roundRect(A4[0] - 90, A4[1] - 20, 72, 14, 5, fill=1, stroke=0)
        canv.setFillColor(white)
        canv.setFont('Helvetica-Bold', 7)
        canv.drawCentredString(A4[0] - 54, A4[1] - 13, 'NEBULA AGENCY')
        # Numéro de page
        canv.setFillColor(NEBULA_MUTED)
        canv.setFont('Helvetica', 7)
        canv.drawCentredString(A4[0] / 2, 10, f'Page {doc.page}')
        canv.restoreState()

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f'PDF généré : {output_path}')


if __name__ == '__main__':
    output = '/home/user/nebula-agency/_docs/NEBULA_Commission_Partenaires_2025.pdf'
    build_pdf(output)
