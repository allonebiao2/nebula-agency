# HH Design — CONTEXT

## ⚠️ PIVOT MAJEUR (2026-07-04) — HH DESIGN = ÉBÉNISTERIE, PAS IMMOBILIER
La première version (2026-06-30) était bâtie comme une **agence immobilière** (erreur de brief).
Les planches de marque envoyées par Mongazi (`_partage/inspiration 1..8.JPG`) révèlent la vraie
identité : **HH DESIGN est une maison d'ébénisterie / mobilier haut de gamme** — meubles en bois
massif noble, faits main. Le site a été **entièrement reconstruit** autour de cette identité.

## Identité
- **Marque** : HH DESIGN — maison d'ébénisterie / mobilier sur-mesure
- **Secteur** : Mobilier bois noble (étagères, bibliothèques, tables de chevet, tables basses, consoles)
- **Ville** : Cotonou, Bénin (présence France aussi)
- **Signatures** : « L'élégance du bois » · « Créé pour durer. Pensé pour vous. » · « Qualité · Durabilité · Élégance »
- **Bois** : mindi massif, acajou (placages) · **Finitions** : roasted coffee, naturelle, pearl brushed
- **WhatsApp** : **+229 01 62 68 67 68** → `wa.me/2290162686768` ⚠️ **À CONFIRMER** (issu de leurs
  propres planches ; **remplace** l'ancien 0167975626 qui était douteux car = n° du client 04)
- **Autre contact** : France +33 6 50 98 56 97 · Instagram « HH DESIGN » (handle exact à confirmer)
- **Couleurs marque** : crème sable · bois (mindi/acajou/roasted) · or vieilli · espresso

## Produits réels (issus des planches, données exactes)
| Modèle | Type | Bois | Finition | Dimensions |
|---|---|---|---|---|
| **AYULA** | Étagère / bibliothèque | Mindi massif / placage | Roasted coffee | 4 niveaux |
| **LEON** | Bibliothèque (façade sculptée main) | Mindi massif / placage | Pearl brushed | L100 × P46 × H190 |
| **CANCUN** | Table de chevet | Mindi massif | Roasted coffee light | L57 × P48 × H60 |
| **TABASCO** | Table de chevet (2 niveaux) | Acajou massif | Roasted coffee light | L50 × P40 × H60 |
| **NATURA** | Table basse (design organique) | Mindi massif | Naturelle | L120 × P60 × H35 |
| **Console TV** | Meuble télé suspendu | Bois massif | Façade verre strié | câbles intégrés |

## Parti-pris design (v2 — TOTALEMENT distinct de la v1 immobilière ET des autres vitrines)
- **Univers** : crème sable + bois noble + or vieilli + espresso (chaud, tactile, galerie). ≠ blanc/or/noir immobilier.
- **Typo** : **Cormorant Garamond** (serif Didone : monogramme HH + noms de pièces) + **Archivo**
  (grotesque : structure, corps). ≠ Marcellus/Manrope de la v1.
- **Hero** : plein cadre en **bois brut dramatique** (photo lames de bois), Ken-Burns + parallaxe,
  « Le bois, le détail, la différence. »
- **Collection** : grille filtrable (Tout/Rangements/Tables/Salon), cartes « spécimen » (produit sur
  fond crème + libellé + méta bois/finition/dimensions) → **fiche modale espresso** (image + specs +
  CTA « Commander ce modèle » / « Version sur-mesure » WhatsApp pré-rempli). ≠ galeries des autres sites.
- **Sections** : hero → bandeau valeurs → manifeste espresso (3 piliers) → collection → bande
  ambiance (lifestyle) → matières & finitions (4 échantillons bois) → sur-mesure (4 étapes) →
  contact (form → WhatsApp) → footer. FAB WhatsApp.
- **Images** : **vraies photos** extraites des planches (produits détourés sur crème + bois + ambiance),
  optimisées WebP (~250 Ko au total). Scripts `_partage` → `assets/images/{hero,collection,materials}`.
- **Motion** : reveals (IntersectionObserver), tracés dorés (scaleX), Ken-Burns, hover cartes. reduced-motion complet.
- **a11y/QC** : hook impeccable passé (transform au lieu de width, placeholder image, em-dashes retirés,
  numéros de piliers retirés — steps sur-mesure gardés car vraie séquence). `node --check` JS OK.
  Capture headless desktop + mobile vérifiée.

## À REMPLACER / CONFIRMER (côté client)
- [ ] **CONFIRMER le n° WhatsApp** +229 01 62 68 67 68 (⚠️ règle absolue avant diffusion large)
- [ ] **Vrai logo** HH (monogramme officiel en PNG transparent) — actuellement rendu en typo Cormorant
- [ ] **Handle Instagram exact** (affiché « HH DESIGN » sans lien réel)
- [ ] **Adresse atelier exacte** + point Google Maps (actuellement « Cotonou »)
- [ ] **Prix** des modèles (le site renvoie vers WhatsApp pour le devis)
- [ ] Autres pièces / nouvelles collections à ajouter
- [ ] Photos produit haute résolution (les visuels actuels viennent des planches marketing, def. limitée)

## Déploiement
- ✅ **LIVE : https://hh-design.pages.dev** (Cloudflare Pages, projet `hh-design`)
- Déploiement depuis un dossier propre (index.html + assets), sans exposer CONTEXT/scripts.
- Affiche A4 + 2 QR (site + WhatsApp) : `assets/docs/Affiche_HH_Design_A4.pdf` (crème/bois/or, HH mono).
- QR : `assets/images/qr/qr-site.png` (site) + `qr-wa.png` (WhatsApp). Ancien `qr-maps.png` supprimé.

## Historique
- **2026-06-30** — v1 : vitrine « agence immobilière » (blanc/or/noir, Marcellus). **Obsolète** (mauvais brief).
- **2026-07-04** — v2 : **refonte totale ébénisterie** (crème/bois/or/espresso, Cormorant+Archivo,
  collection réelle + fiches, matières, sur-mesure). Vraies images des planches. LIVE + affiche + QR refaits.
