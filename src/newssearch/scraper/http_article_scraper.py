# src/newssearch/scraper/http_article_scraper.py
import requests
from bs4 import BeautifulSoup
from newssearch.interfaces import IScraper

class HttpArticleScraper(IScraper):
    """Implementação concreta de IScraper via requests + BeautifulSoup."""

    def __init__(self, timeout_segundos: int = 10):
        self._timeout = timeout_segundos

    def extrair_conteudo(self, url: str) -> str:
        resposta = requests.get(url, timeout=self._timeout, headers={
            "User-Agent": "Mozilla/5.0 (compatible; NewsSearchBot/1.0)"
        })
        resposta.raise_for_status()

        soup = BeautifulSoup(resposta.content, "html.parser")
        paragrafos = soup.find_all("p")
        return "\n".join(p.get_text(strip=True) for p in paragrafos)