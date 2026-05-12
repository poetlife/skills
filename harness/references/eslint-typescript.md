# ESLint 配置（TypeScript）

## 依赖安装

```bash
pnpm add -D eslint @eslint/js typescript-eslint eslint-plugin-jsdoc
```

## 默认配置

**`eslint.config.js`**：

```js
import tseslint from "typescript-eslint";
import jsdoc from "eslint-plugin-jsdoc";
import js from "@eslint/js";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.ts", "**/*.tsx"],
    plugins: { jsdoc },
    rules: {
      // 文件有效代码行上限 800 行（不含注释和空行）
      "max-lines": ["warn", { max: 800, skipBlankLines: true, skipComments: true }],

      // 所有 export 的顶层声明应附带 JSDoc 注释
      "jsdoc/require-jsdoc": ["warn", {
        publicOnly: true,
        require: {
          FunctionDeclaration: true,
          ClassDeclaration: true,
        },
        contexts: [
          "ExportNamedDeclaration > VariableDeclaration",
          "TSInterfaceDeclaration",
          "TSTypeAliasDeclaration",
        ],
      }],
    },
  },
  {
    files: ["**/*.ts"],
    rules: {
      // 单函数体有效代码行上限 100 行（不含注释和空行），不对 .tsx 生效
      "max-lines-per-function": ["warn", { max: 100, skipBlankLines: true, skipComments: true }],
    },
  },
];
```

## 与用户已有配置合并

若项目已存在 `eslint.config.js`，**不要覆盖**，而是将上述规则合并进去：

1. **追加 `plugins`**：将 `jsdoc` 插件加入已有的 `plugins` 对象
2. **追加 `rules`**：将三条规则（`max-lines`、`jsdoc/require-jsdoc`、`max-lines-per-function`）合并到对应 `files` 的 config 块中；若已有同名规则，询问用户是否覆盖
3. **追加 `extends`**：若用户配置尚未 spread `tseslint.configs.recommended`，在数组头部追加

合并时保留用户已有的全部规则，只补充缺失的部分。
