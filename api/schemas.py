from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        description="Research objective"
    )

    max_retries: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Maximum number of agent retries"
    )


class ResearchResponse(BaseModel):
    topic: str
    report: str

    quality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )

    retry_count: int = Field(
        ...,
        ge=0
    )

    tokens_used: int = Field(
        ...,
        ge=0
    )

    duration_seconds: float = Field(
        ...,
        ge=0.0
    )