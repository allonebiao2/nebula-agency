/** Un bloc JSON-LD. `<` est échappé : un nom de plat ne peut pas fermer le script. */
export default function Ld({ donnees }: { donnees: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(donnees).replace(/</g, "\u003c") }}
    />
  );
}
