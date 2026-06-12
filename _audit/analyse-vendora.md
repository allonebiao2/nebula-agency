# Analyse complète de Vendora — audit technique & produit

> NEBULA Agency · Cotonou · juin 2026 · audit interne du code `boutique-ia/` (≈ 17 300 lignes)
> Repères de gravité : 🔴 critique · 🟠 important · 🟡 mineur · 🟢 force

---

## Résumé exécutif

**Verdict global : produit solide, bien architecturé, déjà très complet. Note ≈ 8/10.**
La majorité de la complexité dure (multi-tenant, gating, grounding anti-hallucination,
résilience) est bien traitée. Les vrais chantiers sont **le coût IA** (cache mal exploité,
pas de routage de modèle intelligent) et **l'observabilité** (on ne mesure pas ce qui coûte).
Aucun défaut bloquant ; ce sont des optimisations de marge et de robustesse, pas des
réécritures.

**Top 3 forces** : séparation des rôles (vendeur / manager / assistant / capacités) ·
discipline de grounding (zéro chiffre inventé) · sécurité du gating (jamais confiance au
navigateur).

**Top 3 chantiers** : ① cache de prompt cassé sur les assistants (coût) · ② pas de routage
Haiku/Sonnet par message (coût) · ③ aucune mesure du cache ni du coût par boutique (pilotage à l'aveugle).

---

## 1. Architecture — la fondation est saine 🟢

Le code est découpé proprement, chaque cerveau a un rôle unique et un fichier dédié :

| Module | Rôle | Interlocuteur |
|---|---|---|
| `core/brain.py` | **Le VENDEUR** — vend, prend commande, encaisse | le CLIENT |
| `core/manager.py` | **Le GESTIONNAIRE** — exécute les ordres (ajoute produit…) | la PATRONNE |
| `core/assistant.py` | **Le COPILOTE** — répond, gère caisse/stock/CRM, vision | la PATRONNE + Mongazi |
| `core/capabilities.py` | **La SOURCE DE VÉRITÉ** — qui a droit à quoi (gating) | tout le code |
| `core/model_config.py` | Choix modèle + effort par tâche, pilotable du cockpit | Mongazi |

C'est la bonne façon de faire. Un nouveau développeur comprend le système en lisant ces 5
fichiers. Le reste (`learning`, `strategist`, `experiment`, `followup`, `prospecting`,
`inbox`, `social`, `coach`, `collective`) sont des satellites bien isolés.

---

## 2. Forces détaillées 🟢

1. **Discipline de grounding (excellent).** Tous les chiffres (ventes, commandes, stock,
   caisse) passent par un outil qui lit la vraie base, préfixé `DONNÉES RÉELLES —`. Le
   modèle met en forme, n'invente jamais. C'est LA garantie de confiance — exactement ce
   que tu exiges. (`assistant.py`, tous les helpers.)

2. **Sécurité du gating côté serveur.** `capabilities.sanitize_selection()` re-filtre
   tout choix utilisateur selon le forfait AVANT enregistrement — le navigateur n'est
   jamais cru. Un client malin ne peut pas s'offrir Empire en bidouillant la page.
   (`capabilities.py:217`.)

3. **Repli sans régression.** Les anciennes boutiques (colonne `enabled_capabilities`
   vide) retombent sur les anciens interrupteurs (`_legacy_caps`) → activer le nouveau
   système ne casse personne. (`capabilities.py:168`.)

4. **Résilience.** `assistant.converse()` ne lève JAMAIS : en cas de souci, la patronne
   reçoit toujours une réponse. Try/except + repli partout (envoi photo, RDV, paiement…).
   Le `_fallback_after_order()` rattrape même un vendeur muet après une commande.

5. **Vérrou d'identité robuste.** `is_owner()` compare les **8 derniers chiffres** du
   numéro → survit aux formats +229 / 0… / espaces, gère plusieurs numéros patron.
   Défaut sûr : pas de numéro → jamais owner (on reste en mode vendeur). (`assistant.py:73`.)

6. **Soft cap (jamais couper la vente).** Quand le quota de conversations est dépassé,
   l'agent CONTINUE de vendre ; le quota sert à *nudger* vers la recharge/l'upgrade, pas
   à brider. Bonne décision produit. (`assistant.usage_view`, `PLAN_CONV_INCLUDED`.)

7. **Conformité Meta intégrée.** Les rappels d'agenda ne partent QUE dans la fenêtre
   WhatsApp 24 h (message de service = gratuit + conforme). (`assistant.run_assistant_reminders:1060`.)

8. **Réglage à chaud.** Modèle + effort par tâche changeables depuis le cockpit sans
   redéploiement, avec cache TTL et repli sur `config.py`. (`model_config.py`.)

---

## 3. Faiblesses & erreurs internes (priorisées)

### 🔴 F1 — Le cache de prompt est saboté par l'horloge (coût)

**Constat (vérifié).** L'assistant patronne et l'assistant fondateur injectent la date et
l'heure **à la minute** À L'INTÉRIEUR du bloc système mis en cache :

```python
# core/assistant.py:820  et  :1211
date_fr = f"...{now:%Hh%M}"          # ← change CHAQUE minute
# ... puis ce texte est placé dans le bloc avec cache_control: ephemeral
```

Or le cache de prompt d'Anthropic est un **préfixe exact** : un seul octet qui change
invalide tout le cache. Comme l'heure change chaque minute, le gros préfixe (toutes les
instructions du copilote) est **ré-écrit à plein tarif à presque chaque message** — la
lecture en cache (à 0,1× du prix) ne se déclenche quasi jamais. `core/support.py:80` a le
même défaut.

