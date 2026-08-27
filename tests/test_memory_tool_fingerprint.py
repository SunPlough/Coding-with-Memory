"""memory_tool.py 指纹与脱敏顺序的回归测试。"""

from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "memory_tool.py"

_spec = importlib.util.spec_from_file_location("memory_tool", _SCRIPT)
assert _spec and _spec.loader
_mt = importlib.util.module_from_spec(_spec)
sys.modules["memory_tool"] = _mt
_spec.loader.exec_module(_mt)

init = _mt.init
add_entry = _mt.add_entry


def _args(**overrides):
    values = dict(
        category="pattern",
        summary="db password=supersecret123 here",
        trigger="",
        action="",
        domain=None,
        scope="repository",
        language="zh-CN",
        evidence=["cli"],
        confidence=0.6,
        source="manual",
        effect=[],
        review_after=None,
    )
    values.update(overrides)
    return Namespace(**values)


def _add(repo: Path, **overrides):
    return add_entry(repo, _args(**overrides))


def test_distinct_secrets_are_not_deduplicated(tmp_path):
    init(tmp_path)
    first = _add(tmp_path, summary="db password=supersecret123 here")
    second = _add(tmp_path, summary="db password=DIFFERENTsecret99 here")
    assert first["created"] is True
    # 两者仅密钥不同，脱敏后摘要相同，但原始文本不同，不应被当作重复丢弃。
    assert second["created"] is True
    assert first["entry"]["id"] != second["entry"]["id"]
    assert first["entry"]["fingerprint"] != second["entry"]["fingerprint"]


def test_identical_summary_is_still_deduplicated(tmp_path):
    init(tmp_path)
    first = _add(tmp_path, summary="use ruff for linting")
    second = _add(tmp_path, summary="use ruff for linting")
    assert first["created"] is True
    assert second["created"] is False
    assert second["duplicate_of"] == first["entry"]["id"]


def test_stored_summary_is_redacted(tmp_path):
    init(tmp_path)
    result = _add(tmp_path, summary="db password=supersecret123 here", evidence=["email=alice@example.com"])
    stored = result["entry"]
    assert "supersecret123" not in stored["summary"]
    assert "[REDACTED]" in stored["summary"]
    assert "alice@example.com" not in json.dumps(stored["evidence"], ensure_ascii=False)
