/*
  MA LETTRE À… · les savoir-faire de la plume (2026-10-21).

  Mongazi : « donne-lui tous les outils et les skills qu'il faut pour satisfaire
  n'importe quel client à 100 %, à tout moment ».

  Une règle dit ce qu'il ne faut pas faire ; un savoir-faire dit comment on fait
  bien. `plume.ts` porte les règles (le système, figé et mis en cache) ; ce
  fichier porte le métier, occasion par occasion : comment une lettre de cette
  sorte s'ouvre, ce qui la porte, comment elle finit, et où elle se rate.
  Comme une compétence qu'on ne charge que lorsqu'on en a besoin, SEUL le
  savoir-faire de l'occasion choisie part avec la fiche : la plume reçoit le
  métier de cette lettre-ci, pas un manuel de vingt-sept chapitres.

  ⚠️ LES IDENTIFIANTS SONT CEUX DE `REGISTRES` (et donc de `creer.html`) : un
  contrôle de `_qc_caisse.mjs` exige qu'il n'en manque aucun.
  ⚠️ En français, même pour la plume anglaise : ce sont des consignes, la
  lettre ne les montre jamais (le système anglais le dit).
  ⛔ Aucun fait ici ne doit pouvoir passer dans une lettre : ce sont des façons
  de faire, jamais des souvenirs, des lieux ou des proverbes à recopier.
  ⛔ Aucun tiret long ni demi-tiret dans ce fichier (un contrôle le lit).
*/

