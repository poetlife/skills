# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Repository Overview

This is a personal global skills repository for CodeBuddy Code, located at `~/.config/neo-codebuddy/skills/`. Skills placed here are available across all projects.

## Structure

```
skills/
└── <skill-name>/
    └── SKILL.md       # Skill definition with YAML frontmatter + Markdown instructions
```

Each skill lives in its own subdirectory containing a single `SKILL.md` file.

## Skill File Format

Skills use YAML frontmatter followed by Markdown content:

```markdown
---
name: skill-name                  # Optional; defaults to directory name
description: ...                  # Shown to AI for auto-selection
allowed-tools: Read, Write, Bash  # Comma-separated tool whitelist
context: fork                     # Optional; run in isolated subagent
agent: Explore                    # Optional; only valid with context: fork
user-invocable: false             # Optional; hide from / menu
disable-model-invocation: true    # Optional; prevent auto-trigger by AI
---

# Skill instructions...
```

## Available Skills

### `add-user-memory`

Appends entries to the `## 用户指定记忆` section in the project-level memory file. Supports multi-tool environments:

| Tool | Memory File |
|------|------------|
| CodeBuddy Code | `CODEBUDDY.md` |
| Claude Code | `CLAUDE.md` |
| OpenAI Codex CLI | `AGENTS.md` |

Detection order: `CODEBUDDY.md` → `CLAUDE.md` → `AGENTS.md` → create `CODEBUDDY.md` by default.

**Key constraint**: Existing entries in `## 用户指定记忆` are user-owned. Appending new entries requires no confirmation; modifying or deleting existing entries requires explicit user approval.

Triggered by: "记住……", "帮我记录……", `/add-user-memory <content>`, or `$ARGUMENTS`.

### `harness`

为项目搭建或修改骨架，并维护设计、需求验证（evaluation）、排障、可观测性与持续进化（evolution）体系——支持全新项目和已有项目补全。包含贯穿全生命周期的程序化验证工作流（将初始验证目标及对话纠偏沉淀为可执行验证资产，按 `project-stage` 演进）以及线上数据驱动的持续进化闭环。

支持技术栈：Java/Spring Boot、Node.js/TypeScript、Python 及前端框架。

Triggered by: "初始化项目"、"起一个架子"、"帮我搭个新项目"、"修改项目骨架"、"更新 harness"、"定义验证目标"、"形式化验收"、"搭建 eval"、"进化分析"、"harness"、"scaffold"、"init project"、"补全项目骨架".

### `goal-to-prompt`

提供写入与检索使用两个入口：每类事情保存一份记录，包含不同条件下的处理方案、选择规则、关键流程与 AI 提示词；使用时按当前输入选方案。记录可复用做法及个人经验，不管理单次项目进度。默认目录为 `~/.local/share/goal-to-prompt`，支持持久配置及本次目录覆盖。

Triggered by: “记下这件事怎么做”、“简单情况用这个，复杂情况用那个”、“找以前的处理方案”、“这个素材该用哪种方案”、`/goal-to-prompt`。

## Adding New Skills

1. Create a directory: `skills/<skill-name>/`
2. Create `SKILL.md` inside with YAML frontmatter and instructions
3. Run redline check: `python3 scripts/check_skill_redlines.py` (enforced automatically by `.githooks/pre-commit`; after fresh clone run `git config core.hooksPath .githooks`)
4. Commit to git

## 用户指定记忆

> **重要约束**：本节内容由用户人工维护。AI 在修改、删除或重组本节任何内容之前，**必须先征得用户明确同意**。未经用户许可，不得擅自变更此处的任何条目。

- 创建新 skill 或修改 skill 功能后，需要在 CODEBUDDY.md 的 `## Available Skills` 节中同步更新对应说明
- 非显式说明，不允许生成任何新的文档
