# Modèles IA par tâche

Règle validée (Mongazi, 2026-06) — voir aussi la mémoire `feedback_modeles-vendora`.

| Tâche | Modèle | Pourquoi |
|---|---|---|
| Réponses du vendeur aux clients | **Sonnet** (`claude-sonnet-4-6`) | vente = revenu → qualité ; Opus inutile/cher, Haiku trop léger |
| Ordres commerçant (« piloter ») | **Sonnet** | raisonnement fiable |
| Rédaction (emails, copies, social, coach) | **Sonnet** | qualité/coût optimal |
| Lourd créatif : visuels, images, **back-office luxueux** mobile, raisonnement CEO | **Opus** (`claude-opus-4-8`) | rare, fort enjeu |
| Transcription vocale | Groq Whisper | gratuit |

**Jamais Opus sur les réponses client.** Sonnet > Haiku pour vendre.

## Où c'est réglé
- `boutique-ia/config.py` : `claude_model`, `manager_model`, `writer_model` = Sonnet ; `builder_model` = Opus.
- ⚠️ **Les variables d'env Railway écrasent le code** : `CLAUDE_MODEL` doit aussi valoir `claude-sonnet-4-6` (sinon Haiku persiste en prod). Posé (staged) le 2026-06-10.
- 🔜 Objectif : panneau cockpit pour **ajuster modèle + effort par tâche/niveau** (voir [[evolution]]).

## Coût
Sonnet ≈ plusieurs × Haiku/message, mitigé par le cache du prompt + réponses courtes. Négligeable sans volume ; à surveiller au volume (budget Anthropic, pas de CB). Réversible en 1 variable.
