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

## 指标（Metrics）

- 框架：<如 Micrometer / Prometheus client / statsd>
- 命名规范：`<project>_<module>_<metric>_<unit>`
- 必须暴露的基础指标：请求总数、错误率、响应延迟（P50/P99）

## 链路追踪（Tracing）

- 框架：<如 OpenTelemetry>
- TraceID 传播：通过 HTTP Header `X-Trace-Id`

## 健康检查

- 端点：`GET /health`，返回 `{"status": "ok"}`
