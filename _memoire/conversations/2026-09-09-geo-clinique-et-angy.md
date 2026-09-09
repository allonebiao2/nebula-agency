# 2026-09-09 — GEO : se faire citer par les IA (Luxury Club 229 + Angy Art)

> Demande de Mongazi : « améliore le GEO aussi ». Skill `ai-seo` invoqué.
> GEO / AEO / LLMO : être **cité** dans une réponse d'IA, pas seulement classé
> dans un moteur.

---

## 0. La porte d'abord — sinon rien ne sert

Le skill met ce contrôle en quatrième position ; le dépôt en fait le premier,
parce que **Cloudflare bloque les robots d'IA par défaut** et que le réglage
est introuvable dans le tableau de bord (leçon `ai-seo` du 2026-08-02).

**Mesuré aujourd'hui**, en se présentant comme chacun d'eux :

| Robot | luxuryclub229.com | angy-art.pages.dev |
|---|---|---|
| GPTBot | **200** | **200** |
| ClaudeBot | **200** | **200** |
| PerplexityBot | **200** | **200** |
| Googlebot | **200** | **200** |

La porte est ouverte. Le `robots.txt` de la clinique **les nomme désormais
un par un** (celui d'Angy le faisait déjà) : un `Allow: /` générique suffit
techniquement, mais nommer les robots rend l'intention lisible le jour où
quelqu'un reprend le fichier.

---

## 1. La clinique : ce qui manquait le plus était une FAQ

Une IA ne cite pas une page, elle en extrait **un passage**. Le format le plus
extractible est une question posée comme on la pose, suivie d'une réponse qui
tient debout toute seule. La clinique n'en avait **aucune**.

**Huit questions**, chacune en 40-60 mots : jours et horaires · comment
réserver · combien coûte un soin · qui réalise les soins · annuler ou reporter
· faut-il une consultation avant un peeling · la différence entre les deux
consultations · peut-on venir accompagnée.

⛔ **Chaque réponse vient de la page.** Les jours, l'acompte, le délai de 24 h,
la tolérance de 5 minutes, le nombre d'accompagnateurs, la préparation du
peeling, les durées de suivi : tout était déjà écrit dans le règlement, le
bandeau ou les fiches.

### ⚠️ Une phrase inventée, attrapée avant publication

Mon premier jet écrivait : *« L'acompte de 5 100 FCFA se déduit du montant du
soin le jour du rendez-vous. »* **Ce n'est écrit nulle part.** Le site dit que
l'acompte *valide le créneau* et qu'il *n'est pas remboursable*, jamais qu'il
se déduit. C'était une condition commerciale inventée que la maison aurait dû
tenir. Remplacée par ce que la page dit vraiment.

*Une FAQ qui invente est pire qu'une FAQ absente.*

### ⚠️ Le `FAQPage` est LU dans les questions visibles

`_outils/_jsonld.py` relève les `<summary>`/`<p>` de la section et en fait le
balisage. Il ne recopie rien. Un `FAQPage` déclaré sans question à l'écran est
un balisage qui ment — défaut trouvé chez Hillary le 2026-08-16 — et **un
contrôle compare maintenant les deux côtés** : 8 visibles, 8 balisées, aucune
absente.

---

## 2. Les fichiers que lisent les machines

Le skill est explicite : un agent qui compare des prestations pour quelqu'un
**ne rend pas une page, il lit un fichier**. Un tarif enfermé dans du
JavaScript ou derrière un « nous consulter » sort des comparaisons.

`_outils/_llms.py` produit **deux fichiers, lus dans les pages** :

- **`/tarifs.md`** — les 11 soins, leurs prix, leurs descriptions, plus les
  conditions (qui, quand, acompte, comment réserver). 2,7 Ko.
- **`/llms.txt`** — la maison en dix lignes, ses trois univers, les 8 questions,
  et une section **« ce que ce site ne dit pas »** : pas d'adresse de rue, pas
  d'avis, pas de note. 4,1 Ko.

⚠️ **Rien n'est recopié.** Gloria change un prix dans la page, on relance la
commande, les deux fichiers suivent. Un prix recopié est une deuxième vérité.

⚠️ **Un piège de lecture** : le champ `d:` d'une fiche est sur la **ligne
suivante** du tableau `SERVICES`. Une expression bornée à la ligne courante ne
le voyait pas, et les descriptions manquaient — or c'est la description qui
rend une ligne citable.

---

## 3. Angy Art : le llms.txt qui aurait pu tout défaire

Angélique a retiré ses prix **le 5 septembre**. Écrire un `llms.txt` en
reprenant machinalement le modèle de la clinique aurait **remis ses prix en
ligne par la porte que personne ne regarde**.

Son `llms.txt` porte donc : qui elle est, sa phrase, ses **six œuvres avec
technique, palette et dimensions**, ce qu'on peut lui demander, ses quatre
questions fréquentes, et la mention que **le prix est communiqué sur demande**.
⛔ **Zéro FCFA dans le fichier**, et un contrôle le vérifie.

Il porte aussi l'honnêteté du site : trois photographies sont des **mises en
situation** (les masques sont d'elle, les intérieurs sont des rendus). Une IA
qui lit ce fichier ne peut pas se tromper là-dessus.

⚠️ **`_dist.py` liste ses fichiers un par un** : sans l'y ajouter, `llms.txt`
serait resté sur le disque sans jamais partir en ligne, et **rien ne l'aurait
signalé** (même famille que « un fichier livré n'est pas un fichier affiché »).

---

## 4. Les contrôles

| Suite | Avant | Après |
|---|---|---|
| clinique `_outils/_qc.py` | 136 | **147** |
| Angy `_qc.py` | 220 | **224** |

Les onze contrôles neufs de la clinique : la FAQ affiche au moins 6 questions ·
**chaque question balisée est visible** · autant de balisées que de visibles ·
`llms.txt` et `tarifs.md` existent · **tous les prix du catalogue sont dans
`tarifs.md`** · `tarifs.md` porte les conditions · le `robots.txt` nomme les
quatre robots et ne bloque personne.

Chez Angy : `llms.txt` existe · **aucun prix dedans** · les six œuvres y sont ·
il dit ce que le site ne dit pas.

⚠️ Un contrôle a planté à l'écriture : `io` n'est pas importé dans le `_qc.py`
d'Angy. Un contrôle qui meurt en s'exécutant ne protège rien.

---

## 5. Ce qui n'a pas été fait, et pourquoi

- ⏳ **La présence chez les tiers** est le levier le plus fort du skill (une
  marque est citée **6,5 fois plus** via un tiers que via son propre domaine) :
  fiche Google Business, annuaires béninois, Wikipédia. **Rien de tout cela ne
  se fait d'ici** — il faut les comptes de Gloria et d'Angélique.
- ⏳ **Le suivi de citation** (est-ce qu'une IA nous cite aujourd'hui ?) demande
  de poser les vraies questions dans ChatGPT, Perplexity et Google. À faire à
  la main, une fois par mois, sur une vingtaine de requêtes.
- ⛔ **Aucune statistique inventée.** Le skill donne +37 % de citations aux
  contenus chiffrés : la clinique n'a aucun chiffre vérifiable à publier
  (nombre de clientes, résultats), et en fabriquer un serait pire que de s'en
  passer.
