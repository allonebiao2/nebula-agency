# -*- coding: utf-8 -*-
import os, math, urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import qrcode

CL   = r"C:/Users/USER/nebula-agency/clients/09-au-braise-dor"
IMG  = CL + "/assets/images"
DOCS = CL + "/assets/docs"; os.makedirs(DOCS, exist_ok=True)
F    = "C:/Windows/Fonts/"

W, H = 2480, 3508           # A4 @ 300 DPI
CX   = W // 2
GOLD   = (244, 212, 149); GOLD2=(233,184,102); GOLDD=(200,149,61)
CREAM  = (246, 236, 218); CREAMD=(220,202,169); MUTED=(150,132,110)
EMBER  = (255, 106, 26);  INK=(20,12,7)

def font(name, sz): return ImageFont.truetype(F+name, sz)
cam  = lambda s: font("cambriab.ttf", s)     # serif elegant (headings/brand)
ar   = lambda s: font("arial.ttf", s)
arb  = lambda s: font("arialbd.ttf", s)

# ---------- background : dégradé braise + halo d'ember bas ----------
top=np.array([13,7,4.]); mid=np.array([30,19,10.]); bot=np.array([36,22,13.])
t=np.linspace(0,1,H)[:,None]
grad=np.where(t<0.5, top*(1-t*2)+mid*(t*2), mid*(1-(t-.5)*2)+bot*((t-.5)*2))
bg=np.repeat(grad[:,None,:],W,axis=1)
yy,xx=np.mgrid[0:H,0:W]
def glow(cx,cy,rad,col,strength,pw=1.0):
    r=np.sqrt(((xx-cx)/1.0)**2+((yy-cy)/pw)**2)
    g=np.clip(1-r/rad,0,1)**1.7
    return g[...,None]*np.array(col)*strength
bg=bg+glow(CX, H*1.03, W*0.95, EMBER, .60, 1.15)          # grand halo braise en bas
bg=bg+glow(W*0.12,-H*0.02, W*0.5, (226,64,27),.16)        # coin haut-gauche
bg=bg+glow(W*0.9,  H*0.03, W*0.45,(233,184,102),.10)      # coin haut-droit
bg=np.clip(bg,0,255).astype("uint8")
img=Image.fromarray(bg,"RGB"); d=ImageDraw.Draw(img,"RGBA")

# ---------- helpers ----------
def cover(im,w,h):
    s=max(w/im.width,h/im.height); im=im.resize((math.ceil(im.width*s),math.ceil(im.height*s)),Image.LANCZOS)
    x=(im.width-w)//2; y=(im.height-h)//2; return im.crop((x,y,x+w,y+h))
def rounded(im,rad):
    m=Image.new("L",im.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,im.size[0]-1,im.size[1]-1],rad,fill=255)
    im=im.convert("RGBA"); im.putalpha(m); return im
def paste_photo(path,x,y,w,h,rad,caption=None,cap_sz=40):
    ph=cover(Image.open(path).convert("RGB"),w,h)
    # scrim bas pour lisibilité légende
    if caption:
        sc=Image.new("RGBA",(w,h),(0,0,0,0)); sd=ImageDraw.Draw(sc)
        for i in range(h):
            a=int(200*max(0,(i-(h*0.55))/(h*0.45)))
            sd.line([(0,i),(w,i)],fill=(11,6,3,a))
        ph=Image.alpha_composite(ph.convert("RGBA"),sc).convert("RGB")
    rim=rounded(ph,rad); img.paste(rim,(x,y),rim)
    d.rounded_rectangle([x,y,x+w-1,y+h-1],rad,outline=(233,184,102,150),width=3)
    if caption:
        d.text((x+34,y+h-cap_sz-30),caption,font=cam(cap_sz),fill=CREAM)
def ctext(cx,y,txt,fnt,fill): d.text((cx,y),txt,font=fnt,fill=fill,anchor="mm")
def tracked(cx,y,txt,fnt,fill,sp):
    chars=list(txt); widths=[d.textlength(c,font=fnt)+sp for c in chars]; tot=sum(widths)-sp
    x=cx-tot/2
    for c,wdt in zip(chars,widths):
        d.text((x,y),c,font=fnt,fill=fill,anchor="lm"); x+=wdt
