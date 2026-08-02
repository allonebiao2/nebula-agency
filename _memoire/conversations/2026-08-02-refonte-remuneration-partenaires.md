# 2026-08-02 · Refonte complète de la rémunération des partenaires

> **Le résultat, en trois lignes.** Un partenaire touche **30 %** sur chaque vente et **40 %**
> dès que ses ventes et celles de ses filleuls directs atteignent **3** dans le mois. Il touche
> **20 % de chaque abonnement, à vie**. Il ne touche **rien** sur les ventes de ses filleuls.

---

## Ce qui a changé, et dans quel ordre

La règle a bougé **six fois** dans la journée. Voici l'état final, seul valide :

| | Avant ce jour | Après |
|---|---|---|
| Commission de vente | 25 / 30 / 35 % selon le volume | **30 %**, **40 %** dès 3 ventes (lui + filleuls), remis à zéro le 1er |
| Réseau | N1 10 % · N2 5 % | ⛔ **supprimé, à toute profondeur** |
| Abonnement | 25 % à vie | **20 % à vie** (4 000 F / client / semestre) |
| Rôle superviseur | barème d'équipe séparé | plus de barème, **un insigne** |
| Rangs | noms cosmiques (Météore, Galaxie…) | **titres de vraie société** (Conseiller, Chef de Secteur, Directeur Associé…) |
| Coupure impayé | non défini | **7 jours de courtoisie, coupure à J+8**, données 6 mois |

**Le contrat passe en version 1.2.**

---

## Les décisions de fond, et leur raison

**1 · Plus aucune commission de réseau.** Payer quelqu'un sur le travail d'un autre est ce
qui fait ressembler un programme à une pyramide. Les filleuls comptent maintenant dans le
**seuil de 3** de leur parrain, sans rien lui verser. La phrase « personne ne gagne d'argent
sur le dos de personne » est devenue littéralement vraie, et elle est reprise mot pour mot
dans le manuel, l'arsenal et l'espace partenaire.

**2 · Coupure à J+8, pas à J+45.** J'avais recommandé J+45, c'était une erreur et je l'ai
corrigée. Une échéance qu'on n'applique pas est une échéance qui n'existe pas : le client
apprend que la date est décorative et attend davantage au semestre suivant. Le levier est
maximal juste après l'échéance, tant que le QR est affiché dans la boutique.

**3 · Les 6 mois de conservation des données restent.** Ça ne coûte presque rien et ça garde
récupérable un client qui vaut 20 000 F par semestre.

---

## Ce que le contrat a gagné (articles nouveaux)

| Article | Ce qu'il règle |
|---|---|
| **6.2 bis** | Suspension du service : 7 jours de courtoisie, coupure au 8e, données 6 mois |
| **6.7** | Barème révisable avec **préavis de 30 jours**, sur les ventes futures. Avant, la grille était figée : trop généreuse, elle ne pouvait plus bouger |
| **6.8** | **Reprise de commission** si un encaissement est remboursé. Avant, NEBULA perdait la vente ET payait la commission |
| **7.4 / 7.5** | Le client appartient à NEBULA, le portefeuille n'est ni cessible ni transférable |
| **8.13** | **Indemnités forfaitaires** : double de la somme encaissée en direct, 150 000 F par client démarché, 100 000 F pour un candidat racketté |

**L'exception qui rend 6.8 tenable :** si le remboursement vient d'une faute de NEBULA, la
commission **reste acquise** au partenaire. Sans cette réserve la clause serait abusive et un
juge l'écarterait en entier.

---

## Les pièges rencontrés, à ne pas refaire

**⚠️ « Recrue » servait à trois choses** dans le code de l'espace partenaire : un **rang**, un
**rôle** (« Recrue standard », opposé à superviseur) et une **section admin** (les
candidatures). Un remplacement global aurait cassé les deux dernières. Seul le rang a été
renommé ; le rôle est devenu « Partenaire standard ».

**⚠️ Les CGU servies dans l'application étaient fausses.** `server.py` affichait encore
« 25 % à 35 % + 10 % N1 + 5 % N2 » dans le texte que le partenaire **accepte à
l'inscription**. Faux depuis deux refontes. C'est le seul document accepté formellement en
ligne : un partenaire aurait pu s'en prévaloir. Toujours vérifier ce texte quand un barème
change.

**⚠️ Supprimer le récurrent a cassé la contrepartie du non-démarchage.** L'article 11.2
faisait explicitement du récurrent la contrepartie des 24 mois de non-sollicitation. En
supprimant l'un, l'autre devenait **sans cause**. Le rétablissement du récurrent à 20 % a
réparé ça. **Toute suppression d'avantage doit être vérifiée contre les clauses qui s'y
adossent.**

**⚠️ Le nettoyage automatique des tirets cadratins a cassé 4 endroits** : deux cellules de
tableau devenues `|, |`, un « Bonjour [Prénom] ?, » illisible, et des titres de prix passés
d'un cadratin à une virgule molle. **Un script de remplacement typographique doit toujours
être relu ligne à ligne**, le compteur à zéro ne prouve rien.

---

## Ce qui reste ouvert

- [ ] **Prévenir les 3 partenaires actifs.** L'article 6.7 impose **30 jours de préavis
      écrit** avant toute baisse de barème, et ils sont encore en version 1.1. Le message du
      groupe n'est pas écrit.
- [ ] **Valider les frais de réactivation de 5 000 F** (proposés, pas activés). Le contrat
      renvoie aux « frais en vigueur », donc les activer ne demande pas de nouvelle signature.
- [ ] **Le workflow n8n de relance** reste à construire. `NAFF_CRON_KEY` manque sur Railway.
- [ ] **Faire relire le contrat par un juriste béninois.** Avec quatre articles nouveaux dont
      des pénalités chiffrées, ça devient plus utile qu'avant : les indemnités forfaitaires
      sont la clause qu'un juge réduit le plus volontiers si elle est disproportionnée.

---

## Fichiers touchés

**Documents de vente** (14 fichiers + 11 PDF regénérés) : socle, contrat, avis de
recrutement, annonce publique, manuel, les 3 guides de service, arsenal, mise en ligne,
relance-renouvellement, messages du groupe, **nouveau `12-GUIDE-DES-APPELS.md`**, simulateur,
affiche A4 (QR relu et validé).

**Application `nebula-affilies/`** : `server.py` (grille, parrainage, abonnement, rangs, CGU),
`static/app.js`, `partenaire.html`, `admin.html`.

**Mémoire** : `CLAUDE.md`, `_memoire/REPRENDRE-ICI.md`, `_memoire/affilies/cerveau-affilies.md`.

**Commits** : `cb6860b` → `fc4f8ee`, branche `claude/github-repo-context-nisd2r`.

---

*NEBULA Agency · Cotonou*
