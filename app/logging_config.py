"""
logging_config.py - Structured Logging Setup
"""

import logging
import logging.handlers
import structlog
import sys
from pathlib import Path
from app.config import settings


def setup_logging():
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            filename=settings.log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        ),
    ]

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format="%(message)s"
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True)
        if not settings.is_production
        else structlog.processors.JSONRenderer()
    )

    for handler in handlers:
        handler.setFormatter(formatter)

    logger = structlog.get_logger("app.startup")
    logger.info("logging_initialized", environment=settings.environment, log_level=settings.log_level)
    return logger