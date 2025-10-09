import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configures the root logger for the application with file rotation.
    """
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "my_ai_world.log")

    # Configure the logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent propagation to the default root logger if it has handlers
    logger.propagate = False

    # Remove existing handlers to avoid duplication if this is called more than once
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a rotating file handler
    # This will create up to 5 backup files of 5MB each.
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and set it for both handlers
    # Example format: 2023-10-27 10:30:00,123 - src.bot - INFO - Bot is starting...
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.info("Logging configured successfully.")