# Déploiement Railway du bureau virtuel des affiliés NEBULA.
# Le service "nebula-affilies" est branché sur ce dépôt monorepo et construit
# depuis la racine → ce Dockerfile cible explicitement le sous-dossier nebula-affilies/.
# (N'affecte aucun autre service : les autres se déploient via `railway up` depuis leur propre dossier.)
FROM python:3.12-slim

WORKDIR /app

COPY nebula-affilies/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY nebula-affilies/ ./

ENV PORT=8080
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT}"]
