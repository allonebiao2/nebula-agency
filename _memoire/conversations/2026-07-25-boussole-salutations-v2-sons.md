# 2026-07-25 — Boussole proto : salutations intelligentes v2 + passe d'amélioration sonore

## Demande
1. Le texte d'entrée (HUD accueil) doit être **intéressant** : apprendre sur l'argent, saluer, faire des résumés, donner un **avis honnête** sur la gestion de l'utilisateur, des conseils — **jamais se répéter**, faire réfléchir, donner envie de revenir.
2. Améliorer **tous les effets sonores**.

## 1 — Smart Greeting Engine v2 (le cerveau des salutations)
Trois voix, mélangées avec pondération :
- **Le MIROIR (poids 3)** : ~15 phrases **calculées sur les vrais chiffres** — hier vs avant-hier, % objectif + reste, série 🔥, dettes dehors, ruptures, « avis honnête : ta marge ne couvre pas tes charges (manque X) », bénéfice net = « ton vrai salaire », produit champion 30 j, marge fine (<25 %), **« tu encaisses mais ne notes aucune sortie : ton bénéfice est une illusion »**, poche perso > bénéfice net, résumé semaine + moyenne/jour, première vente.
- **L'ÉCOLE (poids 1)** : 26 leçons d'argent courtes (« retiens ça : … ») — CA vs bénéfice, 3 enveloppes, crédit sans date, stock qui dort, salaire fixe, coût de revient, dettes relancées, charges fixes, constance…
- **L'ÉTINCELLE (poids 1,6)** : 10 questions qui font réfléchir (« question pour toi : … ») — meilleur jour ?, doubler un prix ?, coût d'un jour fermé ?, client disparu ?, 30 jours de bénéfice ?…
**Anti-répétition** : `SM.greetHist` persisté (ids servis, cap 90) — jamais deux fois la même tant que le stock n'est pas épuisé ; à l'épuisement, reset en gardant les 4 derniers. Salutation par moment (Bonjour / Bel après-midi / Bonsoir) + **vitesse de frappe adaptative** (2400/len, 16–45 ms) pour les phrases longues.

## 2 — Passe sonore
- **Bus « la pièce »** dans `audioCtx()` : delay 125 ms + feedback 0.22 + lowpass 2600 → wet 0.13 (0.09 mobile) vers le compresseur — TOUS les sons gagnent une pièce discrète, cohérence premium sans toucher chaque fonction.
- **playClick** : sinus + octave triangle détunée (620/930), plus « bois » que « bip ».
- **playSell** : **carillon doré** — 4 partiels de cloche accordés (880/1318,5/1760/2637) micro-détunés + poussière d'or (bruit façonné en décroissance ², highpass 5800).
- **playSuccess** : arpège **do-mi-sol-do** (523/659/784/1046) sinus + soupçon d'octave, queues 0,34 s.
- **playCoin (nouveau)** : tintement de pièce (3520/4698 Hz détunés) → branché sur la **pluie de pièces de VENDRE** (double tintement au burst) et sur les **confettis d'objectif** (3 tintements en cascade 500/720/990 ms).
- **playHover** adouci (square→triangle, 15 %→12 %) · **playType** 0.035→0.026.

## QC
`qc_v8.js` : **9/9 verts** — 1re phrase servie = miroir réel (« on te doit 26 500 F… »), 9 passages accueil = **9 phrases uniques**, historique persisté, mix miroir+leçons servi, sons déclenchés sans exception. Non-régression v7 + v6 : tout vert. 0 erreur console.

Cf [[2026-07-25-boussole-signatures-mastodontes]].
