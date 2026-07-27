# Clicivo

Generador estático de herramientas online para GitHub Pages.

## Contenido de esta entrega

- 43 herramientas.
- 15 nuevas herramientas de PDF, imágenes, texto y QR.
- Mejoras prioritarias de YouTube, Instagram y empleo basadas en Search Console.
- 88 URL indexables.
- AdSense, `ads.txt`, Consent Mode y páginas de confianza preparados.
- Pruebas automáticas de rutas, SEO, enlaces y cálculos.

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

Consulta `SUBIR_A_GITHUB.txt` y `CHECKLIST_PUBLICACION.md`.
