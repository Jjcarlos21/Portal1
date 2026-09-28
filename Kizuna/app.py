import os
import time
import sqlite3
import requests

from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify, render_template, send_from_directory, send_file, request

from auth import init_auth
from blueprint_noticias import admin_noticias_bp, init_db_noticias
from blueprint_directorio import admin_directorio_bp, init_db_directorio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# Login compartido: registra /login y /logout directo sobre esta app
init_auth(app)

# Los dos paneles admin, cada uno bajo su propio prefijo
app.register_blueprint(admin_noticias_bp, url_prefix="/admin/noticias")
app.register_blueprint(admin_directorio_bp, url_prefix="/admin/directorio")

# Crea las tablas si hace falta. Esto se ejecuta al IMPORTAR el módulo
# (no solo con `python app.py`), para que funcione igual bajo un
# servidor WSGI como el de PythonAnywhere.
init_db_noticias()
init_db_directorio()

DB_PATH = os.path.join(BASE_DIR, "data", "kizuna.db")
MEXT_DOCS_DIR = os.path.join(BASE_DIR, "static", "mext-docs")

# --- FUNCIONES AUXILIARES DE BASE DE CONOCIMIENTO ---
def cargar_documentos_mext():
    """Lee dinámicamente todos los archivos .txt y .md en /static/mext-docs/."""
    contenido_acumulado = ""
    if os.path.exists(MEXT_DOCS_DIR):
        for root, _, files in os.walk(MEXT_DOCS_DIR):
            for file in files:
                if file.endswith(('.txt', '.md')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            contenido_acumulado += f"\n--- DOCUMENTO: {file} ---\n"
                            contenido_acumulado += f.read() + "\n"
                    except Exception as e:
                        print(f"Error al leer {file}: {e}")
    return contenido_acumulado

def obtener_contexto_bd():
    """Extrae las noticias activas y registros del directorio desde kizuna.db."""
    contexto = ""
    if not os.path.exists(DB_PATH):
        return contexto

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Noticias activas
        cursor.execute("SELECT titulo, texto, autor, fecha_inicio FROM noticias WHERE activo = 1 ORDER BY id DESC LIMIT 5")
        noticias = cursor.fetchall()
        if noticias:
            contexto += "\n--- ÚLTIMAS NOTICIAS EN VENEZUELA ---\n"
            for n in noticias:
                contexto += f"• [{n['fecha_inicio']}] {n['titulo']}: {n['texto']} (Autor: {n['autor']})\n"

        # 2. Directorio de dojos / institutos
        cursor.execute("SELECT Nombre, Estado, Ciudad, Responsable, Email, Direccion FROM directorio LIMIT 15")
        directorio = cursor.fetchall()
        if directorio:
            contexto += "\n--- DIRECTORIO CULTURAL Y ACADEMIAS ---\n"
            for d in directorio:
                contexto += f"• {d['Nombre']} | Ciudad: {d['Ciudad']}, {d['Estado']} | Contacto: {d['Responsable']} ({d['Email']}) | Dirección: {d['Direccion']}\n"

        conn.close()
    except Exception as e:
        print(f"Error al consultar la BD SQLite: {e}")

    return contexto

# --- ENDPOINT DEL CHATBOT CON PROXY A GEMINI ---
@app.route("/api/chat", methods=["POST"])
def chat_proxy():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "No se ha configurado la variable GEMINI_API_KEY en el servidor."}), 500

    data = request.json or {}
    messages_history = data.get("contents", [])

    documentos_mext = cargar_documentos_mext()
    contexto_bd = obtener_contexto_bd()

    system_instruction = f"""Eres el asistente virtual oficial de **Kizuna Venezuela**, el portal especializado en cultura japonesa y Becas MEXT en Venezuela.

Tu objetivo es guiar a los usuarios con información precisa basada exclusivamente en los siguientes recursos actualizados:

=== INFORMACIÓN EN TIEMPO REAL (BASE DE DATOS KIZUNA.DB) ===
{contexto_bd}

=== CONOCIMIENTO DETALLADO DE BECAS MEXT (DOCUMENTOS MEXT) ===
{documentos_mext}

INSTRUCCIONES DE RESPUESTA:
1. Responde en español, con un tono amable, claro y servicial.
2. Usa listas de viñetas y negritas para mejorar la legibilidad.
3. Si la pregunta requiere información no presente en las fuentes de arriba, indícalo educadamente e invita al usuario a revisar el portal.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"

    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": messages_history,
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024
        }
    }

    max_intentos = 3
    tiempo_espera = 1.5  # segundos de espera inicial

    for intento in range(max_intentos):
        try:
            response = requests.post(url, json=payload, timeout=25)
            res_data = response.json()

            if response.status_code == 200:
                return jsonify(res_data), 200

            # Si el modelo reporta alta demanda / saturación temporal (429, 503, 539)
            if response.status_code in (429, 503, 539):
                if intento < max_intentos - 1:
                    print(f"[WARN] Alta demanda en Gemini API. Reintentando en {tiempo_espera}s... (Intento {intento + 1}/{max_intentos})")
                    time.sleep(tiempo_espera)
                    tiempo_espera *= 2  # Duplica la espera para dar tiempo al servidor
                    continue

            # Si es otro tipo de error (clave inválida, mal formato, etc.)
            msg_error = res_data.get("error", {}).get("message", "Error en Gemini API")
            return jsonify({"error": msg_error}), response.status_code

        except Exception as e:
            # Se registra el detalle solo en el log del servidor: el mensaje de
            # error de "requests" suele incluir la URL completa de la petición,
            # y esa URL lleva la GEMINI_API_KEY. Nunca debe llegar al cliente.
            print(f"[ERROR] Fallo al contactar Gemini: {e}")
            if intento < max_intentos - 1:
                time.sleep(tiempo_espera)
                tiempo_espera *= 2
                continue
            return jsonify({"error": "Error de conexión con el servidor. Intenta de nuevo en unos segundos."}), 500

    return jsonify({"error": "Los servidores de Google tienen alta demanda en este momento. Por favor, intenta enviar tu mensaje nuevamente en unos segundos."}), 539

# --- RUTAS DE ARCHIVOS ESTÁTICOS Y BD ---
@app.route("/data/<path:filename>")
def serve_data_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "data"), filename)

@app.route("/static/mext-docs/<path:filename>")
def serve_mext_docs(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static", "mext-docs"), filename)

@app.route("/api/noticias", methods=["GET"])
def api_obtener_noticias():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, texto, imagen, autor, url_post, fecha_inicio, fecha_fin FROM noticias WHERE activo = 1 ORDER BY id DESC")
        filas = cursor.fetchall()
        conn.close()
        return jsonify([dict(fila) for fila in filas])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/fondo_pagina.png")
def serve_fondo():
    posibles_rutas = [
        os.path.join(BASE_DIR, "fondo_pagina.png"),
        os.path.join(BASE_DIR, "static", "fondo_pagina.png"),
        os.path.join(BASE_DIR, "static", "images", "fondo_pagina.png"),
        os.path.join(BASE_DIR, "static", "img", "fondo_pagina.png"),
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return send_file(ruta)
    return "Imagen no encontrada", 404

@app.route("/chatbot.js")
def serve_chatbot():
    return send_from_directory(os.path.join(BASE_DIR, "static", "js"), "chatbot.js")

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/<path:page_name>")
def render_page(page_name):
    if not page_name.endswith(".html"):
        page_name += ".html"
    return render_template(page_name)

if __name__ == "__main__":
    print("Servidor Kizuna iniciado en http://127.0.0.1:5000")
    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)
