// Le portrait DESSINÉ du vendeur (jamais un vrai visage), animé : il cligne, il parle pendant que son texte s'écrit,
// et il a trois expressions (neutre, sourire, ravi). Un seul dessin, habillé par métier :
//   avatar({ peau, tenue, col, fond, coiffe: "foulard" | "casquette" | "court", accessoire: "lunettes-atelier" | "casque-audio" | null })
// Pilotage : el.dataset.e = "neutre" | "sourire" | "ravi" ; el.classList.toggle("parle", true|false).
export function avatar(o = {}) {
  const peau = o.peau || "#8a5a3a", ombre = o.ombre || "#6e4429", tenue = o.tenue || "#5b3a24", col = o.col || "#efe6d8",
        fond = o.fond || ["#f3d9b8", "#c98f5c"], cheveux = o.cheveux || "#1c120c", coiffe = o.coiffe || "foulard", tissu = o.tissu || "#c0502f";
  const id = "av" + Math.random().toString(36).slice(2, 7);
  const coiffes = {
    foulard: `<path d="M33 52 C28 22 92 22 87 52 C84 40 36 40 33 52Z" fill="${tissu}"/><path d="M36 30 C48 12 76 12 86 32 C74 24 48 24 36 30Z" fill="${tissu}"/>
      <circle cx="84" cy="30" r="9" fill="${tissu}"/><path d="M80 26 q6 2 8 8" stroke="#0003" stroke-width="2" fill="none"/>
      <path d="M38 44 q22 -10 44 0" stroke="#fff4" stroke-width="2" fill="none"/>`,
    casquette: `<path d="M34 50 C32 26 88 26 86 50Z" fill="${tissu}"/><path d="M60 47 C74 44 92 46 98 52 C88 54 72 54 60 52Z" fill="${tissu}" filter="brightness(.8)"/>
      <rect x="54" y="30" width="12" height="6" rx="3" fill="#fff6"/>`,
    court: `<path d="M36 52 C32 26 88 26 84 52 C80 40 40 40 36 52Z" fill="${cheveux}"/>`,
  };
  const accessoires = {
    "lunettes-atelier": `<g class="av-lunettes"><path d="M34 41 H86" stroke="#2a1c14" stroke-width="3"/>
      <rect x="40" y="34" width="17" height="11" rx="5" fill="#ff9a3c" fill-opacity=".75" stroke="#2a1c14" stroke-width="2"/>
      <rect x="63" y="34" width="17" height="11" rx="5" fill="#ff9a3c" fill-opacity=".75" stroke="#2a1c14" stroke-width="2"/>
      <path d="M43 37 h5" stroke="#fff" stroke-opacity=".8" stroke-width="1.6" stroke-linecap="round"/><path d="M66 37 h5" stroke="#fff" stroke-opacity=".8" stroke-width="1.6" stroke-linecap="round"/></g>`,
    "casque-audio": `<g class="av-casque"><path d="M32 66 C28 30 92 30 88 66" fill="none" stroke="#16161c" stroke-width="6"/>
      <rect x="26" y="58" width="13" height="20" rx="6" fill="#16161c"/><rect x="81" y="58" width="13" height="20" rx="6" fill="#16161c"/>
      <rect x="28" y="62" width="4" height="12" rx="2" fill="${o.neon || "#2ee6d6"}"/><rect x="88" y="62" width="4" height="12" rx="2" fill="${o.neon || "#2ee6d6"}"/>
      <path d="M33 76 q6 12 20 13" stroke="#16161c" stroke-width="2.5" fill="none"/><circle cx="54" cy="89" r="2.6" fill="#16161c"/></g>`,
  };
  return `<svg class="av" viewBox="0 0 120 120" role="img" aria-label="${o.nom || "Le vendeur"}, en dessin" data-e="neutre">
 <defs><radialGradient id="${id}f" cx="50%" cy="35%" r="75%"><stop offset="0" stop-color="${fond[0]}"/><stop offset="1" stop-color="${fond[1]}"/></radialGradient></defs>
 <rect width="120" height="120" fill="url(#${id}f)"/>
 <path d="M16 120 C18 98 36 88 60 88 C84 88 102 98 104 120Z" fill="${col}"/>
 <path d="M34 120 L40 96 Q60 104 80 96 L86 120Z" fill="${tenue}"/>
 <path d="M52 74 L52 90 Q60 95 68 90 L68 74Z" fill="${ombre}"/>
 <ellipse cx="60" cy="60" rx="23" ry="26" fill="${peau}"/>
 <ellipse cx="37.5" cy="62" rx="3.4" ry="5" fill="${ombre}"/><ellipse cx="82.5" cy="62" rx="3.4" ry="5" fill="${ombre}"/>
 ${coiffes[coiffe] || ""}
 <path d="M47 55 Q52 52.5 57 54.5 M63 54.5 Q68 52.5 73 55" stroke="#1c120c" stroke-width="1.8" fill="none" stroke-linecap="round"/>
 <g class="av-yeux"><ellipse cx="52" cy="61" rx="2.4" ry="3" fill="#1c120c"/><ellipse cx="68" cy="61" rx="2.4" ry="3" fill="#1c120c"/>
  <circle cx="52.8" cy="60" r=".8" fill="#fff"/><circle cx="68.8" cy="60" r=".8" fill="#fff"/></g>
 <g fill="#e98a7a" opacity=".55"><ellipse cx="47" cy="70" rx="4.6" ry="2.5"/><ellipse cx="73" cy="70" rx="4.6" ry="2.5"/></g>
 <path d="M60 63 Q58.4 67.4 61 68" stroke="${ombre}" stroke-width="1.3" fill="none" stroke-linecap="round"/>
 <g class="av-bouche">
  <path class="b-neutre" d="M54 75 Q60 77.5 66 75" stroke="#4a1f12" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <path class="b-sourire" d="M52.5 73.5 Q60 80.5 67.5 73.5" stroke="#4a1f12" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path class="b-ravi" d="M52 72.5 Q60 84 68 72.5Z" fill="#4a1f12"/><path class="b-ravi" d="M55 73.4 Q60 75 65 73.4" stroke="#fff" stroke-width="1.6" fill="none"/>
  <ellipse class="b-parle" cx="60" cy="75.5" rx="4.2" ry="2.6" fill="#4a1f12"/>
 </g>
 ${o.accessoire ? accessoires[o.accessoire] || "" : ""}
</svg>`;
}

export const AVATAR_CSS = `.av{display:block;width:100%;height:100%;border-radius:50%}
.av .av-yeux{transform-origin:60px 61px;animation:av-cligne 4.6s infinite}
@keyframes av-cligne{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}
.av .av-bouche>*{display:none}
.av[data-e="neutre"] .b-neutre,.av[data-e="sourire"] .b-sourire,.av[data-e="ravi"] .b-ravi{display:inline}
.parle .av .av-bouche>*{display:none}
.parle .av .b-parle{display:inline;transform-origin:60px 75.5px;animation:av-parle .22s infinite alternate}
@keyframes av-parle{from{transform:scaleY(.35)}to{transform:scaleY(1.15)}}
.av-cadre{animation:av-respire 3.8s ease-in-out infinite}
@keyframes av-respire{50%{transform:translateY(-1.5px) scale(1.015)}}
@media (prefers-reduced-motion:reduce){.av .av-yeux,.parle .av .b-parle,.av-cadre{animation:none}}`;
