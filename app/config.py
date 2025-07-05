"""
Application configuration
"""

import os
from datetime import timedelta

class Config:
    """
    Base application configuration class
    """
    
    # Flask basic settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///requests.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JSON settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # yt-dlp settings
    YT_DLP_OPTIONS = {
        'format': 'best',
        'noplaylist': False,
        'extractaudio': False,
        'audioformat': 'mp3',
        'ignoreerrors': True,
        'no_warnings': False,
        'extract_flat': False,
        'skip_download': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'subtitleslangs': ['ar', 'en'],
        'geo_bypass': True,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'concurrent_fragment_downloads': 5,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Supported formats
    SUPPORTED_FORMATS = [
        'best', 'worst', 'bestvideo', 'worstvideo', 'bestaudio', 'worstaudio',
        '144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p',
        'mp4', 'webm', 'mkv', 'flv', 'avi', 'mov',
        'mp3', 'aac', 'ogg', 'wav', 'flac', 'm4a'
    ]
    
    # Limit settings
    MAX_PLAYLIST_SIZE = 50
    REQUEST_TIMEOUT = 60
    
    # Logger settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Security settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.environ.get('RATE_LIMIT_REQUESTS', '10'))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', '60'))

class DevelopmentConfig(Config):
    """
    Development configuration
    """
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """
    Production configuration
    """
    DEBUG = False
    TESTING = False
    
    # Additional production security settings
    YT_DLP_OPTIONS = {
        **Config.YT_DLP_OPTIONS,
        'socket_timeout': 60,
        'retries': 5,
        'fragment_retries': 5,
        'concurrent_fragment_downloads': 3
    }

class TestingConfig(Config):
    """
    Testing configuration
    """
    TESTING = True
    DEBUG = True

# Environment mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}