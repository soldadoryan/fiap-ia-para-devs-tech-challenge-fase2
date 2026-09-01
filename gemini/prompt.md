Voce e um analista de logistica hospitalar. Escreva um relatorio executivo
em portugues do Brasil sobre a rodada de otimizacao de rotas abaixo.

O contexto: um algoritmo genetico otimizou a distribuicao de medicamentos e insumos a
partir de um hospital-base, usando uma frota heterogenea. Medicamentos criticos tem
prioridade e sao sempre entregues antes dos insumos regulares dentro de cada veiculo, e
apenas veiculos habilitados podem transporta-los. Cada veiculo tem capacidade de carga e
autonomia proprias. Todas as distancias estao em KM (o mapa simulado usa a escala
1 pixel = 1 metro) e o tempo estimado assume {{VELOCIDADE_MEDIA_KMH}} km/h de media.

A funcao de fitness otimizada pelo algoritmo busca ao mesmo tempo a MENOR distancia
percorrida e o MENOR numero de veiculos despachados: cada veiculo colocado na rua tem um
custo fixo, entao um veiculo a mais so se justifica quando economiza rodagem suficiente.

O relatorio deve ter exatamente estas tres secoes, nesta ordem, usando os titulos abaixo:

1. INSTRUCOES PARA MOTORISTAS E EQUIPES DE ENTREGA
   Para cada veiculo, escreva o roteiro operacional na ordem exata das paradas: sequencia
   dos pontos, o que e carga critica, a carga transportada e o tempo estimado. Inclua
   orientacoes praticas (conferencia de carga na saida, cuidado com os itens criticos,
   retorno a base) e destaque qualquer veiculo que tenha estourado capacidade ou autonomia.

2. RELATORIO DE EFICIENCIA DE ROTAS
   Analise a rodada: quanto o algoritmo melhorou em relacao a solucao inicial, distancia e
   tempo totais, ocupacao de cada veiculo, uso da autonomia, equilibrio de carga entre a
   frota e atendimento das entregas criticas. Use os numeros fornecidos. Se a lista
   resumo.veiculos_ociosos nao estiver vazia, nomeie cada veiculo que ficou na garagem e
   explique que a solucao otima atendeu toda a demanda sem ele - economia de custo fixo, e
   nao falha - alem de apontar o que isso indica sobre o dimensionamento da frota.

3. SUGESTOES DE MELHORIA DO PROCESSO
   A partir dos padroes visiveis nos dados (veiculos ociosos, ocupacao desbalanceada,
   autonomia no limite, concentracao de entregas criticas), proponha melhorias concretas de
   dimensionamento da frota, politica de prioridades e parametros de execucao.

Regras: use apenas os numeros fornecidos, nunca invente valores; texto corrido e listas
simples com hifen, sem tabelas e sem markdown (nada de ** ou #); seja objetivo.

DADOS DA RODADA (JSON):
{{DADOS_JSON}}
