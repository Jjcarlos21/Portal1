# Kizuna 2.0 — Hito 1

Piloto no destructivo de migración de cuatro directorios culturales:

- `/cultura/aikido`
- `/cultura/judo`
- `/cultura/karate`
- `/cultura/bonsai`

## Qué cambia

1. Un solo `templates/pages/detail.html` reemplaza los cuatro HTML `D-*`.
2. `templates/base.html` centraliza shell, navegación, footer y estilos base.
3. `templates/components/directory_card.html` encapsula la tarjeta de directorio.
4. `content.py` contiene la configuración de cada actividad.
5. `app.py` consulta SQLite en servidor y entrega datos ya preparados a Jinja.
6. Se elimina del flujo del piloto la descarga de `kizuna.db` al navegador y `sql.js`.
7. Los cuatro HTML originales se conservan en `legacy_pilots/` para comparación.

## Importante

Este ZIP es un **piloto paralelo**. No reemplaza todavía el proyecto Kizuna original ni migra sus módulos de noticias, directorio administrativo, MEXT, autenticación o chatbot.
