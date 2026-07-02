#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère l'image de partage social OG (1200x630) de NEBULA Agency :
fond cosmique + wordmark + accroche + 3 vrais sites clients. UTF-8."""
import os, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=os.path.dirname(os.path.abspath(__file__))
PORT=r"C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-nebula-agency\79468563-0b06-48bc-bdf7-2e27043a505c\scratchpad\port"
os.makedirs(os.path.join(ROOT,"assets"),exist_ok=True)
W,H=1200,630
img=Image.new("RGB",(W,H),(6,7,19))
# glows cosmiques
def glow(cx,cy,r,color,a):
    g=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(g)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=color+(a,));g=g.filter(ImageFilter.GaussianBlur(120))
    img.paste(Image.alpha_composite(img.convert("RGBA"),g).convert("RGB"),(0,0))
glow(980,60,360,(147,51,234),150)
glow(140,180,340,(79,111,255),130)
glow(600,700,420,(34,211,238),60)
d=ImageDraw.Draw(img)
FT=r"C:\Windows\Fonts"
def font(n,s):
    for name in n:
        try:return ImageFont.truetype(os.path.join(FT,name),s)
        except Exception:pass
    return ImageFont.load_default()
f_word=font(["bahnschrift.ttf","segoeuib.ttf","arialbd.ttf"],46)
f_h1=font(["bahnschrift.ttf","segoeuib.ttf","arialbd.ttf"],76)
f_tag=font(["segoeui.ttf","arial.ttf"],27)
f_small=font(["consola.ttf","cour.ttf"],19)
# logo orbital
lx,ly=64,60
d.ellipse([lx,ly,lx+34,ly+34],fill=(138,160,255))
d.ellipse([lx-9,ly+3,lx+43,ly+31],outline=(147,51,234),width=3)
d.text((lx+52,ly-2),"NEBULA AGENCY",font=f_word,fill=(238,240,251))
d.text((lx+54,ly+40),"COTONOU · AFRIQUE DE L'OUEST",font=f_small,fill=(120,126,160))
# accroche
d.text((64,196),"Des vitrines qui vendent.",font=f_h1,fill=(238,240,251))
# ligne dégradée (accent)
grad=Image.new("RGB",(300,6),(0,0,0))
for x in range(300):
    t=x/300;grad.putpixel((x,0),(int(79+(147-79)*t),int(111+(51-111)*t),int(255-(255-234)*t)))
grad=grad.resize((300,6));import itertools
for yy in range(6):
    for xx in range(300):img.putpixel((64+xx,300+yy),grad.getpixel((xx,0)))
d.text((64,320),"Livrées en 5 à 7 jours.",font=f_h1,fill=(192,132,252))
d.text((66,420),"Vitrines sur-mesure · Catalogues WhatsApp · QR codes",font=f_tag,fill=(166,171,206))
# 3 vrais sites clients en bas
shots=["djambar","speedwein","misscakes"]
cw,ch,gap=352,150,20;x0=64;y0=456
for i,sl in enumerate(shots):
    p=os.path.join(PORT,sl+".webp")
    if not os.path.exists(p):continue
    sh=Image.open(p).convert("RGB").resize((cw,ch),Image.LANCZOS)
    # cadre arrondi
    mask=Image.new("L",(cw,ch),0);md=ImageDraw.Draw(mask);md.rounded_rectangle([0,0,cw,ch],14,fill=255)
    fr=Image.new("RGB",(cw+2,ch+2),(40,46,70))
    x=x0+i*(cw+gap)
    img.paste(fr,(x-1,y0-1))
    img.paste(sh,(x,y0),mask)
out=os.path.join(ROOT,"assets","og-nebula.jpg")
img.save(out,quality=88,optimize=True)
print("OG:",out,os.path.getsize(out)//1024,"KB")
