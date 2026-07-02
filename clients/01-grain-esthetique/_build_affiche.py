#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère le QR (vers graindesthetique.com) + l'affiche CARRÉE 1:1 (HTML) de Grain d'Esthétique."""
import io, os, base64
import qrcode
from qrcode.constants import ERROR_CORRECT_H
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join("assets","docs"), exist_ok=True)

URL = "https://graindesthetique.com"
qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, box_size=20, border=2)
qr.add_data(URL); qr.make(fit=True)
imgqr = qr.make_image(fill_color="#231018", back_color="#ffffff").convert("RGB")
buf = io.BytesIO(); imgqr.save(buf, format="PNG")
qr64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
print("QR généré :", imgqr.size, "px")

HTML = """<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,600&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
.poster{width:1080px;height:1080px;position:relative;overflow:hidden;background:
  radial-gradient(120% 80% at 50% -10%,#FBE9F1 0%,#FFFFFF 46%,#FDF5F8 100%);
  font-family:'Jost',sans-serif;color:#1A0E14;display:flex;flex-direction:column;align-items:center;
  justify-content:space-between;padding:74px 70px 60px;text-align:center}
.poster::before,.poster::after{content:"";position:absolute;width:340px;height:340px;border-radius:50%;
  background:radial-gradient(circle,rgba(212,175,114,.16),transparent 68%)}
.poster::before{top:-120px;left:-120px}
.poster::after{bottom:-130px;right:-130px;background:radial-gradient(circle,rgba(196,100,138,.14),transparent 68%)}
.corner{position:absolute;width:78px;height:78px;border:1.5px solid rgba(212,175,114,.55)}
.c1{top:40px;left:40px;border-right:0;border-bottom:0}
.c2{top:40px;right:40px;border-left:0;border-bottom:0}
.c3{bottom:40px;left:40px;border-right:0;border-top:0}
.c4{bottom:40px;right:40px;border-left:0;border-top:0}
.top{position:relative;z-index:2}
.eyebrow{font-size:16px;letter-spacing:.42em;text-transform:uppercase;color:#B0708C;font-weight:500;margin-bottom:14px}
.name{font-family:'Cormorant Garamond',serif;font-weight:300;font-size:78px;line-height:1;color:#1A0E14}
.name em{font-style:italic;color:#C4648A}
.rule{display:flex;align-items:center;justify-content:center;gap:14px;margin:22px 0 10px}
.rl{width:90px;height:1px;background:linear-gradient(90deg,transparent,#D4AF72)}
.rr{width:90px;height:1px;background:linear-gradient(90deg,#D4AF72,transparent)}
.gem{width:9px;height:9px;background:#C4648A;transform:rotate(45deg)}
.place{font-size:17px;letter-spacing:.32em;text-transform:uppercase;color:#9A7A88;font-weight:400}
.mid{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center}
.scan{font-size:15px;letter-spacing:.42em;text-transform:uppercase;color:#C4648A;font-weight:600;margin-bottom:18px}
.qrcard{position:relative;background:#fff;border-radius:26px;padding:26px;
  box-shadow:0 26px 60px -22px rgba(196,100,138,.45),0 0 0 1px rgba(212,175,114,.5),0 0 0 8px #fff,0 0 0 9px rgba(212,175,114,.35)}
.qrcard img{width:360px;height:360px;display:block;image-rendering:pixelated}
.qrgem{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:64px;height:64px;border-radius:14px;
  background:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(26,14,20,.14)}
.qrgem svg{width:38px;height:38px}
.cta{font-family:'Cormorant Garamond',serif;font-size:33px;font-weight:400;color:#2D1E27;margin-top:26px;line-height:1.32;max-width:640px}
.cta b{color:#C4648A;font-weight:600;font-style:italic}
.bot{position:relative;z-index:2;width:100%}
.contact{display:flex;align-items:center;justify-content:center;gap:26px;flex-wrap:wrap;margin-bottom:16px}
.ct{display:inline-flex;align-items:center;gap:9px;font-size:19px;color:#1A0E14;font-weight:500}
.ct svg{width:21px;height:21px;fill:none;stroke:#C4648A;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.web{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:26px;color:#C4648A;letter-spacing:.02em}
.footbar{margin-top:18px;height:3px;width:100%;background:linear-gradient(90deg,transparent,#C4648A 30%,#D4AF72 50%,#C4648A 70%,transparent)}
.credit{margin-top:12px;font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:rgba(138,80,100,.5)}
</style></head><body>
<div class="poster">
  <div class="corner c1"></div><div class="corner c2"></div><div class="corner c3"></div><div class="corner c4"></div>
  <div class="top">
    <div class="eyebrow">Institut de Beauté</div>
    <div class="name">Grain <em>d'Esthétique</em></div>
    <div class="rule"><span class="rl"></span><span class="gem"></span><span class="rr"></span></div>
    <div class="place">Cotonou · Haie-Vive</div>
  </div>
  <div class="mid">
    <div class="scan">Scannez-moi</div>
    <div class="qrcard">
      <img src="__QR__" alt="QR code Grain d'Esthétique">
      <div class="qrgem"><svg viewBox="0 0 24 24" fill="none" stroke="#C4648A" stroke-width="1.5" stroke-linejoin="round"><circle cx="12" cy="12" r="2.4" fill="#C4648A" stroke="none"/><path d="M12 9.6a2.6 2.6 0 1 1 0-5.2 2.6 2.6 0 0 1 0 5.2M12 14.4a2.6 2.6 0 1 1 0 5.2 2.6 2.6 0 0 1 0-5.2M9.6 12a2.6 2.6 0 1 1-5.2 0 2.6 2.6 0 0 1 5.2 0M14.4 12a2.6 2.6 0 1 1 5.2 0 2.6 2.6 0 0 1-5.2 0"/></svg></div>
    </div>
    <div class="cta">Découvrez nos soins<br>&amp; <b>prenez rendez-vous</b> en un scan.</div>
  </div>
  <div class="bot">
    <div class="contact">
      <span class="ct"><svg viewBox="0 0 24 24"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9 9 0 0 1-4-1L3 21l1.5-4.5A8.5 8.5 0 1 1 21 11.5Z"/></svg>01 97 08 55 76</span>
      <span class="ct"><svg viewBox="0 0 24 24"><path d="M12 21s-6.5-5.2-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.8 12 21 12 21Z"/><circle cx="12" cy="10.3" r="2.4"/></svg>Sur rendez-vous</span>
    </div>
    <div class="web">graindesthetique.com</div>
    <div class="footbar"></div>
    <div class="credit">Vitrine signée NEBULA Agency</div>
  </div>
</div></body></html>"""
HTML = HTML.replace("__QR__", qr64)
io.open("affiche_carre.html","w",encoding="utf-8").write(HTML)
print("affiche_carre.html écrite (1080x1080)")
