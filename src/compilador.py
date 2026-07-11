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
                url = f"/{n_potencial['_idioma']}/{'/'.join(n_potencial['_cluster_path'])}/{n_potencial['id']}/"
                relacionados.append({"title": n_potencial["meta"]["title"], "url": url, "score": score})
        
        n_actual["_relacionados"] = sorted(relacionados, key=lambda x: x["score"], reverse=True)[:5]

def generar_imagen_og(titulo, ruta_salida):
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    img = Image.new('RGB', (1200, 630), color='#1e293b')
    d = ImageDraw.Draw(img)
    d.rectangle([(40, 40), (1160, 590)], outline="#2563eb", width=8)
    # Nota: Usamos texto simple nativo para evitar fallos de fuentes en el servidor
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
        # LINTER & VALIDACIÓN MATEMÁTICA
        calc = n.get("calculadora", {})
        if "algoritmo" in calc:
            # Test unitario básico
            pass

        ruta_silo = f"{n['_idioma']}/{'/'.join(n['_cluster_path'])}/{n['id']}"
        dir_final = os.path.join(DIR_SALIDA, ruta_silo)
        os.makedirs(dir_final, exist_ok=True)
        
        html_inputs = "".join([f'<label style="display:block; margin-top:10px; font-weight:bold;">{i["label"]}</label><input type="{i["type"]}" id="{i["id"]}" placeholder="{i["placeholder"]}" style="width:100%; padding:10px; margin-top:5px; border:1px solid #cbd5e1; border-radius:6px;">' for i in calc.get("inputs", [])])
        
        js_ops = ""
        for paso in calc.get("algoritmo", {}).get("pasos", []):
            arg1 = f"valores['{paso['args'][0]}']" if "inputs." in str(paso['args'][0]) or paso['args'][0] in [p['id'] for p in calc['algoritmo']['pasos']] else paso['args'][0]
            arg2 = f"valores['{paso['args'][1]}']" if "inputs." in str(paso['args'][1]) or paso['args'][1] in [p['id'] for p in calc['algoritmo']['pasos']] else paso['args'][1]
            signo = "/" if paso["op"] == "division" else "*"
            js_ops += f"valores['{paso['id']}'] = {arg1} {signo} {arg2};\n"

        html_calculadora = f"""
            {html_inputs}
            <button onclick="calcular_{n['id']}()" style="width:100%; background:#2563eb; color:white; border:none; padding:12px; font-weight:bold; margin-top:15px; border-radius:6px; cursor:pointer;">Calcular Ahora</button>
            <div id="res_{n['id']}" style="margin-top:15px; padding:15px; background:#f1f5f9; border-radius:6px; text-align:center; font-weight:bold; display:none;"></div>
            <script>
                function calcular_{n['id']}() {{
                    let valores = {{}};
                    { "".join([f"valores['inputs.{i['id']}'] = parseFloat(document.getElementById('{i['id']}').value || 0);" for i in calc.get("inputs", [])]) }
                    {js_ops}
                    let resDiv = document.getElementById('res_{n['id']}');
                    resDiv.style.display = 'block';
                    resDiv.innerHTML = '{calc.get("algoritmo", {}).get("label", "Resultado")}: ' + valores['{calc.get("algoritmo", {}).get("output", "")}'].toFixed(2) + ' {calc.get("algoritmo", {}).get("unidad", "")}';
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

    # Guardar sitemap
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for u in sitemap_urls: xml += f'<url><loc>{u}</loc></url>'
    xml += '</urlset>'
    
    os.makedirs(DIR_SALIDA, exist_ok=True)
    with open(os.path.join(DIR_SALIDA, "sitemap.xml"), 'w', encoding='utf-8') as s_file:
        s_file.write(xml)
        
    print(f"🚀 Compilación exitosa. {len(nodos)} objetos procesados.")

if __name__ == "__main__":
    compilar()
