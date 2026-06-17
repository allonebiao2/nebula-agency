# Analyse Vendora — produit · marché · conformité (juin 2026)

> NEBULA Agency · Cotonou · audit **complémentaire** à `_audit/analyse-vendora.md`
> (qui couvre la technique/coût, ≈ 8/10, F1–F4 corrigés). Ici : ce qui MANQUE et qui est
> ultra-important — vérifié dans le code + recherches web (Meta, loi béninoise, concurrents).
>
> Gravité : 🔴 existentiel · 🟠 fort levier · 🟡 robustesse · ✅ vérifié · ⚠️ à confirmer

---

## Résumé

Le **moteur** de Vendora est bon (grounding, gating, multi-tenant, résilience, coût maîtrisé).
Les vrais manques ne sont **pas** dans le code de l'agent : ils sont dans l'**architecture
WhatsApp**, la **conformité**, et quelques **briques business** (paiement, diffusions, analytics)
qui transforment un bon agent en plateforme qui scale.

**Top 3 manques ultra-importants :**
1. 🔴 Modèle « numéro WhatsApp partagé » → plafond de verre (branding, qualité, 250/j).
2. 🔴 Conformité données personnelles (Code du numérique Bénin / APDP) quasi absente.
3. 🔴 Pas d'opt-in / templates / compte officiel → pas de ré-engagement hors 24 h, pas de confiance.

**Top 3 leviers de revenu :** paiement en chat · diffusions/campagnes à la base clients ·
messages interactifs natifs WhatsApp.

---

## 🔴 1. Architecture WhatsApp — le numéro partagé est un plafond de verre

**Constat (✅ code + ✅ Meta).** Toutes les boutiques passent par **un seul numéro**
(`+229 62046155`, routing par code). Règle Meta : **1 numéro = 1 entreprise = 1 WABA/BSP**.

- **Branding cassé** — le client voit « Vendora », pas le nom de la boutique. Contredit la
  promesse « ton employé, pour ta boutique ».
- **Contagion de qualité** — depuis oct. 2025, limites et *quality rating* au niveau du
  *portefeuille* : les blocages des clients d'une boutique font chuter tout le monde.
- **Plafond d'envoi** — numéro non vérifié = **250 contacts/24 h** ; il faut la *Business
  Verification* pour 1 000 → 10 000 → illimité.

**Voie conforme (= ton moat) :** devenir **Meta Tech Provider** + **Embedded Signup** →
chaque boutique connecte **SON propre numéro** en ~5 min, brandé à son nom, qualité isolée
(modèle Wati/Zoko). ⚠️ Meta imposait l'enrôlement Tech Provider avant le 30/06/2025.

**Verdict :** numéro partagé OK pour le **pilote (5-10 boutiques)** ; **chantier n°1**
avant de scaler.

---

## 🔴 2. Conformité données personnelles (Bénin)

**Constat (✅ loi).** Code du numérique (**Loi 2017-20, Livre 5**) + autorité **APDP** active.
Vendora stocke numéros, noms, conversations, CRM, ardoise → données personnelles.

**Manque (⚠️ à confirmer) :**
- **DPA / contrat de sous-traitance** Vendora (sous-traitant) ↔ boutiques (responsables).
- **Consentement du client final** (WhatsApp / 1er message) + **rétention/suppression** des conversations.
- **Droits d'accès/suppression** outillés ; éventuelle **déclaration APDP**.

Base existante : `/confidentialite` + consentement à l'achat (côté marchand) — insuffisant
pour les clients finaux. **Risque légal + argument de confiance fort.**

---

## 🔴 3. Opt-in, templates, compte officiel

**Constat (✅ code + ✅ Meta).** Tarif **au message** depuis 01/07/2025 : réponses entrantes
dans la **fenêtre 24 h = gratuites** (✅ force de Vendora). Hors 24 h = **template approuvé,
payant**.

