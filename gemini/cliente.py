"""
Cliente do Gemini: chave de API, escolha do SDK, cadeia de modelos e retentativas.

A chave da API sai do arquivo .env na raiz do projeto:

    GEMINI_API_KEY=sua-chave

Esse arquivo esta no .gitignore, entao a chave nunca vai parar no repositorio.
Ha um .env.example versionado servindo de modelo. Variavel de ambiente do
sistema (GEMINI_API_KEY ou GOOGLE_API_KEY) tambem funciona e tem precedencia.

Requer: pip install google-genai python-dotenv
(o SDK legado google-generativeai tambem funciona)
"""

import os
import time

import config


class GeminiIndisponivel(Exception):
    """
    O Gemini nao pode ser usado nesta execucao.

    A mensagem descreve o motivo (sem chave, sem SDK, API fora do ar) e e ela
    que aparece no topo do relatorio de contingencia.
    """


def carregar_env() -> None:
    """
    Le o arquivo .env da raiz do projeto e joga as chaves no ambiente.

    Usa python-dotenv se estiver instalado; se nao, faz o parse simples na mao,
    pra nao transformar uma dependencia opcional em erro de execucao. Em nenhum
    dos casos uma variavel de ambiente ja definida no sistema e sobrescrita.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, ".env")
    if not os.path.exists(caminho):
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(caminho)
        return
    except ImportError:
        pass

    with open(caminho, encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))


def obter_api_key(api_key: str = None) -> str:
    """Devolve a chave recebida por parametro, ou a do .env / ambiente."""
    if api_key:
        return api_key
    carregar_env()
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _criar_chamador(api_key: str):
    """
    Escolhe o SDK disponivel e devolve chamar(nome_modelo, prompt) -> texto.

    Tenta primeiro o google-genai (atual) e cai no google-generativeai (legado)
    quando o primeiro nao esta instalado. Os dois ficam atras da mesma interface,
    entao o resto do modulo nao precisa saber qual esta em uso.
    """
    try:
        from google import genai as genai_novo

        cliente = genai_novo.Client(api_key=api_key)

        def chamar(nome_modelo, prompt):
            return cliente.models.generate_content(model=nome_modelo,
                                                   contents=prompt).text

        return chamar
    except ImportError:
        pass
    except Exception as erro:
        raise GeminiIndisponivel(f"falha ao inicializar o Gemini ({erro})")

    try:
        import google.generativeai as genai
    except ImportError:
        raise GeminiIndisponivel("nenhum SDK do Gemini instalado "
                                 "(pip install google-genai)")

    genai.configure(api_key=api_key)

    def chamar(nome_modelo, prompt):
        return genai.GenerativeModel(nome_modelo).generate_content(prompt).text

    return chamar


def gerar_texto(prompt: str, api_key: str = None, modelo: str = None) -> str:
    """
    Envia o prompt ao Gemini e devolve o texto da resposta.

    Duas camadas de resiliencia:

    - cadeia de modelos: comeca pelo modelo pedido e, diante de um 404 (modelo
      indisponivel para aquela chave), passa direto ao proximo dos
      MODELOS_GEMINI_ALTERNATIVOS, sem gastar tentativas;
    - backoff exponencial: 503, 429 e 500 sao temporarios (sobrecarga, limite de
      taxa), entao a chamada e repetida ate TENTATIVAS_GEMINI vezes, esperando
      ESPERA_INICIAL_S x tentativa entre elas. Erro de outra natureza aborta na
      hora, sem insistir a toa.

    Levanta GeminiIndisponivel quando nao ha chave, SDK ou resposta possivel -
    e a mensagem explica o motivo, para quem chamar decidir o plano B.
    """
    chave = obter_api_key(api_key)
    if not chave:
        raise GeminiIndisponivel(
            "GEMINI_API_KEY nao encontrada (copie .env.example para .env)")

    chamar = _criar_chamador(chave)

    modelo = modelo or config.MODELO_GEMINI
    modelos = [modelo] + [m for m in config.MODELOS_GEMINI_ALTERNATIVOS if m != modelo]
    ultimo_erro = None

    for nome_modelo in modelos:
        for tentativa in range(1, config.TENTATIVAS_GEMINI + 1):
            try:
                return chamar(nome_modelo, prompt)
            except Exception as erro:
                ultimo_erro = erro
                texto_erro = str(erro)
                temporario = any(c in texto_erro for c in ("503", "429", "500"))
                indisponivel = "404" in texto_erro

                if indisponivel:
                    print(f"[gemini] Modelo {nome_modelo} indisponivel; tentando o proximo.")
                    break

                if not temporario or tentativa == config.TENTATIVAS_GEMINI:
                    break

                espera = config.ESPERA_INICIAL_S * tentativa
                print(f"[gemini] {nome_modelo} sobrecarregado "
                      f"(tentativa {tentativa}/{config.TENTATIVAS_GEMINI}). "
                      f"Nova tentativa em {espera}s...")
                time.sleep(espera)

        if not any(c in str(ultimo_erro) for c in ("503", "429", "500", "404")):
            break

    raise GeminiIndisponivel(f"falha na chamada ao Gemini ({ultimo_erro})")
