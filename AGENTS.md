# Coding agents: FinHub zero-to-running guide

This public repository is a **white-label overlay** for FinHub. It does **not** ship application images, the full compose stack, or license material. A vendor **offline release tarball** is required before any server can start.

## Read first

| Order | Skill / doc | Purpose |
|-------|-------------|---------|
| 1 | [`skills/finhub-brand/SKILL.md`](skills/finhub-brand/SKILL.md) | Validate branding and persona artifacts **before** deploy (`./scripts/validate-artifacts.sh`, optional login preview). |
| 2 | [`skills/finhub-deploy/SKILL.md`](skills/finhub-deploy/SKILL.md) | End-to-end runbook: obtain release → env/secrets → start stack → white-label overlays → smoke → optional OAuth / finops-staff. |
| 3 | [`docs/smoke-checklist.md`](docs/smoke-checklist.md) | Post-deploy verification checklist. |

Human-readable summary of the same flow: [`docs/agent-deploy-runbook.md`](docs/agent-deploy-runbook.md).

## What you need from the human operator

- Offline release tarball **URL or file path** (and checksum/signature files when the vendor provides them).
- **Deployment license** values from the vendor (`DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER` or names documented in the release `.env.example`). **Never invent license keys.**
- **`LLM_API_KEY`** (or the name documented in the release `.env.example` for your LLM provider).
- Target **public hostname** and TLS plan (or explicit HTTP-only lab mode if the release allows it).
- Admin credentials for platform-settings seeding after the stack is up.

## What the release tarball provides (not in this repo)

Typical **release bundles** include images (or load instructions), `docker-compose.prod.yml`, and scripts such as `init-env.sh`, `gen-secrets.sh`, `preflight-env.sh`, `fleet.sh`, and `doctor.sh`. Canonical order when all are present:

1. `scripts/init-env.sh`
2. `scripts/gen-secrets.sh`
3. Operator sets `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER`, and `LLM_API_KEY` in `.env`
4. `scripts/preflight-env.sh`
5. `scripts/fleet.sh up -d` (also runs preflight automatically)
6. `scripts/doctor.sh`

Exact names and layout are defined in the **bundled README** inside the tarball—follow that README when it disagrees with this repo for core stack bring-up.

## Hard rules for agents

- **No secrets in git or chat logs** — use host `.env` files or a vault; redact when reporting.
- **OAuth** (`OAUTH_PROVIDER_ENABLED`) stays **false** unless the operator explicitly requests Identity OAuth.
- **finops-staff** is **opt-in**; default deploy runs without it. When enabled, start in **readonly**; **supervised** mode and `FINOPS_STAFF_ALERT_PENDING_REPAIR` only if the operator explicitly chooses; **auto-act stays disabled**.
- **Turnstile, Slack, and other outbound integrations** are opt-in; empty webhook URLs mean **no outbound calls**.
- Phase 1 (release-only stack) must remain a valid path; white-label overlays are Phase 2.

## Repository layout (agent-relevant)

```
skills/finhub-brand/SKILL.md    # Pre-deploy validation + preview
skills/finhub-deploy/SKILL.md   # Primary deploy runbook
branding/                       # Product chrome seed + assets
persona-templates.json          # Starter persona pack (pin + replace sync)
deploy/compose/                 # Compose override mounts
deploy/helm/                    # Helm values + ConfigMap stubs
deploy/oauth-provider.env.example
docs/smoke-checklist.md
docs/agent-deploy-runbook.md
scripts/validate-artifacts.sh
```

## Success criteria

1. Release stack healthy on the target host.
2. White-label login shows fork branding and pruned persona pack.
3. Smoke: sign-in, send a chat message, receive a **streamed** reply.
4. `./scripts/validate-artifacts.sh` passes on the fork (run on the repo before or after overlay apply).

Report blockers with service names from the release compose, not invented ports or image tags.
