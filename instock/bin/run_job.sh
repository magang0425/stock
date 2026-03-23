#!/bin/sh

cd /data/InStock
exec uv run --frozen instock-job "$@"
