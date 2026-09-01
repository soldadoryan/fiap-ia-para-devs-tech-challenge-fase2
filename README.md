# VRP Hospitalar com Algoritmo Genético

Roteirização da entrega de medicamentos e insumos a partir de um hospital (base),
resolvida por um algoritmo genético, visualizada em tempo real com Pygame e
documentada por um relatório em PDF escrito pelo Gemini.

O problema é um **VRP (Vehicle Routing Problem)**: uma frota com veículos únicos 
sai da base, atende os pontos de entrega e volta. 
O algoritmo busca **a menor distância rodada com o menor número de veículos**, respeitando:

- **prioridade da carga** - medicamentos críticos são entregues antes dos
  insumos regulares, e só veículos habilitados podem transportá-los;
- **capacidade** de carga de cada veículo;
- **autonomia** (alcance por turno) de cada veículo.

---

## 1. Passos para rodar o projeto

### Pré-requisitos

- Desenvolvido em Python 3.14.6v
- uma chave de API do Gemini (opcional - sem ela o projeto roda igual e o
  relatório sai montado localmente).

### Instalação

```bash
git clone <url-do-repositorio>
cd fiap-ia-para-devs-tech-challenge-fase2

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### Chave do Gemini

```bash
copy .env.example .env
```

Abra o `.env` e preencha:

```
GEMINI_API_KEY=sua-chave-aqui
```

O `.env` está no `.gitignore`, então a chave nunca vai para o repositório.

### Execução

```bash
python vrp.py
```

Abre a janela do simulador. A cada geração a tela mostra o gráfico de evolução a
esquerda e o mapa com as rotas a direita; o console imprime o custo e o estado da
frota. **Feche a janela ou aperte `Q`** para encerrar: nesse momento o relatório
é gerado, salvo em `relatorios/` e aberto na máquina.

### Rodando cenários diferentes

Tudo o que se ajusta está em [config.py](config.py) - nenhum módulo do algoritmo
precisa ser tocado. Os parâmetros mais úteis:

| Parâmetro                     | O que faz                                                       |
| ----------------------------- | --------------------------------------------------------------- |
| `N_CITIES`                    | quantidade de pontos de entrega (o primeiro vira a base)        |
| `POPULATION_SIZE`             | tamanho da população do algoritmo                                      |
| `MUTATION_PROBABILITY`        | chance de mutação por filho                                     |
| `ELITISMO`                    | `True`/`False` - se o melhor indivíduo passa intacto para a próxima geração |
| `PROB_CRITICO`                | fração de entregas classificadas como críticas                  |
| `DEMANDA_MIN` / `DEMANDA_MAX` | faixa de carga sorteada por ponto                               |
| `FROTA`                       | a frota inteira: nome, capacidade, autonomia, habilitação e cor |
| `CUSTO_FIXO_VEICULO`          | quanto custa colocar mais um veículo na rua                     |
| `INSTANCIA`                   | `"aleatoria"` ou `"att48"` (mapa fixo de benchmark)             |
| `SEMENTE`                     | fixa o sorteio para reproduzir exatamente a mesma rodada        |
| `ABRIR_PDF_AO_FINAL`          | abre ou não o PDF automaticamente                               |

### Testes

```bash
pytest -q
```
Cada teste está descrito na [seção 10](#10-testes-automatizados).

```bash
python -m pytest -v                       # um nome por linha
python -m pytest tests/test_fitness.py    # so um arquivo
python -m pytest -x                       # para no primeiro que falhar
```

### Benchmarks

```bash
python -m benchmarks tsp 2000       # compara com o otimo conhecido do att48
python -m benchmarks vrp 2000       # a frota completa no mesmo mapa fixo
```

---

## 2. Bibliotecas usadas
### pygame

Responsável pela renderização do problema e demonstração em
tempo real. Cria os circulos, desenha as linhas e renderiza as setas com as cores corretas de acordo com a legenda. A captura de tela do final do relatório também é capturada por ela.

### matplotlib

Responsável pelo gráfico responsável pela renderização da evolução e número de veículos;

### numpy

Biblioteca responsável por manipulação de arrays numéricos. Utilizada na função fitness.

### google-genai

Responsável pela chamada do agente e escrita do relatório final.

### fpdf2

Monta o arquivo PDF do relatório final.

### python-dotenv

Responsável por ler o arquivo `.env` e distribuir o valor das variáveis de desenvolvimento pelo código;

### pytest

Biblioteca responsável por todo o ambiente de testes.

---

## 3. Como funciona o algoritmo genético

O [algoritmo_genetico/](algoritmo_genetico/) atua como um algoritmo genético genérico. Ou seja, ele não tem ciência do que são os objetos analisados como hospital, veículo, rota e etc.

### Representação

Podemos tratar um indivíduo como uma lista com todos os pontos do mapa considerado
como uma das possíveis soluções:
```python
[(120, 430), (770, 88), (305, 512), ...]
```

A primeira posição é a base (o hospital); as demais formam a fila de entregas na
ordem proposta. Não existe veículo, carga nem prioridade dentro da lista. Desta
forma conseguimos manter a capacidade do algoritmo resolver TSP mesmo sendo adaptado para
VRP.

### O ciclo, geração a geração

O ciclo responsável pela atuação do algoritmo está em [vrp.py](vrp.py) e repete os passos abaixo:

**1. Avaliação** - o indivíduo passa por `calcular_fitness_logistico`, que o
decodifica em rotas e devolve o custo. Regra de fitness: **menor custo =
melhor indivíduo**.

**2. Ordenação** - `sort_population`
([algoritmo_genetico/avaliacao.py](algoritmo_genetico/avaliacao.py)) junta
população e fitness em pares, ordena pelo fitness e separa de novo. É o que
permite ao elitismo saber quem são os melhores.

**3. Elitismo** - controlado por `config.ELITISMO` (`True` por padrão): quando
ligado, o melhor indivíduo passa intacto para a geração seguinte
(`new_population = [population[0]]`), o que garante que a solução nunca piora
de uma geração para a outra. Desligando (`False`), toda a população é
recriada por seleção/cruzamento/mutação a cada geração, sem essa garantia.

**4. Seleção dos pais** - `selecao_por_roleta`
([algoritmo_genetico/selecao.py](algoritmo_genetico/selecao.py)): cada indivíduo
ganha uma fatia da roleta proporcional a `1 / fitness`. A inversão é essencial,
porque aqui fitness é custo, quanto menor melhor, então a rota barata vira o
peso grande. Os indivíduos ruins mantém uma chance pequena de propósito: é o que
preserva diversidade e evita enviesar o algoritmo já nas primeiras gerações.

**5. Cruzamento (Order Crossover)** -
[algoritmo_genetico/cruzamento.py](algoritmo_genetico/cruzamento.py). A escolha 
do Order Crossover veio do fato de que em um algoritmo de rotas, não podemos apenas
agregar características dos pais. Desta forma, teríamos os filhos com destinos 
repetidos ou não cobriríamos todas as localizações necessárias. 

**Os passos de cruzamento são:**

1. sorteia uma fatia contígua do pai 1 e cópia inteira para o filho;
2. lista as posições que sobraram;
3. percorre o pai 2 na ordem dele, pegando só as cidades que ainda não entraram;
4. encaixa essas cidades nos buracos, respeitando a ordem do pai 2.

O filho herda um trecho de rota do pai 1 e a ordem relativa do resto do pai 2 -
e continua sendo uma permutação válida.

**6. Mutação (swap de vizinhos)** -
[algoritmo_genetico/mutacao.py](algoritmo_genetico/mutacao.py). Com probabilidade
`MUTATION_PROBABILITY`, sorteia uma posição e troca aquela cidade com a seguinte.
É o empurrãozinho que impede a população de virar cópia da cópia.

A população inicial vem de `generate_random_population`
([algoritmo_genetico/populacao.py](algoritmo_genetico/populacao.py)) e cada cidade
aparece apenas uma vez para que a população inicial seja sempre válida.

### A ideia central: as restrições ficam na leitura e não no input inicial

Este é o ponto de projeto mais importante. As restrições do VRP não entram no
indivíduo nem nos operadores, elas entram na **leitura** dele:

Consequências práticas:

- os operadores genéticos ficaram intactos, sem nenhum código de reparo;
- nenhum filho nasce inválido, então não há descarte de indivíduos;
---

## 4. Implementação de cada restrição

[restricoes/](restricoes/). Foram separadas as restrições em duas categorias:
as **obrigatórias**, ou seja, aquelas que não podem ser violadas e as **penalizadas**
que são aquelas que sofrem uma penalização mas que podem ser violadas se isto fizer
parte do caminho para encontrar a melhor solução.

### Prioridade da carga - restrição rígida

Em `decodificar_rotas`
([restricoes/roteirizacao.py](restricoes/roteirizacao.py)) a fila é separada em
dois grupos, `criticos` e `regulares`, **preservando a ordem que o indivíduo
propôs**. É nessa ordem que o problema é otimizado pelo algoritimo. Os críticos são distribuidos primeiro, os regulares depois, e cada rota é montada como:

```python
[base] + carteiras_criticas[i] + carteiras_regulares[i]
```

Como a concatenação é nessa ordem, **é impossível** um regular
ser atendido antes de um crítico dentro de um mesmo veículo.

### Habilitação para carga crítica

Cada veículo tem `aceita_criticos`. Na distribuição dos críticos, a lista de
índices passada ao repartidor contém **apenas os veículos habilitados**:

Veículos não habilitados jamais receberão medicamento crítico. Se nenhum veículo for habilitado, o algoritmo ignorará essa restrição para que seja possível o cálculo.

### Capacidade de carga

O algoritimo enche o veículo atual até a próxima
entrega não caber na capacidade dele, e só então passa para o proximo.

O teste de encaixe usa a carga **total** já acumulada no veículo (críticos +
regulares).

Chegando ao último veículo, tudo o que sobrar vai para ele mesmo assim: nenhuma
entrega fica sem atendimento. Em caso da carga ser maior que a capacidade da frota,
adicionamos um valor de fitness de 1000 para cada unidade, deixando caro o suficiente
para o algoritmo sempre optar por rotas que caibam.

### Autonomia

A mesma penalidade acontece para autonomia. Caso a frota não tenha autonomia suficiente
para completar a rota, um valor de fitness é adicionado por unidade deixando caro a ponto do
algoritmo entender que esta solução não deve ser utilizada.

### Dimensionamento da frota

`validar_capacidade` ([restricoes/entregas.py](restricoes/entregas.py)) roda uma
única vez, antes da evolução, e aborta com mensagem clara se:

- a capacidade total da frota for menor que a demanda total; ou
- a capacidade dos veículos habilitados for menor que a demanda crítica.

### Os dados das entregas

`gerar_entregas` sorteia, uma única vez na inicialização, a `prioridade`
(`CRITICO` / `REGULAR`) e a `demanda` de cada ponto. Como as cidades são tuplas
`(x, y)` - portanto hasháveis -, os atributos ficam num dicionário
`cidade -> dados`, sem mexer na representação usada pelo GA.

---

## 5. Visualização

A tela tem 1600x900 e é dividida em duas metades pelo `PLOT_X_OFFSET`: gráfico a
esquerda, mapa a direita. Tudo é redesenhado a cada geração.

### O mapa - [visualizacao/mapa.py](visualizacao/mapa.py)

- **Pontos de entrega** (`draw_cities`): círculos coloridos por prioridade 
  (laranja para críticas, azul claro para regulares). A base é desenhada em verde.
- **Rotas** (`draw_paths`): uma `pygame.draw.lines` fechada por veículo, na cor
  definida em `config.FROTA`. Veículos não utilizados não são desenhados.
- **Sentido do percurso** (`draw_route_arrows`): uma seta triangular no meio de
  cada trecho, apontando da cidade atual para a próxima. Este recurso foi implementado
  para facilitar o entendimento do sentido da rota e qual a próxima cidade visitada por um
  veículo.

### O gráfico - [visualizacao/grafico.py](visualizacao/grafico.py)

O gráfico tem **dois eixos y**:

- **azul, eixo esquerdo**: o custo (fitness) da melhor solução de cada geração -
  uma curva continua que deve cair e estabilizar;
- **laranja, eixo direito**: o número de veículos despachados.

Ao final, salvamos o último status de renderização para anexar ao PDF do relatório.

---

## 6. A função de fitness

Está em [restricoes/fitness.py](restricoes/fitness.py). **Quanto menor, melhor** -
manter essa convenção é o que faz `sort_population` e a roleta (que usa
`1/fitness` como peso) funcionarem sem nenhuma adaptação.

```
custo = soma das distancias de todas as rotas
      + (veiculos despachados x CUSTO_FIXO_VEICULO)
      + excesso de carga     x PENALIDADE_EXCESSO
      + excesso de autonomia x PENALIDADE_AUTONOMIA
      + PESO_EQUILIBRIO x (maior rota - menor rota)     [opcional, 0 por padrão]
