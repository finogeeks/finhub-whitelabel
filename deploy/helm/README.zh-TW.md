[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Helm 覆寫層

白標 FinHub 部署的 values 與 ConfigMap 說明。Chart 路徑來自您的**離線發佈套件**（例如 tarball 中的 `deploy/k8s/helm/chatkit`）。

範例主機：**`hub.example.com`**（僅為 ingress 便利 — 品牌由 `platform_settings` + 掛載決定，而非主機名稱邏輯）。

## 檔案

| File | Role |
|------|------|
| `values-whitelabel.yaml` | Persona pin + sync Job + branding ConfigMap names + example ingress |
| `values-finops-staff-auth.example.yaml` | finops-staff `existingSecret` / `secretKeys` / 開發 `createSecret` 覆寫層 |
| `values-alertmanager-finops.example.yaml` | kube-prometheus-stack 接收器；finops-staff webhook 使用 `bearer_token_file` |
| `persona-pack-configmap.yaml` | Starter pack from repo root `persona-templates.json` |
| `platform-settings-configmap.yaml` | Option B `platform_settings` seed |
| `branding-assets-configmap.yaml` | Mark / wordmark / favicon / OG → `/static/branding` |

## 建立 ConfigMaps

```bash
kubectl create configmap wl-persona-pack \
  --from-file=persona-templates.json=../../persona-templates.json \
  -n <namespace> --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap wl-platform-settings \
  --from-file=platform-settings.json=../../branding/platform-settings.json \
  -n <namespace> --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap wl-branding-assets \
  --from-file=../../branding/assets/ \
  -n <namespace> --dry-run=client -o yaml | kubectl apply -f -
```

在 `persona-service` 上將 persona pack 掛載到 `/pack/persona-templates.json`。將品牌 SVG 掛載到 **`/static/branding`**。

## Persona sync Job（先 dry-run）

```bash
helm upgrade --install chatkit deploy/k8s/helm/chatkit \
  -f deploy/helm/values-whitelabel.yaml \
  --set personaTemplateSyncJob.enabled=true \
  --set personaTemplateSyncJob.packConfigMap=wl-persona-pack \
  --set personaTemplateSyncJob.extraArgs[0]=--dry-run \
  --set servicesEnv.persona-service.PERSONA_TEMPLATE_CONFIG_PATH=/pack/persona-templates.json
```

不帶 `extraArgs` 重新執行以套用 `replace_platform`。

## Platform settings 種子

部署後，透過管理員 **PUT** 使用 `branding/platform-settings.json` 種子，或執行讀取 ConfigMap `wl-platform-settings` 的站點專用 Job。

未使用 `values-whitelabel.yaml` 的預設部署保持上游經典預設值 — 無白標固定。

## 選用 finops-staff

發行 Chart 提供 `finopsStaff` 時，僅在維運明確要求時設定 `enabled: true`；優先 `policyMode: readonly`。預設 `autoActDisabled: true`、`closedLoopEnabled: false`、`notifyMinSeverity: warning`。詳見 [`docs/operations/finops-staff.zh-TW.md`](../../docs/operations/finops-staff.zh-TW.md)。

**認證 Secret（生產）：** 在叢集建立含 `alert_webhook_token`、`internal_api_token` 等鍵的 Secret，設定 `finopsStaff.existingSecret`；勿將令牌寫入 git。合併 [`values-finops-staff-auth.example.yaml`](./values-finops-staff-auth.example.yaml)。僅開發／實驗室可使用 `finopsStaff.createSecret.enabled: true`。

**Alertmanager：** FinHub Chart 不部署 Alertmanager。將同一 `alert_webhook_token` 掛載到 prometheus 堆疊，接收器使用 `bearer_token_file` — 見 [`values-alertmanager-finops.example.yaml`](./values-alertmanager-finops.example.yaml) 與 [`deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml`](../monitoring/alertmanager-finops-staff-receiver-snippet.yml)。

監控 CR 說明：[`docs/operations/monitoring.zh-TW.md`](../../docs/operations/monitoring.zh-TW.md)。
