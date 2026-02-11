import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Lista pública de canales (IPTV-org)
M3U_SOURCE = "https://iptv-org.github.io/iptv/languages/spa.m3u"

@app.route('/')
def home():
    return "Servidor de Streaming Activo. Usa /lista para ver canales."

@app.route('/lista')
def obtener_lista():
    try:
        r = requests.get(M3U_SOURCE, timeout=10)
        # Filtramos solo canales que contengan "Fox" o "Sport"
        lineas = r.text.splitlines()
        canales = []
        for i, linea in enumerate(lineas):
            if "#EXTINF" in linea and ("FOX" in linea.upper() or "SPORT" in linea.upper()):
                canales.append({
                    "nombre": linea.split(",")[-1],
                    "url": lineas[i+1]
                })
        return jsonify(canales)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render usa la variable 'PORT', si no existe, usa el 5000 por defecto
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
    
