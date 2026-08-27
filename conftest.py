"""pytest 共享工具：以模块形式加载 scripts/ 下的脚本。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"


def load_script(name: str):
    """加载 scripts/<name>.py 为模块并返回，供单元测试直接调用其函数。"""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader, f"无法定位脚本：{SCRIPTS / (name + '.py')}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
