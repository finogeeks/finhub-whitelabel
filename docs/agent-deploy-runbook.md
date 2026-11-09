[English](./agent-deploy-runbook.md)

# Agent deploy runbook (human-readable)

Same flow as [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) and [`AGENTS.md`](../AGENTS.md), written for operators who brief a coding agent (Cursor, Claude Code, Codex, etc.).

## What you need before the agent starts

1. **This repo** — fork or clone; customize `branding/` and `persona-templates.json`.
2. **Offline release tarball** — URL or file from your vendor (images + compose + scripts). This public repo cannot start servers by itself.
3. **Deployment license** — key and cipher (or equivalent) from the vendor; the agent must not invent these.
4. **LLM API key** — whichever provider your release `.env.example` documents.
5. **Hostname and TLS** — e.g. `https://hub.example.com` for `APP_URL` and admin API calls.

Optional later: Identity OAuth, finops-staff, Turnstile, Slack webhooks — all **opt-in**.

## Recommended agent order

1. **Brand gate** — `skills/finhub-brand`: `./scripts/validate-artifacts.sh` (and optional login preview).
2. **Deploy** — `skills/finhub-deploy`: tarball → env → secrets → fleet up → white-label overlay → smoke.
3. **Checklist** — `docs/smoke-checklist.md`.

## Phase summary

### Prepare the fork (no Docker)

```bash
git clone https://github.com/finogeeks/finhub-whitelabel
cd finhub-whitelabel
./scripts/validate-artifacts.sh
```

Edit branding and persona files; re-run validate until it passes.

### Bootstrap the release (vendor tarball)

On the target host:

1. Download and verify the tarball (checksum/signature if the vendor provided files).
2. Unpack and read the **bundled README** and `.env.example`.
3. Run `scripts/init-env.sh` if included, else copy `.env.example` → `.env`.
4. Run `scripts/gen-secrets.sh` if included (fills random secrets, does not touch license fields or existing values). Otherwise generate non-license secrets with `openssl rand -hex 32` per empty slot in `.env.example`.
5. You paste **license** and **LLM** values into `.env`.
6. Run `scripts/preflight.sh` if present.
7. Load images and start with `scripts/fleet.sh` or `docker compose` per README.
8. Confirm health and a basic chat (login → message → streamed reply).

### Apply white-label overlay (this repo)

Set `WL_REPO` to your clone path, merge `deploy/compose/docker-compose.whitelabel.override.yml`, run persona sync (dry-run, then apply), PUT `branding/platform-settings.json` to the admin API. Details in the deploy skill and `deploy/compose/README.md`.

Helm deployments use `deploy/helm/values-whitelabel.yaml` plus ConfigMaps built from this repo.

### Optional: OAuth

Only if you asked for it. Set `OAUTH_PROVIDER_ENABLED=true` and related URLs; register OAuth clients using scripts in the **release** tree. See `deploy/oauth-provider.env.example`.

### Optional: finops-staff

Only if your **release** includes the service and you explicitly want it:

- Compose: `--profile finops-staff`
- Helm: `finopsStaff.enabled: true` (see commented stub in `deploy/helm/values-whitelabel.yaml`)

Start in **readonly**. **Supervised** mode and repair alerts only if you opt in. **Auto-act** stays off. Empty Slack webhook = no outbound Slack calls.

## Auto-generated vs human-provided

| Auto-generated (when `gen-secrets.sh` exists or `openssl` fallback) | Human / vendor only |
|-----------------------------------------------------------------------|---------------------|
| Session/JWT/database/redis passwords and similar slots in `.env.example` | `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER` (names per release) |
| Optional `FINOPS_STAFF_*_TOKEN` when finops-staff is enabled | LLM provider API keys |
| | Public hostname / TLS certificates |
| | OAuth client secrets (vault) |
| | Slack webhook URL (optional) |

## Teardown

From the release directory: `docker compose … down` (add `-v` only if you intend to wipe data). Uninstall Helm releases per vendor docs.

## Still depends on the release tarball

| In tarball | Not in finhub-whitelabel |
|------------|---------------------------|
| Container images | Runnable compose stack |
| `docker-compose.prod.yml` | `init-env.sh`, `fleet.sh` |
| `scripts/gen-secrets.sh` (newer releases) | Application source |
| `scripts/preflight.sh` | License material |
| Persona sync binary in image | finops-staff image (when not bundled) |

When your release adds or renames scripts, the bundled README wins for paths and flags; this repo documents the intended agent workflow across release versions.
