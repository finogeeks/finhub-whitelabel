---
name: finhub-deploy
description: >-
  End-to-end FinHub deploy from a vendor offline release tarball, then apply
  finhub-whitelabel overlays (branding, persona pack, optional OAuth and
  finops-staff). Primary customer agent entrypoint for finogeeks/finhub-whitelabel.
---
# FinHub white-label deploy (end-to-end)

Deploy **FinHub** from an **offline release tarball**, configure secrets and license inputs, bring the stack up, then layer branding and persona artifacts from **this repository** (`finhub-whitelabel`).

Use the name **chatkit** only when tarball paths, compose service names, or image names in the release still use that legacy name.

Operator doc map: [`AGENTS.md`](../../AGENTS.md), [`docs/agent-deploy-runbook.md`](../../docs/agent-deploy-runbook.md), [`docs/operations/install.md`](../../docs/operations/install.md), [`docs/operations/env-reference.md`](../../docs/operations/env-reference.md).

## Scope and dependencies

| Provided by | Contents |
|-------------|----------|
| **Vendor offline release tarball** | Container images (or load instructions), `docker-compose.prod.yml`, `scripts/init-env.sh`, `scripts/gen-secrets.sh`, `scripts/preflight-env.sh`, `scripts/fleet.sh`, `scripts/doctor.sh`, `.env.example`, bundled README/DEPLOY.md; finops-staff compose profile / Helm values when bundled |
| **This repo** | Branding seed, assets, persona pack, compose/Helm **overlays** only — no runnable stack alone |

