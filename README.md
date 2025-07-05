# 📄 PDFScanner

Aplicación web desarrollada con Django para importar, renombrar y buscar texto dentro de archivos PDF.

## ✨ Funcionalidades

- Subida múltiple de archivos PDF.
- Búsqueda de texto dentro de los PDFs sin guardarlos.
- Renombrado automático de PDFs con formato `{RUT}_F{Factura}.pdf`.
- Interfaz optimizada con Bootstrap 5.
- Panel dividido en dos vistas: `Importar` y `Buscar`.

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
| Carpeta / Archivo | Descripción | 
| manage.py | Archivo principal para comandos Django | 
| pdfscanner/ | Configuración del proyecto (settings, urls) | 
| analizador/ | App que contiene vistas, templates y lógica | 
| media/ | Carpeta con PDFs importados (ignorada por Git) | 
| templates/ | HTML estilizado con Bootstrap 5 | 


## 📁 Privacidad y exclusiones

Este proyecto genera archivos PDF que se almacenan localmente en la carpeta `media/`.  
Por razones de privacidad y buen control de versiones, esta carpeta está excluida del repositorio mediante `.gitignore`.



📌 Requisitos
- 🐍 Python 3.12
- 🎯 Django 5.x
- 📚 PyMuPDF (fitz) para manipulación de PDFs

🛡️ Autor
Desarrollado por Oscar
Asistencia técnica proporcionada por Copilot
