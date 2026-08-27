"""run_quality_gate.py 命令安全过滤器的回归测试。"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "run_quality_gate.py"

_spec = importlib.util.spec_from_file_location("run_quality_gate", _SCRIPT)
assert _spec and _spec.loader
_qg = importlib.util.module_from_spec(_spec)
sys.modules["run_quality_gate"] = _qg
_spec.loader.exec_module(_qg)

unsafe_command = _qg.unsafe_command
has_shell_string = _qg.has_shell_string


@pytest.mark.parametrize(
    "command",
    [
        ["bash", "-c", "echo hi"],
        ["sh", "-c", "echo hi"],
        ["zsh", "-c", "echo hi"],
        ["bash", "-lc", "echo hi"],
        ["sh", "-ic", "echo hi"],
        ["bash", "-ec", "echo hi"],
        ["cmd.exe", "/c", "echo hi"],
        ["powershell", "-command", "Write-Host hi"],
        ["powershell", "-c", "Write-Host hi"],
        ["pwsh", "-c", "Write-Host hi"],
    ],
)
def test_shell_string_is_rejected(command):
    assert has_shell_string(command)
    assert unsafe_command(command) == "不允许通过 Shell 字符串间接执行"


@pytest.mark.parametrize(
    "command",
    [
        ["bash", "--version"],
        ["sh", "--help"],
        ["zsh", "--version"],
        ["bash", "script.sh"],
        ["python", "-c", "print(1)"],
        ["echo", "hello"],
    ],
)
def test_non_shell_string_is_allowed(command):
    assert unsafe_command(command) is None


def test_clustered_python_module_install_is_rejected():
    # `python -mpip install ...` 必须与 `python -m pip install ...` 一样被拦截。
    assert unsafe_command(["python3", "-mpip", "install", "requests"]) == "不得安装 Python 依赖"
    assert unsafe_command(["python3", "-m", "pip", "install", "requests"]) == "不得安装 Python 依赖"


def test_plain_module_run_is_still_allowed():
    # 普通的 `python -m pytest` 等不应被误伤。
    assert unsafe_command(["python3", "-m", "pytest"]) is None
    assert unsafe_command(["python3", "-m", "ruff", "check", "."]) is None


def _write_config(tmp_path: Path, command: list[str]) -> Path:
    config = tmp_path / ".planning-coding.json"
    config.write_text(
        json.dumps({"version": 1, "checks": [{"name": "sneaky", "command": command}]}),
        encoding="utf-8",
    )
    return config


def _run_gate(tmp_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--repo", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_end_to_end_clustered_flag_is_rejected(tmp_path):
    marker = tmp_path / "pwned.txt"
    _write_config(tmp_path, ["bash", "-lc", f"echo PWNED > {marker}"])
    result = _run_gate(tmp_path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "不安全" in result.stderr
    assert not marker.exists()


def test_end_to_end_python_module_install_is_rejected(tmp_path):
    _write_config(tmp_path, ["python3", "-mpip", "install", "requests"])
    result = _run_gate(tmp_path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "不安全" in result.stderr
