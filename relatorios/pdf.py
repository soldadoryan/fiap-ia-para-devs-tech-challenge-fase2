"""Montagem do arquivo PDF: capa, texto do LLM e anexos de conferencia."""

import os
import subprocess
import sys


def _texto_pdf(texto: str) -> str:
    """FPDF classico trabalha em latin-1; troca o que nao couber."""
    return texto.encode("latin-1", "replace").decode("latin-1")


def _escrever(pdf, altura: float, texto: str) -> None:
    """
    Escreve um bloco de texto de largura total.

    O set_x e necessario: depois de um multi_cell o cursor pode ficar deslocado, e
    o fpdf entao reclama que nao ha espaco horizontal para renderizar.
    """
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, altura, texto)


def exportar_pdf(texto: str, dados: dict, caminho: str,
                 imagem_tela: str = None) -> str:
    """
    Monta o PDF: capa com os indicadores, o texto do LLM e o anexo de conferencia
    com as rotas exatas (dados locais, nao gerados pelo modelo).
    """
    from fpdf import FPDF

    resumo = dados["resumo"]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    _escrever(pdf, 10, _texto_pdf("Relatorio de Rotas - Logistica Hospitalar"))
    pdf.set_font("Helvetica", "", 10)
    _escrever(pdf, 6, _texto_pdf(f"Gerado em {dados['gerado_em']}"))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    _escrever(pdf, 8, _texto_pdf("Indicadores da rodada"))
    pdf.set_font("Helvetica", "", 10)
    indicadores = [
        f"Pontos de entrega: {resumo['n_pontos_entrega']}",
        f"Frota: {resumo['n_veiculos_em_uso']} de {resumo['n_veiculos_frota']} veiculos em uso",
        f"Geracoes executadas: {resumo['geracoes_executadas']} "
        f"({resumo['duracao_execucao_s']} s)",
        f"Fitness: {resumo['fitness_inicial']} -> {resumo['fitness_final']} "
        f"({resumo['melhoria_percentual']}% de melhoria)",
        f"Distancia total: {resumo['distancia_total_km']} km "
        f"({resumo['tempo_total_estimado_min']} min estimados)",
        f"Carga transportada: {resumo['carga_total_transportada']} unidades",
        f"Entregas criticas: {resumo['entregas_criticas']}",
    ]
    for linha in indicadores:
        _escrever(pdf, 6, _texto_pdf(f"- {linha}"))
    pdf.ln(2)

    if resumo["veiculos_ociosos"]:
        pdf.set_font("Helvetica", "B", 10)
        _escrever(pdf, 6, _texto_pdf("Frota nao utilizada por completo"))
        pdf.set_font("Helvetica", "", 10)
        _escrever(pdf, 6, _texto_pdf(
            "A melhor rota atendeu toda a demanda sem "
            f"{len(resumo['veiculos_ociosos'])} de {resumo['n_veiculos_frota']} veiculos: "
            + ", ".join(resumo["veiculos_ociosos"]) + ". "
            "O algoritmo otimiza distancia e tamanho da frota ao mesmo tempo, entao "
            "despachar esses veiculos aumentaria o custo sem reduzir rodagem suficiente. "
            "Eles ficam disponiveis como reserva para picos de demanda ou para outro turno."))
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    _escrever(pdf, 6, _texto_pdf(texto))

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    _escrever(pdf, 8, _texto_pdf("Anexo - Roteiro detalhado por veiculo"))
    pdf.ln(2)

    for veiculo in dados["veiculos"]:
        pdf.set_font("Helvetica", "B", 11)
        _escrever(pdf, 7, _texto_pdf(
            f"{veiculo['nome']} - carga {veiculo['carga_transportada']}/{veiculo['capacidade']} "
            f"({veiculo['ocupacao_percentual']}%) - {veiculo['distancia_km']} km de "
            f"{veiculo['autonomia_km']} ({veiculo['uso_autonomia_percentual']}%)"))
        pdf.set_font("Helvetica", "", 9)

        if not veiculo["paradas"]:
            _escrever(pdf, 5, _texto_pdf("   Sem entregas nesta rodada."))
        else:
            _escrever(pdf, 5, _texto_pdf(
                f"   Habilitado para carga critica: "
                f"{'sim' if veiculo['habilitado_carga_critica'] else 'nao'}"))
            for parada in veiculo["paradas"]:
                _escrever(pdf, 5, _texto_pdf(
                    f"   {parada['ordem']:>2}. ({parada['coordenada'][0]}, "
                    f"{parada['coordenada'][1]}) - {parada['prioridade']} - "
                    f"carga {parada['carga']} - "
                    f"{parada['distancia_do_ponto_anterior_km']} km do ponto anterior"))
        pdf.ln(3)

    if imagem_tela and os.path.exists(imagem_tela):
        pdf.add_page(orientation="L")
        pdf.set_font("Helvetica", "B", 13)
        _escrever(pdf, 8, _texto_pdf(
            "Anexo - Melhor rota encontrada e evolucao do fitness"))
        pdf.set_font("Helvetica", "", 9)
        _escrever(pdf, 5, _texto_pdf(
            "Captura da tela do simulador ao final da execucao. A esquerda, a curva de "
            "fitness por geracao (azul) e a quantidade de veiculos despachados pela melhor "
            "solucao de cada geracao (laranja, eixo da direita); a direita, o mapa com a "
            "base (verde), as entregas "
            "criticas (laranja), as regulares (azul claro) e a rota de cada veiculo."))
        pdf.ln(2)
        largura = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.image(imagem_tela, x=pdf.l_margin, y=pdf.get_y(), w=largura)

    pdf.output(caminho)
    return caminho


def _abrir_arquivo(caminho: str) -> None:
    """Abre o PDF no visualizador padrao da maquina (best effort)."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(caminho)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", caminho])
        else:
            subprocess.Popen(["xdg-open", caminho])
    except Exception:
        pass
