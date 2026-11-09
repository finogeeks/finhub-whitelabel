# Monitoring example configs

Non-secret snippets for **Option A** (reuse your Prometheus / Alertmanager / Grafana). The vendor **offline release** ships canonical paths under `deploy/compose/`, `deploy/observability/`, and optional compose profile `observability`.

| File | Purpose |
|------|---------|
| [`prometheus-scrape-snippet.yml`](./prometheus-scrape-snippet.yml) | Scrape jobs + rule file + Alertmanager target placeholders |
| [`alertmanager-finops-staff-receiver-snippet.yml`](./alertmanager-finops-staff-receiver-snippet.yml) | Webhook to finops-staff with `bearer_token_file` |
| [`finops-alert-rules.yaml`](./finops-alert-rules.yaml) | FinOps alert rule groups (runbook URLs omitted — see release bundle runbooks) |
| [`grafana-finops-compose-dogfood.json`](./grafana-finops-compose-dogfood.json) | Optional starter dashboard (dogfood-oriented series) |

Do not commit tokens, private hostnames, or license material.
