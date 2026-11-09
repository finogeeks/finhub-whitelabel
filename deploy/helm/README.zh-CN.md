[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Helm 覆盖层

白标 FinHub 部署的 values 与 ConfigMap 说明。Chart 路径来自您的**离线发布包**（例如 tarball 中的 `deploy/k8s/helm/chatkit`）。

示例主机：**`hub.example.com`**（仅为 ingress 便利 — 品牌由 `platform_settings` + 挂载决定，而非主机名逻辑）。

## 文件

| File | Role |
|------|------|
| `values-whitelabel.yaml` | Persona pin + sync Job + branding ConfigMap names + example ingress |
| `values-finops-staff-auth.example.yaml` | finops-staff `existingSecret` / `secretKeys` / 开发 `createSecret` 覆盖层 |
| `values-alertmanager-finops.example.yaml` | kube-prometheus-stack 接收器；finops-staff webhook 使用 `bearer_token_file` |
| `persona-pack-configmap.yaml` | Starter pack from repo root `persona-templates.json` |
| `platform-settings-configmap.yaml` | Option B `platform_settings` seed |
| `branding-assets-configmap.yaml` | Mark / wordmark / favicon / OG → `/static/branding` |

## 创建 ConfigMaps

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

在 `persona-service` 上将 persona pack 挂载到 `/pack/persona-templates.json`。将品牌 SVG 挂载到 **`/static/branding`**。

## Persona sync Job（先 dry-run）

```bash
helm upgrade --install chatkit deploy/k8s/helm/chatkit \
  -f deploy/helm/values-whitelabel.yaml \
  --set personaTemplateSyncJob.enabled=true \
  --set personaTemplateSyncJob.packConfigMap=wl-persona-pack \
  --set personaTemplateSyncJob.extraArgs[0]=--dry-run \
  --set servicesEnv.persona-service.PERSONA_TEMPLATE_CONFIG_PATH=/pack/persona-templates.json
```

不带 `extraArgs` 重新运行以应用 `replace_platform`。

## Platform settings 种子

部署后，通过管理员 **PUT** 使用 `branding/platform-settings.json` 种子，或运行读取 ConfigMap `wl-platform-settings` 的站点专用 Job。

未使用 `values-whitelabel.yaml` 的默认部署保持上游经典默认值 — 无白标固定。

## 可选 finops-staff

发行 Chart 提供 `finopsStaff` 时，仅在运维明确要求时设置 `enabled: true`；优先 `policyMode: readonly`。默认 `autoActDisabled: true`、`closedLoopEnabled: false`、`notifyMinSeverity: warning`。详见 [`docs/operations/finops-staff.zh-CN.md`](../../docs/operations/finops-staff.zh-CN.md)。

**认证 Secret（生产）：** 在集群创建含 `alert_webhook_token`、`internal_api_token` 等键的 Secret，设置 `finopsStaff.existingSecret`；勿将令牌写入 git。合并 [`values-finops-staff-auth.example.yaml`](./values-finops-staff-auth.example.yaml)。仅开发/实验室可使用 `finopsStaff.createSecret.enabled: true`。

**Alertmanager：** FinHub Chart 不部署 Alertmanager。将同一 `alert_webhook_token` 挂载到 prometheus 栈，接收器使用 `bearer_token_file` — 见 [`values-alertmanager-finops.example.yaml`](./values-alertmanager-finops.example.yaml) 与 [`deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml`](../monitoring/alertmanager-finops-staff-receiver-snippet.yml)。

监控 CR 说明：[`docs/operations/monitoring.zh-CN.md`](../../docs/operations/monitoring.zh-CN.md)。
