"""
Relatorio executivo em PDF gerado por LLM (Gemini) ao final da otimizacao.

Fluxo:

    rotas otimizadas -> dados.montar_dados_execucao() -> numeros da rodada
                     -> texto.gerar_texto_relatorio() -> Gemini escreve o texto
                     -> pdf.exportar_pdf()            -> PDF salvo e aberto

Ponto importante de projeto: o LLM recebe os dados JA CALCULADOS e so escreve o
texto. Distancias, cargas e percentuais nunca sao inventados por ele - eles vao
tambem para um anexo do PDF, montado localmente, que serve de conferencia.
"""

import os
from datetime import datetime
from typing import Dict, List, Sequence

import config
from restricoes.veiculo import Veiculo
from relatorios.dados import montar_dados_execucao
from relatorios.pdf import _abrir_arquivo, exportar_pdf
from relatorios.texto import gerar_texto_relatorio


def gerar_relatorio_final(cities_locations: List[tuple], entregas: Dict[tuple, dict],
                          veiculos: Sequence[Veiculo], best_solution: List[tuple],
                          best_fitness_values: List[float], duracao_segundos: float,
                          pasta_saida: str = None, abrir: bool = True,
                          api_key: str = None, modelo: str = None,
                          imagem_tela: str = None) -> str:
    """
    Ponto de entrada usado pelo vrp.py quando a simulacao termina.

    Monta os dados, pede o texto ao Gemini, salva o PDF na maquina e o abre.
    Devolve o caminho do arquivo gerado.
    """
    if not best_solution or not best_fitness_values:
        print("[relatorio] Nada a relatar: nenhuma geracao foi executada.")
        return ""

    print("\n[relatorio] Consolidando os dados da rodada...")
    dados = montar_dados_execucao(cities_locations, entregas, veiculos,
                                  best_solution, best_fitness_values, duracao_segundos)

    print("[relatorio] Solicitando o texto ao Gemini...")
    texto = gerar_texto_relatorio(dados, api_key=api_key,
                                  modelo=modelo or config.MODELO_GEMINI)

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta = pasta_saida or os.path.join(raiz, config.PASTA_RELATORIOS)
    os.makedirs(pasta, exist_ok=True)
    nome = f"relatorio_rotas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho = os.path.join(pasta, nome)

    exportar_pdf(texto, dados, caminho, imagem_tela=imagem_tela)
    print(f"[relatorio] PDF salvo em: {caminho}")

    if abrir:
        _abrir_arquivo(caminho)

    return caminho
