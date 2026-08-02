# -*- coding: utf-8 -*-
"""
Optimisation « AI SEO » du site NEBULA : rendre la page extractible et citable
par ChatGPT, Claude, Perplexity, Gemini et les résumés IA de Google.

Idempotent : relançable sans dégât. UTF-8 strict (jamais PowerShell).

Ce qu'il fait, et pourquoi :
 1. retire <meta keywords>      → le bourrage de mots-clés fait PERDRE 10 % de
                                  visibilité IA (étude GEO, Princeton, KDD 2024)
 2. corrige les descriptions    → elles vendaient encore les « avatars IA »,
                                  service retiré du site en v9
 3. remplace le JSON-LD         → un @graph : Organization + OfferCatalog avec les
                                  vrais prix + FAQPage + WebSite
 4. ajoute une vraie FAQ        → visible pour l'humain, extractible par la machine
 5. affiche une date de MAJ     → les IA pondèrent lourdement la fraîcheur
"""
import io, re, sys, datetime

SRC = r"C:/Users/USER/nebula-agency/00-nebula-agency/nebula_agency_v9.html"
AUJ = "2026-08-02"
LISIBLE = "2 août 2026"

# ── les questions, et des réponses chiffrées (une réponse citable est une réponse
#    qui tient debout toute seule, sortie de son contexte) ────────────────────────
FAQ = [
 ("Combien coûte un site web au Bénin ?",
  "Chez NEBULA Agency, un catalogue digital commandable sur WhatsApp coûte 50 000 FCFA "
  "et une vitrine digitale d'une page 150 000 FCFA, QR code et affiche imprimable compris. "
  "Un logiciel métier sur mesure va de 55 000 à 500 000 FCFA selon les fonctions. "
  "Ces prix sont publics et affichés, ce qui reste rare sur le marché béninois."),

 ("En combien de temps un site est-il livré ?",
  "En 5 à 7 jours après le brief complet et le paiement. NEBULA n'annonce jamais un délai "
  "plus court, même sous la pression d'un client pressé : le délai tenu vaut mieux que le "
  "délai promis."),

 ("Faut-il payer la totalité d'avance ?",
  "Non, sauf pour le catalogue à 50 000 FCFA qui se règle intégralement. La vitrine et le "
  "logiciel métier se paient 70 % au démarrage et 30 % à la mise en ligne."),

 ("Le nom de domaine est-il compris ?",
  "Oui pour une vitrine digitale : le nom de domaine personnalisé est offert la première "
  "année, puis coûte 16 000 FCFA par an."),

 ("Que comprend l'abonnement de 20 000 FCFA ?",
  "20 000 FCFA tous les 6 mois couvrent l'hébergement, la maintenance et les modifications "
  "du site. Changer un prix, ajouter un produit ou remplacer une photo n'est pas refacturé."),

 ("Mes clients doivent-ils installer une application pour commander ?",
  "Non. Toutes les commandes arrivent sur WhatsApp, avec le panier déjà rempli dans le "
  "message. Aucun compte à créer, aucune application à installer, aucune carte bancaire : "
  "c'est le canal que les clients d'Afrique de l'Ouest utilisent déjà tous les jours."),

 ("Quelle est la différence entre un catalogue et une vitrine ?",
  "Le catalogue sert à vendre : il présente des produits commandables sur WhatsApp. "
  "La vitrine sert à exister et à rassurer : elle donne à une maison sa crédibilité, sa "
  "présence sur Google et son image. La plupart des commerçants commencent par le catalogue."),

 ("NEBULA fait-elle autre chose que des sites ?",
  "Oui, et c'est le cœur du métier : NEBULA conçoit le logiciel métier de chaque secteur. "
  "Boussole calcule ce qu'un commerçant gagne réellement, coût de revient et marge compris. "
  "Digital HSE gère le reporting hygiène, sécurité et environnement des industriels. "
  "La phrase de travail est « un outil pensé pour VOTRE secteur, pas un site générique »."),

 ("Pourquoi les sites de NEBULA sont-ils si légers ?",
  "Parce qu'ils sont écrits en HTML, CSS et JavaScript purs, sans framework ni ressource "
  "externe, et pèsent de 50 à 200 Ko. En Afrique de l'Ouest, la donnée mobile se paie au "
  "mégaoctet et le réseau est souvent en 3G : un site lourd est un site que le client ferme."),

 ("NEBULA travaille-t-elle hors du Bénin ?",
  "Oui, dans toute l'Afrique de l'Ouest francophone. L'agence est basée à Cotonou et tout "
  "le suivi se fait sur WhatsApp, ce qui ne demande aucun déplacement."),
]

