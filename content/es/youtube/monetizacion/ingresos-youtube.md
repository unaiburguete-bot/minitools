\---

id: ingresos-youtube

entidad: Ingresos estimados de YouTube

version: 1.0

creado: 2026-07-12

actualizado: 2026-07-12



meta:

&#x20; title: "Calculadora de ingresos de YouTube por visitas y RPM"

&#x20; description: "Estima cuánto dinero puede generar un canal de YouTube introduciendo sus visualizaciones y el RPM real o previsto."



vectores:

&#x20; plataforma: YouTube

&#x20; audiencia: Creadores

&#x20; dificultad: Básico

&#x20; objetivo: Monetización

&#x20; intencion: Calcular ingresos estimados de YouTube según visitas y RPM



calculadora:

&#x20; inputs:

&#x20;   - id: visitas

&#x20;     label: "Número de visualizaciones"

&#x20;     type: "number"

&#x20;     placeholder: "Ej. 100000"

&#x20;     min: 0

&#x20;     step: 1



&#x20;   - id: rpm

&#x20;     label: "RPM estimado (€)"

&#x20;     type: "number"

&#x20;     placeholder: "Ej. 4.25"

&#x20;     min: 0

&#x20;     step: 0.01



&#x20; algoritmo:

&#x20;   pasos:

&#x20;     - id: bloques\_mil

&#x20;       op: "division"

&#x20;       args: \["inputs.visitas", 1000]



&#x20;     - id: ingresos\_estimados

&#x20;       op: "multiplicacion"

&#x20;       args: \["bloques\_mil", "inputs.rpm"]



&#x20;   output: "ingresos\_estimados"

&#x20;   unidad: "€"

&#x20;   label: "Ingresos estimados"



monetizacion:

&#x20; cta: ""

&#x20; afiliado\_url: ""



faqs:

&#x20; - q: "¿Cómo se calculan los ingresos estimados de YouTube?"

&#x20;   a: "Se dividen las visualizaciones entre 1.000 y se multiplica el resultado por el RPM del canal. Por ejemplo, 100.000 visualizaciones con un RPM de 4 € producirían una estimación de 400 €."



&#x20; - q: "¿El resultado coincide exactamente con lo que paga YouTube?"

&#x20;   a: "No necesariamente. Es una estimación basada en el RPM introducido. Los ingresos reales pueden variar por país, temática, estacionalidad, duración de los vídeos, anuncios servidos y otras fuentes de monetización."

\---



\# Calculadora de ingresos de YouTube



Esta calculadora estima cuánto podría generar un canal de YouTube a partir de sus visualizaciones y de un RPM conocido o previsto.



El cálculo utiliza esta fórmula:



\*\*Ingresos estimados = visualizaciones ÷ 1.000 × RPM\*\*



\## Ejemplo práctico



Un canal consigue \*\*100.000 visualizaciones\*\* y tiene un RPM de \*\*4,25 €\*\*:



\*\*100.000 ÷ 1.000 × 4,25 = 425 €\*\*



Los ingresos estimados serían \*\*425 €\*\*.



\## Qué RPM debes introducir



Para obtener una estimación útil, utiliza preferentemente el RPM que aparece en YouTube Analytics durante un periodo similar.



Si todavía no tienes datos históricos, puedes probar varios escenarios:



\- Escenario prudente con un RPM bajo.

\- Escenario medio.

\- Escenario optimista con un RPM más alto.



\## Diferencia entre RPM y CPM



El CPM representa el importe pagado por los anunciantes por cada 1.000 impresiones publicitarias.



El RPM representa los ingresos reales obtenidos por el creador por cada 1.000 visualizaciones, después de considerar la participación de YouTube y otras fuentes de ingresos incluidas en la métrica.



Por eso, para estimar lo que recibe el canal, normalmente resulta más útil utilizar el RPM.



\## Limitaciones de la estimación



El resultado no constituye una cifra garantizada. Los ingresos pueden variar según:



\- El país de la audiencia.

\- La temática del canal.

\- La época del año.

\- La duración y el formato de los vídeos.

\- El porcentaje de visualizaciones monetizadas.

\- La presencia de YouTube Premium, membresías u otras fuentes de ingresos.



Actualiza el RPM periódicamente utilizando datos reales de YouTube Analytics.

