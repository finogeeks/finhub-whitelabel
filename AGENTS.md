# AI agent guide (FinHub white-label + runtime)

This repository is the **customer-facing** documentation and artifact template for FinHub. Coding agents should follow the skills and runbooks here end to end. The offline **release tarball** (shipped by your vendor) contains application images, compose/Helm charts, and `scripts/` for environment bootstrap — not this repo.

## Language

- Operator docs exist in **English**, **Simplified Chinese** (`*.zh-CN.md`), and **Traditional Chinese** (`*.zh-TW.md`).
- Keep **env var names**, **commands**, and **code** identical across languages.

## Read order

| Step | Skill / doc | Purpose |
|------|-------------|---------|
| 1 | [`skills/finhub-deploy/SKILL.md`](./skills/finhub-deploy/SKILL.md) | White-label overlays (branding, persona pack, optional OAuth) |
| 1b | [`docs/admin-and-whitelabel.md`](./docs/admin-and-whitelabel.md) | Admin logo/copy and preset-skill sync vs this repo's seeds |
| 2 | [`docs/agent-deploy-runbook.md`](./docs/agent-deploy-runbook.md) | Full path: release unpack → env bootstrap → fleet → doctor → smoke |
| 3 | [`docs/operations/install.md`](./docs/operations/install.md) | First-time install and first `fleet.sh up` |
| 4 | [`docs/operations/env-reference.md`](./docs/operations/env-reference.md) | Auto-generated vs human-supplied `.env` keys |
| 5 | [`docs/operations/monitoring.md`](./docs/operations/monitoring.md) | Optional Prometheus / Alertmanager / Grafana (reuse or deploy) |
| 6 | [`skills/finhub-monitoring/SKILL.md`](./skills/finhub-monitoring/SKILL.md) | Agent workflow: scrape, rules, Alertmanager → finops-staff |
| 7 | [`docs/operations/finops-staff.md`](./docs/operations/finops-staff.md) | Optional supervised self-heal (off by default) |
| 8 | [`docs/operations/finops-notifications.md`](./docs/operations/finops-notifications.md) | Alert notification channels |
| 9 | [`docs/operations/day-2-ops.md`](./docs/operations/day-2-ops.md) | Upgrade, backup, logs, rotation, teardown |
| 10 | [`docs/smoke-checklist.md`](./docs/smoke-checklist.md) | Post-deploy verification |

Optional branding validation: [`skills/finhub-brand/SKILL.md`](./skills/finhub-brand/SKILL.md).

## Hard rules (public repo)

- **Never** commit or echo real secrets, license material, private hostnames, or internal repository URLs.
- **Never** invent `DEPLOYMENT_LICENSE_KEY` / `DEPLOYMENT_LICENSE_CIPHER` — supplier only.
- On-prem default: **zero external dependencies** (no Slack, no Turnstile) unless the operator opts in.
- `finops-staff` is optional; stopping it does **not** stop chat. Compose and Helm both default **auto-act off** and **closed-loop off** (`FINOPS_STAFF_AUTO_ACT_DISABLED=true`, `FINOPS_STAFF_CLOSED_LOOP_ENABLED=false`) unless overridden; do not enable unattended auto-act or closed-loop for customers.
- Bootstrap/finops env semantics in this repo were verified at offline-release git `cb3e6418` (no private repo links in customer docs).
- If release README conflicts with this repo for **unpack/start** commands, follow the **release README** and report the conflict.

## Report back

After a deploy assist, report: release version/sha, workdir, whether `init-env` → `gen-secrets` → `preflight` → `fleet up` → `doctor` ran, white-label overlay paths, finops profile (if any), monitoring path A/B (if any), and smoke checklist results — **names only** for secrets and license fields.
