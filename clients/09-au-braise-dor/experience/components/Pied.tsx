import { WHATSAPP } from "@/data/dishes";

/**
 * LE PIED DE PAGE.
 *
 * ⚠️ CE COMPOSANT N'EST PAS UN ORNEMENT, C'EST UN SAUVETAGE. En basculant le
 * site du client sur cette version, tout ce qui vivait plus bas dans l'ancienne
 * page disparaissait d'un coup : les deux numéros, l'adresse électronique, les
 * services traiteur et place des fêtes, et surtout **les mentions légales**
 * (RC et IFU). Un restaurant qui perd son RCCM de son site, ce n'est pas un
 * détail de mise en page.
 *
 * Tout ce qui suit est repris MOT POUR MOT de l'ancienne page.
 */
export default function Pied() {
  return (
    <footer
      id="infos"
      className="relative z-10 border-t border-white/10 bg-[#0b0805] px-6 py-14 text-[#c9b6a2]"
    >
      <div className="mx-auto grid max-w-5xl gap-10 md:grid-cols-3">
        <div>
          <p className="police-titre mb-3 text-[1.05rem] font-extrabold text-[#f3e9dd]">
            Commande &amp; contact
          </p>
          <p className="text-[0.88rem] leading-relaxed">
            WhatsApp 01 56 05 71 57
            <br />
            01 94 21 30 02
            <br />
            aubraisedor@gmail.com
            <br />
            WiFi 24h/24 · Ouvert tous les jours
          </p>
          <a
            href={`https://wa.me/${WHATSAPP}`}
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-[0.85rem] font-semibold text-white transition hover:brightness-110"
            style={{ background: "#128040" }}
          >
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden>
              <path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5.1-1.3A10 10 0 1 0 12 2m0 2a8 8 0 1 1-4.2 14.8l-.3-.2-2.6.7.7-2.5-.2-.3A8 8 0 0 1 12 4" />
            </svg>
            Écrire sur WhatsApp
          </a>
        </div>

        <div>
          <p className="police-titre mb-3 text-[1.05rem] font-extrabold text-[#f3e9dd]">
            Au-delà du menu
          </p>
          <p className="mb-3 text-[0.88rem] leading-relaxed">
            <b className="text-[#e8a86a]">Traiteur &amp; réceptions.</b> On
            déplace la braise chez vous, et on reçoit vos évènements dans notre
            place des fêtes.
          </p>
          <p className="text-[0.88rem] leading-relaxed">
            <b className="text-[#e8a86a]">Place des fêtes.</b> Un espace pour vos
            anniversaires, mariages et évènements, avec la cuisine de la maison
            à la carte.
          </p>
        </div>

        <div>
          <p className="police-titre mb-3 text-[1.05rem] font-extrabold text-[#f3e9dd]">
            Au Braisé d&apos;Or
          </p>
          <p className="text-[0.88rem] leading-relaxed">
            De Paris à Cotonou.
            <br />
            Cuisine africaine, européenne et américaine : grillades au feu de
            bois, pizzas, chawarma, salades, cocktails.
            <br />
            Sur place, à emporter, traiteur et réceptions.
          </p>
        </div>
      </div>

      <div className="mx-auto mt-12 max-w-5xl border-t border-white/10 pt-6 text-[0.76rem] text-[#8a7a68]">
        <p>RC RB/COT/24 A 102350 · IFU 0202501441177</p>
        <p className="mt-1">Vitrine créée par NEBULA Agency · Cotonou</p>
      </div>
    </footer>
  );
}
