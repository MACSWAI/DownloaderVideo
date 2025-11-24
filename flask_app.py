from flask import Flask, render_template, request, jsonify
import yt_dlp
import logging

# ==========================================
# KONFIGURASI
# ==========================================
# Set ke True jika Anda pakai akun GRATIS PythonAnywhere 
# supaya bisa melihat tampilan UI tanpa error 403.
# Set ke False jika Anda sudah Upgrade Akun / Pindah ke Render.
MOCK_MODE = True  

app = Flask(__name__, template_folder='Vdown')
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'status': 'error', 'message': 'URL tidak boleh kosong'}), 400

    # --- LOGIKA MODE TEST (Untuk Akun Gratis) ---
    if MOCK_MODE:
        import time
        time.sleep(1.5) # Pura-pura loading
        return jsonify({
            'status': 'success',
            'data': {
                'title': '[TEST MODE] Video Keren Banget',
                'thumbnail': 'https://via.placeholder.com/640x360.png?text=Test+Thumbnail',
                'duration': '05:30',
                'platform': 'YouTube (Simulation)',
                'view_count': '1,234,567',
                'download_url': '#'
            }
        })

    # --- LOGIKA ASLI (Yt-dlp) ---
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        # Header palsu agar tidak dianggap bot
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Format durasi
            duration = info.get('duration_string') or "N/A"
            
            # Format angka views
            views = "{:,}".format(info.get('view_count', 0))

            video_data = {
                'title': info.get('title', 'Video Tanpa Judul'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': duration,
                'platform': info.get('extractor_key', 'Unknown'),
                'view_count': views,
                'download_url': info.get('url', '') # Direct Link dari server YouTube
            }
            
        return jsonify({'status': 'success', 'data': video_data})

    except Exception as e:
        app.logger.error(f"Error yt-dlp: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Gagal mengambil data. Pastikan URL benar atau server diizinkan akses.'}), 500

if __name__ == '__main__':
    app.run(debug=True)