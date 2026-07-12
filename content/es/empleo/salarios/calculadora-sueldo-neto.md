---
id: calculadora-sueldo-neto
entidad: Calculadora de sueldo neto 2026
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de sueldo neto 2026 en España"
  description: "Estima el sueldo neto anual, mensual y por paga con cotizaciones generales de 2026 y el porcentaje de IRPF que indiques."

vectores:
  familia: Empleo
  plataforma: Empleo y salarios
  audiencia: Personas trabajadoras en España
  dificultad: Intermedio
  objetivo: Estimación de nómina
  intencion: Calcular el sueldo neto en España en 2026

calculadora:
  inputs:
    - id: salario_bruto_anual
      label: "Salario bruto anual (€)"
      type: "number"
      placeholder: "Ej. 30000"
      min: 1
      max: 1000000
      step: 100

    - id: numero_pagas
      label: "Número de pagas al año"
      type: "number"
      placeholder: "Habitualmente 12 o 14"
      min: 1
      max: 18
      step: 1

    - id: irpf_estimado
      label: "Retención estimada de IRPF (%)"
      type: "number"
      placeholder: "Ej. 15"
      min: 0
      max: 60
      step: 0.01

    - id: desempleo_trabajador
      label: "Cotización por desempleo del trabajador (%)"
      type: "select"
      placeholder: "Selecciona el tipo de contrato"
      options:
        - value: 1.55
          label: "Contrato indefinido: 1,55 %"
        - value: 1.60
          label: "Contrato temporal: 1,60 %"

  algoritmo:
    pasos:
      - id: salario_mensual_cotizacion
        op: "division"
        args: ["inputs.salario_bruto_anual", 12]

      - id: base_mensual_cotizacion
        op: "minimo"
        args: ["salario_mensual_cotizacion", 5101.2]

      - id: base_anual_cotizacion
        op: "multiplicacion"
        args: ["base_mensual_cotizacion", 12]

      - id: cuota_comunes
        op: "multiplicacion"
        args: ["base_anual_cotizacion", 0.047]

      - id: tipo_desempleo_decimal
        op: "division"
        args: ["inputs.desempleo_trabajador", 100]

      - id: cuota_desempleo
        op: "multiplicacion"
        args: ["base_anual_cotizacion", "tipo_desempleo_decimal"]

      - id: cuota_formacion
        op: "multiplicacion"
        args: ["base_anual_cotizacion", 0.001]

      - id: cuota_mei
        op: "multiplicacion"
        args: ["base_anual_cotizacion", 0.0015]

      - id: exceso_tramo_1
        op: "resta"
        args: ["salario_mensual_cotizacion", 5101.2]

      - id: exceso_tramo_1_positivo
        op: "maximo"
        args: ["exceso_tramo_1", 0]

      - id: base_solidaridad_1
        op: "minimo"
        args: ["exceso_tramo_1_positivo", 510.12]

      - id: exceso_tramo_2
        op: "resta"
        args: ["salario_mensual_cotizacion", 5611.32]

      - id: exceso_tramo_2_positivo
        op: "maximo"
        args: ["exceso_tramo_2", 0]

      - id: base_solidaridad_2
        op: "minimo"
        args: ["exceso_tramo_2_positivo", 2040.48]

      - id: exceso_tramo_3
        op: "resta"
        args: ["salario_mensual_cotizacion", 7651.8]

      - id: base_solidaridad_3
        op: "maximo"
        args: ["exceso_tramo_3", 0]

      - id: solidaridad_1_mensual
        op: "multiplicacion"
        args: ["base_solidaridad_1", 0.0019]

      - id: solidaridad_2_mensual
        op: "multiplicacion"
        args: ["base_solidaridad_2", 0.0021]

      - id: solidaridad_3_mensual
        op: "multiplicacion"
        args: ["base_solidaridad_3", 0.0024]

      - id: solidaridad_12
        op: "suma"
        args: ["solidaridad_1_mensual", "solidaridad_2_mensual"]

      - id: solidaridad_mensual
        op: "suma"
        args: ["solidaridad_12", "solidaridad_3_mensual"]

      - id: cuota_solidaridad
        op: "multiplicacion"
        args: ["solidaridad_mensual", 12]

      - id: ss_1
        op: "suma"
        args: ["cuota_comunes", "cuota_desempleo"]

      - id: ss_2
        op: "suma"
        args: ["cuota_formacion", "cuota_mei"]

      - id: ss_3
        op: "suma"
        args: ["ss_1", "ss_2"]

      - id: seguridad_social_anual
        op: "suma"
        args: ["ss_3", "cuota_solidaridad"]

      - id: irpf_decimal
        op: "division"
        args: ["inputs.irpf_estimado", 100]

      - id: irpf_anual
        op: "multiplicacion"
        args: ["inputs.salario_bruto_anual", "irpf_decimal"]

      - id: descuentos_totales
        op: "suma"
        args: ["seguridad_social_anual", "irpf_anual"]

      - id: sueldo_neto_anual
        op: "resta"
        args: ["inputs.salario_bruto_anual", "descuentos_totales"]

      - id: sueldo_neto_mensual_medio
        op: "division"
        args: ["sueldo_neto_anual", 12]

      - id: sueldo_neto_por_paga
        op: "division"
        args: ["sueldo_neto_anual", "inputs.numero_pagas"]

    output: "sueldo_neto_anual"
    resultados:
      - id: sueldo_neto_anual
        label: "Sueldo neto anual estimado"
        formato: "moneda"
      - id: sueldo_neto_mensual_medio
        label: "Neto mensual medio"
        formato: "moneda"
      - id: sueldo_neto_por_paga
        label: "Neto medio por paga"
        formato: "moneda"
      - id: seguridad_social_anual
        label: "Cotizaciones del trabajador"
        formato: "moneda"
      - id: irpf_anual
        label: "Retención de IRPF indicada"
        formato: "moneda"

