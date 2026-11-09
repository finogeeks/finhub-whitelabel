[English](./finops-staff.md) | [简体中文](./finops-staff.zh-CN.md) | [繁體中文](./finops-staff.zh-TW.md)

# finops-staff (optional supervised self-heal)

**finops-staff** is an optional platform service for alert ingress, bounded diagnosis, and **human-approved** repairs. It is **off the user chat path** — stopping or disabling it never stops FinHub conversation services.

Default customer posture: **disabled** (no compose profile / `finopsStaff.enabled=false`).

## Enable

**Docker Compose**

```bash
# Uncomment finops stubs in .env.example, set policy defaults, run gen-secrets again for tokens
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff up -d
```

**Helm**

```bash
helm upgrade --install <release> <chart-path> \
  --set finopsStaff.enabled=true \
  --set finopsStaff.policyMode=readonly
```

Compose (`docker-compose.finops-staff.yml`) and Helm (`finopsStaff` chart values + rendered env) both default **auto-act off** and **closed-loop off**: `FINOPS_STAFF_AUTO_ACT_DISABLED=true`, `FINOPS_STAFF_CLOSED_LOOP_ENABLED=false` unless the operator overrides them. Release behavior verified at `eaf6b93b`.

| Item | Value |
|------|--------|
| Default port | `26116` |
| Health | `GET /health` (open) |
| Alert ingress | `POST /webhooks/alertmanager` |
| Diagnose / act | `POST /internal/*` |
| Approval | `POST /webhooks/approval` |
| Audit | `GET /internal/audit` |
| Doctor JSON | `GET /internal/doctor` |

`INTERNAL_SERVICE_TOKEN` in `.env` authenticates finops-staff to claw-fleet-manager (see release `docker-compose.finops-staff.yml`).

## Doctor snapshot (`GET /internal/doctor`)

Read-only JSON (`finops-doctor/v1`) for posture checks after upgrades — not a substitute for release `scripts/doctor.sh`.

| Field | Customer default | Meaning |
|-------|------------------|---------|
| `auto_act_disabled` | `true` | Automatic remediation acts stay off |
| `closed_loop_enabled` | `false` | Closed-loop controller stays off |

The snapshot also reports `notify_channels_configured`, `notify_channels_listed`, and `notify_startup_warnings`. Use it to confirm kill switches and notification wiring without enabling auto-act.

## Policy modes

| Mode | Diagnose | Remediate |
|------|----------|-----------|
| `readonly` (default) | Yes | Denied |
| `supervised` | Yes | Allowlisted acts; **approval required** |
| `full` | Yes | Broader allowlist; production replica writes gated separately |

Promote to `supervised` only on stacks where SecAI/your security team has signed off. Customer docs do **not** cover enabling unattended auto-act or closed-loop controllers.

## Documented kill switches (keep at defaults)

```bash
FINOPS_STAFF_AUTO_ACT_DISABLED=true
FINOPS_STAFF_CLOSED_LOOP_ENABLED=false
```

Do not enable automatic fleet PATCH or closed-loop ticks for production customers.

## Alert → diagnose → pending repair → approve

1. **Alertmanager** posts to `http://<finops-staff>:26116/webhooks/alertmanager` with optional `Authorization: Bearer <FINOPS_STAFF_ALERT_WEBHOOK_TOKEN>` or header `x-finops-alert-token`.

2. **Ingress modes** (set at most one for production alert flow unless using vendor drill packs):
   - `FINOPS_STAFF_ALERT_DIAGNOSE_ONLY=true` — notification + diagnose only
   - `FINOPS_STAFF_ALERT_PENDING_REPAIR=true` — requires `FINOPS_STAFF_POLICY_MODE=supervised`; creates **pending** allowlisted acts from firing alerts with `act`, `tenant_id`, `deployment_id` labels (never auto-executes)

3. **Human approval** — `POST /webhooks/approval` with JSON body `decision_id`, `approved`, `actor`, and header `x-finops-approval-token` when `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` is set:

```bash
curl -sS -X POST "https://<finops-host>:26116/webhooks/approval" \
  -H 'Content-Type: application/json' \
  -H 'x-finops-approval-token: <FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN>' \
  -d '{"decision_id":"<id>","approved":true,"actor":"oncall"}'
```

4. **Execute** — Re-post `POST /internal/act` with the same `decision_id` after approval.

5. **Cooldown** — `FINOPS_STAFF_RESTART_COOLDOWN_MS` (default `300000`) between restart acts per deployment.

6. **Audit** — Acts record `tenant_id`, `actor`, `decision_id`, `policy_mode`, fleet path; query via `GET /internal/audit`.

## Allowlisted acts (supervised / full)

| Act | Notes |
|-----|-------|
| `log_rotate` | Policy ack only; no host exec |
| `fleet_restart` | Via claw-fleet-manager |
| `fleet_set_desired_replicas` | Non-prod by default; production needs explicit SecAI flags in release |

**Never finops-staff:** PVC delete, DB failover, scale-to-zero, `kubectl exec`, bulk `reconcile-all`, identity admin bypass.

## Tokens (recommended when webhooks are exposed)

After uncommenting stub lines in `.env`, run `./scripts/gen-secrets.sh`:

| Variable | Purpose |
|----------|---------|
| `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` | Alertmanager webhook |
| `FINOPS_STAFF_INTERNAL_API_TOKEN` | `POST /internal/*` (health stays open) |
| `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` | Optional approval webhook gate |

## Prometheus

Set `FINOPS_STAFF_PROMETHEUS_URL` to your in-cluster Prometheus. The compose default `http://chatkit-prometheus-dogfood:9090` is for vendor dogfood only — override for customer stacks.

## Notifications

Optional outbound alerts: [finops-notifications](./finops-notifications.md). Failures are isolated (diagnose still returns 200 when successful).

## Teardown

```bash
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff down
```

Chat and core platform keep running.

## Related

- [Install](./install.md) · [Environment reference](./env-reference.md) · [Day-2 ops](./day-2-ops.md)
