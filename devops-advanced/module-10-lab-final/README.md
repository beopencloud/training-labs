# Module 10 — Lab Final : Chaîne DevOps complète, sécurisée et observable

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

Construire de A à Z une chaîne DevOps **complète**, **sécurisée** et **observable** en intégrant tous les modules de la formation :

1. Code versionné avec GitFlow (module 02)
2. Pipeline CI/CD avec GitHub Actions (module 03)
3. Quality gate : tests + coverage + lint (module 04)
4. Packaging Docker + déploiement Rolling Update (module 05)
5. GitOps avec Argo CD (module 06)
6. Infrastructure provisionnée avec Terraform (module 07)
7. DevSecOps : secrets, dépendances, image (module 08)
8. Observabilité : métriques, logs, alertes (module 09)

---

### ⏱️ Durée estimée

**3h** (à réaliser en binôme ou en équipe de 3)

---

### 📁 Fichiers fournis

```
module-10-lab-final/
├── README.md
├── checklist-finale.md      ← à remplir pour la présentation
└── solution/
    └── pipeline-complete.yml   ← pipeline GitHub Actions finale complète
```

---

### 📋 Schéma de la chaîne cible

```
┌─────────────────────────────────────────────────────────────────┐
│                     CHAÎNE DEVOPS COMPLÈTE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Développeur                                                      │
│     │                                                            │
│     │ git push feature/xxx                                       │
│     ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              GitHub Actions CI/CD                        │   │
│  │  ┌──────┐ ┌──────┐ ┌──────────┐ ┌───────┐ ┌────────┐  │   │
│  │  │Lint  │→│Tests │→│ Security │→│ Build │→│ Push   │  │   │
│  │  │flake8│ │pytest│ │gitleaks  │ │Docker │ │DockerH.│  │   │
│  │  │      │ │cov80%│ │pip-audit │ │       │ │+ sign  │  │   │
│  │  │      │ │      │ │trivy     │ │       │ │Cosign  │  │   │
│  │  └──────┘ └──────┘ └──────────┘ └───────┘ └───┬────┘  │   │
│  └────────────────────────────────────────────────┼───────┘   │
│                                                    │           │
│                                           Update image tag      │
│                                                    ▼           │
│  ┌─────────────────┐    sync    ┌─────────────────────────┐   │
│  │  todo-api-config│ ←───────── │       Argo CD           │   │
│  │  (GitOps repo)  │            │  (surveille Git en continu)│  │
│  └─────────────────┘            └───────────┬─────────────┘   │
│                                             │                  │
│                                    apply manifestes            │
│                                             ▼                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Kubernetes (Minikube)                        │  │
│  │  ┌────────────────────┐   ┌────────────────────────┐    │  │
│  │  │  Deployment        │   │  Monitoring namespace  │    │  │
│  │  │  todo-api (2 pod)  │   │  ┌──────────────────┐ │    │  │
│  │  │  /metrics exposé   │──→│  │ Prometheus       │ │    │  │
│  │  │  /health probe     │   │  │ Loki + Promtail  │ │    │  │
│  │  └────────────────────┘   │  │ Grafana          │ │    │  │
│  │  ┌────────────────────┐   │  │ AlertManager     │ │    │  │
│  │  │  Service LB        │   │  └──────────────────┘ │    │  │
│  │  └────────────────────┘   └────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📋 Étapes du lab final

#### Phase 1 — Validation des prérequis (15 min)

Vérifiez que tous les composants des modules précédents fonctionnent :

```bash
# Kubernetes
minikube status
kubectl get nodes

# Argo CD
kubectl get pods -n argocd

# Stack monitoring
kubectl get pods -n monitoring

# Docker Hub
docker login
```

---

#### Phase 2 — Assembler la pipeline complète (45 min)

Créez `.github/workflows/pipeline-complete.yml` en combinant les pipelines des modules 03, 04 et 08 :

```yaml
name: 🚀 Pipeline DevOps Complète

on:
  push:
    branches: [main, develop, 'feature/**']
  pull_request:
    branches: [main]

concurrency:
  group: pipeline-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: "3.12"
  IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/todo-api

