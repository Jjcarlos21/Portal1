document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('inscription-modal');
  document.querySelectorAll('[data-open-inscription]').forEach(btn => btn.addEventListener('click', () => modal?.classList.remove('hidden')));
  document.querySelectorAll('[data-close-inscription]').forEach(btn => btn.addEventListener('click', () => modal?.classList.add('hidden')));
  modal?.addEventListener('click', e => { if (e.target === modal) modal.classList.add('hidden'); });

  document.querySelectorAll('[data-photo-next]').forEach(btn => {
    btn.addEventListener('click', () => changePhoto(btn.dataset.photoNext, 1));
  });
  document.querySelectorAll('[data-photo-prev]').forEach(btn => {
    btn.addEventListener('click', () => changePhoto(btn.dataset.photoPrev, -1));
  });

  const form = document.getElementById('inscription-form');
  form?.addEventListener('submit', e => {
    e.preventDefault();
    const data = new FormData(form);
    const body = [
      'Solicitud de inscripción al Directorio Kizuna Venezuela', '',
      `Nombre y apellido: ${data.get('nombre')}`,
      `Nombre de la organización: ${data.get('organizacion')}`,
      `Dirección: ${data.get('direccion')}`,
      `Teléfono: ${data.get('telefono')}`,
      `Email: ${data.get('email')}`,
      `Especialidades: ${data.get('especialidades') || 'No indicado'}`,
      `Redes sociales: ${data.get('redes') || 'No indicado'}`,
      `Sitio web: ${data.get('web') || 'No indicado'}`, '',
      'La persona solicitante será contactada una vez verificada la información.'
    ].join('\n');
    const subject = `Solicitud de inscripción - ${data.get('organizacion')}`;
    if (modal) modal.classList.add('hidden');
    form.reset();
    window.location.href = `mailto:admin.kizunavenezuela@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
});

function changePhoto(id, direction) {
  const slides = Array.from(document.querySelectorAll(`.directory-slide[data-card-id="${CSS.escape(String(id))}"]`));
  if (slides.length < 2) return;
  let current = slides.findIndex(s => !s.classList.contains('hidden'));
  if (current < 0) current = 0;
  const next = (current + direction + slides.length) % slides.length;
  slides[current].classList.add('hidden');
  slides[next].classList.remove('hidden');
  const counter = document.querySelector(`[data-photo-counter="${CSS.escape(String(id))}"]`);
  if (counter) counter.textContent = `${next + 1}/${slides.length}`;
}
