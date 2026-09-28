# Kizuna 2 — guía del prototipo de directorio

## 1. Cómo funciona

El navegador solicita una URL como `/cultura/idioma-japones` → `app.py` recibe la solicitud → consulta `data/kizuna.db` → ordena y agrupa las organizaciones → entrega `templates/pages/detail.html` → esa página reutiliza `templates/components/directory_card.html` para cada organización → CSS y JavaScript completan la presentación y las interacciones.

## 2. Archivos principales

- `app.py`: servidor Flask, rutas, consulta SQLite, normalización y agrupación.
- `content.py`: configuración de los directorios (título, actividad y mensajes).
- `data/kizuna.db`: datos de las organizaciones.
- `templates/base.html`: estructura común, fuentes, fondo y estilos globales.
- `templates/pages/home.html`: página de entrada.
- `templates/pages/detail.html`: encabezado del directorio, grupos Caracas/estados y formulario de inscripción.
- `templates/components/directory_card.html`: una tarjeta de organización.
- `static/js/directory.js`: carrusel y formulario de inscripción.
- `DOCUMENTACION/`: explicación pedagógica.

## 3. Regla de Caracas

Toda organización cuyo campo `Ciudad` sea `Caracas` se coloca en el primer grupo `Caracas`, independientemente de que `Estado` sea `Miranda` o `Distrito Capital`. Esas organizaciones no se vuelven a mostrar bajo Miranda.

## 4. Orden

Caracas es siempre el primer grupo. Los demás estados se ordenan alfabéticamente y las tarjetas dentro de cada grupo se ordenan por `Nombre` A–Z.

## 5. WhatsApp

`Whatsapp` vive en SQLite. `NULL` o texto vacío significa que no hay WhatsApp. Si existe un número, la tarjeta muestra el icono y el número como tooltip, pero no crea un enlace a WhatsApp.

## 6. Arranque local

En Windows:

```bat
cd C:\ruta\a\Kizuna_2
py app.py
```

Luego abrir `http://127.0.0.1:5000/`.

El prototipo usa `debug=False` para evitar el doble proceso/reloader que causó problemas anteriormente.