**Impact.** Le copilote (« remplace ChatGPT », usage quotidien intense par la patronne)
paie l'entrée plein pot. C'est le poste où le cache rapporterait le plus, et il est neutralisé.
Bonne nouvelle : le **vendeur client** (`brain.py`, le plus gros volume) n'a PAS de
timestamp dans son système → son cache, lui, fonctionne.

**Correction.** Sortir la ligne date/heure du bloc caché : deux blocs système, le stable
(caché) puis un petit bloc volatil (non caché), placé après le point de cache. Patron
recommandé par Anthropic. Fix bas risque, fort gain. *(diff prêt — voir §5.)*

---

### 🔴 F2 — Pas de routage de modèle par message (coût)

**Constat (vérifié).** Les 4 appels du vendeur utilisent tous `model_for("vendeur")` — **un
seul modèle pour TOUS les messages** (salutation, question simple, négociation, clôture).
Le « Haiku pour le simple, Sonnet pour vendre » n'est pas implémenté : c'est un réglage
global tout-ou-rien dans le cockpit.

**Impact.** Soit tu mets Sonnet partout (qualité max, coût max), soit Haiku partout
(coût bas, mais moins bon pour conclure). Tu ne peux pas avoir les deux. C'est le levier
n°1 d'économie de la présentation coûts, et il dort.

**Correction.** Ajouter un routage léger : Haiku par défaut, bascule Sonnet quand le
message porte un signal d'achat/négociation/objection (mots-clés + longueur + présence
d'un panier en cours), ou systématiquement sur le tour qui suit `enregistrer_commande`.
Gain attendu : coût/conversation ÷ 2 à ÷ 3 sans perte de taux de conversion.

---

### 🟠 F3 — Aucune mesure du cache ni du coût (pilotage à l'aveugle)

**Constat (vérifié).** `cache_control` est posé dans 6 fichiers, mais **0** lecture de
`usage.cache_read_input_tokens` / `cache_creation_input_tokens` dans tout le code. On ne
sait donc PAS si le cache marche (c'est pour ça que F1 est passé inaperçu), ni combien
coûte chaque boutique.

**Impact.** Impossible de répondre à « quelle boutique me coûte le plus », « le cache
tourne-t-il », « Démarrage est-il rentable pour CETTE boutique ». Tu pilotes la marge sans
tableau de bord.

**Correction.** Un petit wrapper autour de `client.messages.create` qui logge tokens
(entrée / sortie / cache_read / cache_creation) + coût estimé, par tâche et par boutique,
dans une table `bia_usage`. Onglet cockpit « Coûts ». C'est ce qui transforme la
présentation coûts en pilotage réel.

---

### 🟠 F4 — Pas d'idempotence sur l'enregistrement de commande/paiement

**Constat.** `enregistrer_commande` / `enregistrer_paiement` ne sont garde-fous QUE par le
prompt (« une seule fois par commande »). Aucun verrou côté code. Si le modèle rappelle
l'outil (ça arrive), tu as 2 commandes + 2 alertes pour le même achat.

**Impact.** Doublons de commandes/alertes occasionnels → confusion patronne, stats
faussées. Faible fréquence mais réel.

**Correction.** Clé d'idempotence par conversation+contenu (hash articles+total) sur une
courte fenêtre, ou drapeau « commande déjà prise dans ce tour ». Quelques lignes dans le
callback `on_order`.

---

### 🟠 F5 — Seuil de cache fragile si passage à Haiku

**Constat.** Le minimum cacheable est de 2 048 tokens sur Sonnet 4.6 mais **4 096 sur
Haiku 4.5**. Si F2 fait basculer le vendeur sur Haiku, une boutique au petit catalogue peut
passer SOUS le seuil → le système ne se met plus en cache du tout (silencieusement).

**Impact.** Optimisation F2 partiellement annulée pour les petites boutiques.

**Correction.** À traiter avec F2/F3 : mesurer la taille réelle du préfixe, et garder Sonnet
(qui cache dès 2 048) sur les tours « vente » de toute façon. Le routage F2 résout ça
naturellement.

---

### 🟡 F6 — Troncature de capacités par ordre de stockage

**Constat.** En cas de downgrade de forfait, `effective_capabilities` garde les `N`
premières capacités **dans l'ordre stocké** (`active[:lim]`), pas les plus utiles.
(`capabilities.py:199`.)

**Impact.** Une boutique rétrogradée pourrait perdre sa capacité la plus rentable et garder
une moins utile. Rare, faible impact.

**Correction.** Trier par priorité métier (réutiliser `CATEGORY_RECO`) avant de tronquer,
ou notifier la patronne pour qu'elle choisisse.

---

### 🟡 F7 — Effort « max » plafonné, base de tokens basse

**Constat.** `tokens_for` borne à 4 096 et le vendeur part d'une base de 500 (× 1,8 en
« max » = 900). Sur une négociation longue ou une liste, la réponse peut être coupée.
(`model_config.py:83`, `brain.py:585`.)

