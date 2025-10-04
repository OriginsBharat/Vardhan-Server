# src/utils/logging.py
# Centralized setup for the project's logging.

import logging
import sys
import os

LOG_DIR = "data/logs"
LOG_FILE = os.path.join(LOG_DIR, "bot_activity.log")

def setup_logging():
    """
    Configures the root logger for the entire application.
    It ensures the log directory exists and sets up handlers
    for both file and console output.
    """
    # Ensure the log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging configured successfully.")