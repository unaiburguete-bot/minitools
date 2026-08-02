# Clicivo

Generador estático de herramientas online para GitHub Pages.

## Entrega 02/08/2026

- 42 herramientas activas.
- 87 URL indexables.
- Consolidación SEO de YouTube, Instagram, empleo, finanzas, PDF, imágenes y productividad.
- Redirecciones para URL antiguas y para una herramienta de YouTube con intención duplicada.
- AdSense, `ads.txt`, Consent Mode y páginas de confianza preparados.
- Contenido público limpiado de notas internas de SEO y listas de palabras clave.
- 16 pruebas automáticas y pruebas JavaScript superadas.

## Construir y probar

```bash
python -m pip install -r requirements.txt
python src/build.py
pytest -q
node --check public/assets/site.js
node --check public/assets/advanced-tools.js
node tests/js_smoke.js
```

## Publicación

El workflow `.github/workflows/deploy.yml` construye, prueba y publica `public` en GitHub Pages.

Consulta `SUBIR_A_GITHUB.txt`, `CHECKLIST_PUBLICACION.md` y `PLAN_90_DIAS.md`.
