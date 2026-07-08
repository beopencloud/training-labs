"""
Tests d'intégration — ils vérifient un parcours complet de l'application,
là où les tests unitaires vérifient une fonction à la fois.
"""
import pytest
from app import app, todos


@pytest.fixture(autouse=True)
def reset_todos():
    """Remet les todos dans leur état initial avant chaque test."""
    original = todos.copy()
    yield
    todos.clear()
    todos.extend(original)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_complete_todo_lifecycle(client):
    # 1. créer
    r = client.post("/todos", json={"title": "Integration test"})
    assert r.status_code == 201
    todo_id = r.get_json()["id"]

    # 2. lire
    assert client.get(f"/todos/{todo_id}").status_code == 200

    # 3. marquer comme terminé
    r = client.put(f"/todos/{todo_id}", json={"done": True})
    assert r.get_json()["done"] is True

    # 4. vérifier les stats
    r = client.get("/stats")
    stats = r.get_json()
    assert stats["total"] == stats["done"] + stats["pending"]

    # 5. supprimer
    assert client.delete(f"/todos/{todo_id}").status_code == 200

    # 6. il n'existe plus
    assert client.get(f"/todos/{todo_id}").status_code == 404
