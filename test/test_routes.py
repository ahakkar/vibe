import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, template_rendered

with patch.dict("sys.modules", {"flask_cors": MagicMock()}):
    from src.frontend.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestRoutes:
    def setup_method(self):
        """Setup method to run before each test."""

    def test_index_route(self, client, captured_templates):
        response = client.get("/")
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "dashboard.html"

    def test_text_gen_route(self, client, captured_templates):
        response = client.get("/text-gen")
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == "textGen.html"

    def test_stt_route(self, client, captured_templates):
        response = client.get("/stt")
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == "stt.html"

    def test_tts_route(self, client, captured_templates):
        response = client.get("/tts")
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == "tts.html"

    def test_all_route(self, client, captured_templates):
        response = client.get("/all")
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == "chat.html"

    def test_ir_route(self, client, captured_templates):
        response = client.get("/ir")
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == "intent.html"

    def test_chat_route(self, client, captured_templates):
        response = client.get("/text-gen/chat")
        assert response.status_code == 200
        template, context = captured_templates[0]
        assert template.name == "chat.html"
