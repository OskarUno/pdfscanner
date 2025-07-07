from django.urls import path
from . import views
from analizador.views import buscar_en_pdfs, reiniciar_busqueda


urlpatterns = [
    path("", views.index, name="inicio"),
    path('', views.index, name='index'),

    path("buscar/", views.buscar_en_pdfs, name="buscar_pdfs"),
    path("reiniciar/", reiniciar_busqueda, name="reiniciar_busqueda"),

    path("importar/", views.importar_pdfs, name="importar_pdfs"),
    path("ver/<str:nombre_archivo>/", views.vista_pdf, name="vista_pdf"),
    path("archivos/", views.ver_archivos_media, name="ver_archivos_media"),
    
    path("archivos/filtrar/", views.filtrar_archivos_media, name="filtrar_archivos_media"),
    
]