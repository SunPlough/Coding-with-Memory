#!/usr/bin/env python3
"""管理项目本地、可审计且不会覆盖工程规范的 Memory。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterator

MEMORY_DIR = ".coding-memory"
CATEGORIES = ("preference", "decision", "pattern", "incident")
FILES = {
    "preference": "preferences.jsonl",
    "decision": "decisions.jsonl",
    "pattern": "patterns.jsonl",
    "incident": "incidents.jsonl",
}
STATUSES = ("candidate", "approved", "rejected", "deprecated")
EFFECTS = (
    "communication_language",
    "planning_granularity",
    "tool_preference",
    "interaction_pace",
    "report_format",
)
TRACE_EVENTS = ("plan", "decision", "retrieval", "tool", "change", "test", "feedback", "result")
SOURCES = ("explicit-feedback", "repeated-choice", "success-path", "failure-analysis", "manual")
DOMAINS = ("communication", "planning", "tool", "delivery", "decision", "pattern", "incident")
SECRET_RE = re.compile(
    r"(?i)(api[_ -]?key|access[_ -]?token|secret|password|passwd|private[_ -]?key)"
    r"\s*[:=]\s*(['\"]?)[^\s,'\"]{6,}\2"
)
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
HOME_RE = re.compile(r"(?i)(?:[A-Z]:\\Users\\|/home/|/Users/)[^\\/\s]+")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def redact(value: str) -> str:
    value = SECRET_RE.sub(lambda match: match.group(1) + "=[REDACTED]", value)
    value = EMAIL_RE.sub("[EMAIL]", value)
    return HOME_RE.sub("[USER_HOME]", value)


def redact_list(values: list[str]) -> list[str]:
    return [redact(value.strip()) for value in values if value.strip()]


def memory_root(repo: Path) -> Path:
    return repo / MEMORY_DIR


@contextmanager
def lock(root: Path, timeout: float = 5.0) -> Iterator[None]:
    lock_path = root / ".write.lock"
    deadline = time.monotonic() + timeout
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError("Memory 正被其他进程写入，请稍后重试。")
            time.sleep(0.05)
    try:
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.close(descriptor)
        descriptor = None
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        lock_path.unlink(missing_ok=True)


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    line = json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    values: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSONL 损坏：{path.name}:{number}：{exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL 条目必须是对象：{path.name}:{number}")
        values.append(value)
    return values


def ensure_initialized(repo: Path) -> Path:
    root = memory_root(repo)
    if not (root / "metadata.json").is_file():
        raise ValueError("尚未初始化 Memory，请先运行 init。")
    return root


def init(repo: Path) -> dict[str, Any]:
    root = memory_root(repo)
    root.mkdir(parents=False, exist_ok=True)
    metadata = root / "metadata.json"
    created = not metadata.exists()
    if created:
        metadata.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "storage": "append-only-events",
                    "default_retrieval_status": "approved",
                    "preference_effects": list(EFFECTS),
                    "created_at": now(),
                },
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
    ignore = root / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n!.gitignore\n", encoding="utf-8")
    for filename in (*FILES.values(), "transitions.jsonl", "traces.jsonl"):
        (root / filename).touch(exist_ok=True)
    return {"created": created, "path": str(root), "schema_version": 1}


def all_entries(root: Path) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for category, filename in FILES.items():
        for entry in read_jsonl(root / filename):
            entry.setdefault("category", category)
            values.append(entry)
    return values


def current_entries(root: Path) -> list[dict[str, Any]]:
    entries = {entry["id"]: dict(entry) for entry in all_entries(root) if "id" in entry}
    for event in read_jsonl(root / "transitions.jsonl"):
        entry = entries.get(event.get("memory_id"))
        if entry:
            entry["status"] = event.get("to_status", entry.get("status"))
            entry["status_updated_at"] = event.get("timestamp")
            entry["last_transition"] = event.get("transition_id")
    return sorted(entries.values(), key=lambda item: item.get("created_at", ""))


def fingerprint(category: str, scope: str, summary: str) -> str:
    normalized = " ".join(summary.lower().split())
    raw = f"{category}\0{scope.lower()}\0{normalized}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def validate_review_after(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("review_after 必须使用 YYYY-MM-DD。") from exc
    return value


def add_entry(repo: Path, args: argparse.Namespace) -> dict[str, Any]:
    root = ensure_initialized(repo)
    summary = redact(args.summary.strip())
    if not summary:
        raise ValueError("summary 不能为空。")
    evidence = redact_list(args.evidence)
    if not evidence:
        raise ValueError("至少提供一条 evidence。")
    if not 0 <= args.confidence <= 1:
        raise ValueError("confidence 必须在 0 到 1 之间。")
    trigger, action = args.trigger.strip(), args.action.strip()
    if bool(trigger) != bool(action):
        raise ValueError("trigger 和 action 必须同时提供或同时省略。")
    if args.domain and not trigger:
        raise ValueError("domain 需要与 trigger 和 action 一起提供。")
    allowed_domains = {
        "preference": {"communication", "planning", "tool", "delivery"},
        "decision": {"decision"},
        "pattern": {"pattern"},
        "incident": {"incident"},
    }
    if args.domain and args.domain not in allowed_domains[args.category]:
        raise ValueError(f"domain {args.domain} 不适用于 {args.category}。")
    if args.category == "preference" and not args.effect:
        raise ValueError("preference 必须声明至少一个允许影响的 effect。")
    if args.category != "preference" and args.effect:
        raise ValueError("effect 只适用于 preference。")
    key = fingerprint(args.category, args.scope, summary)
    supersedes: str | None = None
    for existing in current_entries(root):
        if existing.get("fingerprint") != key:
            continue
        if existing.get("status") in {"candidate", "approved"}:
            return {"created": False, "duplicate_of": existing["id"], "entry": existing}
        supersedes = existing["id"]
    entry = {
        "schema_version": 1,
        "id": "mem-" + uuid.uuid4().hex[:12],
        "category": args.category,
        "summary": summary,
        "trigger": redact(trigger) if trigger else None,
        "action": redact(action) if action else None,
        "domain": args.domain,
        "scope": redact(args.scope.strip()),
        "language": args.language,
        "evidence": evidence,
        "confidence": args.confidence,
        "status": "candidate",
        "source": args.source,
        "allowed_effects": sorted(set(args.effect)) if args.category == "preference" else [],
        "guardrail": "must_not_override_engineering_standards" if args.category == "preference" else None,
        "review_after": validate_review_after(args.review_after),
        "created_at": now(),
        "fingerprint": key,
        "supersedes": supersedes,
    }
    with lock(root):
        append_jsonl(root / FILES[args.category], entry)
    return {"created": True, "entry": entry}


def add_trace(repo: Path, args: argparse.Namespace) -> dict[str, Any]:
    root = ensure_initialized(repo)
    if not args.evidence:
        raise ValueError("轨迹至少需要一条 evidence。")
    event = {
        "schema_version": 1,
        "trace_id": "trace-" + uuid.uuid4().hex[:12],
        "task_id": redact(args.task_id),
        "event": args.event,
        "summary": redact(args.summary),
        "evidence": redact_list(args.evidence),
        "outcome": args.outcome,
        "timestamp": now(),
    }
    with lock(root):
        append_jsonl(root / "traces.jsonl", event)
    return event


def transition(repo: Path, args: argparse.Namespace) -> dict[str, Any]:
    root = ensure_initialized(repo)
    entries = {entry["id"]: entry for entry in current_entries(root)}
    entry = entries.get(args.memory_id)
    if not entry:
        raise ValueError(f"未找到 Memory：{args.memory_id}")
    current, target = entry["status"], args.status
    allowed = {
        "candidate": {"approved", "rejected", "deprecated"},
        "approved": {"deprecated"},
        "rejected": set(),
        "deprecated": set(),
    }
    if target not in allowed.get(current, set()):
        raise ValueError(f"不允许从 {current} 转换到 {target}。")
    if target == "approved" and args.actor not in {"human", "replay"}:
        raise ValueError("批准必须来自 human 或 replay。")
    if target == "approved" and entry["category"] == "preference" and args.actor != "human":
        raise ValueError("用户偏好只能由 human 明确批准。")
    if target == "approved" and args.actor == "replay" and entry["category"] != "pattern":
        raise ValueError("replay 只能批准经过重复验证的 pattern。")
    if not args.reason.strip() or not args.evidence:
        raise ValueError("状态转换必须提供 reason 和 evidence。")
    event = {
        "schema_version": 1,
        "transition_id": "transition-" + uuid.uuid4().hex[:12],
        "memory_id": args.memory_id,
        "from_status": current,
        "to_status": target,
        "actor": args.actor,
        "reason": redact(args.reason.strip()),
        "evidence": redact_list(args.evidence),
        "timestamp": now(),
    }
    with lock(root):
        append_jsonl(root / "transitions.jsonl", event)
    return event


def query_entries(repo: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    root = ensure_initialized(repo)
    query = args.query.lower().strip()
    values = []
    for entry in current_entries(root):
        if args.category and entry.get("category") != args.category:
            continue
        if not args.all_statuses and entry.get("status") != args.status:
            continue
        haystack = json.dumps(entry, ensure_ascii=False).lower()
        if query and query not in haystack:
            continue
        values.append(entry)
    return values


def build_index(repo: Path) -> dict[str, Any]:
    root = ensure_initialized(repo)
    entries = current_entries(root)
    grouped = {status: [] for status in STATUSES}
    for entry in entries:
        grouped.setdefault(entry.get("status", "candidate"), []).append(entry)
    index = {
        "schema_version": 1,
        "generated_at": now(),
        "source": "append-only-jsonl",
        "counts": {key: len(value) for key, value in grouped.items()},
        "approved": grouped["approved"],
        "review_queue": grouped["candidate"],
    }
    temporary = root / "index.json.tmp"
    temporary.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(root / "index.json")
    return index


def output(value: Any, format_name: str) -> None:
    if format_name == "json":
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return
    if isinstance(value, list):
        if not value:
            print("未找到符合条件的 Memory。")
            return
        for entry in value:
            print(f"- [{entry.get('status')}] {entry.get('id')} {entry.get('category')}：{entry.get('summary')}")
        return
    print(json.dumps(value, ensure_ascii=False, indent=2))


def add_query_parser(subparsers: Any, name: str) -> None:
    parser = subparsers.add_parser(name, help="检索 Memory，默认仅返回 approved")
    parser.add_argument("--query", default="")
    parser.add_argument("--category", choices=CATEGORIES)
    parser.add_argument("--status", choices=STATUSES, default="approved")
    parser.add_argument("--all-statuses", action="store_true")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="管理项目本地、可审计的 Coding Memory。")
    root.add_argument("--repo", default=".")
    root.add_argument("--format", choices=("json", "text"), default="json")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="初始化 .coding-memory")

    add = commands.add_parser("add", aliases=["propose"], help="追加候选 Memory")
    add.add_argument("--category", choices=CATEGORIES, required=True)
    add.add_argument("--summary", required=True)
    add.add_argument("--trigger", default="")
    add.add_argument("--action", default="")
    add.add_argument("--domain", choices=DOMAINS)
    add.add_argument("--scope", default="repository")
    add.add_argument("--language", default="zh-CN")
    add.add_argument("--evidence", action="append", default=[], required=True)
    add.add_argument("--confidence", type=float, default=0.6)
    add.add_argument("--source", choices=SOURCES, default="manual")
    add.add_argument("--effect", action="append", choices=EFFECTS, default=[])
    add.add_argument("--review-after")

    trace = commands.add_parser("trace", help="追加任务轨迹")
    trace.add_argument("--task-id", required=True)
    trace.add_argument("--event", choices=TRACE_EVENTS, required=True)
    trace.add_argument("--summary", required=True)
    trace.add_argument("--evidence", action="append", default=[], required=True)
    trace.add_argument("--outcome", choices=("success", "failure", "uncertain"), required=True)

    add_query_parser(commands, "list")
    add_query_parser(commands, "search")

    change = commands.add_parser("transition", help="追加状态转换事件")
    change.add_argument("memory_id")
    change.add_argument("--status", choices=("approved", "rejected", "deprecated"), required=True)
    change.add_argument("--actor", choices=("human", "replay", "agent"), required=True)
    change.add_argument("--reason", required=True)
    change.add_argument("--evidence", action="append", default=[], required=True)
    commands.add_parser("index", aliases=["compact"], help="重建派生索引，保留全部原始事件")
    return root


def main() -> int:
    args = parser().parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        print(f"错误：项目路径不存在或不是目录：{repo}", file=sys.stderr)
        return 2
    try:
        if args.command == "init":
            value = init(repo)
        elif args.command in {"add", "propose"}:
            value = add_entry(repo, args)
        elif args.command == "trace":
            value = add_trace(repo, args)
        elif args.command in {"list", "search"}:
            value = query_entries(repo, args)
        elif args.command == "transition":
            value = transition(repo, args)
        else:
            value = build_index(repo)
    except (ValueError, OSError, TimeoutError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    output(value, args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
