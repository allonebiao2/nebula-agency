# Versions — historique de travail NEBULA

> Photographie de NEBULA à différents moments. Permet de voir le chemin parcouru.
> Mise à jour : à chaque évolution structurante (nouvelle marque, refonte process, nouveau pack, etc.).

---

## v0.2 — 2026-05-14 — Intégration FedaPay + pricing récurrent

**État**
- FedaPay adopté comme provider de paiement standard (Mobile Money + cartes)
- Sécurité secrets : `.env` ignoré par git, `.env.example` commité comme template
- Vitrine `nebula_agency_v8.html` refondue avec arguments Mobile Money + badge sur les cards
- Nouveau pricing : Vitrine 70k setup + 10k/mois · Catalogue 50k setup + 10k/mois
- Workflow versioning : un seul fichier vitrine actif à la fois (v7 supprimé)

**Différenciation NEBULA**
- Vitrines qui **encaissent**, pas juste qui montrent (Mobile Money intégré)
- Abonnement mensuel = modifications illimitées 24h/24 (argument anti-friction)
- 5 arguments vente : paiement direct, 24h/24, zéro app, WhatsApp auto, livraison 48h

**Outils**
- FedaPay (paiement) + MyFeda (app mobile)
- `.env` local + `.env.example` commité
- KARABA = nouvelle direction marketing NEBULA Agency (bio TikTok refondue)

**À faire ensuite**
- Attendre validation compte FedaPay (resoumission avec adresse + description corrigées)
- Intégrer FedaPay Inline JS dans v8 dès validation
- Google Docs template pour catalogue de la nouvelle cliente
- Migrer les vitrines clients existantes vers le nouveau modèle d'abonnement

---

## v0.1 — 2026-05-11 — Mise en place de la mémoire

**État**
- Repo `nebula-agency` structuré : `clients/`, `_memoire/`, `_templates/`, `_knowledge/`
- 3 clients référencés : Grain d'Esthétique (livré), Little Sun Pearls (attente photos), WECS (en cours)
- Stack figée : HTML/CSS inline + base64, n8n VPS, Twilio, Supabase, Netlify
- Marques connues : NEBULA Agency, AXIO IA, KARABA Finance

**Différenciation NEBULA**
- Vitrines premium accessibles + couche IA
- Marché : WAOF (Afrique de l'Ouest francophone)

**Outils**
- Claude Code comme assistant principal
- GitHub `allonebiao2`

**À faire ensuite**
- Documenter SOFIA précisément
- Constituer la bibliothèque de prompts efficaces
- Finir WECS, débloquer Little Sun Pearls (photos)

---

## Modèle d'entrée

```
## vX.Y — YYYY-MM-DD — Titre

**État**
- ...

**Différenciation NEBULA**
- ...

**Outils**
- ...

**À faire ensuite**
- ...
```
