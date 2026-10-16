<!-- HISTOIRE DU NOM -->
# MA LETTRE À… · la lettre digitale (ex-MINUIT, ex-LE PLI)

> Le récit complet du produit. `CLAUDE.md` n'en garde qu'un résumé (règle du
> 2026-09-16 : une ligne de produit y est un résumé, le récit vit ici).
> Le mode d'emploi technique est dans `README.md`, la caisse dans
> `PAIEMENT.md`, les règles de publication et de retrait dans `CONDITIONS.md`.

## Le nom (2026-10-16)

**MA LETTRE À…**. Mongazi : « ma lettre j'aime bien », puis le nom qui se
termine par le prénom de la personne (« Ma lettre à Afi », « Ma lettre à
papa », « Ma lettre à la famille Dossou »). Il remplace **LE PLI** (2026-09-09),
qui avait lui-même remplacé **MINUIT** : « LE PLI c'est un peu bizarre, on doit
comprendre dès qu'on le lit ou qu'on le dit ».
- `lepli/` → **`malettre/`**, schéma `malettre`, fonctions `malettre-*`, clés
  `malettre:*`, marqueur `MALETTRE_DONNEES` (commit `5af692d`).
- ⛔ Les documents datés gardent l'ancien nom (`_plans/`, journaux,
  conversations, leçons) ; la composition vidéo `lepli-demo` aussi, elle sera
  refaite avec la vidéo publicitaire.
- Adresse prévue : **`malettre.nebula-agency.online`** (sous-domaine gratuit).
  `malettre.com` est pris ; `malettre.app`, `.online`, `.bj`, `.ci`
  semblaient libres le 2026-10-16 (le lien `malettre.app/a/afi` se lirait
  « ma lettre à Afi ») : achat à décider par Mongazi.

<!-- FIN HISTOIRE -->

## La page d'accueil (2026-10-16)

`_accueil_src.html` → `python malettre/_build_accueil.py` → `index.html` +
`exemples/*.html` (jamais édités à la main). **La phrase** : *une lettre, c'est
une feuille qui devient une enveloppe scellée, puis qui redevient une feuille
entre les mains de quelqu'un.* **L'objet** : la feuille et son cachet de cire.
- **Le chargement** (demandé par Mongazi) : une lettre nouée d'un ruban de
  satin, le nœud se défait, le rabat se lève, « Ma lettre à toi » paraît,
  « by NEBULA Agency » en dessous. Retiré seul à 3 s, filet à 4,5 s, un toucher
  le passe, absent sans JavaScript.
- **Héros** : « Ma lettre à… » où la plume tape *Afi, papa, Zara, maman,
  Grâce* ; le visiteur tape SON prénom, il part à `creer.html?pour=…`.
- **La scène 3D épinglée** (720 vh, CSS 3D, une seule boucle rAF) : la feuille
  s'écrit, se plie en trois, entre dans l'enveloppe, le cachet tombe et
  s'imprime, dort à 23:57, s'allume à minuit, se brise, la lettre revient.
- **Six exemples** écrits par la vraie plume, personnes inventées et dites
  telles, aucune photo de visage, aucun balisage d'avis ; chacun ouvre la
  VRAIE lettre (`_injecter.poser()`) dans un téléphone.
