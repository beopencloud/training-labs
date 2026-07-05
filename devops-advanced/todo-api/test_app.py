import pytest
from app import app, todos


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_get_todos(client):
    r = client.get("/todos")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_create_todo(client):
    r = client.post("/todos", json={"title": "Test todo"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Test todo"


def test_create_todo_missing_title(client):
    r = client.post("/todos", json={})
    assert r.status_code == 400


def test_get_todo_not_found(client):
    r = client.get("/todos/9999")
    assert r.status_code == 404


def test_update_todo(client):
    r = client.put("/todos/1", json={"done": True})
    assert r.status_code == 200
    assert r.get_json()["done"] is True


def test_delete_todo(client):
    # Créer un todo à supprimer
    r = client.post("/todos", json={"title": "To delete"})
    tid = r.get_json()["id"]
    r = client.delete(f"/todos/{tid}")
    assert r.status_code == 200
    assert r.get_json()["deleted"] == tid
