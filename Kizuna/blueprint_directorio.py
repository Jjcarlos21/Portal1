"""
Panel administrativo del DIRECTORIO, convertido de app Flask independiente
a Blueprint para que pueda vivir dentro de una sola aplicación (necesario
para el plan gratis de PythonAnywhere, que solo permite una app web).

Cambios respecto al admin_directorios.py original:
- Flask(__name__) -> Blueprint("admin_directorio", __name__)
- @app.route(...) -> @admin_directorio_bp.route(...)
- Todos los url_for('index'), url_for('formulario'), etc. ahora llevan
  el prefijo del blueprint: url_for('admin_directorio.index'), etc.
  url_for('logout') NO lleva prefijo porque el login se registra directo
  sobre la app principal (ver app.py).
- PROJECT_ROOT (antes "un nivel arriba de admin_tools/") -> BASE_DIR,
  porque ahora este archivo vive en la misma carpeta que app.py.
- init_db() -> init_db_directorio() (nombre único, se llama desde app.py)
- Se quitó la ruta /static/<path:filename>: la app principal ya sirve
  ese mismo directorio "static/" automáticamente, así que era redundante.
- Ya no tiene bloque `if __name__ == "__main__":` ni su propio waitress:
  este archivo ya no se ejecuta solo, se importa desde app.py.
"""

