from __future__ import annotations

import html
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TOOLS = json.loads((ROOT / "content" / "tools.json").read_text(encoding="utf-8"))
SITE = json.loads((ROOT / "config" / "site.json").read_text(encoding="utf-8"))
ORIGIN = SITE["site_origin"].rstrip("/")
UPDATED = SITE["updated"]

CATEGORY_META = {
    "PDF y documentos": {"path": "/es/pdf/", "icon": "▤", "description": "Une, divide, organiza y convierte documentos PDF sin subirlos a Clicivo."},
    "Imágenes": {"path": "/es/imagenes/", "icon": "▧", "description": "Comprime, redimensiona, convierte, recorta y limpia imágenes en tu navegador."},
    "Texto y productividad": {"path": "/es/productividad/", "icon": "⌁", "description": "Texto, comparación, códigos QR y pequeñas utilidades para el trabajo diario."},
    "Redes sociales": {"path": "/es/redes-sociales/", "icon": "✦", "description": "Analítica, monetización y utilidades para Instagram, YouTube y TikTok."},
    "Finanzas": {"path": "/es/finanzas/", "icon": "€", "description": "Simuladores de ahorro, inversión, hipotecas y préstamos."},
    "Negocios": {"path": "/es/negocios/", "icon": "↗", "description": "Precios, rentabilidad y planificación para profesionales y pequeños negocios."},
    "Empleo": {"path": "/es/empleo/", "icon": "✓", "description": "Salarios, vacaciones, finiquito, indemnización y costes laborales."},
}

SEGMENT_LABELS = {
    "es": "Herramientas",
    "pdf": "PDF y documentos", "unir-dividir": "Unir y dividir", "organizar": "Organizar PDF", "convertir": "Convertir",
    "imagenes": "Imágenes", "optimizar": "Optimizar", "redimensionar": "Redimensionar", "editar": "Editar", "privacidad": "Privacidad",
    "productividad": "Texto y productividad", "qr": "Códigos QR",
    "instagram": "Instagram", "youtube": "YouTube", "tiktok": "TikTok",
    "analitica": "Analítica", "texto": "Texto", "monetizacion": "Monetización",
    "finanzas": "Finanzas", "ahorro-inversion": "Ahorro e inversión", "hipotecas": "Hipotecas", "prestamos": "Préstamos",
    "negocios": "Negocios", "autonomos": "Autónomos", "precios": "Precios", "rentabilidad": "Rentabilidad",
    "empleo": "Empleo", "extincion-contrato": "Extinción de contrato", "liquidacion-laboral": "Liquidación laboral",
    "salarios": "Salarios", "vacaciones": "Vacaciones", "coste-empresa": "Coste de empresa",
}

PLATFORM_ICONS = {
    "PDF": "▤", "Imágenes": "▧", "Texto": "Aa", "Códigos QR": "▦",
    "Instagram": "◎", "YouTube": "▶", "TikTok": "♪", "Ahorro e inversión": "◈",
    "Hipotecas": "⌂", "Préstamos": "¤", "Autónomos": "◷", "Precios": "%",
    "Rentabilidad": "↗", "Extinción de contrato": "§", "Liquidación laboral": "≋",
    "Salarios": "€", "Vacaciones": "☀", "Coste de empresa": "▦",
}

