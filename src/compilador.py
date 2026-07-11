import os
import yaml
import markdown
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

DIR_CONTENIDO = "./content"
TEMPLATE_PATH = "./template.html"
DIR_SALIDA = "./public"

def cargar_entidades():
    nodos = []
    if not os.path.exists(DIR_CONTENIDO):
        os.makedirs(DIR_CONTENIDO, exist_ok=True)
        return nodos
    
    for root, _, archivos in os.walk(DIR_CONTENIDO):
        for archivo in archivos:
            if archivo.endswith('.md'):
                ruta_completa = os.path.join(root, archivo)
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    try:
                        partes = f.read().split('---', 2)
                        if len(partes) >= 3:
                            meta = yaml.safe_load(partes[1])
                            cuerpo = partes[2]
                            
                            ruta_relativa = os.path.relpath(root, DIR_CONTENIDO)
                            componentes_ruta = ruta_relativa.replace("\\", "/").split("/")
                            idioma = componentes_ruta[0]
                            cluster = componentes_ruta[1:]
                            
                            meta["_cuerpo_md"] = cuerpo
                            meta["_idioma"] = idioma
                            meta["_cluster_path"] = cluster
                            meta["_archivo_origen"] = ruta_completa
                            nodos.append(meta)
                    except Exception as e:
                        print(f"❌ ERROR: Estructura Front Matter rota en {archivo}: {e}")
                        sys.exit(1)
    return nodos

def calcular_grafo_semantico(nodos):
    for n_actual in nodos:
        relacionados = []
        vec_actual = n_actual.get("vectores", {})
        
        for n_potencial in nodos:
            if n_actual["id"] == n_potencial["id"] or n_actual["_idioma"] != n_potencial["_idioma"]:
                continue
            
            vec_potencial = n_potencial.get("vectores", {})
            score = 0
            for k in ["plataforma", "audiencia", "dificultad", "objetivo"]:
                if vec_actual.get(k) == vec_potencial.get(k) and vec_actual.get(k) is not None:
                    score += 1
            
            if score > 0:
                url = f"/minitools/{n_potencial['_idioma']}/{'/'.join(n_potencial['_cluster_path'])}/{n_potencial['id']}/"
                relacionados.append({"title": n_potencial["meta"]["title"], "url": url, "score": score})
        
        n_actual["_relacionados"] = sorted(relacionados, key=lambda x: x["score"], reverse=True)[:5]

def generar_imagen_og(titulo, ruta_salida):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    img = Image.new('RGB', (1200, 630), color='#1e293b')
    d = ImageDraw.Draw(img)
    d.rectangle([(40, 40), (1160, 590)], outline="#6366f1", width=8)
    d.text((80, 260), f"Minitools\n\n> {titulo}", fill="#ffffff")
    img.save(ruta_salida, "JPEG", quality=85)

