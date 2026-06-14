# Vitrina — Cerveau (INDEX)

> Point d'entrée du cerveau de Vitrina. À lire en début de session. Brain **segmenté** (7 fichiers) + **maintenable** (convention de MAJ + journal en bas).

## Synthèse en 30 secondes
**Vitrina** = générateur automatique de vitrines pour micro-commerçants francophones (AO). Marque **AUTONOME & ANONYME** = machine de volume derrière la marque premium NEBULA (stratégie 2 marques). **LIVE : https://vitrina.nebula-agency.online**. Cœur : la cliente remplit → voit son site **en direct** (aperçu gratuit) → paie **MoMo** → en ligne en **5 min**.
**Vision long terme** : devenir l'**atelier digital self-service** de tout micro-commerçant francophone (vitrine → boutique → social → marque → RDV → CRM → paiement), multi-vertical, multi-pays AO.

## Carte des segments
1. [[01-identite-vision]] — ce que Vitrina **représente**, positionnement, **vision long terme**
2. [[02-produit-offre]] — produit actuel + offre + ce qu'il **proposera** (suite de modules)
3. [[03-marche-cible]] — marché, cibles, douleurs, concurrence
4. [[04-tech-architecture]] — architecture 3 couches, stack, déploiement/redeploy
5. [[05-operations]] — paiement, livraison, back-office, Telegram, sécurité, échéances
6. [[06-roadmap]] — feuille de route ordonnée
7. [[07-decisions-apprentissages]] — décisions datées + leçons (s'enrichit en continu)

## ⚠️ Garde-fous permanents
- **Anonymat** : ne jamais lier publiquement Vitrina à NEBULA/Mongazi (façade). Domaine `vitrina.nebula-agency.online` (anonymat partiel accepté).
- **Secrets** : uniquement dans `vitrina/.env` (gitignored). Jamais dans ce cerveau, jamais commités.

## 🔄 Convention de mise à jour (« se mettre à jour »)
- Nouvelle **décision** → [[07-decisions-apprentissages]] (avec la date).
- Nouvelle **feature / évolution d'offre** → [[02-produit-offre]] (+ [[06-roadmap]] si planifié).
- Changement **technique / déploiement** → [[04-tech-architecture]].
- Nouvelle **leçon** (ce qui marche / rate, chiffres réels) → [[07-decisions-apprentissages]].
- **Toujours** ajouter une ligne au **Journal** ci-dessous (date + 1 phrase).

## Journal du cerveau
- **2026-06-14** — Cerveau segmenté créé (index + 7 segments) + vision long terme + présentation PDF.
- **2026-06-13** — Vitrina déployé LIVE (Railway + Cloudflare Pages + DNS Hostinger) ; back-office sécurisé (login) ; commandes test nettoyées.
- **2026-06-12** — Conception : produit, packs, gating, paiement manuel + Telegram, email obligatoire.
