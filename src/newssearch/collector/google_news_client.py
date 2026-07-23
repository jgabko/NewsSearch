# src/newssearch/collector/google_news_source.py
import feedparser
from datetime import date
from newssearch.interfaces import INewsSource, NoticiaBruta

class GoogleNewsSource(INewsSource):
    """Implementação concreta de INewsSource usando o RSS do Google News."""

    BASE_URL = "https://news.google.com/rss/search"

    def buscar(self, empresa_alvo: str, max_itens: int) -> list[NoticiaBruta]:
        feed_url = f"{self.BASE_URL}?q={empresa_alvo}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(feed_url)
        return [self._to_noticia(entry) for entry in feed.entries[:max_itens]]

    def buscar_por_periodo(self, empresa_alvo, data_inicio, data_fim) -> list[NoticiaBruta]:
        query = f"{empresa_alvo} after:{data_inicio} before:{data_fim}"
        feed_url = f"{self.BASE_URL}?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(feed_url)
        return [self._to_noticia(entry) for entry in feed.entries]

    def _to_noticia(self, entry) -> NoticiaBruta:
        return NoticiaBruta(
            titulo=entry.title,
            url=entry.link,
            fonte="google_news_rss",
            data_publicacao=self._parse_data(entry.get("published")),
        )

    def _parse_data(self, published_str: str | None) -> date | None:
        # parsing defensivo — RSS às vezes vem sem a data
        ...