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

**触发方式：** "记住……"、"帮我记录……"、`/add-user-memory <内容>`

## 新增 Skill

1. 创建目录 `skills/<skill-name>/`
2. 在目录内创建 `SKILL.md`（YAML frontmatter + Markdown 说明）
3. 在本 README 的 Skills 列表中补充说明
4. 提交到 git
