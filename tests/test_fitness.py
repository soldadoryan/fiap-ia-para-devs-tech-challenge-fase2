"""
Testes da funcao de custo, termo a termo.

Cada teste isola um componente do custo e confere o valor exato, com os pesos
fixados pela fixture config_limpo. O ultimo teste guarda a convencao mais
importante do projeto: menor custo = melhor individuo.
"""

import pytest

import config
from restricoes.fitness import calcular_fitness_logistico, resumo_da_frota
from restricoes.roteirizacao import decodificar_rotas, distancia_da_rota
from restricoes.veiculo import Veiculo


def _distancia_total(individuo, entregas, veiculos):
    rotas = decodificar_rotas(individuo, entregas, veiculos)
    return sum(distancia_da_rota(r) for r in rotas)


def test_sem_violacao_o_custo_e_distancia_mais_custo_fixo(cidades, entregas, frota,
                                                          config_limpo):
    rotas = decodificar_rotas(cidades, entregas, frota)
    em_uso = sum(1 for r in rotas if len(r) > 1)
    esperado = (_distancia_total(cidades, entregas, frota)
                + em_uso * config_limpo.CUSTO_FIXO_VEICULO)

    assert calcular_fitness_logistico(cidades, entregas, frota) == pytest.approx(esperado)


def test_veiculo_ocioso_nao_custa_nada(cidades, entregas, config_limpo):
    """O custo fixo e cobrado por veiculo DESPACHADO, nao por veiculo da frota."""
    um = [Veiculo("Grandao", capacidade=999, autonomia=99999, aceita_criticos=True)]
    dois = um + [Veiculo("Ocioso", capacidade=999, autonomia=99999, aceita_criticos=True)]

    assert (calcular_fitness_logistico(cidades, entregas, dois)
            == pytest.approx(calcular_fitness_logistico(cidades, entregas, um)))


def test_excesso_de_carga_soma_a_penalidade_exata(cidades, entregas, config_limpo):
    folgado = [Veiculo("Folgado", capacidade=50, autonomia=99999, aceita_criticos=True)]
    apertado = [Veiculo("Apertado", capacidade=45, autonomia=99999, aceita_criticos=True)]

    diferenca = (calcular_fitness_logistico(cidades, entregas, apertado)
                 - calcular_fitness_logistico(cidades, entregas, folgado))

    assert diferenca == pytest.approx(5 * config_limpo.PENALIDADE_EXCESSO)


def test_excesso_de_autonomia_soma_a_penalidade_exata(cidades, entregas, config_limpo):
    distancia = _distancia_total(
        cidades, entregas,
        [Veiculo("X", capacidade=999, autonomia=99999, aceita_criticos=True)])

    curto = [Veiculo("Curto", capacidade=999, autonomia=distancia - 100,
                     aceita_criticos=True)]
    longo = [Veiculo("Longo", capacidade=999, autonomia=distancia,
                     aceita_criticos=True)]

    diferenca = (calcular_fitness_logistico(cidades, entregas, curto)
                 - calcular_fitness_logistico(cidades, entregas, longo))

    assert diferenca == pytest.approx(100 * config_limpo.PENALIDADE_AUTONOMIA)


def test_peso_equilibrio_cobra_a_diferenca_entre_a_maior_e_a_menor_rota(
        cidades, entregas, frota, config_limpo, monkeypatch):
    """Zerado (padrao) nao muda nada; ligado, soma o desequilibrio da frota."""
    distancias = [distancia_da_rota(r)
                  for r in decodificar_rotas(cidades, entregas, frota)]
    em_uso = [d for d in distancias if d > 0]
    assert len(em_uso) > 1, "cenario precisa de dois veiculos na rua"

    sem_peso = calcular_fitness_logistico(cidades, entregas, frota)

    monkeypatch.setattr(config, "PESO_EQUILIBRIO", 2.0)
    com_peso = calcular_fitness_logistico(cidades, entregas, frota)

    assert com_peso - sem_peso == pytest.approx(2.0 * (max(em_uso) - min(em_uso)))


def test_individuo_vazio_custa_zero(entregas, frota, config_limpo):
    assert calcular_fitness_logistico([], entregas, frota) == 0.0


def test_menor_custo_significa_rota_melhor(entregas, config_limpo):
    """
    A convencao de que todo o resto depende.

    sort_population ordena crescente e selecao_por_roleta usa 1/fitness como
    peso: se um dia o custo virasse "maior = melhor", os dois inverteriam o
    sentido da busca silenciosamente.
    """
    veiculo = [Veiculo("Unico", capacidade=999, autonomia=99999, aceita_criticos=True)]
    entregas_neutras = {c: {"prioridade": "regular", "demanda": 1}
                        for c in [(0, 0), (100, 0), (100, 100), (0, 100)]}

    boa = [(0, 0), (100, 0), (100, 100), (0, 100)]
    ruim = [(0, 0), (100, 100), (100, 0), (0, 100)]

    assert (calcular_fitness_logistico(boa, entregas_neutras, veiculo)
            < calcular_fitness_logistico(ruim, entregas_neutras, veiculo))


def test_resumo_da_frota_marca_estouro(cidades, entregas):
    ok = [Veiculo("Folgado", capacidade=999, autonomia=99999, aceita_criticos=True)]
    estourado = [Veiculo("Apertado", capacidade=1, autonomia=1, aceita_criticos=True)]

    assert "!" not in resumo_da_frota(decodificar_rotas(cidades, entregas, ok),
                                      entregas, ok)
    assert "!" in resumo_da_frota(decodificar_rotas(cidades, entregas, estourado),
                                  entregas, estourado)
