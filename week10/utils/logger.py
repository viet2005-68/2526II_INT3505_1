import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("payment_api")

logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s'
)

file_handler = RotatingFileHandler(
    f"{LOG_DIR}/app.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)