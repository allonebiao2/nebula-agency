# WhatsApp Business — Connaissances NEBULA

> Tout ce qu'il faut savoir pour intégrer WhatsApp aux vitrines et workflows NEBULA.

---

## Lien direct depuis vitrine

Format standard :

```
https://wa.me/229XXXXXXXX?text=Bonjour%2C%20je%20viens%20de%20votre%20site...
```

- Préfixe pays Bénin : **229**
- Côte d'Ivoire : 225 — Sénégal : 221 — Togo : 228 — Burkina : 226
- Toujours pré-remplir un message court et clair
- Encoder les espaces en `%20`, les sauts de ligne en `%0A`

> **Règle absolue NEBULA** : ces liens ne se modifient JAMAIS sans confirmation explicite de Mongazi.

## CTA WhatsApp dans une vitrine

- Bouton sticky bas-droite sur mobile (souvent décisif)
- Texte clair : "Discuter sur WhatsApp" plutôt que "Contact"
- Logo WhatsApp officiel à respecter (vert `#25D366`)

## Twilio + WhatsApp Business API

- **Sandbox Twilio** pour les phases de test (numéro partagé, opt-in obligatoire)
- **Number Business approuvé** par Meta pour la prod
- **Templates** à valider auprès de Meta avant envoi sortant (proactif)
- Conversation entrante (client → business) : pas besoin de template
- Fenêtre de service : 24h après le dernier message client → après quoi, template obligatoire

## Bonnes pratiques messages

- Identifier l'expéditeur dès le premier message (nom du business)
- Proposer un opt-out clair sur les campagnes
- Ne jamais spammer — Meta bannit vite et durablement
- Personnaliser (prénom, contexte) → bien meilleur taux de réponse

## Coûts à surveiller

- Twilio facture à la **conversation** (fenêtre de 24h) côté WhatsApp Business API
- Tarif variable par pays
- Bien doser les relances automatisées pour ne pas exploser la facture

## Pièges fréquents

- Numéro mal formaté dans `wa.me/...` → lien cassé silencieusement
- Caractères spéciaux non encodés dans le `text` → message tronqué
- Test du lien depuis un PC sans WhatsApp Desktop → fausse impression que ça ne marche pas
