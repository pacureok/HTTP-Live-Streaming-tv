import os
import requests
import re
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Fuentes de canales reales (IPTV-org y otros agregadores)
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/spa.m3u",
    "https://iptv-org.github.io/iptv/index.m3u"
]

def buscar_url_real(keyword):
    """Busca en las listas M3U la URL directa del canal"""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=5)
            lines = r.text.splitlines()
            for i, line in enumerate(lines):
                # Buscamos coincidencia en el nombre del canal
                if "#EXTINF" in line and keyword.upper() in line.upper():
                    # La URL real es la siguiente línea que no sea un comentario
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("http"):
                            return lines[j]
        except:
            continue
    return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_stream')
def get_stream():
    canal = request.args.get('canal', 'FOX')
    url_directa = buscar_url_real(canal)
    if url_directa:
        return jsonify({"url": url_directa})
    return jsonify({"error": "No se encontró señal activa"}), 404

# --- INTERFAZ REAL ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Sports Real</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; text-align: center; margin: 0; }
        .video-box { width: 100%; max-width: 800px; margin: auto; aspect-ratio: 16/9; background: #111; }
        video { width: 100%; height: 100%; }
        .menu { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; padding: 20px; }
        .btn { background: #333; border: 1px solid #444; color: #fff; padding: 12px 20px; cursor: pointer; border-radius: 4px; }
        .btn:hover { background: #ff0000; }
        #status { color: #555; font-size: 0.8em; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="video-box">
        <video id="video" controls></video>
    </div>
    <p id="status">Selecciona un canal para conectar...</p>
    <div class="menu">
        <button class="btn" onclick="cargarCanal('FOX SPORTS')">FOX SPORTS</button>
        <button class="btn" onclick="cargarCanal('ESPN')">ESPN</button>
        <button class="btn" onclick="cargarCanal('TYC')">TYC SPORTS</button>
        <button class="btn" onclick="cargarCanal('DIRECTV')">DSports</button>
    </div>

    <script>
        const video = document.getElementById('video');
        const status = document.getElementById('status');
        const hls = new Hls();

        async function cargarCanal(nombre) {
            status.innerText = "Buscando señal real para " + nombre + "...";
            try {
                const response = await fetch(`/get_stream?canal=${nombre}`);
                const data = await response.json();
                
                if (data.url) {
                    status.innerText = "Conectado a: " + data.url;
                    if (Hls.isSupported()) {
                        hls.loadSource(data.url);
                        hls.attachMedia(video);
                        hls.on(Hls.Events.MANIFEST_PARSED, () => video.play());
                    } else {
                        video.src = data.url;
                        video.play();
                    }
                } else {
                    status.innerText = "Error: Señal no encontrada actualmente.";
                }
            } catch (e) {
                status.innerText = "Error de conexión con el servidor.";
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
