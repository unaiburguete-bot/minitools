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
    "Redes sociales": {"path": "/es/redes-sociales/", "icon": "✦", "description": "Analítica, monetización y utilidades para Instagram, YouTube y TikTok."},
    "Finanzas": {"path": "/es/finanzas/", "icon": "€", "description": "Simuladores de ahorro, inversión, hipotecas y préstamos."},
    "Negocios": {"path": "/es/negocios/", "icon": "↗", "description": "Precios, rentabilidad y planificación para profesionales y pequeños negocios."},
    "Empleo": {"path": "/es/empleo/", "icon": "✓", "description": "Salarios, vacaciones, finiquito, indemnización y costes laborales."},
}

SEGMENT_LABELS = {
    "es": "Herramientas",
    "instagram": "Instagram",
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "analitica": "Analítica",
    "texto": "Texto y biografía",
    "monetizacion": "Monetización",
    "finanzas": "Finanzas",
    "ahorro-inversion": "Ahorro e inversión",
    "hipotecas": "Hipotecas",
    "prestamos": "Préstamos",
    "negocios": "Negocios",
    "autonomos": "Autónomos",
    "precios": "Precios",
    "rentabilidad": "Rentabilidad",
    "empleo": "Empleo",
    "extincion-contrato": "Extinción de contrato",
    "liquidacion-laboral": "Liquidación laboral",
    "salarios": "Salarios",
    "vacaciones": "Vacaciones",
    "coste-empresa": "Coste de empresa",
}

