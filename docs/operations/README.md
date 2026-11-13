# Operations guides

English-first runbooks for install, optional monitoring, finops-staff, and day-2 tasks. Your **offline release tarball** remains the source of truth for compose service names, ports, and bundled files.

| Guide | Purpose |
|-------|---------|
| [Install](./install.md) | `init-env.sh` → `gen-secrets.sh` → `fleet.sh up` → `doctor.sh` |
| [Environment reference](./env-reference.md) | Auto-generated vs operator-supplied `.env` keys |
| [Monitoring](./monitoring.md) | Optional Prometheus / Alertmanager / Grafana; reuse (A) or deploy (B) |
| [FinOps staff](./finops-staff.md) | Optional supervised self-heal (off by default) |
| [FinOps notifications](./finops-notifications.md) | Outbound alert channels |
| [Day-2 ops](./day-2-ops.md) | Upgrade, backup, logs, teardown |
| [Email channel](./email-channel.md) | Optional Reloop email-connector (off by default) |

Each guide has [简体中文](./install.zh-CN.md) / [繁體中文](./install.zh-TW.md) siblings (language bar at top of each English page).

Agent skills: [`skills/finhub-monitoring/SKILL.md`](../../skills/finhub-monitoring/SKILL.md), [`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md).

Example monitoring configs (no secrets): [`deploy/monitoring/`](../../deploy/monitoring/).
