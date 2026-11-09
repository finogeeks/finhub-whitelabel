[English](./agent-deploy-runbook.md)

# Agent deploy runbook (human-readable)

Same flow as [`skills/finhub-deploy/SKILL.md`](../skills/finhub-deploy/SKILL.md) and [`AGENTS.md`](../AGENTS.md), written for operators who brief a coding agent (Cursor, Claude Code, Codex, etc.).

## What you need before the agent starts

1. **This repo** — fork or clone; customize `branding/` and `persona-templates.json`.
2. **Offline release tarball** — URL or file from your vendor (images + compose + scripts). This public repo cannot start servers by itself.
3. **Deployment license** — key and cipher from the vendor; the agent must not invent these.
4. **`LLM_API_KEY`** — per the release `.env.example`.
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

### Bootstrap the release bundle

On the target host:

1. Download and verify the tarball (checksum/signature if the vendor provided files).
2. Unpack and read the **bundled README** and `.env.example`.
3. `./scripts/init-env.sh` — or copy `.env.example` → `.env` on older bundles.
4. `./scripts/gen-secrets.sh` — random secrets only; never license or `LLM_API_KEY`. **Fallback:** `openssl rand -hex 32` per empty non-license slot when the script is absent.
5. You set **`DEPLOYMENT_LICENSE_KEY`**, **`DEPLOYMENT_LICENSE_CIPHER`**, and **`LLM_API_KEY`** in `.env`.
6. `./scripts/preflight-env.sh` — **Fallback:** manual checklist (Docker, `.env`, license, LLM key, disk).
7. `./scripts/fleet.sh up -d` — runs preflight again automatically. **Fallback:** `docker compose` per README.
8. `./scripts/doctor.sh` — post-start diagnostics when bundled.
9. Smoke: login → message → **streamed** reply.

### Apply white-label overlay (this repo)

Set `WL_REPO` to your clone path, merge `deploy/compose/docker-compose.whitelabel.override.yml`, run persona sync (dry-run, then apply), PUT `branding/platform-settings.json` to the admin API. Details in the deploy skill and `deploy/compose/README.md`.

Helm deployments use `deploy/helm/values-whitelabel.yaml` plus ConfigMaps built from this repo.

### Optional: OAuth

Only if you asked for it. Set `OAUTH_PROVIDER_ENABLED=true` and related URLs; register OAuth clients using scripts in the **release bundle**. See `deploy/oauth-provider.env.example`.

### Optional: finops-staff

Only if the **release bundle** includes the service and you explicitly want it:

- Uncomment `FINOPS_STAFF_*` in `.env.example` **§11**, re-run `gen-secrets.sh`, then enable compose `--profile finops-staff` or Helm `finopsStaff.enabled: true` (see `deploy/helm/values-whitelabel.yaml`).

Start in **readonly**. **Supervised** mode and repair alerts only if you opt in. **Auto-act** stays off. Empty Slack webhook = no outbound Slack calls.

## Auto-generated vs human-provided

| Auto-generated (when `gen-secrets.sh` exists or `openssl` fallback) | Human / vendor only |
|-----------------------------------------------------------------------|---------------------|
| Session/JWT/database/redis passwords and similar slots in `.env.example` | `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER` |
| `FINOPS_STAFF_*_TOKEN` only after **§11** stubs are uncommented and `gen-secrets.sh` is re-run | `LLM_API_KEY` |
| | Public hostname / TLS certificates |
| | OAuth client secrets (vault) |
| | Slack webhook URL (optional) |

## Teardown

From the release directory: `docker compose … down` (add `-v` only if you intend to wipe data). Uninstall Helm releases per vendor docs.

## Still depends on the release bundle

| In the release bundle | Not in finhub-whitelabel |
|-----------------------|---------------------------|
| Container images | Runnable compose stack |
| `docker-compose.prod.yml` | Application source |
| `init-env.sh`, `gen-secrets.sh`, `preflight-env.sh`, `fleet.sh`, `doctor.sh` | License material |
| Persona sync binary in image | finops-staff image (when not bundled) |

When a bundle adds or renames scripts, the bundled README wins for paths and flags; this repo documents the intended agent workflow across release versions.
