from flask import Flask, render_template
import requests

app = Flask(__name__)

# Aquí es donde ocurre la magia técnica
# Buscas listas M3U8 de fuentes abiertas (IPTV-ORG)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
