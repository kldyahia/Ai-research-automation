from fastapi.testclient import TestClient

import api.main as main
from api.limits import reset_rate_limits


async def fake_run_agent(request):
    return {
        "report": "# Test Report\n\nRate limit test.",
        "quality_score": 0.90,
        "retry_count": 0,
        "tokens_used": 10,
    }


main.run_agent = fake_run_agent

reset_rate_limits()

client = TestClient(main.app)

for i in range(12):
    response = client.post(
        "/research",
        json={
            "topic": "Rate limit test"
        },
    )

    print(
        f"Request {i + 1}: "
        f"{response.status_code}"
    )