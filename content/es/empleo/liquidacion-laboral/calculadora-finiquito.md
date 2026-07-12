---
id: calculadora-finiquito
entidad: Calculadora de finiquito y liquidación laboral
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de finiquito y liquidación laboral"
  description: "Estima las cantidades pendientes al finalizar un contrato: salario, vacaciones, pagas extraordinarias, otros conceptos y deducciones."

vectores:
  familia: Empleo
  plataforma: Empleo y salarios
  audiencia: Personas trabajadoras y empresas en España
  dificultad: Intermedio
  objetivo: Liquidación del contrato
  intencion: Calcular el finiquito y la liquidación laboral

calculadora:
  inputs:
    - id: salario_bruto_anual
      label: "Salario bruto anual con pagas extra (€)"
      type: "number"
      placeholder: "Ej. 28000"
      min: 1
      max: 1000000
      step: 100

    - id: dias_salario_pendiente
      label: "Días de salario pendientes"
      type: "number"
      placeholder: "Ej. 12"
      min: 0
      max: 62
      step: 0.01

    - id: dias_vacaciones_pendientes
      label: "Días de vacaciones pendientes"
      type: "number"
      placeholder: "Ej. 8"
      min: 0
      max: 90
      step: 0.01

    - id: pagas_extra_pendientes
      label: "Parte pendiente de pagas extraordinarias (€)"
      type: "number"
      placeholder: "Escribe 0 si están prorrateadas"
      min: 0
      max: 1000000
      step: 0.01

    - id: otros_importes
      label: "Otros importes pendientes (€)"
      type: "number"
      placeholder: "Comisiones, variables u otros; 0 si no hay"
      min: 0
      max: 1000000
      step: 0.01

    - id: deducciones
      label: "Deducciones o anticipos (€)"
      type: "number"
      placeholder: "Escribe 0 si no hay"
      min: 0
      max: 1000000
      step: 0.01

  algoritmo:
    pasos:
      - id: salario_diario
        op: "division"
        args: ["inputs.salario_bruto_anual", 365]

      - id: salario_pendiente
        op: "multiplicacion"
        args: ["salario_diario", "inputs.dias_salario_pendiente"]

      - id: vacaciones_pendientes
        op: "multiplicacion"
        args: ["salario_diario", "inputs.dias_vacaciones_pendientes"]

      - id: subtotal_1
        op: "suma"
        args: ["salario_pendiente", "vacaciones_pendientes"]

      - id: subtotal_2
        op: "suma"
        args: ["inputs.pagas_extra_pendientes", "inputs.otros_importes"]

      - id: total_devengado
        op: "suma"
        args: ["subtotal_1", "subtotal_2"]

      - id: liquidacion_estimada
        op: "resta"
        args: ["total_devengado", "inputs.deducciones"]

    output: "liquidacion_estimada"
    resultados:
      - id: liquidacion_estimada
        label: "Liquidación bruta estimada"
        formato: "moneda"
      - id: salario_pendiente
        label: "Salario pendiente"
        formato: "moneda"
      - id: vacaciones_pendientes
        label: "Vacaciones pendientes"
        formato: "moneda"
      - id: total_devengado
        label: "Total antes de deducciones"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿Finiquito e indemnización son lo mismo?"
    a: "No. La liquidación recoge cantidades pendientes al terminar el contrato. La indemnización solo procede en determinados supuestos y debe calcularse por separado."

  - q: "¿Qué salario diario utiliza?"
    a: "Divide el salario bruto anual, incluyendo las pagas extraordinarias, entre 365. Es una aproximación general; el convenio colectivo y los conceptos variables pueden modificar la base aplicable."

  - q: "¿Incluye IRPF y Seguridad Social?"
    a: "No los calcula automáticamente. El resultado mostrado es bruto y permite restar manualmente anticipos u otras deducciones conocidas."

  - q: "¿Cómo sé cuántos días de vacaciones quedan?"
    a: "Debes comparar los días generados según contrato o convenio con los ya disfrutados. Si existe discrepancia, revisa nóminas, calendario laboral y convenio aplicable."
---

# Calculadora de finiquito y liquidación laboral

La **liquidación laboral** reúne las cantidades que pueden quedar pendientes cuando finaliza una relación de trabajo. El término habitual es *finiquito*, mientras que el Estatuto de los Trabajadores se refiere al documento de liquidación de las cantidades adeudadas.

## Conceptos incluidos

La herramienta suma:

- Salario correspondiente a días trabajados y todavía no abonados.
- Vacaciones generadas y no disfrutadas.
- Parte pendiente de pagas extraordinarias.
- Comisiones, variables u otros importes que introduzcas.

Después resta las deducciones o anticipos indicados.

## Cómo calcular cada dato

### Días de salario pendientes

Introduce los días trabajados del último periodo que todavía no estén pagados.

### Vacaciones pendientes

Introduce únicamente los días generados y no disfrutados. El número anual puede depender del convenio y de si se expresa en días naturales o laborables.

### Pagas extraordinarias

Si están prorrateadas en las nóminas, escribe **0**. Si no lo están, introduce la parte proporcional que consideres pendiente según el periodo de devengo.

## Diferencia entre liquidación e indemnización

La liquidación puede existir cualquiera que sea la causa de finalización del contrato. La indemnización, en cambio, depende del tipo de extinción y de sus requisitos legales. Por eso Clicivo las presenta como herramientas separadas.

## Base legal y límites

El [artículo 49.2 del Estatuto de los Trabajadores](https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#a49) establece que, al comunicar la extinción, el empresario debe acompañar una propuesta del documento de liquidación de las cantidades adeudadas y reconoce la posibilidad de solicitar la presencia de un representante legal al firmar el recibo del finiquito.

El resultado de Clicivo es una **estimación bruta**. No determina si existen otros conceptos previstos por convenio, contrato, sentencia o acuerdo, ni calcula automáticamente impuestos y cotizaciones.
