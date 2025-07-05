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
    
