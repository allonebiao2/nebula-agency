# 2026-09-11 · Rapatrier ce qui dormait, et publier ce qui devait l'être

> Session terminal, PC de Cotonou. Demande de Mongazi : « fais-les, déploie ce
> qu'il y a en mémoire, les modifications ».

## Ce que disait le parc avant de toucher à quoi que ce soit

`python scripts/verif_parc.py` : **14 sites identiques au dépôt**, Angy Art
compris (WETHU en ligne, `_verifier_en_ligne.py` : 12 verts). Un seul rouge,
**NEBULA Agency « EN RETARD »**, et c'était la sonde (voir plus bas).

Le vrai retard n'était pas sur un site : il était **dans la base des
partenaires**.

## ⛔ Les partenaires téléchargeaient encore les PDF du 3 août

Mesuré dans `naff.documents` : les dix documents portaient **« 2026-08-03 »**.
Dernier déploiement Render : **2026-08-04** (`fbf6938`). Depuis, trois
sessions avaient bumpé des versions dans `DOCS_PARTENAIRES` (le manuel et le
contrat les 2026-09-02/03, « le contrat v1.3 arrive vraiment jusqu'aux
partenaires », puis 03/06/01b ce matin) et **aucune n'avait redéployé le
service**. Le contrat servi aux partenaires était celui du 3 août (210 247 o).

⚠️ **Et la branche du matin avait son propre trou** : le commit du contrat 1.5
remplaçait le PDF sans changer sa date. `publier_documents()` ne relit un
fichier que si sa date change : sans le redéploiement en retard (qui faisait
passer la date de 08-03 à 09-03), la 1.5 serait restée invisible pour
toujours, et au prochain changement elle aurait porté l'étiquette de la 1.4.
Bumpée à **2026-09-11**.

Vérifié après déploiement (`dep-dahujerl550s73f21pag`, commit `9e28b91`,
live à 11:45 UTC) : **10/10 à la bonne version**, et les cinq republiés
(manuel, contrat 1.5, Catalogue, Arsenal, Annonce) sont **identiques au
fichier du dépôt, octet pour octet** (MD5 du base64 décodé). Les cinq autres
restent ceux du 3 août : texte relu (pypdf, NFKC), seule l'étiquette de
version diffère. `/healthz` 200 sur le domaine et sur l'origine Render.

## Six branches rapatriées dans `main`

| branche | ce qu'elle apportait | conflit |
|---|---|---|
| `nebula-agency-docs-update-ez6o71` (09-11) | grille 25/35 % chassée, montants en francs, contrat 1.5 | aucun |
| `nebula-carousel-post-5cp35d` (09-04) | posts de vente, statuts WhatsApp, affiche « RUBAN » | aucun |
| `business-digital-ideas-mps2rp` (09-03) | dossier des quinze produits | aucun |
| `google-my-business-braise-or-rb4you` (09-02) | affiche Grain d'Esthétique vectorielle, fiche Google du Braisé | `.gitignore`, les deux blocs gardés |
| `whatsapp-automation-agent-ryk9j5` (08-29) | Whapi, installateur, démonstration ; devis tablette Luxury | CONTEXT Luxury, les deux sections gardées |
| `mise-digitale-idea-qdpkok` (09-09) | **MINUIT devient LE PLI**, la lettre tient son heure, la caisse écrite | REPRENDRE-ICI et lecons, les deux côtés gardés |

Relu avant de fusionner : la branche des posts ne contient aucune trace de
l'ancienne grille (25 %, 35 %, 15 000 F, STARTER/SILVER/GOLD, N1/N2).
Contrôles après fusion : **LE PLI 145 verts**, **Le Standard 175/175**.

**Pas fusionnée, exprès** : `video-project-analysis-monetization-18oh7b`. Elle
touche `vitrina/server.py` et `_worker.js`, et ajoute
`.github/workflows/reveil.yml`, un réveil de Render en tâche planifiée : une
automatisation qui tourne seule dès qu'elle est dans `main`, donc à trancher
par Mongazi. Sa variante de la lettre (`vitrina/lettre/`) est antérieure à
LE PLI. Les branches d'avant le 12 août restent où elles sont.

## ⛔ Un devis serait parti en ligne

La branche du 08-29 posait le devis « vitrine sur tablette » (420 000 F) **dans
le dossier du site Luxury** : `devis-vitrine-tablette.html` à la racine,
`assets/docs/Devis_*.pdf`, `_build_devis.py`. `_dist.py` copie tout sauf une
liste fixe : au déploiement suivant, **le prix négocié avec Gloria était
publiquement téléchargeable**. Exclu par son nom, à tout niveau, et vérifié sur
un `_dist` réel (157 fichiers, aucun devis). Même famille que le 2026-09-05
(`CONTEXT.md` et 7,2 Mo de photos sources en 200).

## ⚠️ La sonde du parc retirait des LIGNES

NEBULA Agency sortait « EN RETARD » quatre fois de suite sur une page identique
au dépôt. Le script du défi de Cloudflare (`/cdn-cgi/challenge-platform`) se
pose **tantôt seul sur sa ligne, tantôt collé à `</body>`** : `sans_injection()`
jetait la ligne entière, `</body>` avec. Une heure plus tôt, la même sonde
disait « égal » sur la même page. Retrait désormais **par morceau** (un
`<script>` qui porte une marque de Cloudflare), et l'espace entre deux balises
ne compte plus.

## ⚠️ Deux fautes à moi, rattrapées avant de pousser

- **Des marqueurs de conflit ont été commités.** La résolution de `lecons.md`
  a échoué (le dernier marqueur, en fin de fichier, n'avait pas de saut de
  ligne et échappait à l'expression), mais la chaîne PowerShell a continué
  jusqu'au `git commit`. **Un `;` n'arrête rien** : chaque étape native doit
  être suivie de `if ($LASTEXITCODE -ne 0) { throw }`. Réparé par amendement
  du commit de fusion, jamais poussé cassé (`git grep` des marqueurs avant le
  push).
- **Deux lectures lancées en parallèle d'une fusion** ont comparé `main`… à
  lui-même : la fusion avait avancé la référence entre-temps, et tout sortait
  « identique », contrat compris. On compare contre un **commit nommé**
  (`caa0748`), jamais contre un nom de branche qui peut bouger.

## Aussi

- `whatsapp-agent/_qc.py` plantait sur le PC : `subprocess.run(text=True)`
  décode en cp1252, un octet UTF-8 inconnu tue le fil de lecture et `stdout`
  revient à **None**. UTF-8 imposé aux deux bouts.
- `minuit/` restait sur le disque après le renommage (captures de QC du 02/09
  et `__pycache__` seulement) : supprimé.

## ⏳ Ce qui reste

- **LE PLI** : cinq réponses de Mongazi (compte qui encaisse, n8n ailleurs
  ou non, commission SasPay, qui relit le deuil, premier franc ; le
  sous-domaine est tranché depuis le 2026-09-09, `lepli.nebula-agency.online`).
  Rien n'est déployé, et rien ne peut l'être avant.
- **`video-project-analysis-monetization-18oh7b`** : trancher le réveil de
  Render par GitHub Actions et le sort de `vitrina/lettre/`.
- **Le devis Luxury** est dans le dépôt, pas en ligne : l'envoyer à Gloria
  reste un geste de Mongazi.
