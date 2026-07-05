# Module 05 — Packaging, Artefacts et Déploiement applicatif

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Versionner les artefacts avec SemVer et tags Git
- Promouvoir une image entre environnements (dev → staging → prod)
- Implémenter les stratégies de déploiement : Rolling Update, Blue/Green, Canary
- Configurer un rollback automatique
- Valider le déploiement avec des health checks

---

### 🔧 Prérequis

| Outil | Vérification |
|-------|--------------|
| Module 03 terminé | Image Docker publiée sur Docker Hub |
| Minikube | `minikube start` |
| kubectl | `kubectl version --client` |

---

### ⏱️ Durée estimée

**2h**

---

### 📁 Fichiers fournis

```
module-05-packaging-artefacts-deploiement/
├── README.md
├── k8s/
│   ├── deployment.yml
│   ├── service.yml
│   └── configmap.yml
└── solution/
    ├── k8s/
    │   ├── deployment-blue.yml
    │   ├── deployment-green.yml
    │   ├── service-blue-green.yml
    │   └── canary/
    │       ├── deployment-stable.yml
    │       ├── deployment-canary.yml
    │       └── service.yml
    └── .github/workflows/deploy.yml
```

---

### 📋 Étapes

#### Étape 1 — Déploiement Rolling Update (par défaut Kubernetes)

Créez `k8s/deployment.yml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
  labels:
    app: todo-api
    version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-api

  # Stratégie Rolling Update : remplace les pods un à un
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1    # max 1 pod indisponible pendant la MAJ
      maxSurge: 1          # max 1 pod supplémentaire pendant la MAJ

  template:
    metadata:
      labels:
        app: todo-api
        version: "1.0.0"
    spec:
      containers:
        - name: todo-api
          image: VOTRE_USERNAME/todo-api:latest
          ports:
            - containerPort: 5000
          env:
            - name: APP_VERSION
              valueFrom:
                configMapKeyRef:
                  name: todo-api-config
                  key: APP_VERSION
            - name: APP_ENV
              value: "production"
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 15
            periodSeconds: 20
```

Créez `k8s/configmap.yml` :

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-api-config
data:
  APP_VERSION: "1.0.0"
  LOG_LEVEL: "INFO"
```

Créez `k8s/service.yml` :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-api-service
spec:
  type: LoadBalancer
  selector:
    app: todo-api
  ports:
    - port: 80
      targetPort: 5000
```

---

#### Étape 2 — Déployer et observer le rolling update

```bash
minikube start

# Déployer
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml

# Observer l'état
kubectl get pods -w

# Accéder à l'application
minikube service todo-api-service --url

# Simuler une mise à jour (changer la version de l'image)
kubectl set image deployment/todo-api todo-api=VOTRE_USERNAME/todo-api:sha-NOUVEAU_SHA

# Observer le rolling update en temps réel
kubectl rollout status deployment/todo-api

# Historique des déploiements
kubectl rollout history deployment/todo-api

# Rollback vers la version précédente
kubectl rollout undo deployment/todo-api
```

---

#### Étape 3 — Stratégie Blue/Green

Le Blue/Green déploie une version complète en parallèle de l'ancienne, puis bascule le trafic d'un coup.

```
Avant :  Service → Deployment BLUE (v1.0.0) — 100% du trafic
Pendant: Service → Deployment BLUE (v1.0.0) — 100% du trafic
         Deployment GREEN (v1.1.0) démarré en parallèle
Après:   Service → Deployment GREEN (v1.1.0) — 100% du trafic
```

Créez `k8s/deployment-blue.yml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-api
      slot: blue
  template:
    metadata:
      labels:
        app: todo-api
        slot: blue
        version: "1.0.0"
    spec:
      containers:
        - name: todo-api
          image: VOTRE_USERNAME/todo-api:v1.0.0
          ports:
            - containerPort: 5000
          readinessProbe:
            httpGet: { path: /health, port: 5000 }
            initialDelaySeconds: 5
```

Créez `k8s/deployment-green.yml` (identique avec `slot: green` et `v1.1.0`).

Créez `k8s/service-blue-green.yml` :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-api-service
spec:
  type: LoadBalancer
  # Pointer vers blue ou green en changeant ce sélecteur
  selector:
    app: todo-api
    slot: blue   # ← changer en "green" pour basculer
  ports:
    - port: 80
      targetPort: 5000
```

**Workflow Blue/Green :**

```bash
# 1. Déployer blue (production actuelle)
kubectl apply -f k8s/deployment-blue.yml
kubectl apply -f k8s/service-blue-green.yml

