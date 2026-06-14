# 05 · Opérations

## Paiement (manuel, validé)
- **MTN MoMo : 01 96 74 07 32** (Mongazi Yan Karl). **Pas de Moov** pour l'instant → les clientes uniquement Moov ne peuvent pas payer (ouvrir un compte Moov plus tard).
- Pas de FedaPay au démarrage (volume faible, contrôle, universel). Flux : cliente paie → **notif Telegram** → Mongazi **valide** → site en ligne.

## Livraison
Le produit livré = **un lien hébergé** (`/v/slug`), toujours en ligne. Back-office : boutons **« Prévenir la cliente »** (WhatsApp pré-rempli) + **« Email »** (mail pré-rempli). La cliente met le lien dans sa bio Insta/WhatsApp.

## Back-office
- `https://vitrina.nebula-agency.online/admin` → **login par mot de passe** (= env `VITRINA_ADMIN_KEY`), cookie HMAC httponly/secure. **Plus de `?key=` en clair.**
- Boutons par commande : **Valider** / **Refuser** / **Suppr.** + **Se déconnecter**.
- KPIs : commandes, en attente, en ligne, **encaissé**.

## Telegram
Bot **@Vitrina_nebulabot** (chat `390837922`). Notif à chaque nouvelle commande (avec email + lien back-office).

## Échéance / abonnement
À la **validation**, `expires` = date + 1 an, stocké et affiché. **Email obligatoire** à la commande = clé des **rappels d'échéance** (à automatiser — voir [[06-roadmap]] §1).
