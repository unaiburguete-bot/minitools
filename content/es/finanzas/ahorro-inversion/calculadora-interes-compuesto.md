---
id: calculadora-interes-compuesto
entidad: Calculadora de interés compuesto
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de interés compuesto con aportaciones"
  description: "Calcula el capital final, las aportaciones acumuladas y los intereses generados con aportaciones mensuales e interés compuesto."

vectores:
  familia: Finanzas
  plataforma: Finanzas personales
  audiencia: Ahorradores e inversores
  dificultad: Básico
  objetivo: Planificación de ahorro
  intencion: Calcular el interés compuesto con aportaciones mensuales

calculadora:
  inputs:
    - id: capital_inicial
      label: "Capital inicial (€)"
      type: "number"
      placeholder: "Ej. 10000"
      min: 0
      max: 10000000
      step: 100

    - id: aportacion_mensual
      label: "Aportación mensual (€)"
      type: "number"
      placeholder: "Ej. 200"
      min: 0
      max: 1000000
      step: 10

    - id: rentabilidad_anual
      label: "Rentabilidad anual estimada (%)"
      type: "number"
      placeholder: "Ej. 5"
      min: 0.01
      max: 50
      step: 0.01

    - id: plazo_anos
      label: "Plazo (años)"
      type: "number"
      placeholder: "Ej. 20"
      min: 1
      max: 80
      step: 1

  algoritmo:
    pasos:
      - id: rentabilidad_decimal
        op: "division"
        args: ["inputs.rentabilidad_anual", 100]

      - id: rentabilidad_mensual
        op: "division"
        args: ["rentabilidad_decimal", 12]

      - id: numero_meses
        op: "multiplicacion"
        args: ["inputs.plazo_anos", 12]

      - id: base_factor
        op: "suma"
        args: [1, "rentabilidad_mensual"]

      - id: factor
        op: "potencia"
        args: ["base_factor", "numero_meses"]

      - id: capital_inicial_futuro
        op: "multiplicacion"
        args: ["inputs.capital_inicial", "factor"]

      - id: factor_aportaciones_numerador
        op: "resta"
        args: ["factor", 1]

      - id: factor_aportaciones
        op: "division"
        args: ["factor_aportaciones_numerador", "rentabilidad_mensual"]

      - id: aportaciones_futuras
        op: "multiplicacion"
        args: ["inputs.aportacion_mensual", "factor_aportaciones"]

      - id: capital_final
        op: "suma"
        args: ["capital_inicial_futuro", "aportaciones_futuras"]

      - id: aportaciones_periodicas
        op: "multiplicacion"
        args: ["inputs.aportacion_mensual", "numero_meses"]

      - id: total_aportado
        op: "suma"
        args: ["inputs.capital_inicial", "aportaciones_periodicas"]

      - id: intereses_generados
        op: "resta"
        args: ["capital_final", "total_aportado"]

    output: "capital_final"
    resultados:
      - id: capital_final
        label: "Capital final estimado"
        formato: "moneda"
      - id: total_aportado
        label: "Dinero aportado"
        formato: "moneda"
      - id: intereses_generados
        label: "Rendimiento acumulado"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Qué es el interés compuesto?"
    a: "Es el crecimiento que se produce cuando los rendimientos se incorporan al capital y también generan nuevos rendimientos."

  - q: "¿Cuándo se realizan las aportaciones?"
    a: "La simulación supone que cada aportación mensual se realiza al final del mes."

  - q: "¿La rentabilidad está garantizada?"
    a: "No. Es una hipótesis constante para comparar escenarios. Las inversiones pueden subir o bajar y no ofrecen una rentabilidad fija salvo que el producto lo establezca."

  - q: "¿Incluye impuestos, inflación o comisiones?"
    a: "No. El cálculo es bruto y no descuenta fiscalidad, inflación, gastos de gestión ni otras comisiones."
---

# Calculadora de interés compuesto

Esta herramienta permite simular cuánto podría crecer un capital mediante **interés compuesto** y **aportaciones mensuales**.

## Datos que necesitas

Introduce:

- Capital inicial.
- Aportación mensual.
- Rentabilidad anual estimada.
- Número de años.

La simulación convierte la rentabilidad anual en una tasa mensual y supone que los rendimientos se reinvierten.

## Ejemplo

Con:

- **10.000 €** iniciales.
- **200 € al mes**.
- **5 % anual**.
- **20 años**.

El resultado aproximado sería:

- Capital final: **109.333,14 €**
- Dinero aportado: **58.000 €**
- Rendimiento acumulado: **51.333,14 €**

## Por qué el tiempo es importante

El interés compuesto necesita tiempo para acumularse. Durante los primeros años, la mayor parte del capital suele proceder de las aportaciones. Más adelante, los rendimientos acumulados pueden tener un peso mayor.

## Cómo comparar escenarios

Prueba cambios razonables en:

- La aportación mensual.
- El plazo.
- La rentabilidad prevista.

No utilices una rentabilidad optimista como si fuera segura. Es preferible comparar un escenario prudente, uno intermedio y otro favorable.

## Limitaciones

La herramienta no contempla:

- Variaciones anuales de rentabilidad.
- Pérdidas temporales.
- Inflación.
- Impuestos.
- Comisiones.
- Cambios en las aportaciones.

## Aviso

El resultado es una proyección matemática, no una promesa de rentabilidad ni una recomendación de inversión.
