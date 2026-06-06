"""
logger.py
---------
Centralized logging configuration.
Logs are saved to both the console and a file.
"""

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Log file name includes today's date
log_filename = f"logs/talentscout_{datetime.now().strftime('%Y%m%d')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),                  # Console output
        logging.FileHandler(log_filename)         # File output
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)