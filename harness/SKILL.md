---
name: harness
description: 按照用户的习惯搭建或修改项目骨架（harness）。支持全新项目和已有项目：新项目完整创建目录结构、配置代码规范、生成基础配置文件；已有项目先扫描现状，补充缺失部分或按需修改骨架结构，不覆盖已有内容。当用户说"初始化项目"、"起一个项目架子"、"帮我搭个新项目"、"修改项目骨架"、"更新 harness"、"harness"、"scaffold"、"create project structure"、"init project" 时触发本 skill。
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Harness — 项目骨架与文档体系管理

你是项目文档体系的统一操作入口。用户通过 `/harness` 显式触发你，你需要先**识别用户意图**，再执行对应操作。

## 意图识别

根据用户提供的上下文，判断属于以下哪种情境，然后跳转到对应章节执行：

| 情境关键词 | 执行章节 |
|-----------|---------|
| 新项目、初始化、scaffold、搭架子 | → [初始化流程](#初始化流程) |
| 已有项目补全、缺少文档、harness 不完整 | → [初始化流程](#初始化流程)（已有项目模式） |
| 设计新功能、写 spec、新模块 | → [写设计文档](#写设计文档) |
| 开始排查问题、debugging、报错了想查 | → [开始排障](#开始排障) |
| 排查完问题、记录 bug、复盘 | → [记录排障](#记录排障) |
| 更新可观测性、日志规范变了 | → [更新文档](#更新文档) |
| 修改 harness 约定、调整模板或规范 | → [修改骨架约定](#修改骨架约定) |

若意图不明确，直接询问用户想做什么，给出上表中的选项。

---

## 写设计文档

1. 询问模块名称（若未提供）
2. 检查 `docs/design/` 下是否已有同名文件，避免重复创建
3. 应用 [templates/design.md](templates/design.md)，填写模块名，其余占位符留给用户填写
4. 若同名模块已存在 spec，询问是更新还是拆分子模块

## 开始排障

用户描述了症状但还没排查时，**先检索既有结论**，避免重复劳动：

1. 读取 `docs/debugging/registry.md`，按症状关键词匹配既有记录
2. 若命中：告知用户既有结论与对应记录文件路径，询问是否复用；如复用后仍未解决，再进入新一轮排查
3. 若未命中：协助用户排查；问题解决后跳转到 [记录排障](#记录排障) 登记

## 记录排障

1. 询问症状简述（若未提供），用于文件命名
2. **先检索** `docs/debugging/registry.md`，确认是否已有同质症状的既有结论；若有，告知用户并询问是补充已有记录还是新建
3. 以 `<YYYY-MM-DD>-<症状简述>.md` 命名，应用 [templates/debugging-record.md](templates/debugging-record.md) 生成文件到 `docs/debugging/records/`
4. 在 `docs/debugging/registry.md` 补登一行（症状关键词、根因摘要、文件链接）

## 更新文档

根据用户描述，定位到对应文档文件，直接编辑更新。常见目标：

- `docs/observability.md` — 可观测性规范
- `docs/testing.md` — 测试指南
- `docs/ssot-registry.md` — SSOT 注册表
- `docs/design/<module>.md` — 模块 spec

## 修改骨架约定

用户想调整 harness 本身的模板或规范时（如修改 `templates/` 下的文件、调整目录结构约定），直接按用户指示编辑对应文件。修改后确认是否需要同步更新已有项目中的已生成文件。

---

## 初始化流程

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
