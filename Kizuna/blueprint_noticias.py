"""
Panel administrativo de NOTICIAS, convertido de app Flask independiente
a Blueprint para que pueda vivir dentro de una sola aplicación (necesario
para el plan gratis de PythonAnywhere, que solo permite una app web).

Cambios respecto al admin_noticias.py original:
- Flask(__name__) -> Blueprint("admin_noticias", __name__)
- @app.route(...) -> @admin_noticias_bp.route(...)
- Todos los url_for('index'), url_for('nueva_noticia'), etc. ahora llevan
  el prefijo del blueprint: url_for('admin_noticias.index'), etc.
  url_for('login') / url_for('logout') NO llevan prefijo porque el login
  se registra directo sobre la app principal (ver app.py).
- init_db() -> init_db_noticias() (nombre único, se llama desde app.py)
- Se quitó el endpoint /api/noticias (estaba duplicado: app.py ya expone
  esa misma información en /api/noticias).
- Ya no tiene bloque `if __name__ == "__main__":` ni su propio waitress:
  este archivo ya no se ejecuta solo, se importa desde app.py.
"""

import os
import sqlite3
from flask import Blueprint, redirect, render_template_string, request, url_for
from auth import login_required

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "kizuna.db")

admin_noticias_bp = Blueprint("admin_noticias", __name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_noticias():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            texto TEXT,
            autor TEXT,
            imagen TEXT,
            url_post TEXT,
            fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_fin DATETIME,
            activo INTEGER DEFAULT 1
        )
    """
    )
    conn.commit()
    conn.close()


HTML_ADMIN_NOTICIAS = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Gestión de Noticias - Kizuna Venezuela</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f6f9; color: #333; }
    h1, h2 { color: #2c3e50; }
    .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .btn-logout { color: #e74c3c; text-decoration: none; font-weight: bold; }
    .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .form-group { margin-bottom: 12px; }
    label { display: block; font-weight: bold; margin-bottom: 5px; }
    input[type="text"], input[type="url"], textarea { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
    textarea { height: 80px; }
    .btn { padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
    .btn-primary { background-color: #3498db; color: white; }
    .btn-danger { background-color: #e74c3c; color: white; }
    .btn-warning { background-color: #f39c12; color: white; }
    table { width: 100%; border-collapse: collapse; background: white; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background-color: #ecf0f1; }
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
    .badge-active { background-color: #2ecc71; color: white; }
    .badge-inactive { background-color: #95a5a6; color: white; }
  </style>
</head>
<body>

  <div class="header-bar">
    <h1>Gestión del Carrusel de Noticias</h1>
    <a href="{{ url_for('logout') }}" class="btn-logout">🔒 Cerrar Sesión</a>
  </div>

  <div class="card">
    <h2>{% if noticia %}Editar Noticia #{{ noticia['id'] }}{% else %}Nueva Noticia{% endif %}</h2>
    <form method="POST" action="{% if noticia %}{{ url_for('admin_noticias.editar_noticia', id=noticia['id']) }}{% else %}{{ url_for('admin_noticias.nueva_noticia') }}{% endif %}">
      <div class="form-group">
        <label>Título:</label>
        <input type="text" name="titulo" value="{{ noticia['titulo'] if noticia else '' }}" required>
      </div>
      <div class="form-group">
        <label>Texto / Resumen:</label>
        <textarea name="texto">{{ noticia['texto'] if noticia else '' }}</textarea>
      </div>
      <div class="form-group">
        <label>Autor / Fuente:</label>
        <input type="text" name="autor" value="{{ noticia['autor'] if noticia else '' }}">
      </div>
      <div class="form-group">
        <label>URL de Imagen (ej: static/img/noticia1.jpg):</label>
        <input type="text" name="imagen" value="{{ noticia['imagen'] if noticia else '' }}">
      </div>
      <div class="form-group">
        <label>URL del enlace (opcional):</label>
        <input type="url" name="url_post" value="{{ noticia['url_post'] if noticia else '' }}">
      </div>
      <button type="submit" class="btn btn-primary">Guardar Noticia</button>
      {% if noticia %}
        <a href="{{ url_for('admin_noticias.index') }}" class="btn">Cancelar</a>
      {% endif %}
    </form>
  </div>

  <div class="card">
    <h2>Noticias Registradas</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Título</th>
          <th>Autor</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {% for item in noticias %}
        <tr>
          <td>{{ item['id'] }}</td>
          <td><strong>{{ item['titulo'] }}</strong></td>
          <td>{{ item['autor'] or 'N/A' }}</td>
          <td>
            {% if item['activo'] == 1 %}
              <span class="badge badge-active">Activa</span>
            {% else %}
              <span class="badge badge-inactive">Inactiva</span>
            {% endif %}
          </td>
          <td>
            <a href="{{ url_for('admin_noticias.cambiar_estado', id=item['id']) }}" class="btn btn-warning">
              {% if item['activo'] == 1 %}Desactivar{% else %}Activar{% endif %}
            </a>
            <a href="{{ url_for('admin_noticias.editar_noticia', id=item['id']) }}" class="btn btn-primary">Editar</a>
            <a href="{{ url_for('admin_noticias.eliminar_noticia', id=item['id']) }}" class="btn btn-danger" onclick="return confirm('¿Eliminar esta noticia?')">Eliminar</a>
          </td>
        </tr>
        {% else %}
        <tr><td colspan="5">No hay noticias registradas.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

</body>
</html>
"""


@admin_noticias_bp.route("/")
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM noticias ORDER BY id DESC")
    noticias = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_ADMIN_NOTICIAS, noticias=noticias, noticia=None)


@admin_noticias_bp.route("/nueva", methods=["POST"])
@login_required
def nueva_noticia():
    titulo = request.form.get("titulo")
    texto = request.form.get("texto")
    autor = request.form.get("autor")
    imagen = request.form.get("imagen")
    url_post = request.form.get("url_post")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO noticias (titulo, texto, autor, imagen, url_post, activo)
        VALUES (?, ?, ?, ?, ?, 1)
    """,
        (titulo, texto, autor, imagen, url_post),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_noticias.index"))


@admin_noticias_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_noticia(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        titulo = request.form.get("titulo")
        texto = request.form.get("texto")
        autor = request.form.get("autor")
        imagen = request.form.get("imagen")
        url_post = request.form.get("url_post")

        cursor.execute(
            """
            UPDATE noticias 
            SET titulo = ?, texto = ?, autor = ?, imagen = ?, url_post = ?
            WHERE id = ?
        """,
            (titulo, texto, autor, imagen, url_post, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("admin_noticias.index"))

    cursor.execute("SELECT * FROM noticias WHERE id = ?", (id,))
    noticia = cursor.fetchone()
    cursor.execute("SELECT * FROM noticias ORDER BY id DESC")
    noticias = cursor.fetchall()
    conn.close()

    return render_template_string(HTML_ADMIN_NOTICIAS, noticias=noticias, noticia=noticia)


@admin_noticias_bp.route("/estado/<int:id>")
@login_required
def cambiar_estado(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE noticias SET activo = CASE WHEN activo = 1 THEN 0 ELSE 1 END WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_noticias.index"))


@admin_noticias_bp.route("/eliminar/<int:id>")
@login_required
def eliminar_noticia(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM noticias WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_noticias.index"))
