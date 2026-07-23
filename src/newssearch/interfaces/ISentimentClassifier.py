from abc import ABC, abstractmethod
from newssearch.interfaces.models import ResultadoClassificacao

class ISentimentClassifier(ABC):
    """Contrato para qualquer provedor de classificação de sentimento (OpenRouter, OpenAI, modelo local)."""

    @abstractmethod
    def classificar(self, texto: str, empresa_alvo: str) -> ResultadoClassificacao:
        ...