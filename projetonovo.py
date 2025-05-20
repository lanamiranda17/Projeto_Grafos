"""
PROJETO DE ALGORITMOS EM GRAFOS (GCC218)- Modelagem Logística com Grafos em Python

Alunas: Lana da Silva Miranda, Nina Tobias Novikoff da Cunha Ribeiro
___________________________________________________________________________________
"""

import csv
import pandas as pd
import os

# LEITURA DO ARQUIVO DE ENTRADA

def ler_entrada(arq_entrada):
    cabecalho = {}

    # Leitura do cabeçalho
    with open(arq_entrada, "r", encoding="utf-8") as arq:
        for _ in range(11):
            linha = arq.readline().strip()
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                cabecalho[chave.strip()] = valor.strip()

    N = int(cabecalho['#Nodes'])
    grafo = [[[] for _ in range(N + 1)] for _ in range(N + 1)]

    with open(arq_entrada, "r", encoding="utf-8") as arq:
        linhas = arq.readlines()[11:]

        tabela_atual = None

        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith("the data is"):
                continue

            # Detectar seção atual
            if linha.startswith("ReN."):
                tabela_atual = 'ReN'
                continue
            elif linha.startswith("ReE."):
                tabela_atual = 'ReE'
                continue
            elif linha.startswith("ReA."):
                tabela_atual = 'ReA'
                continue
            elif linha.startswith("EDGE"):
                tabela_atual = 'Edge'
                continue
            elif linha.startswith("ARC"):
                tabela_atual = 'Arc'
                continue

            partes = linha.split()
            try:
                if tabela_atual == 'ReE' and len(partes) == 6:
                    _, u, v, custo, demanda, servico = partes
                    u, v = int(u), int(v)
                    aresta = {
                        'tipo': 'aresta',
                        'obrigatoria': True,
                        'custo_transito': int(custo),
                        'demanda': int(demanda),
                        'custo_servico': int(servico)
                    }
                    grafo[u][v].append(aresta)
                    grafo[v][u].append(aresta)

                elif tabela_atual == 'Edge' and len(partes) == 4:
                    _, u, v, custo = partes
                    u, v = int(u), int(v)
                    aresta = {
                        'tipo': 'aresta',
                        'obrigatoria': False,
                        'custo_transito': int(custo)
                    }
                    grafo[u][v].append(aresta)
                    grafo[v][u].append(aresta)

                elif tabela_atual == 'ReA' and len(partes) == 6:
                    _, u, v, custo, demanda, servico = partes
                    u, v = int(u), int(v)
                    arco = {
                        'tipo': 'arco',
                        'obrigatoria': True,
                        'custo_transito': int(custo),
                        'demanda': int(demanda),
                        'custo_servico': int(servico)
                    }
                    grafo[u][v].append(arco)

                elif tabela_atual == 'Arc' and len(partes) == 4:
                    _, u, v, custo = partes
                    u, v = int(u), int(v)
                    arco = {
                        'tipo': 'arco',
                        'obrigatoria': False,
                        'custo_transito': int(custo)
                    }
                    grafo[u][v].append(arco)

                elif tabela_atual == 'ReN' and len(partes) == 3:
                    nome_no, demanda, servico = partes
                    noh = int(nome_no[1:])
                    grafo[noh][noh].append({
                        'tipo': 'noh',
                        'obrigatoria': True,
                        'demanda': int(demanda),
                        'custo_servico': int(servico)
                    })

            except Exception as e:
                print(f"⚠️ Erro ao processar linha da tabela {tabela_atual}: {linha}")
                print(f"   Detalhes: {e}")

    return cabecalho, grafo


#Funçoes auxiliares para armazenar 
def quant_vertices(cabecalho):
    return int(cabecalho.get('#Nodes', 0))

def quant_arestas(cabecalho):
    return int(cabecalho.get('#Edges', 0))

def quant_arcos(cabecalho):
    return int(cabecalho.get('#Arcs', 0))

def quant_vertices_requeridos(cabecalho):
    return int(cabecalho.get('#Required N', 0))

def quant_arestas_requeridas(cabecalho):
    return int(cabecalho.get('#Required E', 0))

def quant_arcos_requeridos(cabecalho):
    return int(cabecalho.get('#Required A', 0))

def capacidade_veiculo(cabecalho):
    return int(cabecalho.get('Capacity', 0))

def deposito(cabecalho):
    return int(cabecalho.get('Depot Node', 0))


