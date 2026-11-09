[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Helm overlays

Values and ConfigMap notes for a white-label FinHub deploy. Chart path comes from your **offline release** (e.g. `deploy/k8s/helm/chatkit` in the tarball).

Example host: **`hub.example.com`** (ingress convenience only — branding is `platform_settings` + mounts, not hostname logic).

## Files

| File | Role |
|------|------|
| `values-whitelabel.yaml` | Persona pin + sync Job + branding ConfigMap names + example ingress |
| `persona-pack-configmap.yaml` | Starter pack from repo root `persona-templates.json` |
| `platform-settings-configmap.yaml` | Option B `platform_settings` seed |
| `branding-assets-configmap.yaml` | Mark / wordmark / favicon / OG → `/static/branding` |

## Create ConfigMaps

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

Mount the persona pack on `persona-service` at `/pack/persona-templates.json`. Mount brand SVGs at **`/static/branding`**.

## Persona sync Job (dry-run first)

```bash
helm upgrade --install chatkit deploy/k8s/helm/chatkit \
  -f deploy/helm/values-whitelabel.yaml \
  --set personaTemplateSyncJob.enabled=true \
  --set personaTemplateSyncJob.packConfigMap=wl-persona-pack \
  --set personaTemplateSyncJob.extraArgs[0]=--dry-run \
  --set servicesEnv.persona-service.PERSONA_TEMPLATE_CONFIG_PATH=/pack/persona-templates.json
```

Re-run without `extraArgs` to apply `replace_platform`.

## Platform settings seed

After deploy, seed via admin **PUT** with `branding/platform-settings.json`, or run your site-specific Job that reads ConfigMap `wl-platform-settings`.

Default deploy without `values-whitelabel.yaml` keeps upstream classic defaults — no white-label pin.

## Optional finops-staff

If the release Helm chart exposes `finopsStaff`, set `enabled: true` only when requested. Prefer `policyMode: readonly`. Current release charts default `autoActDisabled: true` and `closedLoopEnabled: false` and inject matching pod env unless overridden (same as compose finops-staff profile). See [`docs/operations/finops-staff.md`](../../docs/operations/finops-staff.md) and [`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md).

The FinHub chart does not install Prometheus or Grafana; optional `ServiceMonitor` / `PrometheusRule` CRs are documented in [`docs/operations/monitoring.md`](../../docs/operations/monitoring.md).
