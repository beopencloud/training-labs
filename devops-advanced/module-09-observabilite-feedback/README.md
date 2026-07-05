# Module 09 — Observabilité et feedback opérationnel

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Instrumenter l'application Flask avec des métriques Prometheus
- Déployer la stack PLG (Prometheus + Loki + Grafana) avec Helm
- Centraliser les logs avec Loki et Promtail
- Créer des dashboards Grafana combinant métriques et logs
- Configurer des alertes Prometheus avec AlertManager

---

### 🔧 Prérequis

| Outil | Vérification |
|-------|--------------|
| Minikube (4GB+ RAM) | `minikube start --memory=4096` |
| Helm | `helm version` |
| kubectl | `kubectl version --client` |

---

### ⏱️ Durée estimée

**2h**

---

### 📁 Fichiers fournis

```
module-09-observabilite-feedback/
├── README.md
├── app-instrumented.py      ← todo-api avec métriques Prometheus
├── requirements-observ.txt
└── solution/
    ├── helm/
    │   ├── prometheus-values.yml
    │   ├── loki-values.yml
    │   └── grafana-values.yml
    ├── k8s/
    │   ├── deployment-instrumented.yml
    │   └── prometheus-rules.yml
    └── dashboards/
        └── todo-api-dashboard.json
```

---

### 📋 Étapes

#### Étape 1 — Instrumenter l'application Flask

Ajoutez les métriques Prometheus à `app.py` :

```python
# Ajouter au requirements.txt :
# prometheus-flask-exporter==0.23.1

from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge
import time

# Initialiser les métriques automatiques (toutes les routes)
metrics = PrometheusMetrics(app)

# Métriques personnalisées
todos_total = Gauge(
    'todos_total',
    'Nombre total de todos dans la base'
)
todos_completed = Gauge(
    'todos_completed_total',
    'Nombre de todos complétés'
)
api_errors = Counter(
    'api_errors_total',
    'Nombre total d erreurs API',
    ['method', 'endpoint', 'status_code']
)

# Mettre à jour les gauges dans les routes
@app.route("/todos", methods=["POST"])
def create_todo():
    # ... code existant ...
    todos_total.set(len(todos))
    return jsonify(todo), 201

# L'endpoint /metrics est automatiquement créé par PrometheusMetrics
# Accessible sur http://localhost:5000/metrics
```

Testez localement :

```bash
pip install prometheus-flask-exporter
python app.py &
curl http://localhost:5000/metrics
# Vous devez voir flask_http_request_total, flask_http_request_duration_seconds, etc.
```

---

#### Étape 2 — Déployer la stack PLG avec Helm

```bash
minikube start --memory=4096 --cpus=2

# Ajouter les repos Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Créer le namespace monitoring
kubectl create namespace monitoring
```

**Installer Prometheus + AlertManager :**

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set prometheus.prometheusSpec.retention=24h \
  --set alertmanager.alertmanagerSpec.resources.requests.memory=128Mi \
  --wait
```

**Installer Loki (centralisation des logs) :**

```bash
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set promtail.enabled=true \
  --wait
```

**Installer Grafana :**

```bash
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword=devops2026 \
  --set persistence.enabled=false \
  --set "datasources.datasources\\.yaml.apiVersion=1" \
  --wait
```

---

#### Étape 3 — Accéder aux interfaces

```bash
# Prometheus
kubectl port-forward svc/prometheus-kube-prometheus-prometheus \
  -n monitoring 9090:9090 &

# Grafana
kubectl port-forward svc/grafana -n monitoring 3000:80 &
# Login: admin / devops2026
```

---

#### Étape 4 — Configurer les datasources Grafana

Dans Grafana (http://localhost:3000) :

1. **Configuration → Data Sources → Add data source**
2. **Prometheus** : URL = `http://prometheus-kube-prometheus-prometheus.monitoring:9090`
3. **Loki** : URL = `http://loki.monitoring:3100`

---

#### Étape 5 — Déployer todo-api instrumentée

Créez `k8s/deployment-instrumented.yml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
  labels:
    app: todo-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
      # FR : Annotations pour que Prometheus scrape automatiquement
      # EN : Annotations for automatic Prometheus scraping
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: todo-api
          image: VOTRE_USERNAME/todo-api:latest
          ports:
            - containerPort: 5000
          readinessProbe:
            httpGet: { path: /health, port: 5000 }
```

```bash
kubectl apply -f k8s/deployment-instrumented.yml

# Générer du trafic pour avoir des métriques
kubectl run load-test --image=busybox --restart=Never -- \
  sh -c "while true; do wget -qO- http://todo-api-service/todos; sleep 0.5; done"
```

---

#### Étape 6 — Créer un dashboard Grafana

Dans Grafana → **+ → Dashboard → Add visualization** :

**Panel 1 — Taux de requêtes (Time Series) :**
```promql
rate(flask_http_request_total{job="todo-api"}[5m])
```

**Panel 2 — Latence p99 (Time Series) :**
```promql
histogram_quantile(0.99,
  rate(flask_http_request_duration_seconds_bucket{job="todo-api"}[5m])
)
```

