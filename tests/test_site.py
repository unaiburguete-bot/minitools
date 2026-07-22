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
    assert len(TOOLS) == 28
    assert len({tool["id"] for tool in TOOLS}) == 28
    assert len({tool["path"] for tool in TOOLS}) == 28
    assert sum(bool(tool.get("new")) for tool in TOOLS) == 10


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
    for path in HTML_FILES:
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
    expected = set()
    for path in HTML_FILES:
        rel = path.relative_to(PUBLIC)
        route = "/" if rel.as_posix() == "index.html" else "/" + rel.parent.as_posix().strip("/") + "/"
        expected.add("https://clicivo.com" + route)
    assert locs == expected


def test_brand_assets_and_operational_files_exist():
    expected = [
        "assets/logo-mark.svg", "assets/logo-clicivo.svg", "assets/favicon.svg",
        "assets/favicon-48.png", "assets/apple-touch-icon.png", "assets/og-clicivo.png",
        "assets/styles.css", "assets/site.js", "robots.txt", "manifest.webmanifest", "CNAME", ".nojekyll",
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
        if path.is_file() and path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".zip", ".pyc"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if forbidden.search(text):
                hits.append(str(path.relative_to(ROOT)))
    assert not hits, hits


def test_new_priority_routes_exist():
    routes = {
        "/es/instagram/texto/generador-letras-instagram/",
        "/es/instagram/texto/contador-caracteres-instagram/",
        "/es/instagram/texto/generador-espacios-instagram/",
        "/es/tiktok/analitica/calculadora-engagement-tiktok/",
        "/es/tiktok/monetizacion/calculadora-ingresos-tiktok/",
        "/es/finanzas/ahorro-inversion/calculadora-ahorro-mensual/",
        "/es/finanzas/ahorro-inversion/simulador-fondos-indexados/",
        "/es/finanzas/hipotecas/amortizacion-anticipada-hipoteca/",
        "/es/empleo/vacaciones/calculadora-vacaciones/",
        "/es/empleo/coste-empresa/calculadora-coste-empresa-trabajador/",
    }
    assert routes == {t["path"] for t in TOOLS if t.get("new")}


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
