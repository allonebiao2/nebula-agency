/* HILLARY M. STYL · ce que l'on dit dans le salon.

   ⛔ TROIS RÈGLES, et elles priment sur le style :
   1. TOUT CHIFFRE vient des DONNEES (lues dans la vitrine) : prix, délais,
      express, frais par pays, nombre de mesures. Aucun n'est écrit en dur.
      Si une donnée manque, la réplique qui en a besoin disparaît.
   2. Les visiteuses sont des VISITEUSES INVENTÉES, pas des clientes : elles
      découvrent, elles s'interrogent, elles aiment ou pas une robe. Elles ne
      disent JAMAIS « elle m'a cousu… », « je recommande » : ce serait un faux avis.
   3. Ce qu'on ne sait pas, on ne le dit pas. Le TikTok, les événements, le
      quartier n'apparaissent que s'ils sont dans faits.json.

   Les répliques d'Hillary sont écrites dans le ton d'une maison, en attendant
   SES mots à elle (monde/QUESTIONNAIRE-HILLARY.md) : elles seront remplacées. */
import { fcfa, libDelai } from '../../socle/boutique.js';

export const PERSONNES = {
  hillary: { nom: 'Hillary', couleur: '#ff8cc6', initiales: 'H' },
  afi: { nom: 'Afi', couleur: '#8fc3ff', initiales: 'A' },
  senami: { nom: 'Sènami', couleur: '#ffc061', initiales: 'S' },
  maman: { nom: 'Maman Sènami', couleur: '#9be3b7', initiales: 'M' },
};

const pick = (a) => a[Math.floor(Math.random() * a.length)];
const SEMAINES = ['', 'une semaine', 'deux semaines', 'trois semaines', 'quatre semaines'];
const enMots = (j) => (j % 7 === 0 && SEMAINES[j / 7] ? SEMAINES[j / 7] : `${j} jours`);

/* ---------- les faits de la maison, CALCULÉS ---------- */
export function faitsMaison(D) {
  const pieces = D.pieces.filter(p => p.prix != null);
  const libre = D.pieces.find(p => p.typeLibre);
  const normaux = [...new Set(pieces.map(p => p.jmax))];
  const exMin = Math.min(...D.pieces.filter(p => p.expMin != null).map(p => p.expMin));
  const exMax = Math.max(...D.pieces.filter(p => p.expMax != null).map(p => p.expMax));
  const parPrix = [...pieces].sort((a, b) => a.prix - b.prix);
  const fr = D.pays.find(p => p.id === 'fr'), bj = D.pays.find(p => p.id === 'bj');
  const ceremonie = pieces.filter(p => /c[ée]r[ée]monie/i.test(p.tag || '') && p.img);
  const ville = pieces.filter(p => !/c[ée]r[ée]monie/i.test(p.tag || '') && p.img);
  const main = pieces.filter(p => /fait main/i.test(p.tag || ''));
  const m = D.mesures;
  return {
    n: pieces.length, libre, normal: normaux.length === 1 ? normaux[0] : null, exMin, exMax,
    moinsCher: parPrix[0], plusCher: parPrix[parPrix.length - 1], fr, bj, ceremonie, ville, main, parPrix,
    nbPays: D.pays.filter(p => p.id !== 'other').length,
    mesRobeDroite: m.robe_droite ? m.robe_droite.champs.length : null, mesPantalon: m.pantalon ? m.pantalon.champs.length : null,
    coupDeCoeur: pieces.find(p => /sir[eè]ne/i.test(p.nom) && p.img) || ceremonie[0] || null,
    tiktok: D.faits && D.faits.tiktok && D.faits.tiktok.compte ? D.faits.tiktok : null,
    histoire: (D.faits && D.faits.histoire) || null, vision: (D.faits && D.faits.vision) || null, sensNom: (D.faits && D.faits.sens_nom) || null,
    evenements: (D.faits && D.faits.evenements) || [],
  };
}

const phrase1 = (s) => { const m = String(s || '').match(/^.*?[.!?](\s|$)/); return m ? m[0].trim() : String(s || ''); };

/* ================================================================
   HILLARY, AU COMPTOIR
   ================================================================ */
