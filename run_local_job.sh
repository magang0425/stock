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

if [ "$#" -eq 0 ]; then
  exec python instock/job/execute_daily_job.py
fi

JOB_SCRIPT="$1"
shift

if [[ "$JOB_SCRIPT" != *.py ]]; then
  JOB_SCRIPT="${JOB_SCRIPT}.py"
fi

JOB_PATH="instock/job/$JOB_SCRIPT"

if [ ! -f "$JOB_PATH" ]; then
  echo "作业脚本不存在: $JOB_PATH" >&2
  exit 1
fi

exec python "$JOB_PATH" "$@"
