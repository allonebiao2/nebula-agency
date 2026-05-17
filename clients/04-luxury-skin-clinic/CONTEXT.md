# CONTEXT — LUXURY SKIN CLINIC (Ahouangnimon Gloria)

## Identité

- **Nom du client** : Ahouangnimon Gloria
- **Marque principale** : LUXURY SKIN CLINIC
- **Secteur** : Cosmétique, soins de la peau, institut de beauté
- **Ville** : Cotonou, Bénin
- **WhatsApp** : 0167975626 ⚠️ INTOUCHABLE
- **Cible** : Clientèle beauté & bien-être premium en Afrique de l'Ouest

## Brief

Projet multi-marques composé de **4 pages HTML distinctes** :

1. **index.html** — page d'accueil centrale (hub)
   - 3 cards flottantes vers chaque marque
   - Liens Instagram et TikTok
   - Particules dorées + musique spa douce
   - Son cristal + zoom cinématique au clic

2. **ina-luxury.html** — catalogue produits cosmétiques et capillaires
   - Navigation : Visage / Corps / Capillaires
   - Sous-catégories par type de soin
   - Filtres par préoccupation cliquables
   - Fil d'Ariane retour niveau par niveau

3. **luxury-skin-clinic.html** — soins et prestations de l'institut
   - Navigation par type de soin
   - Filtres par préoccupation
   - Galerie photos + vidéo de présentation

4. **cozy.html** — hygiène intime et autres produits COZY
   - Catalogue produits COZY
   - Navigation par catégorie

## Architecture confirmée par la cliente (2026-05-17)

Architecture EXACTE des 3 marques, validée par Gloria. Elle pilote la navigation
de chaque page et l'arborescence `assets/images/`.

### MARQUE 1 — INA LUXURY (`ina-luxury.html`)
Produits cosmétiques et capillaires. Menu accordéon à 3 niveaux :
Catégorie → Sous-catégorie → filtres par préoccupation.

- **Visage** : Démaquillants · Gel nettoyants · Sérums · Crèmes · Masque
- **Corps** : Beauty bar · Crème corps · Gommage · Huile corps
- **Capillaires** : Shampoing · Après-shampoing · Sérum · Huile · Masque

### MARQUE 2 — LUXURY SKIN CLINIC (`luxury-skin-clinic.html`)
Soins et prestations en institut. Navigation = liste des 6 prestations
(barre de pastilles qui défile vers chaque prestation).

- Soin Oxygène · Soin Glass Skin · Peelings · Massage Luxury ·
  Gommage Luxury · Soin Complet VIP

### MARQUE 3 — COZY (`cozy.html`)
Hygiène intime et bien-être. Navigation = 3 catégories produits.

- Gel nettoyant intime · Huile intime · Crème parfumée

### Arborescence `assets/images/`
```
logo/  ·  galerie/  ·  hub/
ina-luxury/visage/{demaquillants,gel-nettoyants,serums,cremes,masque}
ina-luxury/corps/{beauty-bar,creme-corps,gommage,huile-corps}
ina-luxury/capillaires/{shampoing,apres-shampoing,serum,huile,masque}
luxury-skin-clinic/{soin-oxygene,soin-glass-skin,peelings,
                    massage-luxury,gommage-luxury,soin-complet-vip}
cozy/{gel-nettoyant-intime,huile-intime,creme-parfumee}
```

## Ton et univers

- **Style visuel** : luxe, élégance, premium, raffiné
- **Palette** : Blanc • Or • Noir
- **Typographie** : à définir (esprit haute couture / institut de beauté premium)

## Expérience utilisateur attendue

- Son cristal au touché de chaque carte
- Zoom cinématique à l'entrée dans chaque marque
- Cards marques flottantes avec lévitation douce
- Curseur personnalisé doré
- Particules dorées qui tombent en fond
- Phrase d'accueil qui s'écrit lettre par lettre
- Musique spa douce (bouton mute visible)
- Fil d'Ariane cliquable à chaque niveau
- Bouton retour sans ressortir entièrement
- Vidéo de présentation dans la galerie (clic pour lire)
- Badge Bestseller animé sur les produits phares

