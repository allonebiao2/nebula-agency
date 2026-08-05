# Générateur de devis — de la parole du client au prix de la grille

**Date** : 2026-08-05
**Branche** : `claude/nebula-quote-generator-kmr4i6` (⚠️ pas encore dans `main`)
**Demande de Mongazi** : un artefact qui, à partir de ce qu'un client veut, dit
en texte **ou en note vocale**, propose un prix pour une vitrine, un catalogue
ou un outil, à partir des données de tarification du dépôt.

---

## Ce que c'est

Un outil interne, pensé pour le téléphone d'un partenaire debout dans une
boutique. On colle la demande du client ou on la dicte, et il en sort un devis
chiffré, un message prêt à envoyer au client, et une fiche pour NEBULA.

**Trois mouvements** : la parole → la lecture → le devis.

**Le geste signature** : les mots du client sont **surlignés dans sa propre
phrase**, chacun de la couleur de la ligne de devis qu'il a produite (cyan =
catalogue, violet = vitrine, bleu = outil, or = avis Google, vert = quantité).
Le partenaire voit *pourquoi* le prix est ce qu'il est, il ne subit pas un
chiffre sorti d'une boîte noire.

## Où c'est

| Quoi | Où |
|---|---|
| Artefact publié | https://claude.ai/code/artifact/1b5d4f9e-872f-4185-b3be-e2e570cc0802 |
| Source (on édite ça) | `_documents/nebula-agency/vente/_generateur_devis_src.html` |
| Construction | `python3 _build_devis.py` |
| Page autonome | `_documents/nebula-agency/vente/generateur-devis.html` (212 Ko, hors ligne) |
| Corps pour l'artefact | `_documents/nebula-agency/vente/_artefact_devis.html` (généré) |
| Contrôle | `_qc_devis.mjs` — **47 contrôles, tous verts** |

⚠️ **On n'édite jamais `generateur-devis.html` ni `_artefact_devis.html`** : ils
sont générés. Toute correction passe par `_generateur_devis_src.html`.

## D'où viennent les prix

**Rien n'est inventé.** Deux sources, et deux seulement :

1. `_documents/nebula-agency/vente/00-SOCLE-COMMERCIAL.md` (v2.0, 2026-07-30)
   pour le Catalogue (50 000 F, 20 produits, +15 000 F par lot de 10), la
   Vitrine (150 000 F, +30 000 F par page, domaine offert 1 an puis 16 000 F),
   le QR Google Review (30 000 F), l'abonnement (20 000 F / 6 mois), les
   modalités de paiement et les commissions (30 % / 40 %, récurrent 4 000 F).
2. Le **configurateur du site** (`00-nebula-agency/nebula_agency_v9.html`) pour
   l'Outil métier : base 60 000 F, les 38 poids `data-price`, la fourchette
   ×0,9 / ×1,25, l'arrondi à 5 000 et les bornes 55 000 / 500 000.

> **Le contrôle le plus important de la suite** ouvre la vraie page du site,
> coche les mêmes options, et exige **le même chiffre au franc près**. Le socle
> §1.2 dit que le prix d'un outil sort du configurateur : si notre outil disait
> autre chose, il serait faux par construction. Il donne 300 000 – 420 000 F
> sur le cas de référence, comme le site.

**Un prix qui change doit changer dans le socle d'abord**, puis ici.

## Les garde-fous du §6, affichés au bon moment

L'outil ne se contente pas de chiffrer, il rappelle la doctrine quand le brief
la met en danger :

| Ce que le brief dit | Ce que l'outil rappelle |
|---|---|
| « premier sur Google » | §6.2 · on optimise, on ne garantit aucune position |
| « urgent », « demain » | §6.1 · jamais moins de 5 à 7 jours |
| « facture normalisée », « DGI » | §6.4 · jamais la conformité e-MECeF promise |
| « remise », « négocier » | §6.3 · aucun prix hors grille décidé seul |
| il débute / petit budget | l'escalier · dans le doute, on vend le Catalogue |
| deux offres à la fois | §1.3 · deux offres d'un coup font perdre les deux |
| un outil métier | §6.12 · la fourchette n'est pas un prix ferme |
| un métier reconnu | §10 · la preuve à montrer (Miss Cakes, Djambar, HH Design…) |

