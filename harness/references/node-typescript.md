# Node.js / TypeScript 项目规范

## 包管理器

优先使用 **pnpm**，其次 npm。询问用户偏好。

## TypeScript 配置

**`tsconfig.json`**：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "strict": true,
    "noImplicitAny": true,
    "esModuleInterop": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

## 代码规范配置

ESLint 配置详见 [references/eslint-typescript.md](eslint-typescript.md)，应用时需考虑与用户已有配置合并。

Prettier 管理格式，与 ESLint 职责分离：

**`.prettierrc`**：

```json
{
  "singleQuote": true,
  "semi": false,
  "printWidth": 100,
  "trailingComma": "all"
}
```

## L0 静态门禁与架构边界

在基础 lint/format 之上，建议按需补齐以下 L0 护栏（设计原则见 [static-checks.md](static-checks.md)）：

- **类型检查门禁**：`tsc --noEmit`（独立于构建，作为硬门禁运行）。
- **模块与分层边界**：使用 `eslint-plugin-import`（`import/no-restricted-paths`）或 `dependency-cruiser` 强制单向依赖与域隔离（例如禁止领域层依赖 ORM/框架层、禁止跨模块直连内部实现）。
- **生成物一致性**：若存在 OpenAPI / GraphQL / Protobuf / Prisma 等生成物，提供 `gen:check`（重新生成 + `git diff --exit-code`）。
- **统一门禁入口**：在 `package.json` 中收口单一 `check` 脚本，本地交付与 CI 共用：

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "lint": "eslint .",
    "fmt:check": "prettier --check .",
    "test": "vitest run",
    "check": "pnpm fmt:check && pnpm typecheck && pnpm lint && pnpm test"
  }
}
```
