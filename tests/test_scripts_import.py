"""冒烟测试：五个脚本都能作为模块导入，暴露关键入口函数。"""

from __future__ import annotations

from conftest import load_script


def test_all_scripts_import():
    collect_context = load_script("collect_context")
    comment_audit = load_script("comment_audit")
    memory_tool = load_script("memory_tool")
    run_quality_gate = load_script("run_quality_gate")
    skill_health = load_script("skill_health")

    assert callable(collect_context.main)
    assert callable(comment_audit.main)
    assert callable(memory_tool.main)
    assert callable(run_quality_gate.main)
    assert callable(skill_health.main)
