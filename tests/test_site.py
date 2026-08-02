from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TOOLS = json.loads((ROOT / "content" / "tools.json").read_text(encoding="utf-8"))
HTML_FILES = sorted(PUBLIC.rglob("index.html"))
LEGACY_REDIRECT_ROUTES = {
    "/es/herramientas/": "/",
    "/es/youtube/monetizacion/rpm-youtube/": "/es/youtube/monetizacion/ingresos-youtube/",
    "/es/finanzas-personales/": "/es/finanzas/",
    "/es/negocios-y-autonomos/": "/es/negocios/",
    "/politica-cookies/": "/cookies/",
}


def route_for_file(path: Path) -> str:
    rel = path.relative_to(PUBLIC)
    return "/" if rel.as_posix() == "index.html" else "/" + rel.parent.as_posix().strip("/") + "/"


INDEXABLE_HTML_FILES = [path for path in HTML_FILES if route_for_file(path) not in LEGACY_REDIRECT_ROUTES]


def local_target(url: str) -> Path | None:
    if not url or url.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc and parsed.netloc != "clicivo.com":
        return None
    path = parsed.path
    if path == "/":
        return PUBLIC / "index.html"
    if path.endswith("/"):
        return PUBLIC / path.strip("/") / "index.html"
    return PUBLIC / path.lstrip("/")


def test_expected_tool_count_and_unique_urls():
    assert len(TOOLS) == 42
    assert len({tool["id"] for tool in TOOLS}) == 42
    assert len({tool["path"] for tool in TOOLS}) == 42
    assert sum(bool(tool.get("new")) for tool in TOOLS) == 25


def test_every_tool_route_exists_and_has_form():
    for tool in TOOLS:
        path = PUBLIC / tool["path"].strip("/") / "index.html"
        assert path.exists(), tool["path"]
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        form = soup.select_one(f'form[data-tool="{tool["id"]}"]')
        assert form is not None, tool["id"]
        assert soup.select_one("#result-body") is not None
        assert soup.select_one("h1")


def test_all_pages_have_core_seo_tags():
    canonicals = set()
    for path in INDEXABLE_HTML_FILES:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        assert soup.title and soup.title.get_text(strip=True)
        desc = soup.select_one('meta[name="description"]')
        canonical = soup.select_one('link[rel="canonical"]')
        assert desc and 50 <= len(desc.get("content", "")) <= 160, path
        assert canonical and canonical.get("href", "").startswith("https://clicivo.com/"), path
        assert canonical["href"] not in canonicals, canonical["href"]
        canonicals.add(canonical["href"])
        assert soup.select_one('meta[property="og:title"]')
        assert soup.select_one('meta[property="og:image"]')
        assert soup.select_one('script[type="application/ld+json"]')


def test_internal_links_are_valid():
    broken = []
    for page in HTML_FILES:
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        for tag, attr in [("a", "href"), ("link", "href"), ("script", "src"), ("img", "src")]:
            for node in soup.find_all(tag):
                target = local_target(node.get(attr, ""))
                if target is not None and not target.exists():
                    broken.append((str(page.relative_to(PUBLIC)), node.get(attr), str(target.relative_to(PUBLIC))))
    assert not broken, broken[:20]


