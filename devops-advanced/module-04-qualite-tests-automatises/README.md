# Module 04 — Qualité applicative et tests automatisés

> 🇫🇷 [Français](#français) | 🇬🇧 [English](#english)

---

## Français

### 🎯 Objectifs

- Mettre en place la pyramide des tests complète (unitaires, intégration, fonctionnels)
- Configurer un quality gate avec flake8, bandit et seuil de coverage
- Intégrer l'analyse statique de code dans la pipeline
- Générer et exploiter les rapports de tests
- Configurer des critères de validation avant déploiement

---

### ⏱️ Durée estimée

**1h30**

---

### 📁 Fichiers fournis

```
module-04-qualite-tests-automatises/
├── README.md
├── test_app.py          ← tests de départ (à enrichir)
├── test_integration.py  ← tests d'intégration (à compléter)
├── setup.cfg            ← configuration flake8 + pytest
└── solution/
    ├── test_app.py
    ├── test_integration.py
    ├── setup.cfg
    └── .github/workflows/quality-gate.yml
```

---

### 📋 Étapes

#### Étape 1 — Enrichir les tests unitaires

Ajoutez ces tests à `test_app.py` pour couvrir les cas limites :

```python
# Tests paramétrés avec pytest.mark.parametrize
import pytest
from app import app


@pytest.mark.parametrize("title,expected_status", [
    ("Valid todo", 201),
    ("", 400),          # titre vide
    (None, 400),        # pas de titre
    ("A" * 500, 201),   # titre très long
])
def test_create_todo_parametrized(client, title, expected_status):
    payload = {"title": title} if title is not None else {}
    r = client.post("/todos", json=payload)
    assert r.status_code == expected_status


def test_stats_endpoint(client):
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.get_json()
    assert "total" in data
    assert "done" in data
    assert "pending" in data
    assert data["total"] == data["done"] + data["pending"]


def test_update_nonexistent_todo(client):
    r = client.put("/todos/9999", json={"title": "Ghost"})
    assert r.status_code == 404


def test_delete_nonexistent_todo(client):
    r = client.delete("/todos/9999")
    assert r.status_code == 404
```

---

#### Étape 2 — Écrire les tests d'intégration

Créez `test_integration.py` :

```python
"""
Tests d'intégration — testent les flux complets de l'application.
Contrairement aux tests unitaires, ils testent plusieurs couches ensemble.
"""
import pytest
from app import app, todos


@pytest.fixture(autouse=True)
def reset_todos():
    """Réinitialiser les todos avant chaque test d'intégration."""
    global todos
    original = todos.copy()
    yield
    todos.clear()
    todos.extend(original)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestTodoCRUDWorkflow:
    """Test du workflow complet CRUD : créer → lire → modifier → supprimer."""

    def test_complete_todo_lifecycle(self, client):
        # 1. Créer un todo
        r = client.post("/todos", json={"title": "Integration test todo"})
        assert r.status_code == 201
        todo_id = r.get_json()["id"]

        # 2. Vérifier qu'il apparaît dans la liste
        r = client.get("/todos")
        ids = [t["id"] for t in r.get_json()]
        assert todo_id in ids

        # 3. Récupérer par ID
        r = client.get(f"/todos/{todo_id}")
        assert r.status_code == 200
        assert r.get_json()["title"] == "Integration test todo"
        assert r.get_json()["done"] is False

        # 4. Marquer comme terminé
        r = client.put(f"/todos/{todo_id}", json={"done": True})
        assert r.status_code == 200
        assert r.get_json()["done"] is True

        # 5. Vérifier les stats
        r = client.get("/stats")
        assert r.get_json()["done"] >= 1

        # 6. Supprimer
        r = client.delete(f"/todos/{todo_id}")
        assert r.status_code == 200

        # 7. Vérifier qu'il n'existe plus
        r = client.get(f"/todos/{todo_id}")
        assert r.status_code == 404

    def test_multiple_todos_stats_consistency(self, client):
        """Les stats doivent toujours être cohérentes."""
        # Créer 3 todos
        ids = []
        for i in range(3):
            r = client.post("/todos", json={"title": f"Todo {i}"})
            ids.append(r.get_json()["id"])

        # Marquer 2 comme terminés
        client.put(f"/todos/{ids[0]}", json={"done": True})
        client.put(f"/todos/{ids[1]}", json={"done": True})

        # Vérifier la cohérence des stats
        r = client.get("/stats")
        stats = r.get_json()
        assert stats["total"] == stats["done"] + stats["pending"]
```

---

#### Étape 3 — Configurer `setup.cfg`

```ini
[flake8]
max-line-length = 120
exclude = .git,__pycache__,.venv
ignore = E501,W503

[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml

[coverage:run]
source = app
omit = test_*.py

[coverage:report]
fail_under = 80
show_missing = True
```

---

#### Étape 4 — Ajouter l'analyse de sécurité avec bandit

```bash
pip install bandit

# Analyser le code pour les vulnérabilités de sécurité
bandit -r app.py -f json -o bandit-report.json
bandit -r app.py  # Version lisible

# Vérifier les dépendances avec safety
pip install safety
safety check --json > safety-report.json
```

---

#### Étape 5 — Intégrer le quality gate dans la pipeline

Créez `.github/workflows/quality-gate.yml` :

```yaml
name: Quality Gate

on:
  push:
    branches: [main, develop, 'feature/**']
  pull_request:
    branches: [main, develop]

jobs:
  quality-gate:
    name: 🎯 Quality Gate
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Installer les outils
        run: pip install flask pytest pytest-cov flake8 bandit safety

      - name: 1️⃣ Lint (flake8)
        run: flake8 app.py

      - name: 2️⃣ Tests unitaires + coverage
        run: pytest test_app.py -v --cov=app --cov-fail-under=80

      - name: 3️⃣ Tests d'intégration
        run: pytest test_integration.py -v

      - name: 4️⃣ Analyse sécurité (bandit)
        run: bandit -r app.py -ll  # -ll = niveau medium et high seulement

      - name: 5️⃣ Vérification des dépendances (safety)
        run: safety check
        continue-on-error: true  # Non bloquant pour l'instant

      - name: Uploader tous les rapports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: quality-reports-${{ github.sha }}
          path: |
            coverage.xml
            htmlcov/
          retention-days: 14

      - name: Résumé quality gate
        if: always()
        run: |
          echo "## 🎯 Quality Gate Results" >> $GITHUB_STEP_SUMMARY
          echo "| Check | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|-------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Lint (flake8) | ✅ |" >> $GITHUB_STEP_SUMMARY
          echo "| Unit tests | ✅ |" >> $GITHUB_STEP_SUMMARY
          echo "| Coverage ≥ 80% | ✅ |" >> $GITHUB_STEP_SUMMARY
          echo "| Integration tests | ✅ |" >> $GITHUB_STEP_SUMMARY
          echo "| Security scan (bandit) | ✅ |" >> $GITHUB_STEP_SUMMARY
```

---

#### Étape 6 — Tester le quality gate

```bash
# Vérifier que tout passe localement avant de pousser
pytest test_app.py test_integration.py -v --cov=app --cov-fail-under=80
flake8 app.py
bandit -r app.py -ll
```

---

### ☑️ Points de vérification

- [ ] Les tests paramétrés couvrent les cas limites (titre vide, inexistant, etc.)
- [ ] Le workflow CRUD complet est testé dans `test_integration.py`
- [ ] `setup.cfg` configure flake8, pytest et coverage
- [ ] `bandit` ne retourne aucun finding de niveau HIGH
- [ ] Le quality gate bloque la pipeline si coverage < 80%
- [ ] Les rapports de tests sont disponibles dans les artifacts GitHub

---

### 🔗 Ressources

- [pytest documentation](https://docs.pytest.org/)
- [flake8](https://flake8.pycqa.org/)
- [bandit](https://bandit.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

---

## English

### 🎯 Objectives

- Implement the complete test pyramid (unit, integration, functional)
- Configure a quality gate with flake8, bandit and coverage threshold
- Integrate static code analysis into the pipeline
- Generate and use test reports
- Configure validation criteria before deployment

### 📋 Steps (summary)

1. Enrich unit tests with parametrized tests and edge cases
2. Write integration tests for the complete CRUD workflow
3. Configure `setup.cfg` for flake8, pytest and coverage
4. Add security analysis with bandit and dependency check with safety
5. Create `.github/workflows/quality-gate.yml` with 5 sequential checks
6. Verify all checks pass locally before pushing

### ☑️ Checklist

- [ ] Parametrized tests cover edge cases
- [ ] Complete CRUD workflow tested in `test_integration.py`
- [ ] `setup.cfg` configures flake8, pytest and coverage
- [ ] `bandit` returns no HIGH severity findings
- [ ] Quality gate blocks pipeline if coverage < 80%
- [ ] Test reports available in GitHub artifacts
