# Prouver qu'une publication est arrivée : les documents des partenaires (2026-09-11)

## Le principe

Le bureau des partenaires (Render + Supabase) ne lit pas ses PDF sur le disque :
`publier_documents()` les range **dans la base** (`naff.documents`, en base64),
**au démarrage du service**, et seulement pour les documents dont la date a
changé dans `DOCS_PARTENAIRES` (`nebula-affilies/server.py`). Il faut donc :

1. le PDF remplacé dans `nebula-affilies/assets/docs-partenaires/` ;
2. sa date changée dans `DOCS_PARTENAIRES` (sinon il n'est jamais relu) ;
3. **Render redéployé** (il ne le fait pas au push) ;
4. et la preuve : `python scripts/verif_documents.py`.

Le 2026-09-11, les étapes 1 et 2 avaient été faites trois fois en septembre,
la 3 jamais : la base portait les dix PDF du 3 août.

## Décider s'il faut bumper : comparer le TEXTE, pas les octets

Un PDF refabriqué change d'octets même quand son texte est identique (date de
fabrication, polices embarquées). On compare le texte :

```python
import io, re, unicodedata, pypdf

def mots(octets):
    r = pypdf.PdfReader(io.BytesIO(octets))
    t = unicodedata.normalize("NFKC", "\n".join(p.extract_text() or "" for p in r.pages))
    t = re.sub(r"-\s+", "-", t)        # coupures de ligne
    return t.split()
```

⚠️ **NFKC est obligatoire** : les PDF portent des ligatures (« ﬁlleul »,
« oﬀre »), et une recherche de « filleul » renvoie zéro sans elle.
⚠️ **Comparer contre un commit nommé** (`git show caa0748:chemin`), jamais
contre `main` quand une fusion tourne à côté : on compare alors `main` à
lui-même, et tout sort « identique ».
⚠️ `pypdf` n'était pas installé sur le PC : `python -m pip install pypdf`.

Mesuré ce jour-là : sur dix documents, cinq ne changeaient que par leur
étiquette (« Version 2026-08-02 » devenue « Version 1.0 · 2026-07-30 ») : pas
de bump, les partenaires gardent un document au texte identique. Le contrat,
lui, passait de 1.4 à 1.5 **sans** bump : c'est le seul qui aurait manqué.

## Déclencher Render et attendre

```text
POST https://api.render.com/v1/services/srv-d9nni7e7bikc73c9oksg/deploys   corps {}
GET  https://api.render.com/v1/services/srv-d9nni7e7bikc73c9oksg/deploys/<id>
     jusqu'à status = live (environ une minute)
```

Clé : `secrets/render.env`. Puis `/healthz` (200 sur le domaine et sur
l'origine `nebula-affilies.onrender.com`) et `python scripts/verif_documents.py`.
