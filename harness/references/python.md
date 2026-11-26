# Python 项目规范

## 包管理器

优先使用 **uv**，其次 pip + requirements.txt。询问用户偏好。

## 代码规范与静态门禁配置

**`pyproject.toml`** 基础配置（使用 `ruff` + `mypy`/`pyright` + `pytest`）：

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
strict = false
warn_unused_ignores = true
warn_return_any = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

若不用 ruff，生成 **`.flake8`**：

```ini
[flake8]
max-line-length = 120
```

## L0 架构边界与统一门禁

按需补齐以下 L0 护栏（通用原则见 [static-checks.md](static-checks.md)）：

- **分层与导入边界**：使用 `import-linter` 在 `pyproject.toml` 中声明 `layers` / `forbidden` 契约，阻止领域层反向依赖框架/存储层或跨模块绕开 SSOT 入口。
- **自定义静态检查**：针对项目特定红线（如禁止业务层直接读 `os.environ`、强制上下文透传），可在 `tools/` 下用标准库 `ast` 编写轻量检查器，并配套有因豁免（`#<checker>:allow <原因>`）与棘轮基线。
- **统一门禁入口**：在 `Makefile` 或 `justfile` 中提供单一 `check` 命令，供本地提交前与 CI 共用：

```makefile
.PHONY: fmt-check lint typecheck test check

fmt-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

test:
	uv run pytest

check: fmt-check lint typecheck test
```
