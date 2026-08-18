import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request


# =========================================================
# Rate Limit Configuration
# =========================================================

MAX_REQUESTS_PER_MINUTE = 10
WINDOW_SECONDS = 60


# Stores request timestamps for each client
_requests = defaultdict(list)

_lock = Lock()


# =========================================================
# Client Identification
# =========================================================

def get_client_id(request: Request) -> str:
    """
    Return a simple identifier for the client.
    """

    if request.client is None:
        return "unknown"

    return request.client.host


# =========================================================
# Rate Limit Check
# =========================================================

def check_rate_limit(request: Request) -> None:
    """
    Check whether the client exceeded the allowed
    number of requests per minute.

    Raises:
        HTTPException: 429 when the limit is exceeded.
    """

    client_id = get_client_id(request)

    now = time.time()

    with _lock:

        timestamps = _requests[client_id]

        # Remove old requests
        timestamps[:] = [
            timestamp
            for timestamp in timestamps
            if now - timestamp < WINDOW_SECONDS
        ]

        # Check limit
        if len(timestamps) >= MAX_REQUESTS_PER_MINUTE:

            raise HTTPException(
                status_code=429,
                detail=(
                    "Rate limit exceeded. "
                    "Maximum 10 requests per minute."
                )
            )

        # Store current request
        timestamps.append(now)


# =========================================================
# Reset
# =========================================================

def reset_rate_limits() -> None:
    """
    Clear all stored rate-limit information.

    Mainly useful for tests.
    """

    with _lock:
        _requests.clear()