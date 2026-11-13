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

## Optional email channel (Reloop)

Off by default (Compose `email` profile on `docker-compose.prod.yml`; Helm `services.email-connector.enabled: false`). Full deploy: [email channel](./email-channel.md).

**email-connector** container:

| Variable | Secret | Required |
|----------|--------|----------|
| `DATABASE_URL` | Yes | Yes (`?schema=email`) |
| `PORT` | No | Default `26464` |
| `ORCHESTRATOR_URL` | No | Yes |
| `IDENTITY_SERVICE_URL` | No | Yes |
| `INTERNAL_SERVICE_TOKEN` | Yes | Yes (auto-generated above) |
| `EMAIL_CONNECTOR_TENANT_ID` | No | Optional |

Dev-only on connector (production uses Admin): `RELOOP_*`, `EMAIL_CONNECTOR_AGENT_MAILBOX_DOMAIN`, `EMAIL_CONNECTOR_*` aliases.

**Peers** (orchestrator does **not** take `EMAIL_CONNECTOR_URL`):

| Service | Variable | Compose | Helm |
|---------|----------|---------|------|
| identity-service | `EMAIL_CONNECTOR_URL` | Operator sets `http://chatkit-email-connector:26464` in `.env`; restart service | Chart injects `http://email-connector:26464` when `services.email-connector.enabled: true`; omitted when false |
| delivery | `EMAIL_CONNECTOR_URL`, optional `CONFIG_EMAIL_CONNECTOR_URL` | Operator sets in `.env`; restart service | Chart injects both URLs when connector enabled; omitted when false |

Do **not** set peer `EMAIL_CONNECTOR_*` in Helm `servicesEnv` — the chart owns those when the connector is enabled.

**Admin** → Channels → Email: `reloop_api_key`, `webhook_secret`, `domain_id`, `agent_mailbox_domain`, `api_base_url` (masked on GET/PUT).

## finops-staff documented defaults (customer posture)

Keep these in `.env` when enabling finops-staff:

```bash
FINOPS_STAFF_POLICY_MODE=readonly
FINOPS_STAFF_AUTO_ACT_DISABLED=true
FINOPS_STAFF_CLOSED_LOOP_ENABLED=false
```

Compose overlay (`${FINOPS_STAFF_AUTO_ACT_DISABLED:-true}` / `${FINOPS_STAFF_CLOSED_LOOP_ENABLED:-false}`) and Helm (`finopsStaff.autoActDisabled: true`, `finopsStaff.closedLoopEnabled: false`, always rendered into the pod unless overridden) match the table above. Verified at release semantics `cb3e6418`.

## finops-staff on Helm (auth and notify)

When using the release chart’s `finopsStaff` block, prefer **`finopsStaff.existingSecret`** over plain env for tokens. The chart reads keys via **`finopsStaff.secretKeys`** (defaults below). **`finopsStaff.createSecret.enabled: true`** is for dev/lab only (chart-rendered Secret). Set **`finopsStaff.notifyMinSeverity`** to `info`, `warning`, or `critical` (default `warning`) — same semantics as `FINOPS_STAFF_NOTIFY_MIN_SEVERITY` on compose.

| Helm value | Default secret key | Compose `.env` equivalent |
|------------|-------------------|---------------------------|
| `secretKeys.alertWebhookToken` | `alert_webhook_token` | `FINOPS_STAFF_ALERT_WEBHOOK_TOKEN` |
| `secretKeys.internalApiToken` | `internal_api_token` | `FINOPS_STAFF_INTERNAL_API_TOKEN` |
| `secretKeys.approvalWebhookToken` | `approval_webhook_token` | `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN` |

Example overlays: [`deploy/helm/values-finops-staff-auth.example.yaml`](../../deploy/helm/values-finops-staff-auth.example.yaml). Wire Alertmanager with `bearer_token_file` from the same Secret — see [`deploy/helm/values-alertmanager-finops.example.yaml`](../../deploy/helm/values-alertmanager-finops.example.yaml) and [finops-staff](./finops-staff.md#helm-auth-secrets).

## JWT and license

- **JWT keys** — Files on disk + `.env`; rotate via re-run init/fleet key sync procedures in release docs.
- **License** — Contact vendor for renewal; this package does not ship a license generator.

Full stub list: `.env.example` section 11 (finops) in your release tree.
