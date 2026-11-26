# Go 项目规范

本 reference 定义 Go 项目的代码规范、静态门禁（L0）、测试与统一检查入口。适用于单模块项目与多模块大仓（`go.work`）。

## 模块与目录约定

- **单模块项目**：根目录放 `go.mod`，私有业务放 `internal/`，对外包放 `pkg/`，可执行入口放 `cmd/<app>/`。
- **多模块大仓（`go.work`）**：根目录只放 `go.work`，业务服务位于 `services/<svc>/` 且各自拥有独立 `go.mod` 与私有 `internal/`；跨服务公共契约放 `api/`、公共库放 `pkg/`、数据模型/迁移放 `db/`、自研检查与研发工具放 `tools/`。
- **依赖方向显式单向**：`services/* → pkg → api`、`services/* → db`；`internal/entity`（领域层）保持纯净，不依赖传输层（pb/HTTP/RPC 框架）与存储实现（db/ORM）。

## 静态检查配置（`golangci-lint` v2）

推荐启用基础静态分析 + 导出符号 godoc 检查 + `depguard` 分层守门 + `gofumpt` 格式化。

**`.golangci.yml`**：

```yaml
version: "2"

linters:
  default: none
  enable:
    - govet
    - errcheck
    - staticcheck
    - ineffassign
    - unused
    - revive
    - depguard
  settings:
    revive:
      rules:
        # 所有导出符号（type/func/method/const/var/interface 方法）必须有 godoc 且以符号名开头
        - name: exported
          arguments:
            - checkPublicInterface
            - disableStutteringCheck
    depguard:
      rules:
        # 示例：领域层纯净度守门（按项目实际模块路径调整）
        entity-pure-domain:
          files:
            - "**/internal/entity/**"
          deny:
            - pkg: gorm.io/gorm
              desc: "分层规范：entity 层不得依赖 ORM"
        # 可继续追加：跨服务域模型隔离、禁止绕开统一错误包等规则
  exclusions:
    generated: lax
    # 注意：不要开启默认 comments preset，否则会吞掉导出方法 godoc 命名格式检查
    presets: []

formatters:
  enable:
    - gofumpt
  settings:
    gofumpt:
      module-path: <your-module-prefix>
  exclusions:
    generated: lax
```

> 若项目已存在 `.golangci.yml`，**不要覆盖**，将缺失的 linter、`depguard` 规则与 `gofumpt` 配置增量合并进去。
> 复杂 `depguard` 规则建议配一条轻量反向探针测试（在临时模块中故意 import 被禁包并断言 `golangci-lint` 返回非零），避免 glob 写错导致静默失效（详见 [static-checks.md](static-checks.md)）。

## 自定义 AST / Schema 检查器

当通用 linter 无法覆盖项目红线时（如禁止在请求路径使用 `context.Background()`/`context.TODO()` 切断 trace、禁止裸 `go`、禁止散落读 `os.Getenv`、或校验 Protobuf `FileDescriptorSet` 契约），在 `tools/<name>check/` 下用标准库 `go/ast`、`go/parser` 编写独立检查器：

- 支持行内有因豁免（`//<name>check:allow <非空原因>`）；
- 存量项目使用 `baseline.go` 实现棘轮基线（新增失败、存量减少时强制收缩）；
- 配套 `main_test.go` 验证检查器自身逻辑；
- 在 `Makefile` 的 `lint` 目标中于 `golangci-lint` 之前执行。

详细设计标准见 [static-checks.md](static-checks.md)。

## 单元测试约定

- **目录与命名**：遵循 Go 默认惯例，`*_test.go` 与被测文件同目录；测试对外契约优先使用外部测试包 `package foo_test`。
- **依赖替换**：优先使用标准库 `testing` + Table Driven Tests（`t.Run`）；repo 依赖优先用包内 `Memory` 实现或测试内轻量 fake，避免重度 mock 框架。
- **并发与缓存**：关键并发路径需跑 `go test -race ./...`；集成回归加 `-count=1` 避免命中测试缓存；需要真实外部存储的用例通过环境变量隔离专用测试库，并在文档中注明跳过条件。

## 统一门禁入口（`Makefile`）

推荐在根目录提供统一 `Makefile`，将格式化、生成物校验、静态门禁与测试收口为单一 `make check` 命令，供本地提交前与 CI 共用：

```makefile
.PHONY: fmt fmt-check gen gen-check lint test check

fmt:
	# 格式化源码 / proto 等

fmt-check:
	# 校验格式无差异（CI）

gen:
	# 执行代码生成（proto / wire / sqlc 等）

gen-check:
	# 校验生成工具版本、重新生成并用 git diff --exit-code 验证无漂移

lint:
	# 1. 运行项目自定义检查器（如 go run ./tools/ctxcheck -root .）
	# 2. 运行 golangci-lint run -c .golangci.yml --timeout 5m ./...

test:
	go test ./...

check: fmt-check gen-check lint test
```

## 可观测性建议

- 日志框架：`log/slog`（标准库）或 `zap`（及框架封装）。
- 上下文透传：业务函数首参统一为 `ctx context.Context`，异步任务必须继承上下文并带 panic recover；必要时通过 `ctxcheck` 类检查器在 L0 锁死。
