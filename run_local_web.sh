#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "未检测到 uv，请先安装 uv。" >&2
  exit 1
fi

if [ ! -f ".env" ]; then
  echo ".env 不存在，请先配置数据库连接。" >&2
  exit 1
fi

set -a
source .env
set +a

exec uv run --frozen instock-web
