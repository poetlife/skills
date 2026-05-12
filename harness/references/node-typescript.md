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
