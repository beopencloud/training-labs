# Utiliser une image de base minimale
FROM python:3.10-slim

# Définir un répertoire de travail
WORKDIR /app

# Installer les dépendances en séparant les étapes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier seulement ce qui est nécessaire
COPY app.py .

# Utiliser un port explicite et un CMD clair
EXPOSE 5000
CMD ["python", "app.py"]