def densidade_grafo (cabecalho):
    N = int(cabecalho['#Nodes'])
    E = int(cabecalho['#Edges'])
    A = int(cabecalho['#Arcs'])

    return (E + A)/((N * (N-1))/2)

def graus_nohs (grafo, cabecalho):
    quant_nohs = int(cabecalho['#Nodes'])
    grau_total = [0] * (quant_nohs +1) # Ignorar indice 0 pra facilitar
    grau_entrada = [0] * (quant_nohs +1)
    grau_saida = [0] * (quant_nohs +1)

    for i in range (1,len(grafo)):
        for j in range (1, len(grafo[i])):
            celula = grafo[i][j]

            if not celula == None:
                for conexao in celula:
                    tipo = conexao ['tipo']
                
                    if tipo == 'aresta':
                        if i < j:  # Só processa uma vez para evitar contagem duplicada
                            grau_total[i] += 1
                            grau_total[j] += 1

                    elif tipo == 'arco':
                        grau_entrada [j] += 1
                        grau_saida [i] += 1
                        grau_total[i] += 1 # porque grau_total += grau_entrada + grau_saida
                        grau_total[j] += 1

    return grau_total, grau_entrada, grau_saida

def grau_maximo (grau_total, grau_entrada, grau_saida):
    # Ignora o índice 0
    grau_total_max = max (grau_total[1:])
    grau_entrada_max = max (grau_entrada[1:])
    grau_saida_max = max (grau_saida[1:])

    return grau_total_max, grau_entrada_max, grau_saida_max

def grau_minimo(grau_total, grau_entrada, grau_saida):

    grau_total_min = min(grau_total[1:])
    grau_entrada_min = min(grau_entrada[1:])
    grau_saida_min = min(grau_saida[1:])
    
    return grau_total_min, grau_entrada_min, grau_saida_min

def floyd_warshall(grafo, cabecalho):
    n = int(cabecalho['#Nodes'])
    INF = float('inf') #infinito para inicializar as distâncias entre vértices que ainda não têm ligação direta

    dist = [[INF] * (n+1) for _ in range(n+1)] # Matriz de distâncias
    pred = [[None] * (n+1) for _ in range(n+1)] # Matriz de predecessores

    
    for i in range(1, n+1):
        dist[i][i] = 0 # Distância de cada nó a ele mesmo é 0
        pred[i][i] = i

        for j in range(1, n+1):

            celula = grafo[i][j]
            if celula: # Se não for vazia ou nula

                for conexao in celula:
                    tipo = conexao['tipo']

                    if tipo == 'aresta' or tipo == 'arco':
                        custo = conexao['custo_transito']

                        if tipo == 'aresta' and i < j: # Para evitar duplicação
                            dist[i][j] = min(dist[i][j], custo)
                            dist[j][i] = min(dist[j][i], custo)
                            pred[i][j] = i
                            pred[j][i] = j

                        elif tipo == 'arco':
                            dist[i][j] = min(dist[i][j], custo)
                            pred[i][j] = i

    # Algoritmo principal
    for k in range(1, n+1):
        for i in range(1, n+1):
            for j in range(1, n+1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]

    return dist, pred

def reconstruir_caminho(pred, i, j):
    if pred[i][j] is None:
        return []
    
    caminho = [j]
    while i != j:
        j = pred[i][j]
        caminho.append(j)

    caminho.reverse()
    return caminho

def calculo_intermediacao (grafo, cabecalho):
    n = int(cabecalho['#Nodes'])
    _, pred = floyd_warshall(grafo, cabecalho)

    intermediacao = [0] * (n + 1)  # índice 0 ignorado

    for s in range(1, n + 1):
        for t in range(1, n + 1):
            if s != t:
                caminho = reconstruir_caminho(pred, s, t)
                for v in caminho[1:-1]:  # ignora origem e destino
                    intermediacao[v] += 1

    return intermediacao

def caminho_medio(grafo, cabecalho):
    dist, _ = floyd_warshall(grafo, cabecalho)
    n = int(cabecalho['#Nodes'])
    
    soma = 0
    contagem = 0
    
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j and dist[i][j] != float('inf'):
                soma += dist[i][j]
                contagem += 1

    if contagem == 0:
        return 0  
    
    return soma / contagem

def diametro_grafo(grafo, cabecalho):
    dist, _ = floyd_warshall(grafo, cabecalho)
    n = int(cabecalho['#Nodes'])
    
    max_dist = 0
    
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j and dist[i][j] != float('inf'):
                if dist[i][j] > max_dist:
                    max_dist = dist[i][j]

    return max_dist


