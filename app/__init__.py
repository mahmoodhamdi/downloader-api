"""
Video Download API Application Factory
"""

from flask import Flask, jsonify
from app.config import Config
from app.routes.video_routes import video_bp
from app.utils.logger import setup_logger

def create_app(config_class=Config):
    """
    إنشاء تطبيق Flask مع التكوين المناسب
    
    Args:
        config_class: كلاس التكوين
        
    Returns:
        Flask: تطبيق Flask مُكوَّن
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # إعداد اللوغر
    logger = setup_logger()
    
    # تسجيل المسارات (Blueprints)
    app.register_blueprint(video_bp, url_prefix='/api/v1')
    
    # إضافة مسار الصحة
    @app.route('/health')
    def health_check():
        """فحص صحة التطبيق"""
        return jsonify({
            'status': 'healthy',
            'message': 'Video Download API is running',
            'version': '1.0.0'
        })
    
    # إضافة مسار التوثيق
    @app.route('/')
    def documentation():
        """صفحة التوثيق الأساسية"""
        return jsonify({
            'message': 'Video Download API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'get_download_links': '/api/v1/get-download-links',
                'get_info': '/api/v1/get-info'
            },
            'documentation': {
                'example_request': {
                    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    'format': 'best'
                }
            }
        })
    
    # معالج الأخطاء العام
    @app.errorhandler(404)
    def not_found(error):
        """معالج خطأ 404"""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': 'The requested endpoint does not exist'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """معالج خطأ 500"""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    return app