from abc import ABC, abstractmethod
from newssearch.interfaces.models import NoticiaBruta

class IQueueRepository(ABC):
    """Contrato para a fila (tabela news_queue no Supabase)."""

    @abstractmethod
    def enfileirar(self, noticia: NoticiaBruta, empresa_alvo: str) -> None:
        ...

    @abstractmethod
    def buscar_lote_por_status(self, status: str, limite: int) -> list[dict]:
        ...

    @abstractmethod
    def atualizar_status(self, item_id: int, novo_status: str, **campos_extra) -> None:
        ...

    @abstractmethod
    def registrar_falha(self, item_id: int, erro: str) -> None:
        ...