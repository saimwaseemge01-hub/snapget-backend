from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)

# CORS ko properly configure kiya hai taaki localhost aur production dono chalein
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "SnapGet API is working"}), 200

@app.route('/api/download', methods=['POST'])
def get_video_info():
    # 1. Request Validation
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({"success": False, "error": "Please provide a video URL"}), 400

    # 2. Cookies Setup
    # Files move karne ke baad cookies root par honi chahiye
    cookie_path = os.path.join(os.getcwd(), 'cookies.txt')

    # 3. YT-DLP Options (Optimized for Serverless)
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'cookiefile': cookie_path if os.path.exists(cookie_path) else None,
        'socket_timeout': 10, # Serverless functions ke liye zaroori hai
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info process
            info = ydl.extract_info(video_url, download=False)
            
            # Direct MP4 link nikalne ka logic
            download_url = info.get('url')
            
            # Agar direct link na mile toh formats mein filter karein
            if not download_url and 'formats' in info:
                # Sirf wo links uthayen jo direct video ho (m3u8/manifest na ho)
                valid_formats = [
                    f for f in info['formats'] 
                    if f.get('url') and 'manifest' not in f['url'] and f.get('ext') == 'mp4'
                ]
                if valid_formats:
                    # Best quality mp4 uthayen
                    download_url = valid_formats[-1]['url']

            if not download_url:
                return jsonify({"success": False, "error": "Direct download link not found"}), 404

            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "download_url": download_url,
                "platform": info.get('extractor_key')
            }), 200

    except Exception as e:
        error_msg = str(e)
        # Shorten error message for response
        if "Sign in to confirm" in error_msg:
            error_msg = "YouTube blocked this request. Please update cookies.txt"
        
        return jsonify({"success": False, "error": error_msg}), 500

# Vercel ko ye line chahiye hoti hai
app = app

if __name__ == '__main__':
    app.run(debug=True)