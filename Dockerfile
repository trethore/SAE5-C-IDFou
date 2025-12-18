# Basé sur l'image officielle
FROM postgres:18.0

# 1. Installer les outils de compilation nécessaires
# (build-essential pour gcc, make, etc. et postgresql-server-dev-18 pour les headers)
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-server-dev-18 \
    git \
    ca-certificates \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 2. Télécharger le code source de pgvector
RUN git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git /usr/local/src/pgvector

# 3. Compiler et installer l'extension (elle sera copiée dans le répertoire des extensions de Postgres)
WORKDIR /usr/local/src/pgvector
RUN make && make install

# 4. Nettoyer les outils de compilation pour réduire la taille de l'image finale
# Ceci est crucial pour une image de production légère
RUN apt-get purge -y --auto-remove build-essential git postgresql-server-dev-18

# Retour au répertoire de travail par défaut
WORKDIR /
