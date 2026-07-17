import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class DummyDB:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None

    def close(self):
        return None


class FormSubmissionTests(unittest.TestCase):
    def test_salvar_cliente_accepts_form_submission(self):
        db = DummyDB()

        def override_get_db():
            yield db

        with patch("main.initialize_database"):
            main.app.dependency_overrides[main.get_db] = override_get_db
            with TestClient(main.app) as client:
                response = client.post(
                    "/clientes",
                    data={"nome": "Ana", "cidade": "São Paulo"},
                )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(len(db.added), 1)
        self.assertEqual(db.added[0].nome, "Ana")
        self.assertEqual(db.added[0].cidade, "São Paulo")


if __name__ == "__main__":
    unittest.main()
