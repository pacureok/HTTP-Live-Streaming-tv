import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# --- CONFIGURACIÓN DE INTERFAZ (HTML/CSS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream Center Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        body { background: #0a0a0a; color: white; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; }
        header { background: #1a1a1a; width: 100%; padding: 15px 0; text-align: center; border-bottom: 2px solid #cc0000; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { margin: 0; color: #cc0000; font-size: 1.5rem; letter-spacing: 2px; }
        .video-container { width: 95%; max-width: 900px; margin: 20px 0; background: #000; border-radius: 8px; overflow: hidden; aspect-ratio: 16/9; box-shadow: 0 0 20px rgba(204, 0, 0, 0.2); }
        video { width: 100%; height: 100%; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; width: 95%; max-width: 900px; padding: 20px; }
        .btn { background: #1e1e1e; border: 1px solid #333; color: white; padding: 15px; border-radius: 5px; cursor: pointer; transition: 0.3s; font-weight: bold; text-align: center; }
        .btn:hover { background: #cc0000; border-color: #ff0000; transform: translateY(-3px); }
        .btn.active { background: #cc0000; box-shadow: 0 0 10px #ff0000; }
    </style>
</head>
<body>
    <header><h1>CONTROL CENTER</h1></header>
    
    <div class="video-container">
        <video id="video" controls autoplay></video>
    </div>

    <div class="grid" id="menu">
        <div class="btn" onclick="playStream('https://iptv-org.github.io/iptv/countries/ar.m3u', 'FOX')">FOX SPORTS</div>
        <div class="btn" onclick="playStream('https://iptv-org.github.io/iptv/languages/spa.m3u', 'ESPN')">ESPN (Search)</div>
        <div class="btn" onclick="playStream('https://iptv-org.github.io/iptv/categories/sports.m3u', 'BEIN')">BEIN SPORTS</div>
        <div class="btn" onclick="location.reload()">REFRESCAR LISTA</div>
    </div>

    <script>
        const video = document.getElementById('video');
        const hls = new Hls();

        function playStream(playlistUrl, filter) {
            // En una app real, aquí llamaríamos a nuestra API /get_stream
            // Por ahora simulamos la carga de una señal genérica de deportes
            const testStream = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"; 
            
            if (Hls.isSupported()) {
                hls.loadSource(testStream);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, () => video.play());
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = testStream;
                video.addEventListener('loadedmetadata', () => video.play());
            }
        }
    </script>
</body>
</html>
"""

# --- RUTAS DE FLASK ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return jsonify({"status": "online"}), 200

if __name__ == "__main__":
    # Importante: Render inyecta el puerto en la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
