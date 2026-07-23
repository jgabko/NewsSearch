"""
Cleaner: remove do Supabase as notícias que NÃO mencionam a empresa alvo
de verdade — usando o MESMO critério rígido do resto da pipeline
(`empresa_matcher.mencao_real`, aplicado no collector e no worker).

Isso cobre tanto os registros antigos, salvos antes do filtro rígido
existir, quanto qualquer notícia que passe pelas etapas anteriores por
algum motivo (ex: filtro rodou com uma variação diferente do nome).

Critério de verificação, por linha:
  1. Se houver `corpo` salvo: verifica menção real em título + corpo
     (mesma função usada no worker antes de chamar a IA).
  2. Se `corpo` estiver vazio (registros antigos que não guardaram o
     texto completo): cai para o fallback antigo — procura o padrão
     "sem menção" (configurável) na justificativa que a IA escreveu.

Uso:
    # roda em todas as empresas presentes na tabela
    python scripts/run_cleaner.py

    # roda só para uma empresa específica
    python scripts/run_cleaner.py --empresa "Go Coffee"

    # só mostra o que seria apagado, sem apagar de fato
    python scripts/run_cleaner.py --dry-run

    # ajusta o padrão do fallback (usado só quando não há corpo salvo)
    python scripts/run_cleaner.py --padrao-fallback "não menciona"
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from newssearch.logger import get_logger  # noqa: E402
from newssearch.matching.empresa_matching import mencao_real  # noqa: E402
from newssearch.storage.supabase_repository import (  # noqa: E402
    deletar_noticias_por_id,
    listar_noticias,
)

logger = get_logger(__name__)


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower()


def encontrar_sem_mencao(noticias: list[dict], padrao_fallback: str) -> list[dict]:
    """
    Retorna as notícias que não passam no critério de menção real.
    Cada item devolvido ganha uma chave extra `_motivo` explicando por que
    foi marcado, só para deixar o log claro.
    """
    padrao_fallback_normalizado = _normalizar(padrao_fallback)
    encontradas = []

    for noticia in noticias:
        empresa = noticia.get("empresa_alvo")
        if not empresa:
            continue

        corpo = noticia.get("corpo") or ""
        titulo = noticia.get("titulo") or ""

        if corpo.strip():
            texto_completo = f"{titulo}\n{corpo}"
            if not mencao_real(texto_completo, empresa):
                noticia["_motivo"] = "conteúdo (título+corpo) não menciona a empresa"
                encontradas.append(noticia)
            continue

        # Sem corpo salvo: fallback no texto da justificativa da IA.
        justificativa = noticia.get("sentimento_justificativa") or ""
        if padrao_fallback_normalizado in _normalizar(justificativa):
            noticia["_motivo"] = "sem corpo salvo; justificativa da IA indica falta de menção"
            encontradas.append(noticia)

    return encontradas


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove notícias que não mencionam de fato a empresa alvo."
    )
    parser.add_argument(
        "--empresa",
        type=str,
        default=None,
        help="Filtra por empresa_alvo. Sem esse argumento, varre todas as empresas na tabela.",
    )
    parser.add_argument(
        "--padrao-fallback",
        type=str,
        default="sem menção",
        help=(
            'Trecho a procurar em sentimento_justificativa, usado só quando a '
            'notícia não tem corpo salvo (default: "sem menção").'
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Só lista o que seria apagado, sem apagar nada no Supabase.",
    )
    args = parser.parse_args()

    logger.info(
        'Verificando menção real da empresa%s (critério: título+corpo, com fallback na justificativa)...',
        f' "{args.empresa}"' if args.empresa else "s (todas as empresas)",
    )
    noticias = listar_noticias(empresa=args.empresa)
    logger.info("%d notícias carregadas para análise.", len(noticias))

    encontradas = encontrar_sem_mencao(noticias, args.padrao_fallback)

    if not encontradas:
        logger.info("Nenhuma notícia sem menção real à empresa encontrada. Nada a fazer.")
        return

    logger.info("%d notícias marcadas para remoção:", len(encontradas))
    for noticia in encontradas:
        logger.info(
            "  id=%s | empresa=%s | titulo=%s | motivo=%s",
            noticia.get("id"),
            noticia.get("empresa_alvo"),
            (noticia.get("titulo") or "")[:80],
            noticia.get("_motivo"),
        )

    if args.dry_run:
        logger.info("--dry-run ativo: nada foi apagado.")
        return

    ids = [n["id"] for n in encontradas]
    total_apagado = deletar_noticias_por_id(ids)
    logger.info("%d notícias apagadas do Supabase.", total_apagado)


if __name__ == "__main__":
    main()