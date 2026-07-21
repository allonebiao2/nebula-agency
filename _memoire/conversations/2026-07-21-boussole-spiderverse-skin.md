# 2026-07-21 — Boussole : skin « Spider-Verse » (comic imprimé) sur le proto

## Contexte / correction de cible
Handoff Claude Design `Boussole-SpiderVerse.dc.html` (poster V.10 ULTRA : 9 écrans téléphone en style comic imprimé — encre, halftone Ben-Day, glitch, aberration chromatique, ambre+émeraude+rose+cyan, police **Anton** + Bricolage Grotesque). Objectif : implémenter ce design dans Boussole.

⚠️ **1re erreur** : j'ai d'abord appliqué le skin sur l'**app déployée** (`boussole/index.html` + `assets/`, prod `boussole-19d.pages.dev`). Mongazi : « non, la version **proto** qu'on construisait dernièrement, avec les **boutons en glass** et l'**entrée Google** » → la vraie cible = **`boussole/_proto/app.html` + `_proto/connexion.html`** (refonte récente, cf commits `boussole-proto`). J'ai **reverté** les changements de l'app déployée (git checkout index.html sw.js + rm), gardé seulement `assets/fonts/Anton.woff2` (réutilisable).

## Ce qui a été fait (proto)
Le proto était en **cyber-noir cyan + Liquid Glass** (`#0B0F19`, cyan `#38f0ff`, header verre, grille de profondeur en fuite, poussières). Le design V.10 est un **comic imprimé chaud** (crème `#fdf6e9`, Anton, halftone, ombres d'encre dures `6px 6px 0 #05050c`, chroma rose/cyan, ambre+émeraude).

**Approche = couche additive scopée `html[data-skin="sv"]`** (défaut activé, réversible via `?skin=off`), appendée à la fin du `<style>` de chaque fichier. **Aucune logique touchée** (DOM/JS intacts).
- **`app.html`** : Anton @font-face (`../assets/fonts/Anton.woff2`) ; tokens comic ; fond = grille adoucie + néons radiaux + halftone Ben-Day (`.depth::before/::after`) ; header ink (blur retiré) + logo à liseré chromatique ; titres/greeting/`.kpi__num`/`.panel__ttl`/`.drawer__brand` en Anton + aberration chromatique ; cartes (`.kpi/.panel/.vital/.pos-tile/.seg/…`) = bord crème 2px + ombre dure ; `.seg-btn.is-on` ambre ; `.navbtn.is-on` surlignage comic ; boutons/champs/FAB comic ; `.hbar__fill` rayé ambre ; glitch sur `.drawer__brand`.
- **`connexion.html`** : carte `.glass` = cadre encre + **liseré chromatique rose/cyan** (façon planche BD), blur retiré ; `.title` Anton+chroma (garde le `.title__glitch` existant) ; `.btn-main` ambre comic ; `.btn-google` papier + bord encre + ombre dure (reste reconnaissable) ; inputs crème ; fond image conservé mais assombri + halftone.
- Activation : attribut `data-skin="sv"` sur `<html>` + petit script inline (anti-flash + toggle `?skin=off` persistant en localStorage `boussole:skin`).

## Déploiement (preview, prod intacte)
- `wrangler pages deploy . --project-name boussole --branch spiderverse` → **https://spiderverse.boussole-19d.pages.dev/_proto/connexion** (entrée) → app après login.
- La **prod `boussole-19d.pages.dev` n'est pas touchée** (app root revenue à son état d'origine).
- Vérifié live : connexion 200 (43 Ko) + app 200 (222 Ko), `data-skin="sv"` actif, Anton.woff2 200. ⚠️ Cloudflare Pages redirige `.html`→URL propre (308) : donner le lien **sans `.html`**.

## Reste (vague 2 = peaufinage par écran)
Vague 1 = transformation **globale** (tokens + primitives) en ciblant les classes réelles cartographiées. Le proto a beaucoup d'écrans (caisse POS, ventes, stats/bilan donut, objectifs, carnet clients, catalogue, factures/devis, dépenses, mon équipe, IA). **À faire confirmer écran par écran par Mongazi** (feeling réel) puis caler au pixel : dispo exacte des enveloppes, bulles de l'assistant, tuiles POS, donut stats, etc. + relooker `connexion.html` fond si besoin.

## Notes techniques
- Anton auto-hébergé (offline-first) : `boussole/assets/fonts/Anton.woff2` (8,7 Ko, téléchargé depuis Google Fonts, magic `wOF2` OK).
- Bricolage Grotesque était **déjà** la police du proto ; la palette dark du proto (cyan) était proche → le gros du travail = passer du néon-glow aux **ombres d'encre dures** + Anton + halftone + chroma.
- Standalone : `boussole/_proto/spiderverse.html` = reproduction cliquable fidèle du poster (9 écrans, nav BD) construite en amont comme référence.

Cf [[project_boussole-refonte]], design tokens du handoff (numShadow `-2.5px 0 #ff2d7e,2.5px 0 #23e0ff`, titleShadow `-5px 0 #ff2d7e,5px 0 #23e0ff,10px 10px 0 rgba(0,0,0,.55)`).
