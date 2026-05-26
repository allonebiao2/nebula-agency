# 💛 Témoignages clients — galerie manuelle

Dossier des **photos et captures de témoignages** affichées dans la section
« Témoignages clients » du hub `index.html`.

## Comment ajouter un nouveau témoignage

### 1. Déposer la photo dans ce dossier

- **Formats** : `.jpg`, `.png`, `.webp` (préférés)
- **Poids max** : 600 Ko par image (compresser au besoin via [tinypng.com](https://tinypng.com))
- **Nommage** : kebab-case explicite, ex :
  - `avant-apres-marie-k-2026-04.jpg`
  - `capture-temoignage-luxury-club-2026-05.jpg`
  - `photo-resultat-peeling-2026-03.jpg`

### 2. Ajouter l'entrée dans `index.html`

Ouvrir `clients/04-luxury-skin-clinic/index.html`, chercher la constante
`TESTIMONIALS` (vers la ligne ~1230), et y pousser un nouvel objet :

```js
var TESTIMONIALS=[
  // Le plus récent en premier
  {
    src:'assets/images/temoignages/avant-apres-marie-k-2026-04.jpg',
    type:'avant-apres',         // 'photo' | 'capture' | 'avant-apres'
    caption:'Marie K. — Résultat après 6 séances de Peeling Glow',
    date:'2026-04'
  },
  // ... autres
];
```

### 3. C'est tout

La galerie se met à jour automatiquement au prochain rechargement.

## Catégories disponibles

| `type` | Label affiché | Pour quel contenu |
|---|---|---|
| `photo` | Photo résultat | Photo de la cliente après son soin |
| `capture` | Capture de discussion | Screenshot WhatsApp avec la cliente |
| `avant-apres` | Avant / Après | Comparatif visuel des résultats |

## Bon à savoir

- **Modération préalable** : Mme Sabrina doit avoir l'accord de la cliente
  avant de publier sa photo ou la capture de leur discussion.
- **Aucun visage non flouté** sans accord écrit/audio explicite.
- **Captures WhatsApp** : flouter ou cacher le numéro de téléphone, le nom
  de famille et la photo de profil de la cliente.
- **Suppression** : retirer l'objet du tableau `TESTIMONIALS` puis supprimer
  le fichier image du dossier.

---

*Galerie statique — pas de backend nécessaire. NEBULA Agency · 2026*
