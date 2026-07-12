from __future__ import annotations

import html
import json
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape

import markdown
import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "site.yaml"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELD_PATTERN = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
SUPPORTED_OPERATIONS = {
    "division": "/",
    "multiplicacion": "*",
    "suma": "+",
    "resta": "-",
}


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        fail("Falta config/site.yaml")

    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    required = [
        "site_name",
        "site_description",
        "site_origin",
        "content_dir",
        "output_dir",
        "template_path",
        "custom_domain",
    ]
    missing = [key for key in required if not config.get(key)]
    if missing:
        fail(f"Faltan claves de configuración: {', '.join(missing)}")

    parsed = urlparse(str(config["site_origin"]))
    if parsed.scheme != "https" or not parsed.netloc:
        fail("site_origin debe ser una URL HTTPS válida")

    base_path = str(config.get("base_path", "")).strip()
    if base_path in {"", "/"}:
        config["base_path"] = ""
    else:
        config["base_path"] = "/" + base_path.strip("/")

    return config


CONFIG = load_config()
CONTENT_DIR = ROOT / CONFIG["content_dir"]
OUTPUT_DIR = ROOT / CONFIG["output_dir"]
TEMPLATE_PATH = ROOT / CONFIG["template_path"]
SITE_ORIGIN = str(CONFIG["site_origin"]).rstrip("/")
BASE_PATH = str(CONFIG.get("base_path", ""))
SITE_NAME = str(CONFIG["site_name"])
SITE_TAGLINE = str(CONFIG.get("site_tagline", CONFIG["site_description"]))
SITE_DESCRIPTION = str(CONFIG["site_description"])
CUSTOM_DOMAIN = str(CONFIG["custom_domain"])
ANALYTICS_MEASUREMENT_ID = str(CONFIG.get("analytics_measurement_id", "")).strip()

if ANALYTICS_MEASUREMENT_ID and not re.fullmatch(r"G-[A-Z0-9]+", ANALYTICS_MEASUREMENT_ID):
    fail("analytics_measurement_id debe tener un formato como G-XXXXXXXXXX")



def analytics_snippet(page_type: str, node: dict[str, Any] | None = None) -> str:
    if not ANALYTICS_MEASUREMENT_ID:
        return ""

    page_params: dict[str, Any] = {"page_type": page_type}
    if node is not None:
        page_params.update(
            {
                "tool_id": str(node["id"]),
                "tool_name": str(node["meta"]["title"]),
                "platform": str(node["vectores"]["plataforma"]),
            }
        )

    params_json = json.dumps(page_params, ensure_ascii=False).replace("</", "<\\/")
    measurement_id = json.dumps(ANALYTICS_MEASUREMENT_ID)
    tool_view = (
        f"window.clicivoTrack('tool_view', {params_json});"
        if node is not None
        else ""
    )

    return f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={html.escape(ANALYTICS_MEASUREMENT_ID, quote=True)}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', {measurement_id});
