#!/usr/bin/env python3
"""
Main application entry point for Video Download API
"""

from app import create_app
from app.utils.logger import setup_logger

# إعداد اللوغر
logger = setup_logger()

def main():
    """
    إنشاء وتشغيل تطبيق Flask
    """
    app = create_app()
    
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