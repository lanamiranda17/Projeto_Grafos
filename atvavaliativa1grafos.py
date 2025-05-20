#Nome: Nina Tobias Novikoff da Cunha Ribeiro 

import math
import heapq


def dijkstra_max(grafo, origem, destino, n):
    capacidade = [0] * (n + 1)
    capacidade[origem] = float('inf')
    heap = [(-capacidade[origem], origem)]
    visitado = [False] * (n + 1)

    while heap:
        cap_negativa, u = heapq.heappop(heap)
        cap_atual = -cap_negativa
        if visitado[u]:
            continue
        visitado[u] = True

        for v, w in grafo[u]:
            if not visitado[v]:
                nova_cap = min(cap_atual, w)
                if nova_cap > capacidade[v]:
                    capacidade[v] = nova_cap
                    heapq.heappush(heap, (-nova_cap, v))

    return capacidade[destino]

def main():
    resultados = []
    
    while True:
        x, y = map(int, input().split())
        if x == 0 and y == 0:
            break
        # Monta o grafo
        grafo = [[] for _ in range(x + 1)]
        for _ in range(y):
            u, v, p = map(int, input().split())
            grafo[u].append([v, p])
            grafo[v].append([u, p])

        a, b, c = map(int, input().split())
        cap_caminho = dijkstra_max(grafo, a, b, x)
        cap_onibus = cap_caminho - 1  # -1 por causa do motorista
        viagens = math.ceil(c / cap_onibus)
        resultados.append(viagens)

    for r in resultados:
        print(r)

main()