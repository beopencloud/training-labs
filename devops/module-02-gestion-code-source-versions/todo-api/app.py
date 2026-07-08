# todo-api — Application fil rouge de la formation DevOps Avancé
# BeOpen IT · Dakar 2026

from flask import Flask, jsonify, request
import os
import logging
import time

app = Flask(__name__)

# Configuration via variables d'environnement
PORT = int(os.environ.get("PORT", 5000))
VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENV = os.environ.get("APP_ENV", "development")

# Logging structuré JSON
logging.basicConfig(level=logging.INFO, format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}')
logger = logging.getLogger(__name__)

# Base de données en mémoire (remplacée par Redis en module 5+)
todos = [
    {"id": 1, "title": "Apprendre DevOps", "done": False},
    {"id": 2, "title": "Maîtriser Kubernetes", "done": False},
    {"id": 3, "title": "Déployer avec GitOps", "done": False},
]
next_id = 4


@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": VERSION, "env": ENV})


@app.route("/")
def index():
    return jsonify({"message": "Todo API", "version": VERSION, "env": ENV})


@app.route("/todos", methods=["GET"])
def get_todos():
    logger.info(f"GET /todos — {len(todos)} items")
    return jsonify(todos)


@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    return jsonify(todo)


@app.route("/todos", methods=["POST"])
def create_todo():
    global next_id
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title required"}), 400
    todo = {"id": next_id, "title": data["title"], "done": False}
    todos.append(todo)
    next_id += 1
    logger.info(f"Created todo: {todo['title']}")
    return jsonify(todo), 201


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if "title" in data:
        todo["title"] = data["title"]
    if "done" in data:
        todo["done"] = data["done"]
    return jsonify(todo)


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    todos = [t for t in todos if t["id"] != todo_id]
    return jsonify({"deleted": todo_id})


if __name__ == "__main__":
    logger.info(f"Starting Todo API v{VERSION} on port {PORT} [{ENV}]")
    app.run(host="0.0.0.0", port=PORT)
