---
id: calculadora-tarifa-hora
entidad: Calculadora de tarifa por hora para autónomos
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de tarifa por hora para autónomos"
  description: "Calcula una tarifa mínima por hora y por día según ingresos deseados, gastos, tiempo facturable y margen de seguridad."

vectores:
  familia: Negocios
  plataforma: Negocios y autónomos
  audiencia: Autónomos y profesionales freelance
  dificultad: Intermedio
  objetivo: Fijación de tarifas
  intencion: Calcular la tarifa por hora de un autónomo

calculadora:
  inputs:
    - id: retribucion_mensual
      label: "Retribución mensual deseada antes de impuestos (€)"
      type: "number"
      placeholder: "Ej. 2500"
      min: 0
      max: 1000000
      step: 10

    - id: gastos_mensuales
      label: "Gastos profesionales mensuales (€)"
      type: "number"
      placeholder: "Ej. 500"
      min: 0
      max: 1000000
      step: 10

    - id: dias_no_disponibles
      label: "Días laborables no disponibles al año"
      type: "number"
      placeholder: "Ej. 40"
      min: 0
      max: 250
      step: 1

    - id: horas_diarias
      label: "Horas de trabajo al día"
      type: "number"
      placeholder: "Ej. 8"
      min: 1
      max: 16
      step: 0.5

    - id: porcentaje_facturable
      label: "Tiempo realmente facturable (%)"
      type: "number"
      placeholder: "Ej. 60"
      min: 1
      max: 100
      step: 0.1

    - id: margen_seguridad
      label: "Margen de seguridad (%)"
      type: "number"
      placeholder: "Ej. 10"
      min: 0
      max: 100
      step: 0.1

  algoritmo:
    pasos:
      - id: necesidad_mensual
        op: "suma"
        args: ["inputs.retribucion_mensual", "inputs.gastos_mensuales"]

      - id: necesidad_anual
        op: "multiplicacion"
        args: ["necesidad_mensual", 12]

      - id: margen_decimal
        op: "division"
        args: ["inputs.margen_seguridad", 100]

      - id: factor_seguridad
        op: "suma"
        args: [1, "margen_decimal"]

      - id: facturacion_anual_objetivo
        op: "multiplicacion"
        args: ["necesidad_anual", "factor_seguridad"]

      - id: dias_disponibles
        op: "resta"
        args: [260, "inputs.dias_no_disponibles"]

      - id: horas_trabajo_anuales
        op: "multiplicacion"
        args: ["dias_disponibles", "inputs.horas_diarias"]

      - id: porcentaje_facturable_decimal
        op: "division"
        args: ["inputs.porcentaje_facturable", 100]

      - id: horas_facturables_anuales
        op: "multiplicacion"
        args: ["horas_trabajo_anuales", "porcentaje_facturable_decimal"]

      - id: tarifa_hora
        op: "division"
        args: ["facturacion_anual_objetivo", "horas_facturables_anuales"]

      - id: tarifa_dia
        op: "multiplicacion"
        args: ["tarifa_hora", "inputs.horas_diarias"]

      - id: facturacion_mensual_objetivo
        op: "division"
        args: ["facturacion_anual_objetivo", 12]

      - id: proyecto_20_horas
        op: "multiplicacion"
        args: ["tarifa_hora", 20]

    output: "tarifa_hora"
    resultados:
      - id: tarifa_hora
        label: "Tarifa mínima por hora"
        formato: "moneda"
      - id: tarifa_dia
        label: "Tarifa orientativa por día"
        formato: "moneda"
      - id: facturacion_mensual_objetivo
        label: "Facturación mensual objetivo"
        formato: "moneda"
      - id: facturacion_anual_objetivo
        label: "Facturación anual objetivo"
        formato: "moneda"
      - id: horas_facturables_anuales
        label: "Horas facturables al año"
        formato: "numero"
        unidad: "h"
      - id: proyecto_20_horas
        label: "Proyecto de 20 horas"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Por qué no todas las horas trabajadas son facturables?"
    a: "Porque también dedicas tiempo a presupuestos, administración, captación, formación, reuniones internas y tareas que no se cobran directamente."

  - q: "¿La tarifa incluye impuestos?"
    a: "No calcula IVA, IRPF, cuota de autónomos ni impuesto sobre la renta. La retribución deseada se interpreta antes de impuestos personales y debes adaptar los gastos a tu situación."

  - q: "¿Qué días se consideran disponibles?"
    a: "La herramienta parte de 260 días laborables teóricos al año y resta vacaciones, festivos, enfermedad, formación u otros días completos que indiques."

  - q: "¿Debo cobrar siempre la tarifa mínima?"
    a: "No. Es un suelo orientativo. El precio final puede ser mayor según especialización, urgencia, riesgo, derechos de uso, valor aportado y demanda."
---

# Calculadora de tarifa por hora para autónomos

Esta herramienta estima cuánto debería facturar un profesional por hora para cubrir sus gastos y alcanzar una retribución determinada.

## Qué debes introducir

- Retribución mensual deseada antes de impuestos personales.
- Gastos profesionales mensuales.
- Días laborables que no estarán disponibles.
- Horas de trabajo diarias.
- Porcentaje del tiempo que realmente puedes facturar.
- Margen de seguridad.

## Ejemplo

Supongamos:

- Retribución deseada: **2.500 € al mes**.
- Gastos profesionales: **500 € al mes**.
- Días no disponibles: **40 al año**.
- Jornada: **8 horas**.
- Tiempo facturable: **60 %**.
- Margen de seguridad: **10 %**.

La facturación anual objetivo sería **39.600 €**. Habría aproximadamente **1.056 horas facturables** y la tarifa mínima resultante sería **37,50 € por hora**.

La tarifa diaria orientativa sería **300 €** y un proyecto de 20 horas debería presupuestarse, como mínimo matemático, en unos **750 €**.

## Por qué dividir el salario entre horas no funciona

Un profesional independiente no cobra vacaciones, administración, reuniones comerciales o periodos sin proyectos. Además, debe asumir herramientas, seguros, suministros, formación y otros gastos.

La tarifa debe sostener tanto el trabajo facturable como el tiempo necesario para mantener el negocio.

## Cómo estimar el porcentaje facturable

Como punto de partida:

- Perfil con muchos proyectos estables: porcentaje más alto.
- Profesional que dedica mucho tiempo a ventas y administración: porcentaje más bajo.
- Actividad nueva o irregular: escenario prudente.

Compara varios porcentajes en lugar de tratar uno como exacto.

## Elementos que pueden elevar el presupuesto

- Urgencia.
- Alta especialización.
- Responsabilidad o riesgo.
- Cesión de derechos.
- Muchas revisiones.
- Reuniones y coordinación.
- Alcance poco definido.

## Aviso

La herramienta es una referencia de planificación. No sustituye un cálculo fiscal ni contempla todas las cotizaciones, impuestos o particularidades de cada actividad.