```

O cálculo começa somando a distancia das rotas de cada indivíduo.

**O custo fixo por veículo é o termo mais interessante.** Sem ele, o algoritmo não teria
motivo nenhum para deixar um veículo parado: espalhar as entregas por toda a
frota sempre reduz a distância individual. O custo fixo deve ser calibrado de acordo
com o quanto queremos evitar que veículos sejam utilizados.

As penalidades podem ser configuradas de acordo com a necessidade e com o objetivo
final do algoritmo no arquivo `config.py`.

`PESO_EQUILIBRIO` vem zerado. Ligando-o, o algoritmo passa a preferir rotas de
duração parecida entre os motoristas, ao custo de alguma distância total.

### Escala

O mapa é simulado com **1 pixel = 1 metro** (`METROS_POR_PIXEL`). Todas as contas
internas correm em metros; a conversão para km acontece só na apresentação, pela
função `km()` em [restricoes/veiculo.py](restricoes/veiculo.py). O tempo estimado
assume `VELOCIDADE_MEDIA_KMH = 60`.

---

## 7. Geração do relatório

Ao fechar a janela, [vrp.py](vrp.py) salva a captura da tela e chama
`gerar_relatorio_final` ([relatorios/**init**.py](relatorios/__init__.py)), que
orquestra três etapas:

**Etapa 1 - os números** ([relatorios/dados.py](relatorios/dados.py)). Decodifica
a melhor solução e monta um dicionário pronto para virar JSON: por veículo,
carga, ocupação percentual, distância, uso da autonomia, tempo estimado, flags de
estouro e a lista ordenada de paradas com coordenada, prioridade, carga e
distância do ponto anterior; no resumo, pontos de entrega, veículos em uso,
veículos ociosos nomeados, gerações executadas, fitness inicial e final, melhoria
percentual e totais. **Este módulo é a única fonte de números do relatório.**

**Etapa 2 - o texto** ([relatorios/texto.py](relatorios/texto.py)), que monta o
prompt e chama o pacote [gemini/](gemini/) - ou escreve o relatório local se ele
não responder. Detalhado na seção seguinte.

**Etapa 3 - o PDF** ([relatorios/pdf.py](relatorios/pdf.py)), com `fpdf2`:

1. **capa** com os indicadores da rodada e, quando houver veículo ocioso, um
   parágrafo explicando que isso é economia de custo fixo e não falha;
2. **o texto do Gemini**;
3. **anexo com o roteiro detalhado**, veículo por veículo, parada por parada,
   montado localmente, servindo de conferência do que o LLM escreveu;
4. **anexo em paisagem** com a captura da tela do simulador.

O arquivo sai como `relatorios/relatorio_rotas_AAAAMMDD_HHMMSS.pdf` (a pasta é
criada se não existir) e é aberto no visualizador padrão.

---

## 8. Integração com o Gemini

Toda isolada no pacote [gemini/](gemini/). A análise do LLM é dispensável para que 
o algoritmo rode. Sendo assim, caso algum obstáculo técnico ou financeiro não permita
a integração, ainda sim o algoritmo gerará o relatório.

| Arquivo             | Responsabilidade                                          |
| ------------------- | --------------------------------------------------------- |
| `gemini/prompt.md`  | **o prompt em si**, fora do código Python                 |
| `gemini/prompt.py`  | carrega o `prompt.md` e substitui os marcadores           |
| `gemini/cliente.py` | chave de API, escolha do SDK, cadeia de modelos e backoff |


### O prompt

O texto do prompt vive em [gemini/prompt.md](gemini/prompt.md), não em código:
dá para lê-lo e ajustá-lo sem abrir nenhum `.py`, e a revisão dele no git fica
legível. Ele tem três partes: o papel ("analista de logística hospitalar"), a
explicação do contexto (frota heterogênea, prioridade, escala em km, e o fato de
que o fitness minimiza distância **e** número de veículos) e os dados da rodada.

**O prompt foi otimizado através de um gem de criação de prompts do próprio Gemini.**

`montar_prompt()` carrega o arquivo e troca dois marcadores:

| Marcador                   | Vira                                                      |
| -------------------------- | --------------------------------------------------------- |
| `{{VELOCIDADE_MEDIA_KMH}}` | a velocidade média de `config.py`                         |
| `{{DADOS_JSON}}`           | os números da rodada, já calculados, serializados em JSON |

**Decisão de projeto: o LLM recebe os dados já calculados e só escreve o texto.**
Distâncias, cargas e percentuais saem todos do `dados.py`. O Gemini narra e
analisa; ele não calcula. E os mesmos números vão para o anexo do PDF, montado
localmente, o que permite conferir o texto contra a fonte.

---

## 9. Benchmark att48

O `att48` (48 capitais dos EUA) é um benchmark clássico de TSP com tour ótimo
conhecido. Aqui ele serve para duas coisas: rodar sempre o **mesmo mapa**, o que
permite comparar parâmetros e versões, e medir a distância do ótimo.

```bash
python -m benchmarks tsp 2000
python -m benchmarks vrp 2000
```

Para ver o att48 na tela do simulador, basta `INSTANCIA = "att48"` em
`config.py` (a frota precisa dar conta dos 48 pontos).

---

## 10. Testes automatizados

```bash
pytest -q          # 59 testes, menos de um segundo
```

A suíte vive em [tests/](tests/) e segue três regras:

### `test_roteirizacao.py` - o decodificador (15 testes)

O arquivo mais importante: é aqui que as restrições rígidas do VRP são
garantidas. Os cinco primeiros rodam sobre **30 permutações diferentes** das
mesmas cidades, não sobre um caso único.

| Teste                                                        | O que garante                                                                                                                                         |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `toda_rota_parte_da_base`                                    | todo veículo sai do primeiro ponto do cromossomo                                                                                                      |
| `toda_entrega_atendida_exatamente_uma_vez`                   | nada é duplicado nem esquecido entre as rotas                                                                                                         |
| `criticos_sempre_antes_dos_regulares`                        | a restrição de prioridade, veículo por veículo                                                                                                        |
| `veiculo_sem_habilitacao_nunca_leva_carga_critica`           | a restrição de habilitação                                                                                                                            |
| `critico_nao_transborda_para_veiculo_sem_habilitacao`        | o caso difícil: veículo habilitado pequeno demais e um comum com folga. O excedente crítico tem de estourar no habilitado, nunca vazar para o comum   |
| `com_folga_nenhum_veiculo_estoura_a_capacidade`              | havendo folga, o next-fit empacota sem violar capacidade                                                                                              |
| `capacidade_apertada_nao_descarta_entrega`                   | com capacidade insuficiente, o último veículo absorve o excesso - **nenhuma entrega some**. É o contrato que o fitness pressupõe ao cobrar penalidade |
| `frota_sem_nenhum_habilitado_recebe_os_criticos_mesmo_assim` | o fallback: sem veículo habilitado, todos ficam elegíveis em vez de a carga ficar sem atendimento                                                     |
| `sempre_devolve_uma_rota_por_veiculo`                        | o alinhamento posicional com a frota, de que o `zip()` depende no `vrp.py` e no fitness                                                               |
| `veiculo_ocioso_fica_so_com_a_base`                          | quem não sai da garagem tem rota `[base]`, carga 0 e distância 0                                                                                      |
| `individuo_vazio_devolve_lista_vazia`                        | caso de borda                                                                                                                                         |
| `carga_da_rota_ignora_a_base`                                | a base não é uma entrega                                                                                                                              |
| `distancia_de_rota_fechada`                                  | o quadrado de lado 100 mede 400: a rota **volta** para a base                                                                                         |
| `distancia_de_veiculo_que_nao_saiu_da_garagem`               | rota só com a base custa 0.0                                                                                                                          |
| `decodificador_e_deterministico`                             | o mesmo cromossomo sempre gera as mesmas rotas. Sem isso o fitness de um indivíduo mudaria entre gerações e a busca perderia o chão                   |

### `test_fitness.py` - a função de custo (8 testes)

Cada termo do custo isolado é conferido no valor exato, com os pesos fixados pelo
`config_limpo`.

| Teste                                                            | O que garante                                                                                                                                                                                                                                                      |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `sem_violacao_o_custo_e_distancia_mais_custo_fixo`               | a fórmula base: distância total + despachados x custo fixo                                                                                                                                                                                                         |
| `veiculo_ocioso_nao_custa_nada`                                  | o custo fixo é por veículo **despachado**, não por veículo da frota - é o que permite ao algoritmo enxugar a frota                                                                                                                                                        |
| `excesso_de_carga_soma_a_penalidade_exata`                       | 5 unidades acima da capacidade somam exatamente `5 x PENALIDADE_EXCESSO`                                                                                                                                                                                           |
| `excesso_de_autonomia_soma_a_penalidade_exata`                   | 100 m acima da autonomia somam exatamente `100 x PENALIDADE_AUTONOMIA`                                                                                                                                                                                             |
| `peso_equilibrio_cobra_a_diferenca_entre_a_maior_e_a_menor_rota` | zerado (padrão) não muda nada; ligado, cobra o desequilíbrio da frota                                                                                                                                                                                              |
| `individuo_vazio_custa_zero`                                     | caso de borda                                                                                                                                                                                                                                                      |
| `menor_custo_significa_rota_melhor`                              | **a convenção de que todo o resto depende**: uma rota geometricamente boa custa menos que uma ruim. O `sort_population` ordena crescente e a roleta usa `1/fitness`; se o sinal invertesse, os dois passariam a empurrar a busca para as piores rotas, em silêncio |
| `resumo_da_frota_marca_estouro`                                  | o `!` do log aparece quando há violação e some quando não há                                                                                                                                                                                                       |

### `test_entregas.py` - demanda e porte da frota (8 testes)

A validação roda uma única vez, na inicialização, e é a única barreira entre um
cenário impossível e milhares de gerações presas na penalidade. As mensagens de
erro fazem parte do contrato: é por elas que você descobre o que ajustar.

| Teste                                                 | O que garante                                                                                                                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gerar_entregas_cobre_todas_as_cidades`               | toda cidade recebe prioridade válida e demanda dentro da faixa                                                                                                      |
| `probabilidade_nos_extremos`                          | `prob_critico` 0.0 e 1.0 produzem tudo regular / tudo crítico                                                                                                       |
| `demanda_total_ignora_a_base_e_filtra_por_prioridade` | 50 no total, 15 críticos, 35 regulares                                                                                                                              |
| `frota_vazia_e_recusada`                              | `ValueError` claro, em vez de divisão por zero lá na frente                                                                                                         |
| `capacidade_total_insuficiente_e_recusada`            | a mensagem "Frota subdimensionada"                                                                                                                                  |
| `capacidade_critica_insuficiente_e_recusada`          | o caso sutil: a frota comporta o total, mas não a carga crítica. Sem esta checagem o cenário passaria na validação e só falharia depois, como penalidade permanente |
| `folga_confortavel_passa_em_silencio`                 | sem ruído no console quando está tudo bem                                                                                                                           |
| `folga_baixa_gera_aviso`                              | o `[AVISO]` quando a folga fica abaixo de 1,3x                                                                                                                      |

