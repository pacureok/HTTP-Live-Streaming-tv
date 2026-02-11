import os
import requests
from flask import Flask, jsonify, render_template_string, request, Response

app = Flask(__name__)

# Fuentes de canales reales (IPTV-org)
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/spa.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u"
]

def buscar_url_real(keyword):
    """Busca en las listas M3U la URL directa del canal"""
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            lines = r.text.splitlines()
            for i, line in enumerate(lines):
                if "#EXTINF" in line and keyword.upper() in line.upper():
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("http"):
                            return lines[j].strip()
        except Exception as e:
            print(f"Error buscando en fuente: {e}")
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
    return jsonify({"error": "Señal no encontrada en las listas públicas"}), 404

# --- PROXY PARA EVITAR BLOQUEO DE CORS ---
@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Falta URL", 400
    try:
        # Pedimos el archivo m3u8 simulando ser un navegador
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, stream=True, timeout=10)
        
        # Reenviamos el contenido con los headers de CORS abiertos
        resp = Response(r.content, status=r.status_code)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
        return resp
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- INTERFAZ HTML/JS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Stream Center Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        body { background: #050505; color: white; font-family: sans-serif; text-align: center; margin: 0; }
        .player-container { width: 100%; max-width: 850px; margin: 20px auto; background: #000; aspect-ratio: 16/9; border: 2px solid #222; }
        video { width: 100%; height: 100%; }
        .controls { padding: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; max-width: 850px; margin: auto; }
        .btn { background: #1a1a1a; color: white; border: 1px solid #333; padding: 15px; cursor: pointer; border-radius: 5px; font-weight: bold; }
        .btn:hover { background: #ff0000; border-color: #ff0000; }
        .status { color: #888; font-size: 0.9em; margin-bottom: 10px; }
        .test-btn { background: #222; color: #00ff00; border: 1px solid #00ff00; }
    </style>
</head>
<body>
    <h1 style="color:#ff0000; letter-spacing:2px;">LIVE SPORTS CENTER</h1>
    <div class="player-container">
        <video id="video" controls autoplay></video>
    </div>
    <div id="status" class="status">Listo para transmitir</div>
    
    <div class="controls">
        <button class="btn" onclick="conectarCanal('FOX SPORTS')">FOX SPORTS</button>
        <button class="btn" onclick="conectarCanal('ESPN')">ESPN</button>
        <button class="btn" onclick="conectarCanal('TYC')">TYC SPORTS</button>
        <button class="btn" onclick="conectarCanal('GOL')">GOL TV</button>
        <button class="btn test-btn" onclick="probarReproductor()">TEST (Verificar Player)</button>
    </div>

    <script>
        const video = document.getElementById('video');
        const status = document.getElementById('status');
        const hls = new Hls();

        function playHLS(url) {
            // Usamos nuestro proxy para saltar el CORS
            const proxyUrl = `/proxy?url=` + encodeURIComponent(url);
            
            if (Hls.isSupported()) {
                hls.loadSource(proxyUrl);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, () => video.play());
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = proxyUrl;
                video.play();
            }
        }

        async function conectarCanal(nombre) {
            status.innerText = "Buscando señal para " + nombre + "...";
            try {
                const response = await fetch(`/get_stream?canal=${nombre}`);
                const data = await response.json();
                if (data.url) {
                    status.innerText = "Canal encontrado. Conectando...";
                    playHLS(data.url);
                } else {
                    status.innerText = "No hay señales libres de " + nombre + " ahora.";
                }
            } catch (e) {
                status.innerText = "Error de servidor.";
            }
        }

        function probarReproductor() {
            status.innerText = "Probando motor de video...";
            const testStream = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8";
            if (Hls.isSupported()) {
                hls.loadSource(testStream);
                hls.attachMedia(video);
                video.play();
            }
        }
    </script>
</body>
</html>
"""
