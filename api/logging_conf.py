import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Format log records as JSON.
    """

    def format(self, record: logging.LogRecord) -> str:

        log_data = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "level": record.levelname,

            "message": record.getMessage(),

            "logger": record.name,
        }

        if hasattr(record, "request_id"):
            log_data["request_id"] = (
                record.request_id
            )

        if hasattr(record, "endpoint"):
            log_data["endpoint"] = (
                record.endpoint
            )

        if hasattr(record, "duration_seconds"):
            log_data["duration_seconds"] = (
                record.duration_seconds
            )

        if hasattr(record, "outcome"):
            log_data["outcome"] = (
                record.outcome
            )

        return json.dumps(
            log_data,
            ensure_ascii=False
        )


def configure_logging() -> None:
    """
    Configure application-wide JSON logging.
    """

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setFormatter(
        JsonFormatter()
    )

    root_logger = logging.getLogger()

    root_logger.handlers.clear()

    root_logger.addHandler(
        handler
    )

    root_logger.setLevel(
        logging.INFO
    )