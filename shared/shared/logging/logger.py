import json
import logging
import sys
from contextvars import ContextVar

session_id_context = ContextVar("session_id", default=None)
run_id_context = ContextVar("run_id", default=None)


class RunIDMiddleware:
    """Set the request's X-Run-ID in the logging context."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        run_id = next(
            (
                value.decode("latin-1")
                for name, value in scope.get("headers", [])
                if name.lower() == b"x-run-id"
            ),
            None,
        )
        token = run_id_context.set(run_id)
        try:
            await self.app(scope, receive, send)
        finally:
            run_id_context.reset(token)


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "session_id": None,
            "run_id": None,
        }

        current_session_id = session_id_context.get()
        current_run_id = run_id_context.get()

        if current_session_id is not None:
            log["session_id"] = current_session_id

        if current_run_id is not None:
            log["run_id"] = current_run_id

        return json.dumps(log)


def configure_logging(
    service_name: str,
    level: str = "INFO",
) -> logging.Logger:

    logger = logging.getLogger(service_name)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)

    return logger