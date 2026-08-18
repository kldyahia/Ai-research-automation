from .state import ResearchState


QUALITY_THRESHOLD = 0.8
MAX_RETRIES = 2


def decision(state: ResearchState) -> dict:

    score = state["quality_score"]
    retry_count = state["retry_count"]

    if score >= QUALITY_THRESHOLD:

        print(
            f"[Decision] APPROVE "
            f"(score={score:.2f})"
        )

        return {
            "retry_count": retry_count
        }

    if retry_count < MAX_RETRIES:

        new_retry_count = retry_count + 1

        print(
            f"[Decision] RETRY "
            f"(score={score:.2f}, "
            f"retry={new_retry_count}/{MAX_RETRIES})"
        )

        return {
            "retry_count": new_retry_count
        }

    print(
        f"[Decision] APPROVE AFTER MAX RETRIES "
        f"(score={score:.2f})"
    )

    return {
        "retry_count": retry_count
    }


def route_after_decision(
    state: ResearchState
) -> str:

    score = state["quality_score"]
    retry_count = state["retry_count"]

    if score >= QUALITY_THRESHOLD:

        return "reporting"

    if retry_count < MAX_RETRIES:

        return "planner"

    return "reporting"