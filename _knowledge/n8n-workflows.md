# n8n — Workflows NEBULA

> Connaissances pratiques accumulées sur n8n dans le contexte NEBULA.

---

## Cas d'usage NEBULA

- **Chatbot WhatsApp avec mémoire** : Twilio → n8n → Groq/Claude → Supabase (historique)
- **Génération de devis** : formulaire → n8n → LLM → PDF / message WhatsApp
- **Relance client automatisée** : cron n8n → Twilio WhatsApp
- **Capture lead** : webhook → Supabase → message de bienvenue auto
- **Tableau de bord client** : agrégation données → notification WhatsApp périodique

## Conventions internes

- Nommer chaque workflow : `nebula-[client]-[fonction]`
  - Ex : `nebula-grain-esthetique-sofia`, `nebula-wecs-leadcapture`
- Un node **Error Trigger** par workflow critique → notification WhatsApp vers Mongazi
- **Sticky notes** en haut de chaque workflow pour expliquer le flux
- Variables sensibles → **Credentials n8n**, jamais en dur
- Tagger les workflows par client et par statut (`prod`, `staging`, `test`)

## Structure type d'un chatbot WhatsApp

```
1. Webhook Twilio inbound
2. Récupérer historique Supabase (par numéro)
3. Construire le prompt système + historique
4. Appel LLM (Groq pour vitesse, Claude pour qualité)
5. Sauver le message + la réponse dans Supabase
6. Renvoyer la réponse via Twilio
7. (option) Error Trigger → notif Mongazi
```

## Pièges connus

> À compléter au fil de l'expérience.

- Timeouts webhook Twilio : répondre vite (< 15s), sinon Twilio retry
- Rate limits Groq : prévoir un fallback Claude
- Supabase RLS : bien penser aux policies si on stocke les conversations

## Snippets utiles

> À compléter (Function nodes récurrents, expressions JSON, etc.).

## Hébergement n8n

- Hostinger VPS pour les instances NEBULA
- Backup régulier des workflows (export JSON)
