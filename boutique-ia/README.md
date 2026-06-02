# Boutique IA — by NEBULA

**Produit digital self-service** : un commerçant s'inscrit sur une page web, décrit
sa boutique et ses produits, paie par Mobile Money, et reçoit un **vendeur IA WhatsApp**
qui répond à ses clients, prend les commandes et le prévient à chaque vente.

> Objectif : un SaaS utilisable par n'importe quel commerçant, partout. Récurrent, scalable.

## Les 4 étages du produit

1. **Inscription** (CE QU'ON CONSTRUIT EN PREMIER) — page web publique : fiche complète + paiement MoMo.
2. **Cerveau IA** — un seul code multi-boutiques ; chaque fiche devient un vendeur IA personnalisé.
3. **Vente WhatsApp** — l'IA vend, encaisse (MoMo manuel), prévient le patron.
4. **Tableau de bord admin** — Mongazi voit toutes les boutiques, les paiements, les ventes.

## État actuel — ÉTAGE 1 (Vague 1)

- [x] Schéma base de données multi-boutiques (`db/schema.sql`)
- [x] Page d'inscription (fiche complète) — `web/templates/onboarding.html`
- [x] Enregistrement de la boutique + produits dans Supabase
- [x] Écran « Activez par Mobile Money »
- [x] Alerte Telegram à Mongazi à chaque nouvelle inscription
- [ ] Étage 2 : cerveau IA WhatsApp (Vague 2)
- [ ] Étage 3 : vente + paiement (Vague 3)
- [ ] Étage 4 : tableau de bord admin (Vague 4)

## Lancer en local

```bash
cd boutique-ia
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env   # puis remplir les valeurs
uvicorn web.server:app --reload --port 8010
```

Puis ouvrir http://localhost:8010/

## Base de données

Exécuter `db/schema.sql` dans l'éditeur SQL Supabase (une seule fois).
On réutilise le même projet Supabase que NOVA (tables préfixées `bia_`).
