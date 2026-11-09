[English](./monitoring.md) | [简体中文](./monitoring.zh-CN.md) | [繁體中文](./monitoring.zh-TW.md)

# 監控與 FinOps 告警

FinHub **無需**監控堆疊即可運作。Prometheus、Alertmanager、Grafana 為**選用**，不在業務請求路徑上。

啟用 **finops-staff** 時（見 [FinOps 輔助服務](./finops-staff.zh-TW.md)），服務會**讀取** Prometheus 並**接收** Alertmanager Webhook，不取代您現有的監控平台。

本指南與供應商發行版提交 `64baa121` 的版面一致。完整檔案在**離線發行包**中；本儲存庫僅提供 [範例片段](../../deploy/monitoring/)。

## 架構要點

| 元件 | 預設部署是否包含 | 作用 |
|------|------------------|------|
| finclaw `/metrics` | 是（Observer） | 應用指標 |
| Prometheus / Alertmanager / Grafana | 否（`observability` 設定或自備） | 蒐集、路由、儀表板 |
| finops-staff | 否 | 診斷與受控修復 |

## 指標端點與蒐集認證

`AI_INFRA_RS_OBSERVER_BACKEND` 需包含 `prometheus` 才會暴露 `/metrics`（發行版預設常為 `log,prometheus`）。

| 目標 | 路徑 | 連接埠（典型） | 蒐集認證（發行版設定） | 說明 |
|------|------|----------------|------------------------|------|
| 平台 **ai-infra-rs** | `/metrics` | `26450` | **無** | 狗食 Prometheus 使用 `chatkit-ai-infra-rs:26450` |
| 租戶 claw | `/metrics` 或僅 `/health` | `26450` 等 | **無**（暴露 `/metrics` 時） | Hermes/openclaw 可能僅健康檢查 |
| **api-gateway** | — | — | — | 發行版 compose **無**閘道 `/metrics`；閘道告警需 K8s ingress-nginx 指標 |
| postgres/redis exporter | `/metrics` | `9187` / `9121` | **無** | 僅 observability 設定 |
| finops-staff | `/health` | `26116` | 告警 Webhook 用 Bearer | 非蒐集目標 |
| prometheus-dogfood | UI | `9090` | **無**（僅 localhost） | |
| grafana-dogfood | UI | `3030` | 管理員密碼 `GRAFANA_DOGFOOD_ADMIN_PASSWORD` | |

**緩解措施：** 勿將 `26450` 暴露至公網；使用內網、NetworkPolicy 或反向代理終止蒐集認證。

Kubernetes：可選 `ServiceMonitor`、`PrometheusRule`；Pod 註解 `prometheus.io/scrape` 等（見英文版 Helm 表）。

## FinOps 告警規則

規則檔：發行包 `deploy/observability/finops-alert-rules.yaml`（本儲存庫副本見 [deploy/monitoring](../../deploy/monitoring/finops-alert-rules.yaml)）。Compose 狗食環境主要可靠觸發 **`chatkit.finops.compose`**（finclaw `up`）；多數規則依賴叢集級序列（kubelet、ingress 等）。

| 告警名 | 嚴重度 | 路由 | 意義 |
|--------|--------|------|------|
| `FinHubFinOpsDiskLogVolumeHigh` | critical | page | 磁碟區或容器檔案系統使用率過高 |
| `FinHubFinOpsConvstorePostgresSaturated` | critical | page | convstore 連線數壓力（需 postgres_exporter） |
| `FinHubFinOpsGatewayErrorBudgetBurn` | warning | ticket | 閘道 5xx &gt; 5% |
| `FinHubFinOpsGatewayErrorBudgetBurnCritical` | critical | page | 閘道 5xx &gt; 15% |
| `FinHubFinOpsClawReadyBelowDesired` | warning | ticket | StatefulSet 就緒副本不足 |
| `FinHubFinOpsAdapterProbeFailed` | critical | page | 適配器探針／蒐集失敗 |
| `FinHubFinOpsCapabilityRegression` | warning | ticket | finclaw 迴圈品質回歸信號 |
| `FinHubFinOpsReconcileStuck` | warning | ticket | **占位**（指標未實作，規則不觸發） |
| `FinHubFinOpsComposeFinclawScrapeDown` | critical | page | Compose：finclaw 蒐集目標 down |

## 選項 A — 重用現有監控

1. 合併 [prometheus-scrape-snippet.yml](../../deploy/monitoring/prometheus-scrape-snippet.yml) 與 [finops-alert-rules.yaml](../../deploy/monitoring/finops-alert-rules.yaml)。
2. Alertmanager 合併 [alertmanager-finops-staff-receiver-snippet.yml](../../deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml)；`bearer_token_file` 與 `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` 相同。
3. Webhook：`POST http://<finops-staff>:26116/webhooks/alertmanager`；認證為 `Authorization: Bearer …` 或標頭 `x-finops-alert-webhook-token`。
4. Grafana：設定 Prometheus 資料來源，可匯入 [grafana-finops-compose-dogfood.json](../../deploy/monitoring/grafana-finops-compose-dogfood.json)。

**Helm：** FinHub Chart **不部署** Prometheus/Alertmanager/Grafana；可渲染 `PrometheusRule`、`ServiceMonitor`（需 Prometheus Operator）。**不**包含 `PodMonitor`、`AlertmanagerConfig`、Grafana。`finopsStaff` 預設 `prometheusUrl: http://prometheus-operated:9090`；Chart **未**範本化 `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN`，需站點 Secret 注入。

## 選項 B — 部署 observability 設定

環境變數（僅名稱）：`GRAFANA_DOGFOOD_ADMIN_PASSWORD`、`FINOPS_STAFF_ALERT_WEBHOOK_TOKEN`、`FINOPS_STAFF_INTERNAL_API_TOKEN` 等。

```bash
docker compose -f docker-compose.prod.yml \
  -f docker-compose.observability.yml \
  --profile observability up -d
```

可選疊加 `finops-staff`、`finops-dogfood` 設定。驗證：Prometheus 目標 UP、規則組載入、Grafana `127.0.0.1:3030`。

**離線映像（標籤）：** `prom/prometheus:v2.55.0`、`prom/alertmanager:v0.27.0`、`prometheuscommunity/postgres-exporter:v0.15.0`、`oliver006/redis_exporter:v1.62.0`、`grafana/grafana:11.2.2`。

## 生產加固（已知差距）

發行版標明 **狗食**。要點：postgres-exporter DSN 內含憑證、Prometheus 無持久磁碟區、Prom/AM 無 TLS/認證、單副本、Grafana 管理員口令、未認證的 `/metrics`、Compose 上大量規則處於 idle、Helm 未掛載告警 Webhook Token、`FinHubFinOpsReconcileStuck` 無對應指標。生產優先選 **選項 A** 於企業監控上落地。

## 相關

- [安裝](./install.zh-TW.md) · [環境參考](./env-reference.zh-TW.md) · [日常維運](./day-2-ops.zh-TW.md)
- [FinOps 輔助服務](./finops-staff.zh-TW.md) · [FinOps 通知](./finops-notifications.zh-TW.md)
- [`skills/finhub-monitoring/SKILL.md`](../../skills/finhub-monitoring/SKILL.md)
- [英文完整版](./monitoring.md)
