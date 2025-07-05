# 🎬 Video Download API

## 📋 نظرة عامة

Video Download API هو تطبيق Flask مصمم لاستخراج روابط التحميل المباشرة من YouTube وعشرات المنصات الأخرى باستخدام مكتبة `yt-dlp`. يوفر التطبيق واجهة برمجة تطبيقات RESTful سهلة الاستخدام للتطبيقات المختلفة.

## ✨ المميزات

- 🎯 استخراج روابط التحميل المباشرة من YouTube و 1000+ منصة أخرى
- 📱 دعم كامل للبلايليست والفيديوهات المفردة
- 🎨 صيغ متعددة (جودات مختلفة، صوت فقط، تنسيقات مختلفة)
- 📊 معلومات تفصيلية عن الفيديوهات (العنوان، المدة، الحجم، إلخ)
- 🔍 نظام logging شامل لتتبع الطلبات والأخطاء
- 🏗️ هيكل منظم وقابل للتوسع
- 🚀 جاهز للنشر في بيئة الإنتاج

## 📦 المتطلبات

```bash
Python 3.8+
Flask 2.3.3+
yt-dlp 2023.12.30+
```

## 🚀 التثبيت والتشغيل

### 1. استنساخ المشروع

```bash
git clone <repository-url>
cd video-download-api
```

### 2. إنشاء البيئة الافتراضية

```bash
python -m venv venv

# على Windows
venv\Scripts\activate

# على macOS/Linux  
source venv/bin/activate
```

### 3. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 4. تشغيل التطبيق

```bash
python main.py
```

أو باستخدام Flask:

```bash
flask run
```

التطبيق سيعمل على: `http://127.0.0.1:5000`

## 🔗 API Endpoints

### 1. الصفحة الرئيسية

```
GET /
```

عرض معلومات التطبيق والتوثيق الأساسي.

### 2. فحص الصحة

```
GET /health
```

فحص صحة التطبيق.

### 3. استخراج روابط التحميل

```
POST /api/v1/get-download-links
```

**طلب JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "best"
}
```

**استجابة JSON (فيديو مفرد):**

```json
{
  "success": true,
  "is_playlist": false,
  "video": {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "duration_formatted": "03:33",
    "formats": [
      {
        "format_id": "22",
        "format_note": "720p",
        "ext": "mp4",
        "url": "https://...",
        "filesize_formatted": "50.3 MB"
      }
    ]
  }
}
```

**استجابة JSON (بلايليست):**

```json
{
  "success": true,
  "is_playlist": true,
  "playlist": {
    "title": "My Playlist",
    "total_videos": 5,
    "videos": [
      {
        "id": "dQw4w9WgXcQ",
        "title": "Video 1",
        "formats": [...]
      }
    ]
  }
}
```

### 4. معلومات الفيديو التفصيلية

```
POST /api/v1/get-info
```

**طلب JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "best"
}
```

**استجابة JSON:**

```json
{
  "success": true,
  "is_playlist": false,
  "video": {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "uploader": "Rick Astley",
    "duration": 213,
    "duration_formatted": "03:33",
    "view_count": 1000000,
    "like_count": 50000,
    "description": "...",
    "thumbnail": "https://...",
    "formats": [
      {
        "format_id": "22",
        "format_note": "720p",
        "ext": "mp4",
        "resolution": "1280x720",
        "filesize_formatted": "50.3 MB",
        "url": "https://..."
      }
    ]
  }
}
```

### 5. الصيغ المدعومة

```
GET /api/v1/supported-formats
```

## 📋 الصيغ المدعومة

### جودة الفيديو

- `best` - أفضل جودة متاحة
- `worst` - أقل جودة متاحة
- `720p`, `1080p`, `1440p`, `2160p` - جودات محددة

### تنسيقات الفيديو

- `mp4`, `webm`, `mkv`, `flv`, `avi`, `mov`

### تنسيقات الصوت

- `mp3`, `aac`, `ogg`, `wav`, `flac`, `m4a`

### خيارات خاصة

- `bestvideo` - أفضل فيديو فقط
- `bestaudio` - أفضل صوت فقط
- `audio_only` - صوت فقط

## 🧪 اختبار API

### باستخدام cURL

