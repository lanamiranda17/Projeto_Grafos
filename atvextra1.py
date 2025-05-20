#Nome: Nina Tobias Novikoff da Cunha Ribeiro 

import heapq
import sys

def dijkstra(cidades, estradas, grafo):
    INF = float('inf')
    dist_par = [INF] * (cidades + 1)
    dist_impar = [INF] * (cidades + 1)
    dist_par[1] = 0  # Começamos na cidade 1 com 0 pedágios pagos, que é um número par
    
    # Fila de prioridade (min-heap)
    pq = [(0, 1, 0)]  # (custo, cidade, paridade)
    
    while pq:
        custo, cidade, paridade = heapq.heappop(pq)
        
        # Verifica se o custo já foi atualizado
        if paridade == 0 and custo > dist_par[cidade]:
            continue
        if paridade == 1 and custo > dist_impar[cidade]:
            continue
        
        for vizinho, pedagio in grafo[cidade]:
            novo_custo = custo + pedagio
            nova_paridade = 1 - paridade  # Alterna entre 0 (par) e 1 (ímpar)
            
            # Atualiza o custo para a cidade vizinha com o novo estado (par ou ímpar)
            if nova_paridade == 0 and novo_custo < dist_par[vizinho]:
                dist_par[vizinho] = novo_custo
                heapq.heappush(pq, (novo_custo, vizinho, 0))
            elif nova_paridade == 1 and novo_custo < dist_impar[vizinho]:
                dist_impar[vizinho] = novo_custo
                heapq.heappush(pq, (novo_custo, vizinho, 1))
    
    # O resultado que queremos é o custo de chegar à cidade C com número par de pedágios
    return dist_par[cidades] if dist_par[cidades] != INF else -1

def main():
    cidades, estradas = map(int, input().split())
    
    # Adiciona as estradas no formato de lista de adjacência
    grafo = [[] for _ in range(cidades + 1)]
    
    for _ in range(estradas):
        cidade1, cidade2, pedagio = map(int, input().split())
        grafo[cidade1].append((cidade2, pedagio))
        grafo[cidade2].append((cidade1, pedagio))
    
    # Resolve o problema usando o algoritmo de Dijkstra modificado
    resultado = dijkstra(cidades, estradas, grafo)
    
    # Imprime o resultado
    print(resultado)

if __name__ == "__main__":
    main()
