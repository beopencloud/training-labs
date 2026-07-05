# Module 06 — GitOps et gestion déclarative des déploiements

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Comprendre les principes GitOps et la séparation app/config
- Installer et configurer Argo CD sur Minikube
- Déployer l'application `todo-api` via Argo CD
- Configurer la synchronisation automatique Git → cluster
- Tester la détection de dérive et la correction automatique
- Gérer plusieurs environnements (staging, production)

---

### 🔧 Prérequis

| Outil | Vérification |
|-------|--------------|
| Minikube avec 4GB RAM | `minikube start --memory=4096` |
| kubectl | `kubectl version --client` |
| Helm | `helm version` |
| Module 05 terminé | Image Docker publiée sur Docker Hub |

---

### ⏱️ Durée estimée

**2h**

---

### 📁 Fichiers fournis

```
module-06-gitops-deploiements-declaratifs/
├── README.md
├── apps/
│   ├── todo-api/
│   │   ├── staging/
│   │   │   ├── deployment.yml
│   │   │   ├── service.yml
│   │   │   └── kustomization.yml
│   │   └── production/
│   │       ├── deployment.yml
│   │       ├── service.yml
│   │       └── kustomization.yml
│   └── argocd/
│       ├── app-staging.yml
│       └── app-production.yml
└── solution/
    └── (même structure, complétée)
```

---

### 📋 Étapes

#### Étape 1 — Comprendre l'architecture GitOps

```
┌─────────────────┐    push    ┌──────────────────┐
│  Dev push code  │ ─────────> │  Repo app (CI)   │
│  todo-api/      │            │  Build + push     │
└─────────────────┘            │  image Docker     │
                               └────────┬─────────┘
                                        │ met à jour
                                        ▼
┌─────────────────┐    pull    ┌──────────────────┐
│  Cluster K8s    │ <───────── │  Repo config     │
│                 │  sync      │  (manifestes K8s)│
│  Argo CD        │            │  deployment.yml  │
│  surveille Git  │            │  service.yml     │
└─────────────────┘            └──────────────────┘
```

**Principe clé** : le repo config est la **source de vérité**.
Si quelqu'un modifie le cluster manuellement → Argo CD détecte la dérive et corrige.

---

#### Étape 2 — Créer le repo de configuration (GitOps repo)

Créez un **nouveau dépôt GitHub** séparé : `todo-api-config`

