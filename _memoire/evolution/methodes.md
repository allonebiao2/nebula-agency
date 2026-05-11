# Méthodes — comment NEBULA travaille

> Comment l'agence travaille **aujourd'hui**, et comment cette manière de faire évolue.
> Quand une méthode change durablement, la mettre à jour ici (et logger le pourquoi dans `_memoire/decisions.md`).

---

## Méthode actuelle (v1 — 2026-05)

### Prise de brief
- Canal principal : **WhatsApp**
- Reformuler le besoin par écrit dans `CONTEXT.md` avant de coder
- Valider la reformulation avec le client avant toute production

### Production d'une vitrine
1. Copier `_templates/CONTEXT-template.md` dans le dossier client
2. Collecter les assets dans `assets/images/`, `assets/videos/`, `assets/docs/`
3. Encoder les images en **base64** (jamais de lien externe)
4. Construire `vitrine.html` : HTML pur + CSS inline + JS vanilla si nécessaire
5. Tester sur mobile réel (réseau 4G africain)
6. Dérouler `_templates/checklist-livraison.md`
7. Envoyer preview au client (URL Netlify staging ou capture)
8. **Aucun push sans validation explicite de Mongazi**

### Automatisation IA
- n8n self-hosted (Hostinger VPS `72.61.103.56`)
- Conventions de nommage et structure : voir `_knowledge/n8n-workflows.md`
- LLM : Groq (vitesse) en premier, fallback Claude (qualité) si besoin

### Versioning
- Git local pour chaque modification
- Diff montré à Mongazi avant chaque commit
- Push GitHub `allonebiao2` uniquement après validation

---

## Choses qu'on essaie / qu'on teste

> _vide pour le moment._
> Quand une nouvelle méthode est testée, la noter ici avec **date de début** et **critère de réussite**.

---

## Méthodes abandonnées (et pourquoi)

> _vide pour le moment._
> Quand une méthode est retirée, la déplacer ici avec **date d'arrêt** et **raison**.
