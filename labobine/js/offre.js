// LA BOBINE · l'offre. Comme chez les grands éditeurs, tout s'essaie librement ; c'est la sortie qui se paie :
// le gratuit exporte avec le filigrane, en 720p ou 1080p, à 24, 25 ou 30 images par seconde.
// Le paiement (Mobile Money) arrive à la vague 4 : d'ici là, personne n'est Pro, et aucune porte dérobée
// ne permet de le devenir depuis le navigateur.

export const OFFRES = {
  gratuit: { nom: 'Gratuit', qualites: [720, 1080], cadences: [24, 25, 30], filigrane: true },
  pro: { nom: 'Pro', qualites: [720, 1080, 2160], cadences: [24, 25, 30, 60], filigrane: false },
};

/** Ce que l'abonnement Pro débloquera, dans l'ordre où on le présente. */
export const AVANTAGES_PRO = [
  'Export sans filigrane',
  'Export en 4K',
  '60 images par seconde',
  'Crédits mensuels pour les fonctions IA',
];

import { proActif } from './compte.js';

/** Le droit Pro vient du serveur (paiement confirmé par le webhook signé), relu à chaque ouverture. */
export const estPro = () => proActif();

export const offreCourante = () => (estPro() ? OFFRES.pro : OFFRES.gratuit);
