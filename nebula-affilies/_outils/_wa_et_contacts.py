# -*- coding: utf-8 -*-
"""
Trois corrections demandées par Mongazi, plus une analyse du formulaire.

1. « ENVOYER SUR WHATSAPP » N'OUVRAIT PAS LA BONNE CONVERSATION.
   Le kit de bienvenue ouvrait `wa.me/?text=…`, **sans destinataire** : WhatsApp
   s'ouvrait, mais il fallait choisir le contact à la main. Le numéro existe
   pourtant : il est dans la candidature. On le fait descendre jusqu'au bouton,
   et on passe par `waLink()`, qui sait déjà normaliser un numéro béninois.

2. L'EMAIL DEVIENT OBLIGATOIRE.
   Il était facultatif, donc l'email d'accès automatique ne partait pas toujours,
   et le partenaire n'avait que WhatsApp pour recevoir ses codes. Deux canaux
   valent mieux qu'un quand on transmet un mot de passe.

3. APRÈS LA CANDIDATURE, ON DIT QUOI SURVEILLER.
   Le message de confirmation ne disait pas où la réponse arriverait. Il le dit
   maintenant, en nommant les deux canaux.

Idempotent, UTF-8 strict.
    python nebula-affilies/_outils/_wa_et_contacts.py
"""
import io, re, sys
from pathlib import Path

RACINE = Path(r"C:/Users/USER/nebula-agency/nebula-affilies")


def main():
    faits = []

    # ================= 1. le bouton WhatsApp du kit =========================
    p = RACINE / "admin.html"
    h = io.open(p, encoding="utf-8").read()

    if "numero" not in h.split("function renderAccessKit(")[1].split(")")[0]:
        h = h.replace(
            "function renderAccessKit({ title, code, pin, name, onDone, emailSent, email }) {",
            "function renderAccessKit({ title, code, pin, name, onDone, emailSent, email, numero }) {", 1)
        faits.append("le kit accepte le numéro du partenaire")

    # le lien : avec destinataire quand on connaît le numéro
    vieux_lien = "document.getElementById('am-wa').href = 'https://wa.me/?text=' + encodeURIComponent(msg);"
    neuf_lien = (
        "  // Avec le numéro, WhatsApp ouvre DIRECTEMENT la conversation de la personne.\n"
        "  // Sans lui, il ouvrait juste WhatsApp et il fallait chercher le contact.\n"
        "  const bWa = document.getElementById('am-wa');\n"
        "  bWa.href = numero ? waLink(numero, msg) : 'https://wa.me/?text=' + encodeURIComponent(msg);\n"
        "  bWa.textContent = '';\n"
        "  bWa.innerHTML = (numero ? 'Envoyer à ' + esc(String(numero)) : 'Envoyer sur WhatsApp')\n"
        "    + '<span class=\"ico\">' + icon('phone') + '</span>';")
    if vieux_lien in h:
        h = h.replace(vieux_lien, neuf_lien, 1)
        faits.append("le bouton ouvre la conversation de la personne, pas WhatsApp en général")

    # faire descendre le numéro depuis les 4 points d'appel
    h = h.replace(
        "function showAccessModal(title, code, pin, onDone, emailSent, email) { renderAccessKit({ title, code, pin, onDone, emailSent, email }); }",
        "function showAccessModal(title, code, pin, onDone, emailSent, email, numero) { renderAccessKit({ title, code, pin, onDone, emailSent, email, numero }); }", 1)
    h = h.replace("showAccessModal('Candidature validée', d.code, d.pin, renderRecrues, d.email_sent, d.email)",
                  "showAccessModal('Candidature validée', d.code, d.pin, renderRecrues, d.email_sent, d.email, d.numero)")
    h = h.replace("showAccessModal('Recrue validée', d.code, d.pin, renderRecrues, d.email_sent, d.email)",
                  "showAccessModal('Recrue validée', d.code, d.pin, renderRecrues, d.email_sent, d.email, d.numero)")
    h = h.replace("renderAccessKit({ title: 'Partenaire créé', code: d.code, pin: d.pin, name: (body.prenom + ' ' + body.nom).trim(), onDone: renderAff })",
                  "renderAccessKit({ title: 'Partenaire créé', code: d.code, pin: d.pin, name: (body.prenom + ' ' + body.nom).trim(), onDone: renderAff, numero: body.numero || body.momo_number })")
    io.open(p, "w", encoding="utf-8", newline="").write(h)
    if "d.numero" in h:
        faits.append("le numéro descend depuis la validation jusqu'au bouton")

    # ================= 2. le serveur renvoie le numéro ======================
    p = RACINE / "server.py"
    s = io.open(p, encoding="utf-8").read()
    avant = s
    # partout où l'on répond avec code+pin après validation, on ajoute le numéro
    s = re.sub(r'(\{"ok": True, "code": code, "pin": pin)(,?)',
               lambda m: m.group(1) + ', "numero": (r["numero"] if r else "")' + (m.group(2) or ""), s)
    if s != avant:
        faits.append("le serveur renvoie le numéro avec les accès")

    # l'email devient obligatoire à la candidature
    vieux = '''    email = clean(d.get("email"), 120); ville = clean(d.get("ville"), 80)'''
    neuf = '''    email = clean(d.get("email"), 120); ville = clean(d.get("ville"), 80)
    # L'email est OBLIGATOIRE depuis le 2026-08-03 : c'est le second canal par
    # lequel arrivent les accès. Avec le seul WhatsApp, un numéro mal saisi et
    # le partenaire ne reçoit jamais son code.
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return JSONResponse({"ok": False, "error": "Une adresse email valide est obligatoire : c'est là que NEBULA envoie tes accès."}, status_code=400)'''
    if vieux in s and "OBLIGATOIRE depuis le 2026-08-03" not in s:
        s = s.replace(vieux, neuf, 1)
        faits.append("email obligatoire, vérifié côté serveur")

    io.open(p, "w", encoding="utf-8", newline="").write(s)

    if not faits:
        print("  Tout était déjà en place.")
        return 0
    for x in faits:
        print("  ✓", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