def test_sitemap_matches_indexable_pages():
    tree = ET.parse(PUBLIC / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = {node.text for node in tree.findall("s:url/s:loc", ns)}
    expected = {"https://clicivo.com" + route_for_file(path) for path in INDEXABLE_HTML_FILES}
    assert locs == expected
    assert not any("finanzas-personales" in loc or "negocios-y-autonomos" in loc or "politica-cookies" in loc for loc in locs)


def test_brand_assets_and_operational_files_exist():
    expected = [
        "assets/logo-mark.svg", "assets/logo-clicivo.svg", "assets/favicon.svg",
        "assets/favicon-48.png", "assets/apple-touch-icon.png", "assets/og-clicivo.png",
        "assets/styles.css", "assets/site.js", "assets/advanced-tools.js", "robots.txt", "manifest.webmanifest", "CNAME", ".nojekyll",
    ]
    for item in expected:
        assert (PUBLIC / item).exists(), item
    assert (PUBLIC / "CNAME").read_text().strip() == "clicivo.com"
    assert "Sitemap: https://clicivo.com/sitemap.xml" in (PUBLIC / "robots.txt").read_text()


def test_forbidden_personal_name_removed_everywhere():
    terms = ["".join(map(chr, [117, 110, 97, 105])), "".join(map(chr, [98, 117, 114, 103, 117, 101, 116, 101]))]
    forbidden = re.compile("|".join(terms), re.I)
    hits = []
    for path in ROOT.rglob("*"):
        # .git contiene metadatos locales del repositorio (URL remota, FETCH_HEAD, etc.)
        # y no forma parte de los archivos publicados en Clicivo.
        if ".git" in path.parts:
            continue
        if path.is_file() and path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".zip", ".pyc"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if forbidden.search(text):
                hits.append(str(path.relative_to(ROOT)))
    assert not hits, hits


def test_new_priority_routes_exist():
    expansion_routes = {
        "/es/pdf/unir-dividir/unir-pdf/",
        "/es/pdf/unir-dividir/dividir-pdf/",
        "/es/pdf/organizar/organizar-paginas-pdf/",
        "/es/pdf/convertir/imagenes-a-pdf/",
        "/es/pdf/convertir/pdf-a-jpg/",
        "/es/imagenes/optimizar/comprimir-imagenes/",
        "/es/imagenes/redimensionar/cambiar-tamano-imagen/",
        "/es/imagenes/convertir/convertir-jpg-png-webp/",
        "/es/imagenes/editar/recortar-imagen/",
        "/es/imagenes/privacidad/eliminar-metadatos-exif/",
        "/es/productividad/texto/contador-palabras-caracteres/",
        "/es/productividad/texto/conversor-mayusculas-minusculas/",
        "/es/productividad/texto/comparar-textos/",
        "/es/productividad/qr/generador-codigo-qr/",
        "/es/productividad/qr/generador-qr-wifi/",
    }
    all_routes = {t["path"] for t in TOOLS}
    assert expansion_routes <= all_routes
    assert expansion_routes <= {t["path"] for t in TOOLS if t.get("new")}


def test_new_category_routes_exist():
    for route in ["es/pdf", "es/imagenes", "es/productividad"]:
        assert (PUBLIC / route / "index.html").exists(), route


def test_tool_pages_have_substantial_unique_content():
    titles = set()
    for tool in TOOLS:
        path = PUBLIC / tool["path"].strip("/") / "index.html"
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        text = " ".join(soup.get_text(" ", strip=True).split())
        assert len(text) > 1700, (tool["id"], len(text))
        title = soup.select_one("h1").get_text(" ", strip=True)
        assert title not in titles
        titles.add(title)
        assert len(soup.select(".faq details")) >= 3
        assert len(soup.select(".related-link")) >= 3


def test_legacy_routes_redirect_without_indexing():
    for route, target in LEGACY_REDIRECT_ROUTES.items():
        path = PUBLIC / route.strip("/") / "index.html"
        assert path.exists(), route
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        robots = soup.select_one('meta[name="robots"]')
        canonical = soup.select_one('link[rel="canonical"]')
        assert robots and "noindex" in robots.get("content", "")
        assert canonical and canonical["href"] == "https://clicivo.com" + target
        assert soup.select_one('meta[http-equiv="refresh"]')


def test_no_internal_seo_notes_or_keyword_lists_are_public():
    forbidden = ["Prioridad SEO:", "Consultas relacionadas:"]
    hits = []
    for path in INDEXABLE_HTML_FILES:
        text = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser").get_text(" ", strip=True)
        for phrase in forbidden:
            if phrase in text:
                hits.append((str(path.relative_to(PUBLIC)), phrase))
    assert not hits, hits[:20]


def test_trust_and_monetization_pages_exist():
    routes = [
        "/sobre-clicivo/", "/metodologia/", "/condiciones-de-uso/",
        "/publicidad-y-afiliacion/", "/privacidad/", "/cookies/",
        "/aviso-legal/", "/contacto/",
    ]
    for route in routes:
        path = PUBLIC / route.strip("/") / "index.html"
        assert path.exists(), route
        text = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser").get_text(" ", strip=True)
        assert len(text) > 700, (route, len(text))


def test_adsense_cmp_and_consent_mode_are_prepared():
    home = (PUBLIC / "index.html").read_text(encoding="utf-8")
    assert 'google-adsense-account" content="ca-pub-2391387240778857"' in home
    assert "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2391387240778857" in home
    assert "gtag('consent','default'" in home
    assert "ad_storage:'denied'" in home
    assert "cookie-banner" not in home
    assert (PUBLIC / "ads.txt").read_text(encoding="utf-8").strip() == "google.com, pub-2391387240778857, DIRECT, f08c47fec0942fa0"


def test_priority_tool_forms_contain_new_fields():
    expected_fields = {
        "tiktok-income": {"views", "rpmLow", "rpm", "rpmHigh", "months", "targetIncome"},
        "youtube-income": {"views", "rpmLow", "rpm", "rpmHigh", "months", "targetIncome"},
        "youtube-rpm-revenue": {"revenue", "views", "targetViews"},
        "severance": {"monthly", "salaryDays", "vacationDays", "extraPay", "other", "includeCompensation", "compensation", "deductions"},
    }
    for tool_id, names in expected_fields.items():
        tool = next(t for t in TOOLS if t["id"] == tool_id)
        soup = BeautifulSoup((PUBLIC / tool["path"].strip("/") / "index.html").read_text(encoding="utf-8"), "html.parser")
        found = {el.get("name") for el in soup.select("form input[name], form select[name], form textarea[name]")}
        assert names <= found, (tool_id, names - found)


def test_result_actions_and_quality_signals_present():
    report_categories = {"Redes sociales", "Finanzas", "Negocios", "Empleo"}
    for tool in TOOLS:
        soup = BeautifulSoup((PUBLIC / tool["path"].strip("/") / "index.html").read_text(encoding="utf-8"), "html.parser")
        assert soup.select_one(".js-copy-result")
        if tool["category"] in report_categories:
            assert soup.select_one(".js-download-pdf"), tool["id"]
            assert soup.select_one(".js-copy-client"), tool["id"]
            assert "jspdf" in str(soup).lower(), tool["id"]
        else:
            assert soup.select_one(".js-print-result"), tool["id"]
        assert soup.select_one(".quality-card")
        assert soup.select_one(".hero-outcome-card")
        assert soup.select_one(".benefit-ribbon")
        assert "Última revisión" in soup.get_text(" ", strip=True)


def test_every_tool_has_persuasive_unique_copy_fields():
    hooks=set()
    benefits=set()
    for tool in TOOLS:
        assert 25 <= len(tool.get("hook", "")) <= 120, tool["id"]
        assert 25 <= len(tool.get("benefit_heading", "")) <= 100, tool["id"]
        assert len(tool.get("benefit_copy", "")) >= 70, tool["id"]
        assert tool["hook"] not in hooks, tool["id"]
        assert tool["benefit_heading"] not in benefits, tool["id"]
        hooks.add(tool["hook"])
        benefits.add(tool["benefit_heading"])


def test_homepage_uses_saas_value_proposition():
    soup=BeautifulSoup((PUBLIC / "index.html").read_text(encoding="utf-8"), "html.parser")
    text=soup.get_text(" ", strip=True)
    assert "Calcula, compara y presenta resultados" in text
    assert soup.select_one(".saas-dashboard-preview")
    assert "Resultados que puedes reutilizar" in text
