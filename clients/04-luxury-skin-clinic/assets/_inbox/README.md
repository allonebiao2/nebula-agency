# 📥 _inbox — Boîte de dépôt des images

Dossier tampon pour **déposer les images en vrac** avant de les ranger dans la
bonne arborescence `assets/images/ina-luxury/...`.

## À quoi ça sert

Quand Gloria envoie des photos de produits, on ne sait pas toujours tout de
suite où elles vont. On les pose ici, puis Claude Code les **dispatche** vers la
bonne catégorie / sous-catégorie.

## Comment l'utiliser

1. **Déposer** toutes les images reçues dans ce dossier (`_inbox/`).
2. Si possible, **renommer** chaque fichier pour donner un indice :
   `capillaires-shampoing-aloe.jpg`, `visage-serum-ice.png`, etc.
3. Dire à Claude Code : **« dispatche les images de l'inbox »**.
4. Claude range chaque image dans le bon sous-dossier et **vide l'inbox**.

## Destinations possibles (INA Luxury)

```
assets/images/ina-luxury/
├── visage/        → gel-nettoyants · serums · cremes · masque · demaquillants
├── corps/         → beauty-bar · creme-corps · gommage · huile-corps
├── capillaires/   → shampoing · apres-shampoing · masque · serum · huile-beurre
└── visage/...     (voir l'arborescence réelle du dossier)
```

## Règles NEBULA à respecter

- Les images des vitrines doivent finir **en base64 dans le HTML** — l'inbox et
  les dossiers `assets/images/` servent au **stockage source / archivage**.
- Formats acceptés : `.jpg` `.jpeg` `.png` `.webp`.
- Ce dossier doit rester **vide après chaque dispatch** (seul ce `README.md`
  reste en place).

---
*Boîte de dépôt — clients/04-luxury-skin-clinic/assets/_inbox/*
