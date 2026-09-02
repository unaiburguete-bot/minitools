# Clicivo · paquete definitivo de septiembre 2026

Fecha de preparación: 2 de septiembre de 2026.

Esta entrega concentra en una sola publicación el trabajo técnico, SEO, editorial, UX y de producto planificado para septiembre. Parte de los datos reales acumulados en Google Search Console hasta finales de agosto y mantiene la estrategia acordada: no eliminar páginas sin datos suficientes, proteger las URL que ya muestran señales y mejorar el producto mientras se amplía de forma selectiva.

## Inventario final

- 50 herramientas activas.
- 8 guías editoriales originales.
- 3 suites integradas con flujo propio.
- 112 URL indexables generadas en el sitemap.
- 7 grandes áreas: PDF, imágenes, productividad, creadores, finanzas, negocios y empleo.

## Portada y CTR

- Eliminado el antiguo panel decorativo con 1.248 €, barras ficticias y “0 archivos guardados”.
- Hero directo: “Herramientas online gratuitas para calcular, convertir y crear”.
- Buscador principal y cinco accesos reales: crecimiento de Instagram, ingresos de YouTube, finiquito, redimensionar imágenes y organizar PDF.
- Titles y primeros bloques ajustados sin cambiar URL en Instagram Growth, RPM de YouTube y YouTube Shorts.

## Mejoras de producto basadas en Search Console

Se refuerzan, entre otras, sueldo bruto ↔ neto, finiquito, coste empresa, vacaciones, hipoteca, préstamo personal, margen de beneficio, redimensionado/compresión de imágenes, PDF y las calculadoras prioritarias para creadores. Las mejoras incluyen tablas completas de amortización, escenarios comparables, desgloses, exportaciones, procesamiento por lotes y comparación visual antes/después donde procede.

## Herramientas añadidas durante el paquete de septiembre

- CPM de YouTube.
- RPM real de TikTok.
- ROAS y CAC.
- Beneficio medio por cliente.
- IVA.
- Porcentajes.
- Días entre fechas y laborables.
- Conversor general de unidades: longitud, masa, volumen, temperatura, velocidad y datos.

No se crean URL separadas para variaciones que pueden resolverse dentro de una herramienta existente.

## Tres suites integradas

### Creadores
Ruta: `/es/suites/creadores/`

Un único escenario combina YouTube, TikTok e Instagram para calcular RPM, proyecciones y evolución. Permite guardar/recuperar una fotografía local, copiar el resumen y exportar PDF.

### Laboral España
Ruta: `/es/suites/laboral-espana/`

Un único conjunto de datos conecta salario neto estimado, coste empresa, vacaciones, finiquito e indemnización orientativa. Permite guardar/recuperar escenario, copiar y exportar PDF.

### PDF e imágenes
Ruta: `/es/suites/pdf-imagenes/`

El usuario selecciona el archivo o lote una sola vez y puede ejecutar varias operaciones sin volver a seleccionarlo. PDF permite extraer, separar y pasar páginas a JPG. Imágenes permite optimizar/redimensionar, convertir formato y crear copias re-codificadas sin metadatos habituales. Incluye comparación antes/después y procesamiento local en navegador.

Hub: `/es/suites/`

## Retención y defensibilidad

Las calculadoras profesionales incorporan según contexto:

- Descargar informe PDF.
- Exportar CSV compatible con Excel.
- Copiar resumen para cliente.
- Guardar y recuperar escenario local.
- Compartir resultado.
- Favoritos y herramientas recientes.

Las suites añaden eventos propios de uso, guardado, carga, copia, exportación y procesamiento.

## Ocho guías editoriales

- RPM y CPM de YouTube.
- Cómo interpretar el crecimiento de seguidores de Instagram.
- Ingresos de YouTube Shorts y límites de una estimación por RPM.
- Finiquito e indemnización en España.
- Coste de un trabajador para la empresa.
- Redimensionar y comprimir imágenes sin perder calidad innecesariamente.
- Organizar y dividir PDF.
- Cómo usar calculadoras financieras sin confundir una estimación con una previsión.

Hub: `/es/guias/`

## Confianza y responsabilidad

Cada herramienta incluye un bloque “Quién, cómo y por qué” con responsable editorial, metodología, finalidad, fecha de revisión y fuentes cuando corresponden. En empleo y finanzas se mantienen supuestos y limitaciones visibles. En PDF e imágenes se explica el procesamiento local únicamente donde realmente se realiza.

## Mobile-first

El CSS incluye reglas específicas para 430 px y 390 px, campos táctiles, texto de formulario de 16 px, acciones apiladas, tablas desplazables y resultados adaptados. Después del despliegue debe hacerse una comprobación rápida en un teléfono real para validar el renderizado del navegador de producción.

## Medición

Se conservan o añaden eventos como `tool_view`, `tool_start`, `tool_complete`, `tool_error`, `result_view`, `result_copy`, `result_pdf_download`, `result_csv_download`, `result_share`, `file_upload`, `file_download`, `related_tool_click`, `scenario_save`, `scenario_load`, `favorite_tool`, `suite_view`, `suite_start`, `suite_complete`, `suite_save`, `suite_load`, `suite_copy`, `suite_pdf_download` y Web Vitals.

La recepción efectiva de estos eventos debe verificarse en GA4 después del despliegue.

## Monetización

- Se conserva AdSense y `ads.txt`.
- No se solicita automáticamente una nueva revisión de AdSense.
- La afiliación se limita a contextos realmente relacionados.
- No se colocan anuncios dentro del flujo de cálculo ni pegados a acciones críticas.

## Validación final

La entrega se construye y valida con:

```bash
python src/build.py
pytest -q
node --check public/assets/site.js
node --check public/assets/advanced-tools.js
node --check public/assets/suites.js
node tests/js_smoke.js
```

Consulta `ENTREGA_10_10.md` para el cierre del checklist acordado.
