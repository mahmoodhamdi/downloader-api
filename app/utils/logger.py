"""
Logging system configuration for the application
"""

import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(name: str = 'video_api', log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up the application's logging system
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        
    Returns:
        logging.Logger: Configured logger object
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Message format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler: {e}")
    
    return logger

def log_request(logger: logging.Logger, method: str, url: str, user_agent: str = None):
    """
    Log an HTTP request
    
    Args:
        logger: Logger object
        method: HTTP method
        url: Requested URL
        user_agent: Browser information
    """
    message = f"{method} {url}"
    if user_agent:
        message += f" - User-Agent: {user_agent}"
    
    logger.info(message)

def log_error(logger: logging.Logger, error: Exception, context: str = None):
    """
    Log an error with context
    
    Args:
        logger: Logger object
        error: Exception object
        context: Additional context
    """
    message = f"Error: {str(error)}"
    if context:
        message = f"{context} - {message}"
    
    logger.error(message, exc_info=True)

def log_video_extraction(logger: logging.Logger, url: str, success: bool, 
                        video_count: int = 0, duration: float = 0):
    """
    Log video extraction operation
    
    Args:
        logger: Logger object
        url: Video URL
        success: Operation success status
        video_count: Number of videos extracted
        duration: Operation duration in seconds
    """
    status = "SUCCESS" if success else "FAILED"
    message = f"Video extraction {status} - URL: {url}"
    
    if success:
        message += f" - Videos: {video_count}"
    
    if duration > 0:
        message += f" - Duration: {duration:.2f}s"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)