# 2026-11-18 · Le sprint des fêtes : la prospection WhatsApp

> Le cerveau de ce chantier : `_memoire/prospection/CERVEAU.md` (puis `ROUTINE.md` et `LECONS.md`).
> ⛔ Dépôt public : ici, des chiffres agrégés et des métiers. Les noms, numéros et réponses vivent dans Supabase
> (`piste.prospection`) et dans le suivi privé `C:\Users\USER\nebula-apercus\SUIVI-PROSPECTS.md`.

## Le point de départ

Mongazi n'avait « rien sur lui » et voulait **100 000 F CFA avant la fin de la semaine**, avec la peur de ne pas
pouvoir payer son abonnement. Il a posé l'objectif en `/goal`, d'abord en **dollars** : 100 000 $ (environ 57
millions de F CFA) n'était pas atteignable honnêtement, il l'a su et a choisi « 100 000 F CFA ». Vers 17 h 30, il a
relevé l'objectif : **1 000 000 F CFA « avant vendredi ou la fin de la semaine »**.

## Ce qui a été tranché dans la journée

- Le devis tablette d'une cliente (Luxury Club 229, 420 000 F) : **envoyé en septembre, refusé**. Ne plus le proposer.
  La remise à jour faite par erreur a été annulée.
- Djambar paiera peut-être à la fin du mois : trop tard pour le sprint.
- Les partenaires : « ils foutent rien, je ne compte plus sur eux, je n'ai que toi ». Un message des fêtes est parti
  dans le groupe des partenaires et en direct à une personne du réseau avant cette consigne ; plus rien depuis.
- **Aucun groupe** : une offre est partie dans un groupe de vendeurs avant la consigne ; deux autres groupes étaient
  réservés aux administrateurs.
- **De nouveaux clients, trouvés sur Google, contactés depuis son WhatsApp Web**, avec un feu vert général pour écrire
  et répondre, et le point régulier en échange. Rythme : 30 puis **40 premiers messages par jour**.
- L'accroche refaite à sa demande (« choquer et intriguer, parler moins, ultra humain ») : la v2 en 3 lignes.
- Le paiement : Mobile Money au numéro de NEBULA, **seulement après avoir tout expliqué**.

## Ce qui a été construit

- **La base** `piste.prospection` (Supabase, RLS, aucun accès public) et **l'outil** `scripts/prospection.py` :
  importer, liste, envois (l'accroche écrite pour chaque fiche), statut, relance, suivi, vcf, bilan.
- **La transcription des vocaux** : `scripts/transcrire.py` (Deepgram Nova-3, français), essayée sur deux vocaux réels.
- **La méthode publique** : `_documents/nebula-agency/vente/PROSPECTION-GOOGLE-MAPS.md` (où chercher, note de besoin,
  accroche, exemples par métier, réponses à chaque situation vécue).
- **Le rangement côté WhatsApp** : une liste « Prospects fêtes 2026 », les prospects chauds enregistrés en contacts
  « Prospect <nom> » synchronisés sur son téléphone, et deux fichiers collés dans sa propre conversation : le tableau de
  suivi (.txt) et la fiche contact de tous les prospects (.vcf, à importer).
- **PyMuPDF** installé (sur son accord) pour lire le catalogue PDF d'un prospect.
- **La mémoire** : trois fiches de mémoire automatique (consignes de prospection, état du sprint, statuts quotidiens)
  et cette branche `_memoire/prospection/`.

## Les chiffres (agrégés, vers 17 h 45)

54 fiches en base dans 9 métiers · **31 premiers contacts** · **8 vraies réponses humaines** (les messages
automatiques de WhatsApp Business ne comptent pas) · **4 intéressés** · **0 F encaissé**. Avec l'accroche v1 :
3 vraies réponses sur 18.

## Les pistes chaudes (par métier)

- **Une bijouterie très notée** : « ok » après l'exemple et le prix ; tout lui a été expliqué, avec le numéro de
  paiement ; les questions de découverte sont posées (ambiance, bijoux phares, clientèle). Attend ses photos.
- **Une pâtisserie de 30 ans** : avait déjà un catalogue, un PDF de 87 Mo ; a dit « ok » à un aperçu avec ses
  propres gâteaux. ⏰ **Promis pour le jeudi 19 au matin.**
- **Un grill-traiteur de 68 avis** : a tenté un appel vidéo, s'est dit très intéressé ; Mongazi a répondu lui-même,
  puis l'exemple et le prix sont partis par écrit. À rappeler.
- **Une restauratrice** : deux vocaux transcrits, déjà arnaquée par une société payée qui n'a rien livré, « je vais
  encore essayer » ; on lui a proposé l'aperçu d'abord, le paiement seulement si ça lui plaît.

## Ce qui reste

1. ⏰ L'aperçu promis à la pâtisserie de 30 ans, jeudi matin.
2. Les relances du 19 (les intéressés) et du 20 (les contactés sans vraie réponse).
3. 🙋 Mongazi : importer le fichier `.vcf` sur son téléphone ; rappeler le grill-traiteur.
4. Les statuts WhatsApp et TikTok de chaque jour, dans Google Flow (il y est connecté ; Pinterest en inspiration seulement).
5. L'objectif d'1 000 000 F CFA : volume (40 par jour) et tickets plus gros (Vitrine 150 000 F).

Les leçons techniques et commerciales de la journée : `_memoire/prospection/LECONS.md`.
