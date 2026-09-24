import { faq } from "@/data/maison";

/**
 * LES QUESTIONS FRÉQUENTES, visibles. Le `FAQPage` du balisage est bâti sur le
 * MÊME tableau (`faq()`), donc une question balisée est toujours une question
 * affichée : Google sanctionne l'inverse.
 * `<details>` : lisible sans JavaScript, ouvrable au clavier, et le texte des
 * réponses est dans le HTML même fermé (les robots le lisent).
 */
export default function Questions() {
  const liste = faq();
  return (
    <section
      id="questions"
      className="relative z-10 border-t border-black/[0.06] bg-[color:var(--mur)] px-6 py-20 text-[color:var(--encre)]"
    >
      <div className="mx-auto max-w-3xl">
        <p className="mb-3 text-[0.72rem] font-medium uppercase tracking-[0.32em] text-[#a8542f]">
          Questions fréquentes
        </p>
        <h2 className="police-titre mb-10 text-[clamp(1.8rem,4.4vw,2.8rem)] font-extralight leading-[1.08]">
          Ce qu&apos;on nous demande{" "}
          <span className="font-extrabold italic" style={{ color: "#a8542f" }}>
            le plus souvent
          </span>
        </h2>
        <div className="divide-y divide-black/[0.08] border-y border-black/[0.08]">
          {liste.map(({ q, r }) => (
            <details key={q} className="group py-5">
              <summary className="flex cursor-pointer list-none items-start justify-between gap-6 text-[1.02rem] font-semibold [&::-webkit-details-marker]:hidden">
                <h3 className="police-titre text-[1.02rem] font-bold">{q}</h3>
                <span
                  aria-hidden
                  className="mt-0.5 shrink-0 text-[1.3rem] leading-none text-[#a8542f] transition group-open:rotate-45"
                >
                  +
                </span>
              </summary>
              <p className="mt-3 text-[0.94rem] leading-relaxed text-[color:var(--encre-2)]">{r}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
