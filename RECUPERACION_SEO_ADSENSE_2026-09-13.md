# Clicivo — versión de recuperación SEO + AdSense

Fecha: 13/09/2026

## Motivo

Entre el 27/08 y el 03/09 Clicivo obtuvo 1.369 impresiones (171/día de media). Del 04/09 al 11/09 el informe disponible registra 12 impresiones (1,5/día). AdSense ha rechazado el sitio por "Contenido de poco valor". La versión de recuperación reduce señales de páginas ligeras/repetitivas y limita el código publicitario a contenido editorial.

## Cambios aplicados

1. **Colecciones ligeras fuera del índice**
   - Las colecciones con una sola herramienta pasan a ser redirecciones hacia la utilidad real.
   - Las colecciones con dos herramientas siguen accesibles para navegación, pero llevan `noindex,follow` y no aparecen en el sitemap.
   - Los breadcrumbs ya no enlazan a estas rutas ligeras.

2. **Sitemap más limpio**
   - Solo incluye URLs que permiten indexación.
   - Se eliminan `priority` y `changefreq`.
   - `lastmod` usa la fecha real de revisión de cada herramienta/guía cuando existe, en lugar de poner la fecha del build en toda la web.

3. **Corrección de la URL antigua de RPM**
   - `/es/youtube/monetizacion/rpm-youtube/` apunta ahora a `/es/youtube/monetizacion/calcular-rpm-youtube/`.

4. **Menos texto de plantilla repetido**
   - Se retiran de las 50 herramientas el bloque repetido de “Responsabilidad editorial”, el ribbon genérico y otros elementos de boilerplate.
   - Se mantiene lo que aporta valor específico: herramienta funcional, beneficio, fórmula, ejemplo, FAQ, fuentes, interpretación, guía y herramientas relacionadas.
   - La metodología general queda centralizada en `/metodologia/`.

5. **Más contenido específico en páginas que ya habían mostrado demanda**
   - Se han reforzado, entre otras: engagement Instagram, letras/contador/espacios de Instagram, engagement TikTok, sueldo neto, coste empresa, hipoteca, vacaciones, amortización anticipada, indemnización, ahorro mensual, fondos indexados y margen de beneficio.

6. **Cuatro guías editoriales nuevas**
   - Métricas de TikTok: engagement, RPM e ingresos.
   - Texto para Instagram: negritas, espacios y límites.
   - Salario bruto, neto y coste empresa.
   - Margen, punto de equilibrio, ROAS y CAC.
   - Total de guías: 12.

7. **Modo recuperación de AdSense**
   - El código de AdSense queda únicamente en la portada y en las 12 guías editoriales.
   - Se elimina de herramientas, suites, páginas legales y páginas de navegación/colección.
   - Esto evita que las pantallas de navegación o utilidad ligera formen parte del inventario publicitario durante la nueva revisión.
   - Los enlaces de afiliación quedan desactivados temporalmente.

8. **Portada reforzada**
   - Se elimina el énfasis en el volumen de URLs.
   - Se añade un bloque de criterio editorial que explica por qué Clicivo no indexa automáticamente todas las rutas de navegación.
   - Se muestran más guías originales.

## Validación técnica

- 36 tests Python: OK.
- JavaScript smoke tests: OK.
- 92 URLs indexables en el nuevo sitemap.
- 29 rutas `noindex`/redirecciones auxiliares.
- Ninguna ruta `noindex` carga el script de AdSense.
- El código de AdSense aparece solo en 13 URLs: portada + 12 guías.

## Qué hacer al publicar

1. Subir esta versión completa al repositorio y esperar al despliegue de GitHub Pages.
2. Abrir `https://clicivo.com/sitemap.xml` y comprobar que devuelve el sitemap nuevo.
3. En Search Console, enviar el sitemap **una sola vez**.
4. Inspeccionar solo estas URLs y, si la versión publicada es correcta, solicitar indexación una vez:
   - `/`
   - `/es/instagram/analitica/crecimiento-seguidores-instagram/`
   - `/es/youtube/monetizacion/calcular-rpm-youtube/`
   - `/es/youtube/monetizacion/ingresos-youtube/`
   - `/es/empleo/vacaciones/calculadora-vacaciones/`
   - `/es/empleo/liquidacion-laboral/calculadora-finiquito/`
   - `/es/guias/rpm-cpm-youtube/`
5. No publicar nuevas herramientas durante al menos 2-3 semanas.
6. No hacer clic manualmente en resultados de Clicivo para no contaminar Search Console.
7. Cuando Google haya rastreado la versión nueva y el sitio lleve varios días estable, solicitar de nuevo la revisión de AdSense. No hacer varias solicitudes consecutivas.

## Criterio para volver a crecer

Antes de añadir una nueva herramienta debe cumplirse al menos uno de estos criterios:
- resolver una función que no exista ya en Clicivo;
- aportar una metodología/fuente propia claramente diferenciada;
- integrarse en una guía o suite que añada contexto real;
- tener intención de búsqueda distinta sin crear una simple variación de otra página.

No volver a crear páginas de colección indexables cuando solo contengan 1-2 herramientas.