### `test_algoritmo_genetico.py` - os operadores puros (10 testes)

A propriedade que atravessa quase todos: **o indivíduo é uma permutação**. Nenhum
operador pode repetir ou perder uma cidade - é daí que vem a garantia de que
nenhum filho nasce inválido.

| Teste                                                  | O que garante                                                                                                                                                                                                                       |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `distancia_euclidiana`                                 | o triângulo 3-4-5 dá 5.0, e a distância a si mesmo dá 0.0                                                                                                                                                                           |
| `populacao_inicial_so_tem_permutacoes`                 | 25 indivíduos, cada um uma permutação completa                                                                                                                                                                                      |
| `order_crossover_preserva_a_permutacao`                | 50 sementes: o filho nunca tem cidade repetida ou faltando. **É a razão de existir do OX**                                                                                                                                          |
| `order_crossover_realmente_recombina_os_dois_pais`     | o filho herda do pai 2 também. O código base do desafio chamava `order_crossover(parent1, parent1)`, e nesse regime o operador devolve o próprio pai: não há recombinação e a busca vira mutação pura. Este teste tranca essa porta |
| `mutacao_com_probabilidade_zero_nao_altera`            | a probabilidade é respeitada                                                                                                                                                                                                        |
| `mutacao_preserva_a_permutacao_e_nao_toca_no_original` | o `deepcopy`: mutar um filho não pode corromper um indivíduo que ainda está na população                                                                                                                                            |
| `mutacao_em_individuo_minusculo_nao_quebra`            | listas de 0 e 1 elemento                                                                                                                                                                                                            |
| `sort_population_ordena_do_melhor_para_o_pior`         | ordem crescente **e** o pareamento indivíduo-fitness intacto                                                                                                                                                                        |
| `roleta_devolve_dois_individuos_da_populacao`          | a seleção devolve dois pais válidos                                                                                                                                                                                                 |
| `roleta_favorece_o_individuo_de_menor_custo`           | em 200 sorteios, o barato vence o caro. É o `1/fitness` que faz a roleta apontar para o lado certo                                                                                                                                  |