export function dialoguesHillary({ D, F, boutique, ctx, monde }) {
  const salut = (c) => {
    const h = c.ciel.heure.h;
    const base = c.visites > 1 && !c.vuHillary ? pick(['Re-bonjour ! Contente de te revoir.', 'Tiens, te revoilà ! Ça me fait plaisir.'])
      : h < 12 ? pick(['Bonjour, et bienvenue chez HILLARY M. STYL !', 'Bonjour ! Entre, regarde, touche les tissus.'])
      : h < 18 ? pick(['Bon après-midi, bienvenue chez HILLARY M. STYL !', 'Bienvenue ! Installe-toi, prends ton temps.'])
      : pick(['Bonsoir ! Entre, tu es chez toi.', 'Bonsoir, bienvenue à la maison.']);
    const meteo = c.ciel.pluie > 0.5 ? ' Il pleut fort dehors, mets-toi à l\'aise.' : c.ciel.pluie > 0 ? ' Un peu de pluie ? Ici on est au sec.' : '';
    return base + meteo;
  };
  const menu = (c) => [
    { t: 'Conseille-moi une tenue', va: 'h_conseil' },
    c.quete === 1 ? { t: 'Une tenue en moins de cinq jours, c\'est possible ?', va: 'h_quete' } : { t: 'Les délais et la livraison', va: 'h_delais' },
    { t: 'Parle-moi de la maison', va: 'h_maison' },
    boutique.panier().length ? { t: 'Valider ma commande', va: 'h_cest_tout' } : { t: 'Parle-moi de toi', va: 'h_toi' },
  ];

  /* présenter une pièce : la réplique, puis sa fiche, puis la suite selon le choix */
  const presenter = (liste, i = 0) => (c) => {
    if (!liste.length) return { qui: 'hillary', dit: ['Je n\'ai rien à te montrer dans ce style pour l\'instant.'], suite: 'h_menu' };
    const p = liste[i % liste.length];
    const intro = i === 0 ? pick(['Regarde celle-ci.', 'Je te montre celle-là.', 'Tiens, celle-ci, je l\'aime beaucoup.']) : pick(['Et celle-ci ?', 'Alors regarde plutôt celle-là.', 'Une autre, alors.']);
    return {
      qui: 'hillary',
      dit: [`${intro} ${p.nom}. ${phrase1(p.ds)}`,
        `${fcfa(p.prix)}, prête en ${enMots(p.jmax)}.${p.expPrix != null ? ` En express, ${libDelai(p.expMin, p.expMax)} pour ${fcfa(p.expPrix)}.` : ''}`],
      alors: async () => {
        monde.montrerPiece(p.id);
        const r = await boutique.ouvrirFiche(p.id, { mode: 'presentation' });
        if (r.action === 'normal' || r.action === 'express') { boutique.ajouter(p.id, { express: r.action === 'express', typeMesure: r.typeMesure }); return 'h_cest_tout'; }
        if (r.action === 'autre') return presenter(liste, i + 1);
        return 'h_encore';
      },
    };
  };

  return {
    hillary: (c) => {
      const premier = !c.vuHillary; c.vuHillary = true;
      return { qui: 'hillary', dit: premier ? [salut(c), 'Qu\'est-ce qui te ferait plaisir ?'] : [pick(['Oui ? Je t\'écoute.', 'Dis-moi tout.', 'Je suis là.'])], choix: menu(c) };
    },
    h_menu: (c) => ({ qui: 'hillary', dit: [pick(['Autre chose ?', 'Je t\'écoute.'])], choix: menu(c) }),
    h_encore: (c) => ({ qui: 'hillary', dit: ['Pas de souci. Tu veux voir autre chose ?'], choix: [
      { t: 'Oui, conseille-moi', va: 'h_conseil' }, { t: 'Non, je regarde encore', va: 'h_au_revoir' },
      boutique.panier().length ? { t: 'Valider ma commande', va: 'h_cest_tout' } : null].filter(Boolean) }),
    h_conseil: (c) => ({ qui: 'hillary', dit: ['Avec plaisir. C\'est pour quelle occasion ?'], choix: [
      { t: 'Une cérémonie', action: () => { c.apprendre && c.apprendre('ceremonie'); }, va: presenter(F.ceremonie) },
      { t: 'La ville, tous les jours', va: presenter(F.ville) },
      { t: 'Le plus abordable', va: presenter(F.parPrix.filter(p => p.img)) },
      F.libre ? { t: 'Quelque chose d\'unique', va: 'h_libre' } : null].filter(Boolean) }),
    h_libre: () => ({ qui: 'hillary', savoir: 'creation_libre', dit: [
      'Alors on part de ton idée. C\'est la création libre : tu choisis le vêtement, on parle du tissu et des détails, et je te fais un prix.',
      `Compte ${libDelai(F.libre.jmin, F.libre.jmax)}, ou ${libDelai(F.libre.expMin, F.libre.expMax)} en express.`],
      alors: async () => {
        const r = await boutique.ouvrirFiche(F.libre.id, { mode: 'presentation' });
        if (r.action === 'normal' || r.action === 'express') { boutique.ajouter(F.libre.id, { express: r.action === 'express', typeMesure: r.typeMesure }); return 'h_cest_tout'; }
        return 'h_encore';
      } }),
    h_cest_tout: (c) => ({ qui: 'hillary', dit: [pick(['C\'est noté !', 'Très bon choix.', 'Elle va t\'aller à merveille.']) + ' C\'est tout ?'], choix: [
      { t: 'Oui, c\'est tout', va: 'h_valider' },
      { t: 'Montre-moi autre chose', va: 'h_conseil' },
      { t: 'Je regarde encore un peu', va: 'h_au_revoir_sac' }] }),
    h_valider: () => ({ qui: 'hillary', dit: ['C\'est parfait. Valide ta commande ici, et on se retrouve sur WhatsApp.'],
      alors: () => { setTimeout(() => boutique.ouvrirCadran(), 450); return null; } }),
    h_au_revoir: () => ({ qui: 'hillary', dit: [pick(['Prends ton temps, je suis là.', 'Regarde tranquillement. Si une pièce te parle, touche-la.'])] }),
    h_au_revoir_sac: () => ({ qui: 'hillary', dit: ['Prends ton temps. Ton sac t\'attend, en haut à droite.'] }),
    h_maison: () => ({ qui: 'hillary', savoir: ['sur_mesure', 'mesures', 'devises'], dit: [
      `Ici, tout est cousu sur mesure : ${F.n} créations${F.libre ? ', et une création libre, sur devis, pour ton idée à toi' : ''}.`,
      F.mesRobeDroite && F.mesPantalon ? `Les mesures dépendent du vêtement, pas de la personne : une robe droite, c'est ${F.mesRobeDroite} mesures, un pantalon ${F.mesPantalon}.` : '',
      'Mes prix sont en francs CFA, en euros et en dollars.'].filter(Boolean),
      choix: [
        { t: 'Et le paiement ?', va: 'h_paiement' },
        { t: 'Comment je donne mes mesures ?', va: 'h_mesures' },
        { t: 'Les pièces faites main ?', va: 'h_main', si: () => F.main.length > 0 },
        { t: 'Merci !', va: 'h_menu' }] }),
    h_paiement: () => ({ qui: 'hillary', savoir: ['paiement', 'prevenu'], dit: ['Par Mobile Money, après confirmation sur WhatsApp. Rien ne se paie avant.', 'Je t\'écris dès que la commande est validée, puis je t\'écris ou je t\'appelle quand ta tenue est prête.'], suite: 'h_menu' }),
    h_mesures: () => ({ qui: 'hillary', savoir: 'mesures', dit: [D.aide_mesures, 'Une mesure que tu ne connais pas, on la prend ensemble. Personne n\'est bloqué.'], suite: 'h_menu' }),
    h_main: () => ({ qui: 'hillary', savoir: 'fait_main', dit: [`Celles-là : ${F.main.map(p => p.nom).join(' et ')}. ${phrase1((F.main.find(p => /main/i.test(p.ds || '')) || F.main[0]).ds)}`], suite: 'h_menu' }),
    h_tiktok: () => ({ qui: 'hillary', savoir: 'tiktok', dit: [`Oui ! Je suis sur TikTok : ${F.tiktok.compte}. Abonne-toi !`],
      alors: () => { monde.ouvrirTiktok(); }, suite: 'h_menu' }),
    h_delais: () => ({ qui: 'hillary', savoir: ['delais', 'livraison'], dit: [
      F.normal ? `Mes pièces sont prêtes en ${enMots(F.normal)}. Pressé ? L'express, c'est ${libDelai(F.exMin, F.exMax)} selon la pièce, avec un prix propre à chacune.` : `L'express, c'est ${libDelai(F.exMin, F.exMax)} selon la pièce.`,
      `Pour récupérer ta tenue : ${D.atelier.adresse.replace(' · ', '. ')}.`,
      F.bj && F.fr ? `Ou je l'expédie : ${fcfa(F.bj.frais)} au Bénin, et jusqu'en France pour ${fcfa(F.fr.frais)}. ${F.nbPays} pays en tout.` : ''].filter(Boolean),
      suite: 'h_menu' }),
    /* « Parle-moi de toi » : son histoire, sa vision, le sens du nom n'apparaissent
       qu'une fois ÉCRITS par elle dans faits.json (questionnaire) ; le salon, toujours */
    h_toi: () => ({ qui: 'hillary', dit: ['Moi ? Je couds, et j\'aime ça. Qu\'est-ce que tu veux savoir ?'], choix: [
      { t: 'Comment tout a commencé ?', va: 'h_histoire', si: () => !!F.histoire },
      { t: 'Ta vision ?', va: 'h_vision', si: () => !!F.vision },
      { t: 'Que veut dire le « M. » ?', va: 'h_nom', si: () => !!F.sensNom },
      F.tiktok ? { t: 'Tu es sur TikTok ?', va: 'h_tiktok' } : null,
      { t: 'Et ce salon en 3D ?', va: 'h_salon' },
      { t: 'Merci !', va: 'h_menu' }].filter(Boolean) }),
    h_histoire: () => ({ qui: 'hillary', savoir: 'histoire', dit: [F.histoire], suite: 'h_toi' }),
    h_vision: () => ({ qui: 'hillary', savoir: 'vision', dit: [F.vision], suite: 'h_toi' }),
    h_nom: () => ({ qui: 'hillary', savoir: 'nom', dit: [F.sensNom], suite: 'h_toi' }),
    h_salon: () => ({ qui: 'hillary', savoir: 'salon', dit: ['Ce salon ? C\'est NEBULA Agency qui l\'a construit, ici à Cotonou. Comme ça, on peut visiter la maison depuis n\'importe où, même depuis Paris.'], suite: 'h_toi' }),
    /* la course d'Afi */
    h_quete: (c) => {
      const p = [...F.ceremonie].sort((a, b) => (a.expMax ?? 99) - (b.expMax ?? 99))[0];
      c.quete = 2; monde.objectif('Retourner voir Afi pour lui dire ce qu\'a répondu Hillary.');
      return { qui: 'hillary', savoir: 'express_paris', dit: [
        `Oui, en express : ${libDelai(F.exMin, F.exMax)} selon la pièce.`,
        p ? `La ${p.nom}, par exemple : ${libDelai(p.expMin, p.expMax)}, ${fcfa(p.expPrix)}.` : '',
        F.fr ? `Et si elle préfère la recevoir à Paris, je l'expédie : ${fcfa(F.fr.frais)}, ${F.fr.achem} jours de route.` : '',
        'Dis-lui de venir me voir.'].filter(Boolean), suite: 'h_menu' };
    },
  };
}

