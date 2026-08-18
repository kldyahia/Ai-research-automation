import asyncio
import logging
import time
import uuid
from typing import Any

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent.graph import app as agent_app

from api.limits import check_rate_limit
from api.logging_conf import configure_logging
from api.schemas import ResearchRequest, ResearchResponse


# =========================================================
# Configuration
# =========================================================

APP_VERSION = "1.0.0"

QUALITY_THRESHOLD = 0.80


# =========================================================
# Logging
# =========================================================

configure_logging()

logger = logging.getLogger("research_api")


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="Autonomous Research Agent API",
    description=(
        "Production API for the Task 2 autonomous "
        "multi-agent research system."
    ),
    version=APP_VERSION,
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Background Job Storage
# =========================================================

jobs: dict[str, dict[str, Any]] = {}


# =========================================================
# Helpers
# =========================================================

def create_initial_state(
    request: ResearchRequest,
) -> dict[str, Any]:
    """
    Build the state expected by the Task 2 LangGraph agent.
    """

    return {
        "goal": request.topic,

        "tasks": [],

        "findings": [],

        "critique": "",

        "quality_score": 0.0,

        "retry_count": 0,

        "report": "",

        "tokens_used": 0,

        # These are used by the Task 2 nodes.
        "model_name": "openai/gpt-oss-120b",

        "temperature": 0.2,
    }


def extract_result(
    result: dict[str, Any],
) -> dict[str, Any]:
    """
    Safely extract the fields required by ResearchResponse.
    """

    return {
        "report": str(
            result.get(
                "report",
                ""
            )
        ),

        "quality_score": float(
            result.get(
                "quality_score",
                0.0
            )
        ),

        "retry_count": int(
            result.get(
                "retry_count",
                0
            )
        ),

        "tokens_used": int(
            result.get(
                "tokens_used",
                0
            )
        ),
    }


async def run_agent(
    request: ResearchRequest,
) -> dict[str, Any]:
    """
    Run the synchronous LangGraph agent outside the
    FastAPI event loop.
    """

    state = create_initial_state(
        request
    )

    # app.invoke() is synchronous.
    # asyncio.to_thread() prevents it from blocking
    # the FastAPI event loop.
    result = await asyncio.to_thread(
        agent_app.invoke,
        state,
    )

    return result


# =========================================================
# Health Check
# =========================================================

@app.get(
    "/health",
    tags=["System"],
)
async def health():
    """
    Fast liveness endpoint.

    Does not call the AI agent.
    """

    return {
        "status": "ok",
        "version": APP_VERSION,
    }


# =========================================================
# Main Research Endpoint
# =========================================================

@app.post(
    "/research",
    response_model=ResearchResponse,
    tags=["Research"],
)
async def research(
    request: ResearchRequest,
    http_request: Request,
    _: None = Depends(check_rate_limit),
):
    """
    Run the autonomous research agent and return
    the final structured result.
    """

    request_id = str(
        uuid.uuid4()
    )

    start_time = time.perf_counter()

    endpoint = "/research"

    logger.info(
        "Research request started",
        extra={
            "request_id": request_id,
            "endpoint": endpoint,
        },
    )

    try:

        result = await run_agent(
            request
        )

        extracted = extract_result(
            result
        )

        duration = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "Research request completed",
            extra={
                "request_id": request_id,
                "endpoint": endpoint,
                "duration_seconds": round(
                    duration,
                    4
                ),
                "outcome": "success",
            },
        )

        return ResearchResponse(
            topic=request.topic,

            report=extracted["report"],

            quality_score=extracted[
                "quality_score"
            ],

            retry_count=extracted[
                "retry_count"
            ],

            tokens_used=extracted[
                "tokens_used"
            ],

            duration_seconds=round(
                duration,
                4
            ),
        )

    except Exception as exc:

        duration = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "Research request failed",
            extra={
                "request_id": request_id,
                "endpoint": endpoint,
                "duration_seconds": round(
                    duration,
                    4
                ),
                "outcome": "error",
            },
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Research agent failed to "
                "complete the request."
            ),
        ) from exc


# =========================================================
# Streaming Endpoint
# =========================================================