### `test_relatorios.py` - números e PDF (11 testes)

O `dados.py` é a **única fonte de números** do relatório: o Gemini só narra o que
sai dali. Se estes valores mentirem, o relatório inteiro mente - inclusive o
anexo de conferência, que existe justamente para pegar isso.

| Teste                                           | O que garante                                                                                                                                                               |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `resumo_bate_com_as_rotas`                      | pontos, frota, veículos em uso e carga total conferem com as rotas decodificadas                                                                                            |
| `melhoria_percentual`                           | a conta de fitness inicial -> final                                                                                                                                         |
| `distancia_total_e_a_soma_dos_veiculos`         | o total do resumo não diverge do detalhe por veículo                                                                                                                        |
| `veiculos_ociosos_sao_nomeados`                 | quem ficou na garagem aparece pelo nome - o relatório precisa explicar que é economia, não falha                                                                            |
| `paradas_seguem_a_ordem_da_rota`                | a sequência e a numeração das paradas batem com a rota real. É o que o motorista vai seguir                                                                                 |
| `primeira_parada_mede_a_distancia_desde_a_base` | o primeiro trecho não é medido a partir do lugar errado                                                                                                                     |
| `ocupacao_e_uso_de_autonomia_em_percentual`     | os percentuais conferem com carga e capacidade                                                                                                                              |
| `escala_e_tempo`                                | 1000 px = 1,00 km, e 1 km a 60 km/h leva 1 minuto                                                                                                                           |
| `exportar_pdf_grava_arquivo`                    | o PDF sai e não está vazio (usa `fpdf2` de verdade, em `tmp_path`)                                                                                                          |
| `exportar_pdf_aceita_acento`                    | o FPDF clássico é latin-1. Sem o `encode(..., "replace")`, um único caractere fora da tabela derrubaria a geração **depois** de o usuário ter esperado a otimização inteira |
| `relatorio_sem_geracoes_nao_explode`            | fechar a janela antes da primeira geração devolve `""`, não um stack trace                                                                                                  |

