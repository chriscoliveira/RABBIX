from datetime import datetime
import readline
from unicodedata import numeric
import sys
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import csv
import re
from zabbix_api import ZabbixAPI
import os


app = QApplication([])
window = uic.loadUi('layout.ui')
window.setWindowTitle('Cadastro no Zabbix por API - @chriscoliveira')

# faz a conexão com o zabbix
with open('config.cfg', 'r') as arquivo:
    zabbix_server, zabbix_user, zabbix_pass = '', '', ''
    linhas = arquivo.readlines()
    for linha in linhas:
        if 'server' in linha:
            zabbix_server = linha.split('=')[1].strip()
        if 'user' in linha:
            zabbix_user = linha.split('=')[1].strip()
        if 'pass' in linha:
            zabbix_pass = linha.split('=')[1].strip()
    zapi = ZabbixAPI(server=zabbix_server)
    zapi.login(zabbix_user, zabbix_pass)


def le_grupos_cfg():
    GRUPOID = []
    with open('names_groups_templates.cfg', 'r') as arquivo:
        linhas = arquivo.readlines()

        for linha in linhas:
            if not linha.startswith('#'):
                nome, grupo, template = linha.split(',')
                nome = nome.replace(' ', '').upper()
                grupo = grupo.replace(' ', '').upper()
                template = template.replace('\n', '').replace(' ', '').upper()
                GRUPOID.append([nome, grupo, template])
    return GRUPOID


def get_grupo_template(nome_grupo_host):
    with open('names_groups_templates.cfg', 'r') as arquivo:
        linhas = arquivo.readlines()
        GRUPOID = []
        for linha in linhas:
            if not linha.startswith('#'):
                nome, grupo, template = linha.split(',')
                nome = nome.replace(' ', '').upper()
                grupo = grupo.replace(' ', '').upper()
                template = template.replace('\n', '').replace(' ', '').upper()
                if nome_grupo_host in linha:
                    GRUPOID.append([nome, grupo, template])

    for x in GRUPOID:
        if nome_grupo_host == x[0]:
            return x[1], x[2]


def abrir_csv():
    caminho, _ = QFileDialog.getOpenFileName(
        window.centralwidget,
        'Abrir imagem',
        os.getcwd(),
        options=QFileDialog.DontUseNativeDialog
    )
    return caminho


def get_grupo_loja(loja):
    ct = ''
    if loja:
        grupo_loja = zapi.hostgroup.get({
            'output': 'extend',
            'search': {
                'name': loja
            },
            'sortfield': 'name',
            'sortorder': 'ASC'
        })
        for x in grupo_loja:
            ct = x['groupid']
            print(x['groupid'])
            return x['groupid']


def mapa_zabbix():
    loja = window.ed_ct.text().upper().replace('CT', '')
    if loja:
        with open('ct.txt', 'w') as f:
            f.write(loja)
        os.system('python3 api_cria_mapa.py')
    else:
        QMessageBox.about(
            window, 'Erro', 'Precisa informar o numero da filial')


def getnametemplates(pesquisa=False):
    # zapi = ZabbixAPI(server="http://10.131.0.30/zabbix")
    # zapi.login("USUARIO_API", "tenda123")
    if pesquisa:
        itens = zapi.template.get({
            'output': 'extend',
            'sortfield': 'name',
            'sortorder': 'ASC'
        })

    msg = 'Exibe os templates do zabbix'
    with open('envioTelegram.txt', 'w') as arquivo:
        arquivo.write(f'\n{msg}\n')

        for item in itens:
            if item['templateid'] == pesquisa:
                return item['host']


def getnameGrupo(pesquisa=False):
    # zapi = ZabbixAPI(server="http://10.131.0.30/zabbix")
    # zapi.login("USUARIO_API", "tenda123")
    if pesquisa:
        hosts = zapi.hostgroup.get({
            'output': 'extend',
            'sortfield': 'name',
            'sortorder': 'ASC'
        })

    for host in hosts:
        if host['groupid'] == pesquisa:
            print(host['name'])
            return host['name']


