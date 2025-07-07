import os, re, fitz
from django.shortcuts import render         # 📦 Librerías de sistema y PyMuPDF
from django.contrib import messages         # 1) Importamos sistema de mensajes
from .forms import PDFSearchForm            # 2) Formulario solo para el texto
from django.conf import settings            # Para vista en pdf embebida
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import datetime
from dateutil import parser
from django.shortcuts import redirect
from django.utils.html import escape


def index(request):
    return render(request, "analizador/index.html")

# 📁 Carpeta donde se guardan los archivos PDF importados

MEDIA_DIR = settings.MEDIA_ROOT
TEMP_DIR = os.path.join(MEDIA_DIR, "tmp")

def buscar_en_pdfs(request):
    form = PDFSearchForm(request.POST or None)
    resultados = []

    os.makedirs(TEMP_DIR, exist_ok=True)

    # 🧹 Limpiar TEMP_DIR solo si se suben nuevos archivos
    archivos = request.FILES.getlist("archivos")
    if archivos:
        for archivo in os.listdir(TEMP_DIR):
            ruta_archivo = os.path.join(TEMP_DIR, archivo)
            try:
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {ruta_archivo}: {e}")

        # 📦 Guardamos los nombres en sesión para búsquedas futuras
        request.session["archivos_actuales"] = [archivo.name for archivo in archivos]

    # 🔁 Si no se subieron nuevos, usamos los anteriores guardados en sesión
    elif "archivos_actuales" in request.session:
        archivos = request.session["archivos_actuales"]

    if request.method == "POST":
        palabra = request.POST.get("palabra", "").strip()

        if not archivos:
            messages.error(request, "Debes subir al menos un PDF.")
        if not palabra:
            messages.error(request, "Debes ingresar el texto a buscar.")

        if archivos and palabra:
            lower_palabra = palabra.lower()

            for archivo in archivos:
                if isinstance(archivo, str):
                    nombre = archivo
                    ruta_temp = os.path.join(TEMP_DIR, nombre)
                else:
                    nombre = archivo.name
                    ruta_temp = os.path.join(TEMP_DIR, nombre)
                    try:
                        with open(ruta_temp, "wb") as f:
                            for chunk in archivo.chunks():
                                f.write(chunk)
                    except Exception as e:
                        print(f"⚠️ No se pudo guardar {nombre}: {e}")
                        continue

                fragmento = "–"
                encontrado = False

                # 🔍 Buscar la palabra en el PDF
                try:
                    doc = fitz.open(ruta_temp)
                    for pagina in doc:
                        texto = pagina.get_text()
                        if lower_palabra in texto.lower():
                            for linea in texto.splitlines():
                                if lower_palabra in linea.lower():
                                    patrón = re.compile(re.escape(palabra), re.IGNORECASE)
                                    fragmento = patrón.sub(
                                        lambda m: f"<mark>{m.group(0)}</mark>", linea.strip()
                                    )
                                    encontrado = True
                                    break
                        if encontrado:
                            break
                    doc.close()
                except Exception as e:
                    fragmento = f"⚠️ Error al leer PDF: {e}"

                resultados.append({
                    "nombre": nombre,
                    "fragmento": fragmento,
                    "coincide": encontrado,
                    "ruta": f"/media/tmp/{nombre}"
                })

    # 🧮 Ordenar: primero los que tienen coincidencia
    resultados.sort(key=lambda x: x["coincide"], reverse=True)

    
    archivos_html = ""
    if request.session.get("archivos_actuales"):
        archivos = request.session["archivos_actuales"]
        archivos_html = "<ul class='mb-0 ps-3'>"
        for nombre in archivos:
            nombre_escapado = escape(nombre)
            archivos_html += f"<li>{nombre_escapado}</li>"
    archivos_html += "</ul>"
    
    return render(request, "analizador/busqueda.html", {
        "form": form,
        "resultados": resultados,
        "archivos_html": archivos_html,
    })




def reiniciar_busqueda(request):
    # 🧹 Eliminar archivos temporales
    for archivo in os.listdir(TEMP_DIR):
        ruta = os.path.join(TEMP_DIR, archivo)
        try:
            if os.path.isfile(ruta):
                os.remove(ruta)
        except Exception as e:
            print(f"⚠️ No se pudo eliminar {ruta}: {e}")

    # 🧼 Limpiar sesión de archivos
    request.session.pop("archivos_actuales", None)

    # 🔄 Redirigir al formulario limpio
    return redirect("buscar_pdfs")




