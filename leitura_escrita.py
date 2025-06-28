from estatisticas import *

# Tratamento de erro
def transforma(valor):
    # Tenta converter para inteiro ou retorna 0. Evita quebras em campos mal formatados.
    
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0

# Leitura de arquivo de entrada .dat 
def ler_entrada(arq_entrada):
    cabecalho = {}
    servicos_obrigatorios = []
    id_servico = 1  # contador sequencial dos obrigatórios

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
                if tabela_atual == 'ReN' and len(partes) == 3:
                    nome_no, demanda, servico = partes
                    noh = int(nome_no[1:])
                    servicos_obrigatorios.append({
                        'id': id_servico,
                        'origem': noh,
                        'destino': noh,
                        'demanda': int(demanda),
                        'custo_total': int(servico),
                        'tipo': 'noh'
                    })
                    grafo[noh][noh].append({
                        'tipo': 'noh',
                        'obrigatoria': True,
                        'demanda': int(demanda),
                        'custo_servico': int(servico)
                    })
                    id_servico += 1

                elif tabela_atual == 'ReE' and len(partes) == 6:
                    _, u, v, custo, demanda, servico = partes
                    u, v = int(u), int(v)
                    servicos_obrigatorios.append({
                        'id': id_servico,
                        'origem': u,
                        'destino': v,
                        'demanda': int(demanda),
                        'custo_total': int(custo) + int(servico),
                        'tipo': 'aresta'
                    })
                    grafo[u][v].append({
                        'tipo': 'aresta',
                        'obrigatoria': True,
                        'custo_transito': int(custo),
                        'demanda': int(demanda),
                        'custo_servico': int(servico)
                    })
                    grafo[v][u].append({
                        'tipo': 'aresta',
                        'obrigatoria': True,
                        'custo_transito': int(custo),
                        'demanda': int(demanda),
                        'custo_servico': int(servico)
                    })
                    id_servico += 1

                elif tabela_atual == 'ReA' and len(partes) == 6:
                    _, u, v, custo, demanda, servico = partes
                    u, v = int(u), int(v)
                    servicos_obrigatorios.append({
                        'id': id_servico,
                        'origem': u,
                        'destino': v,
                        'demanda': int(demanda),
                        'custo_total': int(custo) + int(servico),
                        'tipo': 'arco'
                    })
                    grafo[u][v].append({
                        'tipo': 'arco',
                        'obrigatoria': True,
                        'custo_transito': int(custo),
                        'demanda': int(demanda),
                        'custo_servico': int(servico)
                    })
                    id_servico += 1

                elif tabela_atual == 'Edge' and len(partes) == 4:
                    _, u, v, custo = partes
                    u, v = int(u), int(v)
                    grafo[u][v].append({
                        'tipo': 'aresta',
                        'obrigatoria': False,
                        'custo_transito': int(custo)
                    })
                    grafo[v][u].append({
                        'tipo': 'aresta',
                        'obrigatoria': False,
                        'custo_transito': int(custo)
                    })

                elif tabela_atual == 'Arc' and len(partes) == 4:
                    _, u, v, custo = partes
                    u, v = int(u), int(v)
                    grafo[u][v].append({
                        'tipo': 'arco',
                        'obrigatoria': False,
                        'custo_transito': int(custo)
                    })

            except Exception as e:
                print(f"⚠ Erro ao processar linha da tabela {tabela_atual}: {linha}")
                print(f"   Detalhes: {e}")

    return cabecalho, grafo, servicos_obrigatorios


# Salva os resultados no formato padronizado
def salvar_rotas_em_arquivo(nome_saida, rotas, servicos, custo_total, matriz_custos, clocks_alg, clocks_total):
    from heuristica import custo_rota
    # Linha por rota: ID, demanda, custo, visitas e sequência de serviços com (S id,origem,destino)
    
    with open(nome_saida, "w", encoding="utf-8") as f:
        f.write(f"{int(custo_total)}\n")
        f.write(f"{len(rotas)}\n")
        f.write(f"{clocks_alg}\n")     # clocks do algoritmo
        f.write(f"{clocks_total}\n")   # clocks do programa 

        for idx, rota in enumerate(rotas, 1):
            carga_total = sum([servicos[i]['demanda'] for i in set(rota['servicos'])])
            custo_rota_valor = custo_rota(rota, matriz_custos)
            f.write(f"0 1 {idx} {carga_total} {int(custo_rota_valor)} {len(rota['servicos']) + 2} {' '}")
            f.write("(D 0,1,1) ")
            for i in rota['servicos']:
                s = servicos[i]
                f.write(f"(S {i+1},{s['origem']},{s['destino']}) ")
            f.write("(D 0,1,1)\n")