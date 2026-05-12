# 可观测性总览

本文档描述本项目可观测性基础设施的接入方式与使用规范。

## 日志（Logging）

- 框架：<如 SLF4J+Logback / Winston / structlog>
- 格式：结构化 JSON
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