/* ================================================================
   LES VISITEUSES, QUAND ON LEUR PARLE
   ================================================================ */
export function dialoguesVisiteuses({ D, F, ctx, monde }) {
  return {
    /* Afi vient d'elle-même : la course */
    afi_course: (c) => ({ qui: 'afi', dit: [
      'Pardon, excuse-moi… Tu connais la maison ?',
      'Je suis venue de Paris pour un mariage à Ouidah samedi, et je repars dans cinq jours. J\'aimerais tellement une tenue d\'ici.',
      'Tu crois qu\'elle peut coudre quelque chose aussi vite ?'],
      choix: [
        { t: 'Je vais demander à Hillary', action: () => { c.quete = 1; monde.objectif('La course d\'Afi : demander à Hillary si une tenue peut être prête en moins de cinq jours.', 'Le comptoir est au fond.'); }, va: 'afi_merci' },
        { t: 'Regarde les délais sur les fiches', va: 'afi_fiches' },
        { t: 'Désolé, je ne fais que passer', va: 'afi_tant_pis' }] }),
    afi_merci: () => ({ qui: 'afi', dit: ['Oh, merci ! Je t\'attends ici.'] }),
    afi_fiches: (c) => ({ qui: 'afi', dit: ['Ah oui, c\'est écrit sur chaque pièce… Mais j\'aimerais l\'entendre de sa bouche. Tu peux lui demander ?'],
      choix: [{ t: 'D\'accord, j\'y vais', action: () => { c.quete = 1; monde.objectif('La course d\'Afi : demander à Hillary si une tenue peut être prête en moins de cinq jours.', 'Le comptoir est au fond.'); }, va: 'afi_merci' }, { t: 'Pas maintenant', va: 'afi_tant_pis' }] }),
    afi_tant_pis: () => ({ qui: 'afi', dit: ['Pas de souci. Bonne visite !'] }),
    afi: (c) => {
      if (c.quete === 1) return { qui: 'afi', dit: ['Alors ? Tu as pu lui demander ?'], choix: [{ t: 'Pas encore, j\'y vais', va: null }] };
      if (c.quete === 2) {
        c.quete = 3; monde.objectif('La course d\'Afi : réussie.', null, true); monde.afiAuComptoir();
        return { qui: 'afi', savoir: 'express_paris', dit: [`C'est vrai ? ${libDelai(F.exMin, F.exMax)} en express ? Et elle expédie à Paris en plus ?`, 'Tu me sauves. Je vais lui parler tout de suite. Merci !'] };
      }
      const ligneAfi = pick([
        'À Paris, on me demande toujours d\'où viennent mes tenues. Cette fois, j\'aurai une réponse.',
        'Les prix sont aussi en euros et en dollars, c\'est pratique pour moi.',
        'Je regarde surtout les pièces de cérémonie. Pour samedi.']);
      return { qui: 'afi', savoir: /euros/.test(ligneAfi) ? 'devises' : undefined, dit: [ligneAfi],
        choix: [{ t: 'Bonne chance pour samedi !', va: null }, { t: 'Tu as vu la robe au centre ?', va: 'afi_heros' }] };
    },
    afi_heros: () => ({ qui: 'afi', dit: [F.plusCher ? `La ${F.plusCher.nom} ? ${phrase1(F.plusCher.ds)} Elle ne passe pas inaperçue.` : 'Celle du centre ? Magnifique.'] }),

    senami: (c) => {
      if (F.tiktok && F.tiktok.derniere_video && F.tiktok.derniere_video.resume) {
        return { qui: 'senami', dit: [
          `Tu suis ${F.tiktok.compte} sur TikTok ? Sa dernière vidéo… ${F.tiktok.derniere_video.resume} Franchement, ça m'a choquée !`,
          'Tu devrais t\'abonner.'],
          choix: [{ t: 'Montre-moi', action: () => monde.ouvrirTiktok() }, { t: 'Je m\'abonne', action: () => monde.ouvrirTiktok(true) }, { t: 'Pas trop TikTok, moi', va: 'senami_pas_tiktok' }] };
      }
      return { qui: 'senami', dit: [pick([
        'J\'ai une cérémonie dans dix jours. Maman veut du sur-mesure, moi je veux que ce soit prêt à temps.',
        F.coupDeCoeur ? `Tu as vu la ${F.coupDeCoeur.nom} ? ${phrase1(F.coupDeCoeur.ds)} Je suis tombée dedans.` : 'Je ne sais pas laquelle choisir.'])],
        choix: [
          { t: 'Deux semaines, c\'est le délai normal', si: () => F.normal != null, va: 'senami_delai' },
          { t: 'Il y a l\'express', va: 'senami_express' },
          { t: 'Elle est belle, oui', va: null }] };
    },
    senami_delai: () => ({ qui: 'senami', savoir: 'delais', dit: [`${F.normal} jours ? Hein… Alors pour moi ce sera l'express. ${libDelai(F.exMin, F.exMax)}, Maman sera contente.`] }),
    senami_express: () => ({ qui: 'senami', savoir: 'delais', dit: [`${libDelai(F.exMin, F.exMax)} en express ? Parfait. Il faut que je montre ça à Maman.`] }),
    senami_pas_tiktok: () => ({ qui: 'senami', dit: ['Hein ? Tu rates quelque chose !'] }),

    maman: () => ({ qui: 'maman', dit: [pick([
      'De mon temps, on allait chez la couturière du quartier avec son pagne sous le bras. Ici, regarde : tout est expliqué.',
      'Ma fille trouve qu\'on prend trop de mesures. Moi je dis que c\'est ça, le vrai sur-mesure.'])],
      choix: [
        { t: 'On peut donner ses mesures soi-même ?', va: 'maman_mesures' },
        F.mesRobeDroite ? { t: 'Combien de mesures pour une robe ?', va: 'maman_combien' } : null,
        { t: 'Bonne journée, Maman', va: null }].filter(Boolean) }),
    maman_mesures: () => ({ qui: 'maman', savoir: 'mesures', dit: ['Oui, on peut, ou se faire aider. Et ce qu\'on ne connaît pas, Hillary le prend avec nous. C\'est écrit au comptoir.'] }),
    maman_combien: () => ({ qui: 'maman', savoir: 'mesures', dit: [`Pour une robe droite, ${F.mesRobeDroite} mesures. Pour un pantalon, ${F.mesPantalon}. Ça dépend du vêtement, pas de la personne. Voilà.`] }),
  };
}

