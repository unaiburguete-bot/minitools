---
id: simulador-punto-equilibrio
entidad: Simulador de punto de equilibrio
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Simulador de punto de equilibrio para negocios"
  description: "Calcula cuántas unidades necesitas vender para cubrir costes y estima beneficio, facturación y margen de seguridad."

vectores:
  familia: Negocios
  plataforma: Negocios y autónomos
  audiencia: Autónomos y pequeñas empresas
  dificultad: Intermedio
  objetivo: Análisis de rentabilidad
  intencion: Calcular el punto de equilibrio de un negocio

calculadora:
  inputs:
    - id: costes_fijos
      label: "Costes fijos del periodo (€)"
      type: "number"
      placeholder: "Ej. 5000"
      min: 0
      max: 100000000
      step: 0.01

    - id: precio_unitario
      label: "Precio de venta por unidad (€)"
      type: "number"
      placeholder: "Ej. 50"
      min: 0.01
      max: 10000000
      step: 0.01

    - id: coste_variable_unitario
      label: "Coste variable por unidad (€)"
      type: "number"
      placeholder: "Ej. 20"
      min: 0
      max: 10000000
      step: 0.01

    - id: ventas_previstas
      label: "Unidades que esperas vender"
      type: "number"
      placeholder: "Ej. 250"
      min: 1
      max: 100000000
      step: 1

  validaciones:
    - op: "mayor_que"
      args: ["inputs.precio_unitario", "inputs.coste_variable_unitario"]
      mensaje: "El precio de venta debe ser mayor que el coste variable por unidad para que exista margen de contribución."

  algoritmo:
    pasos:
      - id: margen_contribucion_unitario
        op: "resta"
        args: ["inputs.precio_unitario", "inputs.coste_variable_unitario"]

      - id: unidades_equilibrio
        op: "division"
        args: ["inputs.costes_fijos", "margen_contribucion_unitario"]

      - id: facturacion_equilibrio
        op: "multiplicacion"
        args: ["unidades_equilibrio", "inputs.precio_unitario"]

      - id: margen_total_previsto
        op: "multiplicacion"
        args: ["inputs.ventas_previstas", "margen_contribucion_unitario"]

      - id: beneficio_previsto
        op: "resta"
        args: ["margen_total_previsto", "inputs.costes_fijos"]

      - id: facturacion_prevista
        op: "multiplicacion"
        args: ["inputs.ventas_previstas", "inputs.precio_unitario"]

      - id: margen_seguridad_unidades
        op: "resta"
        args: ["inputs.ventas_previstas", "unidades_equilibrio"]

      - id: proporcion_margen_seguridad
        op: "division"
        args: ["margen_seguridad_unidades", "inputs.ventas_previstas"]

      - id: margen_seguridad_porcentaje
        op: "multiplicacion"
        args: ["proporcion_margen_seguridad", 100]

    output: "unidades_equilibrio"
    resultados:
      - id: margen_contribucion_unitario
        label: "Margen de contribución por unidad"
        formato: "moneda"
      - id: unidades_equilibrio
        label: "Unidades para alcanzar el equilibrio"
        formato: "numero"
      - id: facturacion_equilibrio
        label: "Facturación de equilibrio"
        formato: "moneda"
      - id: facturacion_prevista
        label: "Facturación prevista"
        formato: "moneda"
      - id: beneficio_previsto
        label: "Beneficio o pérdida prevista"
        formato: "moneda"
      - id: margen_seguridad_porcentaje
        label: "Margen de seguridad"
        formato: "numero"
        unidad: "%"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Qué es el punto de equilibrio?"
    a: "Es el nivel de ventas en el que el margen de contribución cubre exactamente los costes fijos. Por debajo hay pérdidas y por encima comienza el beneficio."

  - q: "¿Qué es el coste variable por unidad?"
    a: "Es el coste que aumenta al vender una unidad adicional, como materiales, embalaje, comisiones o transporte directamente asociado a la venta."

  - q: "¿Por qué aparecen unidades decimales?"
    a: "El cálculo matemático puede producir decimales. En la práctica debes redondear hacia arriba para conocer el mínimo de unidades completas necesarias."

  - q: "¿Qué significa un margen de seguridad negativo?"
    a: "Significa que las ventas previstas están por debajo del punto de equilibrio y que, con esos datos, el periodo terminaría con pérdidas."
---

# Simulador de punto de equilibrio

El punto de equilibrio indica cuántas unidades debe vender un negocio para cubrir sus costes sin obtener beneficio ni pérdida.

## Datos necesarios

- Costes fijos del periodo.
- Precio de venta por unidad.
- Coste variable por unidad.
- Número de unidades que esperas vender.

Puedes trabajar por mes, trimestre o año, pero todos los datos deben corresponder al mismo periodo.

## Ejemplo

Un negocio tiene:

- Costes fijos: **5.000 €**.
- Precio de venta: **50 €**.
- Coste variable: **20 €**.
- Ventas previstas: **250 unidades**.

El margen de contribución es **30 € por unidad**.

El punto de equilibrio es aproximadamente **166,67 unidades**. Como no pueden venderse fracciones, habría que alcanzar al menos **167 unidades**.

La facturación de equilibrio sería aproximadamente **8.333,33 €**. Con 250 ventas, el beneficio estimado sería **2.500 €** y el margen de seguridad sería cercano al **33,33 %**.

## Fórmulas

**Margen de contribución = precio − coste variable**

**Unidades de equilibrio = costes fijos ÷ margen de contribución**

**Facturación de equilibrio = unidades de equilibrio × precio**

**Beneficio previsto = ventas previstas × margen de contribución − costes fijos**

## Cómo clasificar los costes

### Costes fijos

No cambian directamente con cada unidad vendida:

- Alquiler.
- Suscripciones de software.
- Nóminas fijas.
- Seguros.
- Gestoría.

### Costes variables

Aumentan con la producción o la venta:

- Materias primas.
- Embalaje.
- Comisión de venta.
- Envío asumido por el negocio.
- Mano de obra por unidad.

## Limitaciones

La simulación supone que el precio y el coste variable permanecen constantes. En la realidad pueden existir descuentos, tramos de costes, devoluciones, productos distintos o cambios de capacidad.
