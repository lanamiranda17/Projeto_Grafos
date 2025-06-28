import os
import pandas as pd
import time
import concurrent.futures
import re

from leitura_escrita import *
from estatisticas import *
from heuristica import *

def ordenar_naturalmente(nome):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', nome)]

def processar_instancia(arquivo_entrada):
    nome_base = os.path.basename(arquivo_entrada).replace(".dat", "")
    print(f"Lendo: {nome_base}.dat")
    cabecalho, grafo, servicos_obrigatorios = ler_entrada(arquivo_entrada)

    inicio_total = time.perf_counter_ns()
    dist, _ = floyd_warshall(grafo, cabecalho)
    servicos = servicos_obrigatorios
    matriz_custos = matriz_obrigatorios(servicos, dist)
    capacidade = capacidade_veiculo(cabecalho)

    inicio_alg = time.perf_counter_ns()
    num_servicos = len(servicos)

    # Escolha da heurística baseada no número de serviços
    if num_servicos <= 100:
        rotas = clarke_wright_otimizado(servicos, matriz_custos, capacidade)
    elif num_servicos <= 300:
        rotas = grasp_simples(servicos, matriz_custos, capacidade)
    else:
        rotas = clarke_wright_otimizado(servicos, matriz_custos, capacidade)

    # Refinamento condicional baseado no tamanho da instância
    rotas = refinar_condicional(rotas, servicos, matriz_custos, capacidade, nome_base)

    fim_alg = time.perf_counter_ns()

    custo = sum(custo_rota(rota, matriz_custos) for rota in rotas)
    fim_total = time.perf_counter_ns()

    clocks_alg = fim_alg - inicio_alg
    clocks_total = fim_total - inicio_total

    try:
        estatistica = adicionar_estatisticas(nome_base, cabecalho, grafo)
    except Exception:
        estatistica = None

    return nome_base, rotas, servicos, custo, matriz_custos, clocks_alg, clocks_total, estatistica

    # Executa o processamento de uma instância de arquivo em um caminho específico.
def worker(args):
    _, arq, pasta_entrada = args
    caminho = os.path.join(pasta_entrada, arq) # caminho completo do arquivo
    return processar_instancia(caminho)

def processar_todos():
    pasta_entrada = "instancias/"
    pasta_saida = "G12/"
    os.makedirs(pasta_saida, exist_ok=True)

    # Lista os arquivos .dat na pasta de entrada
    arquivos = os.listdir(pasta_entrada)
    arquivos = [f.strip() for f in arquivos if f.lower().endswith(".dat")]
    arquivos.sort(key=ordenar_naturalmente)

    # Cria uma lista de tuplas (índice, nome_arquivo, pasta_entrada) para passar ao worker
    args_list = [(i, arq, pasta_entrada) for i, arq in enumerate(arquivos)]

    # Utiliza ProcessPoolExecutor para processar os arquivos em paralelo (muliprocessamento)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        resultados = list(executor.map(worker, args_list))

    estatisticas = [] # Lista para armazenar estatísticas de cada instância
    for idx, (nome_base, rotas, servicos, custo, matriz_custos, clocks_alg, clocks_total, estatistica) in enumerate(resultados):
        nome_saida = os.path.join(pasta_saida, f"sol-{nome_base}.dat")  # sem prefixo numérico
        salvar_rotas_em_arquivo(nome_saida, rotas, servicos, custo, matriz_custos, clocks_alg, clocks_total)

        print(f"{nome_base}.dat processado com sucesso.")
        if estatistica:
            estatisticas.append(estatistica)

    try: # Salva as estatísticas em um CSV
        df = pd.DataFrame(estatisticas)
        df.to_csv("estatisticas_gerais.csv", index=False, sep=';', encoding="utf-8")
        print("Estatísticas salvas com sucesso em 'estatisticas_gerais.csv'")
    except Exception as e:
        print(f"Erro ao salvar o CSV: {e}")

if __name__ == "__main__":
    processar_todos()
