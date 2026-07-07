"""
Extração de conteúdo de artigos de notícias a partir da URL.
"""
from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from newssearch.logger import get_logger

logger = get_logger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def _is_google_url(url: str) -> bool:
    return "google.com" in urlparse(url).netloc


def _extrair_corpo(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "iframe"]):
        tag.decompose()

    artigo = (
        soup.find("article")
        or soup.find("main")
        or soup.find(
            class_=lambda c: c
            and any(x in str(c).lower() for x in ["article", "content", "story", "post-body", "materia"])
        )
    )

    alvo = artigo if artigo else soup
    paragrafos = [
        p.get_text(strip=True) for p in alvo.find_all("p") if len(p.get_text(strip=True)) > 80
    ]

    if not paragrafos:
        return ""
    return "\n\n".join(paragrafos[:5])[:3000]


def _extrair_data_publicacao(soup: BeautifulSoup) -> str | None:
    """Tenta extrair a data de publicação via meta tags comuns (best-effort)."""
    seletores = [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"name": "publish-date"}),
        ("meta", {"name": "date"}),
        ("time", {}),
    ]
    for nome_tag, atributos in seletores:
        tag = soup.find(nome_tag, attrs=atributos)
        if tag:
            valor = tag.get("content") or tag.get("datetime") or tag.get_text(strip=True)
            if valor:
                return valor
    return None


def scrape(job_payload: dict) -> dict:
    """
    Recebe o payload do job (dict com pelo menos `url`) e retorna os dados
    completos do artigo: título, url, fonte, corpo e data de publicação.
    """
    url = job_payload.get("url", "")
    titulo_rss = job_payload.get("titulo", "")
    fonte_rss = job_payload.get("fonte", "")

    if _is_google_url(url):
        raise ValueError(f"URL não resolvida (ainda aponta para o domínio do Google): {url}")

    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    if titulo_rss:
        titulo = titulo_rss
        for sep in [" - ", " | ", " – ", " — "]:
            if sep in titulo:
                titulo = titulo.split(sep)[0].strip()
                break
    else:
        tag_title = soup.find("title")
        titulo = tag_title.get_text(strip=True) if tag_title else "Sem título"
        for sep in [" | ", " - ", " – ", " — "]:
            if sep in titulo:
                titulo = titulo.split(sep)[0].strip()
                break

    corpo = _extrair_corpo(soup)
    fonte = fonte_rss or urlparse(url).netloc
    data_publicacao = _extrair_data_publicacao(soup) or job_payload.get("data_publicacao_rss")

    return {
        "titulo": titulo,
        "url": url,
        "fonte": fonte,
        "corpo": corpo,
        "data_publicacao": data_publicacao,
        "empresa_alvo": job_payload.get("empresa_alvo"),
    }
