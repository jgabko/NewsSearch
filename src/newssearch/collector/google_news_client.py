"""
Cliente de coleta de notícias via Google News RSS.

Responsável apenas por BUSCAR e RESOLVER as notícias (sem tocar na fila) —
mantém responsabilidade única. O enfileiramento é feito por
`pipeline/producer.py`, que é usado tanto pela coleta pontual
(`scripts/run_collect.py`) quanto pela carga histórica
(`collector/historical_loader.py`).
"""
from __future__ import annotations

from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from googlenewsdecoder import gnewsdecoder

from newssearch.logger import get_logger

logger = get_logger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"}


def _resolver_url_google(url: str) -> str:
    """Resolve uma URL de redirecionamento do Google News para a URL real da notícia."""
    try:
        resultado = gnewsdecoder(url, interval=1)
        if resultado.get("status"):
            return resultado["decoded_url"]
        logger.warning("gnewsdecoder falhou: %s", resultado.get("message", ""))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Erro ao decodificar URL do Google News: %s", exc)

    try:
        resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        if "google.com" not in resp.url:
            return resp.url
    except Exception:  # noqa: BLE001
        pass

    return url


def buscar_noticias(
    empresa: str,
    max_items: int = 10,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> list[dict]:
    """
    Busca notícias sobre `empresa` no Google News RSS.

    `data_inicio` / `data_fim` (formato 'YYYY-MM-DD') são opcionais e usam a
    sintaxe nativa de busca do Google (`after:` / `before:`), permitindo que
    o módulo de carga histórica busque período por período.
    """
    termos = f"{empresa} notícias"
    if data_inicio:
        termos += f" after:{data_inicio}"
    if data_fim:
        termos += f" before:{data_fim}"

    query = quote(termos)
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    resp = requests.get(rss_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "xml")
    items = soup.find_all("item")

    resultado = []
    for item in items[:max_items]:
        link_tag = item.find("link")
        title_tag = item.find("title")
        source_tag = item.find("source")
        pubdate_tag = item.find("pubDate")

        if not link_tag:
            continue

        gnews_url = link_tag.get_text(strip=True)
        titulo = title_tag.get_text(strip=True) if title_tag else ""
        fonte = source_tag.get_text(strip=True) if source_tag else ""
        data_publicacao = pubdate_tag.get_text(strip=True) if pubdate_tag else None

        logger.info("Resolvendo URL: %s", titulo[:60])
        url_real = _resolver_url_google(gnews_url)

        resultado.append(
            {
                "url": url_real,
                "titulo": titulo,
                "fonte": fonte,
                "data_publicacao_rss": data_publicacao,
                "empresa_alvo": empresa,
            }
        )

    return resultado