FORM_SCHEMAS = {
    "instagram-growth": [
        ("number", "initial", "Seguidores iniciales", 8000, 0, None, 1, "Número al inicio del periodo."),
        ("number", "final", "Seguidores finales", 8640, 0, None, 1, "Número al final del periodo."),
        ("number", "days", "Días analizados", 30, 1, 3650, 1, "Duración del periodo."),
        ("number", "target", "Objetivo de seguidores", 10000, 0, None, 1, "Opcional: tiempo estimado al ritmo actual."),
    ],
    "instagram-engagement-followers": [
        ("number", "followers", "Seguidores", 40000, 1, None, 1, "Tamaño de la cuenta."),
        ("number", "likes", "Me gusta medios", 900, 0, None, 1, "Media por publicación."),
        ("number", "comments", "Comentarios medios", 120, 0, None, 1, "Media por publicación."),
        ("number", "saves", "Guardados medios", 110, 0, None, 1, "Opcional."),
        ("number", "shares", "Compartidos medios", 70, 0, None, 1, "Opcional."),
        ("number", "posts", "Publicaciones analizadas", 10, 1, 500, 1, "Para contextualizar la muestra."),
    ],
    "instagram-engagement-reach": [
        ("number", "reach", "Alcance", 25000, 1, None, 1, "Cuentas alcanzadas."),
        ("number", "likes", "Me gusta", 1100, 0, None, 1, "Interacciones de la pieza."),
        ("number", "comments", "Comentarios", 120, 0, None, 1, "Interacciones de la pieza."),
        ("number", "saves", "Guardados", 160, 0, None, 1, "Interacciones de la pieza."),
        ("number", "shares", "Compartidos", 120, 0, None, 1, "Interacciones de la pieza."),
    ],
    "instagram-fonts": [("textarea", "text", "Escribe tu texto", "Tu mensaje para Instagram", None, None, None, "La conversión se actualiza al escribir.")],
    "instagram-counter": [
        ("select", "preset", "Referencia", "150", None, None, None, [("150", "Biografía · referencia 150"), ("2200", "Texto largo · referencia 2.200"), ("30", "Nombre de usuario · referencia 30"), ("custom", "Límite personalizado")]),
        ("number", "customLimit", "Límite personalizado", 500, 1, 100000, 1, "Solo se usa al elegir la opción personalizada."),
        ("textarea", "text", "Texto", "Escribe o pega aquí…", None, None, None, "El conteo se actualiza al instante."),
    ],
    "instagram-spaces": [("textarea", "text", "Texto original", "Primer párrafo\n\nSegundo párrafo\n\nTercer párrafo", None, None, None, "Deja líneas vacías entre párrafos.")],
    "tiktok-engagement": [
        ("select", "basis", "Calcular respecto a", "views", None, None, None, [("views", "Visualizaciones"), ("followers", "Seguidores")]),
        ("number", "base", "Visualizaciones o seguidores", 300000, 1, None, 1, "Usa la base elegida."),
        ("number", "likes", "Me gusta", 10000, 0, None, 1, "Del mismo vídeo o promedio."),
        ("number", "comments", "Comentarios", 600, 0, None, 1, "Del mismo vídeo o promedio."),
        ("number", "shares", "Compartidos", 900, 0, None, 1, "Del mismo vídeo o promedio."),
        ("number", "saves", "Guardados", 500, 0, None, 1, "Opcional."),
    ],
    "tiktok-income": [
        ("number", "views", "Visualizaciones cualificadas del periodo", 500000, 0, None, 1, "Usa la cifra elegible del mismo periodo."),
        ("number", "rpmLow", "RPM bajo (€)", 0.3, 0, 1000, 0.01, "Escenario prudente introducido por ti."),
        ("number", "rpm", "RPM central (€)", 0.5, 0, 1000, 0.01, "Usa tu RPM real cuando lo tengas."),
        ("number", "rpmHigh", "RPM alto (€)", 0.8, 0, 1000, 0.01, "Escenario alto, no una promesa."),
        ("number", "months", "Meses del periodo", 1, 1, 120, 1, "Permite normalizar la media mensual."),
        ("number", "targetIncome", "Objetivo de ingresos (€)", 500, 0, None, 0.01, "Calcula las vistas necesarias con el RPM central."),
    ],
    "youtube-rpm-revenue": [
        ("number", "revenue", "Ingresos del periodo (€)", 425, 0, None, 0.01, "Ingresos del mismo periodo que las visualizaciones."),
        ("number", "views", "Visualizaciones del periodo", 100000, 1, None, 1, "No mezcles periodos ni formatos distintos."),
        ("number", "targetViews", "Visualizaciones objetivo", 250000, 0, None, 1, "Proyección opcional usando el RPM calculado."),
    ],
    "youtube-watch-hours": [
        ("number", "views", "Visualizaciones", 10000, 0, None, 1, "Visualizaciones públicas estimadas."),
        ("number", "duration", "Duración media del vídeo (min)", 8, 0.01, 1440, 0.01, "Duración completa."),
        ("number", "retention", "Porcentaje medio visto (%)", 50, 0, 100, 0.1, "Dato de Analytics."),
        ("select", "target", "Objetivo de referencia", "4000", None, None, None, [("3000", "3.000 horas"), ("4000", "4.000 horas"), ("custom", "Personalizado")]),
        ("number", "customTarget", "Objetivo personalizado", 4000, 1, 10000000, 1, "Solo se usa al elegir personalizado."),
    ],
    "youtube-shorts-income": [
        ("number", "views", "Visualizaciones con interacción", 1000000, 0, None, 1, "Métrica del periodo."),
        ("number", "rpm", "RPM de Shorts (€)", 0.08, 0, 1000, 0.01, "Usa tu RPM real o una hipótesis."),
    ],
    "youtube-income": [
        ("number", "views", "Visualizaciones del periodo", 250000, 0, None, 1, "Volumen total del periodo analizado."),
        ("number", "rpmLow", "RPM bajo (€)", 2, 0, 1000, 0.01, "Escenario prudente."),
        ("number", "rpm", "RPM central (€)", 3.5, 0, 1000, 0.01, "Usa tu RPM real cuando lo tengas."),
        ("number", "rpmHigh", "RPM alto (€)", 5, 0, 1000, 0.01, "Escenario optimista, no promesa."),
        ("number", "months", "Meses del periodo", 1, 1, 120, 1, "Para normalizar y proyectar."),
        ("number", "targetIncome", "Objetivo de ingresos (€)", 1000, 0, None, 0.01, "Calcula las vistas necesarias con el RPM central."),
    ],
    "youtube-rpm-monthly": [
        ("number", "dailyViews", "Visualizaciones diarias", 5000, 0, None, 1, "Media diaria."),
        ("number", "days", "Días", 30, 1, 366, 1, "Duración del periodo."),
        ("number", "rpm", "RPM (€)", 4, 0, 1000, 0.01, "Ingresos por mil vistas."),
    ],
    "youtube-views-goal": [
        ("number", "targetIncome", "Objetivo de ingresos (€)", 1000, 0, None, 0.01, "Cantidad objetivo."),
        ("number", "rpm", "RPM esperado (€)", 4, 0.01, 1000, 0.01, "Usa tu histórico."),
        ("number", "days", "Días para alcanzarlo", 30, 1, 3650, 1, "Para calcular vistas diarias."),
    ],
    "compound-interest": [
        ("number", "initial", "Capital inicial (€)", 10000, 0, None, 0.01, "Ahorro ya disponible."),
        ("number", "monthly", "Aportación mensual (€)", 200, 0, None, 0.01, "Aportación periódica."),
        ("select", "timing", "Momento de la aportación", "end", None, None, None, [("end", "Final de cada mes"), ("beginning", "Inicio de cada mes")]),
        ("number", "rate", "Rentabilidad bruta anual (%)", 6, -99, 1000, 0.01, "Hipótesis, no garantía."),
        ("number", "fee", "Comisión anual (%)", 0.3, 0, 100, 0.01, "Coste estimado."),
        ("number", "inflation", "Inflación anual (%)", 2, -20, 100, 0.01, "Para valor real."),
        ("number", "years", "Años", 15, 1, 80, 1, "Horizonte temporal."),
    ],
    "mortgage": [
        ("number", "principal", "Capital (€)", 200000, 1, None, 0.01, "Importe financiado."),
        ("number", "rate", "TIN anual (%)", 3, 0, 100, 0.01, "Tipo nominal para el escenario."),
        ("number", "years", "Plazo (años)", 25, 1, 50, 1, "Duración total."),
        ("number", "fees", "Gastos iniciales (€)", 0, 0, None, 0.01, "Opcional; no se financian en la cuota."),
    ],
    "personal-loan": [
        ("number", "principal", "Importe (€)", 15000, 1, None, 0.01, "Capital prestado."),
        ("number", "rate", "TIN anual (%)", 7, 0, 100, 0.01, "Tipo nominal."),
        ("number", "years", "Plazo (años)", 5, 0.08, 30, 0.01, "Duración total."),
        ("number", "commission", "Comisión de apertura (%)", 1, 0, 100, 0.01, "Coste inicial sobre el capital."),
    ],
    "monthly-savings": [
        ("number", "goal", "Objetivo (€)", 20000, 0, None, 0.01, "Cantidad que quieres alcanzar."),
        ("number", "current", "Ahorro actual (€)", 2000, 0, None, 0.01, "Capital disponible hoy."),
        ("number", "months", "Meses", 48, 1, 1200, 1, "Tiempo hasta la meta."),
        ("number", "rate", "Rentabilidad anual estimada (%)", 0, -99, 1000, 0.01, "Deja 0 para ahorro sin rentabilidad."),
    ],
    "index-funds": [
        ("number", "initial", "Capital inicial (€)", 5000, 0, None, 0.01, "Aportación inicial."),
        ("number", "monthly", "Aportación mensual (€)", 250, 0, None, 0.01, "Aportación periódica."),
        ("number", "return", "Rentabilidad bruta anual (%)", 6, -99, 1000, 0.01, "Hipótesis constante."),
        ("number", "fee", "Comisión anual (%)", 0.25, 0, 100, 0.01, "Coste total aproximado."),
        ("number", "inflation", "Inflación anual (%)", 2, -20, 100, 0.01, "Para poder adquisitivo."),
        ("number", "years", "Años", 20, 1, 80, 1, "Horizonte."),
    ],
    "mortgage-prepayment": [
        ("number", "principal", "Capital pendiente (€)", 160000, 1, None, 0.01, "Saldo antes de amortizar."),
        ("number", "rate", "TIN anual (%)", 3, 0, 100, 0.01, "Tipo actual del escenario."),
        ("number", "years", "Años restantes", 20, 0.08, 50, 0.01, "Plazo pendiente."),
        ("number", "extra", "Amortización extraordinaria (€)", 10000, 0, None, 0.01, "Capital que quieres adelantar."),
        ("number", "commission", "Comisión (%)", 0, 0, 100, 0.01, "Según contrato, si existe."),
    ],
    "freelance-rate": [
        ("number", "net", "Neto mensual deseado (€)", 2000, 0, None, 0.01, "Ingreso personal objetivo."),
        ("number", "expenses", "Gastos mensuales (€)", 600, 0, None, 0.01, "Software, oficina, gestoría…"),
        ("number", "reserve", "Reserva impuestos y cotizaciones (%)", 30, 0, 95, 0.1, "Hipótesis editable."),
        ("number", "billable", "Horas facturables por semana", 20, 1, 168, 0.5, "No incluyas administración."),
        ("number", "weeks", "Semanas facturables al año", 46, 1, 52, 1, "Descuenta vacaciones y pausas."),
        ("number", "margin", "Margen de seguridad (%)", 10, 0, 200, 0.1, "Colchón sobre el mínimo."),
    ],
    "profit-margin": [
        ("number", "cost", "Coste unitario (€)", 60, 0, None, 0.01, "Coste completo comparable."),
        ("number", "price", "Precio de venta (€)", 100, 0.01, None, 0.01, "Usa el mismo criterio fiscal."),
        ("number", "units", "Unidades", 100, 0, None, 1, "Para beneficio total."),
        ("number", "targetMargin", "Margen objetivo (%)", 40, 0, 99.99, 0.01, "Para calcular precio objetivo."),
    ],
    "break-even": [
        ("number", "fixed", "Costes fijos (€)", 3000, 0, None, 0.01, "Del periodo analizado."),
        ("number", "variable", "Coste variable por unidad (€)", 20, 0, None, 0.01, "Coste incremental."),
        ("number", "price", "Precio por unidad (€)", 50, 0.01, None, 0.01, "Ingreso unitario."),
        ("number", "expected", "Unidades previstas", 150, 0, None, 1, "Escenario de ventas."),
    ],
    "dismissal-compensation": [
        ("date", "start", "Fecha de inicio", "2021-01-01", None, None, None, "Inicio de la relación laboral."),
        ("date", "end", "Fecha de extinción", "2026-07-22", None, None, None, "Fecha final."),
        ("number", "salary", "Salario bruto anual (€)", 30000, 0.01, None, 0.01, "Salario regulador aproximado."),
        ("select", "type", "Tipo de cálculo", "objective", None, None, None, [("objective", "Despido objetivo · 20 días/año"), ("unfair", "Despido improcedente · 33/45 días"), ("temporary", "Fin temporal orientativo · 12 días/año")]),
    ],
    "severance": [
        ("number", "monthly", "Salario bruto mensual (€)", 2200, 0, None, 0.01, "Base aproximada de 30 días."),
        ("number", "salaryDays", "Días de salario pendientes", 15, 0, 31, 0.5, "Días todavía no abonados."),
        ("number", "vacationDays", "Vacaciones no disfrutadas", 8, 0, 365, 0.1, "Días pendientes de liquidar."),
        ("number", "extraPay", "Pagas extra devengadas (€)", 500, 0, None, 0.01, "Importe pendiente ya calculado."),
        ("number", "other", "Otros conceptos (€)", 0, -10000000, None, 0.01, "Comisiones, bonus u otros importes."),
        ("checkbox", "includeCompensation", "Añadir una indemnización calculada aparte", False, None, None, None, ""),
        ("number", "compensation", "Indemnización a añadir (€)", 0, 0, None, 0.01, "Usa la calculadora de indemnización si corresponde."),
        ("number", "deductions", "Anticipos o deducciones (€)", 0, 0, None, 0.01, "Importes a restar."),
    ],
    "net-salary": [
        ("number", "gross", "Salario bruto anual (€)", 30000, 0, None, 0.01, "Retribución anual."),
        ("select", "payments", "Número de pagas", "14", None, None, None, [("12", "12 pagas"), ("14", "14 pagas")]),
        ("number", "irpf", "IRPF estimado (%)", 15, 0, 100, 0.1, "Ajusta según tu situación."),
        ("number", "ss", "Cotización del trabajador (%)", 6.5, 0, 100, 0.1, "Hipótesis editable."),
        ("number", "other", "Otras deducciones anuales (€)", 0, 0, None, 0.01, "Opcional."),
    ],
    "vacation-days": [
        ("date", "start", "Inicio del periodo trabajado", "2026-01-01", None, None, None, "Dentro del año o periodo analizado."),
        ("date", "end", "Fin del periodo", "2026-07-22", None, None, None, "Fecha de cálculo."),
        ("number", "annual", "Vacaciones anuales", 30, 0, 366, 0.1, "Naturales o laborables según tu criterio."),
        ("number", "taken", "Días ya disfrutados", 5, 0, 366, 0.1, "Con el mismo criterio."),
    ],
    "employer-cost": [
        ("number", "gross", "Salario bruto anual (€)", 30000, 0, None, 0.01, "Retribución bruta."),
        ("number", "rate", "Cotización empresarial estimada (%)", 31, 0, 200, 0.1, "Hipótesis editable, no universal."),
        ("number", "other", "Otros costes anuales (€)", 2500, 0, None, 0.01, "Equipo, formación, seguros…"),
        ("number", "bonus", "Bonus o variable anual (€)", 0, 0, None, 0.01, "Si no está incluido en el bruto."),
    ],
"pdf-merge": [
    ("file", "files", "Selecciona dos o más PDF", ".pdf,application/pdf", True, None, None, "Puedes cambiar el orden o eliminar archivos antes de unirlos."),
],
"pdf-split": [
    ("file", "file", "Selecciona un PDF", ".pdf,application/pdf", False, None, None, "El archivo se procesa en tu navegador."),
    ("select", "mode", "Modo de división", "ranges", None, None, None, [("ranges", "Crear archivos por rangos"), ("each", "Una página por archivo")]),
    ("text", "ranges", "Rangos", "1-3, 4-6, 9", None, None, None, "Separa cada archivo con comas."),
],
"pdf-organize": [
    ("file", "file", "Selecciona un PDF", ".pdf,application/pdf", False, None, None, "Después podrás arrastrar, girar y eliminar páginas."),
],
"images-to-pdf": [
    ("file", "files", "Selecciona imágenes", "image/*", True, None, None, "El orden de la lista será el orden de las páginas."),
    ("select", "pageSize", "Tamaño de página", "a4", None, None, None, [("a4", "A4"), ("letter", "Carta"), ("auto", "Tamaño de cada imagen")]),
    ("select", "orientation", "Orientación", "auto", None, None, None, [("auto", "Automática"), ("portrait", "Vertical"), ("landscape", "Horizontal")]),
    ("number", "margin", "Margen (mm)", 10, 0, 100, 1, "Espacio alrededor de la imagen."),
],
"pdf-to-jpg": [
    ("file", "file", "Selecciona un PDF", ".pdf,application/pdf", False, None, None, "Puedes convertir todas las páginas o solo una selección."),
    ("text", "pages", "Páginas", "todas", None, None, None, "Ejemplos: todas · 1-3, 8"),
    ("select", "scale", "Resolución", "2", None, None, None, [("1.5", "Media · 1,5×"), ("2", "Alta · 2×"), ("3", "Muy alta · 3×")]),
    ("range", "quality", "Calidad JPG", 90, 40, 100, 1, "Porcentaje de calidad de salida."),
],
"image-compress": [
    ("file", "files", "Selecciona imágenes", "image/*", True, None, None, "Puedes procesar varias a la vez."),
    ("select", "format", "Formato de salida", "webp", None, None, None, [("webp", "WebP"), ("jpeg", "JPG"), ("png", "PNG"), ("same", "Mantener formato compatible")]),
    ("range", "quality", "Calidad", 82, 30, 100, 1, "Afecta principalmente a JPG y WebP."),
    ("number", "maxDimension", "Dimensión máxima (px)", 1920, 0, 12000, 1, "0 conserva las dimensiones."),
],
"image-resize": [
    ("file", "files", "Selecciona imágenes", "image/*", True, None, None, "Redimensiona en lote."),
    ("number", "maxWidth", "Ancho máximo (px)", 1200, 0, 20000, 1, "0 ignora este límite."),
    ("number", "maxHeight", "Alto máximo (px)", 1200, 0, 20000, 1, "0 ignora este límite."),
    ("checkbox", "upscale", "Permitir ampliar imágenes pequeñas", False, None, None, None, ""),
    ("select", "format", "Formato de salida", "same", None, None, None, [("same", "Mantener formato compatible"), ("webp", "WebP"), ("jpeg", "JPG"), ("png", "PNG")]),
    ("range", "quality", "Calidad", 90, 30, 100, 1, "Para JPG y WebP."),
],
"image-convert": [
    ("file", "files", "Selecciona imágenes", "image/*", True, None, None, "Convierte varias imágenes en un lote."),
    ("select", "format", "Formato de destino", "webp", None, None, None, [("webp", "WebP"), ("jpeg", "JPG"), ("png", "PNG")]),
    ("range", "quality", "Calidad", 90, 30, 100, 1, "Para JPG y WebP."),
],
"image-crop": [
    ("file", "file", "Selecciona una imagen", "image/*", False, None, None, "La vista previa aparece al seleccionar el archivo."),
    ("select", "aspect", "Proporción", "4:5", None, None, None, [("free", "Original / libre"), ("1:1", "Cuadrada · 1:1"), ("4:5", "Vertical · 4:5"), ("16:9", "Horizontal · 16:9"), ("9:16", "Vertical · 9:16")]),
    ("range", "zoom", "Zoom", 100, 100, 300, 1, "Aumenta para recortar una zona más pequeña."),
    ("range", "positionX", "Posición horizontal", 50, 0, 100, 1, "Mueve el encuadre de izquierda a derecha."),
    ("range", "positionY", "Posición vertical", 50, 0, 100, 1, "Mueve el encuadre de arriba abajo."),
    ("select", "format", "Formato", "jpeg", None, None, None, [("jpeg", "JPG"), ("webp", "WebP"), ("png", "PNG")]),
    ("range", "quality", "Calidad", 92, 30, 100, 1, "Para JPG y WebP."),
],
"remove-exif": [
    ("file", "files", "Selecciona imágenes", "image/*", True, None, None, "Se crearán copias nuevas sin copiar metadatos habituales."),
    ("select", "format", "Formato de salida", "same", None, None, None, [("same", "Mantener formato compatible"), ("jpeg", "JPG"), ("png", "PNG"), ("webp", "WebP")]),
    ("range", "quality", "Calidad", 95, 50, 100, 1, "Para JPG y WebP."),
],
"word-counter": [
    ("textarea", "text", "Escribe o pega tu texto", "Empieza a escribir para ver palabras, caracteres, frases y tiempo de lectura.", None, None, None, "El análisis se actualiza al instante."),
],
"case-converter": [
    ("select", "mode", "Transformación", "upper", None, None, None, [("upper", "MAYÚSCULAS"), ("lower", "minúsculas"), ("title", "Tipo Título"), ("sentence", "Tipo oración"), ("alternating", "aLtErNaDo")]),
    ("textarea", "text", "Texto original", "Una guía práctica para transformar textos.", None, None, None, "Cambia el modo para actualizar el resultado."),
],
"text-diff": [
    ("textarea", "original", "Texto original", "Primera línea\nSegunda línea\nTercera línea", None, None, None, "Versión de partida."),
    ("textarea", "revised", "Texto revisado", "Primera línea\nSegunda línea modificada\nTercera línea", None, None, None, "Versión que quieres comparar."),
],
"qr-generator": [
    ("textarea", "content", "URL o texto", "https://clicivo.com", None, None, None, "El contenido se codifica directamente en el QR."),
    ("number", "size", "Tamaño (px)", 320, 128, 1024, 1, "Tamaño de la imagen PNG."),
    ("color", "foreground", "Color del código", "#111827", None, None, None, ""),
    ("color", "background", "Color de fondo", "#ffffff", None, None, None, ""),
    ("select", "level", "Corrección de errores", "M", None, None, None, [("L", "Baja · L"), ("M", "Media · M"), ("Q", "Alta · Q"), ("H", "Máxima · H")]),
],
"wifi-qr": [
    ("text", "ssid", "Nombre de la red (SSID)", "WiFi Invitados", None, None, None, "Respeta mayúsculas, espacios y símbolos."),
    ("text", "password", "Contraseña", "", None, None, None, "Puede quedar vacía si la red es abierta."),
    ("select", "security", "Seguridad", "WPA", None, None, None, [("WPA", "WPA / WPA2 / WPA3"), ("WEP", "WEP"), ("nopass", "Sin contraseña")]),
    ("checkbox", "hidden", "Red oculta", False, None, None, None, ""),
    ("number", "size", "Tamaño (px)", 320, 128, 1024, 1, "Tamaño de la imagen PNG."),
    ("color", "foreground", "Color del código", "#111827", None, None, None, ""),
    ("color", "background", "Color de fondo", "#ffffff", None, None, None, ""),
],

}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_route(route: str, content: str) -> None:
    route = route.strip()
    if route == "/":
        path = PUBLIC / "index.html"
    else:
        path = PUBLIC / route.strip("/") / "index.html"
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def write_redirect(route: str, target: str) -> None:
    """Create a lightweight static redirect for legacy URLs.

    GitHub Pages cannot emit server-side 301 responses, so the page uses a
    canonical target, noindex, JavaScript replacement and a meta refresh.
    """
    path = PUBLIC / route.strip("/") / "index.html"
    ensure_dir(path.parent)
    target_url = canonical(target)
    content = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Página trasladada | Clicivo</title><meta name="robots" content="noindex,follow"><link rel="canonical" href="{esc(target_url)}"><meta http-equiv="refresh" content="0;url={esc(target)}"><script>location.replace({json.dumps(target)});</script></head><body><p>Esta página se ha trasladado. <a href="{esc(target)}">Continuar en Clicivo</a>.</p></body></html>"""
    path.write_text(content, encoding="utf-8")


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def canonical(route: str) -> str:
    return ORIGIN + (route if route.startswith("/") else "/" + route)


def json_ld(data) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


def head(title: str, description: str, route: str, ld=None, image: str = "/assets/og-clicivo.png") -> str:
    full_title = title if title.endswith("Clicivo") else f"{title} | Clicivo"
    url = canonical(route)
    consent_bootstrap = f"""<script>
