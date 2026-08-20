# 2026-08-19 · Au Braisé d'Or — les corrections de la propriétaire mises en ligne

Mongazi : « y'a des modifications qui ont été apportées au niveau de Au Braisé
d'Or, il faut donc les appliquer sur la vitrine pour que je puisse voir ».

Les modifications existaient dans le dépôt (rapatriées des branches du
téléphone), mais **rien n'avait été publié** : un `git push` ne déploie rien.

## Ce qui est maintenant en ligne

| | |
|---|---|
| Carte | **9 rubriques, 52 plats** |
| Nouveau | catégorie **Sauces (14)**, ses fourchettes de prix, **3 vraies photos** de la maison (gombo, krinkrin, feuille) |
| Héros | ne montre plus **que les sauces**, détourées par la maison |
| Prix | « tout dedans » = **le prix le plus cher**, donc deux prix exacts |
| Retirés | les 13 plats de la note manuscrite (Napolitaine, Oriental, Margherita, Pili chaud, À la crème, Pêcheur, Lapin, Viande de caille, Crispy poulet, Nugget, JOQ Viagra, Mojito, Piña Colada) |
| Gardé | ⚠️ **le Mouton frit**, parce qu'une ligne de menu avec un « ou » est deux produits |

## Vérifié en ligne, dans le CORPS de la page

Un code 200 ne prouve rien (leçon PISTE). Ce qui a été lu dans la page servie :
« Monyo » **0 fois** · gombo 9 · krinkrin 5 · 52 `.ct-item` · les 4 plats
témoins retirés absents · « Mouton frit » présent · les 3 photos de sauces en
`image/webp` · l'affiche A4 en PDF · **un fichier absent répond 404**, pas 200.

## ⚠️ Le contrôle qualité ne démarrait pas sur ce PC

`_outils/_qc.py` avait été écrit sur la machine du nuage. **Trois défauts
d'instrument, aucun ne venait du site** — et chacun aurait pu faire croire à une
panne du site :

1. **Chemin de navigateur codé en dur** : `/opt/pw-browsers/chromium-1194/...`
   n'existe que sur la machine du nuage. Playwright sait trouver le sien tout
   seul : on ne lui impose ce chemin **que s'il existe**.
2. **Une attente fixe de 1,5 s** avant de lire `#cat-petitdej`. Sur un poste
   chargé, la rubrique n'est pas encore montée et tout s'arrête sur un `null`.
   Le diagnostic l'a prouvé : à 0 ms comme à 8 s, l'élément est bien là. Il
   fallait **attendre l'élément**, pas parier sur un délai.
3. **La console Windows écrit en cp1252** : un « ≥ » dans un libellé faisait
   planter la suite **après** qu'elle eut réussi le contrôle. Sortie forcée en
   UTF-8.

**78 contrôles verts, 0 rouge** (mobile 390, bureau 1440, lisibilité des prix
de 13,9:1 à 18:1).

## La publication, telle qu'elle se fait

```bash
cd clients/09-au-braise-dor/experience
npm run build
cp -r ../assets/docs out/
npx wrangler pages deploy out --project-name au-braise-dor --branch main
```

⚠️ `node_modules` avait été effacé pour libérer le disque : `npm install` prend
6 minutes ici. ⚠️ `next@14.2.15` porte une vulnérabilité connue signalée par npm.

## Ce qui reste sur ce client

- **prix du yaourt et de la glace** (affichés « Prix sur demande »)
- la correction manuscrite au surligneur sur **l'aileron**
- **confirmer le n° WhatsApp** (0156057157 contre 43 99 29 29 sur l'enseigne)
- ⛔ **les 48 photos de plats sont générées par IA** (juillet, avant la règle) :
  Au Braisé d'Or est le **dernier site** où la règle n'est pas appliquée,
  décision de Mongazi en attente.

---

## 2026-08-20 · la quatrième sauce, et une leçon de rapatriement

Trois commits poussés **directement sur `main` depuis le téléphone**, après ma
publication de la veille :

- la **sauce krinkrin repart d'une autre photo** : elle n'était pas mal
  détourée, elle était **recadrée trop serré à la source**. Aucun masque ne
  rend des pixels qui n'existent pas (leçon écrite dans `_memoire/lecons.md`) ;
- la **sauce graine** a ses deux photos et **entre au héros** : le héros porte
  désormais **quatre** sauces (gombo, krinkrin, graine, feuille).

⚠️ **Ce qui était en ligne avait donc déjà un cran de retard.** Un `git push`
ne déploie rien, et un rapatriement n'est fini qu'une fois le site republié.
Reconstruit, **76 contrôles verts** (deux de moins que la veille : la sauce
graine n'est plus une ardoise, elle a sa photo), republié, puis vérifié :
`sc-graine` servi en 200, et le krinkrin servi **identique octet pour octet**
au fichier du disque (MD5) — donc pas un vieux fichier en cache.
