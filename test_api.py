#!/usr/bin/env python3
"""
اختبار API بسيط لخدمة استخراج الفيديو
"""

import requests
import json
import time

# إعدادات الاختبار
BASE_URL = "http://127.0.0.1:5000"
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # فيديو مشهور
    "https://www.youtube.com/playlist?list=PLQVvvaa0QuDeFfpmSd7P9-7PgkZhPZMjB",  # بلايليست
]

def test_health_check():
    """اختبار فحص الصحة"""
    print("🔍 اختبار فحص الصحة...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ فحص الصحة نجح")
            return True
        else:
            print(f"❌ فحص الصحة فشل: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطأ في فحص الصحة: {e}")
        return False

def test_supported_formats():
    """اختبار الصيغ المدعومة"""
    print("\n🎯 اختبار الصيغ المدعومة...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/supported-formats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ الصيغ المدعومة: {len(data['supported_formats'])} صيغة")
            return True
        else:
            print(f"❌ فشل في الحصول على الصيغ المدعومة: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطأ في اختبار الصيغ المدعومة: {e}")
        return False

def test_get_download_links(url, format_type="best"):
    """اختبار استخراج روابط التحميل"""
    print(f"\n📥 اختبار استخراج روابط التحميل...")
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
                print(f"✅ نجح الاستخراج في {duration:.2f} ثانية")
                
                if result['is_playlist']:
                    print(f"📋 بلايليست: {result['playlist']['title']}")
                    print(f"📹 عدد الفيديوهات: {result['playlist']['total_videos']}")
                else:
                    print(f"🎬 فيديو: {result['video']['title']}")
                    print(f"⏱️ المدة: {result['video']['duration_formatted']}")
                    print(f"🎞️ عدد الصيغ: {len(result['video']['formats'])}")
                
                return True
            else:
                print(f"❌ فشل الاستخراج: {result.get('error', 'خطأ غير معروف')}")
                return False
        else:
            print(f"❌ فشل الطلب: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ خطأ في اختبار استخراج الروابط: {e}")
        return False

def test_get_video_info(url):
    """اختبار استخراج معلومات الفيديو"""
    print(f"\n📊 اختبار استخراج معلومات الفيديو...")
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
                print(f"✅ نجح الاستخراج في {duration:.2f} ثانية")
                
                if result['is_playlist']:
                    playlist = result['playlist']
                    print(f"📋 بلايليست: {playlist['title']}")
                    print(f"👤 القناة: {playlist['uploader']}")
                    print(f"📹 عدد الفيديوهات: {playlist['total_videos']}")
                else:
                    video = result['video']
                    print(f"🎬 العنوان: {video['title']}")
                    print(f"👤 القناة: {video['uploader']}")
                    print(f"⏱️ المدة: {video['duration_formatted']}")
                    print(f"👁️ المشاهدات: {video.get('view_count', 'غير متاح')}")
                    print(f"🎞️ عدد الصيغ: {len(video['formats'])}")
                
                return True
            else:
                print(f"❌ فشل الاستخراج: {result.get('error', 'خطاء غير معروف')}")
                return False
        else:
            print(f"❌ فشل الطلب: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ خطاء في اختبار استخراج المعلومات: {e}")
        return False