# 📄 Vista principal para importar y renombrar archivos PDF
def importar_pdfs(request):
    form = PDFSearchForm(request.POST or None)   # Instanciamos el formulario
    resultados = []                              # Lista para mostrar resultados en la tabla

    if request.method == "POST":
        archivos = request.FILES.getlist("archivos")

        # ✅ Validación: mostramos error si no se subió ningún archivo
        if not archivos:
            messages.error(request, "Debes subir al menos un PDF.")
        else:
            os.makedirs(MEDIA_DIR, exist_ok=True)

            for archivo in archivos:
                nombre_original = archivo.name
                ruta_temp = os.path.join(MEDIA_DIR, nombre_original)
                rut_emisor = "sin_rut"
                factura = "sin_factura"
                estado = "Importado correctamente"

                # 📥 Guardamos el archivo en disco
                with open(ruta_temp, "wb") as f:
                    for chunk in archivo.chunks():
                        f.write(chunk)

                # 🔍 Intentamos abrir el PDF y extraer información
                try:
                    doc = fitz.open(ruta_temp)
                    todos_ruts = []

                    for pagina in doc:
                        txt = pagina.get_text()
                        todos_ruts += re.findall(r'R\.U\.T\.:\s*([\d\.]+\-\w)', txt)
                        m = re.search(r'Nº\s*(\d+)', txt)
                        if m:
                            factura = m.group(1)
                    doc.close()

                    if len(todos_ruts) >= 2:
                        rut_emisor = todos_ruts[1].replace(".", "")
                    elif todos_ruts:
                        rut_emisor = todos_ruts[0].replace(".", "")

                    nuevo_nombre = f"{rut_emisor}_F{factura}.pdf"
                    ruta_final = os.path.join(MEDIA_DIR, nuevo_nombre)

                    # 🔁 Si el archivo ya existe, lo reemplazamos
                    if os.path.exists(ruta_final):
                        os.remove(ruta_final)
                    os.rename(ruta_temp, ruta_final)

                except Exception as e:
                    estado = f"⚠️ Error: {e}"
                    ruta_final = ruta_temp



                # 🗂️ Agregamos resultado para mostrar en tabla HTML
                resultados.append({
                    "nombre": os.path.basename(ruta_final),
                    "fragmento": estado,
                    "ruta": f"/media/{os.path.basename(ruta_final)}"
                })

    # 📦 Renderizamos plantilla de importación con resultados
    return render(request, "analizador/importacion.html", {
        "form": form,
        "resultados": resultados
    })
    




def extraer_fecha(texto):
    match = re.search(r"Fecha\s*Emision\s*[:\-]?\s*(\d{1,2}\s+de\s+\w+\s+(?:del|de)\s+\d{4})", texto, re.IGNORECASE)
    if match:
        try:
            fecha_raw = match.group(1).strip()

            # Traducir meses en español a inglés
            meses = {
                "enero": "january", "febrero": "february", "marzo": "march",
                "abril": "april", "mayo": "may", "junio": "june",
                "julio": "july", "agosto": "august", "septiembre": "september",
                "octubre": "october", "noviembre": "november", "diciembre": "december"
            }
            for esp, eng in meses.items():
                if esp in fecha_raw.lower():
                    fecha_raw = re.sub(esp, eng, fecha_raw, flags=re.IGNORECASE)
                    break

            # Eliminar 'del' o 'de' antes del año
            fecha_raw = re.sub(r"\s+(del|de)\s+", " ", fecha_raw)
            fecha_dt = parser.parse(fecha_raw, dayfirst=True)
            return fecha_dt.strftime("%d/%m/%Y")
        except:
            return "—"
    return "—"





def ver_archivos_media(request):
    media_dir = settings.MEDIA_ROOT
    archivos = []

    for nombre in os.listdir(media_dir):
        ruta_completa = os.path.join(media_dir, nombre)
        if os.path.isfile(ruta_completa) and nombre.lower().endswith(".pdf"):
            fecha_emision = "—"

            try:
                doc = fitz.open(ruta_completa)
                texto = doc[0].get_text()
                fecha_emision = extraer_fecha(texto)
                doc.close()
            except:
                pass

            archivos.append({
                "nombre": nombre,
                "fecha": fecha_emision,
                "ruta": f"/media/{nombre}"
            })
            
        # 👇 ORDENAR por fecha más nueva (descendente)
    def fecha_valida(x):
        try:
            return parser.parse(x["fecha"], dayfirst=True)
        except:
            return datetime.min

    archivos.sort(key=fecha_valida, reverse=True)

    return render(request, "analizador/media_list.html", { 
        "archivos": archivos, 
        "orden_actual": "fecha_desc"
 })
    
    
    
    
    
    
    
