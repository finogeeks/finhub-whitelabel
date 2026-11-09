[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# Docker Compose overlays

White-label overlay: persona pin, platform settings file mount, branding assets at `/static/branding`. Requires the production compose file from your **offline chatkit / FinHub release** (not shipped in this repo).

Default example host for docs: **`hub.example.com`** — set ingress / `ADMIN_BASE` for your environment.

## Files

| File | Role |
|------|------|
| `docker-compose.whitelabel.override.yml` | Persona pin, platform settings mount, `/static/branding` assets |

## Environment paths

```bash
export WL_PERSONA_PACK_HOST_PATH=/path/to/finhub-whitelabel/persona-templates.json
export WL_PLATFORM_SETTINGS_HOST_PATH=/path/to/finhub-whitelabel/branding/platform-settings.json
export WL_BRANDING_ASSETS_HOST_PATH=/path/to/finhub-whitelabel/branding/assets
```

For persona sync, upstream may use `PERSONA_TEMPLATE_PACK_HOST_PATH` — set it to the same pack file.

## Persona one-shot sync (dry-run first)

```bash
export PERSONA_TEMPLATE_PACK_HOST_PATH="$WL_PERSONA_PACK_HOST_PATH"

docker compose -f docker-compose.prod.yml \
  -f /path/to/finhub-whitelabel/deploy/compose/docker-compose.whitelabel.override.yml \
  --profile persona-skill --profile persona-templates-sync \
  run --rm persona-templates-sync -- --dry-run
```

Remove `--dry-run` to apply `replace_platform` via `/app/bin/sync-platform-persona-templates` in the release image.

## Platform settings seed

After the stack is up:

```bash
export ADMIN_BASE="${ADMIN_BASE:-https://hub.example.com}"

curl -sS -X PUT "$ADMIN_BASE/admin/config/platform-settings" \
  -H "Content-Type: application/json" \
  -d @"$WL_PLATFORM_SETTINGS_HOST_PATH"
```

## Steady-state

```bash
docker compose -f docker-compose.prod.yml \
  -f deploy/compose/docker-compose.whitelabel.override.yml \
  up -d
```

Do not add this override on a default (non-white-label) compose unless you intend to pin your pack and branding files.

## Optional finops-staff (release only)

When your offline release defines a `finops-staff` compose profile, enable it **only** if the operator asked:

```bash
docker compose -f docker-compose.prod.yml --profile finops-staff up -d
```

Start in **readonly**; supervised repair alerts and Slack webhooks are opt-in (empty webhook = no outbound calls). See [`skills/finhub-deploy/SKILL.md`](../../skills/finhub-deploy/SKILL.md).
