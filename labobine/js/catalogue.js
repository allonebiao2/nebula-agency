// LA BOBINE · la vidéo tirée d'un catalogue. On ne fabrique pas un film à part : on fabrique un PROJET ordinaire
// (la piste principale, les textes, les stickers, les effets, la musique), que le commerçant retouche ensuite
// comme n'importe quel montage. Aucun DOM ici : se teste dans Node.

import * as M from './model.js';

export const MODELES = {
  vitrine: { nom: 'La vitrine', note: 'Chaque produit en grand, son nom et son prix sur une étiquette.', duree: 2.5, transition: ['glisse', 0.35] },
  promo: { nom: 'La promo', note: "Le prix en grand, des flashs sur le rythme : l'énergie d'une annonce.", duree: 2, transition: ['flash', 0.3] },
  elegant: { nom: "L'élégante", note: 'Fondus lents, lettres fines, lumières douces : la mode, la beauté.', duree: 3, transition: ['fondu', 0.6] },
};
export const MAX_PRODUITS = 15;
export const DUREE_INTRO = 2;
export const DUREE_FIN = 3;

/** La durée estimée d'une vidéo, avant tout calage sur une musique. */
export const dureeEstimee = (n, modele) => DUREE_INTRO + n * (MODELES[modele] || MODELES.vitrine).duree + DUREE_FIN;

/** L'écart le plus courant entre deux temps (la médiane, qui ignore un temps manqué). */
export function periodeDe(temps) {
  const d = [];
  for (let i = 1; i < temps.length; i += 1) d.push(temps[i] - temps[i - 1]);
  if (!d.length) return 0;
  d.sort((a, b) => a - b);
  return d[Math.floor(d.length / 2)];
}

/** Combien de temps par photo, parmi 1, 2, 4 ou 8, pour approcher la durée voulue. */
export function choisirPas(temps, duree) {
  const per = periodeDe(temps);
  if (!(per > 0)) return 1;
  let mieux = 1;
  for (const pas of [1, 2, 4, 8]) if (Math.abs(pas * per - duree) < Math.abs(mieux * per - duree)) mieux = pas;
  return mieux;
}

const texte = (debut, duree, style, contenu, reglages = {}) => Object.assign(M.clipTexte(debut, style, contenu), { duree }, reglages);
const sticker = (debut, duree, forme, reglages) => Object.assign(M.clipSticker(debut, forme), { duree }, reglages);
const effet = (debut, duree, nom, intensite) => Object.assign(M.clipEffet(debut, nom), { duree, intensite });

/**
 * Fabrique le projet.
 * o = { format, maison, produits: [{ nom, prix, media, detoure }], modele, fond (média image), appel, contact,
 *       musique: { media, rythme } | null, couleurs: { accent, fond } }
 * Un produit sans photo (media null) passe en carte typographique sur le fond, jamais avec une image d'emprunt.
 */
