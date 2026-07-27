<div align="center">

  <h1>NewsSearch — Backend (Pipeline Local Monolítica)</h1>

  <p>
    Pipeline local de coleta, classificação de sentimento (IA) e persistência de
    notícias sobre uma empresa-alvo. Roda inteiramente no seu terminal — sem
    microserviços, sem AWS, sem infraestrutura de cloud para a fila.
  </p>

<!-- Badges -->
<p>
  <a href="https://github.com/jgabko/NewsSearch/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/jgabko/NewsSearch" alt="contributors" />
  </a>
  <a href="">
    <img src="https://img.shields.io/github/last-commit/jgabko/NewsSearch" alt="last update" />
  </a>
  <a href="https://github.com/jgabko/NewsSearch/network/members">
    <img src="https://img.shields.io/github/forks/jgabko/NewsSearch" alt="forks" />
  </a>
  <a href="https://github.com/jgabko/NewsSearch/stargazers">
    <img src="https://img.shields.io/github/stars/jgabko/NewsSearch" alt="stars" />
  </a>
  <a href="https://github.com/jgabko/NewsSearch/issues/">
    <img src="https://img.shields.io/github/issues/jgabko/NewsSearch" alt="open issues" />
  </a>
</p>

<h4>
    <a href="https://github.com/jgabko/NewsSearch/">Ver Demo</a>
  <span> · </span>
    <a href="https://github.com/jgabko/NewsSearch">Documentação</a>
  <span> · </span>
    <a href="https://github.com/jgabko/NewsSearch/issues/">Reportar Bug</a>
  <span> · </span>
    <a href="https://github.com/jgabko/NewsSearch/issues/">Solicitar Feature</a>
  </h4>
</div>

<br />

<!-- Table of Contents -->
# Índice

- [Sobre o Projeto](#sobre-o-projeto)
  * [Arquitetura](#arquitetura)
  * [Tech Stack](#tech-stack)
  * [Features](#features)
  * [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Getting Started](#getting-started)
  * [Pré-requisitos](#pré-requisitos)
  * [Instalação](#instalação)
  * [Rodando o Worker e Coletando Notícias](#rodando-o-worker-e-coletando-notícias)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Roadmap](#roadmap)
- [Licença](#licença)


<!-- About the Project -->
## Sobre o Projeto

O **NewsSearch** é uma pipeline local para coleta, classificação de sentimento
via IA e persistência de notícias sobre uma empresa-alvo. Todo o fluxo roda no
seu terminal, sem depender de microserviços ou infraestrutura de cloud para a
fila de processamento.

<!-- Architecture -->
### Arquitetura

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

<!-- TechStack -->
### Tech Stack

<details>
  <summary>Backend</summary>
  <ul>
    <li><a href="https://www.python.org/">Python</a></li>
    <li><a href="https://www.sqlite.org/">SQLite</a> (fila local)</li>
    <li><a href="https://openrouter.ai/">OpenRouter</a> (classificação de sentimento via IA)</li>
    <li><a href="https://supabase.com/">Supabase</a> (persistência)</li>
  </ul>
</details>

<details>
  <summary>Frontend</summary>
  <ul>
    <li><a href="https://www.typescriptlang.org/">TypeScript</a></li>
    <li>CSS</li>
  </ul>
</details>

<!-- Features -->
### Features

- Coleta de notícias via Google News RSS
- Fila local durável em SQLite, com retry automático (sem AWS SQS)
- Scraping do texto completo do artigo
- Classificação de sentimento das notícias via IA (OpenRouter)
- Persistência dos resultados no Supabase
- Carga histórica configurável (retroativa, por período em anos ou datas)

<!-- Env Variables -->
### Variáveis de Ambiente

Para rodar este projeto, você precisará configurar as seguintes variáveis de
ambiente no seu arquivo `.env` (veja `.env.example` para a lista completa e
comentada):

| Variável                                 | Descrição                                       |
| ----------------------------------------- | ------------------------------------------------ |
| `SUPABASE_URL`, `SUPABASE_KEY`           | Credenciais do projeto Supabase                 |
| `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | Credenciais/modelo de IA no OpenRouter          |
| `EMPRESA_ALVO`                           | Empresa cujo sentimento está sendo analisado    |
| `HISTORICO_ANOS`                         | Anos retroativos da carga histórica (padrão: 2) |
| `NEWSSEARCH_QUEUE_DB_PATH`               | Caminho do arquivo SQLite da fila local         |

<!-- Getting Started -->
## Getting Started

<!-- Prerequisites -->
### Pré-requisitos

Este projeto usa Python e um ambiente virtual (`venv`).

```bash
python -m venv .venv
```

<!-- Installation -->
### Instalação

Clone o projeto

```bash
git clone https://github.com/jgabko/NewsSearch.git
cd NewsSearch
```

Ative o ambiente virtual e instale as dependências

```bash
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Configure as variáveis de ambiente

```bash
cp .env.example .env             # preencha SUPABASE_URL, SUPABASE_KEY, OPENROUTER_API_KEY
```

Rode o `sql/schema.sql` no SQL Editor do seu projeto Supabase para criar a
tabela `newssearch_articles`.

### Rodando o Worker e Coletando Notícias

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

<!-- File Structure -->
## Estrutura de Arquivos

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

<!-- Roadmap -->
## Roadmap

* [x] Pipeline local com fila SQLite (producer/worker)
* [x] Coleta via Google News RSS
* [x] Classificação de sentimento via OpenRouter
* [x] Persistência no Supabase
<!--* [ ] Frontend para visualização dos resultados
* [ ] Dashboard de sentimento por período-->

<!-- License -->
## Licença

Distribuído sem licença definida. Veja LICENSE.txt para mais informações.
