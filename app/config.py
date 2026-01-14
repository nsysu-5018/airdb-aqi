# from pydantic_settings import BaseSettings

import logging

logger = logging.getLogger("uvicorn")

# DEBUG level shows:    DEBUG, INFO, WARNING, ERROR, CRITICAL
# INFO level shows:           INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.INFO)
