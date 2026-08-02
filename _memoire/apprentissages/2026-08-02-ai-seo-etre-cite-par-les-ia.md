# 2026-08-02 — Être cité par les IA : ce qui marche, et le piège Cloudflare

## Le piège à vérifier en premier, sur CHAQUE client

**Cloudflare bloque les robots des IA par défaut depuis le 1er juillet 2025** sur tout
nouveau domaine. Ce n'est pas un réglage qu'on a posé : ça arrive tout seul, en silence.

Deux blocages distincts, à tester séparément :

```bash
# 1. le pare-feu renvoie-t-il 403 aux robots IA ?
curl -sL -o /dev/null -w "%{http_code}\n" \
  -A "Mozilla/5.0 (compatible; GPTBot/1.1; +https://openai.com/gptbot)" https://LEDOMAINE/

# 2. le robots.txt servi est-il le nôtre, ou celui de Cloudflare ?
curl -sL https://LEDOMAINE/robots.txt | grep -c "Cloudflare Managed"
```

| Résultat | Signification |
|---|---|
| 403 sur le test 1 | règle WAF « Block AI bots » active : **aucune IA ne peut lire le site** |
| ≥ 1 sur le test 2 | Cloudflare impose son `robots.txt`, **le nôtre n'est pas servi** |

**Le correctif n'est pas dans le code.** Dashboard Cloudflare → domaine →
**Sécurité → Bots** → désactiver « AI Scrapers and Crawlers » et « Manage robots.txt ».
Un jeton API limité à Pages ne peut pas le faire : il faut les droits zone, ou le dashboard.

**Conséquence pratique : déployer un `robots.txt` ne sert à rien tant que la case n'est pas
décochée.** Vérifier après coup ce qui est réellement servi, pas ce qu'on a envoyé.

## Ce qui augmente vraiment les citations

Mesures de l'étude GEO (Princeton, KDD 2024), classées par gain :

| Méthode | Gain |
|---|---|
| Citer ses sources | +40 % |
| Donner des statistiques chiffrées | +37 % |
| Citer des experts nommés | +30 % |
| Ton d'autorité | +25 % |
| **Bourrer de mots-clés** | **−10 %** |

Pour un site encore peu établi, l'ajout de sources mesure jusqu'à **+115 %**.
La balise `<meta keywords>` n'est donc pas seulement inutile : elle **nuit**.

## La règle d'écriture qui change tout

**Une IA extrait des passages, pas des pages.** Chaque réponse doit tenir debout sortie de
son contexte. « Il coûte 50 000 F » ne s'extrait pas ; « un catalogue digital commandable
sur WhatsApp coûte 50 000 FCFA chez NEBULA Agency, à Cotonou » s'extrait tel quel.

Viser 40 à 60 mots par bloc de réponse. Les titres doivent être formulés **comme la
question posée**, pas comme un slogan : « Combien coûte un site web au Bénin ? » plutôt que
« Un tarif clair, sans surprise ».

## Les formats les plus cités

Comparatifs (~33 % des citations), guides de fond (~15 %), données originales (~12 %).
Un site d'une seule page, aussi beau soit-il, n'offre aucune prise.

## Les fichiers lisibles par une machine

- `robots.txt` — autoriser GPTBot, ChatGPT-User, OAI-SearchBot, ClaudeBot, PerplexityBot,
  Google-Extended. Refuser CCBot et Bytespider : entraînement pur, aucun retour pour nous.
- `llms.txt` — la fiche d'identité : ce qu'on fait, pour qui, les prix, les preuves.
- `pricing.md` — les tarifs en markdown. Les agents IA comparent les produits **avant**
  qu'un humain visite le site ; un prix derrière « contactez-nous » se fait éliminer.
- `sitemap.xml`.

⚠️ **Sur Cloudflare Pages, un fichier absent renvoie 200 avec la page d'accueil**, pas 404.
Un robot qui demande `/sitemap.xml` reçoit donc du HTML sans le savoir. Toujours vérifier
la **taille** de la réponse, pas seulement son code.

## Piège de mesure : les base64 faussent tous les grep

Sur une page qui embarque des images en base64, `grep -c "faq"` a compté 5 occurrences...
toutes dans les données d'images. Conclusion fausse : « il y a une FAQ ». Il n'y en avait
aucune. **Neutraliser les données avant de compter :**

```python
h = re.sub(r'data:[^"\')]{200,}', '[DATA]', h)
```
