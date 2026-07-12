---
id: calculadora-margen-beneficio
entidad: Calculadora de margen de beneficio
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de margen de beneficio y precio de venta"
  description: "Calcula beneficio por unidad, margen, markup, beneficio total y el precio necesario para alcanzar un margen objetivo."

vectores:
  familia: Negocios
  plataforma: Negocios y autónomos
  audiencia: Autónomos y pequeños negocios
  dificultad: Básico
  objetivo: Fijación de precios
  intencion: Calcular el margen de beneficio y el precio de venta

calculadora:
  inputs:
    - id: coste_unitario
      label: "Coste por unidad (€)"
      type: "number"
      placeholder: "Ej. 12"
      min: 0.01
      max: 10000000
      step: 0.01

    - id: precio_venta
      label: "Precio de venta antes del descuento (€)"
      type: "number"
      placeholder: "Ej. 25"
      min: 0.01
      max: 10000000
      step: 0.01

    - id: unidades
      label: "Unidades previstas"
      type: "number"
      placeholder: "Ej. 100"
      min: 1
      max: 100000000
      step: 1

    - id: descuento
      label: "Descuento aplicado (%)"
      type: "number"
      placeholder: "Ej. 10; escribe 0 si no hay descuento"
      min: 0
      max: 95
      step: 0.01

    - id: margen_objetivo
      label: "Margen objetivo (%)"
      type: "number"
      placeholder: "Ej. 40"
      min: 0.01
      max: 95
      step: 0.01

  algoritmo:
    pasos:
      - id: descuento_decimal
        op: "division"
        args: ["inputs.descuento", 100]

      - id: factor_precio
        op: "resta"
        args: [1, "descuento_decimal"]

      - id: precio_real
        op: "multiplicacion"
        args: ["inputs.precio_venta", "factor_precio"]

      - id: beneficio_unitario
        op: "resta"
        args: ["precio_real", "inputs.coste_unitario"]

      - id: proporcion_margen
        op: "division"
        args: ["beneficio_unitario", "precio_real"]

      - id: margen_porcentaje
        op: "multiplicacion"
        args: ["proporcion_margen", 100]

      - id: proporcion_markup
        op: "division"
        args: ["beneficio_unitario", "inputs.coste_unitario"]

      - id: markup_porcentaje
        op: "multiplicacion"
        args: ["proporcion_markup", 100]

      - id: beneficio_total
        op: "multiplicacion"
        args: ["beneficio_unitario", "inputs.unidades"]

      - id: margen_objetivo_decimal
        op: "division"
        args: ["inputs.margen_objetivo", 100]

      - id: factor_margen_objetivo
        op: "resta"
        args: [1, "margen_objetivo_decimal"]

      - id: precio_para_objetivo
        op: "division"
        args: ["inputs.coste_unitario", "factor_margen_objetivo"]

    output: "margen_porcentaje"
    resultados:
      - id: precio_real
        label: "Precio tras descuento"
        formato: "moneda"
      - id: beneficio_unitario
        label: "Beneficio por unidad"
        formato: "moneda"
      - id: margen_porcentaje
        label: "Margen sobre ventas"
        formato: "numero"
        unidad: "%"
      - id: markup_porcentaje
        label: "Markup sobre coste"
        formato: "numero"
        unidad: "%"
      - id: beneficio_total
        label: "Beneficio total previsto"
        formato: "moneda"
      - id: precio_para_objetivo
        label: "Precio para el margen objetivo"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Cuál es la diferencia entre margen y markup?"
    a: "El margen divide el beneficio entre el precio de venta. El markup divide el beneficio entre el coste. Por eso no son porcentajes intercambiables."

  - q: "¿El cálculo incluye IVA?"
    a: "No lo separa automáticamente. Introduce coste y precio con el mismo criterio: ambos sin impuestos o ambos con los impuestos que corresponda."

  - q: "¿Puedo utilizar un descuento?"
    a: "Sí. La herramienta calcula primero el precio real después del descuento y utiliza ese importe para estimar margen y beneficio."

  - q: "¿El precio objetivo garantiza rentabilidad?"
    a: "No. Solo cubre el coste unitario indicado. Añade también costes fijos, devoluciones, comisiones, impuestos y otros gastos antes de tomar una decisión."
---

# Calculadora de margen de beneficio

Esta herramienta reúne en un solo cálculo el **margen**, el **markup**, el beneficio por unidad y el precio necesario para alcanzar un margen objetivo.

## Qué datos debes introducir

- Coste directo de cada unidad.
- Precio de venta antes de descuentos.
- Unidades que esperas vender.
- Descuento previsto.
- Margen que te gustaría alcanzar.

Utiliza siempre importes comparables. Si el coste está expresado sin IVA, introduce también el precio sin IVA.

## Ejemplo práctico

Supongamos:

- Coste por unidad: **12 €**.
- Precio anunciado: **25 €**.
- Descuento: **10 %**.
- Ventas previstas: **100 unidades**.
- Margen objetivo: **40 %**.

El precio real sería **22,50 €**. El beneficio por unidad sería **10,50 €**, con un margen aproximado del **46,67 %** y un markup del **87,5 %**.

El beneficio total previsto sería **1.050 €**. Para obtener un margen del 40 % sobre un coste de 12 €, el precio mínimo matemático sería **20 €**.

## Fórmulas utilizadas

**Beneficio por unidad = precio real − coste unitario**

**Margen = beneficio ÷ precio real × 100**

**Markup = beneficio ÷ coste × 100**

**Precio para un margen objetivo = coste ÷ (1 − margen objetivo)**

## Costes que conviene añadir antes de fijar un precio

El coste unitario puede incluir:

- Compra o fabricación.
- Embalaje.
- Transporte.
- Comisiones de plataforma.
- Comisiones de pago.
- Devoluciones esperadas.
- Mano de obra directamente atribuible.

Los costes fijos se analizan mejor con el simulador de punto de equilibrio.

## Interpretación

Un margen positivo no garantiza que el negocio sea rentable. El beneficio por unidad también debe ser suficiente para cubrir alquileres, software, salarios, publicidad y otros costes fijos.
