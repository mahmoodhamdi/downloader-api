#!/usr/bin/env python3
"""
Main application entry point for Video Download API
"""

from app import create_app
from app.db import db
from app.utils.logger import setup_logger

# Set up logger
logger = setup_logger()

def main():
    """
    Create and run the Flask application
    """
    app = create_app()
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    logger.info("Starting Video Download API...")
    logger.info("API Documentation: http://127.0.0.1:5000/")
    logger.info("Health Check: http://127.0.0.1:5000/health")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    main()