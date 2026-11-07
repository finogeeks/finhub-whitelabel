---
name: finhub-deploy
description: >-
  Use when deploying FinHub from an offline chatkit release tarball URL, then
  applying this white-label repo's overlays: branding seed, persona pack pin,
  and optional Identity OAuth. Primary customer agent entrypoint for
  finogeeks/finhub-whitelabel.
---
# FinHub white-label deploy

Deploy **FinHub** from an offline release tarball, then layer branding and persona artifacts from **this repository** (`finhub-whitelabel`).

Mention **chatkit** only when tarball paths, compose service names, or image names in the release still use that name.

## When this applies

- User gives an offline release URL like `…/chatkit-offline-release-<version>-linux-amd64-<sha>.tar.gz`
- User has cloned or forked this repo and customized `branding/` and `persona-templates.json`
- Goal: branded login chrome + pruned persona pack without editing chatkit source

## Preconditions

- Docker Engine + Compose v2 (or k8s + Helm per release docs)
- Writable work directory on the target host
- Do **not** invent image tags or secrets — use the release README and `.env.example`
- Never commit real secrets into chat; use host env files or a vault

## Phase 1 — Default offline stack

1. **Workdir** — e.g. `~/finhub-offline-<version>`. Do not unpack over live data without a backup plan.
2. **Download** — `curl -fL -o chatkit-offline-release.tar.gz '<URL>'`; verify size and HTTP 200.
3. **Unpack** and `cd` to the release root per the tarball layout.
4. **Read bundled README** (and `DEPLOY.md`, compose files, `.env.example`) **first**. Follow release service names and ports.
5. **Env** — copy `.env.example` → `.env`; fill only user-supplied or documented safe defaults.
6. **Images** — `docker compose pull` or `docker load` per README.
7. **Start** — `docker compose -f <file-from-readme> up -d` (profiles only if README requires).
8. **Smoke** — health checks and UI URL from README; report failing containers.
9. **Stop Phase 1** when default stack is healthy and OAuth is still **off** unless Phase 1.5 was requested.

## Phase 2 — White-label overlays (this repo)

Run when the user wants their fork's branding and persona pack (always for this template).

1. Ensure this repo is on the host (clone path = `WL_REPO`).

2. **Compose** — merge override on top of release compose:

   ```bash
   export WL_PERSONA_PACK_HOST_PATH="$WL_REPO/persona-templates.json"
   export WL_PLATFORM_SETTINGS_HOST_PATH="$WL_REPO/branding/platform-settings.json"
   export WL_BRANDING_ASSETS_HOST_PATH="$WL_REPO/branding/assets"

   docker compose -f docker-compose.prod.yml \
     -f "$WL_REPO/deploy/compose/docker-compose.whitelabel.override.yml" \
     up -d
   ```

   See `deploy/compose/README.md` for env var details.

3. **Pin** — override sets `PERSONA_TEMPLATE_CONFIG_PATH=/pack/persona-templates.json`. Without the pin, restarts can re-import the full default catalog.

4. **Persona sync (one-shot)** — tool ships in the **release image only**:

   ```bash
   export PERSONA_TEMPLATE_PACK_HOST_PATH="$WL_PERSONA_PACK_HOST_PATH"

   docker compose -f docker-compose.prod.yml \
     -f "$WL_REPO/deploy/compose/docker-compose.whitelabel.override.yml" \
     --profile persona-skill --profile persona-templates-sync \
     run --rm persona-templates-sync -- --dry-run
   ```

   Re-run **without** `--dry-run` to apply. Binary path in container: `/app/bin/sync-platform-persona-templates` with `sync_mode: replace_platform` from your pack. See `docs/persona-pack-pin.md`.

5. **Branding seed (Option B)** — after stack is up:

   ```bash
   export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

   curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
     -H "Content-Type: application/json" \
     -d @"$WL_PLATFORM_SETTINGS_HOST_PATH"
   ```

6. **Helm** (if k8s) — create ConfigMaps from `deploy/helm/`, then `helm upgrade --install … -f "$WL_REPO/deploy/helm/values-whitelabel.yaml"` per `deploy/helm/README.md`. Run persona sync Job with `--dry-run` first.

7. **Smoke white-label** — `docs/smoke-checklist.md`: product name, logo, persona picker = pack only, default role correct.

## Phase 1.5 — Identity OAuth (opt-in only)

Run only when the user explicitly needs OAuth / embed "Sign in with …" against this Identity host.

### A. Identity service env

Set on **identity-service** (compose `.env`, Helm values, or unit env), then restart:

| Env | Default | Purpose |
|-----|---------|---------|
| `OAUTH_PROVIDER_ENABLED` | `false` | Hard kill-switch; set `true` to expose `/oauth/*` |
| `OAUTH_ISSUER` | falls back to `APP_URL` | Public issuer (no trailing slash) |
| `OAUTH_LOGIN_URL` | `${APP_URL}/login` | Authorize redirect for unauthenticated users |

Example (replace host):

```bash
OAUTH_PROVIDER_ENABLED=true
OAUTH_ISSUER=https://hub.example.com
OAUTH_LOGIN_URL=https://hub.example.com/login
```

See `deploy/oauth-provider.env.example`.

### B. OAuth client registration

Use the identity-service upsert script from the **release tree** (exact path in release README). Store `client_secret` in a vault; never commit.

### C. Relying party (embed Worker, etc.)

Configure RP secrets per the embed or RP README. Authorize/token issuer must match the Identity host used for `/auth/validate`.

### D. Env-only forever

Keep kill-switch and issuer URLs as deploy-time env, not admin-console toggles.

## Hard rules

- Phase 1 alone must remain a valid default deploy path upstream
- OAuth defaults **off**; never set `OAUTH_PROVIDER_ENABLED=true` unless asked
- No FinHub-named patches inside chatkit middleware/web — seeds + mounts only
- Persona replace: dry-run before write; external pack path only (not bundled default without `--i-know`)
- If release README conflicts with this skill for Phase 1, **follow the release README** and report the conflict

## Report back

- Release URL + version/sha from archive name
- Workdir, compose files, overlay paths from this repo
- OAuth Phase 1.5: issuer host and client-id only (never client_secret in chat)
- `ADMIN_BASE`, persona pin path, whether sync dry-run + apply ran
- Smoke results per `docs/smoke-checklist.md`
- Blockers (Docker, URL, unhealthy services, branding PUT failures)
