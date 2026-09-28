# Cómo modificar una tarjeta

La tarjeta está en `templates/components/directory_card.html`.

- Nombre: `{{ item.Nombre }}`
- Zona: `{{ item.Zona }}`
- Dirección: `{{ item.Direccion }}`
- Teléfono 1: `{{ item.Telefono1 }}`
- Teléfono 2: `{{ item.Telefono2 }}`
- WhatsApp: `{{ item.Whatsapp }}`
- Instagram: `{{ item.Instagram }}`
- Facebook: `{{ item.Facebook }}`
- X: `{{ item.X }}`
- Web: `{{ item.Webpage }}`
- Email: `{{ item.Email }}`
- Logo: `{{ item.logo }}`
- Fotos: `foto1` a `foto4`

Para agregar un nuevo campo, primero debe existir en SQLite; luego se imprime con `{{ item.CampoNuevo }}`. Si el campo requiere una nueva apariencia, se agrega CSS en `base.html`.


## Ajuste v1.4 — composición de la tarjeta

La tarjeta usa una cuadrícula de tres columnas: una columna estrecha para logo y zona, una columna central para el nombre y una columna derecha para la fotografía. La fotografía comienza debajo del nombre y queda a la derecha de Zona, Dirección y Teléfonos. Si no existen fotografías, no se crea ningún contenedor vacío: la tarjeta conserva únicamente el contenido disponible.

El formulario de inscripción incluye ahora **Especialidades** y se cierra al preparar el correo de solicitud.
