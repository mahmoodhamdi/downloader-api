
# 🎥 Video Direct Link Extractor API

API built with Flask to extract direct download links from YouTube or other supported platforms using `yt-dlp`.

## 🚀 Features

- Supports single videos or playlists.
- Returns video title, duration, and all available formats.
- No actual downloading on the server (skip download).
- Ready to add authentication or rate limiting in future.

## 🗂 Project Structure

```structure

app/
routes/
services/
utils/
config.py
**init**.py
main.py
requirements.txt
README.md

````

## ⚙️ Setup

```bash
# Clone repo
git clone <repo-url>
cd your_project

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
````

Server will run on: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 📡 API Usage

### Endpoint

```code
POST /get-download-links
```

### Request JSON

```json
{
  "url": "https://www.youtube.com/watch?v=xxxx",
  "format": "best"
}
```

### Example Curl

```bash
curl -X POST http://127.0.0.1:5000/get-download-links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxxx", "format": "best"}'
```

### Response (Single Video)

```json
{
  "success": true,
  "is_playlist": false,
  "video": {
    "title": "Example Title",
    "duration": "05:30",
    "formats": [
      {
        "format_id": "22",
        "format_note": "720p",
        "ext": "mp4",
        "filesize": 50332672,
        "url": "https://...."
      }
    ]
  }
}
```

## 💬 Notes

- The API only extracts links (skip\_download), no actual file downloads.
- Future improvements: auth, rate limiting, caching.
