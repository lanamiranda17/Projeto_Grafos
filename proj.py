"""
PROJETO DE ALGORITMOS EM GRAFOS (GCC218)- Modelagem Logística com Grafos em Python

Alunas: Lana da Silva Miranda, Nina Tobias Novikoff da Cunha Ribeiro
___________________________________________________________________________________
"""
import pandas as pd 

# LEITURA DO ARQUIVO DE ENTRADA
def ler_entrada(arq_entrada):

    # Dicionário para armazenar os dados do cabeçalho
    cabecalho = {}

    # Leitura do cabeçalho
    with open(arq_entrada, "r", encoding="utf-8") as arq:       # "r" modo de leitura (read)
        
        for _ in range(11):                                     # Já que todo cabeçalho tem 11 linhas
            linha = arq.readline().strip()                      # Strip pra remover espaços em branco e readline para ler a linha toda
            
            if ":" in linha:
                    chave, valor = linha.split(":", 1)          # split divide a linha uma vez em relação ao ":"
                    cabecalho[chave.strip()] = valor.strip()    # armazena no dicionário as duas partes da linha

    # print (cabecalho) # Para depuração

    # CRIANDO O GRAFO
    N = int (cabecalho['#Nodes'])
    grafo = [[[] for _ in range(N + 1)] for _ in range(N + 1)]    # Ignorar o indice 0 e inicializa com uma lista vazia

    # Continuar a leitura a partir da linha 12
    with open(arq_entrada, "r", encoding="utf-8") as arq:
        linhas = arq.readlines()[11:]                           # Pula as 11 primeiras do cabeçalho

        tabela_atual = None                                     # para definir a categoria da tabela

        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith("the data is"):
                continue                                        # Se a linha estiver vazia ou for o "the data is based on...", pula a linha (continue).

            # Detectar qual tabela está lendo
            if linha.startswith("ReN."):                        # Define a categoria de acordo com o início da linha
                tabela_atual = 'ReN' # Nó obrigatório (required node)
                continue

            elif linha.startswith("ReE."):
                tabela_atual = 'ReE' # Aresta obrigatória (required edge)
                continue

            elif linha.startswith("ReA."):
                tabela_atual = 'ReA' # Arco obrigatório (required arc)
                continue

            elif linha.startswith("EDGE"): 
                tabela_atual = 'Edge' # Aresta não obrigatória
                continue

            elif linha.startswith("ARC"):
                tabela_atual = 'Arc' # Arco não obrigatória
                continue


            # Lendo as linhas com base na tabela
            if tabela_atual == 'ReE':

                # Definindo variáveis para armazenar as informações da linha da tabela
                _, noh_origem, noh_destino, custo_transito, demanda, custo_servico = linha.split()

                noh_origem, noh_destino = int(noh_origem), int(noh_destino)


                aresta_add = {
                    'tipo': 'aresta',
                    'obrigatoria': True,
                    'custo_transito': int(custo_transito),
                    'demanda': int(demanda),
                    'custo_servico': int(custo_servico)
                }
                grafo[noh_destino][noh_origem].append (aresta_add)
                grafo[noh_origem][noh_destino].append (aresta_add) # Bidirecional porque é via de mão dupla

            if tabela_atual == 'Edge':

                _, noh_origem, noh_destino, custo_transito = linha.split()

                noh_origem, noh_destino = int(noh_origem), int(noh_destino)

                aresta_add = {
                    'tipo': 'aresta',
                    'obrigatoria': False,
                    'custo_transito': int(custo_transito),
                    # Não tem demanda nem custo_serviço pois não é obrigatório
                }
                grafo[noh_destino][noh_origem].append (aresta_add)
                grafo[noh_origem][noh_destino].append (aresta_add)  # Bidirecional 
                
            elif tabela_atual == 'ReA':

                _, noh_origem, noh_destino, custo_transito, demanda, custo_servico = linha.split()

                noh_origem, noh_destino = int(noh_origem), int(noh_destino)

                arco_add = {
                    'tipo': 'arco',
                    'obrigatoria': True,
                    'custo_transito': int(custo_transito),
                    'demanda': int(demanda),
                    'custo_servico': int(custo_servico)
                }
                grafo[noh_origem][noh_destino].append(arco_add)
                # Não será bidirecional porque é via de mão única

            elif tabela_atual == 'Arc':

                _, noh_origem, noh_destino, custo_transito = linha.split()

                noh_origem, noh_destino = int(noh_origem), int(noh_destino)

                arco_add = {
                    'tipo': 'arco',
                    'obrigatoria': False,
                    'custo_transito': int(custo_transito),
                    # Não tem demanda nem custo_serviço pois não é obrigatório
                }
                grafo[noh_origem][noh_destino].append(arco_add)
                # Não será bidirecional

            elif tabela_atual == 'ReN':

                nome_noh, demanda, custo_servico = linha.split()

                noh = int(nome_noh[1:])                             # tira o "N" e converte o número
        
                noh_add = {
                    'tipo': 'noh',
                    'obrigatoria': True,
                    # custo_transito não existe já refere-se ao próprio nó
                    'demanda': int(demanda),
                    'custo_servico': int(custo_servico)
                }
                grafo[noh][noh].append(noh_add)

    return cabecalho, grafo