### `test_benchmarks.py` - a instância fixa (7 testes)

| Teste                                                 | O que garante                                                                                                                                            |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `carregar_devolve_as_48_cidades_na_tela`              | 48 pontos únicos, dentro da área do mapa                                                                                                                 |
| `tour_otimo_e_uma_permutacao_das_cidades`             | a cidade de fechamento duplicada foi removida. Se ficasse, o tour teria 49 pontos e a comparação com o algoritmo seria entre coisas diferentes                  |
| `instancia_e_reprodutivel`                            | o mesmo mapa e o mesmo ótimo em toda execução - o propósito do benchmark                                                                                 |
| `comprimento_otimo_e_positivo`                        | a linha de base existe                                                                                                                                   |
| `frota_e_replicada_ate_caber_a_demanda`               | regressão do erro "Frota subdimensionada": as 48 entregas não cabem na `FROTA` de `config.py`, então o benchmark despacha turnos inteiros da mesma frota |
| `replicacao_preserva_a_capacidade_para_carga_critica` | a replicação mantém a proporção de veículos habilitados                                                                                                  |
| `frota_folgada_nao_e_replicada`                       | cabendo de primeira, a frota sai idêntica a de `config.py`, sem sufixo de turno                                                                          |

---

## Estrutura do projeto

