# Modelagem Logística com Grafos em Python

## Implementação Final para a Disciplina de Algoritmos em Grafos

Este repositório contém a implementação do projeto final da disciplina de Algoritmos em Grafos, focada em resolver um problema de roteamento logístico complexo utilizando Python.

- **Instituição:** Universidade Federal de Lavras (UFLA)
- **Professor:** Mayron César O. Moreira

---

## 🎯 Sobre o Projeto

O projeto aborda o **Problema de Roteamento de Arcos com Capacidade (CARP)**, um desafio clássico da otimização logística. O objetivo é encontrar um conjunto de rotas de custo mínimo para uma frota de veículos, garantindo que todas as demandas de serviço sejam atendidas sem exceder a capacidade de cada veículo.

A solução implementada é capaz de:
-   **Processar dados complexos** a partir de arquivos de instância `.dat`.
-   **Modelar o problema** usando uma estrutura de grafos mistos (com arestas e arcos).
-   **Calcular os caminhos mínimos** entre todos os pontos de interesse.
-   **Aplicar heurísticas e algoritmos de busca local** para construir e otimizar as rotas.
-   **Processar múltiplas instâncias em paralelo** para maior eficiência.
-   **Gerar relatórios detalhados**, incluindo arquivos de solução para cada instância e uma planilha  com estatísticas dos grafos.

---

## 🧠 Descrição do Problema

O cenário logístico é representado por um **grafo misto e conexo**, onde:

-   **Vértices**: Representam cruzamentos, depósitos ou pontos de interesse.
-   **Arestas**: Representam ruas de mão dupla.
-   **Arcos**: Representam ruas de mão única.

Um subconjunto desses elementos (vértices, arestas ou arcos) possui uma **demanda de serviço** e deve ser obrigatoriamente visitado. O desafio é criar rotas que:
1.  Comecem e terminem em um **depósito central**.
2.  Atendam a todas as **demandas obrigatórias**.
3.  Respeitem a **capacidade máxima** de cada veículo.
4.  Minimizem o **custo total** de deslocamento.

---

## 🛠️ Algoritmos e Estratégias

Para resolver o problema, foi implementada uma abordagem híbrida e adaptativa:

1.  **Cálculo de Caminhos Mínimos**: O algoritmo de **Floyd-Warshall** é utilizado para pré-calcular a matriz de distâncias mínimas entre todos os nós do grafo. Essa matriz é fundamental para determinar o custo de deslocamento entre quaisquer dois serviços.

2.  **Construção de Rotas**:
    -   **Clarke & Wright (Otimizado)**: Uma heurística de economia (savings) para construir uma solução inicial, fundindo rotas menores com base na economia de custo gerada.
    -   **GRASP (Greedy Randomized Adaptive Search Procedure)**: Para instâncias de tamanho intermediário, esta meta-heurística cria múltiplas soluções iniciais de forma semi-aleatória e as refina, ajudando a explorar diferentes partes do espaço de busca e a evitar ótimos locais.

3.  **Refinamento e Busca Local**:
    -   **Realocação de Serviços**: Tenta mover um serviço de uma rota para outra, buscando reduzir o custo total.
    -   **3-opt**: Um algoritmo de busca local que otimiza a sequência de visitas *dentro* de uma mesma rota, testando diferentes combinações de três arestas.

4.  **Estratégia Adaptativa**: O `main.py` seleciona a combinação de algoritmos mais adequada com base no número de serviços obrigatórios de cada instância, balanceando a qualidade da solução e o tempo de execução.
    -   **Instâncias Pequenas (≤ 100 serviços)**: Clarke & Wright + Refinamento completo.
    -   **Instâncias Médias (≤ 300 serviços)**: GRASP para melhor exploração.
    -   **Instâncias Grandes (> 300 serviços)**: Clarke & Wright sem refinamentos pesados para garantir uma solução rápida.

---

## 📁 Estrutura do Projeto

O código foi modularizado para melhor organização e manutenibilidade:

-   `main.py`: O script principal que orquestra todo o processo. Ele lê os arquivos, distribui as tarefas para processamento paralelo e salva os resultados.
-   `leitura_escrita.py`: Contém as funções para ler os arquivos de entrada `.dat` e para formatar e salvar os arquivos de solução.
-   `estatisticas.py`: Centraliza as funções que calculam as métricas do grafo (densidade, graus, diâmetro, centralidade, etc.) e o algoritmo de Floyd-Warshall.
-   `heuristica.py`: O coração do projeto, onde estão implementados os algoritmos de solução do CARP (Clarke & Wright, GRASP, 3-opt, etc.).
-   `instancias/`: Pasta contendo os arquivos `.dat` com os dados de cada problema.
-   `G12/`: Pasta criada automaticamente para armazenar os arquivos de solução (`sol-nome_da_instancia.dat`).
-   `estatisticas_gerais.csv`: Arquivo CSV gerado ao final da execução, com um resumo das características de cada grafo processado.

---

## ⚙️ Como Executar

1.  **Pré-requisitos**: Certifique-se de ter o **Python 3.x** instalado. A única dependência externa é a biblioteca `pandas`. Instale-a com o comando:
    ```bash
    pip install pandas
    ```

2.  **Organização**: Coloque os arquivos (`main.py`, `heuristica.py`, `estatisticas.py`, `leitura_escrita.py`) e a pasta `instancias/` no mesmo diretório.

3.  **Execução**: Abra um terminal na pasta do projeto e execute o script principal:
    ```bash
    python main.py
    ```

4.  **Resultados**: Ao final da execução, a pasta `G12/` conterá os arquivos de solução e o arquivo `estatisticas_gerais.csv` será criado no diretório principal.

---

## 🔹 Padrão de Saída das Soluções

Cada arquivo de solução gerado na pasta `G12/` segue rigorosamente o formato:

<linha 1> custo total da solução
<linha 2> total de rotas
<linha 3> total de clocks para execução do algoritmo de referência
<linha 4> total de clocks para encontrar a solução de referência
<linha 5+> 0 1 <id_rota> <demanda_total_rota> <custo_total_rota> <total_visitas> (D 0,1,1) (S id,origem,destino) ... (D 0,1,1)

-   `(D 0,1,1)`: Indica uma parada no depósito (origem/destino da rota).
-   `(S id,origem,destino)`: Representa um serviço obrigatório realizado (em um vértice, aresta ou arco).

---

## 👩‍💻 Autoras

-   Lana da Silva Miranda
-   Nina Tobias Novikoff da Cunha Ribeiro