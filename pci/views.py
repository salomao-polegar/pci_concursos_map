from django.shortcuts import render
from .helpers import atualizarInformacoes, return_map
from .models import Data

# Create your views here.
def index(request):
    """ View da index da página. """

    if request.GET.get("uf"):
        map, address, invalid_address = return_map(uf = request.GET.get("uf"))
    elif request.GET.get("orgao"):
        map, address, invalid_address = return_map(orgao = request.GET.get("orgao"))
    else:
        map, address, invalid_address = return_map()
    
    context = {
        'map' : map,
        'invalid_address' : invalid_address,
        'address':address
    }
    return render(request, "index.html", context)

def atualizar(request):
    "View para atualizar as informações do banco de dados"
    qtde = atualizarInformacoes()
    if qtde > 0: 
        mensagem = f"Dados atualizados com Sucesso. {qtde} dados atualizados."
    else:
        mensagem = "Dados já estão atualizados."

    map, address, invalid_address = return_map()
    context = {
        'map' : map,
        'invalid_address' : invalid_address,
        'mensagem':mensagem,
        'address':address
    }
    
    return render(request, "index.html", context)

def excluir(request):
    """ View para excluir os dados do banco de dados"""
    Data.objects.all().delete() 
    map, address, invalid_address = return_map()
    context = {
        'map' : map,
        'invalid_address' : invalid_address,
        'mensagem':"Dados excluidos com Sucesso",
        'address':address
    }
    return render(request, "index.html", context)

