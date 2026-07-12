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
        "es/herramientas/index.html",
        "es/redes-sociales/index.html",
        "es/youtube/index.html",
        "es/instagram/index.html",
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
    assert "sitemap.xml/" not in robots


def test_tool_has_canonical_and_open_graph():
    tool = (PUBLIC / "es/youtube/monetizacion/rpm-youtube/index.html").read_text(
        encoding="utf-8"
    )
    canonical = "https://clicivo.com/es/youtube/monetizacion/rpm-youtube/"
    assert f'<link rel="canonical" href="{canonical}">' in tool
    assert f'<meta property="og:url" content="{canonical}">' in tool
    assert "SoftwareApplication" in tool


def test_sitemap_contains_new_architecture_and_old_urls():
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    expected = [
        "https://clicivo.com/",
        "https://clicivo.com/es/herramientas/",
        "https://clicivo.com/es/redes-sociales/",
        "https://clicivo.com/es/youtube/",
        "https://clicivo.com/es/instagram/",
        "https://clicivo.com/es/youtube/monetizacion/",
        "https://clicivo.com/es/youtube/monetizacion/rpm-youtube/",
        "https://clicivo.com/es/instagram/analitica/",
        "https://clicivo.com/es/instagram/analitica/engagement-instagram-seguidores/",
    ]
    for url in expected:
        assert f"<loc>{url}</loc>" in sitemap


def test_instagram_has_its_own_visual_theme():
    tool = (
        PUBLIC
        / "es/instagram/analitica/engagement-instagram-seguidores/index.html"
    ).read_text(encoding="utf-8")
    category = (PUBLIC / "es/instagram/analitica/index.html").read_text(
        encoding="utf-8"
    )
    platform = (PUBLIC / "es/instagram/index.html").read_text(encoding="utf-8")
    youtube = (
        PUBLIC / "es/youtube/monetizacion/rpm-youtube/index.html"
    ).read_text(encoding="utf-8")

    assert '<body class="theme-instagram"' in tool
    assert '<body class="theme-instagram"' in category
    assert '<body class="theme-instagram"' in platform
    assert "CLICIVO INSTAGRAM THEME" in tool
    assert '<body class="theme-youtube"' in youtube


def test_home_is_grouped_by_large_categories():
    home = (PUBLIC / "index.html").read_text(encoding="utf-8")
    assert "Explora por categoría" in home
    assert "Herramientas para redes sociales" in home
    assert 'href="/es/redes-sociales/"' in home
    assert 'href="/es/herramientas/"' in home


def test_social_family_groups_youtube_and_instagram():
    family = (PUBLIC / "es/redes-sociales/index.html").read_text(encoding="utf-8")
    assert "Herramientas para redes sociales" in family
    assert 'href="/es/youtube/"' in family
    assert 'href="/es/instagram/"' in family
    assert "6 herramientas" in family
    assert "3 herramientas" in family


def test_all_tools_page_contains_every_tool():
    catalog = (PUBLIC / "es/herramientas/index.html").read_text(encoding="utf-8")
    tool_pages = [
        path
        for path in (PUBLIC / "es").rglob("index.html")
        if "SoftwareApplication" in path.read_text(encoding="utf-8")
    ]
    assert len(tool_pages) == 9
    for path in tool_pages:
        relative = path.parent.relative_to(PUBLIC).as_posix()
        assert f'href="/{relative}/"' in catalog


def test_tool_breadcrumbs_include_family_platform_and_topic():
    youtube = (PUBLIC / "es/youtube/monetizacion/rpm-youtube/index.html").read_text(
        encoding="utf-8"
    )
    assert 'href="/es/redes-sociales/">Redes sociales</a>' in youtube
    assert 'href="/es/youtube/">YouTube</a>' in youtube
    assert 'href="/es/youtube/monetizacion/">Monetización</a>' in youtube