def fit(txt,make,maxw,start):
    s=start
    while s>18 and d.textlength(txt,font=make(s))>maxw: s-=2
    return make(s)

MG=180; INW=W-2*MG

# ---------- header ----------
tracked(CX, 250, "DE PARIS À COTONOU", arb(40), GOLD, 22)
ctext(CX, 440, "Au Braisé d'Or", cam(238), GOLD)
tag="Grillades au feu de bois · Pizzas · Chawarma · Salades · Cocktails"
ctext(CX, 628, tag, fit(tag,ar,INW-40,48), CREAMD)

# ---------- hero ----------
paste_photo(IMG+"/hero.webp", MG, 710, INW, 900, 56, "La braise, en direct", 52)

# ---------- trio de plats ----------
trio=[("tilapia.webp","Tilapia braisé"),("p-napolitaine.webp","Pizza feu de bois"),("k-mojito.webp","Cocktails maison")]
cw=(INW-2*40)//3; ty=1670; th=470
for i,(fn,lab) in enumerate(trio):
    tx=MG+i*(cw+40)
    paste_photo(IMG+"/"+fn, tx, ty, cw, th, 40, lab, 40)

# ---------- appel à commander ----------
ctext(CX, 2270, "Commandez en un geste", cam(96), GOLD)
sub="Scannez le code, composez votre commande, envoyez sur WhatsApp."
ctext(CX, 2360, sub, fit(sub,ar,INW-40,46), CREAMD)

# ---------- 2 cartes QR ----------
def qr_img(data,px):
    q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=12,border=2)
    q.add_data(data); q.make(fit=True)
    im=q.make_image(fill_color="black",back_color="white").convert("RGB")
    return im.resize((px,px),Image.NEAREST)

SITE="https://au-braise-dor.pages.dev"
WA  ="https://wa.me/2290156057157?text="+urllib.parse.quote("Bonjour Au Braisé d'Or, je voudrais passer une commande.")
cards=[(MG, "LE MENU EN LIGNE", SITE, "au-braise-dor.pages.dev"),
       (W-MG-820, "WHATSAPP DIRECT", WA, "01 56 05 71 57")]
cy0=2440; ch=700; cw2=820; qpx=520
for cx0,label,data,small in cards:
    d.rounded_rectangle([cx0,cy0,cx0+cw2,cy0+ch],46,fill=(247,240,228,255))
    ccx=cx0+cw2//2
    d.text((ccx,cy0+60),label,font=arb(46),fill=INK,anchor="mm")
    qr=qr_img(data,qpx); img.paste(qr,(ccx-qpx//2, cy0+110))
    d.text((ccx,cy0+ch-52),small,font=arb(40),fill=(120,70,20),anchor="mm")

# ---------- footer ----------
fy=3210
ctext(CX, fy,      "WhatsApp  01 56 05 71 57  ·  01 94 21 30 02", arb(42), CREAM)
ctext(CX, fy+64,   "aubraisedor@gmail.com   ·   Cotonou, Bénin   ·   WiFi 24h/24", ar(38), CREAMD)
ctext(CX, fy+130,  "RC RB/COT/24 A 102350  ·  IFU 0202501441177", ar(30), MUTED)
ctext(CX, fy+190,  "Vitrine créée par NEBULA Agency", arb(34), GOLD2)

# ---------- save ----------
png=DOCS+"/Affiche_Au_Braise_dOr_A4.png"
pdf=DOCS+"/Affiche_Au_Braise_dOr_A4.pdf"
img.save(png,"PNG")
img.save(pdf,"PDF",resolution=300.0)
print("PNG", round(os.path.getsize(png)/1024), "KB  |  PDF", round(os.path.getsize(pdf)/1024), "KB")
print("SITE_QR:", SITE)
print("WA_QR:", WA)
