---
name: harness
description: 按照用户的习惯初始化一个新项目的骨架（harness）。当用户说"初始化项目"、"起一个项目架子"、"帮我搭个新项目"、"harness"、"scaffold"、"create project structure"、"init project" 时触发本 skill。自动创建目录结构、配置代码规范、生成基础配置文件，让项目可以立即开始开发。
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Harness — 项目初始化

你的任务是按照用户的习惯，为项目搭建或补全骨架，让用户可以立即开始开发。**项目可能是全新的，也可能是已有项目**——两种情况都需要支持。

## 第一步：收集信息 & 感知现状

如果用户没有提供足够信息，先询问：

1. **项目名称**（目录名）
2. **技术栈**（Java/Spring Boot、Node.js/TypeScript、Python、前端框架等）
3. **项目类型**（REST API、Web 应用、CLI 工具、库/SDK 等）
4. **目标目录**（默认当前目录）
5. **AI 工具**（用于确定项目入口文件名，见下方规则）

**已有项目的处理原则**：若目标目录已存在项目（有代码、配置或部分文档），先用 Glob/Read 扫描现状，识别哪些 harness 约定文件已存在、哪些缺失，然后**只补充缺失部分，不覆盖已有内容**。

**项目入口文件名规则**（按优先级检测当前环境）：

| AI 工具 | 入口文件 |
|---------|---------|
| CodeBuddy Code | `CODEBUDDY.md` |
| Claude Code | `CLAUDE.md` |
| OpenAI Codex CLI | `AGENTS.md` |

若当前对话环境可以判断 AI 工具，直接使用对应文件名；否则询问用户，默认使用 `CODEBUDDY.md`。

如果用户已经提供了足够的上下文，直接开始，不要过度询问。

## 第二步：创建或补全目录结构

**新项目**：完整创建以下约定文件和目录结构。

**已有项目**：只创建缺失的文件/目录；已存在的文件不覆盖，但可在用户明确要求时更新。

harness 只负责创建以下约定文件，其余目录结构由语言 reference 决定：

```
<project-name>/
├── docs/
│   ├── design/               # 功能/模块设计文档（spec），初始为空目录
│   ├── debugging/
│   │   ├── registry.md       # 应用 templates/debugging-registry.md 生成
│   │   └── records/          # 历史排障记录，初始为空目录
│   ├── observability.md      # 应用 templates/observability.md 生成
│   ├── testing.md            # 应用 templates/testing.md 生成
│   └── ssot-registry.md      # 应用 templates/ssot-registry.md 生成
├── <AI_ENTRY>.md             # 应用 templates/ai-entry.md 生成（CODEBUDDY.md / CLAUDE.md / AGENTS.md）
└── README.md                 # 应用 templates/README.md 生成
```

根据用户选择的技术栈，读取对应 reference 文件获取详细目录结构和配置规范：

| 技术栈 | Reference 文件 |
|--------|---------------|
| Node.js / TypeScript | [references/node-typescript.md](references/node-typescript.md) |
| Python | [references/python.md](references/python.md) |

## 第三步：生成基础配置文件

**`README.md`** — 应用 [templates/README.md](templates/README.md)，填写项目名称和简介。

### 代码规范配置

各语言的代码规范配置详见对应 reference 文件，此处不重复。

### 文档体系（必须生成）

#### `<AI_ENTRY>.md` — 项目入口与文档索引

优先使用对应 AI 工具自带的初始化命令生成此文件。仅在工具不支持时，才应用 [templates/ai-entry.md](templates/ai-entry.md) 生成，文件名由第一步确定的 AI 工具决定。

#### `docs/ssot-registry.md` — SSOT 注册表

应用 [templates/ssot-registry.md](templates/ssot-registry.md) 生成，初始为空表。每当抽取公共入口时在此登记一行。

#### `docs/debugging/records/` — 历史排障记录

初始为空目录。每次排查完问题后，以 `<YYYY-MM-DD>-<症状简述>.md` 命名，应用 [templates/debugging-record.md](templates/debugging-record.md) 生成记录，并在 `docs/debugging/registry.md` 补登一行。

**查问题前必须先检索 [`docs/debugging/registry.md`](templates/debugging-registry.md)**，确认是否有同质症状的既有结论——同一个症状不应在仓库里出现两套排查结论（SSOT 原则的延伸）。

#### `docs/observability.md` — 可观测性基础设施总览

应用 [templates/observability.md](templates/observability.md) 生成，按技术栈替换日志框架占位符：

| 技术栈 | 日志框架 |
|--------|---------|
| Node.js / TypeScript | pino |
| Python | loguru |

#### `docs/testing.md` — 测试指南

应用 [templates/testing.md](templates/testing.md) 生成，填写实际的运行命令。

#### `docs/design/<module>.md` — 功能/模块设计文档（spec）

每个功能模块对应一个 spec 文件。应用 [templates/design.md](templates/design.md) 生成，遵循其中的唯一信源原则。

模块可以渐进式拆分：当一个 spec 文件过大、职责不清晰时，拆成子模块目录：

```
docs/design/
├── auth.md               # 小模块，单文件即可
└── order/                # 大模块，拆成子模块
    ├── README.md          # 模块总览：边界、子模块划分、依赖关系
    ├── checkout.md        # 子模块 spec
    └── payment.md         # 子模块 spec
```

拆分时机：单个 spec 文件超过 1000 行，或模块内出现明显独立的子职责，就应考虑拆分。`README.md` 作为父模块总览，只描述整体边界和子模块划分，不重复子模块的细节。
