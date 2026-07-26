"""
Verificação rigorosa de menção real à empresa alvo em um texto.

Problema que este módulo resolve: para uma empresa com nome composto (ex:
"Go Coffee"), buscar apenas a palavra "Coffee" no texto gera falso-positivo
(qualquer notícia sobre café em geral entra na pipeline e é analisada pela
IA à toa, gastando tokens do OpenRouter). Este módulo exige que TODAS as
palavras do nome apareçam juntas, na ordem, com ou sem espaço/hífen entre
elas, sem diferenciar maiúsculas/minúsculas — e sem casar como substring de
outra palavra (ex: não deixa "Go Coffeeshop" casar com "Go Coffee").

Usado em três pontos da pipeline, todos com o MESMO critério:
  1. collector/producer  -> filtro leve, só no título do RSS
  2. pipeline/consumer_worker -> filtro rigoroso, no título + corpo já raspado
  3. scripts/run_cleaner.py  -> auditoria retroativa dos dados já salvos
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache


def _normalizar(texto: str) -> str:
    """Remove acentos (NFKD) para casar 'menção'/'mencao' e afins."""
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii")


@lru_cache(maxsize=64)
def _compilar_padrao(empresa: str) -> re.Pattern:
    """
    Monta um regex a partir do nome da empresa: exige as palavras do nome
    juntas, na ordem, aceitando espaço/hífen opcional entre elas (cobre
    "Go Coffee", "GoCoffee", "go-coffee", "GO COFFEE" etc.), com fronteira
    de palavra nas duas pontas para não casar como parte de outra palavra.
    """
    palavras = _normalizar(empresa).strip().split()
    partes = [re.escape(p) for p in palavras]
    padrao = r"\b" + r"[\s\-]?".join(partes) + r"\b"
    return re.compile(padrao, re.IGNORECASE)


def mencao_real(texto: str, empresa: str) -> bool:
    """
    Retorna True se `texto` realmente menciona `empresa` pelo nome completo
    (todas as palavras do nome, juntas e na ordem — não só uma palavra
    isolada do nome composto).
    """
    if not texto or not empresa:
        return False

    padrao = _compilar_padrao(empresa)
    return padrao.search(_normalizar(texto)) is not None