- **La plume** (fiche qui se coche, lettre qui s'écrit) · **le casier** des
  27 occasions · **le seuil** (une vraie lettre qui s'ouvre 40 s plus tard) ·
  **les timbres** (prix LUS dans `creer.html`, jamais recopiés) · **les
  promesses** · **la fin** (la page blanche qui attend un prénom).
- **Le retrait** : lien WhatsApp au pied, `wa.me/22996740732` (le numéro déjà
  utilisé par `merci.html` et PISTE), comme le prévoit `CONDITIONS.md`.
- Image de partage `og.jpg` (`python malettre/_og.py`, aucune personne).
- **Contrôle** `python malettre/_qc_accueil.py` : **78 verts** (livrable à
  jour, prix égaux au constructeur, prénom transmis, exemples, chargement,
  débordement, CLS, cibles 44 px, contraste sur les pixels avec deux témoins,
  mouvement réduit, sans JavaScript, poids du premier écran). Mesure : la scène
  tient 60 images/s en médiane, processeur ×4.
- **Captures** `python malettre/_voir_accueil.py` → `_vues/accueil/`.
- **Publication prête, pas faite** : `python malettre/_dist.py` (16 fichiers,
  433 Ko, garde anti-fuite) puis `wrangler pages deploy malettre/_dist
  --project-name malettre --branch main` **avec le feu vert de Mongazi**, et
  seulement quand la caisse est branchée (la page vend des lettres payantes).
  ⚠️ La route `/l/<jeton>` arrivera avec la caisse : `_dist` devra la porter.

### Trois défauts trouvés le 2026-10-16, après la coupure du PC

1. ⛔ **Au téléphone, la page était dézoomée** : l'`input` du prénom (Pinyon
   30 px, `size` 20 par défaut) gardait ~440 px de large et poussait la page à
   **597 px**, puis les timbres agrandis avant leur frappe (`scale(1.25)`) à
   414 px. Le contrôle comparait `scrollWidth` à `innerWidth`, qui GRANDIT
   avec le défaut : il passait au vert. Corrigé (`width:0` + `flex:1` sur
   l'input, `overflow-x:clip` sur `#prix`), et le contrôle compare désormais
   à la largeur demandée.
2. ⛔ **En mouvement réduit, billets et timbres restaient invisibles** jusqu'au
   défilement : le repli `.js [data-rv]:not(.vu)` perdait contre leurs règles
   plus spécifiques.
3. ⚠️ **Deux sondes menteuses** : la capture « nœud noué » d'avant la coupure
   montrait un nœud déjà défait (`clock.install()` laisse couler le temps) ;
   la sonde de contraste mesurait le fond une section à côté au téléphone (la
   capture d'élément refait défiler). Témoins ajoutés.

## Ce qui attend Mongazi

- Le **feu vert** pour la mise en ligne, et d'abord **brancher la caisse**
  (5 commandes, `PAIEMENT.md`) et **la plume** (`ANTHROPIC_API_KEY` +
  `malettre-plume`).
- **Acheter `malettre.app`** (ou non).
- **Faire lire les six exemples** à deux ou trois personnes.
- **Filmer 10 secondes de vraie matière** (une main qui ferme une enveloppe,
  un cachet qu'on brise) : sert la page ET la vidéo publicitaire.
- Les 5 réponses déjà en attente (bloc archivé ci-dessous).
- **La vidéo publicitaire** : prochain chantier, questions posées le 2026-10-16.

---

<!-- HISTOIRE DU NOM -->
## Archive : le bloc de `CLAUDE.md` au 2026-10-16, recopié intégralement

### LE PLI — la lettre digitale  *(produit interne, 2026-09-02 · **idée arrêtée le 2026-09-06**)*
- **Ce que c'est** : « une lettre digitale, c'est **une enveloppe cachetée qu'on
  ouvre à l'heure dite** ». L'acheteur écrit son mot, choisit l'heure, paie ;
  il envoie le lien lui-même, elle brise le cachet à l'heure dite, et lit.
  Dossier de décision : `_plans/2026-08-27-lepli-dossier.html` · manuel
  d'exploitation : `_plans/2026-08-28-lepli-manuel.html` · **arrêté (les 12
  décisions) : `_plans/2026-09-06-lepli-arrete.html`** · conditions et retrait :
  **`lepli/CONDITIONS.md`** · code : **`lepli/`**.
- **La thèse** : *le romantique est le marketing, l'événement est le chiffre
  d'affaires, le B2B est la retraite.* Un seul moteur, trois habillages.
- ✅ **LE NOM EST TRANCHÉ LE 2026-09-09 : LE PLI.** Mongazi : « je préfère le
  pli ». **Une seule enseigne**, et ⛔ **MINUIT disparaît comme marque** — le
  mot « minuit » ne survit que là où c'est le mot français (« elle s'ouvre à
  minuit pile »), jamais comme enseigne : garder les deux ferait deux vérités.
  ⚠️ **Le défaut qui a tué MINUIT, mesuré sur les trois registres** : il nommait
  une HEURE, donc il allait à la lettre d'amour, passait sur un faire-part de
  mariage, et ⛔ **ne passait pas sur une annonce de décès** (« MINUIT · Famille
  Dossou »), la ligne à 15 000-50 000 F. Des quatre finalistes (MINUIT · LE PLI ·
  LE CACHET · MISSIVE), **seul LE PLI passe les trois, parce qu'il nomme l'OBJET
  et pas l'occasion** (« un pli », c'est littéralement une lettre qu'on fait
  parvenir). ⚠️ **Le sous-domaine étant tranché** (`lepli.nebula-agency.online`),
  aucun domaine n'était à acheter : la disponibilité n'a contraint personne.
  **Renommé le jour même**, avant la première vente : `minuit/` → **`lepli/`**,
  schéma `minuit` → **`lepli`**, `minuit-*` → **`lepli-*`**, `MINUIT_DONNEES` →
  **`LEPLI_DONNEES`**, `minuit:brouillon` → **`lepli:brouillon`**, la vidéo et
  ses compositions, et l'enseigne partout. **333 remplacements, 28 fichiers**,
  QC **145 + 118 toujours verts**. ⚠️ **Un renommage mécanique abîme les textes
  qui COMPARENT les deux noms** : la note de la veille est ressortie en « LE PLI
  nomme une HEURE » et « les finalistes LE PLI · LE PLI » — relire les endroits
  où l'ancien nom était cité comme objet d'analyse, pas comme enseigne.
  ⛔ **Les documents datés gardent l'ancien nom** (`_plans/2026-08-27-minuit-*`,
  `_plans/2026-09-06-minuit-arrete.html`, les journaux, les conversations, les
  leçons) : à cette date le produit s'appelait MINUIT. L'arrêté porte un bandeau
  qui renvoie ici.
