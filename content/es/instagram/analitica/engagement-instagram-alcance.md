---
id: engagement-instagram-alcance
entidad: Engagement de Instagram por alcance
version: 1.0
creado: 2026-07-12
actualizado: 2026-07-12

meta:
  title: "Calculadora de engagement de Instagram por alcance"
  description: "Calcula la tasa de engagement de una publicación de Instagram usando alcance, Me gusta, comentarios, guardados y compartidos."

vectores:
  plataforma: Instagram
  audiencia: Creadores y agencias
  dificultad: Básico
  objetivo: Analítica
  intencion: Calcular el engagement de Instagram por alcance

calculadora:
  inputs:
    - id: alcance
      label: "Cuentas alcanzadas"
      type: "number"
      placeholder: "Ej. 12000"
      min: 1
      step: 1

    - id: likes
      label: "Me gusta"
      type: "number"
      placeholder: "Ej. 420"
      min: 0
      step: 1

    - id: comentarios
      label: "Comentarios"
      type: "number"
      placeholder: "Ej. 28"
      min: 0
      step: 1

    - id: guardados
      label: "Guardados"
      type: "number"
      placeholder: "Ej. 64"
      min: 0
      step: 1

    - id: compartidos
      label: "Compartidos"
      type: "number"
      placeholder: "Ej. 38"
      min: 0
      step: 1

  algoritmo:
    pasos:
      - id: interacciones_visibles
        op: "suma"
        args: ["inputs.likes", "inputs.comentarios"]

      - id: interacciones_valor
        op: "suma"
        args: ["inputs.guardados", "inputs.compartidos"]

      - id: interacciones_totales
        op: "suma"
        args: ["interacciones_visibles", "interacciones_valor"]

      - id: proporcion_engagement
        op: "division"
        args: ["interacciones_totales", "inputs.alcance"]

      - id: engagement_porcentaje
        op: "multiplicacion"
        args: ["proporcion_engagement", 100]

    output: "engagement_porcentaje"
    unidad: "%"
    label: "Engagement por alcance"

monetizacion:
  proveedor: "Metricool"
  red: "Programa directo de Metricool"
  etiqueta: "Recomendación con enlace de afiliado"
  titulo: "Analiza y organiza tu estrategia de Instagram"
  descripcion: "Programa contenido, revisa el rendimiento de tus publicaciones y gestiona tus redes sociales desde un único panel con Metricool."
  boton: "Conocer Metricool"
  afiliado_url: "https://i.mtr.cool/clicivo"
  aviso: "Clicivo puede recibir una comisión si contratas desde este enlace, sin coste adicional para ti."

faqs:
  - q: "¿Qué fórmula utiliza esta calculadora?"
    a: "Suma Me gusta, comentarios, guardados y compartidos; divide el total entre las cuentas alcanzadas y multiplica el resultado por 100."

  - q: "¿Dónde encuentro el alcance, los guardados y los compartidos?"
    a: "Estas métricas se consultan en las estadísticas de la publicación dentro de Instagram Insights, siempre que la cuenta tenga acceso a ellas."

  - q: "¿Es mejor calcular el engagement por alcance o por seguidores?"
    a: "Depende del análisis. El cálculo por alcance mide la respuesta de quienes vieron el contenido; el cálculo por seguidores relaciona las interacciones con el tamaño total de la comunidad."
---

# Calculadora de engagement de Instagram por alcance

Esta calculadora mide qué porcentaje de las cuentas alcanzadas realizó alguna de las interacciones incluidas: Me gusta, comentarios, guardados o compartidos.

La fórmula utilizada es:

**Engagement por alcance = (Me gusta + comentarios + guardados + compartidos) ÷ alcance × 100**

## Ejemplo práctico

Una publicación registra:

- **12.000 cuentas alcanzadas**
- **420 Me gusta**
- **28 comentarios**
- **64 guardados**
- **38 compartidos**

Las interacciones totales serían:

**420 + 28 + 64 + 38 = 550**

El cálculo sería:

**550 ÷ 12.000 × 100 = 4,58 %**

El engagement por alcance estimado sería **4,58 %**.

## Cuándo utilizar esta métrica

El engagement por alcance resulta especialmente útil para analizar publicaciones concretas porque relaciona las interacciones con las personas que realmente vieron el contenido.

Puede ayudarte a:

- Comparar publicaciones de una misma cuenta.
- Analizar formatos con alcances diferentes.
- Detectar contenido que genera guardados y compartidos.
- Evaluar una campaña o colaboración concreta.
- Observar la evolución del rendimiento con una fórmula constante.

## Cómo obtener los datos

Abre las estadísticas de la publicación en Instagram e introduce:

1. Las cuentas alcanzadas.
2. Los Me gusta.
3. Los comentarios.
4. Los guardados.
5. Los compartidos.

Procura comparar publicaciones del mismo formato y de periodos similares. Un Reel, una imagen y un carrusel pueden tener patrones de consumo distintos.

## Por qué incluimos guardados y compartidos

Los Me gusta y los comentarios son interacciones visibles, pero los guardados y compartidos también reflejan una acción directa sobre el contenido.

Esta calculadora suma las cuatro métricas para ofrecer una visión más amplia de la respuesta generada por la publicación.

## Diferencia frente al engagement por seguidores

El engagement por seguidores utiliza el tamaño total de la comunidad como denominador.

El engagement por alcance utiliza únicamente las cuentas que vieron la publicación.

Por eso, los resultados de ambas calculadoras no deben compararse como si fueran la misma métrica. Lo más útil es elegir una fórmula y aplicarla de forma consistente al analizar la evolución.

## Limitaciones del resultado

El porcentaje no determina por sí solo si una publicación es buena o mala. También conviene observar:

- El objetivo del contenido.
- El tipo de publicación.
- Los clics o conversiones obtenidos.
- La calidad de los comentarios.
- La evolución respecto a publicaciones comparables.

Utiliza el resultado como una métrica de seguimiento, no como una valoración absoluta de una cuenta.
