---
id: calcular-rpm-youtube
entidad: RPM real de YouTube
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de RPM de YouTube con ingresos y visualizaciones"
  description: "Calcula el RPM real de un canal de YouTube introduciendo los ingresos obtenidos y el número de visualizaciones."

vectores:
  plataforma: YouTube
  audiencia: Creadores
  dificultad: Básico
  objetivo: Monetización
  intencion: Calcular el RPM real de YouTube a partir de ingresos y visualizaciones

calculadora:
  inputs:
    - id: ingresos
      label: "Ingresos obtenidos (€)"
      type: "number"
      placeholder: "Ej. 425"
      min: 0
      step: 0.01

    - id: visualizaciones
      label: "Número de visualizaciones"
      type: "number"
      placeholder: "Ej. 100000"
      min: 1
      step: 1

  algoritmo:
    pasos:
      - id: ingresos_por_visita
        op: "division"
        args: ["inputs.ingresos", "inputs.visualizaciones"]

      - id: rpm_real
        op: "multiplicacion"
        args: ["ingresos_por_visita", 1000]

    output: "rpm_real"
    unidad: " €"
    label: "RPM estimado"

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
  - q: "¿Cómo se calcula el RPM de YouTube?"
    a: "Se dividen los ingresos obtenidos entre las visualizaciones y se multiplica el resultado por 1.000."

  - q: "¿Debo usar visualizaciones totales o monetizadas?"
    a: "Para calcular el RPM general del canal, utiliza las visualizaciones totales del periodo correspondiente a los ingresos introducidos."
---

# Calculadora de RPM de YouTube

Esta herramienta calcula el RPM real de un canal de YouTube a partir de los ingresos obtenidos y del número total de visualizaciones.

La fórmula utilizada es:

**RPM = ingresos ÷ visualizaciones × 1.000**

## Ejemplo práctico

Un canal obtiene **425 €** con **100.000 visualizaciones**:

**425 ÷ 100.000 × 1.000 = 4,25 €**

El RPM estimado sería de **4,25 €**.

## Qué datos debes introducir

Utiliza ingresos y visualizaciones del mismo periodo. Por ejemplo:

- Ingresos de los últimos 28 días.
- Visualizaciones de esos mismos 28 días.

No mezcles periodos distintos porque el resultado dejaría de ser comparable.

## Para qué sirve conocer el RPM

El RPM permite:

- Comparar el rendimiento de distintos periodos.
- Estimar ingresos futuros.
- Detectar cambios en la monetización.
- Comparar vídeos o temáticas.
- Planificar objetivos de visualizaciones.

## Diferencia entre RPM y CPM

El CPM representa lo que pagan los anunciantes por 1.000 impresiones publicitarias.

El RPM representa lo que realmente obtiene el creador por cada 1.000 visualizaciones.

Por eso el RPM suele ser la métrica más útil para estimar ingresos reales.

## Limitaciones

El resultado depende de que los ingresos y las visualizaciones correspondan exactamente al mismo periodo. También puede variar por país, temática, época del año, duración de los vídeos y porcentaje de visualizaciones monetizadas.
