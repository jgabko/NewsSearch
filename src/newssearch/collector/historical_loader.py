# src/newssearch/collector/historical_loader.py
from datetime import date, timedelta
from newssearch.interfaces import INewsSource, IQueueRepository

class HistoricalLoader:
    """Orquestra o backfill em janelas pequenas, usando o cursor persistido."""

    def __init__(self, fonte: INewsSource, fila: IQueueRepository, cursor_repo):
        self._fonte = fonte
        self._fila = fila
        self._cursor_repo = cursor_repo

    def processar_proxima_janela(
        self, empresa_alvo: str, dias_por_janela: int = 7
    ) -> dict:
        cursor = self._cursor_repo.buscar_ou_criar(empresa_alvo)

        if cursor["status"] == "concluido":
            return {"status": "ja_concluido"}

        inicio_janela = cursor["ultima_data_processada"] or cursor["data_inicio"]
        fim_janela = min(inicio_janela + timedelta(days=dias_por_janela), cursor["data_fim"])

        noticias = self._fonte.buscar_por_periodo(empresa_alvo, inicio_janela, fim_janela)
        for noticia in noticias:
            self._fila.enfileirar(noticia, empresa_alvo)

        concluido = fim_janela >= cursor["data_fim"]
        self._cursor_repo.atualizar(
            empresa_alvo,
            ultima_data_processada=fim_janela,
            status="concluido" if concluido else "em_andamento",
        )

        return {
            "janela": f"{inicio_janela} a {fim_janela}",
            "coletadas": len(noticias),
            "concluido": concluido,
        }