# Impressão das matrizes
def imprimir_matriz(matriz, usar_inf=False):

    INF = float('inf')
    for linha in matriz:
        for valor in linha:
            if usar_inf and valor == INF:
                print("INF".ljust(5), end=" ")
            else:
                print(str(valor).ljust(5), end=" ")
        print()

# Implementaçao do CARP
def extrair_obrigatorios(grafo, cabecalho):
    servicos = [];

    N = quant_vertices(cabecalho)
    for i in range(1, N+1):
        for j in range(1, N+1):
            celula = grafo[i][j]
            if celula: 
                for conexao in celula: 
                    if conexao.get('obrigatoria', False):
                        custo_total = conexao.get('custo_transito', 0) + conexao.get('custo_servico', 0)
                        if conexao['tipo'] == 'aresta':

                            servicos.append({
                                'origem' : i,
                                'destino' : j,
                                'demanda' : conexao.get('demanda', 0),
                                'custo_total' : custo_total,
                                'tipo' : 'aresta'
                            })
                            servicos.append({
                                'origem' : j,
                                'destino' : i,
                                'demanda' : conexao.get('demanda', 0),
                                'custo_total' : custo_total,
                                'tipo' : 'aresta'
                            })

                        elif conexao['tipo'] == 'arco':
                            servicos.append({
                                'origem' : i,
                                'destino' : j,
                                'demanda' : conexao.get('demanda', 0),
                                'custo_total' : custo_total,
                                'tipo' : 'arco'
                            })
                        
    return servicos 

# Matriz menores caminhos dentre os obrigatorios 

def matriz_obrigatorios(servicos, distancias):
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

# Clarke wright

def clarke_wright(servicos, matriz_custos, capacidade):
    n = len(servicos)

    # Inicializa uma rota para cada serviço (cada rota começa e termina no depósito)
    rotas = [{'servicos': [i], 'carga': servicos[i]['demanda'], 'inicio': i, 'fim': i} for i in range(n)]

    # Calcula economias para todas as combinações possíveis entre serviços
    economias = []
    for i in range(n):
        for j in range(n):
            if i != j:
                economia = (matriz_custos[0][i] + matriz_custos[0][j] - matriz_custos[i][j])
                economias.append((economia, i, j))

    # Ordena as economias em ordem decrescente
    economias.sort(reverse=True, key=lambda x: x[0])

    # União das rotas
    for economia, i, j in economias:
        rota_i = next((r for r in rotas if r['fim'] == i), None)
        rota_j = next((r for r in rotas if r['inicio'] == j), None)

        if rota_i is None or rota_j is None or rota_i == rota_j:
            continue

        # Verifica capacidade para unir as rotas
        if rota_i['carga'] + rota_j['carga'] <= capacidade:
            # Une rotas concatenando
            rota_i['servicos'].extend(rota_j['servicos'])
            rota_i['fim'] = rota_j['fim']
            rota_i['carga'] += rota_j['carga']

            rotas.remove(rota_j)

    return rotas

# Custo total da rota

def custo_rota(rota, matriz_custos):
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



def exportar_csv(cabecalho, grafo):

    grau_total, grau_entrada, grau_saida = graus_nohs (grafo, cabecalho)

    grau_total_max, grau_entrada_max, grau_saida_max = grau_maximo (grau_total, grau_entrada, grau_saida)
    grau_total_min, grau_entrada_min, grau_saida_min = grau_minimo (grau_total, grau_entrada, grau_saida)

    with open("estatisticas.csv", "w", encoding="utf-8") as arq:
        arq.write(f"Estatísticas,Valor\n")
        arq.write(f"Quantidade de vértices:,{int(cabecalho['#Nodes'])}\n")
        arq.write(f"Quantidade de arestas:,{int(cabecalho['#Edges'])}\n")
        arq.write(f"Quantidade de arcos:,{int(cabecalho['#Arcs'])}\n")
        arq.write(f"Quantidade de vértices requeridos:,{int(cabecalho['#Required N'])}\n")
        arq.write(f"Quantidade de arestas requeridas:,{int(cabecalho['#Required E'])}\n")
        arq.write(f"Quantidade de arcos requeridos:,{int(cabecalho['#Required A'])}\n")
        arq.write(f"Densidade do grafo:,{densidade_grafo(cabecalho)}\n")
        arq.write(f"Grau total máximo:,{grau_total_max}\n")
        arq.write(f"Grau de entrada máximo:,{grau_entrada_max}\n")
        arq.write(f"Grau de sída máximo:,{grau_saida_max}\n")
        arq.write(f"Grau total mínimo:,{grau_total_min}\n")
        arq.write(f"Grau de entrada mínimo:,{grau_entrada_min}\n")
        arq.write(f"Grau de saída mínmo:,{grau_saida_min}\n")


