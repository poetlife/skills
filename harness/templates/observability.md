# 可观测性总览

本文档描述本项目可观测性基础设施的接入方式与使用规范。

## 日志（Logging）

- 框架：<如 pino / loguru / zap>
- 格式：
  - 控制台：人类可读的纯文本（含时间戳、级别、消息）
  - 文件：结构化 JSON，每行一条记录（JSON Lines）
- JSON Schema（文件输出字段定义）：
  ```json
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["timestamp", "level", "message", "trace_id"],
    "properties": {
      "timestamp": { "type": "string", "format": "date-time", "description": "ISO 8601 UTC 时间" },
      "level":     { "type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] },
      "message":   { "type": "string" },
      "logger":    { "type": "string", "description": "logger 名称 / 模块路径" },
      "trace_id":  { "type": "string", "description": "链路追踪 ID，用于串联同一请求的事件链" },
      "extra":     { "type": "object", "description": "业务自定义字段，任意键值对" }
    }
  }
  ```
- 级别约定：ERROR=需要立即处理的故障；WARN=可恢复的异常；INFO=关键业务事件；DEBUG=开发调试

### 关键路径日志链路设计

关键路径的日志必须形成可追溯的完整链路，避免故障复盘时出现"日志断点"。设计原则：

- **以排障记录为输入**：定期回顾 [`docs/debugging/registry.md`](./debugging-registry.md) 中反复出现的症状，识别那些"日志缺失/不足导致定位耗时"的故障类型，把这些路径列为关键路径。
- **关键路径的判定**：满足以下任一条件即视为关键路径，必须设计完整日志链路：
  - 在 debug registry 中出现过 ≥2 次同类症状
  - 涉及外部依赖调用（数据库、第三方 API、消息队列）
  - 涉及资金、权限、数据一致性等不可逆操作
  - 跨服务/跨进程的请求链路
- **完整链路的最低要求**：
  - **入口日志**：记录请求进入时的 `trace_id`、关键入参、调用方标识
  - **关键决策点**：分支判断、缓存命中/未命中、降级触发等需 INFO 级日志
  - **外部调用**：调用前记录目标与参数，调用后记录耗时与结果（成功/失败）
  - **异常出口**：所有 catch 分支必须 ERROR 日志包含 `trace_id` + 完整堆栈 + 上下文快照
  - **正常出口**：记录处理结果摘要与总耗时
- **trace_id 传递**：同一请求在所有日志中必须携带相同 `trace_id`，跨服务调用通过 `X-Trace-Id` Header 透传。
- **闭环机制**：每次新增一条 [debugging-record](./debugging-record.md) 时，在"预防措施"小节明确补充：本次故障对应的关键路径是否已具备完整日志？若否，本次修复必须同步补齐日志埋点。

## 指标（Metrics）

- 框架：<如 Micrometer / Prometheus client / statsd>
- 命名规范：`<project>_<module>_<metric>_<unit>`
- 必须暴露的基础指标：请求总数、错误率、响应延迟（P50/P99）

## 链路追踪（Tracing）

- 框架：<如 OpenTelemetry>
- TraceID 传播：通过 HTTP Header `X-Trace-Id`

## 健康检查

- 端点：`GET /health`，返回 `{"status": "ok"}`
