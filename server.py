import subprocess
import threading
import json
import os
import re
import sys
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytubefix
from pytubefix import YouTube

# --- Initialization ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YT_DOWNLOADER_DIR = os.path.join(BASE_DIR, 'YTDownloader')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

app = Flask(__name__, static_folder=BASE_DIR, template_folder=BASE_DIR)
CORS(app)

def load_config():
    # Ensure config file exists with defaults
    if not os.path.exists(CONFIG_FILE):
        defaults = {
            "output_path": os.path.join(os.path.expanduser("~"), "Videos", "YT-Downloads"),
            "browser": "chrome",
            "engine": "yt-dlp",
            "cookies_path": os.path.join(YT_DOWNLOADER_DIR, "cookies.txt")
        }
        save_config(defaults)
        return defaults
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {
            "output_path": os.path.join(os.path.expanduser("~"), "Videos", "YT-Downloads"),
            "browser": "chrome",
            "engine": "yt-dlp"
        }

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# --- Global State ---
download_progress = {}
active_processes = {}
oauth_status = {"url": None, "code": None, "status": "idle"}

def oauth_verifier(url, code):
    global oauth_status
    oauth_status = {"url": url, "code": code, "status": "waiting"}
    print(f"OAuth code generated: {code} at {url}")

def run_download(task_id, url, quality, output_path, cookies_path):
    os.makedirs(output_path, exist_ok=True)
    output_template = os.path.join(output_path, '%(title)s.%(ext)s')
    
    cmd = [
        "yt-dlp",
        "--remote-components", "ejs:github",
        "--newline",
        "--no-playlist",
        "--retries", "10",
        "--fragment-retries", "10",
        "--no-check-certificates",
        "--prefer-free-formats",
    ]

    if quality == 'audio':
        cmd += ['-x', '--audio-format', 'mp3', '--audio-quality', '0']
    else:
        if quality == '1080':
            fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best"
        elif quality == '720':
            fmt = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best"
        elif quality == '480':
            fmt = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best"
        else:
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio"

        cmd += [
            "--format", fmt,
            "--merge-output-format", "mp4",
            "--postprocessor-args", "ffmpeg:-c:v copy -c:a aac -b:a 192k",
        ]

    if cookies_path and os.path.exists(cookies_path):
        cmd += ["--cookies", cookies_path]
    else:
        config = load_config()
        cmd += ["--cookies-from-browser", config.get('browser', 'chrome')]

    # Enhanced yt-dlp arguments to bypass bot detection
    cmd += [
        "--extractor-args", "youtube:player_client=ios,android,web",
        "--add-header", "Accept-Language:en-US,en;q=0.9",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "--output", output_template,
        url
    ]

    download_progress[task_id] = {
        'status': 'downloading', 'percent': 0, 'speed': '', 'eta': '', 'filename': '', 'log': []
    }

    try:
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, encoding='utf-8', errors='replace', startupinfo=startupinfo
        )
        active_processes[task_id] = proc
        
        for line in proc.stdout:
            line = line.strip()
            if not line: continue
            download_progress[task_id]['log'].append(line)
            
            m = re.search(r'\[download\]\s+([\d\.]+)%\s+of\s+[\d\.]+\w+\s+at\s+([\d\.\w/]+)\s+ETA\s+(\S+)', line)
            if m:
                download_progress[task_id]['percent'] = float(m.group(1))
                download_progress[task_id]['speed'] = m.group(2)
                download_progress[task_id]['eta'] = m.group(3)

            m2 = re.search(r'\[(?:download|Merger)\].*Destination:\s+(.+)', line)
            if m2:
                download_progress[task_id]['filename'] = os.path.basename(m2.group(1))

        proc.wait()
        if task_id in active_processes: del active_processes[task_id]

        if proc.returncode == 0:
            download_progress[task_id]['status'] = 'done'
            download_progress[task_id]['percent'] = 100
        else:
            if download_progress[task_id]['status'] != 'stopped':
                download_progress[task_id]['status'] = 'error'
                err_msg = f'Exit code {proc.returncode}.'
                log_text = "".join(download_progress[task_id]['log'])
                if "Sign in" in log_text or "bot" in log_text.lower():
                    err_msg = "YouTube blocked the request. Try clicking 'Fix Connection' or use a different quality."
                elif "Video unavailable" in log_text:
                    err_msg = "Video unavailable (Private, Deleted, or Region-locked)."
                else:
                    # Try to find the last line starting with ERROR:
                    for line in reversed(download_progress[task_id]['log']):
                        if "ERROR:" in line:
                            err_msg = line.split("ERROR:")[1].strip()
                            break
                download_progress[task_id]['error'] = err_msg
    except Exception as e:
        download_progress[task_id]['status'] = 'error'
        download_progress[task_id]['error'] = str(e)