def visualizar_estatisticas():
       
    df = pd.read_csv("estatisticas.csv") # criação do data frame

    def format_value(x): 
        return f"{int(x)}" if x == int(x) else f"{x}" # Exibe como inteiro se não houver parte decimal

    styled_df = ( 
        df.style
        .format({"Valor": format_value})
        .set_caption("ESTÁTISTICAS BÁSICAS DO GRAFO:")
        .hide(axis="index")
    )
    return styled_df

# Imprimir no formato correto 

def imprimir_rotas(rotas, servicos, custo_total, matriz_custos):
    print(int(custo_total))
    print(len(rotas))
    
    for idx, rota in enumerate(rotas, 1):
        carga_total = sum([servicos[i]['demanda'] for i in set(rota['servicos'])])
        servicos_na_rota = rota['servicos']

        custo_rota_valor = custo_rota(rota, matriz_custos)
        print(f"0 1 {idx} {carga_total} {int(custo_rota_valor)} {len(servicos_na_rota) + 2}")

        print("(D 0,1,1)", end=" ")
        for i in servicos_na_rota:
            s = servicos[i]
            print(f"(S {i+1},{s['origem']},{s['destino']})", end=" ")
        print("(D 0,1,1)")


def verificar_factibilidade(rotas, servicos, capacidade):
    print("=== Verificação da Solução ===")
    
    demanda_total_servicos = sum(s['demanda'] for s in servicos)
    demanda_total_rotas = 0
    
    for idx, rota in enumerate(rotas, 1):
        carga = sum(servicos[i]['demanda'] for i in set(rota['servicos']))
        demanda_total_rotas += carga
        status = "OK" if carga <= capacidade else "EXCEDE"
        print(f"Rota {idx}: Carga = {carga} / Capacidade = {capacidade} -> {status}")
    
    print(f"Demanda total dos serviços: {demanda_total_servicos}")
    print(f"Demanda total nas rotas: {demanda_total_rotas}")
    
    if demanda_total_rotas == demanda_total_servicos:
        print("Todos os serviços foram atendidos exatamente uma vez.")
    else:
        print("ATENÇÃO: Diferença entre demanda total dos serviços e das rotas!")


def salvar_rotas_em_arquivo(nome_saida, rotas, servicos, custo_total, matriz_custos):
    with open(nome_saida, "w", encoding="utf-8") as f:
        f.write(f"{int(custo_total)}\n")
        f.write(f"{len(rotas)}\n")
        f.write("0\n0\n")  # clocks simulados

        for idx, rota in enumerate(rotas, 1):
            carga_total = sum([servicos[i]['demanda'] for i in set(rota['servicos'])])
            custo_rota_valor = custo_rota(rota, matriz_custos)
            f.write(f"0 1 {idx} {carga_total} {int(custo_rota_valor)} {len(rota['servicos']) + 2}\n")
            f.write("(D 0,1,1) ")
            for i in rota['servicos']:
                s = servicos[i]
                f.write(f"(S {i+1},{s['origem']},{s['destino']}) ")
            f.write("(D 0,1,1)\n")

def processar_instancia(arquivo_entrada, pasta_saida):
    nome_base = os.path.basename(arquivo_entrada).replace(".dat", "")
    cabecalho, grafo = ler_entrada(arquivo_entrada)
    dist, _ = floyd_warshall(grafo, cabecalho)
    servicos = extrair_obrigatorios(grafo, cabecalho)
    matriz_custos = matriz_obrigatorios(servicos, dist)
    capacidade = capacidade_veiculo(cabecalho)

    rotas = clarke_wright(servicos, matriz_custos, capacidade)
    custo = sum(custo_rota(rota, matriz_custos) for rota in rotas)

    nome_saida = os.path.join(pasta_saida, f"sol-{nome_base}.dat")
    salvar_rotas_em_arquivo(nome_saida, rotas, servicos, custo, matriz_custos)

def processar_todos():
    pasta_entrada = "instancias/"
    pasta_saida = "solucoes/"
    os.makedirs(pasta_saida, exist_ok=True)

    arquivos = [f for f in os.listdir(pasta_entrada) if f.endswith(".dat")]

    for arq in arquivos:
        caminho = os.path.join(pasta_entrada, arq)
        print(f"Processando {arq}...")
        processar_instancia(caminho, pasta_saida)

