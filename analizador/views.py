import os, re, fitz
from django.shortcuts import render         # 📦 Librerías de sistema y PyMuPDF
from django.contrib import messages         # 1) Importamos sistema de mensajes
from .forms import PDFSearchForm            # 2) Formulario solo para el texto
from django.conf import settings            # Para vista en pdf embebida

# 📁 Carpeta donde se guardan los archivos PDF importados
MEDIA_DIR = settings.MEDIA_ROOT



def index(request):
    return render(request, "analizador/index.html")


def buscar_en_pdfs(request):
    form = PDFSearchForm(request.POST or None)
    resultados = []

    if request.method == "POST":
        palabra = request.POST.get("palabra", "").strip()
        archivos = request.FILES.getlist("archivos")

        if not archivos:
            messages.error(request, "Debes subir al menos un PDF.")
        if not palabra:
            messages.error(request, "Debes ingresar el texto a buscar.")

        if archivos and palabra:
            lower_palabra = palabra.lower()

            for archivo in archivos:
                nombre = archivo.name
                ruta_temp = os.path.join(MEDIA_DIR, nombre)
                fragmento = "–"
                encontrado = False

                # 🧾 Guardar archivo en disco para vista previa posterior
                try:
                    with open(ruta_temp, "wb") as f:
                        for chunk in archivo.chunks():
                            f.write(chunk)

                    # 🔍 Abrir PDF y buscar palabra
                    doc = fitz.open(ruta_temp)

                    for pagina in doc:
                        texto = pagina.get_text()
                        if lower_palabra in texto.lower():
                            for linea in texto.splitlines():
                                if lower_palabra in linea.lower():
                                    patrón = re.compile(re.escape(palabra), re.IGNORECASE)
                                    fragmento = patrón.sub(lambda m: f"<mark>{m.group(0)}</mark>", linea.strip())
                                    encontrado = True
                                    break
                        if encontrado:
                            break
                    doc.close()

                except Exception as e:
                    fragmento = f"⚠️ Error al leer PDF: {e}"

                # 📋 Guardamos resultado para mostrar en tabla y vista previa
                resultados.append({
                    "nombre": nombre,
                    "fragmento": fragmento,
                    "coincide": encontrado,
                    "ruta": f"/media/{nombre}"
                })

    return render(request, "analizador/busqueda.html", {
        "form": form,
        "resultados": resultados
    })

  




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
    
    
    
def vista_pdf(request, nombre_archivo):
    ruta_pdf = os.path.join(settings.MEDIA_ROOT, nombre_archivo)
    existe = os.path.exists(ruta_pdf)

    return render(request, "analizador/vista_pdf.html", {
        "archivo": nombre_archivo,
        "existe": existe
    })