monetizacion:
  cta: ""
  afiliado_url: ""

faqs:
  - q: "¿La calculadora determina automáticamente mi IRPF?"
    a: "No. Debes introducir un porcentaje de retención estimado. El algoritmo oficial de la AEAT requiere numerosos datos personales y laborales que esta primera versión no solicita."

  - q: "¿Qué cotizaciones de 2026 incluye?"
    a: "Incluye contingencias comunes, desempleo, formación profesional, MEI y, para retribuciones superiores a la base máxima, la aportación del trabajador a la cotización adicional de solidaridad."

  - q: "¿El neto por paga será idéntico al de mi nómina?"
    a: "No necesariamente. Las cotizaciones y el IRPF pueden distribuirse de forma distinta entre pagas ordinarias y extraordinarias, y pueden existir retribuciones variables o conceptos exentos."

  - q: "¿Sirve para regímenes especiales?"
    a: "No está diseñada para empleados de hogar, artistas, agrarios, trabajadores del mar, funcionarios con particularidades ni otros sistemas especiales."
---

# Calculadora de sueldo neto 2026

Esta herramienta estima el **sueldo neto en España** a partir del salario bruto anual, el número de pagas y el porcentaje de IRPF que indiques.

## Qué calcula

La estimación descuenta:

- Contingencias comunes del trabajador: **4,70 %**.
- Desempleo: **1,55 %** en contratación indefinida o **1,60 %** en contratación temporal.
- Formación profesional: **0,10 %**.
- Mecanismo de Equidad Intergeneracional a cargo del trabajador en 2026: **0,15 %**.
- Cotización adicional de solidaridad cuando la retribución supera la base máxima mensual.
- El porcentaje de IRPF introducido por el usuario.

La base máxima mensual general utilizada para 2026 es **5.101,20 €**.

## Por qué debes indicar el IRPF

El tipo de retención no depende solo del salario. El algoritmo oficial de la Agencia Tributaria utiliza información sobre la situación personal, familiar, contractual y otras circunstancias. Para evitar una falsa precisión, Clicivo no inventa esos datos: debes introducir un porcentaje obtenido de tu nómina, de una simulación oficial o de tu asesoramiento profesional.

## Cómo interpretar los resultados

- **Sueldo neto anual:** bruto anual menos cotizaciones estimadas e IRPF indicado.
- **Neto mensual medio:** neto anual dividido entre doce.
- **Neto medio por paga:** neto anual dividido entre el número de pagas.

La cifra por paga es una media. Una nómina real de 14 pagas puede distribuir las cotizaciones y retenciones de manera diferente.

## Ejemplo orientativo

Para un salario bruto de **30.000 €**, 14 pagas, contrato indefinido y un IRPF indicado del 15 %, el resultado muestra una aproximación del neto anual y del importe medio por paga.

## Fuentes oficiales

- [Agencia Tributaria: retenciones del trabajo personal para 2026](https://sede.agenciatributaria.gob.es/Sede/Retenciones.shtml).
- [Orden PJC/297/2026, de 30 de marzo](https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296): bases y tipos de cotización de 2026.

## Limitaciones importantes

La herramienta no contempla todos los mínimos de cotización, horas extraordinarias, retribuciones en especie, dietas, atrasos, regularizaciones, reducciones, bonificaciones ni peculiaridades sectoriales. El resultado es **orientativo** y no sustituye una nómina, el servicio oficial de la AEAT ni el asesoramiento laboral o fiscal.
