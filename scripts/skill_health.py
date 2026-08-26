#!/usr/bin/env python3
"""对 Coding with Memory 做确定性的结构和边界健康检查。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def check(name: str, passed: bool, detail: str, severity: str = "error") -> dict[str, Any]:
    return {"name": name, "status": "passed" if passed else severity, "detail": detail}


def load_skill(skill_root: Path) -> tuple[str, list[dict[str, Any]]]:
    path = skill_root / "SKILL.md"
    if not path.is_file():
        return "", [check("skill-file", False, "缺少 SKILL.md")]
    text = path.read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []
    frontmatter = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    results.append(check("frontmatter", frontmatter is not None, "YAML frontmatter 存在" if frontmatter else "缺少有效 frontmatter"))
    if frontmatter:
        block = frontmatter.group(1)
        name = re.search(r"^name:\s*([^\n]+)$", block, re.MULTILINE)
        description = re.search(r"^description:\s*(.+)$", block, re.MULTILINE)
        results.append(check("name", bool(name and re.fullmatch(r"[a-z0-9-]+", name.group(1).strip())), "name 使用 hyphen-case"))
        results.append(check("description", bool(description and len(description.group(1).strip()) >= 40), "description 包含具体触发信息"))
    required_sections = ("选择工作流", "建立上下文", "计划与实现", "验证", "Memory", "交付格式")
    missing = [section for section in required_sections if section not in text]
    results.append(check("workflow-sections", not missing, "核心章节齐全" if not missing else "缺少：" + ", ".join(missing)))
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    missing_links = []
    for link in links:
        if link.startswith(("http://", "https://", "#")):
            continue
        target = (skill_root / link.split("#", 1)[0]).resolve()
        if not target.is_file():
            missing_links.append(link)
    results.append(check("local-links", not missing_links, "本地链接可解析" if not missing_links else "缺失：" + ", ".join(missing_links)))
    failure_signal_groups = (("失败", "异常"), ("回滚", "恢复"), ("不得", "严禁"), ("停止", "停下", "暂停"), ("未运行", "未发现"))
    failure_encoding = all(any(signal in text for signal in group) for group in failure_signal_groups)
    results.append(check("failure-encoding", failure_encoding, "包含失败、边界和回滚规则", "warning"))
    results.append(check("evidence", all(signal in text for signal in ("验证", "命令", "证据")), "包含可追溯验证要求"))
    memory_guard = "候选未经批准不得" in text and any(value in text for value in ("不得改变代码规范", "不得用偏好降低"))
    results.append(check("memory-boundary", memory_guard, "Memory 与强制规范隔离"))
    prompts_path = skill_root / "assets" / "evolution" / "test-prompts.json"
    prompt_error = ""
    prompt_sets: set[str] = set()
    try:
        prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        if not isinstance(prompts, list) or not prompts:
            prompt_error = "测试提示词必须是非空数组"
        else:
            prompt_sets = {item.get("set") for item in prompts if isinstance(item, dict)}
            if any(not isinstance(item, dict) or not all(item.get(key) for key in ("id", "set", "prompt", "expected")) for item in prompts):
                prompt_error = "测试提示词缺少 id/set/prompt/expected"
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        prompt_error = str(exc)
    prompts_valid = not prompt_error and {"development", "holdout"}.issubset(prompt_sets)
    results.append(check("evolution-prompts", prompts_valid, "包含 development 与 holdout 提示词" if prompts_valid else prompt_error or "缺少 development 或 holdout 集"))
    return text, results


def render(results: list[dict[str, Any]], format_name: str, skill_root: Path) -> str:
    payload = {"schema_version": 1, "skill": str(skill_root), "checks": results}
    if format_name == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2)
    lines = ["# Skill 健康检查", "", f"- Skill：`{skill_root}`", "", "| 检查 | 状态 | 说明 |", "|---|---|---|"]
    labels = {"passed": "通过", "warning": "警告", "error": "失败"}
    for item in results:
        lines.append(f"| {item['name']} | {labels[item['status']]} | {item['detail']} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 Coding with Memory 的结构、链接和自进化边界。")
    parser.add_argument("--skill", default=".")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    root = Path(args.skill).expanduser().resolve()
    _, results = load_skill(root)
    print(render(results, args.format, root))
    return 1 if any(item["status"] == "error" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
