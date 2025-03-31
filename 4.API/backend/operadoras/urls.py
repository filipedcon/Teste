from django.urls import path
from .views import buscar_operadoras

urlpatterns = [
    path("busca/", buscar_operadoras, name="buscar_operadoras"), 
]