- Relances (`followup.py`) bien cadrées **6-22 h** ✅ → gratuites/conformes. **Mais** aucun
  ré-engagement après >22 h (pas de templates), aucun **opt-in** capturé.
- Pas de **Business Verification / compte officiel** → plafond 250/j + zéro badge de confiance.

---

## 🟠 4. Manques produit (vendre PLUS)

| # | Manque | Pourquoi | État |
|---|---|---|---|
| 1 | **Paiement intégré en chat** (lien FedaPay/MoMo + confirmation auto) | Flux actuel = client paie → envoie preuve → patronne valide à la main. Friction, abandons, travail manuel | ❌ FedaPay documenté (CLAUDE.md) mais **PAS branché** (0 occurrence code) |
| 2 | **Diffusions/campagnes à la base clients** (templates + opt-in) | Répétition d'achat = 1er levier de revenu + colle Vendora | ❌ absent (« campagnes » du code = prospection B2B) |
| 3 | **Messages interactifs natifs** (boutons, listes, catalogue cliquable) | Convertit mieux, plus pro | ❌ sortant = texte + image seulement (`whatsapp_meta.py`) |
| 4 | **Analytics revenu/funnel** marchand (où ça décroche, panier moyen, CLV, top CA) | Le Coach conseille mais ne mesure pas le revenu | ⚠️ KPIs basiques |

**Le n°1 (paiement en chat) est le plus rentable** : moins d'abandons, validation auto,
moins de charge patronne. Provider déjà choisi, juste pas câblé.

---

## 🟡 5. Robustesse & exploitation

- **Reprise humaine en direct** : pouvoir **mettre l'IA en pause** et reprendre à la main (⚠️ à confirmer). Indispensable confiance.
- **Anti-spam / rate-limit entrant** : un spam = coût tokens. ⚠️ Vérifier plafond/client.
- **Supervision « agent down »** : si le token Meta expire (≈24 h) ou webhook KO, **être alerté** — sinon boutique muette = churn.
- **Export/portabilité** clients/commandes : confiance (anti lock-in) + droit d'accès.

---

## ✅ Déjà solide (ne pas refaire)
Grounding, gating serveur, multi-tenant Supabase, résilience, relances 24 h, coût (cache +
routage Haiku/Sonnet + mesure). Le moteur est bon.

---

## Reco priorisée (priorité = 1ers clients payants)

**Maintenant (pilote) :**
1. **Paiement en chat (FedaPay/MoMo)** — plus gros gain conversion.
2. **Mini-DPA + consentement client** + politique de rétention — risque légal, faible coût.
3. **Alerting « agent down »** + **pause IA / reprise humaine**.

**Avant de scaler (>10-20 boutiques) :**
4. **Tech Provider Meta + Embedded Signup** (numéro propre/boutique) — moat + lève le 250/j.
5. **Diffusions/templates + opt-in** — rétention/répétition.

**Confort :** messages interactifs · analytics revenu · export données.

---

## Sources
- Meta — Pricing : https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing
- Meta — Messaging Limits : https://developers.facebook.com/docs/whatsapp/messaging-limits/
- Meta — Tech Provider / Solution Partner : https://developers.facebook.com/documentation/business-messaging/whatsapp/solution-providers/overview
- Meta — Embedded Signup (via Twilio Tech Provider guide) : https://www.twilio.com/docs/whatsapp/isv/tech-provider-program/integration-guide
- Code du numérique Bénin (Loi 2017-20) : https://www.afapdp.org/wp-content/uploads/2018/06/Benin-Loi-2017-20-Portant-code-du-numerique-en-Republique-du-Benin.pdf
- APDP Bénin (organisation/missions) : https://openloibenin.com/2025/03/29/lautorite-de-protection-des-donnees-a-caractere-personnel-organisation-et-missions-selon-le-titre-iii-du-livre-5-du-code-du-numerique-du-benin/
- Comparatif concurrents (Zoko/Wati/Interakt) : https://www.zoko.io/post/interakt-vs-wati-comparison