export const SAVOIRS: Record<string, string> = {
  couple:
    "Ouvre sur le moment où tu as su (le souvenir, s'il y en a un), pas sur une déclaration. Avoue un peu de trac : c'est ce qui rend la demande sincère. Dis simplement ce qui te plaît, avec ce que la fiche donne. La question vient à la fin, posée une seule fois, en clair, avec un point d'interrogation. Juste après, rends la liberté : un non ne changera rien au respect. Jamais d'insistance, jamais « tu ne peux pas dire non ».",
  mois:
    "C'est encore le début : de la légèreté et de l'émerveillement, pas un bilan. Une scène du souvenir, racontée simplement, vaut mieux qu'une promesse d'éternité. Finis tourné vers ce qui vient, avec envie, sans projeter mariage ni enfants si la fiche n'en parle pas.",
  valentin:
    "Amoureux sans sucre : une image vraie (le souvenir) au début, puis ce qui fait craquer, dit avec les mots de la fiche, puis une chute qui revient à l'image du début. Pas de « mon amour » à chaque phrase : une fois, au bon endroit. Évite roses, chocolats et « jour des amoureux » s'ils ne sont pas dans la fiche.",
  nous:
    "C'est l'histoire du couple vue d'aujourd'hui. Pars d'un instant précis (le souvenir), puis dis ce que ce temps a construit, sans inventer d'étapes ni de durée que la fiche ne donne pas. Finis sur ce qui continue, au présent : « on » plutôt que de grandes promesses.",
  demande:
    "Peu de mots, et chacun pèse. Premier temps : ce que ta vie est devenue avec elle ou lui, par une image (le souvenir). Deuxième temps : pourquoi aujourd'hui, et ce que tu promets de tenable. Troisième temps : la question, seule, en dernière phrase, claire et terminée par un point d'interrogation. Ne présume jamais la réponse, n'écris ni bague ni genou à terre si la fiche ne les donne pas.",
  pardon:
    "Une vraie excuse a quatre temps. Nommer la faute avec précision (ce que la fiche dit, sans l'adoucir). Reconnaître ce qu'elle a fait à l'autre. Ne pas se justifier : aucun « mais », aucune circonstance, rien qui rejette la faute. Dire ce qui change, seulement ce qui est tenable. Finis en laissant l'autre libre de son temps : ni ultimatum, ni « pardonne-moi vite », ni chantage aux sentiments.",
  rupture:
    "La décision est claire dès le premier paragraphe : on ne fait pas espérer une suite que « La porte » ne promet pas. Une phrase juste sur ce qui a été bon (le souvenir), sans le retourner contre l'autre. La raison donnée par la fiche, en une phrase, sans reproche détaillé ; si la fiche dit « Je préfère ne pas le dire », ne donne aucune raison. Traduis exactement la réponse « La porte ». Finis sur un vœu sincère pour l'autre.",
  anniv:
    "Ouvre sur la personne (un trait, un souvenir), jamais sur la date ni sur l'âge. Le milieu dit ce qu'elle apporte, concrètement, avec les qualités choisies. La fin est un vœu précis, pris dans « Ce que tu lui souhaites » s'il est rempli : un ou deux, pas une liste. Le mot « anniversaire » une fois au plus.",
  maman:
    "La gratitude d'une mère se dit en gestes, pas en superlatifs : pars d'un geste concret (le souvenir), puis ce qu'elle a appris ou donné, avec les mots de la fiche. Pas de « meilleure maman du monde ». Finis par un merci direct, et la bénédiction si la fiche la demande.",
  papa:
    "Même chemin que pour une mère : un geste concret (le souvenir), ce qu'il a transmis, un merci franc. Un père se remercie souvent pour ce qu'il ne disait pas : la présence, l'exemple, l'effort. Sobre plutôt que lyrique. Finis par le merci, et la bénédiction si elle est demandée.",
  naissance:
    "La joie et l'accueil. Si la lettre est pour les parents, félicite-les et parle de l'enfant qui arrive, sans prédire sa vie ni son caractère. Si elle est « pour plus tard », écris à l'enfant qui la lira grand : dis-lui le jour de son arrivée tel que la fiche le donne, et ce qu'on lui souhaite. Un baptême : l'accueil dans la communauté, une bénédiction courte si elle est demandée.",
  mariage:
    "Des vœux aux mariés : ce que leur union montre déjà (si la fiche le dit), puis des souhaits concrets pour la vie à deux, pas une liste de clichés. Garde-toi de conseils de vie conjugale. Finis par un vœu chaleureux adressé aux deux.",
  amitie:
    "Dire merci d'être là, sans grande déclaration. Un souvenir partagé raconté avec son humour ou sa tendresse, puis ce que cette amitié change au quotidien. Le ton de deux amis qui se parlent, pas d'une carte. Finis sur une promesse simple et tenable (se voir, être là).",
  brouille:
    "Clair et digne. Dis tôt que l'amitié s'arrête ou s'éloigne, selon « La porte ». La raison en une phrase, sans reproche détaillé ni témoin pris à partie ; aucune raison si la fiche préfère ne pas la dire. Une phrase juste sur ce qui a été bon. Finis sans claquer la porte, même si elle est fermée.",
  noel:
    "La chaleur d'une fête qu'on vit ensemble ou de loin. Un détail concret (le souvenir, une habitude de la fiche) plutôt que sapin et neige, surtout à Cotonou. Des vœux pour la personne, pas pour l'humanité. Une bénédiction courte si elle est demandée.",
  nouvelan:
    "Regarde l'année qui vient, en t'appuyant sur ce que la fiche dit de celle qui s'achève. Des vœux précis (pris dans « Ce que tu lui souhaites » s'il est rempli) plutôt que « santé, bonheur, prospérité » en série. Finis sur ce que vous ferez ensemble cette année, si la fiche le permet.",
  tabaski:
    "Des vœux respectueux pour l'Aïd el-Kébir. Un souvenir de fête s'il y en a un (le partage, la famille, la table). Les souhaits de la fiche, puis une bénédiction courte et générale si elle est demandée. Aucune citation du Coran, aucun détail rituel que la fiche ne donne pas.",
  ramadan:
    "Des vœux pour la fin du jeûne : la joie du partage retrouvé, la famille, la paix. Un souvenir de fête s'il y en a un. Une bénédiction courte et générale si elle est demandée. Aucune citation du Coran, aucune leçon de religion.",
  paques:
    "Des vœux de Pâques : le renouveau, la joie, la famille ou la communauté. Un souvenir s'il y en a un. Une bénédiction courte si elle est demandée. Aucune citation de la Bible mot pour mot, aucun sermon.",
  reussite:
    "La fierté juste. Dis précisément quelle réussite (ce que la fiche donne), puis le travail qu'elle a demandé si la fiche en parle. Ne grandis rien : pas de « tu seras président ». Finis tourné vers la suite, avec confiance.",
  courage:
    "Avant une épreuve, on donne de la force, pas un pronostic. Rappelle ce que la personne a déjà traversé ou ce qu'elle sait faire (la fiche), puis dis ta confiance en elle. Jamais « tu vas réussir à coup sûr » : plutôt « quoi qu'il arrive, je suis fier de toi ». Finis sur ta présence.",
  guerison:
    "Doux et présent. Pas un mot sur la maladie au-delà de ce que la fiche dit, aucun conseil, aucune prédiction. Un souvenir heureux ou un projet à faire ensemble, si la fiche le donne, aide à tenir. Finis sur un vœu de force et de repos, et la bénédiction si elle est demandée.",
  travail:
    "Des félicitations sincères pour le nouveau poste ou la promotion : ce qui l'a mérité (qualités de la fiche), puis un vœu pour la suite. Si la lettre va à un patron, une patronne ou une équipe, vouvoie et garde une juste distance. Aucun chiffre de salaire, aucun nom d'entreprise que la fiche ne donne pas.",
  retraite:
    "La reconnaissance d'une vie de travail. Ce que la personne a apporté (la fiche), un souvenir de travail si la fiche en donne un, puis des vœux pour le temps qui s'ouvre. Respectueux, chaleureux, jamais « enfin le repos des vieux jours ».",
  merci:
    "Un merci n'est fort que s'il est précis : dis exactement pour quoi (la fiche), puis ce que ce geste a changé pour toi. Pas de « je ne te remercierai jamais assez » : montre plutôt. Finis par le merci, simplement.",
  rdv:
    "Une invitation légère et claire : ce que tu proposes (la fiche), pourquoi avec elle ou lui, et une question simple pour laisser répondre. Aucune pression, aucune insistance, et la liberté de dire non, dite avec le sourire.",
  autre:
    "Lis l'occasion décrite par l'acheteur et trouve sa forme la plus proche (un merci, une fête, un encouragement, une annonce). Appuie-toi sur la fiche, ne suppose rien de l'occasion qu'elle ne dit pas.",
}

