import csv
import pandas as pd
import os
import time

from leitura_escrita import *
from estatisticas import *


# Implementaçao do CARP

# Matriz menores caminhos dentre os obrigatorios 
def matriz_obrigatorios(servicos, distancias):
    # Cria uma matriz de custos entre os serviços, somando deslocamento e custo do serviço destino

    n = len(servicos)
    matriz_custos = [[float('inf')]* n for _ in range(n)]

    for i in range(n): 
        for j in range(n):
            if i == j:
                matriz_custos[i][j] = 0 
                continue

            origemJ = servicos[j]['origem']
            destinoI = servicos[i]['destino']

            deslocamento = distancias[destinoI][origemJ]

            custo_servicoJ = servicos[j]['custo_total']

            matriz_custos[i][j] = deslocamento + custo_servicoJ

    return matriz_custos

# Otimizacao da heuristica Clarke e Wright
def clarke_wright_otimizado(servicos, matriz_custos, capacidade):
    n = len(servicos)

    # Inicializa uma rota para cada serviço (cada rota começa e termina no depósito)
    rotas = [{'servicos': [i], 'carga': servicos[i]['demanda'], 'inicio': i, 'fim': i} for i in range(n)]

    # Calcula economias para todas as combinações possíveis entre serviços
    economias = []
    for i in range(n):
        for j in range(n):
            if i != j:
                economia = matriz_custos[0][i] + matriz_custos[0][j] - matriz_custos[i][j]
                economias.append((economia, i, j))
    
    # Ordena as economias em ordem decrescente
    economias.sort(reverse=True)

    # União das rotas
    for economia, i, j in economias:
        rota_i = next((r for r in rotas if r['fim'] == i), None)
        rota_j = next((r for r in rotas if r['inicio'] == j), None)

        if rota_i is None or rota_j is None or rota_i == rota_j:
            continue

        nova_carga = rota_i['carga'] + rota_j['carga']
        if nova_carga <= capacidade:

            # Penalização para evitar rotas ruins
            if economia < 0 and len(rota_i['servicos']) + len(rota_j['servicos']) <= 3:
                continue

            # Une rotas
            rota_i['servicos'].extend(rota_j['servicos'])
            rota_i['fim'] = rota_j['fim']
            rota_i['carga'] = nova_carga
            rotas.remove(rota_j)

    return rotas

# Refinamento das rotas por realocação de serviços
def refinar_rotas_por_realocacao(rotas, servicos, matriz_custos, capacidade):
    # Ordena as rotas pelo custo total (do mais caro para o mais barato)
    rotas.sort(key=lambda r: custo_rota(r, matriz_custos), reverse=True)

    i = 0
    iteracoes = 0
    max_iteracoes = 200  # Limite de 200 iterações

    while i < len(rotas) and iteracoes < max_iteracoes:
        rota_atual = rotas[i]
        realocado = False

        for serv_id in rota_atual['servicos']:
            servico = servicos[serv_id]

            for j in range(len(rotas)):
                if i == j:
                    continue

                destino = rotas[j]
                nova_carga = destino['carga'] + servico['demanda']

                if nova_carga > capacidade:
                    continue

                # Simula custo atual e com a realocação
                custo_antigo = custo_rota(destino, matriz_custos)
                destino_simulada = destino['servicos'] + [serv_id]
                destino_simulada.sort()
                destino_tmp = {'servicos': destino_simulada}
                custo_novo = custo_rota(destino_tmp, matriz_custos)

                # Realoca apenas se o custo diminuir significativamente
                if custo_novo < custo_antigo + matriz_custos[0][serv_id] + matriz_custos[serv_id][0]:
                    # Realoca
                    destino['servicos'].append(serv_id)
                    destino['carga'] = nova_carga
                    realocado = True
                    break

            if realocado:
                break

        if realocado:
            rotas.pop(i)
        else:
            i += 1
        iteracoes += 1

    return rotas

# Custo total da rota
def custo_rota(rota, matriz_custos):
    # Soma os custos de ida, entre serviços, e volta ao depósito

    servicos = rota['servicos']
    custo = 0

    # Custo ida do depósito (índice 0) até o primeiro serviço
    custo += matriz_custos[0][servicos[0]]

    # Custo entre serviços consecutivos
    for i in range(len(servicos) - 1):
        custo += matriz_custos[servicos[i]][servicos[i + 1]]

    # Custo retorno do último serviço até o depósito
    custo += matriz_custos[servicos[-1]][0]

    return custo