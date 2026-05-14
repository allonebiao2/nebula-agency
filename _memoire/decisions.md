# Décisions — Nebula Agency

> Journal des décisions structurantes prises sur le projet.
> Chaque décision : date, contexte, choix, raison.

---

## Format

```
## YYYY-MM-DD — Titre court de la décision

- **Contexte** : pourquoi la question s'est posée
- **Décision** : ce qui a été choisi
- **Raison** : pourquoi ce choix
- **Alternatives écartées** : ce qu'on n'a pas pris, et pourquoi
- **Conséquences** : ce que ça implique pour la suite
```

---

## 2026-05-11 — Mise en place de la structure du repo

- **Contexte** : Plusieurs clients en parallèle, besoin d'organisation claire.
- **Décision** : Structure `clients/0X-nom/` + `_memoire/` + `_templates/`.
- **Raison** : Permettre à Claude de retrouver le contexte d'un client en un coup d'œil et capitaliser les apprentissages.
- **Alternatives écartées** : Un repo par client (trop dispersé pour un solo).
- **Conséquences** : Chaque nouveau client suit le même schéma, mémoire transverse centralisée.

---

## 2026-05-14 — Versioning fichiers vitrine : un seul fichier actif

- **Contexte** : Accumulation de fichiers `nebula_agency_vX.html` dans le repo crée de la confusion sur quel fichier est la version active.
- **Décision** : À chaque mise à jour d'un fichier versionné, supprimer l'ancien (`git rm`) avant de créer le nouveau. L'historique git suffit pour retrouver les versions antérieures.
- **Raison** : Repo propre, pas d'ambiguïté sur la version live, clients ne risquent pas d'être servis sur une ancienne version.
- **Alternatives écartées** : Garder tous les vX en parallèle (poubelle qui grossit), branches git par version (overkill pour un solo).
- **Conséquences** : Workflow appliqué aux vitrines `00-nebula-agency/` et `/clients/`. v7 supprimé, v8 devient version active.

---

## 2026-05-14 — Pricing récurrent : setup + 10k FCFA/mois

- **Contexte** : Maintenance, hébergement, modifications répétées des vitrines clients étaient inclus dans un prix one-shot — modèle non soutenable.
- **Décision** : Introduire un abonnement mensuel **10 000 FCFA/mois** en plus du setup pour les services Vitrine Digitale (70k setup) et Catalogue Digital (50k setup). Inclut : hébergement + sécurité + modifications illimitées 24h/24.
- **Raison** : Revenu récurrent prévisible, justifie le support continu, aligné sur la norme SaaS, retient les clients dans l'écosystème NEBULA.
- **Alternatives écartées** : Prix forfaitaire one-shot (épuisant à maintenir), facturation horaire pour chaque modification (friction).
- **Conséquences** : Argumentaire de vente axé sur "24h/24" et "modifications illimitées". Les vitrines déjà livrées (Jocelyne, Cédène, Abakar) restent sur l'ancien modèle ; nouveau modèle pour les prochains clients.

---

## 2026-05-14 — FedaPay devient le provider de paiement standard

- **Contexte** : Besoin d'un moyen de paiement intégré dans les vitrines pour transformer "vitrine de présentation" en "vitrine qui vend".
- **Décision** : Adopter FedaPay comme provider de paiement Mobile Money (Moov, MTN, Wave) + cartes pour toutes les vitrines NEBULA. Compte principal + sous-comptes par client.
- **Raison** : Provider local Afrique de l'Ouest, supporte tous les Mobile Money utilisés au Bénin, dashboard MyFeda, notifications natives, sous-comptes natifs pour facturation par client.
- **Alternatives écartées** : Stripe (pas adapté au Mobile Money local), CinetPay (pas testé), intégration manuelle Moov/MTN (trop de friction).
- **Conséquences** : Clé secrète `sk_live_*` jamais dans le HTML (uniquement `.env` local + n8n côté serveur). Clé publique `pk_live_*` utilisable dans les vitrines. Triple confirmation paiement : WhatsApp + MyFeda + Email.

---

<!-- Ajouter les nouvelles décisions au-dessus -->