**Impact.** Réponses tronquées rares sur les cas longs. Mineur.

**Correction.** Base un peu plus haute pour le vendeur (700–800) et garder le plafond.

---

### 🟡 F8 — Dette de taille sur `server.py` et `db/client.py`

**Constat.** `server.py` = 3 352 lignes, `db/client.py` = 2 089 lignes. Tout fonctionne,
mais ces deux fichiers concentrent énormément de routes/fonctions.

**Impact.** Vitesse d'évolution future : trouver/modifier devient plus lent à mesure que ça
grossit. Pas un bug, une dette.

**Correction (plus tard).** Découper `server.py` par domaine (routes admin / boutique /
webhooks / API) quand tu auras le temps. Pas urgent.

---

## 4. Ce qui est SÛR (vérifié, rien à corriger) 🟢

- **Clés API** : lues depuis `.env` / environnement, jamais en dur, jamais côté client. ✅
- **Base** : Supabase (Postgres), pas de SQLite mono-fichier côté Vendora → multi-tenant OK
  (le SQLite, c'est NEXO, un autre produit). ✅
- **Ordre des outils déterministe** dans le vendeur (ORDER, ESCALATE, PAYMENT, +SHOW, +RDV)
  → bon pour le cache (les outils sont rendus avant le système). ✅
- **Historique** correctement normalisé (commence toujours par un message `user`). ✅

---

## 5. Plan de correction priorisé (par vagues)

**Vague 1 — coût (gros gain, bas risque) : ✅ CODÉE (2026-06-11), en attente de déploiement + migration.**
- [x] **F1** — horloge sortie du bloc caché → 2e bloc système non caché (assistant patronne `reply`, fondateur `admin_reply`, support `support_reply`). Aucun changement de comportement.
- [x] **F3** — module `core/usage.py` + `bia_usage` (schema) + `record_usage`/`usage_summary` (db) ; télémétrie branchée sur vendeur (brain), copilote+fondateur (assistant), gestion (manager), support. Donne coût (USD+FCFA) + **taux de cache** par tâche/boutique. ⚠️ nécessite la migration `bia_usage` pour enregistrer (sinon no-op silencieux).
- [x] **F2** — `model_config.model_for_vendeur()` : Haiku par défaut, Sonnet/Opus configuré dès signal d'achat / négociation / conversation engagée. Interrupteur cockpit `vendeur_smart_routing` (défaut ON). Branché dans `brain.reply`. Testé hors-ligne ✅.

**Suite F3 — ✅ onglet « Coûts » du cockpit (2026-06-11)** : lit `usage_summary()`, affiche coût FCFA+USD, **taux de cache** et ventilation par fonction. Section `#sec-couts` dans `admin.html`.

**Vague 2 — robustesse :**
- [x] **F4** — anti-doublon dans un tour du vendeur (commande / paiement / RDV). Testé.
- [ ] **F5/F7** — réglage seuils tokens après F2 (à faire si on observe des coupures).

**Vague 3 — dette (quand le temps le permet) :**
- [x] **F6** — tri des capacités par priorité métier avant troncature (downgrade). Testé.
- [ ] **F8** — découpage de `server.py` — **reporté** (gros refactor, faible ROI tant que ça tient).

---

## 6. Verdict

Vendora n'est pas un prototype : c'est une vraie plateforme, propre, résiliente, conforme,
avec une discipline anti-hallucination rare. **Le produit n'est pas le problème — la marge
et la mesure le sont.** Les corrections de la Vague 1 protègent directement ta rentabilité
(le thème de la présentation coûts) et se font sans risque pour les boutiques en place.

La priorité business reste inchangée : **des clients payants** > des features. Ces
corrections rendent juste chaque client plus rentable et chaque décision plus mesurable.
