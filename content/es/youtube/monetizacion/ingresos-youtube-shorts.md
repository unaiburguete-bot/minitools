---
id: ingresos-youtube-shorts
entidad: Ingresos estimados de YouTube Shorts
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de ingresos de YouTube Shorts por RPM"
  description: "Estima cuánto dinero pueden generar tus YouTube Shorts introduciendo las visualizaciones con interacción y el RPM real o previsto."

vectores:
  plataforma: YouTube
  audiencia: Creadores
  dificultad: Básico
  objetivo: Monetización
  intencion: Calcular ingresos estimados de YouTube Shorts según visualizaciones con interacción y RPM

calculadora:
  inputs:
    - id: visualizaciones
      label: "Visualizaciones con interacción"
      type: "number"
      placeholder: "Ej. 1000000"
      min: 0
      step: 1

    - id: rpm
      label: "RPM de Shorts (€)"
      type: "number"
      placeholder: "Ej. 0.08"
      min: 0
      step: 0.01

  algoritmo:
    pasos:
      - id: bloques_mil
        op: "division"
        args: ["inputs.visualizaciones", 1000]

      - id: ingresos_estimados
        op: "multiplicacion"
        args: ["bloques_mil", "inputs.rpm"]

    output: "ingresos_estimados"
    unidad: " €"
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
  - q: "¿Cómo se calculan los ingresos de YouTube Shorts?"
    a: "Se dividen las visualizaciones con interacción entre 1.000 y se multiplica el resultado por el RPM de Shorts introducido."

  - q: "¿Dónde puedo encontrar mi RPM de Shorts?"
    a: "Puedes consultarlo en YouTube Studio, dentro de Analytics e Ingresos, filtrando el contenido por Shorts."

  - q: "¿El resultado es una cantidad garantizada?"
    a: "No. Es una estimación basada en el RPM introducido. Los ingresos reales pueden variar por audiencia, país, periodo y reparto de ingresos."
---

# Calculadora de ingresos de YouTube Shorts

Esta herramienta estima cuánto podrían generar tus Shorts a partir de las visualizaciones con interacción y del RPM de Shorts.

La fórmula utilizada es:

**Ingresos estimados = visualizaciones con interacción ÷ 1.000 × RPM**

## Ejemplo práctico

Un canal obtiene **1.000.000 de visualizaciones con interacción** y utiliza un RPM de ejemplo de **0,08 €**:

**1.000.000 ÷ 1.000 × 0,08 = 80 €**

Los ingresos estimados serían **80 €**.

Este RPM se utiliza solo para mostrar el cálculo. No representa una media garantizada del mercado.

## Qué visualizaciones debes introducir

Utiliza las visualizaciones con interacción que aparecen en YouTube Analytics para Shorts. YouTube emplea esta métrica para calcular el RPM y el reparto de ingresos de Shorts.

## Qué RPM debes utilizar

Para conseguir una estimación útil, introduce el RPM real de Shorts que aparece en YouTube Studio durante un periodo comparable.

Si todavía no tienes datos propios, puedes probar varios escenarios:

- Un RPM prudente.
- Un RPM intermedio.
- Un RPM optimista.

Los valores utilizados serán hipótesis, no predicciones de Clicivo.

## Cómo funciona la monetización de Shorts

YouTube agrupa los ingresos publicitarios del feed de Shorts, asigna una parte a los creadores según sus visualizaciones con interacción elegibles y aplica el reparto correspondiente al creador.

La calculadora no reproduce todo ese proceso. Utiliza directamente el RPM final introducido para ofrecer una estimación sencilla.

## Limitaciones

El resultado puede variar por:

- País y composición de la audiencia.
- Periodo analizado.
- Visualizaciones con interacción elegibles.
- Uso de música.
- Rendimiento publicitario.
- Ingresos de YouTube Premium.

## Fuentes y metodología

- [YouTube Help: políticas de monetización de Shorts](https://support.google.com/youtube/answer/12504220?hl=es)
- [YouTube Help: definición de RPM e ingresos publicitarios](https://support.google.com/youtube/answer/9314357?hl=es)
