import itertools
import random

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
                # Penalização adaptativa para fusões de rotas com grande diferença de carga
                if abs(servicos[i]['demanda'] - servicos[j]['demanda']) > 50:
                    economia *= 0.5  # Penaliza fusões de rotas muito desbalanceadas
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
            # União das rotas
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

def aplicar_3opt(rota, matriz_custos):
    servicos = rota['servicos']
    n = len(servicos)
    melhor_custo = custo_rota(rota, matriz_custos)
    melhor_seq = servicos[:]
    if n < 4:
        return rota  # 3-opt só faz sentido para rotas com pelo menos 4 serviços
    for i, j, k in itertools.combinations(range(1, n), 3):
        # Gera as 7 possíveis reconexões do 3-opt
        partes = [servicos[:i], servicos[i:j], servicos[j:k], servicos[k:]]
        opcoes = [  # cada opção é uma nova sequência
            partes[0] + partes[1][::-1] + partes[2] + partes[3],
            partes[0] + partes[1] + partes[2][::-1] + partes[3],
            partes[0] + partes[2] + partes[1] + partes[3],
            partes[0] + partes[2][::-1] + partes[1][::-1] + partes[3],
            partes[0] + partes[2] + partes[1][::-1] + partes[3],
            partes[0] + partes[1][::-1] + partes[2][::-1] + partes[3],
            partes[0] + partes[2][::-1] + partes[1] + partes[3],
        ]
        for nova_seq in opcoes:
            nova_rota = {'servicos': nova_seq}
            novo_custo = custo_rota(nova_rota, matriz_custos)
            if novo_custo < melhor_custo:
                melhor_custo = novo_custo
                melhor_seq = nova_seq[:]
    rota['servicos'] = melhor_seq
    return rota

def refinar_rotas_por_3opt(rotas, servicos, matriz_custos, capacidade):
    novas_rotas = []
    for rota in rotas:
        nova_rota = aplicar_3opt(rota, matriz_custos)
        nova_rota['carga'] = sum(servicos[s]['demanda'] for s in nova_rota['servicos'])
        novas_rotas.append(nova_rota)
    return novas_rotas

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


def grasp_simples(servicos, matriz_custos, capacidade, iteracoes=6):
    # GRASP leve com randomização de savings + realocação.
    
    melhor_solucao = None
    melhor_custo = float('inf')

    for _ in range(iteracoes):
        embaralhado = random.sample(servicos, len(servicos))
        rotas = clarke_wright_otimizado(embaralhado, matriz_custos, capacidade)
        rotas = refinar_rotas_por_realocacao(rotas, servicos, matriz_custos, capacidade)
        custo = sum(custo_rota(r, matriz_custos) for r in rotas)

        if custo < melhor_custo:
            melhor_custo = custo
            melhor_solucao = rotas

    return melhor_solucao


def refinar_condicional(rotas, servicos, matriz_custos, capacidade, nome_instancia):
    """
    Refinamento adaptativo por tamanho da instância:
    - Pequena: 3-opt + realocação
    - Média: realocação apenas
    - Grande: sem refinamento pesado
    """
    num_servicos = len(servicos)

    if num_servicos <= 100:
        rotas = refinar_rotas_por_realocacao(rotas, servicos, matriz_custos, capacidade)
        rotas = refinar_rotas_por_3opt(rotas, servicos, matriz_custos, capacidade)
    elif num_servicos <= 300:
        rotas = refinar_rotas_por_realocacao(rotas, servicos, matriz_custos, capacidade)
    else:
        pass  # sem refinamento pesado

    return rotas
