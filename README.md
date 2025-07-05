# 🎬 Video Download API

## 📋 Overview

Video Download API is a Flask application designed to extract direct download links from YouTube and thousands of other platforms using the `yt-dlp` library. It provides a RESTful API for various applications, supporting video and playlist extraction with caching and detailed logging.

## ✨ Features

- 🎯 Extract direct download links from YouTube and 1000+ other platforms
- 📱 Full support for playlists and single videos
- 🎨 Multiple formats (various qualities, audio-only, different formats)
- 📊 Detailed video information (title, duration, size, etc.)
- 💾 SQLite database caching for request results
- 🔍 Comprehensive logging system with request duration and yt-dlp warnings
- 🛡️ Strict URL and format validation
- 📜 Support for subtitle and thumbnail extraction
- 🏗️ Organized and scalable structure
- 🚀 Production-ready deployment

## 📦 Requirements

```bash
Python 3.8+
Flask 2.3.3+
yt-dlp 2023.12.30+
Flask-SQLAlchemy
```

## 🚀 Installation and Setup

### 1. Clone the Project

```bash
git clone <repository-url>
cd video-download-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

Or using Flask:

```bash
flask run
```

The application will run on: `http://127.0.0.1:5000`

## 🔗 API Endpoints

### 1. Home Page

```
GET /
```

Displays application information and basic documentation.

### 2. Health Check

```
GET /health
```

Checks the application's health.

### 3. Extract Download Links

```
POST /api/v1/get-download-links
```

**Request JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "best"
}
```

Or for batch processing:

```json
{
  "urls": ["url1", "url2", "url3"],
  "format": "best"
}
```

**Response JSON (Single Video):**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
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

**Response JSON (Playlist):**

```json
{
  "url": "https://www.youtube.com/playlist?list=PL...",
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

### 4. Detailed Video Information

```
POST /api/v1/get-info
```

**Request JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "best"
}
```

Or for batch processing:

```json
{
  "urls": ["url1", "url2", "url3"],
  "format": "best"
}
```

**Response JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
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

### 5. Extract Subtitles

```
POST /api/v1/get-subtitles
```

**Request JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "success": true,
  "is_playlist": false,
  "video": {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "subtitles": {
      "en": [
        {
          "url": "https://...",
          "ext": "vtt",
          "name": "English"
        }
      ],
      "auto": {
        "en": [
          {
            "url": "https://...",
            "ext": "vtt",
            "name": "auto-English"
          }
        ]
      }
    }
  }
}
```

### 6. Extract Thumbnails

```
POST /api/v1/get-thumbnails
```

**Request JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response JSON:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "success": true,
  "is_playlist": false,
  "video": {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "thumbnails": [
      {
        "id": "0",
        "url": "https://...",
        "width": 1280,
        "height": 720,
        "resolution": "1280x720"
      }
    ]
  }
}
```

### 7. Supported Formats

```
GET /api/v1/supported-formats
```

## 📋 Supported Formats

### Video Quality

- `best` - Best quality available
- `worst` - Lowest quality available
- `720p`, `1080p`, `1440p`, `2160p` - Specific resolutions

### Video Formats

- `mp4`, `webm`, `mkv`, `flv`, `avi`, `mov`

### Audio Formats

- `mp3`, `aac`, `ogg`, `wav`, `flac`, `m4a`

### Special Options

- `bestvideo` - Best video only
- `bestaudio` - Best audio only
- `audio_only` - Audio only

## 🧪 Testing the API

### Using cURL

```bash
# Extract download links
curl -X POST http://127.0.0.1:5000/api/v1/get-download-links \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "720p"
  }'

# Extract video information
curl -X POST http://127.0.0.1:5000/api/v1/get-info \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'

# Extract subtitles
curl -X POST http://127.0.0.1:5000/api/v1/get-subtitles \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'

# Extract thumbnails
curl -X POST http://127.0.0.1:5000/api/v1/get-thumbnails \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'

# Health check
curl http://127.0.0.1:5000/health

# Supported formats
curl http://127.0.0.1:5000/api/v1/supported-formats
```

### Using Python

```python
import requests
import json

# Extract download links
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

## 🏗️ Project Structure

```
video-download-api/
├── app/
│   ├── routes/
│   │   └── video_routes.py      # API routes
│   ├── services/
│   │   └── video_service.py     # Video extraction logic
│   ├── utils/
│   │   └── logger.py            # Logging system
│   ├── db.py                    SD database configuration
│   ├── config.py                # Application configuration
│   └── __init__.py             # Application factory
├── main.py                      # Main entry point
├── requirements.txt             # Python requirements
├── README.md                    # This file
└── test.py                      # Test script
```

## ⚙️ Configuration

Customize the application via environment variables:

```bash
# Security settings
export SECRET_KEY="your-secret-key"

# Logger settings
export LOG_LEVEL="INFO"
export LOG_FILE="app.log"

# Database settings
export DATABASE_URL="sqlite:///requests.db"

# Rate limiting
export RATE_LIMIT_ENABLED="true"
export RATE_LIMIT_REQUESTS="10"
export RATE_LIMIT_WINDOW="60"
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

## 📊 Supported Platforms

The application supports over 1000 platforms, including:

- **YouTube** - Videos and playlists
- **Vimeo** - Public and private videos
- **Facebook** - Public videos
- **Instagram** - Videos and IGTV
- **Twitter** - Videos and GIFs
- **TikTok** - Short videos
- **Dailymotion** - Videos and playlists
- **Reddit** - Videos
- **Twitch** - Clips and live streams
- **SoundCloud** - Audio tracks
- **And many more**

## 🛠️ Troubleshooting

### Common Errors

1. **Invalid URL**

   ```json
   {
     "success": false,
     "error": "Invalid URL format"
   }
   ```

2. **Video Unavailable**

   ```json
   {
     "success": false,
     "error": "Video is unavailable"
   }
   ```

3. **Geo-Restricted**

   ```json
   {
     "success": false,
     "error": "Video is geo-restricted"
   }
   ```

4. **Unsupported Format**

   ```json
   {
     "success": false,
     "error": "Unsupported format"
   }
   ```

### Checking Logs

```bash
# View live logs
tail -f app.log

# Search for errors
grep "ERROR" app.log
```

## 🔒 Security

### Recommended Security Settings

1. **Use HTTPS in production**
2. **Set a strong SECRET_KEY**
3. **Enable rate limiting**
4. **Use a reverse proxy (Nginx)**
5. **Regularly update dependencies**

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a new feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 📞 Support

For help and inquiries:

- Open an issue on GitHub
- Contact the developer
- Review the documentation

## 🔄 Updates

- **v1.0.0** - Initial release
- Full support for video extraction
- Advanced logging system
- SQLite caching
- Subtitle and thumbnail extraction
- Organized and scalable structure

---

**Note:** This application is for educational and personal use. Please respect copyright and terms of service of various platforms.