If `scripts/gen-secrets.sh` is **missing** in an older release, use the fallback in [Generate secrets](#generate-secrets) — never fabricate deployment license values.

## When this applies

- Operator provides an offline release URL like `…/chatkit-offline-release-<version>-linux-amd64-<sha>.tar.gz` (or a local path).
- This fork is on the deploy host; branding/persona customized as needed.
- Goal: running, branded FinHub with optional OAuth or finops-staff only when explicitly requested.

---

## Phase 0 — Prepare this fork (local, no Docker required)

1. Run `./scripts/validate-artifacts.sh` from the repo root (must exit 0).
2. Optional: follow [`skills/finhub-brand/SKILL.md`](../finhub-brand/SKILL.md) for static login preview.
3. Record `WL_REPO` = absolute path to this clone.

Do not start Phase 1 until Phase 0 passes or the operator accepts documented validation warnings.

---

## Prerequisites (deploy host)

| Requirement | Guidance |
|-------------|----------|
| **Docker** | Docker Engine 24+ and **Compose v2** (`docker compose version`), or Kubernetes + Helm per release docs |
| **CPU/RAM** | Follow minimums in the **release README** (plan headroom for LLM proxy and databases) |
| **Disk** | Enough for image layers + volumes; release README often suggests 50–100 GiB free for lab |
| **Ports** | HTTP/HTTPS ingress and any DB/redis ports documented in release compose — do not guess |
| **Network** | Offline bundle assumes image load from tarball; LLM calls need egress only if using cloud LLM APIs |
| **Shell tools** | `curl`, `tar`, `sha256sum` or `shasum` if vendor ships checksums; `openssl` for secret fallback |

Writable work directory (e.g. `~/finhub-offline-<version>`). Do not unpack over live data without backup.

---

## Phase 1 — Release bootstrap (default stack, OAuth off)

### 1. Obtain and verify tarball

```bash
export RELEASE_URL='<vendor-provided-url>'
export WORKDIR=~/finhub-offline-<version>
mkdir -p "$WORKDIR" && cd "$WORKDIR"

curl -fL -o chatkit-offline-release.tar.gz "$RELEASE_URL"
```

If the vendor ships sidecar files:

- Compare **SHA-256** (`sha256sum -c checksums.txt` or manual compare).
- Verify **OpenPGP signature** only when the vendor documents the command and public key (no keys ship in this repo).

Record version and git/commit token from the archive filename for your report.

### 2. Unpack

```bash
tar -xzf chatkit-offline-release.tar.gz
cd <release-root-per-bundled-readme>   # often one directory down
```

Read **`README`**, **`DEPLOY.md`**, compose files, and **`.env.example` first**. Service names, ports, and compose file names in the release **override** this skill for Phase 1 mechanics.

**Canonical bootstrap** (when the release bundle ships all scripts):

1. `./scripts/init-env.sh`
2. `./scripts/gen-secrets.sh`
3. Operator fills `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER`, `LLM_API_KEY` in `.env`
4. `./scripts/preflight-env.sh`
5. `./scripts/fleet.sh up -d` — **also runs preflight automatically**
6. `./scripts/doctor.sh`

Older bundles may omit scripts; use fallbacks in each step below.

### 3. Initialize environment

If present:

```bash
./scripts/init-env.sh
```

Otherwise: copy `.env.example` → `.env` manually and note every `CHANGE_ME` / empty required field.

**Do not commit `.env`.** Never paste secret values into chat; report only variable **names** set or missing.

### 4. Generate secrets

**Preferred (release includes `scripts/gen-secrets.sh`):**

```bash
./scripts/gen-secrets.sh
```

Behavior (current release bundles): mints random values for documented secret env vars, **never overwrites** existing non-empty values, **never prints** secret values to stdout. **Does not** mint `DEPLOYMENT_LICENSE_*` or `LLM_API_KEY`.

Optional finops-staff tokens (`FINOPS_STAFF_ALERT_WEBHOOK_TOKEN`, `FINOPS_STAFF_INTERNAL_API_TOKEN`, `FINOPS_STAFF_APPROVAL_WEBHOOK_TOKEN`) are generated **only after** the operator uncomments the `FINOPS_STAFF_*` stubs in `.env.example` **§11**, then re-runs `./scripts/gen-secrets.sh`.

**Fallback (older tarball without script):**

For each empty secret slot in `.env.example` that is **not** a deployment license field, generate on the host:

```bash
openssl rand -hex 32
```

Paste into `.env` locally. Do **not** invent `DEPLOYMENT_LICENSE_KEY` / `DEPLOYMENT_LICENSE_CIPHER` (or vendor-documented equivalents).

### 5. Human-only inputs (operator must supply)

Set in `.env` (exact names from release `.env.example`):

| Class | Examples (names vary by release) | Agent rule |
|-------|----------------------------------|------------|
| **Deployment license** | `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER` | Vendor-issued only; **never auto-generate** |
| **LLM** | `LLM_API_KEY` (or name in `.env.example`) | Operator provides; no placeholders in production |
| **Public URLs** | `APP_URL`, admin/API bases | Operator chooses hostname |
| **Admin bootstrap** | First admin user/password if not auto-seeded | Per release README |

### 6. Preflight

If present:

```bash
./scripts/preflight-env.sh
```

If missing: manually confirm Docker daemon running, `.env` exists, `DEPLOYMENT_LICENSE_KEY`, `DEPLOYMENT_LICENSE_CIPHER`, and `LLM_API_KEY` are non-empty, disk free, and compose file path matches README.

### 7. Load images and start fleet

Load images per release README (`docker load`, `docker compose pull`, etc.).

When bundled:

```bash
./scripts/fleet.sh up -d
```

`fleet.sh up -d` **runs preflight automatically**; still run `preflight-env.sh` in step 6 when the operator wants an explicit gate before start.

**Fallback** (no `fleet.sh`):

```bash
docker compose -f docker-compose.prod.yml up -d
```

Use compose **profiles** only when README requires (not for finops-staff until [Optional finops-staff](#optional-finops-staff)).

### 8. Doctor

If present:

```bash
./scripts/doctor.sh
```

If missing: use health checks below.

### 9. Health checks

- `docker compose ps` (or `fleet.sh ps`) — all required services **healthy** or **running** per README.
- Hit health/readiness URLs documented in release.
- Tail logs for failing services: `docker compose logs -f --tail=200 <service>`.

### 10. Phase 1 smoke (unbranded)

Before white-label overlays:

- [ ] Login/app URL loads (operator hostname).
- [ ] Sign in with bootstrap admin.
- [ ] Open chat, send a message, confirm **streamed** assistant reply (SSE/chunked — not a single blocking blob).
- [ ] OAuth provider endpoints still **disabled** unless Phase 1.5 requested later.

Stop Phase 1 reporting here if the operator only wanted a vanilla release stack.

---

## Phase 2 — White-label overlays (this repo)

Run when the default stack is healthy and the operator wants this fork's branding and persona pack.

1. Set paths:

   ```bash
   export WL_REPO=/path/to/finhub-whitelabel
   export WL_PERSONA_PACK_HOST_PATH="$WL_REPO/persona-templates.json"
   export WL_PLATFORM_SETTINGS_HOST_PATH="$WL_REPO/branding/platform-settings.json"
   export WL_BRANDING_ASSETS_HOST_PATH="$WL_REPO/branding/assets"
   ```

2. **Compose** — merge override on release compose:

   ```bash
   docker compose -f docker-compose.prod.yml \
     -f "$WL_REPO/deploy/compose/docker-compose.whitelabel.override.yml" \
     up -d
   ```

   See [`deploy/compose/README.md`](../../deploy/compose/README.md).

3. **Pin** — override sets `PERSONA_TEMPLATE_CONFIG_PATH=/pack/persona-templates.json`. Without the pin, restarts can re-import the full default catalog.

4. **Persona sync (one-shot)** — binary ships in the **release image only**:

   ```bash
   export PERSONA_TEMPLATE_PACK_HOST_PATH="$WL_PERSONA_PACK_HOST_PATH"

   docker compose -f docker-compose.prod.yml \
     -f "$WL_REPO/deploy/compose/docker-compose.whitelabel.override.yml" \
     --profile persona-skill --profile persona-templates-sync \
     run --rm persona-templates-sync -- --dry-run
   ```

   Re-run **without** `--dry-run` to apply. See [`docs/persona-pack-pin.md`](../../docs/persona-pack-pin.md).

5. **Branding seed (Option B)** — after stack is up:

   ```bash
   export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

   curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
     -H "Content-Type: application/json" \
     -d @"$WL_PLATFORM_SETTINGS_HOST_PATH"
   ```

6. **Helm** — create ConfigMaps from [`deploy/helm/`](../../deploy/helm/), then:

   ```bash
   helm upgrade --install chatkit <chart-from-release> \
     -f "$WL_REPO/deploy/helm/values-whitelabel.yaml"
   ```

   Persona sync Job: dry-run first per [`deploy/helm/README.md`](../../deploy/helm/README.md).

7. **Phase 2 smoke** — [`docs/smoke-checklist.md`](../../docs/smoke-checklist.md): product name, logo, persona picker = pack only, default role, streamed chat still works.

---

## Phase 1.6 — finops-staff (opt-in only)

Optional alert diagnose + **human-approved** repairs; **not** on the chat path. Default **off**.

1. Docs: [`docs/operations/finops-staff.md`](../../docs/operations/finops-staff.md), notifications: [`docs/operations/finops-notifications.md`](../../docs/operations/finops-notifications.md).
2. Keep `FINOPS_STAFF_AUTO_ACT_DISABLED=true` and `FINOPS_STAFF_CLOSED_LOOP_ENABLED=false`.
3. Compose: `docker compose -f docker-compose.yml -f docker-compose.finops-staff.yml --profile finops-staff up -d`
4. Helm: `finopsStaff.enabled=true`, `policyMode=readonly` until SecAI approves `supervised`.
5. Uncomment finops token stubs in `.env`, run `gen-secrets.sh` again (names only on stdout).

Do **not** enable unattended auto-act or closed-loop for customers.

## Phase 1.5 — Identity OAuth (opt-in only)

Run **only** when the operator explicitly needs OAuth / embed “Sign in with …” on this Identity host.

### A. Identity service env

Set on **identity-service**, then restart:

| Env | Default | Purpose |
|-----|---------|---------|
| `OAUTH_PROVIDER_ENABLED` | `false` | Hard kill-switch; set `true` only when asked |
| `OAUTH_ISSUER` | falls back to `APP_URL` | Public issuer (no trailing slash) |
| `OAUTH_LOGIN_URL` | `${APP_URL}/login` | Authorize redirect for unauthenticated users |

Example:

```bash
OAUTH_PROVIDER_ENABLED=true
OAUTH_ISSUER=https://hub.example.com
OAUTH_LOGIN_URL=https://hub.example.com/login
```

See [`deploy/oauth-provider.env.example`](../../deploy/oauth-provider.env.example).

### B. OAuth client registration

Use the identity-service upsert script from the **release tree** (path in release README). Store `client_secret` in a vault; never commit.

### C. Relying party (embed Worker, etc.)

Configure RP secrets per embed/RP README. Issuer must match the Identity host used for `/auth/validate`.

### D. Policy

Keep kill-switch and issuer URLs as deploy-time env, not admin-console toggles.

---

## Optional finops-staff

**Default: off.** No Slack/Turnstile outbound unless configured.

The finops-staff service may appear in the **release bundle** as an optional compose profile and Helm subchart/values. This repo does not ship the service image — only documents how to enable it when the bundle includes it.

Before enabling the profile or chart: uncomment `FINOPS_STAFF_*` stubs in `.env.example` **§11**, run `./scripts/gen-secrets.sh` again, then set operating mode per operator choice below.

### Compose (when profile exists in release)

```bash
docker compose -f docker-compose.prod.yml \
  --profile finops-staff \
  up -d
```

Merge the white-label override **after** or together per release README if both are needed.

### Helm (when chart supports it)

```yaml
# deploy/helm/values-whitelabel.yaml (example keys — confirm in release chart)
finopsStaff:
  enabled: true
```

Apply via `helm upgrade` with release chart + `values-whitelabel.yaml`.

### Operating mode (operator choice)

| Mode | When to use |
|------|-------------|
| **readonly** (default when enabling) | Observe-only; enable first on every new environment |
| **supervised** + `FINOPS_STAFF_ALERT_PENDING_REPAIR` | Only when operator **explicitly** wants human-approved repair alerts |
| **auto-act** | **Stays disabled** unless release docs and operator contract say otherwise — do not enable by default |

### finops-staff secrets and Slack

- Uncomment `FINOPS_STAFF_*` stubs in `.env.example` **§11**, then re-run `./scripts/gen-secrets.sh` to mint tokens (only those uncommented slots).
- **Slack webhook URL** (or equivalent): optional; **empty = no outbound HTTP** to Slack.
- Do not enable finops-staff in automation without operator confirmation.

---

## Troubleshooting

| Symptom | Checks |
|---------|--------|
| Compose exits immediately | `docker compose config` for merge errors; re-run `preflight-env.sh` or read `doctor.sh` output |
| License errors on startup | Verify vendor license key/cipher; never substitute random hex |
| Skipped preflight in prod | Remove `FLEET_SKIP_PREFLIGHT`; run `preflight-env.sh` (bypass prints warning — dev/drill only) |
| LLM errors / empty replies | Provider key in `.env`, egress, model name in release config |
| Unhealthy database/redis | Volume permissions, port conflicts, logs from data services |
| Branding PUT fails | `ADMIN_BASE` URL, TLS trust, admin auth, JSON from `branding/platform-settings.json` |
| Persona sync dry-run fails | `PERSONA_TEMPLATE_PACK_HOST_PATH`, mount path, release image version |
| OAuth 404 “provider disabled” | `OAUTH_PROVIDER_ENABLED` not `true` or identity-service not restarted |
| finops-staff crash loop | Profile enabled but image not in bundle; disable profile or upgrade release |

Always prefer **release README** and `docker compose logs` over guessing service topology.

---

## Teardown

Lab / rebuild (destructive — confirm with operator):

```bash
# from release root
docker compose -f docker-compose.prod.yml down
# add -v only when operator agrees to wipe volumes
```

If finops-staff profile was used, same `down` with profiles that were enabled.

Remove workdir tarball extract only after backups. This repo clone can stay for the next deploy.

Kubernetes: `helm uninstall` per release docs; delete PVCs only with operator approval.

---

## Hard rules

- Phase 1 alone must remain a valid default deploy path upstream.
- OAuth defaults **off**; finops-staff defaults **off**; auto-act **off**.
- No FinHub-named patches inside chatkit middleware/web — seeds + mounts only.
- Persona replace: dry-run before write; external pack path only.
- If release README conflicts with this skill for core bring-up, **follow the release README** and report the conflict.

---

## Report back (template)

- Release URL, version/sha from archive name, workdir path.
- Whether `init-env.sh`, `gen-secrets.sh`, `preflight-env.sh`, `fleet.sh up -d`, `doctor.sh` were present and run.
- Secret **names** filled vs still missing (never values).
- License and LLM keys: operator-supplied yes/no only.
- Compose/helm files used; white-label overlay paths.
- OAuth / finops-staff: enabled or explicitly skipped.
- Smoke results per [`docs/smoke-checklist.md`](../../docs/smoke-checklist.md).
- Blockers (unhealthy services, failed PUT, failed persona dry-run).
