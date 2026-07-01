import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def is_google_url(url: str) -> bool:
    return 'google.com' in urlparse(url).netloc


def extrair_corpo(soup: BeautifulSoup) -> str:
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'button', 'iframe']):
        tag.decompose()

    artigo = (
        soup.find('article') or
        soup.find('main') or
        soup.find(class_=lambda c: c and any(
            x in str(c).lower() for x in ['article', 'content', 'story', 'post-body', 'materia']
        ))
    )

    alvo = artigo if artigo else soup
    paragrafos = [
        p.get_text(strip=True)
        for p in alvo.find_all('p')
        if len(p.get_text(strip=True)) > 80
    ]

    if not paragrafos:
        return ''
    return '\n\n'.join(paragrafos[:5])[:3000]


def scrape(mensagem: str) -> dict:
    """
    Aceita JSON (novo formato) ou URL pura (formato legado).
    """
    try:
        dados      = json.loads(mensagem)
        url        = dados.get('url', '')
        titulo_rss = dados.get('titulo', '')
        fonte_rss  = dados.get('fonte', '')
    except (json.JSONDecodeError, TypeError):
        url        = mensagem.strip()
        titulo_rss = ''
        fonte_rss  = ''

    if is_google_url(url):
        raise ValueError(f'URL não resolvida (domínio Google): {url}')

    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    if titulo_rss:
        titulo = titulo_rss
        for sep in [' - ', ' | ', ' – ', ' — ']:
            if sep in titulo:
                titulo = titulo.split(sep)[0].strip()
                break
    else:
        tag_title = soup.find('title')
        titulo = tag_title.get_text(strip=True) if tag_title else 'Sem título'
        for sep in [' | ', ' - ', ' – ', ' — ']:
            if sep in titulo:
                titulo = titulo.split(sep)[0].strip()
                break

    corpo  = extrair_corpo(soup)
    fonte  = fonte_rss if fonte_rss else urlparse(url).netloc

    return {'titulo': titulo, 'url': url, 'fonte': fonte, 'corpo': corpo}