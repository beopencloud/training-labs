"""
Tests d'intégration — Module 04
Formation DevOps Avancé · BeOpen IT

FR : Complétez ce fichier en suivant les instructions du README.
EN : Complete this file by following the README instructions.
"""
import pytest
from app import app, todos


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestTodoCRUDWorkflow:
    """
    FR : Testez le workflow complet CRUD dans cette classe.
         Chaque test doit simuler un scénario utilisateur réel.
    EN : Test the complete CRUD workflow in this class.
    """

    def test_complete_todo_lifecycle(self, client):
        # TODO FR : Implémenter le test du cycle de vie complet
        # TODO EN : Implement the complete lifecycle test
        # 1. Créer un todo → 2. Vérifier liste → 3. Récupérer par ID
        # 4. Marquer terminé → 5. Vérifier stats → 6. Supprimer → 7. Vérifier 404
        pass

    def test_multiple_todos_stats_consistency(self, client):
        # TODO FR : Créer 3 todos, marquer 2 comme terminés, vérifier stats
        # TODO EN : Create 3 todos, mark 2 as done, verify stats consistency
        pass
