# Clicivo

Fábrica estática de calculadoras y herramientas web orientada a rendimiento, utilidad y SEO técnico.

## Compilar localmente

```bash
pip install Pillow markdown pyyaml pytest
python src/compilador.py
pytest -q
```

La salida se genera en `public/`.

## Configuración

La marca, el dominio y las rutas se centralizan en `config/site.yaml`.
