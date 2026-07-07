"""
Classificação de sentimento das notícias via OpenRouter.

Envia o título + corpo da notícia para um modelo eficiente (padrão:
openai/gpt-4o-mini; também funciona com anthropic/claude-3-haiku) e recebe
de volta se a notícia fala BEM (positivo) ou MAL (negativo) sobre a
empresa analisada.
"""
from __future__ import annotations

import json

import requests

from newssearch.config import get_settings
from newssearch.logger import get_logger

logger = get_logger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

_SYSTEM_PROMPT = """\
Você é um analista de reputação de marca. Sua única tarefa é classificar o \
sentimento de uma notícia em relação a UMA empresa específica.

Responda SOMENTE em JSON válido, sem nenhum texto adicional, no formato:
{"sentimento": "positivo" | "negativo" | "neutro", "justificativa": "<até 20 palavras>"}

Regras:
- "positivo": a notícia fala BEM da empresa (elogios, boas notícias, avanços, conquistas).
- "negativo": a notícia fala MAL da empresa (crítica, escândalo, prejuízo, problema, polêmica).
- "neutro": a notícia apenas menciona a empresa de forma factual, sem tom claramente \
positivo ou negativo. Use este rótulo apenas quando realmente não houver tom definido — \
prefira sempre "positivo" ou "negativo" quando houver qualquer inclinação perceptível.
"""


def _montar_prompt_usuario(empresa: str, titulo: str, corpo: str) -> str:
    return (
        f"Empresa analisada: {empresa}\n\n"
        f"Título da notícia: {titulo}\n\n"
        f"Corpo da notícia:\n{corpo[:3000]}"
    )


def classificar_sentimento(empresa: str, titulo: str, corpo: str) -> dict:
    """
    Retorna {"sentimento": "positivo"|"negativo"|"neutro", "justificativa": str}.

    Em caso de falha na API (timeout, erro HTTP, JSON inválido), retorna
    sentimento "neutro" com a justificativa do erro, para que a notícia
    ainda possa ser salva sem travar a pipeline inteira.
    """
    settings = get_settings()

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _montar_prompt_usuario(empresa, titulo, corpo)},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/jgabko/NewsSearch",
        "X-Title": "NewsSearch",
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        conteudo = resp.json()["choices"][0]["message"]["content"]
        resultado = json.loads(conteudo)

        sentimento = str(resultado.get("sentimento", "neutro")).lower()
        if sentimento not in {"positivo", "negativo", "neutro"}:
            sentimento = "neutro"

        return {
            "sentimento": sentimento,
            "justificativa": resultado.get("justificativa", ""),
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Falha na classificação via OpenRouter: %s", exc)
        return {"sentimento": "neutro", "justificativa": f"Erro na classificação: {exc}"}