/* ================================================================
   CE QU'ELLES SE DISENT ENTRE ELLES (on le lit quand on est près)
   Une conversation n'est jamais dite deux fois dans une même visite.
   ================================================================ */
export function conversations(D, F) {
  return (c) => {
    const L = [];
    const add = (id, qui, lignes, si, savoir) => L.push({ id, qui, lignes: lignes.map(([q, t]) => ({ qui: q, t })), si, savoir });
    add('mesures', ['senami', 'maman'], [
      ['senami', 'Maman, il y a vraiment beaucoup de mesures pour une robe…'],
      ['maman', F.mesRobeDroite ? `${F.mesRobeDroite} pour une robe droite. C'est comme ça qu'on coud bien.` : 'C\'est comme ça qu\'on coud bien.'],
      ['senami', 'Et si je ne connais pas mon tour de hanche ?'],
      ['maman', 'On le prend ensemble, avec elle. Arrête de t\'inquiéter.']], null, 'mesures');
    add('euros', ['afi', 'maman'], [
      ['afi', 'Bonjour Maman. Vous savez si on peut payer depuis la France ?'],
      ['maman', 'Bonjour ma fille. Mobile Money, je crois. Demande-lui au comptoir.'],
      ['afi', 'Les prix sont aussi en euros, regardez : c\'est rare.']], null, 'devises');
    if (F.fr) add('paris', ['afi', 'senami'], [
      ['senami', 'Tu viens d\'où, toi ? Ton accent…'],
      ['afi', 'De Paris. Enfin, de Cotonou d\'abord. Je suis rentrée pour un mariage.'],
      ['senami', `Elle expédie en France, tu sais. ${F.fr.achem} jours de route.`],
      ['afi', 'Sérieux ? Alors je reviendrai… par WhatsApp.']], null, 'livraison');
    if (F.coupDeCoeur) add('coup_de_coeur', ['senami', 'afi'], [
      ['senami', `Celle-là, c'est la ${F.coupDeCoeur.nom}. ${phrase1(F.coupDeCoeur.ds)}`],
      ['afi', 'Elle est sublime. Mais pour un mariage à Ouidah, il fait chaud…'],
      ['senami', 'Tu la portes le soir. Le soir, tout le monde danse.']]);
    add('wax', ['maman', 'senami'], [
      ['maman', 'Regarde ce wax sur l\'étagère. Ta tante avait le même en 1998.'],
      ['senami', 'Maman, tout le monde a eu ce wax en 1998.'],
      ['maman', 'Justement. Ça revient toujours, le beau.']]);
    add('fait_main', ['afi', 'maman'], [
      ['afi', F.main.length ? `L'${F.main[0].nom} est fait main, c'est écrit.` : 'Tout est fait ici, à l\'atelier ?'],
      ['maman', 'Fait main… On voit la différence au toucher, ma fille.']], () => F.main.length > 0);
    add('pluie', ['afi', 'senami'], [
      ['afi', 'Il pleut, il pleut… À Paris, la pluie est fine. Ici, elle tombe d\'un coup.'],
      ['senami', 'C\'est la pluie de Cotonou. Dans vingt minutes, il fera soleil.'],
      ['afi', 'J\'avais oublié le bruit sur la tôle.']], () => c.ciel.pluie > 0);
    add('zem', ['maman', 'senami'], [
      ['maman', 'On a bien fait de venir avant la pluie. En zem, avec cette eau…'],
      ['senami', 'Maman, tu dis ça à chaque fois.']], () => c.ciel.pluie > 0);
    add('chaleur', ['senami', 'maman'], [
      ['senami', 'Il fait bon ici. Dehors, je fondais.'],
      ['maman', 'C\'est pour ça qu\'on choisit les tissus légers pour la journée.']], () => c.ciel.pluie === 0 && c.ciel.jour > 0.6);
    add('soir', ['afi', 'maman'], [
      ['afi', 'Il est déjà tard. Elle ferme à quelle heure ?'],
      ['maman', 'Ici, c\'est le salon de la maison : on peut regarder à toute heure. Pour la commande, c\'est sur WhatsApp.']], () => c.ciel.nuit > 0.6);
    add('harmattan', ['maman', 'afi'], [
      ['maman', 'Avec l\'harmattan, la lumière devient toute blanche.'],
      ['afi', 'Et la poussière partout. Je l\'avais oubliée, celle-là.']], () => c.ciel.brume > 0.3);
    if (F.moinsCher) add('budget', ['senami', 'maman'], [
      ['senami', `Maman, il y en a à partir de ${fcfa(F.moinsCher.prix)}.`],
      ['maman', 'Et pour la cérémonie, on ne compte pas. Enfin… un peu quand même.']]);
    add('joueur', ['senami', 'afi'], [
      ['senami', 'Tu as vu, le visiteur là-bas ? Il regarde partout.'],
      ['afi', 'Comme moi la première fois. On ne sait pas où donner de la tête.']]);
    add('maman_afi', ['maman', 'afi'], [
      ['maman', 'Vous êtes de quel quartier, ma fille ?'],
      ['afi', 'J\'ai grandi à Akpakpa. Mais ça fait dix ans que je suis partie.'],
      ['maman', 'Dix ans… Cotonou a changé, hein ?'],
      ['afi', 'Un peu. Pas les embouteillages.']]);
    if (F.tiktok && F.tiktok.derniere_video && F.tiktok.derniere_video.resume) add('tiktok', ['senami', 'maman'], [
      ['senami', `Maman, tu as vu la dernière vidéo de ${F.tiktok.compte} ?`],
      ['maman', 'Encore ton TikTok…'],
      ['senami', `${F.tiktok.derniere_video.resume} Je te jure, j'étais choquée !`]]);
    return L;
  };
}

