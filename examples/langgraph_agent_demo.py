'''运行示例：

    python langgraph_agent_demo.py
    python langgraph_agent_demo.py --task "为项目增加用户登录功能"
    python langgraph_agent_demo.py --format json
    python langgraph_agent_demo.py --self-test
'''

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


DEFAULT_TASK = "为项目增加用户登录功能"
DEFAULT_MEMORY_PATH = Path(".coding-memory") / "preferences.jsonl"
DEFAULT_MAX_REVISIONS = 2
SUPPORTED_FORMATS = ("markdown", "json")

TaskKind = Literal["feature", "bugfix", "refactor", "research", "unknown"]
RunStatus = Literal["planned", "executing", "needs_revision", "approved", "blocked"]


class AgentState(TypedDict, total=False):
    """图节点之间共享的状态契约。

    节点只返回自己负责更新的字段，LangGraph 会将增量合并回状态。
    `revision_count` 和 `max_revisions` 是路由安全边界，不能由 Memory 或
    用户表达偏好覆盖，否则评审失败可能变成不可控的循环。
    """

    task: str
    normalized_task: str
    task_kind: TaskKind
    constraints: list[str]
    acceptance_criteria: list[str]
    approved_preferences: list[dict[str, Any]]
    candidate_preferences: list[dict[str, Any]]
    plan: list[str]
    actions: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    revision_count: int
    max_revisions: int
    status: RunStatus
    final_answer: str
    events: list[dict[str, Any]]
    started_at: str
    finished_at: str


@dataclass(frozen=True)
class RuntimeConfig:
    """运行参数；保持扁平，便于在 CLI、自检和测试中复用。"""

    memory_path: Path = DEFAULT_MEMORY_PATH
    max_revisions: int = DEFAULT_MAX_REVISIONS
    output_format: str = "markdown"
    include_events: bool = True


@dataclass(frozen=True)
class ActionRecord:
    """一次计划动作的可审计结果。"""

    name: str
    owner: str
    result: str
    evidence: str
    risk: str = "低"


@dataclass(frozen=True)
class ReviewFinding:
    """评审发现；严重性越高越需要在最终报告中优先说明。"""

    severity: Literal["P0", "P1", "P2", "P3"]
    title: str
    detail: str
    remediation: str
    resolved: bool = False


