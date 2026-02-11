import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Base de datos de canales de confianza (Fuentes legales/abiertas)
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/spa.m3u", # Canales en español
    "https://iptv-org.github.io/iptv/categories/sports.m3u" # Deportes global
]

def buscar_canal(nombre_canal):
    """
    Busca la URL m3u8 más reciente en los agregadores públicos.
    """
    for source in SOURCES:
        try:
            response = requests.get(source, timeout=5)
            lines = response.text.splitlines()
            for i, line in enumerate(lines):
                if nombre_canal.upper() in line.upper():
                    # La siguiente línea después de #EXTINF suele ser la URL
                    return lines[i+1]
        except Exception as e:
            print(f"Error buscando en {source}: {e}")
    return None

@app.route('/get_stream/<channel_name>')
def get_stream(channel_name):
    url = buscar_canal(channel_name)
    if url:
        return jsonify({"status": "success", "url": url})
    return jsonify({"status": "error", "message": "Canal no encontrado o token expirado"}), 404

# HTML embebido para que Render lo sirva directamente
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = """
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    
