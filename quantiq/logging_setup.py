# quantiq/logging_setup.py

import logging
from logging.handlers import RotatingFileHandler
import os


def set_logging(log_file="logs/quantiq.log"):
    """
    Configures logging for the Quant-IQ application.

    Args:
        log_file (str): Path to the log file.

    Returns:
        logging.Logger: Configured logger.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    log_file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB max file size
        backupCount=1,  # Keep up to 1 backup log file
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            log_file_handler,  # Rotating file handler
            logging.StreamHandler(),  # Output logs to console
        ],
    )
    return logging.getLogger()