@dataclass(frozen=True)
class AuditEvent:
    """图运行事件，帮助观察每个节点的输入意图和输出结果。"""

    timestamp: str
    node: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    """返回可排序的 UTC 时间；报告不依赖本机时区。"""

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def add_event(
    state: AgentState,
    node: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """构造单条事件，不直接修改传入状态。"""

    event = AuditEvent(
        timestamp=utc_now(),
        node=node,
        message=message,
        data=data or {},
    )
    return asdict(event)


def merge_events(state: AgentState, *events: dict[str, Any]) -> list[dict[str, Any]]:
    """追加事件并返回新列表，避免节点之间共享可变列表。"""

    return [*state.get("events", []), *events]


def normalize_task(task: str) -> str:
    """压缩用户输入中的空白，保留任务原意和中文标点。"""

    normalized = re.sub(r"\s+", " ", task.strip())
    return normalized or DEFAULT_TASK


def classify_task(task: str) -> TaskKind:
    """用有限关键词分类任务，分类失败时返回 unknown 而不是臆测。"""

    if any(word in task for word in ("修复", "错误", "bug", "异常", "失败")):
        return "bugfix"
    if any(word in task for word in ("重构", "整理", "重写", "迁移")):
        return "refactor"
    if any(word in task for word in ("调研", "比较", "了解", "研究")):
        return "research"
    if any(word in task for word in ("增加", "新增", "实现", "开发", "支持")):
        return "feature"
    return "unknown"


def infer_constraints(task: str, kind: TaskKind) -> list[str]:
    """提取少量可观察约束；没有证据的约束不自动添加。"""

    constraints: list[str] = []
    if "登录" in task or "认证" in task or "权限" in task:
        constraints.extend(["敏感数据不得写入日志", "认证失败必须返回可解释错误"])
    if "接口" in task or "API" in task:
        constraints.append("外部输入需要显式校验失败路径")
    if kind == "bugfix":
        constraints.append("先保留最小复现，再验证修复没有回归")
    if kind == "refactor":
        constraints.append("行为保持不变，重构与功能变化分开验证")
    if not constraints:
        constraints.append("保持变更范围最小并提供可重复验证")
    return deduplicate(constraints)


def build_acceptance_criteria(task: str, kind: TaskKind) -> list[str]:
    """根据任务类型建立可验证的 Definition of Done 子集。"""

    criteria = [
        "目标行为能够通过一条可重复命令验证",
        "失败路径有明确结果，不吞掉异常",
        "最终报告区分已通过、失败、跳过和未发现的检查",
    ]
    if kind == "feature":
        criteria.insert(0, f"完成任务范围：{task}")
    elif kind == "bugfix":
        criteria.insert(0, "存在可复现的问题描述，并证明修复后不再出现")
    elif kind == "refactor":
        criteria.insert(0, "重构前后外部可观察行为一致")
    elif kind == "research":
        criteria.insert(0, "结论有来源或明确标注为待验证假设")
    else:
        criteria.insert(0, "先澄清任务类型，再执行具体变更")
    return criteria


def deduplicate(items: Iterable[str]) -> list[str]:
    """按首次出现顺序去重，避免报告因重复规则变得嘈杂。"""

    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def parse_jsonl_line(line: str, line_number: int) -> dict[str, Any] | None:
    """解析一行 Memory；坏行只产生审计信息，由调用方决定是否记录。"""

    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    value.setdefault("_line_number", line_number)
    return value


def read_memory_preferences(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """读取 approved 偏好，并单独返回 candidate 供报告展示。

    Memory 文件不存在是正常的首次运行状态，不应阻塞代码任务；文件存在
    但有损坏行时也只跳过该行，避免一个候选条目破坏整个 Agent 运行。
    """

    approved: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    if not path.exists():
        return approved, candidates
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return approved, candidates
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        record = parse_jsonl_line(line, index)
        if record is None:
            continue
        if record.get("category") != "preference":
            continue
        status = record.get("status", "candidate")
        if status not in {"approved", "candidate", "rejected", "deprecated"}:
            continue
        normalized = {
            "id": record.get("id", f"line-{index}"),
            "summary": str(record.get("summary", "")),
            "trigger": str(record.get("trigger", "")),
            "action": str(record.get("action", "")),
            "domain": str(record.get("domain", "")),
            "effect": str(record.get("effect", "")),
            "scope": str(record.get("scope", "repository")),
            "status": status,
        }
        if status == "approved":
            approved.append(normalized)
        elif status == "candidate":
            candidates.append(normalized)
    return approved, candidates


def select_report_preferences(
    preferences: list[dict[str, Any]],
    task: str,
) -> list[dict[str, Any]]:
    """只选择与报告表达相关且触发条件命中的 approved 偏好。"""

    selected: list[dict[str, Any]] = []
    for preference in preferences:
        effect = preference.get("effect")
        trigger = preference.get("trigger", "")
        if effect not in {"communication_language", "planning_granularity", "report_format"}:
            continue
        if trigger and trigger not in task and trigger not in {"交付报告", "所有任务"}:
            continue
        selected.append(preference)
    return selected


def build_plan(task: str, kind: TaskKind, constraints: list[str]) -> list[str]:
    """生成五步以内的最小计划，确保每步都有可观察产物。"""

    if kind == "research":
        plan = ["澄清问题与范围", "收集可核验来源", "比较方案与风险", "输出带证据的结论"]
    elif kind == "bugfix":
        plan = ["建立最小复现", "定位根因", "实施最小修复", "运行回归验证", "记录剩余风险"]
    elif kind == "refactor":
        plan = ["确认行为基线", "拆分最小重构切片", "保持接口与数据契约", "运行回归验证", "复核差异范围"]
    elif kind == "feature":
        plan = ["确认需求边界", "设计数据与接口契约", "实现核心行为", "验证成功与失败路径", "进行交付评审"]
    else:
        plan = ["澄清任务类型", "列出可验证目标", "选择最小实现路径", "执行定向检查", "汇总待确认事项"]
    if any("敏感" in item for item in constraints):
        plan.insert(-1, "复核敏感数据与日志边界")
    return deduplicate(plan)


def action_result_for(
    action: str,
    task: str,
    revision_count: int,
) -> ActionRecord:
    """为规则模型生成动作结果。

    登录任务第一次执行故意留下“测试未补充”的发现，让示例能展示
    review -> revision -> review 的有限回路；第二次执行会补齐该证据。
    这不是模拟真实失败，而是一个稳定的教学探针。
    """

    if "确认" in action or "澄清" in action:
        return ActionRecord(action, "agent", "完成", "形成任务边界和目标清单")
    if "设计" in action or "方案" in action:
        return ActionRecord(action, "agent", "完成", "形成接口、数据和失败路径约束")
    if "复现" in action:
        return ActionRecord(action, "agent", "完成", "记录输入、预期和实际结果")
    if "定位" in action:
        return ActionRecord(action, "agent", "完成", "使用单一假设验证根因")
    if "实现" in action or "修复" in action:
        return ActionRecord(action, "agent", "完成", f"应用最小变更：{task}")
    if "敏感" in action:
        return ActionRecord(action, "reviewer", "完成", "确认凭据和个人数据不进入日志")
    if "测试" in action or "验证" in action or "回归" in action:
        if "登录" in task and revision_count == 0:
            return ActionRecord(action, "tester", "待补充", "尚未覆盖认证失败路径", "中")
        return ActionRecord(action, "tester", "完成", "成功路径和失败路径均有可重复检查")
    if "评审" in action or "复核" in action:
        return ActionRecord(action, "reviewer", "完成", "检查范围、规范、风险和交付证据")
    if "收集" in action or "比较" in action:
        return ActionRecord(action, "agent", "完成", "保留来源、假设和取舍")
    if "输出" in action or "汇总" in action:
        return ActionRecord(action, "agent", "完成", "生成结构化报告")
    return ActionRecord(action, "agent", "完成", "动作已记录")


def initial_state(task: str, config: RuntimeConfig) -> AgentState:
    """创建图运行的最小初始状态。"""

    return AgentState(
        task=task,
        normalized_task="",
        task_kind="unknown",
        constraints=[],
        acceptance_criteria=[],
        approved_preferences=[],
        candidate_preferences=[],
        plan=[],
        actions=[],
        findings=[],
        revision_count=0,
        max_revisions=max(0, config.max_revisions),
        status="planned",
        final_answer="",
        events=[],
        started_at=utc_now(),
        finished_at="",
    )


def intake_node(state: AgentState, config: RuntimeConfig | None = None) -> dict[str, Any]:
    """接收任务并加载可用上下文；不在此节点修改工程文件。"""

    runtime = config or RuntimeConfig()
    normalized = normalize_task(state.get("task", DEFAULT_TASK))
    kind = classify_task(normalized)
    constraints = infer_constraints(normalized, kind)
    criteria = build_acceptance_criteria(normalized, kind)
    approved, candidates = read_memory_preferences(runtime.memory_path)
    selected = select_report_preferences(approved, normalized)
    event = add_event(
        state,
        "intake",
        "任务已标准化，Memory 仅加载 approved 偏好",
        {"task_kind": kind, "approved_count": len(selected), "candidate_count": len(candidates)},
    )
    return {
        "normalized_task": normalized,
        "task_kind": kind,
        "constraints": constraints,
        "acceptance_criteria": criteria,
        "approved_preferences": selected,
        "candidate_preferences": candidates,
        "status": "planned",
        "events": merge_events(state, event),
    }


def planning_node(state: AgentState) -> dict[str, Any]:
    """把任务转为最小可验收计划，并明确不做的事情。"""

    task = state.get("normalized_task", DEFAULT_TASK)
    kind = state.get("task_kind", "unknown")
    constraints = state.get("constraints", [])
    plan = build_plan(task, kind, constraints)
    event = add_event(
        state,
        "planning",
        "已生成最小计划",
        {"step_count": len(plan), "non_goals": ["不调用外部 API", "不修改仓库文件"]},
    )
    return {"plan": plan, "status": "planned", "events": merge_events(state, event)}


def execution_node(state: AgentState) -> dict[str, Any]:
    """执行规则计划并记录每一步证据，不伪造外部系统结果。"""

    task = state.get("normalized_task", DEFAULT_TASK)
    revision_count = state.get("revision_count", 0)
    records = [
        asdict(action_result_for(action, task, revision_count))
        for action in state.get("plan", [])
    ]
    event = add_event(
        state,
        "execution",
        "已完成离线规则执行",
        {"action_count": len(records), "revision_count": revision_count},
    )
    return {"actions": records, "status": "executing", "events": merge_events(state, event)}


def make_findings(state: AgentState) -> list[dict[str, Any]]:
    """根据验收标准生成按严重性排序的评审发现。"""

    findings: list[ReviewFinding] = []
    actions = state.get("actions", [])
    if not actions:
        findings.append(
            ReviewFinding("P1", "没有执行证据", "计划没有产生动作记录", "重新执行计划")
        )
    incomplete = [item for item in actions if item.get("result") in {"待补充", "失败"}]
    if incomplete:
        names = "、".join(str(item.get("name")) for item in incomplete)
        findings.append(
            ReviewFinding(
                "P1",
                "验证证据不完整",
                f"以下动作尚未完成：{names}",
                "补齐成功和失败路径的可重复检查",
            )
        )
    if any("敏感数据" in item for item in state.get("constraints", [])):
        security_evidence = any("敏感" in str(item.get("name")) for item in actions)
        if not security_evidence:
            findings.append(
                ReviewFinding(
                    "P1",
                    "缺少敏感数据边界复核",
                    "任务涉及认证或权限，但动作记录没有日志边界检查",
                    "增加敏感数据和日志审查步骤",
                )
            )
    return [asdict(item) for item in sorted(findings, key=lambda item: item.severity)]


def review_node(state: AgentState) -> dict[str, Any]:
    """评审行为、约束和证据，产出可路由的状态。"""

    findings = make_findings(state)
    status: RunStatus = "needs_revision" if findings else "approved"
    event = add_event(
        state,
        "review",
        "评审完成" if not findings else "评审发现需要修订的问题",
        {"finding_count": len(findings), "status": status},
    )
    return {"findings": findings, "status": status, "events": merge_events(state, event)}


def revision_node(state: AgentState) -> dict[str, Any]:
    """只修订失败证据，不重写整个计划；每次进入都消耗一个预算。"""

    next_count = state.get("revision_count", 0) + 1
    plan = list(state.get("plan", []))
    if any("验证" in item or "测试" in item or "回归" in item for item in plan):
        revised_plan = plan
    else:
        revised_plan = [*plan, "验证成功与失败路径"]
    event = add_event(
        state,
        "revision",
        "根据评审发现进行一次最小修订",
        {"revision_count": next_count, "remaining": max(0, state.get("max_revisions", 0) - next_count)},
    )
    return {
        "revision_count": next_count,
        "plan": revised_plan,
        "actions": [],
        "findings": [],
        "status": "planned",
        "events": merge_events(state, event),
    }


def summarize_findings(findings: list[dict[str, Any]]) -> str:
    """把发现压缩为报告可读的一行，保留严重性和修复动作。"""

    if not findings:
        return "无未解决评审发现。"
    parts = [
        f"{item.get('severity')}：{item.get('title')}（{item.get('remediation')}）"
        for item in findings
    ]
    return "；".join(parts)


def format_preference_line(preference: dict[str, Any]) -> str:
    """格式化偏好，明确它只影响表达而不影响工程门禁。"""

    return (
        f"{preference.get('summary', '未命名偏好')}"
        f" [effect={preference.get('effect', 'unknown')}]"
    )


def build_final_answer(state: AgentState) -> str:
    """生成中文交付报告，区分实际证据与未运行检查。"""

    status = state.get("status", "blocked")
    status_text = {
        "approved": "通过",
        "blocked": "阻塞",
        "needs_revision": "需要修订",
        "executing": "执行中",
        "planned": "已计划",
    }.get(status, status)
    lines = [
        f"# LangGraph Agent Demo 报告",
        "",
        f"- 任务：{state.get('normalized_task', state.get('task', DEFAULT_TASK))}",
        f"- 类型：{state.get('task_kind', 'unknown')}",
        f"- 状态：{status_text}",
        f"- 修订次数：{state.get('revision_count', 0)}/{state.get('max_revisions', 0)}",
        "",
        "## 计划",
    ]
    lines.extend(f"{index}. {item}" for index, item in enumerate(state.get("plan", []), start=1))
    lines.extend(["", "## 执行证据"])
    for action in state.get("actions", []):
        lines.append(
            f"- `{action.get('name')}`：{action.get('result')}；{action.get('evidence')}"
        )
    lines.extend(["", "## 评审"])
    lines.append(summarize_findings(state.get("findings", [])))
    lines.extend(["", "## 验收标准"])
    lines.extend(f"- {item}" for item in state.get("acceptance_criteria", []))
    lines.extend(["", "## Memory"])
    approved = state.get("approved_preferences", [])
    candidates = state.get("candidate_preferences", [])
    if approved:
        lines.append("已应用的 approved 偏好（仅影响报告表达）：")
        lines.extend(f"- {format_preference_line(item)}" for item in approved)
    else:
        lines.append("本次没有命中的 approved 偏好。")
    if candidates:
        lines.append("候选偏好仅展示，不在本次运行生效：")
        lines.extend(f"- {format_preference_line(item)}" for item in candidates)
    else:
        lines.append("本次没有发现候选偏好。")
    lines.extend(["", "## 检查说明"])
    lines.append("- passed：图运行、自检范围内的规则评审已通过。")
    lines.append("- not-found：真实仓库 Formatter、Lint、类型检查和外部 API 测试不适用于此离线示例。")
    lines.append("- rollback：删除本单文件即可回滚，不修改其他工程文件。")
    return "\n".join(lines)


def finalize_node(state: AgentState) -> dict[str, Any]:
    """结束图运行并固定完成时间；最终文本只消费已记录的状态。"""

    final_answer = build_final_answer(state)
    event = add_event(state, "finalize", "已生成最终交付报告")
    return {
        "final_answer": final_answer,
        "finished_at": utc_now(),
        "events": merge_events(state, event),
    }


def review_router(state: AgentState) -> str:
    """决定继续修订还是交付；路由必须尊重最大修订次数。"""

    if state.get("status") == "approved":
        return "finalize"
    if state.get("revision_count", 0) < state.get("max_revisions", 0):
        return "revision"
    return "finalize"


def build_graph(config: RuntimeConfig | None = None):
    """构建并编译 LangGraph 图。

    节点函数保持纯粹的状态增量接口；运行配置通过闭包传入 intake，
    其余节点只依赖状态，因此图仍然容易测试和替换。
    """

    runtime = config or RuntimeConfig()
    graph = StateGraph(AgentState)
    graph.add_node("intake", lambda state: intake_node(state, runtime))
    graph.add_node("planning", planning_node)
    graph.add_node("execution", execution_node)
    graph.add_node("review", review_node)
    graph.add_node("revision", revision_node)
    graph.add_node("finalize", finalize_node)
    graph.add_edge(START, "intake")
    graph.add_edge("intake", "planning")
    graph.add_edge("planning", "execution")
    graph.add_edge("execution", "review")
    graph.add_conditional_edges(
        "review",
        review_router,
        {"revision": "revision", "finalize": "finalize"},
    )
    graph.add_edge("revision", "execution")
    graph.add_edge("finalize", END)
    return graph.compile()


def run_agent(task: str, config: RuntimeConfig | None = None) -> AgentState:
    """运行一次 Agent 并返回完整状态，便于 CLI 和自检共享。"""

    runtime = config or RuntimeConfig()
    graph = build_graph(runtime)
    state = initial_state(task, runtime)
    result = graph.invoke(state)
    return AgentState(**result)


def state_to_json(state: AgentState, include_events: bool = True) -> str:
    """输出稳定、可机器读取的 JSON；事件可按需隐藏以减少噪声。"""

    serializable = dict(state)
    if not include_events:
        serializable.pop("events", None)
    return json.dumps(serializable, ensure_ascii=False, indent=2)


def print_result(state: AgentState, output_format: str, include_events: bool) -> None:
    """向终端输出报告；未知格式在参数解析阶段已被拒绝。"""

    if output_format == "json":
        print(state_to_json(state, include_events=include_events))
        return
    print(state.get("final_answer", "没有生成报告。"))
    if include_events:
        print("\n## 图事件（调试观察）")
        for event in state.get("events", []):
            print(f"- {event.get('timestamp')} `{event.get('node')}`：{event.get('message')}")


def assert_equal(actual: Any, expected: Any, message: str) -> None:
    """自检断言使用明确消息，失败时便于定位状态契约问题。"""

    if actual != expected:
        raise AssertionError(f"{message}；实际值={actual!r}，期望值={expected!r}")


def self_test() -> int:
    """执行离线行为探针，覆盖成功、修订、Memory 隔离和边界输入。"""

    config = RuntimeConfig(memory_path=Path("__missing_memory__.jsonl"), max_revisions=2)
    simple = run_agent("整理项目日志输出", config)
    assert_equal(simple["status"], "approved", "普通任务应通过评审")
    assert_equal(simple["revision_count"], 0, "普通任务不应无故修订")
    assert_equal(len(simple["findings"]), 0, "普通任务不应有评审发现")

    login = run_agent("为项目增加用户登录功能", config)
    assert_equal(login["status"], "approved", "登录任务应在有限修订后通过")
    assert_equal(login["revision_count"], 1, "登录任务应演示一次修订")
    assert_equal(len(login["events"]), 8, "图事件数量应反映一次修订回路")

    no_budget = run_agent(
        "为项目增加用户登录功能",
        RuntimeConfig(memory_path=config.memory_path, max_revisions=0),
    )
    assert_equal(no_budget["status"], "needs_revision", "没有修订预算时应保留阻塞状态")
    assert_equal(no_budget["revision_count"], 0, "没有预算时不能偷偷修订")

    assert_equal(normalize_task("  "), DEFAULT_TASK, "空任务应回退到默认示例")
    assert_equal(classify_task("修复接口异常"), "bugfix", "关键词分类应识别 bugfix")
    assert_equal(deduplicate(["a", "a", "b"]), ["a", "b"], "去重必须保留顺序")
    assert_equal(select_report_preferences([{"effect": "security", "trigger": "所有任务"}], "任务"), [], "非表达偏好不能生效")

    with tempfile.TemporaryDirectory() as directory:
        memory_path = Path(directory) / "preferences.jsonl"
        memory_path.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "id": "approved-1",
                            "category": "preference",
                            "status": "approved",
                            "summary": "交付报告先给结论",
                            "trigger": "交付报告",
                            "action": "先输出结论",
                            "domain": "delivery",
                            "effect": "report_format",
                            "scope": "repository",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "id": "candidate-1",
                            "category": "preference",
                            "status": "candidate",
                            "summary": "候选偏好不得自动生效",
                            "trigger": "所有任务",
                            "action": "等待人工批准",
                            "domain": "delivery",
                            "effect": "report_format",
                            "scope": "repository",
                        },
                        ensure_ascii=False,
                    ),
                ]
            ),
            encoding="utf-8",
        )
        memory_state = run_agent(
            "整理项目日志输出",
            RuntimeConfig(memory_path=memory_path, max_revisions=2),
        )
        assert_equal(len(memory_state["approved_preferences"]), 1, "approved 偏好应可被读取")
        assert_equal(len(memory_state["candidate_preferences"]), 1, "candidate 偏好应只展示不生效")

    print("self-test passed: 9 checks")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """构造 CLI；参数只覆盖演示运行选项，不引入配置系统。"""

    parser = argparse.ArgumentParser(description="Coding with Memory 的 LangGraph 单文件演示")
    parser.add_argument("--task", default=DEFAULT_TASK, help="要交给 Agent 的任务文本")
    parser.add_argument("--memory-path", type=Path, default=DEFAULT_MEMORY_PATH, help="可选 Memory JSONL 路径")
    parser.add_argument("--max-revisions", type=int, default=DEFAULT_MAX_REVISIONS, help="评审失败后的最大修订次数")
    parser.add_argument("--format", choices=SUPPORTED_FORMATS, default="markdown", dest="output_format", help="输出格式")
    parser.add_argument("--no-events", action="store_true", help="隐藏图事件，仅输出报告或 JSON 状态")
    parser.add_argument("--self-test", action="store_true", help="运行离线自检后退出")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口；异常转为非零退出码并保留简短错误信息。"""

    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        try:
            return self_test()
        except AssertionError as error:
            print(f"self-test failed: {error}", file=sys.stderr)
            return 1
    if args.max_revisions < 0:
        parser.error("--max-revisions 不能为负数")
    config = RuntimeConfig(
        memory_path=args.memory_path,
        max_revisions=args.max_revisions,
        output_format=args.output_format,
        include_events=not args.no_events,
    )
    try:
        state = run_agent(args.task, config)
    except Exception as error:  # noqa: BLE001 - CLI 边界需要给出可读错误并退出。
        print(f"Agent 运行失败：{error}", file=sys.stderr)
        return 1
    print_result(state, config.output_format, config.include_events)
    return 0 if state.get("status") == "approved" else 2


if __name__ == "__main__":
    raise SystemExit(main())
