import platform
import subprocess
import sys
import iperf3
import os
import psutil
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from svglib.svglib import svg2rlg
from datetime import datetime
import time


# IP DO SERVIDOR - CASO INSERIDO MAIS ALGUM 
# O MESMO DEVE SER ALTERADO INCLUSIVE NO WHILE DA LINHA 97

IPSERVER = '52.23.185.119'

def teste_rede(host):
    client = iperf3.Client()
    client.duration = 5
    client.server_hostname = host
    client.port = 5201
    client.protocol = 'udp'
    client.blksize = 1408

    result = client.run()

    if result.error:
        return ("error","error","error","error")
    else:
        return (result.jitter_ms, result.Mbps, result.lost_packets, result.packets)

def latencia_media(host):
    try:
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, '5', host]
        r = subprocess.check_output(command).decode("utf-8")
        l = r.split('\n')[9]
        return float(l.split('/')[4])
    except:
        print("Foi mal Hermanoteu, deu pau do Excel!!!")

def dados_machine():
    so = platform.system()
    return (platform.platform(), psutil.cpu_percent(interval=None), psutil.virtual_memory().percent, psutil.virtual_memory().total)

def gerarBytesIMG(lista, eixo_y):
    figura = plt.figure(figsize=(3,2))
    plt.rcParams.update({'font.size':8})
    plt.plot(lista)
    plt.ylabel(eixo_y)
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    imgdata = BytesIO()
    figura.savefig(imgdata, format='svg')
    imgdata.seek(0)
    return svg2rlg(imgdata)

def calcula_perdas_totais(p ,pl):
    resultado = []
    pt = 0
    plt = 0
    qtd = len(p)
    for i in range(qtd):
        resultado.append(100*pl[i]/p[i])
        pt = pt + p[i]
        plt = plt + pl[i]

    return (resultado, pt, plt)

if __name__ == '__main__':
    texto = ["CHECANDO CABOS DO PROVEDOR", \
    "VISH É FIBRA, ESTAVAMOS COM O EQUIPAMENTO ERRADO", \
    "AGORA SIM EQUIPAMENTO CERTO", \
    "BUSCANDO ROTA SUBMARINA", \
    "ASSUSTANDO TUBARÕES PARA NÃO MORDEREM O FIO", \
    "PROCURANDO GREMLINS NO CAMINHO", \
    "UM GREMLIN ENCONTRADO", \
    "MENOS UM GREMLIN NO MUNDO", \
    "RETORNANDO PACOTES", \
    "ESPERANDO A LIBERAÇÃO DA ALFANDEGA", \
    "SAINDO DE CURITIBA", \
    "CAMINHO DE VOTLTA"]  

    jitter = []
    tx_transmissao = []
    perda_dp = []
    packets = []
    latencia = []
    iterador = 0
    testador = 0
    qtd_testes = 0

    while(1):
        print ("Escolha um servidor pada teste")
        print ("1 - Virginia/EUA [ativo]")
        print ("2 - só tem ele")
        s = input("Servidor: ")
        if (s == '1'):
            break
        else:
            print("opção inválida")
            continue

    while(1):
        qtd_testes = int(input("Informe a quantidade de repetições. Entre 3 e 10: \n"))
        if (3 <= qtd_testes <= 10):
            break
        else:
            print("Quantidade Inválida")
    inicio = time.time()

    for i in range(qtd_testes):
        print("\n" * 130)
        print(texto[iterador])
        if (iterador >= 11):
            iterador = 0
        else:
            iterador += 1

        (jit, mb, pl, p) = teste_rede(IPSERVER)
        if (jit == "error"):
            testador = 1
            break
        jitter.append(jit)
        tx_transmissao.append(mb)
        perda_dp.append(pl)
        packets.append(p)
        print("\n" * 130)
        print(texto[iterador])

        if (iterador >= 11):
            iterador = 0
        else:
            iterador += 1
        latencia.append(latencia_media(IPSERVER))
    if (testador == 1):
        print("Foi mal Hermanoteu, deu pau no Excel") 
        exit()

    print("\n" * 130)
    print("FIM, NEM DEMOROU TANTO")
    fim = time.time()
    tempo = (fim - inicio)
    pdf = canvas.Canvas('benchmark_de_rede.pdf', pagesize=A4)
    pdf.setTitle("BENCHMARK DE REDE")
    pdf.setFont("Helvetica-Oblique", 14)
    pdf.drawString(40,800, "Benchmark de Rede")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40,780, "SERVIDOR: IP - {0} / LOCALIZAÇÃO: Virginia/EUA".format(IPSERVER))
    (maquina, cpu, mem, mem_total) = dados_machine()
    pdf.drawString(40,760, "MAQUINA USUÁRIO: {0}".format(maquina))
    pdf.drawString(40,740, "USO DA CPU: {0}% - USO DA MEMÓRIA: {1}% de {2} Bytes ".format(cpu,mem,mem_total))
    pdf.drawString(40,720, "DATA E HORA: {0} - TEMPO DECORRIDO: {1} s".format(datetime.now(), tempo))
    pdf.setFont("Helvetica-Oblique", 14)
    pdf.drawString(40,690, "TESTES NA REDE")
    
    renderPDF.draw(gerarBytesIMG(latencia, "Latência (ms)"), pdf, 40, 490)
    renderPDF.draw(gerarBytesIMG(jitter, "Jitter (ms)"), pdf, 320, 490)
    renderPDF.draw(gerarBytesIMG(tx_transmissao, "Taxa de Transmissão (Mbps)"), pdf, 40, 290)
    (perdaPercent, pacotesTotal, perdaTotal) = calcula_perdas_totais(packets, perda_dp)
    renderPDF.draw(gerarBytesIMG(perdaPercent, "Taxa de Perda de Pacotes (%)"), pdf, 320, 290)
    
    pdf.setFont("Helvetica",10)
    pdf.drawString(40, 270, "Total de pacotes trocados: {0}".format(pacotesTotal))
    pdf.save()

    print("Arquivo gerado com sucesso: benchmark_de_rede.pdf")