- **Fait le 2026-09-02** : **le gabarit** (`lettre.html`) et **le constructeur**
  (`creer.html`), **78 contrôles verts** (`python lepli/_qc.py`).
- 🕛 **FAIT LE 2026-09-06 — LA LETTRE TIENT L'HEURE ELLE-MÊME** (détail
  `_memoire/conversations/2026-09-06-lepli-finalisation.md`) : ⛔ **la fonction
  qui donne son nom au produit n'existait NULLE PART** — l'heure était demandée à
  l'acheteur, promise sur l'écran final (« elle la recevra le 14 février à
  00:00 ») et n'entrait dans aucune lettre ; ⚠️ **aucun contrôle ne pouvait le
  voir** (on ne mesure pas l'absence d'une chose dont personne n'a écrit qu'elle
  devait exister, même famille que la photo livrée et jamais affichée chez Au
  Braisé d'Or) · ⛔ **n8n, à qui le dossier ET le manuel confiaient la livraison,
  tournait sur le VPS Hostinger `72.61.103.56` qui n'appartient plus à
  Mongazi** : la fonction reposait sur une machine perdue → **elle vit dans la
  LETTRE**, qui ne dépend de rien et tient même si l'acheteur envoie son lien
  trois jours trop tôt · **avant l'heure le cachet dort** (cire éteinte, aucun
  bouton), la page **DIT** quand elle s'ouvre et compte à rebours, **à l'heure
  la cire s'allume** et le bouton paraît **sans rechargement** · ⚠️ **le
  garde-fou est dans `ouvrir()`, pas sur le bouton** (le code secret appelle
  `ouvrir()` directement) · ⚠️ **heure de CALENDRIER, sans fuseau** : minuit,
  c'est minuit **sur le téléphone de celle qui lit** (un instant absolu ferait
  s'ouvrir à 22 h à Paris une lettre programmée à minuit depuis Cotonou) ·
  ⛔ **on ne promet JAMAIS le secret** (le texte est dans la page) : le cachet
  tient l'heure, c'est tout, et c'est déjà ce que personne d'autre ne vend ·
  ⛔ **NEBULA n'écrit jamais à la destinataire** → plus besoin du modèle Meta
  hors fenêtre de 24 h, et le risque de harcèlement disparaît par conception ·
  **2 défauts de caisse** : ⛔ **deux échelles de prix** (les occasions
  portaient un « dès 10 000 F » appliqué nulle part → on prenait « Demande en
  mariage · dès 10 000 F » au palier gratuit et on payait **0 F** ; l'occasion
  décide du TON, le palier décide du PRIX) et ⛔ **le palier gratuit passait par
  la caisse** (`aller(p.prix === 0 ? "e-paiement" : "e-paiement")`, deux branches
  identiques = intention écrite puis perdue : une lettre offerte affichait
  « Envoie exactement cette somme, au franc près » au-dessus d'un numéro Mobile
  Money) · ⛔ **le seuil n'était mesuré par rien** alors qu'une lettre programmée
  ne montre que lui pendant des heures : le même gris tient 4,8:1 sur le papier
  et **3,09:1 sur la nuit**, mesuré → `--gris-nuit` · **QC 82 → 115**, avec un
  **TÉMOIN** à chaque verrou (heure passée, palier payé) sans quoi un verrou
  resté fermé pour toujours passerait avec les honneurs.
