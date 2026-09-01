"""
Testes da consolidacao dos numeros e da montagem do PDF.

O modulo dados.py e a UNICA fonte de numeros do relatorio: o Gemini so narra o
que sai daqui. Se estes valores estiverem errados, o relatorio inteiro mente -
inclusive o anexo de conferencia, que deveria servir justamente para pegar isso.
"""

import copy

import pytest

from algoritmo_genetico.avaliacao import calculate_distance
from relatorios import gerar_relatorio_final
from relatorios.dados import montar_dados_execucao
from relatorios.pdf import exportar_pdf
from restricoes.roteirizacao import decodificar_rotas, distancia_da_rota
from restricoes.veiculo import Veiculo, km


@pytest.fixture
def dados(cidades, entregas, frota, config_limpo):
    return montar_dados_execucao(cidades, entregas, frota, cidades,
                                 [100.0, 80.0, 50.0], duracao_segundos=1.5)


def test_resumo_bate_com_as_rotas(dados, cidades, entregas, frota):
    rotas = decodificar_rotas(cidades, entregas, frota)
    em_uso = sum(1 for r in rotas if len(r) > 1)

    assert dados["resumo"]["n_pontos_entrega"] == len(cidades) - 1
    assert dados["resumo"]["n_veiculos_frota"] == len(frota)
    assert dados["resumo"]["n_veiculos_em_uso"] == em_uso
    assert dados["resumo"]["geracoes_executadas"] == 3
    assert dados["resumo"]["carga_total_transportada"] == 50


def test_melhoria_percentual(dados):
    assert dados["resumo"]["fitness_inicial"] == 100.0
    assert dados["resumo"]["fitness_final"] == 50.0
    assert dados["resumo"]["melhoria_percentual"] == pytest.approx(50.0)


def test_distancia_total_e_a_soma_dos_veiculos(dados):
    soma = sum(v["distancia_km"] for v in dados["veiculos"])

    assert dados["resumo"]["distancia_total_km"] == pytest.approx(soma)


def test_veiculos_ociosos_sao_nomeados(cidades, entregas, config_limpo):
    frota = [Veiculo("Trabalhador", capacidade=999, autonomia=99999,
                     aceita_criticos=True),
             Veiculo("Parado", capacidade=999, autonomia=99999, aceita_criticos=True)]
    dados = montar_dados_execucao(cidades, entregas, frota, cidades, [10.0], 1.0)

    assert dados["resumo"]["veiculos_ociosos"] == ["Parado"]
    assert dados["resumo"]["n_veiculos_em_uso"] == 1


def test_paradas_seguem_a_ordem_da_rota(dados, cidades, entregas, frota):
    rotas = decodificar_rotas(cidades, entregas, frota)

    for veiculo_dados, rota in zip(dados["veiculos"], rotas):
        coordenadas = [p["coordenada"] for p in veiculo_dados["paradas"]]
        assert coordenadas == [[int(c[0]), int(c[1])] for c in rota[1:]]

        if veiculo_dados["paradas"]:
            ordens = [p["ordem"] for p in veiculo_dados["paradas"]]
            assert ordens == list(range(1, len(ordens) + 1))


def test_primeira_parada_mede_a_distancia_desde_a_base(dados, cidades, entregas, frota):
    rotas = decodificar_rotas(cidades, entregas, frota)
    primeira_rota = next(r for r in rotas if len(r) > 1)
    veiculo_dados = next(v for v in dados["veiculos"] if v["paradas"])

    esperado = km(calculate_distance(primeira_rota[0], primeira_rota[1]))

    assert veiculo_dados["paradas"][0]["distancia_do_ponto_anterior_km"] == \
        pytest.approx(round(esperado, 2))


def test_ocupacao_e_uso_de_autonomia_em_percentual(dados):
    for veiculo in dados["veiculos"]:
        esperado = 100.0 * veiculo["carga_transportada"] / veiculo["capacidade"]
        assert veiculo["ocupacao_percentual"] == pytest.approx(round(esperado, 1))


def test_escala_e_tempo(cidades, entregas, config_limpo):
    """1 pixel = 1 metro, 1000 px = 1 km, e 1 km a 60 km/h leva 1 minuto."""
    frota = [Veiculo("Reto", capacidade=999, autonomia=99999, aceita_criticos=True)]
    ida_e_volta = [(0, 0), (500, 0)]
    demandas = {c: {"prioridade": "regular", "demanda": 1} for c in ida_e_volta}

    dados = montar_dados_execucao(ida_e_volta, demandas, frota, ida_e_volta, [1.0], 1.0)

    assert dados["resumo"]["distancia_total_km"] == pytest.approx(1.0)
    assert dados["resumo"]["tempo_total_estimado_min"] == pytest.approx(1.0)


def test_exportar_pdf_grava_arquivo(dados, tmp_path):
    caminho = tmp_path / "relatorio.pdf"

    exportar_pdf("Texto do relatorio.", dados, str(caminho))

    assert caminho.exists()
    assert caminho.stat().st_size > 0


def test_exportar_pdf_aceita_acento(dados, tmp_path):
    """
    O FPDF classico e latin-1: o texto passa por encode(..., 'replace').

    Sem isso um unico caractere fora da tabela derrubaria a geracao do PDF no
    fim da execucao, depois de o usuario ja ter esperado a otimizacao inteira.
    """
    com_acento = copy.deepcopy(dados)
    com_acento["veiculos"][0]["nome"] = "Ambulância refrigerada"
    caminho = tmp_path / "acentuado.pdf"

    exportar_pdf("Relatório com acentuação e emoji ✔", com_acento, str(caminho))

    assert caminho.stat().st_size > 0


def test_relatorio_sem_geracoes_nao_explode(cidades, entregas, frota, capsys):
    """Fechar a janela antes da primeira geracao nao pode virar stack trace."""
    assert gerar_relatorio_final(cidades, entregas, frota, [], [], 0.0) == ""
    assert "Nada a relatar" in capsys.readouterr().out
