[English](./env-reference.md) | [简体中文](./env-reference.zh-CN.md) | [繁體中文](./env-reference.zh-TW.md)

# Environment reference

Your release ships `.env.example`. Copy to `.env` via `init-env.sh`. **Never commit real values** to git or paste them in tickets.

Legend: **Auto** = `gen-secrets.sh` or `init-env.sh` fills when placeholder/empty; **Human** = operator or supplier; **Secret** = treat as credential; **Optional** = preflight does not require.

## Bootstrap flow

| Step | Script | Effect |
|------|--------|--------|
| 1 | `init-env.sh` | `.env` file, JWT PEM files, A2A key if missing, URL fixes for fleet |
| 2 | `gen-secrets.sh` | Machine secrets in `.env` |
| 3 | Operator | License, LLM, registry, public URLs |
| 4 | `preflight-env.sh` | Fail on remaining placeholders / missing license |

## Auto-generated (`gen-secrets.sh`)

Replaced only when value is empty, known dev placeholder, or too short (per `env-secrets.ts`):

| Variable | Secret | Notes |
|----------|--------|-------|
| `VERIFY_CODE_SECRET` | Yes | min 32 bytes |
| `INTERNAL_SERVICE_TOKEN` | Yes | Shared with fleet internal API; finops-staff uses this for claw-fleet-manager |
| `OPEN_LOOP_WAKE_JWT_SECRET` | Yes | min 32 chars |
| `FINSAFE_AUTH_TOKEN` | Yes | |
| `USER_SECRETS_KEK` | Yes | base64 32-byte KEK |
| `OIDC_STATE_COOKIE_SECRET` | Yes | |
| `SESSION_COOKIE_SECRET` | Yes | |
| `INTERNAL_APPROVAL_RESOLVE_TOKEN` | Yes | When empty |
| `AI_INFRA_RS_CRON_INTERNAL_TOKEN` | Yes | Mirrors `INTERNAL_SERVICE_TOKEN` when empty |
| `SERVICE_API_KEYS` | Yes | Regenerates dev-style placeholder map |
| `A2A_DELEGATION_SIGNING_KEY` | Yes | Also ensured in `init-env.sh` / `fleet.sh` (≥32 bytes; existing kept) |
| `FINOPS_STAFF_GENERIC_WEBHOOK_HMAC_SECRET` | Yes | Only if key present and empty in `.env` |

**Optional finops tokens** (generated only when the key is **present** in `.env`, including commented stubs with `KEY=`):

| Variable | Secret |
|----------|--------|
| `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` | Yes |
| `FINOPS_STAFF_INTERNAL_API_TOKEN` | Yes |
| `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` | Yes |

Stdout after gen-secrets may list `Optional finops filled: …` (**names only**).

## Auto-generated (`init-env.sh`, not gen-secrets)

| Item | Secret | Notes |
|------|--------|-------|
| `JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`, `IDP_PUBLIC_KEY` | Yes | PEM content inlined in `.env` from `identity-service/keys/` |
| Hermes defaults | No | e.g. `FINSAFE_SKIP_LOCAL_SERVER=0`, `HERMES_EXECUTION_POSTURE=confined` when missing |

## Human-required

| Variable | Secret | Notes |
|----------|--------|-------|
| `DEPLOYMENT_LICENSE_KEY` | Yes | **Supplier only** — never generated |
| `DEPLOYMENT_LICENSE_CIPHER` | Yes | **Supplier only** — never generated |

Missing or invalid license → identity-service refuses to start.

## Human-typical (production)

| Variable | Secret | Preflight |
|----------|--------|-----------|
| `LLM_API_KEY` | Yes | Optional empty (set for real inference) |
| `CHATKIT_REGISTRY`, `CHATKIT_VERSION` | No | Image pull tags |
| `APP_URL`, cookie domains | No | Public browser URL |
| `ADMIN_EMAILS` | No | Bootstrap admins |

## Optional human (integrations)

| Variable | Secret | When |
|----------|--------|------|
| `TURNSTILE_SECRET`, `TURNSTILE_HOSTNAMES`, `TURNSTILE_SITEKEY` | Yes (secret) | Internet-facing registration |
| `FINOPS_STAFF_SLACK_WEBHOOK_URL` | Yes | Slack notifications |
| `FINOPS_STAFF_NOTIFY_MIN_SEVERITY` | No | Notify floor: `info`, `warning`, or `critical` (default `warning`; invalid or empty → `warning`) — see [finops-notifications](./finops-notifications.md) |
| Channel URLs/passwords | Yes | See [finops-notifications](./finops-notifications.md) — **not** minted by gen-secrets except optional HMAC secret above |

## finops-staff documented defaults (customer posture)

Keep these in `.env` when enabling finops-staff:

```bash
FINOPS_STAFF_POLICY_MODE=readonly
FINOPS_STAFF_AUTO_ACT_DISABLED=true
FINOPS_STAFF_CLOSED_LOOP_ENABLED=false
```

Compose overlay (`${FINOPS_STAFF_AUTO_ACT_DISABLED:-true}` / `${FINOPS_STAFF_CLOSED_LOOP_ENABLED:-false}`) and Helm (`finopsStaff.autoActDisabled: true`, `finopsStaff.closedLoopEnabled: false`, always rendered into the pod unless overridden) match the table above. Verified at release semantics `eaf6b93b`.

## JWT and license

- **JWT keys** — Files on disk + `.env`; rotate via re-run init/fleet key sync procedures in release docs.
- **License** — Contact vendor for renewal; this package does not ship a license generator.

Full stub list: `.env.example` section 11 (finops) in your release tree.