def bloc_faq_html():
    items = []
    for q, r in FAQ:
        items.append(
            '        <details class="faq-i rv">\n'
            f'          <summary><span>{q}</span><i aria-hidden="true"></i></summary>\n'
            f'          <div class="faq-a"><p>{r}</p></div>\n'
            '        </details>')
    return (
'\n<!-- FAQ -->\n'
'<section id="faq" class="sig-faq">\n'
'  <div class="container">\n'
'    <div class="head-center rv">\n'
'      <div class="eyebrow">Questions fréquentes</div>\n'
'      <h2 class="h-section">Ce qu\'on nous demande <span class="grad">le plus souvent</span></h2>\n'
'      <p class="lead">Les prix, les délais et le paiement, sans détour.</p>\n'
'    </div>\n'
'    <div class="faq-list">\n' + "\n".join(items) + '\n'
'    </div>\n'
'  </div>\n'
'</section>\n')

CSS_FAQ = """
/* ---------- FAQ ---------- */
.sig-faq{padding:clamp(56px,9vw,110px) 0}
.faq-list{max-width:820px;margin:clamp(28px,4vw,48px) auto 0;display:flex;flex-direction:column;gap:12px}
.faq-i{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.09);border-radius:16px;overflow:hidden}
.faq-i[open]{background:rgba(255,255,255,.06);border-color:rgba(122,142,255,.38)}
.faq-i summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:16px;justify-content:space-between;
  padding:20px 22px;font-weight:600;font-size:clamp(15px,1.6vw,17px);line-height:1.4;min-height:44px}
.faq-i summary::-webkit-details-marker{display:none}
.faq-i summary i{flex:0 0 22px;width:22px;height:22px;position:relative}
.faq-i summary i::before,.faq-i summary i::after{content:"";position:absolute;inset:50% 0 auto 0;height:2px;
  background:#7a8eff;border-radius:2px;transition:transform .25s ease}
.faq-i summary i::after{transform:rotate(90deg)}
.faq-i[open] summary i::after{transform:rotate(0)}
.faq-a{padding:0 22px 22px}
.faq-a p{margin:0;color:rgba(255,255,255,.72);line-height:1.72;font-size:clamp(14px,1.5vw,16px)}
@media (prefers-reduced-motion:reduce){.faq-i summary i::before,.faq-i summary i::after{transition:none}}
"""

