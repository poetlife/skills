# 初始化与补全项目骨架流程

本 reference 定义新项目初始化与已有项目骨架补全的完整操作步骤。仅在需要搭建或补全项目骨架时读取。

你的任务是按照用户的习惯，为项目搭建或补全骨架，让用户可以立即开始开发。**项目可能是全新的，也可能是已有项目**——两种情况都需要支持。

## 第一步：收集信息 & 感知现状

如果用户没有提供足够信息，先询问：

1. **项目名称**（目录名）
2. **技术栈**（Java/Spring Boot、Node.js/TypeScript、Python、前端框架等）
3. **项目类型**（REST API、Web 应用、CLI 工具、库/SDK 等）
4. **目标目录**（默认当前目录）
5. **AI 工具**（用于确定项目入口文件名，见下方规则）
6. **项目阶段**（`project-stage`）。取值与默认规则见 [项目阶段](../SKILL.md#项目阶段)

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
│   ├── design/               # 功能/模块设计文档（spec）与验证目标契约，初始为空目录
│   ├── debugging/
│   │   ├── registry.md       # 应用 templates/debugging-registry.md 生成
│   │   └── records/          # 历史排障记录，初始为空目录
│   ├── evolution/
│   │   ├── registry.md       # 应用 templates/evolution-registry.md 生成
│   │   └── reports/          # 周期分析快照，初始为空目录
│   ├── evaluation.md         # 应用 templates/evaluation.md 生成（验证与评测总览及运行入口）
│   ├── observability.md      # 应用 templates/observability.md 生成
│   ├── testing.md            # 应用 templates/testing.md 生成（单元测试指南）
│   └── ssot-registry.md      # 应用 templates/ssot-registry.md 生成
├── <AI_ENTRY>.md             # 应用 templates/ai-entry.md 生成（CODEBUDDY.md / CLAUDE.md / AGENTS.md）
└── README.md                 # 应用 templates/README.md 生成
```

> 程序化验证资产优先复用项目既有的单测/集成/E2E 目录；当项目需要独立的评测集、黑盒脚本或运行期验证脚本时，按需建立 `evals/` 目录并在 `docs/evaluation.md` 中索引。

根据用户选择的技术栈，读取对应 reference 文件获取详细目录结构、L0 静态门禁与配置规范：

| 技术栈 | Reference 文件 |
|--------|---------------|
| Go | [go.md](go.md) |
| Node.js / TypeScript | [node-typescript.md](node-typescript.md) |
| Python | [python.md](python.md) |

静态门禁、架构边界守门、自定义检查器、棘轮基线与生成物一致性规范统一见 [static-checks.md](static-checks.md)。

## 第三步：生成基础配置文件

**`README.md`** — 应用 [../templates/README.md](../templates/README.md)，填写项目名称和简介。

### 代码规范配置

各语言的代码规范配置详见对应 reference 文件，此处不重复。

### 文档体系（必须生成）

#### `<AI_ENTRY>.md` — 项目入口与文档索引

优先使用对应 AI 工具自带的初始化命令生成此文件。仅在工具不支持时，才应用 [../templates/ai-entry.md](../templates/ai-entry.md) 生成，文件名由第一步确定的 AI 工具决定。

无论入口文件由工具命令生成还是由模板生成，都必须含有「项目阶段」一节，且只写入 [项目阶段](../SKILL.md#项目阶段) 确定的那一个取值及其规则。文件已存在时：没有该节就追加，已有该节则保留原取值，除非用户本次明确要改。入口里若还列着未选中的取值，删到只剩当前这一档。

#### `docs/ssot-registry.md` — SSOT 注册表

应用 [../templates/ssot-registry.md](../templates/ssot-registry.md) 生成，初始为空表。每当抽取公共入口时在此登记一行。

#### `docs/debugging/records/` — 历史排障记录

初始为空目录。属于按需检索的 case 库：每次排查完问题后，以 `<YYYY-MM-DD>-<症状简述>.md` 命名，应用 [../templates/debugging-record.md](../templates/debugging-record.md) 生成简短记录，并在 `docs/debugging/registry.md` 表格中补登一行（严格保持表格格式，不把单篇 record 加入 `<AI_ENTRY>.md` 的主文档索引）。

**查问题前必须先检索 [`docs/debugging/registry.md`](../templates/debugging-registry.md)**，确认是否有同质症状的既有结论——同一个症状不应在仓库里出现两套排查结论（SSOT 原则的延伸）。

#### `docs/evolution/` — 持续进化记录

应用 [../templates/evolution-registry.md](../templates/evolution-registry.md) 生成 `registry.md`，`reports/` 初始为空。周期分析应用 [../templates/evolution-report.md](../templates/evolution-report.md)，创建需求/缺陷草稿时应用 [../templates/evolution-work-item.md](../templates/evolution-work-item.md)。registry 是候选项状态、外部工作项链接和验证结论的唯一信源；报告是按周期生成的不可变证据快照。具体执行协议见 [evolution.md](evolution.md)。

#### `docs/observability.md` — 可观测性基础设施总览

应用 [../templates/observability.md](../templates/observability.md) 生成，按技术栈替换日志框架占位符：

| 技术栈 | 日志框架 |
|--------|---------|
| Go | log/slog 或 zap |
| Node.js / TypeScript | pino |
| Python | loguru |

#### `docs/evaluation.md` — 验证与评测总览

应用 [../templates/evaluation.md](../templates/evaluation.md) 生成 `docs/evaluation.md`，将本项目实际采用的验证载体（单测、集成测试、黑盒/E2E、或按需建立的 `evals/` 评测与运行期脚本）及其运行命令登记于此。具体执行协议见 [evaluation.md](evaluation.md)。

#### `docs/testing.md` — 单元测试指南

应用 [../templates/testing.md](../templates/testing.md) 生成，填写实际的运行命令。关注如何写好单元测试（它本身是 L1 程序化验证的重要载体之一）。

#### `docs/design/<module>.md` — 功能/模块设计文档（spec）

按稳定业务域/子系统建文件（不为单次评审、修复批次或零散小补丁单开文件）。应用 [../templates/design.md](../templates/design.md) 生成，遵循其中的唯一信源与现态原则——更新一律就地改写现态，不堆叠批次流水，废弃文档直接删除交给 Git 留档。

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
