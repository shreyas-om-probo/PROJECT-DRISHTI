import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(
    logger_name='root',
    log_file='Logs.log',
    level=logging.INFO,
    max_bytes=5*1024*1024,  # 5 MB
    backup_count=3,
    log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
):
    """Set up a logger with file and console output."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(log_format)

    try:
        # File Handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    except Exception as e:
        print(f"Error setting up logger: {e}")
        return None

    return logger