# Techniques n8n maîtrisées

> Workflows et patterns n8n qui marchent dans le contexte NEBULA.
> Pour la connaissance générale n8n, voir aussi `_knowledge/n8n-workflows.md`.

---

## Format

```
## Titre du workflow / pattern

**Cas d'usage** : ...
**Schéma** : enchaînement des nodes
**Pièges** : ...
**Export JSON** : (ou lien vers le workflow)
```

---

## Patterns à documenter

### Chatbot WhatsApp avec mémoire (Twilio + Groq + Supabase)

**Cas d'usage** : Répondre automatiquement aux messages WhatsApp d'un client final tout en gardant l'historique.

**Schéma**
```
Webhook Twilio (in) 
  → Get conversation from Supabase (by numéro)
  → Construire prompt système + historique
  → LLM (Groq llama-3.3-70b ; fallback Claude)
  → Save message + réponse to Supabase
  → Twilio (out)
  → (Error Trigger → notif WhatsApp Mongazi)
```

**Pièges**
- Twilio timeout webhook ~15s → répondre vite, sortir tôt si traitement long
- Rate limits Groq → vrai fallback Claude, pas juste un "if"
- RLS Supabase à bien penser sur la table conversations

**À faire** : exporter le JSON d'un workflow réel pour le standardiser.

---

### Capture lead vitrine → onboarding auto

> À documenter quand mis en place.

---

### Relance client automatisée

> À documenter quand mise en place.
