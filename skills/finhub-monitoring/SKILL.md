---
name: finhub-monitoring
description: >-
  Optional FinHub monitoring: detect existing Prometheus/Alertmanager/Grafana,
  choose reuse (A) or deploy observability profile (B), wire FinOps rules and
  finops-staff webhooks, verify scrape/rules/alert delivery. Never print secrets;
  never enable auto-act.
---
# FinHub monitoring (optional)

Apply **after** Phase 1 stack health from [`finhub-deploy`](../finhub-deploy/SKILL.md). Monitoring is **not** required for chat or branding smoke tests.

## Hard rules

- **No secrets in chat or git** — report env **names** only; tokens live in `.env` or vault.
- **finops-staff** stays **off** unless the operator asked; when enabling: `FINOPS_STAFF_POLICY_MODE=readonly`, `FINOPS_STAFF_AUTO_ACT_DISABLED=true`, `FINOPS_STAFF_CLOSED_LOOP_ENABLED=false` unless operator explicitly overrides.
- **Never** enable `FINOPS_STAFF_AUTO_ACT_DISABLED=false` or closed-loop without explicit operator approval.
- **No writes** to Prometheus/Alertmanager/Grafana/production `.env` without operator confirmation.
- Do **not** link or name private vendor git URLs in customer-facing output.

## Scope

| Source | Provides |
|--------|----------|
| Vendor **offline release** | `docker-compose.observability.yml`, `deploy/observability/*`, Helm `observability` / `finopsStaff`, finops-staff image |
| **This repo** | [`docs/operations/monitoring.md`](../../docs/operations/monitoring.md), [`deploy/monitoring/`](../../deploy/monitoring/), this skill |

## Phase 0 — Detect

1. Confirm release root (tarball unpack) and `docker compose` or Helm as deployed.
2. Ask the operator (if unknown):
   - Existing Prometheus / Alertmanager / Grafana / Grafana Cloud / Datadog with PromQL remote read?
   - Need **finops-staff** or metrics-only?
3. Record platform: **Compose** vs **Kubernetes**.

**Signals of existing monitoring (K8s):** `ServiceMonitor`/`PrometheusRule` CRDs, `kube-prometheus-stack`, Alloy, or central scrape config repo.

**Signals (Compose/VM):** host Prometheus unit, existing `prometheus.yml` referencing FinHub.

If none → default recommendation **Option B** for lab only; **Option A** for production.

## Phase 1 — Choose path

| Path | When |
|------|------|
| **A — Reuse** | Customer owns Prom/AM/Graf |
| **B — Deploy** | Release `observability` profile; localhost dogfood |

Read [`docs/operations/monitoring.md`](../../docs/operations/monitoring.md) section for the chosen path.

## Phase 2A — Reuse existing stack

1. **Scrape** — Add jobs for platform ai-infra-rs `:26450` `/metrics`, optional postgres/redis exporters; merge [`deploy/monitoring/prometheus-scrape-snippet.yml`](../../deploy/monitoring/prometheus-scrape-snippet.yml).
2. **Observer** — Confirm `AI_INFRA_RS_OBSERVER_BACKEND` includes `prometheus` on claws (release default often `log,prometheus`).
3. **Rules** — Import [`deploy/monitoring/finops-alert-rules.yaml`](../../deploy/monitoring/finops-alert-rules.yaml) or release copy; reload Prometheus.
4. **Alertmanager** — Merge [`deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml`](../../deploy/monitoring/alertmanager-finops-staff-receiver-snippet.yml) when finops-staff enabled; `bearer_token_file` must match `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN`.
5. **Helm (K8s only)** — If using Prometheus Operator: `observability.alerts.prometheusRule.enabled`, optional `serviceMonitor.enabled`; **do not** expect FinHub chart to install Prometheus. Set `finopsStaff.prometheusUrl` to operator Prometheus URL.
6. **Grafana** — Optional import [`grafana-finops-compose-dogfood.json`](../../deploy/monitoring/grafana-finops-compose-dogfood.json).

Operator confirmation before applying configs to production servers.

## Phase 2B — Deploy observability profile

1. Operator sets `GRAFANA_DOGFOOD_ADMIN_PASSWORD` (and finops tokens if using staff).
2. Create dogfood secret file for Alertmanager bearer (release README under `deploy/compose/dogfood-secrets/`) — **operator pastes values locally**.
3. Compose up with `-f docker-compose.observability.yml --profile observability` per release README; add `finops-staff` + `finops-dogfood` profiles only if requested.
4. Review production gaps in monitoring doc — warn operator dogfood is not production-HA.

## Phase 3 — finops-staff (only if operator requested)

Follow [`docs/operations/finops-staff.md`](../../docs/operations/finops-staff.md) and [`finhub-deploy` § Optional finops-staff](../finhub-deploy/SKILL.md#optional-finops-staff).

1. Uncomment `FINOPS_STAFF_*` in `.env.example` §11 → `./scripts/gen-secrets.sh`.
2. Set `FINOPS_STAFF_PROMETHEUS_URL` to **customer** Prometheus (not dogfood hostname on prod).
3. Enable compose profile or `finopsStaff.enabled=true`.
4. Inject `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` on Kubernetes if Helm template omits it.

## Phase 4 — Verify

| Step | Pass criteria |
|------|---------------|
| Metrics | `curl -sf <claw-host>:26450/metrics` returns Prometheus text (when Observer includes prometheus) |
| Prometheus targets | Target for ai-infra-rs **up** |
| Rules | `chatkit.finops` rule groups present |
| Alertmanager | Config loads; receiver URL points to finops-staff |
| Webhook auth | Test delivery returns **not** `unconfigured` / `403` (use operator's token locally — do not echo token) |
| finops-staff | `GET /health` OK; policy readonly |
| Grafana (if B) | Login on `127.0.0.1:3030`, datasource OK |

Use [`docs/operations/monitoring.md`](../../docs/operations/monitoring.md#verification) tables for commands.

## Phase 5 — Report back

Template:

- Path chosen: A or B
- Prometheus URL (host only, no creds)
- finops-staff: enabled or skipped; policy mode
- Targets up / rules loaded: yes/no
- Alertmanager → staff: verified or blocked reason
- Gaps acknowledged (dogfood hardening, idle rules on compose, helm webhook token overlay)
- Unverified claims called out explicitly

## Troubleshooting

| Symptom | Check |
|---------|--------|
| Empty `/metrics` | `AI_INFRA_RS_OBSERVER_BACKEND` missing `prometheus` |
| Target down | DNS/service name; port `26450` not published on host |
| Rules pending | Missing kube/ingress/postgres series — expected on compose |
| Webhook 401/403 | Token mismatch; `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` unset on staff |
| Staff cannot query Prom | `FINOPS_STAFF_PROMETHEUS_URL` wrong network/DNS |
| Grafana won't start | `GRAFANA_DOGFOOD_ADMIN_PASSWORD` unset |

## Related

- [`docs/operations/monitoring.md`](../../docs/operations/monitoring.md)
- [`docs/operations/finops-staff.md`](../../docs/operations/finops-staff.md)
- [`skills/finhub-deploy/SKILL.md`](../finhub-deploy/SKILL.md)
