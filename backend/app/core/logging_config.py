import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "../logs/codelens/"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    log_file = os.path.join(LOG_DIR, "app.log")
    handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=10)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    root.addHandler(console)
    return root

logger = setup_logging()