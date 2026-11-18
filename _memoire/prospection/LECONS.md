# PROSPECTION · les leçons du 18/11

> Chaque leçon tient en deux lignes : **pourquoi** (ce qui a mordu), puis **comment** (ce qu'on fait désormais).
> Le point d'entrée : `CERVEAU.md`. La journée : `ROUTINE.md`.

---

## Le PC (8 Go)

- **La mémoire sature** : 750 Mo libres, une commande PowerShell de 2 s prenait plus de 2 minutes, un script Python
  a été tué. **Comment** : fermer Edge (+400 Mo d'un coup), les onglets inutiles ; **jamais VS Code**, Claude Code tourne dedans.
- **Le lecteur PDF de WhatsApp garde le fichier en mémoire** (87 Mo) et fait geler la machine.
  **Comment** : télécharger, fermer le lecteur, traiter le PDF hors du navigateur (PyMuPDF, installé le 18/11).
- **`python -I` ignore PYTHONIOENCODING** : la console cp1252 plante sur « → » ou « ✓ ».
  **Comment** : pas de `-I` quand on affiche du texte accentué, ou `sys.stdout.reconfigure(encoding="utf-8")`.

## Trouver les prospects

- **Google Maps exige d'ouvrir chaque fiche** pour lire le numéro : 4 à 5 s par fiche, des fiches « sans numéro » qui
  n'avaient juste pas fini de charger, et l'onglet gèle. **Comment** : la **liste locale Google**
  (`google.com/search?q=<métier>+Cotonou&udm=local&hl=fr`) donne nom, note, avis, numéro et bouton « Site Web » sur chaque carte, 20 par page.
- **Chrome ralentit les onglets en arrière-plan** (minuteries freinées) : une lecture lancée en tâche de fond n'avance presque plus.
  **Comment** : ne rien faire tourner dans un onglet caché ; lire une page, l'exporter, passer à la suivante.
- **Un métier mal rangé fausse le message** (une boutique de mode trouvée sous « chaussures » recevait « vos chaussures »).
  **Comment** : relire `liste` avant `envois`, corriger le métier dans la base.
- **L'outil JS de Chrome tronque sa réponse vers 1 500 caractères.**
  **Comment** : exporter par paquets de 8 à 10 fiches, en tableaux compacts, seulement les fiches utiles.

## WhatsApp Web : envoyer

- **Le lien `web.whatsapp.com/send?phone=229…&text=…` recharge toute l'appli** : ~50 s par envoi sur ce PC.
  **Comment** : attendre ~50 s, puis cliquer Envoyer en JS **seulement si la zone de saisie contient le texte** ; sinon attendre et revérifier.
- **Un lot `browser_batch` trop long expire côté outil, mais continue dans le navigateur.**
  **Comment** : un envoi par lot ; après une expiration, **regarder l'état réel avant de renvoyer** (jamais de doublon).
- **La touche Échap FERME la conversation** ; le texte tapé ensuite part dans le vide.
  **Comment** : ne jamais taper Échap avant d'écrire ; vérifier l'en-tête du chat (`#main header`) juste avant d'envoyer.
- **Un message tapé à la main avec des retours à la ligne s'envoie trop tôt.**
  **Comment** : `shift+Return` entre les lignes, `Return` seulement pour envoyer (ou le texte dans le lien `&text=`).
- **Joindre un fichier** : le menu Document ouvre le sélecteur natif de Windows (impossible à piloter) et le
  glisser-déposer simulé est ignoré. **Comment** : coller un `File` construit en JS par `ClipboardEvent('paste')` sur la zone de saisie (marche pour .vcf et .txt), puis légende et Envoyer.

## WhatsApp Web : lire

- **La liste des conversations est virtualisée** : seules les lignes visibles existent dans la page.
  **Comment** : faire défiler par pas et relire, ou passer par le filtre de liste « Prospects fêtes 2026 ».
- **L'état d'un message (reçu, lu) n'est pas lisible dans le DOM**, mais il l'est dans le nom accessible.
  **Comment** : l'outil `find` affiche `wds-ic-read` (lu) et `wds-ic-delivered` (reçu) sur chaque ligne.
- **Les émojis 🙂 sont des images** : une recherche d'`img` dans un message donne des faux « images reçues ».
  **Comment** : chercher les vraies pièces jointes par leur texte (« PDF », « Photo », durée d'un vocal).
- **Beaucoup de commerces ont WhatsApp Business** : message d'accueil automatique, absence, IA de Meta qui « vous
  connecte à notre équipe ». **Comment** : ce n'est **pas** une réponse ; seule une phrase humaine compte (méthode § 6).

## Ranger

- **Enregistrer un contact** : Infos du contact → Ajouter → Prénom « Prospect » → Nom → « Synchroniser le contact
  sur le téléphone » → ✓. **Piège** : les émojis d'un profil résistent au triple clic, faire **Ctrl+A** dans le champ d'abord.
- **Ajouter à une liste** : dans Infos du contact, « Ajouter à la liste » → cocher → Terminé (le bouton devient « Changer la liste »).
- **Créer une liste** : Plus de listes → Nouvelle liste → nom → Ajouter des personnes → recherche par numéro.
  **Piège** : les coordonnées fixes se décalent dès le premier ajout ; cocher en JS la case dont la ligne contient le numéro.
- **Beaucoup de contacts d'un coup** : un fichier `.vcf` (`prospection.py vcf`) collé dans sa propre conversation,
  qu'il importe sur son téléphone. **Piège** : écrire avec `newline=""`, sinon Windows double chaque fin de ligne.

## Les vocaux

- **On ne peut pas écouter un vocal.** **Comment** : survoler le message → menu → Télécharger (fichier
  `WhatsApp Ptt … .ogg` dans Téléchargements) → `python scripts/transcrire.py` (Deepgram Nova-3 français, clé dans `secrets/deepgram.env`).
- **La voix d'un prospect part aux États-Unis.** **Comment** : usage ponctuel pour répondre, texte gardé, audio supprimé.

## Les numéros béninois

- **Deux formes vivantes** (8 et 10 chiffres) ; WhatsApp ouvre bien le compte resté sur 8 chiffres quand on donne la forme à 10.
  **Comment** : envoyer avec `229` + les 10 chiffres ; noter l'autre forme dans la fiche ; ne jamais retirer le `01`.

## La vente

- **L'accroche v1** (5 lignes, l'offre d'entrée) : 3 vraies réponses sur 18. **Comment** : la v2, 3 lignes qui
  intriguent, l'offre seulement après la réponse (méthode § 3).
- **« J'ai déjà un catalogue »** : chez un commerçant de 30 ans, c'était un PDF de 87 Mo. **Comment** : le poids est
  l'argument (le client télécharge avant de voir un produit), puis un aperçu avec ses propres produits.
- **« J'ai déjà payé une société qui n'a rien fait »** : la méfiance bloque tout. **Comment** : empathie d'abord,
  puis aperçu avec ses vrais produits et paiement seulement si ça plaît.
- **« Je reviendrai plus tard »** : **Comment** : remercier, proposer une relance datée, la noter dans la base.
- **Un prospect qui tente un appel vidéo est le plus chaud.** **Comment** : **BESOIN DE TOI**, Mongazi rappelle ;
  en attendant, exemple concret et prix par écrit.
- **Un catalogue WhatsApp Business existe parfois** (`wa.me/c/…`). **Comment** : le saluer, puis le vrai manque :
  il ne se voit que si on a déjà le numéro, pas sur Google où les nouveaux clients cherchent.

## La veille du soir (18/11)

- **Un message automatique compte comme une réponse pour Mongazi.** Le 18/11 au soir, trois prospects n'avaient
  envoyé que leur accueil automatique ; la méthode disait d'attendre, Mongazi les a vus « sans réponse ».
  **Comment** : répondre une fois à chaque message automatique, en rebondissant sur ce qu'il dit, puis
  « je vous montre un exemple ? » (méthode § 6).
- **Vérifier chaque discussion, pas la liste.** La liste de WhatsApp Web est virtualisée et le statut « non lu »
  disparaît dès que Mongazi lit sur son téléphone. **Comment** : ouvrir chaque prospect de la base par la barre de
  recherche (les 8 derniers chiffres) et regarder qui a écrit le DERNIER message.
- **Un seul gros onglet à la fois dans Chrome.** Un onglet Pinterest ouvert pendant la veille a fait tomber la
  mémoire du PC à 1,1 Go et déconnecté l'extension (22 h 58). **Comment** : la recherche d'images attend que la
  veille soit finie, et on vérifie un aperçu avec un Chromium sans fenêtre (`_socle/regarder.py`, hors dépôt).
- **Deepgram décroche sur un vocal qui mêle le français et les noms des plats du pays** (53 s, arrêt à 12,9 s,
  « Souris, yogourt » pour « riz, igname »). **Comment** : `scripts/transcrire.py` passe seul à Gemini quand le texte
  est trop court pour la durée ; `gemini-2.5-flash` a tout rendu, `gemini-3.8-flash` a dépassé 90 s.
