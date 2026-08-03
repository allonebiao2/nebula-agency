# Carnet de prospection · Bénin et Togo

**187 commerces réels**, relevés le 2026-08-03 : 111 ateliers de couture, 74 restaurants
et maquis, 2 pâtisseries. 113 au Bénin, 74 au Togo.

## Ce qu'il y a dans ce dossier

| Fichier | À quoi ça sert |
|---|---|
| `carnet-prospection.html` | **Le carnet, à ouvrir sur le téléphone.** Un bouton par ligne qui ouvre WhatsApp avec le message déjà écrit pour son métier. On marque Écrit / Rendez-vous / Vendu / Non, et ça se garde même après avoir fermé. |
| `prospects-benin-togo.csv` | La même liste pour Excel ou Google Sheets, si on la partage à plusieurs partenaires. |
| `_donnees.py` | Les données brutes, avec leur source. |
| `_build.py` | Refabrique les deux fichiers. |
| `_qc.js` | Les 13 contrôles (liens WhatsApp, fixes exclus, cibles ≥ 34 px, 390 et 1440). |

## D'où viennent ces numéros

Une seule source : **l'annuaire GoAfricaOnline**, consulté le 3 août 2026.
Rien n'a été deviné, rien n'a été complété.

⚠️ **Un annuaire vieillit.** Un numéro peut avoir changé, un commerce peut avoir fermé.
Le premier contact sert aussi à vérifier. C'est normal et ça se gère : on avance.

⚠️ **L'annuaire n'affiche de site internet pour aucun d'eux.** C'est un signal fort,
ce n'est pas une preuve. Regardez 10 secondes s'il a une page Facebook avant d'écrire :
ça change le message, et ça évite de passer pour quelqu'un qui n'a pas regardé.

⚠️ **13 sont des numéros fixes** (Bénin `01 21…`, Togo `22…`) : pas de WhatsApp,
on les appelle. Le carnet ne leur propose pas de bouton WhatsApp.

## Les numéros

- **Bénin : 10 chiffres.** Seuls les 10 chiffres fonctionnent depuis le 1er janvier 2025
  (réforme ARCEP du 30 novembre 2024, préfixe `01` ajouté devant l'ancien numéro).
  L'annuaire est déjà au bon format.
- **Togo : 8 chiffres.** Mobiles en 90-99, 70, 79. Les `22…` sont des fixes.

## Comment s'en servir

Le message est déjà écrit, et **il ne contient aucun prix** : le prix se dit après la
démonstration, jamais avant. Le raisonnement complet est dans
`../13-PROSPECTION-BENIN-TOGO.md`.

Rythme conseillé : **10 messages par jour**, pas 50. Sur 10, comptez environ 3 réponses.
Notez chaque prospect dans le back-office partenaire le jour même : il vous est réservé
60 jours.

## Pour régénérer

```bash
python _documents/nebula-agency/vente/prospection/_build.py
node   _documents/nebula-agency/vente/prospection/_qc.js
```
