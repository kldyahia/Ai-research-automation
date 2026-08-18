from fastapi.testclient import TestClient

from api.main import app
from api.limits import reset_rate_limits


client = TestClient(app)


def setup_function():
    reset_rate_limits()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "version" in data


def test_research_valid_payload():
    response = client.post(
        "/research",
        json={
            "topic": "Explain training and testing data in machine learning.",
            "max_retries": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["topic"] == (
        "Explain training and testing data in machine learning."
    )

    assert "report" in data
    assert "quality_score" in data
    assert "retry_count" in data
    assert "tokens_used" in data
    assert "duration_seconds" in data


def test_research_missing_topic():
    response = client.post(
        "/research",
        json={
            "max_retries": 2,
        },
    )

    assert response.status_code == 422


def test_research_wrong_topic_type():
    response = client.post(
        "/research",
        json={
            "topic": 123,
            "max_retries": 2,
        },
    )

    assert response.status_code == 422


def test_research_rate_limit():
    reset_rate_limits()

    payload = {
        "topic": "Test rate limiting.",
        "max_retries": 0,
    }

    responses = []

    for _ in range(11):
        response = client.post(
            "/research",
            json=payload,
        )

        responses.append(response.status_code)

    assert responses[:10] == [200] * 10
    assert responses[10] == 429