- 🏦 **LA CAISSE ET L'ADRESSE SONT ÉCRITES ET CONTRÔLÉES le 2026-09-06**
  (marche à suivre : **`lepli/PAIEMENT.md`**) — ⏳ **rien n'est déployé**, il
  manque 5 réponses de Mongazi (le sous-domaine est tranché le 2026-09-09) : **schéma Supabase `lepli`** + **3 fonctions
  de bord** (déposer+payer · la notification signée qui **ouvre la lettre** ·
  servir+**retirer**), sur la forme éprouvée de PISTE · **`_shared/lettre.ts`
  porte TOUT ce qui décide**, en Web standard, donc essayable **sans clé, sans
  réseau et sans base** (`node --experimental-strip-types lepli/_qc_caisse.mjs`,
  **118 contrôles**) · **le constructeur parle enfin à la caisse** (il posait sa
  commande sur `window.LEPLI_COMMANDE` et elle n'allait nulle part) ·
  ⛔ **ON NE STOCKE JAMAIS LE HTML DU NAVIGATEUR** : une porte publique qui
  accepte du HTML et le sert sur notre domaine est un **hébergeur de pages
  arbitraires**, gratuit et anonyme — on stocke les **données**, la lettre est
  **rebâtie** depuis le gabarit (`_gabarit_ts.py` l'y recopie, un contrôle
  compare) · ⛔ **le prix ne vient jamais du navigateur**, ni le pied viral, ni
  le code secret : un contrôle **lit les deux barèmes** et refuse la moindre
  différence · ⛔ **l'écran « colle la référence de ton SMS » DISPARAÎT**, avec
  le numéro Mobile Money et le choix du réseau (c'était le moment le plus
  fragile de la chaîne) · ⛔ **le brouillon ne s'efface qu'après une réponse
  heureuse** · ⛔ **le retrait passe avant tout** (état, date, remboursement) ·
  ⚠️ **U+2028 EN CLAIR dans les regex qui doivent le neutraliser, 3e et 4e fois**
  (dans `lettre.ts`, puis dans le contrôle qui l'essaie) : **un fichier qui
  documente son propre piège doit être vérifié comme s'il le contenait** ·
  ⚠️ **2 sondes menteuses** (l'une lisait la ligne d'**import** au lieu de
  l'appel ; l'autre interrogeait `pg.url` **en boucle pendant une navigation**,
  or le contexte d'exécution est détruit → `wait_for_url`) et ⛔ **`localStorage`
  appartient à l'ORIGINE** (lu depuis la page de paiement, il rend le rangement
  d'un autre site) · ⚠️ **3 contrôles RETOURNÉS**, pas supprimés · ⚠️ **un
  3e sérialiseur = une 3e vérité** : Python écrivait `"a": 1` là où les deux
  autres écrivent `"a":1` → séparateurs compacts partout, et le contrôle exige
  **le même octet** des deux implémentations · **QC 115 → 127 + 118**
- ✒️ **LA PLUME ET 27 OCCASIONS (2026-10-16)** : l'agent écrit la lettre à la
  place de l'acheteur, qui la relit et la signe (option **500 F** qui s'ajoute à
  l'offre, **gratuite à essayer**, 3 versions par brouillon), à partir d'une
  **fiche** : questions à choix propres à l'occasion + un souvenir + « comment tu
  la veux ». **27 occasions en 4 familles** (ruptures de couple et d'amitié, fêtes
  des pères, Noël, Tabaski…), ⛔ **pas de deuil**. Sonnet 5.5, fiche gardée nulle
  part, réponse relue par le code. Essayée en vrai : injection ignorée, deuil
  déguisé refusé, 2 à 6 F la version. ⛔ **Le constructeur n'envoyait pas la clé
  publique Supabase** : 401 garanti au lancement, corrigé. QC **203 + 213**.
  ⚠️ **Le Coffret promet encore « la livraison WhatsApp à l'heure choisie »**,
  contraire à « NEBULA n'écrit jamais à la destinataire » : à trancher. Détail :
  `_memoire/conversations/2026-10-16-lepli-plume.md`.
- ⏳ **CE QUI RESTE** : **brancher** la caisse (5 commandes, `PAIEMENT.md`) et la
  plume (`ANTHROPIC_API_KEY` + `lepli-plume`) ·
  ⛔ **PAS de Render avec le SQLite de `vitrina/`** : le disque de Render
  s'efface à chaque déploiement (c'est ce qui avait fait disparaître les 2 PDF
  des partenaires) — un déploiement, et les lettres payées n'existent plus ·
  le **ménage des lettres expirées** (`lepli_menage()` existe, rien ne
  l'appelle) · le **lien « retirer cette lettre »** dans le pied (la porte
  existe, le bouton non) ·
  **le faire-part pour NOVEMBRE** (saison des mariages + retour de la diaspora,
  ticket 25 000 F), pas pour février (volume, petit ticket) · **critères
  d'arrêt au 1er décembre 2026**, écrits d'avance.
- ⏳ **Les 5 réponses qui n'appartiennent qu'à Mongazi** (le sous-domaine est
  tranché depuis le 2026-09-09 : `lepli.nebula-agency.online`) : le compte qui encaisse ·
  **un n8n tourne-t-il ailleurs, oui ou non** · la commission
  SasPay (elle décide de la marge d'un ticket à 2 000 F, écrite nulle part) ·
  qui relit le deuil · **le premier franc encaissé pour de vrai**.
- **Fait le 2026-09-03** : **la vidéo de démonstration**, composition
  `lepli-demo` dans `_studio-video/` (1080x1920, 30 s, `npm run rendu:lepli`).
  Six plans, **les six signatures du produit rejouées en React** et non
  photographiées : une capture ne montre pas un cachet qui se brise. ⛔ **Ne pas
  la publier en l'état** : elle promet « Elle l'ouvre à minuit pile. Pas
  avant. » et affiche `lepli.nebula-agency.online`, or **ni la remise à
  l'heure dite ni le serveur n'existent** au 2026-09-03. ✅ **Depuis le
  2026-09-06 la promesse est tenue** (la lettre porte le verrou) : il ne reste
  que l'adresse affichée, qui doit exister avant publication.
  ⛔ **Jamais de fondu enchaîné entre deux plans qui
  montrent du papier** : mesuré, deux feuilles à 50 % l'une sur l'autre
  ressemblent à une panne, pas à une transition (les plans partagent le même
  fond de nuit, donc la coupe est déjà invisible).
  Détail : `_memoire/conversations/2026-09-03-lepli-video-demo.md`.
- ⛔ **`</script>` écrit par un acheteur TUE la page** : les données atterrissent
  dans un bloc `<script>`, et **`json.dumps` ne protège pas de ça**. Toute
  sérialisation passe par **`lepli/_injecter.py`**, seul endroit, qui neutralise
  `</`, `<!--` et U+2028/U+2029. ⚠️ **Le commentaire qui documentait ce piège le
  contenait en clair** et fermait lui-même le bloc ; ⚠️ **la fonction qui
  neutralise U+2028 les portait en clair dans ses regex**. → **`node --check` sur
  le script en ligne avant d'écrire**, et se méfier d'un fichier qui documente
  son propre piège.
- ⛔ **Le seuil EST le produit** : une lettre livrée garde toujours son cachet.
  L'aperçu du constructeur s'ouvre (l'acheteur doit voir SES mots, c'est là que
  la vente se fait), mais **le drapeau d'aperçu ne part jamais dans la commande**,
  et un contrôle le vérifie.
- ⚠️ **Aucune police téléchargée, aucun appel réseau, `noindex`** : une lettre
  s'ouvre dans un taxi et n'a rien à faire dans un moteur. **Les photos sont des
  données (`data:`), jamais des liens** : un lien distant ferait dépendre la
  lettre d'un serveur et **fuiterait l'heure d'ouverture** vers un tiers.
- ⛔ **La sauvegarde du formulaire n'est pas un confort** : pour payer, l'acheteur
  QUITTE la page. Sans restauration au retour il perd son quart d'heure, ne
  recommence pas, et **on ne sait même pas que la vente a existé**.
- ✅ **AVANT LA PREMIÈRE VENTE : `lepli/CONDITIONS.md` est écrit** (le dossier
  classait ce risque en *critique* et notait qu'aucune des 5 références ne le
  traite) — adresse impossible à deviner, `X-Robots-Tag` en plus de la balise,
  expiration (7 jours offert / 1 an payé), aucune mesure d'audience, et
  **retrait sous 24 h à la demande de la personne visée, sans discuter, sans
  prévenir l'acheteur, sans rembourser** : ⚠️ **le pouvoir de retirer appartient
  à qui détient le lien**, ce qui est exactement l'ensemble des gens concernés.
  ⛔ **Jamais de MP3 hébergé** (contrefaçon). ⚠️ **Le deuil ne se décore pas** :
  sobriété totale, aucun emoji, relecture par quelqu'un qui vient d'enterrer un
  proche **avant** de le vendre, et c'est la condition d'ouverture de la ligne.
<!-- FIN HISTOIRE -->
