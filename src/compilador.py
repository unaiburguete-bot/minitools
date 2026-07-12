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
    "potencia": "**",
    "minimo": "min",
    "maximo": "max",
}
SUPPORTED_VALIDATIONS = {
    "mayor_que": ">",
    "mayor_o_igual": ">=",
    "menor_que": "<",
    "menor_o_igual": "<=",
    "igual": "===",
    "distinto": "!==",
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
LEGAL_OWNER = str(CONFIG.get("legal_owner", "Unai Burguete"))
LEGAL_TRADE_NAME = str(CONFIG.get("legal_trade_name", "Zurekin Comunicación"))
LEGAL_NIF = str(CONFIG.get("legal_nif", "44571964B"))
LEGAL_ADDRESS = str(CONFIG.get("legal_address", "Calle Santutxu 80, 48006 Bilbao, España"))
LEGAL_EMAIL = str(CONFIG.get("legal_email", "info@zurekincomunicacion.com"))

if ANALYTICS_MEASUREMENT_ID and not re.fullmatch(r"G-[A-Z0-9]+", ANALYTICS_MEASUREMENT_ID):
    fail("analytics_measurement_id debe tener un formato como G-XXXXXXXXXX")



def analytics_snippet(page_type: str, node: dict[str, Any] | None = None) -> str:
    """Implementa consentimiento básico: GA4 no se carga hasta aceptar."""
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
    cookie_policy_url = json.dumps(site_path("politica-cookies"), ensure_ascii=False)

    return f"""
<style>
.cookie-banner{{position:fixed;left:20px;right:20px;bottom:20px;z-index:9999;max-width:760px;margin:auto;background:#fff;border:1px solid #cbd5e1;border-radius:18px;box-shadow:0 22px 70px rgba(15,23,42,.22);padding:22px;color:#0f172a;font-family:'Plus Jakarta Sans',system-ui,sans-serif}}
.cookie-banner[hidden]{{display:none}}
.cookie-banner h2{{font-size:1.1rem;margin:0 0 8px}}
.cookie-banner p{{font-size:.92rem;line-height:1.55;color:#475569;margin:0 0 16px}}
.cookie-banner a{{color:#4f46e5}}
.cookie-actions{{display:flex;gap:10px;flex-wrap:wrap}}
.cookie-actions button{{flex:1;min-width:140px;border:1px solid #4f46e5;border-radius:10px;padding:11px 15px;font:inherit;font-weight:800;cursor:pointer}}
.cookie-accept{{background:#4f46e5;color:#fff}}
.cookie-reject{{background:#fff;color:#4338ca}}
.cookie-settings-link{{background:none!important;border:0!important;color:#475569!important;text-decoration:underline;min-width:auto!important;flex:0 0 auto!important}}
.cookie-preferences{{position:fixed;left:16px;bottom:16px;z-index:9998;border:1px solid #cbd5e1;background:#fff;color:#334155;border-radius:999px;padding:9px 13px;font:600 .82rem 'Plus Jakarta Sans',system-ui,sans-serif;cursor:pointer;box-shadow:0 6px 20px rgba(15,23,42,.12)}}
@media(max-width:560px){{.cookie-banner{{left:12px;right:12px;bottom:12px;padding:18px}}.cookie-actions{{display:grid}}.cookie-actions button{{width:100%}}}}
</style>
<script>
(function(){{
    const measurementId = {measurement_id};
    const pageParams = {params_json};
    const storageKey = 'clicivo_cookie_consent';
    const cookiePolicyUrl = {cookie_policy_url};
    let analyticsLoaded = false;

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function(){{dataLayer.push(arguments);}};
    gtag('consent', 'default', {{
        analytics_storage: 'denied',
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied',
        functionality_storage: 'granted',
        security_storage: 'granted',
        wait_for_update: 500
    }});

    function loadAnalytics() {{
        if (analyticsLoaded) return;
        analyticsLoaded = true;
        gtag('consent', 'update', {{ analytics_storage: 'granted' }});
        const script = document.createElement('script');
        script.async = true;
        script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
        document.head.appendChild(script);
        gtag('js', new Date());
        gtag('config', measurementId, {{ anonymize_ip: true }});
        window.clicivoTrack = function(eventName, parameters) {{
            gtag('event', eventName, parameters || {{}});
        }};
        if (pageParams.tool_id) window.clicivoTrack('tool_view', pageParams);
    }}

    window.clicivoTrack = function() {{}};

    function setConsent(value) {{
        localStorage.setItem(storageKey, value);
        const banner = document.getElementById('clicivo-cookie-banner');
        if (banner) banner.hidden = true;
        if (value === 'accepted') loadAnalytics();
        else gtag('consent', 'update', {{ analytics_storage: 'denied' }});
    }}

    function showBanner() {{
        const banner = document.getElementById('clicivo-cookie-banner');
        if (banner) banner.hidden = false;
    }}

    document.addEventListener('DOMContentLoaded', function() {{
        document.body.insertAdjacentHTML('beforeend',
            '<div id="clicivo-cookie-banner" class="cookie-banner" role="dialog" aria-modal="true" aria-labelledby="clicivo-cookie-title" hidden>' +
            '<h2 id="clicivo-cookie-title">Tu privacidad en Clicivo</h2>' +
            '<p>Usamos cookies analíticas de Google Analytics para saber qué herramientas resultan útiles y mejorar la web. Puedes aceptar o rechazar estas cookies. Las necesarias para guardar tu elección no requieren consentimiento. <a href="' + cookiePolicyUrl + '">Más información</a>.</p>' +
            '<div class="cookie-actions"><button type="button" id="clicivo-cookie-accept" class="cookie-accept">Aceptar analítica</button><button type="button" id="clicivo-cookie-reject" class="cookie-reject">Rechazar</button></div></div>' +
            '<button type="button" id="clicivo-cookie-settings" class="cookie-preferences">Configurar cookies</button>'
        );
        const choice = localStorage.getItem(storageKey);
        if (choice === 'accepted') loadAnalytics();
        else if (choice !== 'rejected') showBanner();

        document.getElementById('clicivo-cookie-accept')?.addEventListener('click', () => setConsent('accepted'));
        document.getElementById('clicivo-cookie-reject')?.addEventListener('click', () => setConsent('rejected'));
        document.getElementById('clicivo-cookie-settings')?.addEventListener('click', showBanner);

        document.addEventListener('click', function(event) {{
            const related = event.target.closest('[data-related-tool]');
            if (related) window.clicivoTrack('related_tool_clicked', {{
                source_tool_id: document.body.dataset.toolId || '',
                destination_tool_id: related.dataset.relatedTool || '',
                link_url: related.href
            }});
            const affiliate = event.target.closest('[data-affiliate-link]');
            if (affiliate) {{
                let destinationDomain = '';
                try {{ destinationDomain = new URL(affiliate.href).hostname; }} catch (error) {{}}
                window.clicivoTrack('affiliate_click', {{
                    tool_id: document.body.dataset.toolId || '',
                    affiliate_provider: affiliate.dataset.affiliateProvider || '',
                    affiliate_network: affiliate.dataset.affiliateNetwork || '',
                    placement: affiliate.dataset.affiliatePlacement || 'after_calculator',
                    destination_domain: destinationDomain
                }});
            }}
        }});
    }});
}})();
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


def absolute_file_url(path: str) -> str:
    clean = path.lstrip("/")
    prefix = BASE_PATH.rstrip("/")
    return f"{SITE_ORIGIN}{prefix}/{clean}"


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
            if str(input_item.get("type")) == "select":
                options = input_item.get("options")
                if not isinstance(options, list) or not options:
                    fail(f"El select '{input_id}' necesita opciones en {source}")
                for option in options:
                    if not isinstance(option, dict) or "value" not in option or not option.get("label"):
                        fail(f"Opción inválida en el select '{input_id}' de {source}")

        available_refs = {f"inputs.{input_id}" for input_id in input_ids}
        for validation in calculator.get("validaciones", []):
            operation = validation.get("op")
            args = validation.get("args")
            if operation not in SUPPORTED_VALIDATIONS:
                fail(
                    f"Validación desconocida '{operation}' en {source}. "
                    f"Permitidas: {', '.join(SUPPORTED_VALIDATIONS)}"
                )
            if not isinstance(args, list) or len(args) != 2:
                fail(f"Cada validación necesita exactamente dos argumentos en {source}")
            for arg in args:
                if isinstance(arg, (int, float)):
                    continue
                if str(arg) not in available_refs:
                    fail(f"Referencia desconocida '{arg}' en una validación de {source}")
            if not validation.get("mensaje"):
                fail(f"Falta el mensaje de una validación en {source}")

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

        for result in algorithm.get("resultados", []):
            result_id = str(result.get("id", ""))
            if result_id not in step_ids:
                fail(f"Resultado '{result_id}' desconocido en {source}")
            if not result.get("label"):
                fail(f"Falta la etiqueta del resultado '{result_id}' en {source}")


def node_route(node: dict[str, Any]) -> str:
    return "/".join([node["_language"], *node["_cluster_path"], node["id"]])


def category_route(node: dict[str, Any]) -> str:
    return "/".join([node["_language"], *node["_cluster_path"]])


CATEGORY_LABELS = {
    "youtube": "YouTube",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "twitch": "Twitch",
    "monetizacion": "Monetización",
    "analitica": "Analítica",
    "crecimiento": "Crecimiento",
    "finanzas": "Finanzas",
    "hipotecas": "Hipotecas",
    "ahorro-inversion": "Ahorro e inversión",
    "prestamos": "Préstamos",
    "negocios": "Negocios",
    "precios": "Precios",
    "rentabilidad": "Rentabilidad",
    "autonomos": "Autónomos",
    "empleo": "Empleo y salarios",
    "salarios": "Salarios",
    "liquidacion-laboral": "Liquidación laboral",
    "extincion-contrato": "Extinción del contrato",
}

SOCIAL_PLATFORMS = {"youtube", "instagram", "tiktok", "twitch"}
FAMILY_DEFINITIONS = {
    "redes-sociales": {
        "label": "Redes sociales",
        "title": "Herramientas para redes sociales",
        "description": (
            "Calculadoras gratuitas para creadores, agencias y marcas que trabajan "
            "con YouTube, Instagram y otras plataformas sociales."
        ),
    },
    "finanzas": {
        "label": "Finanzas",
        "title": "Herramientas de finanzas",
        "description": (
            "Simuladores gratuitos para calcular hipotecas, préstamos, ahorro e "
            "interés compuesto con resultados claros y comparables."
        ),
    },
    "negocios": {
        "label": "Negocios",
        "title": "Herramientas para negocios y autónomos",
        "description": (
            "Calculadoras gratuitas para fijar precios, analizar rentabilidad y "
            "planificar tarifas en pequeños negocios y actividades profesionales."
        ),
    },
    "empleo": {
        "label": "Empleo y salarios",
        "title": "Herramientas de empleo y salarios",
        "description": (
            "Calculadoras orientativas para entender el sueldo neto, la liquidación "
            "laboral y determinadas indemnizaciones por extinción del contrato."
        ),
    },
}
PLATFORM_DESCRIPTIONS = {
    "youtube": "Calculadoras para analizar monetización, ingresos, RPM, visualizaciones y horas de reproducción en YouTube.",
    "instagram": "Herramientas para medir engagement, alcance y crecimiento de perfiles de Instagram.",
    "tiktok": "Herramientas para analizar rendimiento, crecimiento y monetización en TikTok.",
    "twitch": "Calculadoras para streamers, audiencias y monetización en Twitch.",
    "finanzas-personales": "Simuladores para planificar hipotecas, préstamos, ahorro e inversión con cifras orientativas y transparentes.",
    "negocios-y-autonomos": "Herramientas para fijar precios, controlar márgenes, calcular rentabilidad y definir tarifas profesionales.",
    "empleo-y-salarios": "Calculadoras laborales orientativas para estimar sueldo neto, liquidaciones e indemnizaciones en España.",
}


def slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = (
        normalized.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ü", "u")
        .replace("ñ", "n")
    )
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-") or "otros"


def humanize_slug(value: str) -> str:
    normalized = value.strip().lower()
    return CATEGORY_LABELS.get(normalized, value.replace("-", " ").strip().title())


def platform_key(node: dict[str, Any]) -> str:
    platform = str(node.get("vectores", {}).get("plataforma", "")).strip()
    return slugify(platform) if platform else "otros"


def platform_label(node: dict[str, Any]) -> str:
    platform = str(node.get("vectores", {}).get("plataforma", "")).strip()
    return platform or humanize_slug(platform_key(node))


def platform_theme(node: dict[str, Any]) -> str:
    key = platform_key(node)
    supported_themes = SOCIAL_PLATFORMS | {"finanzas-personales", "negocios-y-autonomos", "empleo-y-salarios"}
    return f"theme-{key}" if key in supported_themes else "theme-default"


def family_key(node: dict[str, Any]) -> str:
    explicit = str(node.get("vectores", {}).get("familia", "")).strip()
    if explicit:
        return slugify(explicit)
    if platform_key(node) in SOCIAL_PLATFORMS:
        return "redes-sociales"
    return "otras-herramientas"


def family_info(key: str) -> dict[str, str]:
    if key in FAMILY_DEFINITIONS:
        return FAMILY_DEFINITIONS[key]
    label = humanize_slug(key)
    return {
        "label": label,
        "title": f"Herramientas de {label.lower()}",
        "description": f"Calculadoras y utilidades gratuitas de {label.lower()}.",
    }


def family_route(node: dict[str, Any]) -> str:
    return "/".join([node["_language"], family_key(node)])


def platform_route(node: dict[str, Any]) -> str:
    return "/".join([node["_language"], platform_key(node)])


def topic_name(node: dict[str, Any]) -> str:
    topic_parts = list(node.get("_cluster_path", []))[1:]
    if not topic_parts:
        return "Herramientas"
    return " · ".join(humanize_slug(item) for item in topic_parts)


def category_name(cluster_path: list[str]) -> str:
    if not cluster_path:
        return "Herramientas"
    return " · ".join(humanize_slug(item) for item in cluster_path)


def category_page_title(node: dict[str, Any]) -> str:
    platform = platform_label(node)
    topic = topic_name(node)
    if platform_key(node) == "negocios-y-autonomos":
        if topic == "Herramientas":
            return "Herramientas para negocios y autónomos"
        return f"Herramientas de {topic.lower()} para negocios y autónomos"
    if platform_key(node) == "empleo-y-salarios":
        if topic == "Herramientas":
            return "Herramientas de empleo y salarios"
        return f"Herramientas de {topic.lower()}"
    if topic == "Herramientas":
        return f"Herramientas de {platform}"
    return f"Herramientas de {topic.lower()} de {platform}"


def all_tools_route(language: str = "es") -> str:
    return f"{language}/herramientas"

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
        input_id = html.escape(str(item["id"]), quote=True)
        label_html = (
            f'<label for="{input_id}">{html.escape(str(item["label"]))}</label>'
        )
        if str(item["type"]) == "select":
            options_html = [
                f'<option value="">{html.escape(str(item["placeholder"]))}</option>'
            ]
            for option in item.get("options", []):
                options_html.append(
                    f'<option value="{html.escape(str(option["value"]), quote=True)}">'
                    f'{html.escape(str(option["label"]))}</option>'
                )
            input_html.append(
                label_html + f'<select id="{input_id}">{"".join(options_html)}</select>'
            )
            continue

        attributes = [
            f'type="{html.escape(str(item["type"]), quote=True)}"',
            f'id="{input_id}"',
            f'placeholder="{html.escape(str(item["placeholder"]), quote=True)}"',
            'inputmode="decimal"',
        ]
        for attribute in ["min", "max", "step"]:
            if attribute in item:
                attributes.append(
                    f'{attribute}="{html.escape(str(item[attribute]), quote=True)}"'
                )
        input_html.append(label_html + f'<input {" ".join(attributes)}>')

    input_statements: list[str] = []
    for item in inputs:
        input_id = str(item["id"])
        safe_input_id = input_id.replace("-", "_")
        js_input_id = json.dumps(input_id, ensure_ascii=False)
        js_ref = json.dumps(f"inputs.{input_id}", ensure_ascii=False)
        label = json.dumps(str(item["label"]), ensure_ascii=False)
        minimum = item.get("min")
        maximum = item.get("max")
        input_statements.extend(
            [
                f"const raw_{safe_input_id} = document.getElementById({js_input_id}).value.trim().replace(',', '.');",
                f"if (raw_{safe_input_id} === '') return showError('Completa el campo ' + {label} + '.');",
                f"const number_{safe_input_id} = Number(raw_{safe_input_id});",
                f"if (!Number.isFinite(number_{safe_input_id})) return showError('Introduce un número válido en ' + {label} + '.');",
            ]
        )
        if minimum is not None:
            input_statements.append(
                f"if (number_{safe_input_id} < {repr(minimum)}) return showError('El valor de ' + {label} + ' no puede ser menor que {minimum}.');"
            )
        if maximum is not None:
            input_statements.append(
                f"if (number_{safe_input_id} > {repr(maximum)}) return showError('El valor de ' + {label} + ' no puede ser mayor que {maximum}.');"
            )
        input_statements.append(
            f"values[{js_ref}] = number_{safe_input_id};"
        )

    validation_statements: list[str] = []
    for validation in calculator.get("validaciones", []):
        left = js_reference(validation["args"][0])
        right = js_reference(validation["args"][1])
        operator = SUPPORTED_VALIDATIONS[str(validation["op"])]
        message = json.dumps(str(validation["mensaje"]), ensure_ascii=False)
        validation_statements.append(
            f"if (!({left} {operator} {right})) return showError({message});"
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
        if step["op"] == "potencia":
            operation_statements.append(
                f"values[{step_key}] = Math.pow({left}, {right});"
            )
        elif step["op"] == "minimo":
            operation_statements.append(
                f"values[{step_key}] = Math.min({left}, {right});"
            )
        elif step["op"] == "maximo":
            operation_statements.append(
                f"values[{step_key}] = Math.max({left}, {right});"
            )
        else:
            operation_statements.append(
                f"values[{step_key}] = {left} {SUPPORTED_OPERATIONS[step['op']]} {right};"
            )

    configured_results = algorithm.get("resultados") or [
        {
            "id": algorithm["output"],
            "label": algorithm.get("label", "Resultado"),
            "formato": "numero",
            "unidad": algorithm.get("unidad", ""),
        }
    ]
    result_definitions = [
        {
            "id": str(item["id"]),
            "label": str(item["label"]),
            "format": str(item.get("formato", "numero")),
            "unit": str(item.get("unidad", "")),
        }
        for item in configured_results
    ]
    results_json = json.dumps(result_definitions, ensure_ascii=False).replace("</", "<\\/")

    event_params = json.dumps(
        {
            "tool_id": str(node["id"]),
            "tool_name": str(node["meta"]["title"]),
            "platform": str(node["vectores"]["plataforma"]),
            "family": str(node["vectores"].get("familia", "")),
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
                const resultDefinitions = {results_json};
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
                {''.join(validation_statements)}
                {''.join(operation_statements)}

                for (const item of resultDefinitions) {{
                    if (!Number.isFinite(values[item.id])) {{
                        return showError('No se ha podido calcular el resultado. Revisa los valores.');
                    }}
                }}

                const grid = document.createElement('div');
                grid.className = 'calc-result-grid';
                for (const item of resultDefinitions) {{
                    const card = document.createElement('div');
                    card.className = 'calc-result-item';
                    const label = document.createElement('span');
                    label.className = 'calc-result-label';
                    label.textContent = item.label;
                    const value = document.createElement('strong');
                    value.className = 'calc-result-value';
                    const options = item.format === 'moneda'
                        ? {{style:'currency', currency:'EUR', maximumFractionDigits:2}}
                        : {{maximumFractionDigits:2}};
                    let formatted = new Intl.NumberFormat('es-ES', options).format(values[item.id]);
                    if (item.format !== 'moneda' && item.unit) formatted += ' ' + item.unit;
                    value.textContent = formatted;
                    card.append(label, value);
                    grid.appendChild(card);
                }}
                resultBox.replaceChildren(grid);
                resultBox.hidden = false;
                if (window.clicivoTrack) {{
                    window.clicivoTrack('tool_calculated', {event_params});
                }}
            }}
        </script>
    """


def build_structured_data(node: dict[str, Any], canonical: str) -> str:
    family = family_info(family_key(node))
    breadcrumbs = [
        ("Inicio", absolute_url()),
        (family["label"], absolute_url(family_route(node))),
        (platform_label(node), absolute_url(platform_route(node))),
        (topic_name(node), absolute_url(category_route(node))),
        (str(node["entidad"]), canonical),
    ]
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
                    "position": position,
                    "name": name,
                    "item": item,
                }
                for position, (name, item) in enumerate(breadcrumbs, start=1)
            ],
        },
    ]
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")



