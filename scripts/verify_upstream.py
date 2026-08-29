#!/usr/bin/env python3
"""Verify the pinned Google Style Guide snapshot used by this skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_REPOSITORY = "google/styleguide"
EXPECTED_REF = "gh-pages"
EXPECTED_COMMIT = "1809c769de31ba388c755ad15dd057a9ba8531fd"
ERROR_MARKERS = (
    b"404: Not Found",
    b"Error 404",
    b"This page could not be found",
)


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 manifest: {path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("manifest 根节点必须是 JSON 对象")
    return manifest


def verify(skill_dir: Path) -> list[str]:
    manifest_path = skill_dir / "references" / "coding-standards" / "upstream-manifest.json"
    manifest = _load_manifest(manifest_path)
    upstream = manifest.get("upstream")
    files = manifest.get("files")
    errors: list[str] = []

    if not isinstance(upstream, dict):
        errors.append("upstream 必须是对象")
        upstream = {}
    if upstream.get("repository") != EXPECTED_REPOSITORY:
        errors.append(f"repository 不是 {EXPECTED_REPOSITORY}")
    if upstream.get("ref") != EXPECTED_REF:
        errors.append(f"ref 不是 {EXPECTED_REF}")
    if upstream.get("commit") != EXPECTED_COMMIT:
        errors.append(f"commit 不是固定提交 {EXPECTED_COMMIT}")
    if upstream.get("license") != "CC BY 3.0 Unported":
        errors.append("许可必须声明为 CC BY 3.0 Unported")
    if not isinstance(files, list) or not files:
        errors.append("files 必须是非空数组")
        return errors

    seen: set[str] = set()
    snapshot_root = skill_dir / "references" / "coding-standards"
    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            errors.append(f"files[{index}] 必须是对象")
            continue
        relative = entry.get("local_path")
        upstream_path = entry.get("path")
        if not isinstance(relative, str) or not isinstance(upstream_path, str):
            errors.append(f"files[{index}] 缺少 path/local_path")
            continue
        if relative in seen:
            errors.append(f"重复的 local_path: {relative}")
        seen.add(relative)
        if not relative.startswith("upstream/google-styleguide/"):
            errors.append(f"快照路径越界: {relative}")
            continue
        file_path = snapshot_root / relative
        try:
            file_path.resolve().relative_to((snapshot_root / "upstream" / "google-styleguide").resolve())
        except ValueError:
            errors.append(f"快照路径越界: {relative}")
            continue
        if not file_path.is_file():
            errors.append(f"缺少快照文件: {relative}")
            continue
        data = file_path.read_bytes()
        expected_size = entry.get("size")
        if expected_size != len(data):
            errors.append(f"大小不一致: {relative} (expected {expected_size}, got {len(data)})")
        expected_sha256 = entry.get("sha256")
        actual_sha256 = hashlib.sha256(data).hexdigest()
        if expected_sha256 != actual_sha256:
            errors.append(f"SHA256 不一致: {relative}")
        expected_blob = entry.get("blob_sha")
        actual_blob = _git_blob_sha(data)
        if expected_blob != actual_blob:
            errors.append(f"Git blob SHA 不一致: {relative}")
        if any(marker in data for marker in ERROR_MARKERS):
            errors.append(f"疑似错误页内容: {relative}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验固定版本的 Google Style Guide 快照")
    parser.add_argument(
        "--skill",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skill 根目录，默认使用当前脚本所在 Skill",
    )
    args = parser.parse_args()
    skill_dir = args.skill.resolve()
    try:
        errors = verify(skill_dir)
    except ValueError as exc:
        print(f"FAILED: {exc}")
        return 1
    if errors:
        print("FAILED: 上游 Google Style Guide 快照校验未通过")
        for error in errors:
            print(f"- {error}")
        return 1
    manifest = skill_dir / "references" / "coding-standards" / "upstream-manifest.json"
    count = len(_load_manifest(manifest)["files"])
    print(f"PASSED: {count} 个固定提交快照文件已通过大小、SHA256 和 Git blob SHA 校验")
    return 0


if __name__ == "__main__":
    sys.exit(main())
