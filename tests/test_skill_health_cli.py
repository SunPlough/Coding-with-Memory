"""skill_health.py 结构自检的基线测试。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_health_check_passes_on_repo():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "skill_health.py"), "--skill", str(ROOT), "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    for marker in ("frontmatter", "name", "description", "workflow-sections", "local-links", "memory-boundary"):
        assert marker in result.stdout


def test_missing_skill_exits_nonzero(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "skill_health.py"), "--skill", str(empty), "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 1
    assert "SKILL.md" in result.stdout or "SKILL.md" in result.stderr