@app.post(
    "/research/stream",
    tags=["Research"],
)
async def research_stream(
    request: ResearchRequest,
    http_request: Request,
    _: None = Depends(check_rate_limit),
):
    """
    Stream LangGraph state updates as the agent runs.
    """

    request_id = str(
        uuid.uuid4()
    )

    start_time = time.perf_counter()

    endpoint = "/research/stream"

    async def event_generator():

        state = create_initial_state(
            request
        )

        try:

            logger.info(
                "Streaming research started",
                extra={
                    "request_id": request_id,
                    "endpoint": endpoint,
                },
            )

            async for event in agent_app.astream(
                state,
                stream_mode="values",
            ):

                # Convert the LangGraph state update
                # into a simple JSON-compatible event.
                safe_event = {
                    "event": "state_update",
                    "state": event,
                }

                import json

                yield (
                    json.dumps(
                        safe_event,
                        ensure_ascii=False,
                        default=str,
                    )
                    + "\n"
                )

            duration = (
                time.perf_counter()
                - start_time
            )

            logger.info(
                "Streaming research completed",
                extra={
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "duration_seconds": round(
                        duration,
                        4
                    ),
                    "outcome": "success",
                },
            )

            yield (
                '{"event":"completed"}\n'
            )

        except Exception as exc:

            duration = (
                time.perf_counter()
                - start_time
            )

            logger.exception(
                "Streaming research failed",
                extra={
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "duration_seconds": round(
                        duration,
                        4
                    ),
                    "outcome": "error",
                },
            )

            import json

            yield (
                json.dumps(
                    {
                        "event": "error",
                        "message": (
                            "Research agent failed."
                        ),
                    }
                )
                + "\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
        headers={
            "X-Request-ID": request_id,
        },
    )


# =========================================================
# Background Research Worker
# =========================================================

async def background_research(
    job_id: str,
    request: ResearchRequest,
):
    """
    Run a research job in the background.
    """

    start_time = time.perf_counter()

    jobs[job_id] = {
        "status": "running",
        "topic": request.topic,
    }

    try:

        result = await run_agent(
            request
        )

        extracted = extract_result(
            result
        )

        duration = (
            time.perf_counter()
            - start_time
        )

        jobs[job_id] = {
            "status": "completed",

            "topic": request.topic,

            "report": extracted[
                "report"
            ],

            "quality_score": extracted[
                "quality_score"
            ],

            "retry_count": extracted[
                "retry_count"
            ],

            "tokens_used": extracted[
                "tokens_used"
            ],

            "duration_seconds": round(
                duration,
                4
            ),
        }

        logger.info(
            "Background research completed",
            extra={
                "request_id": job_id,
                "endpoint": "/research/async",
                "duration_seconds": round(
                    duration,
                    4
                ),
                "outcome": "success",
            },
        )

    except Exception as exc:

        duration = (
            time.perf_counter()
            - start_time
        )

        jobs[job_id] = {
            "status": "failed",

            "topic": request.topic,

            "error": str(exc),
        }

        logger.exception(
            "Background research failed",
            extra={
                "request_id": job_id,
                "endpoint": "/research/async",
                "duration_seconds": round(
                    duration,
                    4
                ),
                "outcome": "error",
            },
        )


# =========================================================
# Async Research Endpoint
# =========================================================

@app.post(
    "/research/async",
    status_code=202,
    tags=["Research"],
)
async def research_async(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    _: None = Depends(check_rate_limit),
):
    """
    Accept a research job and return immediately.

    The actual agent execution happens as a background task.
    """

    job_id = str(
        uuid.uuid4()
    )

    jobs[job_id] = {
        "status": "queued",

        "topic": request.topic,
    }

    background_tasks.add_task(
        background_research,
        job_id,
        request,
    )

    logger.info(
        "Background research accepted",
        extra={
            "request_id": job_id,
            "endpoint": "/research/async",
            "outcome": "accepted",
        },
    )

    return {
        "job_id": job_id,

        "status": "accepted",

        "topic": request.topic,

        "message": (
            "Research job accepted and "
            "will run in the background."
        ),
    }


# =========================================================
# Job Status Endpoint
# =========================================================

# This is an extra endpoint.
# It is useful for checking background jobs.

# =========================================================

@app.get(
    "/research/async/{job_id}",
    tags=["Research"],
)
async def get_job_status(
    job_id: str,
):
    """
    Return the current status of a background job.
    """

    job = jobs.get(
        job_id
    )

    if job is None:

        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return {
        "job_id": job_id,
        **job,
    }