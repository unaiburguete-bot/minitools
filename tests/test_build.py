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
        "es/finanzas/index.html",
        "es/finanzas-personales/index.html",
        "es/finanzas/hipotecas/index.html",
        "es/finanzas/hipotecas/calculadora-hipoteca/index.html",
        "es/finanzas/ahorro-inversion/calculadora-interes-compuesto/index.html",
        "es/finanzas/prestamos/calculadora-prestamo-personal/index.html",
        "es/negocios/index.html",
        "es/negocios-y-autonomos/index.html",
        "es/negocios/precios/index.html",
        "es/negocios/precios/calculadora-margen-beneficio/index.html",
        "es/negocios/rentabilidad/simulador-punto-equilibrio/index.html",
        "es/negocios/autonomos/calculadora-tarifa-hora/index.html",
        "es/empleo/index.html",
        "es/empleo-y-salarios/index.html",
        "es/empleo/salarios/index.html",
        "es/empleo/salarios/calculadora-sueldo-neto/index.html",
        "es/empleo/liquidacion-laboral/calculadora-finiquito/index.html",
        "es/empleo/extincion-contrato/calculadora-indemnizacion-despido/index.html",
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
        "https://clicivo.com/es/finanzas/",
        "https://clicivo.com/es/finanzas-personales/",
        "https://clicivo.com/es/finanzas/hipotecas/",
        "https://clicivo.com/es/finanzas/hipotecas/calculadora-hipoteca/",
        "https://clicivo.com/es/finanzas/ahorro-inversion/calculadora-interes-compuesto/",
        "https://clicivo.com/es/finanzas/prestamos/calculadora-prestamo-personal/",
        "https://clicivo.com/es/negocios/",
        "https://clicivo.com/es/negocios-y-autonomos/",
        "https://clicivo.com/es/negocios/precios/",
        "https://clicivo.com/es/negocios/precios/calculadora-margen-beneficio/",
        "https://clicivo.com/es/negocios/rentabilidad/simulador-punto-equilibrio/",
        "https://clicivo.com/es/negocios/autonomos/calculadora-tarifa-hora/",
        "https://clicivo.com/es/empleo/",
        "https://clicivo.com/es/empleo-y-salarios/",
        "https://clicivo.com/es/empleo/salarios/",
        "https://clicivo.com/es/empleo/salarios/calculadora-sueldo-neto/",
        "https://clicivo.com/es/empleo/liquidacion-laboral/calculadora-finiquito/",
        "https://clicivo.com/es/empleo/extincion-contrato/calculadora-indemnizacion-despido/",
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
    assert len(tool_pages) == 18
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


def test_finance_family_and_theme_are_generated():
    home = (PUBLIC / "index.html").read_text(encoding="utf-8")
    family = (PUBLIC / "es/finanzas/index.html").read_text(encoding="utf-8")
    platform = (PUBLIC / "es/finanzas-personales/index.html").read_text(encoding="utf-8")
    mortgage = (
        PUBLIC / "es/finanzas/hipotecas/calculadora-hipoteca/index.html"
    ).read_text(encoding="utf-8")

    assert "Herramientas de finanzas" in home
    assert 'href="/es/finanzas/"' in home
    assert "Finanzas personales" in family
    assert "Hipotecas" in platform
    assert '<body class="theme-finanzas-personales"' in mortgage
    assert "CLICIVO FINANCE THEME" in mortgage


def test_finance_calculators_have_multiple_results_and_power_operation():
    mortgage = (
        PUBLIC / "es/finanzas/hipotecas/calculadora-hipoteca/index.html"
    ).read_text(encoding="utf-8")
    compound = (
        PUBLIC / "es/finanzas/ahorro-inversion/calculadora-interes-compuesto/index.html"
    ).read_text(encoding="utf-8")
    loan = (
        PUBLIC / "es/finanzas/prestamos/calculadora-prestamo-personal/index.html"
    ).read_text(encoding="utf-8")

    assert "Math.pow" in mortgage
    assert "Cuota mensual estimada" in mortgage
    assert "Intereses totales" in mortgage
    assert "Capital final estimado" in compound
    assert "Rendimiento acumulado" in compound
    assert "Comisión de apertura" in loan
    assert "Total a devolver" in loan


def test_navigation_includes_finance():
    pages = [
        PUBLIC / "index.html",
        PUBLIC / "es/redes-sociales/index.html",
        PUBLIC / "es/finanzas/hipotecas/calculadora-hipoteca/index.html",
    ]
    for page in pages:
        html = page.read_text(encoding="utf-8")
        assert 'href="/es/finanzas/"' in html
        assert ">Finanzas</a>" in html


