#!/usr/bin/env bash
# Rode este script na raiz do repositório, com a branch "nuvem" ativa
# (git checkout nuvem && git pull antes de rodar).
set -e

echo "1) Removendo código morto (arquitetura paralela não usada por nada)..."
rm -rf src/newssearch/interfaces
rm -rf src/newssearch/lambdas
rm -f src/newssearch/ai/openrouter_classifier.py
rm -f src/newssearch/scraper/http_article_scraper.py
rm -f src/newssearch/storage/supabase_article_repository.py
rm -f src/newssearch/storage/supabase_queue_repository.py

echo "2) Removendo etapa2.patch (artefato commitado por engano)..."
rm -f etapa2.patch

echo "3) Removendo package-lock.json órfão da raiz (não há package.json na raiz)..."
rm -f package-lock.json

echo "4) Corrigindo import quebrado em scripts/run_cleaner.py..."
sed -i.bak 's/from newssearch\.matching\.empresa_matching import mencao_real/from newssearch.matching.empresa_matcher import mencao_real/' scripts/run_cleaner.py
rm -f scripts/run_cleaner.py.bak

echo "5) Tirando do versionamento (mas mantendo local) o banco da fila e o bytecode..."
git rm -r --cached data/newssearch_queue.db > /dev/null 2>&1 || true
find . -type d -name "__pycache__" -not -path "./frontend/*" | while read -r d; do
  git rm -r --cached "$d" > /dev/null 2>&1 || true
done

echo "6) Atualizando .gitignore..."
cat >> .gitignore << 'EOF'
data/
__pycache__/
*.pyc
node_modules/
.next/
EOF

echo "Pronto. Revise com 'git status' e 'git diff --cached', depois:"
echo "  git add -A"
echo "  git commit -m \"limpeza: remove código morto, artefatos commitados por engano e corrige import do run_cleaner\""
echo "  git push"
