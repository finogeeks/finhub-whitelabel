[English](./install.md) | [简体中文](./install.zh-CN.md) | [繁體中文](./install.zh-TW.md)

# Install and first start

This describes the **default on-prem path** using scripts shipped in your FinHub offline release. Script names and order are fixed; compose file names may differ slightly — follow the release README if it names another compose file.

## Prerequisites

- Docker + Compose v2, `openssl`, `bun`
- Supplier-issued deployment license (`DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER`)
- LLM endpoint and `LLM_API_KEY` for production (dev mock LLM is not sufficient for real users)

## Bootstrap sequence

```bash
cd <release-root>   # directory containing .env.example and scripts/

./scripts/init-env.sh
./scripts/gen-secrets.sh
```

1. **`init-env.sh`** — Creates `.env` from `.env.example` if missing; ensures Hermes/FinSAFE fleet defaults; generates **JWT key PEMs** under `services/platform/identity-service/keys/` and writes `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY` / `IDP_PUBLIC_KEY` into `.env`; ensures A2A delegation key when missing; warns if license lines are empty.

2. **`gen-secrets.sh`** — Idempotent machine secrets via `env-secrets-cli.ts`; **never prints values**; sets `.env` mode `600`. Requires `bun`.

**Operator edits `.env`** (human-supplied):

- `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER`
- `LLM_API_KEY` (and model/provider if not defaults)
- `CHATKIT_REGISTRY` / `CHATKIT_VERSION` when not using local images
- `APP_URL` and related URLs for your public hostname

```bash
./scripts/preflight-env.sh
```

Lists **variable names only** if placeholders remain or license is missing.

Offline bundles:

```bash
./scripts/load-images.sh
```

Start the fleet:

```bash
./scripts/fleet.sh up -d
```

`fleet.sh` runs the same preflight unless bypassed (see below), starts compose, waits for identity/fleet-manager, reconciles tenant claws per release behavior.

```bash
./scripts/doctor.sh
./scripts/doctor.sh --logs    # optional recent logs
```

## On-prem: no external dependencies by default

- **Turnstile** — Optional. Unset `TURNSTILE_SECRET`, `TURNSTILE_HOSTNAMES`, and `TURNSTILE_SITEKEY` for air-gapped signup (no siteverify, no widget).
- **finops-staff notifications** — Off until you configure webhooks/SMTP ([finops-notifications](./finops-notifications.md)).
- **Slack / Feishu / etc.** — Never required for core chat.

## `FLEET_SKIP_PREFLIGHT` (non-production only)

```bash
FLEET_SKIP_PREFLIGHT=1 ./scripts/fleet.sh up -d
```

Prints:

```text
⚠️  FLEET_SKIP_PREFLIGHT=... — skipping scripts/preflight-env.sh
    (dev/drill/dogfood only; production must run preflight + real license)
```

Use only for engineering checkouts, drill bundles, or dogfood when the operator accepts placeholder/license risk. **Do not use for customer production.**

## After the stack is up

- White-label overlays: [`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md)
- Smoke: [`docs/smoke-checklist.md`](../smoke-checklist.md)
- Optional FinOps: [finops-staff](./finops-staff.md)
- Optional email (Reloop): [email channel](./email-channel.md)

## Smoke (API)

When `scripts/test-e2e-api.sh` exists in the release tree, run it; otherwise exercise login and chat via your gateway URL (commonly port `26100` in compose docs).
