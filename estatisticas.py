from leitura_escrita import *
from leitura_escrita import transforma # Para evitar erro de importação

# Funçoes auxiliares extraem do cabeçalho do arquivo .dat.
def quant_vertices(cabecalho):
    return transforma(cabecalho.get('#Nodes'))

def quant_arestas(cabecalho):
    return transforma(cabecalho.get('#Edges'))

def quant_arcos(cabecalho):
    return transforma(cabecalho.get('#Arcs'))

def quant_vertices_requeridos(cabecalho):
    return transforma(cabecalho.get('#Required N'))

def quant_arestas_requeridas(cabecalho):
    return transforma(cabecalho.get('#Required E'))

def quant_arcos_requeridos(cabecalho):
    return transforma(cabecalho.get('#Required A'))

def capacidade_veiculo(cabecalho):
    return transforma(cabecalho.get('Capacity'))

def deposito(cabecalho):
    return transforma(cabecalho.get('Depot Node'))

# Calcula a densidade real do grafo
def densidade_grafo (cabecalho):
    N = int(cabecalho['#Nodes'])
    E = int(cabecalho['#Edges'])
    A = int(cabecalho['#Arcs'])

    return (E + A)/((N * (N-1))/2)

# Calcula grau total, de entrada e de saída de cada nó
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

# Pega os maiores graus de cada tipo
def grau_maximo (grau_total, grau_entrada, grau_saida):
    # Ignora o índice 0
    grau_total_max = max (grau_total[1:])
    grau_entrada_max = max (grau_entrada[1:])
    grau_saida_max = max (grau_saida[1:])

    return grau_total_max, grau_entrada_max, grau_saida_max

# Pega os menores graus de cada tipo
def grau_minimo(grau_total, grau_entrada, grau_saida):

    grau_total_min = min(grau_total[1:])
    grau_entrada_min = min(grau_entrada[1:])
    grau_saida_min = min(grau_saida[1:])
    
    return grau_total_min, grau_entrada_min, grau_saida_min

# Floyd-Warshall 
def floyd_warshall(grafo, cabecalho):

    '''
    * Calcula *distância mínima* entre todos os pares de vértices usando o algoritmo clássico de Floyd-Warshall.
    * Cria também matriz de predecessores (pred) para reconstruir caminhos.
    '''

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

# Reconstroi o caminho entre dois nós usando a matriz pred.
def reconstruir_caminho(pred, i, j):
    if pred[i][j] is None:
        return []
    
    caminho = [j]
    while i != j:
        j = pred[i][j]
        caminho.append(j)

    caminho.reverse()
    return caminho

#  Mede intermediação dos nós: quantas vezes cada nó aparece nos caminhos mínimos entre todos os pares.
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

# Calcula o comprimento médio dos caminhos
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

# Calcula o diâmetro (maior distância entre dois nós).
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

# Coleta estatísticas para salvar num .csv no final (opcional)
def adicionar_estatisticas(nome_base, cabecalho, grafo):
    grau_total, grau_entrada, grau_saida = graus_nohs(grafo, cabecalho)

    grau_total_max = max(grau_total[1:]) if any(grau_total[1:]) else 0
    grau_entrada_max = max(grau_entrada[1:]) if any(grau_entrada[1:]) else 0
    grau_saida_max = max(grau_saida[1:]) if any(grau_saida[1:]) else 0
    grau_total_min = min(grau_total[1:]) if any(grau_total[1:]) else 0
    grau_entrada_min = min(grau_entrada[1:]) if any(grau_entrada[1:]) else 0
    grau_saida_min = min(grau_saida[1:]) if any(grau_saida[1:]) else 0
    densidade = densidade_grafo(cabecalho)

    return {
        'nome': nome_base,
        'num_vertices': quant_vertices(cabecalho),
        'num_arestas': quant_arestas(cabecalho),
        'num_arcos': quant_arcos(cabecalho),
        'num_vertices_requeridos': quant_vertices_requeridos(cabecalho),
        'num_arestas_requeridas': quant_arestas_requeridas(cabecalho),
        'num_arcos_requeridos': quant_arcos_requeridos(cabecalho),
        'densidade': round(densidade, 4),
        'grau_total_max': grau_total_max,
        'grau_entrada_max': grau_entrada_max,
        'grau_saida_max': grau_saida_max,
        'grau_total_min': grau_total_min,
        'grau_entrada_min': grau_entrada_min,
        'grau_saida_min': grau_saida_min
    }