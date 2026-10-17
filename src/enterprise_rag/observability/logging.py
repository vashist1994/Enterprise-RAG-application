import logging
import structlog
from enterprise_rag.config.settings import get_settings

def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(format="%(message)s",
                        level=getattr(logging, settings.log_level.upper(), logging.INFO))
    structlog.configure(
        processors=[structlog.contextvars.merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.JSONRenderer()],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    return structlog.get_logger(name)
