# src/newssearch/ai/openrouter_classifier.py
import requests
import json
from newssearch.interfaces import ISentimentClassifier, ResultadoClassificacao

class OpenRouterClassifier(ISentimentClassifier):
    """Implementação concreta de ISentimentClassifier via API do OpenRouter."""

    def __init__(self, api_key: str, modelo: str):
        self._api_key = api_key
        self._modelo = modelo

    def classificar(self, texto: str, empresa_alvo: str) -> ResultadoClassificacao:
        prompt = self._montar_prompt(texto, empresa_alvo)

        resposta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._modelo,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        resposta.raise_for_status()

        conteudo = resposta.json()["choices"][0]["message"]["content"]
        dados = json.loads(conteudo)
        return ResultadoClassificacao(
            sentimento=dados["sentimento"],
            score=float(dados["score"]),
        )

    def _montar_prompt(self, texto: str, empresa_alvo: str) -> str:
        return (
            f"Classifique o sentimento da notícia abaixo em relação à empresa "
            f"'{empresa_alvo}'. Responda em JSON com as chaves 'sentimento' "
            f"(positivo/negativo/neutro) e 'score' (de -1.0 a 1.0).\n\n"
            f"Notícia:\n{texto[:4000]}"  # limite defensivo de tokens
        )