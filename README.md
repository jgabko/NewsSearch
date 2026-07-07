# NewsSearch — Backend (Pipeline Local Monolítica)

Pipeline local de coleta, classificação de sentimento (IA) e persistência de
notícias sobre uma empresa-alvo. Roda inteiramente no seu terminal — sem
microserviços, sem AWS, sem infraestrutura de cloud para a fila.

## Arquitetura

```
Google News RSS ──▶ producer (enqueue) ──▶ fila local (SQLite) ──▶ worker (consumer)
                                                                        │
                                                    scraping do artigo ─┤
                                                    IA (OpenRouter)     ┤─▶ Supabase
                                                    persistência        ┘
```

- **Sem AWS SQS**: a fila é um arquivo SQLite local (`data/newssearch_queue.db`),
  durável, com retry automático e sem custo de infraestrutura.
- **Sem microserviços**: producer, worker, scraper, IA e persistência rodam
  no mesmo processo Python / mesma máquina, orquestrados por scripts simples.

## Estrutura de arquivos

```
NewsSearch/
├── .env.example
├── requirements.txt
├── README.md
├── sql/
│   └── schema.sql                       # schema da tabela no Supabase
├── data/
│   └── newssearch_queue.db              # criado automaticamente (fila local)
├── src/newssearch/
│   ├── config.py                        # configurações via .env
│   ├── logger.py                        # logging centralizado
│   ├── queue/
│   │   └── local_queue.py               # fila local em SQLite (substitui SQS)
│   ├── collector/
│   │   ├── google_news_client.py        # busca notícias no Google News RSS
│   │   └── historical_loader.py         # carga histórica (2 anos, configurável)
│   ├── scraper/
│   │   └── article_scraper.py           # extrai texto completo do artigo
│   ├── ai/
│   │   └── sentiment_classifier.py      # classificação via OpenRouter
│   ├── storage/
│   │   └── supabase_repository.py       # persistência no Supabase
│   └── pipeline/
│       ├── producer.py                  # enfileira notícias coletadas
│       └── consumer_worker.py           # loop: consome -> classifica -> salva
└── scripts/                             # pontos de entrada (CLI)
    ├── run_collect.py                   # coleta pontual/diária
    ├── run_historical_backfill.py       # carga histórica
    └── run_worker.py                    # inicia o worker (consumer)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # preencha SUPABASE_URL, SUPABASE_KEY, OPENROUTER_API_KEY
```

Rode o `sql/schema.sql` no SQL Editor do seu projeto Supabase para criar a
tabela `newssearch_articles`.

## Uso

Abra **dois terminais** (o worker fica rodando em loop consumindo a fila):

**Terminal 1 — worker (sempre ativo):**
```bash
python scripts/run_worker.py
```

**Terminal 2 — alimentar a fila:**

Coleta pontual (notícias recentes):
```bash
python scripts/run_collect.py
python scripts/run_collect.py --empresa "Go Coffee" --max-items 15
```

Carga histórica (retroativa; padrão = últimos 2 anos, configurável):
```bash
# usa HISTORICO_ANOS do .env (padrão 2)
python scripts/run_historical_backfill.py

# ou sobrepõe via CLI
python scripts/run_historical_backfill.py --anos 3
python scripts/run_historical_backfill.py --data-inicio 2023-01-01 --data-fim 2024-01-01 --empresa "Go Coffee"
```

O worker do Terminal 1 vai processar tudo automaticamente: scraping →
classificação de sentimento (IA) → gravação no Supabase.

## O que mudou em relação à versão anterior

| Antes                                   | Agora                                          |
|------------------------------------------|-------------------------------------------------|
| Fila: AWS SQS (`boto3`)                   | Fila local em SQLite (`local_queue.py`)          |
| `api/app.py` (Vercel + RabbitMQ, solto)   | Removido — não fazia parte do fluxo principal    |
| Sem classificação de sentimento           | `ai/sentiment_classifier.py` via OpenRouter      |
| Sem carga histórica                       | `collector/historical_loader.py`, range configurável |
| Nome do projeto: `tech-Pulse`             | `NewsSearch` (tabela, variáveis, logs, módulos)  |

## Variáveis de ambiente

Veja `.env.example` para a lista completa e comentada. As principais:

| Variável | Descrição |
|---|---|
| `SUPABASE_URL`, `SUPABASE_KEY` | Credenciais do projeto Supabase |
| `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | Credenciais/modelo de IA no OpenRouter |
| `EMPRESA_ALVO` | Empresa cujo sentimento está sendo analisado |
| `HISTORICO_ANOS` | Anos retroativos da carga histórica (padrão: 2) |
| `NEWSSEARCH_QUEUE_DB_PATH` | Caminho do arquivo SQLite da fila local |
