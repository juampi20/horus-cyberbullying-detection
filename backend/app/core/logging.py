import contextvars
import json
import logging
import logging.config

# Context del correlation_id: lo setea el middleware de main.py y lo lee
# JsonFormatter en cada registro.
correlation_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get(),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(log_level: str) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "json"}},
            "root": {"handlers": ["default"], "level": log_level},
            "loggers": {
                name: {"handlers": ["default"], "level": log_level, "propagate": False}
                for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
            },
        }
    )
