# PROSPECTION · la journée type

> À cocher dans l'ordre. Les commandes sont dans `CERVEAU.md` § 3, les pièges dans `LECONS.md`.
> **La cadence mesurée le 18/11** sur ce PC (8 Go) : un envoi WhatsApp Web par lien `send?phone=…&text=…` prend
> **~50 s** (chargement complet de WhatsApp à chaque fois), **un prospect à la fois**, jamais deux envois dans le
> même lot. 40 envois = environ 35 minutes de navigateur, à étaler sur la journée entre les réponses.

---

## Avant tout (5 minutes)

- [ ] `python scripts/rapatrier.py` (règle du dépôt), puis lire `CERVEAU.md` § 6 et § 7.
- [ ] Libérer la mémoire : fermer Edge et les onglets inutiles. **Jamais VS Code** (Claude Code tourne dedans).
- [ ] Ouvrir WhatsApp Web dans Chrome. S'il montre un QR code : **BESOIN DE TOI** (Mongazi scanne avec son téléphone).
- [ ] `python scripts/prospection.py suivi C:/Users/USER/nebula-apercus/SUIVI-PROSPECTS.md` : lire la ligne
      « À FAIRE AUJOURD'HUI ».

## Matin : tenir ce qui est promis

- [ ] **Les promesses datées d'abord** (un aperçu promis « demain matin » passe avant tout nouvel envoi).
- [ ] Les intéressés : où en est chacun ? Photos reçues ? Fiche `#order` remplie ? Paiement ? Questions de découverte.
- [ ] Les relances dues (une seule par prospect, deux jours après) : message de relance de la méthode § 3.
- [ ] Le **statut WhatsApp et TikTok du jour**, fait dans Google Flow (Mongazi y est connecté), avec le logo NEBULA.

## Journée : 40 premiers contacts

- [ ] Trouver les commerces : liste locale Google, un métier par page (`…&udm=local&hl=fr`, puis `&start=20` pour la
      page suivante). Garder ceux qui ont un numéro et pas de vrai site.
- [ ] `importer` puis `liste 25` : vérifier à l'œil le métier de chacun (une boutique de mode trouvée sous
      « chaussures » doit dire « vos tenues »), corriger avant d'envoyer.
- [ ] `envois 20`, puis un envoi à la fois. Après chaque envoi : `statut <id> contacte`.
- [ ] **Toutes les 3 envois : le tour des réponses** (liste WhatsApp « Prospects fêtes 2026 », non lus).
- [ ] Chaque réponse : chaleureux, professionnel, ultra humain. Les situations et leur réponse : méthode § 6.
- [ ] Chaque **vocal** : Télécharger, `python scripts/transcrire.py`, répondre. Si ça coince : **BESOIN DE TOI**.
- [ ] Chaque nouvel intéressé : enregistré en contact « Prospect <nom> » (synchronisé) + liste « Prospects fêtes 2026 ».
- [ ] Faire le point à Mongazi régulièrement, en une ligne.

## Soir : tout ranger (10 minutes)

- [ ] La base à jour : chaque statut, chaque note (ce qu'il a dit, ce qu'on a promis), chaque relance datée.
- [ ] `suivi` + `vcf`, puis les deux fichiers **collés dans sa propre conversation WhatsApp** (il voit tout sans moi).
- [ ] Supprimer les vocaux téléchargés une fois transcrits (on garde le texte, pas la voix).
- [ ] Mémoire : `CERVEAU.md` § 6 et § 7 (chiffres agrégés seulement), `LECONS.md` si quelque chose a mordu,
      le journal du jour dans `_memoire/conversations/`, et `_memoire/EN-INSTANCE.md`.