> 💡 La séparation app/config est fondamentale en GitOps :
> - `todo-api-devops` : code source + CI (pipeline qui build l'image)
> - `todo-api-config` : manifestes Kubernetes (ce que Argo CD surveille)

```bash
mkdir todo-api-config && cd todo-api-config
git init
git remote add origin https://github.com/VOTRE_USERNAME/todo-api-config.git
```

---

#### Étape 3 — Structurer le repo config avec Kustomize

```
todo-api-config/
├── base/                  ← configuration commune
│   ├── deployment.yml
│   ├── service.yml
│   └── kustomization.yml
└── overlays/
    ├── staging/           ← surcharges pour staging
    │   └── kustomization.yml
    └── production/        ← surcharges pour production
        └── kustomization.yml
```

Créez `base/deployment.yml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
    spec:
      containers:
        - name: todo-api
          image: VOTRE_USERNAME/todo-api:latest
          ports:
            - containerPort: 5000
          readinessProbe:
            httpGet: { path: /health, port: 5000 }
            initialDelaySeconds: 5
```

Créez `base/service.yml` :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-api-service
spec:
  type: ClusterIP
  selector:
    app: todo-api
  ports:
    - port: 80
      targetPort: 5000
```

Créez `base/kustomization.yml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yml
  - service.yml
```

Créez `overlays/staging/kustomization.yml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base
namePrefix: staging-
commonLabels:
  env: staging
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 2
    target:
      kind: Deployment
      name: todo-api
```

Créez `overlays/production/kustomization.yml` :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base
namePrefix: prod-
commonLabels:
  env: production
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
    target:
      kind: Deployment
      name: todo-api
```

```bash
git add .
git commit -m "feat: initial GitOps configuration structure"
git push origin main
```

---

#### Étape 4 — Installer Argo CD

```bash
# Démarrer Minikube avec suffisamment de ressources
minikube start --memory=4096 --cpus=2

# Créer le namespace Argo CD
kubectl create namespace argocd

# Installer Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Attendre que tous les pods soient prêts (2-3 minutes)
kubectl wait --for=condition=available deployment --all -n argocd --timeout=300s

# Accéder à l'interface Argo CD
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Récupérer le mot de passe admin
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

Ouvrez [https://localhost:8080](https://localhost:8080) — login : `admin`, mot de passe récupéré ci-dessus.

---

#### Étape 5 — Créer l'application Argo CD pour staging

Créez `apps/argocd/app-staging.yml` dans votre repo `todo-api-config` :

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: todo-api-staging
  namespace: argocd
spec:
  project: default

  # FR : Source = votre repo de configuration GitOps
  # EN : Source = your GitOps configuration repo
  source:
    repoURL: https://github.com/VOTRE_USERNAME/todo-api-config.git
    targetRevision: HEAD
    path: overlays/staging

  # FR : Destination = cluster local, namespace staging
  # EN : Destination = local cluster, staging namespace
  destination:
    server: https://kubernetes.default.svc
    namespace: staging

  # FR : Synchronisation automatique dès qu'un changement est détecté dans Git
  # EN : Auto-sync whenever a change is detected in Git
  syncPolicy:
    automated:
      prune: true       # Supprimer les ressources retirées de Git
      selfHeal: true    # Corriger toute dérive manuelle
    syncOptions:
      - CreateNamespace=true
```

```bash
kubectl create namespace staging
kubectl apply -f apps/argocd/app-staging.yml
```

---

#### Étape 6 — Observer la synchronisation automatique

```bash
# Surveiller l'état de l'application
kubectl get applications -n argocd
kubectl describe application todo-api-staging -n argocd

# Voir les pods déployés par Argo CD
kubectl get pods -n staging -w
```

Dans l'interface Argo CD, vous voyez l'application avec son arbre de ressources.

---

#### Étape 7 — Tester la détection de dérive (drift detection)

```bash
# Modifier manuellement le nombre de replicas (contournement de GitOps)
kubectl scale deployment staging-todo-api --replicas=0 -n staging

# Observer : Argo CD détecte la dérive et restaure automatiquement 2 replicas
watch kubectl get pods -n staging
```

> ✅ En 1-2 minutes, Argo CD recrée les pods pour correspondre à l'état décrit dans Git.

---

#### Étape 8 — Déployer une nouvelle version via GitOps

```bash
# Dans todo-api-config, mettre à jour l'image
# overlays/staging/kustomization.yml — ajouter un patch d'image :
```

```yaml
# Ajouter dans overlays/staging/kustomization.yml
images:
  - name: VOTRE_USERNAME/todo-api
    newTag: sha-NOUVEAU_SHA   # SHA du dernier commit de todo-api-devops
```

```bash
git add overlays/staging/kustomization.yml
git commit -m "chore(staging): update todo-api image to sha-NOUVEAU_SHA"
git push origin main

# Argo CD détecte le changement et synchronise automatiquement
# Observer dans l'interface ou :
kubectl rollout status deployment/staging-todo-api -n staging
```

---

#### Étape 9 — Automatiser la mise à jour de l'image depuis la pipeline CI

Dans le repo `todo-api-devops`, ajoutez un job à la pipeline CI qui met à jour le repo config :

```yaml
update-config-repo:
  name: 🔄 Update GitOps config repo
  runs-on: ubuntu-latest
  needs: build
  if: github.ref == 'refs/heads/main'

  steps:
    - name: Checkout config repo
      uses: actions/checkout@v4
      with:
        repository: VOTRE_USERNAME/todo-api-config
        token: ${{ secrets.CONFIG_REPO_TOKEN }}   # Personal Access Token
        path: config-repo

    - name: Update image tag
      run: |
        cd config-repo
        # Mettre à jour le tag dans l'overlay staging
        sed -i "s|newTag:.*|newTag: sha-${{ github.sha }}|" overlays/staging/kustomization.yml
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"
        git add .
        git commit -m "chore(staging): update image to sha-${{ github.sha }}"
        git push
```

---

### ☑️ Points de vérification

- [ ] Le repo `todo-api-config` existe avec la structure `base/` + `overlays/`
- [ ] Argo CD est installé et accessible sur https://localhost:8080
- [ ] L'application `todo-api-staging` est en état `Synced` et `Healthy`
- [ ] Une modification manuelle du cluster est automatiquement corrigée par Argo CD
- [ ] Une modification dans Git déclenche un re-déploiement automatique
- [ ] La pipeline CI met à jour le repo config avec le nouveau SHA d'image

---

### 🔗 Ressources

- [Argo CD documentation](https://argo-cd.readthedocs.io/)
- [Kustomize](https://kustomize.io/)
- [GitOps principles](https://opengitops.dev/)
- [App of Apps pattern](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/)

---

## English

### 🎯 Objectives

- Understand GitOps principles and app/config separation
- Install and configure Argo CD on Minikube
- Deploy `todo-api` via Argo CD with automatic sync
- Test drift detection and automatic correction
- Manage multiple environments (staging, production)

### 📋 Steps (summary)

1. Understand the GitOps architecture (app repo → CI → image, config repo → Argo CD → cluster)
2. Create a separate `todo-api-config` GitHub repository
3. Structure it with Kustomize: `base/` + `overlays/staging/` + `overlays/production/`
4. Install Argo CD with `kubectl apply` and access the UI
5. Create an Argo CD Application manifest pointing to the config repo
6. Observe automatic synchronization in the UI
7. Test drift detection: manually scale to 0, watch Argo CD restore
8. Deploy a new version by updating the image tag in the config repo
9. Automate config repo update from the CI pipeline

### ☑️ Checklist

- [ ] `todo-api-config` repo exists with `base/` + `overlays/` structure
- [ ] Argo CD installed and accessible at https://localhost:8080
- [ ] `todo-api-staging` application is `Synced` and `Healthy`
- [ ] Manual cluster modification is automatically corrected by Argo CD
- [ ] A Git change triggers automatic re-deployment
- [ ] CI pipeline updates config repo with new image SHA
