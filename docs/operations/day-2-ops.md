[English](./day-2-ops.md) | [简体中文](./day-2-ops.zh-CN.md) | [繁體中文](./day-2-ops.zh-TW.md)

# Day-2 operations

Maintenance tasks after first successful `fleet.sh up`. Commands live in your **release tree**; names below match current FinHub offline releases.

## Upgrade

1. Obtain a new offline tarball from your vendor; read release notes.
2. **Backup** (below) before changing running state.
3. Stop fleet: `./scripts/fleet.sh down` (use `--keep-tenant-claws` only when release docs recommend it).
4. Replace images: `load-images.sh` or registry pull per README.
5. Merge any new `.env.example` keys — run `./scripts/init-env.sh` (no-op copy when `.env` exists) and `./scripts/gen-secrets.sh` for new placeholders only.
6. `./scripts/preflight-env.sh` then `./scripts/fleet.sh up -d`.
7. `./scripts/doctor.sh` and [`smoke-checklist.md`](../smoke-checklist.md).

Re-apply white-label compose override from [`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md) if compose files changed.

**Helm:** `helm upgrade` with updated chart and values; roll finops-staff only when `finopsStaff.enabled=true`.

## Backup and restore

| Asset | Guidance |
|-------|----------|
| `.env` | Encrypted backup off-host; includes JWT inline keys — **secret** |
| `services/platform/identity-service/keys/` | PEM files; backup with `.env` |
| Postgres / conversation data | Use volume snapshots or vendor runbook for DB container/volume names in your release |
| Persona/branding | Source of truth in your `finhub-whitelabel` fork (git) |
| Tenant claw workspaces | Named volume from `CLAW_FLEET_DOCKER_WORKSPACES_VOLUME` (default `chatkit_workspaces` in compose docs) |

Restore: stop fleet → restore volumes/DB → restore `.env` and keys → `preflight` → `fleet up` → doctor.

## Logs

```bash
./scripts/fleet.sh logs -f              # aggregate
./scripts/fleet.sh ps
./scripts/doctor.sh --logs
```

Optional `LOG_FILES=./fleet.log ./scripts/fleet.sh up -d` on Linux when piping output.

Platform observability (Prometheus, Alertmanager) is optional and release-specific; wire finops webhooks only when [finops-staff](./finops-staff.md) is enabled.

## Secret rotation

| Secret | Approach |
|--------|----------|
| Machine secrets (`INTERNAL_SERVICE_TOKEN`, cookie secrets, etc.) | Set new value in `.env`, run targeted service restart per release README; prefer vendor rotation runbook for ordering (identity → fleet → claws) |
| `USER_SECRETS_KEK` | Use `USER_SECRETS_KEK_PREVIOUS` + version fields when release supports re-encryption |
| JWT PEM | Regenerate via init-env procedures; forces re-login |
| finops webhook tokens | Rotate in `.env`, `gen-secrets.sh` only if placeholder; restart finops-staff |
| Deployment license | Vendor-issued renewal — edit `DEPLOYMENT_LICENSE_*` only |

`gen-secrets.sh` **does not overwrite** non-placeholder operator values.

## finops-staff lifecycle

- Enable/disable profile without touching chat: compose `down` on finops overlay only.
- Keep `FINOPS_STAFF_AUTO_ACT_DISABLED=true` and `FINOPS_STAFF_CLOSED_LOOP_ENABLED=false` after upgrades unless SecAI directs otherwise (not offered in customer docs).

## Teardown

```bash
./scripts/fleet.sh down
# Optional: remove volumes when release docs confirm data destruction steps
docker volume ls | grep chatkit   # inspect before prune
```

Document license return/decommission per your vendor contract.

## Troubleshooting

| Symptom | Checks |
|---------|--------|
| identity-service exit / unhealthy | `DEPLOYMENT_LICENSE_KEY` / `DEPLOYMENT_LICENSE_CIPHER` set; preflight passed |
| preflight failures | Run `./scripts/preflight-env.sh` — output lists **names** only |
| Placeholder secrets | Re-run `gen-secrets.sh` |
| Claws stuck `starting` | `doctor.sh`; tune `CLAW_FLEET_MANAGER_*` timeouts in `.env` per release |
| LLM errors | `LLM_API_KEY`, `LLM_BASE_URL`, model name |
| finops webhook 401 | `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` matches Alertmanager bearer |
| Notification missing | Channel listed in `FINOPS_STAFF_NOTIFY_CHANNELS` but URL empty → startup warning |
| Bypassed preflight in prod | Remove `FLEET_SKIP_PREFLIGHT`; run real license + preflight |

Internal JSON health for finops: `GET http://<host>:26116/internal/doctor` when the service is enabled.

## Related

- [Install](./install.md) · [Environment reference](./env-reference.md) · [Agent deploy runbook](../agent-deploy-runbook.md)
