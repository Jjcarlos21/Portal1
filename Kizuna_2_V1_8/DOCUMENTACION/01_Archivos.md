# Qué hace cada tipo de archivo

## Python (`.py`)

Contiene lógica ejecutable del servidor. En Kizuna, `app.py` crea Flask, abre SQLite, transforma los datos y renderiza plantillas.

## HTML (`.html`)

Define la estructura visible. Los archivos HTML de Kizuna usan Jinja: `{{ variable }}` imprime datos y `{% if %}` / `{% for %}` permiten decisiones y recorridos.

## CSS

Define apariencia: tamaños, espaciado, colores, estados hover y proporciones de la tarjeta. En este prototipo la mayor parte está dentro de `base.html` mediante Tailwind y algunas reglas CSS específicas.

## JavaScript (`.js`)

Añade comportamiento en el navegador. `static/js/directory.js` controla el carrusel de fotografías y convierte el formulario en un mensaje `mailto:`.

## SQLite (`.db`)

Base de datos local. No es una página ni un programa: contiene registros estructurados. El campo `Whatsapp` es un dato de cada organización.

## Jinja

Es el lenguaje de plantillas que Flask procesa antes de enviar HTML al navegador. Ejemplo: `{{ item.Nombre }}` toma el nombre del registro actual.
