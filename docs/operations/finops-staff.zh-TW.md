[English](./finops-staff.md) | [简体中文](./finops-staff.zh-CN.md) | [繁體中文](./finops-staff.zh-TW.md)

# finops-staff（選用受監督自愈）

**finops-staff** 為選用平台服務：告警接入、有界診斷、**人工核准**後的修復。不在使用者對話路徑上——停止或停用**不會**影響 FinHub 對話服務。

客戶預設：**不啟用**（無 compose profile / `finopsStaff.enabled=false`）。

## 啟用

**Docker Compose**

```bash
# 在 .env.example 取消 finops 存根註解、設定策略預設，再 gen-secrets 產生權杖
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff up -d
```

**Helm**

```bash
helm upgrade --install <release> <chart-path> \
  -f deploy/helm/values-whitelabel.yaml \
  -f <release-chart>/values-finops-staff-auth.example.yaml \
  --set finopsStaff.enabled=true \
  --set finopsStaff.policyMode=readonly \
  --set finopsStaff.existingSecret=finops-staff-auth
```

Compose（`docker-compose.finops-staff.yml`）與 Helm（`finopsStaff` 值及渲染後的 env）均預設**關閉 auto-act**與**關閉 closed-loop**：`FINOPS_STAFF_AUTO_ACT_DISABLED=true`、`FINOPS_STAFF_CLOSED_LOOP_ENABLED=false`（除非維運覆寫）。發佈套件行為已在 `cb3e6418` 核對。

| 項 | 值 |
|------|--------|
| 預設連接埠 | `26116` |
| 健康檢查 | `GET /health`（公開） |
| 告警入口 | `POST /webhooks/alertmanager` |
| 診斷/執行 | `POST /internal/*` |
| 核准 | `POST /webhooks/approval` |
| 稽核 | `GET /internal/audit` |
| Doctor JSON | `GET /internal/doctor` |

`.env` 中的 `INTERNAL_SERVICE_TOKEN` 供 finops-staff 存取 claw-fleet-manager（見發佈套件 `docker-compose.finops-staff.yml`）。

## Doctor 快照（`GET /internal/doctor`）

唯讀 JSON（`finops-doctor/v1`），用於升級後姿態核對 — 不能取代發佈套件 `scripts/doctor.sh`。

| 欄位 | 客戶預設 | 含義 |
|------|----------|------|
| `auto_act_disabled` | `true` | 自動修復動作保持關閉 |
| `closed_loop_enabled` | `false` | 閉環控制器保持關閉 |

另含 `notify_channels_configured`、`notify_channels_listed` 與 `notify_startup_warnings`。可在不啟用 auto-act 的情況下確認斷路開關與通知配置。

## 策略模式

| 模式 | 診斷 | 修復 |
|------|----------|-----------|
| `readonly`（預設） | 是 | 拒絕 |
| `supervised` | 是 | 白名單動作；**須核准** |
| `full` | 是 | 更廣白名單；生產副本寫入另有閘門 |

僅在 SecAI/安全團隊核准後將 disposable 堆疊升為 `supervised`。客戶文件**不**涵蓋啟用無人值守 auto-act 或 closed-loop。

## 文件化斷路開關（保持預設）

```bash
FINOPS_STAFF_AUTO_ACT_DISABLED=true
FINOPS_STAFF_CLOSED_LOOP_ENABLED=false
```

請勿為客戶生產環境啟用自動艦隊 PATCH 或 closed-loop 週期工作。

## 告警 → 診斷 → 待修復 → 核准

1. **Alertmanager** 呼叫 `http://<finops-staff>:26116/webhooks/alertmanager`，可選 `Authorization: Bearer <FINOPS_STAFF_ALERT_WEBHOOK_TOKEN>` 或標頭 `x-finops-alert-token`。

2. **入口模式**（生產告警流至多擇一，演練套件除外）：
   - `FINOPS_STAFF_ALERT_DIAGNOSE_ONLY=true` — 僅通知與診斷
   - `FINOPS_STAFF_ALERT_PENDING_REPAIR=true` — 需 `FINOPS_STAFF_POLICY_MODE=supervised`；依帶 `act`、`tenant_id`、`deployment_id` 標籤的 firing 告警建立**待處理**白名單動作（不自動執行）

3. **人工核准** — `POST /webhooks/approval`，JSON 含 `decision_id`、`approved`、`actor`；若設定 `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` 則帶標頭 `x-finops-approval-token`：

```bash
curl -sS -X POST "https://<finops-host>:26116/webhooks/approval" \
  -H 'Content-Type: application/json' \
  -H 'x-finops-approval-token: <FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN>' \
  -d '{"decision_id":"<id>","approved":true,"actor":"oncall"}'
```

