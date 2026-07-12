---
id: calculadora-prestamo-personal
entidad: Calculadora de préstamo personal
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de préstamo personal: cuota y coste total"
  description: "Calcula la cuota mensual, los intereses, la comisión de apertura y el coste total estimado de un préstamo personal."

vectores:
  familia: Finanzas
  plataforma: Finanzas personales
  audiencia: Personas que comparan financiación
  dificultad: Básico
  objetivo: Comparación de préstamos
  intencion: Calcular la cuota y el coste de un préstamo personal

calculadora:
  inputs:
    - id: importe
      label: "Importe del préstamo (€)"
      type: "number"
      placeholder: "Ej. 15000"
      min: 100
      max: 1000000
      step: 100

    - id: interes_anual
      label: "Tipo de interés anual (%)"
      type: "number"
      placeholder: "Ej. 7"
      min: 0.01
      max: 100
      step: 0.01

    - id: plazo_meses
      label: "Plazo (meses)"
      type: "number"
      placeholder: "Ej. 60"
      min: 1
      max: 360
      step: 1

    - id: comision_apertura
      label: "Comisión de apertura (%)"
      type: "number"
      placeholder: "Ej. 1; escribe 0 si no existe"
      min: 0
      max: 20
      step: 0.01

  algoritmo:
    pasos:
      - id: interes_decimal
        op: "division"
        args: ["inputs.interes_anual", 100]

      - id: interes_mensual
        op: "division"
        args: ["interes_decimal", 12]

      - id: base_factor
        op: "suma"
        args: [1, "interes_mensual"]

      - id: factor
        op: "potencia"
        args: ["base_factor", "inputs.plazo_meses"]

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

      - id: total_cuotas
        op: "multiplicacion"
        args: ["cuota_mensual", "inputs.plazo_meses"]

      - id: intereses_totales
        op: "resta"
        args: ["total_cuotas", "inputs.importe"]

      - id: comision_decimal
        op: "division"
        args: ["inputs.comision_apertura", 100]

      - id: comision_importe
        op: "multiplicacion"
        args: ["inputs.importe", "comision_decimal"]

      - id: coste_financiacion
        op: "suma"
        args: ["intereses_totales", "comision_importe"]

      - id: coste_total
        op: "suma"
        args: ["total_cuotas", "comision_importe"]

    output: "cuota_mensual"
    resultados:
      - id: cuota_mensual
        label: "Cuota mensual estimada"
        formato: "moneda"
      - id: intereses_totales
        label: "Intereses totales"
        formato: "moneda"
      - id: comision_importe
        label: "Comisión de apertura"
        formato: "moneda"
      - id: coste_total
        label: "Total a devolver"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Qué sistema de amortización utiliza?"
    a: "Utiliza cuotas mensuales constantes mediante el sistema francés, siempre que el tipo de interés no cambie."

  - q: "¿El resultado es la TAE?"
    a: "No. La herramienta muestra una estimación de cuota y coste con los datos introducidos. La TAE puede incluir otros gastos, seguros y condiciones."

  - q: "¿Debo comparar solo la cuota?"
    a: "No. Una cuota baja puede deberse a un plazo más largo. Conviene comparar la TAE, el total a devolver, las comisiones y las condiciones de cancelación."

  - q: "¿La comisión se financia?"
    a: "La simulación la suma al coste total como un pago adicional. Algunas entidades pueden descontarla del importe entregado o tratarla de otra manera."
---

# Calculadora de préstamo personal

Esta calculadora estima la **cuota mensual**, los **intereses**, la **comisión de apertura** y el **total a devolver** de un préstamo personal.

## Cómo utilizarla

Introduce:

1. Importe solicitado.
2. Tipo de interés nominal anual.
3. Plazo en meses.
4. Comisión de apertura.

Escribe **0** en la comisión cuando la oferta no la incluya.

## Ejemplo

Para un préstamo de **15.000 €**, al **7 % anual**, durante **60 meses** y con una comisión de apertura del **1 %**:

- Cuota mensual estimada: **297,02 €**
- Intereses aproximados: **2.821,08 €**
- Comisión de apertura: **150 €**
- Total a devolver: **17.971,08 €**

## Cuota frente a coste total

Una cuota mensual más baja no siempre significa una financiación más barata. Al ampliar el plazo:

- La cuota suele bajar.
- Se pagan más mensualidades.
- El coste total puede aumentar.

## Qué debes comparar

Antes de contratar, revisa:

- TAE.
- Total a devolver.
- Comisiones.
- Seguros o productos vinculados.
- Penalizaciones o compensaciones por amortización anticipada.
- Consecuencias por impago.

## Diferencia entre TIN y TAE

El TIN refleja el tipo de interés nominal. La TAE intenta expresar el coste efectivo anual incorporando la periodicidad y determinados gastos. Esta calculadora no sustituye la TAE informada por la entidad.

## Aviso

El resultado es orientativo. Las condiciones reales dependen del contrato, las comisiones y otros costes de cada oferta.
