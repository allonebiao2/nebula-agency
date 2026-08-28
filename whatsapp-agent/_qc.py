"""LA SUITE DE CONTRÔLES — verte avant tout déploiement, sans clé et sans réseau.

    python whatsapp-agent/_qc.py

⚠️ AUCUN CONTRÔLE NE RECOPIE UN CHIFFRE DE LA CARTE. Écrire ici « 52 articles »
ou « le tilapia est à 3 000 F » fabriquerait la deuxième vérité que tout ce kit
existe pour éviter : le jour où la maison change un prix, c'est le contrôle qui
deviendrait faux. Les contrôles LISENT les deux côtés et les comparent.

⚠️ ILS TOURNENT SANS `anthropic` ET SANS RÉSEAU. Un contrôle qui a besoin d'une
clé ne tourne jamais, et un contrôle qui ne tourne jamais ne protège rien. Le
modèle est remplacé par `tests/faux.py`, qui rejoue des réponses écrites : c'est
la seule façon de vérifier qu'un prix inventé est VRAIMENT bloqué — un vrai
modèle refuserait justement de l'inventer le jour du test.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

RACINE_KIT = Path(__file__).resolve().parent
RACINE = RACINE_KIT.parent
sys.path.insert(0, str(RACINE_KIT))

from agent import maison as maisons_mod                      # noqa: E402
from agent.catalogue import Catalogue, Prix, _pliable        # noqa: E402
from agent.cerveau import Cerveau, contexte, socle           # noqa: E402
from agent.garde_prix import GardePrix, relever              # noqa: E402
from agent.memoire import Memoire, maintenant                # noqa: E402
from agent.service import Service, charger_catalogue         # noqa: E402
from canaux.console import CanalConsole                      # noqa: E402
from canaux.meta import CanalMeta                            # noqa: E402
from canaux.twilio import CanalTwilio                        # noqa: E402
from lecteurs import braise, hillary                         # noqa: E402
from lecteurs.js_litteral import ErreurLitteral, lire_declaration  # noqa: E402
from tests.faux import FauxModele                            # noqa: E402

VERTS: list[str] = []
ROUGES: list[str] = []


def controle(titre: str, condition, detail: str = "") -> bool:
    try:
        bon = bool(condition() if callable(condition) else condition)
    except Exception as exc:  # noqa: BLE001 — un contrôle qui explose est un contrôle rouge
        bon, detail = False, f"{type(exc).__name__}: {exc}"
    (VERTS if bon else ROUGES).append(titre if bon else f"{titre} — {detail}")
    return bon


def base_neuve() -> Memoire:
    return Memoire(Path(tempfile.mkdtemp()) / "qc.db")


def service_faux(fiche: str, scenario: list, catalogue=None):
    """Un service complet dont seul le modèle est simulé."""
    maison = maisons_mod.charger(RACINE_KIT / "maisons" / f"{fiche}.yaml")
    maison.numero_patron = maison.numero_patron or "22900000001"
    faux = FauxModele(scenario)
    canal = CanalConsole()
    service = Service(maison, RACINE, base_neuve(), canal, client=faux, catalogue=catalogue)
    return service, faux, canal


# =====================================================================
# 1. LE LECTEUR DE LITTÉRAUX
# =====================================================================
def controles_parseur() -> None:
    src = (RACINE / braise.CHEMIN).read_text(encoding="utf-8")

    controle("parseur · trouve CARTE malgré l'annotation « : Cat[] »",
             lambda: isinstance(lire_declaration(src, "CARTE"), list))
    controle("parseur · trouve ACC malgré « : Record<string, string[]> »",
             lambda: isinstance(lire_declaration(src, "ACC"), dict))
    controle("parseur · une MENTION n'est pas une déclaration (NB_PLATS = CARTE.reduce)",
             lambda: len(lire_declaration(src, "CARTE")) > 1)
    controle("parseur · commentaires // et /* */ ignorés",
             lambda: lire_declaration(
                 'const X = /* mot */ [1, // deux\n 3];', "X") == [1, 3])
    controle("parseur · virgule finale tolérée",
             lambda: lire_declaration('const X = {a: 1, b: 2,};', "X") == {"a": 1, "b": 2})
    controle("parseur · apostrophe échappée dans une chaîne",
             lambda: lire_declaration(
                 """const X = {d: 'l\\'atelier'};""", "X") == {"d": "l'atelier"})
    controle("parseur · guillemets doubles et simples mélangés",
             lambda: lire_declaration("""const X = {"a": 'b'};""", "X") == {"a": "b"})
    controle("parseur · nombres négatifs et décimaux",
             lambda: lire_declaration("const X = [-3, 1.5];", "X") == [-3, 1.5])
    controle("parseur · true / false / null",
             lambda: lire_declaration("const X = [true, false, null];", "X") == [True, False, None])
    controle("parseur · tableaux imbriqués (les paliers de la glace)",
             lambda: lire_declaration("const X = [['a',1],['b',2]];", "X") == [["a", 1], ["b", 2]])

    def declaration_absente() -> bool:
        try:
            lire_declaration("const Y = 1;", "ZZZ")
        except ErreurLitteral:
            return True
        return False
    controle("parseur · une déclaration absente lève une erreur NOMMÉE, pas None",
             declaration_absente)

    def jamais_de_eval() -> bool:
        source = (RACINE_KIT / "lecteurs" / "js_litteral.py").read_text(encoding="utf-8")
        return "eval(" not in source and "exec(" not in source
    controle("parseur · aucun eval/exec sur un fichier du dépôt", jamais_de_eval)


# =====================================================================
# 2. LES CATALOGUES, LUS DANS LES VRAIS FICHIERS
# =====================================================================
def controles_catalogue() -> None:
    carte = braise.charger(RACINE)
    pieces = hillary.charger(RACINE)

    controle("braise · le fichier source existe vraiment",
             (RACINE / carte.source).exists(), carte.source)
    controle("hillary · le fichier source existe vraiment",
             (RACINE / pieces.source).exists(), pieces.source)

    # Les DEUX côtés sont lus : aucun nombre n'est écrit ici.
    brut = lire_declaration((RACINE / braise.CHEMIN).read_text(encoding="utf-8"), "CARTE")
    attendus = sum(len(c.get("items", [])) for c in brut)
    controle("braise · tous les plats du fichier arrivent au catalogue",
             len(carte) == attendus, f"{len(carte)} lus contre {attendus} dans le fichier")

    bruts_h = lire_declaration(
        (RACINE / hillary.CHEMIN).read_text(encoding="utf-8"), "PIECES")
    controle("hillary · toutes les pièces du fichier arrivent au catalogue",
             len(pieces) == len(bruts_h), f"{len(pieces)} contre {len(bruts_h)}")

    controle("braise · aucun article sans nom",
             all(a.nom.strip() for a in carte.articles))
    controle("braise · aucune catégorie vide",
             all(c.articles for c in carte.categories))
    controle("braise · aucun article sans catégorie",
             all(a.categorie for a in carte.articles))

    modes = {a.prix.mode for a in carte.articles}
    controle("braise · les quatre modes de prix connus sont représentés",
             {"simple", "deux_tailles", "fourchette", "paliers"} <= modes, sorted(modes))

    # La glace : le bug documenté du 2026-08-26 (encaisser 1 000 au lieu de 2 500).
    glace = carte.trouver("Glace")
    brut_glace = next((i for c in brut for i in c["items"] if i["n"] == "Glace"), None)
    controle("braise · la glace suit son BARÈME, pas son prix d'appel",
             glace and brut_glace and glace.prix.mode == "paliers"
             and glace.prix.haut == max(m for _, m in brut_glace["paliers"]),
             f"mode={glace.prix.mode if glace else '?'}")
    controle("braise · chaque cran du barème est repris tel quel",
             glace and [m for _, m in glace.prix.montants]
             == [m for _, m in brut_glace["paliers"]])

    fourchettes = [a for a in carte.articles if a.prix.mode == "fourchette"]
    controle("braise · toute fourchette a une borne haute STRICTEMENT au-dessus",
             fourchettes and all(a.prix.haut > a.prix.bas for a in fourchettes))
    controle("braise · une fourchette n'est jamais confondue avec deux tailles",
             all(not (i.get("pMax") and i.get("p2")) for c in brut for i in c["items"]))

    controle("braise · aucun montant à zéro dans les prix connus",
             all(m > 0 for a in carte.articles if a.prix.connu for _, m in a.prix.montants))
    controle("catalogue · « p: 0 » devient « prix sur demande », jamais 0 F",
             braise._prix({"p": 0}).mode == "sur_demande")
    controle("catalogue · un article sans prix n'entre dans aucun total",
             not Prix("sur_demande").acceptable(1000))

    # Hillary : le supplément express est propre à chaque pièce.
    ecarts = {p["expPrix"] - p["prix"] for p in bruts_h if p.get("expPrix") and p.get("prix")}
    controle("hillary · le supplément express DIFFÈRE d'une pièce à l'autre",
             len(ecarts) > 1, f"écarts observés : {sorted(ecarts)}")
    controle("hillary · les deux prix (normal et express) sont tous deux acceptés",
             all(GardePrix(pieces).montant_connu(p["prix"], "F")
                 and GardePrix(pieces).montant_connu(p["expPrix"], "F")
                 for p in bruts_h[:1] if p.get("expPrix")))
    libre = pieces.trouver("Création libre")
    controle("hillary · la pièce sans prix est « sur demande »",
             libre is not None and libre.prix.mode == "sur_demande")
    controle("hillary · chaque pièce annonce un délai",
             all(a.delai for a in pieces.articles))

    controle("catalogue · recherche insensible aux accents et à la casse",
             carte.trouver("SAUCE CREME") is not None)
    controle("catalogue · repli d'un nom avec apostrophe typographique",
             _pliable("L’ensemble Mira") == _pliable("L'ensemble Mira"))
    controle("catalogue · le repli ne change JAMAIS la longueur du texte",
             all(len(_pliable(x)) == len(x) for x in
                 ["L’ensemble Mira", "Café au lait écrémé", "Sauce Crème", "ŒUF"]))
    controle("catalogue · les accompagnements ne sont écrits qu'une fois",
             carte.texte().count("Accompagnements au choix") <= 1)


# =====================================================================
# 3. LE GARDE-FOU DES PRIX — le cœur
# =====================================================================
def controles_garde() -> None:
    carte = braise.charger(RACINE)
    garde = GardePrix(carte)
    pieces = hillary.charger(RACINE)
    garde_h = GardePrix(pieces)

    tilapia = carte.trouver("Tilapia braisé")
    vrai, grand = tilapia.prix.montants[0][1], tilapia.prix.montants[1][1]
    faux_prix = vrai + 1500          # calculé depuis la carte, jamais écrit en dur
    while garde._prix_de(tilapia, faux_prix):
        faux_prix += 100

    def sur(texte: str) -> bool:
        return garde.verifier(texte).sur

    controle("garde · un prix exact passe",
             sur(f"Le tilapia braisé est à {vrai} F."))
    controle("garde · la deuxième taille passe",
             sur(f"Le tilapia braisé est à {grand} F en grand."))
    controle("garde · un prix INVENTÉ sur un plat nommé est bloqué",
             not sur(f"Le tilapia braisé est à {faux_prix} F."))
    controle("garde · un montant dans la fourchette d'une sauce passe",
             sur("Une sauce gombo bien garnie vous fera 2 800 F."))
    controle("garde · un montant AU-DESSUS de la fourchette est bloqué",
             not sur("Une sauce gombo, ça monte à 4 200 F."))
    controle("garde · la somme de DEUX plats nommés passe",
             sur("Un tilapia braisé et une salade verte : 4 000 F."))
    controle("garde · deux plats, prix CROISÉS, est bloqué",
             not sur("Le cappuccino est à 600 F et le yaourt à 1 500 F."))
    controle("garde · les mêmes deux plats, chacun son prix, passe",
             sur("Le cappuccino est à 1 500 F et le yaourt à 600 F."))
    controle("garde · un palier qui n'existe pas est bloqué",
             not sur("La glace 4 boules est à 3 000 F."))
    controle("garde · un nombre APRÈS le nom ne compte pas comme quantité",
             not sur("La glace 4 boules est à 3 000 F."))
    controle("garde · une quantité AVANT le nom multiplie bien le prix",
             sur("Trois yaourts, ça fait 1 800 F."))
    controle("garde · un total inatteignable est bloqué",
             not sur("Ça vous fera 7 777 F au total."))
    controle("garde · un numéro de téléphone n'est pas un prix",
             sur("Appelez le 01 56 05 71 57."))
    controle("garde · une heure n'est pas un prix",
             sur("Nous ouvrons à 9h et fermons à 23h."))
    controle("garde · une devise que la maison n'annonce pas est bloquée",
             not sur("Cette robe coûte 150 €."))
    controle("garde · un texte sans montant passe",
             sur("Bonsoir, que puis-je pour vous ?"))

    # Les espaces insécables du rendu de la carte.
    rendu = carte.trouver("Sauce gombo").prix.texte()
    controle("garde · lit les montants du rendu de la carte (espaces insécables)",
             [m.montant for m in relever(rendu)]
             == [carte.trouver("Sauce gombo").prix.bas,
                 carte.trouver("Sauce gombo").prix.haut])
    for nom, sep in (("ordinaire", " "), ("insécable", " "),
                     ("fine insécable", " "), ("aucune", "")):
        controle(f"garde · séparateur de milliers « {nom} » reconnu",
                 sur(f"Le tilapia braisé est à 3{sep}000 F.")
                 and not sur(f"Le tilapia braisé est à 4{sep}500 F."))

    controle("garde · les mots distinctifs sont CALCULÉS, pas écrits",
             "tilapia" in garde._mots_distinctifs
             and "sauce" not in garde._mots_distinctifs)
    controle("garde · un mot porté par plusieurs plats n'attache rien",
             not garde.articles_cites("une sauce, s'il vous plaît"))
    controle("garde · le nom entier attache le bon plat",
             [a.nom for a in garde.articles_cites("le tilapia braisé")] == ["Tilapia braisé"])

    controle("garde · hillary, un prix de pièce exact passe",
             garde_h.verifier("La robe de cérémonie est à 100 000 F.").sur)
    controle("garde · hillary, un prix inventé est bloqué",
             not garde_h.verifier("La robe de cérémonie est à 85 000 F.").sur)
    controle("garde · hillary, une pièce nommée par un mot de 4 lettres est reconnue",
             [a.nom for a in garde_h.articles_cites("l’ensemble Mira")] != [])

    controle("garde · le verdict NOMME le montant fautif",
             re.search(r"\b4200\b", garde.verifier(
                 "Une sauce gombo, ça monte à 4 200 F.").explication()) is not None)
    controle("garde · le verdict nomme aussi l'article concerné",
             "Sauce gombo" in garde.verifier(
                 "Une sauce gombo, ça monte à 4 200 F.").explication())

    # Le contrôle faible est annoncé comme faible : on le MESURE.
    hi = max(a.prix.haut for a in carte.articles if a.prix.connu)
    plage = list(range(100, hi * 3, 100))
    part = sum(1 for m in plage if garde.total_atteignable(m)) / len(plage)
    controle("garde · un total NU est un contrôle faible, et on sait de combien",
             part > 0.5, f"{part:.0%} des montants ronds passent — d'où la règle "
                         f"« nomme ce que tu chiffres » dans le prompt")


# =====================================================================
# 4. LA MÉMOIRE
# =====================================================================
def controles_memoire() -> None:
    m = base_neuve()
    m.noter("x", "229", "user", "un", True)
    m.noter("x", "229", "assistant", "deux", False)
    m.noter("x", "229", "user", "trois", True)

    controle("mémoire · l'historique sort DANS L'ORDRE",
             [t["content"] for t in m.historique("x", "229")] == ["un", "deux", "trois"])
    controle("mémoire · l'historique commence toujours par le client",
             m.historique("x", "229")[0]["role"] == "user")

    m2 = base_neuve()
    m2.noter("x", "229", "assistant", "je parle en premier", False)
    m2.noter("x", "229", "user", "bonjour", True)
    controle("mémoire · un historique qui commencerait par l'agent est recadré",
             m2.historique("x", "229")[0]["role"] == "user")

    controle("mémoire · deux maisons ne se mélangent pas",
             m.historique("y", "229") == [])
    controle("mémoire · deux numéros ne se mélangent pas",
             m.historique("x", "228") == [])

    controle("mémoire · la fenêtre de 24 h est ouverte juste après un message",
             m.fenetre_ouverte("x", "229"))
    controle("mémoire · elle se referme au-delà de 24 h",
             not m.fenetre_ouverte("x", "229", maintenant() + timedelta(hours=25)))
    controle("mémoire · elle est fermée pour un numéro inconnu",
             not m.fenetre_ouverte("x", "000"))

    controle("mémoire · un message déjà vu est reconnu",
             not m.deja_vu("wamid.1") and m.deja_vu("wamid.1"))
    controle("mémoire · un message sans identifiant n'est jamais « déjà vu »",
             not m.deja_vu("") and not m.deja_vu(""))

    m.passer_la_main("x", "229")
    controle("mémoire · la main humaine se pose", m.main_humaine("x", "229"))
    m.reprendre("x", "229")
    controle("mémoire · et se reprend", not m.main_humaine("x", "229"))

    m.noter("x", "229", "assistant", [{"type": "text", "text": "bloc"}], False)
    controle("mémoire · un contenu en blocs se relit comme des blocs",
             isinstance(m.historique("x", "229")[-1]["content"], list))


# =====================================================================
# 5. LES CANAUX
# =====================================================================
def controles_canaux() -> None:
    import hashlib
    import hmac

    meta = CanalMeta(jeton_verification="jeton-ok", secret_app="secret-app")
    controle("meta · l'abonnement accepte le bon jeton",
             meta.verifier_abonnement("subscribe", "jeton-ok", "42") == "42")
    controle("meta · l'abonnement refuse un mauvais jeton",
             meta.verifier_abonnement("subscribe", "jeton-faux", "42") is None)
    controle("meta · l'abonnement refuse un mode inattendu",
             meta.verifier_abonnement("unsubscribe", "jeton-ok", "42") is None)

    corps = b'{"objet":"whatsapp"}'
    bonne = "sha256=" + hmac.new(b"secret-app", corps, hashlib.sha256).hexdigest()
    controle("meta · une signature valide est acceptée", meta.verifier_signature(corps, bonne))
    controle("meta · une signature falsifiée est refusée",
             not meta.verifier_signature(corps, "sha256=" + "0" * 64))
    controle("meta · un corps modifié invalide la signature",
             not meta.verifier_signature(corps + b" ", bonne))
    controle("meta · sans en-tête, c'est refusé", not meta.verifier_signature(corps, None))
    controle("meta · SANS SECRET CONFIGURÉ, tout est refusé",
             not CanalMeta().verifier_signature(corps, bonne))

    charge = {"entry": [{"changes": [{"value": {
        "contacts": [{"wa_id": "22951374793", "profile": {"name": "Awa"}}],
        "messages": [{"from": "22951374793", "id": "wamid.1", "type": "text",
                      "text": {"body": "bonsoir"}}]}}]}]}
    lus = CanalMeta.lire_entrant(charge)
    controle("meta · un message texte est lu, avec son nom de profil",
             len(lus) == 1 and lus[0].texte == "bonsoir" and lus[0].nom_profil == "Awa")
    controle("meta · un accusé de livraison ne produit AUCUN message",
             CanalMeta.lire_entrant(
                 {"entry": [{"changes": [{"value": {"statuses": [{"status": "delivered"}]}}]}]})
             == [])
    controle("meta · un appel vide ne casse rien", CanalMeta.lire_entrant({}) == [])
    controle("meta · un message vocal est lu, mais sans texte",
             (lambda r: len(r) == 1 and r[0].type == "audio" and not r[0].texte)(
                 CanalMeta.lire_entrant({"entry": [{"changes": [{"value": {"messages": [
                     {"from": "229", "id": "w2", "type": "audio",
                      "audio": {"id": "a"}}]}}]}]})))
    controle("meta · un canal non configuré n'envoie rien",
             not CanalMeta().envoyer("229", "coucou"))

    t = CanalTwilio.lire_entrant({"From": "whatsapp:+229 01 52 00 64 90",
                                  "Body": "bonjour", "MessageSid": "SM1"})
    controle("twilio · le numéro est réduit à ses chiffres",
             t and t[0].numero == "2290152006490")
    controle("twilio · un formulaire sans expéditeur ne produit rien",
             CanalTwilio.lire_entrant({"Body": "x"}) == [])
    controle("twilio · un canal non configuré n'envoie rien",
             not CanalTwilio().envoyer("229", "coucou"))

    console = CanalConsole()
    console.envoyer("229", "message")
    controle("console · garde ce qu'elle a « envoyé »", console.envoyes == [("229", "message")])


# =====================================================================
# 6. LES FICHES DE MAISON
# =====================================================================
def controles_maisons() -> None:
    fiches = sorted((RACINE_KIT / "maisons").glob("*.yaml"))
    controle("maisons · au moins une fiche existe", bool(fiches))
    for f in fiches:
        m = maisons_mod.charger(f)
        controle(f"maisons · {f.stem} se charge et nomme son lecteur", bool(m.lecteur))
        controle(f"maisons · {f.stem} a un lecteur qui existe",
                 (RACINE_KIT / "lecteurs" / f"{m.lecteur}.py").exists(), m.lecteur)
        controle(f"maisons · {f.stem} : son catalogue se lit vraiment",
                 len(charger_catalogue(m, RACINE)) > 0)
        controle(f"maisons · {f.stem} ne recopie AUCUN prix",
                 not re.search(r"\d{3,}\s*(F|FCFA|francs)", f.read_text(encoding="utf-8")),
                 "un prix dans une fiche est une deuxième vérité")

    def cle_inconnue() -> bool:
        essai = Path(tempfile.mkdtemp()) / "x.yaml"
        essai.write_text("id: x\nnom: X\nlecteur: braise\ntonn: oups\n", encoding="utf-8")
        try:
            maisons_mod.charger(essai)
        except ValueError:
            return True
        return False
    controle("maisons · une clé mal orthographiée fait ÉCHOUER le chargement", cle_inconnue)

    incomplete = maisons_mod.Maison(id="z", nom="Z", lecteur="braise", ton="t",
                                    numero_whatsapp="229")
    controle("maisons · sans numéro à prévenir, la maison n'est pas prête",
             not incomplete.prete[0])
    controle("maisons · et le manque est NOMMÉ",
             any("numero_patron" in x for x in incomplete.prete[1]))
    complete = maisons_mod.Maison(id="z", nom="Z", lecteur="braise", ton="t",
                                  numero_whatsapp="229", numero_patron="228")
    controle("maisons · complète, elle est prête", complete.prete[0])


# =====================================================================
# 7. LE PROMPT
# =====================================================================
def controles_prompt() -> None:
    maison = maisons_mod.charger(RACINE_KIT / "maisons" / "braise-dor.yaml")
    carte = braise.charger(RACINE)
    texte = socle(maison, carte)

    controle("prompt · la carte entière est dans le socle",
             all(a.nom in texte for a in carte.articles))
    controle("prompt · le socle nomme le fichier source",
             carte.source in texte)
    controle("prompt · le socle porte la règle de l'article nommé",
             "NOMME l'article" in texte)
    controle("prompt · le socle dit ce que la maison n'a pas tranché",
             all(x[:20] in texte for x in maison.a_confirmer))
    controle("prompt · le socle explique les cinq façons d'avoir un prix",
             "fourchette" in texte.lower() and "prix sur demande" in texte.lower())

    volatil = contexte(maison, "Awa")
    controle("prompt · l'heure est dans le bloc VOLATIL", ":" in volatil)
    controle("prompt · l'heure n'est PAS dans le socle mis en cache",
             not re.search(r"\b\d{2}:\d{2}\b", texte),
             "une heure dans le préfixe casserait le cache à chaque message")
    controle("prompt · le nom du client n'est pas dans le socle",
             "Awa" not in texte)
    controle("prompt · le socle ne change pas d'un appel à l'autre",
             socle(maison, carte) == texte)


# =====================================================================
# 8. LA CHAÎNE COMPLÈTE, MODÈLE SIMULÉ
# =====================================================================
def controles_chaine() -> None:
    carte = braise.charger(RACINE)
    tilapia = carte.trouver("Tilapia braisé")
    vrai = tilapia.prix.montants[0][1]
    faux_prix = vrai + 1500
    garde = GardePrix(carte)
    while garde._prix_de(tilapia, faux_prix):
        faux_prix += 100

    # --- une réponse honnête part telle quelle
    service, faux, canal = service_faux(
        "braise-dor", [f"Le tilapia braisé est à {vrai} F."])
    t = service.traiter("22900", "le prix du tilapia ?")
    controle("chaîne · une réponse juste est envoyée au client",
             t.envoye and canal.envoyes and str(vrai) in canal.envoyes[0][1])
    controle("chaîne · elle ne réveille personne", not t.reponse.escalades)
    controle("chaîne · le modèle a bien été appelé", len(faux.appels) == 1)

    # --- le modèle est celui de la maison
    controle("chaîne · le modèle utilisé est un Sonnet (règle NEBULA)",
             "sonnet" in faux.appels[0]["model"], faux.appels[0]["model"])
    controle("chaîne · les deux outils sont proposés au modèle",
             {o["name"] for o in faux.appels[0]["tools"]}
             == {"passer_la_main", "noter_la_commande"})

    # --- la mise en cache est posée là où il faut
    systeme = faux.appels[0]["system"]
    controle("chaîne · le socle porte la coupure de cache",
             systeme[0].get("cache_control") == {"type": "ephemeral"})
    controle("chaîne · le bloc volatil ne la porte PAS",
             "cache_control" not in systeme[1])
    controle("chaîne · l'heure est APRÈS la coupure",
             re.search(r"\b\d{2}:\d{2}\b", systeme[1]["text"]) is not None
             and re.search(r"\b\d{2}:\d{2}\b", systeme[0]["text"]) is None)

    # --- UN PRIX INVENTÉ N'ARRIVE JAMAIS AU CLIENT
    service, faux, canal = service_faux(
        "braise-dor", [f"Le tilapia braisé est à {faux_prix} F."])
    t = service.traiter("22901", "le prix du tilapia ?")
    envoye_client = [m for m in canal.envoyes if m[0] == "22901"]
    controle("chaîne · UN PRIX INVENTÉ NE PART PAS",
             envoye_client and str(faux_prix) not in envoye_client[0][1],
             envoye_client[0][1] if envoye_client else "rien envoyé")
    controle("chaîne · le client reçoit quand même une réponse",
             bool(envoye_client and envoye_client[0][1].strip()))
    controle("chaîne · le garde-fou marque la réponse comme non sûre",
             t.reponse.verdict is not None and not t.reponse.verdict.sur)
    controle("chaîne · et le patron est prévenu", t.patron_prevenu)
    controle("chaîne · l'alerte au patron cite ce que l'agent allait écrire",
             any(str(faux_prix) in m[1] for m in canal.envoyes if m[0] != "22901"))
    controle("chaîne · le repli ne promet aucun délai",
             not re.search(r"\b(minute|heure|demain)\b", envoye_client[0][1].lower()))

    # --- l'outil passer_la_main
    service, faux, canal = service_faux("braise-dor", [
        ("outil", "passer_la_main",
         {"raison": "réservation de table", "resume": "Le client veut réserver pour huit."}),
        "Je passe la main à la maison, elle vous répond ici."])
    t = service.traiter("22902", "je veux réserver une table pour huit")
    controle("chaîne · l'outil passer_la_main crée une escalade",
             len(t.reponse.escalades) == 1)
    controle("chaîne · le patron reçoit le motif ET le résumé",
             any("réservation" in m[1] and "huit" in m[1] for m in canal.envoyes))
    controle("chaîne · le client reçoit le message qui suit l'outil",
             any(m[0] == "22902" for m in canal.envoyes))

    # --- l'outil noter_la_commande
    service, faux, canal = service_faux("braise-dor", [
        ("outil", "noter_la_commande",
         {"articles": [{"nom": "Tilapia braisé", "quantite": 1}],
          "retrait_ou_livraison": "retrait", "total_estime": vrai}),
        f"C'est noté : un tilapia braisé, {vrai} F, à récupérer sur place."])
    t = service.traiter("22903", "je prends un tilapia")
    controle("chaîne · une commande est enregistrée", len(t.reponse.commandes) == 1)
    controle("chaîne · la maison reçoit la commande",
             any("Tilapia braisé" in m[1] for m in canal.envoyes))

    # --- le même message deux fois
    service, faux, canal = service_faux("braise-dor", ["Bonsoir !", "Bonsoir !"])
    service.traiter("22904", "bonsoir", identifiant="wamid.7")
    second = service.traiter("22904", "bonsoir", identifiant="wamid.7")
    controle("chaîne · un webhook REJOUÉ ne répond pas deux fois",
             second.doublon and len(faux.appels) == 1)

    # --- la main humaine fait taire l'agent
    service, faux, canal = service_faux("braise-dor", ["je ne devrais pas parler"])
    service.memoire.passer_la_main(service.maison.id, "22905")
    t = service.traiter("22905", "bonsoir")
    controle("chaîne · main humaine posée : l'agent se tait",
             t.reponse.sortie == "silence" and not canal.envoyes)
    controle("chaîne · et il n'appelle même pas le modèle", len(faux.appels) == 0)

    # --- le plafond anti-abus
    service, faux, canal = service_faux("braise-dor", ["ok"] * 200)
    service.maison.limite_messages = 3
    for i in range(5):
        t = service.traiter("22906", f"message {i}")
    controle("chaîne · au-delà du plafond, l'agent se tait",
             t.reponse.sortie == "silence")
    controle("chaîne · et le plafond ÉCONOMISE les appels au modèle",
             len(faux.appels) <= 3, f"{len(faux.appels)} appels")

    # --- un message sans texte
    service, faux, canal = service_faux("braise-dor", ["inutile"])
    t = service.traiter("22907", "")
    controle("chaîne · une photo ou un vocal passe à un humain, sans être ignoré",
             t.reponse.escalades and any(m[0] == "22907" for m in canal.envoyes))
    controle("chaîne · et le modèle n'est pas appelé pour rien", len(faux.appels) == 0)

    # --- sans numéro de patron, l'escalade est journalisée, pas perdue en silence
    maison = maisons_mod.charger(RACINE_KIT / "maisons" / "braise-dor.yaml")
    controle("chaîne · la fiche livrée n'invente AUCUN numéro WhatsApp",
             not maison.numero_whatsapp and not maison.numero_patron,
             "le dépôt en porte deux différents : personne n'a tranché")

    # --- l'historique se construit vraiment
    service, faux, canal = service_faux("braise-dor", ["une", "deux"])
    service.traiter("22908", "premier")
    service.traiter("22908", "second")
    envoyes = faux.appels[-1]["messages"]
    controle("chaîne · le second appel porte l'historique du premier",
             len(envoyes) >= 3 and envoyes[0]["content"] == "premier")
    controle("chaîne · l'historique alterne client / agent",
             [m["role"] for m in envoyes[:3]] == ["user", "assistant", "user"])


# =====================================================================
def main() -> int:
    for bloc in (controles_parseur, controles_catalogue, controles_garde,
                 controles_memoire, controles_canaux, controles_maisons,
                 controles_prompt, controles_chaine):
        bloc()

    for titre in VERTS:
        print(f"  ✓ {titre}")
    for titre in ROUGES:
        print(f"  ✗ {titre}")
    total = len(VERTS) + len(ROUGES)
    print(f"\n{len(VERTS)}/{total} contrôles verts")
    if ROUGES:
        print(f"⛔ {len(ROUGES)} ROUGE(S) — rien ne se déploie tant qu'il en reste un.")
        return 1
    print("✅ tout est vert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