def cadastra_zabbix():
    # coleta os dados para cadastro
    fcsv = abrir_csv()
    grupo = window.ed_ct.text().upper().replace('CT', '')
    GrupoIDLoja = get_grupo_loja(grupo)
    GrupoIDGrupo, TemplateID = get_grupo_template(
        window.comboBox.currentText())

    # verifica se os dados foram preenchidos
    if fcsv and GrupoIDLoja and GrupoIDGrupo and TemplateID and grupo:
        print(fcsv, GrupoIDLoja, GrupoIDGrupo, TemplateID, sep='\n')
        retorno = QMessageBox.question(
            window, 'MUITA ATENÇÃO!!!', f"Tem certeza que deseja cadastrar os itens??\n\nArquivo CSV:{fcsv}\nLoja {getnameGrupo(GrupoIDLoja)}\nGrupo Host: {getnameGrupo(GrupoIDGrupo)}\nTemplate: {getnametemplates(pesquisa=TemplateID)}", QMessageBox.Yes | QMessageBox.No)

        # se o usuario confirmar o cadastro
        if retorno == QMessageBox.Yes:
            itemadd = []
            print(f'arquivo csv {fcsv}')
            itemADD = open(f'{fcsv}')

            # verifica o delimitador do arquivo
            sniffer = csv.Sniffer()
            with open(fcsv) as fp:
                delimiter = sniffer.sniff(fp.read(5000)).delimiter

            # abre a planilha
            listas = csv.reader(itemADD, delimiter=delimiter)

            itemadd1 = []
            itemadd = []
            for lista in listas:
                try:
                    itemadd1 = lista[0], lista[1], lista[2]
                    itemadd.append(itemadd1)
                except Exception as e:
                    pass
            print(itemadd)

            # inicia o cadastro no zabbix
            contador = 0
            for x in itemadd:
                nome = x[0]
                iP = x[1]
                descricao = x[2]
                print(
                    f'NOME {nome.upper()}, IP {iP.upper()}, DESC {descricao.upper()}')
                try:
                    hostcriado = zapi.host.create({
                        "host": nome.upper(),
                        "status": 0,
                        "description": descricao.upper(),
                        "interfaces": [
                            {
                                "type": 1,
                                "main": 1,
                                "useip": 1,
                                "ip": iP,
                                "dns": "",
                                "port": "10050"
                            },
                            {
                                "type": 2,
                                "main": 1,
                                "useip": 1,
                                "ip": iP,
                                "dns": "",
                                "port": "161",
                                "details": {
                                    "version": 3,
                                    "bulk": 0,
                                    "contextname": "",
                                    "securitylevel": 1}
                            }
                        ],
                        "groups": [
                            {
                                "groupid": GrupoIDLoja
                            },
                            {
                                "groupid": GrupoIDGrupo
                            }
                        ],
                        "templates": [
                            {
                                "templateid": TemplateID
                            }
                        ]
                    })

                    contador = contador + 1
                    print(nome + " criado! id:" + hostcriado["hostids"][0])
                except Exception as e:
                    print(f'\n\nErro ao cadastrar o host.\n\n{e}')
                print("\nTotal de itens cadastrados:" + str(contador))

            # cadastro finalizado
            QMessageBox.about(window, 'Importação',
                              f'Foram Cadastrados {contador} itens')

    # caso falte algum campo exibe mensagem de erro
    else:
        QMessageBox.about(window, 'Importação',
                          f'Para cadastrar os itens é necessário preencher todos os campos')


def testecsv():
    fcsv = r'/Scripts/RABBIX/teste.csv'
    itemadd = []
    print(f'arquivo csv {fcsv}')
    itemADD = open(f'{fcsv}')

    # verifica o delimitador do arquivo
    sniffer = csv.Sniffer()
    with open(fcsv) as fp:
        delimiter = sniffer.sniff(fp.read(5000)).delimiter

    # abre a planilha
    listas = csv.reader(itemADD, delimiter=delimiter)

    itemadd1 = []
    itemadd = []
    for lista in listas:
        try:
            itemadd1 = lista[0], lista[1], lista[2]
            itemadd.append(itemadd1)
        except Exception as e:
            pass
    print(itemadd)


def carregaCombo():
    lista = le_grupos_cfg()
    listagem = []
    for item in lista:
        listagem.append(item[0])
    window.comboBox.addItems(listagem)


carregaCombo()
window.bt_enviar.clicked.connect(cadastra_zabbix)
window.bt_mapa.clicked.connect(mapa_zabbix)
# window.bt_mapa.clicked.connect(testecsv)
window.show()
app.exec()
