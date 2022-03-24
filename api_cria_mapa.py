#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
import re
import sys
from zabbix_api import ZabbixAPI

# verifica qual loja sera criado o mapa
Tipo = "Mapa"
loja = open('ct.txt')
LOJA = str(loja.readline())
LOJA = re.sub('\n', '', LOJA)

# faz a conexao com o zabbix
zapi = ZabbixAPI(server="http://10.131.0.30/zabbix")
zapi.login("USUARIO_API", "tenda123")

# espacamento entre colunas
espaco = [70]
for e in range(36):
    espaco.append(espaco[-1] + 55)

# espacamento entre linhas
linhas = [30, 125]
for i in range(40):
    linhas.append(linhas[-1] + 100)

srv = [30, "SRV" + "*" + LOJA + "*", 149]
net = [30, 'Internet_Status_CT' + LOJA, 3]
pdv = [linhas[0], "CT" + LOJA + "PDV", 353]
sat = [linhas[1], "CT" + LOJA + "SAT", 346]
posto = [linhas[1], "CT" + LOJA + "POS", 353]
bsp = [linhas[2], "CT" + LOJA + "BSP", 352]
lin = [linhas[3], "CT" + LOJA, 189]
som = [linhas[4], "CT" + LOJA + "SOM", 188]
carga = [linhas[4], "CT" + LOJA + "ADM", 188]
blc = [linhas[4], "CT" + LOJA + "BLC", 342]
imp = [linhas[5], "CT" + LOJA + "I", 196]
dvr = [605, "CT" + LOJA + "DVR", 195]
swi = [linhas[6], "CT" + LOJA + "-", 153]
acp = [linhas[7], "CT" + LOJA + "ACP", 123]
tip = [linhas[8], "CT" + LOJA + "TIP", 354]
rub = [linhas[9], "CT" + LOJA + "EDA", 350]
cam = [linhas[10], "CT" + LOJA + "CAM", 191]
crm = [linhas[11], "CT" + LOJA + "CRM", 348]
cac = [linhas[11], "CT" + LOJA + "CAC", 351]
alm = [linhas[11], "CT" + LOJA + "ALM", 349]

# logo no mapa
dados = {}
dados['selementid'] = 1
dados['elementtype'] = 4
dados['iconid_off'] = 193
dados['x'] = 600
dados['y'] = 20
json_tmp = []
json_tmp.append(dados)
cont = 0


# linha_atual = 0


def adiciona_mapa(nome, img, linha, cont):
    dados = {}  # dados recebidos da query no for
    info1 = {}  # recebe os ids do zabbix
    info = []  # recebe infos com os ids e adiciona

    linha_atual = linha

    itens = zapi.host.get({
        'output': ['host', 'name', 'status'],
        'search': {'host': '*' + nome + '*'},
        'searchWildcardsEnabled': True
    })
    if itens:
        print(f'{nome[4:]} encontrado!')
        for item in itens:
            if cont == 25:
                cont = 0
                linha_atual = linha_atual + 1

            dados['selementid'] = '1'
            dados['elementtype'] = 0
            dados['iconid_off'] = img
            dados['x'] = espaco[cont]
            dados['y'] = linhas[linha_atual]
            info1['hostid'] = item['hostid']
            info.append(info1)
            dados['elements'] = info
            cont = cont + 1
            json_tmp.append(dados)
            dados = {}
            element = {}
            info = []
            info1 = {}
    else:
        print(f'{nome[4:]} não encontrado')
    print(linha_atual)
    return linha_atual, cont, json_tmp

    # print(json_tmp)


json_final = []
var = adiciona_mapa(nome=srv[1], img=srv[2], linha=0, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=net[1], img=net[2], linha=0, cont=var[1] + 2)
json_final = var[2]

var = adiciona_mapa(nome=pdv[1], img=pdv[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=sat[1], img=sat[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=posto[1], img=posto[2],
                    linha=var[0], cont=var[1] + 1)
json_final = var[2]
var = adiciona_mapa(nome=bsp[1], img=bsp[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=blc[1], img=blc[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=som[1], img=som[2], linha=var[0], cont=var[1] + 1)
json_final = var[2]
var = adiciona_mapa(nome=carga[1], img=carga[2], linha=var[0], cont=var[1])
json_final = var[2]
var = adiciona_mapa(nome=imp[1], img=imp[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=dvr[1], img=dvr[2], linha=var[0], cont=var[1] + 2)
json_final = var[2]
var = adiciona_mapa(nome=alm[1], img=alm[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=cac[1], img=cac[2], linha=var[0], cont=var[1] + 2)
json_final = var[2]
var = adiciona_mapa(nome=crm[1], img=crm[2], linha=var[0], cont=var[1] + 2)
json_final = var[2]
var = adiciona_mapa(nome=swi[1], img=swi[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=acp[1], img=acp[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=tip[1], img=tip[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=rub[1], img=rub[2], linha=var[0] + 1, cont=0)
json_final = var[2]
var = adiciona_mapa(nome=cam[1], img=cam[2], linha=var[0] + 1, cont=0)
json_final = var[2]

json_mapa = {}
json_mapa = {"name": "Mapa_LOJA_CT" + LOJA,
             "width": 1450, "height": linhas[var[0]] + 60}
json_mapa['selements'] = json_final

# dados da loja
dados = {}
dados['text'] = "Tenda Atacado CT" + LOJA + " Monitoramento Zabbix"
dados['type'] = 0
dados['x'] = 725
dados['y'] = 20
dados['width'] = 300
dados['height'] = 80
dados['border_type'] = 0
dados['font'] = 9
dados['font_size'] = 25
dados['font_color'] = "FF0000"
json_shapes = []
json_shapes.append(dados)
json_mapa['shapes'] = json_shapes

# salva os dados em json
with open('resultado.json', 'w') as f:
    json.dump(json_mapa, f, indent=4)

# apaga o mapa se ja existir

mapas = zapi.map.get({
    "output": [
        "sysmapid",
        "name"
    ]
})
#
if mapas:
    for mapa in mapas:
        idmapa = mapa['sysmapid']
        nomemapa = mapa['name']
        if (nomemapa == "Mapa_LOJA_CT" + LOJA):
            zapi.map.delete([idmapa])
            print("Mapa " + nomemapa + " deletado!")

# # cria o mapa
mapa = zapi.map.create(json_mapa)
print("\n\n\nMapa Criado " + LOJA)

# capta o usuario
usuario = zapi.user.get({
    "output": "extend",
    "selectMedias": "extend",
    "filter": {
        "alias": "CT" + LOJA
    }
})
usuario_id = ''
for u in usuario:
    usuario_id = u['userid']
    usuario_media = u['medias']

# capta o id do mapa
mapas = zapi.map.get({
    "output": "extend",
})
if mapas:
    for mapa in mapas:
        # print(f'{mapa}\n\n')
        idmapa = mapa['sysmapid']
        nomemapa = mapa['name']

        if (nomemapa == "Mapa_LOJA_CT" + LOJA):
            pass
#print(mapa)

#print(usuario_id)

# troca o dono do mapa
updatemap = zapi.map.update({
    "sysmapid": idmapa,
    "userid": usuario_id,
})
print('Mapa trocado para o usuario CT' + LOJA)
