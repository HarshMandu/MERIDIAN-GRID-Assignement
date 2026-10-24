"""Basic security regression tests. Run with: pip install pytest; pytest -q"""
import os
os.environ["LLM_API_TOKEN"] = "test-secret"
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_does_not_require_auth():
    assert client.get("/health").status_code == 200

def test_generate_requires_auth():
    response = client.post("/generate", json={"prompt": "hello"})
    assert response.status_code == 401

def test_empty_prompt_rejected_after_auth():
    response = client.post("/generate", headers={"Authorization": "Bearer test-secret"},
                           json={"prompt": " "})
    assert response.status_code == 422

def test_oversized_prompt_rejected():
    response = client.post("/generate", headers={"Authorization": "Bearer test-secret"},
                           json={"prompt": "x" * 8001})
    assert response.status_code == 422
