"""Tests for AI features: chatbot (mocked Ollama) and recommender (scikit-learn)."""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.data import store
from backend.db.database import Base, get_db
from backend.main import app
from backend.models.menu import MenuItem

# Reuse the same fixture pattern as conftest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def client():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=eng)
    SL = sessionmaker(bind=eng)
    db = SL()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    # Seed stores
    store._menu_items = {
        1: MenuItem(id=1, name="Cappuccino", category="Coffee", description="Espresso with foamed milk", price=4.50, image="cap.jpg"),
        2: MenuItem(id=2, name="Latte", category="Coffee", description="Espresso with steamed milk", price=5.00, image="latte.jpg"),
        3: MenuItem(id=3, name="Mocha", category="Coffee", description="Chocolate espresso drink", price=5.25, image="mocha.jpg"),
        4: MenuItem(id=4, name="Croissant", category="Pastries", description="Flaky butter pastry", price=3.50, image="cr.jpg"),
    }
    store._gallery_items = {}

    # Reset recommender index so it rebuilds with our test data
    from backend.services.recommender import reset_index
    reset_index()

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()
    db.close()
    reset_index()


# === Chat tests ===

class TestChat:
    def test_chat_returns_reply(self, client):
        """Mock Ollama and verify the chat endpoint returns a reply."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"message": {"content": "We have a great Cappuccino!"}}
        mock_resp.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post = MagicMock(return_value=mock_resp)

        with patch("backend.routers.chat.httpx.Client", return_value=mock_client):
            resp = client.post("/api/chat", json={"message": "What coffee do you have?"})

        assert resp.status_code == 200
        assert "Cappuccino" in resp.json()["reply"]

    def test_chat_empty_message_rejected(self, client):
        resp = client.post("/api/chat", json={"message": ""})
        assert resp.status_code == 422

    def test_chat_too_long_rejected(self, client):
        resp = client.post("/api/chat", json={"message": "x" * 301})
        assert resp.status_code == 422

    def test_chat_ollama_offline(self, client):
        """When Ollama is not running, return 503."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(side_effect=httpx.ConnectError("refused"))
        mock_client.__exit__ = MagicMock(return_value=False)

        with patch("backend.routers.chat.httpx.Client", return_value=mock_client):
            resp = client.post("/api/chat", json={"message": "Hi"})
        assert resp.status_code == 503
        assert "offline" in resp.json()["detail"].lower()


# === Recommender tests ===

class TestRecommend:
    def test_get_similar_items(self, client):
        resp = client.get("/api/recommend/1?limit=2")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) <= 2
        assert all(i["id"] != 1 for i in items)  # excludes itself

    def test_similar_items_are_coffee(self, client):
        """Items similar to a coffee should prefer other coffees."""
        resp = client.get("/api/recommend/1?limit=3")
        items = resp.json()
        # At least one result should be coffee
        categories = [i["category"] for i in items]
        assert "Coffee" in categories

    def test_recommend_unknown_id_404(self, client):
        resp = client.get("/api/recommend/9999")
        assert resp.status_code == 404

    def test_recommend_cart(self, client):
        resp = client.post("/api/recommend/cart", json={"item_ids": [1, 2]})
        assert resp.status_code == 200
        items = resp.json()
        # Should not include items already in cart
        ids = [i["id"] for i in items]
        assert 1 not in ids
        assert 2 not in ids

    def test_recommend_cart_unknown_id_404(self, client):
        resp = client.post("/api/recommend/cart", json={"item_ids": [9999]})
        assert resp.status_code == 404

    def test_recommend_cart_empty_422(self, client):
        resp = client.post("/api/recommend/cart", json={"item_ids": []})
        assert resp.status_code == 422
