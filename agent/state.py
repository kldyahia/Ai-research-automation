from typing import TypedDict


class ResearchState(TypedDict):
    goal: str
    tasks: list[str]
    findings: list[str]
    critique: str
    quality_score: float
    retry_count: int
    report: str
    tokens_used: int

    model_name: str
    temperature: float