export function fabriquerVideo(o) {
  const cle = MODELES[o.modele] ? o.modele : 'vitrine';
  const m = MODELES[cle];
  const p = M.nouveauProjet(o.format || '9:16', `${o.maison || 'Mes produits'} · vidéo`);
  const coul = { accent: '#ffd23f', fond: '#14110e', ...(o.couleurs || {}) };
  p.fond = { type: 'couleur', couleur: coul.fond };
  const ids = new Set([o.fond.id]);
  const pr = M.principale(p);
  const roles = new Map();
  const poser = (media, duree, role) => {
    const c = M.clipDepuisMedia(media, 0);
    c.sortie = duree;
    pr.clips.push(c);
    roles.set(c.id, role);
    ids.add(media.id);
    return c;
  };

  poser(o.fond, DUREE_INTRO, { type: 'intro' });
  for (const produit of o.produits.slice(0, MAX_PRODUITS)) {
    const c = poser(produit.media || o.fond, m.duree, { type: 'produit', produit });
    if (produit.media) {
      c.ajustement = produit.detoure || cle === 'elegant' ? 'adapter' : 'remplir';
      // une pièce détourée laisse la place, sous elle, à son nom et à son prix
      if (produit.detoure) { c.echelle = 0.76; c.cy = 0.43; }
      c.mouvement = 'avant';
    }
  }
  poser(o.fond, DUREE_FIN, { type: 'fin' });
  pr.clips.forEach((c, i) => { if (i > 0) c.transition = { type: m.transition[0], duree: m.transition[1] }; });
  M.tasserPrincipale(p);

  // la musique : son rythme cale chaque plan sur les temps
  let son = null;
  if (o.musique && o.musique.media) {
    son = M.clipDepuisMedia(o.musique.media, 0);
    ids.add(o.musique.media.id);
    M.poserSurPisteLibre(p, 'audio', son);
    if (Array.isArray(o.musique.rythme) && o.musique.rythme.length >= 4) {
      son.rythme = o.musique.rythme;
      if (o.musique.bpm) son.bpm = o.musique.bpm;
      M.calerSurRythme(p, choisirPas(o.musique.rythme, m.duree));
    }
  }
  const fin = M.dureeProjet({ pistes: [pr] });
  if (son) {
    son.sortie = Math.min(son.sortie, son.entree + fin);
    son.fonduSortie = Math.min(1.5, M.dureeClip(son) / 3);
  }

  // ce qui se pose par-dessus suit les plans tels qu'ils sont APRÈS le calage
  const dessus = { texte: [], sticker: [], effet: [] };
  const plans = pr.clips.map((c) => ({ ...roles.get(c.id), debut: c.debut, duree: M.dureeClip(c) }));
  const produits = plans.filter((x) => x.type === 'produit');
  const debutProduits = produits.length ? produits[0].debut : 0;
  const finProduits = produits.length ? produits[produits.length - 1].debut + produits[produits.length - 1].duree : 0;
  const prixLong = (s) => String(s || '').length > 14;
  const contact = String(o.contact || '').trim();
  const appel = String(o.appel || '').trim() || 'Commandez sur WhatsApp';

  for (const x of plans) {
    const d = x.duree;
    if (x.type === 'intro') {
      if (cle === 'promo') {
        dessus.sticker.push(sticker(x.debut, d, 'promo', { cx: 0.5, cy: 0.4, echelle: 0.62, boucle: son && son.rythme ? 'rythme' : 'pulse' }));
        dessus.texte.push(texte(x.debut, d, 'affiche', o.maison || '', { cy: 0.7 }));
      } else if (cle === 'elegant') {
        dessus.texte.push(texte(x.debut, d, 'elegant', o.maison || '', { cy: 0.48, taille: 0.07 }));
      } else {
        dessus.texte.push(texte(x.debut, d, 'titre', o.maison || '', { cy: 0.46 }));
      }
    } else if (x.type === 'produit') {
      const pd = x.produit;
      const prix = String(pd.prix || '').trim();
      const sansPhoto = !pd.media;
      if (cle === 'promo') {
        dessus.texte.push(texte(x.debut, d, sansPhoto ? 'affiche' : 'pastille', pd.nom, sansPhoto ? { cy: 0.42 } : { cy: 0.13 }));
        if (prix) dessus.texte.push(texte(x.debut, d, 'affiche', prix, { cy: 0.8, taille: prixLong(prix) ? 0.06 : 0.085, couleur: '#ffd23f' }));
      } else if (cle === 'elegant') {
        dessus.texte.push(texte(x.debut, d, 'elegant', pd.nom, { cy: sansPhoto ? 0.46 : 0.84, taille: sansPhoto ? 0.065 : 0.05 }));
        if (prix) dessus.texte.push(texte(x.debut, d, 'elegant', prix, { cy: sansPhoto ? 0.56 : 0.9, police: 'Instrument Sans', poids: 600, taille: 0.032, couleur: coul.accent }));
      } else {
        dessus.texte.push(texte(x.debut, d, sansPhoto ? 'titre' : 'legende', pd.nom, sansPhoto ? { cy: 0.42 } : { cy: 0.86 }));
        if (prix && !prixLong(prix)) {
          dessus.sticker.push(sticker(x.debut, d, 'prix', { texte: prix, cx: 0.7, cy: sansPhoto ? 0.58 : pd.detoure ? 0.74 : 0.7, echelle: 0.44, rotation: -6 }));
        } else if (prix) {
          dessus.texte.push(texte(x.debut, d, 'pastille', prix, { cy: sansPhoto ? 0.58 : 0.74 }));
        }
      }
    } else if (x.type === 'fin') {
      const style = cle === 'promo' ? 'affiche' : cle === 'elegant' ? 'elegant' : 'titre';
      dessus.texte.push(texte(x.debut, d, style, appel, { cy: contact ? 0.42 : 0.5 }));
      // le numéro n'apparaît que s'il est connu : jamais un numéro deviné
      if (contact) {
        dessus.texte.push(texte(x.debut, d, cle === 'elegant' ? 'elegant' : 'pastille', contact,
          cle === 'elegant' ? { cy: 0.56, police: 'Instrument Sans', poids: 600, taille: 0.04, couleur: coul.accent } : { cy: 0.57 }));
      }
    }
  }
  if (produits.length) {
    const d = finProduits - debutProduits;
    if (cle === 'promo') {
      dessus.effet.push(effet(debutProduits, d, 'battement', 0.8));
      dessus.effet.push(effet(debutProduits, d, 'flash', 0.55));
    } else if (cle === 'elegant') {
      dessus.effet.push(effet(0, fin, 'bokeh', 0.45));
    }
  }
  for (const [genre, liste] of Object.entries(dessus)) {
    if (!liste.length) continue;
    // une piste par couche, mais chaque clip garde sa place exacte : poserSurPisteLibre range les chevauchements
    for (const c of liste) M.poserSurPisteLibre(p, genre, c);
  }
  p.medias = [...ids];
  // la vignette du projet, à l'accueil : le premier produit photographié, pas le fond
  const premier = o.produits.find((x) => x.media);
  if (premier) p.couverture = premier.media.id;
  p.catalogue = { maison: o.maison || '', modele: cle, produits: produits.length };
  return p;
}
