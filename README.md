# Clicivo

Plataforma estática de herramientas online, suites integradas, guías prácticas y calculadoras orientada a utilidad, SEO técnico, privacidad, experiencia móvil y monetización progresiva.

## Versión

`2026.09.02-september-complete-10of10`

## Contenido

- 50 herramientas activas.
- 8 guías editoriales originales.
- 3 suites integradas: Creadores, Laboral España y PDF/Imágenes.
- 112 rutas indexables generadas.
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