jobs:
  # ── 1. Security First ──────────────────────────────────────────────────
  secrets-scan:
    name: 🔐 Secrets Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }

  # ── 2. Quality Gate ────────────────────────────────────────────────────
  quality-gate:
    name: 🎯 Quality Gate (lint + tests + coverage)
    runs-on: ubuntu-latest
    needs: secrets-scan
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ env.PYTHON_VERSION }}", cache: pip }
      - run: pip install flask pytest pytest-cov flake8 bandit
      - run: flake8 app.py --max-line-length=120
      - run: pytest test_app.py -v --cov=app --cov-fail-under=80
      - run: bandit -r app.py -ll
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: quality-reports-${{ github.sha }}
          path: coverage.xml

  # ── 3. Build & Security Scan ───────────────────────────────────────────
  build-and-scan:
    name: 🐳 Build + Image Scan (Trivy)
    runs-on: ubuntu-latest
    needs: quality-gate
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=sha-
            type=ref,event=branch
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        if: github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build (+ push si main)
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan image avec Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: 1

  # ── 4. Update GitOps config repo ───────────────────────────────────────
  update-gitops:
    name: 🔄 Update GitOps Config
    runs-on: ubuntu-latest
    needs: build-and-scan
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout config repo
        uses: actions/checkout@v4
        with:
          repository: ${{ github.repository_owner }}/todo-api-config
          token: ${{ secrets.CONFIG_REPO_TOKEN }}
          path: config-repo

      - name: Update image tag
        run: |
          cd config-repo
          sed -i "s|newTag:.*|newTag: sha-${{ github.sha }}|" overlays/staging/kustomization.yml
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add overlays/staging/kustomization.yml
          git diff --staged --quiet || git commit -m "chore(staging): update image sha-${{ github.sha }}"
          git push

  # ── 5. Résumé pipeline ─────────────────────────────────────────────────
  pipeline-summary:
    name: 📊 Pipeline Summary
    runs-on: ubuntu-latest
    needs: [secrets-scan, quality-gate, build-and-scan, update-gitops]
    if: always()
    steps:
      - run: |
          echo "## 🚀 Pipeline DevOps Complète — Résumé" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| Étape | Statut |" >> $GITHUB_STEP_SUMMARY
          echo "|-------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| 🔐 Secrets Scan | ${{ needs.secrets-scan.result == 'success' && '✅ Passed' || '❌ Failed' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| 🎯 Quality Gate | ${{ needs.quality-gate.result == 'success' && '✅ Passed' || '❌ Failed' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| 🐳 Build + Scan | ${{ needs.build-and-scan.result == 'success' && '✅ Passed' || '❌ Failed' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| 🔄 GitOps Update| ${{ needs.update-gitops.result == 'success' && '✅ Passed' || '⏭️ Skipped' }} |" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Commit:** ${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
          echo "**Branch:** ${{ github.ref_name }}" >> $GITHUB_STEP_SUMMARY
          echo "**Actor:** ${{ github.actor }}" >> $GITHUB_STEP_SUMMARY
```

---

#### Phase 3 — Valider Argo CD (20 min)

```bash
# Vérifier que Argo CD a synchronisé la nouvelle version
kubectl get application todo-api-staging -n argocd
kubectl describe application todo-api-staging -n argocd | grep -A5 "Sync Status"

# Vérifier les pods déployés
kubectl get pods -n staging -w

# Accéder à l'application
kubectl port-forward svc/staging-todo-api-service -n staging 5001:80
curl http://localhost:5001/health
curl http://localhost:5001/todos
```

---

#### Phase 4 — Valider l'observabilité (20 min)

```bash
# Générer du trafic
for i in $(seq 1 50); do
  curl -s http://localhost:5001/todos > /dev/null
  curl -s -X POST http://localhost:5001/todos \
    -H "Content-Type: application/json" \
    -d '{"title":"Lab final todo '${i}'"}' > /dev/null
  sleep 0.2
done

# Vérifier les métriques
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090 &
# http://localhost:9090 → query: flask_http_request_total

# Vérifier Grafana
kubectl port-forward svc/grafana -n monitoring 3000:80 &
# http://localhost:3000 → dashboard Todo API
```

---

#### Phase 5 — Présentation finale (30 min)

**Format : 10 minutes par équipe**

Préparez une démonstration live en suivant cet ordre :

1. **Le dépôt** (2 min) — montrer la structure des branches, le CHANGELOG, les releases
2. **La pipeline en action** (3 min) — faire un `git push` en direct et montrer les jobs s'exécuter
3. **Argo CD** (2 min) — montrer l'application synchronisée, l'arbre de ressources
4. **Grafana** (2 min) — montrer le dashboard avec les métriques en temps réel
5. **Rétrospective** (1 min) — ce qu'on a appris, une difficulté surmontée

---

### ☑️ Checklist finale

Cochez chaque point avant la présentation :

**Code & Versioning**
- [ ] Dépôt `todo-api-devops` avec branches `main` et `develop`
- [ ] Au moins 1 release taguée (ex: `v1.0.0`) sur GitHub
- [ ] `CHANGELOG.md` à jour

**Pipeline CI/CD**
- [ ] La pipeline complète passe au vert sur `main`
- [ ] La pipeline bloque si un secret est exposé (gitleaks)
- [ ] La pipeline bloque si coverage < 80%
- [ ] L'image Docker est visible sur Docker Hub avec les tags `sha-*` et `latest`

**GitOps**
- [ ] Dépôt `todo-api-config` existe avec la structure Kustomize
- [ ] Argo CD est installé et l'application `todo-api-staging` est `Synced` et `Healthy`
- [ ] Un `git push` sur `main` déclenche automatiquement la mise à jour sur le cluster

**Observabilité**
- [ ] `curl http://localhost:5001/metrics` retourne des métriques Prometheus
- [ ] Le dashboard Grafana affiche les métriques de l'application
- [ ] Les logs sont visibles dans Grafana via Loki
- [ ] Au moins 2 alertes sont configurées dans Prometheus

**Sécurité**
- [ ] `trivy image` ne retourne aucune vulnérabilité CRITICAL
- [ ] `gitleaks detect` ne trouve aucun secret
- [ ] Les secrets GitHub sont configurés (non en clair dans le code)

---

### 🔗 Ressources de référence

- Tous les modules précédents (01 → 09)
- [DORA Metrics](https://dora.dev/research/)
- [The DevOps Handbook](https://itrevolution.com/product/the-devops-handbook/)

---

## English

### 🎯 Objectives

Build from scratch a **complete**, **secure** and **observable** DevOps chain integrating all training modules:

1. GitFlow versioning (module 02)
2. GitHub Actions CI/CD pipeline (module 03)
3. Quality gate: tests + coverage + lint (module 04)
4. Docker packaging + Rolling Update deployment (module 05)
5. GitOps with Argo CD (module 06)
6. Terraform-provisioned infrastructure (module 07)
7. DevSecOps: secrets, dependencies, image (module 08)
8. Observability: metrics, logs, alerts (module 09)

### 📋 Phases (summary)

1. **Prerequisites validation** (15 min) — verify all components from previous modules work
2. **Assemble the complete pipeline** (45 min) — combine modules 03, 04, 08 workflows
3. **Validate Argo CD** (20 min) — confirm automatic sync after pipeline push
4. **Validate observability** (20 min) — generate traffic, check Grafana dashboard
5. **Final presentation** (30 min) — 10-minute live demo per team

### ☑️ Final Checklist

**Code & Versioning**
- [ ] `todo-api-devops` repo with `main` and `develop` branches
- [ ] At least 1 tagged release (e.g. `v1.0.0`) on GitHub
- [ ] `CHANGELOG.md` up to date

**CI/CD Pipeline**
- [ ] Complete pipeline passes on `main`
- [ ] Pipeline blocks on exposed secrets (gitleaks)
- [ ] Pipeline blocks if coverage < 80%
- [ ] Docker image visible on Docker Hub with `sha-*` and `latest` tags

**GitOps**
- [ ] `todo-api-config` repo with Kustomize structure
- [ ] Argo CD installed, `todo-api-staging` application `Synced` and `Healthy`
- [ ] A `git push` to `main` automatically triggers cluster update

**Observability**
- [ ] `curl http://localhost:5001/metrics` returns Prometheus metrics
- [ ] Grafana dashboard shows application metrics
- [ ] Logs visible in Grafana via Loki
- [ ] At least 2 alerts configured in Prometheus

**Security**
- [ ] `trivy image` returns no CRITICAL vulnerabilities
- [ ] `gitleaks detect` finds no secrets
- [ ] GitHub secrets configured (not in plain text in code)
