from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="inicio"),
    path("buscar/", views.buscar_en_pdfs, name="buscar_pdfs"),
    path("importar/", views.importar_pdfs, name="importar_pdfs"),
]