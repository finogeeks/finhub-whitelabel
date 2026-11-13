[English](./agent-deploy-runbook.md) | [简体中文](./agent-deploy-runbook.zh-CN.md) | [繁體中文](./agent-deploy-runbook.zh-TW.md)

# Agent deploy runbook

End-to-end path for operators and coding agents: bring up a **licensed** FinHub stack from an offline release, then apply this white-label repo.

## Preconditions

| Item | Notes |
|------|--------|
| Host | Docker Engine + Compose v2 (or Kubernetes + Helm per release) |
| Tooling on host | `openssl`, `bun` (bundled in some offline packages) |
| Supplier license | `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER` (paste into `.env` — never mint) |
| LLM | `LLM_API_KEY` and provider settings for production inference |
| White-label fork | Clone [`finogeeks/finhub-whitelabel`](https://github.com/finogeeks/finhub-whitelabel); run `./scripts/validate-artifacts.sh` |

On-prem: leave **Turnstile** (`TURNSTILE_*`) unset unless internet-facing signup needs Cloudflare Turnstile. See [Environment reference](./operations/env-reference.md).

Optional later: Identity OAuth, finops-staff, **Reloop email channel**, monitoring (Prometheus stack or reuse), Turnstile, Slack webhooks — all **opt-in**. Monitoring wiring: [`docs/operations/monitoring.md`](./operations/monitoring.md), [`skills/finhub-monitoring/SKILL.md`](../skills/finhub-monitoring/SKILL.md). Email: [`docs/operations/email-channel.md`](./operations/email-channel.md).

## Phase A — Release runtime (in tarball tree)

Run from the release root (often `deploy/` or the directory that contains `docker-compose.prod.yml` and `scripts/`).

```bash
./scripts/init-env.sh
./scripts/gen-secrets.sh
# Edit .env: DEPLOYMENT_LICENSE_KEY, DEPLOYMENT_LICENSE_CIPHER, LLM_API_KEY, CHATKIT_REGISTRY / version as needed
./scripts/preflight-env.sh
# Offline bundle only:
./scripts/load-images.sh
./scripts/fleet.sh up -d
./scripts/doctor.sh
```

Details: [Install / first start](./operations/install.md).

**Dev/drill only** (not production): `FLEET_SKIP_PREFLIGHT=1 ./scripts/fleet.sh up -d` prints a warning and skips `preflight-env.sh`.

## Phase B — White-label (this repo)

Load [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) Phase 2:

- Merge `deploy/compose/docker-compose.whitelabel.override.yml`
- Pin persona pack; optional platform-settings PUT
- Helm: `deploy/helm/values-whitelabel.yaml` when on Kubernetes

## Phase C — Optional finops-staff

Supervised diagnostics and **human-approved** repairs only. Disabled by default.

```bash
docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff up -d
```

Helm: `finopsStaff.enabled=true` with `finopsStaff.policyMode=readonly` until SecAI approves `supervised`. See [finops-staff](./operations/finops-staff.md).

## Phase C.5 — Email channel (opt-in)

Optional Reloop agent mail; **disabled** by default. Self-host Reloop; register webhook in Reloop’s UI. **Compose:** `email` profile + peer URLs in `.env`, restart identity-service and delivery (gateway 502 on email paths until connector runs). **Helm:** `--set services.email-connector.enabled=true` only — chart wires peers and nginx (routes omitted when off). See [email channel](./operations/email-channel.md).

## Phase D — Smoke

[`docs/smoke-checklist.md`](./smoke-checklist.md) after Phase A and B.

## Agent checklist (copy)

- [ ] Release tarball verified (HTTP 200, expected sha in filename)
- [ ] `init-env.sh` → `gen-secrets.sh` (idempotent; chmod 600 `.env`)
- [ ] License + LLM keys set by operator (not generated)
- [ ] `preflight-env.sh` passed (or documented `FLEET_SKIP_PREFLIGHT` for non-prod only)
- [ ] `fleet.sh up -d` healthy; `doctor.sh` clean
- [ ] White-label override applied; persona sync dry-run then apply
- [ ] Smoke checklist complete
- [ ] No secrets in git, chat, or logs

## Related

- [`AGENTS.md`](../AGENTS.md) — agent entry index
- [`docs/operations/day-2-ops.md`](./operations/day-2-ops.md) — upgrades and maintenance
