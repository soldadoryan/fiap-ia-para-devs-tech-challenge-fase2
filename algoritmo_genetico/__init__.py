"""
Nucleo do algoritmo genetico: operadores puros, sem nenhuma regra de negocio.

Nada aqui sabe o que e um hospital, um veiculo ou uma entrega. Este pacote
manipula individuos genericos - listas de pontos (x, y) sem repeticao - e por
isso serve a qualquer problema de roteirizacao.

- avaliacao.py  -> distancia entre pontos e ordenacao da populacao
- populacao.py  -> cria a populacao inicial
- selecao.py    -> escolhe os pais
- cruzamento.py -> combina dois pais e gera um filho
- mutacao.py    -> sacode o filho para manter diversidade
"""
