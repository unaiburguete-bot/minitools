# Clicivo

Plataforma estática de herramientas online, suites integradas, guías prácticas y calculadoras orientada a utilidad, SEO técnico, privacidad, experiencia móvil y monetización progresiva.

## Versión

`2026.11.06-ux-seo`

## Contenido

- 50 herramientas activas.
- 12 guías editoriales originales.
- 3 suites integradas: Creadores, Laboral España y PDF/Imágenes.
- 92 rutas indexables generadas; se mantienen las 50 URLs de herramientas.
- Generador estático Python.
- GitHub Pages mediante GitHub Actions.
- Procesamiento local en navegador para PDF e imágenes cuando se indica.
- Informes PDF y CSV en calculadoras profesionales.
- Favoritos, recientes y escenarios guardados localmente.
- Analytics con eventos de uso, suites y Web Vitals.
- Configuración de AdSense/ads.txt conservada.

## Construcción local

```bash
pip install -r requirements.txt
python src/build.py
pytest -q
node --check public/assets/site.js
node --check public/assets/advanced-tools.js
node --check public/assets/suites.js
node tests/js_smoke.js
```

Consulta `ENTREGA_10_10.md`, `SUBIR_ESTA_VERSION.txt` y `CHECKLIST_PUBLICACION.md` antes de publicar.

## Actualización de noviembre de 2026

Nueva portada orientada a tareas, buscador mejorado, catálogo accesible y ejemplos prácticos en seis herramientas prioritarias. Cambios preparados en una rama de revisión para preservar la versión pública hasta su validación.
