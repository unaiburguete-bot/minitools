# Clicivo

Sitio estático de calculadoras y herramientas gratuitas. Esta entrega mantiene las 18 URLs de herramientas existentes, incorpora 10 herramientas nuevas, reconstruye el catálogo, añade la identidad visual de Clicivo y mejora SEO, accesibilidad, rendimiento y enlazado interno.

## Publicación

1. Instala dependencias: `pip install -r requirements.txt`
2. Compila: `python src/build.py`
3. Comprueba: `pytest -q`
4. Publica la carpeta `public/` mediante GitHub Pages.

El workflow incluido realiza estos pasos al hacer push a `main`.

## Estructura

- `content/tools.json`: definición de herramientas, textos, preguntas y fuentes.
- `config/site.json`: marca, dominio, Analytics y contacto.
- `src/build.py`: generador estático.
- `public/`: web lista para publicar.
- `tests/`: comprobaciones de enlaces, metadatos, sitemap y contenido.

## Privacidad y analítica

Google Analytics solo se activa después de aceptar las cookies analíticas. Los cálculos se ejecutan en el navegador y no se envían a Clicivo.

## Revisión legal

Se ha eliminado de toda la entrega el nombre personal indicado. Antes de publicar, conviene que la persona responsable del sitio revise el aviso legal y complete cualquier dato identificativo que resulte obligatorio en su caso.
