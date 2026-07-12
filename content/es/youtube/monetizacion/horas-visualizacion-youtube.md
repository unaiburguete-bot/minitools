---
id: horas-visualizacion-youtube
entidad: Horas de visualización de YouTube
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de horas de visualización de YouTube para monetización"
  description: "Calcula cuántas horas de visualización puede generar un vídeo de YouTube según sus visitas, duración y porcentaje medio visto."

vectores:
  plataforma: YouTube
  audiencia: Creadores
  dificultad: Básico
  objetivo: Monetización
  intencion: Calcular horas de visualización de YouTube para alcanzar los requisitos de monetización

calculadora:
  inputs:
    - id: visualizaciones
      label: "Número de visualizaciones"
      type: "number"
      placeholder: "Ej. 10000"
      min: 0
      step: 1

    - id: duracion_minutos
      label: "Duración del vídeo (minutos)"
      type: "number"
      placeholder: "Ej. 8"
      min: 0.01
      step: 0.01

    - id: porcentaje_visto
      label: "Porcentaje medio visualizado"
      type: "number"
      placeholder: "Ej. 50"
      min: 0
      max: 100
      step: 0.01

  algoritmo:
    pasos:
      - id: minutos_potenciales
        op: "multiplicacion"
        args: ["inputs.visualizaciones", "inputs.duracion_minutos"]

      - id: retencion_decimal
        op: "division"
        args: ["inputs.porcentaje_visto", 100]

      - id: minutos_visualizados
        op: "multiplicacion"
        args: ["minutos_potenciales", "retencion_decimal"]

      - id: horas_visualizacion
        op: "division"
        args: ["minutos_visualizados", 60]

    output: "horas_visualizacion"
    unidad: " horas"
    label: "Horas de visualización estimadas"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Cómo se calculan las horas de visualización?"
    a: "Se multiplican las visualizaciones por la duración del vídeo y por el porcentaje medio visto. Después se divide el resultado entre 60 para convertir los minutos en horas."

  - q: "¿Las horas de Shorts cuentan para las 4.000 horas?"
    a: "Las horas obtenidas mediante visualizaciones en el feed de Shorts no cuentan para el requisito de 4.000 horas públicas del Programa para Partners."

  - q: "¿Cuántas horas se necesitan para monetizar YouTube?"
    a: "Para el reparto de ingresos publicitarios, YouTube exige actualmente 1.000 suscriptores y 4.000 horas públicas válidas en los últimos 12 meses, o la alternativa correspondiente de visualizaciones de Shorts. En países admitidos, el programa ampliado ofrece acceso previo a algunas funciones con requisitos inferiores."
---

# Calculadora de horas de visualización de YouTube

Esta herramienta estima cuántas horas de visualización puede generar un vídeo o un conjunto de vídeos según sus visualizaciones, duración y porcentaje medio visto.

La fórmula utilizada es:

**Horas = visualizaciones × duración en minutos × porcentaje visto ÷ 100 ÷ 60**

## Ejemplo práctico

Un vídeo obtiene **10.000 visualizaciones**, dura **8 minutos** y tiene un porcentaje medio visto del **50 %**:

**10.000 × 8 × 50 ÷ 100 ÷ 60 = 666,67 horas**

El vídeo habría generado aproximadamente **666,67 horas de visualización**.

## Qué datos debes introducir

### Visualizaciones

Introduce las visualizaciones del vídeo o del conjunto de vídeos que deseas analizar.

### Duración

Utiliza la duración completa del vídeo expresada en minutos. Por ejemplo:

- 8 minutos.
- 12,5 minutos.
- 20 minutos.

### Porcentaje medio visto

Este dato aparece en YouTube Analytics y representa qué parte del vídeo consume, de media, cada espectador.

## Requisitos de referencia del Programa para Partners

Para acceder al reparto de ingresos publicitarios, YouTube exige actualmente:

- 1.000 suscriptores.
- 4.000 horas públicas válidas durante los últimos 12 meses.

Como alternativa, existe una vía basada en visualizaciones públicas válidas de Shorts.

En países y regiones donde está disponible el Programa para Partners ampliado, determinadas funciones pueden desbloquearse antes con:

- 500 suscriptores.
- 3 vídeos públicos subidos durante los últimos 90 días.
- 3.000 horas públicas válidas durante los últimos 12 meses.

Los requisitos pueden cambiar y deben comprobarse siempre en YouTube Studio.

## Qué horas pueden no contar

La estimación de Clicivo es orientativa. YouTube puede excluir horas procedentes de:

- Vídeos privados.
- Vídeos ocultos o eliminados.
- Campañas publicitarias.
- Visualizaciones no válidas.
- Shorts reproducidos desde el feed de Shorts.

## Cómo utilizar el resultado

Puedes emplear esta estimación para:

- Calcular cuántas horas puede aportar un vídeo.
- Comparar diferentes niveles de retención.
- Planificar objetivos de contenido.
- Estimar cuántas visualizaciones necesitas para acercarte a 3.000 o 4.000 horas.

## Fuentes y metodología

Los requisitos de monetización y la exclusión de horas procedentes del feed de Shorts se basan en la documentación oficial del Programa para Partners de YouTube.
