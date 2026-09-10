# neo-codebuddy skills

个人全局 Skills 仓库，供 CodeBuddy Code 在所有项目中使用。

## 目录结构

```
skills/
├── <skill-name>/
│   └── SKILL.md
└── README.md
```

## Skills 列表

### `add-user-memory`

向项目级记忆文件的 `## 用户指定记忆` 节追加用户自定义条目。

**支持的 AI 工具：**

| 工具 | 记忆文件 |
|------|---------|
| CodeBuddy Code | `CODEBUDDY.md` |
| Claude Code | `CLAUDE.md` |
| OpenAI Codex CLI | `AGENTS.md` |

检测顺序：`CODEBUDDY.md` → `CLAUDE.md` → `AGENTS.md`，均不存在时默认创建 `CODEBUDDY.md`。

**约束：** 已有条目受用户保护，追加无需确认，修改/删除需用户明确授权。

**触发方式：** "记住……"、"帮我记录……"、"以后要记得……"、"remember that"、"keep in mind"、`/add-user-memory <内容>`

### `goal-to-prompt`

提供“写入”和“检索使用”两个入口：按一类事情记录不同条件下的处理方案、关键流程及提示词，使用时根据当前输入选择合适路线。支持逐步沉淀个人经验。

**写入方式：** `/goal-to-prompt 记下这件事的处理方式：简单情况用方案 A，复杂情况用方案 B。`

**检索方式：** `/goal-to-prompt 找一下这件事以前怎么做，根据当前输入选方案并给出提示词。`

默认记录库为 `~/.local/share/goal-to-prompt`，每条记录存于 `records/<record-id>.md`。可以说“把记录库设置为 /指定目录”持久配置，也可临时指定目录；检索默认只读。目录配置与存取约定见 [本地存储说明](goal-to-prompt/references/local-store.md)。

## 新增 Skill

1. 创建目录 `skills/<skill-name>/`
2. 在目录内创建 `SKILL.md`（YAML frontmatter + Markdown 说明）
3. 在本 README 的 Skills 列表中补充说明
4. 提交到 git
