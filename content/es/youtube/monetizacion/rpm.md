---
id: rpm-youtube
entidad: Ingresos mensuales estimados de YouTube
version: 2.0
creado: 2026-07-01
actualizado: 2026-07-12

meta:
  title: "Calculadora de ingresos mensuales de YouTube con RPM"
  description: "Estima cuánto puede generar un canal de YouTube al mes según sus visualizaciones diarias, el número de días y su RPM."

vectores:
  plataforma: YouTube
  audiencia: Creadores
  dificultad: Básico
  objetivo: Monetización
  intencion: Calcular ingresos mensuales estimados de YouTube con visualizaciones diarias y RPM

calculadora:
  inputs:
    - id: visitas_diarias
      label: "Visualizaciones diarias"
      type: "number"
      placeholder: "Ej. 10000"
      min: 0
      step: 1

    - id: dias
      label: "Número de días"
      type: "number"
      placeholder: "Ej. 30"
      min: 1
      step: 1

    - id: rpm
      label: "RPM estimado (€)"
      type: "number"
      placeholder: "Ej. 4.25"
      min: 0
      step: 0.01

  algoritmo:
    pasos:
      - id: visitas_periodo
        op: "multiplicacion"
        args: ["inputs.visitas_diarias", "inputs.dias"]

      - id: bloques_mil
        op: "division"
        args: ["visitas_periodo", 1000]

      - id: ingresos_periodo
        op: "multiplicacion"
        args: ["bloques_mil", "inputs.rpm"]

    output: "ingresos_periodo"
    unidad: " €"
    label: "Ingresos estimados del periodo"

monetizacion:
  proveedor: "Metricool"
  red: "Programa directo de Metricool"
  etiqueta: "Recomendación con enlace de afiliado"
  titulo: "Planifica y analiza tu contenido con Metricool"
  descripcion: "Gestiona tus publicaciones, revisa métricas y organiza tu estrategia de YouTube y otras redes sociales desde un único panel."
  boton: "Conocer Metricool"
  afiliado_url: "https://i.mtr.cool/clicivo"
  aviso: "Clicivo puede recibir una comisión si contratas desde este enlace, sin coste adicional para ti."

faqs:
  - q: "¿Cómo se calculan los ingresos mensuales de YouTube?"
    a: "Se multiplican las visualizaciones diarias por el número de días, se divide el resultado entre 1.000 y se multiplica por el RPM."

  - q: "¿El resultado es una cantidad garantizada?"
    a: "No. Es una estimación basada en el RPM introducido. Los ingresos reales pueden variar por audiencia, temática, estacionalidad y visualizaciones monetizadas."
---

# Calculadora de ingresos mensuales de YouTube

Esta herramienta estima cuánto podría generar un canal durante un mes o cualquier otro periodo a partir de sus visualizaciones diarias y su RPM.

La fórmula utilizada es:

**Ingresos estimados = visualizaciones diarias × días ÷ 1.000 × RPM**

## Ejemplo práctico

Un canal recibe **10.000 visualizaciones diarias**, mantiene ese ritmo durante **30 días** y tiene un RPM de **4,25 €**:

**10.000 × 30 ÷ 1.000 × 4,25 = 1.275 €**

Los ingresos estimados del periodo serían **1.275 €**.

## Cómo utilizar esta calculadora

Introduce:

- La media de visualizaciones que recibe el canal cada día.
- El número de días que deseas proyectar.
- El RPM real o estimado del canal.

Puedes utilizar 30 días para una proyección mensual o cambiar el periodo para calcular una semana, un trimestre u otra duración.

## Qué RPM conviene introducir

Para una estimación realista, utiliza el RPM de YouTube Analytics correspondiente a un periodo reciente y comparable.

También puedes probar tres escenarios:

- Prudente, con un RPM bajo.
- Probable, con el RPM medio del canal.
- Optimista, con un RPM más alto.

## Limitaciones

La proyección presupone que el ritmo de visualizaciones y el RPM se mantienen estables durante todo el periodo. Los resultados reales pueden variar por país, temática, época del año, duración de los vídeos y porcentaje de visualizaciones monetizadas.