def compilar():
    nodos = cargar_entidades()
    calcular_grafo_semantico(nodos)
    
    if not os.path.exists(TEMPLATE_PATH):
        print("❌ Error: Falta template.html")
        sys.exit(1)
        
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
        
    sitemap_urls = []
    
    for n in nodos:
        calc = n.get("calculadora", {})
        ruta_silo = f"{n['_idioma']}/{'/'.join(n['_cluster_path'])}/{n['id']}"
        dir_final = os.path.join(DIR_SALIDA, ruta_silo)
        os.makedirs(dir_final, exist_ok=True)
        
        # FIX EXCLUSIVO: Eliminar guiones medios del ID de funcion JS para evitar cortocircuitos matemáticos
        func_js_name = n['id'].replace('-', '_')
        
        html_inputs = "".join([f'<label>{i["label"]}</label><input type="{i["type"]}" id="{i["id"]}" placeholder="{i["placeholder"]}" oninput="calcular_{func_js_name}()"> ' for i in calc.get("inputs", [])])
        
        js_ops = ""
        for paso in calc.get("algoritmo", {}).get("pasos", []):
            arg1 = f"valores['{paso['args'][0]}']" if "inputs." in str(paso['args'][0]) or paso['args'][0] in [p['id'] for p in calc['algoritmo']['pasos']] else paso['args'][0]
            arg2 = f"valores['{paso['args'][1]}']" if "inputs." in str(paso['args'][1]) or paso['args'][1] in [p['id'] for p in calc['algoritmo']['pasos']] else paso['args'][1]
            signo = "/" if paso["op"] == "division" else "*"
            js_ops += f"valores['{paso['id']}'] = {arg1} {signo} {arg2};\n"

        html_calculadora = f"""
            {html_inputs}
            <button onclick="calcular_{func_js_name}()" class="calc-btn">Calcular Ahora ⚡</button>
            <div id="res_{n['id']}" class="calc-result-box" style="display:none;"></div>
            <script>
                function calcular_{func_js_name}() {{
                    let valores = {{}};
                    { "".join([f"valores['inputs.{i['id']}'] = parseFloat(document.getElementById('{i['id']}').value || 0);" for i in calc.get("inputs", [])]) }
                    {js_ops}
                    let resDiv = document.getElementById('res_{n['id']}');
                    resDiv.style.display = 'block';
                    resDiv.innerHTML = '{calc.get("algoritmo", {}).get("label", "Resultado")}: ' + valores['{calc.get("algoritmo", {}).get("output", "")}'].toLocaleString('es-ES', {{maximumFractionDigits: 2}}) + ' {calc.get("algoritmo", {}).get("unidad", "")}';
                }}
            </script>
        """

        html_faqs = "".join([f'<div class="faq-item"><h3>{f["q"]}</h3><p>{f["a"]}</p></div>' for f in n.get("faqs", [])])
        html_links = "".join([f'<li><a href="{r["url"]}">{r["title"]}</a></li>' for r in n.get("_relacionados", [])])
        cuerpo_html = markdown.markdown(n["_cuerpo_md"])
        
        html_final = template\
            .replace("{{META_TITLE}}", n["meta"]["title"])\
            .replace("{{META_DESCRIPTION}}", n["meta"]["description"])\
            .replace("{{URL_CATEGORIA}}", f"{n['_idioma']}/{'/'.join(n['_cluster_path'])}")\
            .replace("{{URL_HERRAMIENTA}}", n["id"])\
            .replace("{{NOMBRE_CATEGORIA}}", n["_cluster_path"][0].capitalize())\
            .replace("{{NOMBRE_HERRAMIENTA}}", n["entidad"])\
            .replace("{{TITULO_H1_HERRAMIENTA}}", n["vectores"]["intencion"])\
            .replace("{{CODIGO_INTERACTIVO_JS}}", html_calculadora)\
            .replace("{{TEXTO_GANCHO_AFILIADO}}", n["monetizacion"]["cta"])\
            .replace("{{LINK_AFILIADO}}", n["monetizacion"]["afiliado_url"])\
            .replace("{{TEXTO_QUE_ES}}", cuerpo_html)\
            .replace("{{BLOQUE_PREGUNTAS_FRECUENTES}}", html_faqs)\
            .replace("{{REPETIDOR_ENLAZADO_INTERNO}}", html_links)\
            .replace("{{SCHEMA_FAQ}}", "")\
            .replace("{{METRICS_CATCHER}}", "")

        with open(os.path.join(dir_final, "index.html"), 'w', encoding='utf-8') as out:
            out.write(html_final)
            
        generar_imagen_og(n["meta"]["title"], os.path.join(DIR_SALIDA, "assets", "og", f"{n['id']}.jpg"))
        sitemap_urls.append(f"https://minitools.io/{ruta_silo}/")

    # 🏠 DISEÑO DE PORTADA PREMIUM (INDEX.HTML DE LA RAÍZ)
    html_lista_herramientas = "".join([
        f'<div style="background: white; border: 1px solid #e2e8f0; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); transition: all 0.2s;" onmouseover="this.style.borderColor=\'#6366f1\'; this.style.transform=\'translateY(-2px)\';" onmouseout="this.style.borderColor=\'#e2e8f0\'; this.style.transform=\'translateY(0)\';">'
        f'<span style="background: #eef2ff; color: #4f46e5; font-size: 0.75rem; font-weight: 700; padding: 4px 8px; border-radius: 6px; text-transform: uppercase;">{item["vectores"]["plataforma"]}</span>'
        f'<h3 style="margin: 12px 0 8px 0; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em;"><a href="./{item["_idioma"]}/{"/".join(item["_cluster_path"])}/{item["id"]}/" style="color: #0f172a; text-decoration: none;">{item["meta"]["title"]}</a></h3>'
        f'<p style="color: #64748b; font-size: 0.95rem; margin: 0;">{item["meta"]["description"]}</p>'
        f'</div>'
        for item in nodos
    ])

    html_portada = f"""<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Minitools Factory | Directorio Inteligente</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 60px 20px; -webkit-font-smoothing: antialiased; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .hero {{ text-align: center; margin-bottom: 50px; }}
            .hero h1 {{ font-size: 3rem; font-weight: 800; letter-spacing: -0.04em; margin-bottom: 12px; color: #1e293b; }}
            .hero p {{ color: #64748b; font-size: 1.2rem; max-width: 600px; margin: 0 auto; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>⚡ Minitools Factory</h1>
                <p>Calculadoras mecánicas y aplicaciones semánticas de rendimiento atómico. Sin anuncios invasivos ni rastreadores.</p>
            </div>
            <div class="grid">
                {html_lista_herramientas if html_lista_herramientas else "<p>Cargando catálogo primario...</p>"}
            </div>
        </div>
    </body>
    </html>"""

    os.makedirs(DIR_SALIDA, exist_ok=True)
    with open(os.path.join(DIR_SALIDA, "index.html"), 'w', encoding='utf-8') as h_file:
        h_file.write(html_portada)

    # Guardar sitemap
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for u in sitemap_urls: xml += f'<url><loc>{u}</loc></url>'
    xml += '</urlset>'
    
    with open(os.path.join(DIR_SALIDA, "sitemap.xml"), 'w', encoding='utf-8') as s_file:
        s_file.write(xml)
        
    print("🚀 Compilación completada con diseño premium y parche JS activo.")

if __name__ == "__main__":
    compilar()
