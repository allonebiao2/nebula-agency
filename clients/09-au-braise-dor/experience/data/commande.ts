/**
 * LE PONT ENTRE LE HÉROS ET LE MOTEUR DE COMMANDE.
 *
 * Le problème, posé par Mongazi le 2026-08-26 : « on doit pouvoir commander
 * directement depuis la hero, ajouter au panier aussi ». Or le panier, la
 * fiche de commande, la règle de l'accompagnement obligatoire et le message
 * WhatsApp vivent tous dans `Carte.tsx`, tout en bas de la page.
 *
 * ⛔ CE QU'ON NE FAIT PAS : recoder un « ajouter au panier » dans le héros.
 * Ce serait un DEUXIÈME moteur de commande, avec sa propre idée du prix, de
 * l'accompagnement et de la fourchette. Le jour où l'un des deux change, la
 * page vend deux prix différents pour la même sauce, et personne ne le voit.
 *
 * ✅ CE QU'ON FAIT : le héros DEMANDE, la carte OUVRE SA PROPRE FICHE. Une
 * seule fonction traverse, et c'est un nom de plat. La fiche qui s'ouvre est
 * exactement celle du menu : mêmes garnitures, même accompagnement obligatoire,
 * même fourchette, même panier, même message.
 *
 * ⚠️ Pourquoi un module et pas un contexte React : le héros et la carte sont
 * deux sections sœurs, et remonter l'état jusqu'à `page.tsx` (un composant
 * serveur) aurait demandé d'envelopper toute la page dans un client. Ici,
 * `Carte` se branche au montage et se débranche au démontage.
 */

type Ouvrir = (nomDuPlat: string) => boolean;

let ouvrir: Ouvrir | null = null;

/** Appelé par la carte au montage. `null` au démontage. */
export function brancherCommande(f: Ouvrir | null) {
  ouvrir = f;
}

/**
 * Ouvre la fiche de commande du plat nommé. Renvoie `false` si personne
 * n'écoute (carte pas encore montée) ou si le plat n'existe pas : l'appelant
 * garde alors son repli, il ne reste pas sans rien.
 */
export function commander(nomDuPlat: string) {
  return ouvrir ? ouvrir(nomDuPlat) : false;
}