def test_business_family_and_theme_are_generated():
    home = (PUBLIC / "index.html").read_text(encoding="utf-8")
    family = (PUBLIC / "es/negocios/index.html").read_text(encoding="utf-8")
    platform = (PUBLIC / "es/negocios-y-autonomos/index.html").read_text(encoding="utf-8")
    margin = (
        PUBLIC / "es/negocios/precios/calculadora-margen-beneficio/index.html"
    ).read_text(encoding="utf-8")

    assert "Herramientas para negocios y autónomos" in home
    assert 'href="/es/negocios/"' in home
    assert "Negocios y autónomos" in family
    assert "Precios" in platform
    assert '<body class="theme-negocios-y-autonomos"' in margin
    assert "CLICIVO BUSINESS THEME" in margin


def test_business_calculators_have_multiple_results_and_validation():
    margin = (
        PUBLIC / "es/negocios/precios/calculadora-margen-beneficio/index.html"
    ).read_text(encoding="utf-8")
    break_even = (
        PUBLIC / "es/negocios/rentabilidad/simulador-punto-equilibrio/index.html"
    ).read_text(encoding="utf-8")
    hourly = (
        PUBLIC / "es/negocios/autonomos/calculadora-tarifa-hora/index.html"
    ).read_text(encoding="utf-8")

    assert "Margen sobre ventas" in margin
    assert "Markup sobre coste" in margin
    assert "Precio para el margen objetivo" in margin
    assert "El precio de venta debe ser mayor" in break_even
    assert "Facturación de equilibrio" in break_even
    assert "Margen de seguridad" in break_even
    assert "Tarifa mínima por hora" in hourly
    assert "Horas facturables al año" in hourly
    assert "Proyecto de 20 horas" in hourly


def test_navigation_includes_business():
    pages = [
        PUBLIC / "index.html",
        PUBLIC / "es/finanzas/index.html",
        PUBLIC / "es/negocios/precios/calculadora-margen-beneficio/index.html",
    ]
    for page in pages:
        page_html = page.read_text(encoding="utf-8")
        assert 'href="/es/negocios/"' in page_html
        assert ">Negocios</a>" in page_html



def test_employment_family_and_theme_are_generated():
    home = (PUBLIC / "index.html").read_text(encoding="utf-8")
    family = (PUBLIC / "es/empleo/index.html").read_text(encoding="utf-8")
    platform = (PUBLIC / "es/empleo-y-salarios/index.html").read_text(encoding="utf-8")
    salary = (
        PUBLIC / "es/empleo/salarios/calculadora-sueldo-neto/index.html"
    ).read_text(encoding="utf-8")

    assert "Herramientas de empleo y salarios" in home
    assert 'href="/es/empleo/"' in home
    assert "Empleo y salarios" in family
    assert "Salarios" in platform
    assert '<body class="theme-empleo-y-salarios"' in salary
    assert "CLICIVO EMPLOYMENT THEME" in salary


def test_employment_calculators_have_official_2026_parameters_and_limits():
    salary = (
        PUBLIC / "es/empleo/salarios/calculadora-sueldo-neto/index.html"
    ).read_text(encoding="utf-8")
    settlement = (
        PUBLIC / "es/empleo/liquidacion-laboral/calculadora-finiquito/index.html"
    ).read_text(encoding="utf-8")
    dismissal = (
        PUBLIC / "es/empleo/extincion-contrato/calculadora-indemnizacion-despido/index.html"
    ).read_text(encoding="utf-8")

    assert "5.101,20" in salary
    assert "Contrato indefinido: 1,55 %" in salary
    assert "Contrato temporal: 1,60 %" in salary
    assert "Math.min" in salary
    assert "Math.max" in salary
    assert "Liquidación bruta estimada" in settlement
    assert "documento de liquidación" in settlement
    assert "20 días/año" in dismissal
    assert "33 días/año" in dismissal
    assert "12 de febrero de 2012" in dismissal


def test_navigation_includes_employment():
    pages = [
        PUBLIC / "index.html",
        PUBLIC / "es/finanzas/index.html",
        PUBLIC / "es/empleo/salarios/calculadora-sueldo-neto/index.html",
    ]
    for page in pages:
        page_html = page.read_text(encoding="utf-8")
        assert 'href="/es/empleo/"' in page_html
        assert ">Empleo</a>" in page_html


def test_select_inputs_are_rendered_for_employment_tools():
    salary = (
        PUBLIC / "es/empleo/salarios/calculadora-sueldo-neto/index.html"
    ).read_text(encoding="utf-8")
    dismissal = (
        PUBLIC / "es/empleo/extincion-contrato/calculadora-indemnizacion-despido/index.html"
    ).read_text(encoding="utf-8")
    assert '<select id="desempleo_trabajador">' in salary
    assert '<select id="tipo_indemnizacion">' in dismissal
