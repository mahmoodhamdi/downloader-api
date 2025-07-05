"""
API routes for video information extraction
"""

from flask import Blueprint, request, jsonify
import time
from typing import Dict, Any
from app.services.video_service import VideoService
from app.utils.logger import setup_logger, log_request, log_error
from app.config import Config
from app.db import get_stored_result, add_request_log
import yt_dlp

# Create Blueprint
video_bp = Blueprint('video', __name__)

# Set up services
video_service = VideoService()
logger = setup_logger('video_routes')
config = Config()

def validate_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate request data
    
    Args:
        data: Request data
        
    Returns:
        Dict: Validation result
    """
    if not data:
        return {'valid': False, 'error': 'No JSON data provided'}
    
    if 'url' not in data and 'urls' not in data:
        return {'valid': False, 'error': 'URL or URLs list is required'}
    
    format_selector = data.get('format', 'best')
    if format_selector not in config.SUPPORTED_FORMATS:
        return {'valid': False, 'error': f'Unsupported format. Supported formats: {", ".join(config.SUPPORTED_FORMATS)}'}
    
    if 'url' in data:
        url = data['url']
        if not isinstance(url, str) or not url.strip():
            return {'valid': False, 'error': 'URL must be a valid string'}
        return {'valid': True, 'urls': [url.strip()], 'format': format_selector}
    
    elif 'urls' in data:
        urls = data['urls']
        if not isinstance(urls, list) or not all(isinstance(u, str) for u in urls):
            return {'valid': False, 'error': 'URLs must be a list of strings'}
        valid_urls = [u.strip() for u in urls if u.strip()]
        if not valid_urls:
            return {'valid': False, 'error': 'No valid URLs provided'}
        return {'valid': True, 'urls': valid_urls, 'format': format_selector}
    
    return {'valid': False, 'error': 'Invalid request data'}

def get_video_info_with_cache(url: str, format: str, enable_subtitles: bool = False) -> Dict[str, Any]:
    """
    Get video info with caching
    
    Args:
        url: Video URL
        format: Requested format
        enable_subtitles: Whether to enable subtitle extraction
        
    Returns:
        Dict: Video information
    """
    stored_result = get_stored_result(url, format)
    if stored_result:
        logger.info(f"Retrieved cached result for URL: {url}, format: {format}")
        return stored_result
    
    start_time = time.time()
    result = video_service.get_video_info(url, format, enable_subtitles)
    duration = time.time() - start_time
    add_request_log(url, format, result, duration)
    logger.info(f"Processed new request for URL: {url}, format: {format}, duration: {duration:.2f}s")
    return result

@video_bp.route('/get-download-links', methods=['POST'])
def get_download_links():
    """
    Extract direct download links
    
    Expected JSON:
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "format": "best"  // optional
    }
    or
    {
        "urls": ["url1", "url2", ...],
        "format": "best"  // optional
    }
    """
    try:
        start_time = time.time()
        log_request(logger, request.method, request.url, request.headers.get('User-Agent'))
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        validation = validate_request_data(request.json)
        if not validation['valid']:
            return jsonify({'success': False, 'error': validation['error']}), 400
        
        urls = validation['urls']
        format = validation['format']
        results = []
        
        for url in urls:
            info = get_video_info_with_cache(url, format)
            if not info['success']:
                results.append({'url': url, 'success': False, 'error': info['error']})
                continue
            
            if info['is_playlist']:
                download_links = []
                for video in info['playlist']['videos']:
                    video_links = {
                        'id': video['id'],
                        'title': video['title'],
                        'formats': []
                    }
                    for fmt in video['formats']:
                        if fmt['url']:
                            video_links['formats'].append({
                                'format_id': fmt['format_id'],
                                'format_note': fmt['format_note'],
                                'ext': fmt['ext'],
                                'url': fmt['url'],
                                'filesize_formatted': fmt['filesize_formatted']
                            })
                    download_links.append(video_links)
                result = {
                    'url': url,
                    'success': True,
                    'is_playlist': True,
                    'playlist': {
                        'title': info['playlist']['title'],
                        'total_videos': info['playlist']['total_videos'],
                        'videos': download_links
                    }
                }
            else:
                video = info['video']
                download_links = []
                for fmt in video['formats']:
                    if fmt['url']:
                        download_links.append({
                            'format_id': fmt['format_id'],
                            'format_note': fmt['format_note'],
                            'ext': fmt['ext'],
                            'url': fmt['url'],
                            'filesize_formatted': fmt['filesize_formatted']
                        })
                result = {
                    'url': url,
                    'success': True,
                    'is_playlist': False,
                    'video': {
                        'id': video['id'],
                        'title': video['title'],
                        'duration_formatted': video['duration_formatted'],
                        'formats': download_links
                    }
                }
            results.append(result)
        
        duration = time.time() - start_time
        logger.info(f"Request processed in {duration:.2f} seconds")
        
        if len(urls) == 1:
            return jsonify(results[0]), 200 if results[0]['success'] else 400
        return jsonify({'results': results}), 200
        
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
    Extract detailed video information
    
    Expected JSON:
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "format": "best"  // optional
    }
    or
    {
        "urls": ["url1", "url2", ...],
        "format": "best"  // optional
    }
    """
    try:
        start_time = time.time()
        log_request(logger, request.method, request.url, request.headers.get('User-Agent'))
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        validation = validate_request_data(request.json)
        if not validation['valid']:
            return jsonify({'success': False, 'error': validation['error']}), 400
        
        urls = validation['urls']
        format = validation['format']
        results = []
        
        for url in urls:
            result = get_video_info_with_cache(url, format)
            results.append({'url': url, **result})
        
        duration = time.time() - start_time
        logger.info(f"Request processed in {duration:.2f} seconds")
        
        if len(urls) == 1:
            return jsonify(results[0]), 200 if results[0]['success'] else 400
        return jsonify({'results': results}), 200
        
    except Exception as e:
        log_error(logger, e, 'Error in get_video_info')
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while processing your request'
        }), 500

