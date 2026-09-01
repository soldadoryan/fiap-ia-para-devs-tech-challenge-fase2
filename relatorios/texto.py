"""
Texto do relatorio: pede ao Gemini e, se ele nao vier, escreve o plano B local.

A integracao com o LLM (prompt, chave, SDK, retentativas) vive no pacote
gemini/. Aqui fica so a decisao de projeto que interessa ao relatorio: o PDF
sempre sai, com ou sem o Gemini.
"""

import config
from gemini import GeminiIndisponivel, gerar_texto, montar_prompt


def _relatorio_local(dados: dict, motivo: str) -> str:
    """
    Texto de contingencia, escrito localmente quando o Gemini nao esta disponivel.

    Garante que o PDF sempre saia, mesmo sem chave de API ou sem internet.
    """
    resumo = dados["resumo"]
    linhas = [
        f"[Relatorio gerado localmente, sem o Gemini: {motivo}]",
        "",
        "1. INSTRUCOES PARA MOTORISTAS E EQUIPES DE ENTREGA",
        "",
    ]

    for veiculo in dados["veiculos"]:
        if veiculo["n_entregas"] == 0:
            linhas.append(f"- {veiculo['nome']}: sem entregas nesta rodada.")
            continue
        linhas.append(f"- {veiculo['nome']}: {veiculo['n_entregas']} paradas, "
                      f"{veiculo['n_entregas_criticas']} criticas, carga "
                      f"{veiculo['carga_transportada']}/{veiculo['capacidade']}, "
                      f"tempo estimado {veiculo['tempo_estimado_min']} min. "
                      f"Sequencia: " +
                      " -> ".join(f"{p['coordenada']}" for p in veiculo["paradas"]))

    linhas += [
        "",
        "2. RELATORIO DE EFICIENCIA DE ROTAS",
        "",
        f"- Geracoes executadas: {resumo['geracoes_executadas']}",
        f"- Fitness inicial: {resumo['fitness_inicial']} / final: {resumo['fitness_final']} "
        f"(melhoria de {resumo['melhoria_percentual']}%)",
        f"- Distancia total: {resumo['distancia_total_km']} km "
        f"({resumo['tempo_total_estimado_min']} min estimados)",
        f"- Veiculos em uso: {resumo['n_veiculos_em_uso']} de {resumo['n_veiculos_frota']}",
    ]
    if resumo["veiculos_ociosos"]:
        linhas.append("- A melhor rota atendeu toda a demanda sem usar a frota inteira. "
                      "Ficaram na garagem: " + ", ".join(resumo["veiculos_ociosos"])
                      + ". Economia de custo fixo; avalie o dimensionamento da frota.")
    linhas += [
        f"- Entregas criticas atendidas: {resumo['entregas_criticas']}",
        "",
        "3. SUGESTOES DE MELHORIA DO PROCESSO",
        "",
        "- Configure a chave GEMINI_API_KEY para obter a analise completa do LLM.",
    ]
    return "\n".join(linhas)


def gerar_texto_relatorio(dados: dict, api_key: str = None,
                          modelo: str = config.MODELO_GEMINI) -> str:
    """
    Pede ao Gemini o texto do relatorio. Cai no relatorio local se algo falhar.
    """
    try:
        return gerar_texto(montar_prompt(dados), api_key=api_key, modelo=modelo)
    except GeminiIndisponivel as erro:
        return _relatorio_local(dados, str(erro))
