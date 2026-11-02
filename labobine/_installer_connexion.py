# LA BOBINE · étape 5 de INSTALLER-COMPTES.md : la connexion par e-mail du projet Supabase PARTAGÉ.
#   python -I labobine/_installer_connexion.py
# ⛔ Seulement avec l'accord de Mongazi : la configuration Auth sert aussi Boussole.
# Aucun secret ici, tout est lu dans secrets/. Rejouable : la clé Resend n'est créée qu'une fois.
#
# Ce que ça fait :
#   1. crée une clé Resend qui ne sait qu'ENVOYER, et seulement depuis nebula-agency.online (DKIM + SPF vérifiés),
#      rangée dans secrets/supabase.env (RESEND_SMTP_KEY) ;
#   2. branche cette clé comme SMTP de Supabase Auth (sans SMTP, Supabase n'écrit qu'aux membres de l'équipe,
#      2 e-mails par heure : aucun client ne peut se connecter) ;
#   3. ajoute LA BOBINE aux adresses de retour autorisées, en gardant celle de Boussole ;
#   4. met les modèles « Magic Link » et « Confirm signup » en français, avec le code (8 chiffres) en plus du lien.
import json
import pathlib
import urllib.request

R = pathlib.Path(__file__).resolve().parent.parent / "secrets"
PROJET = "https://api.supabase.com/v1/projects/xukduhqqfzogisoimhyo/config/auth"
DOMAINE_RESEND = "e024260b-0d8c-458d-9c91-d10b395fc27a"  # nebula-agency.online
RETOURS = [
    "https://boussole-19d.pages.dev/**",
    "https://labobine.pages.dev/**",
    "https://labobine.nebula-agency.online/**",
]


def lire(nom):
    d = {}
    for ligne in (R / nom).read_text(encoding="utf-8").splitlines():
        if "=" in ligne and not ligne.lstrip().startswith("#"):
            k, v = ligne.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def http(methode, url, jeton, corps=None):
    req = urllib.request.Request(
        url, method=methode, data=json.dumps(corps).encode() if corps is not None else None,
        headers={"Authorization": f"Bearer {jeton}", "Content-Type": "application/json", "User-Agent": "nebula-install/1"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"null")


sb, nf = lire("supabase.env"), lire("nebula-affilies.env")

cle = sb.get("RESEND_SMTP_KEY", "")
if not cle:
    k = http("POST", "https://api.resend.com/api-keys", nf["RESEND_API_KEY"],
             {"name": "supabase-auth-smtp", "permission": "sending_access", "domain_id": DOMAINE_RESEND})
    cle = k["token"]
    with open(R / "supabase.env", "a", encoding="utf-8") as f:
        f.write("\n# Resend : cle d'ENVOI seule (domaine nebula-agency.online), mot de passe SMTP de Supabase Auth\n"
                f"RESEND_SMTP_KEY={cle}\n")
    print("clé Resend d'envoi créée et rangée dans secrets/supabase.env")

# On garde les adresses déjà autorisées, on ajoute les nôtres.
actuel = http("GET", PROJET, sb["SUPABASE_ACCESS_TOKEN"])
retours = [u for u in (actuel.get("uri_allow_list") or "").split(",") if u.strip()]
for u in RETOURS:
    if u not in retours:
        retours.append(u)

BOUTON = ('style="display:inline-block;background:#ffd23f;color:#14110e;padding:12px 22px;'
          'border-radius:999px;text-decoration:none;font-weight:600"')
CODE = ("<p>Ou tape ce code si l'application te le demande :</p>\n"
        '<p style="font-size:26px;letter-spacing:4px;font-weight:700">{{ .Token }}</p>')
FIN = ('<p style="color:#777;font-size:13px">Ce lien et ce code ne servent qu\'une fois et expirent dans une heure. '
       "Si tu n'as rien demandé, ignore cet e-mail.</p>")


def modele(titre, phrase, bouton):
    return (f"<h2>{titre}</h2>\n<p>{phrase}</p>\n"
            f'<p><a href="{{{{ .ConfirmationURL }}}}" {BOUTON}>{bouton}</a></p>\n{CODE}\n{FIN}')


http("PATCH", PROJET, sb["SUPABASE_ACCESS_TOKEN"], {
    "uri_allow_list": ",".join(retours),
    "smtp_host": "smtp.resend.com", "smtp_port": "465", "smtp_user": "resend", "smtp_pass": cle,
    "smtp_admin_email": "connexion@nebula-agency.online", "smtp_sender_name": "NEBULA Agency",
    "rate_limit_email_sent": 60,
    "mailer_subjects_magic_link": "Ton lien de connexion",
    "mailer_templates_magic_link_content": modele("Ton lien de connexion", "Touche le bouton pour te connecter.", "Me connecter"),
    "mailer_subjects_confirmation": "Confirme ton adresse e-mail",
    "mailer_templates_confirmation_content": modele(
        "Confirme ton adresse e-mail", "Touche le bouton pour confirmer ton adresse et terminer ton inscription.",
        "Confirmer mon adresse"),
})

a = http("GET", PROJET, sb["SUPABASE_ACCESS_TOKEN"])
for k in ("site_url", "uri_allow_list", "smtp_host", "smtp_admin_email", "smtp_sender_name", "rate_limit_email_sent",
          "mailer_subjects_magic_link", "mailer_subjects_confirmation"):
    print(f"{k} = {a.get(k)}")
print("code dans les deux modèles :",
      all("{{ .Token }}" in (a.get(x) or "") for x in ("mailer_templates_magic_link_content", "mailer_templates_confirmation_content")))