import os
import sqlite3
from flask import Blueprint, redirect, render_template_string, request, url_for
from PIL import Image
from auth import login_required

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "img", "directorio")
DB_PATH = os.path.join(DATA_DIR, "kizuna.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

admin_directorio_bp = Blueprint("admin_directorio", __name__)

CATEGORIAS = [
    "Aikido", "Judo", "Karate", "Sumo", "Kendo", "Bonsai", "Ceramica", "Te",
    "Butoh", "Origami", "Taiko", "Idioma", "Caligrafia", "Go", "Gastronomia",
    "Anime", "Manga", "Cosplay", "Jpop", "Cultura", "Otro2", "Otro3", "Otro4",
    "Otro5", "Otro6", "Otro7", "Otro8"
]


def procesar_y_guardar_imagen(file_storage, max_size, rel_path):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass

    img = Image.open(file_storage)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    img.save(full_path, "JPEG", quality=85)
    return rel_path


def eliminar_archivo_si_existe(rel_path):
    if rel_path:
        full_path = os.path.join(BASE_DIR, rel_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except OSError:
                pass


def init_db_directorio():
    conexion = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conexion.cursor()
    cat_columns = ", ".join([f"{cat} INTEGER DEFAULT 0" for cat in CATEGORIAS])

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS directorio (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        Estado TEXT,
        Ciudad TEXT,
        Zona TEXT,
        Telefono1 TEXT,
        Telefono2 TEXT,
        Responsable TEXT,
        Instagram TEXT,
        Facebook TEXT,
        X TEXT,
        Webpage TEXT,
        Email TEXT,
        Direccion TEXT,
        logo TEXT DEFAULT NULL,
        foto1 TEXT DEFAULT NULL,
        foto2 TEXT DEFAULT NULL,
        foto3 TEXT DEFAULT NULL,
        foto4 TEXT DEFAULT NULL,
        {cat_columns}
    );
    """)

    cursor.execute("PRAGMA table_info(directorio)")
    columnas_actuales = [columna[1] for columna in cursor.fetchall()]

    if "Direccion" in columnas_actuales and "Zona" not in columnas_actuales:
        cursor.execute("ALTER TABLE directorio RENAME COLUMN Direccion TO Zona")

    cursor.execute("PRAGMA table_info(directorio)")
    columnas_actuales = [columna[1] for columna in cursor.fetchall()]

    NUEVAS_COLUMNAS = {
        "Zona": "TEXT",
        "Direccion": "TEXT",
        "Cultura": "INTEGER DEFAULT 0",
        "logo": "TEXT DEFAULT NULL",
        "foto1": "TEXT DEFAULT NULL",
        "foto2": "TEXT DEFAULT NULL",
        "foto3": "TEXT DEFAULT NULL",
        "foto4": "TEXT DEFAULT NULL",
    }

    for col, col_type in NUEVAS_COLUMNAS.items():
        if col not in columnas_actuales:
            cursor.execute(f"ALTER TABLE directorio ADD COLUMN {col} {col_type}")

    if "Otro1" in columnas_actuales and "Cultura" in columnas_actuales:
        cursor.execute("UPDATE directorio SET Cultura = Otro1 WHERE Cultura = 0")

    conexion.commit()
    conexion.close()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Gestión de Directorio - Kizuna Venezuela</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; color: #333; }
    h1, h2 { color: #c0392b; }
    nav { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    nav a { margin-right: 15px; text-decoration: none; color: #2980b9; font-weight: bold; }
    .btn-logout { color: #e74c3c !important; }
    .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .form-group { margin-bottom: 12px; }
    label { display: block; font-weight: bold; margin-bottom: 5px; }
    input[type="text"], input[type="email"], input[type="tel"], input[type="url"], select, textarea, input[type="file"] {
      width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; font-family: Arial, sans-serif;
    }
    textarea { resize: vertical; height: 60px; }
    .checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; margin-top: 10px; }
    .btn { padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
    .btn-primary { background-color: #27ae60; color: white; }
    .btn-danger { background-color: #e74c3c; color: white; }
    .btn-edit { background-color: #f39c12; color: white; }
    .btn-secondary { background-color: #7f8c8d; color: white; }
    table { width: 100%; border-collapse: collapse; background: white; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
    th { background-color: #f2f2f2; }
    .actions { display: flex; gap: 5px; }
    .img-preview { width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc; }
    .img-thumb { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc; margin-right: 5px; }
  </style>
</head>
<body>

  <h1>Directorio Kizuna Venezuela</h1>
  <nav>
    <div>
      <a href="{{ url_for('admin_directorio.index') }}">📋 Ver Directorio</a>
      <a href="{{ url_for('admin_directorio.formulario') }}">➕ Agregar Registro</a>
    </div>
    <div>
      <a href="{{ url_for('logout') }}" class="btn-logout">🔒 Cerrar Sesión</a>
    </div>
  </nav>

  {% if vista == 'tabla' %}
    <div class="card">
      <h2>Filtros</h2>
      <form method="GET" action="{{ url_for('admin_directorio.index') }}" style="display: flex; gap: 10px;">
        <select name="estado">
          <option value="">Todos los Estados</option>
          {% for est in estados %}
            <option value="{{ est }}" {% if estado_sel == est %}selected{% endif %}>{{ est }}</option>
          {% endfor %}
        </select>
        <select name="categoria">
          <option value="">Todas las Categorías</option>
          {% for cat in categorias %}
            <option value="{{ cat }}" {% if cat_sel == cat %}selected{% endif %}>{{ cat }}</option>
          {% endfor %}
        </select>
        <button type="submit" class="btn btn-secondary">Filtrar</button>
      </form>
    </div>

    <table>
      <thead>
        <tr>
          <th>Logo</th>
          <th>ID</th>
          <th>Nombre</th>
          <th>Ubicación y Dirección</th>
          <th>Contacto</th>
          <th>Fotos</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {% for reg in registros %}
        <tr>
          <td>
            {% if reg['logo'] %}
              <img src="/{{ reg['logo'] }}" class="img-preview" alt="Logo">
            {% else %}
              <small>Sin logo</small>
            {% endif %}
          </td>
          <td>{{ reg['ID'] }}</td>
          <td><strong>{{ reg['Nombre'] }}</strong></td>
          <td>
            <strong>{{ reg['Ciudad'] }}, {{ reg['Estado'] }}</strong>
            {% if reg['Zona'] %}<br><small>🏙️ Zona: {{ reg['Zona'] }}</small>{% endif %}
            {% if reg['Direccion'] %}<br><small>📍 {{ reg['Direccion'] }}</small>{% endif %}
          </td>
          <td>
            {% if reg['Telefono1'] %}📞 {{ reg['Telefono1'] }}<br>{% endif %}
            {% if reg['Email'] %}✉️ {{ reg['Email'] }}{% endif %}
          </td>
          <td>
            {% for i in range(1, 5) %}
              {% set foto_key = 'foto' ~ i %}
              {% if reg[foto_key] %}
                <img src="/{{ reg[foto_key] }}" class="img-thumb" alt="Foto {{ i }}">
              {% endif %}
            {% endfor %}
          </td>
          <td class="actions">
            <a href="{{ url_for('admin_directorio.editar', id=reg['ID']) }}" class="btn btn-edit">Editar</a>
            <a href="{{ url_for('admin_directorio.eliminar', id=reg['ID']) }}" class="btn btn-danger" onclick="return confirm('¿Seguro que deseas eliminar este registro?')">Eliminar</a>
          </td>
        </tr>
        {% else %}
        <tr><td colspan="7">No hay registros guardados.</td></tr>
        {% endfor %}
      </tbody>
    </table>

  {% elif vista == 'form' %}
    <div class="card">
      <h2>{% if reg %}Editar Registro #{{ reg['ID'] }}{% else %}Nuevo Registro{% endif %}</h2>
      <form method="POST" enctype="multipart/form-data" action="{% if reg %}{{ url_for('admin_directorio.editar', id=reg['ID']) }}{% else %}{{ url_for('admin_directorio.formulario') }}{% endif %}">
        
        <div class="form-group"><label>Nombre:</label><input type="text" name="Nombre" value="{{ reg['Nombre'] if reg else '' }}" required></div>
        <div class="form-group"><label>Estado:</label><input type="text" name="Estado" value="{{ reg['Estado'] if reg else '' }}"></div>
        <div class="form-group"><label>Ciudad:</label><input type="text" name="Ciudad" value="{{ reg['Ciudad'] if reg else '' }}"></div>
        <div class="form-group"><label>Zona:</label><input type="text" name="Zona" value="{{ reg['Zona'] if reg else '' }}"></div>
        <div class="form-group"><label>Dirección exacta:</label><textarea name="Direccion">{{ reg['Direccion'] if reg else '' }}</textarea></div>
        <div class="form-group"><label>Teléfono 1:</label><input type="tel" name="Telefono1" value="{{ reg['Telefono1'] if reg else '' }}"></div>
        <div class="form-group"><label>Email:</label><input type="email" name="Email" value="{{ reg['Email'] if reg else '' }}"></div>

        <h3>Archivos Multimedia</h3>
        <div class="form-group">
          <label>Logo (Máx. 400px):</label>
          <input type="file" name="logo" accept="image/*">
        </div>

        {% for i in range(1, 5) %}
          <div class="form-group">
            <label>Foto {{ i }} (Máx. 1200px):</label>
            <input type="file" name="foto{{ i }}" accept="image/*">
          </div>
        {% endfor %}

        <h3>Disciplinas y Categorías</h3>
        <div class="checkbox-grid">
          {% for cat in categorias %}
            <label>
              <input type="checkbox" name="{{ cat }}" value="1" {% if reg and reg[cat] == 1 %}checked{% endif %}>
              {{ cat }}
            </label>
          {% endfor %}
        </div>

        <br><br>
        <button type="submit" class="btn btn-primary">Guardar</button>
        <a href="{{ url_for('admin_directorio.index') }}" class="btn btn-secondary">Cancelar</a>
      </form>
    </div>
  {% endif %}

</body>
</html>
"""


@admin_directorio_bp.route("/")
@login_required
def index():
    estado_filtro = request.args.get("estado", "")
    cat_filtro = request.args.get("categoria", "")

    conexion = sqlite3.connect(DB_PATH, timeout=10)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    where_clause = " WHERE 1=1"
    params = []

    if estado_filtro:
        where_clause += " AND Estado = ?"
        params.append(estado_filtro)

    if cat_filtro and cat_filtro in CATEGORIAS:
        where_clause += f" AND {cat_filtro} = 1"

    query = f"SELECT * FROM directorio{where_clause}"
    cursor.execute(query, params)
    registros = cursor.fetchall()

    cursor.execute("SELECT DISTINCT Estado FROM directorio WHERE Estado IS NOT NULL AND Estado != ''")
    estados = [row["Estado"] for row in cursor.fetchall()]

    conexion.close()

    return render_template_string(
        HTML_TEMPLATE,
        vista="tabla",
        registros=registros,
        estados=estados,
        categorias=CATEGORIAS,
        estado_sel=estado_filtro,
        cat_sel=cat_filtro,
    )


@admin_directorio_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def formulario():
    if request.method == "POST":
        datos_texto = {
            "Nombre": request.form.get("Nombre"),
            "Estado": request.form.get("Estado"),
            "Ciudad": request.form.get("Ciudad"),
            "Zona": request.form.get("Zona"),
            "Direccion": request.form.get("Direccion"),
            "Telefono1": request.form.get("Telefono1"),
            "Email": request.form.get("Email"),
        }
        datos_categorias = {cat: 1 if request.form.get(cat) else 0 for cat in CATEGORIAS}
        todos_los_datos = {**datos_texto, **datos_categorias}

        columnas = ", ".join(todos_los_datos.keys())
        placeholders = ", ".join(["?"] * len(todos_los_datos))

        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        cursor.execute(
            f"INSERT INTO directorio ({columnas}) VALUES ({placeholders})",
            list(todos_los_datos.values()),
        )
        new_id = cursor.lastrowid

        updates_img = {}
        file_logo = request.files.get("logo")
        if file_logo and file_logo.filename != "":
            rel_path = f"static/img/directorio/dir_{new_id}_logo.jpg"
            updates_img["logo"] = procesar_y_guardar_imagen(file_logo, 400, rel_path)

        for i in range(1, 5):
            field_name = f"foto{i}"
            file_foto = request.files.get(field_name)
            if file_foto and file_foto.filename != "":
                rel_path = f"static/img/directorio/dir_{new_id}_foto{i}.jpg"
                updates_img[field_name] = procesar_y_guardar_imagen(file_foto, 1200, rel_path)

        if updates_img:
            set_clause = ", ".join([f"{k} = ?" for k in updates_img.keys()])
            cursor.execute(
                f"UPDATE directorio SET {set_clause} WHERE ID = ?",
                list(updates_img.values()) + [new_id],
            )

        conexion.commit()
        conexion.close()
        return redirect(url_for("admin_directorio.index"))

    return render_template_string(
        HTML_TEMPLATE, vista="form", reg=None, categorias=CATEGORIAS
    )


@admin_directorio_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    conexion = sqlite3.connect(DB_PATH, timeout=10)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    if request.method == "POST":
        datos_texto = {
            "Nombre": request.form.get("Nombre"),
            "Estado": request.form.get("Estado"),
            "Ciudad": request.form.get("Ciudad"),
            "Zona": request.form.get("Zona"),
            "Direccion": request.form.get("Direccion"),
            "Telefono1": request.form.get("Telefono1"),
            "Email": request.form.get("Email"),
        }
        datos_categorias = {cat: 1 if request.form.get(cat) else 0 for cat in CATEGORIAS}
        todos_los_datos = {**datos_texto, **datos_categorias}

        file_logo = request.files.get("logo")
        if file_logo and file_logo.filename != "":
            rel_path = f"static/img/directorio/dir_{id}_logo.jpg"
            todos_los_datos["logo"] = procesar_y_guardar_imagen(file_logo, 400, rel_path)

        for i in range(1, 5):
            field_name = f"foto{i}"
            file_foto = request.files.get(field_name)
            if file_foto and file_foto.filename != "":
                rel_path = f"static/img/directorio/dir_{id}_foto{i}.jpg"
                todos_los_datos[field_name] = procesar_y_guardar_imagen(file_foto, 1200, rel_path)

        set_clause = ", ".join([f"{key} = ?" for key in todos_los_datos.keys()])
        valores = list(todos_los_datos.values()) + [id]

        cursor.execute(f"UPDATE directorio SET {set_clause} WHERE ID = ?", valores)
        conexion.commit()
        conexion.close()
        return redirect(url_for("admin_directorio.index"))

    cursor.execute("SELECT * FROM directorio WHERE ID = ?", (id,))
    reg = cursor.fetchone()
    conexion.close()

    return render_template_string(
        HTML_TEMPLATE, vista="form", reg=reg, categorias=CATEGORIAS
    )


@admin_directorio_bp.route("/eliminar/<int:id>")
@login_required
def eliminar(id):
    conexion = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conexion.cursor()
    cursor.execute("SELECT logo, foto1, foto2, foto3, foto4 FROM directorio WHERE ID = ?", (id,))
    reg = cursor.fetchone()
    if reg:
        for img_path in reg:
            eliminar_archivo_si_existe(img_path)

    cursor.execute("DELETE FROM directorio WHERE ID = ?", (id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for("admin_directorio.index"))