def build_monetization(node: dict[str, Any]) -> str:
    """Construye un bloque de afiliación claro, contextual y sin scripts externos."""
    monetization = node.get("monetizacion") or {}
    affiliate_url = str(monetization.get("afiliado_url", "")).strip()
    if not affiliate_url:
        return ""

    parsed = urlparse(affiliate_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        fail(
            f"afiliado_url debe ser una URL HTTP(S) válida en la herramienta {node.get('id', 'sin-id')}"
        )

    provider = str(monetization.get("proveedor", "")).strip()
    network = str(monetization.get("red", "")).strip()
    label = str(
        monetization.get("etiqueta", "Recomendación con enlace de afiliado")
    ).strip()
    title = str(
        monetization.get("titulo")
        or provider
        or "Recurso recomendado"
    ).strip()
    description = str(
        monetization.get("descripcion")
        or monetization.get("cta")
        or "Una opción relacionada con esta herramienta que puede ayudarte a dar el siguiente paso."
    ).strip()
    button = str(
        monetization.get("boton")
        or (f"Conocer {provider}" if provider else "Ver recurso recomendado")
    ).strip()
    disclosure = str(
        monetization.get("aviso")
        or "Clicivo puede recibir una comisión si contratas desde este enlace, sin coste adicional para ti."
    ).strip()

    provider_html = (
        f'<p class="affiliate-provider">Recurso recomendado: {html.escape(provider)}</p>'
        if provider
        else ""
    )

    return (
        '<section class="affiliate-card" aria-label="Recomendación comercial">'
        f'<p class="affiliate-label">{html.escape(label)}</p>'
        '<div class="affiliate-main">'
        '<div class="affiliate-copy">'
        f'{provider_html}'
        f'<h2>{html.escape(title)}</h2>'
        f'<p>{html.escape(description)}</p>'
        '</div>'
        f'<a class="affiliate-button" data-affiliate-link '
        f'data-affiliate-provider="{html.escape(provider, quote=True)}" '
        f'data-affiliate-network="{html.escape(network, quote=True)}" '
        'data-affiliate-placement="after_calculator" '
        f'href="{html.escape(affiliate_url, quote=True)}" target="_blank" '
        'rel="sponsored noopener noreferrer nofollow">'
        f'{html.escape(button)} <span aria-hidden="true">→</span></a>'
        '</div>'
        f'<p class="affiliate-disclosure">{html.escape(disclosure)}</p>'
        '</section>'
    )

def render_tool(node: dict[str, Any], template: str) -> str:
    route = node_route(node)
    canonical = absolute_url(route)
    og_path = f"assets/og/{node['id']}.jpg"
    og_url = absolute_file_url(og_path)
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

    monetization_html = build_monetization(node)

    updated = str(node.get("actualizado", node.get("creado", "")))
    body_html = markdown.markdown(
        node["_body_md"], extensions=["extra", "sane_lists"]
    )
    family = family_info(family_key(node))

    replacements = {
        "{{LANG}}": node["_language"],
        "{{THEME_CLASS}}": platform_theme(node),
        "{{SITE_NAME}}": SITE_NAME,
        "{{HOME_URL}}": site_path(),
        "{{SOCIAL_URL}}": site_path(f"{node['_language']}/redes-sociales"),
        "{{FINANCE_URL}}": site_path(f"{node['_language']}/finanzas"),
        "{{BUSINESS_URL}}": site_path(f"{node['_language']}/negocios"),
        "{{EMPLOYMENT_URL}}": site_path(f"{node['_language']}/empleo"),
        "{{ALL_TOOLS_URL}}": site_path(all_tools_route(node["_language"])),
        "{{META_TITLE}}": str(node["meta"]["title"]),
        "{{META_DESCRIPTION}}": str(node["meta"]["description"]),
        "{{CANONICAL_URL}}": canonical,
        "{{OG_IMAGE_URL}}": og_url,
        "{{FAMILY_URL}}": site_path(family_route(node)),
        "{{FAMILY_NAME}}": family["label"],
        "{{PLATFORM_URL}}": site_path(platform_route(node)),
        "{{PLATFORM_NAME}}": platform_label(node),
        "{{CATEGORY_URL}}": site_path(category_route(node)),
        "{{CATEGORY_NAME}}": category_name(node["_cluster_path"]),
        "{{TOPIC_NAME}}": topic_name(node),
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
        "{{LEGAL_URL}}": site_path("aviso-legal"),
        "{{PRIVACY_URL}}": site_path("privacidad"),
        "{{COOKIES_URL}}": site_path("politica-cookies"),
    }

    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def home_tool_card(node: dict[str, Any]) -> str:
    return f"""
    <article class="tool-card-home platform-{html.escape(platform_key(node), quote=True)}">
        <span class="tag">{html.escape(platform_label(node))}</span>
        <h3><a href="{html.escape(site_path(node_route(node)), quote=True)}">{html.escape(str(node['meta']['title']))}</a></h3>
        <p>{html.escape(str(node['meta']['description']))}</p>
        <a class="card-link" href="{html.escape(site_path(node_route(node)), quote=True)}">Abrir herramienta →</a>
    </article>
    """


def render_home(nodes: list[dict[str, Any]]) -> str:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        by_family[family_key(node)].append(node)

    family_cards: list[str] = []
    for key, family_nodes in sorted(by_family.items()):
        info = family_info(key)
        route = family_route(family_nodes[0])
        platforms = sorted({platform_label(node) for node in family_nodes})
        platform_text = " · ".join(platforms)
        family_cards.append(
            f"""
            <article class="family-card family-{html.escape(key, quote=True)}">
                <div class="family-icon">◎</div>
                <p class="family-count">{len(family_nodes)} herramientas</p>
                <h2><a href="{html.escape(site_path(route), quote=True)}">{html.escape(info['title'])}</a></h2>
                <p>{html.escape(info['description'])}</p>
                <div class="platform-list">{html.escape(platform_text)}</div>
                <a class="family-link" href="{html.escape(site_path(route), quote=True)}">Explorar categoría →</a>
            </article>
            """
        )

    featured_nodes = sorted(
        nodes,
        key=lambda item: (str(item.get("actualizado", "")), str(item["meta"]["title"])),
        reverse=True,
    )[:6]
    featured_cards = "".join(home_tool_card(node) for node in featured_nodes)

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
    <meta property="og:image" content="{absolute_file_url('assets/og/clicivo-home.jpg')}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(SITE_NAME, quote=True)} | Herramientas gratuitas">
    <meta name="twitter:description" content="{html.escape(SITE_DESCRIPTION, quote=True)}">
    <meta name="twitter:image" content="{absolute_file_url('assets/og/clicivo-home.jpg')}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script type="application/ld+json">{schema}</script>
    {analytics_snippet("home")}
    <style>
        :root {{ --bg:#f8fafc;--surface:#fff;--text:#0f172a;--muted:#64748b;--border:#e2e8f0;--primary:#4f46e5;--primary-light:#eef2ff; }}
        * {{ box-sizing:border-box; }}
        body {{ margin:0;background:var(--bg);color:var(--text);font-family:'Plus Jakarta Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased; }}
        .wrap {{ width:min(1100px,calc(100% - 40px));margin:0 auto; }}
        header {{ border-bottom:1px solid var(--border);background:rgba(255,255,255,.9);backdrop-filter:blur(10px); }}
        .header-inner {{ min-height:70px;display:flex;align-items:center;justify-content:space-between;gap:24px; }}
        .brand {{ color:var(--text);text-decoration:none;font-size:1.25rem;font-weight:800;letter-spacing:-.03em; }}
        .brand-mark {{ color:var(--primary); }}
        .site-nav {{ display:flex;align-items:center;gap:20px; }}
        .site-nav a {{ color:#475569;text-decoration:none;font-size:.9rem;font-weight:700; }}
        .site-nav a:hover {{ color:var(--primary); }}
        .hero {{ padding:88px 0 54px;text-align:center; }}
        .eyebrow {{ color:var(--primary);font-size:.8rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase; }}
        h1 {{ max-width:780px;margin:14px auto 18px;font-size:clamp(2.5rem,7vw,4.8rem);line-height:1.02;letter-spacing:-.06em; }}
        .hero p {{ max-width:680px;margin:0 auto;color:var(--muted);font-size:1.15rem;line-height:1.7; }}
        .section-head {{ display:flex;justify-content:space-between;align-items:end;gap:20px;margin:20px 0 24px; }}
        .section-head h2 {{ margin:0;font-size:1.7rem;letter-spacing:-.035em; }}
        .section-head p {{ margin:6px 0 0;color:var(--muted); }}
        .section-head a {{ color:var(--primary);font-weight:800;text-decoration:none;white-space:nowrap; }}
        .family-grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:22px;margin-bottom:62px; }}
        .family-card {{ position:relative;overflow:hidden;padding:34px;border:1px solid var(--border);border-radius:26px;background:var(--surface);box-shadow:0 16px 45px rgba(15,23,42,.055); }}
        .family-card::after {{ content:"";position:absolute;width:230px;height:230px;right:-110px;top:-120px;border-radius:50%;background:linear-gradient(135deg,rgba(79,70,229,.15),rgba(14,165,233,.12)); }}
        .family-icon {{ position:relative;z-index:1;width:46px;height:46px;display:grid;place-items:center;border-radius:14px;background:var(--primary-light);color:var(--primary);font-size:1.35rem;font-weight:800; }}
        .family-count {{ margin:24px 0 8px!important;color:var(--primary)!important;font-size:.78rem!important;font-weight:800;text-transform:uppercase;letter-spacing:.08em; }}
        .family-card h2 {{ position:relative;z-index:1;margin:0 0 10px;font-size:1.7rem;line-height:1.2;letter-spacing:-.035em; }}
        .family-card h2 a {{ color:var(--text);text-decoration:none; }}
        .family-card p {{ position:relative;z-index:1;color:var(--muted);line-height:1.7; }}
        .platform-list {{ position:relative;z-index:1;margin:18px 0;color:#334155;font-size:.9rem;font-weight:800; }}
        .family-link {{ position:relative;z-index:1;color:var(--primary);font-weight:800;text-decoration:none; }}
        .family-redes-sociales {{ background:linear-gradient(145deg,#fff,#f7f7ff);border-color:#dfe3ff; }}
        .family-finanzas {{ background:linear-gradient(145deg,#fff,#f2fbf7);border-color:#cfe9dc; }}
        .family-finanzas::after {{ background:linear-gradient(135deg,rgba(5,150,105,.17),rgba(14,116,144,.12)); }}
        .family-finanzas .family-icon {{ background:#e7f8f0;color:#047857; }}
        .family-finanzas .family-count,.family-finanzas .family-link {{ color:#047857!important; }}
        .family-negocios {{ background:linear-gradient(145deg,#fff,#f4f9fc);border-color:#cddfea; }}
        .family-negocios::after {{ background:linear-gradient(135deg,rgba(8,47,73,.16),rgba(245,158,11,.16)); }}
        .family-negocios .family-icon {{ background:#e7f2f7;color:#0f4c66; }}
        .family-negocios .family-count,.family-negocios .family-link {{ color:#0f5b78!important; }}
        .tools-grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px;padding-bottom:80px; }}
        .tool-card-home {{ padding:26px;border:1px solid var(--border);border-radius:20px;background:var(--surface);box-shadow:0 10px 30px rgba(15,23,42,.04); }}
        .tag {{ display:inline-block;padding:5px 9px;border-radius:999px;background:var(--primary-light);color:var(--primary);font-size:.75rem;font-weight:800;text-transform:uppercase; }}
        .tool-card-home h3 {{ margin:16px 0 9px;font-size:1.22rem;line-height:1.38;letter-spacing:-.025em; }}
        .tool-card-home h3 a {{ color:var(--text);text-decoration:none; }}
        .tool-card-home.platform-instagram {{ border-color:#efd2e2;background:linear-gradient(145deg,#fff,#fff7fc);box-shadow:0 14px 36px rgba(131,58,180,.08); }}
        .tool-card-home.platform-instagram .tag {{ color:#fff;background:linear-gradient(100deg,#f77737,#d62976,#833ab4); }}
        .tool-card-home.platform-instagram .card-link {{ color:#c02675; }}
        .tool-card-home.platform-finanzas-personales {{ border-color:#cfe9dc;background:linear-gradient(145deg,#fff,#f4fbf8);box-shadow:0 14px 36px rgba(5,150,105,.07); }}
        .tool-card-home.platform-finanzas-personales .tag {{ color:#065f46;background:#dff7eb; }}
        .tool-card-home.platform-finanzas-personales .card-link {{ color:#047857; }}
        .tool-card-home.platform-negocios-y-autonomos {{ border-color:#cddfea;background:linear-gradient(145deg,#fff,#f3f8fb);box-shadow:0 14px 36px rgba(8,47,73,.07); }}
        .tool-card-home.platform-negocios-y-autonomos .tag {{ color:#fff;background:linear-gradient(105deg,#0f4c66,#0e7490 62%,#d97706); }}
        .tool-card-home.platform-negocios-y-autonomos .card-link {{ color:#0f5b78; }}
        .tool-card-home.platform-empleo-y-salarios {{ border-color:#ded6ea;background:linear-gradient(145deg,#fff,#f8f6fc);box-shadow:0 14px 36px rgba(76,29,149,.065); }}
        .tool-card-home.platform-empleo-y-salarios .tag {{ color:#fff;background:linear-gradient(105deg,#312e81,#6d28d9 62%,#a16207); }}
        .tool-card-home.platform-empleo-y-salarios .card-link {{ color:#5b21b6; }}
        .tool-card-home p {{ color:var(--muted);line-height:1.65; }}
        .card-link {{ display:inline-block;margin-top:7px;color:var(--primary);font-weight:700;text-decoration:none; }}
        footer {{ border-top:1px solid var(--border);padding:28px 0;color:var(--muted);font-size:.9rem; }}
        @media(max-width:700px){{.header-inner{{align-items:flex-start;flex-direction:column;padding:16px 0}}.site-nav{{gap:14px;flex-wrap:wrap}}.hero{{padding-top:62px}}.section-head{{align-items:flex-start;flex-direction:column}}}}
    </style>
</head>
<body>
<header><div class="wrap header-inner"><a class="brand" href="{site_path()}"><span class="brand-mark">◆</span> {html.escape(SITE_NAME)}</a><nav class="site-nav" aria-label="Navegación principal"><a href="{site_path('es/redes-sociales')}">Redes sociales</a><a href="{site_path('es/finanzas')}">Finanzas</a><a href="{site_path('es/negocios')}">Negocios</a><a href="{site_path('es/empleo')}">Empleo</a><a href="{site_path(all_tools_route())}">Todas las herramientas</a></nav></div></header>
<main>
    <section class="hero wrap">
        <div class="eyebrow">Herramientas gratuitas</div>
        <h1>{html.escape(SITE_TAGLINE)}</h1>
        <p>{html.escape(SITE_DESCRIPTION)} Sin instalaciones, sin registros y con resultados inmediatos.</p>
    </section>
    <section class="wrap" aria-labelledby="families-title">
        <div class="section-head"><div><h2 id="families-title">Explora por categoría</h2><p>Encuentra cada herramienta dentro de un área clara y fácil de recorrer.</p></div><a href="{site_path(all_tools_route())}">Ver todas →</a></div>
        <div class="family-grid">{''.join(family_cards)}</div>
    </section>
    <section class="wrap" aria-labelledby="featured-title">
        <div class="section-head"><div><h2 id="featured-title">Herramientas destacadas</h2><p>Accesos rápidos a algunas de las calculadoras disponibles.</p></div><a href="{site_path(all_tools_route())}">Catálogo completo →</a></div>
        <div class="tools-grid">{featured_cards}</div>
    </section>
</main>
<footer><div class="wrap">© {date.today().year} {html.escape(SITE_NAME)}. Herramientas claras para decisiones rápidas. · {legal_footer()}</div></footer>
</body>
</html>"""


def catalog_breadcrumbs(items: list[tuple[str, str | None]]) -> str:
    parts: list[str] = []
    for label, url in items:
        if url:
            parts.append(f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>')
        else:
            parts.append(f'<span>{html.escape(label)}</span>')
    return " › ".join(parts)


def render_catalog_shell(
    *,
    language: str,
    title: str,
    description: str,
    canonical: str,
    breadcrumbs: str,
    content_html: str,
    page_type: str,
    theme_class: str = "theme-default",
) -> str:
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "url": canonical,
            "description": description,
            "inLanguage": language,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""<!doctype html>
<html lang="{html.escape(language)}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | {html.escape(SITE_NAME)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{html.escape(SITE_NAME, quote=True)}">
<meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script type="application/ld+json">{schema}</script>
{analytics_snippet(page_type)}
<style>
:root{{--bg:#f8fafc;--surface:#fff;--text:#0f172a;--muted:#64748b;--border:#e2e8f0;--primary:#4f46e5;--primary-light:#eef2ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:'Plus Jakarta Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}}.wrap{{width:min(1040px,calc(100% - 40px));margin:0 auto}}
header{{border-bottom:1px solid var(--border);background:rgba(255,255,255,.9);backdrop-filter:blur(10px)}}.header-inner{{min-height:70px;display:flex;align-items:center;justify-content:space-between;gap:24px}}.brand{{color:var(--text);text-decoration:none;font-size:1.2rem;font-weight:800;letter-spacing:-.03em}}.brand-mark{{color:var(--primary)}}.site-nav{{display:flex;gap:20px;align-items:center}}.site-nav a{{color:#475569;text-decoration:none;font-size:.9rem;font-weight:700}}.site-nav a:hover{{color:var(--primary)}}
main{{padding:56px 0 84px}}.crumbs{{font-size:.88rem;color:var(--muted);margin-bottom:22px}}.crumbs a{{color:var(--primary);text-decoration:none;font-weight:700}}h1{{max-width:850px;font-size:clamp(2.25rem,6vw,4rem);line-height:1.05;letter-spacing:-.055em;margin:0 0 16px}}.intro{{max-width:780px;color:var(--muted);font-size:1.08rem;line-height:1.75;margin:0 0 38px}}
.directory-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px}}.directory-card{{position:relative;overflow:hidden;background:var(--surface);border:1px solid var(--border);border-radius:22px;padding:28px;box-shadow:0 12px 36px rgba(15,23,42,.045)}}.directory-card h2{{margin:12px 0 9px;font-size:1.35rem;line-height:1.3;letter-spacing:-.025em}}.directory-card h2 a{{color:var(--text);text-decoration:none}}.directory-card p{{color:var(--muted);line-height:1.65;margin:0}}.pill{{display:inline-block;padding:5px 10px;border-radius:999px;background:var(--primary-light);color:var(--primary);font-size:.73rem;font-weight:800;text-transform:uppercase}}.open-link{{display:inline-block;margin-top:16px;color:var(--primary);font-size:.9rem;font-weight:800;text-decoration:none}}.subtopics{{margin-top:13px;color:#475569;font-size:.87rem;font-weight:700}}
.catalog-section{{margin-top:48px}}.catalog-section:first-child{{margin-top:0}}.catalog-section-head{{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:18px}}.catalog-section h2{{margin:0;font-size:1.65rem;letter-spacing:-.035em}}.catalog-section-head a{{color:var(--primary);font-weight:800;text-decoration:none}}.tools-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px}}.tool-card{{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:23px}}.tool-card h3{{font-size:1.08rem;line-height:1.42;margin:12px 0 8px}}.tool-card h3 a{{color:var(--text);text-decoration:none}}.tool-card p{{color:var(--muted);font-size:.92rem;line-height:1.6;margin:0}}.tool-card.platform-instagram{{border-color:#efd2e2;background:linear-gradient(145deg,#fff,#fff8fc)}}.tool-card.platform-instagram .pill{{color:#fff;background:linear-gradient(100deg,#f77737,#d62976,#833ab4)}}
body.theme-instagram{{--bg:#fff8fc;--text:#29162f;--muted:#765f7c;--border:#f0d7e5;--primary:#d62976;--primary-light:#fff0f7;background:radial-gradient(circle at 10% 5%,rgba(247,119,55,.18),transparent 26rem),radial-gradient(circle at 92% 8%,rgba(131,58,180,.15),transparent 30rem),linear-gradient(180deg,#fff8fc,#fff 55%,#faf7ff)}}body.theme-instagram header{{background:rgba(255,250,253,.9)}}body.theme-instagram h1{{background:linear-gradient(100deg,#713080,#d62976 52%,#e85d18);-webkit-background-clip:text;background-clip:text;color:transparent}}body.theme-instagram .directory-card{{border-color:#efd2e2;background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(255,247,252,.94));box-shadow:0 20px 55px rgba(131,58,180,.09)}}body.theme-instagram .pill{{color:#fff;background:linear-gradient(100deg,#f77737,#d62976,#833ab4)}}
body.theme-finanzas-personales{{--bg:#f5fbf8;--text:#102a23;--muted:#587067;--border:#cfe9dc;--primary:#047857;--primary-light:#e7f8f0;background:radial-gradient(circle at 10% 5%,rgba(16,185,129,.13),transparent 28rem),radial-gradient(circle at 92% 8%,rgba(14,116,144,.10),transparent 30rem),linear-gradient(180deg,#f4fbf8,#fff 58%,#f4faf8)}}body.theme-finanzas-personales header{{background:rgba(248,253,251,.92);border-bottom-color:#d5eadf}}body.theme-finanzas-personales h1{{color:#123c31}}body.theme-finanzas-personales .directory-card,body.theme-finanzas-personales .tool-card{{border-color:#cfe9dc;background:linear-gradient(145deg,#fff,#f4fbf8);box-shadow:0 20px 55px rgba(5,150,105,.07)}}body.theme-finanzas-personales .pill{{color:#065f46;background:#dff7eb}}body.theme-finanzas-personales .open-link,body.theme-finanzas-personales .crumbs a{{color:#047857}}
body.theme-negocios-y-autonomos{{--bg:#f4f8fb;--text:#102b3a;--muted:#5b7180;--border:#cddfea;--primary:#0f5b78;--primary-light:#e7f2f7;background:radial-gradient(circle at 10% 5%,rgba(14,116,144,.13),transparent 28rem),radial-gradient(circle at 92% 8%,rgba(245,158,11,.12),transparent 30rem),linear-gradient(180deg,#f3f8fb,#fff 58%,#f8fafb)}}body.theme-negocios-y-autonomos header{{background:rgba(248,251,253,.93);border-bottom-color:#d6e4ec}}body.theme-negocios-y-autonomos h1{{color:#123b4d}}body.theme-negocios-y-autonomos .directory-card,body.theme-negocios-y-autonomos .tool-card{{border-color:#cddfea;background:linear-gradient(145deg,#fff,#f2f7fa);box-shadow:0 20px 55px rgba(8,47,73,.07)}}body.theme-negocios-y-autonomos .pill{{color:#fff;background:linear-gradient(105deg,#0f4c66,#0e7490 62%,#d97706)}}body.theme-negocios-y-autonomos .open-link,body.theme-negocios-y-autonomos .crumbs a{{color:#0f5b78}}
body.theme-empleo-y-salarios{{--bg:#f8f7fc;--text:#211b35;--muted:#655f76;--border:#ded8ea;--primary:#5b21b6;--primary-light:#f0eafe;background:radial-gradient(circle at 10% 5%,rgba(91,33,182,.12),transparent 28rem),radial-gradient(circle at 92% 8%,rgba(161,98,7,.10),transparent 30rem),linear-gradient(180deg,#f8f7fc,#fff 58%,#faf9fc)}}body.theme-empleo-y-salarios header{{background:rgba(251,250,253,.93);border-bottom-color:#e3ddec}}body.theme-empleo-y-salarios h1{{color:#2f2350}}body.theme-empleo-y-salarios .directory-card,body.theme-empleo-y-salarios .tool-card{{border-color:#ded8ea;background:linear-gradient(145deg,#fff,#f8f6fc);box-shadow:0 20px 55px rgba(76,29,149,.065)}}body.theme-empleo-y-salarios .pill{{color:#fff;background:linear-gradient(105deg,#312e81,#6d28d9 62%,#a16207)}}body.theme-empleo-y-salarios .open-link,body.theme-empleo-y-salarios .crumbs a{{color:#5b21b6}}
footer{{background:#fff;border-top:1px solid var(--border);padding:28px 0;color:var(--muted);font-size:.88rem}}footer a{{color:#475569}}
@media(max-width:700px){{.header-inner{{align-items:flex-start;flex-direction:column;padding:16px 0}}.site-nav{{gap:14px;flex-wrap:wrap}}main{{padding-top:38px}}.catalog-section-head{{align-items:flex-start;flex-direction:column}}}}
</style>
</head>
<body class="{html.escape(theme_class, quote=True)}">
<header><div class="wrap header-inner"><a class="brand" href="{site_path()}"><span class="brand-mark">◆</span> {html.escape(SITE_NAME)}</a><nav class="site-nav" aria-label="Navegación principal"><a href="{site_path('es/redes-sociales')}">Redes sociales</a><a href="{site_path('es/finanzas')}">Finanzas</a><a href="{site_path('es/negocios')}">Negocios</a><a href="{site_path('es/empleo')}">Empleo</a><a href="{site_path(all_tools_route(language))}">Todas las herramientas</a></nav></div></header>
<main class="wrap"><nav class="crumbs" aria-label="Migas de pan">{breadcrumbs}</nav><h1>{html.escape(title)}</h1><p class="intro">{html.escape(description)}</p>{content_html}</main>
<footer><div class="wrap">© {date.today().year} {html.escape(SITE_NAME)}. Herramientas claras para decisiones rápidas. · {legal_footer()}</div></footer>
</body></html>"""


def render_family(route: str, nodes: list[dict[str, Any]]) -> str:
    language, key = route.split("/", 1)
    info = family_info(key)
    by_platform: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        by_platform[platform_key(node)].append(node)

    cards: list[str] = []
    for key_platform, platform_nodes in sorted(by_platform.items()):
        first = platform_nodes[0]
        topics = sorted({topic_name(node) for node in platform_nodes})
        description = PLATFORM_DESCRIPTIONS.get(
            key_platform,
            f"Herramientas gratuitas para {platform_label(first)}.",
        )
        cards.append(
            f'<article class="directory-card"><span class="pill">{len(platform_nodes)} herramientas</span>'
            f'<h2><a href="{html.escape(site_path(platform_route(first)), quote=True)}">{html.escape(platform_label(first))}</a></h2>'
            f'<p>{html.escape(description)}</p><div class="subtopics">{" · ".join(html.escape(topic) for topic in topics)}</div>'
            f'<a class="open-link" href="{html.escape(site_path(platform_route(first)), quote=True)}">Ver herramientas de {html.escape(platform_label(first))} →</a></article>'
        )

    breadcrumbs = catalog_breadcrumbs([
        ("Inicio", site_path()),
        (info["label"], None),
    ])
    platform_keys = {platform_key(node) for node in nodes}
    family_theme = platform_theme(nodes[0]) if len(platform_keys) == 1 else "theme-default"
    return render_catalog_shell(
        language=language,
        title=info["title"],
        description=info["description"],
        canonical=absolute_url(route),
        breadcrumbs=breadcrumbs,
        content_html=f'<div class="directory-grid">{"".join(cards)}</div>',
        page_type="family",
        theme_class=family_theme,
    )


def render_platform(route: str, nodes: list[dict[str, Any]]) -> str:
    language, _ = route.split("/", 1)
    first = nodes[0]
    family = family_info(family_key(first))
    platform = platform_label(first)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        by_category[category_route(node)].append(node)

    cards: list[str] = []
    for category, category_nodes in sorted(by_category.items()):
        topic = topic_name(category_nodes[0])
        cards.append(
            f'<article class="directory-card"><span class="pill">{len(category_nodes)} herramientas</span>'
            f'<h2><a href="{html.escape(site_path(category), quote=True)}">{html.escape(topic)}</a></h2>'
            f'<p>Calculadoras y recursos de {html.escape(topic.lower())} para {html.escape(platform)}.</p>'
            f'<a class="open-link" href="{html.escape(site_path(category), quote=True)}">Explorar {html.escape(topic.lower())} →</a></article>'
        )

    breadcrumbs = catalog_breadcrumbs([
        ("Inicio", site_path()),
        (family["label"], site_path(family_route(first))),
        (platform, None),
    ])
    description = PLATFORM_DESCRIPTIONS.get(
        platform_key(first),
        f"Calculadoras y utilidades gratuitas para {platform}.",
    )
    platform_title = (
        "Herramientas para negocios y autónomos"
        if platform_key(first) == "negocios-y-autonomos"
        else "Herramientas de empleo y salarios"
        if platform_key(first) == "empleo-y-salarios"
        else f"Herramientas de {platform}"
    )
    return render_catalog_shell(
        language=language,
        title=platform_title,
        description=description,
        canonical=absolute_url(route),
        breadcrumbs=breadcrumbs,
        content_html=f'<div class="directory-grid">{"".join(cards)}</div>',
        page_type="platform",
        theme_class=platform_theme(first),
    )


def render_category(route: str, nodes: list[dict[str, Any]]) -> str:
    language = route.split("/", 1)[0]
    first = nodes[0]
    family = family_info(family_key(first))
    platform = platform_label(first)
    topic = topic_name(first)
    title = category_page_title(first)
    if platform_key(first) == "instagram":
        description = "Mide la interacción, compara el rendimiento y toma mejores decisiones para tu perfil o tus campañas de Instagram."
    elif platform_key(first) == "negocios-y-autonomos":
        description = f"Calculadoras y recursos gratuitos de {topic.lower()} para pequeños negocios, autónomos y profesionales."
    elif platform_key(first) == "empleo-y-salarios":
        description = f"Calculadoras orientativas de {topic.lower()} para personas trabajadoras en España, con metodología y límites explicados."
    else:
        description = f"Calculadoras y utilidades gratuitas de {topic.lower()} para {platform}."

    cards = "".join(
        f'<article class="tool-card platform-{html.escape(platform_key(node), quote=True)}"><span class="pill">{html.escape(platform_label(node))}</span>'
        f'<h3><a href="{html.escape(site_path(node_route(node)), quote=True)}">{html.escape(str(node["meta"]["title"]))}</a></h3>'
        f'<p>{html.escape(str(node["meta"]["description"]))}</p>'
        f'<a class="open-link" href="{html.escape(site_path(node_route(node)), quote=True)}">Abrir herramienta →</a></article>'
        for node in nodes
    )
    breadcrumbs = catalog_breadcrumbs([
        ("Inicio", site_path()),
        (family["label"], site_path(family_route(first))),
        (platform, site_path(platform_route(first))),
        (topic, None),
    ])
    return render_catalog_shell(
        language=language,
        title=title,
        description=description,
        canonical=absolute_url(route),
        breadcrumbs=breadcrumbs,
        content_html=f'<div class="tools-grid">{cards}</div>',
        page_type="category",
        theme_class=platform_theme(first),
    )


def render_all_tools(nodes: list[dict[str, Any]], language: str = "es") -> str:
    language_nodes = [node for node in nodes if node["_language"] == language]
    by_family_platform: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for node in language_nodes:
        by_family_platform[family_key(node)][platform_key(node)].append(node)

    sections: list[str] = []
    for family_key_value, platforms in sorted(by_family_platform.items()):
        family = family_info(family_key_value)
        platform_blocks: list[str] = []
        for platform_key_value, platform_nodes in sorted(platforms.items()):
            first = platform_nodes[0]
            tool_cards = "".join(
                f'<article class="tool-card platform-{html.escape(platform_key(node), quote=True)}"><span class="pill">{html.escape(topic_name(node))}</span>'
                f'<h3><a href="{html.escape(site_path(node_route(node)), quote=True)}">{html.escape(str(node["meta"]["title"]))}</a></h3>'
                f'<p>{html.escape(str(node["meta"]["description"]))}</p></article>'
                for node in sorted(platform_nodes, key=lambda item: str(item["meta"]["title"]))
            )
            platform_blocks.append(
                f'<section class="catalog-section"><div class="catalog-section-head"><h2>{html.escape(platform_label(first))}</h2>'
                f'<a href="{html.escape(site_path(platform_route(first)), quote=True)}">Ver sección →</a></div><div class="tools-grid">{tool_cards}</div></section>'
            )
        sections.append(
            f'<section aria-labelledby="family-{html.escape(family_key_value, quote=True)}"><span class="pill">{html.escape(family["label"])}</span>{"".join(platform_blocks)}</section>'
        )

    breadcrumbs = catalog_breadcrumbs([
        ("Inicio", site_path()),
        ("Todas las herramientas", None),
    ])
    return render_catalog_shell(
        language=language,
        title="Todas las herramientas",
        description=f"Explora las {len(language_nodes)} calculadoras y utilidades disponibles en Clicivo, organizadas por categoría y plataforma.",
        canonical=absolute_url(all_tools_route(language)),
        breadcrumbs=breadcrumbs,
        content_html="".join(sections),
        page_type="all_tools",
    )

def legal_footer() -> str:
    return (
        f'<a href="{site_path("aviso-legal")}">Aviso legal</a> · '
        f'<a href="{site_path("privacidad")}">Privacidad</a> · '
        f'<a href="{site_path("politica-cookies")}">Cookies</a>'
    )


def render_legal_page(slug: str, title: str, body_html: str, description: str) -> str:
    canonical = absolute_url(slug)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | {html.escape(SITE_NAME)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="canonical" href="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
{analytics_snippet("legal")}
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f8fafc;color:#0f172a;font-family:'Plus Jakarta Sans',system-ui,sans-serif;line-height:1.7}}.wrap{{width:min(860px,calc(100% - 40px));margin:0 auto}}header{{background:#fff;border-bottom:1px solid #e2e8f0;padding:20px 0}}header a{{color:#0f172a;text-decoration:none;font-weight:800}}main{{padding:54px 0 80px}}.crumbs{{font-size:.9rem;color:#64748b;margin-bottom:20px}}.crumbs a{{color:#4f46e5;text-decoration:none}}article{{background:#fff;border:1px solid #e2e8f0;border-radius:22px;padding:clamp(24px,5vw,46px);box-shadow:0 10px 30px rgba(15,23,42,.04)}}h1{{font-size:clamp(2rem,5vw,3.2rem);letter-spacing:-.045em;line-height:1.1;margin:0 0 24px}}h2{{font-size:1.35rem;margin:30px 0 10px}}h3{{font-size:1.05rem;margin:22px 0 8px}}p,li{{color:#475569}}ul{{padding-left:22px}}a{{color:#4f46e5}}table{{width:100%;border-collapse:collapse;margin:18px 0;font-size:.92rem}}th,td{{border:1px solid #e2e8f0;padding:10px;text-align:left;vertical-align:top}}th{{background:#f8fafc}}.notice{{background:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;padding:15px}}footer{{background:#fff;border-top:1px solid #e2e8f0;padding:28px 0;color:#64748b;font-size:.88rem}}footer a{{color:#475569}}
</style>
</head>
<body><header><div class="wrap"><a href="{site_path()}">◆ {html.escape(SITE_NAME)}</a></div></header>
<main class="wrap"><div class="crumbs"><a href="{site_path()}">Inicio</a> › {html.escape(title)}</div><article><h1>{html.escape(title)}</h1>{body_html}</article></main>
<footer><div class="wrap">© {date.today().year} {html.escape(SITE_NAME)} · {legal_footer()}</div></footer></body></html>"""


def legal_pages() -> dict[str, tuple[str, str, str]]:
    owner = html.escape(LEGAL_OWNER)
    trade = html.escape(LEGAL_TRADE_NAME)
    nif = html.escape(LEGAL_NIF)
    address = html.escape(LEGAL_ADDRESS)
    email = html.escape(LEGAL_EMAIL)
    email_link = f'<a href="mailto:{html.escape(LEGAL_EMAIL, quote=True)}">{email}</a>'

    notice = f"""
<p>En cumplimiento de la normativa aplicable a los servicios de la sociedad de la información, se facilitan los datos de identificación de la persona responsable de este sitio web.</p>
<h2>1. Titular del sitio</h2>
<ul><li><strong>Titular:</strong> {owner}, persona trabajadora autónoma.</li><li><strong>Nombre comercial:</strong> {trade}.</li><li><strong>NIF:</strong> {nif}.</li><li><strong>Domicilio profesional:</strong> {address}.</li><li><strong>Correo electrónico:</strong> {email_link}.</li><li><strong>Dominio:</strong> clicivo.com.</li></ul>
<h2>2. Objeto</h2><p>Clicivo ofrece calculadoras, herramientas y contenidos informativos de uso gratuito. Los resultados son orientativos y dependen de los datos introducidos por cada usuario.</p>
<h2>3. Condiciones de uso</h2><p>La persona usuaria se compromete a utilizar el sitio de forma lícita y a no realizar acciones que dañen, sobrecarguen o alteren su funcionamiento. No se garantiza que los resultados sean adecuados para decisiones fiscales, jurídicas, financieras o profesionales sin una comprobación adicional.</p>
<h2>4. Propiedad intelectual</h2><p>Salvo indicación contraria, el diseño, código, textos, estructura y elementos propios de Clicivo pertenecen a su titular o se utilizan con licencia. No se autoriza su reproducción o explotación comercial sin permiso, salvo los usos permitidos legalmente.</p>
<h2>5. Enlaces externos y afiliación</h2><p>Clicivo puede incluir enlaces a servicios de terceros. El titular no controla sus contenidos, disponibilidad, precios ni políticas. Algunos enlaces pueden ser de afiliación: se identificarán de forma clara junto al propio bloque comercial. Si una persona contrata o compra mediante uno de esos enlaces, Clicivo puede recibir una comisión sin que ello incremente el precio para la persona usuaria.</p>
<h2>6. Responsabilidad</h2><p>Se procura mantener la información actualizada y el servicio disponible, pero pueden existir errores, interrupciones o cambios de terceros. El uso de los resultados es responsabilidad de quien los consulta.</p>
<h2>7. Legislación aplicable</h2><p>Este sitio se rige por la legislación española. Para cualquier consulta puede utilizarse el correo indicado anteriormente.</p>
<p class="notice"><strong>Última actualización:</strong> 12 de julio de 2026.</p>"""

    privacy = f"""
<p>Esta política explica cómo se tratan los datos personales cuando utilizas Clicivo.</p>
<h2>1. Responsable del tratamiento</h2><ul><li><strong>Responsable:</strong> {owner}, bajo el nombre comercial {trade}.</li><li><strong>NIF:</strong> {nif}.</li><li><strong>Dirección:</strong> {address}.</li><li><strong>Contacto:</strong> {email_link}.</li></ul>
<h2>2. Datos tratados</h2><p>Clicivo no exige registro para utilizar las calculadoras. Los valores que introduces se procesan en tu navegador y no se envían deliberadamente a nuestros servidores ni a Google Analytics.</p><p>Podemos tratar:</p><ul><li>Datos técnicos y de navegación cuando aceptas cookies analíticas, como páginas visitadas, tipo de dispositivo e interacciones con las herramientas.</li><li>Datos que facilites voluntariamente al escribir al correo de contacto.</li></ul>
<h2>3. Finalidades y bases jurídicas</h2><ul><li><strong>Analítica:</strong> conocer el uso de la web y mejorar sus herramientas, únicamente con tu consentimiento.</li><li><strong>Atención de consultas:</strong> responder a comunicaciones, sobre la base de tu solicitud y, cuando proceda, del interés legítimo en atenderla.</li><li><strong>Seguridad:</strong> prevenir abusos y mantener la integridad del sitio, sobre la base del interés legítimo y obligaciones legales.</li></ul>
<h2>4. Destinatarios y proveedores</h2><p>Cuando aceptas analítica, se utiliza Google Analytics, prestado en Europa por Google Ireland Limited. Google puede tratar datos conforme a sus condiciones y políticas. La infraestructura web se publica mediante GitHub Pages y el dominio se gestiona mediante proveedores externos.</p>
<h2>5. Transferencias internacionales</h2><p>Algunos proveedores tecnológicos pueden tratar datos fuera del Espacio Económico Europeo. Cuando sea aplicable, deberán utilizar mecanismos reconocidos por la normativa, como decisiones de adecuación o cláusulas contractuales tipo.</p>
<h2>6. Conservación</h2><p>Los datos se conservarán durante el tiempo necesario para cada finalidad y para cumplir obligaciones legales. Los datos de Analytics se mantienen durante el periodo configurado en la propiedad y las cookies durante su vigencia o hasta que las elimines.</p>
<h2>7. Derechos</h2><p>Puedes solicitar acceso, rectificación, supresión, oposición, limitación o portabilidad escribiendo a {email_link}. También puedes retirar tu consentimiento para Analytics mediante el botón «Configurar cookies».</p><p>Si consideras que el tratamiento no se ajusta a la normativa, puedes presentar una reclamación ante la Agencia Española de Protección de Datos.</p>
<h2>8. Menores</h2><p>Clicivo no está dirigido específicamente a menores ni solicita conscientemente sus datos personales.</p>
<h2>9. Cambios</h2><p>Esta política puede actualizarse para reflejar cambios legales, técnicos o de los servicios utilizados.</p>
<p class="notice"><strong>Última actualización:</strong> 12 de julio de 2026.</p>"""

    cookies = f"""
<p>Clicivo utiliza almacenamiento estrictamente necesario para recordar tu elección y, solo si aceptas, cookies de Google Analytics para medir el uso de la web.</p>
<h2>1. ¿Qué son las cookies?</h2><p>Son pequeños archivos o identificadores que un sitio puede guardar en el dispositivo para recordar información o medir la navegación.</p>
<h2>2. Cookies utilizadas</h2>
<table><thead><tr><th>Nombre</th><th>Proveedor</th><th>Finalidad</th><th>Duración orientativa</th></tr></thead><tbody>
<tr><td>clicivo_cookie_consent</td><td>Clicivo</td><td>Guarda en el almacenamiento local si has aceptado o rechazado la analítica.</td><td>Hasta que borres los datos del navegador o cambies tu elección.</td></tr>
<tr><td>_ga</td><td>Google Analytics</td><td>Distinguir usuarios y elaborar estadísticas agregadas.</td><td>Hasta 2 años.</td></tr>
<tr><td>_ga_*</td><td>Google Analytics</td><td>Mantener el estado de la sesión y medición de la propiedad.</td><td>Hasta 2 años.</td></tr>
</tbody></table>
<p>Las denominaciones o duraciones pueden cambiar si Google modifica su servicio. Puedes consultar información adicional en la documentación y política de privacidad de Google.</p>
<h2>3. Consentimiento</h2><p>Las cookies analíticas no se cargan antes de que pulses «Aceptar analítica». Rechazar es tan sencillo como aceptar y no impide utilizar las calculadoras.</p>
<h2>4. Cambiar o retirar tu elección</h2><p>Utiliza el botón «Configurar cookies», visible en la parte inferior de la web. También puedes borrar cookies y almacenamiento local desde la configuración de tu navegador.</p>
<h2>5. Responsable</h2><p>El responsable es {owner}, bajo el nombre comercial {trade}. Contacto: {email_link}.</p>
<p class="notice"><strong>Última actualización:</strong> 12 de julio de 2026.</p>"""

    return {
        "aviso-legal": ("Aviso legal", notice, "Información legal y condiciones de uso de Clicivo."),
        "privacidad": ("Política de privacidad", privacy, "Información sobre el tratamiento de datos personales en Clicivo."),
        "politica-cookies": ("Política de cookies", cookies, "Información sobre las cookies y la analítica utilizadas por Clicivo."),
    }

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
    platforms: dict[str, list[dict[str, Any]]] = defaultdict(list)
    families: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for node in nodes:
        route = node_route(node)
        output_path = OUTPUT_DIR / route / "index.html"
        write_text(output_path, render_tool(node, template))
        generate_og_image(
            str(node["meta"]["title"]), OUTPUT_DIR / "assets" / "og" / f"{node['id']}.jpg"
        )
        sitemap_entries.append((absolute_url(route), str(node.get("actualizado", "")) or None))
        categories[category_route(node)].append(node)
        platforms[platform_route(node)].append(node)
        families[family_route(node)].append(node)

    for route, category_nodes in sorted(categories.items()):
        write_text(OUTPUT_DIR / route / "index.html", render_category(route, category_nodes))
        sitemap_entries.append((absolute_url(route), None))

    for route, platform_nodes in sorted(platforms.items()):
        write_text(OUTPUT_DIR / route / "index.html", render_platform(route, platform_nodes))
        sitemap_entries.append((absolute_url(route), None))

    for route, family_nodes in sorted(families.items()):
        write_text(OUTPUT_DIR / route / "index.html", render_family(route, family_nodes))
        sitemap_entries.append((absolute_url(route), None))

    languages = sorted({str(node["_language"]) for node in nodes}) or [str(CONFIG.get("default_language", "es"))]
    for language in languages:
        tools_route = all_tools_route(language)
        write_text(OUTPUT_DIR / tools_route / "index.html", render_all_tools(nodes, language))
        sitemap_entries.append((absolute_url(tools_route), None))

    for slug, (title, body_html, description) in legal_pages().items():
        write_text(OUTPUT_DIR / slug / "index.html", render_legal_page(slug, title, body_html, description))
        sitemap_entries.append((absolute_url(slug), None))

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    seen_urls: set[str] = set()
    for url, last_modified in sitemap_entries:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        sitemap_lines.append("  <url>")
        sitemap_lines.append(f"    <loc>{xml_escape(url)}</loc>")
        if last_modified:
            sitemap_lines.append(f"    <lastmod>{xml_escape(last_modified)}</lastmod>")
        sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>")
    write_text(OUTPUT_DIR / "sitemap.xml", "\n".join(sitemap_lines) + "\n")

    write_text(
        OUTPUT_DIR / "robots.txt",
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_ORIGIN}{BASE_PATH}/sitemap.xml\n",
    )
    write_text(OUTPUT_DIR / "CNAME", CUSTOM_DOMAIN + "\n")
    write_text(OUTPUT_DIR / ".nojekyll", "")
    write_text(
        OUTPUT_DIR / "404.html",
        f"<!doctype html><html lang=\"es\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Página no encontrada | {html.escape(SITE_NAME)}</title><body style=\"font-family:system-ui;text-align:center;padding:10vh 20px\"><h1>404</h1><p>La página que buscas no existe.</p><p><a href=\"{site_path()}\">Volver a {html.escape(SITE_NAME)}</a></p></body></html>",
    )

    print(
        f"🚀 Clicivo compilado: {len(nodes)} herramienta(s), "
        f"{len(categories)} categoría(s), {len(platforms)} plataforma(s), "
        f"{len(families)} familia(s) y {len(seen_urls)} URL(s) en sitemap."
    )


if __name__ == "__main__":
    compile_site()
