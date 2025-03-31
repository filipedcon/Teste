from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Operadora

@api_view(["GET"])
def buscar_operadoras(request):
    query = request.GET.get("q", "")
    if not query:
        return Response({"resultado": []})

    operadoras = Operadora.objects.filter(Razao_Social__icontains=query)
    data = [
        {
            "id": op.id,
            "Registro_ANS": op.Registro_ANS,
            "CNPJ": op.CNPJ,
            "Razao_Social": op.Razao_Social,
            "Modalidade": op.Modalidade,
            "Cidade": op.Cidade,
            "UF": op.UF,
        }
        for op in operadoras
    ]
   
    return Response({"resultado": data})
