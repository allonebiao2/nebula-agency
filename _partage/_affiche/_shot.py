
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":1440,"height":900}, device_scale_factor=2)
    pg.goto("https://angyart.online/", wait_until="load")
    pg.wait_for_timeout(4200)          # le rideau d'ouverture dure ~3,4 s
    pg.mouse.wheel(0, 1)               # un contact, pour poser la page
    pg.wait_for_timeout(900)
    pg.screenshot(path="_partage/_affiche/angyart-ecran.png")
    b.close()
print("capture faite")
