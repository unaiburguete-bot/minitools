from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"


def test_core_outputs_exist():
    expected = [
        "index.html",
        "sitemap.xml",
        "robots.txt",
        "CNAME",
        ".nojekyll",
        "404.html",
        "es/youtube/monetizacion/index.html",
        "es/youtube/monetizacion/rpm-youtube/index.html",
        "es/instagram/analitica/index.html",
        "es/instagram/analitica/engagement-instagram-seguidores/index.html",
    ]
    for relative in expected:
        assert (PUBLIC / relative).exists(), f"Falta public/{relative}"


def test_domain_and_brand_are_migrated():
    text_files = [
        path
        for path in PUBLIC.rglob("*")
        if path.is_file() and path.suffix in {".html", ".xml", ".txt", ""}
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in text_files)
    assert "https://clicivo.com" in combined
    assert "Minitools Factory" not in combined
    assert "minitools.io" not in combined
    assert "/minitools/" not in combined


def test_cname_and_robots():
    assert (PUBLIC / "CNAME").read_text(encoding="utf-8").strip() == "clicivo.com"
    robots = (PUBLIC / "robots.txt").read_text(encoding="utf-8")
    assert "Sitemap: https://clicivo.com/sitemap.xml" in robots


def test_tool_has_canonical_and_open_graph():
    tool = (PUBLIC / "es/youtube/monetizacion/rpm-youtube/index.html").read_text(
        encoding="utf-8"
    )
    canonical = "https://clicivo.com/es/youtube/monetizacion/rpm-youtube/"
    assert f'<link rel="canonical" href="{canonical}">' in tool
    assert f'<meta property="og:url" content="{canonical}">' in tool
    assert "SoftwareApplication" in tool


def test_sitemap_contains_home_category_and_tool():
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    assert "<loc>https://clicivo.com/</loc>" in sitemap
    assert "<loc>https://clicivo.com/es/youtube/monetizacion/</loc>" in sitemap
    assert (
        "<loc>https://clicivo.com/es/youtube/monetizacion/rpm-youtube/</loc>"
        in sitemap
    )


def test_instagram_has_its_own_visual_theme():
    tool = (
        PUBLIC
        / "es/instagram/analitica/engagement-instagram-seguidores/index.html"
    ).read_text(encoding="utf-8")
    category = (PUBLIC / "es/instagram/analitica/index.html").read_text(
        encoding="utf-8"
    )
    youtube = (
        PUBLIC / "es/youtube/monetizacion/rpm-youtube/index.html"
    ).read_text(encoding="utf-8")

    assert '<body class="theme-instagram"' in tool
    assert '<body class="theme-instagram"' in category
    assert "CLICIVO INSTAGRAM THEME" in tool
    assert '<body class="theme-youtube"' in youtube


def test_sitemap_contains_instagram_tool_and_category():
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    assert "<loc>https://clicivo.com/es/instagram/analitica/</loc>" in sitemap
    assert (
        "<loc>https://clicivo.com/es/instagram/analitica/"
        "engagement-instagram-seguidores/</loc>"
    ) in sitemap
