/**
 * L'ARDOISE — ce qu'on affiche quand la maison n'a pas encore donné sa photo.
 *
 * ⚠️ PAS DE « PHOTO À VENIR », PAS DE CADRE VIDE. Un cadre vide dit au client
 * que le site est en travaux ; « photo à venir » dit que la maison n'est pas
 * prête. Un restaurant, lui, écrit à l'ardoise ce qu'il n'a pas photographié,
 * et personne n'y voit un manque. La tuile porte donc le nom du plat, écrit,
 * et rien d'autre.
 *
 * ⚠️ DEUX FORMES, LE MÊME OBJET. Dans la carte c'est une tuile qui remplit sa
 * vignette (`forme="tuile"`). Au héros, où les autres sauces sont des
 * assiettes détourées qui flottent, une tuile rectangulaire trahirait le
 * manque : `forme="assiette"` dessine un disque d'ardoise, avec sa lumière et
 * son bord, qui prend exactement la place d'une assiette.
 */
export default function Ardoise({
  nom,
  grand = false,
  forme = "tuile",
  teinte,
}: {
  nom: string;
  grand?: boolean;
  forme?: "tuile" | "assiette";
  /** ⚠️ La couleur propre de la sauce, pour le filet sous le nom. Au héros,
   *  huit ardoises identiques à la file ressemblent à une panne ; la même
   *  pierre avec la couleur de chaque sauce ressemble à une collection. */
  teinte?: string;
}) {
  const filet = teinte ?? "rgba(232,118,58,.75)";
  const grain = (
    <div
      className="pointer-events-none absolute inset-0 rounded-[inherit] opacity-[0.16]"
      style={{
        backgroundImage:
          "repeating-linear-gradient(115deg, rgba(255,255,255,.10) 0 1px, transparent 1px 7px)",
      }}
    />
  );

  if (forme === "assiette") {
    /* ⚠️ LE DISQUE SE MESURE SUR LE PLUS PETIT CÔTÉ DE SA BOÎTE, ET C'EST UN
       DÉFAUT VU SUR CAPTURE. Premier jet : `absolute inset-0` + `aspect-ratio`
       + `margin: auto`. Sur grand écran la boîte de l'assiette est carrée, tout
       allait bien. Sur téléphone elle fait `100 % × 30vh` — 350 × 253 — et les
       deux `inset` fixent DÉJÀ la hauteur et la largeur : `aspect-ratio` est
       alors ignoré, le disque sortait de sa boîte de 100 px et se posait
       par-dessus l'accroche et le titre.
       La boîte devient donc un conteneur mesuré, et le disque prend
       `min(largeur, hauteur)` — ce qu'aucun calcul CSS ne sait faire autrement
       (`width: 100%` reste en repli pour un navigateur sans `cq`). */
    return (
      <div className="ardoise-boite absolute inset-0 grid place-items-center" aria-hidden="true">
        <div
          className="ardoise-plat relative grid place-items-center overflow-hidden rounded-full"
          style={{
            /* la lumière de la pièce vient d'en haut à gauche, comme celle du
               mur : sans elle, un disque mat de 570 px ressemble à une image
               qui n'a pas chargé, pas à de la vaisselle */
            background:
              "radial-gradient(70% 55% at 30% 22%, rgba(255,255,255,.15), transparent 62%)," +
              "radial-gradient(120% 100% at 50% 0%, #443830 0%, #2a231e 55%, #1c1815 100%)",
            /* l'ombre portée des photos détourées, l'aile du plat, et un halo
               très discret à la couleur de la sauce */
            boxShadow:
              "0 30px 60px rgba(0,0,0,0.20), 0 18px 50px -24px " + filet + "," +
              "inset 0 0 0 1px rgba(240,230,216,.13), inset 0 0 0 11px rgba(240,230,216,.045)",
          }}
        >
          {grain}
          <div className="relative px-[14%] text-center">
            <p
              className="police-titre text-[clamp(0.95rem,3vw,1.9rem)] font-extrabold uppercase leading-[1.15] tracking-[0.05em] text-[#f0e6d8]"
              style={{ textShadow: "0 1px 0 rgba(0,0,0,.45)" }}
            >
              {nom}
            </p>
            <span
              className="mx-auto mt-3 block h-[3px] w-14 rounded"
              style={{ background: filet }}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="absolute inset-0 grid place-items-center overflow-hidden"
      style={{
        background:
          "radial-gradient(120% 90% at 50% 0%, #3a312a 0%, #241f1b 60%, #1b1714 100%)",
      }}
      aria-hidden="true"
    >
      {grain}
      <div className="relative px-4 text-center">
        <p
          className={
            "police-titre font-extrabold leading-[1.12] text-[#f0e6d8] " +
            (grand ? "text-[1.5rem]" : "text-[1.02rem]")
          }
          style={{ textShadow: "0 1px 0 rgba(0,0,0,.45)" }}
        >
          {nom}
        </p>
        <span
          className="mx-auto mt-2 block h-px w-10 rounded"
          style={{ background: filet }}
        />
      </div>
    </div>
  );
}
