#!/usr/bin/env bash
# Скрипт не выполняется автоматически — запустите вручную из каталога backend:
#   cd backend && ./scripts/cleanup_backend.sh
# Он удаляет только безопасные для удаления артефакты (кэши, .pyc, временную sqlite)
# Опционально внизу есть закомментированные строки для удаления дампа и лишних статических файлов.
set -euo pipefail
cwd=$(pwd)
echo "Working dir: $cwd"

echo "-> Удаляем __pycache__ и .pyc файлы"
find . -type d -name "__pycache__" -print -exec rm -rf {} + || true
find . -type f -name "*.pyc" -print -delete || true

echo "-> Удаляем временную sqlite (dev.db) если есть"
if [ -f "dev.db" ]; then
  rm -f dev.db
  echo "  removed dev.db"
else
  echo "  no dev.db"
fi

echo "-> Очищаем static/uploads мелких артефактов (оставлю только .gitkeep если нужен)"
if [ -d "../static/uploads" ]; then
  # удаляем все файлы внутри uploads, но оставляем сам каталог
  find ../static/uploads -type f -maxdepth 1 -print -delete || true
  echo "  cleaned ../static/uploads"
else
  echo "  ../static/uploads not found"
fi

echo "-> Готово. Проверяйте git status прежде чем коммитить изменения."

echo "# Дополнительно (не включено по умолчанию):"
echo "# Удалить дамп базы данных в корне репо (если уверены):"
echo "# rm -f ../kremls_db.dump"
echo "# Удалить директорию alembic/versions (если миграции не нужны):"
echo "# rm -rf backend/alembic/versions"

echo "Если хотите, чтобы я автоматически удалил и другие файлы (дамп, alembic/versions и т.п.) — скажите какие из перечисленных удалить, и я подготовлю команду."
