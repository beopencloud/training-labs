# Module 03 — Pipeline CI/CD complète avec GitHub Actions

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Concevoir une pipeline CI/CD multi-stages professionnelle
- Gérer les secrets et variables d'environnement de manière sécurisée
- Gérer les artefacts et la traçabilité des builds
- Implémenter la gestion des erreurs et mécanismes de reprise
- Réutiliser des workflows avec des composite actions et reusable workflows

---

### 🔧 Prérequis

| Outil | Vérification |
|-------|--------------|
| Module 02 terminé | Dépôt `todo-api-devops` avec branches main/develop |
| Compte Docker Hub | [hub.docker.com](https://hub.docker.com) |
| Compte GitHub avec Actions activé | Onglet Actions visible |

---

### ⏱️ Durée estimée

**2h**

---

### 📁 Fichiers fournis

```
module-03-pipeline-cicd/
├── README.md
└── solution/
    └── .github/
        └── workflows/
            ├── ci.yml              ← Pipeline CI complète
            ├── cd.yml              ← Pipeline CD (déploiement)
            └── reusable-build.yml  ← Workflow réutilisable
```

---

### 📋 Étapes

#### Étape 1 — Architecture de la pipeline

Une pipeline CI/CD professionnelle se compose de **jobs distincts** qui s'enchaînent :

```
push / PR
    │
    ├── Job 1: lint          (analyse statique du code)
    │         ↓ si OK
    ├── Job 2: test          (tests unitaires + coverage)
    │         ↓ si OK
    ├── Job 3: build         (build image Docker)
    │         ↓ si OK (main seulement)
    ├── Job 4: publish       (push vers Docker Hub)
    │         ↓ si OK (main seulement)
    └── Job 5: deploy-staging (déploiement staging)
```

> 💡 **Principe "Fail Fast"** : si un job échoue, les jobs suivants ne s'exécutent pas.
> Le développeur est alerté le plus tôt possible, sans gaspiller des ressources.

---

#### Étape 2 — Configurer les secrets GitHub

Avant d'écrire la pipeline, configurez les secrets :

1. **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Nom du secret | Valeur |
|---------------|--------|
| `DOCKERHUB_USERNAME` | Votre username Docker Hub |
| `DOCKERHUB_TOKEN` | Token Docker Hub (Account Settings → Security → New Access Token) |

---

#### Étape 3 — Créer la pipeline CI

Créez `.github/workflows/ci.yml` dans votre dépôt `todo-api-devops` :

```yaml
name: CI — Lint, Test & Build

on:
  push:
    branches: [main, develop, 'feature/**', 'hotfix/**']
  pull_request:
    branches: [main, develop]

# Annuler les runs précédents sur la même branche
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: "3.12"
  IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/todo-api

jobs:
  # ── Job 1 : Analyse statique ─────────────────────────────────────────────
  lint:
    name: 🔍 Lint & Static Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Installer les dépendances de lint
        run: pip install flake8

      - name: Linter Python (flake8)
        run: flake8 app.py --max-line-length=120 --ignore=E501

  # ── Job 2 : Tests unitaires ──────────────────────────────────────────────
  test:
    name: 🧪 Tests & Coverage
    runs-on: ubuntu-latest
    needs: lint

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Installer les dépendances
        run: pip install flask pytest pytest-cov

      - name: Lancer les tests avec coverage
        run: pytest test_app.py -v --cov=app --cov-report=xml --cov-report=term-missing

      - name: Vérifier le seuil de coverage (80%)
        run: pytest test_app.py --cov=app --cov-fail-under=80

      - name: Uploader le rapport de coverage
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report-${{ github.sha }}
          path: coverage.xml
          retention-days: 30

  # ── Job 3 : Build image Docker ───────────────────────────────────────────
  build:
    name: 🐳 Build Docker Image
    runs-on: ubuntu-latest
    needs: test
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Extraire les métadonnées Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=sha-
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Se connecter à Docker Hub
        if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Builder l'image (+ push si main)
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Résumé du build
        if: github.ref == 'refs/heads/main'
        run: |
          echo "## 🐳 Image Docker publiée" >> $GITHUB_STEP_SUMMARY
          echo "**Tags:** ${{ steps.meta.outputs.tags }}" >> $GITHUB_STEP_SUMMARY
          echo "**Digest:** ${{ steps.build.outputs.digest }}" >> $GITHUB_STEP_SUMMARY

  # ── Job 4 : Notification ─────────────────────────────────────────────────
  notify:
    name: 📢 Notification
    runs-on: ubuntu-latest
    needs: [lint, test, build]
    if: failure()

    steps:
      - name: Notifier en cas d'échec
        run: |
          echo "❌ Pipeline échouée sur ${{ github.ref }}"
          echo "Commit: ${{ github.sha }}"
          echo "Auteur: ${{ github.actor }}"
          # En production : envoyer vers Slack, PagerDuty, etc.
```

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add complete CI pipeline with lint, test, build and publish"
git push origin develop
```

---

#### Étape 4 — Observer la pipeline

1. Allez dans l'onglet **Actions** de votre dépôt
2. Observez les 4 jobs s'exécuter en séquence
3. Consultez les **artifacts** — le rapport de coverage est disponible en téléchargement
4. Consultez le **Job Summary** (résumé automatique du build)

---

#### Étape 5 — Tester la gestion des erreurs

Introduisez volontairement une erreur de lint :

```python
# Dans app.py, ajoutez une ligne avec un problème de style
x=1  # Pas d'espaces autour du = → flake8 va échouer
```

```bash
git add app.py
git commit -m "test: trigger lint failure intentionally"
git push origin develop
```

> ✅ **Résultat attendu** : le job `lint` échoue, `test` et `build` ne se lancent pas.
> Corrigez et re-poussez pour revenir au vert.

---

#### Étape 6 — Créer un workflow réutilisable

Les **reusable workflows** permettent de partager des pipelines entre plusieurs dépôts.

Créez `.github/workflows/reusable-build.yml` :

```yaml
name: Reusable — Build & Publish

on:
  workflow_call:
    inputs:
      image-name:
        required: true
        type: string
      push:
        required: false
        type: boolean
        default: false
    secrets:
      DOCKERHUB_USERNAME:
        required: true
      DOCKERHUB_TOKEN:
        required: true
    outputs:
      image-digest:
        description: "Image digest"
        value: ${{ jobs.build.outputs.digest }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.build.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        if: inputs.push
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ inputs.push }}
          tags: ${{ inputs.image-name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

#### Étape 7 — Créer la pipeline CD (déploiement staging)

Créez `.github/workflows/cd.yml` :

```yaml
name: CD — Deploy to Staging

on:
  workflow_run:
    workflows: ["CI — Lint, Test & Build"]
    branches: [main]
    types: [completed]

jobs:
  deploy-staging:
    name: 🚀 Deploy to Staging
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    environment:
      name: staging
      url: http://staging.todo-api.example.com

    steps:
      - name: Déploiement staging (simulation)
        run: |
          echo "🚀 Déploiement de l'image en staging..."
          echo "Image: ${{ secrets.DOCKERHUB_USERNAME }}/todo-api:latest"
          echo "Environment: staging"
          # En production : kubectl set image, Helm upgrade, ArgoCD sync, etc.

      - name: Validation post-déploiement
        run: |
          echo "✅ Validation du déploiement..."
          echo "Health check : curl http://staging.todo-api.example.com/health"
          # En production : curl -f http://staging-url/health
```

---

### ☑️ Points de vérification

- [ ] La pipeline CI s'exécute sur chaque push et PR
- [ ] Les 4 jobs (lint, test, build, notify) s'enchaînent correctement
- [ ] Un échec de lint empêche les jobs suivants de s'exécuter
- [ ] Le rapport de coverage est disponible dans les artifacts
- [ ] L'image Docker est poussée sur Docker Hub uniquement sur `main`
- [ ] Les secrets sont configurés dans GitHub (non visibles dans les logs)
- [ ] Le workflow réutilisable existe et peut être appelé depuis d'autres workflows

---

### 🔥 Aller plus loin

**Bonus 1** — Ajoutez un job de test sur plusieurs versions Python en parallèle avec `matrix` :
```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

**Bonus 2** — Configurez des **GitHub Environments** avec une approbation manuelle avant le déploiement en production.

**Réflexion** — Quelle est la différence entre `needs` (séquentiel) et un job sans `needs` (parallèle) ? Dans quels cas utiliser l'un ou l'autre ?

---

### 🔗 Ressources

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows)
- [docker/build-push-action](https://github.com/docker/build-push-action)
- [Concurrency groups](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs)

---

---

## English

### 🎯 Objectives

- Design a professional multi-stage CI/CD pipeline
- Securely manage secrets and environment variables
- Manage artifacts and build traceability
- Implement error handling and retry mechanisms
- Reuse workflows with composite actions and reusable workflows

### 📋 Steps (summary)

1. Understand the multi-job pipeline architecture (lint → test → build → publish → deploy)
2. Configure GitHub secrets (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
3. Create `.github/workflows/ci.yml` with 4 jobs using `needs` for sequencing
4. Observe pipeline execution and artifact download in the Actions tab
5. Intentionally trigger a lint failure and observe "fail fast" behavior
6. Create a reusable workflow in `reusable-build.yml`
7. Create a CD workflow triggered by successful CI runs

### ☑️ Checklist

- [ ] CI pipeline runs on every push and PR
- [ ] All 4 jobs chain correctly with `needs`
- [ ] A lint failure stops subsequent jobs from running
- [ ] Coverage report is available in artifacts
- [ ] Docker image pushed to Docker Hub only on `main`
- [ ] Secrets configured in GitHub (not visible in logs)
- [ ] Reusable workflow exists and can be called from other workflows

### 🔗 Resources

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows)