# 2. Déployer green (nouvelle version) sans toucher au service
kubectl apply -f k8s/deployment-green.yml
kubectl get pods -l slot=green -w   # Attendre que green soit Ready

# 3. Tester green directement (sans l'exposer)
kubectl port-forward deployment/todo-api-green 5001:5000
curl http://localhost:5001/health

# 4. Basculer le trafic vers green (éditer service ou patch)
kubectl patch service todo-api-service -p '{"spec":{"selector":{"slot":"green"}}}'

# 5. Vérifier que l'app fonctionne sur le service
minikube service todo-api-service --url

# 6. Rollback immédiat si problème (re-pointer vers blue)
kubectl patch service todo-api-service -p '{"spec":{"selector":{"slot":"blue"}}}'
```

---

#### Étape 4 — Stratégie Canary

Le Canary envoie un pourcentage du trafic vers la nouvelle version progressivement.

```
10% trafic → Deployment CANARY (v1.1.0) — 1 replica
90% trafic → Deployment STABLE (v1.0.0) — 9 replicas
```

```bash
# Déployer la version stable (9 replicas)
kubectl apply -f k8s/canary/deployment-stable.yml   # replicas: 9, version: stable

# Déployer le canary (1 replica = ~10% du trafic)
kubectl apply -f k8s/canary/deployment-canary.yml   # replicas: 1, version: canary

# Les deux Deployments partagent le même Service (même label app: todo-api)
# Kubernetes répartit le trafic proportionnellement aux replicas

# Observer la répartition
kubectl get pods -l app=todo-api

# Augmenter progressivement le canary
kubectl scale deployment todo-api-canary --replicas=3   # ~25%
kubectl scale deployment todo-api-canary --replicas=5   # ~50%

# Promotion complète
kubectl scale deployment todo-api-stable --replicas=0   # 100% canary
kubectl scale deployment todo-api-canary --replicas=9

# Rollback
kubectl scale deployment todo-api-canary --replicas=0
```

---

#### Étape 5 — Intégrer le déploiement dans la pipeline

Ajoutez un job de déploiement à la pipeline du module 03 :

```yaml
# Dans .github/workflows/ci.yml — ajouter après le job build
deploy-staging:
  name: 🚀 Deploy to Staging
  runs-on: ubuntu-latest
  needs: build
  if: github.ref == 'refs/heads/main'
  environment:
    name: staging

  steps:
    - uses: actions/checkout@v4

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3

    - name: Update image in deployment
      run: |
        IMAGE="${{ secrets.DOCKERHUB_USERNAME }}/todo-api:sha-${{ github.sha }}"
        kubectl set image deployment/todo-api todo-api=$IMAGE
        kubectl rollout status deployment/todo-api --timeout=120s

    - name: Validation post-déploiement
      run: |
        # Attendre que les pods soient Ready
        kubectl wait --for=condition=ready pod -l app=todo-api --timeout=60s
        # Health check
        echo "✅ Déploiement validé"
```

---

### ☑️ Points de vérification

- [ ] Le Rolling Update déploie les pods un à un sans downtime
- [ ] `kubectl rollout history` montre l'historique des versions
- [ ] `kubectl rollout undo` effectue un rollback en < 30 secondes
- [ ] Le Blue/Green permet de basculer en changeant uniquement le sélecteur du Service
- [ ] Le Canary envoie ~10% du trafic vers la nouvelle version
- [ ] La pipeline déploie automatiquement sur staging après un push sur main

---

### 🔗 Ressources

- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Blue/Green deployments](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Argo Rollouts (canary avancé)](https://argoproj.github.io/rollouts/)

---

## English

### 🎯 Objectives

- Version artifacts with SemVer and Git tags
- Promote an image between environments (dev → staging → prod)
- Implement deployment strategies: Rolling Update, Blue/Green, Canary
- Configure automatic rollback
- Validate deployment with health checks

### 📋 Steps (summary)

1. Create Kubernetes manifests (Deployment, Service, ConfigMap) with Rolling Update strategy
2. Deploy and observe rolling update in real time, then test rollback
3. Implement Blue/Green: two separate Deployments, switch service selector
4. Implement Canary: share a service between stable (9 replicas) and canary (1 replica)
5. Integrate deployment into the CI/CD pipeline from module 03

### ☑️ Checklist

- [ ] Rolling Update deploys pods one by one without downtime
- [ ] `kubectl rollout history` shows version history
- [ ] `kubectl rollout undo` performs rollback in < 30 seconds
- [ ] Blue/Green switch done by changing only the Service selector
- [ ] Canary sends ~10% traffic to new version
- [ ] Pipeline auto-deploys to staging after push to main
