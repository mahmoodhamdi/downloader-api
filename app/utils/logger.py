"""
إعدادات نظام اللوغر للتطبيق
"""

import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(name: str = 'video_api', log_file: Optional[str] = None) -> logging.Logger:
    """
    إعداد نظام اللوغر للتطبيق
    
    Args:
        name: اسم اللوغر
        log_file: مسار ملف اللوغ (اختياري)
        
    Returns:
        logging.Logger: كائن اللوغر المُعد
    """
    
    # إنشاء اللوغر
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # تجنب إضافة متعددة للمعالجات
    if logger.handlers:
        return logger
    
    # تنسيق الرسائل
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # معالج الكونسول
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # معالج الملف (اختياري)
    if log_file:
        try:
            # إنشاء مجلد اللوغس إذا لم يكن موجوداً
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
    تسجيل طلب HTTP
    
    Args:
        logger: كائن اللوغر
        method: طريقة HTTP
        url: الرابط المطلوب
        user_agent: معلومات المتصفح
    """
    message = f"{method} {url}"
    if user_agent:
        message += f" - User-Agent: {user_agent}"
    
    logger.info(message)

def log_error(logger: logging.Logger, error: Exception, context: str = None):
    """
    تسجيل خطأ مع السياق
    
    Args:
        logger: كائن اللوغر
        error: الخطأ
        context: السياق الإضافي
    """
    message = f"Error: {str(error)}"
    if context:
        message = f"{context} - {message}"
    
    logger.error(message, exc_info=True)

def log_video_extraction(logger: logging.Logger, url: str, success: bool, 
                        video_count: int = 0, duration: float = 0):
    """
    تسجيل عملية استخراج الفيديو
    
    Args:
        logger: كائن اللوغر
        url: رابط الفيديو
        success: نجاح العملية
        video_count: عدد الفيديوهات المستخرجة
        duration: مدة العملية بالثواني
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