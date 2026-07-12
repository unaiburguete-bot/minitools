---
id: calculadora-indemnizacion-despido
entidad: Calculadora de indemnización por despido
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de indemnización por despido"
  description: "Estima la indemnización por despido objetivo o improcedente para contratos iniciados desde el 12 de febrero de 2012."

vectores:
  familia: Empleo
  plataforma: Empleo y salarios
  audiencia: Personas trabajadoras y empresas en España
  dificultad: Intermedio
  objetivo: Extinción del contrato
  intencion: Calcular una indemnización por despido

calculadora:
  inputs:
    - id: salario_bruto_anual
      label: "Salario bruto anual con pagas extra (€)"
      type: "number"
      placeholder: "Ej. 30000"
      min: 1
      max: 1000000
      step: 100

    - id: tipo_indemnizacion
      label: "Tipo de indemnización"
      type: "select"
      placeholder: "Selecciona un supuesto"
      options:
        - value: 20
          label: "Extinción objetiva procedente: 20 días/año, máximo 12 mensualidades"
        - value: 33
          label: "Despido improcedente: 33 días/año, máximo 24 mensualidades"

    - id: anos_antiguedad
      label: "Años completos de antigüedad"
      type: "number"
      placeholder: "Ej. 6"
      min: 0
      max: 70
      step: 1

    - id: meses_adicionales
      label: "Meses adicionales de antigüedad"
      type: "number"
      placeholder: "De 0 a 11"
      min: 0
      max: 11
      step: 1

  algoritmo:
    pasos:
      - id: meses_anos
        op: "multiplicacion"
        args: ["inputs.anos_antiguedad", 12]

      - id: meses_totales
        op: "suma"
        args: ["meses_anos", "inputs.meses_adicionales"]

      - id: anos_computables
        op: "division"
        args: ["meses_totales", 12]

      - id: salario_diario
        op: "division"
        args: ["inputs.salario_bruto_anual", 365]

      - id: dias_indemnizacion
        op: "multiplicacion"
        args: ["anos_computables", "inputs.tipo_indemnizacion"]

      - id: importe_sin_limite
        op: "multiplicacion"
        args: ["dias_indemnizacion", "salario_diario"]

      - id: diferencia_tipo
        op: "resta"
        args: ["inputs.tipo_indemnizacion", 20]

      - id: ajuste_limite_1
        op: "multiplicacion"
        args: ["diferencia_tipo", 12]

      - id: ajuste_limite_2
        op: "division"
        args: ["ajuste_limite_1", 13]

      - id: limite_mensualidades
        op: "suma"
        args: [12, "ajuste_limite_2"]

      - id: salario_mensual
        op: "division"
        args: ["inputs.salario_bruto_anual", 12]

      - id: limite_economico
        op: "multiplicacion"
        args: ["salario_mensual", "limite_mensualidades"]

      - id: indemnizacion_estimada
        op: "minimo"
        args: ["importe_sin_limite", "limite_economico"]

    output: "indemnizacion_estimada"
    resultados:
      - id: indemnizacion_estimada
        label: "Indemnización estimada"
        formato: "moneda"
      - id: dias_indemnizacion
        label: "Días de salario calculados"
        formato: "numero"
        unidad: "días"
      - id: importe_sin_limite
        label: "Importe antes del límite"
        formato: "moneda"
      - id: limite_economico
        label: "Límite económico aplicable"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿La herramienta decide si un despido es improcedente?"
    a: "No. Solo calcula una cuantía bajo el supuesto seleccionado. La calificación depende de las circunstancias, el procedimiento y, en su caso, una resolución o acuerdo."

  - q: "¿Sirve para contratos anteriores al 12 de febrero de 2012?"
    a: "No para el despido improcedente. Esos contratos pueden exigir un cálculo mixto de 45 y 33 días con límites transitorios especiales."

  - q: "¿Qué salario incluye la base anual?"
    a: "Debe incluir el salario bruto anual y la parte proporcional de las pagas extraordinarias, además de los conceptos salariales computables que correspondan."

  - q: "¿Incluye el finiquito?"
    a: "No. La indemnización y la liquidación de cantidades pendientes son conceptos distintos. Utiliza también la calculadora de finiquito y liquidación laboral."
---

# Calculadora de indemnización por despido

Esta herramienta estima dos supuestos habituales regulados por el Estatuto de los Trabajadores:

- **Extinción por causas objetivas procedente:** 20 días de salario por año de servicio, con un máximo de 12 mensualidades.
- **Despido improcedente:** 33 días de salario por año de servicio, con un máximo de 24 mensualidades, para contratos suscritos desde el 12 de febrero de 2012.

## Cómo se calcula

1. Se divide el salario bruto anual entre 365 para obtener un salario diario aproximado.
2. La antigüedad se expresa en años y meses completos.
3. Se multiplican los años computables por 20 o 33 días, según el supuesto elegido.
4. Se aplica el límite máximo de mensualidades correspondiente.

## Ejemplo

Una persona con salario bruto anual de **30.000 €** y una antigüedad de **6 años y 6 meses** tendría resultados distintos según se trate de una extinción objetiva procedente o de un despido declarado improcedente.

## Contratos anteriores a febrero de 2012

Esta primera versión no calcula el régimen transitorio del despido improcedente para contratos formalizados antes del 12 de febrero de 2012. En esos casos, el Estatuto prevé un cálculo combinado de 45 días por el periodo anterior y 33 días por el posterior, además de límites especiales. Requiere una revisión individual.

## La herramienta no califica el despido

Seleccionar «improcedente» no significa que el despido lo sea. La calificación jurídica depende de los hechos, la carta, los plazos, el procedimiento y, cuando corresponda, la decisión judicial o un acuerdo válido.

## Fuentes oficiales

- [Artículo 53.1.b del Estatuto de los Trabajadores](https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#a53): 20 días por año y máximo de 12 mensualidades para la extinción objetiva.
- [Artículo 56.1](https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#a56): 33 días por año y máximo de 24 mensualidades para el despido improcedente.
- [Disposición transitoria undécima](https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#dtundecima): régimen de contratos anteriores al 12 de febrero de 2012.

El resultado es **orientativo** y no sustituye el análisis de un profesional laboralista, sindicato, graduado social o servicio público competente.
