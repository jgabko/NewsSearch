from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

@dataclass
class NoticiaBruta:
    titulo: str
    url: str
    fonte: str
    data_publicacao: date | None

class INewsSource(ABC):
    """Contrato para qualquer fonte de notícias (Google News RSS, Bing News, etc.)"""

    @abstractmethod
    def buscar(self, empresa_alvo: str, max_itens: int) -> list[NoticiaBruta]:
        ...

    @abstractmethod
    def buscar_por_periodo(
        self, empresa_alvo: str, data_inicio: date, data_fim: date
    ) -> list[NoticiaBruta]:
        ...