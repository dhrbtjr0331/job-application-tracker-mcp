"""Logging configuration"""

import logging
from typing import Optional

def setup_logging(level: Optional[str] = None) -> None:
    """Setup logging configuration"""
    log_level = getattr(logging, (level or 'INFO').upper())
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('job_tracker.log')
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)