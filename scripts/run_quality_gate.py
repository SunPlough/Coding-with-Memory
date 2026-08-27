#!/usr/bin/env python3
"""发现并执行可审计的项目质量门禁。"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CONFIG_NAME = ".planning-coding.json"
MAX_OUTPUT = 12000


@dataclass
class Check:
    name: str
    command: list[str]
    cwd: str = "."
    timeout_seconds: int = 300
    required: bool = True
    source: str = "auto"


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 JSON：{path}：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON 根节点必须是对象：{path}")
    return value


def safe_cwd(repo: Path, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("cwd 必须是字符串")
    target = (repo / value).resolve()
    try:
        relative = target.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"cwd 超出仓库：{value}") from exc
    if not target.is_dir():
        raise ValueError(f"cwd 不存在：{value}")
    return relative.as_posix() or "."


def split_short_flags(arg: str) -> set[str]:
    # 将 "-lc" 这类组合短选项拆成 "-l" 与 "-c"，避免精确白名单漏判。
    lowered = arg.lower()
    if re.fullmatch(r"-[a-z][a-z]+", lowered):
        return {f"-{char}" for char in lowered[1:]}
    return {lowered}


def module_after_m(arg: str) -> str | None:
    # 解析 `-m` 与其后的模块名，兼容 `-m pip` 与 `-mpip` 两种写法。
    lowered = arg.lower()
    if lowered == "-m" or re.fullmatch(r"-m[a-z_][a-z0-9_.-]*", lowered):
        module = lowered[2:]
        return module or "-m"
    return None


def has_shell_string(command: list[str]) -> bool:
    # 组合短选项（例如 bash -lc、sh -ic）等价于 -c，不能用精确白名单遗漏。
    executable = Path(command[0]).name.lower() if command else ""
    flags = {item.lower() for item in command[1:]}
    shells = {"sh", "bash", "zsh", "cmd", "cmd.exe", "powershell", "pwsh"}
    if executable not in shells:
        return False
    for flag in flags:
        expanded = split_short_flags(flag)
        if executable in {"cmd", "cmd.exe"} and flag.startswith("/"):
            # cmd.exe 的 `/c`（以及 `/c` 后接参数）都表示执行后续字符串。
            if re.fullmatch(r"/[a-z]*c[a-z]*.*", flag):
                return True
            continue
        if "-c" in expanded or flag == "/c":
            return True
        if executable in {"powershell", "pwsh"} and flag == "-command":
            return True
    return False


def unsafe_command(command: list[str]) -> str | None:
    if not command or not all(isinstance(item, str) and item for item in command):
        return "command 必须是非空字符串数组"
    if has_shell_string(command):
        return "不允许通过 Shell 字符串间接执行"
    executable = Path(command[0]).name.lower()
    args = {item.lower() for item in command[1:]}
    if executable in {"pip", "pip3"} and "install" in args:
        return "不得安装 Python 依赖"
    if executable.startswith("python") and "install" in args:
        # 兼容 `python -m pip install ...` 与 `python -mpip install ...`。
        modules = {module_after_m(item) for item in command[1:]}
        if "pip" in modules or "-m" in args and "pip" in args:
            return "不得安装 Python 依赖"
    if executable in {"uv", "uv.exe"} and {"pip", "install"}.issubset(args):
        return "不得安装 Python 依赖"
    if executable in {"npm", "npm.cmd", "pnpm", "pnpm.cmd", "yarn", "yarn.cmd"}:
        if args & {"install", "i", "ci", "add", "remove", "uninstall", "update", "upgrade"}:
            return "不得修改 JavaScript 依赖"
    if executable in {"apt", "apt-get", "brew", "choco", "winget"}:
        return "不得安装系统依赖"
    if executable == "git" and args & {"clean", "reset", "checkout", "restore"}:
        return "不得执行可能覆盖工作区的 Git 命令"
    if executable in {"rm", "rmdir", "del", "erase", "remove-item"}:
        return "质量门禁不得删除文件或目录"
    if executable in {"prettier", "eslint", "biome", "clang-format"} and args & {"--fix", "--write", "-w", "-i"}:
        return "格式化或 Lint 必须使用检查模式"
    if executable == "black" and "--check" not in args:
        return "Black 必须带 --check"
    if executable == "gofmt" and "-w" in args:
        return "gofmt 不得带 -w"
    if executable == "cargo" and "fmt" in args and "--check" not in args:
        return "cargo fmt 必须带 --check"
    if executable == "dotnet" and "format" in args and "--verify-no-changes" not in args:
        return "dotnet format 必须带 --verify-no-changes"
    return None


def script_is_unsafe(script: str) -> bool:
    text_value = f" {script.lower()} "
    markers = (
        " --fix", " --write", "prettier --write", "eslint --fix",
        "gofmt -w", "clang-format -i",
        " npm install", " npm ci", " pnpm install", " yarn install",
    )
    if any(marker in text_value for marker in markers):
        return True
    if "ruff format" in text_value and "--check" not in text_value:
        return True
    if re.search(r"(?:^|[;&| ]+)black(?:\.exe)?\s", text_value) and "--check" not in text_value:
        return True
    return False


def configured_script(repo: Path, check: Check) -> str | None:
    executable_name = Path(check.command[0]).name.lower()
    if executable_name not in {"npm", "npm.cmd", "pnpm", "pnpm.cmd", "yarn", "yarn.cmd"}:
        return None
    arguments = check.command[1:]
    script_name: str | None = None
    if len(arguments) >= 2 and arguments[0] in {"run", "run-script"}:
        script_name = arguments[1]
    elif arguments and executable_name.startswith(("pnpm", "yarn")):
        script_name = arguments[0]
    if not script_name:
        return None
    scripts = package_scripts(repo / check.cwd)
    return scripts.get(script_name)


def config_checks(repo: Path, timeout: int) -> list[Check] | None:
    path = repo / CONFIG_NAME
    if not path.is_file():
        return None
    data = load_json(path)
    if data.get("version") != 1 or not isinstance(data.get("checks"), list):
        raise ValueError(f"{CONFIG_NAME} 必须包含 version=1 和 checks 数组")
    checks: list[Check] = []
    for index, item in enumerate(data["checks"], 1):
        if not isinstance(item, dict) or item.get("enabled", True) is False:
            continue
        name, command = item.get("name"), item.get("command")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"checks[{index}].name 必须是非空字符串")
        if not isinstance(command, list) or not all(isinstance(v, str) and v for v in command):
            raise ValueError(f"checks[{index}].command 必须是非空字符串数组")
        seconds = item.get("timeout_seconds", timeout)
        if not isinstance(seconds, int) or not 1 <= seconds <= 3600:
            raise ValueError(f"checks[{index}].timeout_seconds 必须在 1 到 3600 之间")
        check = Check(
            name=name.strip(), command=command,
            cwd=safe_cwd(repo, item.get("cwd", ".")), timeout_seconds=seconds,
            required=bool(item.get("required", True)), source="config",
        )
        reason = unsafe_command(check.command)
        script = configured_script(repo, check)
        if script is not None and script_is_unsafe(script):
            reason = "项目脚本包含安装、自动修复或写入型格式化命令"
        if reason:
            raise ValueError(f"门禁‘{check.name}’不安全：{reason}")
        checks.append(check)
    return checks


def executable(name: str) -> str | None:
    return shutil.which(name)


def package_scripts(repo: Path) -> dict[str, str]:
    path = repo / "package.json"
    if not path.is_file():
        return {}
    try:
        value = load_json(path).get("scripts", {})
    except ValueError:
        return {}
    if not isinstance(value, dict):
        return {}
    return {key: item for key, item in value.items() if isinstance(key, str) and isinstance(item, str)}


def node_checks(repo: Path, timeout: int) -> list[Check]:
    scripts = package_scripts(repo)
    if not scripts:
        return []
    if (repo / "pnpm-lock.yaml").exists() and executable("pnpm"):
        runner = "pnpm"
    elif (repo / "yarn.lock").exists() and executable("yarn"):
        runner = "yarn"
    elif executable("npm"):
        runner = "npm"
    else:
        return []
    checks = []
    for name in ("lint", "typecheck", "type-check", "check", "test", "test:unit", "build"):
        script = scripts.get(name)
        if isinstance(script, str) and not script_is_unsafe(script):
            checks.append(Check(f"Node.js {name}", [runner, "run", name], timeout_seconds=timeout))
    return checks


def python_checks(repo: Path, timeout: int) -> list[Check]:
    if not ((repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists()):
        return []
    checks: list[Check] = []
    tools: dict[str, Any] = {}
    pyproject = repo / "pyproject.toml"
    if pyproject.is_file():
        try:
            value = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            candidate = value.get("tool", {}) if isinstance(value, dict) else {}
            tools = candidate if isinstance(candidate, dict) else {}
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            tools = {}
    if executable("ruff") and ("ruff" in tools or (repo / "ruff.toml").exists() or (repo / ".ruff.toml").exists()):
        checks += [
            Check("Python Ruff", ["ruff", "check", "."], timeout_seconds=timeout),
            Check("Python Ruff format", ["ruff", "format", "--check", "."], timeout_seconds=timeout),
        ]
    if executable("black") and "black" in tools:
        checks.append(Check("Python Black", ["black", "--check", "."], timeout_seconds=timeout))
    if executable("mypy") and ((repo / "mypy.ini").exists() or "mypy" in tools):
        checks.append(Check("Python mypy", ["mypy", "."], timeout_seconds=timeout))
    if executable("pytest") and ("pytest" in tools or any((repo / name).exists() for name in ("tests", "test", "pytest.ini"))):
        checks.append(Check("Python pytest", ["pytest", "-q"], timeout_seconds=timeout))
    return checks


def auto_checks(repo: Path, timeout: int) -> list[Check]:
    checks = node_checks(repo, timeout) + python_checks(repo, timeout)
    if (repo / "go.mod").is_file() and executable("go"):
        checks += [Check("Go vet", ["go", "vet", "./..."], timeout_seconds=timeout), Check("Go test", ["go", "test", "./..."], timeout_seconds=timeout)]
    if (repo / "Cargo.toml").is_file() and executable("cargo"):
        checks += [
            Check("Rust format", ["cargo", "fmt", "--all", "--", "--check"], timeout_seconds=timeout),
            Check("Rust clippy", ["cargo", "clippy", "--all-targets"], timeout_seconds=timeout),
            Check("Rust test", ["cargo", "test"], timeout_seconds=timeout),
        ]
    if (repo / "pom.xml").is_file():
        wrapper = repo / ("mvnw.cmd" if os.name == "nt" else "mvnw")
        mvn = str(wrapper) if wrapper.is_file() else executable("mvn")
        if mvn:
            checks.append(Check("Maven test", [mvn, "test"], timeout_seconds=timeout))
    if (repo / "build.gradle").is_file() or (repo / "build.gradle.kts").is_file():
        wrapper = repo / ("gradlew.bat" if os.name == "nt" else "gradlew")
        gradle = str(wrapper) if wrapper.is_file() else executable("gradle")
        if gradle:
            checks.append(Check("Gradle test", [gradle, "test"], timeout_seconds=timeout))
    if list(repo.glob("*.sln")) and executable("dotnet"):
        checks.append(Check(".NET test", ["dotnet", "test", "--no-restore"], timeout_seconds=timeout))
    unique, seen = [], set()
    for check in checks:
        key = tuple(check.command)
        if key not in seen and unsafe_command(check.command) is None:
            seen.add(key)
            unique.append(check)
    return unique


def shorten(value: str) -> str:
    return value if len(value) <= MAX_OUTPUT else value[:MAX_OUTPUT] + "\n...（输出已截断）"


def run_check(repo: Path, check: Check) -> dict[str, Any]:
    start = time.monotonic()
    environment = os.environ.copy()
    environment.update({"CI": "1", "NO_COLOR": "1", "FORCE_COLOR": "0"})
    try:
        result = subprocess.run(
            check.command, cwd=repo / check.cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=check.timeout_seconds,
            check=False, shell=False, env=environment,
        )
        status = "passed" if result.returncode == 0 else "failed"
        return {**asdict(check), "status": status, "exit_code": result.returncode, "duration_seconds": round(time.monotonic() - start, 3), "stdout": shorten(result.stdout.strip()), "stderr": shorten(result.stderr.strip())}
    except subprocess.TimeoutExpired as exc:
        return {**asdict(check), "status": "timed_out", "exit_code": None, "duration_seconds": round(time.monotonic() - start, 3), "stdout": shorten(str(exc.stdout or "")), "stderr": shorten(str(exc.stderr or ""))}
    except FileNotFoundError as exc:
        return {**asdict(check), "status": "not-found", "exit_code": None, "duration_seconds": round(time.monotonic() - start, 3), "stdout": "", "stderr": f"未找到命令：{exc.filename or check.command[0]}"}
    except OSError as exc:
        return {**asdict(check), "status": "error", "exit_code": None, "duration_seconds": round(time.monotonic() - start, 3), "stdout": "", "stderr": str(exc)}


def render_markdown(repo: Path, source: str, values: list[dict[str, Any]], listing: bool) -> str:
    mark = chr(96)
    labels = {"planned": "待运行", "passed": "通过", "failed": "失败", "timed_out": "超时", "not-found": "未找到", "skipped": "跳过", "error": "错误"}
    lines = ["# 质量门禁清单" if listing else "# 质量门禁结果", "", f"- 仓库：{mark}{repo}{mark}", f"- 来源：{source}", "", "| 门禁 | 命令 | 必需 | 状态 |", "|---|---|---:|---|"]
    if not values:
        return "\n".join(lines + ["", "未发现可安全执行的质量门禁；交付时必须说明未验证项。"])
    for value in values:
        command = subprocess.list2cmdline(value["command"]).replace("|", "\\|")
        status = labels.get(value.get("status"), value.get("status"))
        lines.append(f"| {value['name']} | {mark}{command}{mark} | {'是' if value['required'] else '否'} | {status} |")
    if not listing:
        fence = mark * 3
        for value in values:
            if value.get("status") == "passed" and not (value.get("stdout") or value.get("stderr")):
                continue
            status = labels.get(value.get("status"), value.get("status"))
            lines += ["", f"## {value['name']}", "", f"- 状态：{status}", f"- 耗时：{value.get('duration_seconds', 0)} 秒"]
            for stream in ("stdout", "stderr"):
                if value.get(stream):
                    lines += ["", f"{stream}：", "", fence + "text", value[stream], fence]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="发现并执行项目质量门禁，不安装依赖或自动修改代码。")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--list", action="store_true", help="只列出门禁，不执行")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir() or not 1 <= args.timeout <= 3600:
        print("错误：仓库路径无效或 timeout 不在 1 到 3600 之间。", file=sys.stderr)
        return 2
    try:
        configured = config_checks(repo, args.timeout)
    except ValueError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2
    checks = configured if configured is not None else auto_checks(repo, args.timeout)
    source = "项目配置" if configured is not None else "保守自动识别"
    values = [{**asdict(check), "status": "planned"} for check in checks] if args.list else []
    if not args.list:
        for check in checks:
            result = run_check(repo, check)
            values.append(result)
            if args.fail_fast and check.required and result["status"] != "passed":
                break
    payload = {"schema_version": 1, "repository": str(repo), "source": source, "listing": args.list, "checks": values}
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(repo, source, values, args.list))
    failed = any(value["required"] and value["status"] != "passed" for value in values)
    return 0 if args.list or not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
