"""
خدمة استخراج معلومات الفيديو باستخدام yt-dlp
"""

import yt_dlp
import time
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse
from app.utils.logger import setup_logger, log_error, log_video_extraction
from app.config import Config

class VideoService:
    """
    خدمة استخراج معلومات الفيديو من منصات متعددة
    """
    
    def __init__(self):
        """
        تهيئة الخدمة
        """
        self.logger = setup_logger('video_service')
        self.config = Config()
        
    def _get_yt_dlp_options(self, format_selector: str = 'best') -> Dict[str, Any]:
        """
        الحصول على خيارات yt-dlp المخصصة
        
        Args:
            format_selector: محدد الصيغة
            
        Returns:
            Dict: خيارات yt-dlp
        """
        options = self.config.YT_DLP_OPTIONS.copy()
        
        # تحديد الصيغة المطلوبة
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
        
        return options
    
    def _validate_url(self, url: str) -> bool:
        """
        التحقق من صحة الرابط
        
        Args:
            url: الرابط المراد التحقق منه
            
        Returns:
            bool: صحة الرابط
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _format_duration(self, seconds: Optional[int]) -> str:
        """
        تنسيق المدة من ثواني إلى تنسيق مقروء
        
        Args:
            seconds: المدة بالثواني
            
        Returns:
            str: المدة منسقة
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
        تنسيق حجم الملف
        
        Args:
            size: حجم الملف بالبايت
            
        Returns:
            str: حجم الملف منسق
        """
        if not size:
            return "Unknown"
        
        # تحويل البايت إلى وحدات أكبر
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _extract_formats(self, info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        استخراج صيغ الفيديو المتاحة
        
        Args:
            info: معلومات الفيديو من yt-dlp
            
        Returns:
            List: قائمة الصيغ المتاحة
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
                    'tbr': fmt.get('tbr'),  # Total bitrate
                    'vbr': fmt.get('vbr'),  # Video bitrate
                    'abr': fmt.get('abr'),  # Audio bitrate
                    'protocol': fmt.get('protocol', 'unknown')
                }
                
                # إضافة حجم الملف المنسق
                size = format_info['filesize'] or format_info['filesize_approx']
                format_info['filesize_formatted'] = self._format_filesize(size)
                
                formats.append(format_info)
        
        return formats
    
    def _extract_video_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        استخراج معلومات الفيديو المهمة
        
        Args:
            info: معلومات الفيديو من yt-dlp
            
        Returns:
            Dict: معلومات الفيديو المنسقة
        """
        return {
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
            'thumbnails': info.get('thumbnails', []),
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
    
    def get_video_info(self, url: str, format_selector: str = 'best') -> Dict[str, Any]:
        """
        استخراج معلومات الفيديو أو البلايليست
        
        Args:
            url: رابط الفيديو أو البلايليست
            format_selector: محدد الصيغة المطلوبة
            
        Returns:
            Dict: معلومات الفيديو أو البلايليست
        """
        start_time = time.time()
        
        try:
            # التحقق من صحة الرابط
            if not self._validate_url(url):
                raise ValueError("Invalid URL format")
            
            # إعداد خيارات yt-dlp
            ydl_opts = self._get_yt_dlp_options(format_selector)
            
            # استخراج المعلومات
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            # تحديد نوع المحتوى
            is_playlist = 'entries' in info
            
            if is_playlist:
                # معالجة البلايليست
                entries = info.get('entries', [])
                
                # فلترة المدخلات الفارغة
                valid_entries = [entry for entry in entries if entry is not None]
                
                # تحديد حد البلايليست
                if len(valid_entries) > self.config.MAX_PLAYLIST_SIZE:
                    valid_entries = valid_entries[:self.config.MAX_PLAYLIST_SIZE]
                    self.logger.warning(f"Playlist limited to {self.config.MAX_PLAYLIST_SIZE} videos")
                
                # استخراج معلومات كل فيديو
                videos = []
                for entry in valid_entries:
                    try:
                        video_info = self._extract_video_info(entry)
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
                # معالجة فيديو واحد
                video_info = self._extract_video_info(info)
                
                result = {
                    'success': True,
                    'is_playlist': False,
                    'video': video_info
                }
                
                video_count = 1
            
            # تسجيل نجاح العملية
            duration = time.time() - start_time
            log_video_extraction(self.logger, url, True, video_count, duration)
            
            return result
            
        except Exception as e:
            # تسجيل فشل العملية
            duration = time.time() - start_time
            log_video_extraction(self.logger, url, False, 0, duration)
            log_error(self.logger, e, f"Error extracting video info from {url}")
            
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to extract video information'
            }
    
    def get_download_links(self, url: str, format_selector: str = 'best') -> Dict[str, Any]:
        """
        استخراج روابط التحميل المباشرة
        
        Args:
            url: رابط الفيديو أو البلايليست
            format_selector: محدد الصيغة المطلوبة
            
        Returns:
            Dict: روابط التحميل المباشرة
        """
        # استخراج معلومات الفيديو
        info = self.get_video_info(url, format_selector)
        
        if not info['success']:
            return info
        
        # استخراج روابط التحميل فقط
        if info['is_playlist']:
            # معالجة البلايليست
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
            # معالجة فيديو واحد
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