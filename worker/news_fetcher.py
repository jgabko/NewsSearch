import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import boto3
import json
from dotenv import load_dotenv
from googlenewsdecoder import gnewsdecoder

load_dotenv()

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'}

sqs = boto3.client('sqs',
    region_name='us-east-2',
    aws_access_key_id=os.environ['AWS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET']
)
QUEUE_URL = os.environ['SQS_QUEUE_URL']
EMPRESA   = os.environ.get('EMPRESA_BUSCA', 'Go Coffee')


def resolver_url_google(url: str) -> str:
    """Resolve a URL do Google News para a URL real. Funciona no GitHub Actions."""
    try:
        resultado = gnewsdecoder(url, interval=1)
        if resultado.get("status"):
            print(f'  ✓ Resolvida: {resultado["decoded_url"][:80]}')
            return resultado["decoded_url"]
        print(f'  ⚠ gnewsdecoder falhou: {resultado.get("message", "")}')
    except Exception as e:
        print(f'  ⚠ Erro: {e}')

    # Fallback: seguir redirecionamentos HTTP
    try:
        resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        if 'google.com' not in resp.url:
            print(f'  ✓ Redirect: {resp.url[:80]}')
            return resp.url
    except Exception:
        pass

    print('  ✗ Não resolvida, mantendo URL original')
    return url


def buscar_items(empresa: str, max_items: int = 10) -> list[dict]:
    query   = quote(f'{empresa} notícias')
    rss_url = f'https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419'

    resp = requests.get(rss_url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup  = BeautifulSoup(resp.text, 'xml')
    items = soup.find_all('item')

    resultado = []
    for item in items[:max_items]:
        link_tag   = item.find('link')
        title_tag  = item.find('title')
        source_tag = item.find('source')

        if not link_tag:
            continue

        gnews_url = link_tag.get_text(strip=True)
        titulo    = title_tag.get_text(strip=True) if title_tag else ''
        fonte     = source_tag.get_text(strip=True) if source_tag else ''

        print(f'\n→ {titulo[:60]}')
        url_real = resolver_url_google(gnews_url)

        resultado.append({'url': url_real, 'titulo': titulo, 'fonte': fonte})

    return resultado


def enviar_para_fila(items: list[dict]) -> None:
    for item in items:
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(item, ensure_ascii=False))
        print(f'✓ Enfileirado: {item["url"][:80]}')


if __name__ == '__main__':
    print(f'Buscando notícias sobre "{EMPRESA}"...')
    items = buscar_items(EMPRESA)
    print(f'\n{len(items)} itens. Enviando para fila...')
    enviar_para_fila(items)
    print('✓ Concluído')