# 2026-05-27 — INA Luxury : sous-catégorie Savon Noir + 2 produits

## Contexte
Mongazi : ajouter 2 produits dans INA Luxury / Corps, dans une **nouvelle
sous-catégorie « Savon Noir »**. Images fournies dans
`clients/04-luxury-skin-clinic/assets/_inbox/`.

## Modifications

### `ina-luxury.html`
1. **`EMO_BY_SUB`** : ajout de `'savon-noir':'🖤'`.
2. **`SUBCATS.corps`** : 5e entrée ajoutée après Huile corps —
   `{key:'savon-noir',label:'Savon Noir'}`.
3. **Famille Corps `desc`** : « Beauty bars, crèmes, gommages, huiles
   et savons noirs pour le corps. ».
4. **`IMG` map** : 2 nouvelles entrées (Savon Noir Papaya + Clarté Black Soap).
5. **`PRODUCTS`** : 2 nouvelles fiches complètes (description, résultats par
   paliers à 4 horizons, caractéristiques, conseils, INCI, lecture experte
   pour le Papaya).

### `index.html` (hub)
- Panneau INA Corps : `subs` étendu avec « Savon Noir ».

### Images
Pipeline `scripts/og-defringe.ps1` → 600×800 JPEG q78 :
- `Savon noir papaya .png` (1023×1537, 1.7 MB) → `savon-noir-papaya.jpg` (38 KB)
- `Clarté black soap .jpg` (1179×1720, 277 KB) → `clarte-black-soap.jpg` (20 KB)

Destination : `assets/images/ina-luxury/corps/savon-noir/`.
Sources archivées dans `_inbox/_processed/`.

## Produits ajoutés

### Savon Noir Papaya — 17 500 F · 500g
- Savon noir africain en texture pâte, papaye + réglisse.
- Concerns : `terne`, `irregulier-corps`, `eclat-corps`, `acne`.
- Résultats : 1ʳᵉ utilisation · 7-14j · 3-6 sem · 2-3 mois.
- INCI : African Black Soap, Carica Papaya Fruit Extract, Glycerin, Betaine,
  Glycyrrhiza Glabra Root Extract, Polyquaternium-7, Cocamidopropyl Betaine.

### Clarté Black Soap — 15 000 F · 300g
- Gel douche illuminateur, savon noir + panthénol + avoine + réglisse.
- Concerns : `terne`, `irregulier-corps`, `eclat-corps`, `peau-seche`.
- Résultats : premières utilisations · 3-6 sem · 2-3 mois.
- INCI complète avec Coco-Glucoside, Helianthus Annuus, Sodium PCA,
  Panthenol, Allantoin, Avena Sativa Extract, Glycyrrhiza Glabra Extract,
  Sodium Ascorbyl Phosphate.

## Points techniques notables

- **Caractères accentués dans `Resolve-Path`** : le script `og-defringe.ps1`
  échoue sur `Clarté black soap .jpg` (PowerShell 5.1 + accent + Resolve-Path
  → PathNotFound). Workaround appliqué : copie temporaire en `clarte-source.jpg`,
  traitement, suppression. À noter pour les prochaines images avec accents.
- **Compteurs auto** : `subCount()` et `PRODUCTS.filter(p=>p.f===f.key).length`
  recomputent dynamiquement → aucun chiffre à ajuster manuellement.
- INA Luxury : **35 → 37 produits** (compteur CONTEXT.md mis à jour).

## Tests visuels rapides (serveur local 8077)
- `ina-luxury.html` → 200 OK · 296 KB.
- Image papaya → 200 OK · 39 KB.
- Image clarté → 200 OK · 20 KB.
- Recherche `grep` dans le HTML servi : 5 occurrences trouvées (SUBCATS,
  EMO, IMG×2, PRODUCTS×2). OK.

## Fichiers touchés
- `clients/04-luxury-skin-clinic/ina-luxury.html`
- `clients/04-luxury-skin-clinic/index.html`
- `clients/04-luxury-skin-clinic/assets/images/ina-luxury/corps/savon-noir/savon-noir-papaya.jpg` (nouveau)
- `clients/04-luxury-skin-clinic/assets/images/ina-luxury/corps/savon-noir/clarte-black-soap.jpg` (nouveau)
- `clients/04-luxury-skin-clinic/assets/_inbox/_processed/Savon noir papaya .png` (déplacé)
- `clients/04-luxury-skin-clinic/assets/_inbox/_processed/Clarté black soap .jpg` (déplacé)
- `clients/04-luxury-skin-clinic/CONTEXT.md`
- `_memoire/journal/2026-05-27-journal.md`
- `_memoire/conversations/2026-05-27-ina-savon-noir.md` (ce fichier)