window.dataLayer=window.dataLayer||[];
function gtag(){{dataLayer.push(arguments);}}
gtag('consent','default',{{ad_storage:'denied',analytics_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',wait_for_update:500}});
gtag('set','ads_data_redaction',true);
gtag('js',new Date());
gtag('config','{esc(SITE["analytics_measurement_id"])}',{{anonymize_ip:true}});
</script>"""
    blocks = [
        "<!doctype html><html lang=\"es\"><head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
        f'<meta name="google-adsense-account" content="{esc(SITE["adsense_account_id"])}">',
        f"<title>{esc(full_title)}</title>",
        f'<meta name="description" content="{esc(description[:158])}">',
        f'<link rel="canonical" href="{esc(url)}">',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">',
        f'<meta property="og:type" content="website"><meta property="og:locale" content="es_ES"><meta property="og:site_name" content="Clicivo"><meta property="og:title" content="{esc(full_title)}"><meta property="og:description" content="{esc(description[:200])}"><meta property="og:url" content="{esc(url)}"><meta property="og:image" content="{esc(canonical(image))}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(full_title)}"><meta name="twitter:description" content="{esc(description[:200])}"><meta name="twitter:image" content="{esc(canonical(image))}">',
        '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="/assets/favicon-48.png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest">',
        '<link rel="preconnect" href="https://www.googletagmanager.com"><link rel="preconnect" href="https://pagead2.googlesyndication.com">',
        '<link rel="stylesheet" href="/assets/styles.css">',
        '<meta name="theme-color" content="#2657d8">',
        consent_bootstrap,
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={esc(SITE["analytics_measurement_id"])}"></script>',
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={esc(SITE["adsense_account_id"])}" crossorigin="anonymous"></script>',
    ]
    if ld:
        for block in (ld if isinstance(ld, list) else [ld]):
            blocks.append(json_ld(block))
    blocks.append("</head><body>")
    return "".join(blocks)


def header() -> str:
    return f'''
<a class="skip-link" href="#contenido">Saltar al contenido</a>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="/"><img src="/assets/logo-mark.svg" width="34" height="34" alt=""><span>Clicivo</span></a>
<button class="menu-button" type="button" aria-controls="main-nav" aria-expanded="false">Menú</button>
<nav class="nav" id="main-nav" aria-label="Navegación principal">
<a href="/es/pdf/">PDF</a><a href="/es/imagenes/">Imágenes</a><a href="/es/productividad/">Productividad</a><a href="/es/finanzas/">Finanzas</a><a href="/es/redes-sociales/">Redes</a><a href="/es/empleo/">Empleo</a>
</nav></div></header>'''


def footer(extra_scripts: str = "") -> str:
    return f'''\
<footer class="site-footer"><div class="container">
<div class="footer-grid">
<div><a class="brand" href="/"><img src="/assets/logo-mark.svg" width="34" height="34" alt=""><span>Clicivo</span></a><p>Calcula, compara y presenta resultados con claridad. Herramientas gratuitas, rápidas y preparadas para trabajar desde cualquier dispositivo.</p><p class="footer-small">Proyecto gestionado por {esc(SITE.get('operator_name','Zurekin Comunicación'))}, {esc(SITE.get('operator_location','Bilbao, España'))}.</p></div>
<div><h3>Herramientas</h3><a href="/es/pdf/">PDF y documentos</a><a href="/es/imagenes/">Imágenes</a><a href="/es/productividad/">Texto y productividad</a><a href="/es/finanzas/">Finanzas</a><a href="/es/redes-sociales/">Creadores</a><a href="/es/empleo/">Empleo</a></div>
<div><h3>Confianza</h3><a href="/sobre-clicivo/">Quiénes somos</a><a href="/metodologia/">Metodología y correcciones</a><a href="/condiciones-de-uso/">Condiciones de uso</a><a href="/publicidad-y-afiliacion/">Publicidad y afiliación</a><a href="/contacto/">Contacto</a></div>
<div><h3>Legal y privacidad</h3><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Política de privacidad</a><a href="/cookies/">Política de cookies</a><p>El mensaje europeo de Google permite revisar o retirar el consentimiento cuando está publicado.</p><a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a></div>
</div><div class="footer-bottom">© 2026 Clicivo · Revisión general: {esc(UPDATED)} · Versión {esc(SITE.get('quality_version','2026.08'))}.</div>
</div></footer>
<script src="/assets/site.js" defer></script>{extra_scripts}</body></html>'''


ADVANCED_TOOL_IDS = {
    "pdf-merge", "pdf-split", "pdf-organize", "images-to-pdf", "pdf-to-jpg",
    "image-compress", "image-resize", "image-convert", "image-crop", "remove-exif",
    "word-counter", "case-converter", "text-diff", "qr-generator", "wifi-qr",
}
PDF_LIB_TOOLS = {"pdf-merge", "pdf-split", "pdf-organize", "images-to-pdf"}
PDF_JS_TOOLS = {"pdf-organize", "pdf-to-jpg"}
ZIP_TOOLS = {"pdf-split", "pdf-to-jpg", "image-compress", "image-resize", "image-convert", "remove-exif"}
QR_TOOLS = {"qr-generator", "wifi-qr"}
REPORT_CATEGORIES = {"Redes sociales", "Finanzas", "Negocios", "Empleo"}


def tool_scripts(tool) -> str:
    tool_id = tool["id"]
    tags = []
    if tool["category"] in REPORT_CATEGORIES:
        tags.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/4.2.1/jspdf.umd.min.js" defer crossorigin="anonymous" referrerpolicy="no-referrer"></script>')
    if tool_id in ADVANCED_TOOL_IDS:
        if tool_id in PDF_LIB_TOOLS:
            tags.append('<script src="https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js" defer></script>')
        if tool_id in PDF_JS_TOOLS:
            tags.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js" defer crossorigin="anonymous" referrerpolicy="no-referrer"></script>')
        if tool_id in ZIP_TOOLS:
            tags.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js" defer crossorigin="anonymous" referrerpolicy="no-referrer"></script>')
        if tool_id in QR_TOOLS:
            tags.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js" defer crossorigin="anonymous" referrerpolicy="no-referrer"></script>')
        tags.append('<script src="/assets/advanced-tools.js" defer></script>')
    return "".join(tags)

def breadcrumb(items):
    lis=[]
    schema=[]
    for i,(label,path) in enumerate(items,1):
        if path:
            lis.append(f'<li><a href="{esc(path)}">{esc(label)}</a></li>')
            item_url=canonical(path)
        else:
            lis.append(f'<li aria-current="page">{esc(label)}</li>')
            item_url=None
        entry={"@type":"ListItem","position":i,"name":label}
        if item_url: entry["item"]=item_url
        schema.append(entry)
    return f'<nav class="breadcrumbs" aria-label="Migas de pan"><ol>{"".join(lis)}</ol></nav>', {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":schema}


def tool_icon(tool):
    return PLATFORM_ICONS.get(tool["cluster"], CATEGORY_META.get(tool["category"], {}).get("icon", "◆"))


def tool_card(tool):
    badge = '<span class="badge">Nueva</span>' if tool.get("new") else ('<span class="badge badge-priority">Destacada</span>' if tool.get("opportunity") else '<span class="badge badge-free">Gratis</span>')
    promise = tool.get('benefit_heading', tool['description'])
    return f'''<a class="tool-card accent-{esc(tool.get('accent','blue'))}" href="{esc(tool['path'])}" data-tool-card="{esc(tool['id'])}" data-category="{esc(tool['category'])}" data-search="{esc((tool['title']+' '+' '.join(tool['keywords'])).lower())}"><div class="top"><span class="tool-icon" aria-hidden="true">{esc(tool_icon(tool))}</span>{badge}</div><h3>{esc(tool['short_title'])}</h3><p>{esc(promise)}</p><span class="link">Abrir herramienta <span aria-hidden="true">→</span></span></a>'''

def field_html(field):
    kind,name,label,value,minv,maxv,step,hint = field
    full = kind in {"textarea", "file"} or name in {"text", "original", "revised", "content"}
    cls = "field full" if full else "field"
    hint_text = hint if isinstance(hint, str) else ""
    if kind == "select":
        opts=[]
        for val,text in hint:
            selected=' selected' if str(val)==str(value) else ''
            opts.append(f'<option value="{esc(val)}"{selected}>{esc(text)}</option>')
        control=f'<select id="{esc(name)}" name="{esc(name)}">{"".join(opts)}</select>'
        hint_text=""
    elif kind == "textarea":
        control=f'<textarea id="{esc(name)}" name="{esc(name)}" spellcheck="true">{esc(value)}</textarea>'
    elif kind == "file":
        multiple=' multiple' if minv else ''
        control=f'<label class="file-drop" for="{esc(name)}"><input type="file" id="{esc(name)}" name="{esc(name)}" accept="{esc(value)}"{multiple}><span><b>Seleccionar archivos</b><small>También puedes arrastrarlos aquí</small></span></label><div class="file-selection" data-file-selection="{esc(name)}">Ningún archivo seleccionado.</div>'
    elif kind == "checkbox":
        checked=' checked' if value else ''
        control=f'<label class="checkbox-row" for="{esc(name)}"><input type="checkbox" id="{esc(name)}" name="{esc(name)}"{checked}><span>{esc(label)}</span></label>'
        label=''
    else:
        attrs=[f'type="{esc(kind)}"',f'id="{esc(name)}"',f'name="{esc(name)}"',f'value="{esc(value)}"']
        if minv is not None: attrs.append(f'min="{esc(minv)}"')
        if maxv is not None: attrs.append(f'max="{esc(maxv)}"')
        if step is not None: attrs.append(f'step="{esc(step)}"')
        attrs.append('required')
        control=f'<input {" ".join(attrs)}>'
    small=f'<small>{esc(hint_text)}</small>' if hint_text else ''
    label_html=f'<label for="{esc(name)}">{esc(label)}</label>' if label else ''
    return f'<div class="{cls}">{label_html}{control}{small}</div>'


def form_html(tool):
    fields=FORM_SCHEMAS[tool['id']]
    live=tool['id'] in {'instagram-fonts','instagram-counter','instagram-spaces','word-counter','case-converter'}
    labels={
        'pdf-merge':'Unir PDF','pdf-split':'Dividir PDF','pdf-organize':'Exportar PDF organizado','images-to-pdf':'Crear PDF','pdf-to-jpg':'Convertir a JPG',
        'image-compress':'Comprimir imágenes','image-resize':'Redimensionar','image-convert':'Convertir imágenes','image-crop':'Recortar y descargar','remove-exif':'Crear copias limpias',
        'text-diff':'Comparar textos','qr-generator':'Generar QR','wifi-qr':'Generar QR Wi-Fi',
    }
    if live:
        button=''
    elif tool['id']=='instagram-spaces':
        button='<button class="btn btn-secondary js-copy-main" type="button">Copiar texto preparado</button>'
    else:
        text=labels.get(tool['id'],'Calcular resultado')
        button=f'<button class="btn btn-primary btn-calculate" type="submit"><span>{esc(text)}</span><span aria-hidden="true">→</span></button><button class="btn btn-ghost" type="reset">Restablecer</button>'
    if tool['category'] in {'PDF y documentos','Imágenes'}:
        title='Sube y configura tus archivos'
        subtitle='Todo se procesa en tu navegador. Ajusta las opciones y descarga el resultado sin registro.'
        privacy='🔒 Tus archivos se procesan localmente y no se envían a Clicivo.'
    elif tool['category']=='Texto y productividad':
        title='Introduce el contenido'
        subtitle='Pega o escribe la información y obtén un resultado listo para reutilizar.'
        privacy='🔒 La transformación se realiza localmente. Clicivo no recibe el contenido introducido.'
    else:
        title='Configura tu escenario'
        subtitle='Usa datos del mismo periodo. Puedes cambiar cualquier variable para comparar alternativas.'
        privacy='🔒 El cálculo se realiza localmente. Clicivo no recibe los datos introducidos.'
    return f'''<section class="calculator app-card" aria-labelledby="calc-title"><div class="app-card-head"><span class="app-step">01</span><div><h2 id="calc-title">{esc(title)}</h2><p>{esc(subtitle)}</p></div></div><form class="tool-form" data-tool="{esc(tool['id'])}" data-tool-title="{esc(tool['title'])}" data-category="{esc(tool['category'])}" novalidate><div class="fields">{"".join(field_html(f) for f in fields)}</div><div class="form-actions">{button}</div><div class="error-message" role="alert" aria-live="polite"></div></form><p class="privacy-line">{privacy}</p></section>'''

def path_breadcrumbs(tool):
    items=[("Inicio","/")]
    cat=CATEGORY_META[tool['category']]
    items.append((tool['category'],cat['path']))
    segs=tool['path'].strip('/').split('/')
    # Prefix pages after /es/; avoid duplicating finance/business/employment category segment.
    if tool['category']=='Redes sociales':
        platform=segs[1]
        items.append((SEGMENT_LABELS.get(platform,platform.title()),f'/es/{platform}/'))
        parent='/'+'/'.join(segs[:-1])+'/'
        if len(segs)>3:
            items.append((SEGMENT_LABELS.get(segs[2],segs[2].title()),parent))
    else:
        parent='/'+'/'.join(segs[:-1])+'/'
        if len(segs)>3:
            items.append((SEGMENT_LABELS.get(segs[2],segs[2].title()),parent))
    items.append((tool['short_title'],None))
    return items


PRIORITY_RELATED = {
    "youtube-income": ["youtube-rpm-revenue", "youtube-shorts-income", "youtube-views-goal"],
    "youtube-rpm-revenue": ["youtube-income", "youtube-shorts-income", "youtube-views-goal"],
    "instagram-growth": ["instagram-engagement-followers", "instagram-engagement-reach", "instagram-counter"],
    "instagram-engagement-followers": ["instagram-engagement-reach", "instagram-growth", "instagram-counter"],
    "severance": ["dismissal-compensation", "vacation-days", "net-salary"],
    "dismissal-compensation": ["severance", "vacation-days", "net-salary"],
    "net-salary": ["severance", "employer-cost", "vacation-days"],
    "compound-interest": ["index-funds", "monthly-savings", "mortgage"],
    "pdf-merge": ["pdf-organize", "pdf-split", "images-to-pdf"],
}


def related_tools(tool):
    chosen = []
    seen = {tool["id"]}
    for tool_id in PRIORITY_RELATED.get(tool["id"], []):
        candidate = next((t for t in TOOLS if t["id"] == tool_id), None)
        if candidate and candidate["id"] not in seen:
            chosen.append(candidate)
            seen.add(candidate["id"])
    pools = [
        [t for t in TOOLS if t["cluster"] == tool["cluster"]],
        [t for t in TOOLS if t["category"] == tool["category"]],
        TOOLS,
    ]
    for pool in pools:
        for candidate in pool:
            if candidate["id"] not in seen:
                chosen.append(candidate)
                seen.add(candidate["id"])
            if len(chosen) >= 3:
                return chosen
    return chosen[:3]

def affiliate_block(tool):
    if tool['category']!='Redes sociales': return ''
    return f'''<aside class="affiliate-card"><span class="sponsor-badge">Recurso para creadores · enlace patrocinado</span><h2>Convierte estas cifras en un calendario de contenido</h2><p>Metricool reúne planificación y analítica para que no tengas que comparar métricas a mano. Clicivo puede recibir una comisión sin coste adicional para ti.</p><a class="btn" href="{esc(SITE['affiliate_url'])}" target="_blank" rel="sponsored nofollow noopener" data-affiliate="metricool">Explorar Metricool <span aria-hidden="true">→</span></a></aside>'''

def usage_block(tool):
    custom_steps = tool.get("usage_steps") or []
    if custom_steps:
        steps = "".join(
            f'<div class="step"><strong>{esc(step["title"])}</strong><p>{esc(step["text"])}</p></div>'
            for step in custom_steps
        )
        return f'<section class="content-card"><h2>Cómo utilizar esta herramienta</h2><div class="steps">{steps}</div></section>'
    if tool['category'] in {'PDF y documentos','Imágenes'}:
        return '''<section class="content-card"><h2>Cómo utilizar esta herramienta</h2><div class="steps"><div class="step"><strong>Selecciona los archivos</strong><p>Elige los documentos o imágenes desde tu dispositivo. Revisa el tamaño y el formato admitido.</p></div><div class="step"><strong>Ajusta las opciones</strong><p>Ordena, selecciona páginas, define formato, tamaño o calidad según la herramienta.</p></div><div class="step"><strong>Descarga el resultado</strong><p>El procesamiento se realiza en el navegador. Guarda el archivo y cierra la página para liberar memoria.</p></div></div></section>'''
    if tool['category']=='Texto y productividad':
        return '''<section class="content-card"><h2>Cómo utilizar esta herramienta</h2><div class="steps"><div class="step"><strong>Introduce el contenido</strong><p>Escribe o pega el texto, la URL o los datos necesarios.</p></div><div class="step"><strong>Revisa el resultado</strong><p>La herramienta analiza o transforma el contenido directamente en el navegador.</p></div><div class="step"><strong>Copia o descarga</strong><p>Comprueba el resultado final antes de utilizarlo o compartirlo.</p></div></div></section>'''
    return '''<section class="content-card"><h2>Cómo utilizar esta herramienta</h2><div class="steps"><div class="step"><strong>Introduce datos comparables</strong><p>Completa los campos con cifras del mismo periodo y revisa unidades, porcentajes y fechas.</p></div><div class="step"><strong>Calcula y comprueba</strong><p>Obtén el resultado principal y revisa el desglose antes de tomar decisiones.</p></div><div class="step"><strong>Prueba escenarios</strong><p>Cambia una variable cada vez para entender qué factor produce cada diferencia.</p></div></div></section>'''

def tool_page(tool):
    crumbs, crumb_ld=breadcrumb(path_breadcrumbs(tool))
    app_ld={
        "@context":"https://schema.org","@type":"WebApplication","name":tool['title'],
        "url":canonical(tool['path']),"applicationCategory":"UtilitiesApplication","operatingSystem":"Any",
        "isAccessibleForFree":True,"description":tool['description'],"inLanguage":"es","dateModified":tool.get('reviewed',UPDATED),
        "publisher":{"@type":"Organization","name":"Clicivo","url":ORIGIN}
    }
    faq_ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in tool['faqs']]}
    badge='<span class="badge">Nueva herramienta</span>' if tool.get('new') else '<span class="eyebrow">Herramienta revisada</span>'
    notes=''.join(f'<div class="notice"><strong>Importante:</strong> {esc(n)}</div>' for n in tool.get('notes',[]))
    sources=''.join(f'<li><a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a></li>' for name,url in tool['sources'])
    faqs=''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in tool['faqs'])
    rel=''.join(f'<a class="related-link" data-related-tool="{esc(t["id"])}" href="{esc(t["path"])}"><span>{esc(t["short_title"])}</span><b aria-hidden="true">→</b></a>' for t in related_tools(tool))
    features=tool.get('features') or ["Resultado inmediato","Metodología visible","Adaptada a móvil","Sin registro"]
    feature_html=''.join(f'<li><span aria-hidden="true">✓</span>{esc(feature)}</li>' for feature in features)
    review_date=tool.get('reviewed',UPDATED)
    report_subject=esc(f'Corrección en {tool["short_title"]}')
    report_enabled=tool['category'] in REPORT_CATEGORIES
    if report_enabled:
        result_actions='''<button class="btn btn-primary js-download-pdf" type="button">Descargar resultado en PDF</button><button class="btn btn-secondary js-copy-client" type="button">Copiar para cliente</button><button class="btn btn-ghost js-copy-result" type="button">Copiar resumen</button>'''
        export_badge='<span class="result-export-badge">PDF y copia profesional incluidos</span>'
    else:
        result_actions='''<button class="btn btn-primary js-copy-result" type="button">Copiar resultado</button><button class="btn btn-secondary js-print-result" type="button">Imprimir o guardar PDF</button>'''
        export_badge='<span class="result-export-badge">Resultado listo para reutilizar</span>'
    accent=esc(tool.get('accent','blue'))
    benefit_heading=esc(tool.get('benefit_heading','Obtén un resultado que puedas utilizar'))
    benefit_copy=esc(tool.get('benefit_copy',tool['description']))
    hook=esc(tool.get('hook',tool['description']))
    return head(tool.get('seo_title',tool['title']),tool['description'],tool['path'],[app_ld,faq_ld,crumb_ld])+header()+f'''
<main id="contenido" class="tool-app accent-{accent}"><div class="container">{crumbs}</div>
<section class="tool-hero saas-hero"><div class="container saas-hero-grid"><div class="saas-hero-copy">{badge}<p class="curiosity-hook">{hook}</p><h1>{esc(tool['title'])}</h1><p class="hero-benefit">{esc(tool['description'])}</p><div class="trust-inline"><span>✓ Gratis y sin registro</span><span>✓ Resultado en segundos</span><span>✓ Privacidad desde el diseño</span></div></div><aside class="hero-outcome-card"><span class="status-dot"><i></i> Lista para usar</span><h2>{benefit_heading}</h2><p>{benefit_copy}</p><ul>{feature_html}</ul></aside></div></section>
<section class="container app-workspace"><div class="tool-layout">{form_html(tool)}<aside class="result-panel app-card" aria-live="polite" data-report-title="{esc(tool['title'])}" data-report-path="{esc(tool['path'])}"><div class="app-card-head result-head"><span class="app-step">02</span><div><p class="result-kicker">Tu resultado</p><h2>Una cifra clara para decidir mejor</h2></div></div>{export_badge}<div id="result-body" class="result-placeholder">Completa los campos y pulsa calcular. Aquí verás el resultado, el desglose y los escenarios.</div><div class="result-actions">{result_actions}</div></aside></div>{notes}
<div class="benefit-ribbon"><div><span>01</span><strong>Calcula</strong><p>Introduce tus datos sin crear una cuenta.</p></div><div><span>02</span><strong>Compara</strong><p>Cambia variables y entiende qué mueve el resultado.</p></div><div><span>03</span><strong>Presenta</strong><p>Copia o descarga una versión lista para compartir.</p></div></div>
<div class="content-stack">
{usage_block(tool)}
<section class="content-card benefit-card"><span class="section-badge">Beneficio directo</span><h2>{benefit_heading}</h2><p class="lead-copy">{benefit_copy}</p><ul class="benefit-list">{feature_html}</ul></section>
<section class="content-card"><span class="section-badge">Cálculo transparente</span><h2>Fórmula, método y un ejemplo realista</h2><p class="formula">{esc(tool['formula'])}</p><h3>Ejemplo práctico</h3><p>{esc(tool['example'])}</p><p>Las estimaciones se separan de los datos introducidos. En materias económicas, laborales o fiscales, contrasta el resultado con documentación y asesoramiento adecuados.</p></section>
<section class="content-card faq"><span class="section-badge">Respuestas rápidas</span><h2>Preguntas frecuentes antes de usar la herramienta</h2>{faqs}</section>
<section class="content-card"><span class="section-badge">Confianza</span><h2>Fuentes, actualización y correcciones</h2><p>Última revisión: <strong>{esc(review_date)}</strong>. Las plataformas, normas y productos pueden cambiar, por eso mostramos las referencias y los límites de cada cálculo.</p><ul class="source-list">{sources}</ul><p><a href="/metodologia/">Consulta la metodología editorial y la política de correcciones de Clicivo.</a></p></section>
{affiliate_block(tool)}
<section class="content-card"><span class="section-badge">Siguiente paso</span><h2>Continúa con una herramienta relacionada</h2><div class="related-grid">{rel}</div></section>
<div class="quality-card"><div><strong>Calidad comprobable</strong><p>Fórmula visible, valores validados, pruebas automáticas y revisión editorial.</p></div><div><strong>¿Algo no cuadra?</strong><p>Comunica un error reproducible y lo revisaremos con prioridad.</p><a href="mailto:{esc(SITE['editorial_email'])}?subject={report_subject}">Informar de un error →</a></div></div>
</div></section></main>'''+footer(tool_scripts(tool))

def page_schema(title,desc,route):
    return {"@context":"https://schema.org","@type":"CollectionPage","name":title,"description":desc,"url":canonical(route),"inLanguage":"es","isPartOf":{"@type":"WebSite","name":"Clicivo","url":ORIGIN}}


def collection_page(title,desc,route,tools,eyebrow="Colección de herramientas"):
    crumbs,crumb_ld=breadcrumb([("Inicio","/"),(title,None)])
    cards=''.join(tool_card(t) for t in tools)
    popular=sorted(tools,key=lambda t:(not bool(t.get('opportunity')),not bool(t.get('new')),t['short_title']))[:3]
    popular_links=''.join(f'<a class="related-link" href="{esc(t["path"])}"><span>{esc(t["short_title"])}</span><b aria-hidden="true">→</b></a>' for t in popular)
    clusters=sorted({t['cluster'] for t in tools})
    cluster_text=', '.join(clusters)
    return head(title,desc,route,[page_schema(title,desc,route),crumb_ld])+header()+f'''
<main id="contenido"><div class="container">{crumbs}</div>
<section class="tool-hero collection-hero"><div class="container"><span class="eyebrow">{esc(eyebrow)}</span><p class="curiosity-hook">Menos pasos, más claridad y resultados que puedes reutilizar.</p><h1>{esc(title)}</h1><p>{esc(desc)}</p><div class="collection-stats"><span><b>{len(tools)}</b> herramientas</span><span>Gratis y sin registro</span><span>Diseñadas para móvil</span></div></div></section>
<section class="section section-tight"><div class="container"><div class="content-card collection-intro"><span class="section-badge">Resuelve la tarea de principio a fin</span><h2>Todo lo que necesitas para {esc(title.lower())}</h2><p>Esta colección reúne herramientas de {esc(cluster_text)}. Cada utilidad tiene una función diferente, una metodología visible y un resultado que puedes copiar, descargar o continuar en otra herramienta.</p><div class="related-grid">{popular_links}</div></div></div></section>
<section class="section"><div class="container"><div class="search-wrap"><span aria-hidden="true">⌕</span><input type="search" class="catalog-search" placeholder="¿Qué necesitas resolver?" aria-label="Buscar herramientas"></div><div class="tool-grid" id="tool-grid">{cards}</div><p class="empty-state">No hemos encontrado una herramienta con ese término.</p></div></section>
<section class="section section-tight"><div class="container"><div class="quality-card"><div><strong>Privacidad práctica</strong><p>Los archivos se procesan localmente cuando la herramienta lo indica. Los cálculos muestran método, ejemplo y fecha de revisión.</p></div><div><strong>Mejora continua</strong><p>Revisamos errores, experiencia móvil y utilidad real para que cada herramienta resuelva una tarea concreta.</p><a href="/metodologia/">Cómo comprobamos la calidad →</a></div></div></div></section></main>'''+footer()

def homepage():
    website_ld={"@context":"https://schema.org","@type":"WebSite","name":"Clicivo","url":ORIGIN,"description":SITE['site_description'],"inLanguage":"es","potentialAction":{"@type":"SearchAction","target":ORIGIN+"/?q={search_term_string}","query-input":"required name=search_term_string"}}
    org_ld={"@context":"https://schema.org","@type":"Organization","name":"Clicivo","alternateName":SITE.get('operator_name','Zurekin Comunicación'),"url":ORIGIN,"logo":canonical('/assets/logo-mark.svg'),"email":SITE['contact_email']}
    featured_ids=['youtube-income','tiktok-income','instagram-growth','severance','pdf-merge','image-compress','qr-generator']
    featured=[next(t for t in TOOLS if t['id']==x) for x in featured_ids]
    catcards=''.join(f'''<a class="category-card" href="{m['path']}"><span aria-hidden="true">{m['icon']}</span><h3>{esc(k)}</h3><p>{esc(m['description'])}</p><b>Explorar área →</b></a>''' for k,m in CATEGORY_META.items())
    allcards=''.join(tool_card(t) for t in TOOLS)
    return head('Herramientas online para calcular, convertir y descargar | Clicivo',SITE['site_description'],'/',[website_ld,org_ld])+header()+f'''
<main id="contenido"><section class="hero saas-home-hero"><div class="container hero-grid"><div><span class="eyebrow">{len(TOOLS)} herramientas · gratis y sin registro</span><p class="curiosity-hook">La decisión cambia cuando por fin ves los números claros.</p><h1>Calcula, compara y presenta resultados sin perder tiempo.</h1><p>Herramientas para creadores, finanzas, empleo, PDF, imágenes y productividad. Introduce tus datos, prueba escenarios y consigue un resultado listo para copiar o descargar.</p><div class="hero-actions"><a class="btn btn-primary" href="#herramientas">Encontrar mi herramienta <span aria-hidden="true">→</span></a><a class="btn btn-secondary" href="/sobre-clicivo/">Por qué confiar en Clicivo</a></div><div class="hero-proof"><span>✓ Resultado inmediato</span><span>✓ Privacidad por diseño</span><span>✓ Uso profesional</span></div></div><aside class="hero-panel saas-dashboard-preview"><span class="status-dot"><i></i> Herramientas operativas</span><h2>Del dato a una decisión útil</h2><div class="dashboard-number"><small>Ejemplo de proyección</small><strong>1.248 €</strong><span>resultado editable y exportable</span></div><div class="dashboard-bars"><i style="height:34%"></i><i style="height:52%"></i><i style="height:44%"></i><i style="height:70%"></i><i style="height:88%"></i></div><div class="stats"><div class="stat"><b>{len(TOOLS)}</b><span>herramientas</span></div><div class="stat"><b>{len(CATEGORY_META)}</b><span>áreas</span></div><div class="stat"><b>0</b><span>archivos guardados</span></div></div></aside></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">Empieza por aquí</span><h2>Herramientas que convierten datos en decisiones</h2></div><p>Seleccionadas por utilidad, oportunidad de búsqueda y capacidad de ayudarte a comparar o presentar un resultado.</p></div><div class="tool-grid">{''.join(tool_card(t) for t in featured)}</div></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">Una plataforma, varias necesidades</span><h2>Elige el área que quieres resolver</h2></div><p>Documentos, imágenes, productividad, cálculos y herramientas para creadores, organizadas para que encuentres la respuesta sin navegar entre webs.</p></div><div class="category-strip">{catcards}</div></div></section>
<section class="section section-trust"><div class="container"><div class="quality-card"><div><strong>Resultados que puedes reutilizar</strong><p>Las calculadoras profesionales permiten copiar un resumen y descargar informes PDF para clientes o para tu propia revisión.</p></div><div><strong>Privacidad práctica</strong><p>Los PDF, imágenes y textos se procesan en tu dispositivo cuando la página lo indica. Clicivo no recibe esos archivos.</p><a href="/metodologia/">Ver metodología y controles →</a></div></div></div></section>
<section class="section" id="herramientas"><div class="container"><div class="section-head"><div><span class="eyebrow">Catálogo completo</span><h2>¿Qué quieres resolver hoy?</h2></div><p>Busca una tarea concreta o filtra por área.</p></div><div class="search-wrap"><span aria-hidden="true">⌕</span><input type="search" class="catalog-search" placeholder="Ej.: ingresos de TikTok, unir PDF, finiquito, comprimir imágenes…" aria-label="Buscar herramientas"></div><div class="filters"><button class="filter active" data-filter="all">Todas</button>{''.join(f'<button class="filter" data-filter="{esc(k)}">{esc(k)}</button>' for k in CATEGORY_META)}</div><div class="tool-grid" id="tool-grid">{allcards}</div><p class="empty-state">No hemos encontrado una herramienta con ese término.</p></div></section></main>'''+footer()

def legal_page(title,route,body):
    crumbs,crumb_ld=breadcrumb([("Inicio","/"),(title,None)])
    return head(title,f"Consulta la información, condiciones y criterios aplicables a {title.lower()} en el sitio web de Clicivo.",route,crumb_ld)+header()+f'<main id="contenido"><div class="container legal">{crumbs}<h1>{esc(title)}</h1>{body}</div></main>'+footer()


def create_logo_assets():
    assets=PUBLIC/'assets'; ensure_dir(assets)
    svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Clicivo"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#2657d8"/><stop offset="1" stop-color="#12b8b0"/></linearGradient></defs><path d="M49 16A23 23 0 1 0 49 48" fill="none" stroke="url(#g)" stroke-width="11" stroke-linecap="round"/></svg>'''
    (assets/'logo-mark.svg').write_text(svg,encoding='utf-8')
    (assets/'favicon.svg').write_text(svg,encoding='utf-8')
    wordmark='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 270 64" role="img" aria-label="Clicivo"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#2657d8"/><stop offset="1" stop-color="#12b8b0"/></linearGradient></defs><path d="M49 16A23 23 0 1 0 49 48" fill="none" stroke="url(#g)" stroke-width="11" stroke-linecap="round"/><text x="76" y="44" font-family="Arial,Helvetica,sans-serif" font-size="38" font-weight="800" fill="#0f172a">Clicivo</text></svg>'''
    (assets/'logo-clicivo.svg').write_text(wordmark,encoding='utf-8')

    def icon(size, white_background=False):
        im=Image.new('RGBA',(size,size),(255,255,255,255 if white_background else 0))
        d=ImageDraw.Draw(im)
        box=(size*.18,size*.18,size*.82,size*.82)
        width=max(4,int(size*.14))
        # segmented gradient arc, open on right
        for i,angle in enumerate(range(45,316,3)):
            p=i/max(1,len(range(45,316,3))-1)
            c=(int(38+(18-38)*p),int(87+(184-87)*p),int(216+(176-216)*p),255)
            d.arc(box,start=angle,end=angle+4,fill=c,width=width)
        return im
    icon(48).save(assets/'favicon-48.png')
    icon(180, white_background=True).save(assets/'apple-touch-icon.png')

    w,h=1200,630
    im=Image.new('RGB',(w,h),(14,25,54)); d=ImageDraw.Draw(im)
    for y in range(h):
        p=y/(h-1); d.line((0,y,w,y),fill=(int(14+20*p),int(25+45*p),int(54+70*p)))
    mark=icon(220).convert('RGBA'); im.paste(mark,(95,100),mark)
    try:
        font_b=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',88)
        font_s=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',38)
    except OSError:
        font_b=font_s=ImageFont.load_default()
    d.text((345,160),'Clicivo',font=font_b,fill='white')
    d.text((350,280),'Calcula, convierte y decide mejor.',font=font_s,fill=(210,224,255))
    d.rounded_rectangle((350,370,1040,445),radius=25,fill=(255,255,255))
    d.text((390,383),'Herramientas online gratuitas',font=font_s,fill=(20,45,90))
    im.save(assets/'og-clicivo.png',quality=92,optimize=True)


def build_collections():
    # Main categories
    for cat,meta in CATEGORY_META.items():
        subset=[t for t in TOOLS if t['category']==cat]
        write_route(meta['path'],collection_page(f"Herramientas de {cat.lower()}",meta['description'],meta['path'],subset))
    # URL-prefix collections, one per platform and one per exact parent directory.
    prefixes=defaultdict(list)
    for t in TOOLS:
        seg=t['path'].strip('/').split('/')
        prefixes[f'/es/{seg[1]}/'].append(t)
        prefixes['/'+'/'.join(seg[:-1])+'/'].append(t)
    for route,subset in prefixes.items():
        if route in {m['path'] for m in CATEGORY_META.values()}: continue
        route_segments=route.strip('/').split('/')
        seg=route_segments[-1]
        label=SEGMENT_LABELS.get(seg,seg.replace('-',' ').title())
        if len(route_segments)==2:
            title=f"Herramientas para {label}"
        elif len(route_segments)>=3 and route_segments[1] in {'instagram','youtube','tiktok'}:
            platform=SEGMENT_LABELS.get(route_segments[1],route_segments[1].title())
            title=f"{label} de {platform}: calculadoras y herramientas"
        else:
            title=f"{label}: calculadoras y herramientas"
        if route == '/es/instagram/texto/':
            title='Texto para Instagram: herramientas'
        desc=f"Colección gratuita de {title.lower()} en Clicivo, con resultados inmediatos, metodología visible y navegación por herramientas relacionadas."
        write_route(route,collection_page(title,desc,route,subset))


def main():
    # Rebuild the complete publish directory from source files.
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    ensure_dir(PUBLIC/'assets')
    shutil.copy2(ROOT/'src'/'assets'/'styles.css', PUBLIC/'assets'/'styles.css')
    shutil.copy2(ROOT/'src'/'assets'/'site.js', PUBLIC/'assets'/'site.js')
    shutil.copy2(ROOT/'src'/'assets'/'advanced-tools.js', PUBLIC/'assets'/'advanced-tools.js')
    create_logo_assets()
    write_route('/',homepage())
    for t in TOOLS:
        write_route(t['path'],tool_page(t))
    build_collections()

    legal_body=f'''<p><strong>Marca y sitio:</strong> Clicivo · clicivo.com</p><p><strong>Gestión editorial y operativa:</strong> {esc(SITE.get('operator_name','Zurekin Comunicación'))}, proyecto profesional con base en {esc(SITE.get('operator_location','Bilbao, Bizkaia, España'))}.</p><p><strong>Contacto:</strong> <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a></p><h2>Objeto del sitio</h2><p>Clicivo ofrece calculadoras, conversores y herramientas informativas para resolver tareas concretas. El acceso es gratuito y, salvo que se indique lo contrario, no exige registro.</p><h2>Uso responsable y limitación de responsabilidad</h2><p>Los resultados dependen de los datos introducidos y de los supuestos visibles en cada herramienta. Las transformaciones de archivos pueden variar según navegador, formato, memoria y recursos del dispositivo. Las calculadoras financieras, laborales, fiscales o empresariales son estimaciones y no constituyen asesoramiento profesional ni una resolución oficial.</p><h2>Propiedad intelectual</h2><p>El diseño, el código, la estructura y los textos propios de Clicivo están protegidos por la normativa aplicable. Las marcas, bibliotecas y fuentes externas pertenecen a sus respectivos titulares y se identifican cuando procede.</p><h2>Enlaces externos, publicidad y afiliación</h2><p>Clicivo puede financiarse mediante publicidad y enlaces de afiliación. Los enlaces patrocinados se identifican y utilizan atributos adecuados. La existencia de una relación comercial no modifica la metodología de las herramientas.</p><h2>Comunicación de errores</h2><p>Los errores funcionales o de cálculo verificables pueden comunicarse mediante el correo de contacto. Consulta también la <a href="/metodologia/">metodología y política de correcciones</a>.</p>'''
    privacy_body=f'''<p>Esta política explica cómo Clicivo trata datos y tecnologías de medición. Última revisión: {esc(UPDATED)}.</p><h2>Responsable y contacto</h2><p>El proyecto es gestionado editorialmente por {esc(SITE.get('operator_name','Zurekin Comunicación'))}, con base en {esc(SITE.get('operator_location','Bilbao, Bizkaia, España'))}. Puedes contactar en <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a>.</p><h2>Datos introducidos en herramientas</h2><p>Los cálculos y transformaciones se ejecutan en el navegador. Los valores, textos, documentos e imágenes introducidos no se envían a Clicivo ni se guardan en una base de datos del sitio. Algunas herramientas cargan bibliotecas JavaScript desde redes de distribución externas; el código de Clicivo no transfiere a esas bibliotecas los archivos seleccionados.</p><h2>Google Analytics</h2><p>Clicivo utiliza Google Analytics para conocer el uso agregado de las herramientas, detectar errores y mejorar la experiencia. La etiqueta se configura con el consentimiento denegado por defecto y se integra con el sistema de consentimiento de Google.</p><h2>Google AdSense y publicidad</h2><p>Clicivo puede utilizar Google AdSense para mostrar publicidad. Google y sus proveedores pueden tratar información técnica, identificadores y datos de uso para medición, seguridad, limitación de frecuencia y, cuando exista consentimiento, personalización publicitaria. La publicidad no altera el resultado de las herramientas.</p><h2>Consentimiento</h2><p>Para usuarios del Espacio Económico Europeo, Reino Unido y Suiza, Clicivo utiliza la plataforma de gestión del consentimiento de Google. El mensaje permite consentir, no consentir y gestionar opciones. Cuando esté publicado, Google mostrará también un enlace para revisar o retirar la elección.</p><h2>Contacto y conservación</h2><p>Los mensajes enviados al correo de contacto se utilizan para responder y resolver la consulta. Se conservan durante el tiempo necesario para gestionar la comunicación y cumplir obligaciones aplicables.</p><h2>Derechos</h2><p>Puedes solicitar información, acceso, rectificación, supresión, oposición, limitación o portabilidad cuando corresponda mediante el correo indicado. También puedes presentar una reclamación ante la autoridad de control competente.</p><h2>Proveedores y enlaces</h2><p>Consulta la <a href="/cookies/">política de cookies</a> y la página de <a href="/publicidad-y-afiliacion/">publicidad y afiliación</a> para ampliar información.</p>'''
    cookies_body=f'''<p>Las cookies y tecnologías similares permiten recordar preferencias, medir el uso y, con la configuración adecuada, mostrar publicidad. Última revisión: {esc(UPDATED)}.</p><h2>Preferencias y almacenamiento necesario</h2><p>El navegador puede guardar preferencias técnicas necesarias para el funcionamiento o para respetar decisiones de privacidad. Las herramientas principales siguen funcionando aunque no se autoricen finalidades opcionales.</p><h2>Analítica</h2><p>Google Analytics ayuda a medir páginas consultadas, herramientas iniciadas, cálculos completados y errores generales. La configuración de consentimiento parte de un estado denegado y se actualiza conforme a la elección del usuario.</p><h2>Publicidad</h2><p>Google AdSense y sus proveedores pueden utilizar cookies o almacenamiento local para seguridad, medición, limitación de frecuencia y personalización cuando exista consentimiento. Los anuncios no personalizados también pueden necesitar almacenamiento para funciones como prevención del fraude y medición agregada.</p><h2>Gestionar o retirar el consentimiento</h2><p>Clicivo utiliza el mensaje europeo de Google. Cuando esté publicado, el propio sistema mostrará el enlace requerido para revisar o retirar la elección. También puedes borrar cookies y almacenamiento desde la configuración del navegador.</p><h2>Más información</h2><p>Consulta la <a href="/privacidad/">política de privacidad</a> para conocer finalidades, proveedores y derechos.</p>'''
    about_body=f'''<p>Clicivo es una plataforma independiente de herramientas online gratuitas para resolver tareas concretas con rapidez, claridad y el mínimo tratamiento de datos posible.</p><h2>Quién gestiona Clicivo</h2><p>El proyecto está gestionado por <strong>{esc(SITE.get('operator_name','Zurekin Comunicación'))}</strong>, con base en {esc(SITE.get('operator_location','Bilbao, Bizkaia, España'))}. El contacto editorial y técnico es <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a>.</p><h2>Qué ofrecemos</h2><p>Utilidades para PDF, imágenes, texto, códigos QR, finanzas, empleo, negocios y creadores. Cada herramienta tiene una función definida, explica su método, muestra ejemplos y enlaza con alternativas relacionadas.</p><h2>Cómo se construyen las herramientas</h2><p>Las calculadoras se basan en fórmulas visibles y valores editables. Las herramientas de archivos se diseñan para procesar localmente cuando se indica. Antes de publicar se comprueban rutas, enlaces, metadatos, formularios y cálculos principales mediante pruebas automáticas y revisión manual.</p><h2>Privacidad desde el diseño</h2><p>Cuando una herramienta trabaja con archivos o textos, el procesamiento se realiza en el navegador siempre que se indica expresamente. Clicivo no recibe ni almacena esos contenidos.</p><h2>Modelo de financiación</h2><p>Clicivo puede financiarse mediante publicidad, afiliación y futuras funciones profesionales. Estas vías se identifican y no cambian las fórmulas ni los resultados.</p><h2>Compromiso editorial</h2><p>Priorizamos utilidad, lenguaje claro, accesibilidad, fuentes reconocibles y advertencias en materias financieras, laborales o sensibles. No publicamos diagnósticos ni presentamos estimaciones como resultados oficiales.</p>'''
    methodology_body=f'''<p>Esta página explica cómo Clicivo selecciona, crea, prueba y corrige sus herramientas. Última revisión: {esc(UPDATED)}.</p><h2>Selección de herramientas</h2><p>Se priorizan tareas con una intención clara, utilidad repetible y posibilidad de resolver el problema de principio a fin. Se evita crear páginas separadas cuando la función es prácticamente idéntica.</p><h2>Fórmulas y fuentes</h2><p>Cada calculadora muestra su fórmula o método. En empleo, finanzas y otras áreas sensibles se incluyen fuentes oficiales o documentación primaria cuando es posible, además de límites y supuestos.</p><h2>Pruebas de calidad</h2><ul><li>Validación de campos, valores mínimos y máximos.</li><li>Pruebas automáticas de rutas, enlaces, SEO básico y cálculos principales.</li><li>Comprobación de funcionamiento en móvil y escritorio.</li><li>Revisión de descargas, archivos y mensajes de error.</li><li>Verificación de que no aparezcan resultados como NaN, undefined o valores imposibles.</li></ul><h2>Actualizaciones</h2><p>Las páginas muestran una fecha de revisión. Las normas, plataformas y productos pueden cambiar, por lo que los resultados deben contrastarse cuando afecten a decisiones relevantes.</p><h2>Correcciones</h2><p>Para comunicar un error, escribe a <a href="mailto:{esc(SITE['editorial_email'])}">{esc(SITE['editorial_email'])}</a> indicando herramienta, dispositivo, navegador, datos de ejemplo y resultado esperado. Los errores reproducibles se revisan con prioridad y se corrigen sin ocultar las limitaciones de la herramienta.</p><h2>Uso de automatización e inteligencia artificial</h2><p>Clicivo puede utilizar automatización como apoyo de producción y pruebas, pero la responsabilidad editorial se mantiene en el proyecto. El objetivo es reducir trabajo repetitivo, no publicar páginas sin utilidad propia.</p>'''
    terms_body=f'''<p>Estas condiciones regulan el uso de Clicivo. Última revisión: {esc(UPDATED)}.</p><h2>Aceptación y uso permitido</h2><p>Al utilizar el sitio aceptas emplear las herramientas de forma lícita y responsable. No debes intentar dañar, saturar, desactivar o utilizar el servicio para vulnerar derechos de terceros.</p><h2>Resultados y decisiones</h2><p>Los resultados son informativos y dependen de los datos introducidos. Clicivo no garantiza que una estimación coincida con una liquidación oficial, oferta contractual, resolución administrativa, rendimiento futuro o resultado de una plataforma externa.</p><h2>Archivos y contenido del usuario</h2><p>Cuando se indica procesamiento local, los archivos se manipulan en el navegador. El usuario es responsable de disponer de derechos y permisos sobre los documentos, imágenes y textos utilizados.</p><h2>Disponibilidad</h2><p>Las herramientas pueden cambiar, interrumpirse o dejar de ser compatibles con determinados navegadores o formatos. Clicivo puede corregir, actualizar o retirar funciones para mantener seguridad y calidad.</p><h2>Propiedad intelectual y enlaces</h2><p>No se permite copiar de forma sustancial el diseño, los textos o el código propio para explotar un servicio equivalente. Los enlaces externos se ofrecen como referencia y se rigen por las condiciones de sus titulares.</p><h2>Contacto</h2><p>Para consultas sobre estas condiciones: <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a>.</p>'''
    ads_body=f'''<p>Clicivo busca mantener gratuitas sus herramientas principales. Para financiar alojamiento, desarrollo, revisión y mejoras puede utilizar publicidad y afiliación.</p><h2>Google AdSense</h2><p>Clicivo está conectado a Google AdSense mediante el identificador de editor correspondiente. Los anuncios solo se mostrarán cuando el sitio sea aprobado y conforme a la configuración de consentimiento aplicable.</p><h2>Independencia de resultados</h2><p>La publicidad no influye en las fórmulas, resultados, fuentes ni recomendaciones editoriales. Los anuncios se mantendrán separados de botones de cálculo, descarga y navegación para evitar confusión.</p><h2>Enlaces de afiliación</h2><p>Algunos enlaces pueden generar una comisión para Clicivo sin coste adicional para el usuario. Se identifican como patrocinados y se marcan técnicamente con atributos adecuados.</p><h2>Criterios de selección</h2><p>Solo se incluyen servicios relacionados con la herramienta o la tarea. Una relación comercial no garantiza que un producto sea adecuado para todas las personas.</p><h2>Contacto</h2><p>Para consultas sobre publicidad o afiliación: <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a>.</p>'''
    contact_body=f'''<p>Para comunicar un error, proponer una mejora o plantear una consulta sobre Clicivo, escribe a <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a>.</p><h2>Qué información ayuda</h2><p>Indica la URL de la herramienta, el navegador, el dispositivo, los pasos realizados, los valores de ejemplo y el resultado esperado. No envíes documentos privados, contraseñas ni datos personales innecesarios.</p><h2>Prioridad de respuesta</h2><p>Las incidencias funcionales, problemas de accesibilidad, enlaces rotos y errores de cálculo reproducibles se revisan con prioridad.</p><h2>Privacidad</h2><p>Los mensajes se utilizan para gestionar la consulta. Consulta la <a href="/privacidad/">política de privacidad</a> para más información.</p>'''
    write_route('/sobre-clicivo/',legal_page('Quiénes somos','/sobre-clicivo/',about_body))
    write_route('/metodologia/',legal_page('Metodología, fuentes y correcciones','/metodologia/',methodology_body))
    write_route('/condiciones-de-uso/',legal_page('Condiciones de uso','/condiciones-de-uso/',terms_body))
    write_route('/publicidad-y-afiliacion/',legal_page('Publicidad y afiliación','/publicidad-y-afiliacion/',ads_body))
    write_route('/contacto/',legal_page('Contacto','/contacto/',contact_body))
    write_route('/aviso-legal/',legal_page('Aviso legal','/aviso-legal/',legal_body))
    write_route('/privacidad/',legal_page('Política de privacidad','/privacidad/',privacy_body))
    write_route('/cookies/',legal_page('Política de cookies','/cookies/',cookies_body))

    # Preserve legacy URLs already visible in Search Console without indexing duplicates.
    write_redirect('/es/herramientas/', '/')
    write_redirect('/es/youtube/monetizacion/rpm-youtube/', '/es/youtube/monetizacion/ingresos-youtube/')
    write_redirect('/es/finanzas-personales/', '/es/finanzas/')
    write_redirect('/es/negocios-y-autonomos/', '/es/negocios/')
    write_redirect('/politica-cookies/', '/cookies/')

    not_found = head('Página no encontrada','La dirección solicitada no existe o se ha trasladado. Busca una herramienta de Clicivo o vuelve al catálogo.','/404/',None)
    not_found = not_found.replace('index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1','noindex,follow')
    not_found += header()+'''<main id="contenido"><section class="tool-hero"><div class="container"><span class="eyebrow">Error 404</span><h1>No encontramos esa página</h1><p>La herramienta puede haberse trasladado o la dirección puede estar incompleta.</p><div class="hero-actions"><a class="btn btn-primary" href="/">Buscar herramientas</a><a class="btn btn-secondary" href="/contacto/">Informar del problema</a></div></div></section></main>'''+footer()
    (PUBLIC/'404.html').write_text(not_found,encoding='utf-8')

    legacy_redirect_routes={'/es/herramientas/','/es/youtube/monetizacion/rpm-youtube/','/es/finanzas-personales/','/es/negocios-y-autonomos/','/politica-cookies/'}
    routes=['/']+[t['path'] for t in TOOLS]+[m['path'] for m in CATEGORY_META.values()]
    # Include every generated index page except legacy redirect helpers.
    for page_path in PUBLIC.rglob('index.html'):
        rel=page_path.relative_to(PUBLIC)
        route='/' if rel.as_posix()=='index.html' else '/'+rel.parent.as_posix().strip('/')+'/'
        if route not in legacy_redirect_routes:
            routes.append(route)
    routes=sorted(set(routes))
    sitemap=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route in routes:
        priority='1.0' if route=='/' else ('0.9' if any(route==m['path'] for m in CATEGORY_META.values()) else '0.7')
        sitemap.append(f'<url><loc>{esc(canonical(route))}</loc><lastmod>{UPDATED}</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>')
    sitemap.append('</urlset>')
    (PUBLIC/'sitemap.xml').write_text('\n'.join(sitemap),encoding='utf-8')
    (PUBLIC/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n',encoding='utf-8')
    (PUBLIC/'ads.txt').write_text(f'google.com, {SITE["adsense_publisher_id"]}, DIRECT, f08c47fec0942fa0\n',encoding='utf-8')
    (PUBLIC/'CNAME').write_text('clicivo.com\n',encoding='utf-8')
    (PUBLIC/'.nojekyll').write_text('',encoding='utf-8')
    manifest={"name":"Clicivo","short_name":"Clicivo","description":SITE['site_description'],"start_url":"/","display":"standalone","background_color":"#f6f8fc","theme_color":"#2657d8","icons":[{"src":"/assets/apple-touch-icon.png","sizes":"180x180","type":"image/png"},{"src":"/assets/favicon-48.png","sizes":"48x48","type":"image/png"}]}
    (PUBLIC/'manifest.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Built {len(routes)} indexable routes and {len(TOOLS)} tools.')

if __name__=='__main__':
    main()