def vista_pdf(request, nombre_archivo):
    tmp_path = os.path.join(settings.MEDIA_ROOT, "tmp", nombre_archivo)
    media_path = os.path.join(settings.MEDIA_ROOT, nombre_archivo)

    if os.path.exists(tmp_path):
        ruta_final = f"/media/tmp/{nombre_archivo}"
        existe = True
    elif os.path.exists(media_path):
        ruta_final = f"/media/{nombre_archivo}"
        existe = True
    else:
        ruta_final = ""
        existe = False

    return render(request, "analizador/vista_pdf.html", {
        "archivo": nombre_archivo,
        "ruta": ruta_final,
        "existe": existe
    })
    
    
    








def filtrar_archivos_media(request):
    query = request.GET.get("query", "").strip()
    orden = request.GET.get("orden", "")
    if not orden:
        orden = "fecha_desc"

    lower_query = query.lower()
    media_dir = settings.MEDIA_ROOT
    resultados = []

    for nombre in os.listdir(media_dir):
        ruta = os.path.join(media_dir, nombre)
        if os.path.isfile(ruta) and nombre.lower().endswith(".pdf"):
            fragmento = "–"
            coincide = False
            fecha_emision = "—"

            try:
                doc = fitz.open(ruta)

                # Extraer fecha desde la primera página para todos los casos
                texto_pagina0 = doc[0].get_text()
                fecha_emision = extraer_fecha(texto_pagina0)

                # Coincidencia en nombre del archivo
                if lower_query in nombre.lower():
                    fragmento = "<em>Coincidencia en el nombre del archivo</em>"
                    coincide = True
                else:
                    # Coincidencia en contenido del PDF
                    for pagina in doc:
                        texto = pagina.get_text()
                        if lower_query in texto.lower():
                            for linea in texto.splitlines():
                                if lower_query in linea.lower():
                                    patrón = re.compile(re.escape(query), re.IGNORECASE)
                                    fragmento = patrón.sub(lambda m: f"<mark>{m.group(0)}</mark>", linea.strip())
                                    coincide = True
                                    break
                        if coincide:
                            break

                doc.close()
            except Exception as e:
                print("⚠️ Error al procesar el PDF:", e)
                fecha_emision = "—"

            if coincide:
                resultados.append({
                    "nombre": nombre,
                    "fragmento": fragmento,
                    "fecha": fecha_emision,
                    "ruta": f"/media/{nombre}"
                })

    # Ordenamiento si se solicita
    def fecha_valida(x):
        try:
            return parser.parse(x["fecha"], dayfirst=True)
        except:
            return datetime.min

    if orden == "fecha_asc":
        resultados.sort(key=fecha_valida)
    elif orden == "fecha_desc":
        resultados.sort(key=fecha_valida, reverse=True)
    elif orden == "nombre_asc":
        resultados.sort(key=lambda x: x["nombre"].lower())
    elif orden == "nombre_desc":
        resultados.sort(key=lambda x: x["nombre"].lower(), reverse=True)

    html = render_to_string("analizador/partials/tabla_archivos.html", {
        "archivos": resultados,
        "orden_actual": orden
    })
    return HttpResponse(html)



def media_list(request):
    media_dir = settings.MEDIA_ROOT
    archivos = []

    for nombre in os.listdir(media_dir):
        ruta = os.path.join(media_dir, nombre)
        if os.path.isfile(ruta) and nombre.lower().endswith(".pdf"):
            fragmento = "–"
            fecha_emision = "—"

            try:
                doc = fitz.open(ruta)
                texto = doc[0].get_text()
                fecha_emision = extraer_fecha(texto)
                doc.close()
            except:
                pass

            archivos.append({
                "nombre": nombre,
                "fragmento": fragmento,
                "fecha": fecha_emision,
                "ruta": f"/media/{nombre}"
            })

    return render(request, "analizador/media_list.html", {
        "archivos": archivos
        
    })