/* ================================================================
   LE CARNET : ce que l'on peut apprendre de la maison
   ⛔ Un savoir sans texte (donnée absente) n'est pas compté.
   ================================================================ */
export function savoirsMaison(D, F) {
  const prixCer = F.ceremonie.map(p => p.prix).filter(x => x != null);
  return [
    { id: 'sur_mesure', titre: 'Tout sur mesure', source: 'Hillary', indice: 'Demandez à Hillary de vous parler de la maison.',
      texte: `${F.n} créations, toutes cousues à vos mesures${F.libre ? ', et une création libre, sur devis' : ''}.` },
    { id: 'mesures', titre: 'Les mesures', source: 'Hillary, Maman Sènami', indice: 'Une maman, ici, a un avis sur les mesures.',
      texte: F.mesRobeDroite ? `Elles dépendent du vêtement : ${F.mesRobeDroite} pour une robe droite, ${F.mesPantalon} pour un pantalon. Une mesure inconnue se prend ensemble.` : null },
    { id: 'delais', titre: 'Les délais', source: 'Hillary', indice: 'Demandez les délais au comptoir.',
      texte: `${F.normal ? `Confection en ${F.normal} jours. ` : ''}Express : ${libDelai(F.exMin, F.exMax)}, avec un prix propre à chaque pièce.` },
    { id: 'livraison', titre: 'La livraison', source: 'Hillary', indice: 'Et pour recevoir sa tenue ?',
      texte: `${D.atelier.adresse}. Expédition dans ${F.nbPays} pays${F.bj ? ' : ' + fcfa(F.bj.frais) + ' au Bénin' : ''}${F.fr ? ', ' + fcfa(F.fr.frais) + ' vers la France' : ''}.` },
    { id: 'paiement', titre: 'Le paiement', source: 'Hillary', indice: 'Comment paie-t-on ?', texte: 'Par Mobile Money, après confirmation sur WhatsApp. Rien ne se paie avant.' },
    { id: 'prevenu', titre: 'Prévenu deux fois', source: 'Hillary', indice: 'Comment sait-on que sa tenue est prête ?',
      texte: 'Un message quand la commande est validée, puis un message ou un appel quand la tenue est prête.' },
    { id: 'devises', titre: 'Trois monnaies', source: 'Hillary, Afi', indice: 'Une visiteuse venue de loin l\'a remarqué.', texte: 'Les prix sont en francs CFA, en euros et en dollars.' },
    { id: 'ceremonie', titre: 'Pour une cérémonie', source: 'Hillary', indice: 'Demandez conseil pour une cérémonie.',
      texte: prixCer.length ? `${F.ceremonie.length} pièces de cérémonie, de ${fcfa(Math.min(...prixCer))} à ${fcfa(Math.max(...prixCer))}.` : null },
    { id: 'fait_main', titre: 'Fait main', source: 'Hillary', indice: 'Certaines pièces sont faites entièrement à la main.',
      texte: F.main.length ? `${F.main.map(p => p.nom).join(' et ')}.` : null },
    { id: 'creation_libre', titre: 'La création libre', source: 'Hillary', indice: 'Et si l\'on veut quelque chose d\'unique ?',
      texte: F.libre ? 'Votre idée, cousue ici : on choisit le vêtement, on parle du tissu, et le prix se fait sur devis.' : null },
    { id: 'express_paris', titre: 'Pressée, et loin', source: 'Afi, Hillary', indice: 'Une visiteuse a une course à vous confier.',
      texte: F.fr ? `En express, une tenue peut être prête en ${libDelai(F.exMin, F.exMax)}, puis partir vers la France : ${F.fr.achem} jours de route.` : null },
    { id: 'salon', titre: 'Ce salon', source: 'Hillary', indice: 'Demandez à Hillary d\'où vient ce salon.',
      texte: 'Un salon virtuel construit par NEBULA Agency, à Cotonou, pour visiter la maison depuis n\'importe où.' },
    { id: 'histoire', titre: 'Son histoire', source: 'Hillary', indice: 'Demandez à Hillary comment tout a commencé.', texte: F.histoire },
    { id: 'vision', titre: 'Sa vision', source: 'Hillary', indice: 'Demandez à Hillary ce qu\'elle veut construire.', texte: F.vision },
    { id: 'nom', titre: 'HILLARY M. STYL', source: 'Hillary', indice: 'Que veut dire le « M. » ?', texte: F.sensNom },
    { id: 'tiktok', titre: 'Sur TikTok', source: 'Sènami, Hillary', indice: 'Une jeune visiteuse ne quitte pas son téléphone.', texte: F.tiktok ? F.tiktok.compte : null },
  ];
}
