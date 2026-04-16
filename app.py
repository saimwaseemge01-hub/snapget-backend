from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os

# Folder paths setup
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder=base_dir, static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(base_dir, 'index.html')

@app.route('/api/download', methods=['POST'])
def get_video_info():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"success": False, "error": "URL missing!"}), 400

    # Cookies file path
    cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # Agar cookies.txt file hai toh use karein
        'cookiefile': cookie_path if os.path.exists(cookie_path) else None,
        # Advanced Headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Direct link nikalne ka logic
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                # Filter for direct mp4 links
                valid_links = [f for f in info['formats'] if f.get('url') and 'manifest' not in f['url']]
                download_url = valid_links[-1]['url'] if valid_links else None

            if not download_url:
                return jsonify({"success": False, "error": "Could not find a direct download link."}), 404

            return jsonify({
                "success": True,
                "title": info.get('title', 'SnapGet_Video'),
                "thumbnail": info.get('thumbnail'),
                "download_url": download_url,
                "platform": info.get('extractor_key')
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 SnapGet Server is Live on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    # '0.0.0.0' public hosting ke liye zaroori hai
    # os.environ.get('PORT') hosting provider ka port uthayega
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)