def run_download_pytubefix(task_id, url, quality, output_path):
    os.makedirs(output_path, exist_ok=True)
    download_progress[task_id] = {
        'status': 'downloading', 'percent': 0, 'speed': 'N/A', 'eta': 'N/A', 'filename': '', 'log': ["Starting pytubefix (OAuth mode)..."]
    }
    
    try:
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        download_progress[task_id]['filename'] = yt.title
        
        if quality == 'audio':
            stream = yt.streams.get_audio_only()
        else:
            # For simplicity, we get the highest progressive stream (usually 720p)
            # or the highest resolution available. 
            # Note: 1080p+ requires manual merging with ffmpeg in pytubefix.
            if quality == '1080':
                stream = yt.streams.filter(res="1080p", file_extension='mp4').first() or yt.streams.get_highest_resolution()
            elif quality == '720':
                stream = yt.streams.get_by_resolution("720p") or yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.get_highest_resolution()
        
        def on_progress(stream, chunk, bytes_remaining):
            total = stream.filesize
            downloaded = total - bytes_remaining
            pct = (downloaded / total) * 100
            download_progress[task_id]['percent'] = round(pct, 1)

        yt.register_on_progress_callback(on_progress)
        out_file = stream.download(output_path=output_path)
        
        download_progress[task_id]['status'] = 'done'
        download_progress[task_id]['percent'] = 100
        download_progress[task_id]['log'].append(f"Saved to: {out_file}")
        
    except Exception as e:
        download_progress[task_id]['status'] = 'error'
        download_progress[task_id]['error'] = str(e)
        download_progress[task_id]['log'].append(f"Error: {str(e)}")

# --- Routes ---

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        config = load_config()
        if 'output_path' in data:
            config['output_path'] = data['output_path']
        save_config(config)
        return jsonify({'ok': True, 'config': config})
    return jsonify(load_config())

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    if not url: return jsonify({'error': 'No URL provided'}), 400

    config = load_config()
    quality = data.get('quality', 'best')
    output_path = data.get('output_path') or config.get('output_path')
    
    # Force save the output path if provided
    if output_path and output_path != config.get('output_path'):
        config['output_path'] = output_path
        save_config(config)

    engine = data.get('engine') or config.get('engine', 'yt-dlp')
    task_id = str(int(time.time() * 1000))
    
    if engine == 'pytubefix':
        t = threading.Thread(target=run_download_pytubefix, args=(task_id, url, quality, output_path), daemon=True)
    else:
        t = threading.Thread(target=run_download, args=(task_id, url, quality, output_path, config.get('cookies_path')), daemon=True)
    
    t.start()
    return jsonify({'task_id': task_id})

@app.route('/api/login', methods=['POST'])
def start_login():
    global oauth_status
    oauth_status = {"url": None, "code": None, "status": "starting"}
    
    def run_login():
        global oauth_status
        try:
            from pytubefix.innertube import InnerTube
            # Direct InnerTube call is more reliable for triggering OAuth
            it = InnerTube(client='TV', use_oauth=True, allow_cache=True, oauth_verifier=oauth_verifier)
            # This forces the OAuth fetch flow
            try:
                it.player("aqz-KE-bpKQ")
            except:
                pass # We only care about the verifier being called
            
            if oauth_status['status'] == 'waiting':
                # This part will be reached only after the verifier returns
                # or if the token was already cached.
                oauth_status['status'] = 'success'
        except Exception as e:
            print(f"Login error: {e}")
            oauth_status['status'] = 'error'
            oauth_status['error'] = str(e)

    threading.Thread(target=run_login, daemon=True).start()
    return jsonify({'ok': True})

@app.route('/api/login_status')
def get_login_status():
    return jsonify(oauth_status)

@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    if task_id not in download_progress: return jsonify({'error': 'Task not found'}), 404
    return jsonify(download_progress[task_id])

@app.route('/api/open_folder', methods=['POST'])
def open_folder():
    data = request.get_json(silent=True) or {}
    config = load_config()
    path = data.get('path') or config.get('output_path', '')
    path = os.path.normpath(os.path.abspath(path))
    
    if not os.path.exists(path):
        # If it doesn't exist, try to create it or just open parent
        try: os.makedirs(path, exist_ok=True)
        except: pass

    if os.path.exists(path):
        if sys.platform == 'win32':
            if os.path.isfile(path):
                subprocess.Popen(f'explorer /select,"{path}"')
            else:
                os.startfile(path)
        else:
            subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', path])
        return jsonify({'ok': True})
    return jsonify({'error': f'Could not open: {path}'}), 400

@app.route('/api/fix_connection', methods=['POST'])
def fix_connection():
    try:
        # Clear yt-dlp cache
        subprocess.run(["yt-dlp", "--clear-cache"], check=True, startupinfo=subprocess.STARTUPINFO() if sys.platform == 'win32' else None)
        return jsonify({'ok': True, 'message': 'Cache cleared. Try downloading again.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"\n  YT Downloader running at: http://localhost:5050\n")
    app.run(port=5050, debug=False)