Na raiz ficam apenas o executável e a configuração; o resto é separado por
responsabilidade:

| Caminho               | Responsabilidade                                                                                   |
| --------------------- | -------------------------------------------------------------------------------------------------- |
| `vrp.py`              | ponto de entrada: laço de evolução, desenho e encerramento                                         |
| `config.py`           | **todos** os parâmetros e a frota mockada - único arquivo a se mexer                               |
| `algoritmo_genetico/` | algoritmo genético puro, sem nenhuma regra de negócio                                              |
| `restricoes/`         | regras do VRP hospitalar: frota, entregas, decodificador, custo                                    |
| `visualizacao/`       | desenho do mapa e do gráfico na tela do Pygame                                                     |
| `gemini/`             | integração com o LLM: o `prompt.md`, a chave, o SDK e as retentativas                              |
| `relatorios/`         | consolidação dos números, chamada ao Gemini, montagem do PDF - é onde os PDFs gerados são gravados |
| `benchmarks/`         | instância fixa att48 e o runner que mede o algoritmo                                               |
| `tests/`              | suíte pytest - não abre janela e não chama a API                                                   |

A dependência entre os pacotes corre sempre numa direção só:

```
config.py                    (nao importa nada do projeto)
   ^
algoritmo_genetico/          (nao conhece logistica)
   ^
restricoes/                  (usa o algoritmo + config)
   ^
visualizacao/  gemini/  benchmarks/
                  ^
              relatorios/  (usa gemini/ para o texto)
   ^
vrp.py                       (amarra tudo)
```

