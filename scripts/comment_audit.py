#!/usr/bin/env python3
"""审计新增或指定源码注释，只报告启发式风险信号。"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {".git", ".coding-memory", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv", "__pycache__"}
SOURCE_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".cs", ".dart", ".go",
    ".html", ".htm", ".css", ".scss", ".java", ".js", ".jsx", ".jsonc",
    ".kt", ".kts", ".lisp", ".cl", ".m", ".mm", ".py", ".r", ".sh",
    ".bash", ".swift", ".ts", ".tsx", ".vim", ".xml",
}
COMMENT_PATTERNS = {
    ".py": ("#",), ".r": ("#",), ".sh": ("#",), ".bash": ("#",),
    ".vim": ('"',), ".lisp": (";",), ".cl": (";",),
    ".html": ("<!--",), ".htm": ("<!--",), ".xml": ("<!--",),
}
DEFAULT_COMMENT_PATTERNS = ("///", "/**", "//", "/*", "*")
MARKER_RE = re.compile(r"\b(TODO|FIXME|HACK)\b(?!\s*\([^\r\n)]+\)\s*:)", re.IGNORECASE)
SECRET_RE = re.compile(
    r"(?i)(api[_ -]?key|access[_ -]?token|secret|password|passwd|private[_ -]?key)"
    r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-=]{8,}"
)
CODE_RE = re.compile(
    r"^\s*(?:if|for|while|return|throw|class|def|function|const|let|var|public|private|protected|import|from)\b|"
    r"[A-Za-z_$][\w$]*\s*\([^)]*\)\s*[;{]?\s*$|\w+\s*=\s*[^=].*;\s*$"
)
LOW_VALUE_RE = re.compile(
    r"^(?:遍历|循环|获取|设置|赋值|返回|调用|创建|初始化|定义|判断|检查|处理|执行|更新|删除|添加|导入|输出)"
    r".{0,24}(?:列表|数组|变量|对象|函数|方法|结果|数据|值|逻辑|操作)?[。.]?$"
)


@dataclass
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    message: str
    excerpt: str


def git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", *args], cwd=repo, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def is_git_repo(repo: Path) -> bool:
    result = git(repo, ["rev-parse", "--is-inside-work-tree"])
    return result is not None and result.returncode == 0 and result.stdout.strip() == "true"


def parse_zero_paths(value: str) -> list[str]:
    return sorted({item for item in value.split("\0") if item})


def changed_paths(repo: Path) -> list[str]:
    paths: set[str] = set()
    for args in (["diff", "--name-only", "-z", "--diff-filter=ACMR"], ["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"], ["ls-files", "--others", "--exclude-standard", "-z"]):
        result = git(repo, list(args))
        if result and result.returncode == 0:
            paths.update(parse_zero_paths(result.stdout))
    return sorted(paths)


def added_line_numbers(repo: Path, relative: str) -> set[int] | None:
    numbers: set[int] = set()
    seen_diff = False
    for cached in (False, True):
        args = ["diff"] + (["--cached"] if cached else []) + ["--unified=0", "--", relative]
        result = git(repo, args)
        if not result or result.returncode != 0:
            continue
        seen_diff = seen_diff or bool(result.stdout)
        for line in result.stdout.splitlines():
            if not line.startswith("@@"):
                continue
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if not match:
                continue
            start, count = int(match.group(1)), int(match.group(2) or "1")
            numbers.update(range(start, start + count))
    tracked = git(repo, ["ls-files", "--error-unmatch", "--", relative])
    if tracked is None or tracked.returncode != 0:
        return None
    return numbers if seen_diff else set()


def source_files(repo: Path, requested: list[str]) -> list[tuple[Path, set[int] | None]]:
    repository_is_git = is_git_repo(repo)
    values = requested or changed_paths(repo) if repository_is_git else requested
    if not values and not repository_is_git:
        for root, dirs, files in os.walk(repo):
            dirs[:] = [item for item in dirs if item not in SKIP_DIRS]
            for name in files:
                path = Path(root) / name
                if path.suffix.lower() in SOURCE_SUFFIXES:
                    values.append(path.relative_to(repo).as_posix())
    selected: list[tuple[Path, set[int] | None]] = []
    for value in sorted(set(values)):
        path = (repo / value).resolve()
        try:
            path.relative_to(repo)
        except ValueError:
            continue
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        numbers = added_line_numbers(repo, path.relative_to(repo).as_posix()) if is_git_repo(repo) and not requested else None
        selected.append((path, numbers))
    return selected


def comment_body(line: str, suffix: str) -> str | None:
    stripped = line.strip()
    patterns = COMMENT_PATTERNS.get(suffix, DEFAULT_COMMENT_PATTERNS)
    for marker in patterns:
        if stripped.startswith(marker):
            body = stripped[len(marker):].strip()
            return body.removesuffix("-->").removesuffix("*/").strip()
    return None


def audit_line(path: str, number: int, body: str, raw: str) -> Iterable[Finding]:
    excerpt = raw.strip()[:240]
    if MARKER_RE.search(body):
        yield Finding("bare-marker", "warning", path, number, "TODO/FIXME/HACK 缺少仓库定义的可追踪引用与说明。", excerpt)
    if SECRET_RE.search(body):
        yield Finding("sensitive-data", "error", path, number, "注释疑似包含凭据或敏感配置，请人工确认并立即移除真实秘密。", excerpt)
    if CODE_RE.search(body) and not body.startswith(("http://", "https://")):
        yield Finding("commented-code", "warning", path, number, "注释疑似保存了旧代码；应删除并依赖版本控制。", excerpt)
    if LOW_VALUE_RE.fullmatch(body) and not any(word in body for word in ("因为", "避免", "否则", "必须", "兼容", "防止")):
        yield Finding("low-value", "info", path, number, "注释可能只是逐行翻译代码，请检查是否包含契约、约束或原因。", excerpt)


def audit(repo: Path, requested: list[str]) -> tuple[list[Finding], list[str], str]:
    findings: list[Finding] = []
    files: list[str] = []
    mode = "指定文件" if requested else "Git 变更行" if is_git_repo(repo) else "非 Git 仓库全量源码"
    for path, numbers in source_files(repo, requested):
        relative = path.relative_to(repo).as_posix()
        files.append(relative)
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, raw in enumerate(lines, 1):
            if numbers is not None and number not in numbers:
                continue
            body = comment_body(raw, path.suffix.lower())
            if body:
                findings.extend(audit_line(relative, number, body, raw))
    return findings, files, mode


def render_markdown(repo: Path, findings: list[Finding], files: list[str], mode: str) -> str:
    mark = chr(96)
    lines = ["# 注释审计", "", f"- 仓库：{mark}{repo}{mark}", f"- 范围：{mode}", f"- 文件：{len(files)} 个", f"- 信号：{len(findings)} 项", ""]
    if not findings:
        lines.append("未发现内置启发式风险信号；仍需人工审查注释的真实性、必要性和时效性。")
        return "\n".join(lines)
    lines += ["| 级别 | 规则 | 位置 | 说明 |", "|---|---|---|---|"]
    for item in findings:
        location = f"{item.path}:{item.line}"
        message = item.message.replace("|", "\\|")
        lines.append(f"| {item.severity} | {item.rule} | {mark}{location}{mark} | {message} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="审计新增或指定源码注释，只报告、不修改。")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--file", action="append", default=[], help="相对仓库路径，可重复使用")
    parser.add_argument("--fail-on", choices=("none", "error", "warning"), default="error")
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"错误：仓库路径不存在或不是目录：{repo}", file=sys.stderr)
        return 2
    findings, files, mode = audit(repo, args.file)
    payload = {"schema_version": 1, "repository": str(repo), "mode": mode, "files": files, "findings": [asdict(item) for item in findings]}
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(repo, findings, files, mode))
    ranks = {"info": 1, "warning": 2, "error": 3}
    threshold = {"none": 99, "warning": 2, "error": 3}[args.fail_on]
    return 1 if any(ranks[item.severity] >= threshold for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
