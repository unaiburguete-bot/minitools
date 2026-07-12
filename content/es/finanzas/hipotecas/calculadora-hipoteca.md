---
id: calculadora-hipoteca
entidad: Calculadora de hipoteca
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de hipoteca: cuota mensual e intereses"
  description: "Calcula la cuota mensual de una hipoteca, el total pagado y los intereses estimados con un tipo fijo y cuotas constantes."

vectores:
  familia: Finanzas
  plataforma: Finanzas personales
  audiencia: Compradores de vivienda
  dificultad: Básico
  objetivo: Planificación financiera
  intencion: Calcular la cuota mensual de una hipoteca

calculadora:
  inputs:
    - id: importe
      label: "Importe de la hipoteca (€)"
      type: "number"
      placeholder: "Ej. 200000"
      min: 1000
      max: 5000000
      step: 100

    - id: interes_anual
      label: "Tipo de interés anual (%)"
      type: "number"
      placeholder: "Ej. 3"
      min: 0.01
      max: 30
      step: 0.01

    - id: plazo_anos
      label: "Plazo (años)"
      type: "number"
      placeholder: "Ej. 30"
      min: 1
      max: 50
      step: 1

  algoritmo:
    pasos:
      - id: interes_decimal
        op: "division"
        args: ["inputs.interes_anual", 100]

      - id: interes_mensual
        op: "division"
        args: ["interes_decimal", 12]

      - id: numero_cuotas
        op: "multiplicacion"
        args: ["inputs.plazo_anos", 12]

      - id: base_factor
        op: "suma"
        args: [1, "interes_mensual"]

      - id: factor
        op: "potencia"
        args: ["base_factor", "numero_cuotas"]

      - id: importe_por_interes
        op: "multiplicacion"
        args: ["inputs.importe", "interes_mensual"]

      - id: numerador
        op: "multiplicacion"
        args: ["importe_por_interes", "factor"]

      - id: denominador
        op: "resta"
        args: ["factor", 1]

      - id: cuota_mensual
        op: "division"
        args: ["numerador", "denominador"]

      - id: total_pagado
        op: "multiplicacion"
        args: ["cuota_mensual", "numero_cuotas"]

      - id: intereses_totales
        op: "resta"
        args: ["total_pagado", "inputs.importe"]

    output: "cuota_mensual"
    resultados:
      - id: cuota_mensual
        label: "Cuota mensual estimada"
        formato: "moneda"
      - id: total_pagado
        label: "Total pagado"
        formato: "moneda"
      - id: intereses_totales
        label: "Intereses totales"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Qué sistema de amortización utiliza?"
    a: "Utiliza el sistema francés: cuotas mensuales constantes mientras no cambien el tipo de interés ni las condiciones del préstamo."

  - q: "¿Incluye impuestos, seguros y otros gastos?"
    a: "No. El resultado estima capital e intereses. No incorpora tasación, seguros, impuestos, comisiones, productos vinculados ni gastos de compraventa."

  - q: "¿Sirve para una hipoteca variable?"
    a: "Solo como escenario puntual. En una hipoteca variable la cuota puede cambiar cuando se revise el índice de referencia y el tipo aplicado."

  - q: "¿Es una oferta bancaria?"
    a: "No. Es una simulación orientativa y no sustituye una oferta vinculante ni asesoramiento financiero."
---

# Calculadora de hipoteca

Esta calculadora estima la **cuota mensual**, el **total pagado** y los **intereses totales** de una hipoteca con tipo fijo y pagos mensuales constantes.

## Cómo utilizarla

Introduce:

1. El capital que necesitas financiar.
2. El tipo de interés nominal anual.
3. El plazo total en años.

La herramienta aplica el sistema de amortización francés, habitual en muchos préstamos hipotecarios: la cuota se mantiene constante mientras no cambie el tipo de interés.

## Ejemplo

Para una hipoteca de **200.000 €**, al **3 % anual** y durante **30 años**, la cuota estimada es de aproximadamente **843,21 € al mes**.

En ese escenario:

- Total pagado aproximado: **303.554,90 €**
- Intereses aproximados: **103.554,90 €**

## Qué incluye el cálculo

Incluye:

- Capital prestado.
- Tipo de interés indicado.
- Plazo.
- Cuotas mensuales constantes.

## Qué no incluye

No incorpora:

- Impuestos de la compraventa.
- Tasación.
- Seguros.
- Comisiones.
- Productos vinculados.
- Gastos de notaría, registro o gestoría.
- Cambios futuros del tipo de interés.

## Cómo comparar escenarios

Prueba distintos plazos y tipos. Un plazo mayor suele reducir la cuota mensual, pero normalmente aumenta el total de intereses. Una cuota más baja no implica necesariamente un préstamo más barato.

## Aviso

La información es orientativa. Comprueba siempre la TAE, las comisiones, los seguros y el coste total de cualquier oferta antes de contratar.
