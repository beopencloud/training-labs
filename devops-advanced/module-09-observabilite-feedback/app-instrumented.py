# Module 09 — todo-api avec métriques Prometheus
# FR : Copier ce fichier en remplacement de app.py pour ajouter l'observabilité
# EN : Copy this file to replace app.py to add observability

from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge
import os, logging

app = Flask(__name__)
metrics = PrometheusMetrics(app)

PORT = int(os.environ.get("PORT", 5000))
VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENV = os.environ.get("APP_ENV", "development")

logging.basicConfig(level=logging.INFO,
  format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}')
logger = logging.getLogger(__name__)

# Métriques personnalisées
todos_total = Gauge('todos_total', 'Nombre total de todos')
todos_completed = Gauge('todos_completed_total', 'Todos complétés')
api_errors = Counter('api_errors_total', 'Erreurs API', ['method', 'endpoint'])

todos = [
    {"id": 1, "title": "Apprendre DevOps", "done": False},
    {"id": 2, "title": "Maîtriser Kubernetes", "done": False},
]
next_id = 3


@app.route("/health")
@metrics.do_not_track()
def health():
    return jsonify({"status": "ok", "version": VERSION})


@app.route("/metrics")
@metrics.do_not_track()
def prometheus_metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.route("/")
def index():
    return jsonify({"message": "Todo API", "version": VERSION})


@app.route("/todos", methods=["GET"])
def get_todos():
    todos_total.set(len(todos))
    return jsonify(todos)


@app.route("/todos", methods=["POST"])
def create_todo():
    global next_id
    data = request.get_json()
    if not data or "title" not in data or not data["title"].strip():
        api_errors.labels(method="POST", endpoint="/todos").inc()
        return jsonify({"error": "title required"}), 400
    todo = {"id": next_id, "title": data["title"], "done": False}
    todos.append(todo)
    next_id += 1
    todos_total.set(len(todos))
    return jsonify(todo), 201


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if "done" in data:
        todo["done"] = data["done"]
    todos_completed.set(len([t for t in todos if t["done"]]))
    return jsonify(todo)


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    todos = [t for t in todos if t["id"] != todo_id]
    todos_total.set(len(todos))
    return jsonify({"deleted": todo_id})


@app.route("/stats")
def stats():
    total = len(todos)
    done = len([t for t in todos if t["done"]])
    return jsonify({"total": total, "done": done, "pending": total - done})


if __name__ == "__main__":
    logger.info(f"Starting instrumented Todo API v{VERSION}")
    app.run(host="0.0.0.0", port=PORT)
