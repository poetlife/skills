# Python 项目规范

## 包管理器

优先使用 **uv**，其次 pip + requirements.txt。询问用户偏好。

## 代码规范配置

**`pyproject.toml`** 基础配置（使用 ruff）：

```toml
[tool.ruff]
line-length = 120
select = ["E", "F", "I"]

[tool.ruff.format]
quote-style = "double"
```

若不用 ruff，生成 **`.flake8`**：

```ini
[flake8]
max-line-length = 120
```
