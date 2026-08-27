"""collect_context.py 只读收集仓库上下文的基线测试。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*extra):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "collect_context.py"), "--repo", str(ROOT), "--format", "json", *extra],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_json_structure_and_identity():
    result = _run()
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["repository"] == str(ROOT)
    assert data["git"]["is_repository"] is True
    assert isinstance(data["files_scanned"], int)
    assert "languages" in data
    assert "manifests" in data
    assert "rule_files" in data


def test_invalid_repo_exits_nonzero(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "collect_context.py"), "--repo", str(tmp_path / "missing"), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode != 0