## Contenu fourni

- [ ] Textes (descriptions produits, soins, prestations)
- [ ] Photos / visuels produits (à encoder en base64)
- [ ] Logos des 3 marques (INA LUXURY, LUXURY SKIN CLINIC, COZY)
- [ ] Vidéo de présentation
- [ ] Coordonnées / horaires / réseaux (Instagram, TikTok)

## Contraintes

- **Deadline** : à définir
- **Budget** : 100 000 FCFA setup + 10 000 FCFA/mois
  (hébergement + sécurité + modifications illimitées 24h/24)
- **Hébergement** : Netlify
- **Technique** : HTML pur, CSS inline, zéro framework
- **Images** : toujours en base64, jamais de CDN externe
- WhatsApp de Gloria (`0167975626`) : **ne jamais modifier sans confirmation**

## État d'avancement

- [x] Brief reçu
- [ ] Brief validé
- [x] Structure dossiers créée
- [ ] Assets collectés
- [x] Maquette / direction artistique (framework v1)
- [x] HTML/CSS — index.html / hub (framework, contenu démo)
- [x] HTML/CSS — ina-luxury.html (framework, contenu démo)
- [x] HTML/CSS — luxury-skin-clinic.html (framework, contenu démo)
- [x] HTML/CSS — cozy.html (framework, contenu démo)
- [x] Architecture confirmée des 3 marques intégrée (navigation + dossiers)
- [ ] Contenu réel intégré (textes + photos base64 de la cliente)
- [ ] Responsive testé sur appareils réels
- [ ] Livré

## Décisions importantes

> Documenter au fur et à mesure les choix structurants.

- 2026-05-16 — Projet structuré en 4 pages HTML distinctes (hub + 3 marques).
- 2026-05-16 — Framework v1 construit avec contenu de démonstration premium
  (noms de produits/soins plausibles, prix indicatifs). À remplacer par le contenu réel.
- 2026-05-16 — Direction artistique : marbre noir animé, particules dorées, curseur doré,
  typographie Cormorant Garamond (titres) + Jost (corps).
- 2026-05-16 — Polices chargées via Google Fonts (seule ressource externe). Peut être
  inlinée plus tard si besoin d'une autonomie totale.
- 2026-05-16 — Sons générés par Web Audio API (son cristal + ambiance spa), zéro fichier externe.
- 2026-05-16 — Vidéo de présentation : embed YouTube (VIDEO_ID à remplacer dans
  luxury-skin-clinic.html).
- 2026-05-17 — Architecture EXACTE des 3 marques confirmée par Gloria et intégrée :
  navigation des 3 pages + arborescence `assets/images/` alignées (voir section
  « Architecture confirmée »).
- 2026-05-17 — INA LUXURY : carte produit enrichie activée (sélecteur de formats +
  accordéons Description / Actifs / Résultats / Ingrédients) pour les Beauty bars.
- 2026-05-17 — LUXURY SKIN CLINIC et COZY : filtres secondaires (préoccupation /
  besoin) retirés — navigation simplifiée aux prestations / catégories confirmées.

## À remplacer avant livraison

- Logos réels des 3 marques (actuellement monogrammes dorés)
- Photos produits/soins en base64 (actuellement placeholders dégradés élégants)
- Liens Instagram et TikTok réels dans index.html (actuellement `#`)
- VIDEO_ID de la vraie vidéo de présentation dans luxury-skin-clinic.html
- Textes, prix et listes produits validés par Gloria
- Photos avant/après réelles dans la galerie

## Liens

- Pages : `index.html` (hub), `ina-luxury.html`, `luxury-skin-clinic.html`, `cozy.html`
- Assets : `assets/`
- Infos client détaillées : `assets/docs/gloria-infos.md`
- URL en ligne : —
