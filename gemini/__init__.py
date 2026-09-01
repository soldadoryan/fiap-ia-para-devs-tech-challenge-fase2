"""
Integracao com o Gemini: tudo que fala com a API do LLM mora aqui.

Nenhum outro pacote do projeto conhece SDK, chave de API ou retentativa - eles
so pedem um texto. Isso mantem o LLM como um detalhe substituivel: trocar de
modelo, de provedor ou desligar a integracao nao encosta no algoritmo nem no
relatorio.

- prompt.md   -> o prompt em si, fora do codigo, para ser ajustado sem Python
- prompt.py   -> carrega o prompt.md e substitui os marcadores
- cliente.py  -> chave de API, escolha do SDK, cadeia de modelos e backoff

Ponto importante de projeto: o Gemini recebe os numeros JA CALCULADOS pelo
projeto e apenas escreve o texto. Ele narra e analisa, nunca calcula.
"""

from gemini.cliente import GeminiIndisponivel, carregar_env, gerar_texto, obter_api_key
from gemini.prompt import carregar_modelo_de_prompt, montar_prompt

__all__ = ["GeminiIndisponivel", "carregar_env", "gerar_texto", "obter_api_key",
           "carregar_modelo_de_prompt", "montar_prompt"]
