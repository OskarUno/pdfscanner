# 📄 PDFScanner

Aplicación web desarrollada con Django para importar, renombrar, buscar y gestionar texto dentro de archivos PDF.

---

## ✨ Funcionalidades principales

- 📁 Subida múltiple de archivos PDF
- 📝 Renombrado automático con formato `{RUT}_F{Factura}.pdf`
- 🔍 Búsqueda de texto dentro de los PDFs **sin guardarlos** (modo temporal)
- 📂 Lote de búsqueda persistente gracias a almacenamiento en sesión
- 🗑️ Botón “Reiniciar lote” para limpiar PDFs temporales sin salir de la vista
- 🧠 Mensaje contextual con recuento dinámico de archivos activos
- 🧭 Popover interactivo con scroll para mostrar nombres de PDFs cargados
- 🎯 Panel dividido en dos vistas principales: `Importar` y `Buscar`
- 📄 Visualización embebida de PDFs con botones rápidos (`Volver`, `Inicio`, `Nueva pestaña`)
- 🗂️ Panel adicional para listar archivos **persistentes** en la carpeta `media/`
- 🎨 Interfaz optimizada con Bootstrap 5 y componentes reutilizables (`include`)
- 🧹 Limpieza inteligente de PDFs temporales solo si se sube un nuevo lote

---

## 🚀 Cómo ejecutar el proyecto

1. Cloná el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/pdfscanner.git
   cd pdfscanner


2. - Activa el entorno virtual:
python -m venv venv
venv\Scripts\activate  # en Windows

3. - Instala dependencias:
pip install -r requirements.txt

4. - Ejecuta el servidor de desarrollo:
python manage.py runserver

5. - Accede en tu navegador: http://127.0.0.1:8000

📁 Estructura clave
| Carpeta / Archivo  | Descripción | 
| manage.py          | Archivo principal para comandos Django | 
| pdfscanner/        | Configuración del proyecto (settings, urls) | 
| analizador/        | App que contiene vistas, templates y lógica | 
| media/             | Carpeta con PDFs importados (ignorada por Git) | 
| media/tmp/         | Carpeta temporal usada para búsqueda sin persistencia | 
| templates/         | HTML estilizado con Bootstrap 5 | 
| components/        | Fragmentos reutilizables (footer, botones_pdf, etc.) | 
| vista_pdfs.css     | Estilos personalizados para visualización | 


🔐 Privacidad y exclusiones
- Los archivos PDF procesados se almacenan localmente en la carpeta media/
- La carpeta media/ está excluida del control de versiones vía .gitignore
- Los archivos temporales se mantienen durante la sesión y se limpian al reiniciar el lote



📌 Requisitos
- 🐍 Python 3.12
- 🎯 Django 5.x
- 📚 PyMuPDF (fitz) para manipulación de PDFs

🛡️ Autor
Desarrollado por Oscar
Asistencia técnica proporcionada por Copilot
