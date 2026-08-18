from fastapi.testclient import TestClient

import api.main as main
from api.limits import reset_rate_limits


client = TestClient(main.app)


async def fake_run_agent(request):
    """
    Fake agent used by tests.

    This prevents tests from calling Groq.
    """
    return {
        "report": "# Test Report\n\nMock research result.",
        "quality_score": 0.90,
        "retry_count": 0,
        "tokens_used": 10,
    }


def setup_function():
    """
    Reset rate-limit state before every test.
    """
    reset_rate_limits()

    # Replace the real AI call with the fake one.
    main.run_agent = fake_run_agent


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

    assert data["quality_score"] == 0.90
    assert data["tokens_used"] == 10


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
        "topic": "Rate limit test",
        "max_retries": 0,
    }

    status_codes = []

    for _ in range(11):
        response = client.post(
            "/research",
            json=payload,
        )

        status_codes.append(
            response.status_code
        )

    # First 10 requests are allowed.
    assert status_codes[:10] == [200] * 10

    # Request number 11 must be rejected.
    assert status_codes[10] == 429