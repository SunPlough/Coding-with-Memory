<div align="center">

# Coding with Memory

<img src="assets/coding-with-memory-banner.svg" alt="Coding with Memory" width="760" />

> Make agents write clearly. Make memory stay bounded.

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-2f855a.svg)](https://agentskills.io)
[![Codex](https://img.shields.io/badge/Codex-ready-2563eb.svg)](https://openai.com/codex/)
[![License](https://img.shields.io/badge/license-MIT-111827.svg)](LICENSE)

</div>

Coding with Memory is an engineering skill for agent-led software development. It combines intent routing, Google-based language standards, Chinese comment rules, deterministic quality gates, systematic debugging, code review, and auditable preference memory.

## Install

```bash
npx skills add SunPlough/Coding-with-Memory
```

## What it enforces

- Project facts and security rules outrank preferences.
- Language standards stay isolated by language.
- Comments explain contracts, constraints, boundaries, and reasons.
- Candidate memory never silently becomes an engineering rule.
- Every delivery separates `passed`, `failed`, `skipped`, and `not-found`.
- Skill evolution is validation-gated and reversible.

## Runtime memory

Memory is stored in the target project's `.coding-memory/`, never in the installed skill directory. Automatic extraction creates only `candidate` entries. Explicit human approval is required before a preference can be applied, and approved preferences can affect communication, planning granularity, tool choice, or report format only.

## Example

```bash
python examples/langgraph_agent_demo.py --self-test
python examples/langgraph_agent_demo.py --task "Add user login to the project"
```

See the [Chinese README](README.md) for the full workflow, repository map, and design boundaries.

## License

MIT
