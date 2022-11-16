from bs4 import BeautifulSoup
import requests
import re
from geopy.geocoders import GoogleV3

import requests
from .models import Data
import folium
import pandas as pd
import os

## Transformar em variável de ambiente
FREQ_ATUALIZACAO_PARCIAL = 20

def return_map(uf=None, orgao=None):
    """ Retorna o mapa a ser inserido no site.
    Parâmetros: uf, orgao """
    if uf:
        address = Data.objects.filter(uf__contains=uf)
        invalid_address = Data.objects.filter(longitude=0)        
    if orgao:
        address = Data.objects.filter(orgao__contains=orgao)
        invalid_address = Data.objects.filter(longitude=0)
        
    if not uf and not orgao:
        address = Data.objects.exclude(longitude=0)
        invalid_address = Data.objects.filter(longitude=0)
    
    
    df = pd.DataFrame(list(address.values('latitude', 'longitude')))
    if df.shape[0]:
        lat_map = (df.latitude.min()+df.latitude.max()) / 2 # Latitude mediana
        lng_map = (df.longitude.min()+df.longitude.max()) / 2 # Latitude mediana
    else:
        lat_map = -14.2400732 # Latitude mediana
        lng_map = -53.1805017  # Latitude mediana
    #zoom = math.pow(df.latitude.max()-df.latitude.min(), 2)
    #print(f"zoom:{zoom}|min:{df.latitude.min()}|max:{df.latitude.max()}")
    m = folium.Map(location=[lat_map, lng_map], zoom_start = 4)
    for i in address:
        latitude = i.latitude
        longitude = i.longitude
        nome = i.orgao
        salario = i.salario
        link = i.link
        vagas = i.vagas
        cargos = i.cargos
        nivel = i.nivel
        inscricoes_ate = i.inscricoes_ate
        
        dados = f"""<p>{nome}    |    {moeda_real(salario)}</p>
        <p>{vagas}</p>
        <p>{cargos}</p>
        <p>{nivel}</p>
        <p>Inscrições até: {inscricoes_ate}</p>        
        <p>Link: <a href={link} target="_blank">Clique Aqui</a></p>"""
        iframe = folium.IFrame(dados,
                       width=300,
                       height=200)
        pop = folium.Popup(iframe)
        
        folium.Marker([latitude, longitude], tooltip=nome+"   |   "+ moeda_real(salario), popup=pop).add_to(m)

    m = m._repr_html_
    return m, address, invalid_address


def divs_concursos():
    """ Salva todas as divs que contém concursos com inscrições futuras, com BeautifulSoup """
    r = requests.get('https://www.pciconcursos.com.br/concursos/')
    html = r.text
    soup = BeautifulSoup(html, features="html.parser")
    
    return soup.select("#concursos > .fa, .na")

def return_endereco(endereco):
    """Retorna o endereço a partir da API do Google"""
    key = SECRET_KEY = os.environ.get("KEY_GOOGLE")
    geolocator = GoogleV3(api_key=key)
    req = geolocator.geocode(endereco)
    return req

def atualizarInformacoes():
    """ Atualiza as informações na base de dados """
    divs = divs_concursos()

    # Carrega os dados atuais do banco de dados
    dados_iniciais =  Data.objects.all()

    dados, orgao, uf, salario, vagas, endereco, latitude, longitude, link, cargos, nivel, inscricoes_ate = [], [], [], [], [], [], [], [], [], [], [], []
    qtde, qtde_util = 0, 0

    for div in divs:
        if qtde_util > 0 and qtde_util % FREQ_ATUALIZACAO_PARCIAL == 0:
            dados = {
            "orgao": orgao,
            "uf": uf,
            "salario": salario,
            "vagas":vagas,
            "endereco": endereco,
            "latitude": latitude,
            "longitude": longitude,
            "link":link,
            "cargos": cargos,
            "nivel":nivel,
            "inscricoes_ate":inscricoes_ate,
            }
            atualizar(dados)
            dados, orgao, uf, salario,vagas, endereco, latitude, longitude, link, cargos, nivel, inscricoes_ate = [], [], [], [], [], [], [], [], [], [], [], []
        
            dados_iniciais =  Data.objects.all()
            
        qtde+=1
        
        # Título
        titulo = div.select("a")[0].text
        orgao.append(titulo)

        # Estado
        uf.append(div.select(".cc")[0].text)

        # Salário
        salario_form = re.findall("[0-9]*\.*[0-9]*,[0-9]*", div.select(".cd")[0].text)
        if len(salario_form) == 0:
            salario.append(0)
        else:
            salario.append(float(salario_form[0].replace('.','').replace(",", ".")))
        sel = div.select(".cd")[0]
        sel = str(sel).split("<span>")
        vagas_infos = [i.replace("<div class=\"cd\">", "").replace("<br/>", "").replace("</span>", "").replace("\n", "").replace("</div>", "") for i in sel]

        vagas.append(vagas_infos[0])
        cargos.append(vagas_infos[1])
        nivel.append(vagas_infos[2])
        inscricoes_ate.append(div.select(".ce")[0].text)
        # Localização
        # Só vamos procurar a lozalização dos dados que não estão salvos no banco de dados, visto que a requisição é demorada
        link.append(div.find("a")["href"])
        
        if dados_iniciais.count():
            titulos_db = [i[0] for i in dados_iniciais.values_list("orgao")]
            
            if titulo in titulos_db:
                print(f"""#    {qtde}   ====>   Repetido   ===>   {titulo[0:20]}...""")
                orgao.pop()
                uf.pop()
                salario.pop()
                link.pop()
                vagas.pop()
                cargos.pop()
                nivel.pop()
                inscricoes_ate.pop()

                continue # Se o dado já existir, ir para a próxima iteração
        
        try:
            location = return_endereco(titulo+ " " +uf[-1]+" Brasil")
            if location != None:
                endereco.append(f"{location.address}")
                latitude.append(location.latitude)
                longitude.append(location.longitude)
                
            else:
                raise AttributeError()

        except AttributeError:
            endereco.append(0)
            latitude.append(0)
            longitude.append(0)
        
        print(f"""#    {qtde}   ====>   OK   ===>   {titulo[0:20]}...""")
        qtde_util+=1

    
    dados_atualizados = {
        "orgao": orgao,
        "uf": uf,
        "salario": salario,
        "vagas":vagas,
        "endereco": endereco,
        "latitude": latitude,
        "longitude": longitude,
        "link":link,
        "cargos": cargos,
        "nivel":nivel,
        "inscricoes_ate":inscricoes_ate,
    }
    atualizar(dados_atualizados)
    return qtde_util
    
def atualizar(dados):
    params = zip(dados['orgao'], dados['uf'], dados['salario'], dados['vagas'], dados['endereco'], dados['latitude'], dados['longitude'], dados['link'], dados['cargos'], dados['nivel'], dados['inscricoes_ate'])
    products = [Data(orgao = param[0], uf=param[1], salario=param[2], vagas=param[3], endereco=param[4], latitude=param[5], longitude=param[6], link=param[7], cargos=param[8], nivel=param[9], inscricoes_ate=param[10]) for param in params]
    Data.objects.bulk_create(products)

def moeda_real(valor):
  val = f"{valor:,.2f}"
  novo_valor = "R$ "+val.replace(".","*").replace(",",'.').replace("*", ",")
  return novo_valor