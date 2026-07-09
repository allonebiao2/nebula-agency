// Boussole — jeu d'icônes SVG (aucun emoji). 24x24, trait 1.5, currentColor.
const wrap = (paths) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;

export const ICONS = {
  home: wrap('<path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-9"/><path d="M10 20v-6h4v6"/>'),
  clock: wrap('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
  ventes: wrap('<path d="M3 6h18"/><path d="M6 6l1.2 12.2a1 1 0 0 0 1 .8h7.6a1 1 0 0 0 1-.8L19 6"/><path d="M9 10v5"/><path d="M15 10v5"/>'),
  bilan: wrap('<path d="M4 19V5"/><path d="M4 19h16"/><rect x="7" y="12" width="3" height="5" rx="0.5"/><rect x="12" y="8" width="3" height="9" rx="0.5"/><rect x="17" y="10" width="3" height="7" rx="0.5"/>'),
  reglages: wrap('<path d="M4 6h10"/><path d="M18 6h2"/><circle cx="16" cy="6" r="2"/><path d="M4 12h4"/><path d="M12 12h8"/><circle cx="10" cy="12" r="2"/><path d="M4 18h10"/><path d="M18 18h2"/><circle cx="16" cy="18" r="2"/>'),
  plus: wrap('<path d="M12 5v14"/><path d="M5 12h14"/>'),
  minus: wrap('<path d="M5 12h14"/>'),
  trash: wrap('<path d="M4 7h16"/><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/><path d="M6 7l1 12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-12"/>'),
  download: wrap('<path d="M12 4v10"/><path d="M8 11l4 4 4-4"/><path d="M4 19h16"/>'),
  upload: wrap('<path d="M12 20V9"/><path d="M8 12l4-4 4 4"/><path d="M4 5h16"/>'),
  whatsapp: wrap('<path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3Z"/><path d="M8.5 8.7c0 3.2 2.6 5.8 5.8 5.8.5 0 .9-.4.9-.9v-1a.6.6 0 0 0-.5-.6l-1.3-.3a.6.6 0 0 0-.6.2l-.3.4a4.6 4.6 0 0 1-2-2l.4-.3a.6.6 0 0 0 .2-.6l-.3-1.3a.6.6 0 0 0-.6-.5h-1c-.5 0-.9.4-.9.9Z"/>'),
  print: wrap('<path d="M7 8V4h10v4"/><rect x="4" y="8" width="16" height="8" rx="1.5"/><path d="M7 14h10v6H7z"/><path d="M17 11h.01"/>'),
  check: wrap('<path d="M5 12.5l4.5 4.5L19 7"/>'),
  close: wrap('<path d="M6 6l12 12"/><path d="M18 6L6 18"/>'),
  alert: wrap('<path d="M12 4l9 16H3z"/><path d="M12 10v4"/><path d="M12 17h.01"/>'),
  user: wrap('<circle cx="12" cy="8" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>'),
  logout: wrap('<path d="M9 5H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h3"/><path d="M15 12H9"/><path d="M13 8l4 4-4 4"/>'),
  cloud: wrap('<path d="M7 18a4 4 0 0 1-.5-8A5 5 0 0 1 16 8a4 4 0 0 1 1 8H7Z"/>'),
  cloudOff: wrap('<path d="M7 18a4 4 0 0 1-.5-8A5 5 0 0 1 16 8a4 4 0 0 1 1 8"/><path d="M3 3l18 18"/>'),
  box: wrap('<path d="M12 3l8 4v10l-8 4-8-4V7z"/><path d="M4 7l8 4 8-4"/><path d="M12 11v10"/>'),
  coins: wrap('<ellipse cx="9" cy="7" rx="5" ry="2.5"/><path d="M4 7v4c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5V7"/><path d="M10 15.5c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5v-4"/><ellipse cx="15" cy="11.5" rx="5" ry="2.5"/>'),
  factory: wrap('<path d="M4 20V10l5 3V10l5 3V7l6 3v10z"/><path d="M4 20h16"/><path d="M8 16h.01"/><path d="M13 16h.01"/>'),
  truck: wrap('<path d="M3 6h11v9H3z"/><path d="M14 9h4l3 3v3h-7z"/><circle cx="7" cy="17.5" r="1.6"/><circle cx="17" cy="17.5" r="1.6"/>'),
  bolt: wrap('<path d="M13 3L5 13h6l-1 8 8-11h-6z"/>'),
  wifi: wrap('<path d="M4 9a13 13 0 0 1 16 0"/><path d="M7 12.5a8 8 0 0 1 10 0"/><path d="M10 16a3.5 3.5 0 0 1 4 0"/><path d="M12 19.5h.01"/>'),
  edit: wrap('<path d="M4 20h4L18 10l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>'),
  chevron: wrap('<path d="M9 6l6 6-6 6"/>'),
  chevronDown: wrap('<path d="M6 9l6 6 6-6"/>'),
  arrowUp: wrap('<path d="M12 19V5"/><path d="M6 11l6-6 6 6"/>'),
  arrowDown: wrap('<path d="M12 5v14"/><path d="M6 13l6 6 6-6"/>'),
  compass: wrap('<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>'),
  target: wrap('<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/>'),
  wallet: wrap('<path d="M4 7a2 2 0 0 1 2-2h11v3"/><rect x="4" y="7" width="16" height="12" rx="2"/><path d="M16 12h4v3h-4a1.5 1.5 0 0 1 0-3Z"/>'),
  spark: wrap('<path d="M12 3v4"/><path d="M12 17v4"/><path d="M3 12h4"/><path d="M17 12h4"/><path d="M6 6l2.5 2.5"/><path d="M15.5 15.5L18 18"/><path d="M18 6l-2.5 2.5"/><path d="M8.5 15.5L6 18"/>'),
  help: wrap('<circle cx="12" cy="12" r="9"/><path d="M9.5 9.2a2.5 2.5 0 0 1 4.8.8c0 1.7-2.3 2-2.3 3.5"/><path d="M12 17h.01"/>'),
  sun: wrap('<circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.4"/><path d="M12 19.1v2.4"/><path d="M4.6 4.6l1.7 1.7"/><path d="M17.7 17.7l1.7 1.7"/><path d="M2.5 12h2.4"/><path d="M19.1 12h2.4"/><path d="M4.6 19.4l1.7-1.7"/><path d="M17.7 6.3l1.7-1.7"/>'),
  moon: wrap('<path d="M20 14.4A8 8 0 0 1 9.6 4 7 7 0 1 0 20 14.4Z"/>'),
  book: wrap('<path d="M5 4h9a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M17 7h2v13H8"/><path d="M8 8h6"/><path d="M8 11h6"/>'),
  trophy: wrap('<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5v1a3 3 0 0 0 3 3"/><path d="M16 6h3v1a3 3 0 0 1-3 3"/><path d="M12 13v3"/><path d="M9 20h6"/><path d="M10 16h4v4h-4z"/>'),
  flame: wrap('<path d="M12 3s5 4 5 9a5 5 0 0 1-10 0c0-2 1-3 1-3 .5 1.5 1.5 2 1.5 2S9 8 12 3z"/>'),
  search: wrap('<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/>'),
  receipt: wrap('<path d="M6 3h12v17l-2-1.3-2 1.3-2-1.3-2 1.3-2-1.3z"/><path d="M9.5 8h5"/><path d="M9.5 11.5h5"/>'),
  calendar: wrap('<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 9h16"/><path d="M8 3v4"/><path d="M16 3v4"/>'),
};

// injecte les icônes dans les [data-icon]
export function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((el) => {
    const name = el.getAttribute('data-icon');
    if (ICONS[name] && !el.dataset.iconDone) {
      el.innerHTML = ICONS[name];
      el.dataset.iconDone = '1';
    }
  });
}

export function icon(name) {
  return ICONS[name] || '';
}