`config.py` não importar nada do projeto é proposital: sendo configuração pura,
ele nunca cria dependência circular com os pacotes que o consomem.

---

## 11. Conclusão

O projeto entrega um VRP hospitalar completo resolvido por algoritmo genético,
com visualização ao vivo e relatório executivo automático. Alguns pontos que
valem como conclusão técnica:

Utilizando benchmarks para medir a eficiência, podemos concluir que calibrando o 
algoritmo com pesos relevantes para excessos de carga, limitações de economia e custo
fixo para adição de novos veículos faz com que o algoritmo tenha resultados agradáveis 
de forma relativamente rápida.

Além disso, identificamos que o elitismo é essencial para esse problema e que o order
crossover pode ser um método de cruzamento eficiente para garantir a herança das características do pai nos filhos de forma que não deixemos pra trás nenhum ponto de entrega.

A parametrização sempre vai ser relativa a qual objetivo queremos alcançar com o algoritmo 
genético. A pergunta que fica é: Qual problema queremos resolver? 

- **Menor rota com menor quantidade de veículos?** Precisaremos aumentar o custo fixo da adição de veículo.
- **Menor rota e menor tempo?** Precisaremos reduzir o custo fixo dos veículos de forma que consigamos balancear o custo da distância da rota com a penalidade de quantidade de veículos;
- **Menor tempo?** Reduzir drasticamente o custo fixo de veículos;
- **Garantir entregas em autonomia e capacidade de carga?** Aumentar drasticamente as penalidades por excesso e por distância de rota sobressalente.

