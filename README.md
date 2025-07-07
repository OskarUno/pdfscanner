# 📄 PDFScanner

Aplicación web desarrollada con Django para importar, renombrar, buscar y gestionar texto dentro de archivos PDF.

## ✨ Funcionalidades

- Subida múltiple de archivos PDF
- Renombrado automático de PDFs con formato `{RUT}_F{Factura}.pdf`
- Búsqueda de texto dentro de los PDFs **sin guardarlos** (modo temporal)
- Panel dividido en dos vistas: `Importar` y `Buscar`
- Visualización embebida de PDFs con botones reutilizables (`Volver`, `Inicio`, `Nueva pestaña`)
- Panel adicional para listar archivos **persistentes** en la carpeta `media/`
- Navegación consistente con footer fijo en todas las vistas
- Interfaz optimizada con Bootstrap 5 y componentes fragmentados (`include`)


## 🚀 Cómo ejecutar el proyecto

1. - Clona el repositorio:
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
| components/         | Fragmentos reutilizables (footer, botones_pdf, etc.) | 
| vista_pdfs.css        | Estilos personalizados para visualización | 


🔐 Privacidad y exclusiones
- Archivos PDF procesados se almacenan localmente en la carpeta media/
- La carpeta media/ está excluida del control de versiones vía .gitignore
- Se aplican buenas prácticas para no guardar PDFs temporales innecesarios (tmp/ se limpia en cada búsqueda)



📌 Requisitos
- 🐍 Python 3.12
- 🎯 Django 5.x
- 📚 PyMuPDF (fitz) para manipulación de PDFs

🛡️ Autor
Desarrollado por Oscar
Asistencia técnica proporcionada por Copilot
