import os, re, fitz
from django.shortcuts import render
from django.contrib import messages        # 1) Importamos sistema de mensajes
from .forms import PDFSearchForm          # 2) Formulario solo para el texto

MEDIA_DIR = "media"

def index(request):
    return render(request, "analizador/index.html")



def buscar_en_pdfs(request):
    # 3) Instanciamos el form con POST (para renderizar valor de 'palabra')
    form = PDFSearchForm(request.POST or None)
    resultados = []  # Aquí acumulamos los resultados para la tabla

    if request.method == "POST":
        # 4) Leemos el texto y los archivos subidos
        palabra = request.POST.get("palabra", "").strip()
        archivos = request.FILES.getlist("archivos")

        # 5) Validaciones: errores si faltan inputs
        if not archivos:
            messages.error(request, "Debes subir al menos un PDF.")
        if not palabra:
            messages.error(request, "Debes ingresar el texto a buscar.")

        # 6) Sólo procesamos si hay archivos y texto
        if archivos and palabra:
            lower_palabra = palabra.lower()

            for archivo in archivos:
                nombre = archivo.name
                fragmento = "–"
                encontrado = False

                try:
                    # 6a) Abrimos PDF en memoria
                    doc = fitz.open(stream=archivo.read(), filetype="pdf")

                    # 6b) Buscamos en cada página
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

                # 6c) Añadimos a resultados
                resultados.append({
                    "nombre": nombre,
                    "fragmento": fragmento,
                    "coincide": encontrado
                })

    # 7) Renderizamos la plantilla con form, resultados y mensajes de error
    return render(request, "analizador/busqueda.html", {
        "form": form,
        "resultados": resultados
    })
  
  


def importar_pdfs(request):
    form = PDFSearchForm(request.POST or None)
    resultados = []

    if request.method == "POST":
        archivos = request.FILES.getlist("archivos")

        # ← Aquí validamos y lanzamos el mensaje
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

                # Guardar el archivo en disco
                with open(ruta_temp, "wb") as f:
                    for chunk in archivo.chunks():
                        f.write(chunk)

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

                    # Si existe, lo sustituimos
                    if os.path.exists(ruta_final):
                        os.remove(ruta_final)
                    os.rename(ruta_temp, ruta_final)

                except Exception as e:
                    estado = f"⚠️ Error: {e}"
                    ruta_final = ruta_temp

                resultados.append({
                    "nombre": os.path.basename(ruta_final),
                    "fragmento": estado,
                    "ruta": f"/media/{os.path.basename(ruta_final)}"
                })

    return render(request, "analizador/importacion.html", {
        "form": form,
        "resultados": resultados
    })