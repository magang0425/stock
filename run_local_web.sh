#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  echo ".venv 不存在，请先创建本地虚拟环境。" >&2
  exit 1
fi

if [ ! -f ".env" ]; then
  echo ".env 不存在，请先配置数据库连接。" >&2
  exit 1
fi

source .venv/bin/activate
set -a
source .env
set +a

exec python instock/web/web_service.py