window.clicivoTrack = function(eventName, parameters) {{
    gtag('event', eventName, parameters || {{}});
}};
document.addEventListener('DOMContentLoaded', function() {{
    {tool_view}
}});
document.addEventListener('click', function(event) {{
    const related = event.target.closest('[data-related-tool]');
    if (related) {{
        window.clicivoTrack('related_tool_clicked', {{
            source_tool_id: document.body.dataset.toolId || '',
            destination_tool_id: related.dataset.relatedTool || '',
            link_url: related.href
        }});
    }}
    const affiliate = event.target.closest('[data-affiliate-link]');
    if (affiliate) {{
        window.clicivoTrack('affiliate_clicked', {{
            tool_id: document.body.dataset.toolId || '',
            link_url: affiliate.href
        }});
    }}
}});
</script>
"""

def site_path(path: str = "") -> str:
    clean = path.strip("/")
    prefix = BASE_PATH
    if clean:
        return f"{prefix}/{clean}/" if prefix else f"/{clean}/"
    return f"{prefix}/" if prefix else "/"


def absolute_url(path: str = "") -> str:
    return f"{SITE_ORIGIN}{site_path(path)}"


def parse_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        fail(f"Front matter ausente o incompleto en {path.relative_to(ROOT)}")
    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        fail(f"YAML inválido en {path.relative_to(ROOT)}: {exc}")
    return metadata, parts[2].strip()


def load_entities() -> list[dict[str, Any]]:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    nodes: list[dict[str, Any]] = []

    for path in sorted(CONTENT_DIR.rglob("*.md")):
        meta, body = parse_front_matter(path)
        relative_parent = path.parent.relative_to(CONTENT_DIR)
        components = list(relative_parent.parts)
        if len(components) < 2:
            fail(
                f"La ruta {path.relative_to(ROOT)} debe incluir idioma y al menos un silo"
            )

        meta["_body_md"] = body
        meta["_language"] = components[0]
        meta["_cluster_path"] = components[1:]
        meta["_source"] = str(path.relative_to(ROOT))
        nodes.append(meta)

    validate_entities(nodes)
    return nodes


def validate_entities(nodes: list[dict[str, Any]]) -> None:
    seen_routes: set[tuple[str, tuple[str, ...], str]] = set()

    for node in nodes:
        source = node.get("_source", "archivo desconocido")
        for key in ["id", "entidad", "meta", "vectores", "calculadora"]:
            if key not in node:
                fail(f"Falta '{key}' en {source}")

        node_id = str(node["id"])
        if not ID_PATTERN.fullmatch(node_id):
            fail(f"ID inválido '{node_id}' en {source}; usa minúsculas y guiones")

        route = (node["_language"], tuple(node["_cluster_path"]), node_id)
        if route in seen_routes:
            fail(f"Ruta duplicada para '{node_id}' en {source}")
        seen_routes.add(route)

        meta = node["meta"]
        if not isinstance(meta, dict) or not meta.get("title") or not meta.get("description"):
            fail(f"meta.title y meta.description son obligatorios en {source}")
        if len(str(meta["title"])) > 65:
            print(f"⚠️ Título largo ({len(str(meta['title']))} caracteres) en {source}")
        if not 80 <= len(str(meta["description"])) <= 170:
            print(
                f"⚠️ Meta description de {len(str(meta['description']))} caracteres en {source}"
            )

        calculator = node["calculadora"]
        inputs = calculator.get("inputs", [])
        algorithm = calculator.get("algoritmo", {})
        steps = algorithm.get("pasos", [])
        if not inputs or not steps or not algorithm.get("output"):
            fail(f"Calculadora incompleta en {source}")

        input_ids: set[str] = set()
        for input_item in inputs:
            input_id = str(input_item.get("id", ""))
            if not FIELD_PATTERN.fullmatch(input_id):
                fail(f"Input inválido '{input_id}' en {source}")
            if input_id in input_ids:
                fail(f"Input duplicado '{input_id}' en {source}")
            input_ids.add(input_id)
            for key in ["label", "type", "placeholder"]:
                if key not in input_item:
                    fail(f"Falta inputs.{input_id}.{key} en {source}")

        available_refs = {f"inputs.{input_id}" for input_id in input_ids}
        step_ids: set[str] = set()
        for step in steps:
            step_id = str(step.get("id", ""))
            operation = step.get("op")
            args = step.get("args")
            if not FIELD_PATTERN.fullmatch(step_id):
                fail(f"Paso inválido '{step_id}' en {source}")
            if step_id in step_ids:
                fail(f"Paso duplicado '{step_id}' en {source}")
            if operation not in SUPPORTED_OPERATIONS:
                fail(
                    f"Operación desconocida '{operation}' en {source}. "
                    f"Permitidas: {', '.join(SUPPORTED_OPERATIONS)}"
                )
            if not isinstance(args, list) or len(args) != 2:
                fail(f"El paso '{step_id}' necesita exactamente dos argumentos en {source}")
            for arg in args:
                if isinstance(arg, (int, float)):
                    continue
                if str(arg) not in available_refs:
                    fail(f"Referencia desconocida '{arg}' en el paso '{step_id}' de {source}")
            step_ids.add(step_id)
            available_refs.add(step_id)

        if algorithm["output"] not in step_ids:
            fail(f"Output '{algorithm['output']}' desconocido en {source}")


def node_route(node: dict[str, Any]) -> str:
    return "/".join([node["_language"], *node["_cluster_path"], node["id"]])


def category_route(node: dict[str, Any]) -> str:
    return "/".join([node["_language"], *node["_cluster_path"]])


def humanize_slug(value: str) -> str:
    return value.replace("-", " ").strip().title()


def category_name(cluster_path: list[str]) -> str:
    if not cluster_path:
        return "Herramientas"
    return " · ".join(humanize_slug(item) for item in cluster_path)


def calculate_semantic_graph(nodes: list[dict[str, Any]]) -> None:
    for current in nodes:
        related: list[dict[str, Any]] = []
        current_vectors = current.get("vectores", {})

        for candidate in nodes:
            if current["id"] == candidate["id"] or current["_language"] != candidate["_language"]:
                continue

            candidate_vectors = candidate.get("vectores", {})
            score = sum(
                1
                for key in ["plataforma", "audiencia", "dificultad", "objetivo"]
                if current_vectors.get(key) is not None
                and current_vectors.get(key) == candidate_vectors.get(key)
            )
            if score:
                related.append(
                    {
                        "id": candidate["id"],
                        "title": candidate["meta"]["title"],
                        "url": site_path(node_route(candidate)),
                        "score": score,
                    }
                )

        current["_related"] = sorted(
            related, key=lambda item: (-item["score"], item["title"])
        )[:5]


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4]


def generate_og_image(title: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 630), color="#0f172a")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((44, 44, 1156, 586), radius=32, outline="#6366f1", width=8)

    brand_font = load_font(48)
    title_font = load_font(58)
    small_font = load_font(28)

    draw.text((86, 86), SITE_NAME, font=brand_font, fill="#a5b4fc")
    y = 205
    for line in wrap_text(draw, title, title_font, 1010):
        draw.text((86, y), line, font=title_font, fill="#ffffff")
        y += 72
    draw.text((86, 530), SITE_ORIGIN.replace("https://", ""), font=small_font, fill="#cbd5e1")
    image.save(output_path, "JPEG", quality=88, optimize=True)


def js_reference(arg: Any) -> str:
    if isinstance(arg, (int, float)):
        return repr(arg)
    return f"values[{json.dumps(str(arg), ensure_ascii=False)}]"


def build_calculator(node: dict[str, Any]) -> str:
    calculator = node["calculadora"]
    inputs = calculator["inputs"]
    algorithm = calculator["algoritmo"]
    function_name = node["id"].replace("-", "_")
    result_id = f"result_{node['id']}"
    error_id = f"error_{node['id']}"

    input_html: list[str] = []
    for item in inputs:
        attributes = [
            f'type="{html.escape(str(item["type"]), quote=True)}"',
            f'id="{html.escape(str(item["id"]), quote=True)}"',
            f'placeholder="{html.escape(str(item["placeholder"]), quote=True)}"',
            'inputmode="decimal"',
        ]
        for attribute in ["min", "max", "step"]:
            if attribute in item:
                attributes.append(
                    f'{attribute}="{html.escape(str(item[attribute]), quote=True)}"'
                )
        input_html.append(
            f'<label for="{html.escape(str(item["id"]), quote=True)}">'
            f'{html.escape(str(item["label"]))}</label>'
            f'<input {" ".join(attributes)}>'
        )

    input_statements: list[str] = []
    for item in inputs:
        input_id = str(item["id"])
        js_input_id = json.dumps(input_id, ensure_ascii=False)
        js_ref = json.dumps(f"inputs.{input_id}", ensure_ascii=False)
        label = json.dumps(str(item["label"]), ensure_ascii=False)
        minimum = item.get("min")
        maximum = item.get("max")
        input_statements.extend(
            [
                f"const raw_{input_id.replace('-', '_')} = document.getElementById({js_input_id}).value.trim();",
                f"if (raw_{input_id.replace('-', '_')} === '') return showError('Completa el campo ' + {label} + '.');",
                f"const number_{input_id.replace('-', '_')} = Number(raw_{input_id.replace('-', '_')});",
                f"if (!Number.isFinite(number_{input_id.replace('-', '_')})) return showError('Introduce un número válido en ' + {label} + '.');",
            ]
        )
        if minimum is not None:
            input_statements.append(
                f"if (number_{input_id.replace('-', '_')} < {repr(minimum)}) return showError('El valor de ' + {label} + ' no puede ser menor que {minimum}.');"
            )
        if maximum is not None:
            input_statements.append(
                f"if (number_{input_id.replace('-', '_')} > {repr(maximum)}) return showError('El valor de ' + {label} + ' no puede ser mayor que {maximum}.');"
            )
        input_statements.append(
            f"values[{js_ref}] = number_{input_id.replace('-', '_')};"
        )

    operation_statements: list[str] = []
    for step in algorithm["pasos"]:
        left = js_reference(step["args"][0])
        right = js_reference(step["args"][1])
        step_key = json.dumps(str(step["id"]), ensure_ascii=False)
        if step["op"] == "division":
            operation_statements.append(
                f"if ({right} === 0) return showError('No es posible dividir entre cero.');"
            )
        operation_statements.append(
            f"values[{step_key}] = {left} {SUPPORTED_OPERATIONS[step['op']]} {right};"
        )

    label = json.dumps(str(algorithm.get("label", "Resultado")), ensure_ascii=False)
    unit = json.dumps(str(algorithm.get("unidad", "")), ensure_ascii=False)
    output = json.dumps(str(algorithm["output"]), ensure_ascii=False)
    event_params = json.dumps(
        {
            "tool_id": str(node["id"]),
            "tool_name": str(node["meta"]["title"]),
            "platform": str(node["vectores"]["plataforma"]),
        },
        ensure_ascii=False,
    )

    return f"""
        {''.join(input_html)}
        <button type="button" onclick="calculate_{function_name}()" class="calc-btn">Calcular ahora</button>
        <p id="{error_id}" class="calc-error" role="alert" hidden></p>
        <div id="{result_id}" class="calc-result-box" role="status" aria-live="polite" hidden></div>
        <script>
            function calculate_{function_name}() {{
                const values = {{}};
                const errorBox = document.getElementById({json.dumps(error_id)});
                const resultBox = document.getElementById({json.dumps(result_id)});
                const showError = (message) => {{
                    resultBox.hidden = true;
                    errorBox.textContent = message;
                    errorBox.hidden = false;
                    if (window.clicivoTrack) {{
                        window.clicivoTrack('calculation_error', {{...{event_params}, error_message: message}});
                    }}
                }};
                errorBox.hidden = true;
                {''.join(input_statements)}
                {''.join(operation_statements)}
                const result = values[{output}];
                if (!Number.isFinite(result)) return showError('No se ha podido calcular el resultado. Revisa los valores.');
                const formatted = new Intl.NumberFormat('es-ES', {{ maximumFractionDigits: 2 }}).format(result);
                resultBox.textContent = {label} + ': ' + formatted + ({unit} ? ' ' + {unit} : '');
                resultBox.hidden = false;
                if (window.clicivoTrack) {{
                    window.clicivoTrack('tool_calculated', {event_params});
                }}
            }}
        </script>
    """


def build_structured_data(node: dict[str, Any], canonical: str) -> str:
    category_url = absolute_url(category_route(node))
    data = [
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": node["meta"]["title"],
            "description": node["meta"]["description"],
            "url": canonical,
            "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "EUR",
            },
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Inicio",
                    "item": absolute_url(),
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": category_name(node["_cluster_path"]),
                    "item": category_url,
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": node["entidad"],
                    "item": canonical,
                },
            ],
        },
    ]
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_tool(node: dict[str, Any], template: str) -> str:
    route = node_route(node)
    canonical = absolute_url(route)
    og_path = f"assets/og/{node['id']}.jpg"
    og_url = absolute_url(og_path)
    related = node.get("_related", [])
    related_html = "".join(
        f'<li><a data-related-tool="{html.escape(str(item["id"]), quote=True)}" '
        f'href="{html.escape(item["url"], quote=True)}">{html.escape(str(item["title"]))}</a></li>'
        for item in related
    ) or '<li class="empty-state">Añadiremos herramientas relacionadas próximamente.</li>'

    faq_html = "".join(
        f'<div class="faq-item"><h3>{html.escape(str(item["q"]))}</h3>'
        f'<p>{html.escape(str(item["a"]))}</p></div>'
        for item in node.get("faqs", [])
    )

    monetization = node.get("monetizacion", {})
    affiliate_url = str(monetization.get("afiliado_url", "")).strip()
    if affiliate_url:
        monetization_html = (
            '<div class="monetization-bar">'
            f'<p>{html.escape(str(monetization.get("cta", "")))}</p>'
            f'<a data-affiliate-link href="{html.escape(affiliate_url, quote=True)}" target="_blank" '
            'rel="sponsored noopener noreferrer nofollow">Ver recurso recomendado →</a>'
            "</div>"
        )
    else:
        monetization_html = ""

    updated = str(node.get("actualizado", node.get("creado", "")))
    body_html = markdown.markdown(
        node["_body_md"], extensions=["extra", "sane_lists"]
    )

    replacements = {
        "{{LANG}}": node["_language"],
        "{{SITE_NAME}}": SITE_NAME,
        "{{HOME_URL}}": site_path(),
        "{{META_TITLE}}": str(node["meta"]["title"]),
        "{{META_DESCRIPTION}}": str(node["meta"]["description"]),
        "{{CANONICAL_URL}}": canonical,
        "{{OG_IMAGE_URL}}": og_url,
        "{{CATEGORY_URL}}": site_path(category_route(node)),
        "{{CATEGORY_NAME}}": category_name(node["_cluster_path"]),
        "{{TOOL_NAME}}": str(node["entidad"]),
        "{{TOOL_H1}}": str(node["vectores"]["intencion"]),
        "{{CALCULATOR_HTML}}": build_calculator(node),
        "{{MONETIZATION_HTML}}": monetization_html,
        "{{ARTICLE_HTML}}": body_html,
        "{{FAQ_HTML}}": faq_html,
        "{{RELATED_HTML}}": related_html,
        "{{LAST_UPDATED}}": updated,
        "{{STRUCTURED_DATA}}": build_structured_data(node, canonical),
        "{{ANALYTICS_SNIPPET}}": analytics_snippet("tool", node),
        "{{TOOL_ID}}": str(node["id"]),
        "{{CURRENT_YEAR}}": str(date.today().year),
    }

    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def render_home(nodes: list[dict[str, Any]]) -> str:
    cards = "".join(
        f"""
        <article class="tool-card-home">
            <span class="tag">{html.escape(str(node['vectores']['plataforma']))}</span>
            <h2><a href="{html.escape(site_path(node_route(node)), quote=True)}">{html.escape(str(node['meta']['title']))}</a></h2>
            <p>{html.escape(str(node['meta']['description']))}</p>
            <a class="card-link" href="{html.escape(site_path(node_route(node)), quote=True)}">Abrir herramienta →</a>
        </article>
        """
        for node in nodes
    ) or '<p class="empty-catalog">Estamos preparando las primeras herramientas.</p>'

    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": absolute_url(),
            "description": SITE_DESCRIPTION,
            "inLanguage": CONFIG.get("default_language", "es"),
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return f"""<!doctype html>
<html lang="{html.escape(str(CONFIG.get('default_language', 'es')))}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(SITE_NAME)} | Herramientas y calculadoras gratuitas</title>
    <meta name="description" content="{html.escape(SITE_DESCRIPTION, quote=True)}">
    <link rel="canonical" href="{absolute_url()}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="{html.escape(SITE_NAME, quote=True)}">
    <meta property="og:title" content="{html.escape(SITE_NAME, quote=True)} | Herramientas gratuitas">
    <meta property="og:description" content="{html.escape(SITE_DESCRIPTION, quote=True)}">
    <meta property="og:url" content="{absolute_url()}">
    <meta property="og:image" content="{absolute_url('assets/og/clicivo-home.jpg')}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(SITE_NAME, quote=True)} | Herramientas gratuitas">
    <meta name="twitter:description" content="{html.escape(SITE_DESCRIPTION, quote=True)}">
    <meta name="twitter:image" content="{absolute_url('assets/og/clicivo-home.jpg')}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script type="application/ld+json">{schema}</script>
    {analytics_snippet("home")}
    <style>
        :root {{ --bg:#f8fafc;--surface:#fff;--text:#0f172a;--muted:#64748b;--border:#e2e8f0;--primary:#4f46e5;--primary-light:#eef2ff; }}
        * {{ box-sizing:border-box; }}
        body {{ margin:0;background:var(--bg);color:var(--text);font-family:'Plus Jakarta Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased; }}
        .wrap {{ width:min(1080px,calc(100% - 40px));margin:0 auto; }}
        header {{ padding:22px 0;border-bottom:1px solid var(--border);background:rgba(255,255,255,.88);backdrop-filter:blur(10px); }}
        .brand {{ color:var(--text);text-decoration:none;font-size:1.25rem;font-weight:800;letter-spacing:-.03em; }}
        .brand-mark {{ color:var(--primary); }}
        .hero {{ padding:88px 0 54px;text-align:center; }}
        .eyebrow {{ color:var(--primary);font-size:.8rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase; }}
        h1 {{ max-width:780px;margin:14px auto 18px;font-size:clamp(2.5rem,7vw,4.8rem);line-height:1.02;letter-spacing:-.06em; }}
        .hero p {{ max-width:680px;margin:0 auto;color:var(--muted);font-size:1.15rem;line-height:1.7; }}
        .catalog-title {{ margin:20px 0 24px;font-size:1.6rem;letter-spacing:-.03em; }}
        .grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px;padding-bottom:80px; }}
        .tool-card-home {{ padding:26px;border:1px solid var(--border);border-radius:20px;background:var(--surface);box-shadow:0 10px 30px rgba(15,23,42,.04); }}
        .tag {{ display:inline-block;padding:5px 9px;border-radius:999px;background:var(--primary-light);color:var(--primary);font-size:.75rem;font-weight:800;text-transform:uppercase; }}
        .tool-card-home h2 {{ margin:16px 0 9px;font-size:1.28rem;line-height:1.35;letter-spacing:-.025em; }}
        .tool-card-home h2 a {{ color:var(--text);text-decoration:none; }}
        .tool-card-home p {{ color:var(--muted);line-height:1.65; }}
        .card-link {{ display:inline-block;margin-top:7px;color:var(--primary);font-weight:700;text-decoration:none; }}
        footer {{ border-top:1px solid var(--border);padding:28px 0;color:var(--muted);font-size:.9rem; }}
    </style>
</head>
<body>
<header><div class="wrap"><a class="brand" href="{site_path()}"><span class="brand-mark">◆</span> {html.escape(SITE_NAME)}</a></div></header>
<main>
    <section class="hero wrap">
        <div class="eyebrow">Herramientas gratuitas</div>
        <h1>{html.escape(SITE_TAGLINE)}</h1>
        <p>{html.escape(SITE_DESCRIPTION)} Sin instalaciones, sin registros y con resultados inmediatos.</p>
    </section>
    <section class="wrap" aria-labelledby="catalog-title">
        <h2 class="catalog-title" id="catalog-title">Herramientas disponibles</h2>
        <div class="grid">{cards}</div>
    </section>
</main>
<footer><div class="wrap">© {date.today().year} {html.escape(SITE_NAME)}. Herramientas claras para decisiones rápidas.</div></footer>
</body>
</html>"""


def render_category(route: str, nodes: list[dict[str, Any]]) -> str:
    parts = route.split("/")
    language = parts[0]
    cluster_parts = parts[1:]
    title = category_name(cluster_parts)
    cards = "".join(
        f'<article><h2><a href="{html.escape(site_path(node_route(node)), quote=True)}">{html.escape(str(node["meta"]["title"]))}</a></h2>'
        f'<p>{html.escape(str(node["meta"]["description"]))}</p></article>'
        for node in nodes
    )
    canonical = absolute_url(route)
    return f"""<!doctype html>
<html lang="{html.escape(language)}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | {html.escape(SITE_NAME)}</title>
<meta name="description" content="Herramientas gratuitas de {html.escape(title)} en {html.escape(SITE_NAME)}.">
<link rel="canonical" href="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
{analytics_snippet("category")}
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f8fafc;color:#0f172a;font-family:'Plus Jakarta Sans',system-ui,sans-serif}}.wrap{{width:min(900px,calc(100% - 40px));margin:0 auto}}header{{background:#fff;border-bottom:1px solid #e2e8f0;padding:20px 0}}header a{{color:#0f172a;text-decoration:none;font-weight:800}}main{{padding:60px 0 80px}}.crumbs{{font-size:.9rem;color:#64748b;margin-bottom:20px}}.crumbs a{{color:#4f46e5;text-decoration:none}}h1{{font-size:clamp(2.2rem,6vw,3.8rem);letter-spacing:-.05em;margin:0 0 14px}}.intro{{color:#64748b;font-size:1.1rem;margin-bottom:34px}}.grid{{display:grid;gap:18px}}article{{background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:24px}}article h2{{margin:0 0 8px;font-size:1.25rem}}article a{{color:#0f172a;text-decoration:none}}article p{{color:#64748b;margin:0;line-height:1.6}}
</style>
</head>
<body><header><div class="wrap"><a href="{site_path()}">◆ {html.escape(SITE_NAME)}</a></div></header>
<main class="wrap"><div class="crumbs"><a href="{site_path()}">Inicio</a> › {html.escape(title)}</div><h1>{html.escape(title)}</h1><p class="intro">Calculadoras y utilidades gratuitas para resolver tareas de {html.escape(title.lower())}.</p><div class="grid">{cards}</div></main></body></html>"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def compile_site() -> None:
    nodes = load_entities()
    calculate_semantic_graph(nodes)

    if not TEMPLATE_PATH.exists():
        fail(f"Falta {TEMPLATE_PATH.relative_to(ROOT)}")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    sitemap_entries: list[tuple[str, str | None]] = [(absolute_url(), None)]

    generate_og_image(
        f"{SITE_NAME}: {SITE_TAGLINE}", OUTPUT_DIR / "assets" / "og" / "clicivo-home.jpg"
    )
    write_text(OUTPUT_DIR / "index.html", render_home(nodes))

    categories: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for node in nodes:
        route = node_route(node)
        output_path = OUTPUT_DIR / route / "index.html"
        write_text(output_path, render_tool(node, template))
        generate_og_image(
            str(node["meta"]["title"]), OUTPUT_DIR / "assets" / "og" / f"{node['id']}.jpg"
        )
        sitemap_entries.append((absolute_url(route), str(node.get("actualizado", "")) or None))
        categories[category_route(node)].append(node)

    for route, category_nodes in sorted(categories.items()):
        write_text(OUTPUT_DIR / route / "index.html", render_category(route, category_nodes))
        sitemap_entries.append((absolute_url(route), None))

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, last_modified in sitemap_entries:
        sitemap_lines.append("  <url>")
        sitemap_lines.append(f"    <loc>{xml_escape(url)}</loc>")
        if last_modified:
            sitemap_lines.append(f"    <lastmod>{xml_escape(last_modified)}</lastmod>")
        sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>")
    write_text(OUTPUT_DIR / "sitemap.xml", "\n".join(sitemap_lines) + "\n")

    write_text(
        OUTPUT_DIR / "robots.txt",
        f"User-agent: *\nAllow: /\n\nSitemap: {absolute_url('sitemap.xml')}\n",
    )
    write_text(OUTPUT_DIR / "CNAME", CUSTOM_DOMAIN + "\n")
    write_text(OUTPUT_DIR / ".nojekyll", "")
    write_text(
        OUTPUT_DIR / "404.html",
        f"<!doctype html><html lang=\"es\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Página no encontrada | {html.escape(SITE_NAME)}</title><body style=\"font-family:system-ui;text-align:center;padding:10vh 20px\"><h1>404</h1><p>La página que buscas no existe.</p><p><a href=\"{site_path()}\">Volver a {html.escape(SITE_NAME)}</a></p></body></html>",
    )

    print(
        f"🚀 Clicivo compilado: {len(nodes)} herramienta(s), "
        f"{len(categories)} categoría(s) y {len(sitemap_entries)} URL(s) en sitemap."
    )


if __name__ == "__main__":
    compile_site()