```bash
# استخراج روابط التحميل
curl -X POST http://127.0.0.1:5000/api/v1/get-download-links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "720p"
  }'

# معلومات الفيديو التفصيلية
curl -X POST http://127.0.0.1:5000/api/v1/get-info \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'

# فحص الصحة
curl http://127.0.0.1:5000/health

# الصيغ المدعومة
curl http://127.0.0.1:5000/api/v1/supported-formats
```

### باستخدام Python

```python
import requests
import json

# استخراج روابط التحميل
url = "http://127.0.0.1:5000/api/v1/get-download-links"
data = {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "best"
}

response = requests.post(url, json=data)
result = response.json()

if result['success']:
    print(f"Title: {result['video']['title']}")
    for fmt in result['video']['formats']:
        print(f"Format: {fmt['format_note']} - {fmt['ext']}")
        print(f"Download: {fmt['url']}")
```

## 🏗️ هيكل المشروع

```
your_project/
├── app/
│   ├── routes/
│   │   └── video_routes.py      # مسارات API
│   ├── services/
│   │   └── video_service.py     # منطق استخراج الفيديو
│   ├── utils/
│   │   └── logger.py            # نظام اللوغر
│   ├── config.py                # إعدادات التطبيق
│   └── __init__.py             # مصنع التطبيق
├── main.py                      # نقطة الدخول الرئيسية
├── requirements.txt             # متطلبات Python
└── README.md                    # هذا الملف
```

## ⚙️ التكوين

يمكن تخصيص التطبيق من خلال متغيرات البيئة:

```bash
# إعدادات الأمان
export SECRET_KEY="your-secret-key"

# إعدادات اللوغر
export LOG_LEVEL="INFO"
export LOG_FILE="app.log"

# إعدادات الحدود
export RATE_LIMIT_ENABLED="true"
export RATE_LIMIT_REQUESTS="10"
export RATE_LIMIT_WINDOW="60"
```

## 🚀 النشر في الإنتاج

### باستخدام Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### باستخدام Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

## 📊 المنصات المدعومة

التطبيق يدعم أكثر من 1000 منصة بما في ذلك:

- **YouTube** - فيديوهات وبلايليست
- **Vimeo** - فيديوهات عامة وخاصة
- **Facebook** - فيديوهات عامة
- **Instagram** - فيديوهات ومقاطع IGTV
- **Twitter** - فيديوهات وGIF
- **TikTok** - فيديوهات قصيرة
- **Dailymotion** - فيديوهات وبلايليست
- **Reddit** - فيديوهات من Reddit
- **Twitch** - مقاطع وبث مباشر
- **SoundCloud** - مقاطع صوتية
- **وعشرات المنصات الأخرى**

## 🛠️ استكشاف الأخطاء

### أخطاء شائعة

1. **URL غير صالح**

   ```json
   {
     "success": false,
     "error": "Invalid URL format"
   }
   ```

2. **فيديو غير متاح**

   ```json
   {
     "success": false,
     "error": "Video unavailable"
   }
   ```

3. **صيغة غير مدعومة**

   ```json
   {
     "success": false,
     "error": "Unsupported format"
   }
   ```

### فحص اللوغز

```bash
# عرض اللوغز المباشرة
tail -f app.log

# البحث عن أخطاء
grep "ERROR" app.log
```

## 🔒 الأمان

### إعدادات الأمان الموصى بها

1. **استخدام HTTPS في الإنتاج**
2. **تعيين SECRET_KEY قوي**
3. **تمكين Rate Limiting**
4. **استخدام Reverse Proxy (Nginx)**
5. **تحديث المكتبات بانتظام**

## 🤝 المساهمة

نرحب بالمساهمات! يرجى:

1. Fork المشروع
2. إنشاء فرع جديد للميزة
3. Commit التغييرات
4. Push إلى الفرع
5. فتح Pull Request

## 📜 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف LICENSE للتفاصيل.

## 📞 الدعم

للمساعدة والاستفسارات:

- فتح issue في GitHub
- مراسلة المطور
- مراجعة التوثيق

## 🔄 التحديثات

- **v1.0.0** - الإصدار الأول
- دعم كامل لاستخراج الفيديوهات
- نظام logging متقدم
- هيكل منظم وقابل للتوسع

---

**ملاحظة:** هذا التطبيق مخصص للاستخدام التعليمي والشخصي. يرجى احترام حقوق الطبع والنشر وشروط استخدام المنصات المختلفة.