/*
  LES RETOUCHES (2026-10-21). « Presque bien » est l'insatisfaction la plus
  fréquente : la lettre plaît, mais elle est trop longue, pas assez tendre,
  trop sérieuse. Plutôt que de tout réécrire ou de tout reprendre à la main,
  l'acheteur demande une retouche, et la plume repart DE LA LETTRE TELLE
  QU'ELLE EST DANS LES CHAMPS (ses corrections à la main comprises).
  ⚠️ Les identifiants sont ceux des boutons de `creer.html` : un contrôle les
  compare. Une retouche inconnue n'est pas une erreur : elle est ignorée, et
  seule la demande écrite (bornée, nettoyée) compte.
*/
export const RETOUCHES: Record<string, string> = {
  courte:
    "Raccourcis d'environ un tiers. Garde le souvenir, la phrase la plus forte et la chute ; retire ce qui répète ou explique.",
  longue:
    "Allonge d'environ un tiers sans rien inventer : développe ce que la fiche donne déjà (le souvenir, les qualités, les souhaits). Jamais un fait nouveau. Reste sous 1 100 caractères.",
  tendre:
    "Rends-la plus tendre : plus de douceur, plus de gratitude, des mots plus proches. Sans mièvrerie ni formule de carte de vœux.",
  drole:
    "Rends-la plus drôle : un humour léger qui rit de la situation ou de soi, jamais de la personne. Si l'occasion ne s'y prête pas (une excuse grave, une rupture douloureuse, une maladie), allège seulement un peu.",
  simple:
    "Rends-la plus simple : des phrases plus courtes, des mots de tous les jours, une idée par phrase.",
  solennelle:
    "Rends-la plus solennelle : un ton posé et respectueux, des phrases plus amples, sans emphase creuse ni mots rares.",
}

/* Ce que vaut une retouche écrite à la main : une demande, pas une consigne de
   NEBULA. Assez pour dire « parle de notre voyage », pas pour un roman. */
export const BORNE_RETOUCHE = 140
