#!/usr/bin/env python3
"""只读收集仓库结构、语言、规则文件和可用质量命令。"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SKIP_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv",
    "node_modules", "vendor", "dist", "build", "target", "coverage",
    ".next", ".nuxt", ".cache", ".coding-memory", "__pycache__",
}

LANGUAGES = {
    ".c": "C", ".cc": "C++", ".cpp": "C++", ".cxx": "C++",
    ".h": "C/C++ Header", ".hpp": "C++", ".cs": "C#", ".dart": "Dart",
    ".go": "Go", ".html": "HTML", ".htm": "HTML", ".css": "CSS",
    ".scss": "SCSS", ".java": "Java", ".js": "JavaScript",
    ".jsx": "JavaScript", ".json": "JSON", ".jsonc": "JSONC",
    ".kt": "Kotlin", ".kts": "Kotlin", ".lisp": "Lisp", ".cl": "Lisp",
    ".md": "Markdown", ".m": "Objective-C", ".mm": "Objective-C++",
    ".py": "Python", ".r": "R", ".sh": "Shell", ".bash": "Shell",
    ".swift": "Swift", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".vim": "Vimscript", ".xml": "XML", ".rs": "Rust",
}

MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "poetry.lock", "uv.lock",
    "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts",
    "gradlew", "gradlew.bat", "mvnw", "mvnw.cmd", "Gemfile", "composer.json",
    "Makefile", "CMakeLists.txt", "pubspec.yaml", "Package.swift",
}

RULE_NAMES = {
    "AGENTS.md", "CONTRIBUTING.md", "CONTRIBUTING", "STYLE.md", "STYLE_GUIDE.md",
    "CODE_OF_CONDUCT.md", "SECURITY.md", "CODEOWNERS", "CLAUDE.md",
    ".editorconfig", ".planning-coding.json",
}


def run_readonly(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=8, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def walk_repository(repo: Path, max_files: int) -> dict[str, Any]:
    language_counts: Counter[str] = Counter()
    manifests: list[str] = []
    rules: list[str] = []
    top_entries: list[str] = []
    scanned = 0
    truncated = False

    for entry in sorted(repo.iterdir(), key=lambda item: item.name.lower()):
        if entry.name not in SKIP_DIRS:
            top_entries.append(entry.name + ("/" if entry.is_dir() else ""))

    for root, dirs, files in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".tox"))
        root_path = Path(root)
        for name in sorted(files):
            scanned += 1
            if scanned > max_files:
                truncated = True
                break
            path = root_path / name
            rel = path.relative_to(repo).as_posix()
            suffix = path.suffix.lower()
            if suffix in LANGUAGES:
                language_counts[LANGUAGES[suffix]] += 1
            if name in MANIFESTS or suffix == ".sln":
                manifests.append(rel)
            if name in RULE_NAMES or name.startswith(("CONTRIBUTING.", "STYLE.")):
                rules.append(rel)
        if truncated:
            break

    return {
        "files_scanned": min(scanned, max_files),
        "scan_truncated": truncated,
        "top_level": top_entries[:80],
        "languages": dict(language_counts.most_common()),
        "manifests": sorted(set(manifests)),
        "rule_files": sorted(set(rules)),
    }


def detect_hints(repo: Path, manifests: list[str]) -> list[str]:
    names = {Path(item).name for item in manifests}
    hints: list[str] = []
    if (repo / ".planning-coding.json").exists():
        hints.append("质量门禁：读取 .planning-coding.json 显式配置")
    if "package.json" in names:
        hints.append("Node.js：检查 package.json scripts 与锁文件")
    if "pyproject.toml" in names or "requirements.txt" in names:
        hints.append("Python：检查 pyproject/pytest/ruff/mypy 配置")
    if "go.mod" in names:
        hints.append("Go：可运行 go test/go vet")
    if "Cargo.toml" in names:
        hints.append("Rust：可运行 cargo fmt/clippy/test")
    if "pom.xml" in names or "mvnw" in names or "mvnw.cmd" in names:
        hints.append("Java Maven：优先使用仓库 wrapper")
    if "build.gradle" in names or "build.gradle.kts" in names:
        hints.append("Java/Kotlin Gradle：优先使用仓库 wrapper")
    if any(name.endswith(".sln") for name in names):
        hints.append(".NET：可运行 dotnet test")
    return hints


def collect(repo: Path, max_files: int) -> dict[str, Any]:
    inventory = walk_repository(repo, max_files)
    branch = run_readonly(["git", "branch", "--show-current"], repo)
    status = run_readonly(["git", "status", "--short"], repo)
    root = run_readonly(["git", "rev-parse", "--show-toplevel"], repo)
    return {
        "repository": str(repo),
        "git": {
            "is_repository": root is not None,
            "root": root,
            "branch": branch,
            "dirty_entries": status.splitlines() if status else [],
        },
        **inventory,
        "quality_hints": detect_hints(repo, inventory["manifests"]),
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = ["# 仓库上下文", "", f"- 路径：`{data['repository']}`"]
    git = data["git"]
    lines.append(f"- Git：{'是' if git['is_repository'] else '否'}")
    if git.get("branch"):
        lines.append(f"- 分支：`{git['branch']}`")
    lines.append(f"- 工作区变更：{len(git['dirty_entries'])} 项")
    suffix = "（已截断）" if data["scan_truncated"] else ""
    lines.append(f"- 扫描文件：{data['files_scanned']} 个{suffix}")
    lines.extend(["", "## 语言", ""])
    if data["languages"]:
        lines.extend(f"- {name}: {count}" for name, count in data["languages"].items())
    else:
        lines.append("- 未识别到源码语言")
    sections = (("规则文件", "rule_files"), ("项目清单", "manifests"), ("质量门禁提示", "quality_hints"))
    for title, key in sections:
        lines.extend(["", f"## {title}", ""])
        values = data[key]
        if values:
            for value in values:
                lines.append(f"- {value}" if key == "quality_hints" else f"- `{value}`")
        else:
            lines.append("- 无")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="只读收集仓库上下文。")
    parser.add_argument("--repo", default=".", help="仓库路径，默认当前目录。")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--max-files", type=int, default=20000, help="最大扫描文件数。")
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"错误：仓库路径不存在或不是目录：{repo}", file=sys.stderr)
        return 2
    if args.max_files < 1:
        print("错误：--max-files 必须大于 0。", file=sys.stderr)
        return 2
    data = collect(repo, args.max_files)
    output = json.dumps(data, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(data)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