4. **執行** — 核准後對同一 `decision_id` 再呼叫 `POST /internal/act`。

5. **冷卻** — `FINOPS_STAFF_RESTART_COOLDOWN_MS`（預設 `300000`）限制同部署重啟頻率。

6. **稽核** — 記錄 `tenant_id`、`actor`、`decision_id`、`policy_mode`、fleet 路徑；`GET /internal/audit` 查詢。

## 白名單動作（supervised / full）

| 動作 | 說明 |
|-----|-------|
| `log_rotate` | 僅策略確認；無主機 exec |
| `fleet_restart` | 經 claw-fleet-manager |
| `fleet_set_desired_replicas` | 預設非生產；生產需發佈套件中 explicit SecAI 旗標 |

**禁止 finops-staff：** 刪 PVC、資料庫 failover、縮容至零、`kubectl exec`、批量 `reconcile-all`、繞過 identity 的管理介面。

## 權杖（Webhook 暴露時建議）

在 `.env` 取消存根後執行 `./scripts/gen-secrets.sh`：

| 變數 | 用途 |
|----------|---------|
| `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` | Alertmanager |
| `FINOPS_STAFF_INTERNAL_API_TOKEN` | `POST /internal/*`（health 仍公開） |
| `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` | 選用核准 Webhook 閘門 |

## Helm 認證密鑰

生產：在叢集中建立 Secret（勿寫入 git），再在發行 Chart 中引用。

```bash
kubectl create secret generic finops-staff-auth \
  --from-literal=alert_webhook_token=<alert-webhook-token> \
  --from-literal=internal_api_token=<internal-api-token> \
  --from-literal=approval_webhook_token=<approval-webhook-token> \
  -n <namespace>
```

| Helm 值 | 預設 | 對應 Pod 環境變數 |
|---------|------|-------------------|
| `finopsStaff.existingSecret` | `""` | 存放認證鍵的 Secret 名稱（生產推薦） |
| `finopsStaff.secretKeys.alertWebhookToken` | `alert_webhook_token` | `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` |
| `finopsStaff.secretKeys.internalApiToken` | `internal_api_token` | `FINOPS_STAFF_INTERNAL_API_TOKEN` |
| `finopsStaff.secretKeys.approvalWebhookToken` | `approval_webhook_token` | `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` |
| `finopsStaff.createSecret.enabled` | `false` | **僅開發／實驗室** — `true` 且未設定 `existingSecret` 時由 Chart 渲染 Secret；`createSecret.*` 使用占位符如 `<alert-webhook-token>` |
| `finopsStaff.notifyMinSeverity` | `warning` | `FINOPS_STAFF_NOTIFY_MIN_SEVERITY`：`info`、`warning` 或 `critical` |

本儲存庫範例（路徑相對於發行包 Chart 目錄）：

- [`deploy/helm/values-finops-staff-auth.example.yaml`](../../deploy/helm/values-finops-staff-auth.example.yaml)
- [`deploy/helm/values-alertmanager-finops.example.yaml`](../../deploy/helm/values-alertmanager-finops.example.yaml) — Alertmanager 對 finops-staff 使用 `bearer_token_file`，勿在設定中寫內聯 `bearer_token`

**Alertmanager：** 將同一 `alert_webhook_token` 掛載到 Alertmanager（如 kube-prometheus-stack 的 `alertmanager.extraSecretMounts`），路徑與接收器中的 `bearer_token_file` 一致。可合併 [`deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml`](../../deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml)。

## Prometheus

將 `FINOPS_STAFF_PROMETHEUS_URL` 設為叢集內 Prometheus。compose 預設 `http://chatkit-prometheus-dogfood:9090` 僅用於供應商內部 dogfood——客戶環境必須覆寫。

**Alertmanager** 路由見 [監控](./monitoring.zh-TW.md)；範例設定見 [`deploy/monitoring/`](../../deploy/monitoring/)。

## 通知

外呼選用：[finops-notifications](./finops-notifications.zh-TW.md)。通道失敗隔離（診斷成功時仍回傳 200）。

## 下線

```bash
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff down
```

對話與核心平台繼續運行。

## 相關

- [監控](./monitoring.zh-TW.md) · [`skills/finhub-monitoring/SKILL.md`](../../skills/finhub-monitoring/SKILL.md)
- [安裝](./install.zh-TW.md) · [環境參考](./env-reference.zh-TW.md) · [日常維運](./day-2-ops.zh-TW.md)
