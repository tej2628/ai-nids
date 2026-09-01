import logging
from logging.handlers import RotatingFileHandler
from config import LOG_PATH


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("ai_nids")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    return logger


logger = configure_logging()
