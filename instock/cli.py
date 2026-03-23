#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
JOB_ROOT = PACKAGE_ROOT / "job"
WEB_SCRIPT = PACKAGE_ROOT / "web" / "web_service.py"


def _exec_script(script_path: Path, args: list[str]) -> None:
    if not script_path.is_file():
        raise SystemExit(f"脚本不存在: {script_path}")

    os.chdir(PROJECT_ROOT)
    os.execv(sys.executable, [sys.executable, str(script_path), *args])


def web() -> None:
    _exec_script(WEB_SCRIPT, sys.argv[1:])


def job() -> None:
    args = sys.argv[1:]
    script_name = args[0] if args else "execute_daily_job"
    script_args = args[1:] if args else []

    if not script_name.endswith(".py"):
        script_name = f"{script_name}.py"

    _exec_script(JOB_ROOT / script_name, script_args)
