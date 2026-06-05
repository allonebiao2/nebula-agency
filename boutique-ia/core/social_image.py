"""Vendora Social — générateur d'IMAGES de posts (templates brandés, SANS IA payante).

Compose une image carrée (1080×1080) prête à poster : photo du produit (déjà
uploadée) en fond + dégradé + accroche + prix + nom de la boutique, aux couleurs
de la marque. 100 % local (Pillow), gratuit, sans carte bancaire. La génération
d'images par IA (scène de zéro) = brique payante séparée, plus tard.
"""
from __future__ import annotations

import io
import logging
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger("boutique-ia.social_image")

_FONTS = Path(__file__).resolve().parent.parent / "web" / "static" / "fonts"
_BOLD = str(_FONTS / "Poppins-Bold.ttf")
_REG = str(_FONTS / "Poppins-Regular.ttf")

W = H = 1080


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = (h or "").strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except Exception:  # noqa: BLE001
        return (124, 58, 237)  # violet par défaut


def _mix(c: tuple, d: tuple, t: float) -> tuple:
    return tuple(int(c[i] + (d[i] - c[i]) * t) for i in range(3))


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """Redimensionne + recadre l'image pour remplir w×h (style object-fit: cover)."""
    img = img.convert("RGB")
    r = max(w / img.width, h / img.height)
    nw, nh = int(img.width * r), int(img.height * r)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def _gradient_bg(c1: tuple, c2: tuple) -> Image.Image:
    """Fond dégradé diagonal (si pas de photo produit)."""
    base = Image.new("RGB", (W, H), c1)
    top = Image.new("RGB", (W, H), c2)
    mask = Image.new("L", (W, H))
    md = mask.load()
    for y in range(H):
        for x in range(0, W, 4):
            v = int(255 * ((x + y) / (W + H)))
            for dx in range(4):
                if x + dx < W:
                    md[x + dx, y] = v
    base.paste(top, (0, 0), mask)
    return base


def _overlay_bottom(img: Image.Image, strength: float = 0.86) -> None:
    """Assombrit le bas pour la lisibilité du texte (dégradé vertical noir)."""
    grad = Image.new("L", (1, H))
    for y in range(H):
        t = max(0.0, (y / H - 0.32) / 0.68)
        grad.putpixel((0, y), int(255 * strength * (t ** 1.5)))
    alpha = grad.resize((W, H))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(black, (0, 0), alpha)


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    words = (text or "").split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:4]


def render_post_image(merchant: dict, headline: str, price_text: str | None = None,
                      product_image_bytes: bytes | None = None) -> bytes:
    """Compose l'image du post → octets PNG."""
    brand = _hex_to_rgb(merchant.get("brand_color") or "#7C3AED")
    shop = (merchant.get("business_name") or "Ma boutique").strip()

    # Fond : photo produit (assombrie en bas) sinon dégradé de marque.
    if product_image_bytes:
        try:
            canvas = _fit_cover(Image.open(io.BytesIO(product_image_bytes)), W, H)
        except Exception:  # noqa: BLE001
            canvas = _gradient_bg(brand, _mix(brand, (0, 0, 0), 0.55))
    else:
        canvas = _gradient_bg(brand, _mix(brand, (0, 0, 0), 0.55))
    _overlay_bottom(canvas)

    draw = ImageDraw.Draw(canvas)
    pad = 72

    # Bandeau marque en haut (pastille couleur + nom).
    draw.rounded_rectangle([pad, pad, pad + 16, pad + 46], radius=8, fill=brand)
    draw.text((pad + 30, pad + 4), shop, font=_font(_BOLD, 40), fill=(255, 255, 255))

    # Accroche (bas), retour à la ligne automatique.
    hl_font = _font(_BOLD, 72)
    lines = _wrap(draw, headline or shop, hl_font, W - 2 * pad)
    line_h = 84
    block_h = len(lines) * line_h
    y = H - pad - block_h - (96 if price_text else 0)
    for ln in lines:
        draw.text((pad, y), ln, font=hl_font, fill=(255, 255, 255))
        y += line_h

    # Badge prix (pastille couleur de marque).
    if price_text:
        pf = _font(_BOLD, 46)
        tw = draw.textlength(price_text, font=pf)
        bx, by = pad, H - pad - 76
        draw.rounded_rectangle([bx, by, bx + tw + 56, by + 76], radius=38, fill=brand)
        draw.text((bx + 28, by + 12), price_text, font=pf, fill=(255, 255, 255))

    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()
