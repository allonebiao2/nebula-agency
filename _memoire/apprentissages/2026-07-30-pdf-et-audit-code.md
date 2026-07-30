# 2026-07-30 — Générer des PDF NEBULA + pièges d'audit de code

## Chaîne PDF sans outil système

Aucun `pandoc`, `wkhtmltopdf` ni `weasyprint` n'est installé. En revanche **Chromium est
disponible** et suffit :

```
Markdown  --(python-markdown)-->  HTML stylé  --(chrome --headless --print-to-pdf)-->  PDF
```

- Binaire : `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`
- Options : `--headless --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf=SORTIE file://SOURCE`
- `pip install markdown` fonctionne (proxy sortant configuré)
- Script de référence : `_documents/nebula-agency/vente/_build_pdf.py`

**Repère de taille :** un document de 20 pages avec tableaux et couverture pèse ~350 Ko.

## Trois pièges rencontrés

1. **`nl2br` casse les phrases.** L'extension `nl2br` de python-markdown transforme chaque
   retour à la ligne en `<br>`. Sur un document rédigé avec des retours à la ligne de confort
   (80 colonnes), les phrases se coupent au milieu. **Ne pas l'activer** pour de la prose.

2. **Une couverture sombre a besoin de `!important`.** La règle générale `h1{color:#0F1224}`
   écrase la couleur claire de la couverture et rend le titre invisible sur fond sombre.
   Poser `.cover h1{color:#EAEEF9 !important; border:0 !important}`.
   **Toujours vérifier par capture d'écran avant de générer une série.**

3. **`node --check` ment sur les blocs JSON-LD.** Extraire tous les `<script>` d'une page et
   les passer à `node --check` fait remonter une erreur sur `application/ld+json`, qui est du
   JSON, pas du JavaScript. **Comparer avec la version d'avant modification** avant de
   conclure à une régression.

## Méthode d'audit qui a payé

Avant de modifier un prix sur un site, vérifier la **cohérence des chaînes couplées** :
sur `nebula_agency_v9.html`, les valeurs de `setTier('...')` doivent correspondre exactement
aux `<option>` du formulaire. Un simple script qui compare les deux ensembles évite une
régression silencieuse du formulaire de commande.

Et vérifier **d'où vient réellement une donnée affichée** : `agency_brain()` de NOVA dérivait
son catalogue du dictionnaire `SERVICES`, qui contenait encore des offres retirées du site
(Fiche Google Maps, Avatar IA). NOVA citait donc au public des offres qui n'existaient plus.
**Un catalogue commercial doit être explicite, pas dérivé d'une structure technique
maintenue ailleurs.**
