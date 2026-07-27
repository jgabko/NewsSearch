from dataclasses import dataclass
from datetime import date

@dataclass
class NoticiaBruta:
    titulo: str
    url: str
    fonte: str
    data_publicacao: date | None

@dataclass
class ResultadoClassificacao:
    sentimento: str      # ex: "positivo", "negativo", "neutro"
    score: float