**Le message client ne contient jamais la commission.** Elle vit dans la fiche
interne, repliée, avec un avertissement explicite. C'est contrôlé par la suite.

## La note vocale

Trois chemins, dans cet ordre :

1. **La dictée du navigateur** (`SpeechRecognition`, fr-FR, continu) quand elle
   existe : on peut faire écouter la note vocale du client à voix haute.
2. **Le micro du clavier du téléphone**, qui écrit dans le champ : ça marche
   partout, y compris là où un cadre interdit le micro. C'est le recours
   annoncé, mot pour mot, dès que la dictée échoue ou n'existe pas.
3. Le texte tapé.

Chaque erreur (`not-allowed`, `no-speech`, `network`…) a sa propre phrase, qui
dit quoi faire, pas seulement ce qui a raté.

## Ce qui a été appris

- ⚠️ **`normaliser()` mangeait les jokers.** Les motifs du lexique s'écrivent
  `produit*`, `command*`. La normalisation transformait l'étoile en espace
  **avant** que le compilateur de motifs la voie : `produit*` cherchait
  « produit » exactement et ne trouvait jamais « produits ». **Une seule cause,
  quatre contrôles rouges** (catalogue non détecté, option graphiques manquée,
  secteur non reconnu, surlignage incomplet). L'étoile se retire maintenant
  **avant** la normalisation. Leçon générale : quand on normalise du texte,
  les métacaractères doivent sortir du texte avant, jamais après.
- **La normalisation garde la longueur exacte** (un caractère pour un
  caractère, accents pliés, ponctuation en espaces). C'est ce qui permet de
  retrouver le mot dans la phrase d'origine et donc de le surligner.
- **Les pages ne se comptent pas comme les produits.** « une page équipe et une
  page tarifs » ne dit pas 1, il dit deux pages **en plus** de l'accueil. Un
  nombre explicite ≥ 2 gagne ; sinon on compte les mentions.
- ⚠️ **Faux positifs de secteur** : `table*` attrapait « tableau de bord » et
  classait un gérant de boutiques en ébéniste ; `or` et `argent` attrapaient
  « il n'a pas beaucoup d'argent ». Un mot de secteur doit être un mot que
  personne n'emploie pour autre chose.
- **Les montants à l'écran sont insécables** (` `), pas dans les textes
  copiés. « 60 / 000 F » coupé sur deux lignes se lit comme deux nombres.
- **Les captures ont trouvé ce que 44 contrôles verts n'ont pas vu** : le
  « à » orphelin du grand chiffre, le tiret vert tout seul du récurrent, le
  bouton WhatsApp souligné, et surtout « Vos 30 avec photo » — le mot
  « produits » manquait dans le message envoyé au client. Le standard du
  2026-08-01 a encore eu raison : **vert ne veut pas dire fini**.

## Reste à faire

- [ ] **Fusionner dans `main`** — la branche `claude/nebula-quote-generator-kmr4i6`
      attend l'accord de Mongazi (règle « jamais pusher sans validation »).
- [ ] Décider si la page autonome rejoint le back-office partenaires (elle est
      hors ligne et tient dans un fichier, donc elle peut aussi juste être
      envoyée en pièce jointe WhatsApp).
- [ ] Y brancher le numéro Mobile Money officiel dans le message client, si
      Mongazi veut qu'il y figure.
- [ ] Le jour où le socle change un prix : modifier `_generateur_devis_src.html`
      **et** relancer `_qc_devis.mjs`, qui compare au configurateur du site.
