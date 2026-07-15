# 2026-07-15 — Luxury Club 229 : QR étiquette produits (INA) + QR « menu des soins » (Skin Clinic)

Deux QR **distincts** demandés par Mme Luxury, en plus du QR « univers » de sa carte de visite (qui pointe vers le hub `luxuryclub229.com`).

## 1) QR étiquette produits → INA Luxury
- Cible : **https://luxuryclub229.com/ina-luxury** (page produits, canonical vérifié 200).
- Usage : à coller sur les **étiquettes de ses produits**.
- Livrables (`clients/04-luxury-skin-clinic/assets/docs/`) :
  - `qr-ina-luxury.svg` (vectoriel, à intégrer sur ses propres étiquettes sans pixeliser) + `qr-ina-luxury.png` (1024 px, ECC **H** robuste pour produit).
  - **`Etiquette_QR_INA_Luxury.pdf` + `.png`** : étiquette prête à imprimer (carré ~60 mm), charte INA (crème #faf6ec + or #c9a84c), wordmark « INA LUXURY · Cosmétiques & Capillaires », CTA « Scannez pour découvrir tous nos produits ».
- Commit `9bb6a61`.

## 2) QR « menu des soins » → Luxury Skin Clinic (pour les tables de la clinique)
- Cible : **https://luxuryclub229.com/luxury-skin-clinic#soins** (atterrit direct sur la section soins ; ancre `#soins` de `luxury-skin-clinic.html`).
- Usage : sur les **petites tables à côté des sièges** des clientes → consulter le menu des soins.
- Action : **affiche carrée modifiée** (`affiche-luxury-skin-clinic-carre.html`) — l'ancien QR pointait vers le hub (l'univers), remplacé par le QR soins ; textes → « Scannez pour le menu des soins » / « Le menu de nos soins ». Régénéré `Affiche_Luxury_Skin_Clinic_Carre.pdf` + `.png` (hi-res). QR nu aussi : `qr-luxury-skin-clinic-soins.png` + `.svg` (ECC M).
- Commit `e757853`.

## Bien distinguer les 3 QR
| QR | Destination | Support |
|---|---|---|
| Carte de visite (existant) | `luxuryclub229.com` (hub) | découvrir tout l'univers |
| **Étiquette produits** | `/ina-luxury` | produits INA sur les étiquettes |
| **Tables clinique** | `/luxury-skin-clinic#soins` | menu des soins sur les tables |

## Méthode QR (rappel)
`qrcode` (npm) → PNG/SVG, **QR toujours vérifié par décodage `jsqr`** (pas juste « affiché »). Affiche régénérée via **puppeteer réel** (`page.pdf` 210×210 mm + screenshot `.sheet`), en attendant `document.fonts.ready` (Google Fonts Cormorant/Jost). ⚠️ chemins node sous Windows = `C:/...` (pas `/c/...`). QR de l'affiche re-décodé après rendu = URL soins exacte. Cf. [[reference_print-generation]].

Rien à déployer (les QR pointent vers le site déjà en ligne).
