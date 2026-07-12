---
id: ingresos-youtube
entidad: Ingresos estimados de YouTube
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de ingresos de YouTube por visitas y RPM"
  description: "Estima cuánto dinero puede generar un canal de YouTube introduciendo sus visualizaciones y el RPM real o previsto."

vectores:
  plataforma: YouTube
  audiencia: Creadores
  dificultad: Básico
  objetivo: Monetización
  intencion: Calcular ingresos estimados de YouTube según visitas y RPM

calculadora:
  inputs:
    - id: visitas
      label: "Número de visualizaciones"
      type: "number"
      placeholder: "Ej. 100000"
      min: 0
      step: 1
    - id: rpm
      label: "RPM estimado (€)"
      type: "number"
      placeholder: "Ej. 4.25"
      min: 0
      step: 0.01

  algoritmo:
    pasos:
      - id: bloques_mil
        op: "division"
        args: ["inputs.visitas", 1000]
      - id: ingresos_estimados
        op: "multiplicacion"
        args: ["bloques_mil", "inputs.rpm"]

    output: "ingresos_estimados"
    unidad: "€"
    label: "Ingresos estimados"

monetizacion:
  proveedor: "Metricool"
  red: "Programa directo de Metricool"
  etiqueta: "Recomendación con enlace de afiliado"
  titulo: "Planifica y analiza tu contenido con Metricool"
  descripcion: "Gestiona tus publicaciones, revisa métricas y organiza tu estrategia de YouTube y otras redes sociales desde un único panel."
  boton: "Conocer Metricool"
  afiliado_url: "https://i.mtr.cool/clicivo"
  aviso: "Clicivo puede recibir una comisión si contratas desde este enlace, sin coste adicional para ti."

faqs:
  - q: "¿Cómo se calculan los ingresos estimados de YouTube?"
    a: "Se dividen las visualizaciones entre 1.000 y se multiplica el resultado por el RPM del canal."
  - q: "¿El resultado coincide exactamente con lo que paga YouTube?"
    a: "No necesariamente. Es una estimación basada en el RPM introducido."
---

# Calculadora de ingresos de YouTube

Esta calculadora estima cuánto podría generar un canal de YouTube a partir de sus visualizaciones y de un RPM conocido o previsto.

**Ingresos estimados = visualizaciones ÷ 1.000 × RPM**

## Ejemplo práctico

100.000 visualizaciones con un RPM de 4,25 €:

**100.000 ÷ 1.000 × 4,25 = 425 €**

## Qué RPM debes introducir

Utiliza preferentemente el RPM que aparece en YouTube Analytics durante un periodo similar.

## Diferencia entre RPM y CPM

El CPM representa el importe pagado por los anunciantes por cada 1.000 impresiones publicitarias.

El RPM representa los ingresos reales obtenidos por el creador por cada 1.000 visualizaciones.

## Limitaciones

El resultado es una estimación. Los ingresos pueden variar según el país, la temática, la época del año, la duración de los vídeos y el porcentaje de visualizaciones monetizadas.
