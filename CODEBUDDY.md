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

## Adding New Skills

1. Create a directory: `skills/<skill-name>/`
2. Create `SKILL.md` inside with YAML frontmatter and instructions
3. Commit to git

## 用户指定记忆

> **重要约束**：本节内容由用户人工维护。AI 在修改、删除或重组本节任何内容之前，**必须先征得用户明确同意**。未经用户许可，不得擅自变更此处的任何条目。

- 创建新 skill 或修改 skill 功能后，需要在 CODEBUDDY.md 的 `## Available Skills` 节中同步更新对应说明
