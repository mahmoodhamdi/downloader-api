"""
مسارات API لاستخراج معلومات الفيديو
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from app.services.video_service import VideoService
from app.utils.logger import setup_logger, log_request, log_error
from app.config import Config

# إنشاء Blueprint
video_bp = Blueprint('video', __name__)

# إعداد الخدمات
video_service = VideoService()
logger = setup_logger('video_routes')
config = Config()

def validate_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    التحقق من صحة بيانات الطلب
    
    Args:
        data: بيانات الطلب
        
    Returns:
        Dict: نتيجة التحقق
    """
    if not data:
        return {
            'valid': False,
            'error': 'No JSON data provided'
        }
    
    # التحقق من وجود الرابط
    if 'url' not in data:
        return {
            'valid': False,
            'error': 'URL is required'
        }
    
    url = data['url']
    if not url or not isinstance(url, str):
        return {
            'valid': False,
            'error': 'URL must be a valid string'
        }
    
    # التحقق من الصيغة (اختياري)
    format_selector = data.get('format', 'best')
    if format_selector not in config.SUPPORTED_FORMATS:
        return {
            'valid': False,
            'error': f'Unsupported format. Supported formats: {", ".join(config.SUPPORTED_FORMATS)}'
        }
    
    return {
        'valid': True,
        'url': url.strip(),
        'format': format_selector
    }

@video_bp.route('/get-download-links', methods=['POST'])
def get_download_links():
    """
    استخراج روابط التحميل المباشرة
    
    Expected JSON:
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "format": "best"  // optional
    }
    """
    try:
        # تسجيل الطلب
        log_request(logger, request.method, request.url, request.headers.get('User-Agent'))
        
        # التحقق من نوع المحتوى
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        # التحقق من صحة البيانات
        validation = validate_request_data(request.json)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        # استخراج روابط التحميل
        result = video_service.get_download_links(
            validation['url'],
            validation['format']
        )
        
        # تحديد رمز الاستجابة
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        log_error(logger, e, 'Error in get_download_links')
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while processing your request'
        }), 500

@video_bp.route('/get-info', methods=['POST'])
def get_video_info():
    """
    استخراج معلومات الفيديو التفصيلية
    
    Expected JSON:
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "format": "best"  // optional
    }
    """
    try:
        # تسجيل الطلب
        log_request(logger, request.method, request.url, request.headers.get('User-Agent'))
        
        # التحقق من نوع المحتوى
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        # التحقق من صحة البيانات
        validation = validate_request_data(request.json)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        # استخراج معلومات الفيديو
        result = video_service.get_video_info(
            validation['url'],
            validation['format']
        )
        
        # تحديد رمز الاستجابة
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        log_error(logger, e, 'Error in get_video_info')
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while processing your request'
        }), 500

@video_bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """
    الحصول على قائمة الصيغ المدعومة
    """
    try:
        log_request(logger, request.method, request.url, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'supported_formats': config.SUPPORTED_FORMATS,
            'format_categories': {
                'quality': ['best', 'worst', 'bestvideo', 'worstvideo', 'bestaudio', 'worstaudio'],
                'resolution': ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p'],
                'video_formats': ['mp4', 'webm', 'mkv', 'flv', 'avi', 'mov'],
                'audio_formats': ['mp3', 'aac', 'ogg', 'wav', 'flac', 'm4a']
            }
        }), 200
        
    except Exception as e:
        log_error(logger, e, 'Error in get_supported_formats')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@video_bp.route('/health', methods=['GET'])
def health_check():
    """
    فحص صحة خدمة الفيديو
    """
    try:
        return jsonify({
            'success': True,
            'service': 'video_service',
            'status': 'healthy',
            'supported_extractors': ['youtube', 'vimeo', 'dailymotion', 'facebook', 'instagram', 'twitter', 'tiktok']
        }), 200
        
    except Exception as e:
        log_error(logger, e, 'Error in video service health check')
        return jsonify({
            'success': False,
            'service': 'video_service',
            'status': 'unhealthy',
            'error': str(e)
        }), 500