**Panel 3 — Taux d'erreurs (Stat) :**
```promql
sum(rate(flask_http_request_total{job="todo-api",status=~"5.."}[5m]))
/ sum(rate(flask_http_request_total{job="todo-api"}[5m])) * 100
```

**Panel 4 — Todos actifs (Gauge) :**
```promql
todos_total{job="todo-api"}
```

**Panel 5 — Logs Loki (Logs panel) :**
```logql
{namespace="default", pod=~"todo-api.*"}
```

---

#### Étape 7 — Configurer des alertes Prometheus

Créez `k8s/prometheus-rules.yml` :

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-api-alerts
  namespace: monitoring
  labels:
    app: kube-prometheus-stack
    release: prometheus
spec:
  groups:
    - name: todo-api.rules
      rules:
        # Alerte : taux d'erreur > 5%
        - alert: TodoApiHighErrorRate
          expr: |
            sum(rate(flask_http_request_total{job="todo-api",status=~"5.."}[5m]))
            / sum(rate(flask_http_request_total{job="todo-api"}[5m])) > 0.05
          for: 2m
          labels:
            severity: warning
          annotations:
            summary: "Taux d'erreur élevé sur Todo API"
            description: "Le taux d'erreur est de {{ $value | humanizePercentage }}"

        # Alerte : latence p99 > 1 seconde
        - alert: TodoApiHighLatency
          expr: |
            histogram_quantile(0.99,
              rate(flask_http_request_duration_seconds_bucket{job="todo-api"}[5m])
            ) > 1
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Latence élevée sur Todo API"
            description: "La latence p99 est de {{ $value }}s"

        # Alerte : pod non disponible
        - alert: TodoApiPodDown
          expr: kube_pod_status_phase{namespace="default",pod=~"todo-api.*",phase!="Running"} > 0
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "Pod Todo API en erreur"
            description: "Le pod {{ $labels.pod }} est en état {{ $labels.phase }}"
```

```bash
kubectl apply -f k8s/prometheus-rules.yml

# Vérifier que les alertes sont chargées
# http://localhost:9090 → Alerts
```

---

#### Étape 8 — Configurer AlertManager (notification Slack)

```yaml
# Dans les values Helm de kube-prometheus-stack
alertmanager:
  config:
    global:
      slack_api_url: 'https://hooks.slack.com/services/VOTRE_WEBHOOK'
    route:
      group_by: ['alertname', 'namespace']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      receiver: 'slack-notifications'
    receivers:
      - name: 'slack-notifications'
        slack_configs:
          - channel: '#alerts-devops'
            title: '{{ .GroupLabels.alertname }}'
            text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
            send_resolved: true
```

---

### ☑️ Points de vérification

- [ ] `curl http://localhost:5000/metrics` retourne les métriques Flask
- [ ] Prometheus scrape automatiquement le pod `todo-api` (via annotations)
- [ ] Le dashboard Grafana affiche au moins 4 panels avec des métriques en temps réel
- [ ] Les logs de l'application sont visibles dans Grafana via le datasource Loki
- [ ] Les alertes `TodoApiHighErrorRate` et `TodoApiPodDown` sont visibles dans Prometheus
- [ ] Je comprends la différence entre métriques (Prometheus), logs (Loki) et traces

---

### 🔗 Ressources

- [prometheus-flask-exporter](https://github.com/rycus86/prometheus_flask_exporter)
- [Loki documentation](https://grafana.com/docs/loki/latest/)
- [LogQL query language](https://grafana.com/docs/loki/latest/query/)
- [PrometheusRule CRD](https://prometheus-operator.dev/docs/api-reference/api/)
- [AlertManager configuration](https://prometheus.io/docs/alerting/latest/configuration/)

---

## English

### 🎯 Objectives

- Instrument the Flask application with Prometheus metrics
- Deploy the PLG stack (Prometheus + Loki + Grafana) with Helm
- Centralize logs with Loki and Promtail
- Create Grafana dashboards combining metrics and logs
- Configure Prometheus alerts with AlertManager

### 📋 Steps (summary)

1. Add `prometheus-flask-exporter` to `app.py` — automatic metrics on all routes + custom gauges/counters
2. Deploy kube-prometheus-stack, loki-stack and Grafana with Helm
3. Access Prometheus (port 9090) and Grafana (port 3000)
4. Configure Prometheus and Loki as Grafana datasources
5. Deploy instrumented todo-api with `prometheus.io/scrape: "true"` annotations
6. Generate traffic and create a Grafana dashboard with 5 panels
7. Create PrometheusRule for error rate, latency p99 and pod availability
8. Optionally configure AlertManager for Slack notifications

### ☑️ Checklist

- [ ] `curl http://localhost:5000/metrics` returns Flask metrics
- [ ] Prometheus automatically scrapes the `todo-api` pod
- [ ] Grafana dashboard shows at least 4 panels with live metrics
- [ ] Application logs visible in Grafana via Loki datasource
- [ ] `TodoApiHighErrorRate` and `TodoApiPodDown` alerts visible in Prometheus
- [ ] I understand the difference between metrics (Prometheus), logs (Loki) and traces
