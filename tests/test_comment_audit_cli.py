"""comment_audit.py 注释审计的基线测试：只报告、不修改。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(repo: Path, *extra):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "comment_audit.py"), "--repo", str(repo), "--format", "json", *extra],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_audit_reports_findings_without_modifying(tmp_path):
    target = tmp_path / "sample.py"
    original = "# TODO: 完成此处逻辑\n"
    target.write_text(original, encoding="utf-8")
    result = _run(tmp_path, "--file", "sample.py", "--fail-on", "none")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert isinstance(data["findings"], list)
    assert target.read_text(encoding="utf-8") == original


def test_fail_on_error_exits_nonzero(tmp_path):
    # sensitive-data 属于 error 级：注释中的疑似凭据应让门禁以 1 退出。
    target = tmp_path / "sample.py"
    target.write_text('# api_key = "supersecret123456"\n', encoding="utf-8")
    result = _run(tmp_path, "--file", "sample.py", "--fail-on", "error")
    assert result.returncode == 1