def quant_vertices(cabecalho):
    return int(cabecalho['#Nodes'])

def quant_arestas(cabecalho):
    return int(cabecalho['#Edges'])

def quant_arcos(cabecalho):
    return int(cabecalho['#Arcs'])

def quant_vertices_requeridos(cabecalho):
    return int(cabecalho['#Required N'])

def quant_arestas_requeridas(cabecalho):
    return int(cabecalho['#Required E'])

def quant_arcos_requeridos(cabecalho):
    return int(cabecalho['#Required A'])


def densidade_grafo (cabecalho):
    N = quant_vertices (cabecalho)
    E = quant_arestas (cabecalho)
    A = quant_arcos (cabecalho)

    return (E + A)/((N * (N-1))/2)

def graus_nohs (grafo, cabecalho):
    quant_nohs = quant_vertices (cabecalho)
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
    n = quant_vertices(cabecalho)
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
    n = quant_vertices(cabecalho)
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
    n = quant_vertices(cabecalho)
    
    soma = 0
    contagem = 0
    
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i != j and dist[i][j] != float('inf'):
                soma += dist[i][j]
                contagem += 1

    if contagem == 0:
        return 0  # ou float('inf'), dependendo do que você quiser indicar
    
    return soma / contagem

def diametro_grafo(grafo, cabecalho):
    dist, _ = floyd_warshall(grafo, cabecalho)
    n = quant_vertices(cabecalho)
    
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

def exportar_csv(cabecalho, grafo):

    grau_total, grau_entrada, grau_saida = graus_nohs (grafo, cabecalho)
    intermediacao = calculo_intermediacao(grafo, cabecalho)

    grau_total_max, grau_entrada_max, grau_saida_max = grau_maximo (grau_total, grau_entrada, grau_saida)
    grau_total_min, grau_entrada_min, grau_saida_min = grau_minimo (grau_total, grau_entrada, grau_saida)

    with open("estatisticas.csv", "w", encoding="utf-8") as arq:
        arq.write(f"Estatísticas,Valor\n")
        arq.write(f"Quantidade de vértices:,{quant_vertices(cabecalho)}\n")
        arq.write(f"Quantidade de arestas:,{quant_arestas(cabecalho)}\n")
        arq.write(f"Quantidade de arcos:,{quant_arcos(cabecalho)}\n")
        arq.write(f"Quantidade de vértices requeridos:,{quant_vertices_requeridos(cabecalho)}\n")
        arq.write(f"Quantidade de arestas requeridas:,{quant_arestas_requeridas(cabecalho)}\n")
        arq.write(f"Quantidade de arcos requeridos:,{quant_arcos_requeridos(cabecalho)}\n")
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



   

   

