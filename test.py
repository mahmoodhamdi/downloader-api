#!/usr/bin/env python3
"""
Simple API test script for video extraction service
"""

import requests
import json
import time

# Test settings
BASE_URL = "http://127.0.0.1:5000"
TEST_URLS = [
    "https://www.youtube.com/watch?v=NcPQm2KkIWE&t=4s&pp=ygUOZmFzdGFwaSDYtNix2K0%3D",  # Popular video
    "https://www.youtube.com/watch?v=yvyKtJVVIdk&list=PLGbzY-VLUfcpzhB-iyGvju-NMMez_NNP9",  # Playlist
]

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check successful")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_supported_formats():
    """Test supported formats endpoint"""
    print("\n🎯 Testing supported formats...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/supported-formats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supported formats: {len(data['supported_formats'])} formats")
            return True
        else:
            print(f"❌ Failed to get supported formats: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Supported formats error: {e}")
        return False

def test_get_download_links(url, format_type="best"):
    """Test download links extraction"""
    print(f"\n📥 Testing download links extraction...")
    print(f"URL: {url}")
    print(f"Format: {format_type}")
    
    try:
        data = {
            "url": url,
            "format": format_type
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/get-download-links",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Extraction successful in {duration:.2f} seconds")
                
                if result['is_playlist']:
                    print(f"📋 Playlist: {result['playlist']['title']}")
                    print(f"📹 Videos: {result['playlist']['total_videos']}")
                else:
                    print(f"🎬 Video: {result['video']['title']}")
                    print(f"⏱️ Duration: {result['video']['duration_formatted']}")
                    print(f"🎞️ Formats: {len(result['video']['formats'])}")
                
                return True
            else:
                print(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Download links error: {e}")
        return False

def test_get_video_info(url):
    """Test video information extraction"""
    print(f"\n📊 Testing video information extraction...")
    print(f"URL: {url}")
    
    try:
        data = {
            "url": url,
            "format": "best"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/get-info",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Extraction successful in {duration:.2f} seconds")
                
                if result['is_playlist']:
                    playlist = result['playlist']
                    print(f"📋 Playlist: {playlist['title']}")
                    print(f"👤 Channel: {playlist['uploader']}")
                    print(f"📹 Videos: {playlist['total_videos']}")
                else:
                    video = result['video']
                    print(f"🎬 Title: {video['title']}")
                    print(f"👤 Channel: {video['uploader']}")
                    print(f"⏱️ Duration: {video['duration_formatted']}")
                    print(f"👁️ Views: {video.get('view_count', 'N/A')}")
                    print(f"🎞️ Formats: {len(video['formats'])}")
                
                return True
            else:
                print(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Video info error: {e}")
        return False

def test_get_subtitles(url):
    """Test subtitles extraction"""
    print(f"\n📜 Testing subtitles extraction...")
    print(f"URL: {url}")
    
    try:
        data = {
            "url": url
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/get-subtitles",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Subtitles extraction successful in {duration:.2f} seconds")
                
                if result['is_playlist']:
                    print(f"📋 Playlist: {result['playlist']['title']}")
                    print(f"📹 Videos: {result['playlist']['total_videos']}")
                else:
                    print(f"🎬 Video: {result['video']['title']}")
                    print(f"📜 Subtitles: {len(result['video']['subtitles'])} languages")
                
                return True
            else:
                print(f"❌ Subtitles extraction failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Subtitles error: {e}")
        return False

def test_get_thumbnails(url):
    """Test thumbnails extraction"""
    print(f"\n🖼️ Testing thumbnails extraction...")
    print(f"URL: {url}")
    
    try:
        data = {
            "url": url
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/get-thumbnails",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Thumbnails extraction successful in {duration:.2f} seconds")
                
                if result['is_playlist']:
                    print(f"📋 Playlist: {result['playlist']['title']}")
                    print(f"📹 Videos: {result['playlist']['total_videos']}")
                else:
                    print(f"🎬 Video: {result['video']['title']}")
                    print(f"🖼️ Thumbnails: {len(result['video']['thumbnails'])}")
                
                return True
            else:
                print(f"❌ Thumbnails extraction failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Thumbnails error: {e}")
        return False

if __name__ == "__main__":
    print("Starting API tests...")
    test_health_check()
    test_supported_formats()
    
    for url in TEST_URLS:
        test_get_download_links(url)
        test_get_video_info(url)
        test_get_subtitles(url)
        test_get_thumbnails(url)
    print("Tests completed.")