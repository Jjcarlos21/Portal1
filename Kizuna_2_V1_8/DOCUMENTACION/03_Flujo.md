# Flujo completo de una página

1. El usuario visita `/cultura/idioma-japones`.
2. Flask ejecuta `culture_detail()` en `app.py`.
3. `content.py` dice que ese directorio usa la columna `Idioma`.
4. SQLite devuelve las organizaciones con `Idioma = 1`.
5. `normalize_record()` convierte rutas de imágenes y normaliza campos vacíos.
6. `group_records()` separa primero Caracas y luego los estados.
7. Se ordena por nombre dentro de cada grupo.
8. `detail.html` crea los títulos de los grupos.
9. `directory_card.html` genera una tarjeta por organización.
10. El navegador aplica estilos y ejecuta `directory.js`.