@video_bp.route('/get-subtitles', methods=['POST'])
def get_subtitles():
    """
    Extract available subtitle links
    
    Expected JSON:
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
    or
    {
        "urls": ["url1", "url2", ...]
    }
    """
    try:
        start_time = time.time()
        log_request(logger, request.method, request.url, request.headers.get('User-Agent'))
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        validation = validate_request_data(request.json)
        if not validation['valid']:
            return jsonify({'success': False, 'error': validation['error']}), 400
        
        urls = validation['urls']
        results = []
        
        for url in urls:
            stored_result = get_stored_result(url, 'subtitles')
            if stored_result:
                logger.info(f"Retrieved cached subtitles for URL: {url}")
                results.append({'url': url, **stored_result})
                continue
            
            result = video_service.get_subtitles(url)
            duration = time.time() - start_time
            add_request_log(url, 'subtitles', result, duration)
            logger.info(f"Processed new subtitles request for URL: {url}, duration: {duration:.2f}s")
            results.append({'url': url, **result})
        
        duration = time.time() - start_time
        logger.info(f"Request processed in {duration:.2f} seconds")
        
        if len(urls) == 1:
            return jsonify(results[0]), 200 if results[0]['success'] else 400
        return jsonify({'results': results}), 200
        
    except Exception as e:
        log_error(logger, e, 'Error in get_subtitles')
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while processing your request'
        }), 500

@video_bp.route('/get-thumbnails', methods=['POST'])
def get_thumbnails():
    """
    Extract available thumbnail links
    
    Expected JSON:
    {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
    or
    {
        "urls": ["url1", "url2", ...]
    }
    """
    try:
        start_time = time.time()
        log_request(logger, request.method, request.url, request.headers.get('User-Agent'))
        
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        validation = validate_request_data(request.json)
        if not validation['valid']:
            return jsonify({'success': False, 'error': validation['error']}), 400
        
        urls = validation['urls']
        results = []
        
        for url in urls:
            stored_result = get_stored_result(url, 'thumbnails')
            if stored_result:
                logger.info(f"Retrieved cached thumbnails for URL: {url}")
                results.append({'url': url, **stored_result})
                continue
            
            result = video_service.get_thumbnails(url)
            duration = time.time() - start_time
            add_request_log(url, 'thumbnails', result, duration)
            logger.info(f"Processed new thumbnails request for URL: {url}, duration: {duration:.2f}s")
            results.append({'url': url, **result})
        
        duration = time.time() - start_time
        logger.info(f"Request processed in {duration:.2f} seconds")
        
        if len(urls) == 1:
            return jsonify(results[0]), 200 if results[0]['success'] else 400
        return jsonify({'results': results}), 200
        
    except Exception as e:
        log_error(logger, e, 'Error in get_thumbnails')
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while processing your request'
        }), 500

@video_bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """
    Get list of supported formats
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
    Video service health check
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