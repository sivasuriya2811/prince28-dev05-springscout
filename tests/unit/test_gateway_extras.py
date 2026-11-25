"""Unit tests for per-model usage breakdown and daily spend budget guardrail."""

from fastapi.testclient import TestClient

from springscout.api.deps import check_db, get_gateway, get_repo, get_usage_repo
from springscout.api.main import create_app
from springscout.config import Settings
from springscout.llm.gateway import FakeLLM, LLMGateway
from tests.conftest import SAMPLE, FakeRepo, FakeUsage


def test_usage_by_model_returns_breakdown(client):
    resp = client.get("/v1/usage/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["calls"] == 3
    assert data["total_cost_inr"] == 0.0642
    assert len(data["models"]) == 2
    assert data["models"][0]["provider"] == "gemini"
    assert data["models"][1]["fallbacks"] == 1


def test_daily_budget_guardrail_blocks_when_exceeded():
    settings = Settings(
        app_env="ci",
        database_url="postgresql://localhost:5432/unused",
        max_daily_cost_inr=0.05,
        _env_file=None,
    )
    app = create_app(settings)
    app.dependency_overrides[get_repo] = lambda: FakeRepo(SAMPLE)
    app.dependency_overrides[check_db] = lambda: True
    app.dependency_overrides[get_gateway] = lambda: LLMGateway([FakeLLM()])
    app.dependency_overrides[get_usage_repo] = lambda: FakeUsage(spent=0.0642)

    with TestClient(app) as client:
        resp = client.post("/v1/chat", json={"message": "Hi", "stream": False})
        assert resp.status_code == 429
        assert "Daily LLM budget exceeded" in resp.json()["detail"]


def test_daily_budget_guardrail_allows_under_cap():
    settings = Settings(
        app_env="ci",
        database_url="postgresql://localhost:5432/unused",
        max_daily_cost_inr=1.00,
        _env_file=None,
    )
    fake_llm = FakeLLM()
    fake_llm.script = ["Spring Boot 3.x uses HikariCP."]
    app = create_app(settings)
    app.dependency_overrides[get_repo] = lambda: FakeRepo(SAMPLE)
    app.dependency_overrides[check_db] = lambda: True
    app.dependency_overrides[get_gateway] = lambda: LLMGateway([fake_llm])
    app.dependency_overrides[get_usage_repo] = lambda: FakeUsage(spent=0.0642)

    with TestClient(app) as client:
        resp = client.post("/v1/chat", json={"message": "Hi", "stream": False})
        assert resp.status_code == 200
        assert "HikariCP" in resp.json()["answer"]
