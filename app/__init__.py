"""
Video Download API Application Factory
"""

from flask import Flask, jsonify
from app.config import Config
from app.routes.video_routes import video_bp
from app.utils.logger import setup_logger
from app.db import db

def create_app(config_class=Config):
    """
    Create a Flask application with the appropriate configuration
    
    Args:
        config_class: Configuration class
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    # Set up logger
    logger = setup_logger()
    
    # Register blueprints
    app.register_blueprint(video_bp, url_prefix='/api/v1')
    
    # Add health check route
    @app.route('/health')
    def health_check():
        """Application health check"""
        return jsonify({
            'status': 'healthy',
            'message': 'Video Download API is running',
            'version': '1.0.0'
        })
    
    # Add documentation route
    @app.route('/')
    def documentation():
        """Basic documentation page"""
        return jsonify({
            'message': 'Video Download API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'get_download_links': '/api/v1/get-download-links',
                'get_info': '/api/v1/get-info',
                'get_subtitles': '/api/v1/get-subtitles',
                'get_thumbnails': '/api/v1/get-thumbnails'
            },
            'documentation': {
                'example_request': {
                    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    'format': 'best'
                }
            }
        })
    
    # General error handlers
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': 'The requested endpoint does not exist'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    return app