"""
Video information extraction service using yt-dlp
"""

import yt_dlp
import time
import re
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse
from app.utils.logger import setup_logger, log_error, log_video_extraction
from app.config import Config

class YTDLPLogger:
    """Logger adapter for yt-dlp"""
    def __init__(self, logger):
        self.logger = logger

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

class VideoService:
    """
    Service for extracting video information from multiple platforms
    """
    
    def __init__(self):
        """
        Initialize the service
        """
        self.logger = setup_logger('video_service')
        self.config = Config()
        
    def _get_yt_dlp_options(self, format_selector: str = 'best', enable_subtitles: bool = False) -> Dict[str, Any]:
        """
        Get customized yt-dlp options
        
        Args:
            format_selector: Format selector
            enable_subtitles: Whether to enable subtitle extraction
            
        Returns:
            Dict: yt-dlp options
        """
        options = self.config.YT_DLP_OPTIONS.copy()
        
        # Set format based on selector
        if format_selector in self.config.SUPPORTED_FORMATS:
            if format_selector == 'audio_only':
                options['format'] = 'bestaudio'
                options['extractaudio'] = True
            elif format_selector in ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']:
                height = format_selector.replace('p', '')
                options['format'] = f'best[height<={height}]'
            else:
                options['format'] = format_selector
        else:
            options['format'] = 'best'
        
        # Enable subtitles if requested
        if enable_subtitles:
            options['writesubtitles'] = True
            options['writeautomaticsub'] = True
        
        # Add logger
        options['logger'] = YTDLPLogger(self.logger)
        
        return options
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate the URL (bypassed to allow all non-empty URLs)
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL is a non-empty string, else False
        """
        return isinstance(url, str) and bool(url.strip())
    
    def _format_duration(self, seconds: Optional[int]) -> str:
        """
        Format duration from seconds to readable format
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            str: Formatted duration
        """
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def _format_filesize(self, size: Optional[int]) -> str:
        """
        Format file size
        
        Args:
            size: File size in bytes
            
        Returns:
            str: Formatted file size
        """
        if not size:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _extract_formats(self, info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract available video formats
        
        Args:
            info: Video information from yt-dlp
            
        Returns:
            List: List of available formats
        """
        formats = []
        
        if 'formats' in info:
            for fmt in info['formats']:
                format_info = {
                    'format_id': fmt.get('format_id', 'unknown'),
                    'format_note': fmt.get('format_note', fmt.get('quality', 'unknown')),
                    'ext': fmt.get('ext', 'unknown'),
                    'resolution': fmt.get('resolution', 'unknown'),
                    'fps': fmt.get('fps'),
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                    'filesize': fmt.get('filesize'),
                    'filesize_approx': fmt.get('filesize_approx'),
                    'url': fmt.get('url'),
                    'tbr': fmt.get('tbr'),
                    'vbr': fmt.get('vbr'),
                    'abr': fmt.get('abr'),
                    'protocol': fmt.get('protocol', 'unknown')
                }
                
                size = format_info['filesize'] or format_info['filesize_approx']
                format_info['filesize_formatted'] = self._format_filesize(size)
                
                formats.append(format_info)
        
        return formats
    
    def _extract_subtitles(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract available subtitles
        
        Args:
            info: Video information from yt-dlp
            
        Returns:
            Dict: Available subtitles
        """
        subtitles = {}
        if 'subtitles' in info:
            for lang, sub_list in info['subtitles'].items():
                subtitles[lang] = [
                    {
                        'url': sub.get('url'),
                        'ext': sub.get('ext'),
                        'name': sub.get('name', lang)
                    }
                    for sub in sub_list
                ]
        if 'automatic_captions' in info:
            subtitles['auto'] = {}
            for lang, sub_list in info['automatic_captions'].items():
                subtitles['auto'][lang] = [
                    {
                        'url': sub.get('url'),
                        'ext': sub.get('ext'),
                        'name': sub.get('name', f'auto-{lang}')
                    }
                    for sub in sub_list
                ]
        return subtitles
    
    def _extract_thumbnails(self, info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract available thumbnails
        
        Args:
            info: Video information from yt-dlp
            
        Returns:
            List: List 끝에 available thumbnails
        """
        thumbnails = []
        if 'thumbnails' in info:
            for thumb in info['thumbnails']:
                thumbnails.append({
                    'id': thumb.get('id', 'unknown'),
                    'url': thumb.get('url'),
                    'width': thumb.get('width'),
                    'height': thumb.get('height'),
                    'resolution': f"{thumb.get('width', 'unknown')}x{thumb.get('height', 'unknown')}"
                })
        return thumbnails
    
    def _extract_video_info(self, info: Dict[str, Any], include_subtitles: bool = False) -> Dict[str, Any]:
        """
        Extract important video information
        
        Args:
            info: Video information from yt-dlp
            include_subtitles: Whether to include subtitles
            
        Returns:
            Dict: Formatted video information
        """
        video_info = {
            'id': info.get('id', 'unknown'),
            'title': info.get('title', 'Unknown Title'),
            'uploader': info.get('uploader', 'Unknown'),
            'uploader_id': info.get('uploader_id'),
            'uploader_url': info.get('uploader_url'),
            'upload_date': info.get('upload_date'),
            'duration': info.get('duration'),
            'duration_formatted': self._format_duration(info.get('duration')),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'dislike_count': info.get('dislike_count'),
            'comment_count': info.get('comment_count'),
            'description': info.get('description', ''),
            'thumbnail': info.get('thumbnail'),
            'thumbnails': self._extract_thumbnails(info),
            'webpage_url': info.get('webpage_url'),
            'original_url': info.get('original_url'),
            'extractor': info.get('extractor'),
            'extractor_key': info.get('extractor_key'),
            'formats': self._extract_formats(info),
            'tags': info.get('tags', []),
            'categories': info.get('categories', []),
            'age_limit': info.get('age_limit'),
            'availability': info.get('availability')
        }
        
        if include_subtitles:
            video_info['subtitles'] = self._extract_subtitles(info)
        
        return video_info
    
    def get_video_info(self, url: str, format_selector: str = 'best', enable_subtitles: bool = False) -> Dict[str, Any]:
        """
        Extract video or playlist information
        
        Args:
            url: Video or playlist URL
            format_selector: Desired format selector
            enable_subtitles: Whether to extract subtitles
            
        Returns:
            Dict: Video or playlist information
        """
        start_time = time.time()
        
        try:
            if not self._validate_url(url):
                raise ValueError("Invalid URL format")
            
            ydl_opts = self._get_yt_dlp_options(format_selector, enable_subtitles)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            is_playlist = 'entries' in info
            
            if is_playlist:
                entries = info.get('entries', [])
                valid_entries = [entry for entry in entries if entry is not None]
                
                if len(valid_entries) > self.config.MAX_PLAYLIST_SIZE:
                    valid_entries = valid_entries[:self.config.MAX_PLAYLIST_SIZE]
                    self.logger.warning(f"Playlist limited to {self.config.MAX_PLAYLIST_SIZE} videos")
                
                videos = []
                for entry in valid_entries:
                    try:
                        video_info = self._extract_video_info(entry, include_subtitles=enable_subtitles)
                        videos.append(video_info)
                    except Exception as e:
                        self.logger.error(f"Error extracting video info: {str(e)}")
                        continue
                
                result = {
                    'success': True,
                    'is_playlist': True,
                    'playlist': {
                        'id': info.get('id', 'unknown'),
                        'title': info.get('title', 'Unknown Playlist'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'uploader_id': info.get('uploader_id'),
                        'uploader_url': info.get('uploader_url'),
                        'description': info.get('description', ''),
                        'webpage_url': info.get('webpage_url'),
                        'total_videos': len(valid_entries),
                        'videos': videos
                    }
                }
                
                video_count = len(videos)
                
            else:
                video_info = self._extract_video_info(info, include_subtitles=enable_subtitles)
                
                result = {
                    'success': True,
                    'is_playlist': False,
                    'video': video_info
                }
                
                video_count = 1
            
            duration = time.time() - start_time
            log_video_extraction(self.logger, url, True, video_count, duration)
            
            return result
            
        except yt_dlp.utils.ExtractorError as e:
            error_msg = str(e)
            if 'video is unavailable' in error_msg.lower():
                error_msg = 'Video is unavailable'
            elif 'geo-restricted' in error_msg.lower():
                error_msg = 'Video is geo-restricted'
            elif 'video has been removed' in error_msg.lower():
                error_msg = 'Video has been removed'
            duration = time.time() - start_time
            log_video_extraction(self.logger, url, False, 0, duration)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            duration = time.time() - start_time
            log_video_extraction(self.logger, url, False, 0, duration)
            log_error(self.logger, e, f"Error extracting video info from {url}")
            return {
                'success': False,
                'error': 'An unexpected error occurred',
                'message': str(e)
            }
    
    def get_download_links(self, url: str, format_selector: str = 'best') -> Dict[str, Any]:
        """
        Extract direct download links
        
        Args:
            url: Video or playlist URL
            format_selector: Desired format selector
            
        Returns:
            Dict: Direct download links
        """
        info = self.get_video_info(url, format_selector)
        
        if not info['success']:
            return info
        
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
            
            return {
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
            
            return {
                'success': True,
                'is_playlist': False,
                'video': {
                    'id': video['id'],
                    'title': video['title'],
                    'duration_formatted': video['duration_formatted'],
                    'formats': download_links
                }
            }
    
    def get_subtitles(self, url: str) -> Dict[str, Any]:
        """
        Extract available subtitle links
        
        Args:
            url: Video or playlist URL
            
        Returns:
            Dict: Available subtitles
        """
        info = self.get_video_info(url, enable_subtitles=True)
        
        if not info['success']:
            return info
        
        if info['is_playlist']:
            subtitles_list = []
            for video in info['playlist']['videos']:
                subtitles_list.append({
                    'id': video['id'],
                    'title': video['title'],
                    'subtitles': video.get('subtitles', {})
                })
            
            return {
                'success': True,
                'is_playlist': True,
                'playlist': {
                    'title': info['playlist']['title'],
                    'total_videos': info['playlist']['total_videos'],
                    'videos': subtitles_list
                }
            }
            
        else:
            return {
                'success': True,
                'is_playlist': False,
                'video': {
                    'id': info['video']['id'],
                    'title': info['video']['title'],
                    'subtitles': info['video'].get('subtitles', {})
                }
            }
    
    def get_thumbnails(self, url: str) -> Dict[str, Any]:
        """
        Extract available thumbnail links
        
        Args:
            url: Video or playlist URL
            
        Returns:
            Dict: Available thumbnails
        """
        info = self.get_video_info(url)
        
        if not info['success']:
            return info
        
        if info['is_playlist']:
            thumbnails_list = []
            for video in info['playlist']['videos']:
                thumbnails_list.append({
                    'id': video['id'],
                    'title': video['title'],
                    'thumbnails': video.get('thumbnails', [])
                })
            
            return {
                'success': True,
                'is_playlist': True,
                'playlist': {
                    'title': info['playlist']['title'],
                    'total_videos': info['playlist']['total_videos'],
                    'videos': thumbnails_list
                }
            }
            
        else:
            return {
                'success': True,
                'is_playlist': False,
                'video': {
                    'id': info['video']['id'],
                    'title': info['video']['title'],
                    'thumbnails': info['video'].get('thumbnails', [])
                }
            }