# Techniques IA — prompts et méthodes

> Méthodes d'usage des LLM (Claude, Gemini, Groq) qui marchent pour NEBULA.
> Différent de `_memoire/prompts-efficaces.md` (qui est une bibliothèque de prompts prêts à coller).
> Ici → **méta-techniques** : comment penser et structurer un prompt.

---

## Principes qui marchent

### 1. Donner un rôle clair
Ouvrir par "Tu es X, qui fait Y pour Z" → recadre immédiatement les réponses.

### 2. Contexte avant question
Mettre la mise en situation **avant** la demande. Le LLM "tient mieux" la consigne quand le contexte est posé d'abord.

### 3. Format de sortie explicite
Toujours dire à quoi doit ressembler la réponse (liste, tableau, JSON, paragraphe ≤ N mots).

### 4. Exemples > explications
1 ou 2 bons exemples valent un paragraphe de règles abstraites.

### 5. Contraintes négatives
Dire ce qu'on **ne veut pas** (ex: "pas d'introduction", "pas de blabla", "pas plus de 5 lignes") évite les ronds-de-jambe.

---

## Choix de modèle par tâche

| Tâche | Modèle préféré | Raison |
|---|---|---|
| Raisonnement long, code complexe | Claude | Meilleure rigueur |
| Réponse rapide chatbot WhatsApp | Groq llama-3.3-70b | Latence très basse |
| Génération de texte créatif | Claude / Gemini | Au feeling, tester les deux |
| Résumé / extraction structurée | Claude | Suit mieux les schémas |
| Vision (analyse image) | Gemini / Claude | Selon dispo |

---

## Pièges identifiés

- LLM hallucine plus quand on lui demande des **chiffres précis** sans source → soit donner la source, soit accepter une fourchette
- Prompt trop long → le LLM oublie le début. Mettre la consigne **finale** à la toute fin.
- Ne jamais coller des secrets / clés API dans un prompt envoyé à un LLM tiers

---

## À approfondir

- Caching de prompt (Claude API) pour réduire les coûts des workflows répétitifs
- Tool use / function calling pour les automatisations critiques
- Évaluation systématique : comparer 2 prompts sur 10 cas réels avant d'en figer un