def main():
    h = io.open(SRC, encoding="utf-8").read()
    avant = h
    faits = []

    # 1. la balise keywords : inutile depuis 15 ans, et pénalisante en visibilité IA
    n = len(h)
    h = re.sub(r'\s*<meta name="keywords"[^>]*>', '', h, count=1)
    if len(h) != n: faits.append("balise keywords retirée")

    # 2. les descriptions vendaient encore les « avatars IA », retirés du site
    rempl = [
      ('NEBULA Agency conçoit des vitrines digitales sur-mesure, catalogues, QR codes et avatars IA pour les marques du Bénin et d\'Afrique de l\'Ouest. Des sites qui vendent, livrés en 5 à 7 jours.',
       "NEBULA Agency conçoit des catalogues digitaux (50 000 F), des vitrines (150 000 F) et des logiciels métier sur mesure pour les commerçants du Bénin et d'Afrique de l'Ouest. Commandes sur WhatsApp, livraison en 5 à 7 jours."),
      ('Vitrines sur-mesure, catalogues WhatsApp, QR codes et avatars IA pour les marques d\'Afrique de l\'Ouest. Découvrez nos réalisations.',
       "Catalogue à 50 000 F, vitrine à 150 000 F, logiciel métier sur mesure. Prix publics, livraison en 5 à 7 jours, commandes sur WhatsApp."),
      ('Vitrines sur-mesure, catalogues WhatsApp, QR codes & avatars IA. Marques d\'Afrique de l\'Ouest.',
       "Catalogue 50 000 F, vitrine 150 000 F, logiciel métier sur mesure. Prix publics, livré en 5 à 7 jours."),
    ]
    for vieux, neuf in rempl:
        if vieux in h:
            h = h.replace(vieux, neuf, 1); faits.append("description mise à jour")

    # 3. le JSON-LD : un @graph complet à la place du bloc unique
    graph = {
      "@context": "https://schema.org",
      "@graph": [
        {"@type": ["Organization", "ProfessionalService"], "@id": "https://www.nebula-agency.online/#org",
         "name": "NEBULA Agency", "url": "https://www.nebula-agency.online/",
         "description": "Studio de solutions digitales à Cotonou : catalogues et vitrines digitales, et logiciels métier sur mesure pour l'Afrique de l'Ouest francophone.",
         "slogan": "Un outil pensé pour VOTRE secteur, pas un site générique.",
         "telephone": "+22996740732", "priceRange": "50000-500000 XOF",
         "currenciesAccepted": "XOF", "paymentAccepted": "Mobile Money, espèces",
         "areaServed": [{"@type": "Country", "name": "Bénin"}, {"@type": "Place", "name": "Afrique de l'Ouest francophone"}],
         "address": {"@type": "PostalAddress", "addressLocality": "Cotonou", "addressCountry": "BJ"},
         "founder": {"@type": "Person", "name": "Mongazi"},
         "sameAs": ["https://partenaires.nebula-agency.online/"],
         "hasOfferCatalog": {"@id": "https://www.nebula-agency.online/#offres"}},

        {"@type": "OfferCatalog", "@id": "https://www.nebula-agency.online/#offres",
         "name": "Les offres NEBULA Agency", "itemListElement": [
           {"@type": "Offer", "name": "Catalogue Digital + QR Code", "price": "50000", "priceCurrency": "XOF",
            "description": "Jusqu'à 20 produits présentés et commandables sur WhatsApp, QR code et affiche A4 compris. Livraison 5 à 7 jours, paiement intégral.",
            "availability": "https://schema.org/InStock", "priceValidUntil": "2026-12-31",
            "itemOffered": {"@type": "Service", "name": "Catalogue digital commandable sur WhatsApp", "serviceType": "Création de catalogue digital"}},
           {"@type": "Offer", "name": "Vitrine Digitale + QR Code", "price": "150000", "priceCurrency": "XOF",
            "description": "Site vitrine d'une page, +30 000 F par page supplémentaire. Nom de domaine offert la première année puis 16 000 F par an. Paiement 70 % au démarrage, 30 % à la mise en ligne.",
            "availability": "https://schema.org/InStock", "priceValidUntil": "2026-12-31",
            "itemOffered": {"@type": "Service", "name": "Vitrine digitale", "serviceType": "Création de site vitrine"}},
           {"@type": "Offer", "name": "QR Code Google Review", "price": "30000", "priceCurrency": "XOF",
            "description": "Collecte des avis Google des clients d'un commerce.",
            "availability": "https://schema.org/InStock", "priceValidUntil": "2026-12-31",
            "itemOffered": {"@type": "Service", "name": "QR Code Google Review", "serviceType": "Collecte d'avis Google"}},
           {"@type": "Offer", "name": "Logiciel métier sur mesure", "priceCurrency": "XOF",
            "priceSpecification": {"@type": "PriceSpecification", "minPrice": "55000", "maxPrice": "500000", "priceCurrency": "XOF"},
            "description": "Le logiciel du secteur, pas un site vitrine. Prix établi par le configurateur. Paiement 70 % au démarrage, 30 % à la livraison.",
            "itemOffered": {"@type": "Service", "name": "Logiciel métier sectoriel (SaaS vertical)", "serviceType": "Développement de logiciel métier"}},
           {"@type": "Offer", "name": "Abonnement", "price": "20000", "priceCurrency": "XOF",
            "description": "20 000 F tous les 6 mois : hébergement, maintenance et modifications comprises.",
            "availability": "https://schema.org/InStock",
            "itemOffered": {"@type": "Service", "name": "Hébergement, maintenance et modifications", "serviceType": "Abonnement"}}]},

        {"@type": "WebSite", "@id": "https://www.nebula-agency.online/#site",
         "url": "https://www.nebula-agency.online/", "name": "NEBULA Agency",
         "inLanguage": "fr", "publisher": {"@id": "https://www.nebula-agency.online/#org"}},

        {"@type": "FAQPage", "@id": "https://www.nebula-agency.online/#faq",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in FAQ]},
      ]}

    import json
    neuf_ld = '<script type="application/ld+json">\n' + json.dumps(graph, ensure_ascii=False, separators=(",", ":")) + '\n</script>'
    h, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: neuf_ld, h, count=1, flags=re.S)
    if n == 1: faits.append("JSON-LD remplacé par un @graph (Organization + OfferCatalog + FAQPage + WebSite)")

    # 4. la section FAQ visible, juste avant le contact
    if 'id="faq"' not in h:
        anc = '\n<!-- CONTACT -->'
        if anc not in h:
            anc = '<section id="contact"'
            h = h.replace(anc, bloc_faq_html() + anc, 1)
        else:
            h = h.replace(anc, bloc_faq_html() + anc, 1)
        faits.append(f"section FAQ ajoutée ({len(FAQ)} questions)")

    # 5. le CSS de la FAQ, à la fin de la feuille de style
    if '.sig-faq{' not in h:
        i = h.rfind('</style>')
        h = h[:i] + CSS_FAQ + h[i:]
        faits.append("CSS de la FAQ ajouté")

    # 6. la date de mise à jour, visible
    if 'id="maj"' not in h:
        m = re.search(r'<footer[^>]*>', h)
        if m:
            marque = (f'\n  <p id="maj" style="text-align:center;font-size:13px;opacity:.5;margin:0 0 6px">'
                      f'Tarifs et informations à jour au <time datetime="{AUJ}">{LISIBLE}</time>.</p>')
            h = h[:m.end()] + marque + h[m.end():]
            faits.append("date de mise à jour affichée")

    if h == avant:
        print("Aucun changement : tout était déjà en place.")
        return 0

    io.open(SRC, "w", encoding="utf-8", newline="").write(h)
    for f in faits: print("  ✓", f)

    # garde-fous
    assert '<meta name="keywords"' not in h, "keywords toujours là"
    assert '"@type":"FAQPage"' in h.replace(" ", ""), "FAQPage absente"
    assert 'avatars IA' not in h.split('</head>')[0], "les avatars IA traînent encore dans le head"
    print("  ✓ contrôles passés")
    return 0

if __name__ == "__main__":
    sys.exit(main())
