# Log de Session — Nouveau client Saeir Thiam Bijouterie

## Date : 2026-06-22
## Sujet principal : Onboarding client #05 (fiche reçue via le site)

## Ce qu'on a fait
- Réception de la fiche de **Saeir THIAM — SAEIR THIAM BIJOUTERIE** (bijoux or/argent/sur-mesure, Cotonou) via le formulaire de `nebula-agency.online`. Commande **acceptée** par Mongazi.
- Création du dossier client **`clients/05-saeir-thiam-bijouterie/`** (+ `assets/images|videos|docs`).
- Rédaction du **`CONTEXT.md`** complet (contact, WhatsApp `2290197967671`, activité, brief, palette bleu/blanc, 6 options demandées, contenu à récupérer, checklist d'avancement).
- Ajout de la **ligne 05** dans le tableau « Clients actifs » de `CLAUDE.md`.
- **Enregistrement dans le back-office de PRODUCTION** (app `nebula-affilies`) via l'endpoint public `POST /api/site-lead` → lead `id=4`, `source='site'`, `affiliate_id=0` (`{"ok":true}`), puis login cockpit réel + passage en **En cours** (commande acceptée). **Aucun doublon** : c'est le **1er et seul lead réel de la prod** (base de lancement vide → l'auto-post du formulaire avait dû échouer/cold-start).

## Ce que j'ai appris / vérifié
- Le formulaire du site agence poste les clients directs vers **`nebula-affilies` `/api/site-lead`** (back-office des leads, table `leads`, `source='site'`). C'est CE back-office qu'il faut mettre à jour pour un client du site.
- La base **`affilies.db` locale est gitignorée** (`*.db`) et ne contient que des leads de test → **≠ la base de production** (volume Railway `NAFF_DATA_DIR`). Écrire dans le `.db` local ne change rien à la prod.
- Le mot de passe admin de prod est **personnalisé** (login par défaut `founder123` = 401) → pour piloter le cockpit en API il faudrait la vraie valeur (env Railway `NAFF_ADMIN_PASS`).
- L'auto-enregistrement du formulaire peut **échouer silencieusement** si Railway free dort au moment du submit (`.catch()` vide) → d'où l'intérêt de l'ajout manuel.

## Décisions prises
- Service « Plusieurs services / besoin de conseils » → mappé en **« Autre / à discuter »** dans le back-office (à préciser avec le client : Vitrine vs Catalogue).
- Numéro WhatsApp client **non câblé** dans une vitrine tant que non confirmé (règle absolue).

## À appliquer / prochaine étape
- ✅ Fait : lead en **En cours** dans le cockpit, dédoublonnage vérifié (1 seul lead).
- Récupérer sur WhatsApp : **logo** + **photos bijoux** (→ base64), **adresse** boutique (Google Maps), avis clients.
- Confirmer le **service final + devis**, puis démarrer la vitrine (mono-fichier HTML, base64, mobile-first, audio baseline mobile, palette bleu/blanc).

## Suite — « savoir quel service le client a pris » (déployé en prod)
Demande de Mongazi : voir clairement, par client, le service choisi.
- **Backend** (`nebula-affilies/server.py`) : nouvelle colonne `leads.service_raw` = **libellé EXACT** choisi (site = texte du formulaire ; affilié = label du service). `/api/site-lead` et `/api/lead` le stockent ; `admin_leads` l'expose ; **backfill** des anciens leads depuis le brief « Service : … » (borné au champ suivant car `clean()` supprime les retours ligne). Nouvel endpoint **`POST /api/admin/leads/{id}/service`** pour **fixer/confirmer** le service retenu (met à jour la clé service = base de commission + le libellé). Notif admin affiche le vrai service.
- **Cockpit** (`admin.html` + `app.css` + `app.js`) : chaque fiche client montre le service en évidence + « **Demandé par le client : …** » + **sélecteur « Service retenu »** (surtout utile pour « Plusieurs services / besoin de conseils »). Icône `tag` ajoutée.
- **Saeir (id=4)** : `service_raw = 'Plusieurs services / besoin de conseils'`, à fixer via le sélecteur après le conseil.
- **Déploiement** : commits `50707f8` + `26a4f53` poussés ; **CLI `railway redeploy` en timeout** (réseau) → déclenché via **GraphQL `serviceInstanceDeploy(latestCommit:true)`** (⚠️ sans `latestCommit:true` il redéploie l'ANCIEN commit figé). LIVE OK.

## Liens utiles
- Back-office : https://partenaires.nebula-agency.online (origine : https://nebula-affilies-production.up.railway.app)
- Dossier client : `clients/05-saeir-thiam-bijouterie/CONTEXT.md`