PLATFORM_ICONS = {
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
        ("number", "views", "Visualizaciones cualificadas", 500000, 0, None, 1, "Usa la cifra que corresponda al programa."),
        ("number", "rpm", "RPM (€ por 1.000)", 0.5, 0, 1000, 0.01, "Introduce tu RPM o una hipótesis."),
        ("number", "months", "Meses equivalentes", 1, 1, 120, 1, "Para mostrar una proyección anual comparable."),
    ],
    "youtube-rpm-revenue": [
        ("number", "revenue", "Ingresos (€)", 425, 0, None, 0.01, "Ingresos del periodo."),
        ("number", "views", "Visualizaciones", 100000, 1, None, 1, "Visualizaciones del mismo periodo."),
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
        ("number", "views", "Visualizaciones", 250000, 0, None, 1, "Volumen del periodo."),
        ("number", "rpm", "RPM central (€)", 3.5, 0, 1000, 0.01, "Escenario principal."),
        ("number", "months", "Meses del periodo", 1, 1, 120, 1, "Para normalizar y proyectar."),
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
        ("number", "monthly", "Aportación mensual (€)", 200, 0, None, 0.01, "Aportación al final de cada mes."),
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
        ("number", "monthly", "Salario bruto mensual (€)", 2200, 0, None, 0.01, "Base de 30 días."),
        ("number", "salaryDays", "Días de salario pendientes", 15, 0, 31, 0.5, "Días aún no abonados."),
        ("number", "vacationDays", "Vacaciones pendientes", 8, 0, 365, 0.1, "Días a liquidar."),
        ("number", "extraPay", "Pagas extra pendientes (€)", 500, 0, None, 0.01, "Importe devengado."),
        ("number", "other", "Otros conceptos (€)", 0, -10000000, None, 0.01, "Comisiones, bonus…"),
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


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def canonical(route: str) -> str:
    return ORIGIN + (route if route.startswith("/") else "/" + route)


def json_ld(data) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


def head(title: str, description: str, route: str, ld=None, image: str = "/assets/og-clicivo.png") -> str:
    full_title = title if title.endswith("Clicivo") else f"{title} | Clicivo"
    url = canonical(route)
    blocks = [
        "<!doctype html><html lang=\"es\"><head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{esc(full_title)}</title>",
        f'<meta name="description" content="{esc(description[:158])}">',
        f'<link rel="canonical" href="{esc(url)}">',
        '<meta name="robots" content="index,follow,max-image-preview:large">',
        f'<meta property="og:type" content="website"><meta property="og:locale" content="es_ES"><meta property="og:site_name" content="Clicivo"><meta property="og:title" content="{esc(full_title)}"><meta property="og:description" content="{esc(description[:200])}"><meta property="og:url" content="{esc(url)}"><meta property="og:image" content="{esc(canonical(image))}">',
        f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(full_title)}"><meta name="twitter:description" content="{esc(description[:200])}"><meta name="twitter:image" content="{esc(canonical(image))}">',
        '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="/assets/favicon-48.png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest">',
        '<link rel="stylesheet" href="/assets/styles.css">',
        '<meta name="theme-color" content="#2657d8">',
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
<a href="/es/redes-sociales/">Redes</a><a href="/es/finanzas/">Finanzas</a><a href="/es/negocios/">Negocios</a><a href="/es/empleo/">Empleo</a>
</nav></div></header>'''


def footer() -> str:
    return f'''
<footer class="site-footer"><div class="container">
<div class="footer-grid">
<div><a class="brand" href="/"><img src="/assets/logo-mark.svg" width="34" height="34" alt=""><span>Clicivo</span></a><p>Herramientas gratuitas para calcular, comparar y decidir con más claridad.</p></div>
<div><h3>Herramientas</h3><a href="/es/redes-sociales/">Redes sociales</a><a href="/es/finanzas/">Finanzas</a><a href="/es/negocios/">Negocios</a><a href="/es/empleo/">Empleo</a></div>
<div><h3>Información</h3><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a><a href="/cookies/">Cookies</a><button class="btn btn-secondary js-cookie-settings" type="button">Configurar cookies</button></div>
<div><h3>Contacto</h3><a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a><p>Los cálculos se realizan en tu navegador.</p></div>
</div><div class="footer-bottom">© 2026 Clicivo · Última actualización general: {esc(UPDATED)}.</div>
</div></footer>
<div class="cookie-banner" role="dialog" aria-modal="true" aria-labelledby="cookie-title"><strong id="cookie-title">Tu privacidad importa</strong><p>Usamos cookies analíticas solo con tu permiso para entender qué herramientas resultan útiles. Los cálculos funcionan aunque las rechaces.</p><div class="cookie-actions"><button class="btn btn-primary" data-cookie="accept">Aceptar analíticas</button><button class="btn btn-secondary" data-cookie="reject">Rechazar</button><a class="btn btn-secondary" href="/cookies/">Más información</a></div></div>
<script src="/assets/site.js" defer></script></body></html>'''


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
    new = '<span class="badge">Nueva</span>' if tool.get("new") else ''
    return f'''<a class="tool-card" href="{esc(tool['path'])}" data-category="{esc(tool['category'])}" data-search="{esc((tool['title']+' '+' '.join(tool['keywords'])).lower())}"><div class="top"><span class="tool-icon" aria-hidden="true">{esc(tool_icon(tool))}</span>{new}</div><h3>{esc(tool['short_title'])}</h3><p>{esc(tool['description'])}</p><span class="link">Abrir herramienta →</span></a>'''


def field_html(field):
    kind,name,label,value,minv,maxv,step,hint = field
    full = kind in {"textarea"} or name in {"text"}
    cls = "field full" if full else "field"
    if kind == "select":
        options = hint
        opts=[]
        for val,text in options:
            selected=' selected' if str(val)==str(value) else ''
            opts.append(f'<option value="{esc(val)}"{selected}>{esc(text)}</option>')
        control=f'<select id="{esc(name)}" name="{esc(name)}">{"".join(opts)}</select>'
        hint_text=""
    elif kind == "textarea":
        control=f'<textarea id="{esc(name)}" name="{esc(name)}" spellcheck="true">{esc(value)}</textarea>'
        hint_text=hint
    else:
        attrs=[f'type="{esc(kind)}"',f'id="{esc(name)}"',f'name="{esc(name)}"',f'value="{esc(value)}"']
        if minv is not None: attrs.append(f'min="{esc(minv)}"')
        if maxv is not None: attrs.append(f'max="{esc(maxv)}"')
        if step is not None: attrs.append(f'step="{esc(step)}"')
        attrs.append('required')
        control=f'<input {" ".join(attrs)}>'
        hint_text=hint
    small=f'<small>{esc(hint_text)}</small>' if hint_text else ''
    return f'<div class="{cls}"><label for="{esc(name)}">{esc(label)}</label>{control}{small}</div>'


def form_html(tool):
    fields=FORM_SCHEMAS[tool['id']]
    live=tool['id'] in {'instagram-fonts','instagram-counter','instagram-spaces'}
    button='' if live else '<button class="btn btn-primary" type="submit">Calcular</button><button class="btn btn-secondary" type="reset">Restablecer</button>'
    if live:
        button='<button class="btn btn-secondary js-copy-main" type="button">Copiar resultado</button>' if tool['id']=='instagram-spaces' else ''
    return f'''<section class="calculator" aria-labelledby="calc-title"><h2 id="calc-title">Introduce tus datos</h2><form class="tool-form" data-tool="{esc(tool['id'])}" novalidate><div class="fields">{''.join(field_html(f) for f in fields)}</div><div class="form-actions">{button}</div><div class="error-message" role="alert" aria-live="polite"></div></form><p class="privacy-line">🔒 El cálculo se realiza localmente. Clicivo no recibe los datos introducidos.</p></section>'''


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


def related_tools(tool):
    same=[t for t in TOOLS if t['id']!=tool['id'] and t['cluster']==tool['cluster']]
    fallback=[t for t in TOOLS if t['id']!=tool['id'] and t['category']==tool['category'] and t not in same]
    global_fallback=[t for t in TOOLS if t['id']!=tool['id'] and t not in same and t not in fallback]
    return (same+fallback+global_fallback)[:3]


def affiliate_block(tool):
    if tool['category']!='Redes sociales': return ''
    return f'''<aside class="affiliate-card"><h2>Organiza tus métricas en un solo lugar</h2><p>Metricool permite planificar contenido y consultar analítica de redes sociales. Enlace patrocinado: Clicivo puede recibir una comisión sin coste adicional para ti.</p><a class="btn" href="{esc(SITE['affiliate_url'])}" target="_blank" rel="sponsored nofollow noopener" data-affiliate="metricool">Probar Metricool</a></aside>'''


def tool_page(tool):
    crumbs, crumb_ld=breadcrumb(path_breadcrumbs(tool))
    app_ld={
        "@context":"https://schema.org","@type":"WebApplication","name":tool['title'],
        "url":canonical(tool['path']),"applicationCategory":"UtilitiesApplication","operatingSystem":"Any",
        "isAccessibleForFree":True,"description":tool['description'],"inLanguage":"es","dateModified":UPDATED,
        "publisher":{"@type":"Organization","name":"Clicivo","url":ORIGIN}
    }
    faq_ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in tool['faqs']]}
    new='<span class="badge">Nueva herramienta</span>' if tool.get('new') else '<span class="eyebrow">Herramienta mejorada</span>'
    notes=''.join(f'<div class="notice"><strong>Importante:</strong> {esc(n)}</div>' for n in tool.get('notes',[]))
    sources=''.join(f'<li><a href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a></li>' for name,url in tool['sources'])
    faqs=''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in tool['faqs'])
    rel=''.join(f'<a class="related-link" href="{esc(t["path"])}">{esc(t["short_title"])} →</a>' for t in related_tools(tool))
    keywords=', '.join(tool['keywords'][:3])
    return head(tool.get('seo_title',tool['title']),tool['description'],tool['path'],[app_ld,faq_ld,crumb_ld])+header()+f'''
<main id="contenido"><div class="container">{crumbs}</div>
<section class="tool-hero"><div class="container">{new}<h1>{esc(tool['title'])}</h1><p>{esc(tool['description'])}</p></div></section>
<section class="container"><div class="tool-layout">{form_html(tool)}<aside class="result-panel" aria-live="polite"><h2>Resultado</h2><div id="result-body" class="result-placeholder">Completa los campos para ver el resultado.</div></aside></div>{notes}
<div class="content-stack">
<section class="content-card"><h2>Cómo utilizar esta herramienta</h2><div class="steps"><div class="step"><strong>Introduce datos comparables</strong><p>Completa los campos con cifras del mismo periodo y revisa unidades, porcentajes y fechas.</p></div><div class="step"><strong>Calcula y compara</strong><p>Obtén el resultado principal y los indicadores secundarios que ayudan a interpretarlo.</p></div><div class="step"><strong>Prueba escenarios</strong><p>Cambia una variable cada vez para entender qué factor tiene más impacto.</p></div></div></section>
<section class="content-card"><h2>Fórmula y metodología</h2><p class="formula">{esc(tool['formula'])}</p><h3>Ejemplo práctico</h3><p>{esc(tool['example'])}</p><p>La herramienta prioriza transparencia: muestra las variables que utiliza y evita convertir una estimación en una promesa. Para decisiones económicas, laborales o fiscales, contrasta el resultado con documentación y asesoramiento adecuados.</p></section>
{affiliate_block(tool)}
<section class="content-card faq"><h2>Preguntas frecuentes</h2>{faqs}</section>
<section class="content-card"><h2>Fuentes y referencias</h2><p>Estas referencias permiten revisar la metodología o las reglas generales relacionadas. Las plataformas, leyes y productos pueden cambiar.</p><ul class="source-list">{sources}</ul><p><strong>Búsquedas relacionadas:</strong> {esc(keywords)}.</p></section>
<section class="content-card"><h2>Herramientas relacionadas</h2><div class="related-grid">{rel}</div></section>
</div></section></main>'''+footer()


def page_schema(title,desc,route):
    return {"@context":"https://schema.org","@type":"CollectionPage","name":title,"description":desc,"url":canonical(route),"inLanguage":"es","isPartOf":{"@type":"WebSite","name":"Clicivo","url":ORIGIN}}


def collection_page(title,desc,route,tools,eyebrow="Colección de herramientas"):
    crumbs,crumb_ld=breadcrumb([("Inicio","/"),(title,None)])
    cards=''.join(tool_card(t) for t in tools)
    return head(title,desc,route,[page_schema(title,desc,route),crumb_ld])+header()+f'''
<main id="contenido"><div class="container">{crumbs}</div><section class="tool-hero"><div class="container"><span class="eyebrow">{esc(eyebrow)}</span><h1>{esc(title)}</h1><p>{esc(desc)}</p></div></section><section class="section"><div class="container"><div class="search-wrap"><span aria-hidden="true">⌕</span><input type="search" class="catalog-search" placeholder="Buscar en esta colección" aria-label="Buscar herramientas"></div><div class="tool-grid" id="tool-grid">{cards}</div><p class="empty-state">No se han encontrado herramientas con ese término.</p></div></section></main>'''+footer()


def homepage():
    website_ld={"@context":"https://schema.org","@type":"WebSite","name":"Clicivo","url":ORIGIN,"description":SITE['site_description'],"inLanguage":"es","potentialAction":{"@type":"SearchAction","target":ORIGIN+"/?q={search_term_string}","query-input":"required name=search_term_string"}}
    org_ld={"@context":"https://schema.org","@type":"Organization","name":"Clicivo","url":ORIGIN,"logo":canonical('/assets/logo-mark.svg')}
    featured_ids=['compound-interest','instagram-fonts','severance','youtube-income','mortgage-prepayment','vacation-days']
    featured=[next(t for t in TOOLS if t['id']==x) for x in featured_ids]
    catcards=''.join(f'''<a class="category-card" href="{m['path']}"><span aria-hidden="true">{m['icon']}</span><h3>{esc(k)}</h3><p>{esc(m['description'])}</p></a>''' for k,m in CATEGORY_META.items())
    allcards=''.join(tool_card(t) for t in TOOLS)
    return head('Herramientas online gratuitas para calcular y decidir | Clicivo',SITE['site_description'],'/',[website_ld,org_ld])+header()+f'''
<main id="contenido"><section class="hero"><div class="container hero-grid"><div><span class="eyebrow">28 herramientas · sin registro</span><h1>Calcula, compara y decide mejor.</h1><p>Herramientas gratuitas para redes sociales, finanzas, empleo y negocios. Resultados inmediatos, fórmulas visibles y datos procesados en tu navegador.</p><div class="hero-actions"><a class="btn btn-primary" href="#herramientas">Ver herramientas</a><a class="btn btn-secondary" href="/es/finanzas/">Explorar finanzas</a></div></div><aside class="hero-panel"><h2>Una web pensada para resolver</h2><ul><li>10 herramientas nuevas en esta entrega.</li><li>18 herramientas existentes revisadas.</li><li>Sin cuentas, sin subir datos y con fuentes visibles.</li></ul><div class="stats"><div class="stat"><b>28</b><span>herramientas</span></div><div class="stat"><b>4</b><span>áreas</span></div><div class="stat"><b>100 %</b><span>gratuitas</span></div></div></aside></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">Empieza aquí</span><h2>Herramientas destacadas</h2></div><p>Una selección que combina las consultas que ya están apareciendo en Google con utilidades nuevas de alta intención.</p></div><div class="tool-grid">{''.join(tool_card(t) for t in featured)}</div></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">Por área</span><h2>Encuentra tu categoría</h2></div></div><div class="category-strip">{catcards}</div></div></section>
<section class="section" id="herramientas"><div class="container"><div class="section-head"><div><span class="eyebrow">Catálogo completo</span><h2>Todas las herramientas</h2></div><p>Busca por palabra clave o filtra por temática.</p></div><div class="search-wrap"><span aria-hidden="true">⌕</span><input type="search" class="catalog-search" placeholder="Ej.: interés compuesto, Instagram, finiquito…" aria-label="Buscar herramientas"></div><div class="filters"><button class="filter active" data-filter="all">Todas</button>{''.join(f'<button class="filter" data-filter="{esc(k)}">{esc(k)}</button>' for k in CATEGORY_META)}</div><div class="tool-grid" id="tool-grid">{allcards}</div><p class="empty-state">No se han encontrado herramientas con ese término.</p></div></section></main>'''+footer()


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
    create_logo_assets()
    write_route('/',homepage())
    for t in TOOLS:
        write_route(t['path'],tool_page(t))
    build_collections()

    legal_body=f'''<p><strong>Sitio web:</strong> Clicivo · <strong>Dominio:</strong> clicivo.com</p><p><strong>Contacto:</strong> <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a></p><h2>Objeto</h2><p>Clicivo ofrece calculadoras y herramientas informativas. El uso del sitio implica aceptar estas condiciones y utilizar los resultados de forma responsable.</p><h2>Limitación de responsabilidad</h2><p>Los resultados son estimaciones basadas en los datos introducidos. No constituyen asesoramiento financiero, laboral, fiscal, jurídico ni profesional. Las normas, plataformas y productos pueden cambiar.</p><h2>Propiedad intelectual</h2><p>El diseño, el código y los textos propios de Clicivo están protegidos por la normativa aplicable. Las marcas y fuentes externas pertenecen a sus respectivos titulares.</p><h2>Enlaces externos y afiliación</h2><p>Algunos enlaces pueden ser patrocinados. Se identifican como tales y no modifican el precio para la persona usuaria.</p>'''
    privacy_body=f'''<p>Clicivo está diseñado para minimizar la recogida de datos.</p><h2>Datos introducidos en las calculadoras</h2><p>Los cálculos se ejecutan en el navegador. Los valores introducidos no se envían a Clicivo ni se guardan en una base de datos del sitio.</p><h2>Analítica</h2><p>Google Analytics solo se carga después de aceptar las cookies analíticas. Puede generar información técnica y estadística sobre el uso del sitio conforme a la configuración de consentimiento.</p><h2>Contacto</h2><p>Los mensajes enviados a <a href="mailto:{esc(SITE['contact_email'])}">{esc(SITE['contact_email'])}</a> se utilizan únicamente para responder a la consulta.</p><h2>Derechos y cambios</h2><p>Puedes solicitar información o ejercer los derechos que correspondan mediante el correo de contacto. Esta política puede actualizarse cuando cambien el servicio o las obligaciones aplicables.</p>'''
    cookies_body='''<p>Las cookies son pequeños archivos que un sitio puede almacenar en el navegador.</p><h2>Cookies necesarias</h2><p>Clicivo guarda una preferencia local para recordar si aceptaste o rechazaste la analítica. Esta preferencia es necesaria para respetar tu decisión.</p><h2>Cookies analíticas</h2><p>Solo se activan con consentimiento. Ayudan a conocer qué páginas se consultan y a detectar problemas generales de uso.</p><h2>Cambiar tu elección</h2><p>Utiliza el botón «Configurar cookies» del pie de página para volver a mostrar el panel y elegir de nuevo.</p>'''
    write_route('/aviso-legal/',legal_page('Aviso legal','/aviso-legal/',legal_body))
    write_route('/privacidad/',legal_page('Política de privacidad','/privacidad/',privacy_body))
    write_route('/cookies/',legal_page('Política de cookies','/cookies/',cookies_body))

    routes=['/']+[t['path'] for t in TOOLS]+[m['path'] for m in CATEGORY_META.values()]
    # Include every generated index page, avoiding duplicates.
    for p in PUBLIC.rglob('index.html'):
        rel=p.relative_to(PUBLIC)
        route='/' if rel.as_posix()=='index.html' else '/'+rel.parent.as_posix().strip('/')+'/'
        routes.append(route)
    routes=sorted(set(routes))
    sitemap=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route in routes:
        priority='1.0' if route=='/' else ('0.9' if any(route==m['path'] for m in CATEGORY_META.values()) else '0.7')
        sitemap.append(f'<url><loc>{esc(canonical(route))}</loc><lastmod>{UPDATED}</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>')
    sitemap.append('</urlset>')
    (PUBLIC/'sitemap.xml').write_text('\n'.join(sitemap),encoding='utf-8')
    (PUBLIC/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n',encoding='utf-8')
    (PUBLIC/'CNAME').write_text('clicivo.com\n',encoding='utf-8')
    (PUBLIC/'.nojekyll').write_text('',encoding='utf-8')
    manifest={"name":"Clicivo","short_name":"Clicivo","description":SITE['site_description'],"start_url":"/","display":"standalone","background_color":"#f6f8fc","theme_color":"#2657d8","icons":[{"src":"/assets/apple-touch-icon.png","sizes":"180x180","type":"image/png"},{"src":"/assets/favicon-48.png","sizes":"48x48","type":"image/png"}]}
    (PUBLIC/'manifest.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Built {len(routes)} indexable routes and {len(TOOLS)} tools.')

if __name__=='__main__':
    main()
