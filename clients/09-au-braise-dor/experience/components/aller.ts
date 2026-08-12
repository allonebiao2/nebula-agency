/**
 * ALLER À UNE SECTION.
 *
 * ⚠️ TOUJOURS PASSER PAR LENIS quand il est là. Il a pris la main sur le
 * défilement de la page ; un `scrollIntoView` lancé à côté se fait interrompre
 * et s'arrête en chemin. Mesuré en ligne : le saut vers « Cocktails » finissait
 * à 7 382 px de sa cible, sans la moindre erreur dans la console.
 * Le repli `scrollIntoView` sert au cas où Lenis n'est pas monté (mouvement
 * réduit, script en échec) : le lien doit marcher quoi qu'il arrive.
 */
type AvecLenis = {
  __lenis?: { scrollTo: (t: string | HTMLElement, o?: Record<string, unknown>) => void };
};

export function allerA(id: string) {
  const el = document.getElementById(id);
  if (!el) return;
  const l = (window as unknown as AvecLenis).__lenis;
  if (l) l.scrollTo(el, { duration: 1.1, offset: -8 });
  else el.scrollIntoView({ behavior: "smooth", block: "start" });
}
