#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rend l'affiche carrée en PNG haute résolution (3240px) + PDF carré, via Playwright."""
import os
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT,"assets","docs"), exist_ok=True)
url="file:///"+os.path.join(ROOT,"affiche_carre.html").replace("\\","/")
png=os.path.join(ROOT,"assets","docs","Affiche_Grain_Carre.png")
pdf=os.path.join(ROOT,"assets","docs","Affiche_Grain_Carre.pdf")
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={"width":1080,"height":1080}, device_scale_factor=3)
    pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(1200)
    pg.screenshot(path=png, clip={"x":0,"y":0,"width":1080,"height":1080})
    pg.pdf(path=pdf, width="1080px", height="1080px", print_background=True, margin={"top":"0","right":"0","bottom":"0","left":"0"})
    b.close()
print("PNG:", png, os.path.getsize(png)//1024, "KB")
print("PDF:", pdf, os.path.getsize(pdf)//1024, "KB")
