# Documents périmés · à ne plus envoyer

> Rangés ici le **2026-09-10**. Ils ne sont pas supprimés : ils servent d'archive, et
> une décision de Mongazi peut les faire refabriquer. **Ils ne doivent plus sortir de
> ce dossier tels quels.**

## Pourquoi ils sont ici

Ces quatre documents décrivent le **programme partenaires d'avant le 2026-08-02**.
Ils annoncent une grille et un mécanisme que NEBULA n'applique plus, et que le contrat
en vigueur **interdit**.

| Ce que le document annonce | Ce qui est vrai aujourd'hui |
|---|---|
| STARTER **25 %** · SILVER **30 %** · GOLD **35 %** | **30 %** par défaut · **40 %** dès 3 ventes dans le mois |
| Palier selon les ventes **cumulées** (1 à 4, 5 à 9, 10 et plus) | Palier **mensuel**, remis à zéro le 1er de chaque mois |
| **10 %** sur les filleuls directs (N1) et **5 %** sur leurs filleuls (N2) | **Aucune commission de réseau, à aucune profondeur.** Les filleuls comptent seulement dans le seuil de 3 |
| « Plafond total 40 % : parrain + N1 + N2 » | Il n'y a pas de plafond à partager : chacun touche sur **ses propres ventes**, point |
| Abonnement **15 000 F / 6 mois** | **20 000 F / 6 mois, modifications comprises** |
| Sept rangs cosmiques (Météore, Comète, Planète, Étoile, Supernova, Nébuleuse, Galaxie) | Neuf rangs, titres de société : Partenaire Junior, Conseiller, Conseiller Confirmé, Conseiller Senior, Chef de Secteur, Chef Régional, Directeur Commercial, Directeur Associé, Président Fondateur |

⚠️ **Le point qui coûte le plus cher est la commission de réseau.** Une diapositive
entière du deck (« Le pouvoir de l'effet réseau ») déroule un arbre Marc → Shad → Paul →
Kofi et conclut que « son réseau lui rapporte 90 000 FCFA de plus, sans effort
supplémentaire ». C'est exactement ce que la décision du 2026-08-02 a supprimé, et ce que
le contrat 1.4 exclut. Montrer cette page à un candidat, c'est lui promettre un revenu
qu'il ne touchera jamais, et donner au programme l'allure d'une pyramide qu'il n'est pas.

## Les quatre fichiers

- **NEBULA_Brochure_Partenaire.pdf** · brochure publique de recrutement, 5 pages.
- **NEBULA_Guide_Lancement_Partenaire.pdf** · guide interne « lancer ton premier
  partenaire », 5 pages.
- **NEBULA_Programme_Partenaires_PREMIUM.pptx** · le deck de 14 diapositives.
- **NEBULA_Programme_Partenaires.pdf** · le même deck exporté en PDF (14 images,
  aucune police : c'est bien l'export du .pptx). Il dormait dans
  `nebula-affilies/assets/`, à côté des PDF que le portail publie vraiment.

## Par quoi les remplacer, aujourd'hui

| Besoin | Le document à jour |
|---|---|
| Recruter, texte à partager publiquement | `vente/01b-ANNONCE-PUBLIQUE.md` (et son PDF) |
| Recruter, dossier interne (grille de notation, entretien) | `vente/01-AVIS-DE-RECRUTEMENT.md` |
| Former un nouveau partenaire | `vente/02-MANUEL-DU-PARTENAIRE.md` |
| Montrer ce qu'il va gagner | `vente/simulateur-commissions.html` |
| Ce qu'il signe | `vente/09-CONTRAT-PARTENAIRE.md` (version 1.4) |

## Ce qu'on ne peut pas faire d'ici

⚠️ **Ces documents ne sont pas modifiables.** Les diapositives du .pptx sont des **images
plein écran** (une PNG par diapositive, aucun texte dans le fichier), et les deux PDF sont
des exports sans source dans le dépôt. Corriger un chiffre demanderait de **refabriquer le
document entier**. Tant que Mongazi n'a pas demandé un nouveau deck, les documents de
`vente/` font le travail et sont, eux, régénérables (`_build_pdf.py`).

⚠️ **NEBULA_Masterclass_Closing.pptx a été vérifié et n'est PAS ici** : il ne parle que de
méthode de vente (écoute, objections, scripts), ne cite aucun taux de commission, et ses
prix vus sur les diapositives concordent avec le socle. Il reste à sa place.
