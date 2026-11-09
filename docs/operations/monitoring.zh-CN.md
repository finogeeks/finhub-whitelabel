[English](./monitoring.md) | [简体中文](./monitoring.zh-CN.md) | [繁體中文](./monitoring.zh-TW.md)

# 监控与 FinOps 告警

FinHub **无需**监控栈即可运行。Prometheus、Alertmanager、Grafana 为**可选**，不在业务请求路径上。

启用 **finops-staff** 时（见 [FinOps 辅助服务](./finops-staff.zh-CN.md)），服务会**读取** Prometheus 并**接收** Alertmanager Webhook，不替代您现有的监控平台。

本指南与供应商发行版提交 `64baa121` 的布局一致。完整文件在**离线发行包**中；本仓库仅提供 [示例片段](../../deploy/monitoring/)。

## 架构要点

| 组件 | 默认部署是否包含 | 作用 |
|------|------------------|------|
| finclaw `/metrics` | 是（Observer） | 应用指标 |
| Prometheus / Alertmanager / Grafana | 否（`observability` 配置或自备） | 采集、路由、看板 |
| finops-staff | 否 | 诊断与受控修复 |

## 指标端点与采集认证

`AI_INFRA_RS_OBSERVER_BACKEND` 需包含 `prometheus` 才会暴露 `/metrics`（发行版默认常为 `log,prometheus`）。

| 目标 | 路径 | 端口（典型） | 采集认证（发行版配置） | 说明 |
|------|------|--------------|------------------------|------|
| 平台 **ai-infra-rs** | `/metrics` | `26450` | **无** | 狗食 Prometheus 使用 `chatkit-ai-infra-rs:26450` |
| 租户 claw | `/metrics` 或仅 `/health` | `26450` 等 | **无**（暴露 `/metrics` 时） | Hermes/openclaw 可能仅健康检查 |
| **api-gateway** | — | — | — | 发行版 compose **无**网关 `/metrics`；网关告警需 K8s ingress-nginx 指标 |
| postgres/redis exporter | `/metrics` | `9187` / `9121` | **无** | 仅 observability 配置 |
| finops-staff | `/health` | `26116` | 告警 Webhook 用 Bearer | 非采集目标 |
| prometheus-dogfood | UI | `9090` | **无**（仅 localhost） | |
| grafana-dogfood | UI | `3030` | 管理员密码 `GRAFANA_DOGFOOD_ADMIN_PASSWORD` | |

**缓解措施：** 勿将 `26450` 暴露到公网；使用内网、NetworkPolicy 或反向代理终止采集认证。

Kubernetes：可选 `ServiceMonitor`、`PrometheusRule`；Pod 注解 `prometheus.io/scrape` 等（见英文版 Helm 表）。

## FinOps 告警规则

规则文件：发行包 `deploy/observability/finops-alert-rules.yaml`（本仓库副本见 [deploy/monitoring](../../deploy/monitoring/finops-alert-rules.yaml)）。Compose 狗食环境主要可靠触发 **`chatkit.finops.compose`**（finclaw `up`）；多数规则依赖集群级序列（kubelet、ingress 等）。

| 告警名 | 严重度 | 路由 | 含义 |
|--------|--------|------|------|
| `FinHubFinOpsDiskLogVolumeHigh` | critical | page | 卷或容器文件系统使用率过高 |
| `FinHubFinOpsConvstorePostgresSaturated` | critical | page | convstore 连接数压力（需 postgres_exporter） |
| `FinHubFinOpsGatewayErrorBudgetBurn` | warning | ticket | 网关 5xx &gt; 5% |
| `FinHubFinOpsGatewayErrorBudgetBurnCritical` | critical | page | 网关 5xx &gt; 15% |
| `FinHubFinOpsClawReadyBelowDesired` | warning | ticket | StatefulSet 就绪副本不足 |
| `FinHubFinOpsAdapterProbeFailed` | critical | page | 适配器探针/采集失败 |
| `FinHubFinOpsCapabilityRegression` | warning | ticket | finclaw 循环质量回归信号 |
| `FinHubFinOpsReconcileStuck` | warning | ticket | **占位**（指标未实现，规则不触发） |
| `FinHubFinOpsComposeFinclawScrapeDown` | critical | page | Compose：finclaw 采集目标 down |

## 选项 A — 复用现有监控

1. 合并 [prometheus-scrape-snippet.yml](../../deploy/monitoring/prometheus-scrape-snippet.yml) 与 [finops-alert-rules.yaml](../../deploy/monitoring/finops-alert-rules.yaml)。
2. Alertmanager 合并 [alertmanager-finops-staff-receiver-snippet.yml](../../deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml)；`bearer_token_file` 与 `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` 相同。
3. Webhook：`POST http://<finops-staff>:26116/webhooks/alertmanager`；认证为 `Authorization: Bearer …` 或头 `x-finops-alert-webhook-token`。
4. Grafana：配置 Prometheus 数据源，可导入 [grafana-finops-compose-dogfood.json](../../deploy/monitoring/grafana-finops-compose-dogfood.json)。

**Helm：** FinHub Chart **不部署** Prometheus/Alertmanager/Grafana；可渲染 `PrometheusRule`、`ServiceMonitor`（需 Prometheus Operator）。**不**包含 `PodMonitor`、`AlertmanagerConfig`、Grafana。`finopsStaff` 默认 `prometheusUrl: http://prometheus-operated:9090`；Chart **未**模板化 `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN`，需站点 Secret 注入。

## 选项 B — 部署 observability 配置

环境变量（仅名称）：`GRAFANA_DOGFOOD_ADMIN_PASSWORD`、`FINOPS_STAFF_ALERT_WEBHOOK_TOKEN`、`FINOPS_STAFF_INTERNAL_API_TOKEN` 等。

```bash
docker compose -f docker-compose.prod.yml \
  -f docker-compose.observability.yml \
  --profile observability up -d
```

可选叠加 `finops-staff`、`finops-dogfood` 配置。验证：Prometheus 目标 UP、规则组加载、Grafana `127.0.0.1:3030`。

**离线镜像（标签）：** `prom/prometheus:v2.55.0`、`prom/alertmanager:v0.27.0`、`prometheuscommunity/postgres-exporter:v0.15.0`、`oliver006/redis_exporter:v1.62.0`、`grafana/grafana:11.2.2`。

## 生产加固（已知差距）

发行版标明 **狗食**。要点：postgres-exporter DSN 内含凭据、Prometheus 无持久卷、Prom/AM 无 TLS/认证、单副本、Grafana 管理员口令、未认证的 `/metrics`、Compose 上大量规则处于 idle、Helm 未挂载告警 Webhook Token、`FinHubFinOpsReconcileStuck` 无对应指标。生产优先选 **选项 A** 在企业监控上落地。

## 相关

- [安装](./install.zh-CN.md) · [环境参考](./env-reference.zh-CN.md) · [日常运维](./day-2-ops.zh-CN.md)
- [FinOps 辅助服务](./finops-staff.zh-CN.md) · [FinOps 通知](./finops-notifications.zh-CN.md)
- [`skills/finhub-monitoring/SKILL.md`](../../skills/finhub-monitoring/SKILL.md)
- [英文完整版](./monitoring.md)
